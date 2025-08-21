from portal_env import EnvSidePortal
from portal_env.config import config
import gymnasium
import numpy as np
import craftium


class PortalWrapper(gymnasium.Wrapper):
    def __init__(self, env, *args, **kwargs):
        super().__init__(env)

    def step(self, action: np.ndarray):
        assert isinstance(action, np.ndarray), f"Got {action} instead"
        if action.ndim == 0:
            action = action.item()
        return self.env.step(action)
    

def env_factory(*args, **kwargs):
    env = gymnasium.make(*args, **kwargs)
    return PortalWrapper(env)


def main():
    portal = EnvSidePortal(env_factory=env_factory, port=config.env_ports['craftium'])
    portal.start()


if __name__ == '__main__':
    main()
