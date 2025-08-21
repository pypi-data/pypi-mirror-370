import os
from ..check import CHECKER
from ..check.utils import (
    CheckModuleNames,
    HostModule,
    DriverModule,
    ContainerToolkitModule,
    TorchMusaModule,
    MusaModule,
    vLLMModule,
    Status,
)
from musa_deploy.utils import (
    REPORT_TITLE,
    REPORT_END_LINE,
    FontGreen,
    FontRed,
    FormatGitVersion,
)


def PrintStatus(status: dict, index: int):
    FIXED_LENGTH = 50
    main_line = f"{index}.{status.name}"
    status.status = (
        Status.UNINSTALLED
        if status.status == Status.WEAK_UNINSTALLED
        else status.status
    )
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
            if status.name in [
                DriverModule.Driver.name,
                ContainerToolkitModule.container_toolkit.name,
                MusaModule.MUSAToolkits.name,
                *TorchMusaModule._member_names_,
                vLLMModule.vLLM.name,
            ]:
                main_line += f" (Status: {status.status.name})"
            if status.name == DriverModule.Driver.name:
                main_line += (
                    "\n"
                    + " ".ljust(FIXED_LENGTH)
                    + f"GPU_Type: {set(status.GPU_Type)}"  # remove duplicate
                )

    elif status.name == HostModule.host_memory.name:
        if status.host_memory_size:
            main_line = (
                f"{index}.Host Memory".ljust(FIXED_LENGTH)
                + f"Size(GB): {status.host_memory_size}"
            )
        else:
            main_line = f"{index}.Host Memory".ljust(FIXED_LENGTH) + "Status: UNKNOWN"
    elif status.mtbios_version:
        version_output = "\n".join(
            [(" " * 39 + version) for version in status.mtbios_version]
        ).lstrip()
        main_line += (
            f"\n{index+1}.MTBios".ljust(FIXED_LENGTH) + f" Version: {version_output}"
        )
    elif status.name == HostModule.IOMMU.name:
        main_line = (
            f"{index}.IOMMU ".ljust(FIXED_LENGTH)
            + "Status: "
            + (
                "\033[31mdisable\033[0m"
                if not status.iommu_enable and "WARNING" == status.status.name
                else ("enable" if status.iommu_enable else "disable")
            )
            + f"({status.status.name})"
        )
    elif status.name == HostModule.InCluster.name:
        main_line = (
            f"{index}.InCluster ".ljust(FIXED_LENGTH)
            + f"Status: {FontGreen(str(False)) if status.status.name == 'SUCCESS' else FontRed(str(True))}"
        )
    else:
        main_line = (
            f"{index}.{status.name}".ljust(FIXED_LENGTH)
            + f"Status: {status.status.name}"
        )
    print(main_line)


# TODO(@caizhi): The logic here needs to be redesigned.
# Note: This parameter is only used for simulation testing, and it defaults to `None`. Please be careful when setting this parameter.
def report(inject_log: dict = None):
    os.environ["LOG_LEVEL"] = "REPORT"
    print(FontGreen("The report is being generated, please wait for a moment......"))

    print(REPORT_TITLE)
    # 1. vllm
    vllm_checker = CHECKER[CheckModuleNames.vllm.name]()
    vllm_checker.inject_inspect_log(inject_log)
    vllm_checker.check()
    index = 0
    for key, value in vllm_checker._check_status.items():
        PrintStatus(value, index)
        index += 1

    # 2. torch_musa
    torch_musa_checker = CHECKER[CheckModuleNames.torch_musa.name]()
    torch_musa_checker.inject_inspect_log(inject_log)
    torch_musa_checker.check()
    for key, value in torch_musa_checker._check_status.items():
        PrintStatus(value, index)
        index += 1

    # 3. musa
    musa_checker = CHECKER[CheckModuleNames.musa.name]()
    musa_checker.inject_inspect_log(inject_log)
    musa_checker.check()
    for key, value in musa_checker._check_status.items():
        PrintStatus(value, index)
        index += 1

    # 4. driver
    driver_checker = CHECKER[CheckModuleNames.driver.name]()
    driver_checker.inject_inspect_log(inject_log)
    driver_checker.check()
    for key, value in driver_checker._check_status.items():
        PrintStatus(value, index)
        index += 1

    # 5. mtlink
    mtlink_checker = CHECKER[CheckModuleNames.mtlink.name]()
    mtlink_checker.inject_inspect_log(inject_log)
    mtlink_checker.check()
    for key, value in mtlink_checker._check_status.items():
        PrintStatus(value, index)
        index += 1

    # 6. container_toolkit
    container_toolkit_checker = CHECKER[CheckModuleNames.container_toolkit.name]()
    container_toolkit_checker.inject_inspect_log(inject_log)
    container_toolkit_checker.check()
    for key, value in container_toolkit_checker._check_status.items():
        PrintStatus(value, index)
        index += 1

    # 7. ib
    IB_checker = CHECKER[CheckModuleNames.ib.name]()
    IB_checker.inject_inspect_log(inject_log)
    IB_checker.check()
    for key, value in IB_checker._check_status.items():
        PrintStatus(value, index)
        index += 1

    # 8. smartio
    smartio_checker = CHECKER[CheckModuleNames.smartio.name]()
    smartio_checker.inject_inspect_log(inject_log)
    smartio_checker.check()
    for key, value in smartio_checker._check_status.items():
        PrintStatus(value, index)
        index += 1

    # 9. host
    host_checker = CHECKER[CheckModuleNames.host.name]()
    host_checker.inject_inspect_log(inject_log)
    host_checker.check()
    for key, value in host_checker._check_status.items():
        # TODO(@caizhi): The logic here needs to be redesigned.
        # 应该集中管理哪些检查项需要跳脱，哪些需要打印，需要打印哪些信息
        if key == HostModule.DriverToolkitFile.name:
            # Skip DriverToolkitFile check
            continue
        PrintStatus(value, index)
        index += 1
    print(REPORT_END_LINE)
