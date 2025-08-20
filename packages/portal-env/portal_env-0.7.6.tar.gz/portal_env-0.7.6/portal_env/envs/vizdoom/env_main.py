from portal_env import EnvSidePortal
import gymnasium
from vizdoom import gymnasium_wrapper  # noqa


def main():
    portal = EnvSidePortal(env_factory=gymnasium.make)
    portal.start()


if __name__ == '__main__':
    main()
