import time
from typing import Optional

import oracledb
from oracledb import DatabaseError

from mb_cruise_migration.db.cruise_connection import CruiseConnection

from ncei_cruise_schema.entity.dataset_type import DatasetType
from ncei_cruise_schema.entity.file_format import FileFormat
from ncei_cruise_schema.entity.file_parameter import FileParameter
from ncei_cruise_schema.entity.file_shape_mapping import FileShapeMapping
from ncei_cruise_schema.entity.file_type import FileType
from ncei_cruise_schema.entity.project_parameter import ProjectParameter
from ncei_cruise_schema.entity.survey_shape_mapping import SurveyShapeMapping
from ncei_cruise_schema.entity.dataset_shape_mapping import DatasetShapeMapping
from ncei_cruise_schema.entity.version_description import VersionDescription

from mb_cruise_migration.db.query_builder import QueryBuilder
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.models.cruise.cruise_access_path import CruiseAccessPath
from mb_cruise_migration.models.cruise.cruise_dataset import CruiseDataset
from mb_cruise_migration.models.cruise.cruise_dataset_types import CruiseDatasetType
from mb_cruise_migration.models.cruise.cruise_file_formats import CruiseFileFormat
from mb_cruise_migration.models.cruise.cruise_file_types import CruiseFileType
from mb_cruise_migration.models.cruise.cruise_files import CruiseFile
from mb_cruise_migration.models.cruise.cruise_instruments import CruiseInstrument
from mb_cruise_migration.models.cruise.cruise_mappings import Mapping
from mb_cruise_migration.models.cruise.cruise_parameter import CruiseProjectParameter, CruiseSurveyParameter, CruiseDatasetParameter, CruiseFileParameter
from mb_cruise_migration.models.cruise.cruise_parameter_details import CruiseParameterDetail
from mb_cruise_migration.models.cruise.cruise_people_and_sources import CruisePeopleAndSources
from mb_cruise_migration.models.cruise.cruise_projects import CruiseProject
from mb_cruise_migration.models.cruise.cruise_shape import CruiseShape
from mb_cruise_migration.models.cruise.cruise_surveys import CruiseSurvey
from mb_cruise_migration.models.cruise.cruise_platforms import CruisePlatform

from ncei_cruise_schema.entity.dataset import Dataset
from ncei_cruise_schema.entity.dataset_instrument_mapping import DatasetInstrumentMapping
from ncei_cruise_schema.entity.dataset_parameter import DatasetParameter
from ncei_cruise_schema.entity.dataset_platform_mapping import DatasetPlatformMapping
from ncei_cruise_schema.entity.dataset_project_mapping import DatasetProjectMapping
from ncei_cruise_schema.entity.dataset_scientist_mapping import DatasetScientistMapping
from ncei_cruise_schema.entity.dataset_source_mapping import DatasetSourceMapping
from ncei_cruise_schema.entity.dataset_survey_mapping import DatasetSurveyMapping
from ncei_cruise_schema.entity.file_access_path_mapping import FileAccessPathMapping
from ncei_cruise_schema.entity.parameter_detail import ParameterDetail
from ncei_cruise_schema.entity.survey_parameter import SurveyParameter
from ncei_cruise_schema.entity.contact import Contact
from ncei_cruise_schema.entity.file import File
from ncei_cruise_schema.entity.instrument import Instrument
from ncei_cruise_schema.entity.platform import Platform
from ncei_cruise_schema.entity.project import Project
from ncei_cruise_schema.entity.shape import Shape
from ncei_cruise_schema.orm.query import Where, Order, And
from ncei_cruise_schema.entity.access_path import AccessPath
from ncei_cruise_schema.entity.survey import Survey
from mb_cruise_migration.models.cruise.cruise_version_descriptions import CruiseVersionDescription
from mb_cruise_migration.utility.common import normalize_date


def retry_on_disconnect(func):
    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (DatabaseError, OSError):
            time.sleep(2)
            try:
                return func(self, *args, **kwargs)
            except (DatabaseError, OSError) as e:
                raise RuntimeError(f"Failed on retry: {str(e)}")
    return wrap


class FileFormatService(object):
    def __init__(self, db):
        self.cruise = db

    @retry_on_disconnect
    def get_all_file_formats(self):
        entities = self.cruise.db.find(cls=FileFormat)
        return [self.from_entity(entity) for entity in entities]

    def save_file_format(self, model: CruiseFileFormat):
        entities = self.find_by_name(model.format_name)

        if entities is None:
            self.save_new_file_format(model)
            return

        for entity in entities:
            if entity.alt_id == model.alt_id:
                return

        first = entities[0]
        model.format_description = first.description
        self.update_file_format(first.id, model)

    @retry_on_disconnect
    def save_new_file_format(self, model: CruiseFileFormat) -> FileFormat:
        return self.cruise.db.save(self.from_model(model))

    @retry_on_disconnect
    def update_file_format(self, format_id: int, update: CruiseFileFormat):
        entity = self.find_by_id(format_id)
        entity.name = update.format_name
        entity.description = update.format_description
        entity.alt_id = update.alt_id

        return self.cruise.db.save(entity)

    @retry_on_disconnect
    def find_by_name(self, name) -> Optional[FileFormat]:
        entities = self.cruise.db.find(
            cls=FileFormat,
            where=Where(cls=FileFormat, field=FileFormat.name, op="=", value=name),
            orders=[Order(cls=FileFormat, field=FileFormat.id)]
        )
        return None if not entities else entities

    @retry_on_disconnect
    def find_by_id(self, id):
        return self.cruise.db.load(id=id, cls=FileFormat)

    @retry_on_disconnect
    def delete_file_format(self, entity: FileFormat):
        self.cruise.db.delete(entity)

    @staticmethod
    def from_model(model: CruiseFileFormat) -> FileFormat:
        return FileFormat(
            id=model.id,
            name=model.format_name,
            description=model.format_description
        )

    @staticmethod
    def from_entity(entity: FileFormat) -> CruiseFileFormat:
        return CruiseFileFormat(
            format_name=entity.name,
            format_description=entity.description,
            alt_id=entity.alt_id,
            id=entity.id
        )


class FileTypeService(object):
    def __init__(self, db):
        self.cruise = db

    @retry_on_disconnect
    def get_all_file_types(self) -> [CruiseFileType]:
        entities = self.cruise.db.find(cls=FileType)
        return [self.from_entity(entity) for entity in entities]

    def get_new_or_existing_file_type(self, model: CruiseFileType) -> FileType:
        entity = self.find_by_name(model.type_name)
        return entity if entity is not None else self.save_new_file_type(model)

    @retry_on_disconnect
    def save_new_file_type(self, model: CruiseFileType) -> FileType:
        return self.cruise.db.save(self.from_model(model))

    @retry_on_disconnect
    def find_by_name(self, name) -> Optional[FileType]:
        entities = self.cruise.db.find(
            cls=FileType,
            where=Where(cls=FileType, field=FileType.name, op="=", value=name),
            orders=[Order(cls=FileType, field=FileType.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def find_by_id(self, id):
        return self.cruise.db.load(id=id, cls=FileType)

    @retry_on_disconnect
    def delete_file_type(self, entity: FileType):
        self.cruise.db.delete(entity)

    @staticmethod
    def from_model(model: CruiseFileType) -> FileType:
        return FileType(
            id=model.id,
            name=model.type_name,
            description=model.type_description
        )

    @staticmethod
    def from_entity(entity: FileType) -> CruiseFileType:
        return CruiseFileType(
            type_name=entity.name,
            type_description=entity.description,
            id=entity.id
        )


class DatasetTypeService(object):
    def __init__(self, db):
        self.cruise = db

    @retry_on_disconnect
    def get_all_dataset_types(self) -> [CruiseDatasetType]:
        entities = self.cruise.db.find(cls=DatasetType)
        return [self.from_entity(entity) for entity in entities]

    def get_new_or_existing_dataset_type(self, model: CruiseDatasetType) -> DatasetType:
        entity = self.find_by_name(model.type_name)
        return entity if entity is not None else self.save_new_dataset_type(model)

    @retry_on_disconnect
    def save_new_dataset_type(self, model: CruiseDatasetType) -> DatasetType:
        return self.cruise.db.save(self.from_model(model))

    @retry_on_disconnect
    def find_by_name(self, name) -> Optional[DatasetType]:
        entities = self.cruise.db.find(
            cls=DatasetType,
            where=Where(cls=DatasetType, field=DatasetType.name, op="=", value=name),
            orders=[Order(cls=DatasetType, field=DatasetType.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def find_by_id(self, id):
        return self.cruise.db.load(id=id, cls=DatasetType)

    @retry_on_disconnect
    def delete_dataset_type(self, entity: DatasetType):
        self.cruise.db.delete(entity)

    @staticmethod
    def from_model(model: CruiseDatasetType) -> DatasetType:
        return DatasetType(
            id=model.id,
            name=model.type_name,
            description=model.type_description
        )

    @staticmethod
    def from_entity(entity: DatasetType) -> CruiseDatasetType:
        return CruiseDatasetType(
            type_name=entity.name,
            type_description=entity.description,
            id=entity.id,
        )


class VersionDescriptionService(object):
    def __init__(self, db):
        self.cruise = db

    @retry_on_disconnect
    def get_all_version_descriptions(self) -> [CruiseVersionDescription]:
        entities = self.cruise.db.find(cls=VersionDescription)
        return [self.from_entity(entity) for entity in entities]

    def get_new_or_existing_version_description(self, model: CruiseVersionDescription) -> VersionDescription:
        entity = self.find_by_id(model.id)  # TODO: update to use whatever other unique value will be used to identify vd
        return entity if entity is not None else self.save_new_version_description(model)

    @retry_on_disconnect
    def save_new_version_description(self, model: CruiseVersionDescription) -> VersionDescription:
        return self.cruise.db.save(self.from_model(model))

    @retry_on_disconnect
    def find_by_id(self, id):
        return self.cruise.db.load(id=id, cls=VersionDescription)

    @retry_on_disconnect
    def delete_version_description(self, entity: VersionDescription):
        self.cruise.db.delete(entity)

    @staticmethod
    def from_model(model: CruiseVersionDescription) -> VersionDescription:
        return VersionDescription(
            id=model.id,
            version_number=model.version_number,
            description=model.description,
            version_level=model.version_level  # TODO: add to orm (same as below)
        )

    @staticmethod
    def from_entity(entity: VersionDescription) -> CruiseVersionDescription:
        return CruiseVersionDescription(
            version_number=entity.version_number,
            description=entity.description,
            version_level=entity.version_level,  # TODO: add to orm (same as above)
            id=entity.id
        )


class ParameterDetailService(object):
    def __init__(self, db):
        self.cruise = db

    @retry_on_disconnect
    def get_all_parameter_details(self):
        entities = self.cruise.db.find(cls=ParameterDetail)
        return [self.from_entity(entity) for entity in entities]

    def get_new_or_existing_parameter_detail(self, parameter_detail: CruiseParameterDetail) -> CruiseParameterDetail:
        entity = self.find_parameter_detail_by_parameter(parameter_detail.parameter)
        return entity if entity is not None else self.save_new_parameter_detail(parameter_detail)

    @retry_on_disconnect
    def find_parameter_detail_by_parameter(self, parameter):
        entities = self.cruise.db.find(
            cls=ParameterDetail,
            where=Where(cls=ParameterDetail, field=ParameterDetail.parameter, op="=", value=parameter),
            orders=[Order(cls=ParameterDetail, field=ParameterDetail.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def find_parameter_detail_by_id(self):
        return self.cruise.db.load(id=id, cls=ParameterDetail)

    @retry_on_disconnect
    def save_new_parameter_detail(self, detail: CruiseParameterDetail) -> CruiseParameterDetail:
        entity = self.from_model(detail)
        return self.from_entity(self.cruise.db.save(entity))

    @staticmethod
    def from_model(model) -> ParameterDetail:
        return ParameterDetail(
            id=model.parameter_id,
            parameter=model.parameter,
            parameter_type=model.parameter_type,
            description=model.description,
            last_update_date=normalize_date(model.last_update_date, "cruise.parameter_detail.last_update_date"),
            last_updated_by=model.last_updated_by
        )

    @staticmethod
    def from_entity(entity: ParameterDetail) -> CruiseParameterDetail:
        return CruiseParameterDetail(
            id=entity.id,
            parameter=entity.parameter,
            parameter_type=entity.parameter_type,
            description=entity.description,
            last_update_date=entity.last_update_date,
            last_updated_by=entity.last_updated_by
        )


class ParameterService(object):
    def __init__(self, db):
        self.cruise = db

    @retry_on_disconnect
    def save_new_project_parameter(self, model: CruiseProjectParameter):
        entity = ProjectParameter(
            id=model.id,
            parameter_detail_id=model.parameter_detail_id,
            project_id=model.project_id,
            value=model.value,
            xml=model.xml,
            json=model.json
        )
        self.cruise.db.save(entity)

    def save_survey_parameter(self, survey_id: int, model: CruiseSurveyParameter):
        entity = self.find_by_survey_and_parameter_detail(survey_id, model.parameter_detail_id)
        return entity if entity is not None else self.save_new_survey_parameter(model)

    @retry_on_disconnect
    def save_new_survey_parameter(self, model: CruiseSurveyParameter):
        entity = SurveyParameter(
            id=model.id,
            parameter_detail_id=model.parameter_detail_id,
            survey_id=model.survey_id,
            value=model.value,
            xml=model.xml,
            json=model.json
        )
        self.cruise.db.save(entity)

    @retry_on_disconnect
    def save_new_dataset_parameter(self, model: CruiseDatasetParameter):
        entity = DatasetParameter(
            id=model.id,
            parameter_detail_id=model.parameter_detail_id,
            dataset_id=model.dataset_id,
            value=model.value,
            xml=model.xml,
            json=model.json
        )
        self.cruise.db.save(entity)

    @retry_on_disconnect
    def save_new_file_parameter(self, model: CruiseFileParameter):
        entity = FileParameter(
            id=model.id,
            parameter_detail_id=model.parameter_detail_id,
            file_id=model.file_id,
            value=model.value,
            xml=model.xml,
            json=model.json
        )
        self.cruise.db.save(entity)

    @retry_on_disconnect
    def find_by_survey_and_parameter_detail(self, survey_id: int, parameter_detail_id: int):
        entities = self.cruise.db.find(
            cls=SurveyParameter,
            where=And([
                Where(cls=SurveyParameter, field=SurveyParameter.survey_id, op="=", value=survey_id),
                Where(cls=SurveyParameter, field=SurveyParameter.parameter_detail_id, op="=", value=parameter_detail_id)
            ]),
            orders=[Order(cls=SurveyParameter, field=SurveyParameter.id)]
        )
        return None if not entities else entities[0]


class SurveyService(object):
    def __init__(self, db):
        self.cruise = db

    def get_new_or_existing_survey(self, survey: CruiseSurvey) -> Survey:
        entity = self.find_by_survey_name(survey.survey_name)
        return entity if entity is not None else self.save_new_survey(survey)

    @retry_on_disconnect
    def save_new_survey(self, model: CruiseSurvey) -> Optional[Survey]:
        try:
            return self.cruise.db.save(self.from_model(model))
        except Exception as e:
            MigrationLog.log_database_error(f"Failed to save survey {model.survey_name}", e)
            MigrationLog.log_exception(e)
            return None

    @retry_on_disconnect
    def save_survey_mapping(self, dataset_id, survey_id):
        mapping = DatasetSurveyMapping(dataset_id, survey_id)
        self.cruise.db.save(mapping)

    @retry_on_disconnect
    def find_by_id(self, id: int) -> Survey:
        return self.cruise.db.load(id=id, cls=Survey)

    @retry_on_disconnect
    def find_by_survey_name(self, name: str) -> Survey:
        entities = self.cruise.db.find(
            cls=Survey,
            where=Where(cls=Survey, field=Survey.name, op="=", value=name),
            orders=[Order(cls=Survey, field=Survey.id)]
        )
        if len(entities) > 1:
            raise ValueError("Multiple surveys with the same name found: " + name)
        return None if not entities else entities[0]

    @retry_on_disconnect
    def delete_survey(self, survey_entity: Survey):
        self.cruise.db.delete(survey_entity)

    @staticmethod
    def from_model(model: CruiseSurvey) -> Survey:
        return Survey(
            id=model.id,
            name=model.survey_name,
            parent=model.parent,
            platform_name=model.platform_name,
            start_date=normalize_date(model.start_date, "cruise.survey.start_date"),
            end_date=normalize_date(model.end_date, "cruise.survey.end_date"),
            departure_port=model.departure_port,
            arrival_port=model.arrival_port,
            last_update=normalize_date(model.last_update, "cruise.survey.last_update"),
            creation_date=normalize_date(model.creation_date, "cruise.survey.creation_date")
        )

    @staticmethod
    def from_entity(entity: Survey) -> CruiseSurvey:
        return CruiseSurvey(
            id=entity.id,
            survey_name=entity.name,
            parent=entity.parent,
            platform_name=entity.platform_name,
            start_date=entity.start_date,
            end_date=entity.end_date,
            departure_port=entity.departure_port,
            arrival_port=entity.arrival_port,
            creation_date=entity.creation_date,
            last_update=entity.last_update,
        )


class DatasetService(object):
    def __init__(self, db):
        self.cruise = db

    def save_survey_dataset(self, survey: Survey, dataset: CruiseDataset):
        entity = self.save_new_dataset(dataset)
        self.save_survey_dataset_mapping(survey.id, entity.id)

    @retry_on_disconnect
    def save_new_dataset(self, model: CruiseDataset) -> Optional[Dataset]:
        try:
            return self.cruise.db.save(self.from_model(model))
        except Exception as e:
            MigrationLog.log_database_error(message=f"Failed to save dataset {model.dataset_name} for survey(s) {model.surveys}", exception=e)
            MigrationLog.log_exception(e)
            return None

    @retry_on_disconnect
    def find_by_id(self, id: int) -> Dataset:
        return self.cruise.db.load(id=id, cls=Dataset)

    @retry_on_disconnect
    def find_by_dataset_name(self, name) -> Dataset:
        entities = self.cruise.db.find(
            cls=Dataset,
            where=Where(cls=Dataset, field=Dataset.name, op="=", value=name),
            orders=[Order(cls=Dataset, field=Dataset.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def save_survey_dataset_mapping(self, survey_id: int, dataset_id: int):
        mapping = DatasetSurveyMapping(dataset_id, survey_id)
        self.cruise.db.save(mapping)

    @retry_on_disconnect
    def find_survey_dataset_mapping(self, survey_id: int, dataset_id: int):
        entities = self.cruise.db.find(
            cls=DatasetSurveyMapping,
            where=And([
                Where(cls=DatasetSurveyMapping, field=DatasetSurveyMapping.survey_id, op="=", value=survey_id),
                Where(cls=DatasetSurveyMapping, field=DatasetSurveyMapping.dataset_id, op="=", value=dataset_id)
            ]),
            orders=[Order(cls=DatasetSurveyMapping, field=DatasetSurveyMapping.survey_id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def delete_dataset(self, entity: Dataset):
        self.cruise.db.delete(entity)

    @retry_on_disconnect
    def delete_survey_dataset_mapping(self, entity: DatasetSurveyMapping):
        self.cruise.db.delete(entity)

    @staticmethod
    def from_model(model: CruiseDataset) -> Dataset:
        return Dataset(
            id=model.id,
            other_id=model.other_id,
            name=model.dataset_name,
            dataset_type_name=model.dataset_type_name,
            dataset_type_id=model.dataset_type_id,
            instruments=model.instruments,
            platforms=model.platforms,
            doi=model.doi,
            archive_date=normalize_date(model.archive_date, "cruise.dataset.archive_date"),
            last_update=normalize_date(model.last_update, "cruise.dataset.last_update"),
            surveys=model.surveys,
            projects=model.projects
        )

    @staticmethod
    def from_entity(entity: Dataset) -> CruiseDataset:
        return CruiseDataset(
            other_id=entity.other_id,
            dataset_name=entity.name,
            dataset_type_name=entity.dataset_type_name,
            instruments=entity.instruments,
            platforms=entity.platforms,
            archive_date=entity.archive_date,
            surveys=entity.surveys,
            projects=entity.projects,
            doi=entity.doi,
            last_update=entity.last_update,
            id=entity.id,
            dataset_type_id=entity.dataset_type_id,
        )


class ContactService(object):
    def __init__(self, db):
        self.cruise = db

    def save_dataset_scientist(self, dataset: Dataset, scientist: CruisePeopleAndSources):
        contact_entity = self.get_new_or_existing_scientist(scientist)
        self.save_scientist_mapping(dataset.id, contact_entity.id)

    def save_dataset_source(self, dataset: Dataset, source: CruisePeopleAndSources):
        contact_entity = self.get_new_or_existing_source(source)
        self.save_source_mapping(dataset.id, contact_entity.id)

    def get_new_or_existing_scientist(self, scientist: CruisePeopleAndSources):
        entity = self.find_by_name_and_organization(scientist.name, scientist.organization)
        return entity if entity is not None else self.save_new_contact(scientist)

    def get_new_or_existing_source(self, source: CruisePeopleAndSources):
        entity = self.find_by_organization_only(source.organization)
        return entity if entity is not None else self.save_new_contact(source)

    @retry_on_disconnect
    def find_by_id(self, id: int) -> Contact:
        return self.cruise.db.load(id=id, cls=Contact)

    @retry_on_disconnect
    def find_by_name_and_organization(self, name, organization) -> Contact:
        entities = self.cruise.db.find(
            cls=Contact,
            where=And([
                Where(cls=Contact, field=Contact.name, op="=", value=name),
                Where(cls=Contact, field=Contact.organization, op="=", value=organization)
            ]),
            orders=[Order(cls=Contact, field=Contact.id)]
        )
        return None if not entities else entities[0]  # finds first even if there are many

    @retry_on_disconnect
    def find_by_organization_only(self, name):
        entities = self.cruise.db.find(
            cls=Contact,
            where=Where(cls=Contact, field=Contact.organization, op="=", value=name),
            orders=[Order(cls=Contact, field=Contact.id)]
        )
        if not entities:
            return None

        for entity in entities:
            if not entity.name:
                return entity  # source contact should be organization only, no name.

        return None

    @retry_on_disconnect
    def save_new_contact(self, model: CruisePeopleAndSources) -> Optional[Contact]:
        try:
            return self.cruise.db.save(self.from_model(model))
        except Exception as e:
            name = model.name
            organization = model.organization
            if name and organization:
                MigrationLog.log_database_error(f"Failed to save contact {name} of {organization}", e)
            if name and not organization:
                MigrationLog.log_database_error(f"Failed to save contact with name {name}", e)
            if not name and organization:
                MigrationLog.log_database_error(f"Failed to save contact with org {organization}", e)
            MigrationLog.log_exception(e)
            return None

    @retry_on_disconnect
    def save_scientist_mapping(self, dataset_id, contact_id):
        mapping = DatasetScientistMapping(dataset_id, contact_id)
        self.cruise.db.save(mapping)

    @retry_on_disconnect
    def save_source_mapping(self, dataset_id, contact_id):
        mapping = DatasetSourceMapping(dataset_id, contact_id)
        self.cruise.db.save(mapping)

    @retry_on_disconnect
    def delete_contact(self, contact_entity: Contact):
        self.cruise.db.delete(contact_entity)

    @retry_on_disconnect
    def delete_scientist_mapping(self, mapping: DatasetScientistMapping):
        self.cruise.db.delete(mapping)

    @retry_on_disconnect
    def delete_source_mapping(self, mapping: DatasetSourceMapping):
        self.cruise.db.delete(mapping)

    @staticmethod
    def from_model(model: CruisePeopleAndSources) -> Contact:
        return Contact(
            id=model.id,
            name=model.name,
            position=model.position,
            organization=model.organization,
            street=model.street,
            city=model.city,
            state=model.state,
            zip=model.zipcode,
            country=model.country,
            phone=model.phone,
            email=model.email,
            orcid=model.orcid,
            docucomp_uuid=model.docucomp_uuid,
            first=model.first,
            last=model.last,
            prefix=model.prefix,
            middle=model.middle,
            suffix=model.suffix
        )

    @staticmethod
    def from_entity(entity: Contact) -> CruisePeopleAndSources:
        return CruisePeopleAndSources(
            id=entity.id,
            name=entity.name,
            position=entity.position,
            organization=entity.position,
            street=entity.street,
            city=entity.city,
            state=entity.state,
            zipcode=entity.zip,
            country=entity.country,
            phone=entity.phone,
            email=entity.email,
            orcid=entity.orcid,
            docucomp_uuid=entity.docucomp_uuid,
            first=entity.first,
            last=entity.last,
            prefix=entity.prefix,
            middle=entity.middle,
            suffix=entity.suffix,
        )


class InstrumentService(object):
    def __init__(self, db):
        self.cruise = db

    def save_dataset_instrument(self, dataset_entity, instrument_model):
        instrument_entity = self.get_new_or_existing_instrument(instrument_model)
        self.save_dataset_instrument_mapping(dataset_entity.id, instrument_entity.id)
        return

    def get_new_or_existing_instrument(self, instrument: CruiseInstrument) -> Instrument:
        entity = self.find_by_instrument_name(instrument.instrument_name)
        return entity if entity is not None else self.save_new_instrument(instrument)

    @retry_on_disconnect
    def find_by_id(self, id: int) -> Instrument:
        return self.cruise.db.load(id=id, cls=Instrument)

    @retry_on_disconnect
    def find_by_instrument_name(self, name: str):
        entities = self.cruise.db.find(
            cls=Instrument,
            where=Where(cls=Instrument, field=Instrument.name, op="=", value=name),
            orders=[Order(cls=Instrument, field=Instrument.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def save_new_instrument(self, model: CruiseInstrument) -> Optional[Instrument]:
        try:
            return self.cruise.db.save(self.from_model(model))
        except Exception as e:
            MigrationLog.log_database_error(f"Failed to save instrument {model.instrument_name}", e)
            MigrationLog.log_exception(e)
            return None

    @retry_on_disconnect
    def save_dataset_instrument_mapping(self, dataset_id: int, instrument_id: id):
        mapping = DatasetInstrumentMapping(dataset_id, instrument_id)
        self.cruise.db.save(mapping)

    @retry_on_disconnect
    def find_dataset_instrument_mapping(self, dataset_id: int, instrument_id: int):
        entities = self.cruise.db.find(
            cls=DatasetInstrumentMapping,
            where=And([
                Where(cls=DatasetInstrumentMapping, field=DatasetInstrumentMapping.dataset_id, op="=", value=dataset_id),
                Where(cls=DatasetInstrumentMapping, field=DatasetInstrumentMapping.instrument_id, op="=", value=instrument_id)
            ]),
            orders=[Order(cls=DatasetInstrumentMapping, field=DatasetInstrumentMapping.instrument_id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def delete_instrument(self, instrument_entity: Instrument):
        self.cruise.db.delete(instrument_entity)

    @retry_on_disconnect
    def delete_dataset_instrument_mapping(self, mapping: DatasetInstrumentMapping):
        self.cruise.db.delete(mapping)

    @staticmethod
    def from_model(model: CruiseInstrument) -> Instrument:
        return Instrument(
            id=model.id,
            name=model.instrument_name,
            long_name=model.long_name,
            docucomp_uuid=model.docucomp_uuid,
        )

    @staticmethod
    def from_entity(entity: Instrument) -> CruiseInstrument:
        return CruiseInstrument(
            id=entity.id,
            instrument_name=entity.name,
            docucomp_uuid=entity.docucomp_uuid,
            long_name=entity.long_name
        )


class PlatformService(object):
    def __init__(self, db):
        self.cruise = db

    @retry_on_disconnect
    def get_all_platforms(self):
        entities = self.cruise.db.find(cls=Platform)
        return [self.from_entity(entity) for entity in entities]

    def save_dataset_platform(self, dataset: Dataset, platform: CruisePlatform):
        platform_entity = self.get_new_or_existing_platform(platform)
        self.save_dataset_platform_mapping(dataset.id, platform_entity.id)

    def get_new_or_existing_platform(self, platform: CruisePlatform) -> Platform:
        entity = self.find_by_internal_name(platform.internal_name)
        return entity if entity is not None else self.save_new_platform(platform)

    @retry_on_disconnect
    def save_new_platform(self, model: CruisePlatform) -> Optional[Platform]:
        try:
            return self.cruise.db.save(self.from_model(model))
        except Exception as e:
            MigrationLog.log_database_error(f"Failed to save platform {model.internal_name}", e)
            MigrationLog.log_exception(e)
            return None

    @retry_on_disconnect
    def save_dataset_platform_mapping(self, dataset_id: int, platform_id: int):
        mapping = DatasetPlatformMapping(dataset_id, platform_id)
        self.cruise.db.save(mapping)

    @retry_on_disconnect
    def find_by_id(self, id: int) -> Platform:
        return self.cruise.db.load(id=id, cls=Platform)

    @retry_on_disconnect
    def find_by_internal_name(self, name):
        entities = self.cruise.db.find(
            cls=Platform,
            where=Where(cls=Platform, field=Platform.internal_name, op="=", value=name),
            orders=[Order(cls=Platform, field=Platform.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def find_dataset_platform_mapping(self, dataset_id, platform_id):
        entities = self.cruise.db.find(
            cls=DatasetPlatformMapping,
            where=And([
                Where(cls=DatasetPlatformMapping, field=DatasetPlatformMapping.dataset_id, op="=", value=dataset_id),
                Where(cls=DatasetPlatformMapping, field=DatasetPlatformMapping.platform_id, op="=", value=platform_id)
            ]),
            orders=[Order(cls=DatasetPlatformMapping, field=DatasetPlatformMapping.platform_id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def delete_platform(self, platform_entity: Platform):
        self.cruise.db.delete(platform_entity)

    @retry_on_disconnect
    def delete_dataset_platform_mapping(self, mapping):
        self.cruise.db.delete(mapping)

    @staticmethod
    def from_model(model: CruisePlatform) -> Platform:
        return Platform(
            id=model.id,
            name=model.platform_name,
            internal_name=model.internal_name,
            long_name=model.long_name,
            type=model.platform_type,
            docucomp_uuid=model.docucomp_uuid,
            designator=model.designator
        )

    @staticmethod
    def from_entity(entity: Platform) -> CruisePlatform:
        return CruisePlatform(
            id=entity.id,
            internal_name=entity.internal_name,
            platform_type=entity.type,
            docucomp_uuid=entity.docucomp_uuid,
            long_name=entity.long_name,
            designator=entity.designator,
            platform_name=entity.name
        )


class ProjectService(object):
    def __init__(self, db):
        self.cruise = db

    def save_dataset_project(self, dataset: Dataset, project: CruiseProject) -> Project:
        project_entity = self.get_new_or_existing_project(project)
        self.save_dataset_project_mapping(dataset.id, project_entity.id)
        return project_entity

    def get_new_or_existing_project(self, project: CruiseProject) -> Project:
        entity = self.find_by_project_name(project.project_name)
        return entity if entity is not None else self.save_new_project(project)

    @retry_on_disconnect
    def save_new_project(self, model: CruiseProject) -> Optional[Project]:
        try:
            return self.cruise.db.save(self.from_model(model))
        except Exception as e:
            MigrationLog.log_database_error(f"Failed to save project {model.project_name}", e)
            MigrationLog.log_exception(e)
            return None

    @retry_on_disconnect
    def save_dataset_project_mapping(self, dataset_id: int, project_id: int):
        mapping = DatasetProjectMapping(dataset_id, project_id)
        self.cruise.db.save(mapping)

    @retry_on_disconnect
    def find_by_id(self, id: int) -> Project:
        return self.cruise.db.load(id=id, cls=Project)

    @retry_on_disconnect
    def find_by_project_name(self, project_name: str) -> Project:
        entities = self.cruise.db.find(
            cls=Project,
            where=Where(cls=Project, field=Project.name, op="=", value=project_name),
            orders=[Order(cls=Project, field=Project.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def find_dataset_project_mapping(self, dataset_id, project_id):
        entities = self.cruise.db.find(
            cls=DatasetProjectMapping,
            where=And([
                Where(cls=DatasetProjectMapping, field=DatasetProjectMapping.dataset_id, op="=", value=dataset_id),
                Where(cls=DatasetProjectMapping, field=DatasetProjectMapping.project_id, op="=", value=project_id)
            ]),
            orders=[Order(cls=DatasetProjectMapping, field=DatasetProjectMapping.project_id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def delete_project(self, project_entity: Project):
        self.cruise.db.delete(project_entity)

    @retry_on_disconnect
    def delete_dataset_project_mapping(self, mapping):
        self.cruise.db.delete(mapping)

    @staticmethod
    def from_model(model: CruiseProject) -> Project:
        return Project(
            id=model.id,
            name=model.project_name
        )

    @staticmethod
    def from_entity(entity: Project) -> CruiseProject:
        return CruiseProject(
            id=entity.id,
            project_name=entity.name
        )


class FileService(object):
    def __init__(self, db):
        self.cruise = db

    @retry_on_disconnect
    def save_new_file(self, model: CruiseFile) -> File:
        return self.cruise.db.save(self.from_model(model))

    @retry_on_disconnect
    def find_by_id(self, id: int) -> File:
        return self.cruise.db.load(id=id, cls=File)

    @retry_on_disconnect
    def find_by_file_name(self, name):
        entities = self.cruise.db.find(
            cls=File,
            where=Where(cls=File, field=File.name, op="=", value=name),
            orders=[Order(cls=File, field=File.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def delete_file(self, file_entity: File):
        self.cruise.db.delete(file_entity)

    @staticmethod
    def from_model(model: CruiseFile) -> File:
        return File(
            id=model.id,
            dataset_id=model.dataset_id,
            name=model.file_name,
            raw_size=model.raw_size,
            publish=model.publish,
            collection_date=normalize_date(model.collection_date, "cruise.file.collection_date"),
            publish_date=normalize_date(model.publish_date, "cruise.file.publish_date"),
            version_id=model.version_id,
            type_id=model.type_id,
            format_id=model.format_id,
            archive_date=normalize_date(model.archive_date, "cruise.file.archive_date"),
            last_update=normalize_date(model.last_update, "cruise.file.last_update"),
            gzip_size=model.gzip_size
        )

    @staticmethod
    def from_entity(entity: File) -> CruiseFile:
        return CruiseFile(
            id=entity.id,
            dataset_id=entity.dataset_id,
            file_name=entity.name,
            raw_size=entity.raw_size,
            publish=entity.publish,
            collection_date=entity.publish_date,
            publish_date=entity.publish_date,
            version_id=entity.version_id,
            type_id=entity.type_id,
            format_id=entity.format_id,
            archive_date=entity.archive_date,
            temp_id=entity.temp_id,
            gzip_size=entity.gzip_size
        )


class AccessPathService(object):
    def __init__(self, db):
        self.cruise = db

    def save_file_access_path(self, file: File, access_path: AccessPath):
        if file is None or file.id is None or access_path is None or access_path.id is None:
            raise RuntimeError("file entity and access path entity must exist before mapping can be created")
        self.save_file_and_access_path_mapping(file.id, access_path.id)

    def get_new_or_existing_access_path(self, access_path: CruiseAccessPath) -> AccessPath:
        entity = self.find_by_path_and_path_type(access_path.path, access_path.path_type)
        return entity if entity is not None else self.save_new_access_path(access_path)

    @retry_on_disconnect
    def save_new_access_path(self, model: CruiseAccessPath) -> AccessPath:
        return self.cruise.db.save(self.from_model(model))

    @retry_on_disconnect
    def save_file_and_access_path_mapping(self, file_id: int, access_path_id: int):
        mapping = FileAccessPathMapping(file_id, access_path_id)
        self.cruise.db.save(mapping)

    @retry_on_disconnect
    def find_by_id(self, id: int) -> AccessPath:
        return self.cruise.db.load(id=id, cls=AccessPath)

    @retry_on_disconnect
    def find_by_path_and_path_type(self, path: str, path_type: str) -> AccessPath:
        entities = self.cruise.db.find(
            cls=AccessPath,
            where=And([
                Where(cls=AccessPath, field=AccessPath.path, op="=", value=path),
                Where(cls=AccessPath, field=AccessPath.path_type, op="=", value=path_type)
            ]),
            orders=[Order(cls=AccessPath, field=AccessPath.id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def find_file_access_path_mapping(self, file_id, access_path_id):
        entities = self.cruise.db.find(
            cls=FileAccessPathMapping,
            where=And([
                Where(cls=FileAccessPathMapping, field=FileAccessPathMapping.file_id, op="=", value=file_id),
                Where(cls=FileAccessPathMapping, field=FileAccessPathMapping.access_path_id, op="=", value=access_path_id)
            ]),
            orders=[Order(cls=FileAccessPathMapping, field=FileAccessPathMapping.access_path_id)]
        )
        return None if not entities else entities[0]

    @retry_on_disconnect
    def delete_access_path(self, access_path: AccessPath):
        self.cruise.db.delete(access_path)

    @retry_on_disconnect
    def delete_file_access_path_mapping(self, mapping: FileAccessPathMapping):
        self.cruise.db.delete(mapping)

    @staticmethod
    def from_model(model: CruiseAccessPath) -> AccessPath:
        return AccessPath(path=model.path, path_type=model.path_type)

    @staticmethod
    def from_entity(entity: AccessPath) -> CruiseAccessPath:
        return CruiseAccessPath(entity.path, entity.path_type, id=entity.id)


class ShapeService(object):
    def __init__(self, db):
        self.cruiseORM = db
        self.cruise = CruiseConnection()
        self.query_builder = QueryBuilder("CRUISE")

        # acquire types used for creating SDO_GEOMETRY objects
        self.shape_obj = self.cruise.get_type_obj("MDSYS.SDO_GEOMETRY")
        self.shape_element_info_obj = self.cruise.get_type_obj("MDSYS.SDO_ELEM_INFO_ARRAY")
        self.shape_ordinates_obj = self.cruise.get_type_obj("MDSYS.SDO_ORDINATE_ARRAY")

    def save_survey_shape(self, survey, model):
        shape = self.save_new_shape(model)
        self.save_survey_shape_mapping(survey.id, shape.id)

    def save_dataset_shape(self, dataset, model: CruiseShape):
        shape = self.save_new_shape(model)
        self.save_dataset_shape_mapping(dataset.id, shape.id)

    @staticmethod
    def chunkstring(self, string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))

    def save_file_shape(self, file, model):
        shape = self.save_new_shape(model)
        self.save_file_shape_mapping(file.id, shape.id)

    def save_new_shape(self, model: CruiseShape) -> Shape:
        """
        creates a temporary LOB object in oracle db, writing WKT object to LOB contents during creation
        uses shapes table sequence to get next id value
        creates shape, inserting temporary lob directly into SDO_GEOMETRY() constructor method, which accepts lobs
        :param CruiseShape model:
        :return: Shape entity
        """
        cmd = "INSERT INTO CRUISE.SHAPES(SHAPE_ID, SHAPE, SHAPE_TYPE, GEOM_TYPE) VALUES (:SHAPE_ID, SDO_GEOMETRY(:SHAPE, 8307), :SHAPE_TYPE, :GEOM_TYPE)"

        with self.cruise.get_connection() as connection:
            cursor = connection.cursor()

            clob = connection.createlob(oracledb.DB_TYPE_CLOB, model.shape)
            cursor.execute("SELECT CRUISE.shapes_seq.nextval FROM dual".format(schema="CRUISE", sequence="shapes_seq"))
            model.id = cursor.fetchone()[0]

            insert_values = {'SHAPE_ID': model.id, 'SHAPE': clob, 'SHAPE_TYPE': model.shape_type, 'GEOM_TYPE': model.geom_type}
            cursor.execute(cmd, insert_values)
            connection.commit()

        return self.from_model(model)

    @retry_on_disconnect
    def save_file_shape_mapping(self, file_id, shape_id):
        mapping = FileShapeMapping(file_id, shape_id)
        self.cruiseORM.db.save(mapping)

    @retry_on_disconnect
    def save_dataset_shape_mapping(self, dataset_id, shape_id):
        mapping = DatasetShapeMapping(dataset_id, shape_id)
        self.cruiseORM.db.save(mapping)

    @retry_on_disconnect
    def save_survey_shape_mapping(self, survey_id, shape_id):
        mapping = SurveyShapeMapping(survey_id, shape_id)
        self.cruiseORM.db.save(mapping)

    @retry_on_disconnect
    def delete_shape(self, shape_entity: Shape):
        self.cruiseORM.db.delete(shape_entity)

    def delete_file_shape_mapping(self, shape_id, file_id):
        pass

    def delete_survey_shape_mapping(self, shape_id, survey_id):
        pass

    @staticmethod
    def from_model(model: CruiseShape) -> Shape:
        return Shape(
            id=model.id,
            shape=model.shape,
            geom_type=model.geom_type,
            shape_type=model.shape_type,
        )

    @staticmethod
    def from_entity(entity: Shape) -> CruiseShape:
        return CruiseShape(
            id=entity.id,
            shape_type=entity.shape_type,
            geom_type=entity.geom_type,
            shape=entity.shape
        )


class BatchService(object):
    def __init__(self):
        self.cruise = CruiseConnection()
        self.query_builder = QueryBuilder("CRUISE")

    def batch_insert_mapping(self, mapping_tuples, mapping: Mapping):
        query = self.query_builder.insert_statement(mapping.get_table(), mapping.fields)
        errors = self.cruise.executemany(query, mapping_tuples)
        if errors:
            MigrationLog.log_batch_insert_errors(errors, mapping_tuples, context_message=mapping.get_context())
