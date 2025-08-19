import click
import os
from pathlib import Path
from vkube_cli.command.config import config
from vkube_cli.command.vkube_deploy import deploy
from vkube_cli.command.version import version
from vkube_cli.constants import VKUBE_CONFIG_PATH

def init_config():
    """Initialize vkube configuration."""
    try:
        config_path = Path(VKUBE_CONFIG_PATH)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(VKUBE_CONFIG_PATH):
            with open(VKUBE_CONFIG_PATH, 'w') as file:
                file.write("# Default vkube configuration\n")
            print(f"[INFO] Created default config file: {VKUBE_CONFIG_PATH}")
    except Exception as e:
        click.echo(f"Error initializing config: {e}", err=True)
        exit(1)



@click.group()
def vkube():
    """vkube CLI: A Kubernetes-like CLI tool."""
    init_config()
vkube.add_command(config)
vkube.add_command(deploy)
vkube.add_command(version)
if __name__ == "__main__":
    vkube()