from vkube_cli.utils.validate_vkubefile import VkubefileValidator
from vkube_cli.utils.validate_vkubefile import ContainerValidator
from vkube_cli.utils.file_io import read_yaml
config_file_path = "./local-vkubefile.yaml"
json_file_path = "./test-service.json"

json_data = read_yaml(json_file_path)
print("......")
print(json_data)
real_resource_unit_str = ""
if json_data:
    buy_resource_unit_str = json_data["serviceOptions"]["resourceUnit"]
else:
    print("read json file failed")

config = read_yaml(config_file_path)
if not config:
    print(f"read config failed or the {config_file_path} content is empty")
else:
    container_docs = config.get("containers",{})
    print("...... test start ......")
    vkubefile_validator = VkubefileValidator()
    container_validator = ContainerValidator(container_docs)
    resource_validated,err_str = container_validator.validate_resources(buy_resource_unit_str)
    resource_unit,ports = container_validator.get_real_used_resource()
    print(f"configured resource unit: {resource_unit}, configured ports: {ports}")
    if not resource_validated:
        print(f"resource validation failed: {err_str}")
    else:
        print("resource validation passed")
    result,errors = vkubefile_validator.validate_vkubefile(config)
    if not result:
        for error in errors:
            print(f"{error}")
    else:
        print("all configuration successfully verified")
