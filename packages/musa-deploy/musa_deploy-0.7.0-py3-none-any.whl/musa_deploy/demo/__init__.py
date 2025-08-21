from .demo import (
    TorchMusaDeployer,
    vLLMMTTDeployer,
    vLLMMusaDeployer,
    KuaeDeployer,
    OllamaDeployer,
)

from musa_deploy.check.utils import CheckModuleNames

DEMO = dict()
DEMO[CheckModuleNames.torch_musa.name] = TorchMusaDeployer()
DEMO[CheckModuleNames.vllm.name] = vLLMMTTDeployer()
DEMO[CheckModuleNames.vllm_mtt.name] = vLLMMTTDeployer()
DEMO["vllm_musa"] = vLLMMusaDeployer()
DEMO["kuae"] = KuaeDeployer()
DEMO["ollama"] = OllamaDeployer()
