import unittest

from mb_cruise_migration.framework.consts.nos_hydro_surveys import NosHydro
from mb_cruise_migration.framework.consts.survey_blacklist import SurveyBlacklist
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.framework.consts.const_initializer import ConstInitializer
from mb_cruise_migration.processors.mb_processor import MbProcessor
from testutils import load_test_mb_data, clean_mb_db


class TestSurveyFiltering(unittest.TestCase):
    MigrationProperties("config_test.yaml")
    MigrationLog()

    def setUp(self) -> None:
        self.tearDown()

    def tearDown(self) -> None:
        clean_mb_db()

    def test_survey_blacklist(self):
        ConstInitializer.initialize_consts()
        test_data_file = "test_blacklist.sql"
        load_test_mb_data(test_data_file)

        mb_processor = MbProcessor()

        mb_cargo = mb_processor.load()
        self.assertEqual(1, len(mb_cargo))

    def test_filter_list_initialization(self):
        blacklist = SurveyBlacklist().BLACKLIST
        nos_hydro = NosHydro().SURVEYS

        assert len(blacklist) == 12
        assert len(nos_hydro) == 290

