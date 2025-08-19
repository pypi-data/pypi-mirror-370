import msal  # type: ignore

from ....utils import BearerAuth
from .constants import Keys
from .credentials import PowerbiCredentials
from .endpoints import PowerBiEndpointFactory


class PowerBiBearerAuth(BearerAuth):
    def __init__(self, credentials: PowerbiCredentials):
        self.credentials = credentials
        endpoint_factory = PowerBiEndpointFactory(
            login_url=self.credentials.login_url,
            api_base=self.credentials.api_base,
        )
        authority = endpoint_factory.authority(self.credentials.tenant_id)
        self.app = msal.ConfidentialClientApplication(
            client_id=self.credentials.client_id,
            authority=authority,
            client_credential=self.credentials.secret,
        )

    def fetch_token(self):
        token = self.app.acquire_token_for_client(
            scopes=self.credentials.scopes
        )

        if Keys.ACCESS_TOKEN not in token:
            raise ValueError(f"No access token in token response: {token}")

        return token[Keys.ACCESS_TOKEN]
