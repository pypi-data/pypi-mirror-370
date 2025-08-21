import unittest
import datetime

from mb_cruise_migration.framework.resolvers.dataset_type_resolver import DTLookup
from mb_cruise_migration.framework.resolvers.file_format_resolver import FFLookup
from mb_cruise_migration.framework.resolvers.file_type_resolver import FTLookup
from mb_cruise_migration.framework.consts.parameter_detail_consts import PDLookup
from mb_cruise_migration.framework.resolvers.version_description_resolver import VDLookup
from mb_cruise_migration.framework.consts.const_initializer import ConstInitializer
from mb_cruise_migration.migration_properties import MigrationProperties
from testutils import create_test_dataset, create_test_instrument, create_test_file, create_test_project, \
    create_test_shape, create_test_platform, create_test_source, create_test_survey, create_test_parameter, \
    create_test_scientist, create_test_access_path, clean_cruise_db
from mb_cruise_migration.models.intermediary.cruise_cargo import CruiseFileCrate, \
  CruiseDatasetCrate, CruiseSurveyCrate, CruiseProjectCrate, CruiseCargo
from mb_cruise_migration.processors.cruise_processor import CruiseProcessor


class TestCruiseProcessor(unittest.TestCase):
    MigrationProperties("config_test.yaml")

    def tearDown(self):
        clean_cruise_db()

    @unittest.skip("REPLACED BY FAST_CRUISE_PROCESSOR")
    def test_cruise_processor(self):
        # initialize consts
        ConstInitializer.initialize_consts()

        # build cargo
        file1 = create_test_file(
            file_name="/path/to/file/filename.mb.all",
            raw_size=52460436,
            publish="Y",
            collection_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
            publish_date=datetime.datetime(2020, 5, 18, 1, 2, 5),
            archive_date=datetime.datetime(2020, 5, 18, 11, 12, 13),
            temp_id=None,
            gzip_size=48460436,
            version_id=VDLookup.get_id_from_description("RAW"),
            format_id=FFLookup.get_id(FFLookup.REVERSE_LOOKUP["MBF_SBSIOSWB"].alt_id),
            type_id=FTLookup.get_id("MB RAW")
        )
        file1_access_path1 = create_test_access_path(path="/path", path_type="winding")
        file1_access_path2 = create_test_access_path(path="/walkway", path_type="straight")
        file1_parameter1 = create_test_parameter(parameter="SUN", value="center", detail_id=PDLookup.get_id("MB_FILE_COUNT"))
        file1_parameter2 = create_test_parameter(parameter="MERCURY", value="retrograde", detail_id=PDLookup.get_id("MB_BATHY_BEAMS"))
        file1_shape = create_test_shape(shape='POINT(0 0)', shape_type="file", geom_type="geom_type",)

        file_crate1 = CruiseFileCrate()
        file_crate1.file = file1
        file_crate1.file_access_paths = [file1_access_path1, file1_access_path2]
        file_crate1.file_parameters = [file1_parameter1, file1_parameter2]
        file_crate1.file_shape = file1_shape

        file2 = create_test_file(
            file_name="/path/to/file/filename.mb.all",
            raw_size=52460436,
            publish="Y",
            collection_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
            publish_date=datetime.datetime(2020, 5, 18, 1, 2, 5),
            archive_date=datetime.datetime(2020, 5, 18, 11, 12, 13),
            temp_id=None,
            gzip_size=48460436,
            version_id=VDLookup.get_id_from_description("PROCESSED"),
            format_id=FFLookup.get_id(FFLookup.REVERSE_LOOKUP["ASCII_TEXT"].alt_id),
            type_id=FTLookup.get_id("MB PRODUCT")
        )
        file2_access_path1 = create_test_access_path(path="/path", path_type="winding")
        file2_access_path2 = create_test_access_path(path="/walkway", path_type="straight")
        file2_parameter1 = create_test_parameter(parameter="VENUS", value="women", detail_id=PDLookup.get_id("Comments"))
        file2_parameter2 = create_test_parameter(parameter="MARS", value="men", detail_id=PDLookup.get_id("MB_AREA_SQ_KM"))
        file2_shape = create_test_shape(shape='POINT(0 0)', shape_type="file", geom_type="geom_type",)

        file_crate2 = CruiseFileCrate()
        file_crate2.file = file2
        file_crate2.file_access_paths = [file2_access_path1, file2_access_path2]
        file_crate2.file_parameters = [file2_parameter1, file2_parameter2]
        file_crate2.file_shape = file2_shape

        file_crates = [file_crate1, file_crate2]

        dataset = create_test_dataset(
            other_id="02030057",
            dataset_name="KN159L5_SeaBeam2112",
            dataset_type_name="MB RAW",
            instruments="SeaBeam2112",
            platforms="Knorr",
            archive_date=datetime.datetime(2020, 5, 19, 1, 2, 3),
            surveys="KN159L5",
            projects="Project Manhattan",
            type_id=DTLookup.get_id("MB RAW")
        )

        dataset_parameter1 = create_test_parameter(parameter="DEPTH", value="infinite", detail_id=PDLookup.get_id("FILE_FORMAT_TYPE"))
        dataset_parameter2 = create_test_parameter(parameter="DIST", value="far", detail_id=PDLookup.get_id("MB_MAX_ALTITUDE"))
        dataset_parameters = [dataset_parameter1, dataset_parameter2]
        dataset_sources = [create_test_source(organization="Styx")]
        dataset_scientist1 = create_test_scientist(
            name="Elizabeth Lobecker",
            organization="NOAA/OAR/OER/OEP"
        )
        dataset_scientist2 = create_test_scientist(
            name="Sally Forthright",
            organization="Atlantis"
        )
        dataset_scientists = [dataset_scientist1, dataset_scientist2]
        dataset_platforms = [create_test_platform(
            internal_name="neil_armstrong",
            platform_type="ship",
            docucomp_uuid="05e94496-2ecc-437d-b875-6c037cb236b5",
            long_name="Neil Armstrong",
            designator="AR",
            platform_name="Neil Armstrong"
        )]

        dataset_instruments = [create_test_instrument(
            instrument_name="EM122",
            docucomp_uuid="05e94496-2ecc-437d-b875-6c037cb236b5",
            long_name="Kongsberg EM122"
        )]

        dataset_crate = CruiseDatasetCrate()
        dataset_crate.dataset = dataset
        dataset_crate.dataset_parameters = dataset_parameters
        dataset_crate.dataset_sources = dataset_sources
        dataset_crate.dataset_scientists = dataset_scientists
        dataset_crate.dataset_platforms = dataset_platforms
        dataset_crate.dataset_instruments = dataset_instruments

        cruise_survey = create_test_survey(
            name="Falkor999",
            parent=5,
            platform="popeye power",
            departure_port="hong kong",
            arrival_port="pearl harbor",
            start_date=datetime.datetime(2020, 5, 19, 1, 2, 3),
            end_date=datetime.datetime(2020, 5, 20, 1, 2, 3)
        )
        survey_parameter1 = create_test_parameter(parameter="METAL", value="tin", detail_id=PDLookup.get_id("DIRECTORY_STRUCTURE_TYPE"))
        survey_parameter2 = create_test_parameter(parameter="WOOD", value="oak", detail_id=PDLookup.get_id("NAV1"))
        survey_parameters = [survey_parameter1, survey_parameter2]
        survey_shape = create_test_shape(shape='POINT(0 0)', shape_type="survey", geom_type="geom_type",)

        survey_crate = CruiseSurveyCrate()
        survey_crate.cruise_survey = cruise_survey
        survey_crate.survey_parameters = survey_parameters
        survey_crate.survey_shape = survey_shape

        project = create_test_project(project_name="Neptune Spear")

        project_parameter1 = create_test_parameter(parameter="ACCURACY", value="bad", detail_id=PDLookup.get_id("MB_SYSTEM_ID"))
        project_parameter2 = create_test_parameter(parameter="EFFICIENCY", value="best", detail_id=PDLookup.get_id("MB_AVG_SPEED_KM_HR"))
        project_parameters = [project_parameter1, project_parameter2]

        project_crate = CruiseProjectCrate()
        project_crate.project = project
        project_crate.project_parameters = project_parameters

        cruise_cargo = CruiseCargo(dataset_crate, survey_crate, project_crate, file_crates)

        # inserts dataset-centric cargo object into cruise /////////////////////
        cruise_processor = CruiseProcessor()
        cruise_processor.ship(cruise_cargo)

        # TODO assertions


if __name__ == '__main__':
    unittest.main()
