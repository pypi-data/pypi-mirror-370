from mb_cruise_migration.db.cruise_db import CruiseDb
from mb_cruise_migration.framework.consts.nos_hydro_surveys import NosHydro
from mb_cruise_migration.framework.consts.survey_blacklist import SurveyBlacklist
from mb_cruise_migration.framework.resolvers.dataset_type_resolver import DTLookup
from mb_cruise_migration.framework.resolvers.platform_designator_resolver import DesignatorLookup
from mb_cruise_migration.framework.resolvers.file_format_resolver import FFLookup
from mb_cruise_migration.framework.resolvers.file_type_resolver import FTLookup
from mb_cruise_migration.framework.consts.parameter_detail_consts import PDLookup
from mb_cruise_migration.framework.resolvers.version_description_resolver import VDLookup
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.services.cruise_service import FileFormatService, FileTypeService, \
    DatasetTypeService, VersionDescriptionService, ParameterDetailService, PlatformService
from mb_cruise_migration.services.mb_service import MbService


class ConstInitializer(object):

    @classmethod
    def initialize_consts(cls):
        MigrationLog.log.info(f"Initializing const values into memory.")
        db = CruiseDb(pooled=False)
        MigrationLog.log.info(f"Loading file formats...")
        cls.__initialize_file_formats(db)
        MigrationLog.log.info(f"Loading file types...")
        cls.__initialize_cruise_file_types(db)
        MigrationLog.log.info(f"Loading dataset types...")
        cls.__initialize_cruise_dataset_types(db)
        MigrationLog.log.info(f"Loading version descriptions...")
        cls.__initialize_cruise_version_descriptions(db)
        MigrationLog.log.info(f"Loading parameter details...")
        cls.__initialize_cruise_parameter_details(db)
        MigrationLog.log.info(f"Loading platform designator reference...")
        cls.__initialize_cruise_designator_reference(db)
        MigrationLog.log.info(f"Loading survey blacklist from config...")
        cls.__initialize_mb_survey_blacklist()
        MigrationLog.log.info(f"Initializing class vars for NOS hydro surveys...")
        cls.__initialize_nos_hydro_list()
        MigrationLog.log.info(f"Done initializing const values used for migration.")

    @staticmethod
    def __initialize_file_formats(db):

        mb_ff_service = MbService()
        cruise_ff_service = FileFormatService(db)

        # pre-validate all mb file formats resolve to a cruise format with matching alt_id
        mb_file_formats = mb_ff_service.get_format_ids()
        FFLookup.pre_validate(cruise_ff_service, mb_file_formats)

        # pre-validate cruise formats before querying them and adding to lookup
        cruise_file_formats = cruise_ff_service.get_all_file_formats()
        FFLookup.set_ff_lookup(cruise_file_formats)

    @staticmethod
    def __initialize_cruise_file_types(db):
        file_type_service = FileTypeService(db)
        file_types = file_type_service.get_all_file_types()
        FTLookup.set_lookup(file_types)
        FTLookup.validate()

    @staticmethod
    def __initialize_cruise_dataset_types(db):
        dataset_type_service = DatasetTypeService(db)
        dataset_types = dataset_type_service.get_all_dataset_types()
        DTLookup.set_lookup(dataset_types)
        DTLookup.validate()

    @staticmethod
    def __initialize_cruise_version_descriptions(db):
        version_description_service = VersionDescriptionService(db)
        version_descriptions = version_description_service.get_all_version_descriptions()
        VDLookup.set_lookups(version_descriptions)
        VDLookup.validate()

    @staticmethod
    def __initialize_cruise_parameter_details(db):
        parameter_detail_service = ParameterDetailService(db)
        parameter_details = parameter_detail_service.get_all_parameter_details()
        PDLookup.set_lookup(parameter_details)
        PDLookup.validate(parameter_detail_service)

    @staticmethod
    def __initialize_cruise_designator_reference(db):
        platform_service = PlatformService(db)
        platforms = platform_service.get_all_platforms()
        DesignatorLookup.set_lookup(platforms)

    @staticmethod
    def __initialize_mb_survey_blacklist():
        SurveyBlacklist()

    @staticmethod
    def __initialize_nos_hydro_list():
        NosHydro()
