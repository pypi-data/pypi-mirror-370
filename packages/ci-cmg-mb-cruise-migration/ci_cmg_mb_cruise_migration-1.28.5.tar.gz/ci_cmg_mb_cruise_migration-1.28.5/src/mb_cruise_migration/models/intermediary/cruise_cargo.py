from mb_cruise_migration.models.cruise.cruise_dataset import CruiseDataset
from mb_cruise_migration.models.cruise.cruise_files import CruiseFile
from mb_cruise_migration.models.cruise.cruise_instruments import CruiseInstrument
from mb_cruise_migration.models.cruise.cruise_parameter import CruiseDatasetParameter
from mb_cruise_migration.models.cruise.cruise_people_and_sources import CruisePeopleAndSources
from mb_cruise_migration.models.cruise.cruise_platforms import CruisePlatform
from mb_cruise_migration.models.cruise.cruise_shape import CruiseShape
from mb_cruise_migration.models.cruise.cruise_surveys import CruiseSurvey


class CruiseDatasetCrate(object):
    def __init__(self, dataset=None, dataset_parameters=None, dataset_shape=None, dataset_sources=None, dataset_scientists=None, dataset_platforms=None, dataset_instruments=None):
        self.dataset: CruiseDataset = dataset
        self.dataset_parameters: [CruiseDatasetParameter] = dataset_parameters if dataset_parameters is not None else []
        self.dataset_shape: CruiseShape = dataset_shape
        self.dataset_sources: [CruisePeopleAndSources] = dataset_sources
        self.dataset_scientists: [CruisePeopleAndSources] = dataset_scientists
        self.dataset_platforms: [CruisePlatform] = dataset_platforms
        self.dataset_instruments: [CruiseInstrument] = dataset_instruments


class CruiseSurveyCrate(object):
    def __init__(self):
        self.cruise_survey: CruiseSurvey = None
        self.survey_parameters = []
        self.survey_shape = None


class CruiseProjectCrate(object):
    def __init__(self):
        self.project = None
        self.project_parameters = []


class CruiseFileCrate(object):
    def __init__(self):
        self.survey_name = None
        self.cruise_file_id = None
        self.file: CruiseFile = None
        self.file_parameters = []
        self.file_access_paths = None
        self.file_shape = None


class CruiseCargo(object):
    """Dataset-centric container for related cruise objects being migrated"""
    def __init__(
            self,
            dataset_crate: CruiseDatasetCrate,
            survey_crates: CruiseSurveyCrate,
            project_crates: CruiseProjectCrate,
            file_crates: [CruiseFileCrate]
            ):
        self.dataset_crate = dataset_crate
        self.related_survey_crate = survey_crates
        self.related_project_crate = project_crates
        self.related_file_crates = file_crates
