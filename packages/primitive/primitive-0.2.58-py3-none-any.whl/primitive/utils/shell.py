import subprocess
from pathlib import Path
from shutil import which
from typing import Dict, Union, List


def add_path_to_shell(path: Path):
    if not path.exists():
        raise Exception(f"{path} does not exist.")

    try:
        subprocess.run(["fish_add_path", path], capture_output=True)
        return True
    except FileNotFoundError:
        pass

    profile_path = None

    if Path.home().joinpath(".bash_profile").exists():
        profile_path = Path.home().joinpath(".bash_profile")
    elif Path.home().joinpath(".bashrc").exists():
        profile_path = Path.home().joinpath(".bashrc")
    elif Path.home().joinpath(".zshrc").exists():
        profile_path = Path.home().joinpath(".zshrc")
    elif Path.home().joinpath(".profile").exists():
        profile_path = Path.home().joinpath(".profile")
    elif Path.home().joinpath(".bash_login").exists():
        profile_path = Path.home().joinpath(".bash_login")
    else:
        raise Exception(f"Failed to add {path} to PATH")

    with open(profile_path, "a") as file:
        file.write(f"export PATH={path}:$PATH\n")

    return True


def env_to_dict(env_vars: Union[bytes, str, List[str]]) -> Dict:
    lines = None
    if isinstance(env_vars, list):
        lines = env_vars
    elif isinstance(env_vars, str):
        lines = env_vars.splitlines()
    elif isinstance(env_vars, bytes):
        lines = env_vars.decode("utf-8").splitlines()
    else:
        raise ValueError("Unsupported type. Env_vars must be a list or a string")

    current_key = None
    current_value = []
    env_dict = {}
    for line in lines:
        if "=" in line:
            if current_key is not None:
                env_dict[current_key] = "\n".join(current_value)

            key, value = line.split("=", 1)

            current_key = key
            current_value = [value]
        else:
            current_value.append(line)

    if current_key is not None:
        env_dict[current_key] = "\n".join(current_value)

    return env_dict


def does_executable_exist(executable_name: str) -> bool:
    """Check if an executable is available on the path."""
    return which(executable_name) is not None
