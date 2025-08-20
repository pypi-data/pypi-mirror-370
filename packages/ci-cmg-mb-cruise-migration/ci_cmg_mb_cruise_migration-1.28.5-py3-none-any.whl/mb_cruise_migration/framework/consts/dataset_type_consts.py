from mb_cruise_migration.framework.consts.data_file_consts import (
    PathVersion,
    PathDataType,
)


class DatasetTypeConsts(object):
    WCSD_RAW = "WCSD Raw"
    WCSD_PROCESSED = "WCSD Processed"
    WCSD_PRODUCT = "WCSD Product"
    MB_RAW = "MB RAW"
    MB_PROCESSED = "MB PROCESSED"
    MB_PRODUCT = "MB PRODUCT"
    MB_RAW_NONPUBLIC = "MB RAW NONPUBLIC"
    MB_PROCESSED_NONPUBLIC = "MB RAW NONPUBLIC"
    MB_PRODUCT_NONPUBLIC = "MB PRODUCT NONPUBLIC"
    ANCILLARY = "ANCILLARY"
    DOCUMENT = "DOCUMENT"
    METADATA = "METADATA"
    ANCILLARY_NONPUBLIC = "ANCILLARY NONPUBLIC"
    DOCUMENT_NONPUBLIC = "DOCUMENT NONPUBLIC"
    METADATA_NONPUBLIC = "METADATA NONPUBLIC"

    @staticmethod
    def dataset_type_consts():
        return {
            "WCSD_RAW": DatasetTypeConsts.WCSD_RAW,
            "WCSD_PROCESSED": DatasetTypeConsts.WCSD_PROCESSED,
            "WCSD_PRODUCT": DatasetTypeConsts.WCSD_PRODUCT,
            "MB_RAW": DatasetTypeConsts.MB_RAW,
            "MB_PROCESSED": DatasetTypeConsts.MB_PROCESSED,
            "MB_PRODUCT": DatasetTypeConsts.MB_PRODUCT,
            "MB_RAW_NONPUBLIC": DatasetTypeConsts.MB_RAW_NONPUBLIC,
            "MB_PROCESSED_NONPUBLIC": DatasetTypeConsts.MB_PROCESSED_NONPUBLIC,
            "MB_PRODUCT_NONPUBLIC": DatasetTypeConsts.MB_PRODUCT_NONPUBLIC,
            "ANCILLARY": DatasetTypeConsts.ANCILLARY,
            "DOCUMENT": DatasetTypeConsts.DOCUMENT,
            "METADATA": DatasetTypeConsts.METADATA,
            "ANCILLARY_NONPUBLIC": DatasetTypeConsts.ANCILLARY_NONPUBLIC,
            "DOCUMENT_NONPUBLIC": DatasetTypeConsts.DOCUMENT_NONPUBLIC,
            "METADATA_NONPUBLIC": DatasetTypeConsts.METADATA_NONPUBLIC,
        }

    @staticmethod
    def dataset_has_associated_instrument(dataset_type):
        if (
            dataset_type == DatasetTypeConsts.MB_RAW
            or dataset_type == DatasetTypeConsts.MB_RAW_NONPUBLIC
        ):
            return True
        if (
            dataset_type == DatasetTypeConsts.MB_PROCESSED
            or dataset_type == DatasetTypeConsts.MB_PROCESSED_NONPUBLIC
        ):
            return True
        if (
            dataset_type == DatasetTypeConsts.MB_PRODUCT
            or dataset_type == DatasetTypeConsts.MB_PRODUCT_NONPUBLIC
        ):
            return False
        if (
            dataset_type == DatasetTypeConsts.METADATA
            or dataset_type == DatasetTypeConsts.METADATA_NONPUBLIC
        ):
            return False
        if (
            dataset_type == DatasetTypeConsts.ANCILLARY
            or dataset_type == DatasetTypeConsts.ANCILLARY_NONPUBLIC
        ):
            return False
        if (
            dataset_type == DatasetTypeConsts.DOCUMENT
            or dataset_type == DatasetTypeConsts.DOCUMENT_NONPUBLIC
        ):
            return False

        raise ValueError(
            "Invalid dataset type provided or dataset type provided is not handled."
        )

    @staticmethod
    def get_dataset_type(version, data_type_dir, is_nonpublic):

        # raw
        if (
            version == PathVersion.VERSION1
            and data_type_dir == PathDataType.MB
            and is_nonpublic is False
        ):
            return DatasetTypeConsts.MB_RAW
        if (
            version == PathVersion.VERSION1
            and data_type_dir == PathDataType.MB
            and is_nonpublic is True
        ):
            return DatasetTypeConsts.MB_RAW_NONPUBLIC

        # processed
        if (
            version == PathVersion.VERSION2
            and data_type_dir == PathDataType.MB
            and is_nonpublic is False
        ):
            return DatasetTypeConsts.MB_PROCESSED
        if (
            version == PathVersion.VERSION3
            and data_type_dir == PathDataType.MB
            and is_nonpublic is False
        ):
            return DatasetTypeConsts.MB_PROCESSED
        if (
            version == PathVersion.VERSION2
            and data_type_dir == PathDataType.MB
            and is_nonpublic is True
        ):
            return DatasetTypeConsts.MB_PROCESSED_NONPUBLIC
        if (
            version == PathVersion.VERSION3
            and data_type_dir == PathDataType.MB
            and is_nonpublic is True
        ):
            return DatasetTypeConsts.MB_PROCESSED_NONPUBLIC

        # product
        if (
            version == PathVersion.VERSION1
            and data_type_dir == PathDataType.PRODUCTS
            and is_nonpublic is False
        ):
            return DatasetTypeConsts.MB_PRODUCT
        if (
            version == PathVersion.VERSION2
            and data_type_dir == PathDataType.PRODUCTS
            and is_nonpublic is False
        ):
            return DatasetTypeConsts.MB_PRODUCT
        if (
            version == PathVersion.VERSION3
            and data_type_dir == PathDataType.PRODUCTS
            and is_nonpublic is False
        ):
            return DatasetTypeConsts.MB_PRODUCT
        if (
            version == PathVersion.VERSION1
            and data_type_dir == PathDataType.PRODUCTS
            and is_nonpublic is True
        ):
            return DatasetTypeConsts.MB_PRODUCT_NONPUBLIC
        if (
            version == PathVersion.VERSION2
            and data_type_dir == PathDataType.PRODUCTS
            and is_nonpublic is True
        ):
            return DatasetTypeConsts.MB_PRODUCT_NONPUBLIC
        if (
            version == PathVersion.VERSION3
            and data_type_dir == PathDataType.PRODUCTS
            and is_nonpublic is True
        ):
            return DatasetTypeConsts.MB_PRODUCT_NONPUBLIC

        # metadata
        if data_type_dir == PathDataType.METADATA and is_nonpublic is False:
            return DatasetTypeConsts.METADATA
        if data_type_dir == PathDataType.METADATA and is_nonpublic is True:
            return DatasetTypeConsts.METADATA_NONPUBLIC

        # ancillary
        if data_type_dir == PathDataType.ANCILLARY and is_nonpublic is False:
            return DatasetTypeConsts.ANCILLARY
        if data_type_dir == PathDataType.ANCILLARY and is_nonpublic is True:
            return DatasetTypeConsts.ANCILLARY_NONPUBLIC

        raise RuntimeError(
            f"Unable to determine dataset type from version {version}, data type dir {data_type_dir}, and is_nonpublic {is_nonpublic}"
        )
