from datetime import date
from unittest.mock import Mock, call, patch

import pytest

from .authentication import msal
from .client import PowerbiClient
from .constants import Keys
from .credentials import CLIENT_APP_BASE, REST_API_BASE_PATH, PowerbiCredentials
from .endpoints import PowerBiEndpointFactory

FAKE_TENANT_ID = "IamFake"
FAKE_CLIENT_ID = "MeTwo"
FAKE_SECRET = "MeThree"

ENDPOINT_FACTORY = PowerBiEndpointFactory(
    login_url=CLIENT_APP_BASE,
    api_base=REST_API_BASE_PATH + "/",  # superfluous "/" to test resiliency
)


@pytest.fixture
def mock_msal():
    with patch.object(msal, "ConfidentialClientApplication") as mock_app:
        mock_app.return_value.acquire_token_for_client.return_value = {
            "access_token": "fake_token"
        }
        yield mock_app


@pytest.fixture
def power_bi_client(mock_msal):
    creds = PowerbiCredentials(
        tenant_id=FAKE_TENANT_ID,
        client_id=FAKE_CLIENT_ID,
        secret=FAKE_SECRET,
    )
    return PowerbiClient(creds)


def test__access_token(power_bi_client, mock_msal):
    # Valid token scenario
    valid_token = "mock_token"
    mock_response = {"access_token": valid_token}
    returning_valid_token = Mock(return_value=mock_response)
    mock_msal.return_value.acquire_token_for_client = returning_valid_token

    assert power_bi_client._auth.fetch_token() == valid_token

    # Invalid token scenario
    invalid_response = {"not_access_token": "666"}
    returning_invalid_token = Mock(return_value=invalid_response)
    mock_msal.return_value.acquire_token_for_client = returning_invalid_token

    with pytest.raises(ValueError):
        power_bi_client._auth.fetch_token()


def test__datasets(power_bi_client):
    with patch.object(power_bi_client, "_get") as mocked_get:
        mocked_get.return_value = {"value": [{"id": 1, "type": "dataset"}]}
        datasets = list(power_bi_client._datasets())
        mocked_get.assert_called_with(ENDPOINT_FACTORY.datasets())
        assert datasets == [{"id": 1, "type": "dataset"}]


def test__dashboards(power_bi_client):
    with patch.object(power_bi_client, "_get") as mocked_get:
        mocked_get.return_value = {"value": [{"id": 1, "type": "dashboard"}]}
        dashboards = list(power_bi_client._dashboards())
        mocked_get.assert_called_with(ENDPOINT_FACTORY.dashboards())
        assert dashboards == [{"id": 1, "type": "dashboard"}]


def test__reports(power_bi_client):
    with patch.object(power_bi_client, "_get") as mocked_get:
        mocked_get.side_effect = [
            {"value": [{"id": 1, "type": "report"}]},
            {
                "value": [
                    {"name": "page_name", "displayName": "page", "order": 0}
                ]
            },
        ]
        reports = list(power_bi_client._reports())
        calls = [
            call(ENDPOINT_FACTORY.reports()),
            call(ENDPOINT_FACTORY.pages("1"), retry_on_timeout=False),
        ]
        mocked_get.assert_has_calls(calls)
        assert reports == [
            {
                "id": 1,
                "type": "report",
                "pages": [
                    {"name": "page_name", "displayName": "page", "order": 0}
                ],
            }
        ]


def test__workspace_ids(power_bi_client):
    with patch.object(power_bi_client, "_get") as mocked_get:
        mocked_get.return_value = [{"id": 1000}, {"id": 1001}, {"id": 1003}]

        ids = power_bi_client._workspace_ids()
        assert ids == [1000, 1001, 1003]

        params = {
            Keys.INACTIVE_WORKSPACES: True,
            Keys.PERSONAL_WORKSPACES: True,
        }

        mocked_get.assert_called_with(
            ENDPOINT_FACTORY.workspace_ids(),
            params=params,
        )


@patch.object(PowerbiClient, "_get_scan_result")
@patch.object(PowerbiClient, "_wait_for_scan_result")
@patch.object(PowerbiClient, "_create_scan")
@patch.object(PowerbiClient, "_workspace_ids")
def test__metadata(
    mock_workspace_ids,
    mock_create_scan,
    mock_wait_for_scan,
    mock_get_scan_result,
    power_bi_client,
):
    mock_workspace_ids.return_value = list(range(200))
    mock_create_scan.return_value = 314
    mock_wait_for_scan.return_value = True
    mock_get_scan_result.return_value = [{"workspace_id": 1871}]

    result = list(power_bi_client._metadata())

    assert result == [{"workspace_id": 1871}, {"workspace_id": 1871}]


def test__activity_events(power_bi_client):
    day = date.today()
    mocked_get_results = [
        {
            Keys.ACTIVITY_EVENT_ENTITIES: ["foo", "bar"],
            Keys.LAST_RESULT_SET: False,
            Keys.CONTINUATION_URI: "https://next-call-1",
        },
        {
            Keys.ACTIVITY_EVENT_ENTITIES: ["baz"],
            Keys.LAST_RESULT_SET: False,
            Keys.CONTINUATION_URI: "https://next-call-2",
        },
        {
            Keys.ACTIVITY_EVENT_ENTITIES: ["biz"],
            Keys.LAST_RESULT_SET: True,
            Keys.CONTINUATION_URI: None,
        },
    ]

    with patch.object(power_bi_client, "_get") as mocked_get:
        mocked_get.side_effect = mocked_get_results

        result = list(power_bi_client._activity_events(day=day))
        assert result == ["foo", "bar", "baz", "biz"]

        expected_calls = [
            call(endpoint=ENDPOINT_FACTORY.activity_events(day=day)),
            call(endpoint="https://next-call-1"),
            call(endpoint="https://next-call-2"),
        ]
        mocked_get.assert_has_calls(expected_calls)


def test_test_connection(power_bi_client):
    with patch.object(power_bi_client._auth, "refresh_token") as mock_refresh:
        power_bi_client.test_connection()
        mock_refresh.assert_called_once()
