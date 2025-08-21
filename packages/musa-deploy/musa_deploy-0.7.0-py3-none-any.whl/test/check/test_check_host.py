import sys
import os
from musa_deploy.check.utils import CheckModuleNames
from musa_deploy.utils import FontGreen, FontRed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, GREEN_PREFIX, RED_PREFIX, COLOR_SUFFIX, set_env


def test_check_CPU_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "CPU": (
            [
                "Architecture:                    x86_64",
                "CPU op-mode(s):                  32-bit, 64-bit",
                "Byte Order:                      Little Endian",
                "Address sizes:                   39 bits physical, 48 bits virtual",
                "CPU(s):                          12",
                "On-line CPU(s) list:             0-11",
                "Thread(s) per core:              2",
                "Core(s) per socket:              6",
                "Socket(s):                       1",
                "NUMA node(s):                    1",
                "Vendor ID:                       GenuineIntel",
                "CPU family:                      6",
                "Model:                           151",
                "Model name:                      12th Gen Intel(R) Core(TM) i5-12400",
                "Stepping:                        5",
                "CPU MHz:                         973.846",
                "CPU max MHz:                     4400.0000",
                "CPU min MHz:                     800.0000",
                "BogoMIPS:                        4992.00",
                "Virtualization:                  VT-x",
                "L1d cache:                       288 KiB",
                "L1i cache:                       192 KiB",
                "L2 cache:                        7.5 MiB",
                "L3 cache:                        18 MiB",
                "NUMA node0 CPU(s):               0-11",
                "Vulnerability Itlb multihit:     Not affected",
                "Vulnerability L1tf:              Not affected",
                "Vulnerability Mds:               Not affected",
                "Vulnerability Meltdown:          Not affected",
                "Vulnerability Spec store bypass: Mitigation; Speculative Store Bypass disabled via prctl and seccomp",
                "Vulnerability Spectre v1:        Mitigation; usercopy/swapgs barriers and __user pointer sanitization",
                "Vulnerability Spectre v2:        Mitigation; Enhanced IBRS, IBPB conditional, RSB filling",
                "Vulnerability Srbds:             Not affected",
                "Vulnerability Tsx async abort:   Not affected",
                "Flags:                           fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf tsc_known_freq pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb cat_l2 invpcid_single cdp_l2 ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid rdt_a rdseed adx smap clflushopt clwb intel_pt sha_ni xsaveopt xsavec xgetbv1 xsaves dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp hwp_pkg_req umip pku ospke waitpkg gfni vaes vpclmulqdq rdpid movdiri movdir64b md_clear flush_l1d arch_capabilities",
            ],
            "",
            0,
        )
    }
    CPU_ground_truth = """\
CPU                         Name: GenuineIntel x86_64
                              Version: 12th Gen Intel(R) Core(TM) i5-12400"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(CPU_ground_truth)
    tester.test_single_module()


def test_check_host_memory_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "host_memory": (
            [
                "Non-Volatile Size: None",
                "Volatile Size: None",
                "Cache Size: None",
                "Logical Size: None",
                "Size: 16384 MB",
                "Non-Volatile Size: None",
                "Volatile Size: 16 GB",
                "Cache Size: None",
                "Logical Size: None",
                "Non-Volatile Size: None",
                "Volatile Size: None",
                "Cache Size: None",
                "Logical Size: None",
                "Size: 16384 MB",
                "Non-Volatile Size: None",
                "Volatile Size: 16 GB",
                "Cache Size: None",
                "Logical Size: None",
            ],
            "",
            0,
        )
    }
    host_memory_ground_truth = "Host Memory                 Size(GB): 32.0"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(host_memory_ground_truth)
    tester.test_single_module()


def test_check_OS_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"OS": ("Ubuntu 20.04.1 LTS", "", 0)}
    OS_ground_truth = "OS                          Version: Ubuntu 20.04.1 LTS"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(OS_ground_truth)
    tester.test_single_module()


def test_check_Kernel_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"Kernel": ("5.4.0-42-generic", "", 0)}
    Kernel_ground_truth = "Kernel                      Version: 5.4.0-42-generic"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(Kernel_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_PCIE_simulation_negative():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"Lspci": (("", "", 1), None)}
    PCIE_ground_truth = "PCIE                        Version: Unknown"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(PCIE_ground_truth)
    tester.test_single_module()


def test_check_Lspci_simulation_8_s4000():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "Lspci": (
            (
                [
                    "08:00.0 0300: 1ed5:0323",
                    "08:00.1 0401: 1ed5:03ff",
                    "09:00.0 0300: 1ed5:0323",
                    "09:00.1 0401: 1ed5:03ff",
                    "0e:00.0 0300: 1ed5:0323",
                    "0e:00.1 0401: 1ed5:03ff",
                    "11:00.0 0300: 1ed5:0323",
                    "11:00.1 0401: 1ed5:03ff",
                    "32:00.0 0300: 1ed5:0323",
                    "32:00.1 0401: 1ed5:03ff",
                    "38:00.0 0300: 1ed5:0323",
                    "38:00.1 0401: 1ed5:03ff",
                    "3b:00.0 0300: 1ed5:0323",
                    "3b:00.1 0401: 1ed5:03ff",
                    "3c:00.0 0300: 1ed5:0323",
                    "3c:00.1 0401: 1ed5:03ff",
                ],
                "",
                0,
            ),
            ("", "", 1),
        )
    }
    lspci_ground_truth = """\
Lspci                       GPU_Type: mp_22:S4000
                                        mp_22:S4000
                                        mp_22:S4000
                                        mp_22:S4000
                                        mp_22:S4000
                                        mp_22:S4000
                                        mp_22:S4000
                                        mp_22:S4000"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(lspci_ground_truth)
    tester.test_single_module()


def test_check_Lspci_simulation_negative_1():
    """get not lspci information"""
    os.environ["EXECUTED_ON_HOST_FLAG"] = "True"

    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"Lspci": (("", "", 1), None)}
    lspci_ground_truth = f"""\
Lspci
    - status: \x1b[91mFAILED\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: Unable to get PCIE related information, please check your device."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(lspci_ground_truth)
    tester.test_single_module()


def test_check_Lspci_simulation_negative_2():
    """device id not in GPU_TYPE_MAP and GPU_ARCH_MAP"""
    os.environ["EXECUTED_ON_HOST_FLAG"] = "True"

    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "Lspci": (
            (["01:00.0 0300: 1ed5:0322", "01:00.1 0401: 1ed5:03ff"], "", 0),
            ("LnkSta:\tSpeed 16GT/s (downgraded), Width x16 (ok)", "", 0),
        ),
    }
    lspci_ground_truth = f"""\
Lspci                       GPU_Type: N/A
    - status: {RED_PREFIX}WARNING{COLOR_SUFFIX}
    - Info: "['01:00.0 0300: 1ed5:0322', '01:00.1 0401: 1ed5:03ff']"
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: Unable to match GPU architecture, please run `mthreads-gmi -q` for GPU-related information if the driver is installed correctly."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(lspci_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_Lspci_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"Lspci": (("", "/bin/sh: 1: lspci: not found\n", 1), None)}
    lspci_ground_truth = f"""\
Lspci
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: The command `musa-deploy` is currently being executed inside a container. To check Lspci, please run the command outside the container."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(lspci_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_IOMMU_simulation_negative():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"IOMMU": (("", "", 1), ("", "", 1))}
    IOMMU_ground_truth = """IOMMU:                      Status: disable"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(IOMMU_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_IOMMU_simulation_no_iommu_file():
    """
    1. 无/var/log/dmesg文件
    2. 无root 权限获取dmesg 命令信息
    """
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "IOMMU": (
            ("", "cat: /var/log/dmesg: No such file or directory\n", 1),
            ("", "dmesg: read kernel buffer failed: Operation not permitted", 1),
        )
    }
    IOMMU_ground_truth = f"""\
IOMMU
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: Please run musa-deploy with `sudo`, or execute it with root privileges to get complete IOMMU information."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(IOMMU_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_IOMMU_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "IOMMU": (
            ("", "grep: /etc/default/grub: No such file or directory\n", 2),
            ("", "", 1),
        )
    }
    IOMMU_ground_truth = f"""\
IOMMU
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: The command `musa-deploy` is currently being executed inside a container. To check IOMMU, please run the command outside the container."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(IOMMU_ground_truth)
    tester.test_single_module()


def test_check_DKMS_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"DKMS": ("2.8.1-5ubuntu2", "", 0)}
    DKMS_ground_truth = "DKMS                        Version: 2.8.1-5ubuntu2"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(DKMS_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_DKMS_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"DKMS": ("", "", 0)}
    DKMS_ground_truth = f"""\
DKMS
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: The command `musa-deploy` is currently being executed inside a container. To check DKMS, please run the command outside the container."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(DKMS_ground_truth)
    tester.test_single_module()


def test_check_Lightdm_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"Lightdm": ("1.30.0-0ubuntu4~20.04.2", "", 0)}
    Lightdm_ground_truth = (
        "Lightdm                     Version: 1.30.0-0ubuntu4~20.04.2"
    )
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(Lightdm_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_Lightdm_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"Lightdm": ("", "", 0)}
    Lightdm_ground_truth = f"""\
Lightdm
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: The command `musa-deploy` is currently being executed inside a container. To check Lightdm, please run the command outside the container."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(Lightdm_ground_truth)
    tester.test_single_module()


def test_check_LinuxModulesExtra_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"LinuxModulesExtra": ("5.4.0-42.46", "", 0)}
    Lightdm_ground_truth = "LinuxModulesExtra           Version: 5.4.0-42.46"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(Lightdm_ground_truth)
    tester.test_single_module()


def test_check_Docker_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "Docker": [
            ("20.10.21", "", 0),
            (
                "active",
                "",
                0,
            ),
        ]
    }
    Docker_ground_truth = "Docker                      Version: 20.10.21('active')"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(Docker_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_Docker_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "Docker": [
            ("", "/bin/sh: 1: docker: not found\n", 0),
            (
                "",
                "System has not been booted with systemd as init system (PID 1). Can't operate.\nFailed to connect to bus: Host is down\n",
                0,
            ),
        ]
    }
    Docker_ground_truth = f"""\
Docker
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: The command `musa-deploy` is currently being executed inside a container. To check Docker, please run the command outside the container."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(Docker_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_Summary_simulation():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {"Lspci": (("", "", 1), None)}
    lspci_ground_truth = f"""\
Lspci
    - status: \x1b[91mFAILED\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: Unable to get PCIE related information, please check your device."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(lspci_ground_truth)
    tester.set_is_successful_ground_truth(is_successful_ground_truth=False)
    summary_ground_truth = """\
.*Summary:.*\
The .*ROOT CAUSE.* is that the following component check failed. Please follow the corresponding .*Recommendation.* provided above to take action.\
.*Lspci                      .*FAILED.*"""
    tester.set_summary(summary_ground_truth)

    tester.test_all()


def test_check_render_group_has_user():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "RenderGroup": (
            (
                "chenyu : chenyu adm cdrom sudo dip video plugdev render lpadmin lxd sambashare docker ollama",
                "",
                0,
            ),
            True,
        )
    }
    ground_truth = "RenderGroup                Status: SUCCESS"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(ground_truth)
    tester.test_single_module()


def test_check_render_group_has_no_user():
    tester = TestChecker(CheckModuleNames.host.name)
    simulation_log = {
        "RenderGroup": (
            (
                "chenyu : chenyu adm cdrom sudo dip video plugdev lpadmin lxd sambashare docker ollama",
                "",
                0,
            ),
            True,
        )
    }
    ground_truth = f"""\
RenderGroup
    - status: {FontRed("WARNING")}
    - {FontGreen("Recommendation")}: Current user is not in the 'render' group, run: `usermod -aG render,video $USER` to add."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_CPU_simulation()
    # test_check_host_memory_simulation()
    # test_check_Lspci_simulation_negative()
    # test_check_IOMMU_simulation_negative()
    # test_check_Summary_simulation()
    # test_check_Lspci_simulation_8_s4000()
    # test_check_Lightdm_simulation_inside_container()
    # test_check_Docker_simulation_inside_container()
    # test_check_DKMS_simulation_inside_container()
    # test_check_IOMMU_simulation_inside_container()
    # test_check_Lspci_simulation_inside_container()
