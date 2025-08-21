from .checker import (
    HostChecker,
    DriverChecker,
    MTLinkChecker,
    IBChecker,
    SmartIOChecker,
    ContainerToolkitChecker,
    MusaChecker,
    TorchMusaChecker,
    vLLMChecker,
)
from .utils import CheckModuleNames


CHECKER = dict()
CHECKER[CheckModuleNames.host.name] = HostChecker
CHECKER[CheckModuleNames.driver.name] = DriverChecker
CHECKER[CheckModuleNames.mtlink.name] = MTLinkChecker
CHECKER[CheckModuleNames.ib.name] = IBChecker
CHECKER[CheckModuleNames.smartio.name] = SmartIOChecker
CHECKER[CheckModuleNames.container_toolkit.name] = ContainerToolkitChecker
CHECKER[CheckModuleNames.musa.name] = MusaChecker
CHECKER[CheckModuleNames.torch_musa.name] = TorchMusaChecker
CHECKER[CheckModuleNames.vllm.name] = vLLMChecker
