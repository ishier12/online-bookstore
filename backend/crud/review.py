"""
书评数据访问模块
"""

from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from models.review import Review
from schemas.review import ReviewCreate


async def get_reviews_for_book(
    db: AsyncSession, book_id: int, page: int = 1, page_size: int = 10
) -> tuple[list[Review], int]:
    """获取某书的书评列表（含用户信息，按时间倒序）"""
    # 总数
    count_query = select(func.count(Review.id)).where(Review.book_id == book_id)
    total = (await db.execute(count_query)).scalar()

    # 分页查询（JOIN 用户表获取用户名）
    offset = (page - 1) * page_size
    query = (
        select(Review)
        .where(Review.book_id == book_id)
        .options(joinedload(Review.user))
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_review(db: AsyncSession, user_id: int, book_id: int, data: ReviewCreate) -> Review:
    """创建书评"""
    review = Review(
        user_id=user_id,
        book_id=book_id,
        rating=data.rating,
        content=data.content,
    )
    db.add(review)
    await db.flush()
    return review


async def get_user_review_for_book(
    db: AsyncSession, user_id: int, book_id: int
) -> Optional[Review]:
    """检查用户是否已评价过某书"""
    result = await db.execute(
        select(Review).where(
            Review.user_id == user_id,
            Review.book_id == book_id,
        )
    )
    return result.scalar_one_or_none()


async def get_book_avg_rating(db: AsyncSession, book_id: int) -> tuple[Optional[float], int]:
    """获取某书的平均评分和评论总数（不缓存，实时计算）"""
    result = await db.execute(
        select(
            func.avg(Review.rating).label("avg"),
            func.count(Review.id).label("cnt"),
        ).where(Review.book_id == book_id)
    )
    row = result.one()
    avg = round(float(row.avg), 1) if row.avg else None
    count = row.cnt
    return avg, count
