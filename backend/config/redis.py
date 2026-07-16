"""
Redis 连接配置模块
功能：
  - 创建异步 Redis 客户端
  - 提供 FastAPI 依赖项（在 main.py 中注入）
"""

from redis.asyncio import Redis
from config.settings import settings

REDIS_URL = settings.REDIS_URL

# 全局 Redis 客户端实例
redis_client: Redis | None = None


async def init_redis():
    """启动时创建 Redis 连接"""
    global redis_client
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
    await redis_client.ping()  # 验证连接
    return redis_client


async def close_redis():
    """关闭时释放 Redis 连接"""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None


def get_redis() -> Redis | None:
    """获取 Redis 客户端（给路由使用）"""
    return redis_client
