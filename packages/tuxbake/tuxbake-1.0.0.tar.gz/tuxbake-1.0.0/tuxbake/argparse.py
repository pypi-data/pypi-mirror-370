#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
from pathlib import Path
import sys
from typing import List
from urllib.parse import urlparse
import yaml

from tuxbake import __version__
from tuxbake.utils import download_file, is_json
from tuxmake.runtime import Runtime


class supported:
    runtimes: List[str] = Runtime.supported()


def file_or_url(value):
    if Path(value).is_file():
        if is_json(Path(value).read_text()):
            raise argparse.ArgumentTypeError(
                "The build definition file is not valid. It must be in YAML format"
            )
        return value
    elif urlparse(value).scheme in ["http", "https"]:
        build_definition = os.path.abspath("build-definition.yaml")
        resp = download_file(value)
        if is_json(resp):
            raise argparse.ArgumentTypeError(
                "The build definition file is not valid. It must be in YAML format"
            )
        try:
            # Dump into yaml
            with open(build_definition, "w+") as f:
                yaml.safe_dump(yaml.safe_load(resp), f, indent=4, sort_keys=True)
        except yaml.YAMLError as e:
            print(f"E: Invalid build definition file\n{e}", file=sys.stderr)
            sys.exit(1)

        return build_definition

    raise argparse.ArgumentTypeError(f"'{value}' is not a valid file path or URL")


##########
# Setups #
##########
def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tuxbake", description="TuxBake")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s, {__version__}"
    )
    group = parser.add_argument_group("OE Build Parameters")
    group.add_argument(
        "--build-definition",
        help="Path/URL to build definition yaml file",
        required=True,
        type=file_or_url,
    )
    group.add_argument(
        "--build-only",
        help="Assume the source tree is already pulled.",
        action="store_true",
    )
    group.add_argument(
        "--debug",
        help="Provides extra output on stderr for debugging tuxbake itself. This output will not appear in the build log.",
        action="store_true",
    )
    group.add_argument(
        "-r",
        "--runtime",
        help=f"Runtime to use for the builds. By default, builds are run in a docker container. With 'docker-local' runtime the --image option needs to be specified to a local container. Supported: {', '.join(supported.runtimes)}.",
        default="docker",
    )
    group.add_argument(
        "-i",
        "--image",
        help="Image to build with, for container-based runtimes (docker etc). Implies --runtime=docker if no runtime is explicit specified. (default: tuxbake-provided images).",
        default=None,
    )
    group.add_argument(
        "--src-dir",
        help="source directory where the sources will be downloaded",
        default="source",
        type=os.path.abspath,  # type: ignore
    )
    group.add_argument(
        "--sync-only",
        help="Download all the meta repositories via repo or git only.",
        action="store_true",
    )
    group.add_argument(
        "--build-dir-name",
        help="Directory name passed to the source script during OE build. It defaults to build",
        default="build",
    )
    group.add_argument(
        "--home-dir",
        help="Path to the home directory to be used as home inside the container. This can be used to pass credentials.",
        default=None,
    )
    group.add_argument(
        "--local-manifest",
        help="Path to a local manifest file which will be used during repo sync. This input is ignored if sources used is git_trees in the build definition",
        default=None,
    )
    group.add_argument(
        "--pinned-manifest",
        help="Path to a local manifest file which will be used to override repo setup before doing repo sync. This input is ignored if sources used is git_trees in the build definition",
        default=None,
    )
    group.add_argument(
        "--publish-artifacts",
        help="Directory where artifacts will be copied",
        default=None,
    )
    return parser
