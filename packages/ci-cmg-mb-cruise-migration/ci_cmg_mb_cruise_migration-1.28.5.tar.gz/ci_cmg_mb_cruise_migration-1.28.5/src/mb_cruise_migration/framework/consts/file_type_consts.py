class FileTypeConsts(object):
    MB_RAW = "MB RAW"
    MB_PROCESSED = "MB PROCESSED"
    MB_PRODUCT = "MB PRODUCT"
    ANCILLARY = "ANCILLARY"
    DOCUMENT = "DOCUMENT"
    METADATA = "METADATA"

    @staticmethod
    def file_type_consts():
        return {
            "MB_RAW": FileTypeConsts.MB_RAW,
            "MB_PROCESSED": FileTypeConsts.MB_PROCESSED,
            "MB_PRODUCT": FileTypeConsts.MB_PRODUCT,
            "ANCILLARY": FileTypeConsts.ANCILLARY,
            "DOCUMENT": FileTypeConsts.DOCUMENT,
            "METADATA": FileTypeConsts.METADATA,
        }
