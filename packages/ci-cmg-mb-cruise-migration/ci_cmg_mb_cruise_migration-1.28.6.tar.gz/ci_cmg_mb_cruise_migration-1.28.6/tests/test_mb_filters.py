import unittest

import datetime

from mb_cruise_migration.framework.consts.file_label_consts import FileLabels
from mb_cruise_migration.framework.file_labeler import FileLabeler
from mb_cruise_migration.framework.file_validator import FileValidator
from mb_cruise_migration.framework.parsed_data_file import ParsedFilePath
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.models.intermediary.mb_cargo import MbFileCrate
from mb_cruise_migration.models.mb.mb_ngdcid_and_file import MbFile
from mb_cruise_migration.framework.file_filter import FileFilter
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.framework.file_decoder import FileDecoder


class TestSurveyFilter(unittest.TestCase):
    pass
    # TODO


class TestFileFilter(unittest.TestCase):

    file_standard = MbFile(
        ngdc_id='NEW2930',
        data_file='ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122/0140_20180617_101452_revelle.all.mb58.gz',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=32143468,
        filesize_gzip=15813031,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_standard.parsed_file = ParsedFilePath(file_standard.data_file)

    file_standard_nonpublic = MbFile(
        ngdc_id='NEW2930',
        data_file='ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/em122/nonpublic/0150_20180617_151453_revelle.all.mb58.gz',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_standard_nonpublic.parsed_file = ParsedFilePath(file_standard_nonpublic.data_file)

    file_standard_no_instrument_dir = MbFile(
        ngdc_id='NEW2930',
        data_file='ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/0140_20180617_101452_revelle.all.mb58.gz',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=32143468,
        filesize_gzip=15813031,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_standard_no_instrument_dir.parsed_file = ParsedFilePath(file_standard_no_instrument_dir.data_file)

    file_WCD = MbFile(
        ngdc_id='NEW2930',
        data_file='WCD',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_WCD.parsed_file = ParsedFilePath(file_WCD.data_file)

    file_singlebeam = MbFile(
        ngdc_id='NEW2930',
        data_file='singlebeam',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_singlebeam.parsed_file = ParsedFilePath(file_singlebeam.data_file)

    file_XTF = MbFile(
        ngdc_id='NEW2930',
        data_file='XTF',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_XTF.parsed_file = ParsedFilePath(file_XTF.data_file)

    file_Canadian = MbFile(
        ngdc_id='NEW2930',
        data_file='ocean/ships/Canadian_Data/1999/1999Sidney/filename.ext',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_Canadian.parsed_file = ParsedFilePath(file_Canadian.data_file)

    file_legs = MbFile(
        ngdc_id='NEW2930',
        data_file='oocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/leg1/0140_20180617_101452_revelle.all.mb58.gz',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_legs.parsed_file = ParsedFilePath(file_legs.data_file)

    file_region = MbFile(
        ngdc_id='NEW2930',
        data_file='ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/kauai/0140_20180617_101452_revelle.all.mb58.gz',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_region.parsed_file = ParsedFilePath(file_region.data_file)

    file_zone = MbFile(
        ngdc_id='NEW2930',
        data_file='ocean/ships/roger_revelle/RR1808/multibeam/data/version1/MB/ZONE_AGH/0140_20180617_101452_revelle.all.mb58.gz',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_zone.parsed_file = ParsedFilePath(file_zone.data_file)

    file_extraneous = MbFile(
        ngdc_id='NEW2930',
        data_file='ocean/ships/roger_revelle/RR1808/multibeam/data/version1/products/Backscatter/filename.ext',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_extraneous.parsed_file = ParsedFilePath(file_extraneous.data_file)

    file_survey_metadata = MbFile(
        ngdc_id='NEW2930',
        data_file='MGG/Multibeam/iso/xml/filename.file',
        format_id=58,
        entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
        status='arrgh matey',
        version=1,
        mostcurrent=1,
        version_id=0,
        process_notes='thar be dragons',
        filesize=23576814,
        filesize_gzip=13715710,
        filenotfound=None,
        publish='yes',
        previous_state='No',
        archive_path='/stornext/ngdc/archive/path/to/filename.ext'
    )
    file_survey_metadata.parsed_file = ParsedFilePath(file_survey_metadata.data_file)

    def test_filter_happy(self):
        MigrationProperties("config_test.yaml")
        MigrationLog()
        config = MigrationProperties.migrate
        config.extraneous = True
        config.legs = True
        config.zones = True
        config.regions = True
        config.survey_metadata = True
        config.standard = True

        files = [TestFileFilter.file_standard,
                 TestFileFilter.file_standard_nonpublic,
                 TestFileFilter.file_standard_no_instrument_dir]

        files = FileFilter.filter_invalid_files(files)
        files, removed = FileFilter.filter_files_not_configured_for_migration(files)
        files = FileLabeler.label(files)

        self.assertEqual(3, len(files))
        self.assertEqual(files[0].label, FileLabels.STANDARD)
        self.assertEqual(files[1].label, FileLabels.STANDARD)
        self.assertEqual(files[2].label, FileLabels.STANDARD)

    def test_filter_skip(self):
        MigrationProperties("config_test.yaml")
        MigrationLog()
        config = MigrationProperties.migrate
        config.extraneous = True
        config.legs = True
        config.zones = True
        config.regions = True
        config.survey_metadata = True
        config.standard = True

        files = [TestFileFilter.file_standard,
                 TestFileFilter.file_standard_nonpublic,
                 TestFileFilter.file_standard_no_instrument_dir,
                 TestFileFilter.file_WCD,
                 TestFileFilter.file_singlebeam,
                 TestFileFilter.file_XTF,
                 TestFileFilter.file_Canadian]

        files = FileFilter.filter_invalid_files(files)
        files, removed = FileFilter.filter_files_not_configured_for_migration(files)
        files = FileLabeler.label(files)

        self.assertEqual(3, len(files))
        self.assertEqual(files[0].label, FileLabels.STANDARD)
        self.assertEqual(files[1].label, FileLabels.STANDARD)
        self.assertEqual(files[2].label, FileLabels.STANDARD)

    def test_filter_config_expected(self):
        MigrationProperties("config_test.yaml")
        MigrationLog()
        config = MigrationProperties.migrate
        config.extraneous = False
        config.legs = False
        config.zones = False
        config.regions = False
        config.survey_metadata = True
        config.standard = True

        files = [TestFileFilter.file_standard,
                 TestFileFilter.file_standard_nonpublic,
                 TestFileFilter.file_standard_no_instrument_dir,
                 TestFileFilter.file_legs,
                 TestFileFilter.file_region,
                 TestFileFilter.file_zone,
                 TestFileFilter.file_survey_metadata,
                 TestFileFilter.file_extraneous]

        files = FileFilter.filter_invalid_files(files)
        files, removed = FileFilter.filter_files_not_configured_for_migration(files)
        files = FileLabeler.label(files)

        self.assertEqual(4, len(files))
        self.assertEqual(files[0].label, FileLabels.STANDARD)
        self.assertEqual(files[1].label, FileLabels.STANDARD)
        self.assertEqual(files[2].label, FileLabels.STANDARD)
        self.assertEqual(files[3].label, FileLabels.SURVEY_METADATA)

    def test_filter_config_flipped(self):
        MigrationProperties("config_test.yaml")
        MigrationLog()
        config = MigrationProperties.migrate
        config.extraneous = True
        config.legs = True
        config.zones = True
        config.regions = True
        config.survey_metadata = False
        config.standard = False

        files = [TestFileFilter.file_standard,
                 TestFileFilter.file_standard_nonpublic,
                 TestFileFilter.file_standard_no_instrument_dir,
                 TestFileFilter.file_legs,
                 TestFileFilter.file_region,
                 TestFileFilter.file_zone,
                 TestFileFilter.file_survey_metadata,
                 TestFileFilter.file_extraneous]

        files = FileFilter.filter_invalid_files(files)
        files, removed = FileFilter.filter_files_not_configured_for_migration(files)
        files = FileLabeler.label(files)

        self.assertEqual(4, len(files))
        self.assertEqual(files[0].label, FileLabels.LEG)
        self.assertEqual(files[1].label, FileLabels.REGION)
        self.assertEqual(files[2].label, FileLabels.ZONE)
        self.assertEqual(files[3].label, FileLabels.EXTRANEOUS)

    def test_missing_file_instrument_and_survey_instrument(self):
        MigrationProperties("config_test.yaml")
        MigrationLog()
        config = MigrationProperties.migrate
        config.standard = True

        files = [TestFileFilter.file_standard,
                 TestFileFilter.file_standard_no_instrument_dir]

        survey_instrument = "EM710"
        result = FileFilter.filter_invalid_files(files)
        result, removed = FileFilter.filter_files_not_configured_for_migration(result)
        result = FileLabeler.label(result)
        result = [MbFileCrate(file, None, None) for file in result]
        result = FileDecoder.decode(result)
        result = FileValidator.validate(result, survey_instrument)
        self.assertEqual(2, len(result))

        survey_instrument = None
        result = FileFilter.filter_invalid_files(files)
        result, removed = FileFilter.filter_files_not_configured_for_migration(result)
        result = FileLabeler.label(result)
        result = [MbFileCrate(file, None, None) for file in result]
        result = FileDecoder.decode(result)
        result, end_count = FileValidator.validate(result, survey_instrument)
        self.assertEqual(1, len(result))

    def test_missing_file_instrument_and_multiple_values_in_survey_instrument(self):
        MigrationProperties("config_test.yaml")
        MigrationLog()
        config = MigrationProperties.migrate
        config.standard = True

        files = [TestFileFilter.file_standard,
                 TestFileFilter.file_standard_no_instrument_dir]

        survey_instrument = "EM710"
        result = FileFilter.filter_invalid_files(files)
        result, removed = FileFilter.filter_files_not_configured_for_migration(result)
        result = FileLabeler.label(result)
        result = [MbFileCrate(file, None, None) for file in result]
        result = FileDecoder.decode(result)
        result = FileValidator.validate(result, survey_instrument)
        self.assertEqual(2, len(result))

        survey_instrument = "EM710; EM122"
        result = FileFilter.filter_invalid_files(files)
        result, removed = FileFilter.filter_files_not_configured_for_migration(result)
        result = FileLabeler.label(result)
        result = [MbFileCrate(file, None, None) for file in result]
        result = FileDecoder.decode(result)
        result, end_count = FileValidator.validate(result, survey_instrument)
        self.assertEqual(1, len(result))

    def test_sally_ride(self):

        file_sally_ride = MbFile(
            ngdc_id='NEW3141',
            data_file='ocean/ships/sally_ride/SR1611/multibeam/data/version1/MB/em712/0014_20161107_035652_ShipName.all.mb58.gz',
            format_id=58,
            entry_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
            process_date=datetime.datetime(2020, 5, 18, 1, 2, 4),
            status='arrgh matey',
            version=1,
            mostcurrent=1,
            version_id=0,
            process_notes='thar be dragons',
            filesize=32143468,
            filesize_gzip=15813031,
            filenotfound=None,
            publish='yes',
            previous_state='No',
            archive_path='/stornext/ngdc/archive/path/to/filename.ext'
        )

        parsed = ParsedFilePath(file_sally_ride.data_file)

        self.assertTrue(parsed.is_standard())
        self.assertTrue(parsed.has_instrument())


if __name__ == '__main__':
    unittest.main()
