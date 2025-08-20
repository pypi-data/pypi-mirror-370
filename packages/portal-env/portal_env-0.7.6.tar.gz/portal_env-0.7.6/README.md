#  Portal-Env  🤖🪞✨➖✨🪞🌍 
<!--  ➿〰️➖🔹-->

A tool for Reinforcement Learning development that separates the runtime environments of agents and RL environments. 
This tool addresses the challenges of dependency management in RL development (e.g., conflicting dependencies) by serving 
RL environments through isolated Docker containers or Micromamba envs without compromising on performance.

* Experimenting with new RL environments without irreversible changes to your Python / Conda environment is now possible!
* Want to use that one environment that requires an ancient Ubuntu & Python 2.7? No problem!
* Multiple RL environments with conflicting dependencies can coexist without any issues!
* Maintaining high performance, no interaction speed degradation! 


Portal-Env creates a clean separation between:
1. The **agent's runtime environment** - where the RL algorithm is implemented and executed.
2. The **RL environment's runtime environment** - containing the RL environment and its dependencies.

A communication "portal" enables seamless interaction between 
the agent and the environment while keeping their runtime environments isolated.

[//]: # (### Core Components)

[//]: # ()
[//]: # (**Agent Side**: )

[//]: # (Interfaces with the environment through an `AgentSidePortal`.)

[//]: # ()
[//]: # (**Environment Side**:)

[//]: # (Interfaces with the agent through an `EnvSidePortal`.)


## Installation
#### Requirements
- Docker
- Unix-based OS if not using Docker to run your agent
- Optional: [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) for a Docker-free mode.

```bash
pip install portal-env
```


## Usage

### Basic Agent Usage

After starting the environment-side portal (detailed below), you can interact with the environment using 
the `AgentSidePortal`, which requires `<env_name>` (detailed below) as the first argument and takes 
optional arguments and keyword arguments for environment setup:
```python
from portal_env import AgentSidePortal
from stable_baselines3 import PPO


# Initialize the agent-side portal and the environment
env = AgentSidePortal(env_name="ale", env_args=["ALE/Pong-v5"])  # pass environment setup arguments here

# Initialize the agent
agent = PPO("MlpPolicy", env, verbose=1)
agent.learn(total_timesteps=10000)
...

```
Or 
```python
from portal_env import AgentSidePortal
from my_agent import Agent


# Initialize the agent-side portal and the environment
env = AgentSidePortal(env_name="ale", env_args=["ALE/Pong-v5"])  # pass environment setup arguments here

# Initialize the agent
agent = Agent(env.action_space)

# Run an episode
obs, info = env.reset()
done = False
while not done:
    action = agent.act(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
```

If your agent is launched through a Docker container, please apply the following two modifications:
1. When calling `AgentSidePortal`, set the `agent_in_docker` argument to `True` (e.g., `AgentSidePortal(..., agent_in_docker=True)`). This is important for establishing the portal connection.
2. Add the portal network name either 
to your `docker run` command via the `--network portal_env_net` argument:
```
docker run --network portal_env_net ... (rest of your command)
```

or to your `docker-compose.yaml` file if you use one:
```
services:
    <agent_service_name>:
        ...
        networks:
            - portal_env_net
        
        
networks:
    portal_env_net:
        external: true
```

We highly recommend using Docker!

### Launching an Environment Portal
We provide a collection of pre-built environment portals for popular environments, 
together with a cli tool `portal-env` for launching them (and also custom environment portals).
Currently, we support the following environments:
- Atari Learning Environment (`ale`)
- Mujoco and Gymnasium environments (`mujoco`)
- [OpenAI Retro](https://github.com/openai/retro) (`retro`)
- [Craftium](https://github.com/mikelma/craftium) (`craftium`)
- [Flappy Bird](https://github.com/robertoschiavone/flappy-bird-env) (`flappy-bird`)
- [ViZDoom](https://github.com/Farama-Foundation/ViZDoom) (`vizdoom`)

We hope to support more environments in the future.
Contributions are welcome!

To launch a supported environment using the cli tool, use:
```bash
portal-env start <env_name>
```
Here, `<env_name>` denotes a unique environment name.
It should be supplied to the agent-side portal, `AgentSidePortal`, as the first argument during initialization.

This command will start the environment portal by automatically building the Docker image and 
starting a corresponding Docker container.
As in the example above, environment setup arguments should be passed to the `AgentSidePortal` (agent-side).

----

#### Custom Environment Portals

To interact with a custom environment, you need to provide two files:

1. **Environment Main Script** (`env_main.py`):
A script that starts the environment-side portal (server) and provides it with an environment factory, a callable that creates and returns a new environment instance upon call.
```python
from portal_env import EnvSidePortal
from your_env import YourEnvironment  # Your custom environment

portal = EnvSidePortal(env_factory=YourEnvironment)
portal.run()
```

E.g., to set up an Atari environment portal:
```python
from portal_env import EnvSidePortal
import gymnasium
import ale_py


def main():
    portal = EnvSidePortal(env_factory=gymnasium.make)
    portal.start()


if __name__ == '__main__':
    main()
```
Note that the environment's dependencies (e.g., `ale_py`) should only be installed through the *environment* Dockerfile (see below).

2. **Environment Dockerfile** (`Dockerfile.env`):
A Dockerfile for building the Docker image of the environment. This Dockerfile should contain the following:
- Install environment-specific dependencies
- Install Portal-Env (`RUN pip install portal-env`)
- Copy your environment code
- Run the main script from step 1 above using `CMD ["python", "env_main.py"]`.
```dockerfile
FROM python:3.12-slim

# Install environment-specific dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your environment code
COPY . .

# Run the environment portal
CMD ["python", "env_main.py"]
```


You can launch your custom environments automatically using the cli tool:
```bash
portal-env start -p <path-to-custom-env-dir> <env-name>
```
where `<path-to-custom-env-dir>` is the path to the directory containing the `Dockerfile.env` and `env_main.py` files,
and `<env-name>` is the name of the environment (should be unique).

---

#### Micromamba Backend
Portal-env inculdes two backends for running and serving the environment-side portal: `docker` and `micromamba` (with a `mm` alias for convenience).
While the default Docker backend is usually the recommended option, it is not viable in some use cases e.g., when running code on remote servers that require a single contrainer.

To overcome this limitation, portal-env provides a `micromamba` backend that sets up a micromamba runtime environment and serves the RL environment-side portal.
Here, instead of the `Dockerfile.env` file, the micromamba backend expects a `spec.yml` file for creating the python environment, and an optional `env_setup.py` file for setting up additional dependencies of the environment. These files are available for some of the supported environments. Please consider them as examples if you need to write your own custom environment portal with the `micromamba` backend.

To launch an environment, use the same `portal-env` cli command with an additional `-b micromamba` argument or its `-b mm` alias:
```
portal-env start <env_name> -b mm
```


### Other CLI functionality
#### The `build` Command
Use `portal-env build -e <env_name> -b <backend>` to build the environment-side portal service without launching it.



## License

MIT License 


## Credits
- [Portal](https://github.com/danijar/portal) (https://github.com/danijar/portal)
