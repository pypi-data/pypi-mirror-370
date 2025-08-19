import logging

from .....utils import SafeMode, safe_mode
from .constants import MEASURES_SESSION_PARAMS, JsonRpcMethod
from .credentials import QlikCredentials
from .error import (
    AccessDeniedError,
    AppSizeExceededError,
    PersistenceReadFailedError,
    QlikResponseKeyError,
)
from .json_rpc import JsonRpcClient
from .websocket import open_websocket

logger = logging.getLogger(__name__)


def _handle(response: dict) -> int:
    """
    Returns the object Handle from the response payload, or raises an error
    if one of the keys can't be found
    """
    try:
        return response["result"]["qReturn"]["qHandle"]
    except KeyError:
        raise QlikResponseKeyError(
            f"Could not fetch handle from response {response}"
        )


def _measure(response: dict) -> list:
    """
    Returns the measure from the response payload, or raises a custom error
    if one of the keys can't be found
    """
    try:
        return response["result"]["qLayout"]["qMeasureList"]["qItems"]
    except KeyError:
        raise QlikResponseKeyError(
            f"Could not fetch measure from response {response}"
        )


def _list_measures(client: JsonRpcClient, app_id: str) -> list:
    """
    Executes JSON-RPC messaging sequence to retrieve the list of measures
    for a given source

    references:
        - https://community.qlik.com/t5/Integration-Extension-APIs/How-to-ask-for-a-list-of-dimensions-and-measures-in-Qlik-Engine/td-p/1412156
        - https://help.qlik.com/en-US/sense-developer/May2021/Subsystems/EngineAPI/Content/Sense_EngineAPI/GenericObject/overview-generic-object.htm
    """
    response = client.send_message(
        method=JsonRpcMethod.OPEN_DOC,
        params=[app_id],
    )
    app_handle = _handle(response)

    response = client.send_message(
        method=JsonRpcMethod.CREATE_SESSION_OBJECT,
        handle=app_handle,
        params=list(MEASURES_SESSION_PARAMS),
    )
    session_handle = _handle(response)

    response = client.send_message(
        method=JsonRpcMethod.GET_LAYOUT,
        handle=session_handle,
    )
    return _measure(response)


class EngineApiClient:
    """
    Engine API client is responsible to send the sequence of messages to
    get measures using JsonRpcClient and websocket connection.
    """

    def __init__(self, credentials: QlikCredentials):
        self.credentials = credentials
        self._safe_mode = SafeMode(
            exceptions=(
                AccessDeniedError,
                AppSizeExceededError,
                PersistenceReadFailedError,
                QlikResponseKeyError,
            ),
            max_errors=float("inf"),
        )

    def measures(self, app_id: str) -> list:
        """
        Opens a websocket and pass it to a JsonRpcClient to return the list
        of measures scoped on an app_id.
        """

        @safe_mode(self._safe_mode, default=list)
        def _call(client: JsonRpcClient, app_id_: str) -> list:
            return _list_measures(client, app_id_)

        with open_websocket(
            app_id=app_id,
            server_url=self.credentials.base_url,
            api_key=self.credentials.api_key,
        ) as websocket:
            json_rpc_client = JsonRpcClient(websocket=websocket)
            return _call(json_rpc_client, app_id)
