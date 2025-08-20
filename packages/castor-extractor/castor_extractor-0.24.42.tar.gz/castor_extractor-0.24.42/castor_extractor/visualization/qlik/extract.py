import logging
from collections.abc import Iterable
from typing import Optional, Union

from ...utils import (
    OUTPUT_DIR,
    current_timestamp,
    deep_serialize,
    from_env,
    get_output_filename,
    write_json,
    write_summary,
)
from .assets import QlikAsset
from .client import QlikClient, QlikCredentials

logger = logging.getLogger(__name__)


def iterate_all_data(
    client: QlikClient,
) -> Iterable[tuple[QlikAsset, Union[list, dict]]]:
    """Iterate over the extracted data from Qlik"""

    logger.info("Extracting CONNECTIONS from REST API")
    connections = client.fetch(QlikAsset.CONNECTIONS)
    yield QlikAsset.CONNECTIONS, deep_serialize(connections)

    logger.info("Extracting SPACES from REST API")
    spaces = client.fetch(QlikAsset.SPACES)
    yield QlikAsset.SPACES, deep_serialize(spaces)

    logger.info("Extracting USERS from REST API")
    users = client.fetch(QlikAsset.USERS)
    yield QlikAsset.USERS, deep_serialize(users)

    logger.info("Extracting APPS from REST API")
    apps = client.fetch(QlikAsset.APPS)
    yield QlikAsset.APPS, deep_serialize(apps)

    logging.info("Extracting LINEAGE data from REST API")
    lineage = client.fetch(QlikAsset.LINEAGE, apps=apps)
    yield QlikAsset.LINEAGE, deep_serialize(lineage)

    logging.info("Extracting MEASURES data from JSON-RPC API")
    measures = client.fetch(QlikAsset.MEASURES, apps=apps)
    yield QlikAsset.MEASURES, deep_serialize(measures)


def extract_all(
    except_http_error_statuses: Optional[list[int]] = None, **kwargs
) -> None:
    """
    Extract data from Qlik REST API
    Store the output files locally under the given output_directory
    """

    credentials = QlikCredentials(**kwargs)
    _output_directory = kwargs.get("output") or from_env(OUTPUT_DIR)

    client = QlikClient(
        credentials=credentials,
        except_http_error_statuses=except_http_error_statuses,
    )

    ts = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key.name.lower(), _output_directory, ts)
        write_json(filename, data)

    write_summary(_output_directory, ts, base_url=credentials.base_url)
