import unittest

from mb_cruise_migration.db.cruise_db import CruiseDb
from mb_cruise_migration.framework.resolvers.platform_designator_resolver import DesignatorLookup
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.models.cruise.cruise_platforms import CruisePlatform
from mb_cruise_migration.framework.consts.const_initializer import ConstInitializer
from mb_cruise_migration.services.cruise_service import PlatformService
from mb_cruise_migration.migration_properties import MigrationProperties


class TestDesignatorResolver(unittest.TestCase):
    MigrationProperties("config_test.yaml")
    MigrationLog()

    def tearDown(self):
        self.clean_db(CruiseDb().db)

    def test_designator_retrieval(self):
        platform_service = PlatformService(CruiseDb())

        # prep db
        platform_service.get_new_or_existing_platform(
            CruisePlatform(
                internal_name="celtic_voyager",
                platform_type="ship",
                docucomp_uuid=None,
                long_name="Celtic Voyager",
                designator="CV",
                platform_name="Celtic Voyager EtC"
            )
        )
        platform_service.get_new_or_existing_platform(
            CruisePlatform(
                internal_name="fugro_americas",
                platform_type="ship",
                docucomp_uuid=None,
                long_name="Fugro Americas",
                designator="FA",
                platform_name=None
            )
        )
        platform_service.get_new_or_existing_platform(
            CruisePlatform(
                internal_name="melville",
                platform_type="ship",
                docucomp_uuid=None,
                long_name="Melville",
                designator=None,
                platform_name="Celtic Voyager EtC"
            )
        )

        # load designator lookup
        ConstInitializer.initialize_consts()

        # test lookup
        self.assertEqual("CV", DesignatorLookup.get_designator_by_parsed_data_file_platform_name("celtic_voyager"))
        self.assertEqual("CV", DesignatorLookup.get_designator_by_mb_survey_platform_name("Celtic Voyager"))

        self.assertEqual("FA", DesignatorLookup.get_designator_by_parsed_data_file_platform_name("fugro_americas"))
        self.assertEqual("FA", DesignatorLookup.get_designator_by_mb_survey_platform_name("Fugro Americas"))

        self.assertIsNone(DesignatorLookup.get_designator_by_parsed_data_file_platform_name("melville"))
        self.assertIsNone(DesignatorLookup.get_designator_by_mb_survey_platform_name("Melville"))

    @staticmethod
    def clean_db(db):
        db.query("DELETE FROM cruise.PLATFORMS")

