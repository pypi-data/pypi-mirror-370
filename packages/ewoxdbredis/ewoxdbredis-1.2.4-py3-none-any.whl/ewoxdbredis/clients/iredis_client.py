from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from abc import ABC, abstractmethod
import redis

T = TypeVar("T", redis.asyncio.RedisCluster, redis.asyncio.Redis)


class IRedisClient(ABC):
    @abstractmethod
    def get_connection(self) -> T:
        """ Get a Redis connection. """
        raise NotImplementedError("Implement inhereted method")
    
    @abstractmethod
    def setup(self) -> None:
        """ Setup the Redis connection. """
        raise NotImplementedError("Implement inhereted method")   

    @abstractmethod
    async def dispose(self) -> None:
        """ Dispose the Redis connection. """
        raise NotImplementedError("Implement inhereted method")