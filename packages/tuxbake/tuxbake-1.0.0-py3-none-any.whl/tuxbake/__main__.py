#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import yaml

# TODO this should not be needed if the tuxmake RPM manages to provide a public
# Python module that is not tied to a specific Python version
sys.path.append("/usr/share/tuxmake")


from tuxbake.models import OEBuild  # noqa: E402
from tuxbake.argparse import setup_parser  # noqa: E402
from tuxbake.build import build  # noqa: E402
from tuxbake.exceptions import (  # noqa: E402
    TuxbakeParsingError,
    TuxbakeRunCmdError,
)


##############
# Entrypoint #
##############
def main() -> int:
    # Parse command line
    parser = setup_parser()
    options = parser.parse_args()
    try:
        contents = open(options.build_definition).read()
        build_definition = yaml.safe_load(contents)
        legacy_target = build_definition.get("target")
        targets = build_definition.get("targets")
        if legacy_target:
            if targets is None:
                build_definition["targets"] = [legacy_target]
            del build_definition["target"]
        OEBuild.validate(build_definition)
        build(
            **(build_definition),
            src_dir=options.src_dir,
            build_dir=options.build_dir_name,
            home_dir=options.home_dir,
            local_manifest=options.local_manifest,
            pinned_manifest=options.pinned_manifest,
            runtime=options.runtime,
            image=options.image,
            debug=options.debug,
            build_only=options.build_only,
            sync_only=options.sync_only,
            artifacts_dir=options.publish_artifacts,
        )
    except yaml.YAMLError as ex:
        print(f"E: Invalid build definition yaml file\n{ex}", file=sys.stderr)
        return 1
    except (TuxbakeParsingError, TuxbakeRunCmdError) as ex:
        print(ex, file=sys.stderr)
        return 1
    return 0


def start():
    if __name__ == "__main__":
        sys.exit(main())


start()
