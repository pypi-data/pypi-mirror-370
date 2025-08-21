import sys
import os

from musa_deploy.install.install import TorchMusaPkgMgr  # noqa

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import set_env, TestInstall  # noqa


# @set_env({"PYTHON_VERSION_TEST": "py310"})
# def test_torch_musa_install_130():
#     test_install = TestInstall(TorchMusaPkgMgr)
#     test_install.install(version="1.3.0")
#     test_install.set_version_ground_truth(
#         torch="2.2.0a0+git8ac9b20",
#         torch_musa="1.3.0",
#         torchvision="0.17.2+c1d70fe",
#         torchaudio="2.2.2+cefdb36",
#     )
#     test_install.check_is_installed_success_with_version()
