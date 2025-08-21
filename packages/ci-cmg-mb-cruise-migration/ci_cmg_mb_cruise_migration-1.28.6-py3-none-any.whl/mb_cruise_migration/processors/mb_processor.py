from typing import Optional

from mb_cruise_migration.framework.consts.error_consts import ErrorConsts
from mb_cruise_migration.framework.file_filter import FileFilter
from mb_cruise_migration.framework.file_labeler import FileLabeler
from mb_cruise_migration.framework.file_validator import FileValidator
from mb_cruise_migration.framework.paginator import Paginator
from mb_cruise_migration.framework.survey_filter import SurveyFilter
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.logging.migration_report import MigrationReport
from mb_cruise_migration.models.intermediary.mb_cargo import MbSurveyCrate, MbFileCrate, MbCargo
from mb_cruise_migration.models.mb.mb_ngdcid_and_file import MbFile
from mb_cruise_migration.framework.file_decoder import FileDecoder
from mb_cruise_migration.services.mb_service import MbService
from mb_cruise_migration.models.mb.mb_survey import MbSurvey
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.utility.common import strip_none


class MbProcessor(object):
    def __init__(self):
        self.set_survey_query()
        self.mb_service = MbService()
        self.survey_pagesize = MigrationProperties.mb_db_config.pagesize
        self.survey_paginator = self.__init_survey_paginator()

    def __init_survey_paginator(self):
        number_of_surveys = self.mb_service.get_survey_count(MigrationProperties.SURVEY_QUERY)
        return Paginator(self.survey_pagesize, number_of_surveys)

    def keep_alive(self):
        query = self.mb_service.query_builder.select_all("SURVEY")
        self.mb_service.db.query(query)

    def surveys_exhausted(self):
        return self.survey_paginator.done()

    def load(self) -> Optional[list[MbCargo]]:
        if not self.surveys_exhausted():
            skip, pagesize = self.survey_paginator.paginate()

            paged_surveys = self.mb_service.get_survey_page(skip, pagesize)
            MigrationLog.log_paged_surveys(paged_surveys)
            MigrationReport.add_paged_surveys(paged_surveys)
            filtered_surveys = SurveyFilter.filter(paged_surveys)

            surveys = strip_none([self.build_cargo(survey) for survey in filtered_surveys])

            if not surveys:
                return self.load()

            return surveys
        else:
            return None

    def build_cargo(self, survey: MbSurvey) -> Optional[MbCargo]:
        MigrationLog.log_tracking(f"Collecting related tables for survey being migrated: {survey.survey_name}")
        survey_reference = self.mb_service.get_survey_reference(survey.ngdc_id)
        survey_shape = self.get_survey_shape(survey)
        survey_crate = MbSurveyCrate(survey, survey_reference, survey_shape)

        files = self.mb_service.get_survey_files(survey.ngdc_id)
        if not files:
            self.__skip_survey(survey.survey_name, "no associated files found for survey in mb schema.")
            return None

        files = FileFilter.filter_invalid_files(files)
        files, files_filtered = FileFilter.filter_files_not_configured_for_migration(files)
        if files_filtered > 0:  # cancel survey migration if any files are filtered.
            self.__skip_survey(survey.survey_name, f"at least {files_filtered} files were filtered, causing the survey to be skipped.")
            return None

        files = FileLabeler.label(files)
        file_crates = [self.build_file_crate(file) for file in files]
        file_crates = FileDecoder.decode(file_crates)

        file_crates_validated, files_invalidated = FileValidator.validate(file_crates, survey.instrument)

        # cancel survey migration if any files are filtered.
        if files_invalidated > 0 or not file_crates_validated or len(file_crates_validated) < len(file_crates):
            self.__skip_survey(survey.survey_name, f"at least {files_invalidated} files were invalidated for migration. Check file logs for reasons why files were skipped.")
            return None

        MigrationLog.log_tracking(f"Collection of related objects for survey {survey.survey_name} successfully completed")
        return MbCargo(survey_crate, file_crates)

    def build_file_crate(self, mb_file: MbFile):
        file_shape = self.get_file_shape(mb_file)
        mb_info = self.mb_service.get_mb_info(mb_file.data_file)

        return MbFileCrate(
            mb_file,
            mb_info,
            file_shape
            )

    def get_survey_shape(self, survey: MbSurvey):
        return self.mb_service.get_survey_shape(survey.ngdc_id) if MigrationProperties.run_parameters.migrate_shapes else None

    def get_file_shape(self, mb_file: MbFile):
        return self.mb_service.get_file_shape(mb_file.data_file) if MigrationProperties.run_parameters.migrate_shapes else None

    @staticmethod
    def set_survey_query():
        if MigrationProperties.manifest.use_list:
            surveys = MigrationProperties.manifest.target_migration_surveys
            if not surveys:
                raise ValueError(ErrorConsts.NO_TARGET_SURVEYS)
            print(type(surveys))
            where_conditions = f"SURVEY_NAME='{surveys.pop(0)}'"
            if surveys:
                for survey in surveys:
                    where_conditions += f" OR SURVEY_NAME='{survey}'"

            MigrationProperties.SURVEY_QUERY = f"SELECT * FROM MB.SURVEY WHERE {where_conditions}"
        else:
            MigrationProperties.SURVEY_QUERY = MigrationProperties.manifest.default_query

    @staticmethod
    def __skip_survey(survey_name: str, message):
        MigrationLog.log_skipped_survey(survey_name, message)
        MigrationReport.add_skipped_survey(survey_name, message)
