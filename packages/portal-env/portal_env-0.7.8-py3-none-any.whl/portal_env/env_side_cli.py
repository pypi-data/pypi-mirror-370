"""
CLI tool for automatically generating the docker files and running the env portal
"""
from typing import Literal, Optional
import click
from pathlib import Path
from portal_env.utils import EnvNotSupportedError

supported_envs_aliases = {
    "atari": "ale",
}
supported_envs = [
    "ale",
    "mujoco",
    "retro",
    "craftium",
    # "flappy-bird",
    "vizdoom",
]


@click.command()
@click.argument("env_name")
@click.option('-d', '--detach', is_flag=True, help="Run the Docker container in detached mode")
@click.option('-b', '--backend', type=click.Choice(['docker', 'micromamba', 'mm']), default='docker')
@click.option('-f', '--force-build', is_flag=True, help="Force building the docker image")
@click.option('-p', '--path', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              help="Path to a directory containing custom Dockerfile.env and env_main.py files.")
def start(
    env_name: str, 
    detach: bool, 
    backend: Literal['docker', 'micromamba', 'mm'], 
    force_build: bool, 
    path: Path = None
):
    if env_name in supported_envs_aliases:
        env_name = supported_envs_aliases[env_name]
    if env_name not in supported_envs and path is None:
        raise ValueError(f"Unsupported env name: {env_name}")
    
    if backend == 'docker':
        from portal_env.docker_backend import run_env
        run_env(env_name, detach, build_flag=force_build, custom_path=path)
    elif backend in ['micromamba', 'mm']:
        from portal_env.micromamba_backend import run_env
        run_env(env_name, detach, build_flag=force_build, custom_path=path)


@click.command()
@click.argument("env_name")
def stop(env_name: str):
    pass


@click.command()
@click.option('-b','--backend', type=click.Choice(['docker', 'micromamba', 'mm']), default='docker')
@click.option('-e', '--env-name', type=click.Choice(supported_envs))
@click.option('-f', '--force-build', is_flag=True)
@click.option('-p', '--custom-path', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              help="Path to a directory containing custom Dockerfile.env and env_main.py files.")
def build(backend: Literal['docker', 'micromamba'], env_name: Optional[str], force_build: bool, custom_path: Path):
    if backend == 'docker':
        from portal_env.docker_backend import build_env_if_necessary
    elif backend in ['micromamba', 'mm']:
        from portal_env.micromamba_backend import build_env_if_necessary

    if env_name is None:
        for env_name in supported_envs:
            try:
                build_env_if_necessary(env_name, force_build)
            except EnvNotSupportedError:
                pass
    else:
        build_env_if_necessary(env_name, force_build, custom_path)


@click.group()
def main():
    pass


main.add_command(start)
main.add_command(build)


if __name__ == '__main__':
    main()