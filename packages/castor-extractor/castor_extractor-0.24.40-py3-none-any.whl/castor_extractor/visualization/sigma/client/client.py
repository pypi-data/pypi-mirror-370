import logging
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from http import HTTPStatus
from typing import Callable, Iterable, Optional

import requests
from pydantic import BaseModel

from ....utils import (
    APIClient,
    BearerAuth,
    RequestSafeMode,
    build_url,
    fetch_all_pages,
    handle_response,
    retry,
)
from ..assets import SigmaAsset
from .credentials import SigmaCredentials
from .endpoints import SigmaEndpointFactory
from .pagination import (
    SIGMA_API_LIMIT,
    SIGMA_QUERIES_PAGINATION_LIMIT,
    SigmaPagination,
)
from .sources_transformer import SigmaSourcesTransformer

logger = logging.getLogger(__name__)

_CONTENT_TYPE = "application/x-www-form-urlencoded"

_DATA_ELEMENTS: tuple[str, ...] = (
    "input-table",
    "pivot-table",
    "table",
    "visualization",
    "viz",
)

_AUTH_TIMEOUT_S = 60
_SIGMA_TIMEOUT_S = 300

_SIGMA_HEADERS = {
    "Content-Type": _CONTENT_TYPE,
}

_VOLUME_IGNORED = 10_000
_IGNORED_ERROR_CODES = (
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.CONFLICT,
    HTTPStatus.NOT_FOUND,
)
SIGMA_SAFE_MODE = RequestSafeMode(
    max_errors=_VOLUME_IGNORED,
    status_codes=_IGNORED_ERROR_CODES,
)
SIGMA_SAFE_MODE_LINEAGE = RequestSafeMode(
    max_errors=_VOLUME_IGNORED,
    status_codes=(
        *_IGNORED_ERROR_CODES,
        HTTPStatus.FORBIDDEN,
    ),
)
_THREADS_LINEAGE = 10  # empirically found; hit the rate limit with 20 workers
_RETRY_NUMBER = 1
_RETRY_BASE_MS = 60_000


class LineageContext(BaseModel):
    """all info needed to build the endpoint for lineage retrieval"""

    workbook_id: str
    element_id: str


class Lineage(BaseModel):
    """holds response from lineage API and context used to retrieve it"""

    lineage: dict
    context: LineageContext


class SigmaBearerAuth(BearerAuth):
    def __init__(self, host: str, token_payload: dict[str, str]):
        auth_endpoint = SigmaEndpointFactory.authentication()
        self.authentication_url = build_url(host, auth_endpoint)
        self.token_payload = token_payload

    def fetch_token(self):
        token_api_path = self.authentication_url
        token_response = requests.post(
            token_api_path, data=self.token_payload, timeout=_AUTH_TIMEOUT_S
        )
        return handle_response(token_response)["access_token"]


class SigmaClient(APIClient):
    def __init__(
        self,
        credentials: SigmaCredentials,
        safe_mode: Optional[RequestSafeMode] = None,
    ):
        auth = SigmaBearerAuth(
            host=credentials.host,
            token_payload=credentials.token_payload,
        )
        super().__init__(
            host=credentials.host,
            auth=auth,
            headers=_SIGMA_HEADERS,
            timeout=_SIGMA_TIMEOUT_S,
            safe_mode=safe_mode or SIGMA_SAFE_MODE,
        )

    def _get_paginated(
        self,
        endpoint: str,
        limit: int = SIGMA_API_LIMIT,
    ) -> Callable:
        """
        Sigma’s API does not experience random timeouts, unlike some other APIs.
        However, extracting queries from certain workbooks can take a
        significant amount of time.
        Previously, when a timeout occurred, the system would retry multiple
        times — even though we knew it would eventually fail due to the inherent
        slowness of the operation.
        These retries only delayed the inevitable failure without adding value.
        To address this, we've disabled retries on timeout and instead adjusted
        the page size when extracting queries.
        """
        return partial(
            self._get,
            retry_on_timeout=False,  # explained in the docstring
            endpoint=endpoint,
            params={"limit": limit},
        )

    def _get_all_datamodels(self) -> Iterator[dict]:
        request = self._get_paginated(
            endpoint=SigmaEndpointFactory.datamodels()
        )
        yield from fetch_all_pages(request, SigmaPagination)

    def _get_all_datasets(self) -> Iterator[dict]:
        request = self._get_paginated(endpoint=SigmaEndpointFactory.datasets())
        yield from fetch_all_pages(request, SigmaPagination)

    def _get_all_files(self) -> Iterator[dict]:
        request = self._get_paginated(endpoint=SigmaEndpointFactory.files())
        yield from fetch_all_pages(request, SigmaPagination)

    def _get_all_members(self) -> Iterator[dict]:
        request = self._get_paginated(endpoint=SigmaEndpointFactory.members())
        yield from fetch_all_pages(request, SigmaPagination)

    def _get_all_workbooks(self) -> Iterator[dict]:
        request = self._get_paginated(endpoint=SigmaEndpointFactory.workbooks())
        yield from fetch_all_pages(request, SigmaPagination)

    def _get_elements_per_page(
        self, page: dict, workbook_id: str
    ) -> Iterator[dict]:
        page_id = page["pageId"]
        request = self._get_paginated(
            SigmaEndpointFactory.elements(workbook_id, page_id)
        )
        elements = fetch_all_pages(request, SigmaPagination)
        for element in elements:
            if element.get("type") not in _DATA_ELEMENTS:
                continue
            yield {
                **element,
                "workbook_id": workbook_id,
                "page_id": page_id,
            }

    def _get_all_elements(self, workbooks: list[dict]) -> Iterator[dict]:
        for workbook in workbooks:
            workbook_id = workbook["workbookId"]

            request = self._get_paginated(
                SigmaEndpointFactory.pages(workbook_id)
            )
            pages = fetch_all_pages(request, SigmaPagination)

            for page in pages:
                yield from self._get_elements_per_page(
                    page=page, workbook_id=workbook_id
                )

    @retry(
        (ConnectionError,),
        max_retries=_RETRY_NUMBER,
        base_ms=_RETRY_BASE_MS,
        log_exc_info=True,
    )
    def _get_lineage(self, lineage_context: LineageContext) -> Lineage:
        """
        return the lineage from API and other ids needed to characterize
        lineage in castor
        """
        workbook_id = lineage_context.workbook_id
        element_id = lineage_context.element_id
        endpoint = SigmaEndpointFactory.lineage(workbook_id, element_id)
        return Lineage(lineage=self._get(endpoint), context=lineage_context)

    @staticmethod
    def _lineage_context(elements: list[dict]) -> list[LineageContext]:
        """
        Helper function to prepare context for lineage retrieval.
        Elements without associated columns are skipped.
        """
        contexts: list[LineageContext] = []
        for element in elements:
            if element.get("columns") is None:
                continue

            context = LineageContext(
                workbook_id=element["workbook_id"],
                element_id=element["elementId"],
            )
            contexts.append(context)
        return contexts

    def _get_all_lineages(self, elements: list[dict]) -> Iterator[dict]:
        """
        The safe mode is temporarily modified to include 403 errors.

        Due to concurrency issues, we force a refresh of the token in hopes that
        the lineage extraction takes less than the token expiration time of
        1 hour.
        """
        safe_mode = self._safe_mode
        self._safe_mode = SIGMA_SAFE_MODE_LINEAGE

        lineage_context = self._lineage_context(elements)

        self._auth.refresh_token()

        with ThreadPoolExecutor(max_workers=_THREADS_LINEAGE) as executor:
            results = executor.map(self._get_lineage, lineage_context)

        for lineage in results:
            if not lineage.lineage:
                continue

            yield {
                **lineage.lineage,
                "workbook_id": lineage.context.workbook_id,
                "element_id": lineage.context.element_id,
            }

        self._safe_mode = safe_mode

    @staticmethod
    def _yield_deduplicated_queries(
        queries: Iterable[dict], workbook_id: str
    ) -> Iterator[dict]:
        """
        Returns unique queries for a workbook. This is necessary because the API
        unfortunately returns duplicate entries for some workbook elements.
        """
        seen_elements = set()

        for query in queries:
            element_id = query["elementId"]
            if element_id in seen_elements:
                continue

            seen_elements.add(element_id)
            yield {**query, "workbook_id": workbook_id}

    def _get_all_queries(self, workbooks: list[dict]) -> Iterator[dict]:
        for workbook in workbooks:
            workbook_id = workbook["workbookId"]
            request = self._get_paginated(
                SigmaEndpointFactory.queries(workbook_id),
                limit=SIGMA_QUERIES_PAGINATION_LIMIT,
            )
            queries = fetch_all_pages(request, SigmaPagination)

            yield from self._yield_deduplicated_queries(queries, workbook_id)

    def _get_all_dataset_sources(self, datasets: list[dict]) -> Iterator[dict]:
        yield from SigmaSourcesTransformer(self).get_dataset_sources(datasets)

    def _get_all_workbook_sources(
        self, workbooks: list[dict]
    ) -> Iterator[dict]:
        yield from SigmaSourcesTransformer(self).get_workbook_sources(workbooks)

    def fetch(
        self,
        asset: SigmaAsset,
        datasets: Optional[list[dict]] = None,
        elements: Optional[list[dict]] = None,
        workbooks: Optional[list[dict]] = None,
    ) -> Iterator[dict]:
        """Returns the needed metadata for the queried asset"""
        if asset == SigmaAsset.DATAMODELS:
            yield from self._get_all_datamodels()

        elif asset == SigmaAsset.DATASETS:
            yield from self._get_all_datasets()

        elif asset == SigmaAsset.DATASET_SOURCES:
            if datasets is None:
                raise ValueError("Missing datasets to extract dataset sources")

            yield from self._get_all_dataset_sources(datasets)

        elif asset == SigmaAsset.ELEMENTS:
            if workbooks is None:
                raise ValueError("Missing workbooks to extract elements")

            yield from self._get_all_elements(workbooks)

        elif asset == SigmaAsset.FILES:
            yield from self._get_all_files()

        elif asset == SigmaAsset.LINEAGES:
            if elements is None:
                raise ValueError("Missing elements to extract lineage")

            yield from self._get_all_lineages(elements)

        elif asset == SigmaAsset.MEMBERS:
            yield from self._get_all_members()

        elif asset == SigmaAsset.QUERIES:
            if workbooks is None:
                raise ValueError("Missing workbooks to extract queries")

            yield from self._get_all_queries(workbooks)

        elif asset == SigmaAsset.WORKBOOKS:
            yield from self._get_all_workbooks()

        elif asset == SigmaAsset.WORKBOOK_SOURCES:
            if workbooks is None:
                raise ValueError(
                    "Missing workbooks to extract workbook sources"
                )

            yield from self._get_all_workbook_sources(workbooks)

        else:
            raise ValueError(f"This asset {asset} is unknown")
