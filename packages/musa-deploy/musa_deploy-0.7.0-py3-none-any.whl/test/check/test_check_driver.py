import sys
import os
from musa_deploy.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env
from musa_deploy.utils import FontRed, FontGreen


@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_driver_from_dpkg_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver_Version_From_Dpkg": (
            "2.7.0-rc3-0822",
            "",
            0,
        )
    }
    driver_from_dpkg_ground_truth = """\
Driver_Version_From_Dpkg    Version: 2.7.0-rc3-0822"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_from_dpkg_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_driver_from_dpkg_simulation_in_docker():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver_Version_From_Dpkg": (
            "",
            "dpkg-query: package 'musa' is not installed and no information is available\
Use dpkg --info (= dpkg-deb --info) to examine archive files.",
            1,
        )
    }
    tester.set_simulation_log(simulation_log)
    tester.capture_report_string()
    assert (
        "Driver_Version_From_Dpkg" not in tester._report_string
    ), f"Check the driver inside the container, skip the Driver_Version_From_Dpkg check, and ensure that the string 'Driver_Version_From_Dpkg' is not present in the report, but report is:{tester._report_string}"


def test_check_driver_from_clinfo_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver_Version_From_Clinfo": (
            "Driver Version                                  20241025 release kuae1.3.0_musa3.1.0 c64ecd8ad@20241024",
            "",
            1,
        )
    }
    driver_from_clinfo_ground_truth = """\
Driver_Version_From_Clinfo  Version: 20241025 kuae1.3.0_musa3.1.0"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_from_clinfo_ground_truth)
    tester.test_single_module()


def test_check_driver_version_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver": (
            [
                "Driver Version: 1.0.0",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
            ],
            "",
            0,
        )
    }
    driver_ground_truth = "Driver                      Version: 1.0.0"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_ground_truth)
    tester.test_single_module()


def test_check_driver_mtbios_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver": (
            [
                "Driver Version: 1.0.0",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
            ],
            "",
            0,
        )
    }
    driver_ground_truth = """\
MTBios                      Version: 3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_ground_truth)
    tester.test_single_module()


def test_check_driver_from_clinfo_simulation_err():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver_Version_From_Clinfo": (
            "Number of platforms                               0",
            "",
            0,
        )
    }
    clinfo_ground_truth = """\
Driver_Version_From_Clinfo
    - status: \x1b[91mWARNING\x1b[0m
    - \x1b[32mRecommendation\x1b[0m: Unable to get detailed driver version by clinfo, try 'sudo chmod 777 /dev/dri/render*'."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(clinfo_ground_truth)
    tester.test_single_module()


def test_check_driver_from_driver_simulation_err():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {"Driver": ("Error: failed to load driver.", "", 8)}
    clinfo_ground_truth = """\
Driver
    - status: \x1b[91mFAILED\x1b[0m
    - Info: "Error: failed to load driver."
    - \x1b[32mRecommendation\x1b[0m: Failed to load driver. If any prechecks in the 'Summary' do not pass, please first resolve the errors in the prechecks;
                      if all prechecks pass, then the driver installation was unsuccessful, please manually install the driver again and pay attention
                      to the logs during the installation process."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(clinfo_ground_truth)
    tester.test_single_module()


def test_check_driver_overall_status_failed_color():
    """
    the color of overall status should be red if status is failed
    """
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {"Driver": ("Error: failed to load driver.", "", 8)}
    report_ground_truth = (
        f"{FontGreen('DRIVER CHECK OVERALL Status: ')}{FontRed('FAILED')}"
    )
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(report_ground_truth)
    tester.test_single_module()


def test_check_driver_no_product_name_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver": (
            [
                "Driver Version: 1.0.0",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Product Name: N/A",
                "Product Name: N/A",
                "Product Name: N/A",
                "Product Name: N/A",
                "Product Name: N/A",
                "Product Name: N/A",
                "Product Name: N/A",
                "Product Name: N/A",
                "Subsystem Device ID: 0x0323",
                "Subsystem Device ID: 0x0323",
                "Subsystem Device ID: 0x0323",
                "Subsystem Device ID: 0x0323",
                "Subsystem Device ID: 0x0323",
                "Subsystem Device ID: 0x0323",
                "Subsystem Device ID: 0x0323",
                "Subsystem Device ID: 0x0323",
            ],
            "",
            0,
        )
    }
    driver_ground_truth = "Driver                      Version: 1.0.0"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_ground_truth)
    tester.test_single_module()


def test_check_driver_output_abnomal_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver": (
            "Error: No MT GPU device found.",
            "",
            0,
        )
    }
    driver_ground_truth = "Please check if IOMMU is enabled by running: `sudo musa-deploy -c host`. If not, please enable IOMMU manually based on the instructions provided in the log output of the above command."
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_ground_truth)
    tester.test_single_module()


# TODO(@caizhi): here need more detailed analysis for driver check(lspci log need send to HostChecker)
# def test_check_driver_summary_simulation_err():
#     tester = TestChecker(CheckModuleNames.driver.name)
#     similation_log = {"Lspci": (("", "", 1), None)}
#     summary_ground_truth = """\
# \x1b[91mSummary:\x1b[0
# The \x1b[91mROOT CAUSE\x1b[0m is that the following component check failed. Please follow the corresponding \x1b[91mRecommendation\x1b[0m provided above to take action.
# 1. Lspci                      \x1b[91mFAILED\x1b[0m"""
#     tester.set_simulation_log(similation_log)
#     tester.set_module_ground_truth(summary_ground_truth)
##     tester.test_single_module()


if __name__ == "__main__":
    # test_check_driver_from_clinfo_simulation()
    # test_check_driver_version_simulation()
    # test_check_driver_mtbios_simulation()
    test_check_driver_from_dpkg_simulation()
