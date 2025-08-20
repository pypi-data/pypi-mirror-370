from typing import Optional

from mb_cruise_migration.framework.consts.version_description_consts import (
    VersionDescriptionConsts,
)
from mb_cruise_migration.models.cruise.cruise_version_descriptions import (
    CruiseVersionDescription,
)


class VDLookup(object):
    LOOKUP = {}
    DEFAULT_VERSION = VersionDescriptionConsts.RAW

    @staticmethod
    def set_lookups(descriptions: [CruiseVersionDescription]):
        for description in descriptions:
            VDLookup.LOOKUP.update({description.description: description})

    @classmethod
    def get_id(cls, version) -> Optional[int]:
        if version == 1 or version == "1":
            return VDLookup.get_id_from_description(VersionDescriptionConsts.RAW)
        if version == 2 or version == "2":
            return VDLookup.get_id_from_description(VersionDescriptionConsts.PROCESSED)
        if version == 3 or version == "3":
            return VDLookup.get_id_from_description(VersionDescriptionConsts.PRODUCT)
        raise ValueError(f"No version entry exists for version:  {version}")

    @staticmethod
    def get_id_from_description(description: str) -> int:
        try:
            version_description = VDLookup.LOOKUP[description]
            return version_description.id
        except KeyError:
            raise RuntimeError(
                f"Version Description provided: '{description}', does not have a match in the version lookup"
            )

    @staticmethod
    def validate():
        for key, value in (
            VersionDescriptionConsts().version_description_consts().items()
        ):
            if VDLookup.get_id_from_description(value) is None:
                raise ValueError(
                    f"Version description value {value} for constant {key} does not exist in cruise db."
                )
