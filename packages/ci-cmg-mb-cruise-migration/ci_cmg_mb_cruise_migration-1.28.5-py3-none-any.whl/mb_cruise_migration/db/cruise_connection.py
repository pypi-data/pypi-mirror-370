import oracledb

from mb_cruise_migration.logging.batch_error import BatchError
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.migration_properties import MigrationProperties


class CruiseConnection(object):
    def __init__(self):
        self.config = MigrationProperties.cruise_db_config
        self.dsn_string = oracledb.makedsn(self.config.server, self.config.port, sid=self.config.sid, service_name=self.config.service)

    def get_connection(self):
        try:
            return oracledb.connect(
                user=self.config.user,
                password=self.config.password,
                dsn=self.dsn_string
            )
        except Exception as e:
            MigrationLog.log_exception(e)
            print("WARNING DB failed to connect. Script closing", e)
            raise e

    def get_type_obj(self, type):
        with self.get_connection() as connection:
            try:
                connection.gettype(type)
            except Exception as e:
                MigrationLog.log.error("Failed to get connection type for string: " + type)
                MigrationLog.log_exception(e)
                raise RuntimeError(f"Failed to get connection type for string: " + type)

    def query(self, command, data=None):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                result = cursor.execute(command, data)
                return result.fetchone()

            except Exception as e:
                MigrationLog.log.error("Statement execution failed due to error:")
                MigrationLog.log_exception(e)
                raise RuntimeError(f"statement execution failed for {command}")

    def execute(self, command, data=None):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                cursor.execute(command, data)
                connection.commit()
            except Exception as e:
                MigrationLog.log.error("Statement execution failed due to error:")
                MigrationLog.log_exception(e)
                raise RuntimeError(f"statement execution failed for {command}")

    def executemany(self, command, data=None):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                cursor.executemany(command, data, batcherrors=True)
                errors: [BatchError] = []
                for error in cursor.getbatcherrors():
                    errors.append(BatchError(error.message, error.offset))
                connection.commit()
                return errors
            except Exception as e:
                connection.rollback()
            raise
