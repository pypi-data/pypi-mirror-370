import portal
import numpy as np
from typing import Any, Optional, Iterable, Union, List, Tuple, Dict
import gymnasium as gym
from portal_env.config import config
from portal_env.utils import parse_gym_space


class AgentSidePortal(gym.Env):
    def __init__(
        self,
        env_name: str,
        env_args: Optional[Union[List[Any], Tuple[Any]]] = None,
        env_kwargs: Optional[Dict[str, Any]] = None,
        agent_in_docker: bool = False
    ):
        """
        :param env_name: string. The name of the environment.
        :param env_args: A list of arguments for creating an instance of 
        the environment.
        :param env_kwargs: a dictionary of keyword arguments for creating
        an instance of the environment.
        :param agent_in_docker: whether the agent is running inside a Docker container
        (True) or directly on the host machine (False). This value is important for
        connecting to the environment container. 
        """
        host_name = 'localhost'
        if agent_in_docker:
            host_name = f"{config.host_name}_{env_name}"
        self.portal = portal.Client(f"{host_name}:{config.port}")
        self._env_id = None

        if env_args is None:
            env_args = []
        assert isinstance(env_args, (list, tuple)), "env_args must be a list or tuple"
        if env_kwargs is None:
            env_kwargs = {}
        assert isinstance(env_kwargs, dict), "env_kwargs must be a dict"

        self._init_env(env_args, env_kwargs)

    def _init_env(self, env_args, env_kwargs):
        assert self._env_id is None, "Environment already initialized"
        future = self.portal.create(env_args, env_kwargs)
        self._env_id = future.result()

    def _assert_env_init(self):
        assert self._env_id is not None, "Environment not initialized"

    def reset(self, **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        self._assert_env_init()
        future = self.portal.reset(self._env_id)
        return future.result()

    def step(self, action) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        self._assert_env_init()
        future = self.portal.step(self._env_id, action)
        # `portal` modifies the object types, convert them back:
        obs, reward, terminated, truncated, info = future.result()
        return obs, float(reward), bool(terminated), bool(truncated), info

    @property
    def action_space(self):
        self._assert_env_init()
        future = self.portal.action_space(self._env_id)
        return parse_gym_space(future.result())

    @property
    def observation_space(self):
        self._assert_env_init()
        future = self.portal.observation_space(self._env_id)
        return parse_gym_space(future.result())
    
    def close(self):
        future = self.portal.close_env(self._env_id)
        res = future.result()
        assert res, f"Failed to close env (response='{res}')"
        self._env_id = None
    
    def __del__(self):
        if self._env_id is not None:
            self.close()
        if hasattr(super(), '__del__'):
            super().__del__()
