import functools
import json
import platform
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import (
    SecretClient
)

from pmsintegration.platform.disk_store import disk_memoize


@functools.lru_cache(1)
def _az_sdk_credentials_provider(**kwargs):
    import platform
    kwargs.update({
        "exclude_powershell_credential": True,
        "exclude_interactive_browser_credential": True,
        "exclude_visual_studio_code_credential": True,
        "exclude_cli_credential": True,
        "exclude_shared_token_cache_credential": True,
        "exclude_developer_cli_credential": True,
    })

    if platform.system() == "Windows":
        # Exclude Managed identity credential in
        # local environment;
        # Here Aim is to use the AzureCli Credential
        kwargs["exclude_managed_identity_credential"] = True
        kwargs["exclude_workload_identity_credential"] = True
        kwargs["exclude_environment_credential"] = True
        kwargs["exclude_cli_credential"] = False

    return DefaultAzureCredential(**kwargs)


@functools.lru_cache(1)
def az_secret_client():
    from pmsintegration.platform.globals import env
    _url = env.get_required("platform.azure.secret_vault_url")
    kwargs = env.get("platform.azure.credential_kwargs", {})
    cred = _az_sdk_credentials_provider(**kwargs)

    return SecretClient(vault_url=_url, credential=cred)  # noqa


def get_secret_from_key_vault(secret_name: str, _json: bool = True) -> str | dict[str, Any]:
    if platform.system() == "Windows":
        @disk_memoize
        def cache_pull_through(_1):
            return az_secret_client().get_secret(_1).value
    else:
        def cache_pull_through(_1):
            return az_secret_client().get_secret(_1).value

    _value = cache_pull_through(secret_name)
    return json.loads(_value) if _json else _value


def get_current_user_info():
    ...
