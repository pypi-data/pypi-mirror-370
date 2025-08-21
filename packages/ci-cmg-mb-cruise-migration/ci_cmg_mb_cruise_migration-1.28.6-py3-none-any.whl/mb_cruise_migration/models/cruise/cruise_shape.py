class CruiseShape(object):
    def __init__(self, shape_type, geom_type, shape, id=None):
        self.shape_type = shape_type
        self.geom_type = geom_type
        self.shape = shape
        self.id = id
