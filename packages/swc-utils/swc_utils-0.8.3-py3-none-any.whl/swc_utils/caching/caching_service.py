from .cache import Cache


class CachingService:
    """
    Caching service that manages multiple caches.
    """
    def __init__(self):
        self.caches = {}

    def get_cache(self, cache_name: str, initiator_type: type, initiator_data: list or int = None) -> Cache:
        """
        Get a cache by name. If the cache does not exist, create a new cache with the given name and initiator data.
        :param cache_name: Name of the cache to get or create.
        :param initiator_type: Type of the initiator (e.g. a class) that will be used to create the cache.
        :param initiator_data: Data that will be used to create the cache.
        :return: The cache instance with the given name.
        """
        if cache_name not in self.caches:
            self.caches[cache_name] = Cache(initiator_type, initiator_data)
        return self.caches[cache_name]

    def clear_cache(self, cache_name: str):
        """
        Clear a cache by name.
        :param cache_name: Name of the cache to clear.
        :return:
        """
        if cache_name in self.caches:
            self.caches[cache_name].clear()

    def clear_all_caches(self):
        """
        Clear all caches.
        :return:
        """
        for cache in self.caches.values():
            cache.clear()

    def clear_expired_caches(self, expiration_time: int):
        """
        Clear all caches that have expired. The expiration time can be provided.
        :param expiration_time: Expiration time in seconds.
        :return:
        """
        for cache in self.caches.values():
            cache.clear_expired(expiration_time)

    def inspect(self):
        """
        Inspect the caching service and return information about all caches.
        Information includes cache size and cache content.
        :return:
        """
        caches = dict()

        for name, cache in self.caches.items():
            caches[name] = cache.inspect()

        return {
            "caches": caches,
            "size": self.size,
        }

    @property
    def size(self):
        """
        Property that returns the total size of all caches in the caching service.
        :return:
        """
        total_size = 0

        for cache in self.caches.values():
            total_size += cache.size

        return total_size
