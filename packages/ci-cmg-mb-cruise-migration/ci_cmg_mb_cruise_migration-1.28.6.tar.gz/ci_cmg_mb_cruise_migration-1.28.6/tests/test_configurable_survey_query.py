import unittest

from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.processors.mb_processor import MbProcessor


class TestConfigurableSurveyQuery(unittest.TestCase):

    def tearDown(self) -> None:
        MigrationProperties.SURVEY_QUERY = None

    def test_false_configuration(self):
        MigrationProperties("config_test.yaml")
        MbProcessor()
        self.assertEqual(False, MigrationProperties.manifest.use_list)
        self.assertEqual("SELECT * FROM MB.SURVEY", MigrationProperties.get_survey_query())

    def test_true_configuration(self):
        MigrationProperties("config_test.yaml")
        MbProcessor()
        MigrationProperties.manifest.use_list = True
        MbProcessor.set_survey_query()
        self.assertEqual("SELECT * FROM MB.SURVEY WHERE SURVEY_NAME='RR1808' OR SURVEY_NAME='H11075' OR SURVEY_NAME='test'", MigrationProperties.get_survey_query())

