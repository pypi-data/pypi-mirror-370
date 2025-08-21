import sys
import io
import re
import os
import shutil
import hashlib
from functools import wraps
from datetime import datetime
import socket
import subprocess
import docker

from musa_deploy.utils import SHELL, get_pip_path
from musa_deploy.check import CHECKER
from musa_deploy.report import report
from musa_deploy.download import Downloader

RED_PREFIX = "\x1b[91m"
GREEN_PREFIX = "\x1b[32m"
COLOR_SUFFIX = "\x1b[0m"

S80_REBOOT_IP = "192.168.5.149"
S80_NORMAL_IP = "192.168.5.150"
S90_DEMO_IP = "192.168.5.44"
NO_GPU_IP = "192.168.4.20"


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    finally:
        s.close()
    return ip_address


LOCAL_IP = get_local_ip()


def capture_print(func, args=None, **kwargs):
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured_output
    if args:
        func(args)  # Pass arguments as is
    elif kwargs:
        func(**kwargs)  # Pass arguments as is
    else:
        func()
    sys.stdout = original_stdout
    captured = captured_output.getvalue()
    captured_output.close()
    return captured


def is_package_installed(package_name: str):
    """
    检查指定的 Debian 包是否已安装
    返回 (是否安装, 详细信息)
    """
    try:
        # 执行 dpkg -s 命令并捕获输出
        result = subprocess.run(
            ["dpkg", "-s", package_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output = result.stdout
        if "Status: install ok installed" in output:
            return True, output.strip()
        return False, output.strip()

    except subprocess.CalledProcessError as e:
        # 包未安装时会抛出此异常
        return False, e.stderr.strip()
    except FileNotFoundError:
        return False, "dpkg 命令不存在 (非 Debian/Ubuntu 系统?)"


def is_container_up(container_name: str):
    """
    Check if the specified Docker container is in the 'up' state.

    Args:
        container_name (str): The name or ID of the Docker container.

    Returns:
        bool: True if the container is up, False otherwise.
    """
    try:
        # Create a Docker client
        client = docker.from_env()
        # Get the container by name or ID
        container = client.containers.get(container_name)
        # Check the container's status
        return container.status == "running"
    except docker.errors.NotFound:
        # Container not found
        return False
    except docker.errors.APIError as e:
        # Handle other Docker API errors
        print(f"Docker API error: {e}")
        return False


def is_running_with_root():
    return True if os.geteuid() == 0 else False


def set_env(env_vars):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for key, value in env_vars.items():
                os.environ[key] = value
            try:
                result = func(*args, **kwargs)
            finally:
                for key, _ in env_vars.items():
                    del os.environ[key]
            return result

        return wrapper

    return decorator


class TestChecker:

    def __init__(self, checker_name: str = None):
        self._checker = CHECKER[checker_name]()
        self._is_successful_ground_truth = True
        self._simulation_log = dict()
        self._report_string = None
        self._report_string_ground_truth = None
        self._ground_truth = None

    def set_is_successful_ground_truth(self, is_successful_ground_truth: bool = True):
        self._is_successful_ground_truth = is_successful_ground_truth

    def set_simulation_log(self, simulation_log: dict = None):
        self._simulation_log = simulation_log

    def set_module_ground_truth(self, ground_truth: str):
        self._ground_truth = ground_truth

    def set_summary(self, summary: str):
        self._summary = summary

    def set_report_ground_truth(self, report_ground_truth: str):
        self._report_string_ground_truth = report_ground_truth

    def test_core_module(self):
        assert (
            self._ground_truth
        ), "Test failed. Ground Truth is empty, please check the ground truth!"
        assert (
            self._ground_truth in self._report_string
        ), f"Test failed. Report '{repr(self._report_string)}' should contain GroundTruth '{repr(self._ground_truth)}', but it does not!"

    def test_overall_status(self):
        assert (
            self._checker._is_successful == self._is_successful_ground_truth
        ), f"Overall status test failed. Expect Ground Truth value is {self._is_successful_ground_truth}, but got value is {self._checker._is_successful}!"
        if self._is_successful_ground_truth:
            ground_truth = f"\x1b[32m{self._checker._tag.upper()} CHECK OVERALL Status: \x1b[0mSUCCESSFUL"
        else:
            ground_truth = f"\x1b[32m{self._checker._tag.upper()} CHECK OVERALL Status: \x1b[0m{RED_PREFIX}FAILED{COLOR_SUFFIX}"
        assert (
            ground_truth in self._report_string
        ), f"Overall status test failed. Report string should contain Ground Truth value {ground_truth}, but report result is {self._report_string}!"

    def test_report_title(self):
        ground_truth = """\
=====================================================================
======================== MOORE THREADS CHECK ========================
=====================================================================\
"""
        assert (
            ground_truth in self._report_string
        ), f"Report title test failed. Report string should contain Ground Truth value {ground_truth}, but report result is {self._report_string}!"

    def test_report_endline(self):
        ground_truth = (
            "====================================================================="
        )
        assert (
            ground_truth in self._report_string
        ), f"Report title test failed. Report string should contain Ground Truth value {ground_truth}, but report result is {self._report_string}!"

    def test_summary(self):
        matched = re.search(
            self._summary,
            self._report_string.replace(RED_PREFIX, "")
            .replace(COLOR_SUFFIX, "")
            .replace("\n", ""),
        )

        assert (
            matched
        ), f"Summary test failed. Report string should contain Ground Truth value {self._summary}, but report result is {self._report_string}!"

    def test_single_module(self):
        self._checker.inject_inspect_log(self._simulation_log)
        self._checker.check()
        self._report_string = capture_print(self._checker.report)

        assert self._report_string, "Report string test failed. Report string is empty!"
        self.test_report_title()
        self.test_core_module()
        self.test_report_endline()

    def test_all(self):
        self._checker.inject_inspect_log(self._simulation_log)
        self._checker.check()
        self._report_string = capture_print(self._checker.report)

        assert self._report_string, "Report string test failed. Report string is empty!"
        self.test_report_title()
        self.test_overall_status()
        self.test_core_module()
        self.test_summary()
        self.test_report_endline()

    def test_whole_report(self):
        self._checker.inject_inspect_log(self._simulation_log)
        self._checker.check()
        self._report_string = capture_print(self._checker.report)

        assert (
            self._report_string == self._report_string_ground_truth
        ), "The whole Report test failed!"

    def capture_report_string(self):
        self._checker.inject_inspect_log(self._simulation_log)
        self._checker.check()
        self._report_string = capture_print(self._checker.report)


def ReportTest(inject_log: dict = None, ground_truth: str = None):
    report_string = capture_print(report, inject_log)
    # 0. test prompt
    prompt_ground_truth = (
        "The report is being generated, please wait for a moment......"
    )
    assert (
        prompt_ground_truth in report_string
    ), f"Prompt string test failed, expected ground truth is:\n{prompt_ground_truth}\nbut it is not found in result:\n{report_string}\n"
    # 1. test title
    title_ground_truth = """\
=====================================================================
======================= MOORE THREADS REPORT ========================
====================================================================="""
    assert (
        title_ground_truth in report_string
    ), "Title string test failed, expected ground truth is:\n{title_ground_truth}\nbut it is not found in result:\n{report_string}\n"

    # 2. test key module
    assert (
        ground_truth
    ), "'ground_truth' must not be None or empty string when testing Report!"
    ground_truth_list = ground_truth.split("\n")
    for ground_truth_value in ground_truth_list:
        assert (
            ground_truth_value in report_string
        ), f"Key string test failed, expected ground truth is:\n{ground_truth_value}\nbut it is not found in result:\n{report_string}\n"

    # 3. test end line
    last_line = report_string.split("\n")[-2]
    last_line_ground_truth = """\
====================================================================="""
    assert (
        last_line_ground_truth == last_line
    ), "Last end line test failed, expected ground truth is:\n{last_line_ground_truth}\nbut it is not found in result:\n{report_string}\n"


class TestDownloader:
    def __init__(self, name, version, path):
        self._download = Downloader()
        self._name = name
        self._version = version
        self._path = path

    def get_file_path(self, path):
        if not path:
            date_time = datetime.now()
            format_data_str = date_time.strftime("%Y-%m-%d-%H-%M-%S")
            folder_path = f"./musa_deploy_download_{format_data_str}"
            return folder_path
        return path

    def set_md5(self, md5_list):
        self._md5_list = md5_list

    def set_ground_truth_files(self, ground_truth_list):
        self.ground_file_list = ground_truth_list

    def check_file_md5(self):
        for file in os.scandir(self._path):
            hash_md5 = hashlib.md5()
            if os.path.isfile(file):
                assert file.name in self.ground_file_list
                file_path = os.path.join(self._path, file.name)
                with open(file_path, "rb") as files:
                    for chunk in iter(lambda: files.read(4096), b""):
                        hash_md5.update(chunk)
                assert hash_md5.hexdigest() in self._md5_list

    def set_error_info(self, info_key, info_value):
        self._info_key = info_key
        self._info_value = info_value

    def run(self):
        try:
            self._download.download(self._name, self._version, self._path)
            self.check_file_md5()
        finally:
            if os.path.isdir(self._download._folder_path):
                shutil.rmtree(self._download._folder_path)

    def run_error(self):
        try:
            self._download._name = self._name
            self._download._version = self._version
            self._download._folder_path = self._path
            self._download.get_version_and_download_link()
            self._download.make_folder()
            for component in self._download._download_link:
                component[self._info_key] = self._info_value
            self._download.download_by_url()
            self.check_file_md5()
        finally:
            if os.path.isdir(self._download._folder_path):
                shutil.rmtree(self._download._folder_path)


class TestInstall:
    def __init__(self, package_manager):
        self._package_manager = package_manager()
        self._package_type = self._package_manager._package_type
        self._target_package_name = self._package_manager._target_package_name
        self._dependency_package_list = self._package_manager._dependency_package_list
        self._shell = SHELL()
        self._pip_path = get_pip_path()

    def remove_ansi_escape(self, log):
        ansi_escape_pattern = re.compile(r"\x1b\[[0-9;]*m")
        return ansi_escape_pattern.sub("", log)

    def install(self, version=None, path=None):
        self._install_log = capture_print(
            self._package_manager.install, version, path=path
        )

    def uninstall(self):
        self._uninstall_log = capture_print(self._package_manager.uninstall)

    def update(self, version=None, path=None):
        self._update_log = capture_print(
            self._package_manager.update, version, path=path
        )

    def _version(self, package_name):
        if self._package_type == "pip":
            version, _, _ = self._shell.run_cmd(
                f"{self._pip_path} show {package_name} | grep -E 'Version:' | awk '{{print $2}}'"
            )
        elif self._package_type == "dpkg":
            version, _, _ = self._shell.run_cmd(
                f"dpkg -s {package_name} 2>/dev/null | awk '/^Version:/ {{print $2; found=1}} END {{exit found!=1}}'"
            )
        return version

    def set_version_ground_truth(self, **kwargs):
        self.ground_truth_version_dict = {}
        for key, value in kwargs.items():
            if key in ["sgpu_dkms", "mt_container_toolkit"]:
                key = key.replace("_", "-")
            self.ground_truth_version_dict[key] = value

    def check_is_installed_success_with_version(self):
        # get installed package version
        version_dict = {}
        if self._target_package_name == "container-toolkit":
            self._target_package_name = "mt-container-toolkit"
        target_package_version = self._version(self._target_package_name)
        version_dict[self._target_package_name] = target_package_version

        for package_name in self._dependency_package_list:
            dependency_package_version = self._version(package_name)
            version_dict[package_name] = dependency_package_version

        # check
        for package_name, package_version in self.ground_truth_version_dict.items():
            if package_name in version_dict:
                assert (
                    version_dict[package_name] == package_version
                ), f"{package_name} version test failed, expected version is:\n{package_version}\nbut installed version is {version_dict[package_name]}"

    def check_report_includes(
        self, captured_log, truth_log=None, truth_log_pattern=None
    ):
        if truth_log_pattern:
            assert re.search(
                self.remove_ansi_escape(truth_log_pattern),
                self.remove_ansi_escape(captured_log),
            ), f"(Ignore version info) truth_log_pattern: {truth_log_pattern} should in self._install_log: {captured_log}"
        else:
            assert (
                truth_log in captured_log
            ), f"truth_log: {truth_log} should in self._install_log: {captured_log}"

    def check_report_excludes(
        self, captured_log, truth_log=None, truth_log_pattern=None
    ):
        if truth_log_pattern:
            assert not re.search(
                self.remove_ansi_escape(truth_log_pattern),
                self.remove_ansi_escape(captured_log),
            ), f"(Ignore version info) truth_log_pattern: {truth_log_pattern} should not in self._install_log: {captured_log}"
        else:
            assert (
                truth_log not in captured_log
            ), f"truth_log: {truth_log} should not in self._install_log: {captured_log}"

    def check_work_after_install(self):
        if self._target_package_name == "mt-container-toolkit":
            _, _, return_code = self._shell.run_cmd(
                "docker run --rm --env MTHREADS_VISIBLE_DEVICES=all registry.mthreads.com/cloud-mirror/ubuntu:20.04 mthreads-gmi"
            )
            assert (
                return_code == 0
            ), "docker run --rm --env MTHREADS_VISIBLE_DEVICES=all registry.mthreads.com/cloud-mirror/ubuntu:20.04 mthreads-gmi failed"
