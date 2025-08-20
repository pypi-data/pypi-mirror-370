from typing import Optional

from ..abstract import (
    CATALOG_ASSETS,
    AbstractQueryBuilder,
    ExtractionQuery,
    TimeFilter,
    WarehouseAsset,
)

DB_FILTERED_ASSETS = (
    *CATALOG_ASSETS,
    WarehouseAsset.VIEW_DDL,
)


def _database_filter(db_list: Optional[list[str]], allow: bool) -> str:
    if not db_list:
        return ""
    keyword = "IN" if allow else "NOT IN"
    db_list_str = ", ".join([f"'{db}'" for db in db_list])
    return f"AND database_name {keyword} ({db_list_str})"


def _transient_filter(has_transient: Optional[bool] = False) -> str:
    return "TRUE" if has_transient else "FALSE"


class SnowflakeQueryBuilder(AbstractQueryBuilder):
    """
    Builds queries to extract assets from Snowflake.
    """

    def __init__(
        self,
        time_filter: Optional[TimeFilter] = None,
        db_allowed: Optional[list[str]] = None,
        db_blocked: Optional[list[str]] = None,
        fetch_transient: Optional[bool] = False,
    ):
        super().__init__(time_filter=time_filter)
        self._db_allowed = _database_filter(db_allowed, allow=True)
        self._db_blocked = _database_filter(db_blocked, allow=False)
        self._fetch_transient = _transient_filter(fetch_transient)

    def _apply_db_filters(self, statement: str) -> str:
        statement = statement.format(
            database_allowed=self._db_allowed,
            database_blocked=self._db_blocked,
            has_fetch_transient=self._fetch_transient,
        )

        return statement

    def build(self, asset: WarehouseAsset) -> list[ExtractionQuery]:
        query = self.build_default(asset)

        if asset in DB_FILTERED_ASSETS:
            query.statement = self._apply_db_filters(query.statement)

        return [query]
