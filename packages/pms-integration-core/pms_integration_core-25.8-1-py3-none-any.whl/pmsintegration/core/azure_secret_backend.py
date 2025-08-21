from typing import Any

from pmsintegration.core import azure_utils
from pmsintegration.platform.credentials import CredentialProvider


class AzureKeyVaultSecretsBackend(CredentialProvider):
    PREFIX = "azkvs"

    def __init__(self):
        super().__init__()

    def get_credential(self, name: str, **kwargs) -> dict[str, Any]:
        return azure_utils.get_secret_from_key_vault(name)
