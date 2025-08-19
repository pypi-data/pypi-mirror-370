
import click
from vkube_cli.utils.version import version_check
from vkube_cli.utils.file_io import write_yaml, read_yaml
from vkube_cli.utils.version import version_check
from vkube_cli.utils.file_io import write_yaml, read_yaml
from vkube_cli.constants import VKUBE_CONFIG_PATH



@click.command(help="Manage vkube configuration.")
@click.option('-w','--write', metavar='KEY=VALUE', help="Write a key-value pair to the config file in the format 'GHCRToken/DockerhubToken=xxx'.")
@click.argument('key', type=str, required=False)
@version_check
def config(write, key):
    """
    Manage vkube configuration.

    Examples:
    - Read a key: vkube config GHCRToken
    - Write a key: vkube config -w GHCRToken=ghcr_XXXXXX
    """

    config = read_yaml(VKUBE_CONFIG_PATH)
    if write:
        # 验证格式为 'GHCRToken=ghcr_XXXXXX'
        if "=" not in write:
            click.echo("Error: Invalid format. Use KEY=VALUE.")
            return
        key, value = write.split("=", 1)
        # 提取 key 和 value
        if key and value:
            config[key] = value
            write_yaml(VKUBE_CONFIG_PATH, config)
            click.echo(f"[INFO] Updated '{key}' in config.yaml file.")
        else:
            click.echo("write failed")
    elif key:
        if not config:
            print("read_config function failed")
            return
        getValue = config.get(key)
        if getValue is not None:
            print(f"{getValue}")
        else:
            click.echo(f"{key} not found in {VKUBE_CONFIG_PATH}.")
    else:
        click.echo("Error: Please specify a key to read or use -w to write.")
        

