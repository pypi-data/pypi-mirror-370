from typing import Any, List, Dict, Text, Optional, Tuple, TypeVar, Union, Awaitable
import logging
import redis
from ewoxdbredis.repositories.redis_base_repository import RedisBaseRepository

T = TypeVar("T", redis.asyncio.RedisCluster, redis.asyncio.Redis)


class RedisSortedSetRepository(RedisBaseRepository):
    def __init__(self, table_name:str="") -> None:
        super().__init__(table_name)


    async def get(self, connection:T, key:str) -> float:
        """ Get the score of a key in the sorted set. If the key does not exist, return -1. """
        if (self._table_name):
            index:int = await connection.zrevrank(self._table_name, key)
            if (index != -1):
                items_inner = await connection.zrange(self._table_name, index, index, desc=True, withscores=True)
                if (items_inner is not None):
                    tup:Tuple[str, float] = items_inner[0]
                    val:float = tup[1]
                    return val

        return -1


    async def delete(self, connection:T, key:str) -> bool:
        """ Delete a key from the sorted set. Returns True if the key was deleted, False otherwise. """
        if (self._table_name):
            await connection.zrem(self._table_name, key)
            return True

        return False


    async def get_num(self, connection:T) -> int:
        """ Get the number of items in the sorted set. Returns 0 if the table name is not set. """
        num:int = 0
        if (self._table_name):
            num = await connection.zcard(self._table_name)
        
        return num


    async def set(self, connection:T, key:str, score:float) -> bool:
        """ Returns true if the order of the set has changed """
        if (self._table_name):
            dict_score:Dict = dict()
            dict_score[key] = score
            val = await connection.zadd(self._table_name, dict_score, ch=True)
            if (val == 1):
                return True
        
        return False


    async def set_items(self, connection:T, items:Dict) -> bool:
        """ Set multiple items in the sorted set. Returns True if the items were added successfully. """
        if (self._table_name):
            await connection.zadd(self._table_name, items)
            return True
        
        return False


    async def get_items(self, connection:T, skip:int, num:int) -> List[Tuple[str, float]]:
        """ Get items from the sorted set with pagination. Returns a list of tuples (key, score). """
        if (self._table_name):
            items:List[Tuple[str, float]] = []

            items_inner = await connection.zrange(self._table_name, skip, num, desc=True, withscores=True)
            if (items_inner is not None):
                for tup in items_inner:
                    key:str = tup[0].decode()
                    val:float = tup[1]
                    items.append((key, val))

                return items

        return []


    async def increment_by(self, connection:T, key:str, value:float) -> bool:
        """ Increment the score of a key in the sorted set by a specified value. Returns True if the key was found and incremented. """
        if (self._table_name):
            val = await connection.zincrby(self._table_name, value, key)
            return True

        return False


    async def get_rank(self, connection:T, key:str) -> int:
        """ The rank (or index) is 0-based, which means that the member with the lowest score has rank 0. """
        index:int = -1
        if (self._table_name):
            index = await connection.zrank(self._table_name, key)

        return index


    async def get_range(self, connection:T, start:int, end:int, descending:bool=False) -> List[tuple[Any, float]]:
        """ Get a range of items from the sorted set. If descending is True, get items in descending order. """
        if (self._table_name):
            return await connection.zrange(self._table_name, start, end, descending, withscores=True)

        return []



if __name__ == "__main__":
    from ewoxdbredis.connection.db_connection import DBConnection
    rep = RedisSortedSetRepository()
    rep.set_table_name("testSortedSet")
    with DBConnection() as connection:
        num:int = rep.get_num(connection)
        rep.set(connection, "123", 100)
        rep.set(connection, "124", 999)
        rep.set(connection, "125", 101)
        rep.set(connection, "126", 9)
        val:float = rep.get(connection, "123")
        val:float = rep.get(connection, "126")
        rep.increment_by(connection, "126", 1)
        val:float = rep.get(connection, "126")
        print(val)

        val:float = rep.get(connection, "123")
        items = rep.get_items(connection, 1, 300)
        print(items)
        rep.delete(connection, "126")
        items = rep.get_items(connection, 1, 3)
        print(items)
