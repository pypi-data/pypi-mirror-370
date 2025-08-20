import os
import yaml

from pathlib import Path


class OracleDbConfig(object):
    def __init__(self, config):
        self.server = config['server']
        self.port = config['port']
        self.user = config['user']
        self.password = config['password']
        self.service = config['service'] if config['service'] else None
        self.sid = config['sid'] if config['sid'] else None


class MbDatabaseProperties(OracleDbConfig):
    def __init__(self, config):
        self.pagesize = config['pagesize']
        super().__init__(config)


class CruiseDatabaseProperties(OracleDbConfig):
    def __init__(self, config):
        self.pooled = config['pooled']
        super().__init__(config)


class LogConfig(object):
    def __init__(self, config):
        self.log_root = config['log_root']
        self.log_path = config['log_dir']
        self.level = config['level']
        self.log_size_mb = config['log_size_mb']


class RunParameters(object):
    def __init__(self, config):
        self.migrate_shapes = config['migrate_shapes']
        self.max_queue_size = config['max_queue_size']
        self.file_processing_thread_count = config['file_processing_thread_count']
        self.batch_insert_mappings = config['batch_insert_mappings']
        self.batch_insertion_size = config['batch_insertion_size']
        self.cache_object_limit = config['cache_object_limit']
        self.queue_timeout = config['queue_timeout']


class Migrate(object):
    def __init__(self, config):
        self.extraneous = config['extraneous']
        self.legs = config['legs']
        self.zones = config['zones']
        self.regions = config['regions']
        self.survey_metadata = config['survey_metadata']
        self.standard = config['standard']


class Manifest(object):
    def __init__(self, config):
        self.default_query = config['default_query']
        self.use_list = config['use_target_list']
        self.target_migration_surveys = config['target_migration_surveys']
        self.survey_blacklist = config['survey_blacklist']
        MigrationProperties.SURVEY_QUERY = self.default_query


class MigrationProperties(object):
    SURVEY_QUERY = None
    PROJECT_ROOT = None
    SRC_DIR = None
    TESTS_DIR = None
    mb_db_config: MbDatabaseProperties = None
    cruise_db_config: CruiseDatabaseProperties = None
    log_config: LogConfig = None
    run_parameters: RunParameters = None
    migrate: Migrate = None
    manifest: Manifest = None

    def __init__(self, filename):
        with open(filename, 'r') as yaml_data_file:
            config = yaml.safe_load(yaml_data_file)

        MigrationProperties.mb_db_config = MbDatabaseProperties(config['multibeam_db'])
        MigrationProperties.cruise_db_config = CruiseDatabaseProperties(config['cruise_db'])
        MigrationProperties.log_config = LogConfig(config['log'])
        MigrationProperties.run_parameters = RunParameters(config['run_parameters'])
        MigrationProperties.migrate = Migrate(config['migrate'])
        MigrationProperties.manifest = Manifest(config['migration_manifest'])
        self.__set_project_dirs()

    @staticmethod
    def get_project_root():
        return MigrationProperties.PROJECT_ROOT

    @staticmethod
    def get_src_dir():
        return MigrationProperties.SRC_DIR

    @staticmethod
    def get_tests_dir():
        return MigrationProperties.TESTS_DIR

    @staticmethod
    def get_survey_query():
        return MigrationProperties.SURVEY_QUERY

    @staticmethod
    def __set_project_dirs():
        MigrationProperties.PROJECT_ROOT = Path(__file__).absolute().parent.parent.parent
        MigrationProperties.SRC_DIR = os.path.join(MigrationProperties.PROJECT_ROOT, 'src')
        MigrationProperties.TESTS_DIR = os.path.join(MigrationProperties.PROJECT_ROOT, 'tests')
