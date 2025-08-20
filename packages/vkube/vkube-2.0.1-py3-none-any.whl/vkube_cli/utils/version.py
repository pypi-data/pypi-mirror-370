import re
from importlib.metadata import version, PackageNotFoundError
import pkg_resources
import requests
import click
import time
import functools

from vkube_cli.utils.file_io import write_yaml, read_yaml
from vkube_cli.constants import PACKAGE_NAME, VKUBE_CONFIG_PATH, VERSION_CHECK_INTERVAL

def is_valid_version(version):
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))

def check_pypi_release():
    try:
        vkube_conf = read_yaml(VKUBE_CONFIG_PATH)
        last_check_time = vkube_conf.get("last_check_time", 0)
        now = time.time()
        if last_check_time != 0 and now - last_check_time < VERSION_CHECK_INTERVAL:
            return
        # Local installed version
        current_version = pkg_resources.get_distribution(PACKAGE_NAME).version
        # PyPI query
        resp = requests.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=2)
        if resp.status_code == 200:
            latest_version = resp.json()["info"]["version"]
            if current_version != latest_version:
                click.secho(
                    f"A new version {latest_version} is available! You are using {current_version}.",
                    fg="yellow"
                )
                click.secho(
                    f"Please run: pip3 install -U {PACKAGE_NAME}",
                    fg="green"
                )
    except Exception as e:
        # Silently fail, don't disturb the user
        print(f"Version check failed: {e}")
        pass
    vkube_conf["last_check_time"] = now
    write_yaml(VKUBE_CONFIG_PATH, vkube_conf)

def version_check(func):
    """Decorator: Check version before executing each command"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        check_pypi_release()  # Check version every time a command is called
        return func(*args, **kwargs)
    return wrapper