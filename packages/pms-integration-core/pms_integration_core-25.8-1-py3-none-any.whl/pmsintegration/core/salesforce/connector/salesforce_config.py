from typing import Any

from pydantic import BaseModel, Field, AliasChoices

from pmsintegration.platform import utils
from pmsintegration.platform.config import ConfigEnvironment
from pmsintegration.platform.credentials import CredentialProvider


class SalesforceSimpleConnectorConfig(BaseModel):
    domain: str
    auth_mechanism: str = "oauth2"

    api_key: str = Field(
        validation_alias=AliasChoices('api_key', "consumer_key", "username")
    )
    api_token: str | None = Field(
        validation_alias=AliasChoices('api_token', "consumer_secret", "password"),
        default=None
    )
    security_token: str | None = None  # Applicable if auth_mechanism is basic
    private_key: str | None = None  # Applicable if auth_mechanism is oauth2_jwt_bearer

    read_timeout_in_seconds: int = 0
    connect_timeout_in_seconds: int = 0
    transport: dict[str, Any] = {}
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    version: str = "61.0"

    def create_auth_dict(self) -> dict[str, str]:
        auth_dict = {}
        if self.auth_mechanism == "oauth2":
            auth_dict["domain"] = self.domain
            auth_dict["consumer_key"] = self.api_key
            auth_dict["consumer_secret"] = self.api_token
        elif self.auth_mechanism == "basic":
            auth_dict["domain"] = self.domain
            auth_dict["username"] = self.api_key
            auth_dict["password"] = self.api_token
        return auth_dict

    def as_dict(self) -> dict[str, Any]:
        return {"version": self.version}

    @classmethod
    def create(cls, env: ConfigEnvironment, name: str) -> 'SalesforceSimpleConnectorConfig':
        config = env.find_matched(f"connectors.{name}")
        utils.check(len(config) != 0, "Missing Salesforce Connection Configuration")
        cred_name = config.pop("credential_name", "")
        if cred_name:
            cred = CredentialProvider.read_credentials(cred_name)
            config.update(cred)
        return cls(**config)


class SalesforcePubSubConnectorConfig(SalesforceSimpleConnectorConfig):
    grpc_host: str
    grpc_port: int

    def grpc_target(self):
        return f"{self.grpc_host}:{self.grpc_port}"
