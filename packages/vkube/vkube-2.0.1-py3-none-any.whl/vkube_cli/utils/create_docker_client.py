import docker
import subprocess
import platform
import json
from docker.errors import DockerException
from typing import Optional
def create_client():
    endpoint = get_current_context_host() or (
        "npipe:////./pipe/docker_engine" 
        if platform.system() == "Windows" 
        else "unix://var/run/docker.sock"
    )
    
    try:
        # create client and test connect
        if platform.system() == "Windows" and endpoint.startswith("npipe://"):
            client = docker.DockerClient(
                base_url=endpoint,
                timeout=5,
                use_ssh_client=False  # not use SSH
            )
        else:
            client = docker.DockerClient(base_url=endpoint, timeout=5)
        res = client.ping() # test connect
        if res:
            return client
        else:
            print("Docker connection failed!")
            return None
    except DockerException as e:
        raise ConnectionError(
            f"Can't connect to the Docker daemon process: {endpoint}\n"
            f"error message: {str(e)}"
        )
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")
def get_current_context_host() -> Optional[str]:
    """use 'docker context ls command' to get the current context  Docker host"""
    try:
        cmd = ["docker", "context", "ls", "--format", "{{json .}}"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        contexts = []
        for line in result.stdout.strip().split('\n'):
            if line:
                ctx = json.loads(line)
                contexts.append(ctx)
        current_ctx = next(
            (ctx for ctx in contexts if ctx.get("Current", "")), 
            None
        )   
        if current_ctx:
            return current_ctx["DockerEndpoint"]
        else:
            print("No current context found.")
            return None
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching contexts: {str(e)}")
    
    return None