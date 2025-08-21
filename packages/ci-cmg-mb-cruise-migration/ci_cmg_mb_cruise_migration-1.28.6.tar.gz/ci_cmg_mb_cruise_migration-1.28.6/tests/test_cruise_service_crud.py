import unittest
import datetime

from ncei_cruise_schema.entity.file import File

from mb_cruise_migration.db.cruise_db import CruiseDb
from mb_cruise_migration.framework.resolvers.dataset_type_resolver import (
    DTLookup,
    DatasetTypeConsts,
)
from mb_cruise_migration.framework.resolvers.file_format_resolver import FFLookup
from mb_cruise_migration.framework.resolvers.file_type_resolver import FTLookup
from mb_cruise_migration.framework.resolvers.version_description_resolver import (
    VDLookup,
)
from mb_cruise_migration.framework.consts.const_initializer import ConstInitializer
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.migration_properties import MigrationProperties

from ncei_cruise_schema.entity.access_path import AccessPath
from ncei_cruise_schema.entity.contact import Contact
from ncei_cruise_schema.entity.dataset import Dataset
from ncei_cruise_schema.entity.instrument import Instrument
from ncei_cruise_schema.entity.platform import Platform
from ncei_cruise_schema.entity.project import Project
from ncei_cruise_schema.entity.survey import Survey

from mb_cruise_migration.models.cruise.cruise_access_path import CruiseAccessPath
from mb_cruise_migration.models.cruise.cruise_dataset import CruiseDataset
from mb_cruise_migration.models.cruise.cruise_instruments import CruiseInstrument
from mb_cruise_migration.models.cruise.cruise_people_and_sources import (
    CruisePeopleAndSources,
)
from mb_cruise_migration.models.cruise.cruise_platforms import CruisePlatform
from mb_cruise_migration.models.cruise.cruise_projects import CruiseProject
from mb_cruise_migration.models.cruise.cruise_surveys import CruiseSurvey
from mb_cruise_migration.services.cruise_service import (
    AccessPathService,
    SurveyService,
    ShapeService,
    ProjectService,
    PlatformService,
    ParameterService,
    InstrumentService,
    FileService,
    ContactService,
    DatasetService,
    DatasetTypeService,
    FileFormatService,
    FileTypeService,
    VersionDescriptionService,
    ParameterDetailService,
)
from testutils import create_test_file, create_test_dataset, clean_cruise_db


class TestCruiseServiceCrud(unittest.TestCase):
    MigrationProperties("config_test.yaml")
    MigrationLog()

    def tearDown(self):
        clean_cruise_db()

    def test_dataset_service(self):
        dataset_service = DatasetService(CruiseDb())
        ConstInitializer.initialize_consts()

        other_id = "02030057"
        dataset_name = "KN159L5_SeaBeam2112"
        dataset_type_name = "MB RAW"
        instruments = "SeaBeam2112"
        platforms = "Knorr"
        archive_date = datetime.datetime(2020, 5, 19, 1, 2, 3).isoformat()
        surveys = "KN159L5"
        projects = "Project Manhattan"
        dataset_type_id = DTLookup.get_id(DatasetTypeConsts.MB_RAW)

        model = CruiseDataset(
            other_id=other_id,
            dataset_name=dataset_name,
            dataset_type_name=dataset_type_name,
            instruments=instruments,
            platforms=platforms,
            archive_date=archive_date,
            surveys=surveys,
            projects=projects,
            dataset_type_id=dataset_type_id,
        )

        # Create new
        saved = dataset_service.save_new_dataset(model)

        self.assertTrue(isinstance(saved, Dataset))
        self.assertEqual(other_id, saved.other_id)
        self.assertEqual(dataset_type_name, saved.dataset_type_name)
        self.assertEqual(instruments, saved.instruments)
        self.assertEqual(platforms, saved.platforms)
        self.assertEqual(archive_date, saved.archive_date)
        self.assertEqual(surveys, saved.surveys)
        self.assertEqual(projects, saved.projects)
        self.assertEqual(dataset_type_id, saved.dataset_type_id)
        self.assertIsNotNone(saved.id)

        # Find existing
        found = dataset_service.find_by_dataset_name(dataset_name)

        self.assertTrue(isinstance(found, Dataset))
        self.assertEqual(other_id, found.other_id)
        self.assertEqual(dataset_type_name, found.dataset_type_name)
        self.assertEqual(instruments, found.instruments)
        self.assertEqual(platforms, found.platforms)
        self.assertEqual(archive_date, found.archive_date)
        self.assertEqual(surveys, found.surveys)
        self.assertEqual(projects, found.projects)
        self.assertEqual(dataset_type_id, found.dataset_type_id)
        self.assertIsNotNone(found.id)
        self.assertEqual(found.id, saved.id)

        found_by_id = dataset_service.find_by_id(found.id)
        self.assertIsNotNone(found_by_id)
        self.assertEqual(found_by_id.id, found.id)

        # Delete
        dataset_service.delete_dataset(found)
        deleted = dataset_service.find_by_dataset_name(dataset_name)
        self.assertIsNone(deleted)

    def test_access_path_service(self):
        self.access_path_service = AccessPathService(CruiseDb())

        path = "/path"
        path_type = "winding"
        model = CruiseAccessPath(path, path_type)

        # Create new
        saved = self.access_path_service.save_new_access_path(model)

        self.assertTrue(isinstance(saved, AccessPath))
        self.assertEqual(model.path, path)
        self.assertEqual(model.path_type, path_type)
        self.assertIsNotNone(saved.id)

        # Find existing
        found = self.access_path_service.find_by_path_and_path_type(path, path_type)

        self.assertTrue(isinstance(found, AccessPath))
        self.assertEqual(model.path, path)
        self.assertEqual(model.path_type, path_type)
        self.assertIsNotNone(found.id)
        self.assertEqual(found.id, saved.id)

        found_by_id = self.access_path_service.find_by_id(found.id)
        self.assertIsNotNone(found_by_id)
        self.assertEqual(found_by_id.id, found.id)
        self.assertEqual(found_by_id.path, found.path)
        self.assertEqual(found_by_id.path_type, found.path_type)

        # Delete
        self.access_path_service.delete_access_path(found)
        deleted = self.access_path_service.find_by_path_and_path_type(path, path_type)
        self.assertIsNone(deleted)

    def test_survey_service(self):
        self.survey_service = SurveyService(CruiseDb())

        name = "Falkor999"
        parent = 5
        platform = "popeye power"
        departure_port = "hong kong"
        arrival_port = "pearl harbor"
        start_date = datetime.datetime(2020, 5, 19, 1, 2, 3)
        end_date = datetime.datetime(2020, 5, 20, 1, 2, 3)

        model = CruiseSurvey(
            survey_name=name,
            parent=parent,
            platform_name=platform,
            departure_port=departure_port,
            arrival_port=arrival_port,
            start_date=start_date,
            end_date=end_date,
        )

        # Create new
        saved = self.survey_service.save_new_survey(model)

        self.assertTrue(isinstance(saved, Survey))
        self.assertEqual(saved.name, name)
        self.assertEqual(saved.parent, parent)
        self.assertEqual(saved.platform_name, platform)
        self.assertEqual(saved.departure_port, departure_port)
        self.assertEqual(saved.arrival_port, arrival_port)
        self.assertEqual(saved.start_date, datetime.datetime.isoformat(start_date))
        self.assertEqual(saved.end_date, datetime.datetime.isoformat(end_date))
        self.assertIsNotNone(saved.id)

        # Find existing
        found = self.survey_service.find_by_survey_name(model.survey_name)
        self.assertTrue(isinstance(found, Survey))
        self.assertEqual(found.name, name)
        self.assertEqual(found.parent, parent)
        self.assertEqual(found.platform_name, platform)
        self.assertEqual(found.departure_port, departure_port)
        self.assertEqual(found.arrival_port, arrival_port)
        self.assertEqual(found.start_date, datetime.datetime.isoformat(start_date))
        self.assertEqual(found.end_date, datetime.datetime.isoformat(end_date))
        self.assertIsNotNone(found.id)

        # Delete
        self.survey_service.delete_survey(found)
        deleted = self.survey_service.find_by_survey_name(name)
        self.assertIsNone(deleted)

    def test_file_format_service(self):
        file_format_service = FileFormatService(CruiseDb())
        file_formats = file_format_service.get_all_file_formats()

        self.assertEqual(167, len(file_formats))

    def test_file_type_service(self):
        file_type_service = FileTypeService(CruiseDb())
        file_types = file_type_service.get_all_file_types()

        self.assertEqual(6, len(file_types))

    def test_dataset_type_service(self):
        dataset_type_service = DatasetTypeService(CruiseDb())
        dataset_types = dataset_type_service.get_all_dataset_types()

        self.assertEqual(15, len(dataset_types))

    def test_version_description_service(self):
        version_description_service = VersionDescriptionService(CruiseDb())
        version_descriptions = (
            version_description_service.get_all_version_descriptions()
        )

        self.assertEqual(3, len(version_descriptions))

    def test_contact_service(self):
        contact_service = ContactService(CruiseDb())

        name = "Elizabeth Lobecker"
        org = "NOAA/OAR/OER/OEP"

        model = CruisePeopleAndSources(name=name, organization=org)

        # CREATE NEW
        saved = contact_service.save_new_contact(model)

        self.assertTrue(isinstance(saved, Contact))
        self.assertEqual(saved.name, name)
        self.assertEqual(saved.organization, org)
        self.assertIsNotNone(saved.id)

        # Find existing
        found = contact_service.find_by_name_and_organization(name, org)
        self.assertTrue(isinstance(found, Contact))
        self.assertEqual(found.name, name)
        self.assertEqual(found.organization, org)
        self.assertIsNotNone(found.id)

        # Delete
        contact_service.delete_contact(found)
        deleted = contact_service.find_by_name_and_organization(name, org)
        self.assertIsNone(deleted)

    def test_file_service(self):
        file_service = FileService(CruiseDb())
        dataset_service = DatasetService(CruiseDb())
        ConstInitializer.initialize_consts()

        dataset_model = create_test_dataset(
            other_id="02030057",
            dataset_name="KN159L5_SeaBeam2112",
            dataset_type_name="MB RAW",
            instruments="SeaBeam2112",
            platforms="Knorr",
            archive_date=datetime.datetime(2020, 5, 19, 1, 2, 3),
            surveys="KN159L5",
            projects="Project Manhattan",
            type_id=DTLookup.get_id(DatasetTypeConsts.MB_RAW),
        )
        dataset = dataset_service.save_new_dataset(dataset_model)

        model = create_test_file(
            file_name="/path/to/file/filename.mb.all",
            raw_size=52460436,
            publish="Y",
            collection_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
            publish_date=datetime.datetime(2020, 5, 18, 1, 2, 5),
            archive_date=datetime.datetime(2020, 5, 18, 11, 12, 13),
            temp_id=None,
            gzip_size=48460436,
            version_id=VDLookup.get_id_from_description("level_01"),
            format_id=FFLookup.get_id(FFLookup.REVERSE_LOOKUP["ASCII_TEXT"].alt_id),
            type_id=FTLookup.get_id("MB PRODUCT"),
        )

        model.dataset_id = dataset.id

        # CREATE NEW
        saved = file_service.save_new_file(model)

        self.assertTrue(isinstance(saved, File))

        self.assertEqual(model.file_name, saved.name)
        self.assertEqual(model.raw_size, saved.raw_size)
        self.assertEqual(model.publish, saved.publish)
        self.assertEqual(
            datetime.datetime.isoformat(model.collection_date), saved.collection_date
        )
        self.assertEqual(
            datetime.datetime.isoformat(model.publish_date), saved.publish_date
        )
        self.assertEqual(
            datetime.datetime.isoformat(model.archive_date), saved.archive_date
        )
        self.assertEqual(model.temp_id, saved.temp_id)
        self.assertEqual(model.gzip_size, saved.gzip_size)
        self.assertEqual(model.version_id, saved.version_id)
        self.assertEqual(model.format_id, saved.format_id)
        self.assertEqual(model.type_id, saved.type_id)

        self.assertIsNotNone(saved.id)

        # Find existing
        found = file_service.find_by_file_name(model.file_name)
        self.assertEqual(model.file_name, found.name)
        self.assertEqual(model.raw_size, found.raw_size)
        self.assertEqual(model.publish, found.publish)
        self.assertEqual(
            datetime.datetime.isoformat(model.collection_date), found.collection_date
        )
        self.assertEqual(
            datetime.datetime.isoformat(model.publish_date), found.publish_date
        )
        self.assertEqual(
            datetime.datetime.isoformat(model.archive_date), found.archive_date
        )
        self.assertEqual(model.temp_id, found.temp_id)
        self.assertEqual(model.gzip_size, found.gzip_size)
        self.assertEqual(model.version_id, found.version_id)
        self.assertEqual(model.format_id, found.format_id)
        self.assertEqual(model.type_id, found.type_id)
        self.assertIsNotNone(found.id)

        # Delete
        file_service.delete_file(found)
        deleted = file_service.find_by_file_name(model.file_name)
        dataset_service.delete_dataset(dataset)
        self.assertIsNone(deleted)

    def test_instrument_service(self):
        self.instrument_service = InstrumentService(CruiseDb())

        instrument_name = "EM122"
        docucomp_uuid = "05e94496-2ecc-437d-b875-6c037cb236b5"
        long_name = "Kongsberg EM122"

        model = CruiseInstrument(
            instrument_name=instrument_name,
            docucomp_uuid=docucomp_uuid,
            long_name=long_name,
        )

        # CREATE
        saved = self.instrument_service.save_new_instrument(model)

        self.assertTrue(isinstance(saved, Instrument))
        self.assertEqual(saved.name, instrument_name)
        self.assertEqual(saved.docucomp_uuid, docucomp_uuid)
        self.assertEqual(saved.long_name, long_name)
        self.assertIsNotNone(saved.id)

        # FIND
        found = self.instrument_service.find_by_instrument_name(instrument_name)

        self.assertTrue(isinstance(found, Instrument))
        self.assertEqual(found.name, instrument_name)
        self.assertEqual(found.docucomp_uuid, docucomp_uuid)
        self.assertEqual(found.long_name, long_name)
        self.assertIsNotNone(found.id, saved.id)

        # DELETE
        self.instrument_service.delete_instrument(found)
        self.assertIsNone(
            self.instrument_service.find_by_instrument_name(instrument_name)
        )

    def test_parameter_detail_service(self):
        parameter_detail_service = ParameterDetailService(CruiseDb())
        parameter_details = parameter_detail_service.get_all_parameter_details()

        self.assertEqual(132, len(parameter_details))

    def test_parameter_service(self):
        self.parameter_service = ParameterService(CruiseDb())
        # TODO

    def test_platform_service(self):
        self.platform_service = PlatformService(CruiseDb())

        internal_name = "neil_armstrong"
        platform_type = "ship"
        docucomp_uuid = "05e94496-2ecc-437d-b875-6c037cb236b5"
        long_name = "Neil Armstrong"
        designator = "AR"
        platform_name = "Neil Armstrong"

        model = CruisePlatform(
            internal_name=internal_name,
            platform_type=platform_type,
            docucomp_uuid=docucomp_uuid,
            long_name=long_name,
            designator=designator,
            platform_name=platform_name,
        )

        # CREATE
        saved = self.platform_service.save_new_platform(model)

        self.assertTrue(isinstance(saved, Platform))
        self.assertEqual(saved.internal_name, internal_name)
        self.assertEqual(saved.type, platform_type)
        self.assertEqual(saved.docucomp_uuid, docucomp_uuid)
        self.assertEqual(saved.long_name, long_name)
        self.assertEqual(saved.designator, designator)
        self.assertEqual(saved.name, platform_name)
        self.assertIsNotNone(saved.id)

        # FIND
        found = self.platform_service.find_by_internal_name(internal_name)

        self.assertTrue(isinstance(found, Platform))
        self.assertEqual(found.internal_name, internal_name)
        self.assertEqual(found.type, platform_type)
        self.assertEqual(found.docucomp_uuid, docucomp_uuid)
        self.assertEqual(found.long_name, long_name)
        self.assertEqual(found.designator, designator)
        self.assertEqual(found.name, platform_name)
        self.assertEqual(found.id, saved.id)

        # DELETE
        self.platform_service.delete_platform(found)
        self.assertIsNone(self.platform_service.find_by_internal_name(internal_name))

    def test_project_service(self):
        self.project_service = ProjectService(CruiseDb())

        project_name = "Neptune Spear"

        model = CruiseProject(project_name)

        # CREATE
        saved = self.project_service.save_new_project(model)

        self.assertTrue(isinstance(saved, Project))
        self.assertEqual(saved.name, project_name)
        self.assertIsNotNone(saved.id)

        # FIND
        found = self.project_service.find_by_project_name(project_name)

        self.assertTrue(isinstance(found, Project))
        self.assertEqual(found.name, project_name)
        self.assertEqual(found.id, saved.id)

        # DELETE
        self.project_service.delete_project(found)
        self.assertIsNone(self.project_service.find_by_project_name(project_name))


if __name__ == "__main__":
    unittest.main()
