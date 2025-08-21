import atexit
from contextlib import contextmanager
from typing import Any

from pydantic import BaseModel

from pmsintegration.platform import utils, sshutils
from pmsintegration.platform.config import ConfigEnvironment
from pmsintegration.platform.credentials import CredentialProvider
from pmsintegration.platform.sshutils import SSHTunnelConfig


@contextmanager
def use_conn(pool, *args, **kwargs):
    old_autocommit = None
    conn = pool.getconn(*args, **kwargs)
    try:
        old_autocommit = conn.autocommit
        conn.autocommit = True
        yield conn
    finally:
        if not conn.closed:
            conn.autocommit = old_autocommit
        if not pool.closed:
            pool.putconn(conn)


class PostgresConnectorConfig(BaseModel):
    db_host: str
    db_port: int = 5432
    db_user: str
    db_password: str
    db_name: str
    db_schema: str | None = "pms_data"
    sshtunnel: SSHTunnelConfig | None = None
    pool_impl: str = "psycopg_pool.pool.ConnectionPool"
    pool_kwargs: dict[str, Any] = {}
    db_kwargs: dict[str, Any] = {}

    def new_pool(self, **kwargs):
        pool_kwargs: dict[str, Any] = {
            "min_size": 1,
            "max_size": 40,
        }
        pool_kwargs.update(self.pool_kwargs.copy())

        db_kwargs: dict[str, Any] = {
            "application_name": "pms-integration-apps",
            "user": self.db_user,
            "host": self.db_host,
            "port": self.db_port,
            "password": self.db_password,
            "dbname": self.db_name,
            "options": "",
        }
        db_kwargs.update(self.db_kwargs)

        if self.db_schema:
            db_kwargs["options"] = f"{db_kwargs['options']} -c search_path={self.db_schema}"
        if kwargs:
            # Overwrite with the custom params
            db_kwargs.update(**kwargs)

        pool_kwargs["kwargs"] = db_kwargs

        tunnel_server = None
        if self.sshtunnel:
            tunnel_server = self.sshtunnel.new_tunnel_server(db_kwargs["host"], db_kwargs["port"])
            tunnel_server.start()
            db_kwargs["host"] = sshutils.resolve_localhost(tunnel_server.local_bind_host)
            db_kwargs["port"] = tunnel_server.local_bind_port

        pool = utils.instantiate(self.pool_impl, **pool_kwargs)

        def stop_all():
            print("*** Stopping database connection pool")
            # Let's close the connection pool before stopping the tunnel server
            pool.close()
            try:
                if tunnel_server is not None:
                    tunnel_server.stop(True)
            except Exception as e:  # noqa
                ...

        # let's close the pool during shutdown
        atexit.register(stop_all)

        return pool

    @classmethod
    def create(cls, env: ConfigEnvironment, name: str = "default") -> 'PostgresConnectorConfig':
        config = env.find_matched(f"connectors.postgres_{name}")
        cred_name = config.pop("credential_name", "")
        if cred_name:
            cred = CredentialProvider.read_credentials(cred_name)
            config.update(cred)
        return cls(**config)
