"""
数据库会话依赖模块
功能：
  - 提供 FastAPI 依赖项 get_database
  - 自动管理 Session 的生命周期（创建 → 提交/回滚 → 关闭）
"""

from config.db_conf import AsyncSessionLocal


async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise  # 把异常重新抛给 FastAPI
        finally:
            await session.close()
