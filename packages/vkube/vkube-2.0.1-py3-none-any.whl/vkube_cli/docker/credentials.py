import click
import os
import base64
import json
import subprocess
from subprocess import CalledProcessError
import docker
from docker.errors import DockerException
from vkube_cli.constants import DOCKER_CONFIG_PATH, DOCKER_URL, GHCR_URL
def check_auth_field():
    # 将 JSON 字符串解析为 Python 字典
    try:
        with open(DOCKER_CONFIG_PATH, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {DOCKER_CONFIG_PATH}")
        return False
    except FileNotFoundError:
        print(f"Error: {DOCKER_CONFIG_PATH} not found")
        return False

    # 检查 "auths" 字段是否存在
    if "auths" not in data:
        print("The 'auths' field does not exist.")
        return False
    if DOCKER_URL not in data["auths"]:
        return False
    return True
#Linux
def get_logined_username(registry_url):
    try:
        # 加载配置文件
        with open(DOCKER_CONFIG_PATH, 'r') as file:
            config = json.load(file)
        if config.get("credsStore"):
            if os.name == 'posix':
                if 'linux' in os.uname().sysname.lower():
                    if 'microsoft' in os.uname().release.lower():  # WSL
                        result = subprocess.run(['docker-credential-wincred.exe', 'list'], capture_output=True, check=True, text=True)
                    else:
                        result = subprocess.run(['docker-credential-secretservice', 'list'], capture_output=True, check=True, text=True)
                elif 'darwin' in os.uname().sysname.lower():
                    result = subprocess.run(['docker-credential-osxkeychain', 'list'], capture_output=True, check=True, text=True)
                else:
                    raise Exception("Unsupported POSIX system")
            elif os.name == 'nt':
                result = subprocess.run(['docker-credential-desktop.exe', 'list'], capture_output=True, check=True, text=True)
            output = result.stdout[1:-2]
            if len(output) <= 0 :
                return ""
            s = output.replace('"', '')

            # 以逗号分隔字符串
            key_value_pairs = s.split(',')

             # 创建空字典
            result_dict = {}

            # 处理每个键值对
            for pair in key_value_pairs:
            # 找到最后一个分号的位置
                last_colon_index = pair.rfind(':')
            
                if last_colon_index != -1:
                # 切割成键和值并去除空格
                    key = pair[:last_colon_index].strip()
                    value = pair[last_colon_index + 1:].strip()
                    result_dict[key] = value
                    if "ghcr.io" == key and "ghcr.io" in registry_url:
                        return result_dict.get("ghcr.io","")
            return result_dict.get(registry_url,"")
        # 获取 auths 字段
        auths = config.get("auths", {})
        credentials = {}
        
        for registry, data in auths.items():
            auth_base64 = data.get("auth")
            if auth_base64:
                # Base64 解码
                decoded = base64.b64decode(auth_base64).decode('utf-8')
                username, _ = decoded.split(":", 1)
                if registry in registry_url:
                    return username
                credentials[registry] = username
        print(f"No credentials found for registry: {registry_url}")
        return None
    
    except FileNotFoundError:
        print(f"Error: Docker config file not found at {DOCKER_CONFIG_PATH}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {DOCKER_CONFIG_PATH}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def is_docker_opened():
    try:
        client = docker.from_env()
        info = client.info()
        print("Docker Info Retrieved Successfully:")
        return True
    except DockerException as e:
        print(f"Failed to get Docker info. Error: {str(e)}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False
    
def check_and_login(imageRegistry):
    """Check registry login or not"""
    try:
        registry_url= get_registry_url(imageRegistry)
        if not registry_url:
            print("Error: support Docker and GHCR registries only!")
            return None
        name = get_logined_username(registry_url=registry_url)
        if not name:
            print("You have not logined the registry")
            # login
            username = click.prompt("Enter your image registry username")
            password = click.prompt("Enter your image registry  password",hide_input=True)

                # Construct the docker login command
            command = [
                'docker', 'login',
                '--username', username,
                '--password', password,
                registry_url
            ]

                # Execute the command using subprocess
            result = subprocess.run(command, check=False, text=True, capture_output=True)

            # Check the return code to determine if the login was successful
            if result.returncode == 0:
                print("Login successful:")
                return username
            else:
                print("Login failed: {result.stderr}")
                return None
        else:
            print(f"{imageRegistry} account already logined in")
            return name
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None

def get_registry_url(imageRegistry):
    if imageRegistry == "docker":
        return DOCKER_URL
    elif imageRegistry == "ghcr":
        return GHCR_URL
    else:
        return None
if __name__ == "__main__":
    urls = ["https://index.docker.io/v1/", "ghcr.io", "https://ghcr.io"]
    for url in urls:
        res = get_logined_username(url)
        print(f"url-->{url},res-->{res}")
