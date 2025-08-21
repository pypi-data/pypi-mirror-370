import abc
import logging
from abc import abstractmethod

from pydantic import BaseModel

from pmsintegration.core.addepar.connector.api_models import DataWrapper, APIData
from pmsintegration.core.app import AppContext
from pmsintegration.core.core_models import LET
from pmsintegration.core.salesforce.pubsub.types import SfEvent
from pmsintegration.core.salesforce.store import SubscribeParams, EventBatchProcessingError
from pmsintegration.platform import utils

_log = logging.getLogger(__name__)


class ProcessorConfig(BaseModel):
    name: str
    impl: str


class SalesforceEventProcessor(abc.ABC):

    def __init__(self, config: ProcessorConfig, app_context: AppContext):
        self.config = config
        self.app_context = app_context
        self.replay_store = app_context.topic_subscription_store
        self.addepar = app_context.addepar
        self.salesforce = app_context.salesforce

    @abc.abstractmethod
    def process(self, events: list[SfEvent]) -> bool:
        """Process the given set of salesforce events received from the topic

        :param: events list of events
        :return: true if no more events should be processed, otherwise continue processing
        """

    def subscribe_parameters(self) -> SubscribeParams:
        return self.replay_store.get_subscription_param(self.config.name)

    @classmethod
    def create(cls, name: str, **kwargs) -> 'SalesforceEventProcessor':
        from pmsintegration.platform.globals import env
        raw_config = env.find_matched(f"event_processors.salesforce.{name}")
        raw_config.update(kwargs)
        config = ProcessorConfig(name=name, **raw_config)
        impl = config.impl
        processor = utils.instantiate(impl, config=config, app_context=AppContext.global_context())
        utils.check(
            isinstance(processor, SalesforceEventProcessor),
            message=f"'{impl}' must be a subclass of '{SalesforceEventProcessor.__name__}'"
        )
        _log.info(f"Process instantiate: {name} using impl: {impl}")
        return processor


class NoopSalesforceEventProcessor(SalesforceEventProcessor):
    def process(self, events: list[SfEvent]) -> bool:
        ...


class GenericUpdateEventProcessor(SalesforceEventProcessor):

    def process(self, events: list[SfEvent]) -> bool:
        entities = [self.create_entity(e) for e in events]

        # to_be_deleted = [e for e in entities if e.is_deleted()]
        # to_be_updated = [e for e in entities if not e.is_deleted()]
        should_stop = None
        try:
            # if to_be_updated:
            should_stop = self.process_updates(entities)
            # if to_be_deleted:
            #     should_stop = self.process_deletes(to_be_deleted)
            return should_stop
        except EventBatchProcessingError:
            raise
        except Exception as e:
            raise EventBatchProcessingError({}) from e

    @classmethod
    def make_request_payload(
            cls,
            entities: list[LET],
            entity_type: str = "entities",
            fill_attributes: bool = True
    ) -> DataWrapper:
        api_data_list = []
        for entity in entities:
            addepar_id = entity.id if entity.id else None
            api_data_list.append(APIData(
                id=addepar_id,
                type=entity_type,
                attributes=entity if fill_attributes else None
            ))

        return DataWrapper.create(api_data_list)

    @classmethod
    def update_request_payload(cls, entities: list[LET], entity_type: str = "positions") -> DataWrapper:
        api_data_list = []
        for entity in entities:
            addepar_id = entity.id if entity.id else None
            api_data_list.append(
                APIData(
                    id=addepar_id,
                    type=entity_type,
                    attributes=entity,
                    relationships={
                        "owner": DataWrapper.create(APIData(type="entities", id=entity.owner)),
                        "owned": DataWrapper.create(APIData(type="entities", id=entity.owned))
                    },
                )

            )

        return DataWrapper.create(api_data_list)

    @abstractmethod
    def process_updates(self, events: list[LET]) -> bool:
        ...

    @abstractmethod
    def process_deletes(self, events: list[LET]) -> bool:
        ...

    @abstractmethod
    def create_entity(self, e: SfEvent) -> LET:
        ...


class GenericContactUpdateEventProcessor(SalesforceEventProcessor):

    def process(self, events: list[SfEvent]) -> bool:
        entities = [self.create_contact(c) for c in events]

        should_stop = None
        try:
            # if to_be_updated:
            should_stop = self.process_updates(entities)
            return should_stop
        except EventBatchProcessingError:
            raise
        except Exception as e:
            raise EventBatchProcessingError({}) from e

    @classmethod
    def make_request_payload(
            cls,
            contacts: list[LET],
            model_type: str = "contacts",
            fill_attributes: bool = True
    ) -> DataWrapper:
        api_data_list = []
        for contact in contacts:
            addepar_id = contact.id if contact.id else None
            api_data_list.append(APIData(
                id=addepar_id,
                type=model_type,
                attributes=contact if fill_attributes else None
            ))

        return DataWrapper.create(api_data_list)

    @classmethod
    def update_request_payload(cls, contacts: list[LET], contact_type: str = "contacts") -> DataWrapper:
        api_data_list = []
        for contact in contacts:
            addepar_id = contact.id if contact.id else None
            api_data_list.append(
                APIData(
                    id=addepar_id,
                    type=contact_type,
                    attributes=contact,
                )
            )

        return DataWrapper.create(api_data_list)

    @abstractmethod
    def create_contact(self, e: SfEvent) -> LET:
        ...

    @abstractmethod
    def process_updates(self, events: list[LET]) -> bool:
        ...

    @abstractmethod
    def process_deletes(self, events: list[LET]) -> bool:
        ...
