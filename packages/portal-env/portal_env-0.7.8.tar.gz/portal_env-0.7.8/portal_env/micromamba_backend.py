from typing import Literal, Union, Optional
import subprocess
from importlib.resources import files
from portal_env.config import config
from portal_env.utils import EnvNotSupportedError
from pathlib import Path
import yaml
from loguru import logger


def read_env_name(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("name")


def get_micromamba_env_path(env_name: str, root_prefix=None) -> Union[Path, None]:
    query = ["micromamba", "env", "list", "--json"]
    if root_prefix is not None:
        query += [ "--root-prefix", root_prefix]
    try:
        result = subprocess.run(
            query,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        import json
        envs = json.loads(result.stdout)["envs"]
        for env in envs:
            suffix = Path('envs') / env_name
            if env.endswith(str(suffix)):
                return Path(env)
            
    except Exception as e:
        logger.error("Error checking micromamba environments:", e)
        return None    


def build_env_if_necessary(env_name: str, build_flag: bool, custom_path: Optional[Path] = None) -> str:
    # Locate the path to the target env directory
    env_path = files("portal_env.envs").joinpath(env_name)

    path_prefix = env_path if custom_path is None else custom_path
    micromamba_spec_path = path_prefix / "spec.yml"
    env_main_path = path_prefix / "env_main.py"
    env_setup_path = path_prefix / "env_setup.py"
    if not (micromamba_spec_path.exists() and env_main_path.exists()):
        raise EnvNotSupportedError(f"Could not locate spec.yml and env_main.py files in '{path_prefix}'")

    # Run micromamba create / update and run using that directory as the working dir
    micromamba_env_name = read_env_name(micromamba_spec_path)
    micromamba_env_path = get_micromamba_env_path(micromamba_env_name)
    if micromamba_env_path is None:
        logger.info(f"Building micromamba env for '{env_name}'...")
        subprocess.run(["micromamba", "create", "-f", micromamba_spec_path.absolute(), "-y"], check=True)
        micromamba_env_path = get_micromamba_env_path(micromamba_env_name)
        assert micromamba_env_path is not None

        if env_setup_path.exists():
            subprocess.run(["micromamba", "run", "-n", micromamba_env_name, "python", env_setup_path], check=True)

    elif build_flag:
        logger.info('Updating micromamba env...')
        # "micromamba env update --file environment.yml --prune"
        subprocess.run(["micromamba", "env", "update", "--file", micromamba_spec_path.absolute(), "--prune"], check=True)

    return micromamba_env_name


def run_env(env_name: str, detach: bool, build_flag: bool, custom_path: Optional[Path]):
    env_path = files("portal_env.envs").joinpath(env_name)
    pkg_path = files("portal_env")
    micromamba_env_name = build_env_if_necessary(env_name, build_flag, custom_path)

    # Run the server:
    path_prefix = env_path if custom_path is None else custom_path
    env_main_path = path_prefix / "env_main.py"
    run_args = [
        "micromamba", "run", "-n", micromamba_env_name, "python", env_main_path.absolute()
    ]
    run_args.append(micromamba_env_name)
    subprocess.run(run_args, cwd=str(pkg_path), check=True)
