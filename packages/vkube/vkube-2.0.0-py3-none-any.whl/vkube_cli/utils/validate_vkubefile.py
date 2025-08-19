import re
from typing import List, Dict, Tuple
from vkube_cli.utils.image import validate_image_name

from vkube_cli.constants import (
    REGEX_CONTAINER_NAME_PATTERN,
    REGEX_LOCAL_FILE_PATH_PATTERN,
    REGEX_SUBDOMAIN_PATH_PATTERN,
    REGEX_MOUNT_FILE_PATH_PATTERN,
    REGEX_TAG_PATTERN,
    REGEX_IMAGE_NAME_PATTERN
)
supported_kinds = ["vkube"]
supported_image_registries = ["docker","ghcr"]
def validate_string_by_regexp(pattern:str,validate_str:str)-> bool:
    """
    validate string by regexp pattern
    """
    try:
        return bool(re.match(pattern, validate_str))
    except re.error:
        return False
class VkubefileValidator:

    def __init__(self):
        self.supported_kinds = supported_kinds
        self.supported_image_registries = supported_image_registries
        self.errors = []
    def validate_base_fields(self,documents:Dict):
        errors = []
        kind = documents.get('Kind')
        if kind is None:
            errors.append("Kind field is required")
        if isinstance(kind,str):
            if kind.strip() == "":
                errors.append("Kind field can't be empty")
            if kind not in self.supported_kinds:
                errors.append(f"Kind must be one of {self.supported_kinds}")
        else:
            errors.append("Kind must be string type")
        token = documents.get("vkubeToken", None)
        if token is None:
            errors.append("vkube token field is required")
        if isinstance(token,str):
            if token.strip() == "":
                errors.append("vkube token field can't be empty")
        else:
            errors.append("token must be string type")

        image_registry = documents.get("imageRegistry", None)
        if image_registry is None or image_registry.strip() == "":
            image_registry = "docker"
            documents.update({"imageRegistry": image_registry})
        if isinstance(image_registry, str):
            if image_registry not in self.supported_image_registries:
                errors.append(f"imageRegistry must be one of {self.supported_image_registries}")
        else:
            errors.append("imageRegistry must be string type")

        return len(errors) == 0,errors
    def validate_vkubefile(self, documents:Dict):
        # validate base fields
        print("------  start validate configurations ------")
        is_valid,base_errors = self.validate_base_fields(documents)
        if not is_valid:
            self.errors.extend(base_errors)
        
        container_docs = documents.get("containers") 
        if container_docs:
            container_validator = ContainerValidator(container_docs)
            containers_valid, container_errors = container_validator.validate_containers()
            if not containers_valid:
                self.errors.extend(container_errors)
        else:
            self.errors.append("containers configuration not exist")
        return len(self.errors) == 0,self.errors


class ContainerValidator:
    def __init__(self,container_docs:List[Dict]):
        self.container_docs = container_docs
        self.errors = []
    def get_containers_num(self):
        return len(self.container_docs)
    def get_real_used_resource(self)-> Tuple[int,int]:
        total_resourceUnit = 0
        total_ports = 0
        for container_doc in self.container_docs:
            deploy_doc = container_doc.get("deploy",{})
            if deploy_doc:
                total_resourceUnit = total_resourceUnit + int(deploy_doc.get("resourceUnit",0))
                total_ports = total_ports + len(deploy_doc.get("ports",[]))
        return total_resourceUnit,total_ports
    def validate_containers(self) -> Tuple[bool,List[str]]:
        """validate containers list configuration"""  
        for index,container_doc in enumerate(self.container_docs):
            container_index = index + 1
            is_valid, error_msg = self.validate_single_container(container_index,container_doc)
            if not is_valid:
                self.errors.extend(error_msg)     
        return len(self.errors) == 0,self.errors
    def validate_single_container(self, index:int,container_doc: Dict) -> Tuple[bool, List[str]]:
        """Validate all configuration fields for a single container.
        Args:
            index (int): Container index number, used for error_message indentification
            container_doc (Dict): Container configuration dictionary to validate
        Returns:
        Tuple[bool, List[str]]: Return a validtion result tuple contained two values:
            - bool: Whether all validations passed or not
            - List[str]: List of error messages.Even when encounting the first error, continue to validate other fields and returns all found errors 
        """
        
        all_errors = []
        # Validate required deploy field
        deploy_doc = container_doc.get("deploy",None)
        if deploy_doc is None:
            all_errors.append(f"field deploy in num.{index} container not exist")
            return False,all_errors
        else:
            is_valid,error_msgs = self.validate_deploy(index,deploy_doc)
            if not is_valid:
                all_errors.extend(error_msgs)
        # Retrieve container configuration fields 
        registry_image_path = container_doc.get('registryImagePath')
        local_image_path = container_doc.get('localImagePath')
        build_doc = container_doc.get('build',None)
        image_name = container_doc.get('imageName')
        tag = container_doc.get('tag')
        if registry_image_path:
        # When registryImagePath exists, build, tag and imageName fields should not be present
            if build_doc:
                all_errors.append(
                    f"Error:In num.{index} container, Container cannot have both 'registryImagePath' and 'build' fields"
                )
            if tag or image_name:
                all_errors.append(
                    f"Error: In num.{index} container, 'registryImagePath' is specified, 'imageName' field should not be present"
                )
            if local_image_path:
                all_errors.append(
                    f"Error:In num.{index} container, 'registryImagePath' is specified, 'localImagePath' field should not be present"
                )
            # Validate registryImagePath format
            validate_tuple = validate_image_name(registry_image_path)
            if not validate_tuple[0]:
                all_errors.append(
                    f"Error:In num.{index} container, Invalid registry image path format: {registry_image_path}. "
                    "Must be one of these formats:\n"
                    "- ghcr.io/account/image-name:tag\n"
                    "- docker.io/account/image-name:tag\n"
                    "- image-name:tag (for DockerHub)\n"
                    "- account/image-name:tag (for DockerHub)"
                )
        elif local_image_path:
            if build_doc:
                all_errors.append(
                    f"Error:In num.{index} container, Container cannot have both 'registryImagePath' and 'build' fields"
                )
            if tag or image_name:
                all_errors.append(
                    f"Error: In num.{index} container, 'registryImagePath' is specified, 'imageName' field should not be present"
                )
            # Validate registryImagePath format
            validate_tuple = validate_image_name(local_image_path)
            if not validate_tuple[0]:
                all_errors.append(
                    f"Error:In num.{index} container, Invalid registry image path format: {local_image_path}. "
                    "Must be one of these formats:\n"
                    "- ghcr.io/account/image-name:tag\n"
                    "- docker.io/account/image-name:tag\n"
                    "- image-name:tag (for DockerHub)\n"
                    "- account/image-name:tag (for DockerHub)"
                )
        else:
            # When registryImagePath is not present, validate the relationship between build, imageName and tag
            if build_doc:
                res, error_msgs = self.validate_build(index,build_doc)
                if not res:
                    all_errors.extend(error_msgs)
                # When build field exists, both imageName and tag must be present
                if tag is None:
                    all_errors.append(
                        f"Error:In num.{index} container, when 'build' field is present, 'tag' field are required"
                    )
                if isinstance(tag, str):
                    if tag == "":
                        tag = "latest"
                    if not validate_string_by_regexp(REGEX_TAG_PATTERN,tag):
                        all_errors.append(f"tag field in num.{index} container is invalid")
                
                if image_name is None:
                    all_errors.append(
                        f"Error:In num.{index} container, when 'build' field is present, 'imageName' field are required"
                    )
                if isinstance(image_name, str):
                    if not validate_string_by_regexp(REGEX_IMAGE_NAME_PATTERN,image_name):
                        all_errors.append(f"imageName field in num.{index} container is invalid")
                else:
                    all_errors.append(f"imageName field in num.{index} container is not a string type")
            else:
                if registry_image_path is None and image_name is None and tag is None:
                    all_errors.append(
                        f"Error:In num.{index} container, Either 'imageName'and 'tag', 'registryImagePath' or 'build' must be specified"
                    )
                elif registry_image_path == "":
                    all_errors.append(
                        f"Error:In num.{index} container, 'registryImagePath' must not be empty"
                    )
        # If there are errors, return False and error list
        if all_errors:
            return False, all_errors
        
        return True, []
    def validate_ports(self, index:int,ports: List[Dict]) -> Tuple[bool, List[str]]:
        """validate ports"""
        all_errors = []
        for port in ports:
            container_port = port.get('containerPort', None)
            host_port = port.get('hostPort', None)
            if host_port is not None and container_port is None:
                all_errors.append(f"In num.{index} container, containerPort must be set when hostPort is set")

            if container_port and (not isinstance(port['containerPort'], int) or container_port < 1 or container_port > 65535) :
                all_errors.append(f"In num.{index} container,containerPort must be an integer 1 ~ 65535")

            # TODO: microk8s node port range is 30000-32767, user cannot set hostPort in this range
            if host_port and (not isinstance(host_port, int) or container_port < 1 or container_port > 65535) :
                all_errors.append(f"In num.{index} container, host must be an integer 1 ~ 65535")

            path = port.get('path', None)
            rewrite = port.get('rewrite', None)
            if (path is None) != (rewrite is None):
                all_errors.append(f"In num.{index} container, path and rewrite must be both set or not set,current path:{path},rewrite:{rewrite}")
            if path is not None:
                if container_port is None:
                    all_errors.append(f"In num.{index} container, path must be set when containerPort is set")
                if not isinstance(port['path'], str):
                    all_errors.append(f"In num.{index} container,path is not a string")
                if not validate_string_by_regexp(REGEX_SUBDOMAIN_PATH_PATTERN,port['path']):
                    all_errors.append(f"In num.{index} container,path is illegal")
        return len(all_errors) == 0, all_errors
    def validate_envs(self, index:int,envs: List[Dict]) -> Tuple[bool, List[str]]:
        """validate envs"""
        all_errors = []
        for env in envs:
            if 'name' not in env or 'value' not in env:
                all_errors.append(f"the envs in num.{index} container,missing required fields:name or value")
            
            if not isinstance(env['name'], str) or not isinstance(env['value'], str):
                all_errors.append(f"the envs in num.{index} container, the name or value is not a string")
                
            if not env['name']:
                all_errors.append(f"the name of envs in num.{index} container can not be empty")
        
        return len(all_errors) == 0,all_errors
    def validate_build(self,index:int,build_doc:Dict) -> Tuple[bool, List[str]]:
        all_errors = []
        if build_doc is None:
            all_errors.append(f"build field in num.{index} container is required")
            return False,all_errors
        if not isinstance(build_doc, dict):
            all_errors.append(f"build field in num.{index} container must be a dict")
            return False,all_errors
        docker_file_path = build_doc.get('dockerfilePath')
        if docker_file_path is None:
            all_errors.append(f"dockerfilePath field in num.{index} container must be set")
        if not isinstance(docker_file_path,str):
            all_errors.append(f"dockerfilePath field in num.{index} container must be string")
        installSSH = build_doc.get('installSSH',False)
        sshPubKeyPath = build_doc.get('sshPubKeyPath',"")
        if installSSH and sshPubKeyPath:
            if not validate_string_by_regexp(REGEX_LOCAL_FILE_PATH_PATTERN,sshPubKeyPath):
                all_errors.append(f"sshPubKeyPath field in num.{index} container is illegal")
        return len(all_errors) == 0, all_errors
    def validate_deploy(self,index:int,deploy_doc:Dict) -> Tuple[bool, List[str]]:
        all_errors = []
        if not deploy_doc:
            all_errors.append(f"deploy field in num.{index} container is required")
        if not isinstance(deploy_doc, dict):
            all_errors.append(f"deploy field in num.{index} container must be a dict")
        # validate resourceUnit
        resource_unit = deploy_doc.get('resourceUnit')
        if resource_unit is None:
            all_errors.append(f"resourceUnit field in num.{index} container is required")
        if not isinstance(resource_unit, int):
            all_errors.append(f"resourceUnit field in num.{index} container is not int type")
        if resource_unit < 1:
            all_errors.append(f"resourceUnit field in num.{index} container must greate than or equal to 1")
        # validate containerName
        container_name = deploy_doc.get('containerName')
        if container_name is None:
            all_errors.append(f"containerName field in num.{index} container is required")
        if isinstance(container_name, str):
            if container_name == "":
                all_errors.append(f"containerName field in num.{index} container is empty")
            if not validate_string_by_regexp(REGEX_CONTAINER_NAME_PATTERN,container_name):
                all_errors.append(f"containerName field in num.{index} container is illegal")
        else:
             all_errors.append(f"containerName field in num.{index} container is not a string type")

        # validate port configuration
        if 'ports' in deploy_doc:
            is_valid, error_msgs = self.validate_ports(index,deploy_doc['ports'])
            if not is_valid:
                all_errors.extend(error_msgs)
        
        # validate envs
        if 'env' in deploy_doc:
            is_valid, error_msgs = self.validate_envs(index,deploy_doc['env'])
            if not is_valid:
                all_errors.extend(error_msgs)
        if "configurations" in deploy_doc:
            config_doc = deploy_doc.get("configurations")
            if config_doc and isinstance(config_doc, dict):
                for local_path,mount_path in config_doc.items():
                    local_path_is_valid = validate_string_by_regexp(REGEX_LOCAL_FILE_PATH_PATTERN,local_path)
                    mountpath_is_valid = validate_string_by_regexp(REGEX_MOUNT_FILE_PATH_PATTERN,mount_path)
                    if not local_path_is_valid or not mountpath_is_valid:
                        all_errors.append(f"localPath or mountPath in num.{index} container is illegal")
        return len(all_errors)==0,all_errors
    def validate_resources(self,resource_unit_str:str) -> Tuple[bool,str]:
        try:
            if resource_unit_str == "":
                return False,f"parameter {resource_unit_str} can not be empty"
            if "-" in resource_unit_str:
                buy_resource_unit = int(resource_unit_str.split('-')[0])
                if self.get_containers_num() > buy_resource_unit:
                    return False, f"the containers number of configured file is over the resourceUnit you buy"
                real_used_unit,ports = self.get_real_used_resource()
                if real_used_unit > buy_resource_unit:
                    return False,f"Error: total resource unit is excessive,real_buy:{buy_resource_unit},used:{real_used_unit}"
    
                if ports > buy_resource_unit:
                    return False,"Error: the number of configured ports is greater than buy resource unit"
                else:
                    return True, ""
        
            else:
                return False, f"Invalid parameter {resource_unit_str}"
        except ValueError:
            return False,f"change str resource unit to int failed: {resource_unit_str}"
