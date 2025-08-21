from typing import Any, List, Dict, Mapping, Text, Optional, Tuple, TypeVar, Union, Awaitable
import logging
import redis
import os
from redis.client import Pipeline

T = TypeVar("T", redis.asyncio.RedisCluster, redis.asyncio.Redis)


class RedisBaseRepository():
    def __init__(self, table_name:str="") -> None:
        self._table_name:str = ""
        if (table_name != ""):
            self.set_table_name(table_name)


    def set_table_name(self, table_name:str) -> None:
        """ Set the table name with the environment prefix. """
        self._table_name = self.get_enviroment_prefix() + table_name


    def get_table_name(self) -> str:
        """ Get the table name with the environment prefix. """
        return self._table_name


    def get_enviroment_prefix(self) -> str:
        """ Get the environment prefix from the environment variable APP_ENV. """
        env_prefix:str = os.getenv("APP_ENV").lower() + "_"
        return env_prefix


    async def get_keys(self, connection:T) -> List[str]:
        """ Get all keys from the Redis connection. """
        keys = await connection.keys()
        keys_decoded:List[str] = []
        if (keys):
            for key in keys:
                keys_decoded.append(key.decode())

        return keys_decoded


    async def get_pipeline(self, connection:T) -> Pipeline:
        """ NOTE: Using the Pipeline requires extra responsibility. 
                  All keys must be prefixed with the environment. """
        return await connection.pipeline()
