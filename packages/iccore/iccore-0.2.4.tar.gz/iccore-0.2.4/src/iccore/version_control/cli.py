import logging
import os
from pathlib import Path

from iccore.serialization import write_json
from iccore.filesystem import write_file
from iccore.version_control import git

from .gitlab_client import (
    get_latest_release,
    get_milestones,
    upload_release_assets,
    upload_release_manifest,
)

logger = logging.getLogger(__name__)


def get_milestones_cli(args):

    logger.info("Fetching milestones for %s %s", args.resource_type, args.resource_id)

    output_json = get_milestones(
        args.resource_type, args.resource_id, args.url, args.token, args.token_type
    )

    if args.output:
        write_json(output_json, args.output)
    else:
        print(output_json)

    logger.info("Finished fetching milestones")


def register_milestones(subparsers):

    parser = subparsers.add_parser("milestone")
    parser.add_argument(
        "resource_id", type=int, help="Id of the group or project being queried"
    )
    parser.add_argument(
        "--resource_type",
        type=str,
        default="project",
        help="Whether to query 'project' or 'group' milestones",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Path to output, if not given the output is dumped to terminal",
    )
    parser.set_defaults(func=get_milestones_cli)


def get_latest_release_cli(args):

    logger.info("Getting latest release for project %s", args.project_id)

    version = get_latest_release(
        args.project_id,
        args.url,
        args.token,
        args.token_type,
        args.asset_name,
        args.download_dir,
    )

    if version:
        print(version)

    logger.info("Finished getting latest release")


def register_latest_release(subparsers):

    parser = subparsers.add_parser("latest_release")
    parser.add_argument("project_id", type=int, help="Id of the project being queried")
    parser.add_argument(
        "--asset_name", type=str, help="Name of a release asset to download", default=""
    )
    parser.add_argument(
        "--download_dir",
        type=Path,
        help="Directory to download release assets to",
        default=Path(os.getcwd()),
    )
    parser.set_defaults(func=get_latest_release_cli)


def upload_release_manifest_cli(args):
    upload_release_manifest(
        args.manifest_path.resolve(),
        args.tartget_path.resolve(),
        args.token,
        args.token_type,
    )


def register_upload_release_manifest(subparsers):

    parser = subparsers.add_parser("upload_release_manifest")
    parser.add_argument(
        "--manifest_path",
        type=Path,
        help="Path to the release manifest",
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default="",
        help="Upload endpoint",
    )
    parser.add_argument(
        "--token",
        type=str,
        default="",
        help="Access token for the Gitlab resource - if required",
    )
    parser.add_argument(
        "--token_type",
        type=str,
        help="Type of token - corresponding to the header key in http requests",
        default="PRIVATE-TOKEN",
    )
    parser.set_defaults(func=upload_release_manifest_cli)


def upload_release_assets_cli(args):
    upload_release_assets(
        args.manifest_path.resolve(),
        args.source_path.resolve(),
        args.target_path,
        args.token,
        args.token_type,
    )


def register_upload_release_assets(subparsers):

    parser = subparsers.add_parser("upload_release_assets")
    parser.add_argument(
        "--manifest_path",
        type=Path,
        help="Path to the release manifest",
    )
    parser.add_argument(
        "--source_path",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to asset sources",
    )
    parser.add_argument(
        "--target_path",
        type=str,
        default="",
        help="Path to asset targets",
    )
    parser.add_argument(
        "--token",
        type=str,
        default="",
        help="Access token for the Gitlab resource - if required",
    )
    parser.add_argument(
        "--token_type",
        type=str,
        help="Type of token - corresponding to the header key in http requests",
        default="PRIVATE-TOKEN",
    )
    parser.set_defaults(func=upload_release_assets_cli)


def get_git_info(args):

    repo = git.get_repo_info(args.repo_dir.resolve())
    repo_json = repo.model_dump_json(indent=4)
    write_file(args.output_path.resolve(), repo_json)


def register_gitlab(subparsers):
    parser = subparsers.add_parser("gitlab")

    parser.add_argument(
        "--token",
        type=str,
        default="",
        help="Access token for the Gitlab resource - if required",
    )
    parser.add_argument(
        "--token_type",
        type=str,
        help="Type of token - corresponding to the header key in http requests",
        default="PRIVATE-TOKEN",
    )
    parser.add_argument(
        "--url",
        type=str,
        help="URL for the Gitlab repo instance",
        default="https://git.ichec.ie",
    )

    gitlab_subparsers = parser.add_subparsers(required=True)
    register_milestones(gitlab_subparsers)
    register_latest_release(gitlab_subparsers)
    register_upload_release_assets(gitlab_subparsers)
    register_upload_release_manifest(gitlab_subparsers)


def register_git(subparsers):

    parser = subparsers.add_parser("git")
    git_subparsers = parser.add_subparsers(required=True)

    info_subparser = git_subparsers.add_parser("info")
    info_subparser.add_argument(
        "--repo_dir", type=Path, default=Path(os.getcwd()), help="Path to the repo"
    )
    info_subparser.add_argument(
        "--output_path",
        type=Path,
        default=Path(os.getcwd()) / "repo_info.json",
        help="Path to the output",
    )
    info_subparser.set_defaults(func=get_git_info)


def register(subparsers):

    register_gitlab(subparsers)
    register_git(subparsers)
