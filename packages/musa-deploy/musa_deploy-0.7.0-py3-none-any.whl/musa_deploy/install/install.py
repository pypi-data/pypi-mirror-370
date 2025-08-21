import os
import re
from abc import ABC, abstractmethod
from typing import Literal
import sys
import platform


from musa_deploy.check import CHECKER
from musa_deploy.check.utils import (
    Status,
    CheckModuleNames,
    HostModule,
    DriverModule,
    MusaModule,
    TorchMusaModule,
    ContainerToolkitModule,
    EXECUTED_ON_HOST_FLAG,
    DRIVERTOOLKIT_PATH,
)
from musa_deploy.download import DOWNLOADER
from musa_deploy.utils import (
    SHELL,
    MUSA_BIN_PATH,
    MUSA_LIB_PATH,
    FontGreen,
    FontRed,
    get_pip_path,
    BaseDecompressor,
    require_root_privileges_check,
    generate_name_with_time,
    continue_or_exit,
    get_original_command,
    get_os_name,
)

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
CURRENT_WORK_DIR = os.getcwd()

# TODO(@wangkang): 驱动版本这里做临时映射，后面看怎么优化
DRIVER_VERSION_MAP = {
    "3.1.0": "2.7.0",
    "3.0.1": "1.2.0",
    "3.1.1": "2.7.1",
    "3.0.0-rc4.0.0-server": "3.0.0-rc4.0.0-server",
    "4.1.0": "3.0.0-rc-KuaE2.0",
}


class DownloadDecompressor(BaseDecompressor):

    def __init__(self, archive_dict: dict):
        super().__init__()
        self._archive_dict = archive_dict
        self._decompress_dict = dict()

    def create_dir_and_extract(self, archive_path: str) -> str:
        # 1. create output dir base on archive file name
        if os.path.isfile(archive_path) and re.search(
            r"\.(tar\.gz|tar|zip)$", archive_path, re.IGNORECASE
        ):
            to_create_dir = generate_name_with_time(
                re.sub(
                    r"\.tar\.gz$|\.zip|\.tar$", "", archive_path, flags=re.IGNORECASE
                )
            )  # 去掉后缀并创建输出目录
            output_dir = self.create_output_dir(to_create_dir)
        else:
            return archive_path
        # 2. extract content to output_dir
        if archive_path.endswith(".tar.gz"):
            self.extract_tar_gz(archive_path, output_dir)
        elif archive_path.endswith(".zip"):
            self.extract_zip(archive_path, output_dir)
        else:
            raise ValueError(
                f"Unsupported archive format: '{archive_path}'. "
                "Supported formats are '.tar.gz' and '.zip'. "
                f"Please check the file path and ensure it uses a valid archive format."
            )
        return output_dir

    def extract_container_toolkit(self, tag: str, archive: str):
        """
        get mt-container-toolkit, mtml, sgpu-dkms deb path

        Attention:
        self.archive_path: /xxx/mt-container-toolkit-x.x.x.zip

        Returns:
            dict: A dictionary containing the paths to the downloaded files, eg:
            {
                "mtml": "/xxx/mtml_x.x.x.deb",
                "sgpu-dkms": "/xxx/sgpu-dkms_x.x.x.deb",
                "container-toolkit": "/xxx/mt-container-toolkit-x.x.x.deb"
            }
        """
        packages_path_dict = {}
        # 1. create output_dir and extract archive to output_dir
        output_dir = self.create_dir_and_extract(archive)
        # 2. get deb path in output_dir by regex
        deb_pattern = re.compile(
            rf"([^.]*({ContainerToolkitModule.mtml.name}|{ContainerToolkitModule.sgpu_dkms.name.replace('_', '-')}|{ContainerToolkitModule.container_toolkit.name.replace('_', '-')}).*\.deb$)",
            re.IGNORECASE,
        )

        for root, dirs, files in os.walk(output_dir):
            for file in files:
                match = deb_pattern.match(file)
                if match:
                    abs_path = os.path.abspath(os.path.join(root, file))
                    packages_path_dict[match.group(2)] = abs_path

        self._decompress_dict.update(packages_path_dict)

    def extract_musa_single_component(
        self, tag: str, archive: str, target_filename_part="install"
    ):
        """
        get install.sh path for musa_toolkits, mudnn or mccl

        Args:
            component_name (str): The name of the component to extract information for, eg: musa_toolkits, mudnn, mccl, etc.
            target_filename_part (str): The part of the filename to search for, eg: install_mudnn.sh
        """
        pattern = re.compile(
            r"""
            .*         #
            install    # filename contain str: "install"
            .*
            \.sh$      # end with .sh
            """,
            re.IGNORECASE | re.VERBOSE,
        )
        packages_path_dict = {}
        output_dir = self.create_dir_and_extract(archive)
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if pattern.match(file):
                    packages_path_dict[tag] = os.path.join(root, file)
                    break
        self._decompress_dict.update(packages_path_dict)

    def extract_sdk_components(self, tag: str, archive: str):
        """
        get mccl, mudnn, musa_toolkits, driver, smartio file path

        Attention:
            We assume mccl, mudnn, and musa_toolkit file path are compressed packages, while the others are .deb packages.
        """
        packages_path_dict = {}
        output_dir = self.create_dir_and_extract(archive)
        # TODO(@caizhi): 取名不统一(musa_toolkits, smartio)
        pattern = re.compile(
            r"""
            .*         # Match the general part of the path
            (?P<keyword>  # Capture the keyword group
            mccl                                    |  # Match "mccl"
            mudnn                                   |  # Match "mudnn"
            musa_toolkits                           |  # Match "musa_toolkits"
            driver                                  |  # Match "driver"
            smartio                                 # Match "smartio"
            )
            .*
            \.         # Match the period before the file extension
            (tar\.gz|deb|zip|tar)$  # Match supported file extensions
            """,
            re.IGNORECASE | re.VERBOSE,
        )
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                match = pattern.match(file_path)
                if match:
                    # get mccl, mudnn, musa_toolkits, driver, smartio file path
                    # mccl, mudnn, musa_toolkits is .tar.gz file
                    packages_path_dict[match.group("keyword").lower()] = file_path
        self._decompress_dict.update(packages_path_dict)
        self.extract_musa_single_component(
            "musa_toolkits", self._decompress_dict["musa_toolkits"]
        )
        self.extract_musa_single_component(
            MusaModule.mudnn.name, self._decompress_dict[MusaModule.mudnn.name]
        )
        if self._decompress_dict.get(
            MusaModule.mccl.name, None
        ):  # not all sdk has mccl, eg: 3.1.1
            self.extract_musa_single_component(
                MusaModule.mccl.name, self._decompress_dict[MusaModule.mccl.name]
            )

    def decompress(self):
        for key, value in self._archive_dict.items():
            if "container_toolkit" in key:
                self.extract_container_toolkit(key, value)
            elif "sdk" in key or "smartio" in key:
                self.extract_sdk_components(key, value)
            elif "musa_toolkits" in key or "mudnn" in key or "mccl" in key:
                self.extract_musa_single_component(key, value)
            else:
                self._decompress_dict[key] = value
        return self._decompress_dict


class PackageManager(ABC):

    def __init__(self):
        self._name = None
        self._checker = None
        self._preinstaller = list()
        self._target_package_name = None  # 目标包名
        self._dependency_package_list = []  # 依赖包列表
        self._shell = SHELL()
        self._version = None
        self._pkg_path_dict = dict()
        self._driver_version = None  # Driver version is always a key element
        self._auto_install = False
        # TODO(@caizhi): need store all recommendation
        self._last_recommendation = list()
        self._is_installed_file_flag = (
            None  # using for verify after uninstall by sh script
        )
        # =========
        # need check name
        self._gmi_version = None

    def precheck_environment(self):
        pass

    def update_version(self, version: str = None):
        self._target_version = version

    @abstractmethod
    def uninstall_cmd(self):
        # TODO(@wangkang): torch_musa存在需要多次卸载的情况
        pass

    def verify_is_installed(
        self,
        package_name: str,
        is_installed_file_flag: str,
        package_type: Literal["dpkg", "pip", "apt", "sh"],
    ) -> bool:
        """
         Verifies whether a package or directory is installed or exists based on its type.

        Args:
            package_name_or_dir (str):
                The name of the package (for dpkg, pip, or apt) or the directory path (for sh).
            package_type (Literal["dpkg", "pip", "apt", "sh"]):
                The type of the package or check method:
                - "dpkg": if the package is managed by dpkg.
                - "pip": if the package is managed by pip.
                - "apt": if the package is managed by apt.
                - "sh": if the directory exists(package is installed via the sh script).

        Returns:
            bool: True if the package or directory is installed or exists, False otherwise.

        """
        if package_type in ["dpkg", "apt"]:
            stdout, _, _ = self._shell.run_cmd(f"dpkg -s {package_name}")
        elif package_type == "pip":
            stdout, _, _ = self._shell.run_cmd(
                f"pip show {package_name}"
            )  # pip show package_name
        elif package_type == "sh":
            stdout, _, _ = self._shell.run_cmd(
                f"test -e {package_name}"
            )  # test -e path

        return bool(stdout)

    def is_uninstalled(self):
        name = self._name
        # TODO: （wangkang）能否对外暴露区分大小写，内部逻辑统一lower()处理
        name_map = {"driver": "Driver", "smartio": "mt_peermem"}
        name = name_map.get(name, name)
        if name == "host":
            return any(
                not self.verify_is_installed(
                    package_name=pkg, is_installed_file_flag=None, package_type="apt"
                )
                for pkg in self._dependency_package_list
            )
        else:
            status = self._checker.get_key_status(name)
            if status == Status.UNINSTALLED:
                return True
            else:
                return False

    def uninstall(self):
        # uninstall
        self.uninstall_cmd()
        # verify
        uninstall_package_list = []
        if self._target_package_name is not None:
            uninstall_package_list.append(self._target_package_name)
        if self._dependency_package_list:
            uninstall_package_list.extend(self._dependency_package_list)
        for package_name in uninstall_package_list:
            is_installed_bool = self.verify_is_installed(
                package_name=self._target_package_name,
                package_type=self._package_type,
                is_installed_file_flag=self._is_installed_file_flag,
            )
            if is_installed_bool:
                if self._name == CheckModuleNames.driver.name:
                    print(
                        f"Warning: maybe uninstall {FontRed(f'{self._name}')} Failed, please uninstall it manually!"
                    )
                else:
                    print(
                        f"Warning: maybe uninstall {FontRed(f'{package_name}')} Failed, please uninstall it manually!"
                    )
            else:
                if self._name == CheckModuleNames.driver.name:
                    print(f"Successfully uninstall {FontRed(f'{self._name}')}.")
                else:
                    print(f"Successfully uninstall {FontRed(f'{package_name}')}.")

    @abstractmethod
    def install_cmd(self) -> bool:
        """
        return bool -> need reboot
        """
        pass
        return False

    def set_driver_target_version(self, driver_version: str):
        self._driver_version = driver_version

    def version_lookup(self):
        if (
            self._name == CheckModuleNames.container_toolkit.name
            and self._driver_version
        ):
            return self._driver_version

        pre_component_version = None
        # TODO(@caizhi): please implement me here
        # print("=============please implement version_lookup==========")
        return pre_component_version

    def download(self):
        # TODO(@wangkang): 代码需要优化迁移(for kylin)
        if (
            self._name == "container_toolkit"
            and self._target_version == "2.0.0"
            and get_os_name().lower() == "kylin"
        ):
            for key, value in {self._name: "2.0.0", "mtml": "2.0.0"}.items():
                archive_dict = DOWNLOADER().download(key, value)
                if key == self._name:
                    self._pkg_path_dict["container-toolkit"] = archive_dict[key]
                else:
                    self._pkg_path_dict.update(archive_dict)
        else:
            archive_dict = DOWNLOADER().download(self._name, self._target_version)
            self._pkg_path_dict.update(DownloadDecompressor(archive_dict).decompress())

    def _gmi_map_version(self, version: str):
        if version not in DRIVER_VERSION_MAP:
            print(
                f"Error: Unknown driver version mapping for: {version}", file=sys.stderr
            )
            sys.exit(1)
        return DRIVER_VERSION_MAP.get(version)

    def install(
        self,
        version: str = None,
        path: str = None,
        allow_force_install=False,
        auto_install: bool = False,
    ):
        self._target_version = version
        self._auto_install = auto_install
        # TODO(@gl): should check the version is valid
        # temp for target_version -> driver version, avoid confusion
        if self._name == "driver":
            if version:
                self._gmi_version = self._gmi_map_version(version)

        # 1. first execute check
        success_flag, status = self._checker.check()
        # 2. if dependency check failed, return directly
        if self._checker._has_dependency_failed:
            print(
                f"The pre-requisite dependency check failed. Please manually install {self._name}. For detailed check information, use the `musa-deploy -c {self._name}` command!"
            )
            exit()
        # 3. if path is specified
        if path:
            if not self.is_uninstalled():
                self.uninstall()
            self._pkg_path_dict[self._name] = path
            return self.install_cmd()

        is_driver_version_matched = True
        if success_flag and self._name == CheckModuleNames.container_toolkit.name:
            driver_check = CHECKER[CheckModuleNames.driver.name]()
            flag, status = driver_check.check()
            cur_driver_version = driver_check.get_version()
            print(FontGreen(f"The current driver version is {cur_driver_version}."))
            target_driver_version = self.version_lookup()

            if target_driver_version and cur_driver_version != DRIVER_VERSION_MAP.get(
                target_driver_version, None
            ):
                is_driver_version_matched = False

                if not allow_force_install:
                    sys.exit(
                        FontRed("WARNING: ")
                        + f"The current driver version is {cur_driver_version}, but the target version is {DRIVER_VERSION_MAP.get(target_driver_version)}. If you make sure you want to update to version {DRIVER_VERSION_MAP.get(target_driver_version)}, please add the '--force' option."
                    )
        if (
            success_flag
            and is_driver_version_matched
            and (
                self._gmi_version == self._checker.get_version()
                if self._name == "driver"
                else self._checker.get_version() == self._target_version
                or (
                    self._target_version is None and self._checker.get_version() is None
                )
            )
            and self._name not in [MusaModule.mccl.name, MusaModule.mudnn.name]
        ):  # TODO(@wangkang): when install mccl or mudnn, checker is from MusaChecker
            current_version = (
                (self._checker.get_version() + " ")
                if self._checker.get_version()
                else ""
            )
            print(
                FontGreen(
                    f"{self._name} {current_version}has already been installed successfully!"
                )
            )
            return
        elif (
            success_flag
            and is_driver_version_matched
            and self._target_version is None
            and self._name not in [MusaModule.mccl.name, MusaModule.mudnn.name]
        ):  # TODO(@wangkang): when install mccl or mudnn, checker is from MusaChecker
            # 5. path is None, target_version is None and has been installed
            current_version = (
                (self._checker.get_version() + " ")
                if self._checker.get_version()
                else ""
            )
            print(
                FontGreen(
                    f"{self._name} {current_version}has already been installed successfully!"
                )
            )
            # TODO(@caizhi): need print newest version
            # if newest version != self._checker.get_version():
            #    print(FontGreen()
            return
        else:
            self.precheck_environment()

            for preinstaller in self._preinstaller:
                target_pre_version = self.version_lookup()
                preinstaller._target_version = target_pre_version
                need_return = preinstaller.install(
                    target_pre_version,
                    allow_force_install=allow_force_install,
                    auto_install=self._auto_install,
                )
                if need_return:
                    return True
            if (not success_flag and not self.is_uninstalled()) or (
                success_flag and allow_force_install
            ):  # 已安装，但是检查不通过 or 检查通过要求强制重装
                self.uninstall()
            elif not self.is_uninstalled() and not allow_force_install:
                sys.exit(
                    FontRed("WARNING: ")
                    + f"The {self._name}{self._checker.get_version()} has been installed. If you make sure you want to update to version {self._target_version}, please add the '--force' option."
                )
            self.download()
            return self.install_cmd()

    def update(self, version: str = None, path: str = None):
        if not self.is_uninstalled():
            self.uninstall()
        self.install(version, path)


class HostPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.host.name
        self._checker = CHECKER[self._name]()
        self._package_type = "apt"
        self._dependency_package_list = ["dkms", "lightdm"]

    def download(self):
        pass

    def uninstall_cmd(self):
        """
        Used only when called by another class
        package_name: docker.io, dkms, lightdm, clinfo, ...
        """
        print(f"Uninstalling {FontRed('dkms')} ...")
        self._shell.run_cmd_with_error_print("dpkg -P dkms")
        print(f"Uninstalling {FontRed('lightdm')} ...")
        self._shell.run_cmd_with_error_print("dpkg -P lightdm")

    def install_cmd(self):
        require_root_privileges_check()
        """
        package_name: docker.io, dkms, lightdm, linux-modules-extra-`uname -r`
        """
        # 系统预装包，但部分机器缺少该包，需要手动安装，否则驱动无法加载
        print(
            f"Installing {FontGreen(f'linux-modules-extra-{platform.release()}')} ..."
        )
        self._shell.run_cmd_with_error_print(
            f"apt install -y linux-modules-extra-{platform.release()}"
        )

        print(f"Installing {FontGreen('dkms')} ...")
        self._shell.run_cmd_with_error_print("apt install -y dkms")

        print(f"Installing {FontGreen('lightdm')} ...")
        if self._auto_install:
            self._shell.run_cmd_with_error_print(
                "DEBIAN_FRONTEND=noninteractive apt-get install -y lightdm"
            )
            self._shell.run_cmd_with_error_print(
                "DEBIAN_FRONTEND=noninteractive dpkg-reconfigure -f noninteractive lightdm"
            )
        else:
            print(
                f"Please choose the display manager: {FontGreen('lightdm')}\nPlease choose the display manager: {FontGreen('lightdm')}\nPlease choose the display manager: {FontGreen('lightdm')}"
            )
            print(input("Press any key to continue..."))
            self._shell.run_cmd_with_error_print("apt install -y lightdm")

        return False


class DriverPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.driver.name
        self._checker = CHECKER[self._name]()
        self._target_package_name = "musa"
        self._package_type = "dpkg"
        self._preinstaller = [
            HostPkgMgr(),
        ]

    def precheck_environment(self):
        """
        检测节点环境，特定情况阻止驱动安装
        1. 节点在 mccp 平台中（ 验证：kebuctl get node | grep workerxxx ）
        2. 存在/etc/modprobe.d/drivertoolkit.conf文件（首次从集群踢出一般该文件都会存在）
        """
        _, host_check = CHECKER[CheckModuleNames.host.name](
            check_list=[HostModule.InCluster, HostModule.DriverToolkitFile]
        ).check()
        if host_check[HostModule.InCluster.name].status == Status.ATTENTION:
            sys.exit(
                FontRed("ERROR: ")
                + f"Installation is not permitted on a cluster node. Please contact the cluster administrator to install the required driver version({self._target_version})."
            )
        if host_check[HostModule.DriverToolkitFile.name].status == Status.WARNING:
            sys.exit(
                FontRed("ERROR: ")
                + f"The file {DRIVERTOOLKIT_PATH} was detected, which may cause issues during driver installation. Please delete it manually before retrying."
            )

    def uninstall_cmd(self):
        require_root_privileges_check()
        print(f"Uninstalling {FontRed(f'{self._name}')} ...")
        self._shell.run_cmd_with_error_print(f"dpkg -P {self._target_package_name}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {FontGreen(f'{self._name}')} ...")
        self._shell.run_cmd_with_error_print(
            f"dpkg -i {self._pkg_path_dict[self._name]}"
        )
        original_command = get_original_command()
        if self._auto_install:
            print(
                f"System will be restarted to load the driver, please continue to execute: {FontGreen(original_command)} after reboot!"
            )
            self._shell.run_cmd_with_standard_print("reboot")
        else:
            if "-i driver" in original_command:
                is_continue = continue_or_exit(
                    prompt_log="\nSystem needs to be restarted to load the driver. Restart now? "
                )
            else:
                is_continue = continue_or_exit(
                    prompt_log=f"\nSystem needs to be restarted to load the driver, then continue to execute: {FontGreen(original_command)} \nRestart now? "
                )
            if is_continue:
                self._shell.run_cmd_with_standard_print("reboot")

        return True


class SmartIOPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.smartio.name
        self._checker = CHECKER[self._name]()
        self._target_package_name = "mt-peermem"
        self._package_key = (
            "smartio"  # TODO(@wangkang): only to get package path from download
        )
        self._package_type = "dpkg"
        self._preinstaller = [DriverPkgMgr()]  # SmartIO depends on driver

    def precheck_environment(self):
        """
        Deny installation in special environments.
        The SmartIO package can only be installed in the following environments:
        1. The driver has been installed and loaded.
        """
        _, driver_check = CHECKER[CheckModuleNames.driver.name](
            check_list=[DriverModule.Driver]
        ).check()
        if driver_check[DriverModule.Driver.name].status != Status.SUCCESS:
            sys.exit(
                FontRed("ERROR: ")
                + "Installation is not permitted in the current environment. Please install the driver first."
            )

    def _load_kernel_module(self):
        """
        Load the SmartIO package.
        This method is used to load the SmartIO package after installation.
        """
        print(f"Loading {FontGreen(f'{self._target_package_name}')} ...")
        self._shell.run_cmd_with_error_print(
            f"modprobe {self._target_package_name.replace('-', '_')}"
        )
        code = self._shell.run_cmd_with_standard_print(
            f"lsmod | grep {self._target_package_name.replace('-', '_')}"
        )
        if code != 0:
            sys.exit(
                FontRed("ERROR: ")
                + f"Failed to load {FontGreen(f'{self._target_package_name}')}."
            )
        else:
            print(
                f"{FontGreen(f'{self._target_package_name}')}: Kernel module loaded and active."
            )

    def uninstall_cmd(self):
        require_root_privileges_check()
        print(f"Unloading {FontRed(f'{self._target_package_name}')} ...")
        self._shell.run_cmd_with_standard_print(
            f"rmmod {self._target_package_name.replace('-', '_')}"
        )
        print(f"Uninstalling {FontRed(f'{self._target_package_name}')} ...")
        self._shell.run_cmd_with_error_print(f"dpkg -P {self._target_package_name}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {FontGreen(f'{self._target_package_name}')} ...")
        self._shell.run_cmd_with_error_print(
            f"dpkg -i {self._pkg_path_dict[self._package_key]}"
        )
        self._load_kernel_module()


class ContainerToolkitsPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.container_toolkit.name
        self._checker = CHECKER[self._name]()
        self._package_type = "dpkg"
        self._target_package_name = "container-toolkit"
        self._dependency_package_list = ["mtml", "sgpu-dkms"]
        self._preinstaller = [
            DriverPkgMgr(),
        ]

    def uninstall_cmd(self):
        require_root_privileges_check()
        # 1.uninstall mt-container-toolkit
        _, _, code = self._shell.run_cmd("dpkg -l mt-container-toolkit >/dev/null 2>&1")
        if code == 0:
            print(f"Uninstalling {FontRed('mt-container-toolkit')} ...")
            self._shell.run_cmd_with_error_print("dpkg -P mt-container-toolkit")
        else:
            print(f"{FontRed('mt-container-toolkit')} is not found.")
        # 2.uninstall mtml
        _, _, code = self._shell.run_cmd("dpkg -l mtml >/dev/null 2>&1")
        if code == 0:
            print(f"Uninstalling dependencies {FontRed('mtml')} ...")
            self._shell.run_cmd_with_error_print("dpkg -P mtml")
        else:
            print(f"{FontRed('mtml')} is not found.")
        # 3.uninstall sgpu-dkms
        _, _, code = self._shell.run_cmd("dpkg -l sgpu-dkms >/dev/null 2>&1")
        if code == 0:
            print(f"Uninstalling dependencies {FontRed('sgpu-dkms')} ...")
            self._shell.run_cmd_with_error_print("dpkg -P sgpu-dkms")
        else:
            print(f"{FontRed('sgpu-dkms')} is not found.")

    def install_cmd(self):
        require_root_privileges_check()
        # 0.install docker
        _, _, code = self._shell.run_cmd("dpkg -l docker.io >/dev/null 2>&1")
        if code == 0:
            print(f"{FontGreen('docker.io has already been installed successfully!')}")
        else:
            print(f"Installing {FontGreen('docker')} ...")
            self._shell.run_cmd_with_error_print("apt install docker.io -y")
        # 1.install mtml
        print(f"Installing {FontGreen('mtml')} ...")
        self._shell.run_cmd_with_error_print(
            f"dpkg -i \"{self._pkg_path_dict['mtml']}\""
        )
        # 2.install sgpu-dkms
        if self._pkg_path_dict.get("sgpu-dkms"):
            print(f"Installing {FontGreen('sgpu-dkms')} ...")
            self._shell.run_cmd_with_error_print(
                f"dpkg -i \"{self._pkg_path_dict['sgpu-dkms']}\""
            )
        # 3.install mt-container-toolkit
        print(f"Installing {FontGreen('mt-container-toolkit')} ...")
        if self._auto_install:
            self._shell.run_cmd_with_error_print(
                f'DEBIAN_FRONTEND=noninteractive dpkg --force-confdef --force-confold -i "{self._pkg_path_dict.get(self._target_package_name)}"'
            )
        else:
            self._shell.run_cmd_with_error_print(
                f'dpkg -i "{self._pkg_path_dict.get(self._target_package_name)}"'
            )
        # 4.binding
        print(f"Binding {FontGreen('mthreads runtime')} to docker ...")
        self._shell.run_cmd_with_error_print(
            "(cd /usr/bin/musa && ./docker setup $PWD)"
        )
        return False


class MusaPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.musa.name
        self._checker = CHECKER[self._name]()
        self._target_package_name = "musa_toolkits"
        self._package_type = "sh"
        self._is_installed_file_flag = "/usr/local/musa/lib/libmusa.so"
        if EXECUTED_ON_HOST_FLAG:
            self._preinstaller = [
                DriverPkgMgr(),
            ]

    def _add_env_to_bashrc(self) -> None:
        """
        Adds an environment variable to the user's .bashrc file and reloads it.
        """
        self._shell.run_cmd(
            f"echo 'export PATH={MUSA_BIN_PATH}:${{PATH}}' >> ~/.bashrc"
        )
        self._shell.run_cmd(
            f"echo 'export LD_LIBRARY_PATH={MUSA_LIB_PATH}:${{LD_LIBRARY_PATH}}' >> ~/.bashrc"
        )

        self._shell.run_cmd("source ~/.bashrc")

    def uninstall_cmd(self):
        print(f"Uninstalling {FontRed(f'{self._target_package_name}')} ...")
        uninstall_script_path = os.path.join(
            CURRENT_FOLDER, "uninstall_" + self._target_package_name + ".sh"
        )
        self._shell.run_cmd_with_error_print(f"bash {uninstall_script_path}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {FontGreen(f'{self._target_package_name}')} ...")
        self._shell.run_cmd_with_error_print(
            f"bash {self._pkg_path_dict[self._target_package_name]} -i"
        )

        self._add_env_to_bashrc()
        return False


class muDNNPkgMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._name = MusaModule.mudnn.name
        self._checker = CHECKER[CheckModuleNames.musa.name]()
        self._target_package_name = "mudnn"
        self._package_type = "sh"
        self._is_installed_file_flag = "/usr/local/musa/lib/libmudnn.so"
        self._preinstaller = [
            MusaPkgMgr(),
        ]

    def uninstall_cmd(self):
        print(f"Uninstalling {FontRed(f'{self._target_package_name}')} ...")
        uninstall_script_path = os.path.join(
            CURRENT_FOLDER, "uninstall_" + self._target_package_name + ".sh"
        )
        self._shell.run_cmd_with_error_print(f"bash {uninstall_script_path}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {FontGreen(f'{self._target_package_name}')} ...")
        bash_dir = os.path.dirname(self._pkg_path_dict[self._target_package_name])
        os.chdir(bash_dir)
        self._shell.run_cmd_with_error_print(
            f"bash {self._pkg_path_dict[self._target_package_name]} -i"
        )
        os.chdir(CURRENT_WORK_DIR)
        return False


class McclPkgMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._name = MusaModule.mccl.name
        self._target_package_name = "mccl"
        self._checker = CHECKER[CheckModuleNames.musa.name]()
        self._package_type = "sh"
        self._is_installed_file_flag = "/usr/local/musa/lib/libmccl.so"
        self._preinstaller = [
            MusaPkgMgr(),
        ]

    def uninstall_cmd(self):
        print(f"Uninstalling {FontRed(f'{self._target_package_name}')} ...")
        uninstall_script_path = os.path.join(
            CURRENT_FOLDER, "uninstall_" + self._target_package_name + ".sh"
        )
        self._shell.run_cmd_with_error_print(f"bash {uninstall_script_path}")

    def install_cmd(self):
        require_root_privileges_check()
        print(f"Installing {FontGreen(f'{self._target_package_name}')} ...")
        bash_dir = os.path.dirname(self._pkg_path_dict[self._target_package_name])
        os.chdir(bash_dir)
        self._shell.run_cmd_with_error_print(
            f"bash {self._pkg_path_dict[self._target_package_name]} -i"
        )
        os.chdir(CURRENT_WORK_DIR)
        return False


class TorchMusaPkgMgr(PackageManager):

    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.torch_musa.name
        self._checker = CHECKER[self._name]()
        self._target_package_name = "torch_musa"
        self._package_type = "pip"
        self._pip_path = get_pip_path()
        self._dependency_package_list = ["torch", "torchvision", "torchaudio"]
        self._preinstaller = [
            MusaPkgMgr(),
            muDNNPkgMgr(),
            McclPkgMgr(),
        ]

    def uninstall_cmd(self):
        print(f"Uninstalling {FontRed(f'{self._target_package_name}')} ...")
        self._shell.run_cmd_with_error_print(
            f"{self._pip_path} uninstall {self._target_package_name} -y"
        )

        print(f"Uninstalling {FontRed('torch')} ...")
        self._shell.run_cmd_with_error_print(f"{self._pip_path} uninstall torch -y")

        print(f"Uninstalling {FontRed('PyTorch')} extensions ...")
        self._shell.run_cmd_with_error_print(
            f"{self._pip_path} uninstall {TorchMusaModule.TorchAudio.name.lower()} -y"
        )
        self._shell.run_cmd_with_error_print(
            f"{self._pip_path} uninstall {TorchMusaModule.TorchVision.name.lower()} -y"
        )

    def install_cmd(self):
        print(f"Installing {FontGreen(f'{self._target_package_name}')} ...")
        self._shell.run_cmd_with_error_print(
            f"{self._pip_path} install {self._pkg_path_dict[self._target_package_name]}"
        )

        print(f"Installing {FontGreen('torch')} ...")
        self._shell.run_cmd_with_error_print(
            f"{self._pip_path} install {self._pkg_path_dict['torch']}"
        )

        print(f"Installing {FontGreen('PyTorch')} extensions ...")
        self._shell.run_cmd_with_error_print(
            f"{self._pip_path} install {self._pkg_path_dict[TorchMusaModule.TorchAudio.name.lower()]}"
        )
        self._shell.run_cmd_with_error_print(
            f"{self._pip_path} install {self._pkg_path_dict[TorchMusaModule.TorchVision.name.lower()]}"
        )
        return False


class vLLMPkgMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._name = CheckModuleNames.vllm.name
        self._checker = CHECKER[self._name]()
        self._package_type = "pip"
        self._target_package_name = "vllm"
        self._dependency_package_list = ["mttransformer"]
        self._preinstaller = [
            TorchMusaPkgMgr(),
        ]

    def uninstall_cmd(self):
        print(
            f"Uninstalling {FontRed(f'{self._target_package_name}')} dependencies ..."
        )
        for package in self._dependency_package_list:
            self._shell.run_cmd_with_error_print(f"pip uninstall {package}")

    def install_cmd(self):
        # 1.install dependencies
        print(
            f"Installing {FontGreen(f'{self._target_package_name}')} dependencies ..."
        )
        # 1.1 install mttransformer
        self._shell.run_cmd_with_error_print(
            f"pip install {self._pkg_path_dict['mttransformer']}"
        )
        # TODO(@wangkang): requirements need test
        # 1.2 install other dependencies with requirements.txt
        vllm_requirements = os.path.join(CURRENT_FOLDER, "vllm_requirements.txt")
        self._shell.run_cmd_with_error_print(f"pip install -r {vllm_requirements}")

        # 2.install vllm
        print(f"Installing {FontGreen(f'{self._target_package_name}')} ...")
        # TODO(@wangkang): add vllm install cmd
        return False


class SDKPkgMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._musa_toolkit = MusaPkgMgr()
        self._mudnn = muDNNPkgMgr()
        self._mccl = McclPkgMgr()
        self._driver = DriverPkgMgr()
        self._smartio = SmartIOPkgMgr()

    def uninstall(self):
        self._musa_toolkit.uninstall()
        self._driver.uninstall()
        self._smartio.uninstall()

    # TODO(@wangkang): 暂时不考虑version匹配问题
    def install_cmd(self):
        pass
        return False


class KylinMgr(PackageManager):
    def __init__(self):
        super().__init__()
        self._name = None
        self._target_version = None

    def _update_package_path(self):
        if self._name == "driver":
            archive_dict = DOWNLOADER().download(self._name, self._target_version)
            self._pkg_path_dict.update(DownloadDecompressor(archive_dict).decompress())
        elif self._name == "container_toolkit" and self._target_version == "2.0.0":
            container_dict = {"container_toolkit": "2.0.0", "mtml": "1.14.2"}
            for key, version in container_dict.items():
                archive_dict = DOWNLOADER().download(key, version)
                self._pkg_path_dict.update(archive_dict)
        else:
            archive_dict = DOWNLOADER().download(self._name, self._target_version)
            self._pkg_path_dict.update(DownloadDecompressor(archive_dict).decompress())

    def uninstall(self, name: str):
        self._name = name
        self.uninstall_cmd()

    def uninstall_cmd(self):
        require_root_privileges_check()
        # 卸载driver
        if self._name == "driver":
            print(f"Uninstalling {FontRed('musa')} ...")
            self._shell.run_cmd_with_error_print("rpm -e musa")
        # 卸载container
        if self._name == "container_toolkit":
            print(f"Uninstalling {FontRed('container-toolkit')} ...")
            self._shell.run_cmd_with_error_print("rpm -e container-toolkit")
            print(f"Uninstalling {FontRed('mtml')} ...")
            self._shell.run_cmd_with_error_print("rpm -e mtml")
            print(f"Uninstalling {FontRed('sgpu-dkms')} ...")
            self._shell.run_cmd_with_error_print("rpm -e sgpu-dkms")

    def install(self, name: str, version: str):
        self._name = name
        self._target_version = version
        self.install_cmd()

    def install_cmd(self):
        require_root_privileges_check()
        self._update_package_path()
        # 安装driver
        if self._name == "driver":
            _, _, code = self._shell.run_cmd("rpm -qa musa >/dev/null 2>&1")
            if code == 0:
                print(
                    f"{FontGreen('driver')} is already installed, you can skip this step."
                )
            else:
                print(f"Installing {FontGreen('musa')} ...")
                self._shell.run_cmd_with_error_print(
                    f"rpm -i {self._pkg_path_dict['driver']}"
                )
        # 安装container
        if self._name == "container_toolkit":
            # print(f"Installing {FontGreen('docker')} ...")
            # self._shell.run_cmd_with_error_print("yum install docker.io -y")
            _, _, code = self._shell.run_cmd("rpm -qa mtml >/dev/null 2>&1")
            if code == 1:
                print(
                    f"{FontGreen('mtml')} is already installed, you can skip this step."
                )
            else:
                print(f"Installing {FontGreen('mtml')} ...")
                self._shell.run_cmd_with_error_print(
                    f"rpm -i {self._pkg_path_dict['mtml']}"
                )
            if "sgpu-dkms" in self._pkg_path_dict.keys():
                print(f"Installing {FontGreen('sgpu-dkms')} ...")
                self._shell.run_cmd_with_error_print(
                    f"rpm -i {self._pkg_path_dict['sgpu-dkms']}"
                )
            _, _, code = self._shell.run_cmd(
                "rpm -qa mt-container-toolkit >/dev/null 2>&1"
            )
            if code == 0:
                print(
                    f"{FontGreen('mt-container-toolkit')} is already installed, you can skip this step."
                )
            else:
                print(f"Installing {FontGreen('container_toolkit')} ...")
                self._shell.run_cmd_with_error_print(
                    f"rpm -i {self._pkg_path_dict[self._name]}"
                )
            print(f"Binding {FontGreen('mthreads runtime')} to docker ...")
            self._shell.run_cmd_with_error_print(
                "(cd /usr/bin/musa && ./docker setup $PWD)"
            )
