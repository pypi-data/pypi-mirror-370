from mb_cruise_migration.framework.consts.error_consts import ErrorConsts
from mb_cruise_migration.framework.consts.instrument_consts import InstrumentConsts
from mb_cruise_migration.models.cruise.cruise_instruments import CruiseInstrument


class InstrumentLookup(object):

    @staticmethod
    def get_instrument_name_from_mb_survey_instrument(survey_instrument):
        if survey_instrument is None:
            raise RuntimeError("Illegal null value provided for survey instrument.")
        const = InstrumentLookup.get_const_from_mb_survey_instrument(survey_instrument)
        instrument = InstrumentLookup.get_instrument_from_const_value(const)
        return instrument.instrument_name

    @staticmethod
    def get_instrument_name_from_parsed_file_instrument(data_file_inst):
        if data_file_inst is None:
            raise RuntimeError("Illegal null value provided for data file instrument.")
        const = InstrumentLookup.get_const_from_parsed_datafile_instrument(
            data_file_inst=data_file_inst
        )
        instrument = InstrumentLookup.get_instrument_from_const_value(const)
        return instrument.instrument_name

    @staticmethod
    def convert_survey_instrument_to_const_format(survey_instrument_name: str):
        upper_case = survey_instrument_name.upper()
        no_spaces = upper_case.replace(" ", "")
        no_dashes = no_spaces.replace("-", "")
        return no_dashes

    @staticmethod
    def get_const_from_parsed_datafile_instrument(data_file_inst):
        if data_file_inst == "em710":
            return InstrumentConsts.KONGSBERGEM710
        if data_file_inst == "em122":
            return InstrumentConsts.KONGSBERGEM122
        if data_file_inst == "em302":
            return InstrumentConsts.KONGSBERGEM302
        if data_file_inst == "reson8101":
            return InstrumentConsts.RESON8101
        if data_file_inst == "t50-p":
            return InstrumentConsts.RESONSEABATT50P
        if data_file_inst == "t20p" or data_file_inst == "t20-p":
            return InstrumentConsts.RESONSEABATT20P
        if data_file_inst == "em300":
            return InstrumentConsts.SIMRADEM300
        if data_file_inst == "em300d":
            return InstrumentConsts.SIMRADEM300D
        if data_file_inst == "em120":
            return InstrumentConsts.SIMRADEM120
        if (
            data_file_inst == "reson7125"
            or data_file_inst == "7125"
            or data_file_inst == "reson7125_200"
            or data_file_inst == "reson7125_400"
            or data_file_inst == "reson7125_ppk"
        ):
            return InstrumentConsts.RESON7125
        if data_file_inst == "em712":
            return InstrumentConsts.KONGSBERGEM712
        if data_file_inst == "em3002" or data_file_inst == "EM3002":
            return InstrumentConsts.KONGSBERGEM3002
        if data_file_inst == "7160":
            return InstrumentConsts.RESONSEABAT7160
        if data_file_inst == "EM3000" or data_file_inst == "em3000":
            return InstrumentConsts.SIMRADEM3000
        if data_file_inst == "em1002":
            return InstrumentConsts.SIMRADEM1002
        if data_file_inst == "EM1000":
            return InstrumentConsts.SIMRADEM1000
        if data_file_inst == "em3002d":
            return InstrumentConsts.SIMRADEM3002D
        if data_file_inst == "swathplus" or data_file_inst == "sea_swathplus":
            return InstrumentConsts.SEASWATHPLUS
        if data_file_inst == "em124":
            return InstrumentConsts.KONGSBERGEM124
        if data_file_inst == "me70":
            return InstrumentConsts.SIMRADME70
        if data_file_inst == "hydrosweep":
            return InstrumentConsts.ATLASHYDROSWEEPDS
        if data_file_inst == "reson8150":
            return InstrumentConsts.RESONSEABAT8150
        if data_file_inst == "sb2112" or data_file_inst == "2112":
            return InstrumentConsts.SEABEAM2112
        if data_file_inst == "8125" or data_file_inst == "reson8125":
            return InstrumentConsts.RESONSEABAT8125
        if data_file_inst == "8101":
            return InstrumentConsts.RESONSEABAT8101
        if data_file_inst == "em121":
            return InstrumentConsts.SIMRADEM121
        if data_file_inst == "EM1002":
            return InstrumentConsts.KONGSBERGEM1002
        if data_file_inst == "r2sonic2022":
            return InstrumentConsts.R2SONIC2022
        if data_file_inst == "elac3020":
            return InstrumentConsts.ELACNAUTIK3020
        if data_file_inst == "3012-p1":
            return InstrumentConsts.SEABEAM3012P1
        if data_file_inst == "3012-l3":
            return InstrumentConsts.SEABEAM3012L3
        if data_file_inst == "3012":
            return InstrumentConsts.SEABEAM3012
        if data_file_inst == "reson7111":
            return InstrumentConsts.RESON7111
        if data_file_inst == "sb2120":
            return InstrumentConsts.SEABEAM2120
        if data_file_inst == "7101":
            return InstrumentConsts.RESONSEABAT7101
        if data_file_inst == "em304":
            return InstrumentConsts.KONGSBERGEM304
        if data_file_inst == "em2040":
            return InstrumentConsts.KONGSBERGEM2040
        if data_file_inst == "em2040c":
            return InstrumentConsts.KONGSBERGEM2040C
        if data_file_inst == "em2040p":
            return InstrumentConsts.KONGSBERGEM2040P
        if data_file_inst == "r2sonic2024":
            return InstrumentConsts.R2SONIC2024

    @staticmethod
    def get_const_from_mb_survey_instrument(survey_instrument):
        if survey_instrument is None:
            raise ValueError(ErrorConsts.NONE_VALUE_PROVIDED_WHERE_DISALLOWED)
        if survey_instrument == "BSSS":
            return InstrumentConsts.BSSS
        if survey_instrument == "Reson SeaBat 9003":
            return InstrumentConsts.RESONSEABAT9003
        if survey_instrument == "Kongsberg EM710":
            return InstrumentConsts.KONGSBERGEM710
        if survey_instrument == "Kongsberg EM122":
            return InstrumentConsts.KONGSBERGEM122
        if survey_instrument == "Kongsberg EM302":
            return InstrumentConsts.KONGSBERGEM302
        if survey_instrument == "Reson 8101":
            return InstrumentConsts.RESON8101
        if survey_instrument == "Reson SeaBat T50-P":
            return InstrumentConsts.RESONSEABATT50P
        if survey_instrument == "SeaBeam":
            return InstrumentConsts.SEABEAM
        if survey_instrument == "Simrad EM300":
            return InstrumentConsts.SIMRADEM300
        if survey_instrument == "EM300D":
            return InstrumentConsts.SIMRADEM300D
        if survey_instrument == "SeaBeam 1050D":
            return InstrumentConsts.SEABEAM1050D
        if survey_instrument == "Simrad EM120":
            return InstrumentConsts.SIMRADEM120
        if survey_instrument == "SeaBeam 1180":
            return InstrumentConsts.SEABEAM1180
        if survey_instrument == "SeaMarc II":
            return InstrumentConsts.SEAMARCII
        if survey_instrument == "Odom Echotrac CV2 singlebeam":
            return InstrumentConsts.ODOMECHOTRACCV2SINGLEBEAM
        if survey_instrument == "Simrad EM950":
            return InstrumentConsts.SIMRADEM950
        if survey_instrument == "SeaBeam 3012":
            return InstrumentConsts.SEABEAM3012
        if (
            survey_instrument == "Reson 7125"
            or survey_instrument == "Reson SeaBat 7125"
        ):
            return InstrumentConsts.RESON7125
        if survey_instrument == "Kongsberg EM712":
            return InstrumentConsts.KONGSBERGEM712
        if survey_instrument == "Kongsberg EM3002":
            return InstrumentConsts.KONGSBERGEM3002
        if survey_instrument == "Reson Seabat 7160":
            return InstrumentConsts.RESONSEABAT7160
        if survey_instrument == "Simrad EM3000":
            return InstrumentConsts.SIMRADEM3000
        if survey_instrument == "Simrad EM1002":
            return InstrumentConsts.SIMRADEM1002
        if survey_instrument == "ELAC":
            return InstrumentConsts.ELAC
        if survey_instrument == "Kongsberg EM300":
            return InstrumentConsts.KONGSBERGEM300
        if survey_instrument == "Kongsberg EM2040D":
            return InstrumentConsts.KONGSBERGEM2040D
        if survey_instrument == "SeaBeam 2000":
            return InstrumentConsts.SEABEAM2000
        if survey_instrument == "Simrad EM302":
            return InstrumentConsts.SIMRADEM302
        if survey_instrument == "Simrad EM1000":
            return InstrumentConsts.SIMRADEM1000
        if survey_instrument == "Simrad EM3002d":
            return InstrumentConsts.SIMRADEM3002D
        if survey_instrument == "SeaBeam 1050":
            return InstrumentConsts.SEABEAM1050
        if survey_instrument == "Sea Swathplus":
            return InstrumentConsts.SEASWATHPLUS
        if survey_instrument == "Kongsberg EM124":
            return InstrumentConsts.KONGSBERGEM124
        if survey_instrument == "Simrad ME70":
            return InstrumentConsts.SIMRADME70
        if survey_instrument == "Hollming ECHOS 625":
            return InstrumentConsts.HOLLMINGECHOS625
        if survey_instrument == "Atlas Hydrosweep DS":
            return InstrumentConsts.ATLASHYDROSWEEPDS
        if survey_instrument == "Reson SeaBat 9001":
            return InstrumentConsts.RESONSEABAT9001
        if survey_instrument == "SeaBeam 2100":
            return InstrumentConsts.SEABEAM2100
        if survey_instrument == "Reson SeaBat 8150":
            return InstrumentConsts.RESONSEABAT8150
        if survey_instrument == "MR1":
            return InstrumentConsts.MR1
        if survey_instrument == "Kongsberg EM2040":
            return InstrumentConsts.KONGSBERGEM2040
        if survey_instrument == "Kongsberg EM2040C":
            return InstrumentConsts.KONGSBERGEM2040C
        if survey_instrument == "Kongsberg EM2040p":
            return InstrumentConsts.KONGSBERGEM2040P
        if survey_instrument == "Reson SeaBat 7101":
            return InstrumentConsts.RESONSEABAT7101
        if survey_instrument == "Reson SeaBat T20-P":
            return InstrumentConsts.RESONSEABATT20P
        if survey_instrument == "Kongsberg EM120":
            return InstrumentConsts.KONGSBERGEM120
        if survey_instrument == "R2Sonic 2024":
            return InstrumentConsts.R2SONIC2024
        if survey_instrument == "Kongsberg EM304":
            return InstrumentConsts.KONGSBERGEM304
        if survey_instrument == "SeaBeam 2112":
            return InstrumentConsts.SEABEAM2112
        if survey_instrument == "Atlas Hydrosweep DS-2":
            return InstrumentConsts.ATLASHYDROSWEEPDS2
        if survey_instrument == "Reson SeaBat 8125":
            return InstrumentConsts.RESONSEABAT8125
        if survey_instrument == "Reson SeaBat 8160":
            return InstrumentConsts.RESONSEABAT8160
        if survey_instrument == "Reson SeaBat 8101":
            return InstrumentConsts.RESONSEABAT8101
        if survey_instrument == "unknown":
            return InstrumentConsts.UNKNOWN
        if survey_instrument == "Innerspace 455 singlebeam":
            return InstrumentConsts.INNERSPACE455SINGLEBEAM
        if survey_instrument == "LADSMkII":
            return InstrumentConsts.LADSMKII
        if survey_instrument == "Simrad EM121":
            return InstrumentConsts.SIMRADEM121
        if survey_instrument == "Kongsberg EM1002":
            return InstrumentConsts.KONGSBERGEM1002
        if survey_instrument == "R2Sonic 2022":
            return InstrumentConsts.R2SONIC2022
        if survey_instrument == "ELAC Nautik 3020":
            return InstrumentConsts.ELACNAUTIK3020
        if survey_instrument == "SeaBeam 3012-L3":
            return InstrumentConsts.SEABEAM3012L3
        if survey_instrument == "Hydrochart II":
            return InstrumentConsts.HYDROCHARTII
        if survey_instrument == "Simrad EM122":
            return InstrumentConsts.SIMRADEM122
        if survey_instrument == "Simrad EM3002":
            return InstrumentConsts.SIMRADEM3002
        if survey_instrument == "HawkEye II":
            return InstrumentConsts.HAWKEYEII
        if survey_instrument == "SeaBeam 3012-P1":
            return InstrumentConsts.SEABEAM3012P1
        if survey_instrument == "SeaBeam 3012-L3":
            return InstrumentConsts.SEABEAM3012L3
        if survey_instrument == "Reson 7111":
            return InstrumentConsts.RESON7111
        if survey_instrument == "SeaBeam 2120":
            return InstrumentConsts.SEABEAM2120
        raise ValueError(ErrorConsts.NO_MATCHING_INSTRUMENT + ": " + survey_instrument)

    @staticmethod
    def get_instrument_from_const_value(const):
        if const is None:
            raise ValueError(ErrorConsts.NONE_VALUE_PROVIDED_WHERE_DISALLOWED)
        if const == InstrumentConsts.BSSS:
            return CruiseInstrument(
                instrument_name="BSSS", docucomp_uuid=None, long_name="BSSS"
            )
        if const == InstrumentConsts.RESONSEABAT9003:
            return CruiseInstrument(
                instrument_name="RESON9003",
                docucomp_uuid=None,
                long_name="Reson SeaBat 9003",
            )
        if const == InstrumentConsts.KONGSBERGEM710:
            return CruiseInstrument(
                instrument_name="EM710", docucomp_uuid=None, long_name="Kongsberg EM710"
            )
        if const == InstrumentConsts.KONGSBERGEM122:
            return CruiseInstrument(
                instrument_name="EM122", docucomp_uuid=None, long_name="Kongsberg EM122"
            )
        if const == InstrumentConsts.KONGSBERGEM302:
            return CruiseInstrument(
                instrument_name="EM302", docucomp_uuid=None, long_name="Kongsberg EM302"
            )
        if const == InstrumentConsts.RESON8101:
            return CruiseInstrument(
                instrument_name="RESON8101", docucomp_uuid=None, long_name="Reson 8101"
            )
        if const == InstrumentConsts.RESONSEABATT50P:
            return CruiseInstrument(
                instrument_name="RESONT50-P",
                docucomp_uuid=None,
                long_name="Reson SeaBat T50-P",
            )
        if const == InstrumentConsts.SEABEAM:
            return CruiseInstrument(
                instrument_name="SB", docucomp_uuid=None, long_name="SeaBeam"
            )
        if const == InstrumentConsts.SIMRADEM300:
            return CruiseInstrument(
                instrument_name="EM300", docucomp_uuid=None, long_name="Simrad EM300"
            )
        if const == InstrumentConsts.SIMRADEM300D:
            return CruiseInstrument(
                instrument_name="EM300D", docucomp_uuid=None, long_name="EM300D"
            )
        if const == InstrumentConsts.SEABEAM1050D:
            return CruiseInstrument(
                instrument_name="SB1050D", docucomp_uuid=None, long_name="SeaBeam 1050D"
            )
        if const == InstrumentConsts.SIMRADEM120:
            return CruiseInstrument(
                instrument_name="EM120", docucomp_uuid=None, long_name="Simrad EM120"
            )
        if const == InstrumentConsts.SEABEAM1180:
            return CruiseInstrument(
                instrument_name="SB1180", docucomp_uuid=None, long_name="SeaBeam 1180"
            )
        if const == InstrumentConsts.SEAMARCII:
            return CruiseInstrument(
                instrument_name="SEAMARCII", docucomp_uuid=None, long_name="SeaMarc II"
            )
        if const == InstrumentConsts.ODOMECHOTRACCV2SINGLEBEAM:
            return CruiseInstrument(
                instrument_name="ECHOTRACSINGLEBEAM",
                docucomp_uuid=None,
                long_name="Odom Echotrac CV2 singlebeam",
            )  # shouldn't be migrated
        if const == InstrumentConsts.SIMRADEM950:
            return CruiseInstrument(
                instrument_name="EM950", docucomp_uuid=None, long_name="Simrad EM950"
            )
        if const == InstrumentConsts.SEABEAM3012:
            return CruiseInstrument(
                instrument_name="SB3012", docucomp_uuid=None, long_name="SeaBeam 3012"
            )
        if const == InstrumentConsts.RESON7125:
            return CruiseInstrument(
                instrument_name="RESON7125", docucomp_uuid=None, long_name="Reson 7125"
            )
        if const == InstrumentConsts.KONGSBERGEM712:
            return CruiseInstrument(
                instrument_name="EM712", docucomp_uuid=None, long_name="Kongsberg EM712"
            )
        if const == InstrumentConsts.KONGSBERGEM3002:
            return CruiseInstrument(
                instrument_name="EM3002",
                docucomp_uuid=None,
                long_name="Kongsberg EM3002",
            )
        if const == InstrumentConsts.RESONSEABAT7160:
            return CruiseInstrument(
                instrument_name="RESON7160",
                docucomp_uuid=None,
                long_name="Reson Seabat 7160",
            )
        if const == InstrumentConsts.SIMRADEM3000:
            return CruiseInstrument(
                instrument_name="EM3000", docucomp_uuid=None, long_name="Simrad EM3000"
            )
        if const == InstrumentConsts.SIMRADEM1002:
            return CruiseInstrument(
                instrument_name="EM1002", docucomp_uuid=None, long_name="Simrad EM1002"
            )
        if const == InstrumentConsts.ELAC:
            return CruiseInstrument(
                instrument_name="ELAC", docucomp_uuid=None, long_name="ELAC"
            )
        if const == InstrumentConsts.KONGSBERGEM300:
            return CruiseInstrument(
                instrument_name="EM300", docucomp_uuid=None, long_name="Kongsberg EM300"
            )
        if const == InstrumentConsts.KONGSBERGEM2040D:
            return CruiseInstrument(
                instrument_name="EM2040D",
                docucomp_uuid=None,
                long_name="Kongsberg EM2040D",
            )
        if const == InstrumentConsts.SEABEAM2000:
            return CruiseInstrument(
                instrument_name="SB2000", docucomp_uuid=None, long_name="SeaBeam 2000"
            )
        if const == InstrumentConsts.SIMRADEM302:
            return CruiseInstrument(
                instrument_name="EM302", docucomp_uuid=None, long_name="Simrad EM302"
            )
        if const == InstrumentConsts.SIMRADEM1000:
            return CruiseInstrument(
                instrument_name="EM1000", docucomp_uuid=None, long_name="Simrad EM1000"
            )
        if const == InstrumentConsts.SIMRADEM3002D:
            return CruiseInstrument(
                instrument_name="EM3002D",
                docucomp_uuid=None,
                long_name="Simrad EM3002d",
            )
        if const == InstrumentConsts.SEABEAM1050:
            return CruiseInstrument(
                instrument_name="SB1050", docucomp_uuid=None, long_name="SeaBeam 1050"
            )
        if const == InstrumentConsts.SEASWATHPLUS:
            return CruiseInstrument(
                instrument_name="SEASWATHPLUS",
                docucomp_uuid=None,
                long_name="Sea Swathplus",
            )
        if const == InstrumentConsts.KONGSBERGEM124:
            return CruiseInstrument(
                instrument_name="EM124", docucomp_uuid=None, long_name="Kongsberg EM124"
            )
        if const == InstrumentConsts.SIMRADME70:
            return CruiseInstrument(
                instrument_name="ME70", docucomp_uuid=None, long_name="Simrad ME70"
            )
        if const == InstrumentConsts.HOLLMINGECHOS625:
            return CruiseInstrument(
                instrument_name="ECHOS625",
                docucomp_uuid=None,
                long_name="Hollming ECHOS 625",
            )
        if const == InstrumentConsts.ATLASHYDROSWEEPDS:
            return CruiseInstrument(
                instrument_name="HYDROSWEEPDS",
                docucomp_uuid=None,
                long_name="Atlas Hydrosweep DS",
            )
        if const == InstrumentConsts.RESONSEABAT9001:
            return CruiseInstrument(
                instrument_name="SB9001",
                docucomp_uuid=None,
                long_name="Reson SeaBat 9001",
            )
        if const == InstrumentConsts.SEABEAM2100:
            return CruiseInstrument(
                instrument_name="SB2100", docucomp_uuid=None, long_name="SeaBeam 2100"
            )
        if const == InstrumentConsts.RESONSEABAT8150:
            return CruiseInstrument(
                instrument_name="SB8150",
                docucomp_uuid=None,
                long_name="Reson SeaBat 8150",
            )
        if const == InstrumentConsts.MR1:
            return CruiseInstrument(
                instrument_name="MR1", docucomp_uuid=None, long_name="MR1"
            )
        if const == InstrumentConsts.KONGSBERGEM2040:
            return CruiseInstrument(
                instrument_name="EM2040",
                docucomp_uuid=None,
                long_name="Kongsberg EM2040",
            )
        if const == InstrumentConsts.KONGSBERGEM2040C:
            return CruiseInstrument(
                instrument_name="EM2040C",
                docucomp_uuid=None,
                long_name="Kongsberg EM2040C",
            )
        if const == InstrumentConsts.KONGSBERGEM2040P:
            return CruiseInstrument(
                instrument_name="EM2040P",
                docucomp_uuid=None,
                long_name="Kongsberg EM2040P",
            )
        if const == InstrumentConsts.RESONSEABAT7101:
            return CruiseInstrument(
                instrument_name="SB7101",
                docucomp_uuid=None,
                long_name="Reson SeaBat 7101",
            )
        if const == InstrumentConsts.RESONSEABATT20P:
            return CruiseInstrument(
                instrument_name="SBT20-P",
                docucomp_uuid=None,
                long_name="Reson SeaBat T20-P",
            )
        if const == InstrumentConsts.KONGSBERGEM120:
            return CruiseInstrument(
                instrument_name="EM120", docucomp_uuid=None, long_name="Kongsberg EM120"
            )
        if const == InstrumentConsts.R2SONIC2024:
            return CruiseInstrument(
                instrument_name="R2SONIC2024",
                docucomp_uuid=None,
                long_name="R2Sonic 2024",
            )
        if const == InstrumentConsts.KONGSBERGEM304:
            return CruiseInstrument(
                instrument_name="EM304", docucomp_uuid=None, long_name="Kongsberg EM304"
            )
        if const == InstrumentConsts.SEABEAM2112:
            return CruiseInstrument(
                instrument_name="SB2112", docucomp_uuid=None, long_name="SeaBeam 2112"
            )
        if const == InstrumentConsts.ATLASHYDROSWEEPDS2:
            return CruiseInstrument(
                instrument_name="HYDROSWEEPDS2",
                docucomp_uuid=None,
                long_name="Atlas Hydrosweep DS-2",
            )
        if const == InstrumentConsts.RESONSEABAT8125:
            return CruiseInstrument(
                instrument_name="RESON8125",
                docucomp_uuid=None,
                long_name="Reson SeaBat 8125",
            )
        if const == InstrumentConsts.RESONSEABAT8160:
            return CruiseInstrument(
                instrument_name="RESON8160",
                docucomp_uuid=None,
                long_name="Reson SeaBat 8160",
            )
        if const == InstrumentConsts.RESONSEABAT8101:
            return CruiseInstrument(
                instrument_name="RESON8101",
                docucomp_uuid=None,
                long_name="Reson SeaBat 8101",
            )
        if const == InstrumentConsts.UNKNOWN:
            return CruiseInstrument(
                instrument_name="unknown", docucomp_uuid=None, long_name="unknown"
            )
        if const == InstrumentConsts.INNERSPACE455SINGLEBEAM:
            return CruiseInstrument(
                instrument_name="INNERSPACE455",
                docucomp_uuid=None,
                long_name="Innerspace 455 singlebeam",
            )  # shouldn't be migrated
        if const == InstrumentConsts.LADSMKII:
            return CruiseInstrument(
                instrument_name="LADSMkII", docucomp_uuid=None, long_name="LADSMkII"
            )
        if const == InstrumentConsts.SIMRADEM121:
            return CruiseInstrument(
                instrument_name="EM121", docucomp_uuid=None, long_name="Simrad EM121"
            )
        if const == InstrumentConsts.KONGSBERGEM1002:
            return CruiseInstrument(
                instrument_name="EM1002",
                docucomp_uuid=None,
                long_name="Kongsberg EM1002",
            )
        if const == InstrumentConsts.R2SONIC2022:
            return CruiseInstrument(
                instrument_name="R2SONIC2022",
                docucomp_uuid=None,
                long_name="R2Sonic 2022",
            )
        if const == InstrumentConsts.ELACNAUTIK3020:
            return CruiseInstrument(
                instrument_name="ELACNAUTIK3020",
                docucomp_uuid=None,
                long_name="ELAC Nautik 3020",
            )
        if const == InstrumentConsts.SEABEAM3012L3:
            return CruiseInstrument(
                instrument_name="SB3012-L3",
                docucomp_uuid=None,
                long_name="SeaBeam 3012-L3",
            )
        if const == InstrumentConsts.HYDROCHARTII:
            return CruiseInstrument(
                instrument_name="HYDROCHARTII",
                docucomp_uuid=None,
                long_name="Hydrochart II",
            )
        if const == InstrumentConsts.SIMRADEM122:
            return CruiseInstrument(
                instrument_name="EM122", docucomp_uuid=None, long_name="Simrad EM122"
            )
        if const == InstrumentConsts.SIMRADEM3002:
            return CruiseInstrument(
                instrument_name="EM3002", docucomp_uuid=None, long_name="Simrad EM3002"
            )
        if const == InstrumentConsts.HAWKEYEII:
            return CruiseInstrument(
                instrument_name="HAWKEYEII", docucomp_uuid=None, long_name="HawkEye II"
            )
        if const == InstrumentConsts.SEABEAM3012P1:
            return CruiseInstrument(
                instrument_name="SB3012-P1",
                docucomp_uuid=None,
                long_name="SeaBeam 3012-P1",
            )
        if const == InstrumentConsts.RESON7111:
            return CruiseInstrument(
                instrument_name="RESON7111", docucomp_uuid=None, long_name="Reson 7111"
            )
        if const == InstrumentConsts.SEABEAM2120:
            return CruiseInstrument(
                instrument_name="SB2120", docucomp_uuid=None, long_name="SeaBeam 2120"
            )
        raise ValueError(ErrorConsts.NO_MATCHING_INSTRUMENT + ": " + const)
