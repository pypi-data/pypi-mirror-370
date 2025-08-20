from typing import Optional, Callable

from mb_cruise_migration.framework.consts.dataset_type_consts import DatasetTypeConsts
from mb_cruise_migration.framework.consts.error_consts import ErrorConsts
from mb_cruise_migration.framework.consts.file_label_consts import FileLabels
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.models.intermediary.mb_cargo import MbFileCrate
from mb_cruise_migration.utility.common import strip_none, multiple_values_in_survey_instrument


class FileValidator(object):
    """
    Remove files with known issues from migration
    """

    @classmethod
    def validate(cls, files: [MbFileCrate], survey_instrument: Optional[str]):
        start_count = len(files)
        files = [cls.__file_check(file, survey_instrument) for file in files]
        files = strip_none(files)
        files_removed = start_count - len(files)

        return files, files_removed

    @classmethod
    def __file_check(cls, file: MbFileCrate, survey_instrument: Optional[str]):
        validator = cls.__get_validator(file.mb_file.label)
        return validator(file, survey_instrument)

    @classmethod
    def __get_validator(cls, label: str) -> Callable:
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

        raise RuntimeError(ErrorConsts.NO_MATCHING_LABEL)

    @classmethod
    def __standard(cls, file: MbFileCrate, survey_instrument: Optional[str]):
        parsed_file = file.mb_file.parsed_file

        if DatasetTypeConsts.dataset_has_associated_instrument(file.dataset_type):
            if not parsed_file.has_instrument():
                if survey_instrument is None:
                    reason = "no instrument in data_file path and no survey instrument"
                    MigrationLog.log_invalidated_file(file, reason)
                    return None
                if multiple_values_in_survey_instrument(survey_instrument):
                    reason = "no instrument in data_file path and multiple instruments found for survey"
                    MigrationLog.log_invalidated_file(file, reason)
                    return None

        return file

    @classmethod
    def __survey_metadata(cls, file: MbFileCrate, survey_instrument: Optional[str]):
        return file  # no validation required.

    @classmethod
    def __extraneous(cls, file: MbFileCrate, survey_instrument: Optional[str]):
        raise NotImplementedError(ErrorConsts.NO_FILE_VALIDATOR)

    @classmethod
    def __with_leg(cls, file: MbFileCrate, survey_instrument: Optional[str]):
        raise NotImplementedError(ErrorConsts.NO_FILE_VALIDATOR)

    @classmethod
    def __with_zone(cls, file: MbFileCrate, survey_instrument: Optional[str]):
        raise NotImplementedError(ErrorConsts.NO_FILE_VALIDATOR)

    @classmethod
    def __with_region(cls, file: MbFileCrate, survey_instrument: Optional[str]):
        raise NotImplementedError(ErrorConsts.NO_FILE_VALIDATOR)
