from typing import Optional

from mb_cruise_migration.framework.consts.dataset_type_consts import DatasetTypeConsts
from mb_cruise_migration.framework.consts.error_consts import ErrorConsts
from mb_cruise_migration.framework.consts.file_type_consts import FileTypeConsts
from mb_cruise_migration.framework.parsed_data_file import ParsedFilePath
from mb_cruise_migration.framework.resolvers.instrument_resolver import InstrumentLookup
from mb_cruise_migration.framework.resolvers.platform_designator_resolver import DesignatorLookup
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.logging.migration_report import MigrationReport
from mb_cruise_migration.models.intermediary.mb_cargo import MbFileCrate


def get_dataset_type(parsed_file: ParsedFilePath, version, is_nonpublic):
    type_found_in_datafile_path = parsed_file.identify_data_type_in_path()
    return DatasetTypeConsts.get_dataset_type(version, type_found_in_datafile_path, is_nonpublic)


def get_file_type_of_dataset(dataset_type):
    if dataset_type == DatasetTypeConsts.MB_RAW or dataset_type == DatasetTypeConsts.MB_RAW_NONPUBLIC:
        return FileTypeConsts.MB_RAW
    if dataset_type == DatasetTypeConsts.MB_PROCESSED or dataset_type == DatasetTypeConsts.MB_PROCESSED_NONPUBLIC:
        return FileTypeConsts.MB_PROCESSED
    if dataset_type == DatasetTypeConsts.MB_PRODUCT or dataset_type == DatasetTypeConsts.MB_PROCESSED_NONPUBLIC:
        return FileTypeConsts.MB_PRODUCT
    if dataset_type == DatasetTypeConsts.METADATA or dataset_type == DatasetTypeConsts.METADATA_NONPUBLIC:
        return FileTypeConsts.METADATA
    if dataset_type == DatasetTypeConsts.ANCILLARY or dataset_type == DatasetTypeConsts.ANCILLARY_NONPUBLIC:
        return FileTypeConsts.ANCILLARY
    if dataset_type == DatasetTypeConsts.DOCUMENT or dataset_type == DatasetTypeConsts.DOCUMENT_NONPUBLIC:
        return FileTypeConsts.DOCUMENT


def get_designator(date_file_platform, ship_name) -> Optional[str]:
    designator = DesignatorLookup.get_designator_by_parsed_data_file_platform_name(date_file_platform)
    if designator is None:
        return DesignatorLookup.get_designator_by_mb_survey_platform_name(ship_name)
    return designator


def build_platform_name(ship_name, designator):
    if designator is not None:
        return " ".join([ship_name, "(" + designator + ")"])

    return ship_name


def build_dataset_name(dataset_type, survey_name, instrument, provider):

    if dataset_type == DatasetTypeConsts.MB_RAW:
        return "_".join([survey_name, "RAW", instrument])
    elif dataset_type == DatasetTypeConsts.MB_RAW_NONPUBLIC:
        return "_".join([survey_name, "RAW", instrument, "NONPUBLIC"])
    elif dataset_type == DatasetTypeConsts.MB_PROCESSED:
        return "_".join([survey_name, "PROCESSED", instrument, provider])
    elif dataset_type == DatasetTypeConsts.MB_PROCESSED_NONPUBLIC:
        return "_".join([survey_name, "PROCESSED", instrument, provider, "NONPUBLIC"])
    elif dataset_type == DatasetTypeConsts.MB_PRODUCT:
        return "_".join([survey_name, "PRODUCTS", provider])
    elif dataset_type == DatasetTypeConsts.MB_PRODUCT_NONPUBLIC:
        return "_".join([survey_name, "PRODUCTS", provider, "NONPUBLIC"])
    elif dataset_type == DatasetTypeConsts.METADATA:
        return "_".join([survey_name, "METADATA"])
    elif dataset_type == DatasetTypeConsts.METADATA_NONPUBLIC:
        return "_".join([survey_name, "METADATA", "NONPUBLIC"])
    elif dataset_type == DatasetTypeConsts.ANCILLARY:
        return "_".join([survey_name, "ANCILLARY"])
    elif dataset_type == DatasetTypeConsts.ANCILLARY_NONPUBLIC:
        return "_".join([survey_name, "ANCILLARY", "NONPUBLIC"])
    else:
        raise RuntimeError(ErrorConsts.BAD_DATASET_TYPE)


def get_dataset_instrument(dataset_type: DatasetTypeConsts, mb_file: MbFileCrate, survey_instrument: str) -> Optional[str]:
    parsed_file = mb_file.mb_file.parsed_file
    if DatasetTypeConsts.dataset_has_associated_instrument(dataset_type):
        if parsed_file.has_instrument():
            data_file_instrument = parsed_file.identify_instrument_in_path()

            return InstrumentLookup.get_instrument_name_from_parsed_file_instrument(data_file_instrument)

        else:
            instrument = InstrumentLookup.get_instrument_name_from_mb_survey_instrument(survey_instrument)
            MigrationReport.increment_review_files_total()
            MigrationLog.log_file_for_manual_review(mb_file, instrument)

            return instrument

    return None


def dataset_has_shape(dataset_type: DatasetTypeConsts) -> bool:
    if dataset_type == DatasetTypeConsts.MB_RAW or dataset_type == DatasetTypeConsts.MB_RAW_NONPUBLIC:
        return True
    if dataset_type == DatasetTypeConsts.MB_PROCESSED or dataset_type == DatasetTypeConsts.MB_PROCESSED_NONPUBLIC:
        return True
    if dataset_type == DatasetTypeConsts.MB_PRODUCT or dataset_type == DatasetTypeConsts.MB_PRODUCT_NONPUBLIC:
        return True

    return False
