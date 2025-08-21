from abc import ABC, abstractmethod
import copy
import os
import platform
from typing import Tuple
from .diagnoser import (
    HostDiagnoser,
    DriverDiagnoser,
    ContainerToolkitDiagnoser,
    MusaDiagnoser,
    TorchMusaDiagnoser,
    MTLinkDiagnoser,
    IBDiagnoser,
    SmartIODiagnoser,
    vLLMDiagnoser,
)
from .shell_executor import (
    ShellExecutor,
    MusaShellExecutor,
    TorchMusaShellExecutor,
    vLLMShellExecutor,
    DockerShellExecutor,
)
from .utils import (
    Status,
    PrintCheckStatus,
    CheckModuleNames,
    HostModule,
    DriverModule,
    MTLinkModule,
    IBModule,
    SmartIOModule,
    ContainerToolkitModule,
    MusaModule,
    TorchMusaModule,
    vLLMModule,
    EXECUTED_ON_HOST_FLAG,
    DRIVERTOOLKIT_PATH,
)

from musa_deploy.utils import (
    CHECK_TITLE,
    REPORT_END_LINE,
    SEPARATION_LINE,
    FontGreen,
    FontRed,
)


class Checker(ABC):

    def __init__(self, check_list: list = list(), container_name: str = None) -> None:
        """ """
        self._tag = ""
        self._container_name = container_name
        self._version_name = None
        self._check_list = check_list
        self._injected_log = dict()
        self._log = dict()
        self._check_status = dict()
        self._total_check_status = dict()
        self._root_cause_status = dict()
        self._shell = None
        self._diagnoser = None
        self._precheckers = list()
        self._is_successful = True
        self._has_uninstalled = False
        self._has_failed = False
        self._has_dependency_failed = False
        # used for report
        self._status_index = 0
        # Automatically detect whether the current environment is
        # in a Docker container or on the host.
        if not EXECUTED_ON_HOST_FLAG:
            if (
                self._container_name
            ):  # if in docker, self._container_name should be None
                print(
                    FontRed(
                        "Warning: When using the musa-deploy tool within a container, the -c parameter should be passed alone, not both -c and --container."
                    )
                )
                exit()

        if self._container_name and not DockerShellExecutor.is_container_running(
            self._container_name
        ):
            print(
                FontRed(
                    f"Warning: The container {self._container_name} status is not ruuning, please start it and try again."
                )
            )
            exit()

    @abstractmethod
    def inspect(self):
        """
        get log from ShellExecutor
        """
        pass

    def precheck(self):
        for checker in self._precheckers:
            check, check_status = checker.check()
            if checker._has_failed or checker._has_dependency_failed:
                self._has_dependency_failed = True
            self._total_check_status.update(check_status)
        return self._total_check_status

    def inject_inspect_log(self, injected_log: dict):
        """
        Leave a backdoor here for everyone to manually set up the log.
        'injected_log' will be updated to self._log.
        """
        self._injected_log = injected_log

    def _find_root_cause(self):
        if self._is_successful:
            return None

        root_cause = dict()
        for key, status in self._total_check_status.items():
            if status.status == Status.UNINSTALLED:
                self._root_cause_status.update({key: status})

        prechecker_find_root_cause = False
        for checker in self._precheckers:
            root_cause = checker._find_root_cause()
            if root_cause:
                self._root_cause_status.update(root_cause)
                prechecker_find_root_cause = True
        if prechecker_find_root_cause:
            return root_cause

        for key, status in self._check_status.items():
            if status.status.value < 0:
                self._root_cause_status.update({key: status})
                if root_cause:
                    root_cause.update({key: status})
                else:
                    root_cause = {key: status}

        return root_cause

    def report(self):
        # 1. Print the title
        print(CHECK_TITLE.center(80))

        # 2. Print the overall status of the current module.
        status = "SUCCESSFUL" if self._is_successful else FontRed("FAILED")
        overall_status = (
            FontGreen(f"{self._tag.upper()} CHECK OVERALL Status: ") + status
        )
        print(overall_status)

        status_index = 0
        # 3. Print the current module status first.
        for key, status_value in self._check_status.items():
            if key == HostModule.DriverToolkitFile.name:
                continue
            PrintCheckStatus(status_value, status_index)
            status_index += 1

        # 4. Print information about the prerequisite dependency modules if failed.
        for key, status_value in self._total_check_status.items():
            if key not in self._check_status:
                PrintCheckStatus(status_value, status_index)
                status_index += 1

        # 5. Print summary.
        if not self._is_successful:
            print(SEPARATION_LINE)
            self._find_root_cause()
            print(FontRed("Summary:"))
            print(
                "The "
                + FontRed("ROOT CAUSE")
                + " is that the following component check failed. Please follow the corresponding "
                + FontRed("Recommendation")
                + " provided above to take action."
            )
            root_cause_index = 1
            SUMMARY_LENGTH = 30
            for key, root_cause_status in self._root_cause_status.items():
                print(
                    f"{root_cause_index}. {root_cause_status.name}".ljust(
                        SUMMARY_LENGTH
                    )
                    + FontRed(root_cause_status.status.name)
                )
                root_cause_index += 1

        # 6. Print the end-of-line marker.
        print(REPORT_END_LINE)

    def get_version(self, name: str = None):
        name = name if name else self._version_name
        if name in self._check_status:
            return self._check_status[name].version
        else:
            return None

    def get_key_status(self, name: str = None):
        if name in self._total_check_status:
            return self._total_check_status[name].status
        else:
            return None

    def check(self) -> Tuple[bool, dict]:
        self.inspect()
        # Sometimes we need to forcibly set up detection logs, such as for simulating negative tests.
        if self._injected_log:
            self._log.update(self._injected_log)

        self._diagnoser.init_log(self._log)
        # Dict[CheckStatus]
        self._check_status = copy.deepcopy(self._diagnoser.run())
        self._total_check_status.update(self._check_status)
        for key, value in self._check_status.items():
            if value.status == Status.FAILED:
                self._is_successful = False
                self._has_failed = True
            if value.status == Status.UNINSTALLED:
                self._is_successful = False
                self._has_uninstalled = True
        if self._is_successful:
            return True, self._total_check_status
        else:
            precheck_status = self.precheck()
            self._total_check_status.update(precheck_status)

            self._diagnoser.update_check_status(self._total_check_status)
            self._diagnoser.post_diagnose()

            return False, self._total_check_status


class HostChecker(Checker):

    def __init__(
        self, check_list: list = list(HostModule), container_name: str = None
    ) -> None:
        super().__init__(check_list, container_name)
        self._tag = CheckModuleNames.host.name
        self._diagnoser = HostDiagnoser(self._tag)
        # Although a container is specified, we still perform the HostChecker
        # on the host.
        if self._container_name:
            self._container_name = None
        self._shell = ShellExecutor(container_name)

    def inspect(self):
        # stage 1: CPU, host_memory
        if HostModule.CPU in self._check_list:
            self._log[HostModule.CPU.name] = self._shell.cpu_info()
        if HostModule.host_memory in self._check_list:
            self._log[HostModule.host_memory.name] = self._shell.host_memory_size()
        # stage 2: OS, kernel, lspci, pcie, iommu
        if HostModule.OS in self._check_list:
            self._log[HostModule.OS.name] = self._shell.system_version()
        if HostModule.Kernel in self._check_list:
            self._log[HostModule.Kernel.name] = self._shell.kernel_version()
        if HostModule.IOMMU in self._check_list:
            self._log[HostModule.IOMMU.name] = self._shell.IOMMU_info()
        if HostModule.Lspci in self._check_list:
            self._log[HostModule.Lspci.name] = self._shell.lspci_info()
        # stage 3: dkms, lightdm, linux-modules-extra-<kernel_version>
        if HostModule.DKMS in self._check_list:
            self._log[HostModule.DKMS.name] = self._shell.get_dpkg_package_version(
                "dkms"
            )
        if HostModule.Lightdm in self._check_list:
            self._log[HostModule.Lightdm.name] = self._shell.get_dpkg_package_version(
                "lightdm"
            )
        if HostModule.LinuxModulesExtra in self._check_list:
            self._log[HostModule.LinuxModulesExtra.name] = (
                self._shell.get_dpkg_package_version(
                    f"linux-modules-extra-{platform.release()}"
                )
            )
        # stage 4: Docker
        if HostModule.Docker in self._check_list:
            self._log[HostModule.Docker.name] = [
                self._shell.docker_version(),
                self._shell.get_service_status(service_name="docker"),
            ]
        # stage 5: InCluster render_group status
        if HostModule.InCluster in self._check_list:
            self._log[HostModule.InCluster.name] = self._shell.get_InCluster_status()
        if HostModule.RenderGroup in self._check_list:
            self._log[HostModule.RenderGroup.name] = (
                self._shell.get_groups_info(),
                self._shell.is_render_group_exits(),
            )
        if HostModule.DriverToolkitFile in self._check_list:
            self._log[HostModule.DriverToolkitFile.name] = self._shell.is_path_exists(
                DRIVERTOOLKIT_PATH
            )


class SmartIOChecker(Checker):

    def __init__(
        self, check_list: list = list(SmartIOModule), container_name: str = None
    ) -> None:
        super().__init__(check_list, container_name)
        self._tag = CheckModuleNames.smartio.name
        self._version_name = SmartIOModule.mt_peermem.name
        self._diagnoser = SmartIODiagnoser(self._tag)
        self._precheckers = [
            HostChecker(
                [
                    HostModule.CPU,
                    HostModule.OS,
                    HostModule.Kernel,
                    HostModule.Lspci,
                    HostModule.DKMS,
                    HostModule.Lightdm,
                ],
                self._container_name,
            )
        ]
        self._shell = ShellExecutor(container_name)

    def inspect(self):
        if SmartIOModule.mt_peermem in self._check_list:
            self._log[SmartIOModule.mt_peermem.name] = [
                self._shell.get_dpkg_package_version("mt-peermem"),
                self._shell.get_lsmod_loaded_module("mtgpu.*mt_peermem"),
            ]


class DriverChecker(Checker):

    def __init__(
        self, check_list: list = list(DriverModule), container_name: str = None
    ) -> None:
        self._container_name = container_name
        if self._container_name:
            self._container_name = None
        super().__init__(check_list, self._container_name)
        self._tag = CheckModuleNames.driver.name
        self._version_name = DriverModule.Driver.name
        self._diagnoser = DriverDiagnoser(self._tag)
        self._precheckers = [
            HostChecker(
                [
                    HostModule.CPU,
                    HostModule.OS,
                    HostModule.Kernel,
                    HostModule.IOMMU,
                    HostModule.host_memory,
                    HostModule.Lspci,
                    HostModule.DKMS,
                    HostModule.Lightdm,
                    HostModule.LinuxModulesExtra,
                ],
                self._container_name,
            )
        ]
        self._shell = ShellExecutor(container_name)

    def inspect(self):
        if DriverModule.Driver in self._check_list:
            self._log[DriverModule.Driver.name] = self._shell.mthreads_gmi_info()
        if DriverModule.Driver_Version_From_Dpkg in self._check_list:
            self._log[DriverModule.Driver_Version_From_Dpkg.name] = (
                self._shell.get_dpkg_package_version("musa")
            )
        if DriverModule.Driver_Version_From_Clinfo in self._check_list:
            self._log[DriverModule.Driver_Version_From_Clinfo.name] = (
                self._shell.clinfo_info()
            )


class MTLinkChecker(Checker):

    def __init__(
        self, check_list: list = list(MTLinkModule), container_name: str = None
    ) -> None:
        super().__init__(check_list, container_name)
        self._tag = CheckModuleNames.mtlink.name
        self._version_name = MTLinkModule.MTLink.name
        self._diagnoser = MTLinkDiagnoser(self._tag)
        self._precheckers = [DriverChecker(container_name=self._container_name)]
        self._shell = ShellExecutor(container_name)

    def inspect(self):
        if MTLinkModule.MTLink in self._check_list:
            self._log[MTLinkModule.MTLink.name] = self._shell.MTLink_status()


class IBChecker(Checker):
    def __init__(
        self, check_list: list = list(IBModule), container_name: str = None
    ) -> None:
        super().__init__(check_list, container_name)
        self._tag = CheckModuleNames.ib.name
        self._version_name = IBModule.ibstat.name
        self._diagnoser = IBDiagnoser(self._tag)
        self._precheckers = [
            HostChecker(
                [
                    HostModule.CPU,
                    HostModule.OS,
                    HostModule.Kernel,
                    HostModule.IOMMU,
                    HostModule.host_memory,
                    HostModule.Lspci,
                    HostModule.DKMS,
                    HostModule.Lightdm,
                ],
                container_name=self._container_name,
            )
        ]
        self._shell = ShellExecutor(container_name)

    def inspect(self):
        if IBModule.ibstat in self._check_list:
            self._log[IBModule.ibstat.name] = self._shell.get_ibstat_info()


class ROCEChecker(Checker):

    # TODO(@wangkang)
    def __init__(self, check_list: list = list(), container_name: str = None) -> None:
        super().__init__(check_list, container_name)
        pass

    def inspect(self):
        pass


class ContainerToolkitChecker(Checker):

    def __init__(
        self,
        check_list: list = list(ContainerToolkitModule),
        container_name: str = None,
    ) -> None:
        super().__init__(check_list, container_name)
        self._tag = CheckModuleNames.container_toolkit.name
        self._version_name = ContainerToolkitModule.container_toolkit.name
        self._diagnoser = ContainerToolkitDiagnoser(self._tag)
        self._precheckers = [DriverChecker(container_name=self._container_name)]
        self._shell = ShellExecutor(container_name)
        self._version_name = CheckModuleNames.container_toolkit.name

    def inspect(self):
        if ContainerToolkitModule.container_toolkit in self._check_list:
            self._log[ContainerToolkitModule.container_toolkit.name] = (
                self._shell.get_dpkg_package_version("mt-container-toolkit")
            )
            self._log[ContainerToolkitModule.is_binding.name] = (
                self._shell.docker_runtime_info()
            )
            self._log[ContainerToolkitModule.test_mthreads_gmi.name] = (
                self._shell.get_container_toolkit_status()
            )
            self._log[ContainerToolkitModule.is_dir_exist.name] = (
                self._shell.is_path_exists("/usr/bin/musa")
            )
        if ContainerToolkitModule.mtml in self._check_list:
            self._log[ContainerToolkitModule.mtml.name] = (
                self._shell.get_dpkg_package_version("mtml")
            )
        if ContainerToolkitModule.sgpu_dkms in self._check_list:
            self._log[ContainerToolkitModule.sgpu_dkms.name] = (
                self._shell.get_dpkg_package_version("sgpu-dkms")
            )


class MusaChecker(Checker):

    def __init__(
        self, check_list: list = list(MusaModule), container_name: str = None
    ) -> None:
        super().__init__(check_list, container_name)
        self._tag = CheckModuleNames.musa.name
        self._version_name = MusaModule.MUSAToolkits.name
        self._shell = MusaShellExecutor(container_name)
        self._diagnoser = MusaDiagnoser(self._tag)
        if self._container_name or not EXECUTED_ON_HOST_FLAG:
            self._precheckers = [
                DriverChecker(container_name=self._container_name),
                ContainerToolkitChecker(
                    list(ContainerToolkitModule), self._container_name
                ),
            ]
        else:
            self._precheckers = [DriverChecker(container_name=self._container_name)]

    def inspect(self):
        if MusaModule.MUSAToolkits in self._check_list:
            self._log[MusaModule.MUSAToolkits.name] = [
                self._shell.get_musaInfo_info(),
                self._shell.is_path_exists("/usr/local/musa"),
            ]
            self._log[MusaModule.musa_version.name] = self._shell.get_musa_version()
            self._log[MusaModule.test_musa.name] = self._shell.test_musa()


class TorchMusaChecker(Checker):

    def __init__(
        self, check_list: list = list(TorchMusaModule), container_name: str = None
    ) -> None:
        super().__init__(check_list, container_name)
        self._shell = TorchMusaShellExecutor(container_name)
        self._tag = CheckModuleNames.torch_musa.name
        self._version_name = TorchMusaModule.Torch_musa.name
        self._diagnoser = TorchMusaDiagnoser(self._tag)
        self._precheckers = [MusaChecker(container_name=self._container_name)]

    def inspect(self):
        # TODO(@caizhi): need log system here
        if os.getenv("LOG_LEVEL") != "REPORT":
            print(
                f"Retrieving {self._tag} information, please wait patiently for about 10 seconds......"
            )
        if TorchMusaModule.PyTorch in self._check_list:
            self._log[TorchMusaModule.PyTorch_version.name] = [
                self._shell.get_pip_package_version("torch"),
                self._shell.get_python_package_git_version("torch"),
            ]
            self._log[TorchMusaModule.PyTorch.name] = self._shell.get_package_status(
                "torch"
            )
        if TorchMusaModule.Torch_musa in self._check_list:
            self._log[TorchMusaModule.Torch_musa_version.name] = [
                self._shell.get_pip_package_version("torch_musa"),
                self._shell.get_python_package_git_version("torch_musa"),
            ]
            self._log[TorchMusaModule.Torch_musa.name] = self._shell.get_package_status(
                "torch_musa"
            )
        if TorchMusaModule.TorchVision in self._check_list:
            self._log[TorchMusaModule.TorchVision_version.name] = [
                self._shell.get_pip_package_version("torchvision"),
                self._shell.get_python_package_git_version("torchvision"),
            ]
            self._log[TorchMusaModule.TorchVision.name] = (
                self._shell.get_package_status("torchvision")
            )
        if TorchMusaModule.TorchAudio in self._check_list:
            self._log[TorchMusaModule.TorchAudio_version.name] = [
                self._shell.get_pip_package_version("torchaudio"),
                self._shell.get_python_package_git_version("torchaudio"),
            ]
            self._log[TorchMusaModule.TorchAudio.name] = self._shell.get_package_status(
                "torchaudio"
            )


class vLLMChecker(Checker):
    def __init__(
        self, check_list: list = list(vLLMModule), container_name=None
    ) -> None:
        super().__init__(check_list, container_name)
        self._tag = CheckModuleNames.vllm.name
        self._version_name = vLLMModule.vLLM.name
        self._diagnoser = vLLMDiagnoser(self._tag)
        self._shell = vLLMShellExecutor(self._container_name)
        self._precheckers = [TorchMusaChecker(container_name=self._container_name)]

    def inspect(self):
        # TODO(@caizhi): need log system here
        if os.getenv("LOG_LEVEL") != "REPORT":
            print(
                f"Retrieving {self._tag} information, please wait patiently for about 10 seconds......"
            )
        if vLLMModule.vLLM in self._check_list:
            self._log[vLLMModule.vLLM.name] = self._shell.get_package_status("vllm")
            self._log[vLLMModule.vLLM_version.name] = (
                self._shell.get_python_package_version("vllm")
            )
        if vLLMModule.MTTransformer in self._check_list:
            self._log[vLLMModule.MTTransformer.name] = (
                self._shell.get_pip_package_version("mttransformer")
            )


if __name__ == "__main__":
    # pass
    # hostcheck = HostChecker()
    # print(status, log)
    # print("=====================")
    # driverchecker = DriverChecker()
    # status, log = driverchecker.check()
    # print(log, status)
    # print("=====================")
    # containertoolkitchecker = ContainerToolkitChecker()
    # status, log = containertoolkitchecker.check()
    # print(log, status)
    # print("=====================")
    musachecker = MusaChecker()
    status, log = musachecker.check()
    print(log, status)
    # print("=====================")
    # torch_musa_checker = TorchMusaChecker(container_name="torch_musa_release")
    # status, log = torch_musa_checker.check()
    # print(log, status)
    print("=====================")
    vllm = vLLMChecker(container_name="vllm_mtt_test")
    # print("=====================")
    # ib = IBChecker()
    # status, log = ib.check()
    # print(log, status)
    # print("=====================")
