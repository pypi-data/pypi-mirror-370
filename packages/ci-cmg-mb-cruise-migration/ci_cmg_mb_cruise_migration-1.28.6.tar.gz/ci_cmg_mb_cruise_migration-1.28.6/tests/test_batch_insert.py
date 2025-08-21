import unittest

import datetime

from mb_cruise_migration.db.cruise_db import CruiseDb
from mb_cruise_migration.db.cruise_connection import CruiseConnection
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.models.cruise.cruise_dataset import CruiseDataset
from mb_cruise_migration.models.cruise.cruise_files import CruiseFile
from mb_cruise_migration.services.cruise_service import FileService, DatasetService
from mb_cruise_migration.utility.common import normalize_date
from testutils import get_file_parameters


class TestBatchInsert(unittest.TestCase):
    MigrationProperties("config_test.yaml")

    def setUp(self) -> None:
        self.tearDown()

    def tearDown(self) -> None:
        cruise_db = CruiseDb()
        cruise_db.db.query("DELETE FROM cruise.FILE_PARAMETERS")

    def test_insert_file_format_parameters(self):

        cruise_connection = CruiseConnection()

        dataset_service = DatasetService(CruiseDb())

        dataset_model = CruiseDataset(
          other_id="02030057",
          dataset_name="KN159L5_SeaBeam2112",
          dataset_type_name="MB RAW",
          instruments="SeaBeam2112",
          platforms="Knorr",
          archive_date=normalize_date(datetime.datetime(2020, 5, 19, 1, 2, 3, 579410)),
          surveys="KN159L5",
          projects="Project Manhattan",
          dataset_type_id=1
        )

        # Create new
        dataset_entity = dataset_service.save_new_dataset(dataset_model)

        file_service = FileService(CruiseDb())

        file_model = CruiseFile(
          file_name="/path/to/file/filename.mb.all",
          raw_size=52460436,
          publish="Y",
          collection_date=normalize_date(datetime.datetime(2020, 5, 18, 1, 2, 4, 579410)),
          publish_date=normalize_date(datetime.datetime(2020, 5, 18, 1, 2, 5, 579410)),
          version_id=1,
          type_id=1,
          format_id=32,
          archive_date=normalize_date(datetime.datetime(2020, 5, 18, 11, 12, 13, 579410)),
          temp_id=None,
          gzip_size=48460436,
          dataset_id=dataset_entity.id,
        )

        file_entity = file_service.save_new_file(file_model)

        query = "INSERT INTO CRUISE.FILE_PARAMETERS (FILE_PARAMETER_ID, PARAMETER_DETAIL_ID, FILE_ID, VALUE, XML, JSON, LAST_UPDATE_DATE, LAST_UPDATED_BY) VALUES (:FILE_PARAMETER_ID, :PARAMETER_DETAIL_ID, :FILE_ID, :VALUE, :XML, :JSON, TO_DATE(:LAST_UPDATE_DATE,'YYYY-MM-DD\"T\"HH24:MI:SS'), TO_DATE(:LAST_UPDATED_BY,'YYYY-MM-DD\"T\"HH24:MI:SS'))"

        data = [
          (None, 68, file_entity.id, '58', None, None, normalize_date(datetime.datetime(2023, 2, 2, 23, 9, 48, 579393)), None),
          (None, 23, file_entity.id, '199', None, None, normalize_date(datetime.datetime(2023, 2, 2, 23, 9, 48, 579410)), None),
          (None, 24, file_entity.id, '85968', None, None, normalize_date(datetime.datetime(2023, 2, 2, 23, 9, 48, 579420)), None),
          (None, 24, file_entity.id, '85968', None, None, normalize_date(datetime.datetime(2023, 2, 2, 23, 9, 48, 579429)), None),
          (None, 25, file_entity.id, '37828', None, None, normalize_date(datetime.datetime(2023, 2, 2, 23, 9, 48, 579438)), None),
          (None, 27, file_entity.id, '0', None, None, normalize_date(datetime.datetime(2023, 2, 2, 23, 9, 48, 579448)), None)
        ]

        cruise_connection.executemany(query, data)

        file_parameters = get_file_parameters()
        self.assertEqual(6, len(file_parameters))
