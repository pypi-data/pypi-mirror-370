from mb_cruise_migration.framework.consts.data_file_consts import PathPlatformType
from mb_cruise_migration.framework.consts.error_consts import ErrorConsts


class PlatformTypeConsts(object):
    AUV = "auv"
    SHIP = "ship"
    SENTRY = "sentry"
    AIRCRAFT = "aircraft"
    STATIONARY = "stationary"
    AEROCOMMANDER = "aerocommander"


class PlatformTypeResolver(object):
    @staticmethod
    def resolve_platform_from_path_derived_platform(path_platform_type):
        if path_platform_type == PathPlatformType.SHIPS:
            return PlatformTypeConsts.SHIP
        if path_platform_type == PathPlatformType.AUVS:
            return PlatformTypeConsts.AUV
        if path_platform_type == PathPlatformType.SENTRY:
            return PlatformTypeConsts.SENTRY
        if path_platform_type == PathPlatformType.AIRCRAFT:
            return PlatformTypeConsts.AIRCRAFT
        if path_platform_type == PathPlatformType.AEROCOMMANDER:
            return PlatformTypeConsts.AEROCOMMANDER
        if path_platform_type == PathPlatformType.STATIONARY:
            return PlatformTypeConsts.STATIONARY
        raise ValueError(ErrorConsts.NO_MATCHING_PLATFORM_TYPE + path_platform_type)
