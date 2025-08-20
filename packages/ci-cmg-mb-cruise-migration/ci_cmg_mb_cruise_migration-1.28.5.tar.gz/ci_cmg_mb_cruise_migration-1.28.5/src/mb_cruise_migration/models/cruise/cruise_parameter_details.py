class CruiseParameterDetail(object):
    def __init__(self, parameter, parameter_type, description, id=None, last_update_date=None, last_updated_by=None):
        self.parameter_id = id
        self.parameter = parameter
        self.parameter_type = parameter_type
        self.description = description
        self.last_update_date = last_update_date
        self.last_updated_by = last_updated_by
