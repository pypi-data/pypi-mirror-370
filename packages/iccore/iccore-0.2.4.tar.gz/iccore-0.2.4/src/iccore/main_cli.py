#!/usr/bin/env python3

"""
This is the main entrypoint for the iccore utility
"""

import argparse
import logging

from iccore.cli_utils import launch_common
import iccore.network.cli
import iccore.filesystem.cli
import iccore.version_control.cli


logger = logging.getLogger(__name__)


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        type=int,
        default=0,
        help="Dry run script - 0 can modify, 1 can read, 2 no modify - no read",
    )
    subparsers = parser.add_subparsers(required=True)

    iccore.network.cli.register(subparsers)
    iccore.filesystem.cli.register(subparsers)
    iccore.version_control.cli.register(subparsers)

    args = parser.parse_args()
    launch_common(args)
    args.func(args)


if __name__ == "__main__":
    main_cli()
