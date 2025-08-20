class CruisePlatform(object):
    def __init__(self, internal_name, platform_type, docucomp_uuid, long_name, designator, platform_name, id=None):
        self.internal_name = internal_name
        self.platform_type = platform_type
        self.docucomp_uuid = docucomp_uuid
        self.long_name = long_name
        self.designator = designator
        self.platform_name = platform_name
        self.id = id
