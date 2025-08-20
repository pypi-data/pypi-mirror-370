import re,os,requests
from vkube_cli.utils.file_io import read_file_to_string
from vkube_cli.constants import INJECTED_DOCKER_FILE,DOWNLOAD_SHELL_PATH, ENTRYPOINT_SCRIPT

def check_ssh_injection_compatibility(dockerfile_content: str) -> tuple[bool, str]:
    """
    检测 Dockerfile 是否支持 SSH 注入
    
    参数:
    dockerfile_content (str): Dockerfile 内容

    返回:
    tuple[bool, str]: (是否支持, 原因说明)
    """
    # 检查是否使用了 distroless 或 scratch 镜像
    incompatible_patterns = [
        (r'gcr\.io/distroless/', "Google distroless images don't contain shell or package managers"),
        (r'distroless', "Distroless images are minimal and don't support SSH"),
        (r'FROM\s+scratch', "Scratch images are empty and don't contain any tools"),
    ]

    for pattern, reason in incompatible_patterns:
        if re.search(pattern, dockerfile_content, re.IGNORECASE):
            return False, reason
    
    # 检查是否已经有 ENTRYPOINT 指令
    entrypoint_pattern = r'^\s*ENTRYPOINT\s+'
    if re.search(entrypoint_pattern, dockerfile_content, re.MULTILINE):
        return False, "Dockerfile already contains ENTRYPOINT instruction"

    # 检查是否是支持的基础镜像
    supported_patterns = [
        r'ubuntu',
        r'debian',
        r'alpine',  # Alpine Linux 完全支持 SSH
        r'centos',
        r'fedora',
        r'amazonlinux',
        r'node',     # Node.js (包括 alpine 变种)
        r'python',   # Python (包括 alpine 变种)
        r'openjdk',
        r'golang',   # Go (包括 alpine 变种)
        r'ruby',
        r'php',
        r'nginx',
        r'httpd',
        r'tomcat',
    ]

    base_images = re.findall(r'FROM\s+([^\s]+)', dockerfile_content, re.IGNORECASE)
    if not base_images:
        return False, "No FROM instruction found"

    # 检查最后一个基础镜像
    final_base_image = base_images[-1].lower()

    # 如果明确匹配支持的镜像
    for pattern in supported_patterns:
        if re.search(pattern, final_base_image, re.IGNORECASE):
            return True, f"Compatible base image detected: {final_base_image}"

    # 如果不在已知的不兼容列表中，假设兼容但给出警告
    return True, f"Unknown base image '{final_base_image}', assuming compatible"

def inject_ssh_support(dockerfile_content: str, injected_content: str) -> str:
    """
    将SSH配置脚本注入到Dockerfile的最后一个stage

    参数:
    dockerfile_content (str): 原始Dockerfile内容
    injected_content (str): SSH配置脚本内容

    返回:
    str: 修改后的Dockerfile内容
    """
    # 检查是否支持 SSH 注入
    is_compatible, reason = check_ssh_injection_compatibility(dockerfile_content)
    if not is_compatible:
        print(f"Warning: SSH injection is not compatible with this Dockerfile.")
        print(f"Reason: {reason}")
        print("Skipping SSH injection for this Dockerfile.")
        raise RuntimeError(f"SSH injection is not compatible: {reason}")
    else:
        print(f"SSH injection compatibility check passed: {reason}")

    # 查找所有FROM指令及其位置
    from_pattern = re.compile(r'^FROM\s+([^\s]+)(?:\s+AS\s+([^\s]+))?', re.MULTILINE)
    from_matches = list(from_pattern.finditer(dockerfile_content))

    if not from_matches:
        # 如果没有FROM指令，直接返回原始内容
        return dockerfile_content

    # 获取最后一个FROM指令的位置
    last_from_match = from_matches[-1]
    last_from_end = last_from_match.end()

    # 将Dockerfile内容按行分割
    lines = dockerfile_content.splitlines()
    injected_content = injected_content + "\n" + ENTRYPOINT_SCRIPT
    injected_lines = injected_content.splitlines()

    # 找到最后一个FROM指令所在的行号
    last_from_line = -1
    for i, line in enumerate(lines):
        if re.match(r'^\s*FROM\s+', line, re.IGNORECASE):
            last_from_line = i

    if last_from_line == -1:
        # 如果没有找到FROM指令，添加到文件开头
        insert_line = 0
    else:
        # 在最后一个FROM指令之后插入
        insert_line = last_from_line + 1

    # 找到最后一个stage的范围
    stage_start = last_from_line
    stage_end = len(lines)
    
    # 检查最后一个stage是否已经有ENTRYPOINT或EXPOSE 22
    has_entrypoint = False
    has_expose_22 = False
    cmd_index = None
    original_cmd = None

    for i in range(stage_start, stage_end):
        line = lines[i].strip()
        if re.match(r'^\s*ENTRYPOINT\s+', line, re.IGNORECASE):
            has_entrypoint = True
        elif re.match(r'^\s*EXPOSE\s+22\b', line, re.IGNORECASE):
            has_expose_22 = True
        elif line.startswith('CMD'):
            cmd_index = i
            original_cmd = line

    # 如果已经有ENTRYPOINT，抛出错误
    if has_entrypoint:
        raise RuntimeError("The original Dockerfile already has an ENTRYPOINT in the final stage. Please remove it before injecting SSH support.")

    # 插入SSH安装脚本到最后一个stage的FROM后
    for idx, injected_line in enumerate(injected_lines):
        lines.insert(insert_line + idx, injected_line.strip())
    
    # 更新索引（因为插入了新行）
    lines_added = len(injected_lines)
    if cmd_index is not None:
        cmd_index += lines_added

    # 插入EXPOSE 22（如果还没有的话）
    if not has_expose_22:
        if cmd_index is not None:
            lines.insert(cmd_index, "EXPOSE 22")
            cmd_index += 1
        else:
            lines.append("EXPOSE 22")

    # 处理原有的CMD或添加新的ENTRYPOINT
    if cmd_index is not None and original_cmd:
        # 有原始CMD，替换为ENTRYPOINT+CMD组合
        cmd_args = original_cmd[3:].strip()
        lines[cmd_index] = 'ENTRYPOINT ["/entrypoint.sh"]'
        lines.insert(cmd_index + 1, f'CMD {cmd_args}')
    else:
        # 没有原始CMD，只添加ENTRYPOINT
        lines.append('ENTRYPOINT ["/entrypoint.sh"]')

    return "\n".join(lines)

def generate_dockerfile(original_dockerfile_path: str, final_dockerfile_path: str, ssh_key_path: str):
    """
    生成带有 SSH 支持的 Dockerfile

    参数:
    original_dockerfile_path (str): 原始 Dockerfile 路径
    final_dockerfile_path (str): 输出 Dockerfile 路径
    ssh_key_path (str): SSH 公钥路径
    """
    original_dockerfile_content = read_file_to_string(original_dockerfile_path)

    # 先检查兼容性
    is_compatible, reason = check_ssh_injection_compatibility(original_dockerfile_content)

    if not is_compatible:
        print(f"SSH injection compatibility check failed: {reason}")
        raise RuntimeError(f"SSH injection is not compatible: {reason}")

    # 如果兼容，进行 SSH 注入
    # 读取并清理 SSH 公钥内容
    ssh_pub_content = read_file_to_string(ssh_key_path).strip()

    # 确保 SSH 公钥格式正确（移除多余的换行符和空格）
    ssh_pub_content = ' '.join(ssh_pub_content.split())

    new_injected_content = INJECTED_DOCKER_FILE.format(
        ssh_pub_content=ssh_pub_content,
        download_shell_url=DOWNLOAD_SHELL_PATH
    )
    modified_dockerfile_content = inject_ssh_support(original_dockerfile_content, new_injected_content)

    with open(final_dockerfile_path, 'w') as f:
        f.write(modified_dockerfile_content)
    print(f"Successfully generated Dockerfile with SSH support: {final_dockerfile_path}")

def analyze_dockerfile_for_ssh_support(dockerfile_path: str) -> dict:
    """
    分析 Dockerfile 对 SSH 注入的支持情况

    参数:
    dockerfile_path (str): Dockerfile 路径

    返回:
    dict: 包含详细分析结果的字典
    """
    try:
        dockerfile_content = read_file_to_string(dockerfile_path)
        is_compatible, reason = check_ssh_injection_compatibility(dockerfile_content)

        # 提取基础镜像信息
        base_images = re.findall(r'FROM\s+([^\s]+)', dockerfile_content, re.IGNORECASE)

        # 检查是否有 ENTRYPOINT
        has_entrypoint = bool(re.search(r'^\s*ENTRYPOINT\s+', dockerfile_content, re.MULTILINE))

        # 检查是否有 CMD
        has_cmd = bool(re.search(r'^\s*CMD\s+', dockerfile_content, re.MULTILINE))

        # 检查是否已经暴露了 22 端口
        has_ssh_port = bool(re.search(r'EXPOSE\s+22', dockerfile_content, re.IGNORECASE))

        return {
            "compatible": is_compatible,
            "reason": reason,
            "base_images": base_images,
            "final_base_image": base_images[-1] if base_images else None,
            "has_entrypoint": has_entrypoint,
            "has_cmd": has_cmd,
            "has_ssh_port": has_ssh_port,
            "dockerfile_path": dockerfile_path
        }
    except Exception as e:
        return {
            "compatible": False,
            "reason": f"Error reading Dockerfile: {e}",
            "error": str(e)
        }

def get_shell_content(gist_url:str) -> str:
    """
    获取下载脚本的内容
    """
    try:
        response = requests.get(gist_url)
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching shell content: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    # 测试不同类型的 Dockerfile
    test_dockerfiles = [
        ("Ubuntu Dockerfile", "FROM ubuntu:20.04\nRUN apt-get update\nCMD ['echo', 'hello']"),
        ("Distroless Dockerfile", "FROM gcr.io/distroless/base-debian12\nCOPY app .\nCMD ['./app']"),
        ("Alpine Dockerfile", "FROM alpine:3.18\nRUN apk add --no-cache curl\nCMD ['/bin/sh']"),
        ("Scratch Dockerfile", "FROM scratch\nCOPY app /app\nENTRYPOINT ['/app']"),
        ("Node.js Dockerfile", "FROM node:18\nWORKDIR /app\nCMD ['node', 'index.js']")
    ]

    print("SSH Injection Compatibility Analysis:")
    print("=" * 50)

    for name, content in test_dockerfiles:
        print(f"\n{name}:")
        is_compatible, reason = check_ssh_injection_compatibility(content)
        status = "✅ COMPATIBLE" if is_compatible else "❌ NOT COMPATIBLE"
        print(f"  Status: {status}")
        print(f"  Reason: {reason}")

    # 如果有实际的 Dockerfile 文件，也可以测试
    input_dockerfile_path = '../configs/dockerfiles/user.Dockerfile'
    output_dockerfile_path = '../configs/dockerfiles/final.Dockerfile'
    rsa_path = '~/.ssh/id_rsa.pub'

    if os.path.exists(input_dockerfile_path):
        print(f"\n\nAnalyzing actual Dockerfile: {input_dockerfile_path}")
        analysis = analyze_dockerfile_for_ssh_support(input_dockerfile_path)
        print(f"Compatible: {analysis['compatible']}")
        print(f"Reason: {analysis['reason']}")
        print(f"Base images: {analysis.get('base_images', [])}")

        # generate_dockerfile(input_dockerfile_path, output_dockerfile_path, rsa_path)



