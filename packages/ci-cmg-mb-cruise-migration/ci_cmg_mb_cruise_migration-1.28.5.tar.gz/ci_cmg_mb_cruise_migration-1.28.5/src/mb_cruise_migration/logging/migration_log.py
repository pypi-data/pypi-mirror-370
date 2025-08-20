import datetime
import logging
from logging.handlers import RotatingFileHandler

from mb_cruise_migration.framework.consts.log_level_consts import LogLevels
from mb_cruise_migration.logging.batch_error import BatchError
from mb_cruise_migration.logging.migration_logger import LoggerBuilder
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.models.cruise.cruise_files import CruiseFile
from mb_cruise_migration.models.intermediary.cruise_cargo import CruiseCargo, CruiseSurveyCrate
from mb_cruise_migration.models.intermediary.mb_cargo import MbFileCrate
from mb_cruise_migration.models.intermediary.migrating_survey import MigratingSurvey
from mb_cruise_migration.models.mb.mb_ngdcid_and_file import MbFile
from mb_cruise_migration.models.mb.mb_survey import MbSurvey


class LogConsts(object):
    START = "START"
    END = "END"
    SKIP = "SKIP"
    BEGIN = "BEGIN"
    DONE = "DONE"
    REVIEW = "REVIEW"
    ERROR = "ERROR"
    TRACKING = "TRACKING"
    CONST = "CONST"


class MigrationLog(object):
    log: logging.Logger = None
    review: logging.Logger = None

    def __init__(self):
        self.__pre_check()
        self.__initialize_log()
        self.__initialize_review()

    def __initialize_log(self):
        keyword = "migration"
        directory = "log"

        level = MigrationProperties.log_config.level
        log_size_mb = MigrationProperties.log_config.log_size_mb
        handler = self. __get_log_handler(log_size_mb, keyword, directory)
        formatter = self.__get_log_formatter()

        builder = LoggerBuilder(keyword, level, handler, formatter)
        MigrationLog.log = builder.get_logger()

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        MigrationLog.log.addHandler(console_handler)

        self.__validate_level(MigrationLog.log, level)

    def __initialize_review(self):
        keyword = "audit"
        directory = "audit"

        level = MigrationProperties.log_config.level
        log_size_mb = MigrationProperties.log_config.log_size_mb
        handler = self.__get_log_handler(log_size_mb, keyword, directory)
        formatter = self.__get_log_formatter()

        builder = LoggerBuilder(keyword, level, handler, formatter)
        MigrationLog.review = builder.get_logger()

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        MigrationLog.review.addHandler(console_handler)

        self.__validate_level(MigrationLog.review, level)

    @staticmethod
    def __pre_check():
        if not MigrationProperties.log_config:
            raise RuntimeError("Properties must be loaded prior to creating a logger")

    @staticmethod
    def __get_log_handler(log_size_mb, keyword, log_dir):
        log_path = LoggerBuilder.create_log_file_path(log_dir, keyword)
        log_size = int(log_size_mb)*1024*1024  # 10MB
        return logging.handlers.RotatingFileHandler(log_path, maxBytes=log_size, backupCount=10)

    @staticmethod
    def __get_log_formatter():
        return logging.Formatter('%(asctime)s %(levelname)-7s %(message)s', '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def __validate_level(logger, level):
        if level == LogLevels.INFO:
            logger.info(f"Logger initialized at level {LogLevels.INFO}.")
            return
        if level == LogLevels.WARNING:
            logger.info(f"Logger initialized at level {LogLevels.WARNING}.")
            return
        if level == LogLevels.CRITICAL:
            logger.info(f"Logger initialized at level {LogLevels.CRITICAL}.")
            return
        if level == LogLevels.DEBUG:
            logger.info(f"Logger initialized at level {LogLevels.DEBUG}.")
            return
        logger.info("Provided log level unrecognized. Logger defaulting to DEBUG level logging.")

    @staticmethod
    def log_start():
        MigrationLog.log.info(f"{LogConsts.START} -- Migration start at {datetime.datetime.now()}")
        MigrationLog.log.info(f"")

    @staticmethod
    def log_end():
        MigrationLog.log.info(f"{LogConsts.END} -- Migration end at {datetime.datetime.now()}")

    @staticmethod
    def log_skipped_file(file: MbFile):
        MigrationLog.log.debug(f"{LogConsts.SKIP} -- File: skipping migration of file {file.data_file} with ngdc_id {file.ngdc_id}")

    @staticmethod
    def log_filtered_file(file: MbFile, category: str):
        MigrationLog.log.debug(f"{LogConsts.SKIP} -- File: removing file {file.data_file} with ngdc_id {file.ngdc_id} from migration: not configured to migrate files in category {category}")

    @staticmethod
    def log_invalidated_file(file: MbFileCrate, reason: str):
        filename = file.mb_file.data_file
        MigrationLog.review.warning(f"{LogConsts.REVIEW} -- File migration skipped for {filename} due to: \n {reason}")

    @staticmethod
    def log_file_for_manual_review(mb_file_crate: MbFileCrate, instrument: str):
        file = mb_file_crate.mb_file.data_file

        MigrationLog.review.info(f"{LogConsts.REVIEW} -- File Instrument: {instrument} derived from mb.survey.instrument for file {file}")

    @staticmethod
    def log_failed_file_migration(survey_name: str, file: CruiseFile, e: Exception):
        message = "Failed to identify issue with file migration. File migration was skipped due to thrown error."
        try:
            message = str(e)
        except UnicodeDecodeError:
            print("Failed to decode exception message.")
        MigrationLog.log.error(f"{LogConsts.ERROR} -- File Insertion: file in survey {survey_name} with name {file.file_name} failed to migrate with error message: \r {message}")

    @staticmethod
    def log_dataset_start(cargo: CruiseCargo):
        dataset_name = cargo.dataset_crate.dataset.dataset_name
        num_files = len(cargo.related_file_crates)
        MigrationLog.log.info(f"{LogConsts.BEGIN} -- Dataset Migration: start migration of dataset {dataset_name} and its {num_files} associated files")

    @staticmethod
    def log_migrated_dataset(cargo: CruiseCargo, actual_files, expected_files):
        dataset_name = cargo.dataset_crate.dataset.dataset_name
        survey_name = cargo.related_survey_crate.cruise_survey.survey_name

        if actual_files < expected_files:
            MigrationLog.log.warning(f"{LogConsts.REVIEW} -- Dataset Migrated with problems: Survey: {survey_name}; {actual_files} files migrated out of {expected_files}")
        else:
            MigrationLog.log.info(f"{LogConsts.DONE} -- Dataset Migrated: {dataset_name};  Survey: {survey_name};  Number of migrated files: {actual_files}")

    @staticmethod
    def log_failed_dataset(message):
        MigrationLog.log.error(f"{LogConsts.ERROR} -- Dataset Migration Failed: {message}")

    @staticmethod
    def log_survey_start(survey_crate: CruiseSurveyCrate):
        survey_name = survey_crate.cruise_survey.survey_name
        MigrationLog.log.info(f"{LogConsts.BEGIN} -- Survey Migration was started: {survey_name}")

    @staticmethod
    def log_migrated_survey(survey: MigratingSurvey, problem_flag: bool, problem_message: str):
        survey_name = survey.survey_name
        num_datasets = survey.migrated_datasets
        num_actual_files = survey.migrated_files
        num_expected_files = survey.expected_files
        if num_actual_files < num_expected_files:
            problem_flag = True
            problem_message = f"Only {num_actual_files} files of {num_expected_files} migrated successfully;" + problem_message
        if problem_flag:
            MigrationLog.log_problem_survey(survey_name, problem_message)
        else:
            MigrationLog.log.info(f"{LogConsts.DONE} -- Survey Migration: {survey_name};  Number of migrated datasets: {num_datasets};  Number of migrated files: {num_actual_files}")

    @staticmethod
    def log_skipped_survey(survey_name: str, reason: str):
        MigrationLog.log.info(f"{LogConsts.SKIP} -- Survey: skipping migration of survey {survey_name} because {reason}.")

    @staticmethod
    def log_problem_survey(survey_name: str, message: str):
        MigrationLog.log.warning(f"{LogConsts.REVIEW} -- Problem Survey: problems identified with {survey_name} with message: {message}")

    @staticmethod
    def log_failed_survey(survey_name: str, e):
        message = f"Failed to identify issue with survey {survey_name}. Survey migration was cancelled due to thrown error."
        try:
            message = str(e)
        except UnicodeDecodeError:
            print("Failed to decode exception message.")

        MigrationLog.log.error(f"{LogConsts.ERROR} -- Survey: survey {survey_name} failed to migrate with message:\n {message}")

    @staticmethod
    def log_batch_insert_errors(errors: [BatchError], batch_data, context_message):
        for error in errors:
            try:
                data = batch_data[error.offset]
                MigrationLog.log.error(f"{LogConsts.ERROR} -- Batch Insert: Error received during {context_message} batch insert of {data}: {error.error}")
            except IndexError:
                MigrationLog.log.error(f"{LogConsts.ERROR} -- Batch Insert: Error received during {context_message} batch insert at offset {error.offset}: {error.error}")

    @staticmethod
    def log_database_error(message: str, exception: Exception):
        try:
            exception_message = str(exception)
            MigrationLog.log.error(f"{LogConsts.ERROR} -- Database Error: {message} with exception: {exception_message}")
        except UnicodeDecodeError:
            print("Failed to decode exception message.")
            MigrationLog.log.error(f"{LogConsts.ERROR} -- Database Error: {message}")

    @staticmethod
    def log_cruise_processor_unhandled_error(cruise_cargo: [CruiseCargo], error_message):
        datasets = []
        for cargo in cruise_cargo:
            datasets.append(cargo.dataset_crate.dataset.dataset_name)
        MigrationLog.log.error(f"{LogConsts.ERROR} -- Error occurred during dataset insertion. Potentially affected datasets include {datasets}. ERROR: {error_message}")

    @staticmethod
    def log_mb_survey_query(query):
        MigrationLog.log.debug(f"{LogConsts.TRACKING} -- Querying MB.SURVEY for next batch of surveys: \n\t\t{query}")

    @staticmethod
    def log_exception(exception):
        MigrationLog.log.exception(exception)

    @staticmethod
    def log_no_raw_processed_product(survey):
        MigrationLog.log.warning(f"{LogConsts.SKIP} -- Survey: No raw, processed, or product dataset found for survey {survey}. Survey will not be migrated.")

    @staticmethod
    def log_no_file_label_error(mb_file: MbFile):
        MigrationLog.log.error(f"{LogConsts.ERROR} -- no valid file label identified for file {mb_file.data_file} with ngdc_id {mb_file.ngdc_id}")

    @staticmethod
    def log_no_file_category_error(mb_file: MbFile):
        MigrationLog.log.error(f"{LogConsts.ERROR} -- File: no valid file category identified for file {mb_file.data_file} with ngdc_id {mb_file.ngdc_id}. Survey will be skipped.")

    @staticmethod
    def log_paged_surveys(surveys: [MbSurvey]):
        survey_names = [survey.survey_name for survey in surveys]
        MigrationLog.log.debug(f"{LogConsts.TRACKING} -- Surveys paged: " + ", ".join(survey_names))

    @classmethod
    def log_error(cls, message):
        MigrationLog.log.error(f"{LogConsts.ERROR} -- {message}")

    @classmethod
    def log_tracking(cls, message):
        MigrationLog.log.debug(f"{LogConsts.TRACKING} -- {message}")

    @classmethod
    def log_const_update(cls, message):
        MigrationLog.log.warning(f"{LogConsts.CONST} -- {message}")
