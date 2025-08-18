from portal_env import EnvSidePortal
import gymnasium
import ale_py


def main():
    portal = EnvSidePortal(env_factory=gymnasium.make)
    portal.start()


if __name__ == '__main__':
    main()
