from ruamel.yaml import YAML
import json
import os


def generate_yaml(template_path, service_updates, output_path):
    """
    根据模板文件、生成新的文件。

    参数:
        template_path (str): 模板文件路径。
        service_updates: 新增字符串。
        output_path (str): 输出文件路径。
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.default_flow_style = False
    yaml.Representer.ignore_aliases = lambda self, data: True

    with open(template_path, "r") as f:
        compose_data = yaml.load(f)

    for service_name, updates in service_updates.items():
        service = compose_data["services"][service_name]
        for key, items in updates.items():
            if key not in service:
                service[key] = []
            if key == "environment":
                for env_name, env_value in items.items():
                    service[key].append(f"{env_name}={env_value}")
            else:
                service[key].extend(items)

    with open(output_path, "w") as f:
        yaml.dump(compose_data, f)


def generate_docker_service(
    template_path, volume_mounts, ports, pid, env_vars, output_path
):
    base_volumes = [
        {
            "type": "tmpfs",
            "target": "/dev/shm",
            "tmpfs": {"size": 85899345920, "mode": 1777},
        },
        {"type": "bind", "source": "/tmp", "target": "/tmp"},
    ]
    custom_volumes = []
    for vol in volume_mounts:
        src, tgt = vol.split(":", 1)
        custom_volumes.append(
            {"type": "bind", "source": src.strip(), "target": tgt.strip()}
        )

    port_list = []
    for port in ports:
        host_port, container_port = port.split(":", 1)
        port_list.append(f"{host_port.strip()}:{container_port.strip()}")

    new_env_vars = {}
    for var in env_vars:
        if "=" not in var:
            continue
        key, value = var.split("=", 1)
        new_env_vars[key.strip()] = value.strip()
    if not new_env_vars:
        new_env_vars["MTHREADS_VISIBLE_DEVICES"] = "all"

    service_updates = {
        "task1": {
            "volumes": base_volumes + custom_volumes,
            "environment": new_env_vars,
        },
        "task2": {
            "volumes": base_volumes + custom_volumes,
            "environment": new_env_vars,
        },
    }
    if port_list:
        service_updates["task2"]["ports"] = port_list
    if pid:
        pass
        # service_updates["task1"]["pid"] = pid
        # service_updates["task2"]["pid"] = pid
    generate_yaml(template_path, service_updates, output_path)


def generate_kuae_chat_json(
    model_name: str,
    ip: str,
    port: int,
    output_path: str = "./kuae-chat-public/models.json",
) -> None:
    """
    生成模型配置的 JSON 文件

    Args:
        model_name: 模型名称（如 "QwQ-32B"）
        ip: 服务 IP 地址（如 "10.1.0.133"）
        port: 服务端口（如 3020）
        output_path: 输出文件路径（默认 ./kuae-chat-public/models.json）
    """
    # 构建数据结构
    host_ip = ip.split(",")[0]
    config_data = [
        {
            "model_name": model_name,
            "url": f"http://{host_ip}:{port}/v1/chat/completions",
        }
    ]

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 写入 JSON 文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    print(f"配置文件已生成至 {output_path}")
