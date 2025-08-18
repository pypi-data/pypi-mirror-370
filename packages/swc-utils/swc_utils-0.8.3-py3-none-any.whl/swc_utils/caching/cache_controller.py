from .caching_service import CachingService


class CacheController:
    """
    A class that manages multiple caching services. It can create new caching services, clear all caches,
    clear a specific service's caches, clear a specific cache, and inspect the current state of all services.
    """
    def __init__(self, cache_services: dict[str, CachingService] = None):
        """
        :param cache_services: A dictionary of caching services to start with.
        The key is the name of the service and the value is the service itself.
        """
        self._cache_services = cache_services or dict()

    def create_cache_service(self, name: str):
        """
        Create a new caching service with the given name. If a service with the same name already exists,
        return the existing service.
        :param name: The name of the service to create.
        :return: The caching service with the given name.
        """
        if name in self._cache_services:
            return self._cache_services[name]

        service = CachingService()
        self._cache_services[name] = service
        return service

    def clear_all(self):
        """
        Send a clear_all_caches command to all caching services.
        :return:
        """
        for service in self._cache_services.values():
            service.clear_all_caches()

    def clear_service(self, name: str):
        """
        Send a clear_all_caches command to the caching service with the given name.
        :param name:
        :return:
        """
        service = self._cache_services.get(name)
        if service is None:
            raise KeyError(f'Service {name} does not exist')

        service.clear_all_caches()
        
    def clear_service_cache(self, name: str, cache_name: str):
        """
        Send a clear_cache command to the caching service with the given name.
        :param name:
        :param cache_name:
        :return:
        """
        service = self._cache_services.get(name)
        if service is None:
            raise KeyError(f'Service {name} does not exist')

        service.clear_cache(cache_name)

    def tree(self):
        """
        Inspect all caching services and return a dictionary with the service names as keys and the service's
        inspect method as values.
        :return:
        """
        service_tree = dict()

        for name, service in self._cache_services.items():
            service_tree[name] = service.inspect()

        return service_tree

    @property
    def cache_services(self):
        """
        Property to access the cache services.
        :return:
        """
        return self._cache_services

    @property
    def size(self):
        """
        Property to get the total size of all caching services.
        :return:
        """
        total_size = 0

        for service in self._cache_services.values():
            total_size += service.size

        return total_size
