TuxBake, by [Linaro](https://www.linaro.org/), is a command line tool and
Python library that provides portable and repeatable OE builds. TuxBake is a part of [TuxSuite](https://tuxsuite.com), a suite of tools and services to help developers do build and boot test Linux kernel and OE distros.

[[_TOC_]]


# About TuxBake

TuxBake is a python application to build OE Distros. It takes a yaml file as input which
describes the layers needed to be downloaded, local_conf and bblayers_conf parameters along
with machine, distro targets. It downloads the layers for with using either git protocols or
the repo tool. It uses containers (both Docker and Podman) to provide a standardised build
environments to do the build which can be easily reproduced by other users.

# Installing Tuxbake

There are several options for installing TuxBake (TuxMake is a prerequisite):
```
pip3 install tuxmake
git clone https://gitlab.com/Linaro/tuxbake
cd tuxbake/
pip3 install .
```
## Tools required
The tools that needs to be installed on the host system are:
```
docker or podman, git, repo
```


# build-definition.yaml template with repo
```yaml
container: ubuntu-20.04
distro: rpb
envsetup: setup-environment
machine: dragonboard-845c
extraconfigs: []
sources:
  repo:
    branch: qcom/dunfell
    manifest: default.xml
    url: https://github.com/96boards/oe-rpb-manifest.git
target: rpb-console-image rpb-console-image-test rpb-desktop-image
  rpb-desktop-image-test
```

# build-definition.yaml template with git repositories
```yaml
sources:
  git_trees:
    - url: http://git.yoctoproject.org/git/poky
      branch: honister
    - url: https://github.com/ndechesne/meta-qcom
      branch: honister
container: ubuntu-20.04
envsetup: poky/oe-init-build-env
extraconfigs: []
distro: poky
machine: dragonboard-845c
target: core-image-minimal
bblayers_conf:
  - BBLAYERS += "../meta-qcom/"
environment: {}
```

# Fields of build-definition.yaml

## sources
The sources is a dictionary with single item. It could be either git_trees or repo.

### git_trees
The git_trees is a list of dictionary object. Each dictionary
object will have "url" and one of the following "branch", "ref"
or the "sha" field.  If specifying the "ref" feild that should
be in any of the formats:

"ref": "refs/pull/number/head"
"ref": "refs/pull/number/merge"
"ref": "refs/tags/tag"

Note: The "number" is the number of the pull request. and for
merge requests in Gitlab, just change "pull" to
"merge-requests".

### repo
The repo field is a dictionary object. The dictionary should have "branch", "manifest" and "url" field describing where the manifests are hosted along with the branch and manifest file to be used in the build.

## distro
This is the distro variable passed to OE build.

## dl_dir
This should be the absolute path to the download directory that is passed to OE build. NOTE: It will not work specifying the 'dl_dir' string with '~/' or '$HOME' in the path.

## sstate_dir
This should be the absolute path to the sstate-cache directory that is passed to OE build. NOTE: It will not work specifying the 'sstate_dir' string with '~/' or '$HOME' in the path.

## sstate_mirror
This should start with 'file:///some/local/dir/sstate/PATH' and/or 'https://someserver.tld/share/sstate/PATH;downloadfilename=PATH' sstate-cache directory that is passed to OE build.

## envsetup
This is path to the script relative to the source directory that needs to be sourced to setup bitbake build environment.

## extraconfigs
This is a list of string and each entry corresponds to some extra configs that will be used while building the target.

## machine
This is the machine variable passed to OE build.

## target
This the target passed to the bitbake command.

## container
This is the container used by Docker or Podman to do the build. We currently support ubuntu-16.04, ubuntu-18.04, ubuntu-20.04, ubuntu-22.04, ubuntu-24.04, centos-7, centos-8, debian-bookworm, debian-bullseye, debian-buster, debian-stretch, fedora-33, fedora-34, opensuse-leap-15.1, opensuse-leap-15.2

## local_conf
This is a list of of string and each entry corresponds to a line in local.conf file. The list of string is converted to local.conf file.

## bblayers_conf
This is a list of of string and each entry corresponds to a line in bblayers.conf file. The list of string is converted to bblayers.conf file.

## environment
This is a dictionary of environment variables which are set before calling bitbake.

# Using TuxBake

TuxBake takes the build-definition as input along with a source directory path where the code is downloaded.

# Examples

Build OE example:

    $ tuxbake --build-definition examples/oe-rpb.yaml --src-dir $PWD/oe/
