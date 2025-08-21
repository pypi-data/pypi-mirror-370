import sys
import os
import pytest
import platform

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import (
    TestInstall,
    is_running_with_root,
)
from musa_deploy.install import (
    DriverPkgMgr,
    HostPkgMgr,
    ContainerToolkitsPkgMgr,
    SmartIOPkgMgr,
)
from musa_deploy.utils import FontGreen


@pytest.mark.skipif(
    not is_running_with_root(), reason="This test needs root permission."
)
def test_install_hosts_with_interaction(request):
    if request.config.getoption("capture") != "no":
        pytest.skip("需要使用 -s 运行此测试（例如：pytest -s ...）")
    test_driver_install = TestInstall(DriverPkgMgr)
    test_container_toolkit_install = TestInstall(ContainerToolkitsPkgMgr)
    test_smartio_install = TestInstall(SmartIOPkgMgr)
    test_host_install = TestInstall(HostPkgMgr)
    # uninstall dependencies
    test_container_toolkit_install.uninstall()
    test_driver_install.uninstall()
    test_smartio_install.uninstall()
    # uninstall
    test_host_install.uninstall()
    # install

    test_host_install.install()

    test_host_install.check_report_includes(
        test_host_install._install_log, f"Installing {FontGreen('dkms')} ..."
    )

    test_host_install.check_report_includes(
        test_host_install._install_log,
        f"Please choose the display manager: {FontGreen('lightdm')}\nPlease choose the display manager: {FontGreen('lightdm')}\nPlease choose the display manager: {FontGreen('lightdm')}",
    )
    test_host_install.check_report_includes(
        test_host_install._install_log,
        f"Installing {FontGreen(f'linux-modules-extra-{platform.release()}')} ...",
    )
