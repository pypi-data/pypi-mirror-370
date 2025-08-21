from pydantic import BaseModel


class GitlabToken(BaseModel, frozen=True):
    """
    A gitlab access token
    """

    value: str
    token_type: str = "PRIVATE-TOKEN"


class GitlabResource(BaseModel, frozen=True):
    """
    An addressable resource
    """

    name: str
    id: int


class GitlabReleaseAssetLink(BaseModel):
    """
    Link to a release asset
    """

    name: str
    base_url: str
    url: str = ""
    archive_name: str = ""
    link_type: str = "package"
    direct_asset_path: str = "/"

    def model_post_init(self, __context):
        self.url = f"{self.base_url}/{self.name}"
        if self.archive_name:
            self.direct_asset_path += f"{self.archive_name}/"
            self.direct_asset_path += self.name


class GitlabReleaseAssetCollection(BaseModel, frozen=True):
    """
    A collection of release assets
    """

    names: list[str] = []
    links: list[GitlabReleaseAssetLink] = []


class GitlabReleaseManifest(BaseModel):
    """
    A release manifest
    """

    project_version: str
    base_url: str
    assets: GitlabReleaseAssetCollection
    name: str = ""
    tag_name: str = ""
    ref: str = "master"

    def model_post_init(self, __context):
        self.name = f"Release {self.project_version}"
        self.tag_name = f"v{self.project_version}"
        self.assets.links.extend(
            [GitlabReleaseAssetLink(name=n, base_url=self.base_url)]
            for n in self.assets.names
        )


class GitlabRelease(BaseModel, frozen=True):
    """
    A gitlab release
    """

    manifest: GitlabReleaseManifest | None = None


class GitlabProject(GitlabResource, frozen=True):
    """
    A gitlab project
    """

    group_name: str = ""
    releases: list[GitlabRelease] = []


class GitlabGroup(GitlabResource, frozen=True):
    """
    A gitlab group
    """

    projects: list[GitlabProject] = []


class GitlabInstance(BaseModel):
    """
    A gitlab instance
    """

    url: str
    groups: list[GitlabGroup] = []
    api_url: str = ""

    def model_post_init(self, __context):
        self.api_url = f"{self.url}/api/v4"
