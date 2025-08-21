import oracledb

from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.migration_properties import MigrationProperties


class MbDb(object):
    def __init__(self):
        config = MigrationProperties.mb_db_config
        self.__dsn_string = oracledb.makedsn(config.server, config.port, sid=config.sid, service_name=config.service)
        self.__user = config.user
        self.__password = config.password

    def get_connection(self):
        try:
            return oracledb.connect(
              user=self.__user,
              password=self.__password,
              dsn=self.__dsn_string
            )
        except Exception as e:
            MigrationLog.log_exception(e)
            print("WARNING DB failed to connect. Script closing", e)
            raise e

    def query(self, command, data=None):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                result = cursor.execute(command, data)
                connection.commit()
                return result

            except Exception as e:
                MigrationLog.log.error("Statement execution failed due to error:")
                MigrationLog.log_exception(e)
                raise RuntimeError(f"statement execution failed for {command}")

    def fetch_one(self, command, data=None, row_factory=True):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                result = cursor.execute(command, data)
                names = [c[0] for c in result.description]
                row = result.fetchone()
                if row_factory and row:
                    return self.row_factory(names, row)[0]
                else:
                    return row

            except Exception as e:
                MigrationLog.log.error("Statement execution failed due to error:")
                MigrationLog.log_exception(e)
                raise RuntimeError(f"statement execution failed for {command}")

    def fetch_shape(self, command, shape_field, data=None, row_factory=True):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                result = cursor.execute(command, data)
                names = [c[0] for c in result.description]
                row = result.fetchone()
                if row_factory and row:
                    row_result = self.row_factory(names, row)[0]
                else:
                    row_result = row
                shape = None if row_result is None else row_result[shape_field]
                return None if shape is None else shape.read()

            except Exception as e:
                MigrationLog.log.error("Statement execution failed due to error:")
                MigrationLog.log_exception(e)
                raise RuntimeError(f"statement execution failed for {command}")

    def fetch_all(self, command, data=None, row_factory=True):
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                result = cursor.execute(command, data)
                names = [c[0] for c in result.description]
                rows = result.fetchall()
                if row_factory and rows:
                    return self.row_factory(names, rows)
                else:
                    return rows

            except Exception as e:
                MigrationLog.log.error("Statement execution failed due to error:")
                MigrationLog.log_exception(e)
                raise RuntimeError(f"statement execution failed for {command}")

    def columns(self, command=None):
        with self.get_connection() as connection:
            cursor = connection.cursor()
            if command:
                cursor.execute(command)
            names = [c[0] for c in cursor.description]
            return names

    @staticmethod
    def row_factory(names, data):
        #  Create list of dictionaries of query results with filed name as keys.
        row_list = []
        if not isinstance(data, list):
            data = [data]
        for row in data:
            row_dict = {}
            temp_map = zip(names, row)
            for item in temp_map:
                row_dict[item[0]] = item[1]
            row_list.append(row_dict)

        return row_list
