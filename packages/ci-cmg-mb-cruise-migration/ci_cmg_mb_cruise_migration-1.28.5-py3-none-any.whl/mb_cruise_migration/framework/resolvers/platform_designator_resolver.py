from typing import Optional

from mb_cruise_migration.models.cruise.cruise_platforms import CruisePlatform


class DesignatorLookup(object):
    LOOKUP_by_internal_name = {}
    LOOKUP_by_long_name = {}

    @staticmethod
    def set_lookup(cruise_platforms: [CruisePlatform]):
        for platform in cruise_platforms:
            if platform.designator is not None:
                DesignatorLookup.LOOKUP_by_internal_name.update({platform.internal_name: platform.designator})
                DesignatorLookup.LOOKUP_by_long_name.update({platform.long_name: platform.designator})

    @staticmethod
    def get_designator_by_parsed_data_file_platform_name(platform_name: str) -> Optional[str]:
        if platform_name in DesignatorLookup.LOOKUP_by_internal_name:
            return DesignatorLookup.LOOKUP_by_internal_name[platform_name]
        else:
            return None

    @staticmethod
    def get_designator_by_mb_survey_platform_name(platform_name) -> Optional[str]:
        if platform_name in DesignatorLookup.LOOKUP_by_long_name:
            return DesignatorLookup.LOOKUP_by_long_name[platform_name]
        else:
            return None
