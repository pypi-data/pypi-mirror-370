from mb_cruise_migration.framework.consts.file_label_consts import FileLabels
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.models.mb.mb_ngdcid_and_file import MbFile


class FileLabeler(object):
    """
    Labels file using groupings derived from variations in data_file field values
    """

    @classmethod
    def label(cls, files: [MbFile]):
        return [cls.__apply_label(file) for file in files]

    @classmethod
    def __apply_label(cls, file: MbFile):
        parsed_file = file.parsed_file
        if parsed_file.is_survey_metadata():
            file.label = FileLabels.SURVEY_METADATA
            return file
        if parsed_file.has_extraneous():
            file.label = FileLabels.EXTRANEOUS
            return file
        if parsed_file.has_leg():
            file.label = FileLabels.LEG
            return file
        if parsed_file.has_zone():
            file.label = FileLabels.ZONE
            return file
        if parsed_file.has_region():
            file.label = FileLabels.REGION
            return file
        if parsed_file.is_standard():
            file.label = FileLabels.STANDARD
            return file
        MigrationLog.log_no_file_label_error(file)
        raise ValueError(f"no valid file label identified for file {file.data_file} with ngdc_id {file.ngdc_id}")
