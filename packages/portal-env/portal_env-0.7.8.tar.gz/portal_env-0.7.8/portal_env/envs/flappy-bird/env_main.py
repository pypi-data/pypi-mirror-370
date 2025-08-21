from portal_env import EnvSidePortal
from portal_env.config import config
import gymnasium
import os
# os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
# os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import flappy_bird_env  # noqa
from functools import partial


def main():
    env_factory = partial(gymnasium.make, render_mode="rgb_array")
    portal = EnvSidePortal(env_factory=env_factory, port=config.env_ports['flappy-bird'])
    portal.start()


if __name__ == '__main__':
    main()
