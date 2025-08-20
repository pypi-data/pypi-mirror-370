import unittest

from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.models.intermediary.mb_cargo import MbCargo
from mb_cruise_migration.framework.consts.const_initializer import ConstInitializer
from mb_cruise_migration.processors.transfer_station import TransferStation


class TestSurveyMetadataMapping(unittest.TestCase):

    @unittest.skip("TODO")
    def test_survey_iso_metadata(self):
        MigrationProperties("config_test.yaml")

        # PREP DB
        ConstInitializer.initialize_consts()

        # SETUP MB TEST OBJECTS
        mb_survey_crate = self._create_sm_test_mb_survey_crate()
        mb_file_crates = self._create_sm_test_mb_file_crates()

        mb_crate = MbCargo(file_crates=mb_file_crates, survey_crate=mb_survey_crate)
        station = TransferStation(mb_crate)

        # TEST
        cruise_cargo = station.transfer()

        #  TODO assertions

    def _create_sm_test_mb_survey_crate(self):
        pass

    def _create_sm_test_mb_file_crates(self):
        pass
