import re
from enum import Enum
from dataclasses import dataclass, astuple, fields, field

from .shell_executor import BaseShellExecutor
from musa_deploy.utils import FontGreen, FontRed, FormatGitVersion


EXECUTED_ON_HOST_FLAG = BaseShellExecutor().is_executed_on_host()


class CheckModuleNames(Enum):
    host = 0
    driver = 5
    container_toolkit = 10
    mtlink = 15
    ib = 16
    smartio = 17
    musa = 20
    torch_musa = 25
    vllm = 30  # vllm_mtt
    vllm_mtt = 31


DRIVERTOOLKIT_PATH = "/etc/modprobe.d/drivertoolkit.conf"


class HostModule(Enum):
    CPU = 0
    host_memory = 1

    OS = 10
    Kernel = 11
    Lspci = 12
    IOMMU = 13
    PCIE = 14

    DKMS = 20
    Lightdm = 21
    LinuxModulesExtra = 22

    Docker = 40

    InCluster = 50
    RenderGroup = 55
    DriverToolkitFile = 60


class DriverModule(Enum):
    Driver = 0
    Driver_Version_From_Dpkg = 1
    Driver_Version_From_Clinfo = 5


class MTLinkModule(Enum):
    MTLink = 0


class IBModule(Enum):
    ibstat = 0


class SmartIOModule(Enum):
    mt_peermem = 0


class ContainerToolkitModule(Enum):
    container_toolkit = 6
    mtml = 7
    sgpu_dkms = 8

    # only for storing log
    is_binding = 10
    is_dir_exist = 11
    test_mthreads_gmi = 0  # base test


class MusaModule(Enum):
    MUSAToolkits = 0

    # TODO(@wangkang): 在musa checker中加上 mudnn, mccl 版本打印??
    mudnn = 1
    mccl = 2
    # only for storing log
    musa_version = 5
    test_musa = 6


class TorchMusaModule(Enum):
    PyTorch = 0
    Torch_musa = 1
    TorchVision = 2
    TorchAudio = 3

    # The following elements are only used when storing logs.
    PyTorch_version = 10
    Torch_musa_version = 11
    TorchVision_version = 12
    TorchAudio_version = 13


class vLLMModule(Enum):
    vLLM = 0
    MTTransformer = 1

    # only used when storing logs.
    vLLM_version = 19


class Status(Enum):
    SUCCESS = 20  # Success
    ATTENTION = 15  # Attention

    UNKNOWN = 7
    WARNING = 6  # ...
    WEAK_UNINSTALLED = 5  # only warning if not installed
    WEAK_FAILED = 4

    MISMATCH = -10  # Error if not matching
    UNINSTALLED = -8  # Error if not installed
    FAILED = -1  # ...


@dataclass
class CheckStatus:
    name: str = ""
    status: Status = Status.SUCCESS
    version: str = ""
    info: str = ""
    solution: str = ""
    tag: str = ""

    number: int = 0

    host_memory_size: int = None
    iommu_enable: bool = None
    gpu_memory: dict = field(
        default_factory=dict
    )  # {"standard_memory": xxx, "actual_memory": xxx}
    mtbios_version: list = field(default_factory=list)
    GPU_Type: list = field(default_factory=list)
    mttransformer_version: str = ""
    CPU_Name: str = ""

    def __repr__(self):
        """
        Instance properties can be added dynamically if necessary
        """
        base_repr = ", ".join(
            f"{field.name}={value}" for field, value in zip(fields(self), astuple(self))
        )
        extra_repr = ", ".join(
            f"{name}={value}"
            for name, value in vars(self).items()
            if name not in {field.name for field in fields(self)}
        )
        return f"{self.__class__.__name__}({base_repr}, {extra_repr})"


INDENTATION_LENGTH = 4
INDENTATION = " " * INDENTATION_LENGTH
SOLUTION_INDENTATION_LENGTH = INDENTATION_LENGTH + len("Recommendation") + 4


def PrintCheckStatus(status: CheckStatus, index: int):
    FIXED_LENGTH = 30

    main_line = f"{index}.{status.name}"
    if status.version:
        if status.name == vLLMModule.MTTransformer.name:
            main_line = (
                f"{index}.{status.name}".ljust(FIXED_LENGTH)
                + f"Version: {status.version}"
            )
        else:
            main_line = (
                f"{index}.{status.name}".ljust(FIXED_LENGTH)
                + f"Version: {FormatGitVersion(status.version)}"
            )
    if status.name == "InCluster":
        main_line = (
            f"{index}.InCluster".ljust(FIXED_LENGTH)
            + f"Status: {FontGreen('False') if status.status == Status.SUCCESS else FontRed('True')}"  # We don't want it in the cluster, so SUCCESS means not in the cluster
        )

    # For RenderGroup
    if status.name == HostModule.RenderGroup.name:
        if status.status == Status.SUCCESS:
            main_line = (
                f"{index}.{status.name}".ljust(FIXED_LENGTH)
                + f"Status: {Status.SUCCESS.name}"
            )

    if status.host_memory_size:
        main_line = (
            f"{index}.Host Memory".ljust(FIXED_LENGTH)
            + f"Size(GB): {status.host_memory_size}"
        )

    if status.name == "IOMMU" and status.status.name != "UNKNOWN":
        main_line = (
            f"{index}.IOMMU: ".ljust(FIXED_LENGTH)
            + f"Status: {'enable' if status.iommu_enable else 'disable'}"
        )
    # For CPU
    if status.name == "CPU":
        main_line = (
            f"{index}.{status.name}".ljust(FIXED_LENGTH)
            + f"Name: {status.CPU_Name}\n"
            + " " * FIXED_LENGTH
            + f"Version: {status.version}"
        )
    # For IB
    if status.name == IBModule.ibstat.name:
        if status.status == Status.SUCCESS:
            main_line = (
                f"{index}.{status.name}".ljust(FIXED_LENGTH)
                + f"Status: {Status.SUCCESS.name}"
            )

    # For MTBios
    if status.mtbios_version:
        version_output = "\n".join(
            [(" " * 39 + version) for version in status.mtbios_version]
        ).lstrip()
        main_line += "\n  MTBios".ljust(FIXED_LENGTH) + f" Version: {version_output}"
    # For Lspci
    if status.GPU_Type and status.name == "Lspci":
        gpu_type_output = "\n".join(
            [(" " * 40 + gpu_type) for gpu_type in status.GPU_Type]
        ).lstrip()
        main_line = (
            f"{index}.{status.name}".ljust(FIXED_LENGTH)
            + f"GPU_Type: {gpu_type_output}"
        )

    # 2. if status is not Status.SUCCESS, only key metrics will be printed.
    if status.status == Status.WEAK_UNINSTALLED:
        status_line = f"{INDENTATION}- status: {FontRed('UNINSTALLED')}"
    elif status.status == Status.WEAK_FAILED:
        status_line = f"{INDENTATION}- status: {FontRed('FAILED')}"
    elif status.status != Status.SUCCESS:
        status_line = f"{INDENTATION}- status: {FontRed(status.status.name)}"
    else:
        status_line = None

    info_line = None
    solution_line = None
    if status.status != Status.SUCCESS:
        info_line = f'{INDENTATION}- Info: "{status.info}"' if status.info else None
        solution_line = (
            f"{INDENTATION}- {FontGreen('Recommendation')}: {status.solution}"
            if status.solution
            else None
        )

    for line in [main_line, status_line, info_line, solution_line]:
        if line:
            print(line)


def match_python_version(version_log_list):
    version_pattern = r"^\d+\.\d+\.\d+.*"
    for line in version_log_list:
        match = re.match(version_pattern, line)
        if match:
            return match.group(0)
