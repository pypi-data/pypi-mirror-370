import os
import json
import shutil
import subprocess
from typing import List
from pathlib import Path
from collections import OrderedDict
from configparser import ConfigParser as OrigConfigParser

from tuxbake import __version__
from tuxbake.exceptions import UnsupportedMetadata, UnsupportedMetadataType


def run_command(cmd, src_dir=None):
    try:
        out = subprocess.check_output(cmd, cwd=src_dir, text=True).strip()
        return out
    except Exception as e:
        print(e)


class ConfigParser(OrigConfigParser):
    def optionxform(self, opt):
        return str(opt)


class Metadata:
    basedir = "metadata"

    def __init__(self, oebuild):
        self.oebuild = oebuild
        self.runtime = self.oebuild._runtime
        self.src_dir = self.oebuild.src_dir
        self.build_dir = Path(f"{self.runtime.source_dir}/{self.oebuild.build_dir}")
        self.metadata = OrderedDict()
        self.files = self.meta_files()
        self.types = {}

    def collect(self):
        self.metadata["build"] = {
            "envsetup": self.oebuild.envsetup,
            "targets": self.oebuild.targets,
            "distro": self.oebuild.distro,
            "name": self.oebuild.name,
            "machine": self.oebuild.machine,
            "container": self.oebuild.container,
            "environment": self.oebuild.environment,
            "local_conf": self.oebuild.local_conf,
            "bblayers_conf": self.oebuild.bblayers_conf,
            "runtime": self.oebuild.runtime,
            "image": self.oebuild.image,
            "sstate_dir": self.oebuild.sstate_dir,
            "sstate_mirror": self.oebuild.sstate_mirror,
            "dl_dir": self.oebuild.dl_dir,
            "local_manifest": self.oebuild.local_manifest,
            "pinned_manifest": self.oebuild.pinned_manifest,
            "artifacts": self.oebuild.artifacts,
        }
        self.metadata["tuxbake"] = {"version": __version__}
        self.metadata["runtime"] = self.get_runtime_info()
        self.metadata["git"] = self.get_git_info()
        # collect data by running perl script
        self.metadata.update(self.generate_meta_dict())
        if self.metadata.get("hardware"):
            self.metadata["hardware"]["free_disk_space"] = self.free_disk_space()
        if hasattr(self.oebuild, "result"):
            self.metadata["results"] = {
                "status": "PASS" if self.oebuild.result == "pass" else "FAIL",
            }
        # save metadata.json file
        self.save_metadata()

    def get_runtime_info(self):
        if self.runtime.name in ["null", "docker-local", "podman-local"]:
            return {}

        return self.runtime.get_metadata()

    def save_metadata(self):
        with (Path(self.src_dir) / "metadata.json").open("w") as f:
            f.write(json.dumps(self.metadata, indent=4, sort_keys=True))
            f.write("\n")

    def meta_files(self) -> List[str]:
        # get all available '*.ini' files from metadata folder
        files = (Path(__file__).parent / self.basedir).glob("*.ini")
        return [str(f.name).replace(".ini", "") for f in files]

    def generate_meta_dict(self):
        # Generate metadata extractions pecification in JSON format to pass to script file
        # then process the script output and then return metadata dictionary
        metadata_input_data = {}
        for file in self.files:
            metadata_input_data[file] = {}
            conffile = Path(__file__).parent / self.basedir / f"{file}.ini"
            config = ConfigParser()
            config.read(conffile)
            # parse types field
            try:
                for k, t in config["types"].items():
                    if t not in ["int", "str", "linelist"]:
                        raise UnsupportedMetadataType(t)
                    self.types[k] = eval(t)
            except KeyError:
                pass
            # parse commands field
            try:
                commands = {
                    k: self.replace_placeholders(v)
                    for k, v in dict(config["commands"]).items()
                }
                metadata_input_data[file] = commands
            except KeyError as key:
                raise UnsupportedMetadata(f"{key} is required in '{file}.ini' file")

        metadata_input = self.build_dir / "metadata.in.json"
        metadata_input.write_text(json.dumps(metadata_input_data), encoding="utf-8")

        script_src = Path(__file__).parent / "metadata.pl"
        script = self.build_dir / "metadata.pl"
        shutil.copy(script_src, script)

        stdout = Path(self.build_dir / "extracted-metadata.json")
        with stdout.open("w") as f:
            self.runtime.run_cmd(
                ["perl", str(script), str(metadata_input)],
                echo=False,
                stdout=f,
                offline=False,
            )
        metadata = self.read_json(stdout.read_text())
        return metadata

    def replace_placeholders(self, key):
        return key.format(build_dir=self.build_dir)

    def read_json(self, metadata_json):
        # Loads the json, typecast its values into desired datatype and return result dict.
        if not metadata_json:
            return {}
        try:
            metadata = json.loads(metadata_json)
        except json.JSONDecodeError:
            return {"invalid_metadata": metadata_json}
        if not metadata:
            return {}

        result = {}
        for key in metadata:
            for k, v in metadata[key].items():
                if v:
                    v = v.strip()
                if v:
                    result.setdefault(key, {})
                    result[key][k] = self.cast(k, v)

        return result

    def cast(self, key, v):
        # typecast the command output with desired datatype
        t = self.types.get(key, str)
        return t(v)

    def free_disk_space(self):
        disk_usage = shutil.disk_usage(self.build_dir)
        return int(disk_usage.free / (2**20))

    def get_git_info(self):
        git_cmds = {
            "branch": "git rev-parse --abbrev-ref HEAD",
            "commit": "git rev-parse HEAD",
            "url": "git remote get-url origin",
        }
        ret = {}
        oebuild = self.oebuild
        if oebuild.sources.get("repo"):
            for key, cmd in git_cmds.items():
                ret[key] = run_command(cmd.split(), f"{self.src_dir}/.repo/repo")
        else:
            for git_object in oebuild.git_trees:
                temp = {}
                url = git_object.url.rstrip("/")
                dest = git_object.dest
                basename = os.path.splitext(os.path.basename(url))[0]
                if dest:
                    abs_dest = (
                        os.path.abspath(
                            os.path.join(self.src_dir, os.path.expanduser(dest))
                        )
                        + os.sep
                    )
                    dir_path = Path(os.path.join(abs_dest, basename))
                else:
                    dir_path = Path(os.path.join(self.src_dir, basename))

                for key, cmd in git_cmds.items():
                    temp[key] = run_command(cmd.split(), dir_path)
                ret[basename] = temp
        return ret
