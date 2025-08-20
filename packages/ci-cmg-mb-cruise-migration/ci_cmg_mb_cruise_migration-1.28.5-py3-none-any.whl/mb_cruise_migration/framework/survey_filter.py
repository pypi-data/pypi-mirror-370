from mb_cruise_migration.framework.consts.nos_hydro_surveys import NosHydro
from mb_cruise_migration.framework.consts.survey_blacklist import SurveyBlacklist
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.logging.migration_report import MigrationReport
from mb_cruise_migration.models.mb.mb_survey import MbSurvey


class SurveyFilter(object):
    @classmethod
    def filter(cls, surveys: [MbSurvey]):
        return [survey for survey in surveys if not cls.__catch_survey(survey)]

    @classmethod
    def __catch_survey(cls, survey: MbSurvey) -> bool:

        is_blacklisted = survey.survey_name in SurveyBlacklist().BLACKLIST
        if is_blacklisted:
            skip_reason = "survey was blacklisted for this migration run."
            MigrationReport.add_skipped_survey(survey.survey_name, skip_reason)
            MigrationLog.log_skipped_survey(survey.survey_name, skip_reason)
            return is_blacklisted

        is_nos_hydro = survey.survey_name in NosHydro().SURVEYS
        if is_nos_hydro:
            skip_reason = "survey was an NOS Hydro survey that will not be migrated."
            MigrationReport.add_skipped_survey(survey.survey_name, skip_reason)
            MigrationLog.log_skipped_survey(survey.survey_name, skip_reason)
            return is_nos_hydro
        return False
