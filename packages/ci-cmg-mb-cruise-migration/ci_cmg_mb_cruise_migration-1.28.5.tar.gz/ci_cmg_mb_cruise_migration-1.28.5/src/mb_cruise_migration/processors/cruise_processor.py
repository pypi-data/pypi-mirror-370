from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple

from ncei_cruise_schema.entity.access_path import AccessPath
from ncei_cruise_schema.entity.contact import Contact
from ncei_cruise_schema.entity.dataset import Dataset
from ncei_cruise_schema.entity.instrument import Instrument
from ncei_cruise_schema.entity.platform import Platform
from ncei_cruise_schema.entity.survey import Survey

from mb_cruise_migration.db.cruise_db import CruiseDb
from mb_cruise_migration.framework.cache import Cache
from mb_cruise_migration.framework.thread_safe_mappings import ThreadSafeMappings
from mb_cruise_migration.logging.migration_log import MigrationLog
from mb_cruise_migration.migration_properties import MigrationProperties
from mb_cruise_migration.logging.migration_report import MigrationReport
from mb_cruise_migration.models.cruise.cruise_access_path import CruiseAccessPath
from mb_cruise_migration.models.cruise.cruise_instruments import CruiseInstrument
from mb_cruise_migration.models.cruise.cruise_mappings import FileAccessPath, DatasetsSurveys, DatasetScientist, DatasetSource, DatasetPlatform, \
    DatasetProject, DatasetInstrument
from mb_cruise_migration.models.cruise.cruise_people_and_sources import CruisePeopleAndSources
from mb_cruise_migration.models.cruise.cruise_platforms import CruisePlatform
from mb_cruise_migration.models.intermediary.cruise_cargo import CruiseCargo, \
    CruiseSurveyCrate, CruiseDatasetCrate, CruiseProjectCrate, CruiseFileCrate
from mb_cruise_migration.models.intermediary.migrating_survey import MigratingSurvey
from mb_cruise_migration.services.cruise_service import ParameterService, SurveyService, \
    DatasetService, ContactService, InstrumentService, PlatformService, \
    ProjectService, FileService, AccessPathService, ShapeService, BatchService
from mb_cruise_migration.utility.common import strip_none


class CruiseProcessor(object):
    platform_cache = Cache()
    scientist_cache = Cache()
    source_cache = Cache()
    project_cache = Cache()
    instrument_cache = Cache()

    def __init__(self):
        db = CruiseDb(MigrationProperties.cruise_db_config.pooled)
        self.use_batch = MigrationProperties.run_parameters.batch_insert_mappings
        self.parameter_service = ParameterService(db)
        self.survey_service = SurveyService(db)
        self.dataset_service = DatasetService(db)
        self.contact_service = ContactService(db)
        self.instrument_service = InstrumentService(db)
        self.platform_service = PlatformService(db)
        self.project_service = ProjectService(db)
        self.file_service = FileService(db)
        self.access_path_service = AccessPathService(db)
        self.shape_service = ShapeService(db)
        self.batch_service = BatchService()
        self.survey_cache = Cache()
        self.access_path_cache = Cache()
        self.migrating_surveys: set[MigratingSurvey] = set()
        self.dataset_instrument_mappings = ThreadSafeMappings()
        self.dataset_project_mappings = ThreadSafeMappings()
        self.dataset_platform_mappings = ThreadSafeMappings()
        self.dataset_source_mappings = ThreadSafeMappings()
        self.dataset_scientist_mappings = ThreadSafeMappings()
        self.dataset_survey_mappings = ThreadSafeMappings()
        self.file_access_path_mappings = ThreadSafeMappings()

    def ship(self, cruise_cargo: [CruiseCargo]):
        try:
            for cargo in cruise_cargo:
                try:
                    self.__process_cargo(cargo)
                except Exception as w:
                    MigrationLog.log_failed_dataset(str(w))
                    continue
            if self.use_batch:
                self.__batch_process_join_table_mappings()
            self.__lazy_log_survey_completion()
            self.__trim_caches()
        except Exception as e:
            MigrationLog.log_exception(e)
            MigrationLog.log_cruise_processor_unhandled_error(cruise_cargo, str(e))
            return

    def __trim_caches(self):
        soft_cap = MigrationProperties.run_parameters.cache_object_limit
        self.platform_cache.trim_cache(soft_cap)
        self.scientist_cache.trim_cache(soft_cap)
        self.source_cache.trim_cache(soft_cap)
        self.project_cache.trim_cache(soft_cap)
        self.instrument_cache.trim_cache(soft_cap)

    def __process_cargo(self, cargo):
        dataset_crate = cargo.dataset_crate
        survey_crate = cargo.related_survey_crate
        projects_crate = cargo.related_project_crate
        file_crates = cargo.related_file_crates

        MigrationLog.log_dataset_start(cargo)
        self.__add_survey_to_tracking(survey_crate)

        dataset = self.__process_dataset(dataset_crate)

        if dataset is None:
            MigrationLog.log_failed_dataset("dataset insertion failed, skipping migration of related tables and files.")
            return

        with ThreadPoolExecutor(6) as thread_pool:
            future_survey = thread_pool.submit(self.__process_survey, survey_crate, dataset.id)
            future_scientists = thread_pool.submit(self.__process_scientists, dataset_crate.dataset_scientists, dataset.id)
            future_platforms = thread_pool.submit(self.__process_platforms, dataset_crate.dataset_platforms, dataset.id)
            future_sources = thread_pool.submit(self.__process_sources, dataset_crate.dataset_sources, dataset.id)
            future_instruments = thread_pool.submit(self.__process_instruments, dataset_crate.dataset_instruments, dataset.id)
            future_project = thread_pool.submit(self.__process_project, projects_crate, dataset.id)

            thread_pool.submit(self.__update_files, file_crates, dataset.id)

            survey = future_survey.result()
            scientists = future_scientists.result()
            sources = future_sources.result()
            platforms = future_platforms.result()
            instruments = future_instruments.result()
            project = future_project.result()

        self.__validate_dataset_relations(dataset, survey, scientists, sources, platforms, instruments, project)

        unique_access_paths = self.__get_unique_access_paths(file_crates)
        for access_path in unique_access_paths:
            self.__process_access_path(access_path)

        thread_limit = MigrationProperties.run_parameters.file_processing_thread_count
        with ThreadPoolExecutor(min(thread_limit, len(file_crates))) as thread_pool:
            updated_crates_iterator = thread_pool.map(self.__process_file_crate, file_crates)
            thread_pool.shutdown(wait=True)

        updated_file_crates = strip_none(list(updated_crates_iterator))
        self.__process_results(cargo, dataset, updated_file_crates)

    def __process_dataset(self, dataset_crate: CruiseDatasetCrate):
        dataset = self.dataset_service.save_new_dataset(dataset_crate.dataset)
        if dataset:
            if dataset_crate.dataset_shape is not None:
                try:
                    self.shape_service.save_dataset_shape(dataset, dataset_crate.dataset_shape)
                except Exception as e:
                    MigrationLog.log_error("Failed to save dataset shape for dataset: " + dataset.name + " due to " + str(e))
                    MigrationReport.add_failed_dataset_shape_migration(dataset.name)
            for parameter in dataset_crate.dataset_parameters:
                parameter.set_parameter_id(dataset.id)
                self.parameter_service.save_new_dataset_parameter(parameter)
        return dataset

    def __process_survey(self, survey_crate: CruiseSurveyCrate, dataset_id: int) -> Survey:
        survey = self.survey_cache.request(
            Survey(name=survey_crate.cruise_survey.survey_name),
            (lambda survey1, survey2: survey1.name == survey2.name)
        )
        if not survey:
            MigrationLog.log_survey_start(survey_crate)
            survey = self.survey_service.get_new_or_existing_survey(survey_crate.cruise_survey)
            if survey is not None:
                self.survey_cache.update(survey)
                for parameter in survey_crate.survey_parameters:
                    parameter.set_parameter_id(survey.id)
                    self.parameter_service.save_survey_parameter(survey.id, parameter)

        if self.use_batch:
            self.dataset_survey_mappings.add((dataset_id, survey.id))
        else:
            self.survey_service.save_survey_mapping(dataset_id, survey.id)

        return survey

    def __process_platforms(self, dataset_platforms: [CruisePlatform], dataset_id: int):
        platforms = []
        if dataset_platforms:
            for platform in dataset_platforms:
                cached_platform = CruiseProcessor.platform_cache.request(
                    Platform(internal_name=platform.internal_name),
                    (lambda platform1, platform2: platform1.internal_name == platform2.internal_name)
                )
                if not cached_platform:
                    db_platform = self.platform_service.get_new_or_existing_platform(platform)
                    platforms.append(db_platform)
                    if db_platform is not None:
                        CruiseProcessor.platform_cache.update(db_platform)
                else:
                    platforms.append(cached_platform)

        for platform in platforms:
            if self.use_batch:
                self.dataset_platform_mappings.add((dataset_id, platform.id))
            else:
                self.platform_service.save_dataset_platform_mapping(dataset_id, platform.id)

        return platforms

    def __process_scientists(self, dataset_scientists: [CruisePeopleAndSources], dataset_id: int):
        scientists = []
        if dataset_scientists:
            for scientist in dataset_scientists:
                cached_scientist = CruiseProcessor.scientist_cache.request(
                    Contact(name=scientist.name, organization=scientist.organization),
                    (lambda scientist1, scientist2: scientist1.name == scientist2.name and scientist1.organization == scientist2.organization)
                )
                if not cached_scientist:
                    db_scientist = self.contact_service.get_new_or_existing_scientist(scientist)
                    scientists.append(db_scientist)
                    if db_scientist is not None:
                        CruiseProcessor.scientist_cache.update(db_scientist)
                else:
                    scientists.append(cached_scientist)

        for scientist in scientists:
            if self.use_batch:
                self.dataset_scientist_mappings.add((dataset_id, scientist.id))
            else:
                self.contact_service.save_scientist_mapping(dataset_id, scientist.id)

        return scientists

    def __process_sources(self, dataset_sources: [CruisePeopleAndSources], dataset_id: int):
        sources = []
        if dataset_sources:
            for source in dataset_sources:
                cached_source = CruiseProcessor.source_cache.request(
                  Contact(organization=source.organization),
                  (lambda source1, source2: source1.organization == source2.organization)
                )
                if not cached_source:
                    db_source = self.contact_service.get_new_or_existing_source(source)
                    sources.append(db_source)
                    if db_source is not None:
                        CruiseProcessor.source_cache.update(db_source)
                else:
                    sources.append(cached_source)

        for source in sources:
            if self.use_batch:
                self.dataset_source_mappings.add((dataset_id, source.id))
            else:
                self.contact_service.save_source_mapping(dataset_id, source.id)

        return sources

    def __process_instruments(self, dataset_instruments: [CruiseInstrument], dataset_id: int):
        instruments = []
        if dataset_instruments:
            for instrument in dataset_instruments:
                cached_instrument = CruiseProcessor.instrument_cache.request(
                  Instrument(name=instrument.instrument_name),
                  (lambda instrument1, instrument2: instrument1.name == instrument2.name)
                )
                if not cached_instrument:
                    db_instrument = self.instrument_service.get_new_or_existing_instrument(instrument)
                    instruments.append(db_instrument)
                    if db_instrument is not None:
                        CruiseProcessor.instrument_cache.update(db_instrument)
                else:
                    instruments.append(cached_instrument)

        for instrument in instruments:
            if self.use_batch:
                self.dataset_instrument_mappings.add((dataset_id, instrument.id))
            else:
                self.instrument_service.save_dataset_instrument_mapping(dataset_id, instrument.id)

        return instruments

    def __process_project(self, project_crate: CruiseProjectCrate, dataset_id: int):
        dataset_project = project_crate.project
        project = self.project_service.get_new_or_existing_project(dataset_project) if dataset_project else None
        if project:
            if self.use_batch:
                self.dataset_project_mappings.add((dataset_id, project.id))
            else:
                self.project_service.save_dataset_project_mapping(dataset_id, project.id)
        return project

    @staticmethod
    def __update_files(file_crates, dataset_id):
        for crate in file_crates:
            crate.file.dataset_id = dataset_id

    def __process_access_path(self, access_path: CruiseAccessPath):
        cached_access_path = self.__get_cached_access_path(access_path)
        if cached_access_path is None:
            db_access_path = self.access_path_service.get_new_or_existing_access_path(access_path)
            if db_access_path is not None:
                self.access_path_cache.update(db_access_path)
            else:
                raise RuntimeError(f"Failed to save access path {access_path}")

    def __process_file_crate(self, file_crate: CruiseFileCrate) -> Optional[CruiseFileCrate]:
        try:
            file = self.file_service.save_new_file(file_crate.file)
            if file_crate.file_shape is not None:
                try:
                    self.shape_service.save_file_shape(file, file_crate.file_shape)
                except Exception as e:
                    MigrationLog.log_error("Failed to save file shape for file: " + file.name + "due to " + str(e))
                    MigrationReport.add_failed_file_shape_migration_survey(file_crate.survey_name)

            for parameter in file_crate.file_parameters:
                parameter.set_parameter_id(file.id)
                self.parameter_service.save_new_file_parameter(parameter)

            for acc_path in file_crate.file_access_paths:
                access_path = self.__get_cached_access_path(acc_path)
                if access_path is None:
                    raise RuntimeError(f"access path {acc_path} was not properly created and cannot be linked to file {file}.")
                # self.access_path_service.save_file_access_path(file, access_path)
                self.file_access_path_mappings.add((file.id, access_path.id))

        except Exception as e:
            MigrationLog.log_failed_file_migration(file_crate.survey_name, file_crate.file, e)
            MigrationLog.log_exception(e)
            return None

        return file_crate

    def __get_cached_access_path(self, access_path: CruiseAccessPath) -> Optional[AccessPath]:
        return self.access_path_cache.request(
            AccessPath(path=access_path.path, path_type=access_path.path_type),
            (lambda acc_path1, acc_path2: acc_path1.path == acc_path2.path and acc_path1.path_type == acc_path2.path_type)
        )

    @staticmethod
    def __get_unique_access_paths(file_crates) -> [CruiseAccessPath]:
        unique_access_paths = set()
        for crate in file_crates:
            for access_path in crate.file_access_paths:
                unique_access_paths.add(access_path)
        return unique_access_paths

    def __batch_process_join_table_mappings(self):
        with ThreadPoolExecutor(7) as thread_pool:
            thread_pool.submit(self.__batch_insert_mapping, self.dataset_survey_mappings, DatasetsSurveys)
            thread_pool.submit(self.__batch_insert_mapping, self.dataset_scientist_mappings, DatasetScientist)
            thread_pool.submit(self.__batch_insert_mapping, self.dataset_source_mappings, DatasetSource)
            thread_pool.submit(self.__batch_insert_mapping, self.dataset_platform_mappings, DatasetPlatform)
            thread_pool.submit(self.__batch_insert_mapping, self.dataset_project_mappings, DatasetProject)
            thread_pool.submit(self.__batch_insert_mapping, self.dataset_instrument_mappings, DatasetInstrument)
            thread_pool.submit(self.__batch_insert_mapping, self.file_access_path_mappings, FileAccessPath)

    def __batch_insert_mapping(self, mapping_data: ThreadSafeMappings, mapping):
        for chunk in self.__segment(mapping_data.get()):
            self.batch_service.batch_insert_mapping(chunk, mapping)

    @staticmethod
    def __segment(seq):
        max_size = MigrationProperties.run_parameters.batch_insertion_size
        return (seq[pos:pos + max_size] for pos in range(0, len(seq), max_size))

    def __add_survey_to_tracking(self, survey_crate):
        self.migrating_surveys.add(MigratingSurvey(survey_crate))

    def __lazy_log_survey_completion(self):
        tracked_survey_set = self.migrating_surveys
        for survey in tracked_survey_set:
            survey_name = survey.survey_name
            flag = survey.problem_identified
            message = survey.problem_message

            MigrationReport.add_migrated_survey(survey_name, flag, message)
            MigrationLog.log_migrated_survey(survey, flag, message)

    @staticmethod
    def __validate_dataset_file_entry(actual: int, expected_files_length: int, dataset_name: str, flag: bool, message: str) -> Tuple[bool, str]:
        if actual < expected_files_length:
            flag = True
            message = f"Some or all files failed insertion for dataset {dataset_name}; " + message
        return flag, message

    def __validate_dataset_relations(self, dataset: Dataset, survey: Survey, scientists, sources, platforms, instruments, project):
        valid = True
        failure_messages = []
        dataset_name = dataset.name
        if survey is None:
            valid = False
            failure_messages.append(f"Related survey found missing for {dataset_name} during validation: {survey}")
        for scientist in scientists:
            if scientist is None:
                valid = False
                failure_messages.append(f"Related scientist found missing for {dataset_name} during validation: {scientist}")
        for source in sources:
            if source is None:
                valid = False
                failure_messages.append(f"Related source found missing for {dataset_name} during validation: {source}")
        for platform in platforms:
            if platform is None:
                valid = False
                failure_messages.append(f"Related platform found missing for {dataset_name} during validation: {platform}")
        for instrument in instruments:
            if instrument is None:
                valid = False
                failure_messages.append(f"Related instrument found missing for {dataset_name} during validation: {instrument}")
        if not valid:
            self. __fail_dataset(dataset, failure_messages)
            raise RuntimeWarning(f"Issue found with dataset or dataset related tables. Cancelling dataset migration for dataset {dataset_name}")

    def __fail_dataset(self, dataset, issues):
        message = f"Issue identified with dataset during validation:"
        for issue in issues:
            message += "\n\t" + issue
        message += "\nAttempting to rollback dataset."
        MigrationLog.log_failed_dataset(message)
        try:
            self.dataset_service.delete_dataset(dataset)
            return None
        except:
            MigrationLog.log.error(f"ERROR while attempting to cleanup dataset {dataset.name} after dataset failed validation.")

    def __process_results(self, cargo, dataset, inserted_file_crates):
        file_crates = cargo.related_file_crates
        survey_crate = cargo.related_survey_crate

        problem_flag = False
        problem_message = ""

        inserted_datasets = 1
        inserted_files = len(inserted_file_crates)
        expected_file_insertions = len(file_crates)

        problem_flag, problem_message = self.__validate_dataset_file_entry(inserted_files, expected_file_insertions, dataset.name, problem_flag, problem_message)

        MigrationReport.add_migrated_dataset(cargo)
        MigrationLog.log_migrated_dataset(cargo, inserted_files, expected_file_insertions)

        self.__update_survey_tracking(problem_flag, problem_message, survey_crate, inserted_datasets, inserted_files, expected_file_insertions)

    def __update_survey_tracking(self, problem_flag: bool, problem_message: str, survey_crate: CruiseSurveyCrate, num_datasets: int, num_actual_files: int, num_expected_files: int):
        survey_name = survey_crate.cruise_survey.survey_name
        tracked_survey_set = self.migrating_surveys
        for survey in tracked_survey_set:
            if survey.survey_name == survey_name:
                survey.update(problem_flag, problem_message, num_datasets, num_actual_files, num_expected_files)
