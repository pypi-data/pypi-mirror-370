import subprocess
import platform
import os
import re
import time
import tarfile
import zipfile
import sys
import requests
import pexpect
import logging
from datetime import datetime
from tqdm import tqdm
from typing import Union
import shutil
import psutil
import tempfile
from pathlib import Path
import yaml
from collections import OrderedDict


GPU_ARCH_MAP = {
    "0111": "mp_10",
    "0106": "mp_10",
    "0105": "mp_10",
    "0102": "mp_10",
    "0101": "mp_10",
    "0100": "mp_10",
    "0123": "mp_10",
    "0122": "mp_10",
    "0121": "mp_10",
    "0201": "mp_21",
    "0200": "mp_21",
    "0211": "mp_21",
    "0222": "mp_21",
    "0225": "mp_21",
    "0203": "mp_21",
    "0202": "mp_21",
    "0301": "mp_22",
    "0300": "mp_22",
    "0323": "mp_22",
    "0327": "mp_22",
}

GPU_TYPE_MAP = {
    "0121": "S1000M",
    "0101": "S10",
    "0102": "S30",
    "0105": "S50",
    "0106": "S60",
    "0202": "S70",
    "0201": "S80",
    "0200": "S80ES",
    "0301": "S90",
    "0122": "S1000",
    "0123": "S2000",
    "0222": "S3000",
    "0225": "S3000E",
    "0327": "S4000",
    "0323": "S4000",
    "0321": "S5000",
    "0211": "X300",
}

GPU_MEMORY_MAP = {
    "MTT S10": 4096,
    "MTT S30": 4096,
    "MTT S50": 8196,
    "MTT S60": 8196,
    "MTT S70": 7168,
    "MTT S80": 16384,
    "MTT S80ES": 16384,
    "MTT S90": 24576,
    "MTT S1000": 8192,
    "MTT S1000M": 8192,
    "MTT S2000": 16384,
    "MTT S3000": 32768,
    "MTT S3000E": 32768,
    "MTT S4000": 49152,
    "MTT S5000": 81920,
    "MTT X300": 16384,
}

VALID_CHOICES_NAME = [
    "kuae",
    "sdk",
    "musa",
    "mudnn",
    "mccl",
    "driver",
    "smartio",
    "container_toolkit",
    "torch_musa",
    "vllm",
    "host",
    "mutriton",
]

MUSA_BIN_PATH = "/usr/local/musa/bin"
MUSA_LIB_PATH = "/usr/local/musa/lib"


def FontGreen(string: str):
    return "\033[32m" + string + "\033[0m"


def FontRed(string: str):
    return "\033[91m" + string + "\033[0m"


def FontBlue(string: str):
    return "\033[34m" + string + "\033[0m"


def parse_args(args):
    pattern = re.compile(r"([a-zA-Z0-9_]+)(==|=|--|-)?(.*)")
    match = pattern.match(args)
    if match:
        name = match.group(1)
        version = match.group(3).strip() if match.group(3) else None
        if name in VALID_CHOICES_NAME:
            return name, version
        else:
            print(
                "Invalid input. The specified option is not in the list of valid options. Please select one of the following: 'kuae', 'sdk', 'musa', 'mudnn', 'mccl', 'driver', 'smartio', 'container_toolkit', 'torch_musa', 'vllm', 'host', 'mutriton'."
            )
    else:
        print(f"Invalid input format: {args}")
    sys.exit(1)


def demo_parse_args(args):
    pattern = re.compile(r"([a-zA-Z0-9_]+)(==|=|--|-)([0-9.]+)(==|=|--|-)(docker)?")
    match = pattern.match(args)
    if match:
        name = match.group(1)
        version = match.group(3)
        is_docker = bool(match.group(5))
        return name, version, is_docker
    else:
        pattern = re.compile(r"([a-zA-Z0-9_]+)(==|=|--|-)?(.*)")
        match = pattern.match(args)
        if match:
            name = match.group(1)
            kargs = match.group(3).strip() if match.group(3) else None
            if not kargs:
                return name, None, False
            elif "docker" == kargs:
                return name, None, True
            else:
                return name, kargs, False
        else:
            print(f"Invalid input format: {args}")
            sys.exit(1)


def require_root_privileges_check():
    if os.geteuid() != 0:
        print(
            FontRed(
                "This process must be ran with 'root' or 'sudo' privileges, but now it is not!"
            )
        )
        exit()


def ping(url):
    # 参数解析：'-n' 表示发送的echo请求的次数，'-w' 表示等待回复的超时时间（毫秒）
    # 这些参数在不同的操作系统中可能有所不同，这里以Windows为例
    parameter = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", parameter, "1", url]  # 对URL执行一次ping操作

    try:
        response = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # ping命令执行成功，返回码为0
        if response.returncode == 0:
            print(f"Ping {url} successful")
            return True
        else:
            print(f"Ping {url} failed")
            return False
    except Exception as e:
        print(f"Error pinging {url}: {e}")
        return False


def FormatGitVersion(version: str = None):
    split_version = version.split("+")
    return (
        split_version[0] + "+" + split_version[1][0:7]
        if len(split_version) == 2
        else version
    )


class SHELL:
    def __init__(self, shell=True, text_mode=True):
        self.shell = shell
        self.text_mode = text_mode

    def run_cmd(self, cmd: str, is_split=True):
        completed_process = subprocess.run(
            cmd,
            shell=self.shell,
            text=self.text_mode,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        # Flexible control of whether to preprocess the original output
        if is_split:
            completed_process.stdout = self.check_output(completed_process.stdout)
        return (
            completed_process.stdout,
            completed_process.stderr,
            completed_process.returncode,
        )

    def run_cmd_with_error_print(self, cmd: str):
        try:
            subprocess.run(
                cmd, shell=True, check=True, stderr=subprocess.PIPE, text=True
            )
        except subprocess.CalledProcessError as e:
            print(e.stderr, file=sys.stderr, end="")

    def run_cmd_with_standard_print(self, cmd: str) -> int:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=sys.__stdout__,
            stderr=sys.__stderr__,
            text=True,
        )

        return_code = process.wait()
        return return_code

    def check_output(self, output) -> list:
        """
        If the output is a string with newline characters, split it into a list
        """
        if isinstance(output, str):
            output = output.strip()
            if "\n" in output:
                return [line.strip() for line in output.splitlines()]
            else:
                return output
        else:
            return output


shell_cmd = SHELL()


def download_file_with_progress(url, save_path, max_retries=10, retry_delay=5):
    temp_path = save_path + ".part"

    if os.path.exists(save_path):
        print(f"The file already exists. No need to download again: {save_path}")
        return

    for attempt in range(max_retries):
        try:
            headers = {}
            pos = 0

            # 如果存在未下载完的文件，启用断点续传
            if os.path.exists(temp_path):
                pos = os.path.getsize(temp_path)
                headers["Range"] = f"bytes={pos}-"
                print(f"Resuming from byte {pos}")

            # 发送带 Range 的请求（支持续传）
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code not in [200, 206]:
                print(
                    f"Failed to download file from {url}. HTTP status code: {response.status_code}"
                )
                sys.exit(1)

            total_size = int(response.headers.get("content-length", 0)) + pos
            mode = "ab" if pos else "wb"

            progress_bar = tqdm(
                total=total_size,
                initial=pos,
                unit="B",
                unit_scale=True,
                desc=os.path.basename(save_path),
            )

            with open(temp_path, mode) as file:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))
            progress_bar.close()

            final_size = os.path.getsize(temp_path)
            if final_size >= total_size:
                os.rename(temp_path, save_path)
                print(f"File downloaded successfully: {save_path}")
                return
            else:
                print(
                    f"Incomplete download. Expected {total_size}, got {final_size}. Retrying..."
                )

        except Exception as e:
            print(f"Error during download (attempt {attempt + 1}): {e}")
            time.sleep(retry_delay)


def generate_name_with_time(prefix: str = None):
    date_time = datetime.now()
    timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
    name = f"{prefix}_{timestamp}"
    return name


def get_pip_path():
    pip_path = "pip"
    python_directory = os.path.dirname(sys.executable)
    sys_name = platform.system().lower()
    # TODO: MacOS(Darwin) and Windows need to be tested
    if sys_name in ["linux", "darwin"]:
        pip_path = os.path.join(python_directory, "pip")
    elif sys_name == "windows":
        pip_path = os.path.join(python_directory, "Scripts", "pip.exe")
    return pip_path


# TODO(@caizhi): 后期整合log相关功能
def fetch_last_n_logs(log_text, num_lines=15, truncate_marker="..."):
    log_lines = log_text.splitlines()
    if len(log_lines) > num_lines:
        return f"{truncate_marker}\n" + "\n".join(log_lines[-num_lines:])
    return log_text


class BaseDecompressor:
    def __init__(self):
        pass

    def create_output_dir(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            return output_dir

    def extract_tar_gz(self, archive_path, output_dir):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(output_dir)

    def extract_zip(self, archive_path, output_dir):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)


def get_gpu_type() -> tuple:
    gmi_infos = SHELL().run_cmd("mthreads-gmi -q")[0]
    lspci_infos = SHELL().run_cmd("lspci -n | grep 1ed5")
    key_arch = None
    # 只是为了测试增加环境变量
    if os.getenv("GPU_ARCH_MAP_TEST", 0) != 0:
        if os.getenv("GPU_ARCH_MAP_TEST") != "None":
            key_arch = os.getenv("GPU_ARCH_MAP_TEST")
        else:
            print(
                f"{FontRed('WARNING:')} The GPU type was not recognized. Please check the environment."
            )
            return (None, None)

    if gmi_infos and key_arch is None:
        for value in gmi_infos:
            if "Device ID" in value:
                key_arch = value.split(":")[-1].strip()
                if len(key_arch) == 6:
                    key_arch = key_arch[2:]
    if lspci_infos[2] == 0 and key_arch is None:
        key_arch = lspci_infos[0][0].split(":")[-1]
    if key_arch is None:
        print(
            f"{FontRed('WARNING:')} The GPU type was not recognized. Please check the environment."
        )
    elif key_arch in GPU_ARCH_MAP:
        return GPU_ARCH_MAP[key_arch], GPU_TYPE_MAP[key_arch]
    else:
        print(
            f"{FontRed('WARNING:')} The current architecture({key_arch}) is not supported. Please add issues to the repository(https://sh-code.mthreads.com/ai/musa_deploy)."
        )
    return (None, None)


def convert_underline_to_hyphen(
    name: Union[str, list], reverse=False
) -> Union[str, list]:
    """
    Converts underscores to hyphens or hyphens to underscores in a given string or list of strings.

    Parameters:
        name (Union[str, List[str]]): The input string or list of strings to be converted.
        reverse (bool): If True, converts hyphens to underscores.
                        If False (default), converts underscores to hyphens.

    Returns:
        Union[str, List[str]]: The converted string or list of strings with the changes applied.
    """

    if isinstance(name, str):
        if reverse:
            return name.replace("-", "_")
        else:
            return name.replace("_", "-")
    else:
        return [convert_underline_to_hyphen(item, reverse) for item in name]


REPORT_TITLE = """\
=====================================================================
======================= MOORE THREADS REPORT ========================
====================================================================="""

CHECK_TITLE = """\
=====================================================================
======================== MOORE THREADS CHECK ========================
====================================================================="""

REPORT_END_LINE = """\
====================================================================="""

SEPARATION_LINE = """\
---------------------------------------------------------------------"""


def GenerateContainerName(demo: str, task: str, prefix: str = "musa_deploy") -> str:
    """Generate a container name based on the current timestamp

    Args:
        task (str): Task will be run by DEMO module.
        prefix (str, optional): Defaults to "musa-deploy".

     Returns:
        str: A unique container name.
    """
    date_time = datetime.now()
    timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
    return f"{prefix}_{demo}_{task}_{timestamp}"


def continue_or_exit(prompt_log="是否继续执行？"):
    while True:
        user_input = input(f"{prompt_log}(y/n): ").strip().lower()
        if user_input in ["y", ""]:
            return True
        elif user_input == "n":
            return False
        else:
            print("invalid input, please input 'n' or 'y'")


def get_original_command():
    # 获取当前进程
    current_process = psutil.Process()

    # 获取父进程
    parent_process = current_process.parent()

    # 检查父进程的命令行参数
    if parent_process and "sudo" in parent_process.cmdline()[0]:
        # 返回父进程的命令行参数
        return " ".join(parent_process.cmdline())
    else:
        return " ".join(current_process.cmdline())


def get_free_space_gb(path):
    """
    获取指定路径的剩余空间（以 GB 为单位）。

    :param path: 路径
    :return: 剩余空间（GB）
    """
    if not os.path.exists(path):
        print(f"Error: The path '{path}' does not exist, please create it manually!")
        sys.exit(1)  # 退出程序，返回状态码 1
    usage = shutil.disk_usage(path)
    return round(usage.free / (1024**3), 2)  # 转换为 GB 并保留两位小数


def get_os_name():
    os_name = os.uname().release + os.uname().version
    partten = re.compile(r"\b(Ubuntu|ky\d+|kylinos)\b", re.IGNORECASE)
    os_name = partten.findall(os_name)[0]
    if "ky" in os_name:
        os_name = "Kylin"
    return os_name


class InventoryGenerator:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def parse_hostfile(self, hostfile: Path) -> OrderedDict:
        """解析主机文件并生成有序字典结构"""
        inventory = OrderedDict()
        inventory["myhosts"] = OrderedDict()
        inventory["myhosts"]["hosts"] = OrderedDict()

        with hostfile.open() as f:
            for idx, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                ip, user, password = line.split()

                if idx == 1:
                    hostname = "leader"
                else:
                    hostname = f"worker_{idx:02d}"
                inventory["myhosts"]["hosts"][hostname] = OrderedDict(
                    [
                        ("ansible_host", ip),
                        ("ansible_user", user),
                        ("ansible_become_pass", f'"{password}"'),
                        ("ansible_become_method", "sudo"),
                        (
                            "ansible_ssh_common_args",
                            "-o ServerAliveInterval=30 -o ServerAliveCountMax=60",
                        ),
                    ]
                )

        inventory["myhosts"]["vars"] = OrderedDict(
            [("ansible_python_interpreter", "/usr/bin/python3")]
        )
        return inventory

    def generate_temp_inventory(self, hostfile: Path) -> str:
        """生成临时Inventory文件并返回路径"""
        try:
            # 生成有序数据结构
            inventory = self.parse_hostfile(hostfile)

            # 创建唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"ansible_inventory_{timestamp}.yml"
            output_path = os.path.join(self.temp_dir, filename)

            # 自定义YAML格式
            class OrderedDumper(yaml.SafeDumper):
                pass

            def dict_representer(dumper, data):
                return dumper.represent_mapping(
                    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                    data.items(),
                    flow_style=False,
                )

            OrderedDumper.add_representer(OrderedDict, dict_representer)

            # 写入临时文件
            with open(output_path, "w") as f:
                yaml.dump(
                    inventory,
                    f,
                    Dumper=OrderedDumper,
                    default_flow_style=False,
                    sort_keys=False,
                    width=1000,
                    allow_unicode=True,
                )

            # 设置文件权限 (rw-r-----)
            os.chmod(output_path, 0o640)

            return output_path

        except Exception as e:
            raise RuntimeError(f"生成临时Inventory失败: {str(e)}")


def parse_hostfile_ip_to_string(filepath: str):
    """
    解析hostfile文件并生成IP地址逗号分隔字符串
    参数：
        filepath: hostfile文件路径
    返回：
        格式化的字符串 hostfile_ip="ip1,ip2,..."
    """
    ip_list = []

    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    ip = parts[0]
                    ip_list.append(ip)

    except FileNotFoundError:
        raise FileNotFoundError(f"Hostfile {filepath} not found")
    except Exception as e:
        raise RuntimeError(f"Error reading hostfile: {str(e)}")

    ips_str = ",".join(ip_list)
    return ips_str


def configure_ssh_access(hostfile_path):
    """
    自动配置SSH免密登录的主函数
    功能包括：
    1. 检查并生成SSH密钥
    2. 读取hostfile文件
    3. 批量执行ssh-copy-id
    """
    # 配置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 1. 检查并生成SSH密钥
    ssh_dir = Path.home() / ".ssh"
    private_key = ssh_dir / "id_rsa"
    pub_key = ssh_dir / "id_rsa.pub"
    # 同时检查公私钥
    if not (private_key.exists() and pub_key.exists()):
        logging.info("开始生成SSH密钥对...")
        try:
            cmd = f'ssh-keygen -t rsa -N "" -f {ssh_dir/"id_rsa"}'
            child = pexpect.spawn(cmd, timeout=10)  # 改进点2：延长超时

            # 多情况处理
            patterns = [
                "Overwrite (y/n)?",  # 覆盖提示
                "Enter file in which",  # 文件路径确认
                pexpect.EOF,  # 正常结束
            ]

            while True:
                index = child.expect(patterns)
                if index == 0:
                    logging.warning("检测到已存在密钥")
                    child.sendline("n")
                    break
                elif index == 1:
                    child.sendline("")
                elif index == 2:
                    break

            # 添加最终验证
            child.wait()
            if child.exitstatus == 0:
                logging.info("密钥生成成功")
            else:
                logging.error(f"密钥生成失败，退出码: {child.exitstatus}")
                return False

        except pexpect.TIMEOUT:
            logging.error("操作超时，请检查系统响应")
            return False
        except Exception as e:
            logging.error(f"意外错误: {str(e)}")
            return False
    else:
        logging.info("SSH密钥对已存在")

    # 2. 读取hostfile文件
    hosts = []
    try:
        with open(hostfile_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                if len(parts) < 3:
                    logging.warning(f"第{line_num}行格式错误: {line}")
                    continue

                ip, user, password = parts[0], parts[1], parts[2]
                hosts.append((ip, user, password))

        if not hosts:
            logging.error("hostfile中没有有效的主机记录")
            return False
    except Exception as e:
        logging.error(f"读取hostfile失败: {str(e)}")
        return False

    # 3. 批量配置SSH
    success_count = 0
    for ip, user, password in hosts:
        try:
            logging.info(f"正在配置 {user}@{ip}...")

            # 构造命令
            cmd = f"ssh-copy-id -i {pub_key} {user}@{ip}"

            # 使用pexpect自动交互
            child = pexpect.spawn(cmd, timeout=15)

            # 处理可能的确认提示
            ret = child.expect(["yes/no", "password:", "already exist", pexpect.EOF])

            if ret == 0:  # 首次连接确认
                child.sendline("yes")
                child.expect("password:")

            if ret in [0, 1]:  # 需要输入密码
                child.sendline(password)
                child.expect(pexpect.EOF)

            # 检查结果
            output = child.before.decode()
            if "All keys were skipped" in output:
                logging.info(f"{ip} 已配置过密钥，跳过")
                success_count += 1
            elif "No route to host" in output:
                logging.error(FontRed(f"{ip} 无法连接，可能是网络问题"))
            elif "ERROR" in output or "Permission denied" in output:
                raise Exception("密码错误或权限不足")
            else:
                logging.info(f"{ip} 配置成功")
                success_count += 1

        except pexpect.TIMEOUT:
            logging.error(f"{ip} 连接超时")
        except Exception as e:
            logging.error(f"{ip} 配置失败: {str(e)}")

    logging.info(f"配置完成，成功 {success_count}/{len(hosts)} 台主机")
    return success_count == len(hosts)
