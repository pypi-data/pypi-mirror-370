class CruiseInstrument(object):
    def __init__(self, instrument_name, docucomp_uuid, long_name, id=None):
        self.instrument_name = instrument_name
        self.docucomp_uuid = docucomp_uuid
        self.long_name = long_name
        self.id = id
