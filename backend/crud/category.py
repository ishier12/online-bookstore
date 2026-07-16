"""
分类数据访问模块
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.category import Category


async def get_category_tree(db: AsyncSession) -> list[Category]:
    """
    获取完整分类树（两级）
    - 查所有顶级分类（parent_id IS NULL）
    - 预加载 children（避免 N+1）
    - 业务逻辑限制最多两级
    """
    result = await db.execute(
        select(Category)
        .where(Category.parent_id.is_(None))
        .options(selectinload(Category.children))
        .order_by(Category.id)
    )
    return list(result.scalars().all())
