from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type, cast
import redis
import asyncio
from redis.exceptions import ConnectionError, TimeoutError
from tenacity import retry, wait_exponential, wait_fixed, stop_after_attempt, RetryError
from ewoxcore.utils.json_util import JsonUtil
from ewoxdbredis.clients.iredis_client import IRedisClient
from ewoxdbredis.settings.publisher_settings import PublisherSettings
from ewoxdbredis.stream.imessage_stream_publisher import IMessageStreamPublisher
from ewoxcore.message.message_args import MessageArgs

T = TypeVar("T")
C = TypeVar("C", redis.asyncio.RedisCluster, redis.asyncio.Redis)


class MessageStreamPublisher(IMessageStreamPublisher):
    def __init__(self, settings:PublisherSettings, client:IRedisClient) -> None:
        self._settings:PublisherSettings = settings
        self._client:IRedisClient = client


    async def publish(self, model:T) -> bool:
        """ Publish a message to the stream. """
        encoded_data:str = JsonUtil.serializeJson64(model)
        args:MessageArgs = MessageArgs(encoded_data)
        res:bool = await self.publish_message(args)

        return res


    async def publish_command(self, command:str, model:T) -> bool:
        """ Publish a command to the stream. """
        encoded_data:str = JsonUtil.serializeJson64(model)
        args:MessageArgs = MessageArgs(encoded_data, command=command)
        res:bool = await self.publish_message(args)

        return res


    @retry(
        wait=wait_exponential(min=1, max=10),
        stop=stop_after_attempt(5),
        retry_error_callback=lambda retry_state: None,
        retry=lambda retry_state: isinstance(
            retry_state.outcome.exception(),
            (ConnectionError, TimeoutError, OSError)
        )
    )
    async def publish_message(self, args:MessageArgs) -> bool:
        """ Publish a message to the stream. """
        connection:C = self._client.get_connection()
        if not connection:
            print("No Redis connection available.")
            return False

        try:
            data:Dict[str, str] = {
                "data": args.data,
                "correlationId": args.correlationId,
                "command": args.command,
                "serviceName": args.serviceName,
                "serverName": args.serverName,
                "sendAt": args.sendAt.isoformat()
            }

            mid = await connection.xadd(self._settings.stream_name, data)
            print(f"Published message with ID: {mid}")
        except (ConnectionError, TimeoutError) as e:
            print(f"Error publishing message: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

        return True
