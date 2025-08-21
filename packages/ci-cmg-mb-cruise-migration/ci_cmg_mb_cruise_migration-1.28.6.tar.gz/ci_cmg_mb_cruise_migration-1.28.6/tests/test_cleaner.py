import unittest

from mb_cruise_migration.cleaner import Cleaner
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.migrator import Migrator
from testutils import load_test_mb_data, clean_cruise_db, \
    get_cruise_datasets, get_files, get_access_paths, get_dataset_projects, \
    get_dataset_platforms, get_dataset_instrument, get_dataset_surveys, \
    get_file_access_paths, get_dataset_parameters, get_file_parameters, clean_mb_db


class TestCleaner(unittest.TestCase):
    MigrationProperties("config_test.yaml")

    def setUp(self) -> None:
        self.tearDown()

        test_data_file = "RR1808_lite.sql"
        load_test_mb_data(test_data_file)

        migrator = Migrator("config_test.yaml")
        migrator.migrate()

    def tearDown(self) -> None:
        clean_mb_db()
        clean_cruise_db()

    def test_delete(self):
        datasets = get_cruise_datasets()
        self.assertTrue(len(datasets) > 0)
        files = get_files()
        self.assertTrue(len(files) > 0)
        access_paths = get_access_paths()
        self.assertTrue(len(access_paths) > 0)
        dataset_project_mappings = get_dataset_projects()
        self.assertTrue(len(dataset_project_mappings) > 0)
        dataset_platform_mappings = get_dataset_platforms()
        self.assertTrue(len(dataset_platform_mappings) > 0)
        dataset_instrument_mappings = get_dataset_instrument()
        self.assertTrue(len(dataset_instrument_mappings) > 0)
        dataset_surveys_mappings = get_dataset_surveys()
        self.assertTrue(len(dataset_surveys_mappings) > 0)
        file_access_path_mappings = get_file_access_paths()
        self.assertTrue(len(file_access_path_mappings) > 0)
        dataset_params = get_dataset_parameters()
        self.assertTrue(len(dataset_params) > 0)
        # file_params = get_file_parameters()
        # self.assertTrue(len(file_params) > 0) # file params are being migrated anymore

        cleaner = Cleaner('config_test.yaml')
        cleaner.delete_multibeam_data_from_cruise()

        datasets = get_cruise_datasets()
        self.assertTrue(len(datasets) == 0)
        files = get_files()
        self.assertTrue(len(files) == 0)
        access_paths = get_access_paths()
        self.assertTrue(len(access_paths) == 0)
        dataset_project_mappings = get_dataset_projects()
        self.assertTrue(len(dataset_project_mappings) == 0)
        dataset_platform_mappings = get_dataset_platforms()
        self.assertTrue(len(dataset_platform_mappings) == 0)
        dataset_instrument_mappings = get_dataset_instrument()
        self.assertTrue(len(dataset_instrument_mappings) == 0)
        dataset_surveys_mappings = get_dataset_surveys()
        self.assertTrue(len(dataset_surveys_mappings) == 0)
        file_access_path_mappings = get_file_access_paths()
        self.assertTrue(len(file_access_path_mappings) == 0)
        dataset_params = get_dataset_parameters()
        self.assertTrue(len(dataset_params) == 0)
        file_params = get_file_parameters()
        self.assertTrue(len(file_params) == 0)
