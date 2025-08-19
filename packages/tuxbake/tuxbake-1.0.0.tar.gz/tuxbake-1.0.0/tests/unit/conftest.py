import os
import subprocess
import sys
import pytest
import yaml

# TODO this should not be needed if the tuxmake RPM manages to provide a public
# Python module that is not tied to a specific Python version
sys.path.append("/usr/share/tuxmake")
from tuxmake.runtime import Runtime


@pytest.fixture
def git_build_definition():
    return """
sources:
  git_trees:
    - url: http://git.yoctoproject.org/git/poky
      branch: main
    - url: https://github.com/ndechesne/meta-qcom
      branch: main

src_dir: tmp/src
build_dir: test/build
container: ubuntu-20.04
envsetup: poky/oe-init-build-env
distro: poky
machine: dragonboard-845c
targets:
  - core-image-minimal
bblayers_conf:
  - BBLAYERS += "../meta-qcom/"
environment: {}
local_manifest: tests/unit/test.xml
pinned_manifest: ""
sstate_mirror: test_sstate
dl_dir: test_dl_dir
runtime: ""
"""


@pytest.fixture
def repo_build_definition():
    return """
sources:
  repo:
    url: https://gitlab.com/alok.ranjan1/test-project
    branch: main
    manifest: default.xml

src_dir: tmp/src
build_dir: test/build
container: ubuntu-20.04
envsetup: poky/oe-init-build-env
distro: poky
machine: dragonboard-845c
targets:
  - core-image-minimal
local_conf:
  - PREFERRED_PROVIDER_virtual/kernel = "linux-generic-mainline"
  - PREFERRED_VERSION_linux-generic-mainline = "git%"
  - SRCREV_kernel_hikey = "1d1df41c5a33359a00e919d54eaebfb789711fdc"
  - SRCREV_kernel_juno = "99613159ad749543621da8238acf1a122880144e"
  - SRCREV_ltp_hikey = "9b0740b72622f56c4d1909e2fdf38e948cf85b53"
  - PREFERRED_VERSION_ltp = "20210927+git%"
bblayers_conf:
  - BBLAYERS += "../meta-qcom/"
environment:
  TEMPLATECONF: ../oniro/flavours/linux
local_manifest: tests/unit/test.xml
pinned_manifest: ""
sstate_mirror: test_sstate
dl_dir: test_dl_dir
runtime: ""
"""


class Helpers:
    """Generic utility functions."""

    @staticmethod
    def setup_git(git_path):
        """
        Create a repo at git_path with two files and one commit.
        """
        files = [
            {
                "filename": "one",
                "contents": "The nice thing about standards is that you have so many to choose from.",
            },
            {"filename": "two", "contents": "☁️🐧☁️"},
        ]
        for f in files:
            with open(os.path.join(git_path, f["filename"]), "w") as h:
                h.write(f["contents"])
        subprocess.check_call(["git", "init"], cwd=git_path)
        subprocess.check_call(["git", "add", "."], cwd=git_path)
        subprocess.check_call(
            ["git", "config", "--local", "user.name", '"pytest ci"'], cwd=git_path
        )
        subprocess.check_call(
            ["git", "config", "--local", "user.email", '"test@email.com"'], cwd=git_path
        )
        subprocess.check_call(["git", "commit", "-m", '"Initial commit"'], cwd=git_path)

    @staticmethod
    def get_branch(path):
        """Get branch name from some repo at path"""
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path
            )
            .strip()
            .decode("utf-8")
        )

    @staticmethod
    def get_sha(path):
        """Get first commit hash from some repo at path"""
        return (
            subprocess.check_output(
                ["git", "rev-list", "--max-parents=0", "HEAD"], cwd=path
            )
            .strip()
            .decode("utf-8")
        )

    @staticmethod
    def setup_temp_workspace(src_dir, content_list, path_suffix=""):
        """THis function creates a temporary workspace folder with some files in it with the respective name and contents provided in content List"""
        # @param -> path_suffix: recursive path folder if needed
        # @param -> content_list: expects a list of objects with keys filename and contents to be written in that file
        path_with_suffix = os.path.join(src_dir, path_suffix)
        os.makedirs(path_with_suffix, exist_ok=True)
        for f in content_list:
            with open(os.path.join(path_with_suffix, f["filename"]), "w") as h:
                h.write(f["contents"])
        return path_with_suffix


@pytest.fixture
def helpers():
    """Provide a helpers fixture so it's available to all tests."""
    return Helpers


@pytest.fixture()
def oebuild_git_object(helpers, tmpdir_factory, git_build_definition):
    from tuxbake.models import OEBuild

    build_definition = yaml.safe_load(git_build_definition)
    git_repo_1 = tmpdir_factory.mktemp("git_1")
    git_repo_2 = tmpdir_factory.mktemp("git_2")
    helpers.setup_git(git_repo_1)
    helpers.setup_git(git_repo_2)
    git_branch_1 = helpers.get_branch(git_repo_1)
    git_branch_2 = helpers.get_branch(git_repo_2)
    git_sha_1 = helpers.get_sha(git_repo_1)
    git_sha_2 = helpers.get_sha(git_repo_2)
    build_definition["sources"]["git_trees"][0]["url"] = f"{git_repo_1}"
    build_definition["sources"]["git_trees"][1]["url"] = f"{git_repo_2}"
    build_definition["sources"]["git_trees"][0]["branch"] = git_branch_1
    build_definition["sources"]["git_trees"][1]["branch"] = git_branch_2
    build_definition["sources"]["git_trees"][0]["sha"] = git_sha_1
    build_definition["sources"]["git_trees"][1]["sha"] = git_sha_2
    source_dir = tmpdir_factory.mktemp("src")
    build_definition["src_dir"] = source_dir

    oebuild = OEBuild(**build_definition)
    return (
        oebuild,
        git_repo_1,
        git_repo_2,
        git_branch_1,
        git_branch_2,
        git_sha_1,
        git_sha_2,
        source_dir,
    )


@pytest.fixture()
def oebuild_repo_init_object(repo_build_definition):
    from tuxbake.models import OEBuild

    build_definition = yaml.safe_load(repo_build_definition)
    oebuild = OEBuild(**build_definition)
    return oebuild


@pytest.fixture()
def metadata_obj(oebuild_repo_init_object):
    from tuxbake.metadata import Metadata

    oebuild = oebuild_repo_init_object
    # prepare runtime
    runtime = Runtime.get(oebuild.runtime)
    oebuild._runtime = runtime
    return Metadata(oebuild)
