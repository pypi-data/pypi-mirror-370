from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.models.mb.mb_ngdcid_and_file import MbFile
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.utility.common import strip_none


class FileFilter(object):

    @classmethod
    def filter_invalid_files(cls, files: [MbFile]):
        files = [file for file in files if not cls.__is_invalid_file(file)]
        files = strip_none(files)

        return files

    @classmethod
    def filter_files_not_configured_for_migration(cls, files: [MbFile]):
        start_count = len(files)
        files = [file for file in files if cls.__is_being_migrated(file)]
        files = strip_none(files)
        end_count = start_count - len(files)

        return files, end_count

    @classmethod
    def __is_invalid_file(cls, file: MbFile):
        parsed_file = file.parsed_file
        if parsed_file.is_empty():
            MigrationLog.log_skipped_file(file)
            return True
        if parsed_file.is_wcd():
            MigrationLog.log_skipped_file(file)
            return True
        if parsed_file.is_xtf():
            MigrationLog.log_skipped_file(file)
            return True
        if parsed_file.is_singlebeam():
            MigrationLog.log_skipped_file(file)
            return True
        if parsed_file.is_canadian_data():
            MigrationLog.log_skipped_file(file)
            return True

        return False

    @classmethod
    def __is_being_migrated(cls, file: MbFile) -> bool:

        migrate: bool = False
        parsed_file = file.parsed_file
        if parsed_file.is_survey_metadata():
            return cls.__to_filter_or_not_to_filter(file, MigrationProperties.migrate.survey_metadata, "survey_metadata")
        if parsed_file.has_extraneous():
            return cls.__to_filter_or_not_to_filter(file, MigrationProperties.migrate.extraneous, "extraneous")
        if parsed_file.has_leg():
            return cls.__to_filter_or_not_to_filter(file, MigrationProperties.migrate.legs, "legs")
        if parsed_file.has_zone():
            return cls.__to_filter_or_not_to_filter(file, MigrationProperties.migrate.zones, "zone")
        if parsed_file.has_region():
            return cls.__to_filter_or_not_to_filter(file, MigrationProperties.migrate.regions, "region")
        if parsed_file.is_standard():
            return cls.__to_filter_or_not_to_filter(file, MigrationProperties.migrate.standard, "standard")

        MigrationLog.log_no_file_category_error(file)
        return migrate

    @staticmethod
    def __to_filter_or_not_to_filter(file: MbFile, config: bool, category: str):
        if not config:
            MigrationLog.log_filtered_file(file, category)
        return config

