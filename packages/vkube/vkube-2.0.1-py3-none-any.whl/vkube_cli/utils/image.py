import requests
from requests.models import Response
import base64,json
from typing import Tuple, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from vkube_cli.constants import GHCR_IMAGE_TAG_URL,DOCKER_IMAGE_TAG_URL,ARCH_X86

def validate_image_name(image_path: str) -> Tuple[bool,str,str,str,str]:
    """Validate and parse container image name format

    Supports the following image name formats:
    - ghcr.io/account/image-name:tag
    - docker.io/account/image-name:tag
    - image-name:tag (defaults to docker.io/library/image-name:tag)
    - account/image-name:tag (defaults to docker.io/account/image-name:tag)

    Args:
        image_path (str): Image path to validate

    Returns:
        Tuple[bool,str,str,str,str]: Returns a tuple containing 5 elements:
            - bool: Whether validation passed
            - str: Registry domain (e.g., 'docker.io' or 'ghcr.io')
            - str: Account name (e.g., 'library' or user account)
            - str: Image name
            - str: Tag name
    """

    if not image_path:
        return False,"","","",""
    # handle different format registryImage name
    # Split image path into parts and handle registry prefix
    parts = image_path.split('/')
    registry = "docker.io"  # default registry
    if image_path.startswith(('ghcr.io/', 'docker.io/')):
        if len(parts) != 3:
            return False, "", "", "", ""
        registry = parts[0]
        account = parts[1]
        image_with_tag = parts[2]
    else:
        # Handle image-name:tag or account/image-name:tag format
        account = "library" if len(parts) == 1 else parts[0]
        image_with_tag = parts[-1]

    # Validate and split tag
    if ':' not in image_with_tag:
        return False, "", "", "", ""

    image_name, tag = image_with_tag.rsplit(":", 1)
    return True, registry, account, image_name, tag

# check if remote image exist and support x86/linux, return image digest
def check_single_image(image_path: str, auths: Dict[str, str]) -> Tuple[str, str, str]:
    """Check if a single container image exists in the registry

    Args:
        image_path (str): Image path to check (e.g., "nginx:latest" or "ghcr.io/owner/repo:tag")
        auths (Dict[str, str]): Dictionary containing registry auths { "docker": {"username": "username", "token": "token"}, "ghcr": {"username": "username", "token": "token"}

    Returns:
        Tuple[str, str, str]: A tuple containing:
            - str: Original image path
            - str: Image digest if exists, empty string otherwise
            - str: Error message if any, empty string if successful
    """
    try:
        image_digest = ""
        # Validate image path format first
        validate_tuple = validate_image_name(image_path)
        if not validate_tuple[0]:
            return image_path, "", f"Invalid image path format:{image_path} can not be empty"
        # Check Docker Hub
        image_name = f"{validate_tuple[2]}/{validate_tuple[3]}"
        tag = validate_tuple[-1]
        if validate_tuple[1] == 'docker.io':
            auth = auths.get("docker", {})
            password = auth.get("password", "")
            username = auth.get("username", "")
            if password and username:
                token = get_docker_hub_token(username,password)
            else:
                return image_path, "", "Docker Hub credentials not found"


            if not token:
                return image_path, "", "Docker token not found"

            headers = {'Authorization': f'Bearer {token}'}
            api_url = f"{DOCKER_IMAGE_TAG_URL}/repositories/{image_name}/tags/{tag}"
            response = requests.get(api_url, headers=headers)
               
            if response.status_code == 404:
                return image_path, "", "Image not found in Docker Hub"
            elif response.status_code != 200:
                return image_path, "", f"Docker Hub API error: {response.text}"
            
            data = response.json()
            image_digest = data.get('digest', '')
            
            if 'images' in data:
                for image in data['images']:
                    if image.get('architecture') == 'amd64' and image.get('os') == 'linux':
                        print(f"Image {image_path} supports x86/linux architecture")
                        return image_path, image_digest, ""
                return image_path, "", f"Image {image_path} does not support x86/linux architecture"
            return image_path, image_digest, ""

        # Check GHCR
        elif validate_tuple[1] == 'ghcr.io':
            auth = auths.get("ghcr", {})
            token = auth.get("password", "")
            if not token:
                return image_path, "", "GitHub token not found"
            ghcr_token = get_ghcr_token(token)
            response = get_ghcr_manifests(image_name, tag, ghcr_token)
            
            if response.status_code == 404:
                return image_path, "", "Image not found in GHCR"
            elif response.status_code != 200:
                return image_path, "", f"GHCR API error: {response.text}"

            image_digest = response.headers.get('docker-content-digest', '')
            content_type = response.headers.get("content-type")
            if content_type == "application/vnd.docker.distribution.manifest.v2+json":
                result, err = handle_ghcr_single_arch_response(response, image_name, ghcr_token)
                if 'digest' in result:
                    image_digest = result['digest']
            elif content_type == "application/vnd.oci.image.manifest.v1+json":
                result, err = handle_ghcr_single_arch_response(response, image_name, ghcr_token)
                if 'digest' in result:
                    image_digest = result['digest']
            elif content_type == "application/vnd.oci.image.index.v1+json":
                result, err = handle_ghcr_multiple_arch_response(response, image_name)
                if 'digest' in result:
                    image_digest = result['digest']
            elif content_type == "application/vnd.docker.distribution.manifest.list.v2+json":
                result, err = handle_ghcr_multiple_arch_response(response, image_name)
                if 'digest' in result:
                    image_digest = result['digest']
            else:
                err = f"Unsupported content type: {content_type}"
            if err == "":
                print(f"Image {image_path} supports x86/linux architecture")
                return image_path, image_digest, ""
            return image_path, "", f"Image {image_path} not support manifest"
        else:
            return image_path, "", f"Registry of image path is not supported:{image_path}"

    except requests.exceptions.RequestException as e:
        return image_path, "", f"Network error: {str(e)}"
    except Exception as e:
        return image_path, "", f"Unexpected error: {str(e)}"

def get_ghcr_token(original_token:str)->str:
    input_bytes = original_token.encode('utf-8')  # 将字符串转为 bytes
    return base64.b64encode(input_bytes).decode('utf-8')
def get_docker_hub_token(username: str, password: str) -> str:
    """Retrieve the Bearer Token of DockerHub
    Args:
        username (str): Docker Hub username
        password (str): Docker Hub password
    Returns:
        str: Bearer token if successful, empty string otherwise
    """
    url = "https://hub.docker.com/v2/users/login/"
    data = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # 检查请求是否成功
        token = response.json().get("token")
        return token if token else ""
    except requests.exceptions.RequestException as e:
        print(f"Failed to get token: {e}")
        return ""
def get_ghcr_manifests(image_name, tag, ghcr_token:str):
    headers = {
        'Accept': 'application/vnd.docker.distribution.manifest.v2+json,application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.oci.image.index.v1+json',
        'Authorization': f'Bearer {ghcr_token}'
    }
    api_url = f"{GHCR_IMAGE_TAG_URL}/{image_name}/manifests/{tag}"
    response = requests.get(api_url, headers=headers)
    return response

def handle_ghcr_multiple_arch_response(resp:Response,image_name)->tuple[Dict,str]:
    if resp.status_code != 200:
        return {},"paremeter wrong"
    response_json = resp.json()
    manifests_list = response_json.get("manifests",[])
    for manifest in manifests_list:
        architecture = manifest.get("platform",{}).get("architecture")
        if architecture == ARCH_X86:
            image_digest = manifest.get('digest', "")
            return {"digest":image_digest},""

    return {},f"Image {image_name} does not support architecture {ARCH_X86}"

def handle_ghcr_single_arch_response(resp:Response,image_name,token:str)->tuple[str,Dict]:
    response_json = resp.json()
    config = response_json.get("config",None)
    image_digest = resp.headers.get('docker-content-digest')
    if config is not None:
        result_tuple = get_ghcr_image_config(config,image_name,token)
        if result_tuple[0] != ARCH_X86:
            return {},f"Image {image_name} does not support architecture {ARCH_X86}"
        else:
            return {"digest":image_digest},""
    else:
        return {},"Parameter is wrong"

def get_ghcr_image_config(single_config:Dict,image_name,token)->tuple[str,str]:
    image_config_digest = single_config.get("digest",None)
    if image_config_digest is None:
        return "","parameter single_config does not have the digest field"
    req_url = f"{GHCR_IMAGE_TAG_URL}/{image_name}/blobs/{image_config_digest}"
    headers = {
        'Accept': '*/*',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(req_url, headers=headers)
    if response.status_code != 200:
        return "","response status code is not equal to 200"
    data = response.json()
    architecture = data["architecture"]
    if architecture == "":
        return "","get architecture failed"
    return architecture, ""
    
def check_images_exist(image_paths: List[str], auths: Dict[str, str], max_workers: int = 5) -> Tuple[Dict[str, str], str]:
    """Check multiple container images existence in parallel

    Args:
        image_paths (List[str]): List of image paths to check
        auths (Dict[str, dict]): Dictionary containing registry auths: { "docker": {"username": "username", "token": "token"}, "ghcr": {"username": "username", "token": "token"}
        max_workers (int): Maximum number of concurrent threads

    Returns:
        Tuple[Dict[str, str], str]: A tuple containing:
            - Dict[str, str]: Results dictionary mapping image paths to digests
            - str: Error message if any, empty string if successful
    """
    results = {}
    error_msg = ""
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_image = {
            executor.submit(check_single_image, image_path, auths): image_path for image_path in image_paths
        }
        
        for future in as_completed(future_to_image):
            image_path, digest, error = future.result()
            results[image_path] = digest
            if error:
                error_msg += f"{image_path}: {error}\n"
    
    return results, error_msg.strip()


def get_ghcr_image_digest(image_name:str,tag:str,token:str)->str:
    """Get the digest of a specific image in GHCR

    Args:
        image_name (str): Image name
        tag (str): Image tag
        tokens (Dict[str,str]): Tokens for authentication

    Returns:
        str: Image digest
    """
    ghcr_token = get_ghcr_token(token)
    response = get_ghcr_manifests(image_name, tag, ghcr_token)
    if response.status_code == 200:
        return response.headers.get('docker-content-digest')
    return ""

def get_docker_image_digest(image_name:str,tag:str,token:str)->str:
    """Get the digest of a specific image in Docker Hub

    Args:
        image_name (str): Image name
        tag (str): Image tag
        tokens (Dict[str,str]): Tokens for authentication

    Returns:
        str: Image digest
    """
    headers = {'Authorization': f'Bearer {token}'}
    # For personal/org repositories, use: account/repository
    # For official images, use: library/repository
    if '/' not in image_name:  # Official image
        api_url = f"{DOCKER_IMAGE_TAG_URL}/repositories/library/{image_name}/tags/{tag}"
    else:  # Personal/org repository
        api_url = f"{DOCKER_IMAGE_TAG_URL}/repositories/{image_name}/tags/{tag}"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('digest')
    return ""
