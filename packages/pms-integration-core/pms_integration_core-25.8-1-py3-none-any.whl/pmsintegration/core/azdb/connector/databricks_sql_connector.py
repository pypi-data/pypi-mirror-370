import logging
from pathlib import Path
from typing import Any, Optional, List, Dict

from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sql.client import Connection
from pydantic import BaseModel

from pmsintegration.platform import utils
from pmsintegration.platform.config import ConfigEnvironment
from pmsintegration.platform.credentials import CredentialProvider
from pmsintegration.platform.utils import dict_ignoring_nulls

logging.getLogger("databricks.sql").setLevel("WARNING")

_log = logging.getLogger(__name__)


class DatabricksSQLConnectorConfig(BaseModel):
    server_hostname: str
    http_path: str
    access_token: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    catalog: str | None = None
    schema: str | None = None

    @classmethod
    def create(cls, env: ConfigEnvironment, name: str = None) -> 'DatabricksSQLConnectorConfig':
        config = env.find_matched(f"connectors.{name or 'databricks_sql'}")
        utils.check(len(config) != 0, "Missing Databricks Connection Configuration")
        cred_name = config.pop("credential_name", "")
        if cred_name:
            cred = CredentialProvider.read_credentials(cred_name)
            config.update(cred)
        return DatabricksSQLConnectorConfig(**config)

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True, exclude_unset=True)

    def as_dbt_profile(self, project: str, target: str, schema: str = None, threads: int = 4) -> dict[str, Any]:
        """
        Convert Databricks credentials to a DBT profile dictionary.

        Example output:
        {
            "pms_integration_data": {
                "target": "prod",
                "outputs": {
                    "prod": {
                        "type": "databricks",
                        "catalog": "prod_addepar_recon",
                        "host": "adb-xyz.4.azuredatabricks.net",
                        "http_path": "/sql/1.0/warehouses/xyz",
                        "schema": "recon",
                        "threads": 4,
                        "token": "xyz"
                    }
                }
            }
        }
        """
        output = dict_ignoring_nulls(
            type="databricks",
            catalog=self.catalog,
            host=self.server_hostname,
            http_path=self.http_path,
            schema=schema or self.schema,
            threads=threads,
            token=self.access_token,
        )

        return {
            project: {
                "target": target,
                "outputs": {
                    target: output
                }
            }
        }


class DatabricksSQLConnector:
    def __init__(self, config: DatabricksSQLConnectorConfig):
        self._config = config
        self._ws = WorkspaceClient(
            host=config.server_hostname,
            token=config.access_token,
        )

    def config(self):
        return self._config

    def connect(self, **kwargs) -> Connection:
        config = self._config.as_dict()
        if kwargs:
            config.update(kwargs)

        return sql.connect(
            config.pop("server_hostname"),
            config.pop("http_path"),
            **config
        )

    def upload_file(self, local_file: str | Path, target_path: str):
        w = self._ws
        with open(local_file, "rb") as f:
            w.files.upload(target_path, contents=f, overwrite=True)

    def execute_update_query(self, query: str, catalog: Optional[str] = None) -> List[Dict]:
        """Execute SQL query. For SELECT, return rows. For UPDATE/INSERT/DELETE, return affected row count."""
        _log.info(f"Executing query:\n{query}")
        with self.connect(catalog=catalog) as conn:
            cursor = conn.cursor()
            total_rows_affected = 0

            for stmt in query.strip().split(";"):
                if stmt.strip():
                    cursor.execute(stmt)
                    if cursor.rowcount != -1:
                        total_rows_affected += cursor.rowcount
                    else:
                        _log.warning("Row count not reported for statement")

            conn.commit()
            return [{"rows_affected": total_rows_affected}]
