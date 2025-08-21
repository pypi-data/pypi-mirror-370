from typing import Any

from pydantic import BaseModel, Field, AliasChoices

from pmsintegration.platform import utils
from pmsintegration.platform.config import ConfigEnvironment
from pmsintegration.platform.credentials import CredentialProvider


class AddeparRestConnectorConfig(BaseModel):
    endpoint: str = Field(validation_alias=AliasChoices('endpoint', 'api_endpoint'))
    addepar_firm: int = Field(validation_alias=AliasChoices('addepar_firm', 'firm_id'))
    addepar_api_key: str = Field(validation_alias=AliasChoices('addepar_api_key', 'username'))
    addepar_api_token: str = Field(validation_alias=AliasChoices('addepar_api_token', 'password'))
    auth_mechanism: str = "basic"
    read_timeout_in_seconds: int = 0
    connect_timeout_in_seconds: int = 0
    transport: dict[str, Any] = {}

    @classmethod
    def create(cls, env: ConfigEnvironment) -> 'AddeparRestConnectorConfig':
        config = env.find_matched("connectors.addepar")
        utils.check(len(config) != 0, "Missing Addepar Connection Configuration")
        cred_name = config.pop("credential_name", "")
        if cred_name:
            cred = CredentialProvider.read_credentials(cred_name)
            config.update(cred)
        return AddeparRestConnectorConfig(**config)
