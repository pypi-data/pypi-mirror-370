from mb_cruise_migration.models.intermediary.cruise_cargo import CruiseSurveyCrate


class MigratingSurvey(object):
    def __init__(self, survey_crate: CruiseSurveyCrate):
        self.survey_name = survey_crate.cruise_survey.survey_name
        self.survey_crate = survey_crate
        self.problem_identified = False
        self.problem_message = ""
        self.migrated_datasets = 0
        self.migrated_files = 0
        self.expected_files = 0

    def update(self, problem_flag, problem_message, num_datasets, actual_files, expected_files):
        self.problem_identified = problem_flag
        self.problem_message = problem_message + self.problem_message
        self.migrated_datasets += num_datasets
        self.migrated_files += actual_files
        self.expected_files += expected_files

    def __hash__(self):
        return hash(self.survey_name)

    def __eq__(self, obj):
        if isinstance(obj, MigratingSurvey):
            return self.survey_name == obj.survey_name
        return False

    def __ne__(self, obj):
        if not isinstance(obj, MigratingSurvey):
            return self.survey_name != obj.survey_name
        return False
