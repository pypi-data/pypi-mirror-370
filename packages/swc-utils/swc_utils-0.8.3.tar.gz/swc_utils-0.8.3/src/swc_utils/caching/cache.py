import io
import json
import sys
import zipfile
import pickle
from time import time


class Cache:
    """
    A simple cache class that can be used to store data in memory and dump it to a ZIP archive
    """
    def __init__(self, initiator: type = dict, initiator_data: dict or list = None):
        """
        :param initiator: The type of the cache, i.e. dict or list
        :param initiator_data:
        """
        self.__initiator = initiator
        self.__initiator_data = initiator_data
        self.__init_cache()
        self._updated = time()

    def __init_cache(self):
        self.__cache = self.__initiator(self.__initiator_data) if self.__initiator_data is not None else self.__initiator()

    def _set(self, key, value):
        self.__cache[key] = value
        self._updated = time()

    def _get(self, key):
        return self.__cache[key]

    def __setitem__(self, key, value):
        self._set(key, value)

    def __getitem__(self, key):
        return self._get(key)

    def __dir__(self):
        return dir(self.__cache)

    def __iter__(self):
        return iter(self.__cache)

    def __len__(self):
        return len(self.__cache)

    def __contains__(self, key):
        return key in self.__cache

    def __delitem__(self, key):
        del self.__cache[key]

    def serialize(self):
        return self.__cache

    @staticmethod
    def __auto_dump(data):
        try:
            return json.dumps(data), True
        except (TypeError, OverflowError):
            return pickle.dumps(data), False

    def dump(self) -> bytes:
        """
        Dumps the cache to a ZIP archive containing the serialized data either as JSON or binary data
        """
        data = self.serialize()
        print(self, len(data), data)

        if type(data) is list:
            data = zip(range(len(data)), data)
        if type(data) is not dict:
            data = {"data": data}

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for key, value in data.items():
                if type(value) is bytes:
                    zip_file.writestr(f"{key}.bin", value)
                else:
                    data, is_json = self.__auto_dump(value)
                    zip_file.writestr(f"{key}.{'json' if is_json else 'bin'}", data)

        buffer.seek(0)
        return buffer.getvalue()

    def clear(self):
        """
        Clears the cache
        :return:
        """
        self.__init_cache()
        self._updated = time()

    def clear_expired(self, expiration_time: int):
        """
        Clears the cache if it has not been updated for a certain amount of time
        :param expiration_time:
        :return:
        """
        if self._updated + expiration_time < time():
            self.clear()

    def inspect(self) -> dict:
        """
        Returns a dictionary containing information about the cache
        :return:
        """
        return {
            "type": type(self.__cache).__name__,
            "initial_size": sys.getsizeof(self.__initiator_data),
            "length": len(self.__cache),
            "updated": self._updated,
            "size": self.size
        }

    @property
    def updated(self):
        """
        Property that returns the last time the cache was updated
        :return:
        """
        return self._updated

    @property
    def size(self) -> int:
        """
        Property that returns the size of the cache in integer
        :return:
        """
        return sys.getsizeof(self.__cache)

    # Dict-only methods

    def keys(self):
        """
        Returns the keys of the cache if it is a dictionary
        :return:
        """
        if type(self.__cache) is not dict:
            raise TypeError("Can't get keys from non-dict cache")
        return self.__cache.keys()

    def values(self):
        """
        Returns the values of the cache if it is a dictionary
        :return:
        """
        if type(self.__cache) is not dict:
            raise TypeError("Can't get values from non-dict cache")
        return self.__cache.values()

    def items(self):
        """
        Returns the items of the cache if it is a dictionary
        :return:
        """
        if type(self.__cache) is not dict:
            raise TypeError("Can't get items from non-dict cache")
        return self.__cache.items()

    def get(self, key, default=None):
        """
        Returns the value of a key in the cache if it is a dictionary
        :param key:
        :param default:
        :return:
        """
        if type(self.__cache) is not dict:
            raise TypeError("Can't get items from non-dict cache")
        return self.__cache.get(key, default)

    # List-only methods

    def extend(self, data):
        """
        Extends the cache if it is a list
        :param data:
        :return:
        """
        if type(self.__cache) is not list:
            raise TypeError("Can't extend non-list cache")
        self.__cache.extend(data)
        self._updated = time()

    def sort(self, key=None, reverse=False):
        """
        Sorts the cache if it is a list
        :param key:
        :param reverse:
        :return:
        """
        if type(self.__cache) is not list:
            raise TypeError("Can't sort non-list cache")
        self.__cache.sort(key=key, reverse=reverse)
        self._updated = time()
