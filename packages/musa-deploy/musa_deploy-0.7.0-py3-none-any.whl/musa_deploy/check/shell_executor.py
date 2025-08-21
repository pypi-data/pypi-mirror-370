import musa_deploy.check.utils as utils
from musa_deploy.utils import (
    SHELL,
    MUSA_BIN_PATH,
    MUSA_LIB_PATH,
    FontGreen,
    FontRed,
    get_free_space_gb,
)
import os
import sys
from typing import Tuple, Literal


os.environ["PATH"] = f"{MUSA_BIN_PATH}:{os.environ['PATH']}"
os.environ["LD_LIBRARY_PATH"] = (
    f"{MUSA_LIB_PATH}:{os.environ.get('LD_LIBRARY_PATH', '')}"
)
PYTHON_CMD = sys.executable

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))


class BaseShellExecutor:
    def __init__(self, container_name: str = None):
        self.shell = SHELL()
        self._container_name = container_name

    def _execute_cmd(self, command: str, is_split=True) -> tuple:
        """
        Executes a shell command.

        Args:
            command: shell command
            is_split: whether the original output is split into a list based on '\n'

        Returns:
            tuple: (stdout, stderr, returncode)
                - stdout(list if is_split else str): The standard output of the command.
                - err(str): The standard error of the command.
                - returncode(int): The return code of the command.(0: Success, None-zero: Failure)
        """
        if self._container_name:
            exec_command = f"docker exec {self._container_name} /bin/bash -c 'source ~/.bashrc; {command}'"
        else:
            exec_command = f"{command}"
        output = self.shell.run_cmd(exec_command, is_split)
        return output

    def is_path_exists(self, path) -> bool:
        """
        Checks whether the specified path exists.

        Args:
            path (str): The absolute or relative path to the file or directory to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        _, _, returncode = self._execute_cmd(f"test -e {path}")
        return True if not returncode else False

    def is_executed_on_host(self) -> bool:
        """
        True: The current execution environment is host
        False: The current execution environment is container
        """
        # out: docker, none
        out, _, _ = self.shell.run_cmd("systemd-detect-virt")
        _, _, code = self.shell.run_cmd("test -f /.dockerenv")
        if out != "docker" and code != 0:
            return True
        else:
            return False

    def get_dpkg_package_version(self, package_name: str) -> tuple:
        """
        Whether package is installed or not, and if so, get it's version

        Args:
            package_name: dkms, lightdm, mtml, sgpu-dkms, mt-container-toolkit, mt-peermem
        """
        dpkg_package_version = self.shell.run_cmd(
            f"dpkg -s {package_name} 2>/dev/null | awk '/^Version:/ {{print $2; found=1}} END {{exit found!=1}}'"
        )
        return dpkg_package_version

    def get_pip_package_version(self, package_name) -> tuple:
        """get pip package version"""
        cmd = f"pip show {package_name}"
        pip_package_version = self._execute_cmd(cmd)
        return pip_package_version

    def get_lsmod_loaded_module(self, module_name_pattern: str):
        """
        Get loaded modules
        """
        lsmod_result = self._execute_cmd(
            f"lsmod | grep -E '{module_name_pattern}'"
        )  # eg: mtgpu.*mt_peermem
        return lsmod_result

    def get_command_location(self, exe_name) -> tuple:
        """get command path, eg: /usr/bin/docker"""
        cmd = f"source ~/.bashrc; command -v {exe_name}"
        env_path = self._execute_cmd(cmd)
        return env_path


class ShellExecutor(BaseShellExecutor):
    def __init__(self, container_name: str = None):
        super().__init__(container_name)

    def get_InCluster_status(self) -> tuple:
        InCluster_status = self._execute_cmd(
            'kubectl get nodes | grep "$(cat /etc/hostname)"'
        )
        return InCluster_status

    def cpu_info(self):
        """get cpu info, need sudo permission"""
        cpu_info = self._execute_cmd("lscpu")
        return cpu_info

    def host_memory_size(self):
        """get host memory size"""
        host_memory_size = self._execute_cmd(
            "dmidecode -t memory | grep Size| grep -v 'No Module Installed'"
        )
        return host_memory_size

    def lspci_info(self) -> Tuple[tuple, tuple]:
        """
        Identify the 1ed5 device(MT GPU device) and get the link speed
        """
        lspci_info = self._execute_cmd("lspci -n | grep 1ed5")
        lspci_speed = None
        if not lspci_info[2]:
            first_pcie_address = lspci_info[0][0].split()[0]
            lspci_speed = self._execute_cmd(
                f"lspci -vvvvs {first_pcie_address} | grep LnkSta:"  # need sudo permission, otherwise, return empty
            )
        return lspci_info, lspci_speed

    def system_version(self) -> tuple:
        """Get system version, eg: Ubuntu 20.04.5 LTS"""
        system_version = self._execute_cmd(
            r"lsb_release -d | sed 's/^Description:\s*//'"
        )
        return system_version

    def kernel_version(self) -> tuple:
        """Get kernel version, eg: 5.15.0-56-generic"""
        kernel_version = self._execute_cmd("uname -r | tr -d '" "|\n '")
        return kernel_version

    def docker_version(self) -> tuple:
        """get driver version"""
        docker_version = self.shell.run_cmd(
            "docker --version | sed 's/,//g' | awk '{print $3}'| tr -d '" "|\n '"
        )
        return docker_version

    def get_service_status(self, service_name) -> tuple:
        service_status = self.shell.run_cmd(f"systemctl is-active {service_name}")
        return service_status

    def IOMMU_info(self) -> Tuple[Tuple, Tuple]:
        """
        Check whether IOMMU is enabled
        """
        iommu_log_from_file = self._execute_cmd(
            'cat /var/log/dmesg | grep -e "AMD-Vi: Interrupt remapping enabled" -e "IOMMU enabled" -e "iommu enable" -e "Adding to iommu group"'
        )
        iommu_log_from_dmesg = self.shell.run_cmd('dmesg | grep -i -e "iommu: enable"')
        return iommu_log_from_file, iommu_log_from_dmesg

    def MTLink_status(self) -> tuple:
        """Get MTLink status"""
        MTLink_status = self._execute_cmd("mthreads-gmi mtlink -s")
        return MTLink_status

    def get_ibstat_info(self):
        ibstat_info = self._execute_cmd(
            "ibstat", is_split=False
        )  # get original output, do not split text with '/n'
        return ibstat_info

    def mthreads_gmi_info(self) -> tuple:
        """Whether MT GPU Driver is installed or not, and if so, get info about MT GPU and driver"""
        mthreads_gmi_info = self._execute_cmd("mthreads-gmi -q")
        return mthreads_gmi_info

    def clinfo_info(self) -> tuple:
        """Whether MT GPU Driver is installed or not, and if so, get detailed info about driver version"""
        clinfo_info = self._execute_cmd("clinfo", is_split=False)
        return clinfo_info

    def docker_runtime_info(self) -> tuple:
        """Verify that the container runtime is set to mthreads"""
        bond_info = self.shell.run_cmd(
            "grep '\"default-runtime\"' /etc/docker/daemon.json | awk -F'\"' '{print $4}'"
        )
        return bond_info

    def get_container_toolkit_status(self) -> tuple:
        """
        Verifying that the container is running as mthreads succeeds
        """
        get_container_toolkit_status = self.shell.run_cmd(
            "docker run --rm --env MTHREADS_VISIBLE_DEVICES=all registry.mthreads.com/cloud-mirror/ubuntu:20.04 mthreads-gmi"
        )
        return get_container_toolkit_status

    def get_groups_info(self):
        out, err, code = self.shell.run_cmd("groups ${SUDO_USER:-$USER}")
        return (out, err, code)

    def is_render_group_exits(self):
        _, _, code = self.shell.run_cmd("getent group render")
        return True if not code else False


# TODO：@caizhi
# 将该工具类挪到最外层utils当中，改名为ContainerManager
class DockerShellExecutor(BaseShellExecutor):
    """
    Operate docker image
    """

    def __init__(self, container_name: str = None) -> None:
        super().__init__(container_name)
        self.image_type_map = {
            "torch_musa": [
                "musa-pytorch-release-public",
                "musa-pytorch-dev-public",
                "musa-pytorch-release-py38",
            ],
            "vllm": ["musa-pytorch-transformer-vllm"],
            "ubuntu": ["ubuntu"],
        }

    def get_container_config(self) -> Tuple[Tuple, Tuple]:
        """
        Get container config, eg: is privileged, env, etc
        """
        container_host_config = self.shell.run_cmd(
            f"docker inspect {self._container_name}"
            + " --format='{{json .HostConfig}}'"
        )
        container_env_config = self.shell.run_cmd(
            f"docker inspect {self._container_name}" + " --format='{{json .Config}}'"
        )
        return container_host_config, container_env_config

    def get_image_type(self, image_name) -> Literal["torch_musa", "vllm", "ubuntu"]:
        """
        Determine image type from image name: torch_musa, vllm or ubuntu
        """
        if "/" in image_name:
            image_name = image_name.split("/")[-1]
        image_name, image_tag = image_name.split(":")
        for type, name_list in self.image_type_map.items():
            if image_name in name_list:
                return type

    def get_image_info_from_container(self) -> Tuple[tuple, str]:
        """
        get image name and image type
        """
        container_image_name = self.shell.run_cmd(
            f"docker ps -a --filter 'name={self._container_name}'"
            + " --format '{{.Image}}'"
        )
        return container_image_name, self.get_image_type(container_image_name[0])

    @staticmethod
    def get_container_status(container_name) -> tuple:
        """
        Get container status, eg: running, exited, etc
        """
        container_status = SHELL().run_cmd(
            f"docker inspect {container_name}" + " --format='{{.State.Status}}'"
        )
        return container_status

    @staticmethod
    def is_container_running(container_name):
        is_running = DockerShellExecutor.get_container_status(container_name)
        if is_running[0] == "running":
            return True
        else:
            return False

    def create_container(
        self,
        image_name,
        privileged=True,
        shm_size="80g",
        env="MTHREADS_VISIBLE_DEVICES=all",
        network="bridge",  # default value
        pid="",  # default value
        workdir="",
        volume_list=[],
        port_list=[],
        image_cmd="/bin/bash",
        extra_docker_para="",
        need_pull_image=True,
    ) -> tuple:
        """
        Create a container and it's status is created
        """
        container_cmd = f"--privileged={str(privileged).lower()} --name {self._container_name} --net={network}  --env {env} --shm-size={shm_size} {extra_docker_para}"

        # Check whether the following parameters exist. If yes, add them
        if pid:
            container_cmd += f" --pid={pid}"
        if workdir:
            container_cmd += f" -w {workdir}"
        if volume_list:
            host_dir_free_space_list = []
            for host_dir, container_dir in volume_list:
                container_cmd += f" -v {host_dir}:{container_dir}"
                host_dir_free_space_list.append([host_dir, get_free_space_gb(host_dir)])

        if port_list:
            for ports in port_list:
                if len(ports) == 2:
                    container_cmd += f" -p {ports[0]}:{ports[1]}"
                else:
                    container_cmd += f" -p {ports[0]}"

        # TODO: (待解耦拆开)
        print(f"image: {image_name}")
        if need_pull_image:
            print(f"docker pull {image_name} ......")
            returncode = self.shell.run_cmd_with_standard_print(
                f"docker pull {image_name}"
            )
            if returncode != 0:
                print(FontRed(f"Error: Failed to pull image {image_name}."))
                exit()
        print(
            f"Start creating docker container: {FontGreen(f'docker create -it {container_cmd} {image_name} {image_cmd}')}"
        )
        print(f"docker create container {self._container_name} ......")
        returncode = self.shell.run_cmd_with_standard_print(
            f"docker create -it {container_cmd} {image_name} {image_cmd}"
        )
        if returncode != 0:
            exit()
        out, err, code = self.shell.run_cmd(f"docker start {self._container_name}")
        if not code:
            print(
                FontGreen(
                    f"Docker container named {self._container_name} has been created successfully."
                )
            )
            print(
                f"Please execute {FontGreen(f'`docker exec -it {self._container_name} bash`')} to enter the container."
            )
        else:
            print(FontRed(err))  # provide error reason
            exit()

        if volume_list:
            max_host_len = max(len(h) for h, _ in volume_list)

            mappings = "\n".join(
                f"  {i}. Host: {h.ljust(max_host_len)} → Container: {c}"
                for i, (h, c) in enumerate(volume_list, 1)
            )
            print(FontGreen(f"Directory mappings configured:\n{mappings}"))
            print(
                "Note: Host directory"
                + ", ".join(
                    f" '{host_dir}' has {FontRed(str(host_dir_free_space))} GB free space"
                    for host_dir, host_dir_free_space in host_dir_free_space_list
                )
                + ". Please ensure the available space meets your usage requirements to avoid potential issues."
            )

        return out, err, code

    def start_docker(self) -> int:
        _, _, code = self.shell.run_cmd(f"docker start {self._container_name}")
        return code

    def stop_docker(self) -> int:
        _, _, code = self.shell.run_cmd(f"docker stop {self._container_name}")
        return code

    def delete_image(self, image_name) -> int:
        _, _, code = self.shell.run_cmd(f"docker image rm {image_name}")
        return code

    def copy_to_docker(self, src, dst) -> int:
        """
        Copy file or directory from host env to container
        """
        _, _, code = self.shell.run_cmd(f"docker cp {src} {self._container_name}:{dst}")
        return code

    def copy_gmi_to_docker(self) -> int:
        """
        Copy mthreads-gmi from host env to container
        """
        host_gmi_path, _, _ = self.get_command_location("mthreads-gmi")
        docker_gmi_path, _, _ = self.get_command_location(
            "mthreads-gmi", container_name=self._container_name
        )
        code = self.copy_to_docker(host_gmi_path, docker_gmi_path)
        return code

    # TODO:@liang.geng
    def is_pid_running(self) -> bool:
        """If the task is running

        Returns:
            True: The task is running
            False: The task is not running
        """
        return False


class MusaShellExecutor(DockerShellExecutor):
    def __init__(self, container_name: str = None) -> None:
        super().__init__(container_name)
        self.test_dir_path = os.path.join(CURRENT_FOLDER, "test")

    def get_musaInfo_info(self) -> tuple:
        """
        check musa with musaInfo command.
        """
        musaInfo_info = self._execute_cmd("musaInfo", is_split=False)
        return musaInfo_info

    def get_musa_version(self) -> tuple:
        """
        Return musa version.
        """
        musa_version = self._execute_cmd("musa_version_query", is_split=False)
        return musa_version

    def test_musa(self) -> tuple:
        """
        Return information about testing test_musa.mu.
        """
        test_result = self._execute_cmd(
            f"mcc {self.test_dir_path}/test_musa.mu -lmusart -o ./test_musa.exe && ./test_musa.exe"
        )
        self._execute_cmd("rm -rf ./test_musa.exe")
        return test_result


class TorchMusaShellExecutor(DockerShellExecutor):
    def __init__(self, container_name: str = None) -> None:
        super().__init__(container_name)
        self.test_dir_path = os.path.join(CURRENT_FOLDER, "test")

        if self._container_name:
            self.shell.run_cmd(
                f"docker cp {self.test_dir_path} {self._container_name}:/home/"
            )  # cp test_file to container if container is not None
            self.test_dir_path = "/home/test"  # change test_dir_path to container path
            self.python_path = self.get_command_location("python")[
                0
            ]  # get python path after load bashrc
        else:
            self.python_path = PYTHON_CMD

    def get_python_package_version(self, package_name: str) -> tuple:
        """
        Get python package version
        """
        version_cmd = f"{self.python_path} -c 'import {package_name}; print({package_name}.__version__)'"
        version_out, version_error, version_code = self._execute_cmd(version_cmd)
        if isinstance(version_out, list):
            version_out = utils.match_python_version(version_out)
        return version_out, version_error, version_code

    def get_python_package_git_version(self, package_name: str) -> tuple:
        """
        Get python package git version
        """
        version_cmd = f'{self.python_path} -c "import {package_name}; print({package_name}.version.git_version)"'  # noqa
        version = self._execute_cmd(version_cmd)
        return version

    def get_package_status(self, package_name) -> tuple:
        """
        check torch, torch_musa, torchvision, torchaudio, etc
        """
        demo_filepath = self.test_dir_path + f"/{package_name}_demo.py"
        package_status = self._execute_cmd(f"{self.python_path} {demo_filepath}")
        return package_status


class vLLMShellExecutor(TorchMusaShellExecutor):
    """shell command for vllm info"""

    def __init__(self, container_name=None) -> None:
        super().__init__(container_name)
        self.vllm_filepath = os.path.join(CURRENT_FOLDER, "test_file", "test_vllm.py")
        self.vllm_dir = None

    def has_vllm_dir(self) -> tuple:
        """check if vllm dir exists"""
        if self._container_name:
            self.vllm_dir = "/home/workspace/vllm_mtt"
        has_vllm_dir = self._execute_cmd(f"test -d '{self.vllm_dir}'")
        return has_vllm_dir

    def has_vllm_env(self) -> tuple:
        """check if vllm env exists"""
        has_vllm_env = self._execute_cmd("echo $PYTHONPATH")
        return has_vllm_env


if __name__ == "__main__":
    # shell_info = BaseShellExecutor()
    # print(shell_info.get_command_location('docker'))
    # print(shell_info.get_execute_env())
    # print(shell_info.cpu_info())
    # print(shell_info.memory_size())
    # print(shell_info.system_version())
    # print(shell_info.lspci_info())
    # print(shell_info.docker_info())
    # print(shell_info.IOMMU_info())
    # print(docker.container_status())

    musa = TorchMusaShellExecutor(container_name="torch_musa_release")
    # print(musa.get_python_package_git_version("torch"))
    print(musa.get_python_package_version("torch"))
    musa_host = TorchMusaShellExecutor()
    print(musa_host.get_python_package_version("wheel"))
