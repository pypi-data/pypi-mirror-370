class CruiseFile(object):
    def __init__(
            self,
            file_name,
            raw_size,
            publish,
            collection_date,
            publish_date,
            archive_date,
            temp_id,
            gzip_size,
            id=None,
            dataset_id=None,
            version_id=None,
            type_id=None,
            format_id=None,
            last_update=None
            ):
        self.file_name = file_name
        self.raw_size = raw_size
        self.publish = publish
        self.collection_date = collection_date
        self.publish_date = publish_date
        self.archive_date = archive_date
        self.temp_id = temp_id
        self.gzip_size = gzip_size
        self.id = id
        self.dataset_id = dataset_id
        self.version_id = version_id
        self.type_id = type_id
        self.format_id = format_id
        self.last_update = last_update
