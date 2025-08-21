from iccore.version_control import gitlab


def test_gitlab_models():

    asset_link = gitlab.GitlabReleaseAssetLink(
        name="my_asset", base_url="http://example.com", archive_name="my_archive"
    )
    assert asset_link.url == "http://example.com/my_asset"
    assert asset_link.direct_asset_path == "/my_archive/my_asset"

    assets = gitlab.GitlabReleaseAssetCollection()
    release_manifest = gitlab.GitlabReleaseManifest(
        project_version="1.2.3", base_url="http://example.com", assets=assets
    )
    assert release_manifest.name == "Release 1.2.3"
