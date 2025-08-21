class CruiseDataset(object):
    def __init__(
            self,
            other_id,
            dataset_name,
            dataset_type_name,
            instruments,
            platforms,
            archive_date,
            surveys,
            projects,
            dataset_type_id,
            doi=None,
            last_update=None,
            id=None,
            ):

        self.other_id = other_id
        self.dataset_name = dataset_name
        self.dataset_type_name = dataset_type_name
        self.instruments = instruments
        self.platforms = platforms
        self.doi = doi
        self.archive_date = archive_date
        self.last_update = last_update
        self.surveys = surveys
        self.projects = projects
        self.id = id
        self.dataset_type_id = dataset_type_id
