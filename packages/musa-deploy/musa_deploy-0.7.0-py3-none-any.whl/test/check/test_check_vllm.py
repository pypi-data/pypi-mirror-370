import sys
import os
from musa_deploy.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker


def test_check_vllm_simulation():
    tester = TestChecker(CheckModuleNames.vllm.name)
    simulation_log = {
        "vLLM": ("True", "", 0),
        "vLLM_version": ("0.4.2", "/bin/sh: 1: source: not found\n", 0),
        "MTTransformer": (
            [
                "Name: mttransformer",
                "Version: 20240402.dev63+g4aa4bd9.d20241120",
                "Summary: MT Transformer",
                "Home-page:",
                "Author:",
                "Author-email:",
                "License:",
                "Location: /home/mccxadmin/.local/lib/python3.10/site-packages",
                "Requires:",
                "Required-by:",
            ],
            "mttransformer                     20240402.dev63+g4aa4bd9.d20241120",
            "/bin/sh: 1: source: not found\n",
            0,
        ),
    }
    vllm_ground_truth = """\
0.MTTransformer               Version: 20240402.dev63+g4aa4bd9.d20241120
1.vLLM                        Version: 0.4.2"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(vllm_ground_truth)
    tester.test_single_module()


def test_check_vllm_simulation_PYTHONPATH_error():
    tester = TestChecker(CheckModuleNames.vllm.name)
    simulation_log = {
        "vLLM": (
            "",
            "Traceback (most recent call last):\n  File \"/opt/conda/envs/py38/lib/python3.8/site-packages/musa_deploy-0.0.4-py3.8.egg/musa_deploy/check/test/vllm_demo.py\", line 1, in <module>\n    from vllm.model_executor.layers.rotary_embedding import get_rope\nModuleNotFoundError: No module named 'vllm'\n",
            1,
        ),
        "vLLM_version": (
            "",
            "/bin/sh: 1: source: not found\nTraceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nModuleNotFoundError: No module named 'vllm'\n",
            1,
        ),
        "MTTransformer": (
            [
                "Name: mttransformer",
                "Version: 20240402.dev63+g4aa4bd9.d20241120",
                "Summary: MT Transformer",
                "Home-page:",
                "Author:",
                "Author-email:",
                "License:",
                "Location: /home/mccxadmin/.local/lib/python3.10/site-packages",
                "Requires:",
                "Required-by:",
            ],
            # "mttransformer                     20240402.dev63+g4aa4bd9.d20241120",
            "/bin/sh: 1: source: not found\n",
            0,
        ),
    }
    vllm_ground_truth = """\
0.MTTransformer               Version: 20240402.dev63+g4aa4bd9.d20241120
1.vLLM
    - status: \x1b[91mUNINSTALLED\x1b[0m
    - Info: "Traceback (most recent call last):
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/musa_deploy-0.0.4-py3.8.egg/musa_deploy/check/test/vllm_demo.py", line 1, in <module>
    from vllm.model_executor.layers.rotary_embedding import get_rope
ModuleNotFoundError: No module named \'vllm\'"
"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(vllm_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_vllm_simulation_PYTHONPATH_error()
