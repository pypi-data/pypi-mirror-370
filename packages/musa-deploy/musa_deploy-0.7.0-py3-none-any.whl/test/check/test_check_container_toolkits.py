import sys
import os
import pytest
from musa_deploy.check.utils import CheckModuleNames, EXECUTED_ON_HOST_FLAG
from musa_deploy.utils import FontGreen, FontRed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, GREEN_PREFIX, COLOR_SUFFIX, set_env


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_mtml_sgpu_toolkit_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.container_toolkit.name)
    simulation_log = {
        "container_toolkit": ("", "", 0),
        "sgpu_dkms": ("", "", 0),
        "mtml": ("", "", 0),
    }
    mtml_ground_truth = f"""\
container_toolkit
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: The command `musa-deploy` is currently being executed inside a container. To check container_toolkit, please run the command outside the container."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(mtml_ground_truth)
    tester.test_single_module()


@pytest.mark.skipif(
    not EXECUTED_ON_HOST_FLAG, reason="ignore this test, if executing in container"
)
@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_runtime_unbinding_simulation():
    tester = TestChecker(CheckModuleNames.container_toolkit.name)
    simulation_log = {
        "container_toolkit": ("1.9.0-1", "", 0),
        "is_binding": ("runc", "", 0),
        "test_mthreads_gmi": (
            "",
            'docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "mthreads-gmi": executable file not found in $PATH: unknown.\n',
            127,
        ),
        "mtml": ("1.9.2-linux", "", 0),
        "sgpu_dkms": ("1.2.1", "", 0),
    }
    ground_truth = f"""\
2.container_toolkit           Version: 1.9.0-1
    - status: {FontRed('FAILED')}
    - Info: "docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "mthreads-gmi": executable file not found in $PATH: unknown.
"
    - {FontGreen('Recommendation')}: Bind the Moore thread container runtime to Docker: (cd /usr/bin/musa && sudo ./docker setup $PWD), and try again."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(ground_truth)
    tester.test_single_module()


@pytest.mark.skipif(
    not EXECUTED_ON_HOST_FLAG, reason="ignore this test, if executing in container"
)
@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_runtime_unbinding_undriver_simulation():
    tester = TestChecker(CheckModuleNames.container_toolkit.name)
    simulation_log = {
        "container_toolkit": ("1.9.0-1", "", 0),
        "is_binding": ("runc", "", 0),
        "test_mthreads_gmi": (
            "",
            'docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "mthreads-gmi": executable file not found in $PATH: unknown.\n',
            127,
        ),
        "mtml": ("1.9.2-linux", "", 0),
        "sgpu_dkms": ("1.2.1", "", 0),
        "Driver": ("", "/bin/sh: 1: mthreads-gmi: not found\n", 127),
        "Driver_Version_From_Dpkg": ("", "", 1),
        "Driver_Version_From_Clinfo": (
            "Number of platforms                               0\n",
            "",
            0,
        ),
    }
    ground_truth = f"""\
2.container_toolkit           Version: 1.9.0-1
    - status: {FontRed('FAILED')}
    - Info: "docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "mthreads-gmi": executable file not found in $PATH: unknown.
"
    - {FontGreen('Recommendation')}: Bind the Moore thread container runtime to Docker: (cd /usr/bin/musa && sudo ./docker setup $PWD), and try again."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(ground_truth)
    tester.test_single_module()


@pytest.mark.skipif(
    not EXECUTED_ON_HOST_FLAG, reason="ignore this test, if executing in container"
)
@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_runtime_not_exist_dir_simulation():
    """not exist /usr/bin/musa --> note: needs to reinstall container_toolkit"""
    tester = TestChecker(CheckModuleNames.container_toolkit.name)
    simulation_log = {
        "container_toolkit": ("1.9.0-1", "", 0),
        "is_binding": ("mthreads", "", 0),
        "test_mthreads_gmi": (
            "",
            "docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: unable to retrieve OCI runtime error (open /run/containerd/io.containerd.runtime.v2.task/moby/562934106d093386d793b9d4177168af18109418e9d269fa5347f0bfb6aa9aa4/log.json: no such file or directory): fork/exec /usr/bin/musa/mthreads-container-runtime: no such file or directory: unknown.\n",
            127,
        ),
        "is_dir_exist": False,
        "mtml": ("1.9.2-linux", "", 0),
        "sgpu_dkms": ("1.2.1", "", 0),
        "Driver": ("", "/bin/sh: 1: mthreads-gmi: not found\n", 127),
        "Driver_Version_From_Dpkg": ("", "", 1),
        "Driver_Version_From_Clinfo": (
            "Number of platforms                               0\n",
            "",
            0,
        ),
    }
    ground_truth = f"""\
2.container_toolkit           Version: 1.9.0-1
    - status: {FontRed('FAILED')}
    - Info: "docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: unable to retrieve OCI runtime error (open /run/containerd/io.containerd.runtime.v2.task/moby/562934106d093386d793b9d4177168af18109418e9d269fa5347f0bfb6aa9aa4/log.json: no such file or directory): fork/exec /usr/bin/musa/mthreads-container-runtime: no such file or directory: unknown.
"
    - {FontGreen("Recommendation")}: The directory '/usr/bin/musa' does not exist, causing the mt-container-toolkit package to be corrupted. Please run `sudo musa-deploy -i container_toolkit` to reinstall mt-container-toolkit."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_mtml_sgpu_toolkit_simulation_inside_container()
