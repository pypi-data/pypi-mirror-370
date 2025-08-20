from typing import Iterator, Optional

from ....utils import empty_iterator
from ....warehouse.abstract import WarehouseAsset
from ....warehouse.bigquery import BigQueryClient, BigQueryQueryBuilder
from .. import LookerStudioAsset
from .admin_sdk_client import USER_EMAIL_FIELD, AdminSDKClient
from .credentials import LookerStudioCredentials
from .looker_studio_api_client import LookerStudioAPIClient


class LookerStudioQueryBuilder(BigQueryQueryBuilder):
    def job_history_queries(self) -> list:
        """
        This class and method are a convenient workaround to build the
        ExtractionQueries which retrieve BigQuery's job history, but filtered on
        Looker Studio only.

        Compared to the generic BigQuery query history, only the SQL "template"
        changes. By defining this class here, this will pick the SQL file
        `queries/query.sql` located in the same directory as this file.
        """
        return super().build(WarehouseAsset.QUERY)  # type: ignore


class LookerStudioClient:
    """
    Acts as a wrapper class to fetch Looker Studio assets, which requires
    coordinating calls between the Admin SDK API and the Looker Studio API.

    If the BigQuery credentials are provided, it can also fetch the source queries
    of BigQuery data sources.
    """

    def __init__(
        self,
        credentials: LookerStudioCredentials,
        bigquery_credentials: Optional[dict] = None,
        user_emails: Optional[list[str]] = None,
    ):
        self.admin_sdk_client = AdminSDKClient(credentials)
        self.looker_studio_client = LookerStudioAPIClient(credentials)
        self.user_emails = user_emails

        self.bigquery_client: Optional[BigQueryClient] = None
        if bigquery_credentials:
            self.bigquery_client = BigQueryClient(bigquery_credentials)

    def _list_user_emails(self) -> Iterator[str]:
        """
        Lists user emails either from a provided JSON file or via the Admin SDK API.

        Using all Google Workspace users can be inefficient for large clients -
        the client might spend hours checking thousands of users for Looker Studio
        assets when only a handful actually own any. A JSON file allows
        targeting known owners instead.
        """
        if self.user_emails is not None:
            yield from self.user_emails
            return

        for user in self.admin_sdk_client.list_users():
            yield user[USER_EMAIL_FIELD]

    def _get_assets(self) -> Iterator[dict]:
        """
        Extracts reports and data sources user by user. The loop is necessary
        because the Looker Studio API can only retrieve the assets owned by a
        single user.
        """
        for user_email in self._list_user_emails():
            yield from self.looker_studio_client.fetch_user_assets(user_email)

    def _get_source_queries(self) -> Iterator[dict]:
        """
        Extracts the BigQuery jobs triggered by Looker Studio. The last job
        per data source is returned.
        """
        if not self.bigquery_client:
            return empty_iterator()

        query_builder = LookerStudioQueryBuilder(
            regions=self.bigquery_client.get_regions(),
            datasets=self.bigquery_client.get_datasets(),
            extended_regions=self.bigquery_client.get_extended_regions(),
        )

        queries = query_builder.job_history_queries()

        for query in queries:
            yield from self.bigquery_client.execute(query)

    def fetch(self, asset: LookerStudioAsset) -> Iterator[dict]:
        if asset == LookerStudioAsset.ASSETS:
            yield from self._get_assets()

        elif asset == LookerStudioAsset.SOURCE_QUERIES:
            yield from self._get_source_queries()

        elif asset == LookerStudioAsset.VIEW_ACTIVITY:
            yield from self.admin_sdk_client.list_view_events()

        else:
            raise ValueError(f"The asset {asset}, is not supported")
