from typing import Any, List, Dict, Text, Optional, Tuple, TypeVar, Union, Awaitable
import os
import time
import logging
import redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from ewoxcore.constants.server_env import ServerEnv
from ewoxdbredis.clients.iredis_client import IRedisClient
from ewoxdbredis.settings.connection_settings import ConnectionSettings

T = TypeVar("T", redis.asyncio.RedisCluster, redis.asyncio.Redis)


class RedisInstanceClient(IRedisClient):
    def __init__(self, settings:ConnectionSettings=ConnectionSettings()) -> None:
        self._settings:ConnectionSettings = settings
        self._connection:T = None


    def get_connection(self) -> T:
        """ Get the current connection. """
        if (self._connection is None):
            self._connection = self._connect()

        return self._connection
    

    def setup(self) -> None:
        """ Setup the connection if it is not already established. """
        if (self._connection is None):
            self._connection = self.get_connection()
    

    async def dispose(self) -> None:
        """ Dispose the current connection. """
        if (self._connection is not None):
            try:
                await self._connection.close()
            except Exception as error:
                logging.error(f"RedisInstanceClient.dispose. Error: {error}")
            finally:
                self._connection = None


    def _connect(self) -> Optional[redis.asyncio.Redis]:
        client:redis.asyncio.Redis = None

        try:
            client = redis.asyncio.Redis(host=self._settings.host, port=self._settings.port, 
                                 decode_responses=self._settings.decode_responses,
                                 ssl=self._settings.use_ssl,
                                 retry=Retry(ExponentialBackoff(), retries=5))
        except Exception as error:
            logging.error(f"RedisInstanceClient - Error: {error}")

        return client