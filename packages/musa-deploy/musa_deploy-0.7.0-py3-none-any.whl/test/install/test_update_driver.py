import sys
import os
import pytest
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import (
    TestInstall,
    is_running_with_root,
)
from musa_deploy.install import DriverPkgMgr


@pytest.mark.skipif(
    not is_running_with_root(), reason="This test needs root permission."
)
def test_update_driver_310():
    test_install = TestInstall(DriverPkgMgr)
    mock_input = StringIO("n\n")
    with patch.object(sys, "stdin", mock_input):
        test_install.update(version="3.1.0")
    test_install.check_report_includes(
        test_install._update_log, "System needs to be restarted to load the driver"
    )


@pytest.mark.skipif(
    not is_running_with_root(), reason="This test needs root permission."
)
def test_update_driver_311():
    test_install = TestInstall(DriverPkgMgr)
    mock_input = StringIO("n\n")
    with patch.object(sys, "stdin", mock_input):
        test_install.update(version="3.1.1")
    test_install.check_report_includes(
        test_install._update_log, "System needs to be restarted to load the driver"
    )
