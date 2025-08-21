import os
import re
from abc import ABC, abstractmethod
from ..config.yaml_read import YAML
from .utils import (
    CheckStatus,
    Status,
    HostModule,
    DriverModule,
    MTLinkModule,
    IBModule,
    SmartIOModule,
    ContainerToolkitModule,
    MusaModule,
    TorchMusaModule,
    vLLMModule,
    CheckModuleNames,
    EXECUTED_ON_HOST_FLAG,
    SOLUTION_INDENTATION_LENGTH,
)
from musa_deploy.utils import (
    GPU_ARCH_MAP,
    GPU_TYPE_MAP,
    GPU_MEMORY_MAP,
    fetch_last_n_logs,
)


CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
VERSION_REQUIREMENTS_FILE = os.path.join(
    CURRENT_FOLDER, "../config/version_requirements.yaml"
)


def match_mtgpu_arch(lspci_info: list) -> list:
    """
    get mtgpu model from lspci info with GPU_ARCH_MAP and GPU_TYPE_MAP

    Args:
        lspci_info (list): lspci info

    Returns:
        list: mtgpu model info, eg: ["mp_21:S70"] (list length depends on the number of Gpus in the machine)
    """
    arch_list = [i.split(":")[-1] for i in lspci_info]
    gpu_type = list()
    for arch in arch_list:
        arch_in_arch_map = arch in GPU_ARCH_MAP
        arch_in_type_map = arch in GPU_TYPE_MAP
        if arch_in_arch_map and arch_in_type_map:
            # Both maps contain the arch
            gpu_type.append(f"{GPU_ARCH_MAP[arch]}:{GPU_TYPE_MAP[arch]}")
        elif arch_in_arch_map and not arch_in_type_map:
            # Only GPU_ARCH_MAP contains the arch
            gpu_type.append(f"{GPU_ARCH_MAP[arch]}:N/A")
        elif not arch_in_arch_map and arch_in_type_map:
            # Only GPU_TYPE_MAP contains the arch
            gpu_type.append(f"N/A:{GPU_TYPE_MAP[arch]}")

    return gpu_type


def extract_musa_version_query_info(
    component_name: str, musa_version_query_info: str
) -> dict:
    """
    extract musa info from musa_version_query command, eg: musa_toolkits, mcc, mccl, etc.

    Args:
        - component_name (str): The name of the component to extract information for, eg: musa_toolkits, mcc, mccl, etc.
        - musa_version_query_info (str): The string containing the output of the musa_version_query command.

    Returns:
        - dict: A dictionary containing the extracted information for the specified component, eg:
                {
                    "version": "2.1.0",
                    "git branch": "release-kuae-1.2.0",
                    "git tag": "No tag",
                    "commit id": "af514d1954d2c5adeab5ce0d88a44b5ea7a73296",
                    "commit date": "2024-07-03 15:47:19 +0800"
                }
    """
    pattern = component_name + r":\s*\{([\s\S]*?)\}"
    match_component = re.search(pattern, musa_version_query_info)
    if match_component:
        component_content = match_component.group(1)
        key_value_pattern = r'"(.*?)":\s*"([^"]*?)"'
        component_dict = {
            key: value
            for key, value in re.findall(key_value_pattern, component_content)
        }
    else:
        component_dict = {}
    return component_dict


class Diagnoser(ABC):

    def __init__(self, tag: str = None) -> None:
        """ """
        self._check_status = dict()
        self._log = None
        self._tag = tag
        self._version_requirements = YAML(VERSION_REQUIREMENTS_FILE)
        # The following override of the global variable is only for simulating tests, please set this environment variable cautiously.
        global EXECUTED_ON_HOST_FLAG
        if os.getenv("EXECUTED_ON_HOST_FLAG") == "False":
            EXECUTED_ON_HOST_FLAG = False
        if os.getenv("EXECUTED_ON_HOST_FLAG") == "True":
            EXECUTED_ON_HOST_FLAG = True

    def init_log(self, log: str):
        self._log = log

    def update_check_status(self, check_status: dict):
        self._check_status.update(check_status)

    def diagnose_version_match(self):
        if self._tag in self._version_requirements.yaml_data.keys():
            # get module name, eg: Driver_Version_From_Dpkg
            module_name, _ = self._version_requirements.get_sub_key_list(self._tag)
            # module has been installed if needs version match
            if (
                module_name in self._check_status.keys()
                and self._check_status[module_name].status != Status.UNINSTALLED
            ):

                module_version = self._check_status[module_name].version
                special_version_dict = self._version_requirements.get_dict_in_list(
                    self._tag, module_version
                )

                if not special_version_dict:
                    self._check_status[module_name].solution += (
                        (
                            "\n" + " " * SOLUTION_INDENTATION_LENGTH
                            if self._check_status[module_name].solution
                            else ""
                        )
                        + f"The current {module_name} version may not be an official release version. The version compatibility check has been skipped. If necessary, please manually check the version compatibility."
                    )
                else:
                    modules_to_match_dict = special_version_dict["dependency"]

                    for k, v in modules_to_match_dict.items():
                        if k in [
                            ContainerToolkitModule.mtml.name,
                            ContainerToolkitModule.sgpu_dkms.name,
                            DriverModule.Driver_Version_From_Clinfo.name,
                        ] and (
                            self._check_status[k].version != v
                            if isinstance(v, str)
                            else self._check_status[k].version not in v
                        ):  # TODO(wangkang):临时绕过clinfo问题
                            if (
                                not EXECUTED_ON_HOST_FLAG
                                and k != DriverModule.Driver_Version_From_Clinfo.name
                            ):
                                self._check_status[module_name].solution += (
                                    f"\n{' '*SOLUTION_INDENTATION_LENGTH}The {k} version details are unavailable inside the container. Please check its version in the host environment using: dpkg -s {k if k in ['mtml', 'sgpu_dkms'] else 'musa'}. "
                                    f"The {k} version compatible with the current {module_name} version is {v}."
                                )
                            else:
                                self._check_status[module_name].status = Status.MISMATCH
                                self._check_status[module_name].solution = (
                                    f"The {k} version is incompatible with MUSA. The current {module_name} requires {k}'s version is {v}, but is {self._check_status[k].version}."
                                )
                        if HostModule.Kernel.name in self._check_status:
                            if (
                                k == "unsupported_kernel"
                                and self._check_status[
                                    HostModule.Kernel.name
                                ].version.split("(")[0]
                                in v
                            ):
                                self._check_status[module_name].status = Status.MISMATCH
                                self._check_status[module_name].solution = (
                                    f"the version of {k} is {self._check_status[HostModule.Kernel.name].version}, but the version of {HostModule.Kernel.name} that matches the current {module_name} version is {v}"
                                )
                            elif (
                                k == "supported_kernel"
                                and self._check_status[
                                    HostModule.Kernel.name
                                ].version.split("(")[0]
                                not in v
                            ):
                                self._check_status[module_name].solution = (
                                    f"\nATTENTION: The current {module_name} version is {module_version}, and the known system kernel matched version is {(', '.join(v))}"
                                )
                        if (
                            k
                            in [
                                MusaModule.MUSAToolkits.name,
                                TorchMusaModule.PyTorch.name,
                            ]
                            and self._check_status[k].version not in v
                        ):
                            self._check_status[module_name].status = Status.MISMATCH
                            self._check_status[module_name].solution = (
                                f"the version of {k} is {self._check_status[k].version}, but the version of {k} that matches the current {module_name} version is {v}"
                            )
                        if (
                            k in [TorchMusaModule.TorchVision.name]
                            and self._check_status[k].version not in v
                        ):
                            self._check_status[module_name].solution = (
                                f"\nThe torchvision version does not match the torch_musa version, please install the correct torchvision version:{v} or torchvision will not work"
                            )
        return self._check_status

    def diagnose_dependency(self):
        pass

    def post_diagnose(self):
        self.diagnose_version_match()
        self.diagnose_dependency()

        return self._check_status

    @abstractmethod
    def run(self) -> CheckStatus:
        pass
        return self._check_status


class HostDiagnoser(Diagnoser):
    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)

    def diagnose_host_memory(self):
        if HostModule.host_memory.name in self._log:
            memory_size = self._log[HostModule.host_memory.name]
            host_memory_status = CheckStatus(HostModule.host_memory.name, tag=self._tag)
            total_size_gb = 0
            for item in memory_size[0]:
                if re.match(r"Size:\s*(\d+)\s*(MB|GB)", item):
                    size_str = item.split(":")[1].strip()
                    if "MB" in size_str:
                        size_gb = int(size_str.replace("MB", "").strip()) / 1024
                    elif "GB" in size_str:
                        size_gb = int(size_str.replace("GB", "").strip())
                    total_size_gb += size_gb
            host_memory_status.host_memory_size = total_size_gb
            self._check_status[HostModule.host_memory.name] = host_memory_status
            return host_memory_status

    def diagnose_iommu(self) -> None:
        """
        Status.SUCCESS: iommu on or (iommu off and memory < 256G)
        Status.WARNING：iommu off and memory > 256GB
        Status.ATTENTION: Can't get iommu info in /etc/default/grub
        """
        if HostModule.IOMMU.name in self._log:
            iommu_status = CheckStatus(name=HostModule.IOMMU.name, tag=self._tag)
            (_, _, code_from_log), (_, error_form_dmesg, code_from_dmesg) = self._log[
                HostModule.IOMMU.name
            ]

            if not EXECUTED_ON_HOST_FLAG:
                iommu_status.status = Status.UNKNOWN
                iommu_status.solution = f"The command `musa-deploy` is currently being executed inside a container. To check {HostModule.IOMMU.name}, please run the command outside the container."
                self._check_status[HostModule.IOMMU.name] = iommu_status
                return

            if not code_from_log or not code_from_dmesg:
                iommu_status.status = Status.SUCCESS
                iommu_status.iommu_enable = True
            elif "Operation not permitted" in error_form_dmesg:
                iommu_status.status = Status.UNKNOWN
                iommu_status.solution = "Please run musa-deploy with `sudo`, or execute it with root privileges to get complete IOMMU information."
            else:
                iommu_status.iommu_enable = False

                host_memory_size = self._check_status[
                    HostModule.host_memory.name
                ].host_memory_size
                if not host_memory_size > 256:
                    iommu_status.status = Status.SUCCESS
                else:
                    iommu_status.status = Status.WARNING
                    iommu_status.solution = f"""The memory is {host_memory_size} (>256GB), it is recommended to enable IOMMU. See:
                      https://github.com/MooreThreads/tutorial_on_musa/blob/master/FAQ/environment_FAQ.md."""

            self._check_status[HostModule.IOMMU.name] = iommu_status

    def diagnose_kernel(self) -> None:
        """
        Status.SUCCESS: get kernel version by 'uname -r'
        Status.WARNING: Can't get kernel version
        """
        if HostModule.Kernel.name in self._log:
            kernel_status = CheckStatus(name=HostModule.Kernel.name, tag=self._tag)
            kernel_out, kernel_err, kernel_code = self._log[HostModule.Kernel.name]
            if kernel_out:
                # kernel_out, example: 5.4.0-42-generic
                kernel_status.version = f"{kernel_out}{'(Docker)' if not EXECUTED_ON_HOST_FLAG else '(System)'}"
                kernel_status.status = Status.SUCCESS
            else:
                kernel_status.status = Status.WARNING
                kernel_status.info = kernel_err
                kernel_status.solution = "Unable to get kernel version, please check your kernel version manually."

            self._check_status[HostModule.Kernel.name] = kernel_status

    def diagnose_cpu(self) -> None:
        """
        Status.SUCCESS: cpu_arch is x86_64
        Status.Warning：cpu_arch is "arm" or "aarch64" , or Unable to get CPU info by 'lscpu'
        """
        if HostModule.CPU.name in self._log:
            cpu_dict = CheckStatus(name=HostModule.CPU.name, tag=self._tag)
            cpu_out, err, _ = self._log[HostModule.CPU.name]
            if cpu_out:
                cpu_info = {
                    re.split(r"[:：]", item)[0]
                    .strip(): re.split(r"[:：]", item)[1]
                    .strip()
                    for item in cpu_out
                }
                cpu_vendor = (
                    cpu_info.get("Vendor ID")
                    if cpu_info.get("Vendor ID")
                    else cpu_info.get("厂商 ID")
                )
                cpu_arch = (
                    cpu_info.get("Architecture")
                    if cpu_info.get("Architecture")
                    else cpu_info.get("架构")
                )
                cpu_model = (
                    cpu_info.get("Model name")
                    if cpu_info.get("Model name")
                    else cpu_info.get("型号名称")
                )
                cpu_dict.version = cpu_model
                cpu_dict.CPU_Name = f"{cpu_vendor} {cpu_arch}"
            else:
                cpu_dict.info = err
                cpu_dict.status = Status.WARNING
                cpu_dict.solution = (
                    "Unable to get CPU information, please check your CPU manually."
                )

            if "x86_64" in cpu_dict.CPU_Name.lower():
                cpu_dict.status = Status.SUCCESS
            elif (
                "arm" in cpu_dict.version.lower()
                or "aarch64" in cpu_dict.version.lower()
            ):
                cpu_dict.status = Status.ATTENTION
                cpu_dict.solution = f"The CPU architecture is {cpu_arch}, not X86_64 , which may cause the problem of unsuitable MUSA GPU."
            else:
                cpu_dict.status = Status.WARNING

            self._check_status[HostModule.CPU.name] = cpu_dict

    def diagnose_package(self, dependency_name: str):
        """
        Status.SUCCESS: get package version(installed)
        Status.UNINSTALLED: not install
        """
        if dependency_name in self._log:
            status = CheckStatus(name=dependency_name, tag=self._tag)
            out, _, _ = self._log[dependency_name]
            if out:
                status.version = out
            else:
                if dependency_name == HostModule.LinuxModulesExtra.name:
                    dependency_name = f"linux-modules-extra-{os.uname().release}"
                if EXECUTED_ON_HOST_FLAG:
                    status.status = Status.UNINSTALLED
                    status.solution = f"Please install {dependency_name} first or check the {dependency_name} package is installed correctly."
                else:
                    status.status = Status.UNKNOWN
                    status.solution = f"The command `musa-deploy` is currently being executed inside a container. To check {dependency_name}, please run the command outside the container."

            self._check_status[dependency_name] = status

    def diagnose_docker(self) -> None:
        """
        Status.SUCCESS: docker's status is ruuning
        Status.FAILED: docker is installed and it's active is not running
        Status.INSTALL: not install
        """
        if HostModule.Docker.name in self._log:
            docker_dict = CheckStatus(name=HostModule.Docker.name, tag=self._tag)
            docker_version, docker_status = self._log[HostModule.Docker.name]
            # docker installed
            if docker_version[0]:
                docker_dict.version = f"{docker_version[0]}({docker_status[0]})"
                # docker's status is not running
                if "active" != docker_status[0]:
                    docker_dict.solution = "Docker's status is not running, please manually check your docker status."
                    docker_dict.status = Status.WEAK_FAILED
            # docker not installed
            else:
                if EXECUTED_ON_HOST_FLAG:
                    docker_dict.status = Status.WEAK_UNINSTALLED
                    docker_dict.solution = "Please install docker first, refer to the command: `sudo apt install docker.io`."
                else:
                    docker_dict.status = Status.UNKNOWN
                    docker_dict.solution = f"The command `musa-deploy` is currently being executed inside a container. To check {HostModule.Docker.name}, please run the command outside the container."
            self._check_status[HostModule.Docker.name] = docker_dict

    def _diagnoser_pcie(self, pcie_speed, pcie_dict):
        """
        get PCIE version from lspci info
        Status.SUCCESS: get PCIE info and pcie version
        Status.WARNING: get no PCIE info or unknown PCIE version
        """
        match = re.search(r"Speed (\d+)GT/s", pcie_speed[0])
        # no output
        if pcie_speed[2] == 1 and not pcie_speed[0]:
            pcie_dict.status = Status.WARNING
            pcie_dict.solution = "Please run musa-deploy with `sudo`, or execute it with root privileges to get PCIE version."
        # has output but no match
        elif pcie_speed[0] and not match:
            pcie_dict.status = Status.WARNING
            pcie_dict.solution = "Speed value not found in Lspci log."
            return pcie_dict
        # has output and matched
        elif match:
            speed = int(match.group(1))
            pcie_dict.speed = speed
            if speed == 32:
                pcie_dict.version = "Gen5"
            elif speed == 16:
                pcie_dict.version = "Gen4"
            elif speed == 8:
                pcie_dict.version = "Gen3"
            else:
                pcie_dict.version = "Unknown"
                pcie_dict.status = Status.WARNING
                pcie_dict.solution = f"Speed is ${speed}, but is unknown PCIE version!"
        return pcie_dict

    def diagnose_lspci(self) -> None:
        """
        Status.SUCCESS: get gpu arch version
        Status.WARNING: get lspci info, but got unknown arch version
        Status.FAILED: get no info by 'lspci'
        """
        if HostModule.Lspci.name in self._log:
            lspci_dict = CheckStatus(HostModule.Lspci.name, tag=self._tag)
            pcie_dict = CheckStatus(HostModule.PCIE.name, tag=self._tag)
            pcie_dict.version = "Unknown"
            lspci_info, pcie_speed = self._log[HostModule.Lspci.name]
            if lspci_info[2]:
                if EXECUTED_ON_HOST_FLAG:
                    lspci_dict.status = Status.FAILED
                    lspci_dict.log = lspci_info[1]
                    lspci_dict.solution = "Unable to get PCIE related information, please check your device."
                else:
                    lspci_dict.status = Status.UNKNOWN
                    lspci_dict.log = lspci_info[1]
                    lspci_dict.solution = f"The command `musa-deploy` is currently being executed inside a container. To check {HostModule.Lspci.name}, please run the command outside the container."
            else:
                pcie_dict = self._diagnoser_pcie(pcie_speed, pcie_dict)
                lspci_dict.number = len(lspci_info[0]) // 2
                lspci_dict.info = lspci_info[0]
                gpu_type = match_mtgpu_arch(lspci_info[0])
                if gpu_type:
                    lspci_dict.GPU_Type = gpu_type
                else:
                    lspci_dict.GPU_Type = ["N/A"]
                    lspci_dict.status = Status.WARNING
                    lspci_dict.solution = "Unable to match GPU architecture, please run `mthreads-gmi -q` for GPU-related information if the driver is installed correctly."

            self._check_status[HostModule.PCIE.name] = pcie_dict
            self._check_status[HostModule.Lspci.name] = lspci_dict

    def diagnose_OS(self) -> None:
        """
        Status.SUCCESS: 'Ubuntu'
        Status.ATTENTION: not Ubuntu system
        Status.WARNING: get not info by 'lsb_release -a'
        """
        if HostModule.OS.name in self._log:
            system_dict = CheckStatus(HostModule.OS.name, tag=self._tag)
            out, err, code = self._log[HostModule.OS.name]
            if out:
                system_dict.version = out

                if "Ubuntu" in out:
                    system_dict.status = Status.SUCCESS
                else:
                    system_dict.status = Status.ATTENTION
                    system_dict.solution = f"The current system is {out}, not Ubuntu, which may cause the problem of unsuitable MUSA GPU."
            else:
                system_dict.status = Status.WARNING
                system_dict.info = err
                system_dict.solution = "Unable to get system information, please check your system manually."
            self._check_status[HostModule.OS.name] = system_dict

    def diagnose_InCluster(self):
        if HostModule.InCluster.name in self._log:
            _, _, returncode = self._log[HostModule.InCluster.name]
            InCluster_status = CheckStatus(HostModule.InCluster.name, tag=self._tag)
            InCluster_status.status = (
                Status.ATTENTION if not returncode else Status.SUCCESS
            )
            self._check_status[HostModule.InCluster.name] = InCluster_status

    def diagnose_RenderGroup(self):
        if HostModule.RenderGroup.name in self._log:
            render_group_info, is_render_exits = self._log[HostModule.RenderGroup.name]
            RenderGroup_status = CheckStatus(HostModule.RenderGroup.name, tag=self._tag)
            if "render" in render_group_info[0]:
                RenderGroup_status.status = Status.SUCCESS
            else:
                RenderGroup_status.status = Status.WARNING
                if not is_render_exits:
                    RenderGroup_status.solution = "The 'render' group not found, please check system environment manually."
                else:
                    RenderGroup_status.solution = "Current user is not in the 'render' group, run: `usermod -aG render,video $USER` to add."
            self._check_status[HostModule.RenderGroup.name] = RenderGroup_status

    def diagnose_DriverToolkitFile(self):
        if HostModule.DriverToolkitFile.name in self._log:
            driver_toolkit_file = CheckStatus(
                HostModule.DriverToolkitFile.name, tag=self._tag
            )
            is_exists = self._log[HostModule.DriverToolkitFile.name]
            driver_toolkit_file.status = Status.WARNING if is_exists else Status.SUCCESS
            self._check_status[HostModule.DriverToolkitFile.name] = driver_toolkit_file

    def run(self) -> CheckStatus:

        # stage 1. cpu, host_memory
        self.diagnose_cpu()
        self.diagnose_host_memory()

        # stage 2. os, kernel, lspci, iommu
        self.diagnose_OS()
        self.diagnose_kernel()
        self.diagnose_lspci()
        self.diagnose_iommu()

        # stage 3. DKMS, lightdm
        self.diagnose_package(HostModule.DKMS.name)
        self.diagnose_package(HostModule.Lightdm.name)
        self.diagnose_package(HostModule.LinuxModulesExtra.name)

        # stage 4. docker
        self.diagnose_docker()

        # stage 5. InCluster, render group, DriverToolkitFile
        self.diagnose_InCluster()
        self.diagnose_RenderGroup()
        self.diagnose_DriverToolkitFile()
        return self._check_status


class SmartIODiagnoser(Diagnoser):

    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)

    def diagnose_SmartIO(self) -> None:
        if SmartIOModule.mt_peermem.name in self._log:
            SmartIO_dict = CheckStatus(SmartIOModule.mt_peermem.name, tag=self._tag)
            if EXECUTED_ON_HOST_FLAG:
                SmartIO_package, SmartIO_lsmod = self._log[
                    SmartIOModule.mt_peermem.name
                ]
                if SmartIO_package[0]:
                    SmartIO_dict.version = SmartIO_package[0]
                    if SmartIO_lsmod[0]:
                        SmartIO_dict.status = Status.SUCCESS
                    else:
                        SmartIO_dict.status = Status.FAILED
                        SmartIO_dict.solution = "mt-peermem is installed, but it does not work. Please restart the system and run 'lsmod | grep mt_peermem' to verify whether it works."
                else:
                    SmartIO_dict.status = Status.UNINSTALLED
                    SmartIO_dict.solution = "It has been detected that you do not have mt-peermem installed. If you need multi-card communication, install it."

            else:
                SmartIO_dict.status = Status.UNKNOWN
                SmartIO_dict.solution = f"The command `musa-deploy` is currently being executed inside a container. To check {self._tag}, please run the command outside the container."
            self._check_status[SmartIOModule.mt_peermem.name] = SmartIO_dict

    def run(self) -> CheckStatus:
        self.diagnose_SmartIO()
        return self._check_status


class DriverDiagnoser(Diagnoser):

    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)

    def _process_gmi_q_log(self, log) -> dict:
        """Convert the output of the mthreads-gmi -q command to dict"""
        log_dict = {}
        for item in log:
            if ":" in item:
                k, v = item.split(":")[0].strip(), item.split(":")[1].strip()
                if k not in log_dict.keys():
                    log_dict.update({k: [v]})
                else:
                    log_dict[k].append(v)
        return log_dict

    def diagnose_gmi(self) -> None:
        """
        gmi:
            Status.SUCCESS: mthreads-gmi -q 正常输出
            Status.UNINSTALLED：not install driver
            Atatus.FAILED: get no info by 'mthreads-gmi -q'
        mtbios:
            Status.SUCCESS: gmi success and get mtbios version, version is consistent
            Status.ATTENTION: gmi success and get mtbios version, version is not consistent
            Status.ATTENTION: gmi success and get no mtbios version
        """
        if DriverModule.Driver.name in self._log:
            gmi_dict = CheckStatus(name=DriverModule.Driver.name, tag=self._tag)
            driver_out, driver_err, driver_code = self._log[DriverModule.Driver.name]
            # normal output(returncode: 0)
            if not driver_code and isinstance(
                driver_out, list
            ):  # if driver_out is nomal output, it's type should be list.
                # get gmi output dict
                out_dict = self._process_gmi_q_log(driver_out)
                # driver version
                gmi_dict.version = out_dict["Driver Version"][0]

                # mtbios
                gmi_dict.mtbios_version = out_dict["MTBios Version"]
                # MTBios version is not consistent
                if len(set(out_dict["MTBios Version"])) != 1:
                    gmi_dict.status = Status.WARNING
                    gmi_dict.solution = f"The MTBios version is not consistent: {gmi_dict.mtbios_version}."
                # gpu model
                if "N/A" in out_dict["Product Name"]:
                    device_id = out_dict["Subsystem Device ID"][0][2:]
                    gmi_dict.GPU_Type = [
                        "MTT " + GPU_TYPE_MAP.get(device_id)
                        for _ in out_dict["Product Name"]
                    ]
                else:
                    gmi_dict.GPU_Type = out_dict["Product Name"]
                # gpu mem
                memory_list = out_dict["Total"]
                gpu_standard_memory = GPU_MEMORY_MAP.get(
                    gmi_dict.GPU_Type[0]
                )  # eg: S80 --> 16384
                gpu_actual_memory = [
                    int(re.search(r"\d+", mem_str).group(0)) for mem_str in memory_list
                ]
                gmi_dict.gpu_memory = {
                    "standard_memory": gpu_standard_memory,
                    "actual_memory": gpu_actual_memory,
                }
                # gpu memory size is not consistent with standard memory size
                if not gpu_standard_memory:
                    gmi_dict.status = Status.ATTENTION
                    gmi_dict.solution = f"The standard memory size of {out_dict['Product Name'][0]} GPU has not been recorded."
                elif gpu_standard_memory != gpu_actual_memory[0]:
                    gmi_dict.status = Status.WARNING
                    gmi_dict.solution = f"The GPU memory size of {out_dict['Product Name'][0]} GPU is {gpu_actual_memory},  not consistent with the standard memory size: {gpu_standard_memory}."

            # no output(return: 0)
            elif not driver_code and not driver_out:
                gmi_dict.status = Status.FAILED
                gmi_dict.info = driver_err
                gmi_dict.solution = "The mthreads-gmi command produces no output."

            # output abnormally(return: not 0 or 0)(规避这样情况：('Error: No MT GPU device found.', '', 0))
            elif driver_out:
                gmi_dict.status = Status.FAILED
                gmi_dict.info = driver_out
                if "failed to initialize mtml" in driver_out:
                    gmi_dict.solution = "please try: 'usermod -aG render,video $USER', then exit and re-enter the Shell window."
                elif "No MT GPU device found." in driver_out:
                    gmi_dict.solution = "Please check if IOMMU is enabled by running: `sudo musa-deploy -c host`. If not, please enable IOMMU manually based on the instructions provided in the log output of the above command."
                elif "failed to load driver" in driver_out:
                    gmi_dict.solution = """Failed to load driver. If any prechecks in the \'Summary\' do not pass, please first resolve the errors in the prechecks;
                      if all prechecks pass, then the driver installation was unsuccessful, please manually install the driver again and pay attention
                      to the logs during the installation process."""

            # uninstall driver
            elif driver_code and "not found" in driver_err:
                gmi_dict.status = Status.UNINSTALLED
                gmi_dict.info = driver_err
                gmi_dict.solution = "The command mthreads-gmi is not recognized, please install driver manually."
            self._check_status[DriverModule.Driver.name] = gmi_dict

    def diagnose_dpkg_driver(self) -> None:
        """
        Status.UNINSTALLED: not installed
        Status.SUCCESS: get driver version
        """
        if (
            DriverModule.Driver_Version_From_Dpkg.name in self._log
            and EXECUTED_ON_HOST_FLAG
        ):
            dpkg_driver_dict = CheckStatus(
                name=DriverModule.Driver_Version_From_Dpkg.name, tag=self._tag
            )
            self.dpkg_driver_version = self._log[
                DriverModule.Driver_Version_From_Dpkg.name
            ][0]

            # get driver version info
            if self.dpkg_driver_version:
                dpkg_driver_dict.status = Status.SUCCESS
                dpkg_driver_dict.version = self.dpkg_driver_version
            # no driver_version info(not installed driver)
            else:
                # TODO(@caizhi): It is not possible to distinguish whether it is not installed or if the installation failed here; the log collection needs to be improved.
                dpkg_driver_dict.status = Status.UNINSTALLED
                dpkg_driver_dict.solution = f"Unable to get driver info from dpkg{'.' if EXECUTED_ON_HOST_FLAG else ', please get detailed driver version on host with command `dpkg -s musa`.'}"

            self._check_status[DriverModule.Driver_Version_From_Dpkg.name] = (
                dpkg_driver_dict
            )

    def _get_driver_version_from_clinfo(self, clinfo_out) -> list:
        match = re.search(r"Driver Version\s+(.+)", clinfo_out)
        if match:
            return match.group(
                1
            ).split()  # eg: ['20240703', 'release', 'release-kuae-1.2.0', '4dc3b4b36@20240701']

    def diagnose_clinfo(self) -> None:
        """
        Status.UNINSTALLED: not install clinfo
        Status.SUCCESS: get driver version
        Status.WARNING: just got info 'Number of platforms'
        """
        if DriverModule.Driver_Version_From_Clinfo.name in self._log:
            clinfo_dict = CheckStatus(
                name=DriverModule.Driver_Version_From_Clinfo.name, tag=self._tag
            )
            clinfo_out, clinfo_err, clinfo_code = self._log[
                DriverModule.Driver_Version_From_Clinfo.name
            ]

            # uninstall
            if "Command 'clinfo' not found" in clinfo_err:
                clinfo_dict.status = Status.UNINSTALLED
                clinfo_dict.info = clinfo_err
                clinfo_dict.solution = "The clinfo command is not recognized, please install it: \n \t sudo apt install clinfo"
            # installed
            else:
                driver_detailed_version = self._get_driver_version_from_clinfo(
                    clinfo_out
                )
                # get driver_version info
                if driver_detailed_version:
                    clinfo_dict.status = Status.SUCCESS
                    clinfo_dict.version = " ".join(driver_detailed_version[0:3:2])
                # no driver_version info
                else:
                    clinfo_dict.status = Status.WARNING
                    clinfo_dict.solution = "Unable to get detailed driver version by clinfo, try 'sudo chmod 777 /dev/dri/render*'."

            self._check_status[DriverModule.Driver_Version_From_Clinfo.name] = (
                clinfo_dict
            )

    def run(self) -> CheckStatus:
        self.diagnose_gmi()
        self.diagnose_dpkg_driver()
        self.diagnose_clinfo()
        return self._check_status


class MTLinkDiagnoser(Diagnoser):

    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)

    def diagnose_mtlink(self):
        # TODO(@caizhi): here need more detailed analysis about mtlink status
        if MTLinkModule.MTLink.name in self._log:
            out, err, code = self._log[MTLinkModule.MTLink.name]
            mtlink_dict = CheckStatus(name=MTLinkModule.MTLink.name, tag=self._tag)
            if code:
                mtlink_dict.status = Status.FAILED
                mtlink_dict.info = out
                mtlink_dict.solution = "An error occurred during the MTLink check. Please use the command `mthreads-gmi mtlink -s` to view detailed information."
            else:
                mtlink_dict.status = Status.SUCCESS

            self._check_status[MTLinkModule.MTLink.name] = mtlink_dict

    def run(self) -> CheckStatus:
        self.diagnose_mtlink()
        return self._check_status


class IBDiagnoser(Diagnoser):
    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)

    def _extract_infiniband_info(self, ib_dict, ibstat_out) -> None:
        """
        extract infiniband info from ibstat output
        get the number of active and down infiniband devices
        """
        active_pattern = r"State: Active"
        active_matches = re.findall(active_pattern, ibstat_out)
        down_pattern = r"State: Down"
        down_matches = re.findall(down_pattern, ibstat_out)

        ib_dict.info = {
            "Link": "InfiniBand",
            "Active Port Number": len(active_matches),
            "Down Port Number": len(down_matches),
        }
        if len(down_matches) > 0:
            ib_dict.status = Status.WARNING
            ib_dict.solution = f"There are {len(down_matches)} InfiniBand ports with status of 'DOWN'. Please manually check the InfiniBand status."
        else:
            ib_dict.status = Status.SUCCESS

        return ib_dict

    def diagnose_ib(self) -> None:
        if IBModule.ibstat.name in self._log:
            ib_dict = CheckStatus(name=IBModule.ibstat.name, tag=self._tag)
            ibstat_out, ibstat_err, ibstat_code = self._log[IBModule.ibstat.name]
            # ibstat is not installed
            if "not found" in ibstat_err:
                ib_dict.status = Status.UNINSTALLED
                ib_dict.info = ibstat_err
                ib_dict.solution = "The ibstat command is not recognized, please install it: 'sudo apt install infiniband-diags'."
            # ibstat has no output
            elif not ibstat_out:
                ib_dict.status = Status.WARNING
                ib_dict.solution = "Get no information about infiniband, please check the network device."
            elif ibstat_out:
                ib_dict = self._extract_infiniband_info(ib_dict, ibstat_out)

            self._check_status[IBModule.ibstat.name] = ib_dict

    def run(self) -> CheckStatus:
        self.diagnose_ib()
        return self._check_status


class ContainerToolkitDiagnoser(Diagnoser):

    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)

    def get_package_status(self, name: str):
        package_status = CheckStatus(name=name, tag=self._tag)
        out, err, return_code = self._log[name]
        if out:
            package_status.version = out
            package_status.status = Status.SUCCESS
        else:
            package_status.status = Status.UNINSTALLED
            package_status.solution = f"Please install {name} first."

        return package_status

    def diagnose_docker_runtime(self) -> None:
        """
        docker_runtime:
            Status.SUCCESS: docker_runtime check is ok
            Status.FAILED: docker_runtime check failed
        """
        # 0. EXECUTED_ON_HOST_FLAG or not
        # 1. test mthreads-gmi
        # 2. containertoolkit version
        # 3. mtml version
        # 4. sgpu_dkms version
        # 5. is binding

        if ContainerToolkitModule.container_toolkit.name in self._log:
            # get container_toolkit version
            toolkit_status = self.get_package_status(
                ContainerToolkitModule.container_toolkit.name
            )
            if EXECUTED_ON_HOST_FLAG:
                assert (
                    ContainerToolkitModule.test_mthreads_gmi.name in self._log
                ), "Log of testing mthreads-gmi inside container is not found!"
                test_gmi_log = self._log[ContainerToolkitModule.test_mthreads_gmi.name]

                # test mthreads_gmi inside container failed
                if test_gmi_log[2]:
                    # 1. mtml install or not
                    assert (
                        ContainerToolkitModule.mtml.name in self._log
                    ), "Log of testing mtml is not found!"
                    self._check_status[ContainerToolkitModule.mtml.name] = (
                        self.get_package_status(ContainerToolkitModule.mtml.name)
                    )
                    # 2. sgpu_dkms install or not
                    assert (
                        ContainerToolkitModule.sgpu_dkms.name in self._log
                    ), "Log of testing sgpu-dkms is not found!"
                    self._check_status[ContainerToolkitModule.sgpu_dkms.name] = (
                        self.get_package_status(ContainerToolkitModule.sgpu_dkms.name)
                    )
                    # 3. is bound or not
                    assert (
                        ContainerToolkitModule.is_binding.name in self._log
                    ), "Log of testing whether docker runtime is bound is not found!"
                    toolkit_status.info = test_gmi_log[1]
                    if (
                        self._check_status[ContainerToolkitModule.mtml.name].status
                        == Status.UNINSTALLED
                        or self._check_status[
                            ContainerToolkitModule.sgpu_dkms.name
                        ].status
                        == Status.UNINSTALLED
                        or toolkit_status.status == Status.UNINSTALLED
                    ):
                        toolkit_status.solution = "Please keep 'mtml', 'sgpu-dkms', 'container_toolkit' package installed successfully first."
                    else:
                        if (
                            self._log[ContainerToolkitModule.is_binding.name][0]
                            != "mthreads"
                        ):
                            toolkit_status.solution = "Bind the Moore thread container runtime to Docker: (cd /usr/bin/musa && sudo ./docker setup $PWD), and try again."
                        elif not self._log[ContainerToolkitModule.is_dir_exist.name]:
                            toolkit_status.solution = "The directory '/usr/bin/musa' does not exist, causing the mt-container-toolkit package to be corrupted. Please run `sudo musa-deploy -i container_toolkit` to reinstall mt-container-toolkit."
                    # Here Status.SUCCESS only means contain_toolkit package installed successfully, but overall status is failed, so we need override the final status
                    if toolkit_status.status == Status.SUCCESS:
                        toolkit_status.status = Status.FAILED
                else:
                    toolkit_status.status = Status.SUCCESS
            else:
                toolkit_status.status = Status.UNKNOWN
                toolkit_status.solution = f"The command `musa-deploy` is currently being executed inside a container. To check {ContainerToolkitModule.container_toolkit.name}, please run the command outside the container."
            self._check_status[ContainerToolkitModule.container_toolkit.name] = (
                toolkit_status
            )

    def diagnose_dependency(self):
        docker_dict = self._check_status[DriverModule.Driver.name]
        container_toolkit_dict = self._check_status[
            ContainerToolkitModule.container_toolkit.name
        ]
        # docker not work or not installed
        if docker_dict.status in [Status.WEAK_UNINSTALLED, Status.WEAK_FAILED]:
            container_toolkit_dict.solution = "mt-container-toolkit relies on docker, so make sure docker is installed correctly and its status is active."
            container_toolkit_dict.status = Status.FAILED
            docker_dict.status = (
                Status.FAILED
                if docker_dict.status == Status.WEAK_FAILED
                else Status.UNINSTALLED
            )

    def run(self) -> CheckStatus:
        self.diagnose_docker_runtime()
        return self._check_status


class MusaDiagnoser(Diagnoser):
    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)

    def diagnose_musa(self) -> None:
        """
        - musa uninstalled(by musaInfo log)
        - musa installed(by musaInfo log)
            get musa_toolkits version(by musa_version_query log)
            - musaInfo test failure
            - musaInfo test success
                - test musa demo(by test_musa.mu test)

        """
        if MusaModule.MUSAToolkits.name in self._log:
            musa_dict = CheckStatus(name=MusaModule.MUSAToolkits.name, tag=self._tag)
            (musaInfo_out, musaInfo_err, musaInfo_code), musa_installed_flag = (
                self._log[MusaModule.MUSAToolkits.name]
            )
            if not musa_installed_flag:
                # not installed musa_toolkit
                musa_dict.status = Status.UNINSTALLED
                musa_dict.solution = "Unable to find /usr/local/musa directory, please check if musa_toolkits is installed."
            else:
                # means installed musa_toolkit
                # get musa_toolkit version
                musa_version_out, musa_version_err, musa_version_code = self._log[
                    MusaModule.musa_version.name
                ]
                musa_dict.version = "UNKNOWN"
                if not musa_version_code:
                    musa_toolkit_info_dict = extract_musa_version_query_info(
                        "musa_toolkits", musa_version_out
                    )
                    if musa_toolkit_info_dict:
                        musa_dict.version = (
                            musa_toolkit_info_dict["version"]
                            + "+"
                            + musa_toolkit_info_dict["commit id"]
                        )
                else:
                    musa_dict.info = musa_version_out
                    musa_dict.status = Status.WARNING
                    musa_dict.solution = "The `musaInfo` execution was successful, but retrieving the musa_runtime version using the `musa_version_query` command failed."
                # musaInfo test failed
                if musaInfo_code:
                    musa_dict.status = Status.FAILED
                    musa_dict.info = musaInfo_out
                    if musa_dict.solution:
                        musa_dict.solution += "\nThe execution result of `musaInfo` is abnormal, please check if musa_toolkits version matches the driver, or if the kernel version supports it."
                    else:
                        musa_dict.solution = "The execution result of `musaInfo` is abnormal, please check if musa_toolkits version matches the driver, or if the kernel version supports it."
                else:
                    # musaInfo test success, test musa demo
                    test_musa_out, test_musa_err, test_musa_code = self._log[
                        MusaModule.test_musa.name
                    ]
                    if test_musa_code:
                        musa_dict.status = Status.FAILED
                        musa_dict.info = test_musa_out
                        if musa_dict.solution:
                            musa_dict.solution += "\nThe execution result of `musaInfo` is normal, but the `test_musa.mu` test failed, please check if the musa_runtime version and the driver version are compatible."
                        else:
                            musa_dict.solution = "The execution result of `musaInfo` is normal, but the `test_musa.mu` test failed, please check if the musa_runtime version and the driver version are compatible."
                    else:
                        musa_dict.status = Status.SUCCESS
            self._check_status[MusaModule.MUSAToolkits.name] = musa_dict

    def run(self) -> CheckStatus:
        self.diagnose_musa()
        return self._check_status


class TorchMusaDiagnoser(Diagnoser):

    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)

    def _diagnose_package(
        self, name: str = None, git_version_module: str = None
    ) -> None:
        # 1. pip version (pip list|grep)
        # 2. git version (import xxx; xxx.version.git_version)
        # 3. test_demo.py
        # installed, get version
        check_status = CheckStatus(name=name, tag=self._tag)
        run_demo_log = self._log[name]
        pip_version, git_version = self._log[git_version_module]
        if pip_version[0] and not pip_version[2]:
            pip_version_value = ""
            for line in pip_version[0]:
                if "Version: " in line:
                    pip_version_value = line.split()[
                        -1
                    ]  # eg: 'Version: 2.2.0a0+git8ac9b20' -> 2.2.0a0+git8ac9b20
            commit_id = None
            if git_version[0] and not git_version[2]:
                commit_id = git_version[0]
                pip_version_without_git = pip_version_value.split("+")[
                    0
                ]  # remove git version, eg: 1.9.0+d0c0c0 -> 1.9.0
                check_status.version = pip_version_without_git + "+" + commit_id
            else:
                check_status.version = pip_version_value

            if run_demo_log[2]:
                if (
                    name == TorchMusaModule.TorchVision.name
                    or name == TorchMusaModule.TorchAudio.name
                ):
                    check_status.status = Status.WEAK_FAILED
                else:
                    check_status.status = Status.FAILED
                check_status.info = fetch_last_n_logs(run_demo_log[1])
            else:
                check_status.status = Status.SUCCESS
        else:
            if (
                name == TorchMusaModule.TorchVision.name
                or name == TorchMusaModule.TorchAudio.name
            ):
                check_status.status = Status.WEAK_UNINSTALLED
            else:
                check_status.status = Status.UNINSTALLED
            check_status.solution = f"Unable to get the {name} package version, please manually check whether {name} package is installed."
        self._check_status[name] = check_status

    def diagnose_pytorch(self) -> None:
        if TorchMusaModule.PyTorch.name in self._log:
            self._diagnose_package(
                TorchMusaModule.PyTorch.name,
                TorchMusaModule.PyTorch_version.name,
            )

    def diagnose_torch_musa(self) -> None:
        if TorchMusaModule.Torch_musa.name in self._log:
            self._diagnose_package(
                TorchMusaModule.Torch_musa.name,
                TorchMusaModule.Torch_musa_version.name,
            )

    def diagnose_torch_vision(self) -> None:
        if TorchMusaModule.TorchVision.name in self._log:
            self._diagnose_package(
                TorchMusaModule.TorchVision.name,
                TorchMusaModule.TorchVision_version.name,
            )

    def diagnose_torch_audio(self) -> None:
        if TorchMusaModule.TorchAudio.name in self._log:
            self._diagnose_package(
                TorchMusaModule.TorchAudio.name,
                TorchMusaModule.TorchAudio_version.name,
            )

    def run(self) -> CheckStatus:
        self.diagnose_pytorch()
        self.diagnose_torch_musa()
        self.diagnose_torch_vision()
        self.diagnose_torch_audio()
        return self._check_status


class vLLMDiagnoser(Diagnoser):
    def __init__(self, tag: str = None) -> None:
        super().__init__(tag)
        self.support_gpu_type = ["S4000"]

    def diagnose_mttransformer(self) -> None:
        """
        only check mttransformer version
        """
        if vLLMModule.MTTransformer.name in self._log:
            mtt_dict = CheckStatus(name=vLLMModule.MTTransformer.name, tag=self._tag)
            mtt_version = self._log[vLLMModule.MTTransformer.name]
            # get mttransformer version
            if mtt_version[0]:
                mtt_dict.status = Status.SUCCESS
                mtt_dict.version = mtt_version[0][1].split(": ")[-1]
            else:
                mtt_dict.status = Status.UNINSTALLED
                mtt_dict.solution = "Unable to get the mttransformer package version, please install it before testing the vllm environment."
            self._check_status[vLLMModule.MTTransformer.name] = mtt_dict

    def diagnose_vllm(self) -> None:
        """
        if vllm check failed, find the reason
        """
        if vLLMModule.vLLM.name in self._log:
            vllm_dict = CheckStatus(name=vLLMModule.vLLM.name, tag=self._tag)
            vllm_status = self._log[vLLMModule.vLLM.name]
            vllm_version = self._log[vLLMModule.vLLM_version.name]
            if vllm_version[0]:
                vllm_dict.version = vllm_version[0]
            else:
                vllm_dict.status = Status.UNINSTALLED
            # vllm_demo test failed
            if vllm_status[2]:
                if vllm_version[0]:
                    vllm_dict.status = Status.FAILED
                vllm_dict.info = vllm_status[1].rstrip()
                if "No module named 'vllm'" in vllm_status[1]:
                    vllm_dict.solution = """Please confirm whether the vllm source code exists (default location is '/home/workspace/vllm_mtt'). If existed, please execute 'export PYTHONPATH=/home/workspace/vllm_mtt/:$PYTHONPATH' and try it again."""
            else:
                vllm_dict.status = Status.SUCCESS
            self._check_status[vLLMModule.vLLM.name] = vllm_dict

    def diagnose_dependency(self) -> None:
        """
        check gpu type: vllm only support s4000
        """
        if DriverModule.Driver.name in self._check_status:
            if self._check_status[DriverModule.Driver.name].status == Status.SUCCESS:
                gpu_type = (
                    self._check_status[DriverModule.Driver.name]
                    .GPU_Type[0]
                    .split(" ")[-1]
                )
                if gpu_type not in self.support_gpu_type:
                    self._check_status[vLLMModule.vLLM.name].solution = (
                        f"The current GPU type is {gpu_type}, which is not supported by vllm, please use S4000 or newer GPU."
                    )

    def run(self) -> CheckStatus:
        self.diagnose_mttransformer()
        self.diagnose_vllm()
        return self._check_status


if __name__ == "__main__":
    host_diagnoser = HostDiagnoser(CheckModuleNames.host.name)
    pass
