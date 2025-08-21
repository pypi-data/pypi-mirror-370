from typing import Optional

from mb_cruise_migration.framework.consts.dataset_type_consts import DatasetTypeConsts
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.logging.migration_report import MigrationReport
from mb_cruise_migration.models.intermediary.mb_cargo import MbCargo, MbSurveyCrate
from mb_cruise_migration.models.intermediary.transfer import Transfer
from mb_cruise_migration.models.intermediary.cruise_cargo import CruiseCargo
from mb_cruise_migration.framework.consts.error_consts import ErrorConsts
from mb_cruise_migration.utility.common import strip_none


class TransferStation(object):
    """
    Orchestrates generation of dataset objects and creation of cruise schema objects
    """

    def __init__(self, shipment: MbCargo):
        self.survey_context: MbSurveyCrate = shipment.mb_survey_crate
        self.related_files = shipment.related_mb_file_crates
        self.transfers = []

    def transfer(self) -> Optional[list[CruiseCargo]]:
        MigrationLog.log_tracking(f"Transferring files from MB survey {self.survey_context.mb_survey.survey_name} to dataset-centric CRUISE structure")
        try:
            self.transfers = [Transfer.build(self.survey_context, file_context) for file_context in self.related_files]
            self.__consolidate_transfers()
            self.__populate_data_across_datasets()

            return [transfer.load_cruise_cargo() for transfer in self.transfers]

        except (RuntimeError, ValueError) as e:
            MigrationReport.add_failed_survey(self.survey_context, e)
            MigrationLog.log_failed_survey(self.survey_context.mb_survey.survey_name, e)

            return None

    def __consolidate_transfers(self):
        MigrationLog.log.debug("consolidating datasets generated from files...")
        transfers = strip_none(self.transfers)

        if len(transfers) == 0:
            raise RuntimeError(ErrorConsts.NO_VALID_DATASETS)

        if len(transfers) == 1:
            return

        reduced = []
        for transfer in transfers:
            self.__add_to_reduced_list(transfer, reduced)

        self.transfers = self.__fill_gaps(reduced)

    @staticmethod
    def __add_to_reduced_list(consider: Transfer, confirmed: [Transfer]):
        for keeper in confirmed:
            if keeper.prefab == consider.prefab:
                for file in consider.mb_file_crates:
                    keeper.mb_file_crates.append(file)
                if keeper.prefab.platform is None:
                    keeper.prefab.platform = consider.prefab.platform
                if keeper.prefab.datafile_path_platform_name is None:
                    keeper.prefab.datafile_path_platform_name = consider.prefab.datafile_path_platform_name
                if keeper.prefab.datafile_path_platform_type is None:
                    keeper.prefab.datafile_path_platform_type = consider.prefab.datafile_path_platform_type
                return

        confirmed.append(consider)
        return

    @staticmethod
    def __fill_gaps(reduced: [Transfer]):
        for i in reduced:
            if i.prefab.platform is None:
                for j in reduced:
                    if j.prefab is not None:
                        i.prefab.platform = j.prefab.platform
                        i.prefab.datafile_path_platform_name = j.prefab.datafile_path_platform_name
                        i.prefab.datafile_path_platform_type = j.prefab.datafile_path_platform_type
                        break
        return reduced

    def __populate_data_across_datasets(self):
        source_transfer = self.__get_raw_processed_or_product()
        consolidated_transfers = self.transfers

        for transfer in consolidated_transfers:
            platform = transfer.prefab.platform
            dataset_type = transfer.prefab.dataset_type_name
            metadata = DatasetTypeConsts.METADATA
            metadata_nonpublic = DatasetTypeConsts.METADATA_NONPUBLIC
            if dataset_type == metadata or dataset_type == metadata_nonpublic and platform is None and source_transfer is not None:
                transfer.prefab.platform = source_transfer.prefab.platform
                transfer.prefab.datafile_path_platform_name = source_transfer.prefab.datafile_path_platform_name
                transfer.prefab.datafile_path_platform_type = source_transfer.prefab.datafile_path_platform_type

    def __get_raw_processed_or_product(self) -> Transfer:
        for transfer in self.transfers:
            if transfer.prefab.dataset_type_name == DatasetTypeConsts.MB_RAW:
                return transfer
            if transfer.prefab.dataset_type_name == DatasetTypeConsts.MB_RAW_NONPUBLIC:
                return transfer
            if transfer.prefab.dataset_type_name == DatasetTypeConsts.MB_PROCESSED:
                return transfer
            if transfer.prefab.dataset_type_name == DatasetTypeConsts.MB_PROCESSED_NONPUBLIC:
                return transfer
            if transfer.prefab.dataset_type_name == DatasetTypeConsts.MB_PRODUCT:
                return transfer
            if transfer.prefab.dataset_type_name == DatasetTypeConsts.MB_PRODUCT_NONPUBLIC:
                return transfer

        survey = self.transfers[0].mb_survey_crate.mb_survey.survey_name
        MigrationLog.log_no_raw_processed_product(self.transfers)
        raise RuntimeError(f"Cannot migrate survey {survey} without at least raw, processed, or product data.")
