from typing import Any, List, Dict, Mapping, Text, Optional, Tuple, TypeVar, Union, Awaitable
from datetime import date, datetime, timedelta
import logging
import redis
from ewoxdbredis.repositories.redis_base_repository import RedisBaseRepository

T = TypeVar("T", redis.asyncio.RedisCluster, redis.asyncio.Redis)


class RedisHashRepository(RedisBaseRepository):
    def __init__(self, table_name:str="") -> None:
        super().__init__(table_name)


    async def set(self, connection:T, key:str, value:str) -> bool:
        """ Set a key/value without expiration. """
        if (self._table_name):
            await connection.hset(self._table_name, key, value)
            return True
        
        return False


    async def set_expire(self, connection:T, key:str, value:str, expire_at:datetime) -> bool:
        """ Add a key/value that expires in x-seconds. """
        if (self._table_name):
            await connection.hset(self._table_name, key, value)
            await connection.expireat(key, expire_at)
            return True
        
        return False


    async def get(self, connection:T, key:str) -> str:
        """ Get a value by its key. If the key does not exist, return an empty string. """
        if (self._table_name):
            value:str = await connection.hget(self._table_name, key)
            return value.decode() if (value is not None) else ""
        
        return ""


    async def set_item(self, connection:T, key:str, item:Dict) -> bool:
        """ Set a hash item in the Redis store. """
        env_key:str = self.get_enviroment_prefix() + key
        return await connection.hset(env_key, mapping=item)


    async def set_item_expire_at(self, connection:T, key:str, item:Dict, expire_at:datetime) -> bool:
        """ Set a hash item in the Redis store with an expiration time. """
        env_key:str = self.get_enviroment_prefix() + key
        await connection.hset(env_key, mapping=item)
        await connection.expireat(key, expire_at)
        return True


    async def get_item(self, connection:T, key:str, use_env:bool=True) -> Dict:
        """ Get a hash item by its key. If the key does not exist, return an empty dictionary. """
        env_key:str = self.get_enviroment_prefix() + key if (use_env) else key
        data:Dict = await connection.hgetall(env_key)
        model:Dict = dict()
        for key, value in data.items():
            model[key.decode()] = value.decode()

        return model


    async def get_keys_by_filter(self, connection:T, match:str) -> List[str]:
        """ Get all keys that match a specific pattern. """
        keys:List[str] = []
        env_match:str = self.get_enviroment_prefix() + match
        for key in await connection.scan_iter(match=env_match):
            keys.append(key.decode())

        return keys


    async def delete_item(self, connection:T, key:str) -> int:
        """ Delete a hash item by its key. Returns the number of deleted fields. """
        env_key:str = self.get_enviroment_prefix() + key
        return await connection.hdel(env_key)


    async def get_items(self, connection:T, keys:List[str]) -> List[Tuple[str, str]]:
        """ Get multiple items by their keys. Returns a list of tuples (key, value). """
        num_keys:int = len(keys)
        if (num_keys == 0):
            return []
        if (self._table_name):
            items:List[Tuple[str, str]] = []
            items_internal:List[str] = await connection.hmget(self._table_name, keys)
            if (items_internal is not None):
                for index, val in enumerate(items_internal):
                    if (val is not None):
                        if (index < num_keys):
                            items.append((keys[index], val.decode()))
            return items
        
        return []


    async def delete(self, connection:T, key:str) -> bool:
        """ Delete a key from the Redis hash table. Returns True if the key was deleted, False otherwise. """
        if (self._table_name):
            await connection.hdel(self._table_name, key)
            return True
        
        return False


    async def exist(self, connection:T, key:str) -> bool:
        """ Check if a key exists in the Redis hash table. Returns True if the key exists, False otherwise. """
        if (self._table_name):
            return await connection.hexists(self._table_name, key)
        
        return False


    async def get_num(self, connection:T) -> int:
        """ Get the number of items in the Redis hash table. """
        if (self._table_name):
            return await connection.hlen(self._table_name)

        return 0


    async def increment_by(self, connection:T, key:str, value:int) -> int:
        """ Increment the value of a key in the Redis hash table by a specified amount. """
        new_value:int = await connection.hincrby(self._table_name, key, value)
        return new_value


    async def get_table_keys(self, connection:T) -> List[str]:
        """ Get all keys in a hash table. Do not use this function on production. """
        keys_decoded:List[str] = []
        if (self._table_name):
            keys = await connection.hkeys(self._table_name)
            for key in keys:
                keys_decoded.append(key.decode())

        return keys_decoded


if __name__ == "__main__":
    from ewoxdbredis.connection.db_connection import DBConnection

    rep = RedisHashRepository()
    rep.set_table_name("cache")
    with DBConnection() as connection:
        expire_at:datetime = datetime.now() + timedelta(seconds=20)
        rep.set_expire(connection, "cacheKey1", "123", expire_at)

    rep = RedisHashRepository()
    rep.set_table_name("users")
    with DBConnection() as connection:
        rep.set_table_name("users")
        keys:List[str] = rep.get_keys(connection)
        user:Dict = dict()
        user["id"] = 1
        user["name"] = "Dude"
        user["video_likes"] = "user:1:video_likes"
        rep.set_item(connection, "user:1", user)

        video_likes:Dict = dict()
        video_likes["video1"] = 100
        video_likes["video2"] = 100
        video_likes["video3"] = 90
        rep.set_item(connection, "user:1:video_likes", video_likes)
        item = rep.get_item(connection, "user:1:video_likes")
        rep.set(connection, "123", 100)
        rep.set(connection, "124", 99)
        rep.set(connection, "125", 101)
        rep.set(connection, "126", 9)

        rep.get_keys_by_filter(connection, "user:*")

        value:str = rep.get(connection, "124")
        keys:List[str] = []
        keys.append("124")
        keys.append("126")
        items = rep.get_items(connection, keys)
        print(items)
