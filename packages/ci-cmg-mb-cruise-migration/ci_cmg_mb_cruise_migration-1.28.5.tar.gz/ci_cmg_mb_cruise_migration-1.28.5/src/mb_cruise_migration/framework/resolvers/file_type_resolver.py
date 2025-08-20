from typing import Optional

from mb_cruise_migration.framework.consts.dataset_type_consts import DatasetTypeConsts
from mb_cruise_migration.framework.consts.file_type_consts import FileTypeConsts
from mb_cruise_migration.models.cruise.cruise_file_types import CruiseFileType


class FTLookup(object):
    LOOKUP = {}

    @staticmethod
    def set_lookup(file_types: [CruiseFileType]):
        for file_type in file_types:
            FTLookup.LOOKUP.update({file_type.type_name: file_type.id})

    @staticmethod
    def get_id(file_type: str) -> Optional[int]:
        try:
            return FTLookup.LOOKUP[file_type]
        except KeyError:
            return None

    @staticmethod
    def validate():
        for key, value in FileTypeConsts().file_type_consts().items():
            if FTLookup.get_id(value) is None:
                raise ValueError(
                    f"File type value {value} for constant {key} does not exist in cruise db."
                )
