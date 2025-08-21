import unittest

from mb_cruise_migration.framework.consts.version_description_consts import (
    VersionDescriptionConsts,
)
from mb_cruise_migration.framework.resolvers.dataset_type_resolver import DTLookup
from mb_cruise_migration.framework.resolvers.file_format_resolver import FFLookup
from mb_cruise_migration.framework.resolvers.file_type_resolver import FTLookup
from mb_cruise_migration.framework.resolvers.version_description_resolver import (
    VDLookup,
)
from mb_cruise_migration.framework.consts.const_initializer import ConstInitializer
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.migration_properties import MigrationProperties


class TestConstInitializer(unittest.TestCase):
    MigrationProperties("config_test.yaml")
    MigrationLog()

    def test_cruise_const_setup(self):
        try:
            ConstInitializer.initialize_consts()

            self.assertEqual(1, DTLookup.get_id("MB RAW"))
            self.assertEqual(9, DTLookup.get_id("METADATA"))

            self.assertEqual(2, FTLookup.get_id("MB PROCESSED"))
            self.assertEqual(5, FTLookup.get_id("DOCUMENT"))

            self.assertEqual(
                21, FFLookup.get_id(FFLookup.REVERSE_LOOKUP["MBF_HSLDEDMB"].alt_id)
            )
            self.assertEqual(
                77, FFLookup.get_id(FFLookup.REVERSE_LOOKUP["ASCII_TEXT"].alt_id)
            )

            self.assertEqual(
                1, VDLookup.get_id_from_description(VersionDescriptionConsts.RAW)
            )
            self.assertEqual(
                2, VDLookup.get_id_from_description(VersionDescriptionConsts.PROCESSED)
            )
            self.assertEqual(
                3, VDLookup.get_id_from_description(VersionDescriptionConsts.PRODUCT)
            )
            self.assertEqual(1, VDLookup.get_id(1))
            self.assertEqual(2, VDLookup.get_id(2))
            self.assertEqual(3, VDLookup.get_id(3))
            self.assertEqual(1, VDLookup.get_id("1"))
            self.assertEqual(2, VDLookup.get_id("2"))
            self.assertEqual(3, VDLookup.get_id("3"))

        except:
            self.fail()
