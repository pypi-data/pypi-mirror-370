import mb_cruise_migration.utility.common as util


class MbSurvey(object):
    def __init__(self,
                 ngdc_id,
                 chief_scientist,
                 departure_port,
                 arrival_port,
                 start_time,
                 end_time,
                 survey_name,
                 ship_name,
                 source,
                 nav1,
                 nav2,
                 instrument,
                 horizontal_datum,
                 vertical_datum,
                 tide_correction,
                 sound_velocity,
                 ship_owner,
                 project_name,
                 contact_id,
                 chief_sci_organization,
                 publish,
                 comments,
                 proprietary,
                 entered_date,
                 previous_state,
                 file_count,
                 track_length,
                 total_time,
                 bathy_beams,
                 amp_beams,
                 sidescans,
                 survey_size,
                 modify_date_data,
                 modify_date_metadata,
                 extract_metadata
                 ):
        self.__ngdc_id = ngdc_id
        self.__chief_scientist = chief_scientist
        self.__departure_port = departure_port
        self.__arrival_port = arrival_port
        self.__start_time = start_time
        self.__end_time = end_time
        self.__survey_name = survey_name
        self.__ship_name = ship_name
        self.__source = source
        self.__nav1 = nav1
        self.__nav2 = nav2
        self.__instrument = instrument
        self.__horizontal_datum = horizontal_datum
        self.__vertical_datum = vertical_datum
        self.__tide_correction = tide_correction
        self.__sound_velocity = sound_velocity
        self.__ship_owner = ship_owner
        self.__project_name = project_name
        self.__contact_id = contact_id
        self.__chief_sci_organization = chief_sci_organization
        self.__publish = publish
        self.__comments = comments
        self.__proprietary = proprietary
        self.__entered_date = entered_date
        self.__previous_state = previous_state
        self.__file_count = file_count
        self.__track_length = track_length
        self.__total_time = total_time
        self.__bathy_beams = bathy_beams
        self.__amp_beams = amp_beams
        self.__sidescans = sidescans
        self.__survey_size = survey_size
        self.__modify_date_data = modify_date_data
        self.__modify_date_metadata = modify_date_metadata
        self.__extract_metadata = extract_metadata

    @property
    def ngdc_id(self):
        return self.__ngdc_id

    @ngdc_id.setter
    def ngdc_id(self, ngdc_id):
        self.__ngdc_id = ngdc_id

    @property
    def chief_scientist(self):
        return self.__chief_scientist

    @chief_scientist.setter
    def chief_scientist(self, chief_scientist):
        self.__chief_scientist = chief_scientist

    @property
    def departure_port(self):
        return self.__departure_port

    @departure_port.setter
    def departure_port(self, departure_port):
        self.__departure_port = departure_port

    @property
    def arrival_port(self):
        return self.__arrival_port

    @arrival_port.setter
    def arrival_port(self, arrival_port):
        self.__arrival_port = arrival_port

    @property
    def start_time(self):
        return self.__start_time

    @start_time.setter
    def start_time(self, start_time):
        self.__start_time = start_time

    @property
    def end_time(self):
        return self.__end_time

    @end_time.setter
    def end_time(self, end_time):
        self.__end_time = end_time

    @property
    def survey_name(self):
        return self.__survey_name

    @survey_name.setter
    def survey_name(self, survey_name):
        self.__survey_name = survey_name

    @property
    def ship_name(self):
        return self.__ship_name

    @ship_name.setter
    def ship_name(self, ship_name):
        self.__ship_name = ship_name

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, source):
        self.__source = source

    @property
    def nav1(self):
        return self.__nav1

    @nav1.setter
    def nav1(self, nav1):
        self.__nav1 = nav1

    @property
    def nav2(self):
        return self.__nav2

    @nav2.setter
    def nav2(self, nav2):
        self.__nav2 = nav2

    @property
    def instrument(self):
        return self.__instrument

    @instrument.setter
    def instrument(self, instrument):
        self.__instrument = instrument

    @property
    def horizontal_datum(self):
        return self.__horizontal_datum

    @horizontal_datum.setter
    def horizontal_datum(self, horizontal_datum):
        self.__horizontal_datum = horizontal_datum

    @property
    def vertical_datum(self):
        return self.__vertical_datum

    @vertical_datum.setter
    def vertical_datum(self, vertical_datum):
        self.__vertical_datum = vertical_datum

    @property
    def tide_correction(self):
        return self.__tide_correction

    @tide_correction.setter
    def tide_correction(self, tide_correction):
        self.__tide_correction = tide_correction

    @property
    def sound_velocity(self):
        return self.__sound_velocity

    @sound_velocity.setter
    def sound_velocity(self, sound_velocity):
        self.__sound_velocity = sound_velocity

    @property
    def ship_owner(self):
        return self.__ship_owner

    @ship_owner.setter
    def ship_owner(self, ship_owner):
        self.__ship_owner = ship_owner

    @property
    def project_name(self):
        return self.__project_name

    @project_name.setter
    def project_name(self, project_name):
        self.__project_name = project_name

    @property
    def contact_id(self):
        return self.__contact_id

    @contact_id.setter
    def contact_id(self, contact_id):
        self.__contact_id = contact_id

    @property
    def chief_sci_organization(self):
        return self.__chief_sci_organization

    @chief_sci_organization.setter
    def chief_sci_organization(self, chief_sci_organization):
        self.__chief_sci_organization = chief_sci_organization

    @property
    def publish(self):
        return self.__publish

    @publish.setter
    def publish(self, publish):
        self.__publish = publish

    @property
    def comments(self):
        return self.__comments

    @comments.setter
    def comments(self, comments):
        self.__comments = comments

    @property
    def proprietary(self):
        return self.__proprietary

    @proprietary.setter
    def proprietary(self, proprietary):
        self.__proprietary = proprietary

    @property
    def entered_date(self):
        return self.__entered_date

    @entered_date.setter
    def entered_date(self, entered_date):
        self.__entered_date = entered_date

    @property
    def previous_state(self):
        return self.__previous_state

    @previous_state.setter
    def previous_state(self, previous_state):
        self.__previous_state = previous_state

    @property
    def file_count(self):
        return self.__file_count

    @file_count.setter
    def file_count(self, file_count):
        self.__file_count = file_count

    @property
    def track_length(self):
        return self.__track_length

    @track_length.setter
    def track_length(self, track_length):
        self.__track_length = track_length

    @property
    def total_time(self):
        return self.__total_time

    @total_time.setter
    def total_time(self, total_time):
        self.__total_time = total_time

    @property
    def bathy_beams(self):
        return self.__bathy_beams

    @bathy_beams.setter
    def bathy_beams(self, bathy_beams):
        self.__bathy_beams = bathy_beams

    @property
    def amp_beams(self):
        return self.__amp_beams

    @amp_beams.setter
    def amp_beams(self, amp_beams):
        self.__amp_beams = amp_beams

    @property
    def sidescans(self):
        return self.__sidescans

    @sidescans.setter
    def sidescans(self, sidescans):
        self.__sidescans = sidescans

    @property
    def survey_size(self):
        return self.__survey_size

    @survey_size.setter
    def survey_size(self, survey_size):
        self.__survey_size = survey_size

    @property
    def modify_date_data(self):
        return self.__modify_date_data

    @modify_date_data.setter
    def modify_date_data(self, modify_date_data):
        self.__modify_date_data = modify_date_data

    @property
    def modify_date_metadata(self):
        return self.__modify_date_metadata

    @modify_date_metadata.setter
    def modify_date_metadata(self, modify_date_metadata):
        self.__modify_date_metadata = modify_date_metadata

    @property
    def extract_metadata(self):
        return self.__extract_metadata

    @extract_metadata.setter
    def extract_metadata(self, extract_metadata):
        self.__extract_metadata = extract_metadata

    @staticmethod
    def build(survey: dict):
        return MbSurvey(
            survey['NGDC_ID'],
            util.dict_value_or_none(survey, 'CHIEF_SCIENTIST'),
            util.dict_value_or_none(survey, 'DEPARTURE_PORT'),
            util.dict_value_or_none(survey, 'ARRIVAL_PORT'),
            util.dict_value_or_none(survey, 'START_TIME'),
            util.dict_value_or_none(survey, 'END_TIME'),
            util.dict_value_or_none(survey, "SURVEY_NAME"),
            util.dict_value_or_none(survey, "SHIP_NAME"),
            survey['SOURCE'],
            util.dict_value_or_none(survey, 'NAV1'),
            util.dict_value_or_none(survey, 'NAV2'),
            util.dict_value_or_none(survey, 'INSTRUMENT'),
            util.dict_value_or_none(survey, 'HORIZONTAL_DATUM'),
            util.dict_value_or_none(survey, 'VERTICAL_DATUM'),
            util.dict_value_or_none(survey, 'TIDE_CORRECTION'),
            util.dict_value_or_none(survey, 'SOUND_VELOCITY'),
            util.dict_value_or_none(survey, 'SHIP_OWNER'),
            util.dict_value_or_none(survey, 'PROJECT_NAME'),
            util.dict_value_or_none(survey, 'CONTACT_ID'),
            util.dict_value_or_none(survey, 'CHIEF_SCI_ORGANIZATION'),
            util.dict_value_or_none(survey, 'PUBLISH'),
            util.dict_value_or_none(survey, 'COMMENTS'),
            util.dict_value_or_none(survey, 'PROPRIETARY'),
            util.dict_value_or_none(survey, 'ENTERED_DATE'),
            util.dict_value_or_none(survey, 'PREVIOUS_STATE'),
            util.dict_value_or_none(survey, 'FILE_COUNT'),
            util.dict_value_or_none(survey, 'TRACK_LENGTH'),
            util.dict_value_or_none(survey, 'TOTAL_TIME'),
            util.dict_value_or_none(survey, 'BATHY_BEAMS'),
            util.dict_value_or_none(survey, 'AMP_BEAMS'),
            util.dict_value_or_none(survey, 'SIDESCANS'),
            util.dict_value_or_none(survey, 'SURVEY_SIZE'),
            util.dict_value_or_none(survey, 'MODIFY_DATE_DATA'),
            util.dict_value_or_none(survey, 'MODIFY_DATE_METADATA'),
            util.dict_value_or_none(survey, 'EXTRACT_METADATA')
        )
