import logging
import os
import uuid
from functools import lru_cache, cached_property

from pmsintegration.core.addepar.connector.addepar_config import AddeparRestConnectorConfig
from pmsintegration.core.addepar.connector.client import AddeparRestAPIClient
from pmsintegration.core.azdb.connector.databricks_sql_connector import DatabricksSQLConnector, \
    DatabricksSQLConnectorConfig
from pmsintegration.core.pmsdb.config import PostgresConnectorConfig
from pmsintegration.core.salesforce.connector.rest_api_connector import SalesforceSimpleConnector
from pmsintegration.core.salesforce.connector.salesforce_config import SalesforceSimpleConnectorConfig
from pmsintegration.core.salesforce.store import SubscriptionStore, EventStore
from pmsintegration.core.smtp.smtp_client import SmtpRestAPIClient
from pmsintegration.core.smtp.smtp_config import SmtpRestConnectorConfig
from pmsintegration.platform.config import ConfigEnvironment, YamlPropertySource


class AppContext:
    def __init__(self, env: ConfigEnvironment):
        self.env = env

    @classmethod
    @lru_cache()
    def global_context(cls) -> 'AppContext':
        from pmsintegration.platform.globals import env
        return AppContext(env)

    @staticmethod
    def uuid():
        return uuid.uuid4().hex

    @cached_property
    def addepar(self):
        return AddeparRestAPIClient(
            AddeparRestConnectorConfig.create(self.env)
        )

    @cached_property
    def smtp(self):
        return SmtpRestAPIClient(
            SmtpRestConnectorConfig.create(self.env)
        )

    @cached_property
    def salesforce(self):
        return SalesforceSimpleConnector(
            SalesforceSimpleConnectorConfig.create(self.env, "salesforce_rest_api")
        )

    @cached_property
    def pmsdb(self):
        _log = logging.getLogger(__name__)
        _log.info("Creating new connection pool")
        return PostgresConnectorConfig.create(self.env).new_pool()

    @cached_property
    def databricks(self) -> DatabricksSQLConnector:
        return DatabricksSQLConnector(
            DatabricksSQLConnectorConfig.create(self.env)
        )

    @cached_property
    def topic_subscription_store(self) -> SubscriptionStore:
        return SubscriptionStore(self.pmsdb)

    @cached_property
    def event_store(self) -> EventStore:
        return EventStore(self.pmsdb)

    def env_name(self):
        return self.env.env_name

    def update(self, conf_resource: str):
        env = self.env
        env.add_source(YamlPropertySource(os.path.join(env.conf_root, conf_resource)))
