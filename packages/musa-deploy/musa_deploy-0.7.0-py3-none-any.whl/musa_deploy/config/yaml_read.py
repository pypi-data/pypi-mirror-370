import yaml
from typing import Literal
from dataclasses import dataclass
import os
import re
import sys
import cpuinfo
import distro
from musa_deploy.utils import FontRed

DRIVER_VERSION_MAP = {
    "20241025": "3.1.0",
    "20240703": "3.0.1",
    "20240731": "3.0.1",
    "20250211": "3.1.1",
    "20250218": "3.1.2",
}
EX_DRIVER_CLINFO_MAP = {
    "3.1.0": "20241025",
    "3.0.1": "20240731",
    "3.1.1": "20250211",
}

IN_DRIVER_CLINFO_MAP = {
    "3.1.2": "20250218",
    "3.1.1": "20250211",
    "3.1.0": "20241025",
    "3.0.1": "20240703",
}


@dataclass
class ImageClass:
    image_type: str = ""
    driver_version: str = ""
    gpu_type: str = ""
    image_tag: str = ""


class YAML:

    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        self.yaml_data = self.get_yaml_data(self.yaml_path)

    def get_yaml_data(self, file_path):
        """reade yaml file"""
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        return data

    def get_sub_key_list(self, module_name):
        dict_list = self.yaml_data[module_name]
        sub_key_list = list(dict_list[0].keys())
        return sub_key_list

    def get_dict_in_list(self, module_name: str, special_version: str) -> int:
        """
        Determine this dictionary in the list by v of the first kv pair in the dictionary
        return the index of the dictionary

        Example:
        'driver': [{'Driver_Version_From_Dpkg': '2.7.0-rc3-0822',
             'dependency': {'supported_kernel': ['5.4.0-42-generic',
                                                 '5.15.0-105-generic'],
                            'unsupported_kernel': ['5.15.0-127-generic']}}],
        special_version_dict, first_key = YAML(file_path).get_dict_in_list('driver', '2.7.0-rc3-0822')

        special_version_dict:
                    {'Driver_Version_From_Dpkg': '2.7.0-rc3-0822',
                    'dependency': {'supported_kernel': ['5.4.0-42-generic',
                                                        '5.15.0-105-generic'],
                                    'unsupported_kernel': ['5.15.0-127-generic']}}
        first_key: 'Driver_Version_From_Dpkg'
        """
        dict_list = self.yaml_data[module_name]  # get special module version list
        first_key, *_ = self.get_sub_key_list(module_name)
        for d in dict_list:
            if str(d[first_key]) == special_version:
                return d

    def print_error_result(self, data_dict, name: str):
        version_result = []
        for data in data_dict:
            if data.get(name, 0) != 0:
                version = DRIVER_VERSION_MAP.get(str(data.get(name)), data.get(name))
                if version not in version_result:
                    version_result.append(version)
            elif data.get("name") == name:
                version = DRIVER_VERSION_MAP.get(
                    str(data.get("version")), data.get("version")
                )
                if version not in version_result:
                    version_result.append(version)
        return version_result


# class ImageYaml(YAML):
# TODO:@liang.geng
class ImageYaml:
    def __init__(self, path: str):
        self.root_path = path
        self.images_dict = {
            "torch_musa": os.path.join(
                self.root_path, "download/images/torch_musa_images.yaml"
            ),
            "ubuntu": os.path.join(
                self.root_path, "download/images/ubuntu_images.yaml"
            ),
            "vllm": os.path.join(self.root_path, "download/images/vllm_images.yaml"),
        }

    def _get_image_data(self, image_type: str):
        # read image yaml
        data = self.get_yaml_data(self.images_dict[image_type])
        # get image data
        image_dicts = data[image_type]
        # get image_name without tag
        image_name = image_dicts["image_name"]
        # get version list
        image_list = image_dicts["version"]
        return image_name, image_list

    def get_image_name(self, image_args: ImageClass):
        """get image name
        ImageClass:
        - image_type: ubuntu, torch_musa, mtt-vllm
        - dri_version: xxxx
        - gpu_type: s70, s80, s3000, s4000, all
        - tag: py38, py39, py310
        """
        image_name, image_list = self._get_image_data(image_args.image_type)
        image_tag = str(self._get_image_tag(image_list, image_args))
        return image_name + ":" + image_tag

    def get_image_list(
        self, image_type: str, image_version: str, gpu_arch: str
    ) -> list:
        """
        Get image list from yaml file according to image type and driver version
        """
        image_list = []
        image_name, image_all_versions_list = self._get_image_data(image_type)
        for images in image_all_versions_list:
            if images["version"] == image_version:
                for gpu_type in list(images.keys())[1:]:
                    if gpu_type == gpu_arch:
                        image_list += list(images[gpu_type].values())

                return [image_name + ":" + image_tag for image_tag in image_list]

    def _get_image_tag(self, image_list: list, image_args: ImageClass):
        if image_args.image_type in ["mtt-vllm", "ubuntu", "torch_musa"]:
            image_dict = self.get_dict_in_list(image_args.driver_version, image_list)
            image_tag = image_dict[image_args.gpu_type][image_args.image_tag]
            return image_tag
        else:
            print("Image type not supported, only support mtt-vllm, ubuntu, torch_musa")
            exit()


class ComponentsYaml(YAML):
    """
    get driver、mtml、mt-container-toolkit、sgpu-dkms info
    """

    def __init__(self, in_host):
        self._in_host = in_host
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.driver_yaml = os.path.join(self.root_path, "download/driver.yaml")
        self.mtml_yaml = os.path.join(self.root_path, "download/mtml.yaml")
        self.mt_container_toolkit_yaml = os.path.join(
            self.root_path, "download/mt-container-toolkit.yaml"
        )
        self.sgpu_dkms_yaml = os.path.join(self.root_path, "download/sgpu-dkms.yaml")
        self.mccl_yaml = os.path.join(self.root_path, "download/mccl.yaml")
        self.mudnn_yaml = os.path.join(self.root_path, "download/mudnn.yaml")
        self.musa_toolkits_yaml = os.path.join(
            self.root_path, "download/musa_toolkits.yaml"
        )
        self.smartio_yaml = os.path.join(self.root_path, "download/smartio.yaml")
        self.torch_musa_yaml = os.path.join(self.root_path, "download/torch_musa.yaml")
        self.sdk_yaml = os.path.join(self.root_path, "download/sdk.yaml")
        self._in_url = "oss.mthreads.com"

        self.components_dict = {
            "driver": self.driver_yaml,
            "mtml": self.mtml_yaml,
            "container_toolkit": self.mt_container_toolkit_yaml,
            "sgpu-dkms": self.sgpu_dkms_yaml,
            "mccl": self.mccl_yaml,
            "mudnn": self.mudnn_yaml,
            "musa_toolkits": self.musa_toolkits_yaml,
            "smartio": self.smartio_yaml,
            "torch_musa": self.torch_musa_yaml,
            "sdk": self.sdk_yaml,
        }

    def get_component_info(self, component_type: str, version: str):  # type: ignore
        """
        get info: version, url, sha256
        """
        cpu_model = cpuinfo.get_cpu_info().get("brand_raw", "Unknown")
        os_name = distro.name(pretty=True)
        partten = re.compile(
            r"\b(Intel|Hygon|Kunpeng|Ubuntu|UnionTech|Kylin)\b", re.IGNORECASE
        )
        cpu_model = partten.findall(cpu_model)[0]
        os_name = partten.findall(os_name)[0]
        # 测试在kylin系统，Hygon Kunpeng cpu下载sdk
        if os.getenv("DOWNLOAD_CPU_TEST"):
            cpu_model = os.getenv("DOWNLOAD_CPU_TEST")
        if os.getenv("DOWNLOAD_OS_TEST"):
            os_name = os.getenv("DOWNLOAD_OS_TEST")
        if "UnionTech".casefold() == os_name.casefold():
            os_name = "Ubuntu"
            cpu_model = "Intel"
        if (
            "Ubuntu".casefold() == os_name.casefold()
            and "Hygon".casefold() == cpu_model.casefold()
        ):
            cpu_model = "Intel"
        file_path = self.components_dict[component_type]
        if component_type == "driver" and self._in_host:
            version = IN_DRIVER_CLINFO_MAP.get(version, version)
        if component_type == "driver" and not self._in_host:
            version = EX_DRIVER_CLINFO_MAP.get(version, version)

        data = self.get_yaml_data(file_path)

        if version is None:
            for item in data:
                if item.get("url", 0) == 0 and (
                    item.get("os", "Ubuntu").casefold() == os_name.casefold()
                    and item.get("cpu", "Intel").casefold() == cpu_model.casefold()
                ):
                    return item
                elif (self._in_url in item.get("url")) == self._in_host and (
                    item.get("os", "Ubuntu").casefold() == os_name.casefold()
                    and item.get("cpu", "Intel").casefold() == cpu_model.casefold()
                ):
                    return item
        for d_dict in data:
            if str(d_dict["version"]) == version and (
                d_dict.get("url", 0) == 0
                and (
                    d_dict.get("os", "Ubuntu").casefold() == os_name.casefold()
                    and d_dict.get("cpu", "Intel").casefold() == cpu_model.casefold()
                )
            ):
                return d_dict
            elif str(d_dict["version"]) == version and (
                (self._in_url in d_dict.get("url")) == self._in_host
                and (
                    d_dict.get("os", "Ubuntu").casefold() == os_name.casefold()
                    and d_dict.get("cpu", "Intel").casefold() == cpu_model.casefold()
                )
            ):
                return d_dict
        if self._in_host and component_type in ["sdk"]:
            print(
                f"{FontRed('ERROR:')} The {component_type} only supports downloading over an external network."
            )
        # TODO (@wangwenxing) 目前这几个组件需要区分OS环境和CPU环境，需要对下载进行区分。
        elif component_type in ["sdk", "driver", "mtml", "container_toolkit"]:
            print(
                f"""{FontRed('ERROR:')} OS: {os_name}, CPU: {cpu_model}, version of the {component_type} you want to downloand is incorrect.\
 The currently supported versions are {[DRIVER_VERSION_MAP.get(str(d['version']), d['version']) for d in data if (d['os'].casefold() == os_name.casefold() and d['cpu'].casefold() == cpu_model.casefold())]}"""
            )
        else:
            print(
                f"""{FontRed('ERROR:')} The version of the {component_type} you want to download is incorrect.\
 The currently supported versions are {self.print_error_result(data, component_type)}"""
            )
        sys.exit(1)

    def get_dependency_component_version(
        self,
        component_name: Literal[
            "mt-container-toolkit", "driver", "musa_runtime", "torch_musa"
        ],
        component_version: str,
        component_commit_id: str = "",
    ):
        data = self.get_yaml_data(self.requirements)
        # musa_runtime need commit id for query
        query_version = component_version + component_commit_id
        dependency_component_info = data[component_name][query_version]
        return dependency_component_info


class KuaeAndSdkYaml(YAML):
    def __init__(self, name="kuae", in_host=False):
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.platform_yaml = os.path.join(self.root_path, "download/kuae_sdk.yaml")
        self._name = name
        self._in_host = in_host

    def get_component_info(self, platform_name: str, version: str):
        data = self.get_yaml_data(self.platform_yaml)["kuae_sdk"]
        if platform_name == "driver" and self._in_host:
            version = IN_DRIVER_CLINFO_MAP.get(version, version)
        if platform_name == "driver" and not self._in_host:
            version = EX_DRIVER_CLINFO_MAP.get(version, version)
        for d_dict in data:
            if (
                not version
                and d_dict.get(platform_name, 0) != 0
                and d_dict.get(self._name, 0) != 0
            ):
                return d_dict
            if (
                str(d_dict.get(platform_name, 0)) == version
                and d_dict.get(self._name, 0) != 0
            ):
                return d_dict
        print(
            f"""{FontRed('ERROR:')} The version of the {platform_name} you want to download is incorrect.\
 The currently supported versions are {self.print_error_result(data, platform_name)}"""
        )
        sys.exit(1)

    def get_all_data(self):
        return self.get_yaml_data(self.platform_yaml)


if __name__ == "__main__":
    # yaml_obj = ImageYaml()
    # image_class = ImageClass("torch_musa", "1.3.0", "s80", "py38")
    # # 获取特定镜像
    # print(yaml_obj.get_image_name(image_class))
    # print("*"*30)
    # # 获取特定驱动支持的镜像列表
    # print(yaml_obj.get_image_list('torch_musa', "s80", '1.3.0'))
    # print("*"*30)
    # components_obj = ComponentsYaml()
    # print(
    #     components_obj.get_dependency_component_version(
    #         "mt-container-toolkit", "1.9.0-1"
    #     )
    # )
    # print(components_obj.get_dependency_component_version("driver", "2.7.0-rc3-0822"))
    # print(components_obj.get_dependency_component_version("musa_runtime", ""))

    dependency_obj = YAML("version_requirements.yaml")
    dict, first_key = dependency_obj.get_dict_in_list("torch_musa", "1.3.0+60e54d8")
    first_key = dependency_obj.get_first_key("torch_musa")
    print(first_key)
