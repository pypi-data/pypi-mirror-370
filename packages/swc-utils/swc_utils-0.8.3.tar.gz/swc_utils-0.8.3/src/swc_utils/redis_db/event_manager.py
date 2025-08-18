import uuid
import pickle
import traceback

from swc_utils.exceptions.package_exceptions import MissingDependencyError

try:
    from redis import Redis
except ImportError:
    raise MissingDependencyError("redis")

try:
    from flask import Flask
except ImportError:
    raise MissingDependencyError("flask")

from threading import Thread
from swc_utils.caching import CachingService


class SessionEventManager:
    """
    A class that manages events between different services using Redis as a message broker.
    It can be used to send queries to other services and receive responses.
    The class can also act as a listener for incoming queries and execute callbacks based on the query channel,
    similar to an event listener, but using multiple message receivers for a single redis server is not recommended.
    Thus, the class is designed to be used as a single instance per service and only one application should be
    listening to the queries.
    """
    def __init__(self, app: Flask, redis: Redis, redis_cache: CachingService, data_lifetime=10, host=False):
        """
        :param app: Flask application
        :param redis: Redis connection
        :param redis_cache: CachingService instance
        :param data_lifetime: Lifetime of the cached data in seconds
        :param host: If True, the event manager will start listening for incoming queries
        """
        self.app = app
        self.redis = redis
        self.cache = redis_cache.get_cache("redis-event-manager", dict)
        self.__events = {}
        self.__data_lifetime = data_lifetime

        if host:
            self._start()

    def _start(self):
        try:
            import gevent
            from gevent import monkey

            monkey.patch_all()
            gevent.spawn(self.__thread, self.app)
        except ImportError:
            self.app.logger.warn("REDIS EM Gevent not found, using threading instead. This is not recommended!")
            Thread(target=self.__thread, args=(self.app,), daemon=True).start()

    # Event handling ----------------------------------------------------------

    def on_callback(self, channel: str, callback: callable, *e_args, **e_kwargs):
        """
        Adds a callback to the event manager
        :param channel: Message channel
        :param callback: Callback function
        :param e_args: Additional arguments for the callback
        :param e_kwargs: Additional keyword arguments for the callback
        :return:
        """
        if channel in self.__events:
            raise Exception(f"Event {channel} already exists")

        self.__events[channel] = lambda *args, **kwargs: callback(*args, *e_args, **kwargs, **e_kwargs)

    def on(self, channel: str) -> callable:
        """
        Decorator for adding a callback to the event manager.
        Operates like the on_callback method, but allows for a more concise syntax.
        :param channel: Message channel
        :return: Decorator
        """
        def decorator(func, *args, **kwargs):
            self.on_callback(channel, func, *args, **kwargs)

        return decorator

    def off(self, channel):
        """
        Removes a callback from the event manager
        :param channel: Message channel
        :return:
        """
        self.__events.pop(channel)

    def __call_callback(self, channel: str, *args: list[any], **kwargs: dict[any, any]) -> any:
        if channel not in self.__events:
            return

        return self.__events[channel](*args, **kwargs)

    def __thread(self, app: Flask):
        pubsub = self.redis.pubsub()
        pubsub.subscribe("session-queries")

        for message in pubsub.listen():
            if message["type"] == "message":
                query = pickle.loads(message["data"])
                query_id = query.get("id")
                channel = query.get("channel")
                args = query.get("args") or []
                kwargs = query.get("kwargs") or {}

                response_key = f"session-response:{query_id}"
                try:
                    with app.app_context():
                        app.logger.info(f"REDIS [{channel}] {args}")
                        response = app.ensure_sync(self.__call_callback)(channel, *args, **kwargs)

                    self.redis.publish(response_key, pickle.dumps({"id": query_id, "res": pickle.dumps(response), "err": None}))
                except Exception as e:
                    self.redis.publish(response_key, pickle.dumps({"id": query_id, "res": None, "err": {
                        "message": str(e),
                        "traceback": traceback.format_exc(),
                        "args": args,
                        "kwargs": kwargs
                    }}))
                    raise e

    # Event sending -----------------------------------------------------------

    @staticmethod
    def __parse_response(response: any) -> any:
        if type(response) is bytes:
            return pickle.loads(response)
        return response

    def query(self, channel: str, *args: any, **kwargs: [any, any]) -> any:
        """
        Sends a query to the event manager and waits for a response.
        :param channel: Message channel
        :param args: Query data arguments
        :param kwargs: Query data keyword arguments
        :return: Response data or None
        """
        cache_key = f"{channel}:{args}:{kwargs}"
        self.cache.clear_expired(self.__data_lifetime)
        if cache_hit := self.cache.get(cache_key):
            return self.__parse_response(cache_hit)

        query_id = str(uuid.uuid4())
        response_key = f"session-response:{query_id}"

        self.redis.publish("session-queries", pickle.dumps(
            {"id": query_id, "channel": channel, "args": args, "kwargs": kwargs})
        )

        pubsub = self.redis.pubsub()
        pubsub.subscribe(response_key)

        for message in pubsub.listen():
            if message["type"] == "message":
                response = pickle.loads(message["data"])
                if response.get("id") != query_id:
                    continue

                err = response.get("err")
                if err is not None:
                    raise Exception(err)

                resp_data = response.get("res")
                if resp_data is not None:
                    self.cache[cache_key] = resp_data
                    return self.__parse_response(resp_data)

        return None

