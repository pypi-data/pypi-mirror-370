from swc_utils.exceptions.package_exceptions import MissingDependencyError

try:
    from redis import Redis
except ImportError:
    raise MissingDependencyError("redis")

try:
    from flask import Flask, current_app
except ImportError:
    raise MissingDependencyError("flask")

try:
    from flask_session import Session
except ImportError:
    raise MissingDependencyError("flask_session")

from swc_utils.caching import CachingService
from swc_utils.redis_db.event_manager import SessionEventManager


def get_app_redis_interface(app: Flask = current_app) -> "AppRedisInterface":
    """
    Get the AppRedisInterface object from the app context
    :param app: Flask app
    :return: AppRedisInterface object
    """
    return app.config["APP_REDIS_INTERFACE"]


class AppRedisInterface:
    """
    AppRedisInterface class to manage the Redis connection and session event manager
    and bind it to the Flask app
    """
    def __init__(self, app: Flask, is_host: bool = False,
                 redis_host="127.0.0.1", redis_port=6379, redis_db=0, redis_unix_socket_path=None,
                 cache: CachingService = None):
        """
        Initialize the AppRedisInterface object.
        When unix_socket_path is provided, host and port will be ignored.
        When no cache is provided, a new CachingService object will be created.
        :param app: Flask app
        :param is_host: If True, the app is the host of the session event manager
        :param redis_host: Redis host
        :param redis_port: Redis port
        :param redis_db: Redis database index
        :param redis_unix_socket_path: Redis unix socket path
        :param cache: CachingService object
        """
        self.app = app

        self.__redis_session = Redis(host=redis_host, port=redis_port, db=redis_db) \
            if redis_unix_socket_path is None else Redis(unix_socket_path=redis_unix_socket_path)
        self.__redis_cache = cache or CachingService()

        self.__event_manager = SessionEventManager(self.app, self.__redis_session, self.__redis_cache, host=is_host)

        self.__initialize_on_app()

    def __initialize_on_app(self):
        self.app.config["SESSION_COOKIE_SAMESITE"] = "None"
        self.app.config["SESSION_COOKIE_SECURE"] = True
        self.app.config["SESSION_TYPE"] = "redis"
        self.app.config["SESSION_SERIALIZATION_FORMAT"] = "json"
        self.app.config["SESSION_REDIS"] = self.__redis_session
        self.app.config["APP_REDIS_INTERFACE"] = self
        Session(self.app)

    @property
    def redis_session(self) -> Redis:
        """
        Get the Redis session object
        :return: Redis session object
        """
        return self.__redis_session

    @property
    def event_manager(self) -> SessionEventManager:
        """
        Get the session event manager object
        :return: SessionEventManager object
        """
        return self.__event_manager

    @property
    def redis_cache(self) -> CachingService:
        """
        Get the CachingService object.
        :return: CachingService object
        """
        return self.__redis_cache
