class Mapping:
    table = ""
    fields = []
    context = ""

    @classmethod
    def get_table(cls):
        return cls.table

    @classmethod
    def get_fields(cls):
        return cls.fields

    @classmethod
    def get_context(cls):
        return cls.context


class DatasetsSurveys(Mapping):
    table = "DATASET_SURVEYS"
    fields = ["DATASET_ID", "SURVEY_ID"]
    context = "survey mappings"


class DatasetScientist(Mapping):
    table = "SCIENTISTS"
    fields = ["DATASET_ID", "CONTACT_ID"]
    context = "scientist mappings"


class DatasetSource(Mapping):
    table = "SOURCES"
    fields = ["DATASET_ID", "CONTACT_ID"]
    context = "source mappings"


class DatasetPlatform(Mapping):
    table = "DATASET_PLATFORMS"
    fields = ["DATASET_ID", "PLATFORM_ID"]
    context = "platform mappings"


class DatasetInstrument(Mapping):
    table = "DATASET_INSTRUMENTS"
    fields = ["DATASET_ID", "INSTRUMENT_ID"]
    context = "instrument mappings"


class DatasetProject(Mapping):
    table = "DATASET_PROJECTS"
    fields = ["DATASET_ID", "PROJECT_ID"]
    context = "project mappings"


class FileAccessPath(Mapping):
    table = "FILE_ACCESS_PATHS"
    fields = ["FILE_ID", "PATH_ID"]
    context = "file access path mappings"

