class Prefab(object):
    def __init__(
            self,
            other_id,
            dataset_name,
            dataset_type_name,
            instrument,
            platform,
            archive_date,
            survey,
            project,
            path_platform_type,
            path_platform_name,
            level,
            platform_designator,
            is_nonpublic,
            files_type,
            last_updated
            ):
        # dataset model values
        self.other_id = other_id
        self.dataset_name = dataset_name
        self.dataset_type_name = dataset_type_name
        self.instrument = instrument
        self.platform = platform
        self.archive_date = archive_date
        self.survey = survey
        self.project = project
        self.datafile_path_platform_type = path_platform_type
        self.datafile_path_platform_name = path_platform_name
        self.datafile_level = level
        self.platform_designator = platform_designator
        self.is_nonpublic = is_nonpublic
        self.files_type = files_type
        self.last_updated = last_updated

    def __eq__(self, obj):
        IS_EQUAL = True
        NOT_EQUAL = False

        if not isinstance(obj, Prefab):
            return NOT_EQUAL

        if obj.dataset_name != self.dataset_name:
            return NOT_EQUAL
        if obj.dataset_type_name != self.dataset_type_name:
            return NOT_EQUAL

        # no case where same survey names exist between different platforms
        # if obj.platform != self.platform:
        #     return NOT_EQUAL

        # already validated via dataset_type
        # if obj.is_nonpublic != self.is_nonpublic:
        #     return NOT_EQUAL

        # already validated via dataset name comparison
        # if obj.instrument != self.instrument:
        #     return NOT_EQUAL
        # if obj.survey != self.survey:
        #     return NOT_EQUAL

        return IS_EQUAL

    def __ne__(self, obj):
        IS_EQUAL = False
        NOT_EQUAL = True

        if not isinstance(obj, Prefab):
            return IS_EQUAL

        if obj.dataset_name == self.dataset_name:
            return IS_EQUAL
        if obj.dataset_type_name == self.dataset_type_name:
            return IS_EQUAL

        # no case where same survey names exist between different platforms
        # if obj.platform == self.platform:
        #     return IS_EQUAL

        # already validated via dataset_type
        # if obj.is_nonpublic == self.is_nonpublic:
        #     return IS_EQUAL

        # already validated via dataset name comparison
        # if obj.instrument == self.instrument:
        #     return IS_EQUAL
        # if obj.survey == self.survey:
        #     return IS_EQUAL

        return NOT_EQUAL
