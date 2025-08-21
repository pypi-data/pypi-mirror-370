import sys
import os
from musa_deploy.check.utils import CheckModuleNames
from musa_deploy.utils import FontGreen, FontRed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_pytorch_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.torch_musa.name)
    simulation_log = {
        "PyTorch_version": [
            (["Name: torch", "Version: 2.2.0"], "", 0),
            ("8ac9b20d4b090c213799e81acf48a55ea8d437d6", "", 0),
        ],
        "PyTorch": ("", "", 0),
    }
    pytorch_ground_truth = """\
PyTorch                     Version: 2.2.0+8ac9b20"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(pytorch_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_torch_musa_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.torch_musa.name)
    simulation_log = {
        "Torch_musa_version": [
            (["Name: torch_musa", "Version: 1.3.0+87a0b4f"], "", 0),
            ("87a0b4f61ef93a5b7b14d0ab5ae0286cac8b4023", "", 0),
        ],
        "Torch_musa": ("", "", 0),
    }
    torch_musa_ground_truth = """\
Torch_musa                  Version: 1.3.0+87a0b4f"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(torch_musa_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_torchvision_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.torch_musa.name)
    simulation_log = {
        "TorchVision_version": [
            (["Name: torchvision", "Version: 0.17.2+c1d70fe"], "", 0),
            ("c1d70fe1aa3f37ecdc809311f6c238df900dfd19", "", 0),
        ],
        "TorchVision": ("", "", 0),
    }
    torchvision_ground_truth = """\
TorchVision                 Version: 0.17.2+c1d70fe"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(torchvision_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_torch_musa_version_error_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.torch_musa.name)
    simulation_log = {
        "PyTorch_version": [
            (
                [
                    "Name: torch",
                    "Version: 2.4.1",
                    "Summary: Tensors and Dynamic neural networks in Python with strong GPU acceleration",
                    "Home-page: https://pytorch.org/",
                    "Author: PyTorch Team",
                    "Author-email: packages@pytorch.org",
                    "License: BSD-3",
                    "Location: /opt/conda/envs/py38/lib/python3.8/site-packages",
                    "Requires: filelock, fsspec, jinja2, networkx, nvidia-cublas-cu12, nvidia-cuda-cupti-cu12, nvidia-cuda-nvrtc-cu12, nvidia-cuda-runtime-cu12, nvidia-cudnn-cu12, nvidia-cufft-cu12, nvidia-curand-cu12, nvidia-cusolver-cu12, nvidia-cusparse-cu12, nvidia-nccl-cu12, nvidia-nvtx-cu12, sympy, triton, typing-extensions",
                    "Required-by: torchaudio, torchvision",
                ],
                "",
                0,
            ),
            ("38b96d3399a695e704ed39b60dac733c3fbf20e2", "", 0),
        ],
        "PyTorch": ("", "", 0),
        "Torch_musa_version": [
            (
                [
                    "Name: torch_musa",
                    "Version: 1.3.0",
                    "Summary: A PyTorch backend extension for Moore Threads MUSA",
                    "Home-page: https://github.mthreads.com/mthreads/torch_musa",
                    "Author: Moore Threads PyTorch AI Dev Team",
                    "Author-email:",
                    "License:",
                    "Location: /opt/conda/envs/py38/lib/python3.8/site-packages",
                    "Requires: packaging",
                    "Required-by:",
                ],
                "",
                0,
            ),
            (
                "",
                '/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121\n  warnings.warn(\nTraceback (most recent call last):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>\n    import torch_musa._MUSAC\nImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "<string>", line 1, in <module>\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>\n    raise ImportError("Please try running Python from a different directory!") from err\nImportError: Please try running Python from a different directory!\n',
                1,
            ),
        ],
        "Torch_musa": (
            "",
            '/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121\n  warnings.warn(\nTraceback (most recent call last):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>\n    import torch_musa._MUSAC\nImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "/home/musa_deploy/musa_deploy/check/test/torch_musa_demo.py", line 1, in <module>\n    import torch, torch_musa  # noqa\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>\n    raise ImportError("Please try running Python from a different directory!") from err\nImportError: Please try running Python from a different directory!\n',
            1,
        ),
        "TorchVision_version": [
            (
                [
                    "Name: torchvision",
                    "Version: 0.17.2+c1d70fe",
                    "Summary: image and video datasets and models for torch deep learning",
                    "Home-page: https://github.com/pytorch/vision",
                    "Author: PyTorch Core Team",
                    "Author-email: soumith@pytorch.org",
                    "License: BSD",
                    "Location: /opt/conda/envs/py38/lib/python3.8/site-packages/torchvision-0.17.2+c1d70fe-py3.8-linux-x86_64.egg",
                    "Requires: numpy, pillow, torch",
                    "Required-by:",
                ],
                "",
                0,
            ),
            (
                "",
                'Traceback (most recent call last):\n  File "<string>", line 1, in <module>\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchvision-0.17.2+c1d70fe-py3.8-linux-x86_64.egg/torchvision/__init__.py", line 6, in <module>\n    from torchvision import _meta_registrations, datasets, io, models, ops, transforms, utils\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchvision-0.17.2+c1d70fe-py3.8-linux-x86_64.egg/torchvision/_meta_registrations.py", line 164, in <module>\n    def meta_nms(dets, scores, iou_threshold):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/library.py", line 654, in register\n    use_lib._register_fake(op_name, func, _stacklevel=stacklevel + 1)\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/library.py", line 154, in _register_fake\n    handle = entry.abstract_impl.register(func_to_register, source)\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/_library/abstract_impl.py", line 31, in register\n    if torch._C._dispatch_has_kernel_for_dispatch_key(self.qualname, "Meta"):\nRuntimeError: operator torchvision::nms does not exist\n',
                1,
            ),
        ],
        "TorchVision": (
            "",
            'Traceback (most recent call last):\n  File "/home/musa_deploy/musa_deploy/check/test/torchvision_demo.py", line 1, in <module>\n    import torchvision.models as models\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchvision-0.17.2+c1d70fe-py3.8-linux-x86_64.egg/torchvision/__init__.py", line 6, in <module>\n    from torchvision import _meta_registrations, datasets, io, models, ops, transforms, utils\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchvision-0.17.2+c1d70fe-py3.8-linux-x86_64.egg/torchvision/_meta_registrations.py", line 164, in <module>\n    def meta_nms(dets, scores, iou_threshold):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/library.py", line 654, in register\n    use_lib._register_fake(op_name, func, _stacklevel=stacklevel + 1)\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/library.py", line 154, in _register_fake\n    handle = entry.abstract_impl.register(func_to_register, source)\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/_library/abstract_impl.py", line 31, in register\n    if torch._C._dispatch_has_kernel_for_dispatch_key(self.qualname, "Meta"):\nRuntimeError: operator torchvision::nms does not exist\n',
            1,
        ),
        "TorchAudio_version": [
            (
                [
                    "Name: torchaudio",
                    "Version: 2.2.2+cefdb36",
                    "Summary: An audio package for PyTorch",
                    "Home-page: https://github.com/pytorch/audio",
                    "Author: Soumith Chintala, David Pollack, Sean Naren, Peter Goldsborough, Moto Hira, Caroline Chen, Jeff Hwang, Zhaoheng Ni, Xiaohui Zhang",
                    "Author-email: soumith@pytorch.org",
                    "License:",
                    "Location: /opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg",
                    "Requires: torch",
                    "Required-by:",
                ],
                "",
                0,
            ),
            (
                "",
                'Traceback (most recent call last):\n  File "<string>", line 1, in <module>\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/__init__.py", line 2, in <module>\n    from . import _extension  # noqa  # usort: skip\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/__init__.py", line 38, in <module>\n    _load_lib("libtorchaudio")\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/utils.py", line 60, in _load_lib\n    torch.ops.load_library(path)\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/_ops.py", line 1295, in load_library\n    ctypes.CDLL(path)\n  File "/opt/conda/envs/py38/lib/python3.8/ctypes/__init__.py", line 373, in __init__\n    self._handle = _dlopen(self._name, mode)\nOSError: /opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/lib/libtorchaudio.so: undefined symbol: _ZNK5torch8autograd4Node4nameB5cxx11Ev\n',
                1,
            ),
        ],
        "TorchAudio": (
            "",
            'Traceback (most recent call last):\n  File "/home/musa_deploy/musa_deploy/check/test/torchaudio_demo.py", line 65, in <module>\n    main()\n  File "/home/musa_deploy/musa_deploy/check/test/torchaudio_demo.py", line 42, in main\n    _run_smoke_test(options.ffmpeg)\n  File "/home/musa_deploy/musa_deploy/check/test/torchaudio_demo.py", line 25, in _run_smoke_test\n    base_smoke_test()\n  File "/home/musa_deploy/musa_deploy/check/test/torchaudio_demo.py", line 9, in base_smoke_test\n    import torchaudio  # noqa: F401\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/__init__.py", line 2, in <module>\n    from . import _extension  # noqa  # usort: skip\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/__init__.py", line 38, in <module>\n    _load_lib("libtorchaudio")\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/utils.py", line 60, in _load_lib\n    torch.ops.load_library(path)\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/_ops.py", line 1295, in load_library\n    ctypes.CDLL(path)\n  File "/opt/conda/envs/py38/lib/python3.8/ctypes/__init__.py", line 373, in __init__\n    self._handle = _dlopen(self._name, mode)\nOSError: /opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/lib/libtorchaudio.so: undefined symbol: _ZNK5torch8autograd4Node4nameB5cxx11Ev\n',
            1,
        ),
    }
    ground_truth = f"""\
{FontGreen("TORCH_MUSA CHECK OVERALL Status: ")}{FontRed("FAILED")}
0.PyTorch                     Version: 2.4.1+38b96d3
1.Torch_musa                  Version: 1.3.0
    - status: {FontRed("FAILED")}
    - Info: "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121
  warnings.warn(
Traceback (most recent call last):
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>
    import torch_musa._MUSAC
ImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/musa_deploy/musa_deploy/check/test/torch_musa_demo.py", line 1, in <module>
    import torch, torch_musa  # noqa
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>
    raise ImportError("Please try running Python from a different directory!") from err
ImportError: Please try running Python from a different directory!
"
    - {FontGreen("Recommendation")}: The current Torch_musa version may not be an official release version. The version compatibility check has been skipped. If necessary, please manually check the version compatibility.
2.TorchVision                 Version: 0.17.2+c1d70fe
    - status: {FontRed("FAILED")}
    - Info: "Traceback (most recent call last):
  File "/home/musa_deploy/musa_deploy/check/test/torchvision_demo.py", line 1, in <module>
    import torchvision.models as models
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchvision-0.17.2+c1d70fe-py3.8-linux-x86_64.egg/torchvision/__init__.py", line 6, in <module>
    from torchvision import _meta_registrations, datasets, io, models, ops, transforms, utils
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchvision-0.17.2+c1d70fe-py3.8-linux-x86_64.egg/torchvision/_meta_registrations.py", line 164, in <module>
    def meta_nms(dets, scores, iou_threshold):
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/library.py", line 654, in register
    use_lib._register_fake(op_name, func, _stacklevel=stacklevel + 1)
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/library.py", line 154, in _register_fake
    handle = entry.abstract_impl.register(func_to_register, source)
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/_library/abstract_impl.py", line 31, in register
    if torch._C._dispatch_has_kernel_for_dispatch_key(self.qualname, "Meta"):
RuntimeError: operator torchvision::nms does not exist
"
3.TorchAudio                  Version: 2.2.2+cefdb36
    - status: {FontRed("FAILED")}
    - Info: "...
  File "/home/musa_deploy/musa_deploy/check/test/torchaudio_demo.py", line 25, in _run_smoke_test
    base_smoke_test()
  File "/home/musa_deploy/musa_deploy/check/test/torchaudio_demo.py", line 9, in base_smoke_test
    import torchaudio  # noqa: F401
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/__init__.py", line 2, in <module>
    from . import _extension  # noqa  # usort: skip
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/__init__.py", line 38, in <module>
    _load_lib("libtorchaudio")
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/utils.py", line 60, in _load_lib
    torch.ops.load_library(path)
  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/_ops.py", line 1295, in load_library
    ctypes.CDLL(path)
  File "/opt/conda/envs/py38/lib/python3.8/ctypes/__init__.py", line 373, in __init__
    self._handle = _dlopen(self._name, mode)
OSError: /opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/lib/libtorchaudio.so: undefined symbol: _ZNK5torch8autograd4Node4nameB5cxx11Ev\""""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_pytorch_simulation_inside_container()
    # test_check_torch_musa_simulation_inside_container()
    # test_check_torchvision_simulation_inside_container()
