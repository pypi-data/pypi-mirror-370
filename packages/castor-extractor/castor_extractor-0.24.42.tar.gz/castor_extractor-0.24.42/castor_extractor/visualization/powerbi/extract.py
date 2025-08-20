import logging
from collections.abc import Iterable
from typing import Union

from ...utils import (
    OUTPUT_DIR,
    current_timestamp,
    deep_serialize,
    from_env,
    get_output_filename,
    write_json,
    write_summary,
)
from .assets import PowerBiAsset
from .client import PowerbiClient, PowerbiCredentials

logger = logging.getLogger(__name__)


def iterate_all_data(
    client: PowerbiClient,
) -> Iterable[tuple[PowerBiAsset, Union[list, dict]]]:
    for asset in PowerBiAsset:
        if asset in PowerBiAsset.optional:
            continue

        logger.info(f"Extracting {asset.name} from API")
        data = list(deep_serialize(client.fetch(asset)))
        yield asset, data
        logger.info(f"Extracted {len(data)} {asset.name} from API")


def extract_all(**kwargs) -> None:
    """
    Extract data from PowerBI REST API
    Store the output files locally under the given output_directory
    """
    _output_directory = kwargs.get("output") or from_env(OUTPUT_DIR)
    creds = PowerbiCredentials(**kwargs)
    client = PowerbiClient(creds)
    ts = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key.name.lower(), _output_directory, ts)
        write_json(filename, data)

    write_summary(_output_directory, ts)
