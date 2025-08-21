from typing import Optional

from mb_cruise_migration.framework.consts.dataset_type_consts import DatasetTypeConsts
from mb_cruise_migration.models.cruise.cruise_dataset_types import CruiseDatasetType


class DTLookup(object):
    LOOKUP = {}

    @staticmethod
    def set_lookup(dataset_types: [CruiseDatasetType]):
        for dataset_type in dataset_types:
            DTLookup.LOOKUP.update({dataset_type.type_name: dataset_type.id})

    @staticmethod
    def get_id(dataset_type: str) -> Optional[int]:
        try:
            return DTLookup.LOOKUP[dataset_type]
        except KeyError:
            return None

    @staticmethod
    def validate():
        for key, value in DatasetTypeConsts().dataset_type_consts().items():
            if DTLookup.get_id(value) is None:
                raise ValueError(
                    f"Dataset type value {value} for constant {key} does not exist in cruise db."
                )
