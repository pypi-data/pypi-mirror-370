from portal_env import EnvSidePortal
from portal_env.config import config
import gymnasium


def main():
    portal = EnvSidePortal(env_factory=gymnasium.make, port=config.env_ports['mujoco'])
    portal.start()


if __name__ == '__main__':
    main()
