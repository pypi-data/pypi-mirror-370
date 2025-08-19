import pytest
from tuxmake.runtime import Runtime
from tuxbake.exceptions import TuxbakeParsingError
from pathlib import Path
import os
from tuxbake.models import OEBuild
from dataclasses import asdict
from unittest.mock import patch


def test_oebuild(oebuild_git_object):
    (
        oebuild,
        git_repo_1,
        git_repo_2,
        git_branch_1,
        git_branch_2,
        git_sha_1,
        git_sha_2,
        source_dir,
    ) = oebuild_git_object
    assert oebuild.git_trees[0].url == git_repo_1
    assert oebuild.git_trees[0].branch == git_branch_1
    assert oebuild.git_trees[1].url == git_repo_2
    assert oebuild.git_trees[1].branch == git_branch_2
    assert oebuild.git_trees[0].sha == git_sha_1
    assert oebuild.git_trees[1].sha == git_sha_2
    assert oebuild.src_dir == source_dir


def test_repo_init_oebuild(oebuild_repo_init_object):
    oebuild = oebuild_repo_init_object
    assert oebuild.repo.url == "https://gitlab.com/alok.ranjan1/test-project"
    assert oebuild.repo.branch == "main"
    assert oebuild.repo.manifest == "default.xml"


def test_do_cleanup(oebuild_repo_init_object):
    oebuild_obj = oebuild_repo_init_object
    oebuild_obj._runtime = Runtime.get(None)
    oebuild_obj.do_cleanup()


""" Test map for validation of all api arguments. can add or delete ..depending upon use case"""
test_map = {
    "envsetup": [None, 1],
    "targets": [None, 1],
    "distro": [1],
    "repo": [
        {"url": "", "branch": "main", "manifest": "default.xml"},
        {"url": 1, "branch": "main", "manifest": "default.xml"},
        {"url": "file://", "branch": "main", "manifest": "default.xml"},
        {"url": "git://" + "a" * 1020, "branch": "main", "manifest": "default.xml"},
        {
            "url": "https://gitlab.com/alok.ranjan1/test-project",
            "branch": None,
            "manifest": "default.xml",
        },
        {
            "url": "https://gitlab.com/alok.ranjan1/test-project",
            "branch": "main",
            "manifest": "default.txt",
        },
    ],
    "git_trees": [
        [{"url": "", "branch": "main", "ref": None, "sha": None}],
        [{"url": 1, "branch": "main", "ref": None, "sha": None}],
        [{"url": "file://", "branch": "main", "ref": None, "sha": None}],
        [{"url": "git://" + "a" * 1020, "branch": "main", "ref": None, "sha": None}],
        [
            {
                "url": "https://gitlab.com/alok.ranjan1/test-project",
                "branch": "main",
                "ref": 1,
                "sha": None,
            }
        ],
        [
            {
                "url": "https://gitlab.com/alok.ranjan1/test-project",
                "branch": "main",
                "ref": None,
                "sha": 1,
            }
        ],
        [
            {
                "url": "https://gitlab.com/alok.ranjan1/test-project",
                "branch": "main",
                "ref": "a" * 129,
                "sha": None,
            }
        ],
        [
            {
                "url": "https://gitlab.com/alok.ranjan1/test-project",
                "branch": "main",
                "ref": "?test",
                "sha": None,
            }
        ],
        [
            {
                "url": "https://gitlab.com/alok.ranjan1/test-project",
                "branch": "main",
                "ref": None,
                "sha": "test",
            }
        ],
    ],
    "container": ["unknown_container", "invalid_container", 1],
    "environment": ["test", {1: "test"}, {"test": 1}],
    "local_conf": ["conf", [1]],
    "bblayers_conf": ["bb_conf", [1]],
    "sstate_mirror": [1, 1.4],
    "dl_dir": [1],
}


def test_validate(oebuild_repo_init_object):
    # case - similar with repo obj as it has repo instead of git_trees
    oebuild_obj = asdict(oebuild_repo_init_object)
    OEBuild.validate(oebuild_obj)
    # handling all defined test in test_map
    sources = oebuild_obj["sources"]
    for key in test_map:
        if key in ["repo", "git_trees"]:
            if key == "repo":
                oebuild_obj["sources"]["git_trees"] = None
            else:
                oebuild_obj["sources"]["repo"] = None
            for test_case in test_map[key]:
                oebuild_obj["sources"][key] = test_case
                with pytest.raises(TuxbakeParsingError):
                    OEBuild.validate(oebuild_obj)
            oebuild_obj["sources"] = sources

        else:
            prev_val = oebuild_obj[key]
            for test_case in test_map[key]:
                oebuild_obj[key] = test_case
                with pytest.raises(TuxbakeParsingError):
                    OEBuild.validate(oebuild_obj)
            oebuild_obj[key] = prev_val

    with pytest.raises(TuxbakeParsingError):
        # case - when both repo and git_trees are not present
        oebuild_obj["sources"]["repo"] = None
        oebuild_obj["sources"]["git_trees"] = None
        OEBuild.validate(oebuild_obj)


def test_as_dict(oebuild_repo_init_object):
    data = oebuild_repo_init_object.as_dict()
    assert isinstance(data, dict)


def test_prepare(oebuild_repo_init_object):
    oebuild_obj = oebuild_repo_init_object
    oebuild_obj.local_manifest = None
    with patch.object(OEBuild, "__prepare__"):
        oebuild_obj.prepare()
    assert oebuild_obj._runtime == "null"
    assert oebuild_obj._runtime.source_dir == Path(oebuild_obj.src_dir)
    assert oebuild_obj._runtime.basename == "build"
    assert oebuild_obj._runtime.environment["MACHINE"] == oebuild_obj.machine
    assert oebuild_obj._runtime.environment["DISTRO"] == oebuild_obj.distro

    # reading extra_local.conf file from src dir
    file = Path(f"{os.path.abspath(oebuild_obj.src_dir)}/extra_local.conf")
    if file.exists():
        with open(file, "r") as f:
            data = f.read()

            # validating conf
            if oebuild_obj.dl_dir:
                assert oebuild_obj.dl_dir in data
            if oebuild_obj.sstate_mirror:
                assert oebuild_obj.sstate_mirror in data
                assert 'USER_CLASSES += "buildstats buildstats-summary"\n' in data
            if oebuild_obj.local_conf:
                for val in oebuild_obj.local_conf:
                    assert val in data

    # reading bblayers.conf file from src dir
    file = Path(f"{os.path.abspath(oebuild_obj.src_dir)}/bblayers.conf")
    if file.exists():
        with open(file, "r") as f:
            data = f.read()

            # validating bblayers_conf
            if oebuild_obj.bblayers_conf:
                for val in oebuild_obj.bblayers_conf:
                    assert val in data


def test_publish_artifacts(helpers, tmpdir_factory):
    from tuxbake.models import OEBuild

    temp_src_dir = tmpdir_factory.mktemp("openbmc")
    build_definition = {
        "src_dir": temp_src_dir,
        "distro": "openbmc-openpower",
        "artifacts": ["two.txt"],
        "artifacts_dir": "test-output",
        "build_dir": "build",
        "machine": "palmetto",
        "sources": {
            "git_trees": [
                {"url": "http://git.yoctoproject.org/git/poky"},
                {"url": "https://github.com/ndechesne/meta-qcom"},
            ]
        },
    }
    """ For openbmc builds """
    # setup bitbake-environment file
    deploy_dir = "openbmc/deploy"
    bitbake_env_dir = f"openbmc/{build_definition['build_dir']}"
    content_list = [
        {
            "filename": "bitbake-environment",
            "contents": f"DEPLOY_DIR={temp_src_dir}/{deploy_dir}",
        }
    ]
    helpers.setup_temp_workspace(temp_src_dir, content_list, bitbake_env_dir)
    # setup artifacts file to be copied
    content_list = [
        {"filename": "one.txt", "contents": "file one"},
        {"filename": "two.txt", "contents": "file two"},
    ]
    helpers.setup_temp_workspace(temp_src_dir, content_list, deploy_dir)
    oebuild_obj = OEBuild(**build_definition)
    oebuild_obj._runtime = Runtime.get(None)
    oebuild_obj._runtime.source_dir = Path(f"{temp_src_dir}/openbmc")
    # calling publish artifacts and artifacts will be published at 'artifacts_dir' inside our src_dir"
    oebuild_obj.publish_artifacts()
    published_artifacts = os.listdir(
        f"{temp_src_dir}/{build_definition['artifacts_dir']}"
    )
    assert len(published_artifacts) == 2
    assert "two.txt" in published_artifacts
    assert "bitbake-environment" in published_artifacts
    assert "one.txt" not in published_artifacts

    """ For Non-openbmc builds """
    # setup bitbake-environment file
    temp_src_dir = tmpdir_factory.mktemp("non-openbmc")
    deploy_dir = "build/deploy"
    bitbake_env_dir = build_definition["build_dir"]
    content_list = [
        {
            "filename": "bitbake-environment",
            "contents": f"DEPLOY_DIR={temp_src_dir}/{deploy_dir}",
        }
    ]
    helpers.setup_temp_workspace(temp_src_dir, content_list, bitbake_env_dir)
    # setup artifacts file to be copied
    content_list = [{"filename": "one.txt", "contents": "file one"}]
    helpers.setup_temp_workspace(temp_src_dir, content_list, deploy_dir)
    build_definition["distro"] = "test-distro"
    build_definition["src_dir"] = temp_src_dir
    build_definition["artifacts"] = []  # empty, Whole deploy_dir to be published
    oebuild_obj = OEBuild(**build_definition)
    oebuild_obj._runtime = Runtime.get(None)
    oebuild_obj._runtime.source_dir = Path(temp_src_dir)
    # calling publish artifacts and artifacts will be published at 'artifacts_dir' inside our src_dir"
    oebuild_obj.publish_artifacts()
    published_artifacts = os.listdir(
        f"{temp_src_dir}/{build_definition['artifacts_dir']}"
    )
    assert len(published_artifacts) == 2
    assert "one.txt" in published_artifacts
    assert "bitbake-environment" in published_artifacts
