from dataclasses import dataclass


@dataclass()
class Config:
    host_name: str = "env_portal"
    port: int = 7000
    docker_network_name: str = "portal_env_net"


config = Config()


