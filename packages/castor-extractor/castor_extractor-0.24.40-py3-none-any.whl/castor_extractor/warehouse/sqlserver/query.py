import logging
from typing import Optional

from ..abstract import (
    AbstractQueryBuilder,
    ExtractionQuery,
    TimeFilter,
    WarehouseAsset,
)

logger = logging.getLogger(__name__)


_DATABASE_REQUIRED = (
    WarehouseAsset.SCHEMA,
    WarehouseAsset.TABLE,
    WarehouseAsset.COLUMN,
)


class MSSQLQueryBuilder(AbstractQueryBuilder):
    """
    Builds queries to extract assets from SQL Server.
    """

    def __init__(
        self,
        databases: list[str],
        time_filter: Optional[TimeFilter] = None,
    ):
        super().__init__(time_filter=time_filter)
        self._databases = databases

    @staticmethod
    def _format(query: ExtractionQuery, values: dict) -> ExtractionQuery:
        return ExtractionQuery(
            statement=query.statement.format(**values),
            params=query.params,
        )

    def build(self, asset: WarehouseAsset) -> list[ExtractionQuery]:
        query = self.build_default(asset)

        if asset not in _DATABASE_REQUIRED:
            return [query]

        logger.info(
            f"\tWill run queries with following database params: {self._databases}",
        )
        return [
            self._format(query, {"database": database})
            for database in self._databases
        ]
