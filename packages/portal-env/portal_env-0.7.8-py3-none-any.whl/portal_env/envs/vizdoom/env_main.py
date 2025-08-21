from portal_env import EnvSidePortal
from portal_env.config import config
import gymnasium
from vizdoom import gymnasium_wrapper  # noqa


def main():
    portal = EnvSidePortal(env_factory=gymnasium.make, port=config.env_ports['vizdoom'])
    portal.start()


if __name__ == '__main__':
    main()
