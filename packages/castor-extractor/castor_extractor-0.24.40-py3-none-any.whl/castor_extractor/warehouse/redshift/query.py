from typing import Optional

from ..abstract import (
    AbstractQueryBuilder,
    ExtractionQuery,
    TimeFilter,
    WarehouseAsset,
)


class RedshiftQueryBuilder(AbstractQueryBuilder):
    """
    Builds queries to extract assets from Redshift.
    """

    def __init__(
        self,
        is_serverless: bool = False,
        time_filter: Optional[TimeFilter] = None,
    ):
        super().__init__(time_filter=time_filter)
        self.is_serverless = is_serverless

    def build_query_serverless(self) -> ExtractionQuery:
        """To get the query history in Redshift Serverless, we cannot use STL tables."""
        statement = self._load_from_file("query_serverless.sql")
        params = self._time_filter.to_dict()
        return ExtractionQuery(statement, params)

    def build(self, asset: WarehouseAsset) -> list[ExtractionQuery]:
        if asset == WarehouseAsset.QUERY and self.is_serverless:
            query = self.build_query_serverless()
        else:
            query = self.build_default(asset)
        return [query]
