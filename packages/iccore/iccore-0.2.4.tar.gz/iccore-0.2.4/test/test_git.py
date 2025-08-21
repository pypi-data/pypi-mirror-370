import os
import shutil

from iccore.version_control import GitRepo, GitUser, git
from iccore.filesystem import write_file_lines
from iccore.test_utils import get_test_output_dir


def test_git_repo():

    output_dir = get_test_output_dir()
    repo_dir = output_dir / "test_repo"
    os.makedirs(output_dir / "test_repo", exist_ok=True)

    user_in = GitUser(name="testuser", email="testuser@testdomain.com")
    git.init_repo(repo_dir)
    git.set_user(repo_dir, user_in)

    user = git.get_user(repo_dir)
    repo = GitRepo(**{"user": user, "path": repo_dir})
    assert repo.user.name == "testuser"

    write_file_lines(repo_dir / "test.txt", ["hello world"])
    git.add_all(repo_dir)
    git.commit(repo_dir, "my_commit")

    git.set_tag(repo_dir, "0.0.1")

    write_file_lines(repo_dir / "test2.txt", ["hello world, again"])
    git.add_all(repo_dir)
    git.commit(repo_dir, "my_commit2")

    git.increment_tag(repo_dir, field="patch", branch="master", check=True, push=False)
    latest_tag = git.get_latest_tag_on_branch(repo_dir)
    assert latest_tag == "0.0.2"

    shutil.rmtree(output_dir)
