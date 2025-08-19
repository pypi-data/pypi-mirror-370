import logging
from argparse import ArgumentParser

from castor_extractor.utils import parse_filled_arguments  # type: ignore
from castor_extractor.visualization import powerbi  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main():
    parser = ArgumentParser()

    parser.add_argument("-t", "--tenant_id", help="PowerBi tenant ID")
    parser.add_argument("-c", "--client_id", help="PowerBi client ID")
    parser.add_argument("-s", "--secret", help="PowerBi password")
    parser.add_argument(
        "-sc",
        "--scopes",
        help="PowerBi scopes, optional",
        nargs="*",
    )
    parser.add_argument("-o", "--output", help="Directory to write to")
    parser.add_argument("-l", "--login_url", help="Login url (Optional)")
    parser.add_argument("-a", "--api_base", help="REST API base (Optional)")

    powerbi.extract_all(**parse_filled_arguments(parser))
