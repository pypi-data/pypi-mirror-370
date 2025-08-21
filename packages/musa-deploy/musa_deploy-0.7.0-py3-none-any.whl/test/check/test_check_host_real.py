import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../musa_deploy"))
)
from musa_deploy.check.utils import CheckModuleNames
from test.utils import TestChecker


def check_host_S80():
    # tester = TestChecker(CheckModuleNames.host.name)
    # tester.test_all()
    print("======s80========")


def check_host_S3000():
    # tester = TestChecker(CheckModuleNames.host.name)
    # tester.test_all()
    print("======s3000========")


def check_host_S4000():
    tester = TestChecker(CheckModuleNames.host.name)
    ground_truth = """\
=====================================================================
======================== MOORE THREADS CHECK ========================
=====================================================================
\x1b[32mHOST CHECK OVERALL Status: \x1b[0mSUCCESSFUL
0.CPU                         Version: GenuineIntel x86_64
1.host_memory
2.OS                          Version: Ubuntu 22.04.5 LTS
3.Kernel                      Version: 5.15.0-105-generic
4.PCIE                        Version: Unknown
    - status: \x1b[91mWARNING\x1b[0m
    - Recommendation: Please run musa-deploy with 'sudo', or execute it with 'root' privileges to get PCIE version.
5.Lspci
6.IOMMU:                      True
7.DKMS                        Version: 2.8.7-2ubuntu2.2
8.Lightdm                     Version: 1.30.0-0ubuntu5
9.Docker                      Version: 24.0.7
=====================================================================
"""
    tester.set_report_ground_truth(ground_truth)
    tester.test_whole_report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "device", type=str, help="device type (e.g., s80, s3000, s4000, s5000)"
    )
    args = parser.parse_args()
    if args.device == "s80":
        check_host_S80()
    elif args.device == "s3000":
        check_host_S3000()
    elif args.device == "s4000":
        check_host_S4000()
    else:
        raise ValueError(
            f"Provided argument {args.device} is not supported, only 's80'，'s3000', 's4000' is supported!"
        )
