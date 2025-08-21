import os
import sys
import hashlib
from musa_deploy.check import CHECKER
from musa_deploy.utils import get_gpu_type
from musa_deploy.config.yaml_read import ComponentsYaml, KuaeAndSdkYaml
from musa_deploy.utils import (
    download_file_with_progress,
    FontRed,
    generate_name_with_time,
    SHELL,
)


def get_python_version():
    version_info = sys.version_info
    # the environment variable `get_python_version()_TEST` is merely for simulation testing purposes.
    # Do not set this environment variable during normal use.
    return (
        f"py{version_info.major}{version_info.minor}"
        if not os.getenv("PYTHON_VERSION_TEST")
        else os.getenv("PYTHON_VERSION_TEST")
    )


WARNING_DEFAULT = "WARNING:"
PRE_CHECK_REFLECT = {
    "kuae": "Driver_Version_From_Clinfo",
    "container_toolkit": "Driver_Version_From_Clinfo",
    "smartio": "Driver_Version_From_Clinfo",
    "sdk": "Driver_Version_From_Clinfo",
    "driver": "Driver_Version_From_Clinfo",
    "musa": "Driver_Version_From_Clinfo",
    "mccl": "MUSAToolkits",
    "mudnn": "MUSAToolkits",
    "torch_musa": "MUSAToolkits",
    "musa_toolkits": "Driver_Version_From_Clinfo",
    "mtml": "Driver_Version_From_Clinfo",
}
POST_CHECK_REFLECT = {
    "MUSAToolkits": "musa_toolkits",
    "Driver_Version_From_Clinfo": "driver",
}
GPU_ARCH = {"mp_31": "ph1", "mp_22": "qy2", "mp_21": "qy1"}


class Downloader:

    def __init__(self) -> None:
        self._name = None
        self._version = None
        self._folder_path = None
        self._download_link = list()
        self._file_path = dict()
        self._inhouse = self._pin_host()
        self._yaml_dict = self._get_yaml_dict()
        self._prechecker = self._get_prechecker()
        self._gpu_arch = get_gpu_type()
        self._arch = GPU_ARCH.get(
            self._gpu_arch[0] if self._gpu_arch else self._gpu_arch
        )

    def precheck(self, name):
        # 该环境变量仅用于运行测试用例
        if os.getenv("MUSA_TOOLKITS_TEST"):
            return "musa_toolkits", os.getenv("MUSA_TOOLKITS_TEST")
        check_status, _ = self._prechecker[name].check()
        # TODO: 暂不考虑目标检查
        # if not check_status:
        #     print(
        #         f"{FontRed(WARNING_DEFAULT)} Pre-component checking is Failing, please try running 'musa-deploy -c'"
        #     )
        # TODO 对于获取版本后续会增加函数，保证版本具有唯一性。
        version = self._prechecker[name].get_version(PRE_CHECK_REFLECT[name])
        if version:
            if "+" in version:
                version = version.split("+")[0]
            if " " in version:
                version = version.split(" ")[0]
            # TODO (@wenxing.wang) 目前driver的clinfo结果在kylin中是20250211，在ubuntu中是20250218，等后续统一版本，可以删除。
            if "2025" in version:
                version = "20250211"
            if version == "UNKNOWN":
                version = None
        return POST_CHECK_REFLECT[PRE_CHECK_REFLECT[name]], version

    def _get_yaml_dict(self):
        kuae_sdk_yaml = KuaeAndSdkYaml(in_host=self._inhouse)
        components_yaml = ComponentsYaml(self._inhouse)
        return {
            "kuae": kuae_sdk_yaml,
            "sdk": components_yaml,
            "driver": components_yaml,
            "mccl": components_yaml,
            "container_toolkit": components_yaml,
            "mtml": components_yaml,
            "mudnn": components_yaml,
            "musa_toolkits": components_yaml,
            "sgpu-dkms": components_yaml,
            "smartio": components_yaml,
            "torch_musa": components_yaml,
        }

    def _pin_host(self):
        # 测试下载外网数据
        if os.getenv("DOWNLOAD_IN_HOST_TEST"):
            return os.getenv("DOWNLOAD_IN_HOST_TEST") == "True"
        _, _, oss_code = SHELL().run_cmd("ping -c 1 oss.mthreads.com")
        _, _, baidu_code = SHELL().run_cmd("ping -c 1 www.baidu.com")
        if os.getenv("DOWNLOAD_NOT_NETWORK"):
            oss_code = 1
            baidu_code = 1
        if baidu_code == 0:
            return False
        elif oss_code == 0:
            return True
        else:
            print(
                f"{FontRed('ERROR:')} The machine is unable to connect to the network. Please check the machine's network configuration."
            )
            sys.exit(1)

    def _calculate_md5(self, file_path, sha):
        hash_md5 = hashlib.md5()
        if os.path.exists(file_path):
            with open(file_path, "rb") as files:
                for chunk in iter(lambda: files.read(4096), b""):
                    hash_md5.update(chunk)
        if hash_md5.hexdigest() != sha:
            print(
                f"{FontRed(WARNING_DEFAULT)} The file of {file_path} MD5 verification failed. Please download it again."
            )

    def _get_prechecker(self):
        driver_check = CHECKER["driver"]()
        musa_check = CHECKER["musa"]()
        host_check = CHECKER["host"]()
        return {
            "kuae": driver_check,
            "container_toolkit": driver_check,
            "smartio": driver_check,
            # TODO(@wangkang): 默认安装musa检测driver_Check(暂时不考虑容器内安装)
            "musa": driver_check,
            "mccl": musa_check,
            "mudnn": musa_check,
            "torch_musa": musa_check,
            "driver": host_check,
            "sdk": driver_check,
            "musa_toolkits": driver_check,
            "mtml": driver_check,
        }

    def get_version_and_download_link(self):
        if not self._inhouse and self._name in [
            "driver",
            "musa_toolkits",
            "mccl",
            "mudnn",
            "mutriton",
        ]:
            kuae_sdk_yaml = KuaeAndSdkYaml("sdk", self._inhouse)
            component = kuae_sdk_yaml.get_component_info(self._name, self._version)
            self._name = "sdk"
            self._version = str(component.get("sdk"))
        pre_module, pre_version = self.precheck(self._name)
        if pre_version:
            check_yaml = KuaeAndSdkYaml(self._name, self._inhouse).get_component_info(
                pre_module, pre_version
            )
            if self._version and str(check_yaml[self._name]) != str(self._version):
                print(
                    f"{FontRed(WARNING_DEFAULT)} The version({self._version}) of the {self._name} you want to download does not match the version of dependencies installed in the environment."
                )
        yaml_dict = self._yaml_dict[self._name].get_component_info(
            self._name, self._version
        )
        self._version = (
            yaml_dict.get("version")
            if yaml_dict.get("version", 0) != 0
            else yaml_dict.get(self._name)
        )
        if self._name == "kuae":
            for k, val in yaml_dict.items():
                if k == "torch_musa":
                    component = ComponentsYaml(self._inhouse).get_component_info(
                        k, val if isinstance(val, str) else str(val)
                    )
                    torch_musa_link = self.get_torch_musa_link(component)
                    self._download_link.append(torch_musa_link)
                elif k != "kuae":
                    component = ComponentsYaml(self._inhouse).get_component_info(
                        k, val if isinstance(val, str) else str(val)
                    )
                    self._download_link.append(component)
        elif self._name == "torch_musa":
            torch_musa_link = self.get_torch_musa_link(yaml_dict)
            self._download_link.append(torch_musa_link)
        else:
            self._download_link.append(yaml_dict)

    def get_torch_musa_link(self, yaml_dict):
        python_version = get_python_version()
        if yaml_dict.get(python_version, 0) != 0:
            if yaml_dict[python_version].get(self._arch, 0) != 0:
                return yaml_dict[python_version]
            else:
                print(
                    f"torch_musa does not support the current architecture({self._arch})."
                )
                sys.exit(1)
        else:
            print(
                f"torch_musa({yaml_dict['version']}) does not support the current python version({python_version})."
            )
            sys.exit(1)

    def make_folder(self):
        if not os.path.exists(self._folder_path):
            os.makedirs(self._folder_path, exist_ok=True)

    def _download_and_md5(
        self, name: str, url: str, folder_path: str, sha256: str, version: str = "None"
    ):
        folder_path = os.path.normpath(folder_path)
        file_name = url.split("/")[-1]
        if name == "sdk" and file_name.endswith(".zip"):
            save_path = f"{folder_path}/sdk_rc{version}.zip"
        elif name == "container_toolkit" and file_name.endswith(".zip"):
            save_path = f"{folder_path}/mt-container-toolkit-{version}.zip"
        else:
            save_path = f"{folder_path}/{file_name}"
        download_file_with_progress(url, save_path)
        self._file_path[name] = os.path.abspath(save_path)
        self._calculate_md5(save_path, sha256)

    def download_by_url(self):
        # TODO 需要重新解析torch_musa的dict，并添加MD5的比对,等sdk的url解析出来，还要针对这块下载进行重新编写
        for component in self._download_link:
            if component.get("url", 0) != 0:
                self._download_and_md5(
                    component["name"],
                    component["url"],
                    self._folder_path,
                    component["md5"],
                    component["version"],
                )
            else:
                for key, value in component.items():
                    if value.get("url", 0) != 0:
                        self._download_and_md5(
                            key, value["url"], self._folder_path, value["md5"]
                        )
                    elif key == self._arch:
                        for key_deep, value_deep in value.items():
                            self._download_and_md5(
                                key_deep,
                                value_deep["url"],
                                self._folder_path,
                                value_deep["md5"],
                            )

    def download(self, name, version=None, path=None):
        # TODO 针对driver的version，太过于混乱，目前输入3.1.0->20241025, 3.0.1->20240703
        self._version = version
        self._folder_path = path if path else generate_name_with_time("./musa_deploy")
        if name == "musa":
            self._name = "musa_toolkits"
        else:
            self._name = name
        if not self._inhouse and self._name == "kuae":
            print(
                f"{FontRed('ERROR:')} The download of kuae failed. Please verify that you can successfully 'ping oss.mthreads.com'."
            )
            sys.exit(1)
        self.get_version_and_download_link()
        self.make_folder()
        self.download_by_url()

        return self._file_path

    def get_path(self):
        return self._file_path

    def check_python_version(self):
        current_py_version = get_python_version()
        check_yaml = KuaeAndSdkYaml(self._name).get_all_data()
        if current_py_version not in check_yaml["python_versions"]:
            print(
                f"""{FontRed(WARNING_DEFAULT)} The current environment's Python version is not yet supported. \
The currently supported versions are {check_yaml["python_versions"]}"""
            )
            sys.exit(1)
