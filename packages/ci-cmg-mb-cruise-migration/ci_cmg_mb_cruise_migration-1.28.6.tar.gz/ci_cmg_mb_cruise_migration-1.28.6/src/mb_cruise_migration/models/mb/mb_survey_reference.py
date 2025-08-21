import mb_cruise_migration.utility.common as util


class SurveyReference(object):
    def __init__(self,
                 ngdc_id,
                 doi,
                 abstract,
                 purpose,
                 project_url,
                 create_date,
                 created_by,
                 last_update_date,
                 last_updated_by,
                 download_url
                 ):
        self.__ngdc_id = ngdc_id
        self.__doi = doi
        self.__abstract = abstract
        self.__purpose = purpose
        self.__project_url = project_url
        self.__create_date = create_date
        self.__created_by = created_by
        self.__last_update_date = last_update_date
        self.__last_updated_by = last_updated_by
        self.__download_url = download_url

    @property
    def ngdc_id(self):
        return self.__ngdc_id

    @ngdc_id.setter
    def ngdc_id(self, ngdc_id):
        self.__ngdc_id = ngdc_id

    @property
    def doi(self):
        return self.__doi

    @doi.setter
    def doi(self, doi):
        self.__doi = doi

    @property
    def abstract(self):
        return self.__abstract

    @abstract.setter
    def abstract(self, abstract):
        self.__abstract = abstract

    @property
    def purpose(self):
        return self.__purpose

    @purpose.setter
    def purpose(self, purpose):
        self.__purpose = purpose

    @property
    def project_url(self):
        return self.__project_url

    @project_url.setter
    def project_url(self, project_url):
        self.__project_url = project_url

    @property
    def create_date(self):
        return self.__create_date

    @create_date.setter
    def create_date(self, create_date):
        self.__create_date = create_date

    @property
    def created_by(self):
        return self.__created_by

    @created_by.setter
    def created_by(self, created_by):
        self.__created_by = created_by

    @property
    def last_update_date(self):
        return self.__last_update_date

    @last_update_date.setter
    def last_update_date(self, last_update_date):
        self.__last_update_date = last_update_date

    @property
    def last_updated_by(self):
        return self.__last_updated_by

    @last_updated_by.setter
    def last_updated_by(self, last_updated_by):
        self.__last_updated_by = last_updated_by

    @property
    def download_url(self):
        return self.__download_url

    @download_url.setter
    def download_url(self, download_url):
        self.__download_url = download_url

    @staticmethod
    def build(survey: dict):
        return SurveyReference(
            survey['NGDC_ID'],
            util.dict_value_or_none(survey, 'DOI'),
            util.dict_value_or_none(survey, 'ABSTRACT'),
            util.dict_value_or_none(survey, 'PURPOSE'),
            util.dict_value_or_none(survey, 'PROJECT_URL'),
            util.dict_value_or_none(survey, 'CREATE_DATE'),
            util.dict_value_or_none(survey, 'CREATED_BY'),
            util.dict_value_or_none(survey, 'LAST_UPDATE_DATE'),
            util.dict_value_or_none(survey, 'LAST_UPDATED_BY'),
            util.dict_value_or_none(survey, 'DOWNLOAD_URL')
        )
