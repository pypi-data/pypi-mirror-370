class CruisePeopleAndSources(object):
    def __init__(
            self,
            id=None,
            name=None,
            position=None,
            organization=None,
            street=None,
            city=None,
            state=None,
            zipcode=None,
            country=None,
            phone=None,
            email=None,
            orcid=None,
            docucomp_uuid=None,
            first=None,
            last=None,
            prefix=None,
            middle=None,
            suffix=None,
            ):
        self.id = id
        self.name = name
        self.position = position
        self.organization = organization
        self.street = street
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.country = country
        self.phone = phone
        self.email = email
        self.orcid = orcid
        self.docucomp_uuid = docucomp_uuid
        self.first = first
        self.last = last
        self.prefix = prefix
        self.middle = middle
        self.suffix = suffix


# class CruiseSource(CruisePeopleAndSources):
#     def __init__(self):
#         super().__init__()
#
#
# class CruiseScientist(CruisePeopleAndSources):
#     def __init__(self):
#         super().__init__()
