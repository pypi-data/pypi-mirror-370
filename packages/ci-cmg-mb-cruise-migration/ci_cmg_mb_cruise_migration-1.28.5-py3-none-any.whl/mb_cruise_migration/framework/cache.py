import threading


class Cache(object):
    def __init__(self):
        self.__lock = threading.Lock()
        self.__cache = []

    def request(self, item, equality_func):
        with self.__lock:
            if not self.__cache:
                return None

            for cached in self.__cache:
                if equality_func(cached, item):
                    return cached  # Hit

            return None  # Miss

    def update(self, item):
        if not item.id:
            raise ValueError("Cache items must have an 'id' parameter")

        with self.__lock:
            self.__cache.insert(0, item)

    def clean_cache(self):
        with self.__lock:
            self.__cache = []

    def trim_cache(self, limit):
        with self.__lock:
            cache_size = len(self.__cache)
            if cache_size > limit:
                self.__cache = self.__cache[:limit]

