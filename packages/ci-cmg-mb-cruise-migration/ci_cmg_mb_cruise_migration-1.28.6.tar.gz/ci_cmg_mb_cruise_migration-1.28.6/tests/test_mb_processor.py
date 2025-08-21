import unittest

from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.models.intermediary.mb_cargo import MbCargo, MbSurveyCrate, MbFileCrate
from mb_cruise_migration.processors.mb_processor import MbProcessor
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.services.mb_service import MbService
from mb_cruise_migration.models.mb.mb_ngdcid_and_file import MbFile
from mb_cruise_migration.models.mb.mb_mbinfo_file_tsql import MbInfo
from testutils import clean_mb_db, load_test_mb_data


class TestMbIntegration(unittest.TestCase):
    test_data_file = "RR1808_lite.sql"

    def setUp(self) -> None:
        MigrationProperties("config_test.yaml")  # load app configuration from file
        MigrationLog()
        load_test_mb_data(self.test_data_file)

    def tearDown(self) -> None:
        clean_mb_db()

    def test_mb_processor(self):

        retriever = MbProcessor()
        dockets = retriever.load()

        self.assertTrue(len(dockets) == 1)
        self.assertIsInstance(dockets[0], MbCargo)
        self.assertIsInstance(dockets[0].mb_survey_crate, MbSurveyCrate)
        self.assertEqual(8, len(dockets[0].related_mb_file_crates))

        mb_files = []
        mb_infos = []
        for crate in dockets[0].related_mb_file_crates:
            self.assertIsInstance(crate, MbFileCrate)
            mb_file = crate.mb_file
            self.assertIsInstance(mb_file, MbFile)
            mb_files.append(mb_file)
            mb_info = crate.mb_info
            if mb_info:
                self.assertIsInstance(mb_info, MbInfo)
                mb_infos.append(mb_info)

        self.assertEqual(8, len(mb_files))
        self.assertEqual(2, len(mb_infos))

    def test_list_select(self):
        MigrationProperties.SURVEY_QUERY = None
        MigrationProperties.manifest.use_list = True
        MigrationLog()

        try:
            retriever = MbProcessor()
            dockets = retriever.load()
        except Exception as e:
            self.fail(f"Error was thrown: {str(e)}")


if __name__ == '__main__':
    unittest.main()
