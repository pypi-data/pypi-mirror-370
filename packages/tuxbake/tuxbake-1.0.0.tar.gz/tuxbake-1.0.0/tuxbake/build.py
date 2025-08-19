#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tuxbake.models import OEBuild
from tuxbake.metadata import Metadata
from tuxmake.runtime import Terminated
import signal
import sys


def build(**kwargs):
    old_sigterm = signal.signal(signal.SIGTERM, Terminated.handle_signal)
    oebuild = OEBuild(**kwargs)
    try:
        oebuild.prepare()
        oebuild.do_build()
    except (KeyboardInterrupt, Terminated):
        print("tuxbake Interrupted")

    if oebuild.artifacts_dir:
        oebuild.publish_artifacts()
    # try to collect metadata
    try:
        metadata = Metadata(oebuild)
        metadata.collect()
    except Exception as ex:
        sys.stderr.write(f"{str(ex)}\n")

    oebuild.do_cleanup()
    signal.signal(signal.SIGTERM, old_sigterm)
    return oebuild
