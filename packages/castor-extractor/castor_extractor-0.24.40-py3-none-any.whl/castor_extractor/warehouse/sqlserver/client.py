import logging
from collections.abc import Iterator

from sqlalchemy import text

from ...utils import ExtractionQuery, SqlalchemyClient, uri_encode

logger = logging.getLogger(__name__)

SERVER_URI = "{user}:{password}@{host}:{port}/{database}"
MSSQL_URI = f"mssql+pymssql://{SERVER_URI}"
DEFAULT_PORT = 1433

_KEYS = ("user", "password", "host", "port", "database")

_SYSTEM_DATABASES = ("master", "model", "msdb", "tempdb", "DBAdmin")


def _check_key(credentials: dict) -> None:
    for key in _KEYS:
        if key not in credentials:
            raise KeyError(f"Missing {key} in credentials")


class MSSQLClient(SqlalchemyClient):
    """Microsoft Server SQL client"""

    @staticmethod
    def name() -> str:
        return "MSSQL"

    def _engine_options(self, credentials: dict) -> dict:
        return {}

    def _build_uri(self, credentials: dict) -> str:
        _check_key(credentials)
        uri = MSSQL_URI.format(
            user=credentials["user"],
            password=uri_encode(credentials["password"]),
            host=credentials["host"],
            port=credentials.get("port") or DEFAULT_PORT,
            database=credentials["database"],
        )
        return uri

    def execute(self, query: ExtractionQuery) -> Iterator[dict]:
        """
        Re-implements the SQLAlchemyClient execute function to ensure we consume
        the cursor before calling connection.close() as it wipes out the data
        otherwise
        """
        connection = self.connect()
        try:
            proxy = connection.execute(text(query.statement), query.params)
            results = list(self._process_result(proxy))
            yield from results
        finally:
            self.close()

    def get_databases(self) -> list[str]:
        result = self.execute(
            ExtractionQuery("SELECT name FROM sys.databases", {})
        )
        return [
            row["name"]
            for row in result
            if row["name"] not in _SYSTEM_DATABASES
        ]
