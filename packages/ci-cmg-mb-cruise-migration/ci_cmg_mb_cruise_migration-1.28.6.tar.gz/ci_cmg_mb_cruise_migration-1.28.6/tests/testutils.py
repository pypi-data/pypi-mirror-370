import datetime
import os
import shutil

from mb_cruise_migration.db.cruise_db import CruiseDb
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.models.cruise.cruise_access_path import CruiseAccessPath
from mb_cruise_migration.models.cruise.cruise_dataset import CruiseDataset
from mb_cruise_migration.models.cruise.cruise_files import CruiseFile
from mb_cruise_migration.models.cruise.cruise_instruments import CruiseInstrument
from mb_cruise_migration.models.cruise.cruise_parameter import CruiseParameter
from mb_cruise_migration.models.cruise.cruise_people_and_sources import CruisePeopleAndSources
from mb_cruise_migration.models.cruise.cruise_platforms import CruisePlatform
from mb_cruise_migration.models.cruise.cruise_projects import CruiseProject
from mb_cruise_migration.models.cruise.cruise_shape import CruiseShape
from mb_cruise_migration.models.cruise.cruise_surveys import CruiseSurvey
from mb_cruise_migration.services.mb_service import MbService


def load_test_mb_data(test_data_file):
    test_db_container_name = "mb-test-db-1"
    test_schema_user = "MB"
    test_schema_pass = "letmein"

    command = f'docker exec --user oracle {test_db_container_name} ' \
              f'sqlplus {test_schema_user}/{test_schema_pass}@XEPDB1 ' \
              f'@/home/oracle/setup-files/test_data/{test_data_file}'
    os.system(command)


def reset_properties():
    MigrationProperties.SURVEY_QUERY = None  # important, or will persist between tests.
    MigrationProperties.PROJECT_ROOT = None
    MigrationProperties.SRC_DIR = None
    MigrationProperties.TESTS_DIR = None
    MigrationProperties.mb_db_config = None
    MigrationProperties.cruise_db_config = None
    MigrationProperties.log_config = None
    MigrationProperties.run_parameters = None
    MigrationProperties.migrate = None
    MigrationProperties.manifest = None


def clean_mb_db():
    mb_service: MbService = MbService()
    for table in ["SURVEY", "MBINFO_FILE_TSQL", "NGDCID_AND_FILE", "SURVEY_REFERENCE", "MBINFO_SURVEY_TSQL"]:
        mb_service.delete_table_rows(table)


def clean_cruise_db():
    db = CruiseDb().db
    db.query("DELETE FROM cruise.SURVEY_PARAMETERS")
    db.query("DELETE FROM cruise.PROJECT_PARAMETERS")
    db.query("DELETE FROM cruise.DATASET_PARAMETERS")
    db.query("DELETE FROM cruise.FILE_PARAMETERS")
    db.query("DELETE FROM cruise.DATASET_PROJECTS")
    db.query("DELETE FROM cruise.DATASET_PLATFORMS")
    db.query("DELETE FROM cruise.DATASET_INSTRUMENTS")
    db.query("DELETE FROM cruise.DATASET_SURVEYS")
    db.query("DELETE FROM cruise.SCIENTISTS")
    db.query("DELETE FROM cruise.SOURCES")
    db.query("DELETE FROM cruise.dataset_shapes")
    db.query("DELETE FROM cruise.survey_shapes")
    db.query("DELETE FROM cruise.FILE_SHAPES")
    db.query("DELETE FROM cruise.FILE_ACCESS_PATHS")
    db.query("DELETE FROM cruise.ACCESS_PATHS")
    db.query("DELETE FROM cruise.PROJECTS")
    db.query("DELETE FROM cruise.PLATFORMS")
    db.query("DELETE FROM cruise.PEOPLE_AND_SOURCES")
    db.query("DELETE FROM cruise.shapes")
    db.query("DELETE FROM cruise.INSTRUMENTS")
    db.query("DELETE FROM cruise.FILES")
    db.query("DELETE FROM cruise.SURVEYS")
    db.query("DELETE FROM cruise.DATASETS")


def get_cruise_surveys():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.SURVEYS")


def get_cruise_datasets():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.DATASETS")


def get_survey_parameters():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.SURVEY_PARAMETERS")


def get_project_parameters():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.PROJECT_PARAMETERS")


def get_dataset_parameters():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.DATASET_PARAMETERS")


def get_file_parameters():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.FILE_PARAMETERS")


def get_dataset_projects():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.DATASET_PROJECTS")


def get_dataset_platforms():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.DATASET_PLATFORMS")


def get_dataset_instrument():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.DATASET_INSTRUMENTS")


def get_dataset_surveys():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.DATASET_SURVEYS")


def get_scientists():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.SCIENTISTS")


def get_sources():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.SOURCES")


def get_dataset_shapes():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.dataset_shapes")


def get_survey_shapes():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.survey_shapes")


def get_file_shapes():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.FILE_SHAPES")


def get_file_access_paths():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.FILE_ACCESS_PATHS")


def get_access_paths():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.ACCESS_PATHS")


def get_projects():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.PROJECTS")


def get_platforms():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.PLATFORMS")


def get_people_and_sources():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.PEOPLE_AND_SOURCES")


def get_shapes():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.shapes")


def get_instruments():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.INSTRUMENTS")


def get_files():
    db = CruiseDb().db
    return db.query("SELECT * FROM cruise.FILES")


def build_insert_survey_command(ngdc_id):
    return f"INSERT INTO MB.SURVEY (" \
           f"NGDC_ID) " \
           f"VALUES ({ngdc_id})"


def build_insert_file_command(ngdc_id):
    return f"INSERT INTO MB.NGDCID_AND_FILE (" \
           f"NGDC_ID) " \
           f"VALUES ({ngdc_id})"


def build_insert_mb_info_command(ngdc_id):
    return f"INSERT INTO MB.MBINFO_FILE_TSQL (" \
           f"NGDC_ID) " \
           f"VALUES ({ngdc_id})"


def build_insert_survey_reference_command(ngdc_id, doi, abstract, purpose, project_url, created_by, last_updated_by, download_ur):
    return f"INSERT INTO MB.SURVEY_REFERENCE (" \
           f"NGDC_ID, DOI, ABSTRACT, PURPOSE, PROJECT_URL, CREATED_BY, LAST_UPDATED_BY, DOWNLOAD_URL) " \
           f"VALUES ({ngdc_id}, {doi}, {abstract}, {purpose}, {project_url}, {created_by}, {last_updated_by}, {download_ur})"

def build_insert_mb_info_format_command(ngdc_id):
    return f"INSERT INTO MB.MBINFO_FORMATS (" \
           f"NGDC_ID) " \
           f"VALUES ({ngdc_id})"


def create_test_access_path(path, path_type):
    return CruiseAccessPath(path, path_type)


def create_test_file(file_name, raw_size, publish, collection_date, publish_date, archive_date, temp_id, gzip_size, version_id, type_id, format_id):
    return CruiseFile(
        file_name=file_name,
        raw_size=raw_size,
        publish=publish,
        collection_date=collection_date,
        publish_date=publish_date,
        version_id=version_id,
        type_id=type_id,
        format_id=format_id,
        archive_date=archive_date,
        temp_id=temp_id,
        gzip_size=gzip_size,
    )


def create_test_survey(name, parent, platform, departure_port, arrival_port, start_date, end_date):
    return CruiseSurvey(
        survey_name=name,
        parent=parent,
        platform_name=platform,
        departure_port=departure_port,
        arrival_port=arrival_port,
        start_date=start_date,
        end_date=end_date
    )


def create_test_instrument(instrument_name, docucomp_uuid, long_name):
    return CruiseInstrument(
        instrument_name=instrument_name,
        docucomp_uuid=docucomp_uuid,
        long_name=long_name
    )


def create_test_platform(internal_name, platform_type, docucomp_uuid, long_name, designator, platform_name):
    return CruisePlatform(
        internal_name=internal_name,
        platform_type=platform_type,
        docucomp_uuid=docucomp_uuid,
        long_name=long_name,
        designator=designator,
        platform_name=platform_name
    )


def create_test_project(project_name):
    return CruiseProject(project_name)


def create_test_dataset(other_id, dataset_name, dataset_type_name, instruments, platforms, archive_date, surveys, projects, type_id):
    return CruiseDataset(
        other_id=other_id,
        dataset_name=dataset_name,
        dataset_type_name=dataset_type_name,
        instruments=instruments,
        platforms=platforms,
        archive_date=datetime.datetime(2020, 5, 19, 1, 2, 3),
        surveys=surveys,
        projects=projects,
        dataset_type_id=type_id
    )


def create_test_source(organization):
    return CruisePeopleAndSources(
        organization=organization
    )


def create_test_scientist(name, organization):
    return CruisePeopleAndSources(
        name=name,
        organization=organization,
    )


def create_test_parameter(parameter, value, detail_id):
    return CruiseParameter(
            id=None,
            parameter_detail_name=parameter,
            parameter_detail_id=detail_id,
            value=value,
            xml=None,
            json=None,
            last_update_date=None,
            last_updated_by=None,
        )


def create_test_shape(shape, shape_type, geom_type):
    return CruiseShape(
        shape=shape,
        shape_type=shape_type,
        geom_type=geom_type,
    )


def delete_test_logs():

    if os.path.exists("log"):
        shutil.rmtree("log")
