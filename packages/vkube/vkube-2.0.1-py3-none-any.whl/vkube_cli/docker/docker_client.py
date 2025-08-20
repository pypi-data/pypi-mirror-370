import docker
import subprocess
import platform
import json
from docker.errors import DockerException
from typing import Optional
from typing import Optional, List, Dict, Any
from pathlib import Path

from vkube_cli.logger.loading_printer import LoadingPrinter

class DockerClient:
    def __init__(self):
        self.client = self.create_docker_client()
    def get_current_context(self) -> Optional[str]:
        """Get the current Docker context."""
        endpoint = self.get_current_context_host() or (
            "npipe:////./pipe/docker_engine" 
            if platform.system() == "Windows" 
            else "unix://var/run/docker.sock"
        )
        return endpoint
    def create_docker_client(self):
        
        endpoint = self.get_current_context()
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

    @staticmethod
    def get_current_context_host() -> Optional[str]:
        """use 'docker context ls command' to get the current context Docker host"""
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
        
    def get_local_image_digest(self, image_name) -> tuple[bool, str]:
        try:
            api_client = docker.APIClient(base_url=self.get_current_context())
            response = api_client.inspect_image(image_name)

            if 'Architecture' in response and 'Os' in response:
                arch = response['Architecture']
                os = response['Os']
                if os != 'linux' or arch not in ['amd64', 'x86_64']:
                    print(f"Warning: Image architecture ({os}/{arch}) may not be compatible with linux/amd64")
            if 'RepoDigests' in response and response['RepoDigests']:
                return True, response['RepoDigests'][0].split('@')[1]
            if 'Id' in response:
                return True, response['Id']
            return False, "No digest found in image metadata"

        except docker.errors.NotFound:
            return False, "Image not found locally"
        except docker.errors.APIError as e:
            return False, f"API Error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected Error: {str(e)}"
        
    def tag_image(self, source_image, target_image) -> tuple[bool, str]:
        """
        Tags a Docker image with a new name.
        
        Args:
            source_image: The source image name or ID
            target_image: The target image name with tag
            
        Returns:
            tuple[bool, str]: Success status and a message
        """
        try:
            image = self.client.images.get(source_image)
            image.tag(target_image)
            return True, f"Successfully tagged {source_image} as {target_image}"
        except docker.errors.ImageNotFound:
            return False, f"Source image '{source_image}' not found"
        except docker.errors.APIError as e:
            return False, f"API Error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected Error: {str(e)}"
        
    def build_docker_image(self, full_img_ref, build_args, context_path=".", dockerfile_path="Dockerfile"):
        printer = LoadingPrinter()
        try:
            # Convert paths to absolute paths
            context_path = str(Path(context_path).absolute())
            dockerfile_path = str(Path(dockerfile_path).absolute())
            repository = full_img_ref
            build_logs: List[Dict[str, Any]] = []
            print(f"Start building image-->{repository}")
             # Stream build logs
            for line in self.client.api.build(
                path=context_path,
                dockerfile=dockerfile_path,
                tag=repository,
                rm=True,
                decode=True,
                buildargs=build_args,
                platform='linux/amd64'
            ):
                if 'stream' in line:
                    printer.print(line['stream'].strip())
                    build_logs.append(line['stream'].strip())
                elif 'status' in line:
                    printer.print(line['status'].strip())
                    build_logs.append(line['status'].strip())
                elif 'progress' in line:
                    printer.print(line['progress'].strip())
                elif 'error' in line:
                    build_logs.append(line['error'].strip())
                    raise docker.errors.BuildError(reason=line['error'], build_log=build_logs)
                elif 'errorDetail' in line:
                    printer.print(f"Error detail: {line['errorDetail']}")
                else:
                    printer.print(str(line))
            printer.stop()
            print(f"\nSuccessfully built image: {repository}")

            # Get image digest after successful build
            ok, digest = self.get_local_image_digest(repository)
            if ok and digest:
                print(f"Image digest: {digest}")
                return True, digest
            return True, None

        except DockerException as e:
            print(f"Error while building the image: {str(e)}")
            return False, None
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return False, None
        finally:
            printer.stop()
        

    def docker_push(self, full_img_ref)-> bool:
        success = True
        push_logs = []
        printer = LoadingPrinter()
        try:
            push_response = self.client.images.push(repository=full_img_ref, stream=True, decode=True)
            for log_line in push_response:
                if 'status' in log_line:
                    printer.print(f"Status: {log_line['status'].strip()}")
                    push_logs.append(log_line['status'].strip())
                elif 'progress' in log_line:
                    printer.print(log_line['progress'].strip())
                elif 'errorDetail' in log_line:
                    error_detail = log_line['errorDetail']
                    printer.print(f"Error Detail: {error_detail['message']}")
                else:
                    printer.print(f"Log Entry: {log_line}")
                if "error" in log_line:
                    push_logs.append(log_line['error'].strip())
                    success = False  # Set to failure if error occurs
                    break  # Stop processing on error

        except Exception as e:
            success = False
            print(f"Error pushing image: {e}")
            return False
        finally:
            printer.stop()
        if success:
            print(f"Image {full_img_ref} pushed successfully!")
            return True
        else:
            print(f"Pushing image encounting error: {push_logs}")
            return False
    def ping(self):
        try:
            return self.client.ping()
        except DockerException as e:
            print(f"Error pinging Docker: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False
