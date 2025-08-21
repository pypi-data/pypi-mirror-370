from typing import Optional

from mb_cruise_migration.models.cruise.cruise_file_formats import CruiseFileFormat
from mb_cruise_migration.models.mb.mb_mbinfo_formats import MbFileFormat
from mb_cruise_migration.services.cruise_service import FileFormatService


class FFLookup(object):
    LOOKUP = {}
    REVERSE_LOOKUP = {}

    @staticmethod
    def set_ff_lookup(cruise_file_formats: [CruiseFileFormat]):
        for cruise_file_format in cruise_file_formats:
            FFLookup.LOOKUP.update({cruise_file_format.alt_id: cruise_file_format})
            FFLookup.REVERSE_LOOKUP.update({cruise_file_format.format_name: cruise_file_format})

    @staticmethod
    def get_id(mb_id: int) -> Optional[int]:
        try:
            return FFLookup.LOOKUP[str(mb_id)].id
        except KeyError:
            raise RuntimeError("MB.MBINFO_FORMATS.ID not found in ALT_ID column of CRUISE.FILE_FORMATS")

    @staticmethod
    def pre_validate(file_format_service: FileFormatService, mb_file_formats: [MbFileFormat]):
        for file_format in mb_file_formats:
            cruise_file_format = CruiseFileFormat(format_name=file_format.format_name, alt_id=str(file_format.id), format_description=None)
            file_format_service.save_file_format(cruise_file_format)
