import copy
import threading


class ThreadSafeMappings(object):
    def __init__(self):
        self.__lock = threading.Lock()
        self.__mappings = []

    def add(self, mapping: tuple):
        with self.__lock:
            self.__mappings.append(mapping)

    def get(self):
        joins = []
        with self.__lock:
            joins = copy.deepcopy(self.__mappings)
        return joins
