"""
Alembic 迁移环境配置
- 从 config/settings.py 读取数据库连接
- 自动发现所有 ORM 模型（导入 main.py 中注册的模型）
- 支持 async 引擎
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Alembic Config 对象
config = context.config

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ====== 导入所有模型的 Base.metadata ======
# 必须导入所有模型类，否则 Alembic 的 autogenerate 检测不到表
from config.db_conf import Base

# 导入所有模型以注册到 Base.metadata
import models.book           # Book 模型
import models.user           # User 模型
import models.publisher      # Publisher 模型
import models.category       # Category 模型
import models.review         # Review 模型
import models.cart           # Cart + CartItem（第二期）
import models.address        # Address（第二期）
import models.order          # Order + OrderItem（第二期）
import models.payment        # Payment（第二期）
import models.user_favorite  # UserFavorite（第二期）

target_metadata = Base.metadata


def get_url():
    """从项目配置中读取数据库 URL（同步版本，Alembic 需要）"""
    from config.settings import settings
    # Alembic 离线模式需要同步 URL，把 aiomysql 换成 pymysql
    # 在线模式用 async 引擎，不需要替换
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """
    离线模式：生成 SQL 脚本而不连接数据库
    用法：alembic upgrade head --sql
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """在已有连接上执行迁移"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    在线模式（async）：连接数据库执行迁移
    """
    from config.settings import settings

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    在线模式入口：检测当前是否在 async 事件循环中
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # 没有运行中的事件循环，创建一个
        asyncio.run(run_async_migrations())
    else:
        # 已经在事件循环中（如通过 uvicorn 触发），需要特殊处理
        # 实际使用中一般不在事件循环中调用 alembic
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
