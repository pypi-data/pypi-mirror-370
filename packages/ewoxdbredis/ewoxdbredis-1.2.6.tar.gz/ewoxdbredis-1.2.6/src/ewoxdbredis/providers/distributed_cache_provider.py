from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from datetime import date, datetime, timedelta
from ewoxcore.utils.json_util import JsonUtil
from ewoxcore.cache.cache import Cache
from ewoxcore.cache.icache_provider import ICacheProvider
from redis.asyncio import client
from ewoxdbredis.clients.iredis_client import IRedisClient
from ewoxdbredis.connection.db_connection import DBConnection
from ewoxdbredis.repositories.redis_expire_repository import RedisExpireRepository

T = TypeVar("T")


class DistributedCacheProvider(ICacheProvider):
    def __init__(self, client:IRedisClient):
        self._repository:RedisExpireRepository = RedisExpireRepository()
        self._repository.set_table_name("cache")
        self._cache = Cache()
        self._use_local:bool = False
        self._client:IRedisClient = client


    def init(self, use_local:bool) -> None:
        """ Initialize the cache provider."""
        self._use_local = use_local


    def change_use_local(self, use_local:bool) -> None:
        """ Change the use of local cache."""
        self._use_local = use_local


    def activate_expiration(self, timer_interval:int) -> None:
        """ Activate expiration for the cache."""
        if (self._use_local):
            self._cache.activate_expiration(timer_interval)


    def set_cache_size(self, size:int) -> None:
        """ Set the size of the cache."""
        if (self._use_local):
            self._cache.set_cache_size(size)


    async def get(self, cacheKey:str) -> Any:
        """ Get a value from the cache by its key."""
        value:Any = None
        if (self._use_local):
            value = self._cache.get(cacheKey)
            if (value is not None):
                return value

        return await self._repository.get(self._client.get_connection(), cacheKey)


    async def insert(self, cacheKey:str, cacheValue:Any) -> None:
        """ Insert a value into the cache with the given key."""
        if (self._use_local):
            self._cache.insert(cacheKey, cacheValue)

        await self._repository.set(self._client.get_connection(), cacheKey, cacheValue)


    async def remove(self, cacheKey:str) -> None:
        """ Remove a value from the cache by its key."""
        if (self._use_local):
            self._cache.remove(cacheKey)

        await self._repository.delete(self._client.get_connection(), cacheKey)


    def get_all_values(self) -> List[Any]:
        """ Get all values from the cache."""
        raise NotImplementedError("Not supported.")


    async def add(self, key:str, value:str, absolute_expiration:timedelta) -> None:
        """ Add a value to the cache with an absolute expiration."""
        if (self._use_local):
            self._cache.add(key, value, absolute_expiration)

        await self._repository.set_expire(self._client.get_connection(), key, value, absolute_expiration)


    async def add_expire_at(self, key:str, value:str, expire_at:datetime) -> None:
        """ Add a value to the cache with an expiration at a specific datetime."""
        if (self._use_local):
            self._cache.add_expire_at(key, value, expire_at)

        await self._repository.set_expire_at(self._client.get_connection(), key, value, expire_at)


    async def clear(self) -> None:
        """ Clear local cache L1 """
        self._cache.clear()


    async def add_ext(self, key:str, value:T, absolute_expiration:timedelta) -> None:
        """ Add a value to the cache with an absolute expiration, serialized as Base64 encode JSON."""
        value_internal:str = JsonUtil.serializeJson64(value)
        await self.add(key, value_internal, absolute_expiration)


    async def add_expire_at_ext(self, key:str, value:T, expire_at:datetime) -> None:
        """ Add a value to the cache with an expiration at a specific datetime, serialized as Base64 encode JSON."""
        value_internal:str = JsonUtil.serializeJson64(value)
        await self.add_expire_at(key, value_internal, expire_at)


    async def insert_ext(self, key:str, value:T) -> None:
        """ Insert a value into the cache with the given key, serialized as Base64 encode JSON."""
        value_internal:str = JsonUtil.serializeJson64(value)
        await self.insert(key, value_internal)


    async def get_ext(self, class_type:T, key:str) -> T:
        """ Get a value from the cache by its key, deserialized from Base64 encode JSON."""
        value_enc:str = await self.get(key)
        return JsonUtil.deserialize_json64(class_type, value_enc)



if __name__ == "__main__":
    prov:DistributedCacheProvider = DistributedCacheProvider()
    prov.add("cacheKey2", "Dude has a car!", timedelta(seconds=20))
    val:str = prov.get("cacheKey2")
    print(val)