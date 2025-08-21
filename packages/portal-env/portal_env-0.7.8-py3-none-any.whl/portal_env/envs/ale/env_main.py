from portal_env import EnvSidePortal
from portal_env.config import config
import gymnasium
import ale_py


def main():
    portal = EnvSidePortal(env_factory=gymnasium.make, port=config.env_ports['ale'])
    portal.start()


if __name__ == '__main__':
    main()
