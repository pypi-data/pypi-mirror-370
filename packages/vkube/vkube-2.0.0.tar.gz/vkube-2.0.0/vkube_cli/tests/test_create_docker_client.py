from vkube_cli.docker.docker_client import DockerClient
from vkube_cli.docker.credentials import is_docker_opened
def test_create_client():
    client = DockerClient()
    assert client is not None
    assert client.ping() is True
def test_is_docker_opened():
    if not is_docker_opened():
        print("not opened")
if __name__ == "__main__":
    test_create_client()