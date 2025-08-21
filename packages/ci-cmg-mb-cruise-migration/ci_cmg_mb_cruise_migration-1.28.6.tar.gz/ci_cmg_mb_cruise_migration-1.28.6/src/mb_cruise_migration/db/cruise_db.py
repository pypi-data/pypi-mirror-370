from ncei_cruise_schema.orm.cx_oracle import CxOraclePersistenceEngine

from mb_cruise_migration.db.oracledb_pooled import OracledbPooledPersistenceEngine
from mb_cruise_migration.migration_properties import MigrationProperties


class CruiseDb(object):
    def __init__(self, pooled=False):
        config = MigrationProperties.cruise_db_config
        if pooled:
            self.db = OracledbPooledPersistenceEngine(
                host=config.server,
                port=config.port,
                sid=config.sid,
                service_name=config.service,
                user=config.user,
                password=config.password,
                debug_query=True,
                debug_params=True,
            )
        else:
            self.db = CxOraclePersistenceEngine(
                host=config.server,
                port=config.port,
                sid=config.sid,
                service_name=config.service,
                user=config.user,
                password=config.password,
                debug_query=True,
                debug_params=True,
            )
