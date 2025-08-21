import datetime
import unittest

from mb_cruise_migration.db.cruise_db import CruiseDb
from mb_cruise_migration.framework.parsed_data_file import ParsedFilePath
from mb_cruise_migration.framework.file_decoder import FileDecoder
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.processors.schema_mapper import SchemaMapper
from testutils import clean_cruise_db
from mb_cruise_migration.migration_properties import MigrationProperties

from mb_cruise_migration.framework.resolvers.dataset_type_resolver import (
    DatasetTypeConsts,
    DTLookup,
)
from mb_cruise_migration.framework.consts.file_label_consts import FileLabels
from mb_cruise_migration.framework.consts.platform_type_consts import PlatformTypeConsts
from mb_cruise_migration.models.cruise.cruise_access_path import CruiseAccessPath
from mb_cruise_migration.models.cruise.cruise_dataset import CruiseDataset
from mb_cruise_migration.models.cruise.cruise_files import CruiseFile
from mb_cruise_migration.models.cruise.cruise_instruments import CruiseInstrument
from mb_cruise_migration.models.cruise.cruise_parameter import (
    CruiseDatasetParameter,
    CruiseFileParameter,
    CruiseSurveyParameter,
)
from mb_cruise_migration.models.cruise.cruise_people_and_sources import (
    CruisePeopleAndSources,
)
from mb_cruise_migration.models.cruise.cruise_platforms import CruisePlatform
from mb_cruise_migration.models.cruise.cruise_projects import CruiseProject
from mb_cruise_migration.models.cruise.cruise_shape import CruiseShape
from mb_cruise_migration.models.cruise.cruise_surveys import CruiseSurvey
from mb_cruise_migration.models.intermediary.cruise_cargo import CruiseCargo
from mb_cruise_migration.models.intermediary.mb_cargo import (
    MbCargo,
    MbSurveyCrate,
    MbFileCrate,
)
from mb_cruise_migration.models.mb.mb_mbinfo_file_tsql import MbInfo
from mb_cruise_migration.models.mb.mb_ngdcid_and_file import MbFile
from mb_cruise_migration.models.mb.mb_survey import MbSurvey
from mb_cruise_migration.models.mb.mb_survey_reference import SurveyReference
from mb_cruise_migration.framework.consts.const_initializer import ConstInitializer
from mb_cruise_migration.processors.transfer_station import TransferStation
from mb_cruise_migration.services.cruise_service import PlatformService


class TestStandardMapping(unittest.TestCase):

    collection_date_start = datetime.datetime.strptime("13-JUN-18", "%d-%b-%y")
    collection_date_end = datetime.datetime.strptime("17-JUN-18", "%d-%b-%y")
    data_last_update = datetime.datetime.strptime("05-MAY-20", "%d-%b-%y")
    data_archive_date = datetime.datetime.strptime("04-SEP-19", "%d-%b-%y")
    file_last_update = datetime.datetime.strptime("05-SEP-19", "%d-%b-%y")

    def tearDown(self) -> None:
        clean_cruise_db()

    def test_standard(self):
        MigrationProperties("config_test.yaml")
        MigrationLog()

        # PREP DB
        platform_service = PlatformService(CruiseDb())
        platform_service.get_new_or_existing_platform(
            CruisePlatform(
                internal_name="roger_revelle",
                platform_type="ship",
                docucomp_uuid=None,
                long_name="Roger Revelle",
                designator="RR",
                platform_name=None,
            )
        )

        ConstInitializer.initialize_consts()

        # SETUP MB TEST OBJECTS
        mb_survey_crate = self._create_standard_test_mb_survey_crate()
        mb_file_crates = self._create_standard_test_mb_file_crates()

        mb_crate = MbCargo(file_crates=mb_file_crates, survey_crate=mb_survey_crate)
        station = TransferStation(mb_crate)

        # TEST
        cruise_cargo = station.transfer()
        self.assertEqual(1, len(cruise_cargo))

        cargo = cruise_cargo[0]
        self.assertTrue(isinstance(cargo, CruiseCargo))

        # survey and survey related tables
        survey = cargo.related_survey_crate.cruise_survey
        self.assertTrue(isinstance(survey, CruiseSurvey))
        self.assertIsNone(survey.id)
        self.assertEqual("RR1808", survey.survey_name)
        self.assertIsNone(survey.parent)
        self.assertEqual("Roger Revelle", survey.platform_name)
        self.assertEqual(
            "2018-06-13T00:00:00",
            survey.start_date,  # datetime.datetime.isoformat(survey.start_date)
        )
        self.assertEqual(
            "2018-06-17T00:00:00",
            survey.end_date,  # datetime.datetime.isoformat(survey.end_date)
        )
        self.assertEqual("Newport, Oregon", survey.departure_port)
        self.assertEqual("Newport, Oregon", survey.arrival_port)
        self.assertIsNone(survey.creation_date)
        self.assertIsNone(survey.last_update)

        survey_parameters = cargo.related_survey_crate.survey_parameters
        self.assertEqual(0, len(survey_parameters))

        survey_shape = cargo.related_survey_crate.survey_shape
        self.assertTrue(isinstance(survey_shape, CruiseShape))
        self.assertEqual("survey", survey_shape.shape_type)
        self.assertEqual("line", survey_shape.geom_type)
        self.assertEqual("LINESTRING (30 10, 10 30, 40 40)", survey_shape.shape)  # TODO
        self.assertIsNone(survey_shape.id)

        # dataset and dataset related tables
        dataset = cargo.dataset_crate.dataset
        self.assertTrue(isinstance(dataset, CruiseDataset))
        self.assertEqual("NEW2930", dataset.other_id)
        self.assertEqual("RR1808_RAW_EM122", dataset.dataset_name)
        self.assertEqual(DatasetTypeConsts.MB_RAW, dataset.dataset_type_name)
        self.assertEqual("EM122", dataset.instruments)
        self.assertEqual("Roger Revelle (RR)", dataset.platforms)
        self.assertEqual(self.data_archive_date, dataset.archive_date)
        self.assertEqual("RR1808", dataset.surveys)
        self.assertEqual("Cascadia GPS-A", dataset.projects)
        self.assertEqual(
            DTLookup.get_id(DatasetTypeConsts.MB_RAW), dataset.dataset_type_id
        )
        self.assertIsNone(dataset.doi)
        self.assertEqual(
            self.data_last_update.isoformat(), dataset.last_update.isoformat()
        )
        self.assertIsNone(dataset.id)

        self.assertEqual(1, len(cargo.dataset_crate.dataset_platforms))
        platform = cargo.dataset_crate.dataset_platforms[0]
        self.assertTrue(isinstance(platform, CruisePlatform))
        self.assertEqual("roger_revelle", platform.internal_name)
        self.assertEqual(PlatformTypeConsts.SHIP, platform.platform_type)
        self.assertIsNone(platform.docucomp_uuid)
        self.assertEqual("Roger Revelle", platform.long_name)
        self.assertEqual("RR", platform.designator)
        self.assertEqual("Roger Revelle", platform.platform_name)
        self.assertIsNone(platform.id)

        self.assertEqual(1, len(cargo.dataset_crate.dataset_instruments))
        instrument = cargo.dataset_crate.dataset_instruments[0]
        self.assertTrue(isinstance(instrument, CruiseInstrument))
        self.assertEqual("EM122", instrument.instrument_name)
        self.assertIsNone(instrument.docucomp_uuid)
        self.assertEqual("Kongsberg EM122", instrument.long_name)
        self.assertIsNone(instrument.id)

        self.assertEqual(1, len(cargo.dataset_crate.dataset_scientists))
        scientist = cargo.dataset_crate.dataset_scientists[0]
        self.assertTrue(isinstance(scientist, CruisePeopleAndSources))
        self.assertIsNone(scientist.id)
        self.assertEqual("C. David Chadwell", scientist.name)
        self.assertIsNone(scientist.position)
        self.assertEqual("Scripps Institution of Oceanography", scientist.organization)
        self.assertIsNone(scientist.street)
        self.assertIsNone(scientist.city)
        self.assertIsNone(scientist.state)
        self.assertIsNone(scientist.zipcode)
        self.assertIsNone(scientist.country)
        self.assertIsNone(scientist.phone)
        self.assertIsNone(scientist.email)
        self.assertIsNone(scientist.orcid)
        self.assertIsNone(scientist.docucomp_uuid)
        self.assertEqual("C. David", scientist.first)
        self.assertEqual("Chadwell", scientist.last)
        self.assertIsNone(scientist.prefix)
        self.assertIsNone(scientist.middle)
        self.assertIsNone(scientist.suffix)

        self.assertEqual(1, len(cargo.dataset_crate.dataset_sources))
        source = cargo.dataset_crate.dataset_sources[0]
        self.assertTrue(isinstance(source, CruisePeopleAndSources))
        self.assertIsNone(source.id)
        self.assertIsNone(source.name)
        self.assertIsNone(source.position)
        self.assertEqual("Rolling Deck to Repository (R2R)", source.organization)
        self.assertIsNone(source.street)
        self.assertIsNone(source.city)
        self.assertIsNone(source.state)
        self.assertIsNone(source.zipcode)
        self.assertIsNone(source.country)
        self.assertIsNone(source.phone)
        self.assertIsNone(source.email)
        self.assertIsNone(source.orcid)
        self.assertIsNone(source.docucomp_uuid)
        self.assertIsNone(source.first)
        self.assertIsNone(source.last)
        self.assertIsNone(source.prefix)
        self.assertIsNone(source.middle)
        self.assertIsNone(source.suffix)

        self.assertEqual(11, len(cargo.dataset_crate.dataset_parameters))
        dataset_parameters = cargo.dataset_crate.dataset_parameters
        for d_param in dataset_parameters:
            self.assertTrue(isinstance(d_param, CruiseDatasetParameter))
            self.assertIsNone(d_param.id)
            self.assertIsNone(d_param.dataset_id)

            if d_param.parameter_detail_name == "DOWNLOAD_URL":
                self.assertEqual(
                    "https://www.ngdc.noaa.gov/ships/roger_revelle/RR1808_mb.html",
                    d_param.value,
                )  # MB.SURVEY_REFERENCE.DOWNLOAD_URL
            elif d_param.parameter_detail_name == "COMMENTS":
                self.assertEqual(
                    "fake comment, I am", d_param.value
                )  # MB.SURVEY.COMMENTS
            elif d_param.parameter_detail_name == "PROPRIETARY":
                self.assertEqual("No", d_param.value)  # MB.SURVEY.PROPRIETARY
            elif d_param.parameter_detail_name == "NAV1":
                self.assertEqual("GPS", d_param.value)  # MB.SURVEY.NAV1
            elif d_param.parameter_detail_name == "NAV2":
                self.assertEqual("fake_nav2", d_param.value)  # MB.SURVEY.NAV2
            elif d_param.parameter_detail_name == "HORIZONTAL_DATUM":
                self.assertEqual("fake_hd", d_param.value)  # MB.SURVEY.HORIZONTAL_DATUM
            elif d_param.parameter_detail_name == "VERTICAL_DATUM":
                self.assertEqual("fake_vd", d_param.value)  # MB.SURVEY.VERTICAL_DATUM
            elif d_param.parameter_detail_name == "TIDE_CORRECTION":
                self.assertEqual("fake_tc", d_param.value)  # MB.SURVEY.TIDE_CORRECTION
            elif d_param.parameter_detail_name == "SOUND_VELOCITY":
                self.assertEqual("fake_sv", d_param.value)  # MB.SURVEY.SOUND_VELOCITY
            elif d_param.parameter_detail_name == "ABSTRACT":
                self.assertEqual(
                    "fake_abstract_value", d_param.value
                )  # MB.SURVEY_REFERENCE.ABSTRACT
            elif d_param.parameter_detail_name == "PURPOSE":
                self.assertEqual(
                    "fake_purpose_value", d_param.value
                )  # MB.SURVEY_REFERENCE.PURPOSE

            else:
                self.assertTrue(False)  # must match a case

        # project and project related tables
        project = cargo.related_project_crate.project
        self.assertTrue(isinstance(project, CruiseProject))
        self.assertEqual("Cascadia GPS-A", project.project_name)
        self.assertIsNone(project.id)

        self.assertEqual(1, len(cargo.related_project_crate.project_parameters))
        project_parameters = cargo.related_project_crate.project_parameters
        for project_param in project_parameters:
            if project_param.parameter_detail_name == "PROJECT_URL":
                self.assertEqual(
                    "https://url.to.cool.project", project_param.value
                )  # MB.SURVEY_REFERENCE.PROJECT_URL
            else:
                self.assertTrue(False)  # must match a case

        # files and file related tables
        self.assertEqual(1, len(cargo.related_file_crates))
        file_crates = cargo.related_file_crates
        for crate in file_crates:
            file = crate.file
            self.assertTrue(isinstance(file, CruiseFile))
            self.assertEqual("0140_20180617_101452_revelle.all.mb58.gz", file.file_name)
            self.assertEqual(32143468, file.raw_size)
            self.assertEqual("Y", file.publish)
            self.assertEqual(
                self.collection_date_start.isoformat(), file.collection_date
            )
            self.assertEqual(self.data_archive_date.isoformat(), file.publish_date)
            self.assertEqual(self.file_last_update.isoformat(), file.last_update)
            self.assertEqual(self.data_archive_date.isoformat(), file.archive_date)
            self.assertEqual(15813031, file.gzip_size)
            self.assertIsNone(file.id)
            self.assertIsNone(file.dataset_id)
            self.assertEqual(1, file.version_id)
            self.assertEqual(1, file.type_id)
            self.assertEqual(67, file.format_id)

            shape = crate.file_shape
            self.assertTrue(isinstance(shape, CruiseShape))
            self.assertEqual("file", shape.shape_type)
            self.assertEqual("line", shape.geom_type)
            self.assertEqual("LINESTRING (32 10, 30 10, 10 30)", shape.shape)
            self.assertIsNone(shape.id)

            self.assertEqual(2, len(crate.file_access_paths))
            access_paths = crate.file_access_paths
            for access_path in access_paths:
                self.assertTrue(isinstance(access_path, CruiseAccessPath))

                if access_path.path_type == "Disk":
                    self.assertEqual(
                        "ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122",
                        access_path.path,
                    )  # MB.NGDCID_AND_FILE.DATA_FILE
                elif access_path.path_type == "Stornext":
                    self.assertEqual(
                        "/stornext/ngdc/archive/insitu_ocean/trackline/roger_revelle/rr1808/multibeam/data/version1/MB/em122",
                        access_path.path,
                    )  # MB.NGDCID_AND_FILE.ARCHIVE_PATH
                else:
                    self.assertTrue(
                        False
                    )  # must be one of either stornext or disk path type
                self.assertIsNone(access_path.id)

            self.assertFalse(crate.file_parameters)
            # self.assertEqual(2, len(crate.file_parameters))
            file_parameters = crate.file_parameters
            for file_parameter in file_parameters:
                self.assertTrue(isinstance(file_parameter, CruiseFileParameter))
                self.assertIsNone(file_parameter.id)
                self.assertIsNone(file_parameter.file_id)

    def _create_standard_test_mb_survey_crate(self):
        mb_survey = self._get_standard_test_mb_survey()
        mb_survey_reference = self._get_standard_survey_reference()

        return MbSurveyCrate(
            survey=mb_survey,
            survey_reference=mb_survey_reference,
            shape="LINESTRING (30 10, 10 30, 40 40)",
        )

    def _create_standard_test_mb_file_crates(self):
        mbfile = self._get_standard_test_file()
        mbinfo = self._get_standard_test_mbinfo()
        mbfile.label = FileLabels.STANDARD
        file_crate1 = MbFileCrate(
            mb_file=mbfile, mb_info=mbinfo, shape="LINESTRING (32 10, 30 10, 10 30)"
        )
        file_crates = FileDecoder.decode([file_crate1])

        return file_crates

    @staticmethod
    def _get_standard_test_mb_survey():
        return MbSurvey(
            ngdc_id="NEW2930",
            chief_scientist="Chadwell, C. David",
            departure_port="Newport, Oregon",
            arrival_port="Newport, Oregon",
            start_time=datetime.datetime.strptime("13-JUN-18", "%d-%b-%y"),
            end_time=datetime.datetime.strptime("17-JUN-18", "%d-%b-%y"),
            survey_name="RR1808",
            ship_name="Roger Revelle",
            source="Rolling Deck to Repository (R2R)",
            nav1="GPS",
            nav2="fake_nav2",
            instrument="Kongsberg EM122",
            horizontal_datum="fake_hd",
            vertical_datum="fake_vd",
            tide_correction="fake_tc",
            sound_velocity="fake_sv",
            ship_owner=None,
            project_name="Cascadia GPS-A",
            contact_id=None,
            chief_sci_organization="Scripps Institution of Oceanography",
            publish="yes",
            comments="fake comment, I am",
            proprietary="No",
            entered_date=datetime.datetime.strptime("04-SEP-19", "%d-%b-%y"),
            previous_state="No",
            file_count=142,
            track_length=965.8628,
            total_time=68.5061,
            bathy_beams=36583920,
            amp_beams=36583920,
            sidescans=173434880,
            survey_size=6797,
            modify_date_data=datetime.datetime.strptime("05-MAY-20", "%d-%b-%y"),
            modify_date_metadata=datetime.datetime.strptime("04-SEP-19", "%d-%b-%y"),
            extract_metadata="yes",
        )

    @staticmethod
    def _get_standard_survey_reference():
        return SurveyReference(
            ngdc_id="NEW2930",
            doi=None,
            abstract="fake_abstract_value",
            purpose="fake_purpose_value",
            project_url="https://url.to.cool.project",
            create_date=datetime.datetime.strptime("05-SEP-19", "%d-%b-%y"),
            created_by="initial load",
            last_update_date=None,
            last_updated_by=None,
            download_url="https://www.ngdc.noaa.gov/ships/roger_revelle/RR1808_mb.html",
        )

    @staticmethod
    def _get_standard_test_file():
        file1 = MbFile(
            ngdc_id="NEW2930",
            data_file="ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122/0140_20180617_101452_revelle.all.mb58.gz",
            format_id=58,
            entry_date=datetime.datetime.strptime("04-SEP-19", "%d-%b-%y"),
            process_date=datetime.datetime.strptime("05-SEP-19", "%d-%b-%y"),
            status="Processed by jdbload-mb_track with /opt/gis_contrib/bin/mbinfo -G -F 58 -I/mgg/MB/ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122/0140_20180617_101452_revelle.all.mb58",
            version=1,
            mostcurrent=1,
            version_id=0,
            process_notes="min_amp < min amp: -77.8 truncated to 0.0, max_amp < min amp: -20.3 truncated to 0.0, min_sidescan < min sidescan value: -84.55 truncated to 0.0, max_sidescan < min sidescan value: -20.3 truncated to 0.0",
            filesize=32143468,
            filesize_gzip=15813031,
            filenotfound=None,
            publish="yes",
            previous_state="No",
            archive_path="/stornext/ngdc/archive/insitu_ocean/trackline/roger_revelle/rr1808/multibeam/data/version1/MB/em122/0140_20180617_101452_revelle.all.mb58.gz",
        )
        file1.parsed_file = ParsedFilePath(file1.data_file)

        return file1

        # file2 = MbFile(
        #     ngdc_id="NEW2930",
        #     data_file="ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122/0150_20180617_151453_revelle.all.mb58.gz",
        #     format_id=58,
        #     entry_date="04-SEP-19",
        #     process_date="05-SEP-19",
        #     status="Processed by jdbload-mb_track with /opt/gis_contrib/bin/mbinfo -G -F 58 -I/mgg/MB/ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122/0150_20180617_151453_revelle.all.mb58",
        #     version=1,
        #     mostcurrent=1,
        #     version_id=0,
        #     process_notes="min_amp < min amp: -75.1 truncated to 0.0, max_amp < min amp: -0.9 truncated to 0.0, min_sidescan < min sidescan value: -97.9 truncated to 0.0, max_sidescan < min sidescan value: -10.2 truncated to 0.0",
        #     filesize=23576814,
        #     filesize_gzip=13715710,
        #     filenotfound=None,
        #     publish="yes",
        #     previous_state="No",
        #     archive_path="/stornext/ngdc/archive/insitu_ocean/trackline/roger_revelle/rr1808/multibeam/data/version1/MB/em122/0150_20180617_151453_revelle.all.mb58.gz"
        # )

        # return file1, file2

    @staticmethod
    def _get_standard_test_mbinfo():

        mbinfo1 = MbInfo(
            data_file="ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122/0140_20180617_101452_revelle.all.mb58.gz",
            ngdc_id="NEW2930",
            mbio_format_id=58,
            record_count=199,
            bathy_beams=85968,
            bb_good=37828,
            bb_zero=0,
            bb_flagged=48140,
            amp_beams=85968,
            ab_good=37828,
            ab_zero=0,
            ab_flagged=48140,
            sidescans=407552,
            ss_good=51130,
            ss_zero=0,
            ss_flagged=356422,
            total_time=0.0484,
            track_length=0.8739,
            avg_speed=18.0479,
            start_time=datetime.datetime.strptime("13-JUN-18", "%d-%b-%y"),
            start_lon=-124.9368864,
            start_lat=43.9380677,
            start_depth=526.6157,
            start_speed=18.72,
            start_heading=29.79,
            start_sonar_depth=6.1956,
            start_sonar_alt=517.012,
            end_time=datetime.datetime.strptime("17-JUN-18", "%d-%b-%y"),
            end_lon=-124.9315114,
            end_lat=43.94489725,
            end_depth=452.7342,
            end_speed=18.72,
            end_heading=31.93,
            end_sonar_depth=5.8218,
            end_sonar_alt=446.4576,
            min_lon=-124.941614557,
            max_lon=-124.929731436,
            min_lat=43.936409568,
            max_lat=43.945754166,
            min_sonar_depth=4.311,
            max_sonar_depth=7.2459,
            min_sonar_alt=440.5044,
            max_sonar_alt=1142.1681,
            min_depth=438.2145,
            max_depth=1206.4799,
            min_amp=0,
            max_amp=0,
            min_sidescan=0,
            max_sidescan=0,
            objectid=1704625,
            shape=None,  # MDSYS.SDO_GEOMETRY(2002, 8307, NULL, MDSYS.SDO_ELEM_INFO_ARRAY(1, 2, 1), MDSYS.SDO_ORDINATE_ARRAY(-124.9368864, 43.9380677, -124.9315114, 43.94489725))
            publish="yes",
            previous_state="No",
            shape_gen=None,  # MDSYS.SDO_GEOMETRY(2002, 8307, NULL, MDSYS.SDO_ELEM_INFO_ARRAY(1, 2, 1), MDSYS.SDO_ORDINATE_ARRAY(-124.9368864, 43.9380677, -124.9315114, 43.94489725))
        )

        return mbinfo1

        # mbinfo2 = MbInfo(
        #     data_file="ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122/0150_20180617_151453_revelle.all.mb58.gz",
        #     ngdc_id="NEW2930",
        #     mbio_format_id=58,
        #     record_count=619,
        #     bathy_beams=267408,
        #     bb_good=218558,
        #     bb_zero=0,
        #     bb_flagged=48850,
        #     amp_beams=267408,
        #     ab_good=218558,
        #     ab_zero=0,
        #     ab_flagged=48850,
        #     sidescans=1267712,
        #     ss_good=476874,
        #     ss_zero=0,
        #     ss_flagged=790838,
        #     total_time=0.0458,
        #     track_length=0.8038,
        #     avg_speed=17.5349,
        #     start_time="17-JUN-18",
        #     start_lon=-124.3676899,
        #     start_lat=44.3984174,
        #     start_depth=231.9126,
        #     start_speed=17.424,
        #     start_heading=38.5,
        #     start_sonar_depth=5.2363,
        #     start_sonar_alt=226.8021,
        #     end_time="17-JUN-18",
        #     end_lon=-124.3609625,
        #     end_lat=44.4037969,
        #     end_depth=147.8297,
        #     end_speed=17.424,
        #     end_heading=41.41,
        #     end_sonar_depth=5.8082,
        #     end_sonar_alt=142.0824,
        #     min_lon=-124.368744437,
        #     max_lon=-124.359581432,
        #     min_lat=44.397857001,
        #     max_lat=44.404673958,
        #     min_sonar_depth=4.5649,
        #     max_sonar_depth=6.9716,
        #     min_sonar_alt=141.3245,
        #     max_sonar_alt=226.8021,
        #     min_depth=101.3383,
        #     max_depth=242.115,
        #     min_amp=0,
        #     max_amp=0,
        #     min_sidescan=0,
        #     max_sidescan=0,
        #     objectid=1704626,
        #     shape=None,  # MDSYS.SDO_GEOMETRY(2002, 8307, NULL, MDSYS.SDO_ELEM_INFO_ARRAY(1, 2, 1), MDSYS.SDO_ORDINATE_ARRAY(-124.3676899, 44.3984174, -124.3609625, 44.4037969))
        #     publish="yes",
        #     previous_state="No",
        #     shape_gen=None  # MDSYS.SDO_GEOMETRY(2002, 8307, NULL, MDSYS.SDO_ELEM_INFO_ARRAY(1, 2, 1), MDSYS.SDO_ORDINATE_ARRAY(-124.3676899, 44.3984174, -124.3609625, 44.4037969))
        # )
        #
        # return mbinfo1, mbinfo2

    def test_source_parsing(self):
        MigrationProperties("config_test.yaml")
        MigrationLog()

        original_source = (
            "Rolling Deck to Repository; Marine Geoscience Data System (R2R/MGDS)"
        )
        result = SchemaMapper.parse_sources_from_original_source(original_source)
        self.assertIsInstance(
            result,
            list,
        )
        self.assertEqual(2, len(result))
        source_result1 = result[0]
        self.assertIsInstance(source_result1, CruisePeopleAndSources)
        source_result2 = result[1]
        self.assertIsInstance(source_result2, CruisePeopleAndSources)
        self.assertEqual(
            "Rolling Deck to Repository (R2R)", source_result1.organization
        )
        self.assertEqual(
            "Marine Geoscience Data System (MGDS)", source_result2.organization
        )
