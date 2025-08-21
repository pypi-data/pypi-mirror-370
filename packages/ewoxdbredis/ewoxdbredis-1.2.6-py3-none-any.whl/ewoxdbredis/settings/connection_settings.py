from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable
import os
from ewoxcore.constants.server_env import ServerEnv


class ConnectionSettings():
    def __init__(self,
                 env_host:str="REDIS_HOST",
                 env_port:str="REDIS_PORT",
                 use_ssl:bool=False,
                 is_cluster:bool=False,
                 decode_responses:bool=True) -> None:
        self.host:str = os.getenv(env_host)
        self.port:int = 6379
        if (os.getenv(env_port)):
            self.port = int(os.getenv(env_port))

        self.use_ssl:bool = use_ssl
        self.is_cluster:bool = is_cluster
        self.decode_responses:bool = decode_responses
