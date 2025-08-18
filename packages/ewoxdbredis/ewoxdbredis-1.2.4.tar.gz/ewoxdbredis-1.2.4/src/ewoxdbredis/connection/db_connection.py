from typing import Any, List, Dict, Text, Optional, Tuple, TypeVar, Union, Awaitable
import os
import time
import logging
import redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from ewoxcore.constants.server_env import ServerEnv
from ewoxdbredis.settings.connection_settings import ConnectionSettings

T = TypeVar("T", redis.RedisCluster, redis.Redis)


class DBConnection():
    def __init__(self, settings:ConnectionSettings=ConnectionSettings()) -> None:
        self._settings:ConnectionSettings = settings
        self._connection:T = None


    """ Enter & Exit to use together with the WITH statement. """
    def __enter__(self):
        self._connection = self._connect()
        return self._connection


    def __exit__(self, exc_type, exc_value, tb):
        self._connection.close()


    def _connect(self) -> Union[redis.RedisCluster, redis.Redis]:
        self._connection = self._connect_cluster() if (self._settings.is_cluster) else self._connect_single()
        return self._connection


    def _connect_single(self, num_retries:int=3) -> redis.Redis:
        client:redis.Redis = None

        try:
            client = redis.Redis(host=self._settings.host, port=self._settings.port, 
                                 retry=Retry(ExponentialBackoff(), retries=5))
        except Exception as error:
            logging.error(f"RedisClient.Process. numRetries: {str(num_retries)}, Error: {error}")
            if (num_retries > 0):
                time.sleep(15)
                num_retries -= 1
                return self._connect_single(num_retries)

        return client


    def _connect_cluster(self, num_retries:int=3) -> redis.RedisCluster:
        rc:redis.RedisCluster = None

        try:
            rc = redis.RedisCluster(host=self._settings.host, port=self._settings.port, ssl=True)
        except Exception as error:
            logging.error(f"RedisClient.Process. numRetries: {str(num_retries)}, Error: {error}")
            if (num_retries > 0):
                time.sleep(15)
                num_retries -= 1
                return self._connect_cluster(num_retries)

        return rc
