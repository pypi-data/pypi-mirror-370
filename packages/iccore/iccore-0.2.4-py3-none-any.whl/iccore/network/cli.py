import os
from pathlib import Path
import logging

from iccore.cli_utils import launch_common

from .http_client import HttpClient

logger = logging.getLogger(__name__)


def download(args):

    launch_common(args)
    logger.info("Attempting to download from %s", args.url)

    headers = {args.token_header: args.token}

    http_client = HttpClient()
    http_client.download_file(args.url, args.download_dir, headers)


def register(subparsers):

    parser = subparsers.add_parser("network")

    subparsers = parser.add_subparsers(required=True)

    download_parser = subparsers.add_parser("download")

    download_parser.add_argument("url", type=str, help="Url to download")
    download_parser.add_argument(
        "--token", type=str, help="Optional auth token", default=""
    )
    download_parser.add_argument(
        "--token_header", type=str, help="Optional auth token header key", default=""
    )
    download_parser.add_argument(
        "--download_dir",
        type=Path,
        help="Directory to download to",
        default=Path(os.getcwd()),
    )
    download_parser.set_defaults(func=download)
