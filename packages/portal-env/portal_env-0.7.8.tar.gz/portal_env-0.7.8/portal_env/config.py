from dataclasses import dataclass, field


@dataclass()
class Config:
    host_name: str = "env_portal"
    port: int = 7000
    env_ports: dict[str, int] = field(default_factory=dict)
    docker_network_name: str = "portal_env_net"


config = Config(
    env_ports={
        'ale': 7001,
        'mujoco': 7002,
        'retro': 7003,
        'craftium': 7004,
        'vizdoom': 7005,
        'flappy-bird': 7006,
    }
)


