class MbFileFormat(object):
    def __init__(self, format_name, id):
        self.format_name = format_name
        self.id = id

    @staticmethod
    def build(file_format: dict):
        return MbFileFormat(
            file_format['FORMAT_NAME'],
            file_format['ID']
        )
