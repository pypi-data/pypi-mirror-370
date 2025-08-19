# -*- coding: utf-8 -*-

import json
import os
from dataclasses import asdict, dataclass, field, fields
from typing import Dict, List, Optional
from tuxmake.runtime import Runtime
from tuxmake.logging import set_debug, debug
from tuxbake.utils import (
    repo_init,
    git_init,
    copy_artifacts,
    get_filtered_paths,
    find_bitbake_env,
)
from pathlib import Path
from tuxbake.exceptions import TuxbakeParsingError
from tuxbake.helper import (
    check_instance,
    validate_artifacts,
    validate_bblayers_conf,
    validate_container,
    validate_environment,
    validate_extraconfigs,
    validate_git_dest,
    validate_git_ref,
    validate_git_repo,
    validate_git_sha,
    validate_local_conf,
)


class Base:
    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(self.as_dict())

    @classmethod
    def new(cls, **kwargs):
        fields_names = [f.name for f in fields(cls)]
        i_kwargs = {}
        v_kwargs = {}
        for k in kwargs:
            if k in fields_names:
                v_kwargs[k] = kwargs[k]
            else:
                i_kwargs[k] = kwargs[k]

        return cls(**v_kwargs, extra=i_kwargs)


@dataclass
class OEBuild(Base):
    src_dir: str
    build_dir: str
    envsetup: Optional[str] = None
    targets: Optional[List[str]] = None
    after_cmds: Optional[List[str]] = None
    extraconfigs: Optional[List[str]] = None
    extraconfigs_cmd: str = ""
    distro: Optional[str] = None
    build_only: bool = False
    sync_only: bool = False
    name: Optional[str] = None
    debug: bool = False
    machine: Optional[str] = None
    container: Optional[str] = None
    environment: Dict = field(default_factory=dict)
    local_conf: Optional[List[str]] = None
    bblayers_conf: Optional[List[str]] = None
    runtime: str = "docker"
    image: Optional[str] = None
    sources: Optional[List[Dict]] = None
    sstate_dir: Optional[str] = None
    sstate_mirror: Optional[str] = None
    dl_dir: Optional[str] = None
    __logger__ = None
    repo: Optional[Dict] = None
    git_trees: Optional[List] = None
    local_manifest: Optional[str] = None
    pinned_manifest: Optional[str] = None
    # For future use
    artifacts: Optional[List[str]] = None
    artifacts_dir: Optional[str] = None
    home_dir: str = None

    @dataclass
    class Repo:
        url: str
        branch: str
        manifest: str

    @dataclass
    class Git:
        url: str
        branch: Optional[str] = None
        ref: Optional[str] = None
        sha: Optional[str] = None
        dest: Optional[str] = None

    def __post_init__(self):
        self.log_dir = self.src_dir
        if self.sources.get("repo"):
            self.repo = self.Repo(**self.sources.get("repo"))
        elif self.sources.get("git_trees"):
            self.git_trees = []
            for git_entry in self.sources.get("git_trees"):
                self.git_trees.append(self.Git(**git_entry))

    @staticmethod
    def validate(oebuild_data):
        if not oebuild_data.get("sources"):
            raise (
                TuxbakeParsingError(
                    "Please specify either git_trees or repo in sources of build definition"
                )
            )

        check_instance(
            oebuild_data["sources"],
            dict,
            f"Unexpected value of sources in build definition: {oebuild_data['sources']}, expected dictionary object with either git_trees or repo",
        )
        if oebuild_data["sources"].get("repo") and oebuild_data["sources"].get(
            "git_trees"
        ):
            raise (
                TuxbakeParsingError("repo or git_trees may be specified, but not both")
            )

        elif oebuild_data["sources"].get("repo"):
            repo = oebuild_data["sources"]["repo"]
            check_instance(
                repo,
                dict,
                f"Unexpected value of repo in sources of build definition: {repo}, expected dictionary object with url, branch and manifest",
            )
            for val in ["url", "branch", "manifest"]:
                if val not in repo.keys():
                    raise (
                        TuxbakeParsingError(
                            f"Please specify the mandatory field {val} in repo of sources"
                        )
                    )
            url, branch, manifest = repo["url"], repo["branch"], repo["manifest"]
            validate_git_repo(url)
            check_instance(
                branch,
                str,
                f"Unexpected argument for branch: {branch}, expected string: '{branch}'",
            )
            check_instance(
                manifest,
                str,
                f"Unexpected argument for manifest: {manifest}, expected string: '{manifest}'",
            )
            ext = os.path.splitext(manifest)[1]
            if manifest and ext.lower() != ".xml":
                raise (
                    TuxbakeParsingError(
                        f"unknown manifest file extension: '{ext}', must be '.xml': '{manifest}'"
                    )
                )

        elif oebuild_data["sources"].get("git_trees"):
            git_trees = oebuild_data["sources"]["git_trees"]
            check_instance(
                git_trees,
                list,
                f"Unexpected argument for git_trees: {git_trees}, expected list: '{git_trees}'",
            )

            for git_obj in git_trees:
                check_instance(
                    git_obj,
                    dict,
                    f"Unexpected values of git_trees List: {git_obj}, expected dictionary objects in the List",
                )
                if "url" not in git_obj.keys():
                    raise (
                        TuxbakeParsingError(
                            "Please specify the mandatory field url in git_trees of sources"
                        )
                    )

                url = git_obj["url"]
                branch = git_obj.get("branch", "")
                ref = git_obj.get("ref", "")
                sha = git_obj.get("sha", "")
                dest = git_obj.get("dest", "")
                # validations
                validate_git_repo(url)
                if branch:
                    check_instance(
                        branch,
                        str,
                        f"Unexpected argument for branch: {branch}, expected string: '{branch}'",
                    )
                if ref:
                    validate_git_ref(ref)
                if sha:
                    validate_git_sha(sha)
                if dest:
                    validate_git_dest(dest)
        else:
            raise (TuxbakeParsingError("repo or git_trees must be specified!!"))

        if oebuild_data.get("envsetup"):
            check_instance(
                oebuild_data["envsetup"],
                str,
                f"Unexpected argument for envsetup: {oebuild_data['envsetup']}, expected string: '{oebuild_data['envsetup']}'",
            )
        else:
            raise (
                TuxbakeParsingError("Please specify the envsetup in build definition")
            )

        if oebuild_data.get("targets"):
            check_instance(
                oebuild_data["targets"],
                list,
                f"Unexpected argument for targets: {oebuild_data['targets']}, expected list: '{oebuild_data['targets']}'",
            )
        else:
            raise (
                TuxbakeParsingError("Please specify the targets in build definition")
            )

        if oebuild_data.get("machine"):
            check_instance(
                oebuild_data["machine"],
                str,
                f"Unexpected argument for target: {oebuild_data['machine']}, expected string: '{oebuild_data['machine']}'",
            )
        else:
            raise (
                TuxbakeParsingError("Please specify the machine in build definition")
            )

        if oebuild_data.get("distro"):
            check_instance(
                oebuild_data["distro"],
                str,
                f"Unexpected argument for distro: {oebuild_data['distro']}, expected string: '{oebuild_data['distro']}'",
            )
        else:
            raise (TuxbakeParsingError("Please specify the distro in build definition"))

        if oebuild_data.get("container"):
            validate_container(oebuild_data["container"])
        else:
            raise (
                TuxbakeParsingError("Please specify the container in build definition")
            )

        if oebuild_data.get("environment"):
            validate_environment(oebuild_data["environment"])
        if oebuild_data.get("local_conf"):
            validate_local_conf(oebuild_data["local_conf"])
        if oebuild_data.get("bblayers_conf"):
            validate_bblayers_conf(oebuild_data["bblayers_conf"])
        if oebuild_data.get("extraconfigs"):
            validate_extraconfigs(oebuild_data["extraconfigs"])

        if oebuild_data.get("sstate_dir"):
            check_instance(
                oebuild_data["sstate_dir"],
                str,
                f"Unexpected argument for sstate_dir, expected string: '{oebuild_data['sstate_dir']}'",
            )
        if oebuild_data.get("sstate_mirror"):
            check_instance(
                oebuild_data["sstate_mirror"],
                str,
                f"Unexpected argument for sstate_mirror, expected string: '{oebuild_data['sstate_mirror']}'",
            )
        if oebuild_data.get("dl_dir"):
            check_instance(
                oebuild_data["dl_dir"],
                str,
                f"Unexpected argument for dl_dir, expected string: '{oebuild_data['dl_dir']}'",
            )
        if oebuild_data.get("artifacts"):
            validate_artifacts(oebuild_data["artifacts"])

    def __prepare__(self):
        os.makedirs(self.src_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        debug(f"build-only flag set to: {self.build_only}")
        debug(f"sync-only flag set to: {self.sync_only}")
        if self.build_only and self.sync_only:
            print("ERROR: Both build-only and sync-only shouldn't be set.")
        if self.build_only:
            return
        if self.sources.get("repo"):
            repo_init(self, self.src_dir, self.local_manifest, self.pinned_manifest)
        else:
            git_init(self, self.src_dir)

    def prepare(self):
        set_debug(self.debug)
        self.__prepare__()
        os.environ["SKIP_OVERLAYFS"] = "true"
        self._runtime = Runtime.get(self.runtime)
        if self.sync_only:
            return
        if self.distro.startswith("openbmc"):
            self._runtime.source_dir = Path(f"{self.src_dir}/openbmc")
            self.envsetup = f"{self.envsetup} {self.machine}"
        else:
            self._runtime.source_dir = Path(self.src_dir)
        self._runtime.set_user("tuxbake")
        self._runtime.set_group("tuxbake")
        self._runtime.basename = "build"
        _container_name = f"docker.io/tuxbake/{self.container}"
        if "-local" in self.runtime:
            _container_name = f"{self.image}"
        self._runtime.set_image(f"{_container_name}")
        self._runtime.output_dir = Path(self.log_dir)
        if self.dl_dir:
            self._runtime.add_volume(self.dl_dir)
        if self.home_dir:
            self._runtime.add_volume(self.home_dir, "/home/tuxbake")
        if self.sstate_dir and not self.sstate_dir.startswith(self.src_dir):
            self._runtime.add_volume(self.sstate_dir)
        environment = self.environment
        environment["MACHINE"] = self.machine
        environment["DISTRO"] = self.distro
        self._runtime.environment = environment

        self._runtime.prepare()
        with open(
            f"{os.path.abspath(self.src_dir)}/extra_local.conf", "w"
        ) as extra_local_conf:
            if self.dl_dir:
                extra_local_conf.write(f'DL_DIR = "{self.dl_dir}"\n')
            if self.sstate_dir:
                extra_local_conf.write(f'SSTATE_DIR = "{self.sstate_dir}"\n')
            if self.sstate_mirror:
                extra_local_conf.write(f'SSTATE_MIRRORS = "{self.sstate_mirror}"\n')
                extra_local_conf.write(
                    'USER_CLASSES += "buildstats buildstats-summary"\n'
                )
            if self.local_conf:
                for line in self.local_conf:
                    extra_local_conf.write(f"{line}\n")

        if self.bblayers_conf:
            with open(
                f"{os.path.abspath(self.src_dir)}/bblayers.conf", "w"
            ) as bblayers_conf_file:
                for line in self.bblayers_conf:
                    bblayers_conf_file.write(f"{line}\n")

        if self.extraconfigs:
            copies = []
            for extra in self.extraconfigs:
                copies.append(f"cp -a {extra} conf/")
            self.extraconfigs_cmd += "&& " + " && ".join(copies)

        return

    def do_build(self):
        if self.sync_only:
            return
        # Setup bitbake environment
        cmd = [
            "bash",
            "-c",
            f"rm -f {self.build_dir}/conf/bblayers.conf && rm -f {self.build_dir}/conf/local.conf && source {self.envsetup} {self.build_dir} {self.extraconfigs_cmd} && cat ../extra_local.conf >> conf/local.conf && cat ../bblayers.conf >> conf/bblayers.conf || true && echo 'Dumping local.conf..' && cat conf/local.conf",
        ]
        if self._runtime.run_cmd(cmd, offline=False):
            self.result = "pass"
        else:
            self.result = "fail"
            return

        # Dump bitbake -e separately
        cmd = [
            "bash",
            "-c",
            f"source {self.envsetup} {self.build_dir} && bitbake -e > bitbake-environment",
        ]
        self._runtime.run_cmd(cmd, offline=False)

        for target in self.targets:
            cmd = [
                "bash",
                "-c",
                f"source {self.envsetup} {self.build_dir} && bitbake {target}",
            ]
            if self._runtime.run_cmd(cmd, offline=False):
                self.result = "pass"
            else:
                self.result = "fail"
                return

        if not self.after_cmds:
            return

        for cmd in self.after_cmds:
            cmd = [
                "bash",
                "-c",
                f"source {self.envsetup} {self.build_dir} && {cmd}",
            ]
            if self._runtime.run_cmd(cmd, offline=False):
                self.result = "pass"
            else:
                self.result = "fail"
                return

    def publish_artifacts(self):
        build_dir = f"{self._runtime.source_dir}/{self.build_dir}"
        bitbake_env_file = f"{build_dir}/bitbake-environment"
        deploy_dir = find_bitbake_env(bitbake_env_file, "DEPLOY_DIR")
        artifacts_path_list = [bitbake_env_file]
        if self.artifacts:
            build_dir_paths = get_filtered_paths(self.artifacts, build_dir)
            deploy_dir_paths = get_filtered_paths(self.artifacts, deploy_dir)
            artifacts_path_list += build_dir_paths + deploy_dir_paths
        elif deploy_dir is not None:
            # whole DEPLOY_DIR to be published
            artifacts_path_list += [f"{deploy_dir}/."]

        dest_dir = f"{self.src_dir}/{self.artifacts_dir}"
        copy_artifacts(artifacts_path_list, dest_dir)

    def do_cleanup(self):
        if self._runtime:
            self._runtime.cleanup()
