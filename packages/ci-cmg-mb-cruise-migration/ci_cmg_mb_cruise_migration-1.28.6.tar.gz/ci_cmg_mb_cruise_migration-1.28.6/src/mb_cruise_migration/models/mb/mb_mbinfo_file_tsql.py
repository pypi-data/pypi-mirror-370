import mb_cruise_migration.utility.common as util


class MbInfo(object):
    def __init__(self,
                 data_file,
                 ngdc_id,
                 mbio_format_id,
                 record_count,
                 bathy_beams,
                 bb_good,
                 bb_zero,
                 bb_flagged,
                 amp_beams,
                 ab_good,
                 ab_zero,
                 ab_flagged,
                 sidescans,
                 ss_good,
                 ss_zero,
                 ss_flagged,
                 total_time,
                 track_length,
                 avg_speed,
                 start_time,
                 start_lon,
                 start_lat,
                 start_depth,
                 start_speed,
                 start_heading,
                 start_sonar_depth,
                 start_sonar_alt,
                 end_time,
                 end_lon,
                 end_lat,
                 end_depth,
                 end_speed,
                 end_heading,
                 end_sonar_depth,
                 end_sonar_alt,
                 min_lon,
                 max_lon,
                 min_lat,
                 max_lat,
                 min_sonar_depth,
                 max_sonar_depth,
                 min_sonar_alt,
                 max_sonar_alt,
                 min_depth,
                 max_depth,
                 min_amp,
                 max_amp,
                 min_sidescan,
                 max_sidescan,
                 objectid,
                 shape,
                 publish,
                 previous_state,
                 shape_gen
                 ):
        self.__data_file = data_file
        self.__ngdc_id = ngdc_id
        self.__mbio_format_id = mbio_format_id
        self.__record_count = record_count
        self.__bathy_beams = bathy_beams
        self.__bb_good = bb_good
        self.__bb_zero = bb_zero
        self.__bb_flagged = bb_flagged
        self.__amp_beams = amp_beams
        self.__ab_good = ab_good
        self.__ab_zero = ab_zero
        self.__ab_flagged = ab_flagged
        self.__sidescans = sidescans
        self.__ss_good = ss_good
        self.__ss_zero = ss_zero
        self.__ss_flagged = ss_flagged
        self.__total_time = total_time
        self.__track_length = track_length
        self.__avg_speed = avg_speed
        self.__start_time = start_time
        self.__start_lon = start_lon
        self.__start_lat = start_lat
        self.__start_depth = start_depth
        self.__start_speed = start_speed
        self.__start_heading = start_heading
        self.__start_sonar_depth = start_sonar_depth
        self.__start_sonar_alt = start_sonar_alt
        self.__end_time = end_time
        self.__end_lon = end_lon
        self.__end_lat = end_lat
        self.__end_depth = end_depth
        self.__end_speed = end_speed
        self.__end_heading = end_heading
        self.__end_sonar_depth = end_sonar_depth
        self.__end_sonar_alt = end_sonar_alt
        self.__min_lon = min_lon
        self.__max_lon = max_lon
        self.__min_lat = min_lat
        self.__max_lat = max_lat
        self.__min_sonar_depth = min_sonar_depth
        self.__max_sonar_depth = max_sonar_depth
        self.__min_sonar_alt = min_sonar_alt
        self.__max_sonar_alt = max_sonar_alt
        self.__min_depth = min_depth
        self.__max_depth = max_depth
        self.__min_amp = min_amp
        self.__max_amp = max_amp
        self.__min_sidescan = min_sidescan
        self.__max_sidescan = max_sidescan
        self.__objectid = objectid
        self.__shape = shape
        self.__publish = publish
        self.__previous_state = previous_state
        self.__shape_gen = shape_gen

    @property
    def data_file(self):
        return self.__data_file

    @data_file.setter
    def data_file(self, data_file):
        self.__data_file = data_file

    @property
    def ngdc_id(self):
        return self.__ngdc_id

    @ngdc_id.setter
    def ngdc_id(self, ngdc_id):
        self.__ngdc_id = ngdc_id

    @property
    def mbio_format_id(self):
        return self.__mbio_format_id

    @mbio_format_id.setter
    def mbio_format_id(self, mbio_format_id):
        self.__mbio_format_id = mbio_format_id

    @property
    def record_count(self):
        return self.__record_count

    @record_count.setter
    def record_count(self, record_count):
        self.__record_count = record_count

    @property
    def bathy_beams(self):
        return self.__bathy_beams

    @bathy_beams.setter
    def bathy_beams(self, bathy_beams):
        self.__bathy_beams = bathy_beams

    @property
    def bb_good(self):
        return self.__bb_good

    @bb_good.setter
    def bb_good(self, bb_good):
        self.__bb_good = bb_good

    @property
    def bb_zero(self):
        return self.__bb_zero

    @bb_zero.setter
    def bb_zero(self, bb_zero):
        self.__bb_zero = bb_zero

    @property
    def bb_flagged(self):
        return self.__bb_flagged

    @bb_flagged.setter
    def bb_flagged(self, bb_flagged):
        self.__bb_flagged = bb_flagged

    @property
    def amp_beams(self):
        return self.__amp_beams

    @amp_beams.setter
    def amp_beams(self, amp_beams):
        self.__amp_beams = amp_beams

    @property
    def ab_good(self):
        return self.__ab_good

    @ab_good.setter
    def ab_good(self, ab_good):
        self.__ab_good = ab_good

    @property
    def ab_zero(self):
        return self.__ab_zero

    @ab_zero.setter
    def ab_zero(self, ab_zero):
        self.__ab_zero = ab_zero

    @property
    def ab_flagged(self):
        return self.__ab_flagged

    @ab_flagged.setter
    def ab_flagged(self, ab_flagged):
        self.__ab_flagged = ab_flagged

    @property
    def sidescans(self):
        return self.__sidescans

    @sidescans.setter
    def sidescans(self, sidescans):
        self.__sidescans = sidescans

    @property
    def ss_good(self):
        return self.__ss_good

    @ss_good.setter
    def ss_good(self, ss_good):
        self.__ss_good = ss_good

    @property
    def ss_zero(self):
        return self.__ss_zero

    @ss_zero.setter
    def ss_zero(self, ss_zero):
        self.__ss_zero = ss_zero

    @property
    def ss_flagged(self):
        return self.__ss_flagged

    @ss_flagged.setter
    def ss_flagged(self, ss_flagged):
        self.__ss_flagged = ss_flagged

    @property
    def total_time(self):
        return self.__total_time

    @total_time.setter
    def total_time(self, total_time):
        self.__total_time = total_time

    @property
    def track_length(self):
        return self.__track_length

    @track_length.setter
    def track_length(self, track_length):
        self.__track_length = track_length

    @property
    def avg_speed(self):
        return self.__avg_speed

    @avg_speed.setter
    def avg_speed(self, avg_speed):
        self.__avg_speed = avg_speed

    @property
    def start_time(self):
        return self.__start_time

    @start_time.setter
    def start_time(self, start_time):
        self.__start_time = start_time

    @property
    def start_lon(self):
        return self.__start_lon

    @start_lon.setter
    def start_lon(self, start_lon):
        self.__start_lon = start_lon

    @property
    def start_lat(self):
        return self.__start_lat

    @start_lat.setter
    def start_lat(self, start_lat):
        self.__start_lat = start_lat

    @property
    def start_depth(self):
        return self.__start_depth

    @start_depth.setter
    def start_depth(self, start_depth):
        self.__start_depth = start_depth

    @property
    def start_speed(self):
        return self.__start_speed

    @start_speed.setter
    def start_speed(self, start_speed):
        self.__start_speed = start_speed

    @property
    def start_heading(self):
        return self.__start_heading

    @start_heading.setter
    def start_heading(self, start_heading):
        self.__start_heading = start_heading

    @property
    def start_sonar_depth(self):
        return self.__start_sonar_depth

    @start_sonar_depth.setter
    def start_sonar_depth(self, start_sonar_depth):
        self.__start_sonar_depth = start_sonar_depth

    @property
    def start_sonar_alt(self):
        return self.__start_sonar_alt

    @start_sonar_alt.setter
    def start_sonar_alt(self, start_sonar_alt):
        self.__start_sonar_alt= start_sonar_alt

    @property
    def end_time(self):
        return self.__end_time

    @end_time.setter
    def end_time(self, end_time):
        self.__end_time = end_time

    @property
    def end_lon(self):
        return self.__end_lon

    @end_lon.setter
    def end_lon(self, end_lon):
        self.__end_lon = end_lon

    @property
    def end_lat(self):
        return self.__end_lat

    @end_lat.setter
    def end_lat(self, end_lat):
        self.__end_lat = end_lat

    @property
    def end_depth(self):
        return self.__end_depth

    @end_depth.setter
    def end_depth(self, end_depth):
        self.__end_depth = end_depth

    @property
    def end_speed(self):
        return self.__end_speed

    @end_speed.setter
    def end_speed(self, end_speed):
        self.__end_speed = end_speed

    @property
    def end_heading(self):
        return self.__end_heading

    @end_heading.setter
    def end_heading(self, end_heading):
        self.__end_heading = end_heading

    @property
    def end_sonar_depth(self):
        return self.__end_sonar_depth

    @end_sonar_depth.setter
    def end_sonar_depth(self, end_sonar_depth):
        self.__end_sonar_depth = end_sonar_depth

    @property
    def end_sonar_alt(self):
        return self.__end_sonar_alt

    @end_sonar_alt.setter
    def end_sonar_alt(self, end_sonar_alt):
        self.__end_sonar_alt = end_sonar_alt

    @property
    def min_lon(self):
        return self.__min_lon

    @min_lon.setter
    def min_lon(self, min_lon):
        self.__min_lon = min_lon

    @property
    def max_lon(self):
        return self.__max_lon

    @max_lon.setter
    def max_lon(self, max_lon):
        self.__max_lon = max_lon

    @property
    def min_lat(self):
        return self.__min_lat

    @min_lat.setter
    def min_lat(self, min_lat):
        self.__min_lat = min_lat

    @property
    def max_lat(self):
        return self.__max_lat

    @max_lat.setter
    def max_lat(self, max_lat):
        self.__max_lat = max_lat

    @property
    def min_sonar_depth(self):
        return self.__min_sonar_depth

    @min_sonar_depth.setter
    def min_sonar_depth(self, min_sonar_depth):
        self.__min_sonar_depth = min_sonar_depth

    @property
    def max_sonar_depth(self):
        return self.__max_sonar_depth

    @max_sonar_depth.setter
    def max_sonar_depth(self, max_sonar_depth):
        self.__max_sonar_depth = max_sonar_depth

    @property
    def min_sonar_alt(self):
        return self.__min_sonar_alt

    @min_sonar_alt.setter
    def min_sonar_alt(self, min_sonar_alt):
        self.__min_sonar_alt = min_sonar_alt

    @property
    def max_sonar_alt(self):
        return self.__max_sonar_alt

    @max_sonar_alt.setter
    def max_sonar_alt(self, max_sonar_alt):
        self.__max_sonar_alt = max_sonar_alt

    @property
    def min_depth(self):
        return self.__min_depth

    @min_depth.setter
    def min_depth(self, min_depth):
        self.__min_depth = min_depth

    @property
    def max_depth(self):
        return self.__max_depth

    @max_depth.setter
    def max_depth(self, max_depth):
        self.__max_depth = max_depth

    @property
    def min_amp(self):
        return self.__min_amp

    @min_amp.setter
    def min_amp(self, min_amp):
        self.__min_amp = min_amp

    @property
    def max_amp(self):
        return self.__max_amp

    @max_amp.setter
    def max_amp(self, max_amp):
        self.__max_amp = max_amp

    @property
    def min_sidescan(self):
        return self.__min_sidescan

    @min_sidescan.setter
    def min_sidescan(self, min_sidescan):
        self.__min_sidescan = min_sidescan

    @property
    def max_sidescan(self):
        return self.__max_sidescan

    @max_sidescan.setter
    def max_sidescan(self, max_sidescan):
        self.__max_sidescan = max_sidescan

    @property
    def objectid(self):
        return self.__objectid

    @objectid.setter
    def objectid(self, objectid):
        self.__objectid = objectid

    @property
    def shape(self):
        return self.__shape

    @shape.setter
    def shape(self, shape):
        self.__shape = shape

    @property
    def publish(self):
        return self.__publish

    @publish.setter
    def publish(self, publish):
        self.__publish = publish

    @property
    def previous_state(self):
        return self.__previous_state

    @previous_state.setter
    def previous_state(self, previous_state):
        self.__previous_state = previous_state

    @property
    def shape_gen(self):
        return self.__shape_gen

    @shape_gen.setter
    def shape_gen(self, shape_gen):
        self.__shape_gen = shape_gen

    @staticmethod
    def build(mbinfo: dict):
        return MbInfo(
            mbinfo['DATA_FILE'],
            mbinfo['NGDC_ID'],
            mbinfo['MBIO_FORMAT_ID'],
            mbinfo['RECORD_COUNT'],
            mbinfo['BATHY_BEAMS'],
            mbinfo['BB_GOOD'],
            mbinfo['BB_ZERO'],
            mbinfo['BB_FLAGGED'],
            mbinfo['AMP_BEAMS'],
            mbinfo['AB_GOOD'],
            mbinfo['AB_ZERO'],
            mbinfo['AB_FLAGGED'],
            mbinfo['SIDESCANS'],
            mbinfo['SS_GOOD'],
            mbinfo['SS_ZERO'],
            mbinfo['SS_FLAGGED'],
            mbinfo['TOTAL_TIME'],
            mbinfo['TRACK_LENGTH'],
            mbinfo['AVG_SPEED'],
            mbinfo['START_TIME'],
            mbinfo['START_LON'],
            mbinfo['START_LAT'],
            mbinfo['START_DEPTH'],
            mbinfo['START_SPEED'],
            mbinfo['START_HEADING'],
            util.dict_value_or_none(mbinfo, 'START_SONAR_DEPTH'),
            util.dict_value_or_none(mbinfo, 'START_SONAR_ALT'),
            mbinfo['END_TIME'],
            mbinfo['END_LON'],
            mbinfo['END_LAT'],
            mbinfo['END_DEPTH'],
            mbinfo['END_SPEED'],
            mbinfo['END_HEADING'],
            util.dict_value_or_none(mbinfo, 'END_SONAR_DEPTH'),
            util.dict_value_or_none(mbinfo, 'END_SONAR_ALT'),
            mbinfo['MIN_LON'],
            mbinfo['MAX_LON'],
            mbinfo['MIN_LAT'],
            mbinfo['MAX_LAT'],
            util.dict_value_or_none(mbinfo, 'MIN_SONAR_DEPTH'),
            util.dict_value_or_none(mbinfo, 'MAX_SONAR_DEPTH'),
            util.dict_value_or_none(mbinfo, 'MIN_SONAR_ALT'),
            util.dict_value_or_none(mbinfo, 'MAX_SONAR_ALT'),
            util.dict_value_or_none(mbinfo, 'MIN_DEPTH'),
            util.dict_value_or_none(mbinfo, 'MAX_DEPTH'),
            util.dict_value_or_none(mbinfo, 'MIN_AMP'),
            util.dict_value_or_none(mbinfo, 'MAX_AMP'),
            util.dict_value_or_none(mbinfo, 'MIN_SIDESCAN'),
            util.dict_value_or_none(mbinfo, 'MAX_SIDESCAN'),
            mbinfo['OBJECTID'],
            util.dict_value_or_none(mbinfo, 'SHAPE'),
            util.dict_value_or_none(mbinfo, 'PUBLISH'),
            util.dict_value_or_none(mbinfo, 'PREVIOUS_STATE'),
            util.dict_value_or_none(mbinfo, 'SHAPE_GEN')
        )
