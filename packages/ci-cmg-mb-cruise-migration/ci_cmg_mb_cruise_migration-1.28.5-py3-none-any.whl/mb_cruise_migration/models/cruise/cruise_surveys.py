class CruiseSurvey(object):
    def __init__(self, survey_name, parent, platform_name, start_date, end_date, departure_port, arrival_port, id=None, creation_date=None, last_update=None):
        self.id = id
        self.survey_name = survey_name
        self.parent = parent
        self.platform_name = platform_name
        self.start_date = start_date
        self.end_date = end_date
        self.departure_port = departure_port
        self.arrival_port = arrival_port
        self.creation_date = creation_date
        self.last_update = last_update
