import sys
from pathlib import Path
from typing import Callable

from pmsintegration.core.app import AppContext
from pmsintegration.core.core_models import LenientEntity
from pmsintegration.core.pmsdb.config import use_conn
from pmsintegration.platform.utils import ContextualDict


class DBMigrationConfig(LenientEntity):

    @staticmethod
    def _infer_database_migration_dir() -> str | None:
        candidate = "database/migrations"
        fs_root = Path(f"/{candidate}").resolve()
        while True:
            p = Path(candidate).resolve()
            if p.exists() and p.is_dir():
                return candidate
            if p == fs_root:
                break
            candidate = f"../{candidate}"

    @classmethod
    def create(cls):
        app_ctx = AppContext.global_context()
        kwargs = app_ctx.env.find_matched("flyway.settings", flatten=False)

        return ContextualDict.adopt(kwargs)


def run_check(write_log: Callable[..., None]):
    pool = AppContext.global_context().pmsdb

    try:
        with use_conn(pool) as conn:
            cursor = conn.cursor()
            write_log("Executing Test Query")
            cursor.execute(
                "SELECT cast(CURRENT_TIMESTAMP as text) as now, "
                "CURRENT_ROLE, current_catalog , current_schema"
            )
            info = cursor.fetchall()[0]
            write_log(f"Info returned by server is: {info}")
        write_log("Connection successful - OK")
    except Exception as e:
        write_log(f"Exception occurred while connecting: {e}")
        sys.exit(1)


def run_migrate(write_log: Callable[..., None]):
    write_log("NOTICE: Run database migration via flyway. It is not supported")
