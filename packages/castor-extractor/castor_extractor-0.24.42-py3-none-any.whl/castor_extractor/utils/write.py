import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

import pkg_resources

ENCODING = "utf8"
SUMMARY_FILENAME = "summary.json"

logger = logging.getLogger(__name__)


def timestamped_filename(filename: str, ts: int) -> str:
    """format file with a timestamp prefix"""
    return f"{ts}-{filename}"


def get_summary_filename(output_directory: str, ts: int) -> str:
    """return the summary filename"""
    filename = timestamped_filename(SUMMARY_FILENAME, ts)
    return os.path.join(output_directory, filename)


def get_output_filename(name: str, output_directory: str, ts: int) -> str:
    """return the output filename, including directory and timestamp prefix"""
    return os.path.join(output_directory, f"{ts}-{name}.json")


def write_json(filename: str, data: Any):
    """
    write the data to a json file at path filename
    """
    with open(filename, "w", encoding=ENCODING) as f:
        json.dump(data, f)
        logger.info(f"Wrote output file: {filename} ({f.tell()} bytes)")


def _current_version() -> str:
    """fetch the current version of castor extractor running"""
    packages = pkg_resources.require("castor-extractor")
    return str(packages[0].version)


def write_summary(output_directory: str, ts: int, **kwargs):
    """
    write a json file containing extraction session information
    """
    summary = get_output_filename("summary", output_directory, ts)
    write_json(
        summary,
        {
            "python_version": sys.version,
            "version": _current_version(),
            "executed_at": datetime.fromtimestamp(ts).isoformat(),
            **kwargs,
        },
    )


def get_summary_payload(client_info: dict, dt: datetime) -> dict:
    """
    return the payload to be stored in the summary file
    """
    return {
        **client_info,
        "executed_at": dt.isoformat(),
    }


def write_errors_logs(output_directory: str, ts: int, errors: list[str]):
    """
    write a json file logs from code execution
    """
    filename = get_output_filename("errors_logs", output_directory, ts)
    write_json(filename, errors)
