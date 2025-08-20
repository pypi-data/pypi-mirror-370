from fairdomseek.cache.cash_assay import AssaysCache
from fairdomseek.cache.cash_datafile import DataFileCache
from fairdomseek.cache.cash_investigation import CashInvestigation
from fairdomseek.cache.cash_model import ModelCache
from fairdomseek.cache.cash_sample import SampleCache
from fairdomseek.cache.cash_sample_type import SampleTypeCache
from fairdomseek.cache.cash_studies import StudiesCache
from fairdomseek.mapper.attribute_mapper import AttributeMapper
from fairdomseek.mapper.policy_mapper import PolicyMapper
from fairdomseek.service.actor_service import ActorsService
from fairdomseek.service.assay_service import AssayService
from fairdomseek.service.data_file_service import DataFileService
from fairdomseek.service.investigations_service import InvestigationService
from fairdomseek.service.models_service import ModelsService
from fairdomseek.service.sample_service import SamplesService
from fairdomseek.service.sample_types_service import SampleTypeService
from fairdomseek.service.studies_service import StudiesService
from fairdomseek.translator.assay_translator import AssayTranslator
from fairdomseek.translator.datafile_translator import DataFileTranslator
from fairdomseek.translator.investigation_translator import InvestigationTranslator
from fairdomseek.translator.model_translator import ModelTranslater
from fairdomseek.translator.sample_translator import SampleTranslator
from fairdomseek.translator.sample_type_translator import SampleTypeTranslator
from fairdomseek.translator.study_translator import StudyTranslator


class FairdomSeekContext:

    def __init__(self, client=None, project_name=None):

        # Service
        self._actors_service = ActorsService()

        # Caches
        self._cash_investigation = CashInvestigation(actor_service=self._actors_service,
                                                    translator=InvestigationTranslator(PolicyMapper()),
                                                    client=client)
        self._studies_cache = StudiesCache(actor_service=self._actors_service,
                                           translator=StudyTranslator(PolicyMapper()),
                                           client=client)
        self._sample_type_cache = SampleTypeCache(actor_service=self._actors_service,
                                                  translator=SampleTypeTranslator(PolicyMapper(),
                                                                                  AttributeMapper()),
                                                  client=client)
        self._assay_cache = AssaysCache(actor_service=self._actors_service,
                                        translator=AssayTranslator(PolicyMapper()),
                                        client=client)
        self._data_file_cache = DataFileCache(actor_service=self._actors_service,
                                        translator=DataFileTranslator(PolicyMapper()),
                                        client=client)
        self._model_cache = ModelCache(actor_service=self._actors_service,
                                        translator=ModelTranslater(PolicyMapper()),
                                        client=client)
        self._sample_cache = SampleCache(
            actor_service=self._actors_service,
            translator=SampleTranslator(PolicyMapper()),
            client=client)

        # Services used for syncing
        self._sample_types_service = SampleTypeService(actors_service=self._actors_service,
                                                     cache=self._sample_type_cache,
                                                     translator=SampleTypeTranslator(PolicyMapper(),
                                                                                     AttributeMapper()))
        self._investigations_service = InvestigationService(actors_service=self._actors_service,
                                                           cache=self._cash_investigation,
                                                           translator=InvestigationTranslator(PolicyMapper())
                                                           )
        self._studies_service = StudiesService(actors_service=self._actors_service,
                                              investigation_service=self._investigations_service,
                                              cache=self._studies_cache,
                                              translator=StudyTranslator(PolicyMapper()))
        self._data_file_service = DataFileService(
            actors_service=self._actors_service,
            cache=self._data_file_cache,
            translator=DataFileTranslator(PolicyMapper())
        )
        self._model_service = ModelsService(
            actors_service=self._actors_service,
            cache=self._model_cache,
            translator=ModelTranslater(PolicyMapper())
        )
        self._samples_service = SamplesService(
            actors_service=self._actors_service,
            sample_type_service=self._sample_types_service,
            data_file_service=self._data_file_service,
            cache=self._sample_cache,
            translator=SampleTranslator(PolicyMapper())
        )
        self._assays_service = AssayService(actors_service=self._actors_service,
                                           studies_service=self._studies_service,
                                           samples_service = self._samples_service,
                                           model_service = self._model_service,
                                           datafile_service= self._data_file_service,
                                           sop_service = None,
                                           cache=self._assay_cache,
                                            translator=AssayTranslator(PolicyMapper))

        self.project_name = project_name
        self.client = client

        self.__services = [self._actors_service, self._sample_types_service, self._investigations_service,
                           self._studies_service, self._data_file_service, self._model_service,
                           self._assays_service, self._samples_service]

        self.__caches = [self._cash_investigation, self._studies_cache, self._sample_type_cache, self._assay_cache,
                        self._data_file_cache, self._model_cache, self._sample_cache]

        if self.client is not None:
            self.set_client(client)
        if self.project_name is not None:
            self.set_project_name(project_name)

    def set_client(self, client):
        # Services
        for s in self.__services:
            s.set_client(client)

        # Cache
        for c in self.__caches:
            c.set_client(client)

        self.client = client

    def set_project_name(self, project_name):
        # Services
        for s in self.__services:
            s.set_project_name(project_name)

        # Cache
        for c in self.__caches:
            c.set_project_name(project_name)

        self.project_name = project_name

    def investigations_service(self):
        return self._investigations_service

    def studies_service(self):
        return self._studies_service

    def assays_service(self):
        return self._assays_service

    def sample_types_service(self):
        return self._sample_types_service

    def models_service(self):
        return self._model_service

    def samples_service(self):
        return self._samples_service

    def data_file_service(self):
        return self._data_file_service