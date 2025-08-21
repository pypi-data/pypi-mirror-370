import time

from oracledb import DatabaseError
from mb_cruise_migration.db.mb_db import MbDb
from mb_cruise_migration.db.query_builder import QueryBuilder
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.models.mb.mb_mbinfo_formats import MbFileFormat
from mb_cruise_migration.models.mb.mb_survey import MbSurvey
from mb_cruise_migration.models.mb.mb_ngdcid_and_file import MbFile
from mb_cruise_migration.models.mb.mb_mbinfo_file_tsql import MbInfo
from mb_cruise_migration.models.mb.mb_survey_reference import SurveyReference


def retry_on_disconnect(func):
    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (DatabaseError, OSError):
            time.sleep(2)
            try:
                return func(self, *args, **kwargs)
            except (DatabaseError, OSError) as e:
                raise RuntimeError(f"Failed on retry: {str(e)}")
    return wrap


class MbService(object):
    def __init__(self):
        self.db = MbDb()
        self.schema = 'MB'
        self.query_builder = QueryBuilder(self.schema)

    @retry_on_disconnect
    def get_survey_count(self, view):
        results = self.db.fetch_one(self.query_builder.select_query_size(f"({view})"))
        return results['COUNT(*)']

    @retry_on_disconnect
    def get_format_ids(self):
        query = self.query_builder.select_all("MBINFO_FORMATS")
        results = self.db.fetch_all(query)

        return [MbFileFormat.build(file_format) for file_format in results]

    @retry_on_disconnect
    def get_survey_page(self, skip: int, limit: int) -> [MbSurvey]:
        survey_query = MigrationProperties.get_survey_query()
        query = self.query_builder.select_subset(survey_query, skip, limit)
        MigrationLog.log_mb_survey_query(query)
        results = self.db.fetch_all(query)

        return [MbSurvey.build(survey) for survey in results] if results else None

    @retry_on_disconnect
    def get_survey_reference(self, ngdc_id: str) -> SurveyReference:
        query, value = self.query_builder.select_all_where_fields_match("SURVEY_REFERENCE", {'NGDC_ID': ngdc_id})
        result = self.db.fetch_one(query, value)

        return SurveyReference.build(result) if result else None

    @retry_on_disconnect
    def get_survey_shape(self, ngdc_id) -> str:
        shape_field = 'SHAPE_GEN'
        query, value = self.query_builder.select_survey_shape("MBINFO_SURVEY_TSQL", ngdc_id, shape_field)
        shape = self.db.fetch_shape(query, shape_field, value)

        if not shape:
            shape_field = 'SHAPE'
            query, value = self.query_builder.select_survey_shape("MBINFO_SURVEY_TSQL", ngdc_id, shape_field)
            shape = self.db.fetch_shape(query, shape_field, value)

        return shape

    @retry_on_disconnect
    def get_survey_files(self, ngdc_id: str) -> [MbFile]:
        query, values = self.query_builder.select_all_where_fields_match("NGDCID_AND_FILE", {'NGDC_ID': ngdc_id})
        results = self.db.fetch_all(query, values)

        return [MbFile.build(file) for file in results] if results else None

    @retry_on_disconnect
    def get_mb_info(self, data_file: str) -> MbInfo:
        query, value = self.query_builder.select_all_where_fields_match("MBINFO_FILE_TSQL", {'DATA_FILE': data_file})
        result = self.db.fetch_one(query, value)

        return MbInfo.build(result) if result else None

    @retry_on_disconnect
    def get_file_shape(self, data_file: str) -> str:
        query, value = self.query_builder.select_file_shape("MBINFO_FILE_TSQL", data_file)
        return self.db.fetch_shape(query, 'SHAPE', value)

    @retry_on_disconnect
    def delete_table_rows(self, table):
        query = self.query_builder.delete_all_rows(table)
        self.db.query(query)

    @retry_on_disconnect
    def insert_row(self, table, row):
        query, data = self.query_builder.insert(table, row)
        self.db.query(query, data)
