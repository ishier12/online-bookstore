"""
Redis 缓存工具函数
"""

import json
from typing import Optional
from redis.asyncio import Redis


async def get_cache(redis: Redis, key: str) -> Optional[str]:
    """从 Redis 获取缓存"""
    if redis is None:
        return None
    return await redis.get(key)


async def set_cache(redis: Redis, key: str, value: str, ttl: int = 60):
    """写入 Redis 缓存（带过期时间，单位秒）"""
    if redis is None:
        return
    await redis.set(key, value, ex=ttl)


async def delete_cache(redis: Redis, pattern: str):
    """按通配符模式删除缓存（如 book:*）"""
    if redis is None:
        return
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)


def build_cache_key(prefix: str, *args) -> str:
    """生成缓存键，如 book:1 或 books:list:page=1_size=4"""
    parts = [prefix]
    parts.extend(str(a) for a in args)
    return ":".join(parts)
