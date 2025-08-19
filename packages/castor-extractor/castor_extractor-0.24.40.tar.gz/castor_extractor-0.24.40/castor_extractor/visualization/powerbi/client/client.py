import logging
from collections.abc import Iterator
from datetime import date
from functools import partial
from http import HTTPStatus
from time import sleep
from typing import Optional, Union

import requests
from requests import HTTPError

from ....utils import (
    APIClient,
    fetch_all_pages,
    retry_request,
)
from ..assets import PowerBiAsset
from .authentication import PowerBiBearerAuth
from .constants import Keys
from .credentials import PowerbiCredentials
from .endpoints import PowerBiEndpointFactory
from .pagination import PowerBiPagination

POWERBI_DEFAULT_TIMEOUT_S = 30
# The route we use to fetch workspaces info can retrieve a maximum of
# 100 workspaces per call
# More: https://learn.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-post-workspace-info#request-body
METADATA_BATCH_SIZE = 100
POWERBI_SCAN_STATUS_DONE = "Succeeded"
POWERBI_SCAN_SLEEP_S = 1
POWERBI_SCAN_TIMEOUT_S = 60

MAX_RETRY_PAGES = 1
RETRY_PAGES_TIMEOUT_MS = 35 * 1000  # 35 seconds

logger = logging.getLogger(__name__)


class PowerbiClient(APIClient):
    def __init__(
        self,
        credentials: PowerbiCredentials,
    ):
        auth = PowerBiBearerAuth(credentials=credentials)
        super().__init__(
            auth=auth,
            timeout=POWERBI_DEFAULT_TIMEOUT_S,
        )
        self.endpoint_factory = PowerBiEndpointFactory(
            login_url=credentials.login_url,
            api_base=credentials.api_base,
        )

    def _activity_events(self, day: Optional[date] = None) -> Iterator[dict]:
        """
        Returns a list of activity events for the organization.
        https://learn.microsoft.com/en-us/power-bi/admin/service-admin-auditing#activityevents-rest-api
        - when no day is specified, fallback is yesterday
        """
        request = partial(
            self._get,
            endpoint=self.endpoint_factory.activity_events(day),
        )
        yield from fetch_all_pages(request, PowerBiPagination)

    def _datasets(self) -> Iterator[dict]:
        """
        Returns a list of datasets for the organization.
        https://learn.microsoft.com/en-us/rest/api/power-bi/admin/datasets-get-datasets-as-admin
        """
        yield from self._get(self.endpoint_factory.datasets())[Keys.VALUE]

    def _dashboards(self) -> Iterator[dict]:
        """
        Returns a list of dashboards for the organization.
        https://learn.microsoft.com/en-us/rest/api/power-bi/admin/dashboards-get-dashboards-as-admin
        """
        yield from self._get(self.endpoint_factory.dashboards())[Keys.VALUE]

    @retry_request(
        status_codes=(HTTPStatus.TOO_MANY_REQUESTS,),
        max_retries=MAX_RETRY_PAGES,
        base_ms=RETRY_PAGES_TIMEOUT_MS,
    )
    def _pages(self, report_id: str) -> Iterator[dict]:
        """
        Extracts the pages of a report.
        This endpoint is very flaky and frequently returns 400 and 404 errors.
        After around 50 requests, it hits the rate limit and returns 429 Too Many Requests,
        which is why we retry it after a short delay.
        Timeouts are also common; we must skip them because the extraction task
        might take too long otherwise.
        """
        pages_endpoint = self.endpoint_factory.pages(report_id)
        return self._get(pages_endpoint, retry_on_timeout=False)[Keys.VALUE]

    def _reports(self) -> Iterator[dict]:
        """
        Returns a list of reports for the organization.
        https://learn.microsoft.com/en-us/rest/api/power-bi/admin/reports-get-reports-as-admin
        """
        reports_endpoint = self.endpoint_factory.reports()
        reports = self._get(reports_endpoint)[Keys.VALUE]

        for report in reports:
            report_id = report.get(Keys.ID)

            try:
                pages = self._pages(report_id)
                report["pages"] = pages
            except (requests.HTTPError, requests.exceptions.Timeout) as e:
                logger.debug(e)
                continue

        return reports

    def _workspace_ids(self) -> list[str]:
        """
        Get workspaces ids from powerBI admin API.
        more: https://learn.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-get-modified-workspaces
        """
        params: dict[str, Union[bool, str]] = {
            Keys.INACTIVE_WORKSPACES: True,
            Keys.PERSONAL_WORKSPACES: True,
        }

        response = self._get(
            self.endpoint_factory.workspace_ids(),
            params=params,
        )

        return [x[Keys.ID] for x in response]

    def _get_scan_result(self, scan_id: int) -> Iterator[dict]:
        endpoint = self.endpoint_factory.metadata_scan_result(scan_id)
        yield from self._get(endpoint)[Keys.WORKSPACES]

    def _wait_for_scan_result(self, scan_id: int) -> bool:
        """
        Periodically checks the status of the metadata scan until the results
        are ready.
        """
        endpoint = self.endpoint_factory.metadata_scan_status(scan_id)
        total_waiting_time_s = 0

        while total_waiting_time_s < POWERBI_SCAN_TIMEOUT_S:
            try:
                result = self._get(endpoint)
            except HTTPError as e:
                logger.error(f"Scan {scan_id} failed. Error: {e}")
                return False

            if result[Keys.STATUS] == POWERBI_SCAN_STATUS_DONE:
                logger.info(f"scan {scan_id} ready")
                return True

            total_waiting_time_s += POWERBI_SCAN_SLEEP_S
            logger.info(
                f"Waiting {POWERBI_SCAN_SLEEP_S} sec for scan {scan_id} to be ready…",
            )
            sleep(POWERBI_SCAN_SLEEP_S)

        logger.warning(f"Scan {scan_id} timed out")
        return False

    def _create_scan(self, workspaces_ids: list[str]) -> int:
        """
        Tells the Power BI API to start an asynchronous metadata scan.
        Returns the scan's ID.
        https://learn.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-post-workspace-info
        """
        params = {
            "datasetExpressions": True,
            "datasetSchema": True,
            "datasourceDetails": True,
            "getArtifactUsers": True,
            "lineage": True,
        }
        request_body = {"workspaces": workspaces_ids}
        scan_id = self._post(
            self.endpoint_factory.metadata_create_scan(),
            params=params,
            data=request_body,
        )
        return scan_id[Keys.ID]

    def _metadata(self) -> Iterator[dict]:
        """
        Fetch metadata by workspace. The metadata scanning is asynchronous and
        requires the following steps:
        - create the asynchronous scan
        - periodically check the scan status to know when it's finished
        - get the actual scan results
        https://learn.microsoft.com/en-us/power-bi/enterprise/service-admin-metadata-scanning
        """
        ids = self._workspace_ids()

        for index in range(0, len(ids), METADATA_BATCH_SIZE):
            batch_ids = ids[index : index + METADATA_BATCH_SIZE]
            scan_id = self._create_scan(batch_ids)
            self._wait_for_scan_result(scan_id)
            yield from self._get_scan_result(scan_id)

    def test_connection(self) -> None:
        """Use credentials & verify requesting the API doesn't raise an error"""
        self._auth.refresh_token()

    def fetch(
        self,
        asset: PowerBiAsset,
        *,
        day: Optional[date] = None,
    ) -> Iterator[dict]:
        """
        Given a PowerBi asset, returns the corresponding data using the
        appropriate client.
        """
        if asset == PowerBiAsset.ACTIVITY_EVENTS:
            yield from self._activity_events(day=day)

        elif asset == PowerBiAsset.DATASETS:
            yield from self._datasets()

        elif asset == PowerBiAsset.DASHBOARDS:
            yield from self._dashboards()

        elif asset == PowerBiAsset.REPORTS:
            yield from self._reports()

        elif asset == PowerBiAsset.METADATA:
            yield from self._metadata()

        else:
            raise ValueError(f"This asset {asset} is unknown")
