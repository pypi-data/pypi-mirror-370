from typing import Callable

from mb_cruise_migration.framework.consts.data_file_consts import PathVersion
from mb_cruise_migration.framework.consts.dataset_type_consts import DatasetTypeConsts
from mb_cruise_migration.framework.consts.error_consts import ErrorConsts
from mb_cruise_migration.framework.consts.file_label_consts import FileLabels
from mb_cruise_migration.models.intermediary.mb_cargo import MbFileCrate
from mb_cruise_migration.utility import common as util
from mb_cruise_migration.utility.dataset import get_dataset_type, get_file_type_of_dataset


class FileDecoder(object):
    """
    Populate crate data required for file validation from parsed data file
    """

    @classmethod
    def decode(cls, mb_file_crates: [MbFileCrate]):
        decoded = [cls.__decode_file(file) for file in mb_file_crates]
        return util.strip_none(decoded)

    @classmethod
    def __decode_file(cls, mb_file_crate: MbFileCrate):
        decoder = cls.__get_decoder(mb_file_crate.mb_file.label)
        return decoder(mb_file_crate)

    @classmethod
    def __get_decoder(cls, label: str) -> Callable:
        if label == FileLabels.STANDARD:
            return cls.__standard
        if label == FileLabels.SURVEY_METADATA:
            return cls.__survey_metadata
        if label == FileLabels.EXTRANEOUS:
            return cls.__extraneous
        if label == FileLabels.LEG:
            return cls.__with_leg
        if label == FileLabels.ZONE:
            return cls.__with_zone
        if label == FileLabels.REGION:
            return cls.__with_region

        raise RuntimeError(ErrorConsts.NO_FILE_DECODER)

    @staticmethod
    def __with_region(mb_file_crate: MbFileCrate):
        raise NotImplementedError(f"Attempted to migrate file without matching file decoder implementation.")

    @staticmethod
    def __with_zone(mb_file_crate: MbFileCrate):
        raise NotImplementedError(f"Attempted to migrate file without matching file decoder implementation.")

    @staticmethod
    def __with_leg(mb_file_crate: MbFileCrate):
        raise NotImplementedError(f"Attempted to migrate file without matching file decoder implementation.")

    @staticmethod
    def __extraneous(mb_file_crate: MbFileCrate):
        raise NotImplementedError(f"Attempted to migrate file without matching file decoder implementation.")

    @staticmethod
    def __survey_metadata(mb_file_crate: MbFileCrate):
        mb_file_crate.non_public = False
        mb_file_crate.dataset_type = DatasetTypeConsts.METADATA
        mb_file_crate.file_type = get_file_type_of_dataset(DatasetTypeConsts.METADATA)

        return mb_file_crate

    @staticmethod
    def __standard(mb_file_crate: MbFileCrate):

        parsed_file = mb_file_crate.mb_file.parsed_file

        is_nonpublic = parsed_file.is_nonpublic()
        version = parsed_file.identify_version_in_path()
        level = PathVersion.get_level(version)
        dataset_type = get_dataset_type(parsed_file, version, is_nonpublic)
        file_type = get_file_type_of_dataset(dataset_type)
        platform_name = parsed_file.identify_platform_in_path()
        platform_type = parsed_file.identify_platform_type_in_path()

        mb_file_crate.non_public = is_nonpublic
        mb_file_crate.level = level
        mb_file_crate.dataset_type = dataset_type
        mb_file_crate.file_type = file_type
        mb_file_crate.platform_name = platform_name
        mb_file_crate.platform_type = platform_type

        return mb_file_crate
