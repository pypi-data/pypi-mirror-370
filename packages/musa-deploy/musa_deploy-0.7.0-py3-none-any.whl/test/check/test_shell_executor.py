from musa_deploy.check.shell_executor import BaseShellExecutor


BASESHELL = BaseShellExecutor()


def test_baseShellExecutor_get_dpkg_package_version_success():
    """assume that mt-container-toolkit is installed, and it's version is 1.9.0-1"""
    version, _, _ = BASESHELL.get_dpkg_package_version("mt-container-toolkit")
    version_groud_truth = "1.9.0-1"
    assert (
        version == version_groud_truth
    ), f"get_dpkg_package_version test failed, assume that mt-container-toolkit is installed and is at version: {version_groud_truth}, but the actual version fetched is {version}"
