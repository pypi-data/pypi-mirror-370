import pytest
import requests
from tuxbake.exceptions import TuxbakeRunCmdError
import os
from unittest.mock import patch, Mock


def test_run_cmd(tmp_path):
    from tuxbake.utils import run_cmd

    cmd = "ls nofile".split()
    run_cmd(cmd, src_dir=tmp_path, fail_ok=True)
    with pytest.raises(TuxbakeRunCmdError):
        run_cmd(cmd, src_dir=tmp_path, fail_ok=False)


def test_git_init(oebuild_git_object, tmpdir_factory):
    """
    oebuild_git_object is a gobal fixture defined in conftest file.
    and we are receiving it as a tuple object (oebuild_obj, src_path_1, src_path_2, git_branch_1, git_branch_2, src_dir)
    """
    from tuxbake.utils import git_init

    oebuild_object = oebuild_git_object[0]
    src_dir = oebuild_object.src_dir
    with patch("tuxbake.utils.run_cmd") as run_cmd:
        git_init(oebuild_object, src_dir)
        assert run_cmd.call_count == 12

    # case when only url is present and not branch
    for git_obj in oebuild_object.git_trees:
        # adding ref also , so as to cover ref if block
        git_obj.ref = f"refs/heads/{git_obj.branch}"
        git_obj.branch = None

    temp_src2 = tmpdir_factory.mktemp("src2")
    with patch("tuxbake.utils.run_cmd") as run_cmd:
        git_init(oebuild_object, temp_src2)
        assert run_cmd.call_count == 12

    with patch("tuxbake.utils.run_cmd", side_effect=TuxbakeRunCmdError) as run_cmd:
        with pytest.raises((TuxbakeRunCmdError, FileNotFoundError)):
            git_init(oebuild_object, "/some/wrong/folder")

    # check the retries
    for git_obj in oebuild_object.git_trees:
        git_obj.branch = None
        git_obj.sha = None
        git_obj.ref = None
    # git_init(oebuild_object, temp_src2)
    with patch("tuxbake.utils.run_cmd") as mock_run_cmd:
        with patch("tuxbake.utils.git_get_sha") as patch_get_git_sha:
            patch_get_git_sha.return_value = None
            with pytest.raises(TuxbakeRunCmdError):
                git_init(oebuild_object, temp_src2)
                assert mock_run_cmd.call_count == 3


def test_repo_init(oebuild_repo_init_object, tmpdir_factory, tmpdir):
    from tuxbake.utils import repo_init

    oebuild = oebuild_repo_init_object
    url, branch = oebuild.repo.url, oebuild.repo.branch
    temp_src = tmpdir_factory.mktemp("test_repo_init")

    # case - checking with all right parameters ( url, branch, manifest)
    with patch("tuxbake.utils.run_cmd") as run_cmd:
        repo_init(oebuild, temp_src)
        assert run_cmd.call_count == 3

    # case - checking with all right parameters with a tag.
    with patch("tuxbake.utils.run_cmd") as run_cmd:
        oebuild.repo.branch = "refs/tags/1.0.0"
        repo_init(oebuild, temp_src)
        assert run_cmd.call_count == 3

    # case - checking with wrong branch name
    oebuild.repo.branch = "some-wrong-branch"
    with patch("tuxbake.utils.run_cmd", side_effect=TuxbakeRunCmdError):
        with pytest.raises(TuxbakeRunCmdError):
            repo_init(oebuild, temp_src)

    oebuild.repo.branch = branch

    # case - checking with wrong url
    oebuild.repo.url = "https://gitlab.com/some/wrong/url/=?"
    with patch("tuxbake.utils.run_cmd", side_effect=TuxbakeRunCmdError):
        with pytest.raises(TuxbakeRunCmdError):
            repo_init(oebuild, temp_src)
    oebuild.repo.url = url

    # case - checking with local manifest file
    manifest_path = oebuild.local_manifest
    local_manifest = os.path.abspath(manifest_path)
    with patch("tuxbake.utils.run_cmd") as run_cmd:
        repo_init(oebuild, tmpdir, local_manifest)
        assert run_cmd.call_count == 5

    # case - checking with wrong manishfest file name
    oebuild.repo.manifest = "some-wrong-name.xml"
    with patch("tuxbake.utils.run_cmd", side_effect=TuxbakeRunCmdError):
        with pytest.raises(TuxbakeRunCmdError):
            repo_init(oebuild, temp_src)

    # check the retry
    # wrong manifest, will raise TuxbakeRunCmdError
    oebuild.repo.manifest = "some-wrong-name.xml"
    with patch(
        "tuxbake.utils.run_cmd", side_effect=TuxbakeRunCmdError
    ) as patch_run_cmd:
        with pytest.raises(TuxbakeRunCmdError):
            repo_init(oebuild, temp_src)
            assert patch_run_cmd.call_count == 3


def test_find_bitbake_env():
    from tuxbake.utils import find_bitbake_env

    path = os.path.abspath("tests/unit/bitbake-environment")
    assert find_bitbake_env(path, "DL_DIR")
    with pytest.raises(AssertionError):
        assert find_bitbake_env(path, "DUMMY_VAR")

    # Bitbake environment doesn't exists
    path = os.path.abspath("tests/bitbake-environment")
    assert find_bitbake_env(path, "DL_DIR") is None


def test_handle_log(capsys, oebuild_git_object):
    from tuxbake.utils import handle_log, git_init

    logs_list = ["test", b"test-check-out", b"test-check-err"]
    handle_log(logs_list)
    out, err = capsys.readouterr()
    assert "test-check-err" in err

    with capsys.disabled():
        oebuild_object = oebuild_git_object[0]
        src_dir = oebuild_object.src_dir
        git_init(oebuild_object, src_dir)

        assert os.path.exists(f"{src_dir}/fetch.log")
        with open(f"{src_dir}/fetch.log") as f:
            data = f.readline()
            assert "INFO - Running cmd:" in data


def test_copy_artifacts(tmpdir):
    from tuxbake.utils import copy_artifacts

    artifacts_path_list = ["tests/unit/conftest.py", "tests/unit/test_argparse.py"]
    copy_artifacts(artifacts_path_list, tmpdir)

    artifacts = os.listdir(tmpdir)
    assert len(artifacts) == 2
    assert "conftest.py" in artifacts
    assert "test_argparse.py" in artifacts

    artifacts_path_list = [1, 2, None]
    with pytest.raises(TuxbakeRunCmdError):
        copy_artifacts(artifacts_path_list, tmpdir)
    artifacts = os.listdir(tmpdir)
    assert len(artifacts) == 0


def test_get_filtered_paths():
    from tuxbake.utils import get_filtered_paths

    path = os.path.abspath("tests/unit/")
    artifacts = [
        "../../tuxbake/__init__.py",
        "test_utils.py",
        "../../tuxbake.spec",
        "test_build.py",
    ]
    filtered_artifacts = get_filtered_paths(artifacts, path)
    assert len(filtered_artifacts) == 2
    assert os.path.abspath("tests/unit/test_utils.py") in filtered_artifacts
    assert os.path.abspath("tests/unit/test_build.py") in filtered_artifacts

    # if path is None
    filtered_artifacts = get_filtered_paths(artifacts, None)
    assert len(filtered_artifacts) == 0

    # if artifacts is empty
    filtered_artifacts = get_filtered_paths([], path)
    assert len(filtered_artifacts) == 0


def test_download_file(tmp_path, repo_build_definition):
    from tuxbake.utils import download_file

    url = "https://www.example.com/file/definition.yaml"
    dest = tmp_path / "raw.txt"
    req_mock = Mock(text="hello")

    # case: successful response
    req_mock.status_code = 200
    with patch("requests.get") as request:
        request.return_value = req_mock
        assert download_file(url, dest) == "hello"
        assert dest.read_text() == "hello"
    request.assert_called_once_with(url)

    # case: Unsuccessful response
    req_mock.reset_mock()
    req_mock.status_code = 400
    req_mock.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=req_mock
    )
    with patch("requests.get") as request:
        request.return_value = req_mock
        with pytest.raises(SystemExit):
            download_file(url, dest)

    request.assert_called_once_with(url)
