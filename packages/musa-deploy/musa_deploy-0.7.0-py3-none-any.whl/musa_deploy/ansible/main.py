import os
import sys
import tempfile
from datetime import datetime
import argparse
from pathlib import Path

from musa_deploy.check.shell_executor import BaseShellExecutor
from musa_deploy.utils import (
    InventoryGenerator,
    parse_hostfile_ip_to_string,
    configure_ssh_access,
)
from musa_deploy.auto_gen import generate_docker_service, generate_kuae_chat_json


CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
PLAYBOOK_TEMPLATE = os.path.join(CURRENT_FOLDER, "playbook", "playbook_template.yaml")
RESET_PLAYBOOK_TEMPLATE = os.path.join(
    CURRENT_FOLDER, "playbook", "reset_docker_swarm_playbook.yaml"
)
INIT_CLUSTER_PLAYBOOK_TEMPLATE = os.path.join(
    CURRENT_FOLDER, "playbook", "init_docker_swarm_playbook.yaml"
)
DOCKER_STACK_TEMPLATE = os.path.join(CURRENT_FOLDER, "service", "stack_template.yaml")
START_SERVICE_PLAYBOOK = os.path.join(
    CURRENT_FOLDER, "playbook", "start_service_playbook.yaml"
)
SHELL_SCRIPT_FOLDER = os.path.join(CURRENT_FOLDER, "shell")
ROLES_FOLDER = os.path.join(CURRENT_FOLDER, "playbook", "roles")


class AnsibleExecutor(BaseShellExecutor):
    def __init__(self):
        super().__init__()

    def __call__(
        self,
        inventory_file,
        playbook,
        task_name="",
        model_path="",
        tp_size=8,
        pp_size=4,
        pp_layer_partition="",
        max_model_len="",
        host_ip="",
        disable_kuae_chat=False,
        musa_deploy_args="",
        force_install_driver=False,
        **kwargs,
    ):
        print(f"ansible-playbook -i {inventory_file} {playbook}")
        host_num = len(host_ip.split(","))
        worker_num = 0 if host_num < 2 else (host_num - 1)
        worker_num_vars = f"worker_num={worker_num}"
        host_ip_vars = f"host_ip={host_ip}"
        task_name_vars = f"task_name={task_name}"
        model_path_vars = f"model_path={model_path}" if model_path else ""
        tp_size_vars = f"tp_size={tp_size}"
        pp_size_vars = f"pp_size={pp_size}"
        pp_partition_vars = f"pp_layer_partition={pp_layer_partition}"
        max_model_len_vars = f"max_model_len={max_model_len}" if max_model_len else ""
        musa_deploy_vars = (
            f"musa_deploy_arguments='{musa_deploy_args}'" if musa_deploy_args else ""
        )
        kuae_chat_vars = (
            "disable_kuae_chat=--disable-kuae-chat" if disable_kuae_chat else ""
        )
        force_install_driver = f"force_install_driver={force_install_driver}"

        os.system(
            f'ansible-playbook -i {inventory_file} {playbook} -v --extra-vars "{max_model_len_vars} {tp_size_vars} {pp_size_vars} {pp_partition_vars} {host_ip_vars} {worker_num_vars} {task_name_vars} {model_path_vars} {kuae_chat_vars} {musa_deploy_vars} {force_install_driver}"'
        )


def generate_playbook(template_path: str, command: str):
    try:
        with open(template_path, "r") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"错误：模板文件 {template_path} 不存在")
        return

    # 执行参数替换
    modified_content = template.replace("{musa_deploy_command}", command)

    # 生成输出文件名
    temp_dir = tempfile.gettempdir()  # 返回系统标准临时目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"generated_playbook_{timestamp}.yml"
    output_path = os.path.join(temp_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(modified_content)
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(
        prog="musa-deploy-ansible",
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description="",
    )
    parser.add_argument(
        "--hostfile",
        type=Path,
        help="输入文件路径，格式：IP 用户名 密码\n"
        "示例：\n"
        "192.168.5.150 ggn 000000\n"
        "192.168.5.149 ggn 000000",
    )
    parser.add_argument(
        "--init-cluster",
        dest="init_cluster",
        action="store_true",
        default=False,
        help="init cluster according to hostfile",
    )
    parser.add_argument(
        "--reset-cluster",
        dest="reset_cluster",
        action="store_true",
        default=False,
        help="clear cluster configuration",
    )
    parser.add_argument(
        "--generate-stack-yaml",
        dest="generate_stack_yaml",
        action="store_true",
        default=False,
        help="cp stack yaml to /tmp",
    )
    parser.add_argument(
        "--ssh-copy-id",
        dest="ssh_copy_id",
        action="store_true",
        default=False,
        help="ssh-copy-id",
    )
    parser.add_argument(
        "--generate-shell-script",
        dest="generate_shell_script",
        action="store_true",
        default=False,
        help="cp shell script to /tmp",
    )
    parser.add_argument(
        "--task",
        dest="task",
        type=str,
        help="specify model name",
    )
    parser.add_argument(
        "--host-leader-ip",
        dest="host_leader_ip",
        type=str,
        help="specify leader host ip",
    )
    parser.add_argument(
        "--model-path",
        dest="model_path",
        default="",
        help="(optional) the model path for vllm-musa",
    )
    parser.add_argument(
        "-v",
        "--volume",
        dest="volume_list",
        metavar="<HOST_DIR>:<CTNR_DIR>",
        action="append",
        default=[],
        help="(optional) map a host directory to a container directory.",
    )
    parser.add_argument(
        "-e",
        "--env",
        dest="env_list",
        metavar="env_name=env_value",
        action="append",
        default=[],
        help="(optional) set up env variables inside container.",
    )
    parser.add_argument(
        "-p",
        "--publish",
        dest="port_list",
        action="append",
        default=[],
        help="(optional) specify a port mapping. Format: host_port:container_port",
    )
    parser.add_argument(
        "--pid",
        dest="pid",
        default="private",
        help="(optional) set the PID mode for the container. Default is private.",
    )
    parser.add_argument(
        "--max-model-len",
        dest="max_model_len",
        default="",
        help="(optional)",
    )
    parser.add_argument(
        "--tensor-parallel-size",
        "--tp-size",
        dest="tp_size",
        default="",
        help="(optional) number of partitions for tensor parallelism to distribute model computation across multiple devices(just for vllm demo).",
    )
    parser.add_argument(
        "--pipeline-parallel-size",
        "--pp-size",
        dest="pp_size",
        default="",
        help="(optional) number of partitions for pipeline parallelism to distribute model computation across multiple devices(just for vllm demo).",
    )
    parser.add_argument(
        "--pp-layer-partition",
        "--pp-partition",
        dest="pp_layer_partition",
        default="",
        help="(optional)",
    )
    parser.add_argument(
        "--demo",
        dest="demo",
        type=str,
        help="""please refer to musa-deploy -h""",
    )
    parser.add_argument(
        "--cluster-demo",
        dest="cluster_demo",
        type=str,
        help="""start a demo in cluster""",
    )
    parser.add_argument(
        "--disable-kuae-chat",
        dest="disable_kuae_chat",
        action="store_false",
        default=False,
        help="""please refer to musa-deploy -h""",
    )
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="""please refer to musa-deploy -h""",
    )
    return parser.parse_known_args()


def main():
    args, unknown_args = parse_args()
    if args.hostfile:
        if not args.hostfile.exists():
            print(f"输入文件不存在: {args.hostfile}")
        try:
            generator = InventoryGenerator()
            inventory_path = generator.generate_temp_inventory(args.hostfile)
        except Exception as e:
            print(f"[错误] {str(e)}")
            return 1
    if args.ssh_copy_id:
        if not args.hostfile or not args.hostfile.exists():
            print(
                "Error: the hostfile must be specified, and the hostfile file must exist, but now it is not!"
            )
            return 1
        configure_ssh_access(args.hostfile)
        return 0

    ansible = AnsibleExecutor()
    if args.reset_cluster:
        if not args.hostfile or not args.hostfile.exists():
            print(
                "Error: the hostfile must be specified, and the hostfile file must exist, but now it is not!"
            )
            return 1
        ansible(inventory_path, RESET_PLAYBOOK_TEMPLATE)
        return 0

    if args.generate_shell_script:
        os.system(f"cp -r {SHELL_SCRIPT_FOLDER}/* /tmp")
        return 0

    if args.demo:
        # setup base musa environment in cluster
        # 0. get full command
        musa_deploy_args = " ".join(sys.argv[1:])  # eg: --demo vllm_musa
        full_command = "musa-deploy " + musa_deploy_args + " --auto-install"
        if args.force:
            full_command += " --force"
        # 1. generate playbook
        playbook_file = generate_playbook(PLAYBOOK_TEMPLATE, full_command)
        # 临时目录，TODO（@wangkang）：待整体优化
        os.system(f"cp -r {ROLES_FOLDER}/ /tmp")
        # 2. ansible-playbook
        ansible(
            inventory_path,
            playbook_file,
            disable_kuae_chat=True,
            force_install_driver=args.force,
        )
        return 0

    if args.init_cluster:
        if not args.hostfile or not args.hostfile.exists():
            print(
                "Error: the hostfile must be specified, and the hostfile file must exist, but now it is not!"
            )
            return 1
        # init docker swarm cluster
        ansible(inventory_path, INIT_CLUSTER_PLAYBOOK_TEMPLATE)
        return 0

    if args.generate_stack_yaml:
        # get mapping folder
        for volume_dirs in args.volume_list:
            if ":" not in volume_dirs:
                print(
                    f"Error: Invalid mount directory format: '{args.volume_list}'. Missing ':' separator. Expected format: HOST_DIR:CONTAINER_DIR"
                )
                return 1
            elif len(volume_dirs.split(":")) != 2:
                print(
                    f"Error: Invalid mount directory format: '{args.volume_list}'. Requiring two directory. Expected format: HOST_DIR:CONTAINER_DIR"
                )
                return 1
        generate_docker_service(
            DOCKER_STACK_TEMPLATE,
            args.volume_list,
            args.port_list,
            args.pid,
            args.env_list,
            "/tmp/stack_template.yaml",
        )
        return 0

    if not args.disable_kuae_chat and args.host_leader_ip:
        kuae_chat_port = "8000"
        generate_kuae_chat_json(
            args.task,
            args.host_leader_ip,
            kuae_chat_port,
            "/tmp/kuae-chat-public/models.json",
        )
        return 0

    if args.cluster_demo and args.task:
        if not args.hostfile or not args.hostfile.exists():
            print(
                "Error: the hostfile must be specified, and the hostfile file must exist, but now it is not!"
            )
            return 1
        filtered = []
        i = 0
        command_args = sys.argv[1:]
        while i < len(command_args):
            if command_args[i] == "--hostfile":
                i += 2  # 跳过 --hostfile 和其后的参数
            else:
                filtered.append(command_args[i])
                i += 1
        musa_deploy_args = " ".join(filtered)

        if not args.model_path:
            print(
                "Error: argument '--model-path' must be specified, but now it is not!"
            )
            return 1

        ansible(
            inventory_path,
            START_SERVICE_PLAYBOOK,
            args.task,
            args.model_path,
            args.tp_size,
            args.pp_size,
            args.pp_layer_partition,
            args.max_model_len,
            parse_hostfile_ip_to_string(args.hostfile),
            args.disable_kuae_chat,
            musa_deploy_args,
        )

        return 0


if __name__ == "__main__":
    main()
