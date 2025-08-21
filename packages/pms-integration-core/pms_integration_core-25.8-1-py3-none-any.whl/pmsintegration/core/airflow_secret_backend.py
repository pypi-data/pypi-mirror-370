from typing import Any

from pmsintegration.platform import utils
from pmsintegration.platform.credentials import CredentialProvider

_IS_AIRFLOW_MODULE_AVAILABLE = utils.module_exists("models", "airflow")


class AirflowVariableBackend(CredentialProvider):
    PREFIX = "var"

    def get_credential(self, name: str, **kwargs) -> dict[str, Any]:
        if _IS_AIRFLOW_MODULE_AVAILABLE:
            from airflow.models import Variable  # noqa

            return Variable.get(name, deserialize_json=True)
        else:
            raise ValueError(f"airflow module is not available. Can't find: {name}")
