import sys
import os
from musa_deploy.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, GREEN_PREFIX, COLOR_SUFFIX, set_env


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_smartio_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.smartio.name)
    simulation_log = {
        "mt_peermem": [
            ("", "", 0),
            ("mtgpu                3227648  1 mt_peermem", "", 0),
        ]
    }
    smartio_ground_truth = f"""\
mt_peermem
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: The command `musa-deploy` is currently being executed inside a container. To check smartio, please run the command outside the container."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(smartio_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "True"})
def test_check_smartio_simulation():
    tester = TestChecker(CheckModuleNames.smartio.name)
    simulation_log = {
        "mt_peermem": [
            ("1.2", "", 0),
            ("mtgpu                3076096  109 mt_peermem", "", 0),
        ]
    }
    smartio_ground_truth = """\
mt_peermem                  Version: 1.2"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(smartio_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_smartio_simulation_inside_container()
    test_check_smartio_simulation()
