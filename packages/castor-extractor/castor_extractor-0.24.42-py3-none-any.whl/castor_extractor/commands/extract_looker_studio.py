from argparse import ArgumentParser

from castor_extractor.utils import parse_filled_arguments  # type: ignore
from castor_extractor.visualization import looker_studio  # type: ignore


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--credentials",
        help="File path to Service Account credentials with Looker Studio access",
    )
    parser.add_argument(
        "-a",
        "--admin-email",
        help="Email of a Google Workspace user with admin access",
    )
    parser.add_argument(
        "-b",
        "--bigquery-credentials",
        help=(
            "Optional: file path to Service Account credentials with BigQuery access. "
            "This can be the same file path as for Looker Studio."
        ),
    )
    parser.add_argument(
        "--skip-view-activity-logs",
        action="store_true",
        default=False,
        help="Skips the extraction of activity logs",
    )
    parser.add_argument(
        "--users-file-path",
        help=(
            "Optional path to a JSON file with user email addresses "
            'as a list of strings (e.g. ["foo@bar.com", "fee@bar.com"]). '
            "If provided, only extracts assets owned by the specified users."
        ),
    )

    parser.add_argument("-o", "--output", help="Directory to write to")

    looker_studio.extract_all(**parse_filled_arguments(parser))
