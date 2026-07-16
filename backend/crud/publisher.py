"""
出版社数据访问模块
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.publisher import Publisher


async def get_publishers(db: AsyncSession) -> list[Publisher]:
    """获取所有出版社"""
    result = await db.execute(select(Publisher).order_by(Publisher.id))
    return list(result.scalars().all())
