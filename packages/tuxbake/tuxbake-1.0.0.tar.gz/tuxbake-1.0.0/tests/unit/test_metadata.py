import os
import json
import pytest
from unittest.mock import patch, MagicMock
from tuxbake.exceptions import UnsupportedMetadata
from tuxbake import __version__


def test_run_command():
    from tuxbake.metadata import run_command

    cmd = "echo hello".split()
    out = run_command(cmd, None)
    assert out == "hello"

    # case: Exception
    cmd = "catt abc.yaml".split()
    out = run_command(cmd, None)
    assert out is None


def test_collect(metadata_obj, tmp_path):
    from tuxbake.metadata import Metadata

    metadata_obj.src_dir = tmp_path
    with patch.object(Metadata, "generate_meta_dict"):
        with patch.object(Metadata, "free_disk_space"):
            with patch.object(Metadata, "get_git_info") as patch_git_info:
                patch_git_info.return_value = {}
                metadata_obj.collect()
    with open(f"{metadata_obj.src_dir}/metadata.json", "r") as f:
        data = json.loads(f.read())
        assert data["tuxbake"]["version"] == __version__


def test_get_runtime_info(metadata_obj):
    # update runtime
    assert metadata_obj.get_runtime_info() == {}


def test_save_metadata(metadata_obj, tmp_path):
    metadata_obj.metadata = {"a": {"key_1": "value_1", "key_2": "value_2"}}
    metadata_obj.src_dir = tmp_path
    metadata_obj.save_metadata()
    metadata = json.load(open(f"{tmp_path}/metadata.json"))
    assert metadata == metadata_obj.metadata


def test_meta_files(metadata_obj):
    available_meta_files = ["hardware", "os", "resources", "tools", "uname"]
    meta_files = metadata_obj.meta_files()
    assert sorted(meta_files) == available_meta_files


def test_generate_meta_dict(metadata_obj, tmpdir_factory):
    def prepare_ini_file(ini_data):
        # prepare a test.ini file with provided ini data
        # at temp location and return its path
        temp_dir = tmpdir_factory.mktemp("temp")
        ini_file = temp_dir / "test.ini"
        ini_file.write_text(ini_data, encoding="utf-8")
        return temp_dir

    ini_data = f"[types]\ncores=str\n\n[commands]\ncores=nproc"
    temp_dir = prepare_ini_file(ini_data)
    metadata_obj.basedir = temp_dir
    metadata_obj.files = ["test"]
    build_dir = tmpdir_factory.mktemp("build_dir")
    metadata_obj.build_dir = build_dir
    mock = MagicMock()
    mock.run_cmd.return_value = {"test": {"cores": "8"}}
    metadata_obj.runtime = mock
    with patch("shutil.copy"):
        result = metadata_obj.generate_meta_dict()
        assert result == {}

    # test exception ( without 'commands' )
    ini_data = f"[types]\ncores=str\n\n"
    temp_dir = prepare_ini_file(ini_data)
    metadata_obj.basedir = temp_dir
    metadata_obj.files = ["test"]
    with pytest.raises(UnsupportedMetadata) as msg:
        metadata_obj.generate_meta_dict()
    assert str(msg.value) == "'commands' is required in 'test.ini' file"


def test_replace_placeholders(metadata_obj):
    key = "{build_dir} placeholder check"
    value = metadata_obj.replace_placeholders(key)
    abs_path = os.path.abspath(metadata_obj.oebuild.build_dir)
    assert value == f"{abs_path} placeholder check"


def test_read_json(metadata_obj):
    # case: empty metadata json
    result = metadata_obj.read_json(None)
    assert result == {}
    # case: with 'test_key' value of type 'int'
    metadata_obj.types["test_key"] = eval("int")
    metadata_json = '{"a": {"test_key": "8"}}'
    result = metadata_obj.read_json(metadata_json)
    assert type(result["a"]["test_key"]) == int

    # case: JSONDecodeError exception
    result = metadata_obj.read_json("invalid json")
    assert result == {"invalid_metadata": "invalid json"}


def test_cast(metadata_obj):
    metadata_obj.types = {"nproc": eval("int")}
    val = metadata_obj.cast("nproc", "8")
    # int type
    assert type(val) == int
    assert val == 8


def test_free_disk_space(metadata_obj):
    metadata = metadata_obj
    with patch("shutil.disk_usage") as disk_usage:
        mock_disk_usage = MagicMock()
        mock_disk_usage.free = pow(2, 20) * 35
        disk_usage.return_value = mock_disk_usage
        assert metadata.free_disk_space() == 35


def test_get_git_info(oebuild_repo_init_object, oebuild_git_object):
    from tuxbake.metadata import Metadata

    oebuild = oebuild_repo_init_object
    # mock runtime
    runtime = MagicMock()
    runtime.source_dir = "test"
    oebuild._runtime = runtime
    metadata = Metadata(oebuild)
    # case: repo check
    with patch.object(Metadata, "meta_files") as files:
        files.return_value = []
        with patch("tuxbake.metadata.run_command") as run_cmd:
            metadata.get_git_info()
            assert run_cmd.call_count == 3

    # case: git check
    oebuild, repo1, *_ = oebuild_git_object
    # mock runtime
    runtime = MagicMock()
    runtime.source_dir = "test"
    oebuild._runtime = runtime
    metadata = Metadata(oebuild)
    # at path: repo1
    metadata.src_dir = repo1
    with patch("os.path.basename", side_effect=lambda x: ""):
        with patch("tuxbake.metadata.run_command") as run_cmd:
            metadata.get_git_info()
            assert run_cmd.call_count == 6  # 2 git repo, so 3*2 run_cmd calls
