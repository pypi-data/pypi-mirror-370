import sys
import os
from musa_deploy.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env


def test_check_ib_simulation():
    tester = TestChecker(CheckModuleNames.ib.name)
    simulation_log = {
        "ibstat": (
            "State: Active State: Active State: Active State: Active State: Active State: Active",
            "",
            0,
        )
    }
    ib_ground_truth = "ibstat                      Status: SUCCESS"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(ib_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_ib_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.ib.name)
    simulation_log = {
        "ibstat": (
            "State: Active State: Active State: Active State: Active State: Active State: Active",
            "",
            0,
        )
    }
    ib_ground_truth = "ibstat                      Status: SUCCESS"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(ib_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    # test_check_ib_simulation()
    test_check_ib_simulation_inside_container()
