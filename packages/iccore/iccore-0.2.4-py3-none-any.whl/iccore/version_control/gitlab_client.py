"""
Client for interacting with the Gitlab API
"""

from pathlib import Path
import logging
import json

from iccore.network import HttpClient
from iccore.project import Milestone
from iccore.url_utils import Url
from iccore.serialization import read_yaml

from iccore.version_control import git
from .git import GitRepo, GitRemote, GitUser
from .gitlab import (
    GitlabInstance,
    GitlabToken,
    GitlabReleaseManifest,
    GitlabReleaseAssetCollection,
)


logger = logging.getLogger(__name__)


class GitlabClient:
    """
    Client for interacting with the Gitlab API
    """

    def __init__(
        self,
        instance: GitlabInstance | None = None,
        token: GitlabToken | None = None,
        user: GitUser | None = None,
        local_repo: GitRepo | None = None,
        http_client: HttpClient = HttpClient(),
    ) -> None:

        self.token = token
        self.instance = instance
        self.user = user
        self.local_repo = local_repo
        self.remote_initialized = False
        self.http_client: HttpClient = http_client

    def initialize_oath_remote(self, name: str = "oath_origin"):
        """
        Set up a git remote that uses oath authorization rather than
        e.g. SSH. This allows interaction with external repos
        on a CI runner.
        """

        err_msg = "Attempted to init oath remote with no "
        if not self.instance:
            raise RuntimeError(f"{err_msg} instance set")

        if not self.local_repo:
            raise RuntimeError(f"{err_msg} repo set")

        if not self.token:
            raise RuntimeError(f"{err_msg} token")

        url_prefix = f"https://oauth2:{self.token.value}"
        url = f"{url_prefix}@{self.instance.url}.git"
        git.add_remote(self.local_repo.path, GitRemote(name=name, url=url))

    def upload_release_asset(self, endpoint: str, token: GitlabToken, path: Path):
        """
        Upload a single release asset
        """

        logger.info("Uploading release asset %s, to %s", path, endpoint)

        headers = {token.token_type: token.value}
        response = self.http_client.upload_file(endpoint, path, headers)

        logger.info("Finished upload with response %s", response)

    def upload_release_manifest(
        self, endpoint: str, manifest: GitlabReleaseManifest, token: GitlabToken
    ):
        """
        Upload the manifest of release assets
        """

        logger.info("Uploading release manifest to %s", endpoint)

        headers = {token.token_type: token.value}
        response = self.http_client.post_json(endpoint, headers, manifest.model_dump())
        logger.info("Finished uploading manifest with response %s", response)

    def push_change(self, message: str, target_branch="main", remote_name="origin"):
        """
        Push a change to the specified remote
        """

        if not self.local_repo:
            return

        if not self.user:
            raise RuntimeError("Attempted to init oath remote with no user")

        git.set_user(self.local_repo.path, self.user)

        if not self.remote_initialized:
            self.initialize_oath_remote()
            self.remote_initialized = True

        git.add_all(self.local_repo.path)
        git.commit(self.local_repo.path, message)
        git.push(self.local_repo.path, remote_name, "HEAD", target_branch, "-o ci.skip")

    def set_ci_variable(self, endpoint: str, key: str, value: str, token: GitlabToken):
        """
        Set a Gitlab CI variable
        """

        logger.info("Setting CI variable %s", key)

        headers = {token.token_type: token.value}
        payload = f"value={value}"

        response = self.http_client.make_put_request(endpoint, headers, payload)

        logger.info("Finished setting CI variable with response %s", response)

    def get_latest_release(
        self, project_id: int, asset_name: str = "", download_path: Path = Path()
    ):
        """
        Get the latest release, optionally including assets
        """

        url = f"projects/{project_id}/releases"
        releases_json = self._make_request(url)
        if not releases_json:
            return None

        if not asset_name:
            return releases_json[0]["tag_name"]

        logger.info("Searching for release asset %s", asset_name)
        asset_url = ""
        for asset_link in releases_json[0]["assets"]["links"]:
            if asset_link["name"] == asset_name:
                asset_url = asset_link["url"]

        if not asset_url:
            logging.info("Didn't find named asset, returning")
            return releases_json[0]["tag_name"]

        logger.info("Found named asset at %s, attempting to download", asset_url)
        self._do_pre_request_checks()
        headers = self._get_request_headers()

        self.http_client.download_file(asset_url, download_path / asset_name, headers)
        return releases_json[0]["tag_name"]

    def get_latest_release_sources(self, project_url: str, download_path: Path) -> Path:
        """
        Download the latest release sources for the project
        """

        logger.info("Getting release sources for '%s':", project_url)

        project_id = self.get_project_id(project_url)

        releases = self.get_project_releases(project_id)
        if not releases:
            raise RuntimeError("Requested sources for project with no releases")

        latest_tag = releases[0]["tag_name"]
        project_name = project_url.split("/")[-1]
        asset_name = f"{project_name}-{latest_tag}.tar.gz"
        asset_url = ""
        for source_asset in releases[0]["assets"]["sources"]:
            if source_asset["format"] == "tar.gz":
                asset_url = source_asset["url"]

        if not asset_url:
            raise RuntimeError("Couldn't find sources in release assets")

        logger.info("Found release sources at %s, attempting to download", asset_url)
        self._do_pre_request_checks()
        headers = self._get_request_headers()

        self.http_client.download_file(asset_url, download_path / asset_name, headers)
        return download_path / asset_name

    def download_release_package(self):
        """
        Download a particular release package
        """

    def get_milestones(self, resource_id: int, resource_type: str) -> list[Milestone]:
        """
        List the project milestones
        """
        url = f"{resource_type}s/{resource_id}/milestones"
        milestones_json = self._make_request(url)
        milestones = [Milestone(**j) for j in milestones_json]
        return milestones

    def get_project_releases(self, project_id: int):
        return self._make_request(f"projects/{project_id}/releases")

    def get_project_id(self, path: str) -> int:
        # urllib.parse.urlencode(path)
        encoded = path.replace("/", "%2F")
        response = self._make_request(f"projects/{encoded}")
        return response["id"]

    def _do_pre_request_checks(self):
        if not self.instance:
            raise RuntimeError(
                "Attempted to make api request with no Gitlab instance set"
            )

    def _get_request_headers(self, token_is_bearer=False):
        headers = {}
        if self.token:
            if token_is_bearer:
                headers["Authorization"] = f"Bearer {self.token.value}"
            else:
                headers[self.token.token_type] = self.token.value
        return headers

    def _get_resolved_url(self, url: str) -> str:
        if self.instance:
            return f"{self.instance.api_url}/{url}"
        return url

    def _make_request(self, url: str):
        self._do_pre_request_checks()
        headers = self._get_request_headers(token_is_bearer=True)

        full_url = self._get_resolved_url(url)
        logger.info("Making request to %s", full_url)
        response = self.http_client.make_get_request(full_url, headers)
        return json.loads(response)


def get_milestones(
    resource_type: str, resource_id: int, url: str, token: str, token_type: str
) -> str:
    """
    Return the Gitlab milestones for the referenced project or group as
    a json string.
    """

    client = GitlabClient(
        GitlabInstance(url=url), GitlabToken(value=token, token_type=token_type)
    )

    milestones = client.get_milestones(resource_id, resource_type)
    return json.dumps([m.model_dump_json() for m in milestones], indent=4)


def get_latest_release(
    project_id: int,
    url: str,
    asset_name: str,
    download_dir: Path,
    token: str = "",
    token_type: str = "",
) -> str:
    """
    Fetch the latest release for the referenced project.
    Download the specified asset and return the version number.
    """

    client = GitlabClient(
        GitlabInstance(url=url), GitlabToken(value=token, token_type=token_type)
    )
    return client.get_latest_release(project_id, asset_name, download_dir)


def get_latest_release_by_url(
    url: Url,
    asset_name: str,
    download_dir: Path,
    token: str = "",
    token_type: str = "",
) -> str:
    """
    Fetch the latest release for the referenced project.
    Download the specified asset and return the version number.
    """

    client = GitlabClient(
        GitlabInstance(url=f"{url.scheme}://{url.netloc}"),
        GitlabToken(value=token, token_type=token_type),
    )
    project_id = client.get_project_id(url.path[1:])
    return client.get_latest_release(project_id, asset_name, download_dir)


def get_latest_release_sources(url: Url, download_dir: Path):

    client = GitlabClient(instance=GitlabInstance(url=f"{url.scheme}://{url.netloc}"))
    return client.get_latest_release_sources(
        url.path[1:], download_dir
    )  # avoid leading slash


def upload_release_assets(
    manifest_path: Path, source_path: Path, target: str, token: str, token_type: str
):

    gitlab_token = GitlabToken(value=token, token_type=token_type)

    client = GitlabClient()

    manifest = read_yaml(manifest_path)
    for asset in manifest["assets"]:
        source = Path(asset["source"])
        if "target" in asset:
            target_url = f"{target}/{asset['target']}"
        else:
            target_url = f"{target}/{source.name}"
        client.upload_release_asset(target_url, gitlab_token, source_path / source)


def upload_release_manifest(
    manifest_path: Path, endpoint: str, token: str, token_type: str
):

    client = GitlabClient()
    manifest = read_yaml(manifest_path)
    client.upload_release_manifest(
        endpoint,
        GitlabReleaseManifest(
            project_version="0.0", base_url="", assets=GitlabReleaseAssetCollection()
        ),
        GitlabToken(value=token, token_type=token_type),
    )
    print(manifest)
