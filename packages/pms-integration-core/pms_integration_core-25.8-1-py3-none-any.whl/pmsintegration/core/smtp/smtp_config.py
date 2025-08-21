from typing import Any

from pmsintegration.platform import utils
from pmsintegration.platform.config import ConfigEnvironment
from pmsintegration.platform.credentials import CredentialProvider
from pydantic import BaseModel, Field, AliasChoices


class SmtpRestConnectorConfig(BaseModel):
    smtp_port: str = Field(validation_alias=AliasChoices('smtp_port', 'smtp_port'))
    smtp_server: str = Field(validation_alias=AliasChoices('smtp_server', 'smtp_server'))
    smtp_user: str = Field(validation_alias=AliasChoices('smtp_user', 'smtp_user'))
    smtp_password: str = Field(validation_alias=AliasChoices('smtp_password', 'smtp_password'))
    auth_mechanism: str = "basic"
    read_timeout_in_seconds: int = 0
    connect_timeout_in_seconds: int = 0
    transport: dict[str, Any] = {}

    @classmethod
    def create(cls, env: ConfigEnvironment) -> 'SmtpRestConnectorConfig':
        config = env.find_matched("connectors.smtp_credentials")
        utils.check(len(config) != 0, "Missing Smtp Connection Configuration")
        cred_name = config.pop("credential_name", "")
        if cred_name:
            cred = CredentialProvider.read_credentials(cred_name)
            config.update(cred)
        return SmtpRestConnectorConfig(**config)
