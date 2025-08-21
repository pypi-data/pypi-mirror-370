class CruiseAccessPath(object):
    def __init__(self, path, path_type, id=None):
        self.path = path
        self.path_type = path_type
        self.id = id

    def __hash__(self):
        return hash((self.path, self.path_type))

    def __eq__(self, obj):
        EQUAL = True
        NOT_EQUAL = False

        if isinstance(obj, CruiseAccessPath) and self.path == obj.path and self.path_type == obj.path_type:
            return EQUAL

        return NOT_EQUAL

    def __ne__(self, obj):
        EQUAL = False
        NOT_EQUAL = True

        if not isinstance(obj, CruiseAccessPath):
            return NOT_EQUAL

        if self.path != obj.path and self.path_type != obj.path_type:
            return NOT_EQUAL

        return EQUAL
