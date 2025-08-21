import logging
import os

from mb_cruise_migration.logging.migration_logger import LoggerBuilder
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.models.intermediary.cruise_cargo import CruiseCargo
from mb_cruise_migration.models.intermediary.mb_cargo import MbSurveyCrate
from mb_cruise_migration.models.mb.mb_survey import MbSurvey


class FailedSurvey(object):
    def __init__(self, survey, error):
        self.survey_name = survey
        self.error_message = error


class ProblemSurvey(object):
    def __init__(self, survey, message):
        self.survey_name = survey
        self.message = message


class SkippedSurvey(object):
    def __init__(self, survey, reason):
        self.survey_name = survey
        self.reason = reason


class MigrationReport(object):
    report: logging.Logger = None
    success: logging.Logger = None
    skipped: logging.Logger = None
    problem: logging.Logger = None

    start = None
    end = None
    is_success = True
    failure_message = None

    paged_surveys: [str] = []
    migrated_surveys: [str] = []
    problem_surveys: [ProblemSurvey] = []
    skipped_surveys: [SkippedSurvey] = []
    failed_surveys: [FailedSurvey] = []
    failed_dataset_shapes: [str] = []
    failed_file_shape_surveys: set[str] = set()

    total_migrated_datasets = 0
    total_migrated_files = 0
    total_instrument_review_files = 0

    def __init__(self):
        self.__pre_check()
        self.__initialize_report()
        self.__initialize_success()
        self.__initialize_skipped()
        self.__initialize_problem()

    def __initialize_report(self):
        keyword = "migration_report"

        level = MigrationProperties.log_config.level
        handler = self.__get_report_handler(keyword, "")
        formatter = self.__get_report_formatter()

        builder = LoggerBuilder(keyword, level, handler, formatter)
        MigrationReport.report = builder.get_logger()

    def __initialize_success(self):
        keyword = "completed_surveys"

        level = MigrationProperties.log_config.level
        handler = self.__get_report_handler(keyword, "success")
        formatter = self.__get_report_formatter()

        builder = LoggerBuilder(keyword, level, handler, formatter)
        MigrationReport.success = builder.get_logger()

    def __initialize_skipped(self):
        keyword = "skipped_surveys"

        level = MigrationProperties.log_config.level
        handler = self.__get_report_handler(keyword, "skipped")
        formatter = self.__get_report_formatter()

        builder = LoggerBuilder(keyword, level, handler, formatter)
        MigrationReport.skipped = builder.get_logger()

    def __initialize_problem(self):
        keyword = "problem_surveys"

        level = MigrationProperties.log_config.level
        handler = self.__get_report_handler(keyword, "problem")
        formatter = self.__get_report_formatter()

        builder = LoggerBuilder(keyword, level, handler, formatter)
        MigrationReport.problem = builder.get_logger()

    @staticmethod
    def __pre_check():
        if not MigrationProperties.log_config:
            raise RuntimeError("Properties must be loaded prior to creating a logger")

    @staticmethod
    def __get_report_handler(keyword, subdir):
        log_dir = os.path.join("report", subdir)
        log_path = LoggerBuilder.create_log_file_path(log_dir, keyword)

        return logging.FileHandler(log_path, 'w')

    @staticmethod
    def __get_report_formatter():
        return logging.Formatter('%(message)s')

    @staticmethod
    def add_migrated_dataset(cargo: CruiseCargo):
        MigrationReport.total_migrated_datasets += 1
        num_files = len(cargo.related_file_crates)
        MigrationReport.total_migrated_files += num_files

    @staticmethod
    def add_failed_dataset_shape_migration(dataset_name):
        MigrationReport.failed_dataset_shapes.append(dataset_name)

    @staticmethod
    def add_migrated_survey(survey_name: str, problem_flag: bool, problem_message: str):
        if problem_flag:
            MigrationReport.add_problem_survey(survey_name, problem_message)
        else:
            MigrationReport.migrated_surveys.append(survey_name)

    @staticmethod
    def add_problem_survey(survey_name: str, message: str):
        MigrationReport.problem_surveys.append(ProblemSurvey(survey_name, message))

    @staticmethod
    def add_skipped_survey(survey_name: str, reason: str):
        MigrationReport.skipped_surveys.append(SkippedSurvey(survey_name, reason))

    @staticmethod
    def add_failed_survey(survey_crate: MbSurveyCrate, exception):
        message = f"Failed to identify issue with survey {survey_crate.mb_survey.survey_name}. Survey migration was cancelled due to thrown error."
        try:
            message = str(exception)
        except UnicodeDecodeError:
            print("Failed to decode exception message.")

        MigrationReport.failed_surveys.append(FailedSurvey(survey_crate.mb_survey.survey_name, message))

    @staticmethod
    def add_failed_file_shape_migration_survey(survey_name: str):
        MigrationReport.failed_file_shape_surveys.update({survey_name})

    @staticmethod
    def increment_review_files_total():
        MigrationReport.total_instrument_review_files += 1

    @staticmethod
    def migration_final_report():
        logger = MigrationReport.report
        total_migrated_surveys = len(MigrationReport.migrated_surveys)
        total_failed_surveys = len(MigrationReport.failed_surveys)
        total_skipped_surveys = len(MigrationReport.skipped_surveys)
        total_problem_surveys = len(MigrationReport.problem_surveys)
        total_time = (MigrationReport.end - MigrationReport.start).total_seconds() / 60

        logger.info(f"MIGRATION COMPLETED {'SUCCESSFULLY' if MigrationReport.is_success else 'UNSUCCESSFULLY'}")
        if not MigrationReport.is_success:
            logger.info(f"\n{MigrationReport.failure_message}\n")
        logger.info(f'Elapsed time in minutes: {total_time}')
        logger.info(f"\r")

        logger.info(f'SUMMARY')
        logger.info(f"\tmigrated surveys: {total_migrated_surveys}")
        logger.info(f"\tfailed surveys: {total_failed_surveys}")
        logger.info(f"\tskipped surveys: {total_skipped_surveys}")
        logger.info(f"\tproblem surveys: {total_problem_surveys}")
        logger.info(f"\r")
        logger.info(f"\tmigrated datasets: {MigrationReport.total_migrated_datasets}")
        logger.info(f"\tmigrated files: {MigrationReport.total_migrated_files}")
        logger.info(f"\r")
        logger.info(f"\tfailed dataset shape migrations: {MigrationReport.failed_dataset_shapes}")
        try:
            reviewable_percent = int((MigrationReport.total_instrument_review_files / MigrationReport.total_migrated_files) * 100)
            logger.info(f"\tfiles requiring instrument review: {MigrationReport.total_instrument_review_files} -- {reviewable_percent}% of total files")
        except ZeroDivisionError:
            logger.info("No files were migrated.")
        logger.info(f"\r")
        print("MIGRATION COMPLETED: Elapsed time: ", total_time)

    @staticmethod
    def migration_successful_surveys_report():
        logger = MigrationReport.success

        logger.info(f"Migrated surveys (no problems flagged):")
        migrated_surveys = MigrationReport.get_successful_surveys_without_problems()
        for survey in migrated_surveys:
            logger.info(f"\t{survey}")

    @staticmethod
    def migration_skipped_surveys_report():
        logger = MigrationReport.skipped
        logger.info(f"Skipped surveys:")
        for survey in MigrationReport.skipped_surveys:
            logger.info(f"\t{survey.survey_name} -- {survey.reason}")

    @classmethod
    def migration_problem_surveys_report(cls):
        logger = MigrationReport.problem

        logger.info(f"Surveys that were paged but not accounted for in either successful, skipped, problem, or failed surveys:")
        for survey in cls.identify_missing_paged_surveys():
            logger.info(f"\t{survey}")
            logger.info(f"\r")

        logger.info(f"Problem surveys (surveys flagged for review during migration):")
        for survey in MigrationReport.problem_surveys:
            logger.info(f"\t{survey.survey_name} -- {survey.message}")
        logger.info(f"\r")

        logger.info(f"Failed surveys (migration was attempted, but an error occurred):")
        for survey in MigrationReport.failed_surveys:
            logger.info(f"\t{survey.survey_name};\r\t\t{survey.error_message}\r")

    @classmethod
    def identify_missing_paged_surveys(cls):
        surveys_missing = list(
            set(cls.paged_surveys) -
            set([survey.survey_name for survey in cls.problem_surveys]) -
            set([survey.survey_name for survey in cls.failed_surveys]) -
            set(cls.migrated_surveys) -
            set([survey.survey_name for survey in cls.skipped_surveys])
        )
        return surveys_missing

    @staticmethod
    def get_successful_surveys_without_problems():
        successful = MigrationReport.migrated_surveys
        problems = MigrationReport.problem_surveys
        problems = [problem.survey_name for problem in problems]
        if problems and successful:
            successful = [survey for survey in successful if survey not in problems]

        return successful

    @classmethod
    def add_paged_surveys(cls, surveys: [MbSurvey]):
        survey_names = [survey.survey_name for survey in surveys]
        cls.paged_surveys.extend(survey_names)
