import click
from importlib.metadata import version as get_version, PackageNotFoundError
from vkube_cli.utils.version import version_check
from vkube_cli.constants import PACKAGE_NAME
@click.command(help="Get vkube version.")
@version_check
def version():
    try:
        cli_version = get_version(PACKAGE_NAME)
    except PackageNotFoundError:
        cli_version = "unknown"  # fallback when not installed in dev environment

    click.echo(f"VKube CLI version: {cli_version}")