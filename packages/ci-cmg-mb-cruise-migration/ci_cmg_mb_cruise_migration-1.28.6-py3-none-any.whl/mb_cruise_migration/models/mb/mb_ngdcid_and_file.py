import mb_cruise_migration.utility.common as util
from mb_cruise_migration.framework.parsed_data_file import ParsedFilePath


class MbFile(object):
    def __init__(self,
                 ngdc_id,
                 data_file,
                 format_id,
                 entry_date,
                 process_date,
                 status,
                 version,
                 mostcurrent,
                 version_id,
                 process_notes,
                 filesize,
                 filesize_gzip,
                 filenotfound,
                 publish,
                 previous_state,
                 archive_path
                 ):
        self.__ngdc_id = ngdc_id
        self.__data_file = data_file
        self.__format_id = format_id
        self.__entry_date = entry_date
        self.__process_date = process_date
        self.__status = status
        self.__version = version
        self.__mostcurrent = mostcurrent
        self.__version_id = version_id
        self.__process_notes = process_notes
        self.__filesize = filesize
        self.__filesize_gzip = filesize_gzip
        self.__filenotfound = filenotfound
        self.__publish = publish
        self.__previous_state = previous_state
        self.__archive_path = archive_path
        self.parsed_file = None
        self.label = None

    @property
    def ngdc_id(self):
        return self.__ngdc_id

    @ngdc_id.setter
    def ngdc_id(self, ngdc_id):
        self.__ngdc_id = ngdc_id

    @property
    def data_file(self):
        return self.__data_file

    @data_file.setter
    def data_file(self, data_file):
        self.__data_file = data_file

    @property
    def format_id(self):
        return self.__format_id

    @format_id.setter
    def format_id(self, format_id):
        self.__format_id = format_id

    @property
    def entry_date(self):
        return self.__entry_date

    @entry_date.setter
    def entry_date(self, entry_date):
        self.__entry_date = entry_date

    @property
    def process_date(self):
        return self.__process_date

    @process_date.setter
    def process_date(self, process_date):
        self.__process_date = process_date

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, version):
        self.__version = version

    @property
    def mostcurrent(self):
        return self.__mostcurrent

    @mostcurrent.setter
    def mostcurrent(self, mostcurrent):
        self.__mostcurrent = mostcurrent

    @property
    def version_id(self):
        return self.__version_id

    @version_id.setter
    def version_id(self, version_id):
        self.__version_id = version_id

    @property
    def process_notes(self):
        return self.__process_notes

    @process_notes.setter
    def process_notes(self, process_notes):
        self.__process_notes = process_notes

    @property
    def filesize(self):
        return self.__filesize

    @filesize.setter
    def filesize(self, filesize):
        self.__filesize = filesize

    @property
    def filesize_gzip(self):
        return self.__filesize_gzip

    @filesize_gzip.setter
    def filesize_gzip(self, filesize_gzip):
        self.__filesize_gzip = filesize_gzip

    @property
    def filenotfound(self):
        return self.__filenotfound

    @filenotfound.setter
    def filenotfound(self, filenotfound):
        self.__filenotfound = filenotfound

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
    def archive_path(self):
        return self.__archive_path

    @archive_path.setter
    def archive_path(self, archive_path):
        self.__archive_path = archive_path

    @staticmethod
    def build(file: dict):
        file = MbFile(
            file['NGDC_ID'],
            file['DATA_FILE'],
            file['FORMAT_ID'],
            util.dict_value_or_none(file, 'ENTRY_DATE'),
            util.dict_value_or_none(file, 'PROCESS_DATE'),
            util.dict_value_or_none(file, 'STATUS'),
            file['VERSION'],
            file['MOSTCURRENT'],
            util.dict_value_or_none(file, 'VERSION_ID'),
            util.dict_value_or_none(file, 'PROCESS_NOTES'),
            util.dict_value_or_none(file, 'FILESIZE'),
            util.dict_value_or_none(file, 'FILESIZE_GZIP'),
            util.dict_value_or_none(file, 'FILENOTFOUND'),
            util.dict_value_or_none(file, 'PUBLISH'),
            util.dict_value_or_none(file, 'PREVIOUS_STATE'),
            util.dict_value_or_none(file, 'ARCHIVE_PATH')
        )
        file.parsed_file = ParsedFilePath(file.data_file)
        return file

