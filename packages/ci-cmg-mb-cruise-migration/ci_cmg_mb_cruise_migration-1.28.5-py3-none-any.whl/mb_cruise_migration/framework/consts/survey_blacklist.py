from mb_cruise_migration.migration_properties import MigrationProperties


class SurveyBlacklist(object):
    BLACKLIST = []

    def __init__(self):
        SurveyBlacklist.BLACKLIST = MigrationProperties.manifest.survey_blacklist
