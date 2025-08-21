from mb_cruise_migration.framework.consts.data_file_consts import *
from mb_cruise_migration.framework.consts.data_file_part_consts import (
    DataFilePartsLookup,
)


class ParsedFilePath(object):
    def __init__(self, data_file):
        self.__file_path_parts = data_file.split("/")
        self.__normalized_parts = self.__normalize(self.__file_path_parts)

    def is_empty(self) -> bool:
        return len(self.__file_path_parts) == 0

    def is_wcd(self) -> bool:
        return self.__file_path_parts[PathIndexes.ROOT] == PathRoot.WCD

    def is_xtf(self):
        return self.__file_path_parts[PathIndexes.ROOT] == PathRoot.XTF

    def is_singlebeam(self):
        return self.__file_path_parts[PathIndexes.ROOT] == PathRoot.SINGLEBEAM

    def is_canadian_data(self) -> bool:
        return (
            self.__normalized_parts[PathIndexes.POSSIBLE_CANADIAN]
            == PathSubDir.CANADIAN
        )

    def is_survey_metadata(self) -> bool:
        return self.__file_path_parts[PathIndexes.ROOT] == PathRoot.MGG

    def is_nonpublic(self) -> bool:
        return any([part == PathSubDir.NONPUBLIC for part in self.__file_path_parts])

    def has_instrument(self):
        if PathIndexes.INSTRUMENT > len(self.__normalized_parts) - 1:
            return False
        survey_name = self.__normalized_parts[PathIndexes.SURVEY_NAME]
        if (
            survey_name in DataFilePartsLookup.surveys_with_instrument_in_filenames
        ) and (
            self.parse_instrument_from_filename()
            in DataFilePartsLookup.valid_instruments
        ):
            return True
        return (
            self.__normalized_parts[PathIndexes.INSTRUMENT]
            in DataFilePartsLookup.valid_instruments
        )

    def has_extraneous(self):
        for index in PathIndexes.POSSIBLE_ERRONEOUS:
            if index > len(self.__normalized_parts) - 1:
                continue
            if self.__normalized_parts[index] in DataFilePartsLookup.known_erroneous:
                return True
        return False

    def has_leg(self):
        for index in PathIndexes.POSSIBLE_LEG:
            if index > len(self.__normalized_parts) - 1:
                continue
            if self.__normalized_parts[index] in DataFilePartsLookup.known_legs:
                return True
        return False

    def has_zone(self):
        for index in PathIndexes.POSSIBLE_ZONE:
            if index > len(self.__normalized_parts) - 1:
                continue
            if self.__normalized_parts[index] in DataFilePartsLookup.known_zones:
                return True
        return False

    def has_region(self):
        for index in PathIndexes.POSSIBLE_REGION:
            if index > len(self.__normalized_parts) - 1:
                continue
            if self.__normalized_parts[index] in DataFilePartsLookup.known_regions:
                return True
        return False

    def is_standard(self):
        standard = (
            (self.__normalized_parts[PathIndexes.ROOT] == PathRoot.OCEAN)
            and (len(self.__normalized_parts) == 10)
            and self.has_instrument()
        )

        standard_no_instrument = (
            (self.__normalized_parts[PathIndexes.ROOT] == PathRoot.OCEAN)
            and (len(self.__normalized_parts) == 9)
            and not self.has_instrument()
        )

        standard_instrument_in_filename = (
            (self.__normalized_parts[PathIndexes.ROOT] == PathRoot.OCEAN)
            and (len(self.__normalized_parts) == 9)
            and self.__normalized_parts[PathIndexes.SURVEY_NAME]
            in DataFilePartsLookup.surveys_with_instrument_in_filenames
        )

        return standard or standard_no_instrument or standard_instrument_in_filename

    def identify_instrument_in_path(self) -> str:
        if (
            self.__normalized_parts[PathIndexes.SURVEY_NAME]
            in DataFilePartsLookup.surveys_with_instrument_in_filenames
        ):
            instrument = self.parse_instrument_from_filename()
        else:
            instrument = self.__normalized_parts[PathIndexes.INSTRUMENT]
        if instrument not in DataFilePartsLookup.valid_instruments:
            raise RuntimeError(
                "Validate that the parsed path has instrument before retrieval"
            )
        return instrument

    def parse_instrument_from_filename(self):
        filename = self.__normalized_parts[-1]
        filename_parts = filename.split("-")
        instrument = filename_parts[0]
        return instrument

    def identify_version_in_path(self) -> str:
        return self.__normalized_parts[PathIndexes.VERSION]

    def identify_data_type_in_path(self) -> str:
        return self.__normalized_parts[PathIndexes.DATASET_TYPE]

    def identify_platform_type_in_path(self) -> str:
        return self.__normalized_parts[PathIndexes.PLATFORM_TYPE]

    def identify_platform_in_path(self) -> str:
        return self.__normalized_parts[PathIndexes.PLATFORM_NAME]

    def derive_dataset_name_from_path(self) -> str:
        # TODO
        pass

    def __normalize(self, file_path_parts):
        file_path_parts = self.__strip_nonpublic_dirs(file_path_parts)
        file_path_parts = self.__strip_unnecessary_raw_demarcation(file_path_parts)
        file_path_parts = self.__strip_backscatter_lowercase_dir(file_path_parts)
        file_path_parts = self.__strip_km1718_grids_dir(file_path_parts)
        return file_path_parts

    @staticmethod
    def __strip_nonpublic_dirs(path_parts) -> list:
        return list(filter(lambda part: part != PathSubDir.NONPUBLIC, path_parts))

    @staticmethod
    def __strip_unnecessary_raw_demarcation(path_parts):
        return list(filter(lambda part: part != PathSubDir.RAW, path_parts))

    @staticmethod
    def __strip_backscatter_lowercase_dir(path_parts) -> list:
        return list(filter(lambda part: part != "backscatter", path_parts))

    @staticmethod
    def __strip_km1718_grids_dir(path_parts) -> list:
        return list(filter(lambda part: part != "KM1718_Grids", path_parts))
