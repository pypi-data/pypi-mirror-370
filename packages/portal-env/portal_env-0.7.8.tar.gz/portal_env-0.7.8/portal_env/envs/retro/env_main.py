from typing import Literal
from portal_env import EnvSidePortal
from portal_env.config import config
import gymnasium
import retro
from pathlib import Path
from platformdirs import user_cache_dir
import os
import urllib.request
import zipfile
import subprocess
import wget
import numpy as np


class GymnasiumWrapper(gymnasium.Env):
    def __init__(self, *args, use_restricted_actions: Literal['discrete'] = None, **kwargs):
        super().__init__()
        self._ensure_roms()

        processed_kwargs = {}
        if use_restricted_actions is not None:
            if use_restricted_actions == "discrete":
                processed_kwargs["use_restricted_actions"] = retro.Actions.DISCRETE
        self.retro_env = retro.make(*args, **processed_kwargs, **kwargs)
        self._is_closed = False

    def _ensure_roms(self):
        rom_paths = [Path('/app/cache'), Path(user_cache_dir("portal-env"))]
        if not any([p.exists() for p in rom_paths]):
            print(f"Couldn't locate ROM, downloading to '{rom_paths[1]}'...")
            rom_paths[1].mkdir(parents=True)
            cache_dir = rom_paths[1]
            zip_path = os.path.join(cache_dir, "sega-megadrive-genesis.zip")
            zip_url = "https://archive.org/download/No-Intro-Collection_2016-01-03/Sega-MegaDrive-Genesis.zip"

            # Download the zip file
            # print("Downloading ROMs...")
            wget.download(zip_url, zip_path)

            # Unzip it
            print("Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(cache_dir)

            # Run retro.import
            print("Importing ROMs to gym-retro...")
            subprocess.run(["python3", "-m", "retro.import", cache_dir], check=True)

            # Clean up
            print("Cleaning up...")
            os.remove(zip_path)

    @property
    def action_space(self):
        return gymnasium.spaces.MultiBinary(n=self.retro_env.action_space.n)
    
    @property
    def observation_space(self):
        base_space = self.retro_env.observation_space
        return gymnasium.spaces.Box(
            low=base_space.low,
            high=base_space.high,
            shape=base_space.shape,
            dtype=base_space.dtype
        )

    def step(self, action):
        obs, reward, done, info = self.retro_env.step(action)
        terminated = done
        truncated = False

        obs = np.ascontiguousarray(obs)
        return obs, reward, terminated, truncated, info
    
    def reset(self, *, seed = None, options = None):
        return np.ascontiguousarray(self.retro_env.reset()), {}
    
    def close(self):
        self.retro_env.close()
        self._is_closed = True

    def __del__(self):
        if not self._is_closed:
            self.close()
            del self.retro_env


class AsyncWrapper(gymnasium.Env):
    def __init__(self, env_factory):
        super().__init__()
        self.env = gymnasium.vector.AsyncVectorEnv([env_factory])
        self.action_space = self.env.single_action_space
        self.observation_space = self.env.single_observation_space

    def reset(self, *, seed = None, options = None):
        obs, info = self.env.reset(seed=seed, options=options)
        return obs[0], info
    
    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step([action])
        return obs[0], reward, terminated, truncated, info
    

def env_factory(*arg, **kwargs):
    return AsyncWrapper(env_factory=lambda: GymnasiumWrapper(*arg, **kwargs))


def main():
    portal = EnvSidePortal(env_factory=env_factory, port=config.env_ports['retro'])
    portal.start()


if __name__ == '__main__':
    main()
