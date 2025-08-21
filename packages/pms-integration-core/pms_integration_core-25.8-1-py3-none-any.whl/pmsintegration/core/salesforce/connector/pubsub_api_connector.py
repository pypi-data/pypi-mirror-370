import logging
from collections.abc import Callable
from functools import lru_cache
from typing import Any

import certifi
import grpc

import pmsintegration.core.salesforce.pubsub.gen.pubsub_api_pb2_grpc as pb2_grpc
from pmsintegration.core.salesforce.connector.rest_api_connector import SalesforceSimpleConnector
from pmsintegration.core.salesforce.connector.salesforce_config import SalesforcePubSubConnectorConfig
from pmsintegration.core.salesforce.pubsub import types
from pmsintegration.core.salesforce.pubsub.pubsub_utils import (
    LockMechanism,
    Subscription,
    fetch_req_stream,
    decode_avro_payload,
)
from pmsintegration.core.salesforce.pubsub.types import SfEvent
from pmsintegration.core.salesforce.store import SubscribeParams
from pmsintegration.platform.config import ConfigEnvironment

_log = logging.getLogger(__name__)


class SalesforcePubSubConnector:
    def __init__(self, config: SalesforcePubSubConnectorConfig):
        self._auth_client = SalesforceSimpleConnector(config)
        self._config = config
        self._client: pb2_grpc.PubSubStub
        self._channel = None

    def __enter__(self):
        channel = self._create_secure_channel()
        self._client = pb2_grpc.PubSubStub(channel)
        self._channel = channel
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.__exit__(exc_type, exc_val, exc_tb)

    def refresh_auth_metadata(self):
        # TODO: Should have TTL here
        auth = self._auth_client
        # Below call may re-trigger the auth flow internally
        tenant_id = auth.get_tenant_id()

        return [
            ("accesstoken", auth.client.session_id),
            ("instanceurl", f"https://{auth.client.sf_instance}"),
            ("tenantid", tenant_id),
        ]

    def _create_secure_channel(self):
        with open(certifi.where(), 'rb') as f:
            creds = grpc.ssl_channel_credentials(f.read())
        return grpc.secure_channel(self._config.grpc_target(), creds)

    @property
    def client(self):
        return self._client

    @lru_cache()
    def get_schema_json(self, schema_id: Any):
        return self._client.GetSchema(
            types.SchemaRequest(schema_id=schema_id),
            metadata=self.refresh_auth_metadata()
        ).schema_json

    def decode_event(self, event: types.ProducerEvent) -> dict[str, Any]:
        payload = event.payload
        schema = self.get_schema_json(event.schema_id)
        return decode_avro_payload(schema, payload)

    def subscribe(
            self,
            topic: str,
            callback: Callable[[Any], bool],
            subscription_params_provider: Callable[[], SubscribeParams],
            num_requested: int = 10,
    ):
        """Subscribe topic for receiving the events.
        """
        lock_mechanism = LockMechanism()
        pubsub = self

        def callback_with_semaphore(fetch_response: types.FetchResponse):
            consumer_events = fetch_response.events
            pending_num_requested = fetch_response.pending_num_requested
            # rpc_id = fetch_response.rpc_id
            # latest_replay_id = fetch_response.latest_replay_id
            if consumer_events:
                if pending_num_requested == 0 or lock_mechanism.is_done:
                    lock_mechanism.semaphore.release()
                decoded_events = [SfEvent.create(e, pubsub.decode_event(e.event)) for e in consumer_events]
                lock_mechanism.is_done = callback(decoded_events)
            return lock_mechanism.is_done

        event_stream = self._client.Subscribe(
            request_iterator=fetch_req_stream(lock_mechanism, topic, subscription_params_provider, num_requested),
            metadata=self.refresh_auth_metadata(),
        )
        _log.info(f"A new subscription is created for topic: {topic} [{subscription_params_provider()}]")
        return Subscription(event_stream, callback_with_semaphore)

    @classmethod
    def create(cls, env: ConfigEnvironment, connector_name: str) -> 'SalesforcePubSubConnector':
        config = SalesforcePubSubConnectorConfig.create(env, connector_name)
        return SalesforcePubSubConnector(config)
