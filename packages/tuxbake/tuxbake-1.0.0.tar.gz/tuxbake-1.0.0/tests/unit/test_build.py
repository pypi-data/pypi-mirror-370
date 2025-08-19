from unittest.mock import patch, MagicMock
from tuxbake.models import OEBuild


@patch.multiple(
    OEBuild,
    prepare=MagicMock(),
    do_cleanup=MagicMock(),
    do_build=MagicMock(return_value="build_called"),
    publish_artifacts=MagicMock(return_value="publish_artifacts_called"),
)
def test_build(oebuild_repo_init_object):
    from tuxbake.build import build

    oebuild_repo_init_object.local_manifest = None
    oebuild_object = oebuild_repo_init_object.as_dict()

    data = build(**oebuild_object)
    assert data == OEBuild(**oebuild_object)
    ret_val = data.do_build()
    assert ret_val == "build_called"
    ret_val = data.publish_artifacts()
    assert ret_val == "publish_artifacts_called"
