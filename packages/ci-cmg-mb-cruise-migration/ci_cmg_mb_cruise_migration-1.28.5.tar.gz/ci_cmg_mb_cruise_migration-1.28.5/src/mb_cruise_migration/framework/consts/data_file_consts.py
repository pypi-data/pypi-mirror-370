class PathIndexes(object):
    ROOT = 0
    PLATFORM_TYPE = 1
    PLATFORM_NAME = 2
    POSSIBLE_CANADIAN = 2
    SURVEY_NAME = 3
    MULTIBEAM = 4
    DATA = 5
    VERSION = 6
    DATASET_TYPE = 7
    INSTRUMENT = 8
    POSSIBLE_LEG = [8, 9]
    POSSIBLE_REGION = [8, 9]
    POSSIBLE_ZONE = [8, 9]
    POSSIBLE_ERRONEOUS = [8, 9]


class PathRoot(object):
    OCEAN = "ocean"
    MGG = "MGG"
    WCD = "WCD"
    SINGLEBEAM = "singlebeam"
    XTF = "XTF"


class PathPlatformType(object):
    SHIPS = "ships"
    AIRCRAFT = "aircraft"
    AUVS = "auvs"
    AEROCOMMANDER = "aerocommander"
    SENTRY = "sentry"
    STATIONARY = "stationary"


class PathVersion(object):
    VERSION1 = "version1"
    VERSION2 = "version2"
    VERSION3 = "version3"

    @staticmethod
    def get_level(version):
        if version == PathVersion.VERSION1:
            return "level_00"
        if version == PathVersion.VERSION2:
            return "level_01"
        if version == PathVersion.VERSION3:
            return "level_02"
        raise ValueError(f"{version} should be one of {PathVersion.VERSION1}, {PathVersion.VERSION2}, or {PathVersion.VERSION3}")


class PathSubDir(object):
    NONPUBLIC = "nonpublic"
    MULTIBEAM = "multibeam"
    DATA = "data"
    CANADIAN = "Canadian_Data"
    RAW = "raw"


class PathDataType(object):
    METADATA = "metadata"
    MB = "MB"
    PRODUCTS = "products"
    ANCILLARY = "ancillary"
