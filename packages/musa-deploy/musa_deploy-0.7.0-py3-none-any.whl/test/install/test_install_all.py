import pytest
from unittest.mock import patch, call
from musa_deploy.install import PACKAGE_MANAGER
from musa_deploy.install.install import DownloadDecompressor
from musa_deploy.download import DOWNLOADER
from musa_deploy.check.utils import Status
from musa_deploy.utils import (
    SHELL,
)


# Unit test
def test_update_version():
    """测试 update_version 方法是否正确更新版本"""
    driver_install = PACKAGE_MANAGER["driver"]
    driver_install.update_version("2.0.0")
    assert driver_install._target_version == "2.0.0"


@patch.object(SHELL, "run_cmd", return_value=(None, None, 0))
def test_verify_is_installed_dpkg_success(mock_run_cmd):
    """测试 verify_is_installed 方法在 dpkg 包已安装时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    driver_install.verify_is_installed(
        package_name=driver_install._target_package_name,
        is_installed_file_flag=None,
        package_type="dpkg",
    )
    mock_run_cmd.assert_called_once_with(
        f"dpkg -s {driver_install._target_package_name}"
    )


@patch.object(SHELL, "run_cmd", return_value=("", "", 0))
def test_verify_is_installed_pip_failure(mock_run_cmd):
    """测试 verify_is_installed 方法在 pip 包未安装时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    assert (
        driver_install.verify_is_installed("invalid_pkg", "installed_flag", "pip")
        is False
    )
    mock_run_cmd.assert_called_once()


@patch.object(SHELL, "run_cmd", return_value=(1, "", 0))
def test_verify_is_installed_sh_file_exists(mock_run_cmd):
    """测试 verify_is_installed 方法在文件存在时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    assert (
        driver_install.verify_is_installed("/path/to/file", "installed_flag", "sh")
        is True
    )
    mock_run_cmd.assert_called_once()


@patch.object(SHELL, "run_cmd", return_value=("", "", 0))
def test_verify_is_installed_sh_file_not_exists(mock_run_cmd):
    """测试 verify_is_installed 方法在文件不存在时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    assert (
        driver_install.verify_is_installed(
            "/path/to/nonexistent", "installed_flag", "sh"
        )
        is False
    )
    mock_run_cmd.assert_called_once()


def test_is_uninstalled_true(mocker):
    """测试 is_uninstalled 方法在包未安装时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(
        driver_install._checker, "get_key_status", return_value=Status.UNINSTALLED
    )
    assert driver_install.is_uninstalled() is True


def test_is_uninstalled_false(mocker):
    """测试 is_uninstalled 方法在包已安装时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(
        driver_install._checker, "get_key_status", return_value=Status.SUCCESS
    )
    assert driver_install.is_uninstalled() is False


def test_driver_uninstall_success(mocker):
    """测试 uninstall 方法成功卸载的情况"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "verify_is_installed", return_value=False)
    mock_uninstall_cmd = mocker.patch.object(driver_install, "uninstall_cmd")
    mock_print = mocker.patch("builtins.print")
    driver_install.uninstall()
    mock_uninstall_cmd.assert_called_once()
    mock_print.assert_called_with("Successfully uninstall \x1b[91mdriver\x1b[0m.")


def test_driver_uninstall_failure(mocker):
    """测试 uninstall 方法在卸载失败时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "verify_is_installed", return_value=True)
    mock_uninstall_cmd = mocker.patch.object(driver_install, "uninstall_cmd")
    mock_print = mocker.patch("builtins.print")
    driver_install.uninstall()
    mock_uninstall_cmd.assert_called_once()
    mock_print.assert_called_with(
        "Warning: maybe uninstall \x1b[91mdriver\x1b[0m Failed, please uninstall it manually!"
    )


def test_container_toolkit_uninstall_success(mocker):
    """测试 uninstall 方法成功卸载的情况"""
    container_toolkit_install = PACKAGE_MANAGER["container_toolkit"]
    mocker.patch.object(
        container_toolkit_install, "verify_is_installed", return_value=False
    )
    mock_uninstall_cmd = mocker.patch.object(container_toolkit_install, "uninstall_cmd")
    mock_print = mocker.patch("builtins.print")
    container_toolkit_install.uninstall()
    mock_uninstall_cmd.assert_called_once()
    expected_calls = [
        call("Successfully uninstall \x1b[91mcontainer-toolkit\x1b[0m."),
        call("Successfully uninstall \x1b[91mmtml\x1b[0m."),
        call("Successfully uninstall \x1b[91msgpu-dkms\x1b[0m."),
    ]
    assert mock_print.call_count == 3
    mock_print.assert_has_calls(expected_calls)


def test_container_toolkit_uninstall_failure(mocker):
    """测试 uninstall 方法在卸载失败时的行为"""
    container_toolkit_install = PACKAGE_MANAGER["container_toolkit"]
    mocker.patch.object(
        container_toolkit_install, "verify_is_installed", return_value=True
    )
    mock_uninstall_cmd = mocker.patch.object(container_toolkit_install, "uninstall_cmd")
    mock_print = mocker.patch("builtins.print")
    container_toolkit_install.uninstall()
    mock_uninstall_cmd.assert_called_once()
    expected_calls = [
        call(
            "Warning: maybe uninstall \x1b[91mcontainer-toolkit\x1b[0m Failed, please uninstall it manually!"
        ),
        call(
            "Warning: maybe uninstall \x1b[91mmtml\x1b[0m Failed, please uninstall it manually!"
        ),
        call(
            "Warning: maybe uninstall \x1b[91msgpu-dkms\x1b[0m Failed, please uninstall it manually!"
        ),
    ]
    assert mock_print.call_count == 3
    mock_print.assert_has_calls(expected_calls)


@patch.object(SHELL, "run_cmd_with_error_print")
@patch.object(SHELL, "run_cmd_with_standard_print")
def test_install_cmd(
    mock_run_cmd_with_standard_print, mock_run_cmd_with_error_print, mocker
):
    """测试 install_cmd 方法是否返回 True"""
    mock_root = mocker.patch(
        "musa_deploy.install.install.require_root_privileges_check", return_value=True
    )
    mock_continue_or_exit = mocker.patch(
        "musa_deploy.install.install.continue_or_exit", return_value=True
    )
    driver_install = PACKAGE_MANAGER["driver"]
    driver_install._pkg_path_dict["driver"] = "/home/sdkrc3.1.1/musa_driver.deb"
    mock_print = mocker.patch("builtins.print")
    assert driver_install.install_cmd() is True
    mock_root.assert_called_once()
    mock_print.assert_called_with("Installing \x1b[32mdriver\x1b[0m ...")
    mock_run_cmd_with_error_print.assert_called_with(
        "dpkg -i /home/sdkrc3.1.1/musa_driver.deb"
    )
    mock_continue_or_exit.assert_called_once()
    mock_run_cmd_with_standard_print.assert_called_with("reboot")


@patch.object(SHELL, "run_cmd_with_error_print")
@patch.object(SHELL, "run_cmd_with_standard_print")
def test_install_cmd_not_reboot(
    mock_run_cmd_with_standard_print, mock_run_cmd_with_error_print, mocker
):
    """测试 install_cmd 方法是否返回 True"""
    mock_root = mocker.patch(
        "musa_deploy.install.install.require_root_privileges_check", return_value=True
    )
    mock_continue_or_exit = mocker.patch(
        "musa_deploy.install.install.continue_or_exit", return_value=False
    )
    driver_install = PACKAGE_MANAGER["driver"]
    driver_install._pkg_path_dict["driver"] = "/home/sdkrc3.1.1/musa_driver.deb"
    mock_print = mocker.patch("builtins.print")
    assert driver_install.install_cmd() is True
    mock_root.assert_called_once()
    mock_print.assert_called_with("Installing \x1b[32mdriver\x1b[0m ...")
    mock_run_cmd_with_error_print.assert_called_with(
        "dpkg -i /home/sdkrc3.1.1/musa_driver.deb"
    )
    mock_continue_or_exit.assert_called_once()
    mock_run_cmd_with_standard_print.assert_not_called()


@patch.object(SHELL, "run_cmd_with_error_print")
def test_uninstall_cmd(mock_run_cmd_with_error_print, mocker):
    """测试 uninstall_cmd 方法是否被调用"""
    mock_root = mocker.patch(
        "musa_deploy.install.install.require_root_privileges_check", return_value=True
    )
    driver_install = PACKAGE_MANAGER["driver"]
    mock_print = mocker.patch("builtins.print")
    driver_install.uninstall_cmd()
    mock_root.assert_called_once()
    mock_print.assert_called_with("Uninstalling \x1b[91mdriver\x1b[0m ...")
    mock_run_cmd_with_error_print.assert_called_with("dpkg -P musa")


def test_set_driver_target_version():
    """测试 set_driver_target_version 方法是否正确设置驱动版本"""
    driver_install = PACKAGE_MANAGER["driver"]
    driver_install.set_driver_target_version("2.7.2")
    assert driver_install._driver_version == "2.7.2"


def test_version_lookup_without_driver_version():
    """测试 version_lookup 方法在无驱动版本时的行为"""
    container_toolkit_install = PACKAGE_MANAGER["container_toolkit"]
    assert container_toolkit_install.version_lookup() is None


def test_version_lookup_with_driver_version():
    """测试 version_lookup 方法在有驱动版本时的行为"""
    container_toolkit_install = PACKAGE_MANAGER["container_toolkit"]
    container_toolkit_install._driver_version = "2.7.0"
    assert container_toolkit_install.version_lookup() == "2.7.0"


@patch.object(DOWNLOADER, "download", return_value={"driver": "/home/sdkrc3.1.1.zip"})
@patch.object(
    DownloadDecompressor,
    "decompress",
    return_value={"driver": "/home/sdkrc3.1.1/musa_driver.deb"},
)
def test_download_success(mock_decompress, mock_download):
    """测试 download 方法成功下载的情况"""
    driver_install = PACKAGE_MANAGER["driver"]
    driver_install.update_version()
    driver_install.download()
    assert driver_install._pkg_path_dict["driver"] == "/home/sdkrc3.1.1/musa_driver.deb"
    mock_download.assert_called_once()
    mock_decompress.assert_called_once()


@patch.object(DOWNLOADER, "download", side_effect=Exception("Download failed"))
def test_download_failure(mock_download):
    """测试 download 方法在下载失败时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    with pytest.raises(Exception):
        driver_install.download()
        mock_download.assert_called_once()


def test_install_with_path(mocker):
    """测试 install 方法在指定路径时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "is_uninstalled", return_value=True)
    mocker.patch.object(driver_install, "install_cmd")
    driver_install.install(version="3.1.1", path="/home/sdkrc3.1.1/musa_driver.deb")
    assert driver_install._pkg_path_dict["driver"] == "/home/sdkrc3.1.1/musa_driver.deb"


def test_install_with_dependency_failure(mocker):
    """测试 install 方法在依赖检查失败时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install._checker, "_has_dependency_failed", True)
    mock_print = mocker.patch("builtins.print")
    with pytest.raises(SystemExit):
        driver_install.install(version="3.1.1")
        mock_print.assert_called_with(
            f"The pre-requisite dependency check failed. Please manually install {driver_install._name}. For detailed check information, use the `musa-deploy -c {driver_install._name}` command!"
        )


def test_update_success(mocker):
    """测试 update 方法成功更新的情况"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "is_uninstalled", return_value=True)
    mocker.patch.object(driver_install, "uninstall")
    mocker.patch.object(driver_install, "install_cmd")
    driver_install.update(version="3.1.1", path="/home/sdkrc3.1.1/musa_driver.deb")
    assert driver_install._pkg_path_dict["driver"] == "/home/sdkrc3.1.1/musa_driver.deb"


def test_install_driver_with_valid_version(mocker):
    """测试 install 方法在 _name 为 'driver' 且提供有效版本时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "is_uninstalled", return_value=True)
    mocker.patch.object(driver_install, "uninstall")
    mocker.patch.object(driver_install, "install_cmd")
    mocker.patch.object(driver_install, "download")
    mock_gmi_map_version = mocker.patch.object(
        driver_install, "_gmi_map_version", return_value="mapped_version"
    )
    driver_install.install(version="3.1.0")
    assert driver_install._gmi_version == "mapped_version"
    mock_gmi_map_version.assert_called_once_with("3.1.0")


def test_install_driver_with_invalid_version(mocker):
    """测试 install 方法在 _name 为 'driver' 且提供无效版本时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mock_print = mocker.patch("builtins.print")
    with pytest.raises(SystemExit):
        driver_install.install(version="invalid_version")
        mock_print.assert_called_with(
            "Error: Unknown driver version mapping for: invalid_version"
        )


def test_install_with_uninstall_required(mocker):
    """测试 install 方法在需要卸载时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "is_uninstalled", return_value=False)
    mocker.patch.object(driver_install._checker, "check", return_value=(False, "None"))
    mock_uninstall = mocker.patch.object(driver_install, "uninstall")
    mocker.patch.object(driver_install, "download")
    mocker.patch.object(driver_install, "install_cmd")
    driver_install.install(version="3.1.1", allow_force_install=True)
    mock_uninstall.assert_called_once()


def test_install_without_uninstall_required(mocker):
    """测试 install 方法在无需卸载时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "is_uninstalled", return_value=True)
    mock_uninstall = mocker.patch.object(driver_install, "uninstall")
    mocker.patch.object(driver_install, "download")
    mocker.patch.object(driver_install, "install_cmd")
    driver_install.install(version="3.1.1")
    mock_uninstall.assert_not_called()


def test_install_with_success_and_version_match(mocker):
    """测试 install 方法在成功标志和版本匹配时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install._checker, "check", return_value=(True, "OK"))
    mocker.patch.object(driver_install._checker, "get_version", return_value="2.7.0")
    mocker.patch.object(driver_install, "is_uninstalled", return_value=True)
    mock_print = mocker.patch("builtins.print")
    driver_install.install(version="3.1.0")
    mock_print.assert_called_with(
        "\x1b[32mdriver 2.7.0 has already been installed successfully!\x1b[0m"
    )


def test_install_with_version_mismatch(mocker):
    """测试 install 方法在版本不匹配时的行为"""
    container_toolkit_install = PACKAGE_MANAGER["container_toolkit"]
    mock_exit = mocker.patch("sys.exit")
    mocker.patch.object(
        container_toolkit_install._checker, "check", return_value=(True, "OK")
    )
    mocker.patch.object(container_toolkit_install, "is_uninstalled", return_value=True)
    mock_driver_install = mocker.MagicMock()
    mock_driver_install.install.return_value = False
    container_toolkit_install._preinstaller = [mock_driver_install]
    mock_driver_check = mocker.MagicMock()
    mock_driver_check.check.return_value = (True, "OK")
    mock_driver_check.get_version.return_value = "2.7.0"
    mocker.patch.dict(
        "musa_deploy.install.install.CHECKER", {"driver": lambda: mock_driver_check}
    )
    container_toolkit_install.set_driver_target_version("2.7.0")
    mocker.patch.object(container_toolkit_install, "uninstall")
    mocker.patch.object(container_toolkit_install, "download")
    mocker.patch.object(container_toolkit_install, "install_cmd")
    container_toolkit_install.install(version="3.0.1")
    mock_exit.assert_called_once()
    exit_message = mock_exit.call_args[0][0]
    assert (
        "\x1b[91mWarning:\x1b[0mIncompatible driver version detected. Please uninstall the current driver(2.7.0) with command `sudo musa-deploy -u driver`, and try again."
        in exit_message
    )


def test_install_with_no_target_version(mocker):
    """测试 install 方法在未指定目标版本时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install._checker, "check", return_value=(True, "OK"))
    mocker.patch.object(driver_install._checker, "get_version", return_value=None)
    mock_print = mocker.patch("builtins.print")
    driver_install.install()
    mock_print.assert_called_with(
        "\x1b[32mdriver has already been installed successfully!\x1b[0m"
    )


def test_install_with_preinstallers(mocker):
    """测试 install 方法在存在前置安装器时的行为"""
    container_toolkit_install = PACKAGE_MANAGER["container_toolkit"]
    mocker.patch.object(
        container_toolkit_install._checker, "check", return_value=(False, "OK")
    )
    mocker.patch.object(container_toolkit_install, "is_uninstalled", return_value=True)
    mocker.patch.object(container_toolkit_install, "uninstall")
    mocker.patch.object(container_toolkit_install, "download")
    mocker.patch.object(container_toolkit_install, "install_cmd")
    mock_preinstaller = mocker.MagicMock()
    mock_preinstaller.install.return_value = True
    container_toolkit_install._preinstaller = [mock_preinstaller]
    container_toolkit_install.install()
    mock_preinstaller.install.assert_called_once()


def test_install_with_download_and_install_cmd(mocker):
    """测试 install 方法在执行下载和安装命令时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "is_uninstalled", return_value=True)
    mocker.patch.object(driver_install, "uninstall")
    mock_download = mocker.patch.object(driver_install, "download")
    mock_install_cmd = mocker.patch.object(
        driver_install, "install_cmd", return_value=True
    )
    driver_install.install("3.0.1")
    mock_download.assert_called_once()
    mock_install_cmd.assert_called_once()


def test_install_with_gmi_map_version_failure(mocker):
    """测试 install 方法在 _gmi_map_version 抛出异常时的行为"""
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install, "_gmi_map_version")
    mock_print = mocker.patch("builtins.print")
    with pytest.raises(SystemExit):
        driver_install.install(version="invalid_version")
        mock_print.assert_called_with(
            "Error: Unknown driver version mapping for: invalid_version"
        )


# 集成测试：验证模块间协作
@patch.object(DOWNLOADER, "download")
@patch.object(
    DownloadDecompressor,
    "decompress",
    return_value={"driver": "/home/sdkrc3.1.1/musa_driver.deb"},
)
@patch.object(SHELL, "run_cmd_with_error_print")
@patch.object(SHELL, "run_cmd_with_standard_print")
def test_install_and_uninstall_integration(
    mock_run_cmd_with_standard_print,
    mock_run_with_error_print,
    mock_decompress,
    mock_download,
    mocker,
):
    """测试安装和卸载的联调"""
    # 安装
    mocker.patch("sys.exit")
    mocker.patch(
        "musa_deploy.install.install.require_root_privileges_check", return_value=True
    )
    mock_continue_or_exit = mocker.patch(
        "musa_deploy.install.install.continue_or_exit", return_value=True
    )
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install._checker, "check", return_value=(False, "None"))
    driver_install.install(version="3.1.1")
    mock_download.assert_called_once()
    mock_decompress.assert_called_once()
    assert driver_install._pkg_path_dict["driver"] == "/home/sdkrc3.1.1/musa_driver.deb"
    mock_run_with_error_print.assert_any_call(
        "dpkg -i /home/sdkrc3.1.1/musa_driver.deb"
    )
    mock_continue_or_exit.assert_called_once()
    mock_run_cmd_with_standard_print.assert_any_call("reboot")

    # 卸载
    driver_install.uninstall()
    mock_run_with_error_print.assert_any_call("dpkg -P musa")


@patch.object(DOWNLOADER, "download")
@patch.object(
    DownloadDecompressor,
    "decompress",
    return_value={"driver": "/home/sdkrc3.1.1/musa_driver.deb"},
)
@patch.object(SHELL, "run_cmd_with_error_print")
@patch.object(SHELL, "run_cmd_with_standard_print")
def test_update_flow(
    mock_run_cmd_with_standard_print,
    mock_run_with_error_print,
    mock_decompress,
    mock_download,
    mocker,
):
    """测试更新流程"""
    mocker.patch("sys.exit")
    mocker.patch(
        "musa_deploy.install.install.require_root_privileges_check", return_value=True
    )
    mock_continue_or_exit = mocker.patch(
        "musa_deploy.install.install.continue_or_exit", return_value=True
    )
    driver_install = PACKAGE_MANAGER["driver"]
    mocker.patch.object(driver_install._checker, "check", return_value=(False, "None"))
    # 更新
    driver_install.update(version="3.1.1")
    mock_download.assert_called_once()
    mock_decompress.assert_called_once()
    assert driver_install._pkg_path_dict["driver"] == "/home/sdkrc3.1.1/musa_driver.deb"
    mock_run_with_error_print.assert_any_call("dpkg -P musa")
    mock_run_with_error_print.assert_any_call(
        "dpkg -i /home/sdkrc3.1.1/musa_driver.deb"
    )
    mock_continue_or_exit.assert_called_once()
    mock_run_cmd_with_standard_print.assert_any_call("reboot")
