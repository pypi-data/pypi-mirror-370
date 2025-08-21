from pathlib import Path
import logging

from iccore.cli_utils import launch_common

from .filesystem import read_file, replace_in_files


logger = logging.getLogger(__name__)


def cli_replace_in_files(args):

    launch_common(args)

    search_term = read_file(args.search.resolve()).strip()
    replace_term = read_file(args.insert.resolve()).strip()

    target_dir = args.target.resolve()
    logger.info(
        "Replacing '%s' with '%s' in files in %s", search_term, replace_term, target_dir
    )
    count = replace_in_files(target_dir, search_term, replace_term, args.extension)
    logger.info("Replaced in %d files", count)


def register(subparsers):

    parser = subparsers.add_parser("filesystem")
    subparsers = parser.add_subparsers(required=True)

    replace_files_parser = subparsers.add_parser("replace_in_files")

    replace_files_parser.add_argument(
        "--target",
        type=Path,
        help="Path to the directory containing the files",
    )
    replace_files_parser.add_argument(
        "--search", type=Path, help="File containing the term to be replaced"
    )
    replace_files_parser.add_argument(
        "--insert", type=Path, help="File containing the term to be inserted"
    )
    replace_files_parser.add_argument(
        "--extension",
        type=str,
        default="",
        help="Only process files with this extension, if set",
    )

    replace_files_parser.set_defaults(func=cli_replace_in_files)
