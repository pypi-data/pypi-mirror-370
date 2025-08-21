import sys
import os
import pytest
from musa_deploy.check.utils import CheckModuleNames, BaseShellExecutor
from musa_deploy.utils import FontRed, FontGreen

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_musa_installed_inside_container():
    """
    check musa installed, whether it works or not

    Simulation Log Details:
        - `simulation_log["MUSAToolkits"]`: A tuple where the second element
          (`True` or `False`) signifies the installation status.
        - other log do not impact the installation check
    """
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [("", "", 0), True],
        "musa_version": (
            """\
musa_toolkits:
{
        "version":      "3.0.0",
        "git branch":   "dev3.0.0",
        "git tag":      "No tag",
        "commit id":    "f50264844211b581e1d9b0dab2447243c8d4cfb0",
        "commit date":  "2024-06-21 15:20:10 +0800
}""",
            "",
            0,
        ),
        "test_musa": ("", "", 0),
    }
    musa_ground_truth = "MUSAToolkits                Version: 3.0.0+f502648"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_musa_uninstalled_inside_container():
    """
    check musa uninstalled, whether it works or not
    see more in function above: test_check_musa_installed_inside_container
    """
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [("", "", 0), False],
        "musa_version": (
            """\
musa_toolkits:
{
        "version":      "3.0.0",
        "git branch":   "dev3.0.0",
        "git tag":      "No tag",
        "commit id":    "f50264844211b581e1d9b0dab2447243c8d4cfb0",
        "commit date":  "2024-06-21 15:20:10 +0800
}""",
            "",
            0,
        ),
        "test_musa": ("", "", 0),
    }
    musa_ground_truth = f"""\
MUSAToolkits
    - status: {FontRed('UNINSTALLED')}
    - {FontGreen("Recommendation")}: Unable to find /usr/local/musa directory, please check if musa_toolkits is installed."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_musa_failed_version_match_unrecorded():
    """
    ground:
    1. check musa failed for its version not matched with the driver
    2. cur musa version in log not recorded
    """
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [
            (
                """\
\ncompiler: mcc
error: 'system has unsupported display driver / musa driver combination'(803) at /home/jenkins/agent/workspace/compute_musa_pkg_gitlab/musa_toolkit/MUSA-Runtime/src/tools/musaInfo.cpp:155
error: API returned error code.
error: TEST FAILED""",
                "",
                1,
            ),
            True,
        ],
        "musa_version": (
            """\
musa_toolkits:
{
        "version":      "3.0.0",
        "git branch":   "dev3.0.0",
        "git tag":      "No tag",
        "commit id":    "f50264844211b581e1d9b0dab2447243c8d4cfb0",
        "commit date":  "2024-06-21 15:20:10 +0800
}""",
            "",
            0,
        ),
        "test_musa": (
            [
                "MUSA Error:",
                "Error code: 803",
                "Error text: system has unsupported display driver / musa driver combination",
            ],
            "",
            1,
        ),
    }
    musa_ground_truth = f"""\
MUSAToolkits                Version: 3.0.0+f502648
    - status: {FontRed('FAILED')}
    - Info: "
compiler: mcc
error: 'system has unsupported display driver / musa driver combination'(803) at /home/jenkins/agent/workspace/compute_musa_pkg_gitlab/musa_toolkit/MUSA-Runtime/src/tools/musaInfo.cpp:155
error: API returned error code.
error: TEST FAILED\"
    - {FontGreen('Recommendation')}: The execution result of `musaInfo` is abnormal, please check if musa_toolkits version matches the driver, or if the kernel version supports it.
                      The current MUSAToolkits version may not be an official release version. The version compatibility check has been skipped. If necessary, please manually check the version compatibility."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


@pytest.mark.skipif(
    BaseShellExecutor().get_dpkg_package_version("musa")[0] == "2.7.0-rc3-0822",
    reason="Driver version should not be 2.7.0-rc3-0822",
)
def test_check_musa_failed_driver_version_unmatched():
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [
            (
                "\ncompiler: mcc\n\x1b[31merror: 'system has unsupported display driver / musa driver combination'(803) at /home/jenkins/workspace/compute_musa_pkg_gitlab@2/musa_toolkit/MUSA-Runtime/src/tools/musaInfo.cpp:155\x1b[0m\n\x1b[31merror: API returned error code.\nerror: TEST FAILED\n\x1b[0m",
                "",
                1,
            ),
            True,
        ],
        "musa_version": (
            'musa_toolkits:\n{\n\t"version":\t"3.1.0",\n\t"git branch":\t"kuae1.3.0_musa3.1.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"38fe8761d291e32cad642435d9f84c97e4a37bba",\n\t"commit date":\t"2024-09-05 19:33:56 +0800"\n}\nCUB:\n{\n\t"version":\t"1.12.1",\n\t"git branch":\t"musa-1.12.1",\n\t"commit id":\t"5ffbaa4336090806eacfb46394cc8b66cea2b0e5",\n\t"commit date":\t"2024-09-13 16:27:37 +0800"\n}\nThrust:\n{\n\t"version":\t"1.12.1",\n\t"git branch":\t"musa-1.12.1",\n\t"commit id":\t"5a5e67602f52056122186cd5c07d3fc540274ea6",\n\t"commit date":\t"2024-09-14 09:00:20 +0800"\n}\nmcc:\n{\n\t"version":\t"3.1.0",\n\t"git branch":\t"kuae1.3.0_musa3.1.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"baf70da0ba9f1a95a844726d8b2c28a1365b886a",\n\t"commit date":\t"2024-10-08 16:20:58 +0800"\n}\nmccl:\n{\n\t"version":\t"2.11.4",\n\t"build archs":\t"22",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_mccl1.7.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"3354f892e15c13ef74b6d7d1bee317c11f9d0af6",\n\t"commit date":\t"2024-06-18 11:21:07 +0800"\n}\nmuPP:\n{\n\t"version":\t"1.7.0",\n\t"build archs":\t"21;22",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_muPP1.7.0",\n\t"git tag":\t"20241024_develop",\n\t"commit id":\t"f0e7e1c596943e2fe98e14ff096e3c2f2c877247",\n\t"commit date":\t"2024-08-23 10:42:21 +0800"\n}\nmublas:\n{\n\t"version":\t"1.6.0",\n\t"build archs":\t"21,22",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_mublas1.6.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"7bd80754907ffe182da297f54737c74f6e4d4e09",\n\t"commit date":\t"2024-09-30 11:42:09 +0800"\n}\nmudnn:\n{\n\t"version":\t"2.7.0",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_mudnn2.7.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"2fa2f81bf0d77fa977ee398f37a3fdfc6d18cfb1",\n\t"commit date":\t"2024-09-14 16:31:08 +0800"\n}\nmufft:\n{\n\t"version":\t"1.6.0",\n\t"build archs":\t"21;22",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_muFFT1.6.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"a4790e6ac030a68fb033928c54b2d5044d33cf9e",\n\t"commit date":\t"2024-08-23 10:33:45 +0800"\n}\nmurand:\n{\n\t"version":\t"1.0.0",\n\t"build archs":\t"21;22",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_muRand1.0.0",\n\t"git tag":\t"20241024_develop",\n\t"commit id":\t"bc218b10bf4ab6454fe03816297478391ee6d503",\n\t"commit date":\t"2024-05-17 15:37:47 +0800"\n}\nmusify:\n{\n\t"version":\t"1.0.0",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_musify1.0.0",\n\t"commit id":\t"d0720f523c8744a882484be081133054ebd9012f",\n\t"commit date":\t"2024-08-23 11:19:27 +0800"\n}\nmusolver:\n{\n\t"version":\t"1.0.0",\n\t"build archs":\t"21,22",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_musolver1.0.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"65e4a393fa32b27068a993d8bf080645dd16f534",\n\t"commit date":\t"2024-08-29 10:20:23 +0800"\n}\nmusparse:\n{\n\t"version":\t"1.1.0",\n\t"build archs":\t"21,22",\n\t"git branch":\t"kuae1.3.0_musa3.1.0_musparse1.1.0",\n\t"git tag":\t"20240909_develop",\n\t"commit id":\t"73a84b13534251f7d0ea4d832c9f11839914c59a",\n\t"commit date":\t"2024-08-23 10:32:58 +0800"\n}\nmusa_runtime:\n{\n\t"version":\t"3.1.0",\n\t"git branch":\t"kuae1.3.0_musa3.1.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"7b1fcc028ea2604d0571afb18b3662c25edd1512",\n\t"commit date":\t"2024-10-24 06:47:08 +0000"\n}\ndriver_dependency:\n{\n\t"git branch":\t"kuae1.3.0_musa3.1.0",\n\t"git tag":\t"No tag",\n\t"commit id":\t"c64ecd8ad4fa3fd696a5eba63f01e9c8b42c7924",\n\t"commit date":\t"2024-10-24 06:42:43 +0000"\n}\n',
            "",
            0,
        ),
        "test_musa": (
            [
                "MUSA Error:",
                "Error code: 803",
                "Error text: system has unsupported display driver / musa driver combination",
            ],
            "",
            1,
        ),
    }
    musa_ground_truth = f"""\
0.MUSAToolkits                Version: 3.1.0+38fe876
    - status: {FontRed("MISMATCH")}
    - Info: "
compiler: mcc
\x1b[31merror: 'system has unsupported display driver / musa driver combination'(803) at /home/jenkins/workspace/compute_musa_pkg_gitlab@2/musa_toolkit/MUSA-Runtime/src/tools/musaInfo.cpp:155\x1b[0m
\x1b[31merror: API returned error code.
error: TEST FAILED
\x1b[0m"
    - {FontGreen('Recommendation')}: The Driver_Version_From_Clinfo version is incompatible with MUSA. The current MUSAToolkits requires Driver_Version_From_Clinfo's version is 20241025 kuae1.3.0_musa3.1.0, but is"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_musa_installed_inside_container()
