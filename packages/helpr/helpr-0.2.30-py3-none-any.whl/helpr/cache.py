from typing import Dict, List, Optional, Union, Any
from enum import Enum
import redis
from fastapi.responses import JSONResponse

class CacheDatabase(int, Enum):
    GENERAL = 0
    TETRIS = 1
    FEED = 2
    ATLAS = 3
    SALEOR = 4
    CART = 5
    ATTRIBUTION = 6
    REVIEW_RATING = 7
    INVENTORY = 8

class BulkRedisActionType(int, Enum):
    ADD_TO_SET = 0
    SET_STRING = 1
    DELETE_STRING = 2
    DELETE_FROM_SET = 3
    SAVE_SORTED_SET = 4

class BulkRedisAction:
    def __init__(self, 
                 action_type: BulkRedisActionType, 
                 key: str, 
                 value: str = None, 
                 values: Union[set, Dict] = None, 
                 expire: int = None, 
                 overwrite: bool = False):
        self.action_type = action_type
        self.key = key
        if action_type == BulkRedisActionType.SET_STRING and value is None:
            raise ValueError("Value cannot be None for SET_STRING action type")
        if (action_type == BulkRedisActionType.ADD_TO_SET or action_type == BulkRedisActionType.DELETE_FROM_SET) and values is None:
            raise ValueError("Values cannot be None for ADD_TO_SET or DELETE_FROM_SET action type")
        if (action_type == BulkRedisActionType.SAVE_SORTED_SET) and (values is None or not isinstance(values, dict)):
            raise ValueError("Values cannot be None for SAVE_SORTED_SET action type")
        self.value = value
        self.values = values
        self.expire = expire
        self.overwrite = overwrite

class RedisHelper:
    def __init__(self, redis_client: redis.Redis, cache_db: CacheDatabase = CacheDatabase.GENERAL, enable_multidb: bool = False):
        self.redis_client = redis_client
        self.cache_db = cache_db
        self.enable_multidb = enable_multidb

    def _tk(self, key: str) -> str:
        """Transform key to include database prefix if multidb is not enabled"""
        if self.enable_multidb:
            return key
        return f"{self.cache_db.value}:{key}"

    def _tks(self, keys: List[str]) -> List[str]:
        """Transform multiple keys"""
        return [self._tk(key) for key in keys]

    # String Operations
    def get_string(self, key: str) -> Optional[str]:
        safe_key = self._tk(key)
        value = self.redis_client.get(safe_key)
        return value.decode('utf-8') if value else None

    def get_strings(self, keys: List[str]) -> List[Optional[str]]:
        safe_keys = self._tks(keys)
        values = self.redis_client.mget(safe_keys)
        return [v.decode('utf-8') if v else None for v in values]

    def save_string(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        safe_key = self._tk(key)
        if value is not None:
            return bool(self.redis_client.set(safe_key, value, ex=expire))
        return False

    def save_string_if_not_exists(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        safe_key = self._tk(key)
        if value is not None:
            return bool(self.redis_client.set(safe_key, value, ex=expire, nx=True))
        return False

    # Set Operations
    def get_set(self, key: str) -> set:
        safe_key = self._tk(key)
        members = self.redis_client.smembers(safe_key)
        return {m.decode('utf-8') for m in members}

    def save_set(self, key: str, value: set, expire: Optional[int] = None, overwrite: bool = False) -> bool:
        safe_key = self._tk(key)
        if len(value) > 0:
            if overwrite:
                self.redis_client.delete(safe_key)
            result = self.redis_client.sadd(safe_key, *value)
            if expire is not None:
                self.redis_client.expire(safe_key, expire)
            return bool(result)
        return False

    def remove_from_set(self, key: str, value: str) -> bool:
        safe_key = self._tk(key)
        return bool(self.redis_client.srem(safe_key, value))

    def is_member_of_set(self, key: str, value: str) -> bool:
        safe_key = self._tk(key)
        return bool(self.redis_client.sismember(safe_key, value))

    # Sorted Set Operations
    def get_sorted_set(self, key: str, start: int = 0, end: int = -1, withscores: bool = False):
        safe_key = self._tk(key)
        results = self.redis_client.zrevrange(safe_key, start, end, withscores=withscores)
        if withscores:
            return [(item[0].decode('utf-8'), item[1]) for item in results]
        return [item.decode('utf-8') for item in results]

    def get_sorted_set_by_score(self, key: str, min_score: int = 0, max_score: int = -1, withscores: bool = False):
        safe_key = self._tk(key)
        results = self.redis_client.zrevrangebyscore(safe_key, max_score, min_score, withscores=withscores)
        if withscores:
            return [(item[0].decode('utf-8'), item[1]) for item in results]
        return [item.decode('utf-8') for item in results]

    def save_sorted_set(self, key: str, values: Dict[str, float], expire: Optional[int] = None, overwrite: bool = False):
        safe_key = self._tk(key)
        if overwrite:
            self.redis_client.delete(safe_key)
        for value, score in values.items():
            self.redis_client.zadd(safe_key, {value: score}, incr=True)
        if expire is not None:
            self.redis_client.expire(safe_key, expire)

    # List Operation
    def save_list(self, key: str, values: list, expire: Optional[int] = None, overwrite: bool = False):
        safe_key = self._tk(key)
        if overwrite:
            self.redis_client.delete(safe_key)
        self.redis_client.rpush(safe_key, *values)
        if expire is not None:
            self.redis_client.expire(safe_key, expire)

    def get_list(self, key: str) -> List[str]:
        safe_key = self._tk(key)
        values = self.redis_client.lrange(safe_key, 0, -1)
        return [v.decode('utf-8') for v in values]

    # Hash Operations
    def save_hset(self, key: str, field: str, value: str, expire: Optional[int] = None):
        safe_key = self._tk(key)
        self.redis_client.hset(safe_key, field, value)
        if expire is not None:
            self.redis_client.expire(safe_key, expire)

    def save_hset_bulk(self, key: str, mapping: dict, expire: Optional[int] = None):
        safe_key = self._tk(key)
        self.redis_client.hset(safe_key, mapping=mapping)
        if expire is not None:
            self.redis_client.expire(safe_key, expire)

    def get_hset(self, key: str, field: str) -> Optional[str]:
        safe_key = self._tk(key)
        value = self.redis_client.hget(safe_key, field)
        return value.decode('utf-8') if value else None

    def get_hset_bulk(self, key: str, fields: list) -> List[Optional[str]]:
        safe_key = self._tk(key)
        values = self.redis_client.hmget(safe_key, fields)
        return [v.decode('utf-8') if v else None for v in values]

    def get_hmset(self, key: str) -> Dict[str, str]:
        safe_key = self._tk(key)
        result = self.redis_client.hgetall(safe_key)
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in result.items()}

    def del_hmset_field(self, key: str, field: str):
        safe_key = self._tk(key)
        self.redis_client.hdel(safe_key, field)

    def del_hmset_fields(self, key: str, fields: list):
        safe_key = self._tk(key)
        self.redis_client.hdel(safe_key, *fields)

    # Bulk Operations
    def save_strings(self, actions: List[BulkRedisAction]):
        with self.redis_client.pipeline() as pipe:
            expiry_time = {}
            for action in actions:
                safe_key = self._tk(action.key)
                if action.action_type == BulkRedisActionType.SET_STRING:
                    pipe.set(safe_key, action.value, ex=action.expire)
                elif action.action_type == BulkRedisActionType.DELETE_STRING:
                    pipe.delete(safe_key)
                elif action.action_type == BulkRedisActionType.DELETE_FROM_SET:
                    pipe.srem(safe_key, *action.values)
                elif action.action_type == BulkRedisActionType.ADD_TO_SET:
                    pipe.sadd(safe_key, *action.values)
                    if action.expire is not None:
                        expiry_time[safe_key] = action.expire
                elif action.action_type == BulkRedisActionType.SAVE_SORTED_SET:
                    if action.overwrite:
                        pipe.delete(safe_key)
                    for value, score in action.values.items():
                        pipe.zadd(safe_key, {value: score}, incr=True)
                    if action.expire is not None:
                        expiry_time[safe_key] = action.expire

            for k, v in expiry_time.items():
                pipe.expire(k, v)

            return pipe.execute()

    # Key Operations
    def delete_key(self, key: str):
        safe_key = self._tk(key)
        return self.redis_client.delete(safe_key)

    def delete_keys(self, matches: str):
        """Delete all keys matching a pattern"""
        safe_matches = self._tk(matches)
        cursor = '0'
        while cursor != 0:
            cursor, keys = self.redis_client.scan(cursor=cursor, match=safe_matches, count=5000)
            if keys:
                self.redis_client.delete(*keys)

    def exists(self, key: str) -> bool:
        safe_key = self._tk(key)
        return bool(self.redis_client.exists(safe_key))

    def rename_key(self, old_key: str, new_key: str):
        safe_old_key = self._tk(old_key)
        safe_new_key = self._tk(new_key)
        self.redis_client.rename(safe_old_key, safe_new_key)

    def update_ttl(self, key: str, expire: int):
        safe_key = self._tk(key)
        self.redis_client.expire(safe_key, expire)

    def get_ttl(self, key: str) -> Optional[int]:
        safe_key = self._tk(key)
        ttl = self.redis_client.ttl(safe_key)
        return None if ttl == -1 else ttl

    # Lock Operations
    def get_lock(self, key: str, timeout: Optional[float] = None):
        safe_key = self._tk(key)
        return self.redis_client.lock(safe_key, timeout=timeout)

    # Set Operations
    def zunionstore(self, destination: str, keys: list, aggregate: Optional[str] = None):
        safe_keys = self._tks(keys)
        self.redis_client.zunionstore(destination, safe_keys, aggregate=aggregate)

    def get_set_length(self, key: str) -> int:
        safe_key = self._tk(key)
        return self.redis_client.hlen(safe_key)