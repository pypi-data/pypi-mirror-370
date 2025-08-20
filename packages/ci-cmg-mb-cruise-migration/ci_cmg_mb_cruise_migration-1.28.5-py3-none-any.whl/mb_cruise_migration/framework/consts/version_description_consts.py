class VersionDescriptionConsts(object):
    RAW = "level_00"
    PROCESSED = "level_01"
    PRODUCT = "level_02"

    @staticmethod
    def version_description_consts():
        return {
            "RAW": VersionDescriptionConsts.RAW,
            "PROCESSED": VersionDescriptionConsts.PROCESSED,
            "PRODUCT": VersionDescriptionConsts.PRODUCT,
        }
