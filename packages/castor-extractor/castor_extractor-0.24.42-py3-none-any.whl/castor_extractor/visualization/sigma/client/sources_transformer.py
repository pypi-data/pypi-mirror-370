import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Callable, Iterator

from ....utils import retry_request
from .endpoints import SigmaEndpointFactory

if TYPE_CHECKING:
    from .client import SigmaClient

logger = logging.getLogger(__name__)

SIGMA_CONNECTION_PATH_MAX_RETRY = 1
SIGMA_CONNECTION_PATH_SLEEP_MS = 30_000  # 30 seconds


class SigmaSourcesTransformer:
    """Retrieves asset sources and enhances them with additional information."""

    def __init__(self, api_client: "SigmaClient"):
        self.api_client = api_client

    @retry_request(
        status_codes=(HTTPStatus.TOO_MANY_REQUESTS,),
        max_retries=SIGMA_CONNECTION_PATH_MAX_RETRY,
        base_ms=SIGMA_CONNECTION_PATH_SLEEP_MS,
    )
    def _get_connection_path(self, table_id: str) -> dict:
        """Retrieves the connection path for a given table id"""
        return self.api_client._get(
            endpoint=SigmaEndpointFactory.connection_path(table_id)
        )

    def _map_table_id_to_connection_path(
        self, all_sources: list
    ) -> dict[str, dict]:
        """Maps a table id to its connection and path information."""
        logger.info("Mapping table ids to connection and path information")

        unique_table_ids = {
            source["inodeId"]
            for asset_sources in all_sources
            for source in asset_sources["sources"]
            if source["type"] == "table"
        }

        return {
            table_id: self._get_connection_path(table_id)
            for table_id in unique_table_ids
        }

    @staticmethod
    def _enhance_table_source(source: dict, table_to_path: dict) -> dict:
        """
        Combines a single table source with its connection and path information.
        """
        if source["type"] != "table":
            return source

        path_info = table_to_path.get(source["inodeId"], {})
        source["connectionId"] = path_info.get("connectionId")
        source["path"] = path_info.get("path")
        return source

    def _transform_sources(
        self, all_sources: list, table_to_path: dict
    ) -> Iterator[dict]:
        """
        Yields all sources, with table sources being enhanced with additional information.
        """
        logger.info("Merging sources with table information")

        for asset_sources in all_sources:
            enhanced_sources = [
                self._enhance_table_source(source, table_to_path)
                for source in asset_sources["sources"]
            ]

            yield {
                "asset_id": asset_sources["asset_id"],
                "sources": enhanced_sources,
            }

    def _get_all_sources(
        self, endpoint: Callable[[str], str], asset_ids: set[str]
    ) -> Iterator[dict]:
        """Returns transformed sources for the given assets"""
        all_sources = []

        for asset_id in asset_ids:
            sources = self.api_client._get(endpoint=endpoint(asset_id))
            all_sources.append({"asset_id": asset_id, "sources": sources})

        table_to_path = self._map_table_id_to_connection_path(all_sources)

        yield from self._transform_sources(all_sources, table_to_path)

    def get_dataset_sources(self, datasets: list[dict]) -> Iterator[dict]:
        asset_ids = {dataset["datasetId"] for dataset in datasets}
        yield from self._get_all_sources(
            endpoint=SigmaEndpointFactory.dataset_sources, asset_ids=asset_ids
        )

    def get_workbook_sources(self, workbooks: list[dict]) -> Iterator[dict]:
        asset_ids = {workbook["workbookId"] for workbook in workbooks}
        yield from self._get_all_sources(
            endpoint=SigmaEndpointFactory.workbook_sources, asset_ids=asset_ids
        )
