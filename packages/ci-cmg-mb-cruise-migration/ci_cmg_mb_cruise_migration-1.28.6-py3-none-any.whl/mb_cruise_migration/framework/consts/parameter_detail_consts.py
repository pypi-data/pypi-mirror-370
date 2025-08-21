from typing import Optional

from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.models.cruise.cruise_parameter_details import (
    CruiseParameterDetail,
)


class PDLookup(object):
    LOOKUP = {}
    REVERSE_LOOKUP = {}

    @staticmethod
    def set_lookup(parameter_details: [CruiseParameterDetail]):
        for parameter_detail in parameter_details:
            PDLookup.LOOKUP.update(
                {parameter_detail.parameter: parameter_detail.parameter_id}
            )
            PDLookup.REVERSE_LOOKUP.update(
                {parameter_detail.parameter_id: parameter_detail.parameter}
            )

    @staticmethod
    def get_id(parameter: str) -> Optional[int]:
        try:
            return PDLookup.LOOKUP[parameter]
        except KeyError:
            return None

    @staticmethod
    def validate(parameter_detail_service):
        for key, value in vars(ParameterDetailConsts).items():
            if key.startswith("__") or callable(key):
                continue
            if PDLookup.get_id(value) is None:
                MigrationLog.log_const_update(
                    f"Parameter detail {value} did not exist but is required and is being added to CRUISE schema."
                )
                detail = parameter_detail_service.save_new_parameter_detail(
                    CruiseParameterDetail(
                        parameter=value, parameter_type=None, description=None
                    )
                )
                PDLookup.LOOKUP.update({detail.parameter: detail.parameter_id})


class ParameterDetailConsts(object):
    FILE_FORMAT_TYPE = "FILE_FORMAT_TYPE"
    FILE_FORMAT_PROTOCOL = "FILE_FORMAT_PROTOCOL"
    FILE_FORMAT_ATTRIBUTES = "FILE_FORMAT_ATTRIBUTES"
    MB_SYSTEM_ID = "MB_SYSTEM_ID"
    MB_FILE_FORMAT_ID = "MB_FILE_FORMAT_ID"
    MD5_CHECKSUM = "MD5_CHECKSUM"
    SHA256_CHECKSUM = "SHA256_CHECKSUM"
    MB_OBJECT_COUNT = "MB_OBJECT_COUNT"
    MB_TOTAL_TIME_HOURS = "MB_TOTAL_TIME_HOURS"
    MB_TOTAL_TRACK_LENGTH_KM = "MB_TOTAL_TRACK_LENGTH_KM"  # a.k.a 'Track_Length'
    MB_AVG_SPEED_KM_HR = "MB_AVG_SPEED_KM_HR"  # a.k.a 'AVG_Speed'
    MB_MIN_SONAR_DEPTH_M = "MB_MIN_SONAR_DEPTH_M"  # a.k.a "Min_Sonar_Depth"
    MB_MAX_SONAR_DEPTH_M = "MB_MAX_SONAR_DEPTH_M"  # a.k.a "Max_Sonar_Depth"
    MB_MIN_ALTITUDE = "MB_MIN_ALTITUDE"
    MB_MAX_ALTITUDE = "MB_MAX_ALTITUDE"
    MB_MIN_DEPTH = "MB_MIN_DEPTH"  # a.k.a 'Min_Depth'
    MB_MAX_DEPTH = "MB_MAX_DEPTH"  # a.k.a 'Max_Depth'
    MB_MIN_AMPLITUDE = "MB_MIN_AMPLITUDE"  # a.k.a 'Min_Amp'
    MB_MAX_AMPLITUDE = "MB_MAX_AMPLITUDE"  # a.k.a 'Max_Amp'
    MB_MIN_SIDESCAN = "MB_MIN_SIDESCAN"  # a.k.a 'Min_Sidescan'
    MB_MAX_SIDESCAN = "MB_MAX_SIDESCAN"  # a.k.a 'Max_Sidescan'
    MB_FILE_COUNT = "MB_FILE_COUNT"
    MB_RECORD_COUNT = "MB_RECORD_COUNT"
    MB_BATHY_BEAMS = "MB_BATHY_BEAMS"
    MB_GOOD_BATH_TOTAL = "MB_GOOD_BATH_TOTAL"
    MB_GOOD_BATH_PERCENT = "MB_GOOD_BATH_PERCENT"
    MB_ZERO_BATH_TOTAL = "MB_ZERO_BATH_TOTAL"
    MB_ZERO_BATH_PERCENT = "MB_ZERO_BATH_PERCENT"
    MB_FLAGGED_BATH_TOTAL = "MB_FLAGGED_BATH_TOTAL"
    MB_FLAGGED_BATH_PERCENT = "MB_FLAGGED_BATH_PERCENT"
    MB_AMP_BEAMS = "MB_AMP_BEAMS"  # a.k.a. 'AMP_Beams'
    MB_GOOD_AMP_TOTAL = "MB_GOOD_AMP_TOTAL"  # a.k.a. 'AB_Good'
    MB_GOOD_AMP_PERCENT = "MB_GOOD_AMP_PERCENT"
    MB_ZERO_AMP_TOTAL = "MB_ZERO_AMP_TOTAL"  # a.k.a 'AB_Zero'
    MB_ZERO_AMP_PERCENT = "MB_ZERO_AMP_PERCENT"
    MB_FLAGGED_AMP_TOTAL = "MB_FLAGGED_AMP_TOTAL"  # a.k.a. 'AB_Flagged'
    MB_FLAGGED_AMP_PERCENT = "MB_FLAGGED_AMP_PERCENT"
    MB_SIDESCANS = "MB_SIDESCANS"  # a.k.a.'Sidescans'
    MB_GOOD_SIDESCANS_TOTAL = "MB_GOOD_SIDESCANS_TOTAL"  # a.k.a 'SS_Good'
    MB_GOOD_SIDESCANS_PERCENT = "MB_GOOD_SIDESCANS_PERCENT"
    MB_ZERO_SIDESCANS_TOTAL = "MB_ZERO_SIDESCANS_TOTAL"  # a.k.a 'SS_Zero'
    MB_ZERO_SIDESCANS_PERCENT = "MB_ZERO_SIDESCANS_PERCENT"
    MB_FLAGGED_SIDESCANS_TOTAL = "MB_FLAGGED_SIDESCANS_TOTAL"  # a.k.a 'SS_Flagged'
    MB_FLAGGED_SIDESCANS_PERCENT = "MB_FLAGGED_SIDESCANS_PERCENT"
    MB_BBOX_NORTH = "MB_BBOX_NORTH"
    MB_BBOX_SOUTH = "MB_BBOX_SOUTH"
    MB_BBOX_EAST = "MB_BBOX_EAST"
    MB_BBOX_WEST = "MB_BBOX_WEST"
    DIRECTORY_STRUCTURE_TYPE = "DIRECTORY_STRUCTURE_TYPE"
    MB_NGDC_ID = "MB_NGDC_ID"
    MB_DATASET_DIR = "MB_DATASET_DIR"
    DATASET_DIRECTORY = "DATASET_DIRECTORY"
    MB_AREA_SQ_KM = "MB_AREA_SQ_KM"
    PUBLISH = "PUBLISH"
    PROPRIETARY = "PROPRIETARY"
    COMMENTS = "COMMENTS"
    NAV1 = "NAV1"
    NAV2 = "NAV2"
    HORIZONTAL_DATUM = "HORIZONTAL_DATUM"
    VERTICAL_DATUM = "VERTICAL_DATUM"
    TIDE_CORRECTION = "TIDE_CORRECTION"
    SOUND_VELOCITY = "SOUND_VELOCITY"
    PREVIOUS_STATE = "PREVIOUS_STATE"
    MODIFY_DATE_DATA = "MODIFY_DATE_DATA"
    MODIFY_DATE_METADATA = "MODIFY_DATE_METADATA"
    EXTRACT_METADATA = "EXTRACT_METADATA"
    DOWNLOAD_URL = "DOWNLOAD_URL"
    MBIO_FORMAT_ID = "MBIO_FORMAT_ID"

    MB_START_TIME = "START_TIME"
    MB_START_LONGITUDE = "START_LON"
    MB_START_LATITUDE = "START_LAT"
    MB_START_DEPTH = "START_DEPTH"
    MB_START_SPEED = "START_SPEED"
    MB_START_HEADING = "START_HEADING"
    MB_START_SONAR_DEPTH = "START_SONAR_DEPTH"
    MB_START_SONAR_ALTITUDE = "START_SONAR_ALT"
    MB_END_TIME = "END_TIME"
    MB_END_LONGITUDE = "END_LON"
    MB_END_LATITUDE = "END_LAT"
    MB_END_DEPTH = "END_DEPTH"
    MB_END_SPEED = "END_SPEED"
    MB_END_HEADING = "END_HEADING"
    MB_END_SONAR_DEPTH = "END_SONAR_DEPTH"
    MB_END_SONAR_ALTITUDE = "END_SONAR_ALT"
    MB_MIN_LONGITUDE = "MIN_LON"
    MB_MAX_LONGITUDE = "MAX_LON"
    MB_MIN_LATITUDE = "MIN_LAT"
    MB_MAX_LATITUDE = "MAX_LAT"
    MB_MIN_SONAR_ALTITUDE = "MIN_SONAR_ALT"
    MB_MAX_SONAR_ALTITUDE = "MAX_SONAR_ALT"
    MB_OBJECT_ID = "OBJECT_ID"

    ABSTRACT = "ABSTRACT"
    PURPOSE = "PURPOSE"

    PROJECT_URL = "PROJECT_URL"
