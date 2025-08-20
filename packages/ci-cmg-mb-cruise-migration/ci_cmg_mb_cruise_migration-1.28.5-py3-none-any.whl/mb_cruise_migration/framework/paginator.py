class Paginator(object):
    def __init__(self, pagesize, table_size):
        self.__pagesize = pagesize
        self.__last = table_size
        self.__skip = 0
        self.__next = pagesize if table_size > pagesize else table_size

    def done(self):
        return False if self.__skip < self.__last else True

    def paginate(self):
        if self.done():
            raise StopIteration("Paginator has exhausted known table size, check done status prior to paging.")
        current_skip, current_limit = self.__get_current()
        self.__skip = self.__increment(self.__skip)
        self.__next = self.__increment(self.__next)
        return current_skip, current_limit - current_skip

    def __get_current(self):
        return self.__skip, self.__next

    def __increment(self, incrementee):
        return incrementee + self.__pagesize if incrementee + self.__pagesize < self.__last else self.__last
