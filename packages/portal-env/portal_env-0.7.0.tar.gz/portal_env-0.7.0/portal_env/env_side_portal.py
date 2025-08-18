import threading

import portal
import gymnasium as gym
from functools import partial
from portal_env.config import config
from portal_env.utils import handle_raw_integer
from typing import Callable, Any
from loguru import logger


class EnvSidePortal:
    def __init__(self, env_factory: Callable[[Any], gym.Env], port: int = config.port):
        self.portal = portal.BatchServer(port)
        self.env_factory = env_factory
        self._envs = {}
        self._lock = threading.Lock()
        self._next_id = 0

        self.portal.bind('create', self._create_env)
        self.portal.bind('reset', self._reset_handler)
        self.portal.bind('step', self._step_handler)
        self.portal.bind('action_space', partial(self._space_handler, space_type='action_space'))
        self.portal.bind('observation_space', partial(self._space_handler, space_type='observation_space'))
        self.portal.bind('close_env', self._close_env_handler)

    def _create_env(self, env_args, env_kwargs):
        env = self.env_factory(*env_args, **env_kwargs)
        
        with self._lock:
            env_id = self._next_id
            self._envs[env_id] = env
            self._next_id += 1
        
        logger.info(f"Launched a new environment with id={env_id}")
        return env_id

    def _reset_handler(self, env_id: int):
        env_id = handle_raw_integer(env_id)
        assert env_id in self._envs, f"Invalid env_id: {env_id}"
        env = self._envs[env_id]
        return env.reset()

    def _step_handler(self, env_id, action):
        env_id = handle_raw_integer(env_id)
        assert isinstance(env_id, int), f"Got invalid env_id: {env_id}"
        assert env_id in self._envs, f"Invalid env_id: {env_id}"
        env = self._envs[env_id]
        return env.step(action)

    def _space_handler(self, env_id: int, space_type: str):
        env_id = handle_raw_integer(env_id)
        assert isinstance(env_id, int), f"Got invalid env_id: {env_id}"
        assert env_id in self._envs, f"Invalid env_id: {env_id}"
        env = self._envs[env_id]
        return str(getattr(env, space_type))

    def start(self):
        self.portal.start()

    def __del__(self):
        with self._lock:
            for env_id, env in self._envs.items():
                logger.info(f"Closing environment '{env_id}'...", flush=True)
                env.close()
        logger.info(f"Closed all envs!", flush=True)

    def _close_env_handler(self, env_id: int):
        env_id = handle_raw_integer(env_id)
        assert env_id in self._envs, f"Invalid env_id: {env_id}"
        logger.info(f"Closing env '{env_id}'...", flush=True)
        with self._lock:
            self._envs[env_id].close()
            del self._envs[env_id]
        logger.info(f"Closed!", flush=True)
        return True


