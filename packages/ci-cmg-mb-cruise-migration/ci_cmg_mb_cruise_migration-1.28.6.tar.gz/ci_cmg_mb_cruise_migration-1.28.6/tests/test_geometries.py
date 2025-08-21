import unittest

from mb_cruise_migration.db.cruise_connection import CruiseConnection
from mb_cruise_migration.db.cruise_db import CruiseDb
from mb_cruise_migration.db.mb_db import MbDb
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.models.cruise.cruise_dataset import CruiseDataset
from mb_cruise_migration.models.cruise.cruise_shape import CruiseShape
from mb_cruise_migration.processors.cruise_processor import CruiseProcessor
from mb_cruise_migration.services.cruise_service import (
    ShapeService,
    DatasetService,
    SurveyService,
)
from mb_cruise_migration.services.mb_service import MbService

from testutils import clean_mb_db, clean_cruise_db, load_test_mb_data


class TestGeometries(unittest.TestCase):
    MigrationProperties("config_test.yaml")
    MigrationLog()

    def setUp(self) -> None:
        self.tearDown()

        load_test_mb_data("RR1808.sql")
        self.ngdc_id = "NEW2930"
        self.value = {"NGDC_ID": self.ngdc_id}

        self.mb = MbDb()
        self.cruise = CruiseConnection()
        self.mb_service = MbService()
        self.shape_service = ShapeService(CruiseDb())
        self.dataset_service = DatasetService(CruiseDb())
        self.survey_service = SurveyService(CruiseDb())
        self.dataset = self.get_dummy_dataset()

    def tearDown(self) -> None:
        clean_mb_db()
        clean_cruise_db()
        CruiseProcessor.source_cache.clean_cache()
        CruiseProcessor.instrument_cache.clean_cache()
        CruiseProcessor.scientist_cache.clean_cache()
        CruiseProcessor.platform_cache.clean_cache()
        CruiseProcessor.project_cache.clean_cache()

    def get_dummy_dataset(self):
        return self.dataset_service.save_new_dataset(
            CruiseDataset(
                archive_date=None,
                dataset_name="name",
                dataset_type_id=1,
                dataset_type_name="dname",
                instruments="instr1",
                other_id="NEW10",
                platforms="flak",
                projects="mission impossible",
                surveys="survey",
            )
        )

    @unittest.skip(
        "This test fails; migration uses WKT in favor of WKB for that reason"
    )
    def test_wkb_shape_migration(self):
        query = f"SELECT SDO_UTIL.TO_WKBGEOMETRY(SHAPE) as SHAPE FROM MB.MBINFO_SURVEY_TSQL WHERE NGDC_ID=:NGDC_ID"
        wkb_result = self.mb.fetch_one(query, self.value)
        wkb_blob = wkb_result["SHAPE"]
        wkb = wkb_blob.read()

        try:
            self.shape_service.save_dataset_shape(
                self.dataset,
                CruiseShape(shape_type="dataset", geom_type="line", shape=wkb),
            )
            self.assertTrue(True)  # pass on no error
        except Exception as e:
            self.assertTrue(False)  # fail on exception

    def test_wkt_shape_migration(self):
        query = f"SELECT SDO_UTIL.TO_WKTGEOMETRY(SHAPE) as SHAPE FROM MB.MBINFO_SURVEY_TSQL WHERE NGDC_ID=:NGDC_ID"
        wkt_clob = self.mb.fetch_shape(query, "SHAPE", self.value)

        try:
            self.shape_service.save_dataset_shape(
                self.dataset,
                CruiseShape(shape_type="dataset", geom_type="line", shape=wkt_clob),
            )
            self.assertTrue(True)  # pass on no error
        except Exception:
            self.assertTrue(False)  # fail on exception

    def test_to_clob_simple_get_simple_put(self):
        query = f"SELECT TO_CLOB(SDO_UTIL.TO_WKTGEOMETRY(SHAPE)) as SHAPE FROM MB.MBINFO_SURVEY_TSQL WHERE NGDC_ID=:NGDC_ID"
        clob = self.mb.fetch_shape(query, "SHAPE", self.value)
        shape = CruiseShape(shape_type="dataset", geom_type="line", shape=clob)

        try:
            shape_dict = {
                "SHAPE": shape.shape,
                "SHAPE_TYPE": shape.shape_type,
                "GEOM_TYPE": shape.geom_type,
            }
            i_command = f"INSERT INTO CRUISE.SHAPES (SHAPE, SHAPE_TYPE, GEOM_TYPE) VALUES(SDO_GEOMETRY(:SHAPE, 8307), :SHAPE_TYPE, :GEOM_TYPE)"
            self.cruise.execute(command=i_command, data=shape_dict)
            self.assertTrue(True)  # pass on no error
        except Exception:
            self.assertTrue(False)  # fail on exception

    def get_shape(self, *ordinates):
        """example of creating shape object that can be inserted directly into SDO_GEOMETRY columns"""
        geometry = self.shape_service.shape_obj.newobject()
        geometry.SDO_GTYPE = 2003
        geometry.SDO_SRID = 8307
        geometry.SDO_ELEM_INFO = self.shape_service.shape_element_info_obj.newobject()
        geometry.SDO_ELEM_INFO.extend([1, 1003, 1])
        geometry.SDO_ORDINATES = self.shape_service.shape_ordinates_obj.newobject()
        geometry.SDO_ORDINATES.extend(ordinates)
