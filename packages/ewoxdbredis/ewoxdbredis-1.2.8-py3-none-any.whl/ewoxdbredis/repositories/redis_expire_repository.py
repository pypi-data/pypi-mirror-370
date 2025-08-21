from typing import Any, List, Dict, Mapping, Text, Optional, Tuple, TypeVar, Union, Awaitable
from datetime import date, datetime, timedelta
import logging
import redis
from ewoxdbredis.repositories.redis_base_repository import RedisBaseRepository
from ewoxdbredis.settings.connection_settings import ConnectionSettings

T = TypeVar("T", redis.asyncio.RedisCluster, redis.asyncio.Redis)


class RedisExpireRepository(RedisBaseRepository):
    def __init__(self, table_name:str="") -> None:
        super().__init__(table_name)


    def _get_internal_key(self, key:str) -> str:
        return f"{self._table_name}_{key}"


    async def set_expire(self, connection:T, key:str, value:str, expire:timedelta) -> bool:
        """ Add a key/value that expires in x-time from now. """
        if (self._table_name):
            internal_key:str = self._get_internal_key(key)
            await connection.set(internal_key, value)
            expire_at:datetime = datetime.now() + expire
            await connection.expireat(internal_key, expire_at)
            return True

        return False


    async def set_expire_at(self, connection:T, key:str, value:str, expire_at:datetime) -> bool:
        """ Add a key/value that expires at. """
        if (self._table_name):
            internal_key:str = self._get_internal_key(key)
            await connection.set(internal_key, value)
            await connection.expireat(internal_key, expire_at)
            return True
        
        return False


    async def set(self, connection:T, key:str, value:str) -> bool:
        """ Set a key/value without expiration. """
        if (self._table_name):
            internal_key:str = self._get_internal_key(key)
            await connection.set(internal_key, value)
            return True
        
        return False


    async def get(self, connection:T, key:str) -> str:
        """ Get a value by its key. If the key does not exist, return an empty string. """
        if (self._table_name):
            internal_key:str = self._get_internal_key(key)
            value:str = await connection.get(internal_key)
            return value.decode() if (value is not None) else ""
        
        return ""


    async def delete(self, connection:T, key:str) -> bool:
        """ Delete a key from the Redis store. """
        if (self._table_name):
            internal_key:str = self._get_internal_key(key)
            await connection.delete(internal_key)
            return True
        
        return False


    async def exist(self, connection:T, key:str) -> bool:
        """ Check if a key exists in the Redis store. """
        if (self._table_name):
            internal_key:str = self._get_internal_key(key)
            return await connection.exists(internal_key)

        return False



if __name__ == "__main__":
    from ewoxdbredis.connection.db_connection import DBConnection

    rep = RedisExpireRepository()
    rep.set_table_name("cache")
    with DBConnection() as connection:
        rep.set_expire(connection, "cacheKey1", "123", timedelta(seconds=20))

