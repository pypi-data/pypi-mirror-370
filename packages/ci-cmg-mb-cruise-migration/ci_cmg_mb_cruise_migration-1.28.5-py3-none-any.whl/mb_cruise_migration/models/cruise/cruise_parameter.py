class CruiseParameter(object):
    def __init__(self, parameter_detail_name, value, xml, json, parameter_detail_id, last_update_date, last_updated_by, id):
        self.parameter_detail_name = parameter_detail_name
        self.parameter_detail_id = parameter_detail_id
        self.value = value
        self.xml = xml
        self.json = json
        self.last_update_date = last_update_date
        self.last_updated_by = last_updated_by
        self.id = id


class CruiseSurveyParameter(CruiseParameter):
    def __init__(self, parameter_detail_name, value, xml, json, parameter_detail_id=None, last_update_date=None, last_updated_by=None, survey_id=None, id=None):
        super(CruiseSurveyParameter, self).__init__(parameter_detail_name, value, xml, json, parameter_detail_id, last_update_date, last_updated_by, id)
        self.survey_id = survey_id

    def set_parameter_id(self, survey_id):
        self.survey_id = survey_id
        return self


class CruiseProjectParameter(CruiseParameter):
    def __init__(self, parameter_detail_name, value, xml, json, parameter_detail_id=None, last_update_date=None, last_updated_by=None, project_id=None,  id=None):
        super(CruiseProjectParameter, self).__init__(parameter_detail_name, value, xml, json, parameter_detail_id, last_update_date, last_updated_by, id)
        self.project_id = project_id

    def set_parameter_id(self, project_id):
        self.project_id = project_id
        return self


class CruiseDatasetParameter(CruiseParameter):
    def __init__(self, parameter_detail_name, value, xml, json, parameter_detail_id=None, last_update_date=None, last_updated_by=None, dataset_id=None,  id=None):
        super(CruiseDatasetParameter, self).__init__(parameter_detail_name, value, xml, json, parameter_detail_id, last_update_date, last_updated_by, id)
        self.dataset_id = dataset_id

    def set_parameter_id(self, dataset_id):
        self.dataset_id = dataset_id
        return self


class CruiseFileParameter(CruiseParameter):
    def __init__(self, parameter_detail_name, value, xml, json, parameter_detail_id=None, last_update_date=None, last_updated_by=None, file_id=None, id=None):
        super(CruiseFileParameter, self).__init__(parameter_detail_name, value, xml, json, parameter_detail_id, last_update_date, last_updated_by, id)
        self.file_id = file_id

    def set_parameter_id(self, file_id):
        self.file_id = file_id
