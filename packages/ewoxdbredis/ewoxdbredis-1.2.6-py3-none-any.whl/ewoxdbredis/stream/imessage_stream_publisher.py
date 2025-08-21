from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from abc import ABC, abstractmethod
import redis
from ewoxcore.message.message_args import MessageArgs

T = TypeVar("T", redis.RedisCluster, redis.Redis)


class IMessageStreamPublisher(ABC):
    @abstractmethod
    async def publish(self, model:T) -> bool:
        """ Publish a message to the stream. """
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def publish_command(self, command:str, model:T) -> bool:
        """ Publish a command to the stream. """
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    async def publish_message(self, args:MessageArgs) -> bool:
        """ Publish a message to the stream. """
        raise NotImplementedError("Implement inhereted method")
