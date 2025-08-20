import os.path
import unittest

from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.logging.migration_report import MigrationReport
from mb_cruise_migration.migration_properties import MigrationProperties
from testutils import delete_test_logs


class TestLoggers(unittest.TestCase):
    MigrationProperties("config_test.yaml")
    MigrationLog()
    MigrationReport()

    def test_file_creation(self):
        MigrationLog.log.info("THIS IS A TEST")
        MigrationLog.review.info("THIS IS A TEST")
        MigrationReport.report.info("THIS IS A TEST")

        assert os.path.exists("log")
        sub_dir = os.listdir("log")[0]
        assert os.path.exists(os.path.join("log", sub_dir, "log"))
        assert os.path.exists(os.path.join("log", sub_dir, "audit"))
        assert os.path.exists(os.path.join("log", sub_dir, "report"))

        delete_test_logs()
