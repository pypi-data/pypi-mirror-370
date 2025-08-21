from abc import ABC, abstractmethod
from musa_deploy.install import PACKAGE_MANAGER
from musa_deploy.config.yaml_read import ImageYaml, ImageClass
from musa_deploy.check.shell_executor import DockerShellExecutor
from musa_deploy.check.utils import CheckModuleNames
from musa_deploy.utils import (
    GenerateContainerName,
    FontRed,
    FontGreen,
    SHELL,
    get_gpu_type,
    get_os_name,
)
from musa_deploy.demo.utils import get_IP_address, GITEE_REPO_URL

import os
from dataclasses import dataclass, field

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
IMAGE_FILE_PATH = os.path.join(CURRENT_FOLDER, "../config/")


# TODO(@caizhi): please read from yaml files
# TODO(@wangkang): 驱动版本这里做临时映射，后面看怎么优化
GLOBAL_TORCH_MUSA_DRIVER_MAP = {"1.3.0": "3.1.0"}
GLOBAL_KUAE_DRIVER_MAP = {"1.3.0": "3.1.0"}
GLOBAL_VLLM_DRIVER_MAP = {"0.2.1": "3.1.0"}
GLOBAL_VLLM_MUSA_DRIVER_MAP = {
    "0.7.3": "3.0.0-rc4.0.0-server",
    "0.8.4": "4.1.0",
}
GLOBAL_OLLAMA_DRIVER_MAP = {"3.1.1": "3.1.1"}

VLLM_SUPPORTED_GPUS = ["S4000", "S90"]
OLLAMA_SUPPORT_GPUS = ["S80", "X300", "S80ES"]

DEMO_SUPPORT_LATEST_VERSION = {
    "vllm_mtt": "0.2.1",
    "vllm_musa": "0.8.4",
    "torch_musa": "1.3.0",
    "kuae": "1.3.0",
    "ollama": "3.1.1",
}


@dataclass
class DemoTask:
    torch_task: list = field(
        default_factory=lambda: [
            "base",
            "train_cifar10",
            #  "resnet50", "yolov5"
        ]
    )
    # TODO(@wk): How to due with vllm task list
    # vllm_task: list = field(
    #     default_factory=lambda: ["qwen2-0.5b", "deepseek-r1-distill-qwen1.5b"]
    # )

    def get_all_task(self) -> list:
        return self.torch_task


class BaseDemoDeployer(ABC):

    def __init__(self) -> None:
        self._version = None
        self._task: str = None
        self._demo: str = None
        self._installer = list()
        self._use_docker = False
        self._image = None
        self._driver_installer = PACKAGE_MANAGER[CheckModuleNames.driver.name]
        self._container_toolkit_installer = PACKAGE_MANAGER[
            CheckModuleNames.container_toolkit.name
        ]

        self._status: bool = False
        self._image_args = ImageClass()
        self._image_reader = ImageYaml(IMAGE_FILE_PATH)
        self._task_list = DemoTask()
        self._docker_shell = None
        self._target_driver_version = None
        self.model = None
        self.converted_model = None
        self._auto_install = False

    def precheck_gpu_type(self) -> bool:
        pass

    def precheck_version(self):
        driver_map = {
            "torch_musa": GLOBAL_TORCH_MUSA_DRIVER_MAP,
            "kuae": GLOBAL_KUAE_DRIVER_MAP,
            "vllm_mtt": GLOBAL_VLLM_DRIVER_MAP,
            "vllm_musa": GLOBAL_VLLM_MUSA_DRIVER_MAP,
            "ollama": GLOBAL_OLLAMA_DRIVER_MAP,
        }
        if self._version not in driver_map[self._demo]:
            print(
                FontRed(
                    f"The {self._demo} demo only supports version {list(driver_map[self._demo])}."
                )
            )
            return False

    def prepare_dependency(self):
        pass

    def prepare_demo_shell(self):
        pass

    def set_demo_shell(self, *args, **kwargs):
        pass

    def print_demo_summary(self):
        pass

    def get_docker_image(self, img_tag: str = None) -> str:
        # image_str = None
        # self.perpare_img_arg(img_tag)
        # image_str = self._image_reader.get_image_name(self._image_args)
        # return image_str
        pass

    def perpare_img_arg(self, img_tag: str = None) -> None:
        """Prepare the image arguments with the specified tag and type.

        Args:
            img_type(str): type of docker image, such as 'torch_musa', 'mtt-vllm'
            img_tag(str):
        """
        # 针对仅启动一个开发容器，用torch_musa作为开发容器，因为torch_musa容器有driver信息
        # 维护列表，将相同容器类型的任务放在同一个列表中
        if self._task in self._task_list.torch_task:
            if not img_tag:
                self._image_args.image_tag = "py310"  # torch_musa默认tag为py310
            else:
                self._image_args.image_tag = img_tag
            self._image_args.image_type = "torch_musa"
        elif self._task in self._task_list.kuae_task:
            # 如果是kuae容器，不需要tag
            if img_tag:
                print(
                    f"The container of {self._task} task don't need image tag, \
                        please remove the '--tag' parameter and run again"
                )
                exit()
            self._image_args.image_type = "mtt-vllm"
        else:
            print(
                "The application is not integrated in musa-deploy, \
                please run 'musa-deploy -h' to see how to use it"
            )
            exit()

    def start_container(
        self,
        container_name: str = None,
        workdir: str = None,
        volume_list: list = [],
        port_list: list = [],
        network: str = "bridge",
        pid: str = "",
        shm_size: str = "80g",
        image_cmd: str = "/bin/bash",  # default value
        extra_docker_para: str = "",
        need_pull_image: bool = True,
    ) -> bool:
        """Start a container to run the AI applications

        Args:
            img_name (str): docker image name, obtained by the get_img_name() function

        Returns:
            True: start container success
            False: start container failed
        """
        # 不同的task虽然容器不同但是启动方式相同
        # TODO：需要更改create_container接口
        if self.model:
            # 获取模型目录的父目录（无论路径是否以/结尾）
            model_parent = os.path.dirname(self.model.rstrip("/"))
            volume_list.append([model_parent, model_parent])

        if self.converted_model:
            converted_parent = os.path.dirname(self.converted_model.rstrip("/"))
            volume_list.append([converted_parent, converted_parent])

        self._docker_shell.create_container(
            image_name=self._image,
            workdir=workdir,
            volume_list=volume_list,
            port_list=port_list,
            network=network,
            pid=pid,
            shm_size=shm_size,
            image_cmd=image_cmd,
            extra_docker_para=extra_docker_para,
            need_pull_image=need_pull_image,
        )
        status = True

        return status

    @abstractmethod
    def set_installer(self):
        pass

    def get_driver_requirement(self):
        pass

    def set_docker_image_requirement(self):
        pass

    def set_driver_target_version(self):
        if self._version:
            if self._demo in ["torch_musa", "kuae"]:
                self._target_driver_version = GLOBAL_TORCH_MUSA_DRIVER_MAP[
                    self._version
                ]
            elif self._demo == "vllm_mtt":
                self._target_driver_version = GLOBAL_VLLM_DRIVER_MAP[self._version]
            elif self._demo == "vllm_musa":
                self._target_driver_version = GLOBAL_VLLM_MUSA_DRIVER_MAP[self._version]
            elif self._demo == "ollama":
                self._target_driver_version = GLOBAL_OLLAMA_DRIVER_MAP[self._version]
            else:
                print(FontRed("==========wrong demo ==============!"))
                exit()
        else:
            self._target_driver_version = None

    def start(
        self,
        version: str,
        task: str,
        use_docker: bool,
        container_name: str = None,
        demo: str = None,
        port_list: list = [],
        volume_list: list = [],
        workdir: str = "",
        network: str = "bridge",
        pid: str = "",
        shm_size: str = "80g",
        image_cmd: str = "/bin/bash",
        model: str = "",
        converted_model: str = "",
        tp_size: int = 0,
        webui: bool = False,
        git_branch: str = "",
        allow_force_install: bool = False,
        image: str = None,
        auto_install: bool = False,
        extra_args: str = "",
        docker_para: str = "",
        repo: str = "",
    ) -> bool:
        self._auto_install = auto_install
        self._task = task
        self._use_docker = use_docker
        self._demo = demo
        self.model = model
        self.tp_size = tp_size
        self.converted_model = converted_model
        self._version = version if version else DEMO_SUPPORT_LATEST_VERSION[self._demo]
        self.git_branch = git_branch
        self.extra_args = extra_args
        self.docker_para = docker_para

        if self.precheck_gpu_type() is False or self.precheck_version() is False:
            return False
        self.set_installer()
        # 1. prepare dependency environment
        if self._use_docker:
            # 1.1 set dependency driver version
            self.set_driver_target_version()
            # 1.2 set driver version in container_toolkit_installer
            if get_os_name() == "Kylin" and self._demo == "ollama":
                PACKAGE_MANAGER["kylin"].install("driver", self._target_driver_version)
                PACKAGE_MANAGER["kylin"].install("container_toolkit", "2.0.0")
            else:
                self._container_toolkit_installer.set_driver_target_version(
                    self._target_driver_version
                )
                # 1.3 install container_toolkits
                need_reboot = self._container_toolkit_installer.install(
                    allow_force_install=allow_force_install,
                    auto_install=self._auto_install,
                )
                if need_reboot:
                    return True
        else:
            # ===================
            pass

        # 2. start docker if need
        need_pull_image = True
        if self._use_docker:
            # 2.1 get image name
            if image:
                self._image = image
                need_pull_image = False
            else:
                self.set_docker_image_requirement()
            if not self._image:
                print(
                    FontRed(
                        f"No suitable image was found for the current task {self._demo} : {self._task}!"
                    )
                )
                return False
            # 2.2 get container name
            if not container_name:
                container_name = GenerateContainerName(self._demo, self._task)
            self.container_name = container_name
            # 2.3 start docker container
            self._docker_shell = DockerShellExecutor(container_name)

            # TODO(@wangkang): 这里需要优化，可以用钩子方法
            if self._demo == "vllm_musa":
                shm_size = "500g"
                pid = "host"
                network = "host"
                image_cmd = "bash"
            if self._demo == "ollama":
                image_cmd = ""

            container_start_status = self.start_container(
                container_name,
                volume_list=volume_list,
                port_list=port_list,
                network="host" if webui else network,
                pid=pid,
                workdir=workdir,
                shm_size=shm_size,
                image_cmd=image_cmd,
                extra_docker_para=docker_para,
                need_pull_image=need_pull_image,
            )
            if not container_start_status:
                return False

        # 3. prepare demo code for task
        self.set_demo_shell(volume_list=volume_list, webui=webui, repo=repo)

        # 4. run demo code
        if not self._use_docker:
            SHELL().run_cmd(f"bash {self._demo_shell}")
        else:
            # TODO(@wangkang): 优化
            # self._docker_shell.send_container_cmd(self._demo_shell)
            SHELL().run_cmd_with_error_print(
                f"docker exec -it {container_name} /bin/bash -c 'source ~/.bashrc; {self._demo_shell}'"
            )

        # 5. print demo necessary information
        self.print_demo_summary()


class TorchMusaDeployer(BaseDemoDeployer):
    def __init__(self) -> None:
        super().__init__()
        self._demo = CheckModuleNames.torch_musa.name
        self.gpu_map = {
            "X300": "S80",
            "S70": "S80",
            "S3000": "S80",
            "S90": "S4000",
            "S80ES": "S80",
        }

    def set_installer(self):
        if not self._use_docker:
            self._installer = PACKAGE_MANAGER[CheckModuleNames.torch_musa.name]

    def set_docker_image_requirement(self):
        if self._use_docker:
            # get gpu type
            gpu_type = get_gpu_type()[1]
            # TODO(@caizhi): lookup table and get right image
            if gpu_type not in ["S70", "S80", "S90", "S3000", "S4000", "X300", "S80ES"]:
                return

            gpu_type = self.gpu_map.get(gpu_type, gpu_type)
            self._image = f"registry.mthreads.com/mcconline/musa-pytorch-release-public:rc3.1.0-v1.3.0-{gpu_type}-py310"
            # 获取img_name,通过task，gpu_type等变量从yaml中获取镜像名
            # img = self.get_image(img_tag)

    def set_demo_shell(self, *args, **kwargs):
        if self._task == "base":
            self._demo_shell = ":"
        elif self._task == "train_cifar10":
            self._demo_shell = f"git clone {GITEE_REPO_URL} && cd tutorial_on_musa/pytorch/QuickStart/ && python train_cifar10.py 2>&1|tee GGN-train_cifar10.log"
        elif self._task == "yolov5":
            self._demo_shell = ":"
        else:
            print("No task is specified.")
            self._demo_shell = ":"


class vLLMMTTDeployer(BaseDemoDeployer):
    def __init__(self) -> None:
        super().__init__()
        self._demo = CheckModuleNames.vllm_mtt.name

    def precheck_gpu_type(self):
        gpu_type = get_gpu_type()[1]
        if gpu_type not in VLLM_SUPPORTED_GPUS:
            print(
                FontRed(
                    f"vLLM-MTT only supports S4000 Gpus, but the current GPU model is {gpu_type}"
                )
            )
            return False

    def set_installer(self):
        if not self._use_docker:
            self._installer = PACKAGE_MANAGER[CheckModuleNames.vllm_mtt.name]

    def set_docker_image_requirement(self):
        if self._use_docker:
            # get gpu type
            self._image = "registry.mthreads.com/mcconline/mtt-vllm-public:v0.2.1-kuae1.3.0-s4000-py38"
            # # 获取img_name,通过task，gpu_type等变量从yaml中获取镜像名
            # img = self.get_image(img_tag)

    def set_demo_shell(self, *args, **kwargs):
        if not self._use_docker:
            print(
                FontRed(
                    "The vLLM demo can only be run in a container, please run 'musa-deploy -h' to see how to use it"
                )
            )
            exit()
        if self._task == "base":
            self._demo_shell = ":"
        else:
            cmd_parts = []

            if not kwargs.get("repo"):
                clone_cmd = f"git clone {GITEE_REPO_URL}"
                if self.git_branch:
                    clone_cmd += f" -b {self.git_branch}"
                cmd_parts.append(clone_cmd)

                cmd_parts.append("cd tutorial_on_musa/vllm/demo")
            else:
                self._docker_shell.copy_to_docker(
                    kwargs.get("repo"), "/home/tutorial_on_musa"
                )
                cmd_parts.append("cd /home/tutorial_on_musa/vllm/demo")

            run_cmd = "bash ./run_vllm_serving.sh"
            run_cmd += f" --task {self._task}"

            if self.model:
                run_cmd += f" --model {self.model}"
            if self.converted_model:
                run_cmd += f" --converted-model {self.converted_model}"
            if self.tp_size:
                run_cmd += f" -tp-size {self.tp_size}"
            if kwargs.get("volume_list"):
                run_cmd += f" --download-model-dir {kwargs['volume_list'][0][-1]}"
            if kwargs.get("webui"):
                run_cmd += f" --vllm-host {get_IP_address()}"
            run_cmd += f" --container-name {self.container_name}"
            if kwargs.get("webui"):
                run_cmd += " --webui"

            cmd_parts.append(run_cmd)

            # 最终拼接为一行 shell 命令
            self._demo_shell = " && ".join(cmd_parts)


class vLLMMusaDeployer(BaseDemoDeployer):
    def __init__(self) -> None:
        super().__init__()
        self._demo = "vllm_musa"

    def set_installer(self):
        if not self._use_docker:
            pass

    def precheck_gpu_type(self):
        gpu_type = get_gpu_type()[1]
        if gpu_type not in VLLM_SUPPORTED_GPUS:
            print(
                FontRed(
                    f"vLLM-MUSA only supports S4000 Gpus, but the current GPU model is {gpu_type}"
                )
            )
            return False

    def set_docker_image_requirement(self):
        # get gpu type
        if self._version == "0.7.3":
            self._image = "registry.mthreads.com/mcconline/vllm-musa-qy2-py310:v0.7.3"
        if self._version == "0.8.4":
            self._image = (
                "registry.mthreads.com/mcconline/vllm-musa-qy2-py310:v0.8.4-release"
            )
        # # 获取img_name,通过task，gpu_type等变量从yaml中获取镜像名
        # img = self.get_image(img_tag)

    def set_demo_shell(self, *args, **kwargs):
        if not self._use_docker:
            print(
                FontRed(
                    "The vLLM demo can only be run in a container, please run 'musa-deploy -h' to see how to use it"
                )
            )
            exit()
        if not self.model:
            self._demo_shell = ":"
        else:  # just single node inference
            cmd_parts = []
            if not kwargs.get("repo"):
                clone_cmd = f"git clone {GITEE_REPO_URL}"
                if self.git_branch:
                    clone_cmd += f" -b {self.git_branch}"
                cmd_parts.append(clone_cmd)

                cmd_parts.append("cd tutorial_on_musa/vllm_musa/")
            else:
                self._docker_shell.copy_to_docker(
                    kwargs.get("repo"), "/home/tutorial_on_musa"
                )
                cmd_parts.append("cd /home/tutorial_on_musa/vllm_musa/")

            cmd_parts.append(
                f"bash start_vllm_server.sh {self.model} {self.extra_args} --container-name {self.container_name}"
            )

            if kwargs.get("webui"):
                cmd_parts[-1] += f" --host {get_IP_address()} --webui"

            self._demo_shell = " && ".join(cmd_parts)


class KuaeDeployer(BaseDemoDeployer):
    def __init__(self) -> None:
        super().__init__()
        # TODO: 待将kuae在utils中统一管理
        self._demo = "kuae"

    def precheck_gpu_type(self):
        # check for kuae image
        if self._use_docker:
            gpu_arch = get_gpu_type()[0]
            if gpu_arch != "mp_22":
                print(
                    FontRed(
                        f"The current GPU architecture is {gpu_arch}, but the kuae image only supports mp_22 architecture GPUs, such as S4000."
                    )
                )
                return False

    def set_installer(self):
        if not self._use_docker:
            self._installer = PACKAGE_MANAGER[CheckModuleNames.torch_musa.name]

    def set_docker_image_requirement(self):
        if self._use_docker:
            # get gpu type
            self._image = (
                "registry.mthreads.com/mcctest/mt-ai-kuae-qy2:v1.3.0-release-1031-ggn"
            )
            # # 获取img_name,通过task，gpu_type等变量从yaml中获取镜像名
            # img = self.get_image(img_tag)

    def set_demo_shell(self, *args, **kwargs):
        if self._task == "base":
            self._demo_shell = ":"
        elif self._task == "train_cifar10":
            self._demo_shell = f"git clone {GITEE_REPO_URL} && cd tutorial_on_musa/pytorch/QuickStart/ && python train_cifar10.py 2>&1|tee GGN-train_cifar10.log"
        else:
            print("No task is specified.")
            self._demo_shell = ":"


class OllamaDeployer(BaseDemoDeployer):
    def __init__(self) -> None:
        super().__init__()
        self._demo = "ollama"

    def set_installer(self):
        if not self._use_docker:
            self._installer = PACKAGE_MANAGER[CheckModuleNames.torch_musa.name]

    def precheck_gpu_type(self):
        gpu_type = get_gpu_type()[1]
        if gpu_type not in OLLAMA_SUPPORT_GPUS:
            print(
                FontRed(
                    f"Ollama only supports {OLLAMA_SUPPORT_GPUS} Gpus, but the current GPU model is {gpu_type}."
                )
            )
            return False

    def set_demo_shell(self, *args, **kwargs):
        if self._task == "base":
            self._demo_shell = ":"

    def set_docker_image_requirement(self):
        if self._use_docker:
            # get gpu type
            self._image = "registry.mthreads.com/public/mt-ai/mthreads-ollama:latest-qy1-rc3.1.1-2"

    def print_demo_summary(self):
        if self._use_docker:
            print(
                f"\nGuide:\n"
                f"{FontGreen('✔ Step 1:')} Run the following command inside the container({self.container_name}) to try out the DeepSeek inference service:\n"
                f"   {FontGreen('ollama run deepseek-r1:7b --verbose')}\n"
                f"   → Supported models: 'deepseek-r1:1.5b, 7b, 8b, 14b'\n"
                f"{FontGreen('✔ Step 2:')} Model weights will be stored in '/root/.ollama' inside the container.\n"
            )
