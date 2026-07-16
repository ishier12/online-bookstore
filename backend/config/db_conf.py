"""
数据库配置模块
功能：
  - 创建异步数据库引擎（连接池）
  - 定义 ORM 基类（所有模型类都继承它，自动包含 created_at / updated_at）

配置来源：
  - 优先读取环境变量（docker-compose 注入或 .env 文件）
  - 默认值用于本地快速开发
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
from config.settings import settings

# 创建异步引擎
# echo=True → 终端打印所有 SQL 语句（开发调试用，生产环境通过 DB_ECHO=false 关闭）
# pool_size=10 → 连接池默认连接数
# max_overflow=20 → 连接池超出后的最大额外连接数
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=10,
    max_overflow=20,
)

# 创建 Session 工厂（每次请求通过 get_database() 依赖获取新的 Session）
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不使对象过期，避免懒加载时重复查询
)


class Base(DeclarativeBase):
    """ORM 基类 — 所有模型继承此类，自动获得 created_at / updated_at 字段"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="修改时间"
    )
