import logging
from collections.abc import Iterator
from typing import Optional

import requests
import tableauserverclient as TSC  # type: ignore

from ....utils import SerializedAsset, retry
from ..assets import TableauAsset
from ..constants import DEFAULT_PAGE_SIZE
from .errors import TableauApiError, TableauApiTimeout
from .gql_queries import FIELDS_QUERIES, GQL_QUERIES, QUERY_TEMPLATE

logger = logging.getLogger(__name__)

# These assets are known to be error-prone, so it's acceptable if a few are missed.
# If errors occur, skip the current batch.
_SAFE_MODE_ASSETS = (
    TableauAsset.COLUMN,
    TableauAsset.FIELD,
)

# increase the value when extraction is too slow
# decrease the value when timeouts arise
_CUSTOM_PAGE_SIZE: dict[TableauAsset, int] = {
    # fields are light but volumes are bigger
    TableauAsset.FIELD: 1000,
    # tables are sometimes heavy
    TableauAsset.TABLE: 50,
}

_TIMEOUT_MESSAGE = (
    "Execution canceled because timeout of 30000 millis was reached"
)

_RETRY_BASE_MS = 10_000
_RETRY_COUNT = 4


def _is_timeout(error: dict) -> bool:
    error_message = error.get("message")
    return error_message == _TIMEOUT_MESSAGE


def _is_warning(error: dict) -> bool:
    extensions = error.get("extensions")
    if not extensions:
        return False

    severity = extensions.get("severity")
    if not severity:
        return False

    return severity.lower() == "warning"


def _check_errors(answer: dict) -> None:
    """
    Handle errors in graphql response:
    - return None when there's no errors in the answer
    - raise TableauApiTimeout if any of the errors is a timeout
    - else raise TableauApiError if any of the errors is critical
    - return None otherwise
    More info about Tableau errors:
    https://help.tableau.com/current/api/metadata_api/en-us/docs/meta_api_errors.html#other-errors
    """
    if "errors" not in answer:
        return

    errors = answer["errors"]

    has_timeout_errors = False
    has_critical_errors = False

    for error in errors:
        if _is_timeout(error):
            has_timeout_errors = True
            continue

        if _is_warning(error):
            # in this case, the answer contains the data anyway
            # just display the warning
            logger.warning(error)
            continue

        # at this point, it's not a timeout error
        # besides, it's not a warning (severity is either "error" or Unknown)
        has_critical_errors = True

    if has_timeout_errors:
        raise TableauApiTimeout(errors)
    if has_critical_errors:
        raise TableauApiError(errors)

    return None


def gql_query_scroll(
    server,
    resource: str,
    fields: str,
    page_size: int,
    skip_batch: bool,
) -> Iterator[SerializedAsset]:
    """
    Iterate over GQL query results, handling pagination and cursor

    We have a retry strategy when timeout issues arise.
    It's a known issue on Tableau side, still waiting for their fix:
    https://issues.salesforce.com/issue/a028c00000zKahoAAC/undefined
    """

    @retry(
        exceptions=(TableauApiTimeout,),
        max_retries=_RETRY_COUNT,
        base_ms=_RETRY_BASE_MS,
    )
    def _call(first: int, offset: int) -> dict:
        query = QUERY_TEMPLATE.format(
            resource=resource,
            fields=fields,
            first=first,
            offset=offset,
        )
        answer = server.metadata.query(query)
        _check_errors(answer)
        return answer["data"][f"{resource}Connection"]

    current_offset = 0
    while True:
        try:
            payload = _call(first=page_size, offset=current_offset)
            yield payload["nodes"]

            current_offset += len(payload["nodes"])
            total = payload["totalCount"]
            logger.info(f"Extracted {current_offset}/{total} {resource}")

            if not payload["pageInfo"]["hasNextPage"]:
                break
        except requests.exceptions.ReadTimeout:
            if not skip_batch:
                raise

            logger.warning("Skipping batch because of TableauServer Timeout")
            current_offset += page_size


def _deduplicate(result_pages: Iterator[SerializedAsset]) -> SerializedAsset:
    """
    Sometimes assets are duplicated, which triggers UniqueViolation errors
    during store_all down the line.

    We suspect the offset pagination to be the root cause, because we had no
    problem until recently, when we switched from cursor pagination to offset
    pagination (for performance reasons)
    https://help.tableau.com/current/api/metadata_api/en-us/docs/meta_api_examples.html#pagination

    This is a straightforward solution to remove these duplicates directly at
    extraction.
    We don't show warnings because duplicates are expected, and we keep only
    the first occurrence since those duplicates are probably identical.
    """
    deduplicated: SerializedAsset = []
    seen_ids: set[str] = set()
    for page in result_pages:
        for asset in page:
            asset_id = asset["id"]
            if asset_id in seen_ids:
                # skip duplicate
                continue
            deduplicated.append(asset)
            seen_ids.add(asset_id)
    return deduplicated


class TableauClientMetadataApi:
    """
    Calls the MetadataAPI, using graphQL
    https://help.tableau.com/current/api/metadata_api/en-us/reference/index.html
    """

    def __init__(
        self,
        server: TSC.Server,
        override_page_size: Optional[int] = None,
    ):
        self._server = server
        self._override_page_size = override_page_size

    def _call(
        self,
        resource: str,
        fields: str,
        page_size: int = DEFAULT_PAGE_SIZE,
        skip_batch: bool = False,
    ) -> SerializedAsset:
        result_pages = gql_query_scroll(
            self._server,
            resource=resource,
            fields=fields,
            page_size=page_size,
            skip_batch=skip_batch,
        )
        return _deduplicate(result_pages)

    def _page_size(self, asset: TableauAsset) -> int:
        return (
            self._override_page_size
            or _CUSTOM_PAGE_SIZE.get(asset)
            or DEFAULT_PAGE_SIZE
        )

    def _fetch_fields(self, skip_batch: bool = False) -> SerializedAsset:
        result: SerializedAsset = []
        page_size = self._page_size(TableauAsset.FIELD)
        for resource, fields in FIELDS_QUERIES:
            current = self._call(
                resource,
                fields,
                page_size,
                skip_batch=skip_batch,
            )
            result.extend(current)
        return result

    @staticmethod
    def _should_skip_batch_with_timeout(
        asset: TableauAsset,
        ignore_metadata_errors: bool = False,
    ) -> bool:
        return asset in _SAFE_MODE_ASSETS and ignore_metadata_errors

    def fetch(
        self,
        asset: TableauAsset,
        ignore_errors: bool = False,
    ) -> SerializedAsset:
        skip_batch = self._should_skip_batch_with_timeout(asset, ignore_errors)

        if asset == TableauAsset.FIELD:
            return self._fetch_fields(skip_batch=skip_batch)

        page_size = self._page_size(asset)
        resource, fields = GQL_QUERIES[asset]
        return self._call(
            resource=resource,
            fields=fields,
            page_size=page_size,
            skip_batch=skip_batch,
        )
