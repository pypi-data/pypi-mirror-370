import argparse
import pytest
import os
from unittest.mock import patch


def test_setup_parser(tmp_path, git_build_definition):
    from tuxbake.argparse import setup_parser

    assert isinstance(setup_parser(), argparse.ArgumentParser)

    """
      ( -- ) Refers to named optional arguments, i.e parser_map data can be in any order and also optional until specified as required.
    """
    build_definition = tmp_path / "oniro.yaml"
    build_definition.write_text(git_build_definition)
    parser_map = {
        "--build-definition": str(build_definition),
        "--runtime": "docker",
        "--image": None,
        "--src-dir": "test",
        "--build-dir-name": "build",
        "--local-manifest": None,
        "--pinned-manifest": None,
    }
    data = ["test.py"]  # adding first argument as file_name
    for key in parser_map:
        data.extend([key, parser_map[key]])
    with patch("sys.argv", data):
        data = setup_parser().parse_args()
        print(data)
        assert all(
            [
                data.build_definition == parser_map["--build-definition"],
                data.runtime == parser_map["--runtime"],
                data.image == parser_map["--image"],
                data.src_dir == os.path.abspath(parser_map["--src-dir"]),
                data.build_dir_name == parser_map["--build-dir-name"],
                data.local_manifest == parser_map["--local-manifest"],
                data.pinned_manifest == parser_map["--pinned-manifest"],
            ]
        )


def test_file_or_url(tmp_path, git_build_definition):
    from tuxbake.argparse import file_or_url

    # case: Path to build definition file
    build_definition = tmp_path / "build-definition.yaml"
    build_definition.write_text(git_build_definition)
    assert file_or_url(build_definition) == build_definition

    # case: URL build definition file
    build_definition = "https://url/to/build-definition.yaml"
    with patch("tuxbake.argparse.download_file") as df, patch(
        "os.path.abspath", return_value=str(tmp_path / "file.yaml")
    ):
        df.return_value = "called"
        file_or_url(build_definition)
        assert df.call_count == 1
        df.assert_called_once_with(build_definition)

    # case: invalid path
    build_definition = "/tmp/definition.yaml"
    with pytest.raises(argparse.ArgumentTypeError):
        file_or_url(build_definition)

    # case: invalid URL scheme
    build_definition = "www.example.com/file/definition.yaml"
    with pytest.raises(argparse.ArgumentTypeError):
        file_or_url(build_definition)
