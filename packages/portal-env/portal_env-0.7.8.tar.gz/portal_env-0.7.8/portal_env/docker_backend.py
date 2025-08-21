import subprocess
from importlib.resources import files
from portal_env.config import config
from portal_env.utils import docker_image_exists, ensure_docker_network_exists, EnvNotSupportedError
from pathlib import Path
from typing import Optional
from loguru import logger


def build_env_if_necessary(env_name: str, build_flag: bool, custom_path: Optional[Path]) -> str:
    # Locate the path to the target env directory
    env_path = files("portal_env.envs").joinpath(env_name)

    if custom_path is not None:
        dockerfile_path = custom_path / "Dockerfile.env"
        env_main_path = custom_path / "env_main.py"
        if not (dockerfile_path.exists() and env_main_path.exists()):
            raise EnvNotSupportedError("Custom path must contain Dockerfile.env and env_main.py files")
    else:
        dockerfile_path = f"Dockerfile.env"

    # Convert to string path
    env_dir = str(env_path) if custom_path is None else str(custom_path)

    # Run docker build and run using that directory as the working dir
    # subprocess.run(["docker", "build", "-f", "Dockerfile.env", "-t", config.host_name, "."], cwd=env_dir, check=True)
    container_name = f"{config.host_name}_{env_name}"
    image_name = container_name
    if build_flag or (not docker_image_exists(image_name)):
        logger.info(f"Building image for '{env_name}'...")
        subprocess.run(["docker", "build", "-f", dockerfile_path, "-t", image_name, "."], cwd=env_dir, check=True)

    # Check if a docker network exists, create if not:
    ensure_docker_network_exists(config.docker_network_name)

    return container_name


def run_env(env_name: str, detach: bool, build_flag: bool, custom_path: Optional[Path] = None):
    pkg_path = files("portal_env")
    container_name = build_env_if_necessary(env_name, build_flag, custom_path)
    image_name = container_name

    # Run the container:
    run_args = [
        "docker", "run", "--rm", "--name", container_name, "-v", ".:/app/portal_env",
        "-p", f"{config.port}:{config.port}", "--network", config.docker_network_name,
    ]
    if detach:
        run_args.append("-d")
    run_args.append(image_name)
    subprocess.run(run_args, cwd=str(pkg_path), check=True)
