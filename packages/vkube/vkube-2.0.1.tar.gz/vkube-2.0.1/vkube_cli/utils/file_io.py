import yaml,os
import click
def read_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            doc = yaml.safe_load(f)
            return doc if doc is not None else {}
    except FileNotFoundError:
        click.echo(f"File not found: {file_path}")
    except yaml.YAMLError as e:
        click.echo(f"Error reading YAML file: {e}")
    except Exception as e:
        click.echo(f"Unexpected error: {e}")
    return {}
    
def write_yaml(file_path, data):
    if not data:
        return
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
    except Exception as e:
        click.echo(f"Error writing YAML file: {e}", err=True)


def read_file_to_string(file_path):
    try:
        expanded_path = os.path.expanduser(file_path)
        # Check if the file exists
        if not os.path.exists(expanded_path):
            print(f"File does not exist: {expanded_path}")
            return None
        
        # Check if the file is readable
        if not os.access(expanded_path, os.R_OK):
            print(f"File is not readable: {expanded_path}")
            return None
        
        with open(expanded_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except UnicodeDecodeError:
        # if read by utf-8 failed, try the binary format
        try:
            with open(expanded_path, 'rb') as file:
                content = file.read()
                return content.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"read file binary format failed,: {str(e)}")
            return None
    except Exception as e:
        print(f"read file failed: {str(e)}")
        return None

def resolve_config_path(config_path, runfile_path=None):
    """
    Resolve config file path, supporting:
    1. Absolute path
    2. Path relative to current command execution directory
    3. Path relative to the running file's directory (if runfile_path is provided)

    :param config_path: User input config file path
    :param runfile_path: Running file path (optional)
    :return: Absolute path
    """
    # Case 1: Absolute path
    if os.path.isabs(config_path):
        return config_path

    # Case 2: Try relative to current working directory first
    cwd_path = os.path.abspath(config_path)
    if os.path.exists(cwd_path):
        return cwd_path
    searched_paths = [cwd_path]
    # Case 3: If runfile_path is provided, try relative to runfile directory
    if runfile_path:
        runfile_abs = os.path.abspath(runfile_path)
        runfile_dir = os.path.dirname(runfile_abs)
        runfile_relative_path = os.path.join(runfile_dir, config_path)
        searched_paths.append(runfile_relative_path)
        if os.path.exists(runfile_relative_path):
            return runfile_relative_path
    raise FileNotFoundError(
        f"Config file not found: {config_path}\n"
        f"Searched paths:\n  " + "\n  ".join(searched_paths)
    )
