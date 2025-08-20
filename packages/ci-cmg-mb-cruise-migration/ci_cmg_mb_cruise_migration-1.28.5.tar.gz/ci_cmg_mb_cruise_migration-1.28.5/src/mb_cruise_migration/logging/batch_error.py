class BatchError(object):
    def __init__(self, error, offset):
        self.error = error
        self.offset = offset