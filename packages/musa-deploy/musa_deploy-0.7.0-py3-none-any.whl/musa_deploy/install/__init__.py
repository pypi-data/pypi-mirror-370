from .install import (
    SmartIOPkgMgr,
    HostPkgMgr,
    DriverPkgMgr,
    ContainerToolkitsPkgMgr,
    MusaPkgMgr,
    McclPkgMgr,
    muDNNPkgMgr,
    TorchMusaPkgMgr,
    vLLMPkgMgr,
    KylinMgr,
)
from musa_deploy.check.utils import CheckModuleNames


PACKAGE_MANAGER = dict()
PACKAGE_MANAGER[CheckModuleNames.smartio.name] = SmartIOPkgMgr()
PACKAGE_MANAGER[CheckModuleNames.host.name] = HostPkgMgr()
PACKAGE_MANAGER[CheckModuleNames.driver.name] = DriverPkgMgr()
PACKAGE_MANAGER[CheckModuleNames.container_toolkit.name] = ContainerToolkitsPkgMgr()
PACKAGE_MANAGER[CheckModuleNames.musa.name] = MusaPkgMgr()
# TODO(@wangkang): add module for mccl mudnn
PACKAGE_MANAGER["mccl"] = McclPkgMgr()
PACKAGE_MANAGER["mudnn"] = muDNNPkgMgr()
PACKAGE_MANAGER[CheckModuleNames.torch_musa.name] = TorchMusaPkgMgr()
PACKAGE_MANAGER[CheckModuleNames.vllm.name] = vLLMPkgMgr()
PACKAGE_MANAGER["kylin"] = KylinMgr()
