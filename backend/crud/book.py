"""
书籍数据访问模块
多条件搜索（FULLTEXT 优先，LIKE 兜底）+ 分页 + 联表查询
"""

from typing import Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from models.book import Book, book_category
from models.category import Category
from models.publisher import Publisher


async def get_books(
    db: AsyncSession,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    publisher_id: Optional[int] = None,

    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: str = "created_at_desc",
    page: int = 1,
    page_size: int = 12,
) -> tuple[list[Book], int]:
    """
    多条件搜索书籍（支持分页）

    搜索策略（三阶段演进 — 便于对比学习）：
      阶段一 — LIKE '%keyword%'（全表扫描，慢）
      阶段二 — FULLTEXT 索引（倒排索引，快）
      阶段三 — Elasticsearch（专用搜索引擎，更多能力）
      当前使用阶段二

    参数：
      keyword      — 搜索关键字（匹配书名、作者、描述）
      category_id  — 分类筛选（M:N 关联）
      min_price    — 最低价格
      max_price    — 最高价格
      sort         — 排序：created_at_desc（默认）/ price_asc / price_desc / title_asc
    """
    conditions = []

    # 关键字搜索（阶段一：LIKE 模糊匹配）
    # 演进路线：LIKE → FULLTEXT → Elasticsearch
    # 当前使用 LIKE，体验全表扫描；后续切换 FULLTEXT 时只需替换此段代码，API 不变
    if keyword and keyword.strip():
        kw = f"%{keyword.strip()}%"
        conditions.append(
            (Book.book_name.like(kw)) |
            (Book.author.like(kw)) |
            (Book.description.like(kw))
        )

    # 分类筛选（通过 M:N 中间表）
    if category_id is not None:
        conditions.append(
            Book.id.in_(
                select(book_category.c.book_id).where(
                    book_category.c.category_id == category_id
                )
            )
        )
    # 出版社筛选
    if publisher_id is not None:
        conditions.append(Book.publisher_id == publisher_id)

    # 价格范围
    if min_price is not None:
        conditions.append(Book.price >= min_price)
    if max_price is not None:
        conditions.append(Book.price <= max_price)

    # 排序映射
    sort_map = {
        "created_at_desc": Book.created_at.desc(),
        "price_asc": Book.price.asc(),
        "price_desc": Book.price.desc(),
        "title_asc": Book.book_name.asc(),
    }
    order_by = sort_map.get(sort, Book.created_at.desc())

    # 基础查询（预加载出版社，避免列表页 N+1）
    base_query = select(Book).options(joinedload(Book.publisher))

    # 总数查询
    count_query = select(func.count()).select_from(Book)
    if conditions:
        count_query = count_query.where(*conditions)
    total = (await db.execute(count_query)).scalar()

    # 分页数据查询
    offset = (page - 1) * page_size
    data_query = base_query
    if conditions:
        data_query = data_query.where(*conditions)
    data_query = data_query.order_by(order_by).offset(offset).limit(page_size)

    result = await db.execute(data_query)
    return list(result.scalars().all()), total


async def get_book_by_id(db: AsyncSession, book_id: int) -> Optional[Book]:
    """根据 ID 获取单本书"""
    return await db.get(Book, book_id)


async def get_book_with_relations(db: AsyncSession, book_id: int) -> Optional[Book]:
    """获取书籍详情（含出版社、分类）"""
    result = await db.execute(
        select(Book)
        .where(Book.id == book_id)
        .options(
            joinedload(Book.publisher),
            selectinload(Book.categories).selectinload(Category.children),
        )
    )
    return result.scalar_one_or_none()


async def create_book(db: AsyncSession, book_data) -> Book:
    """新增书籍"""
    data = book_data.model_dump()
    category_ids = data.pop("category_ids", [])

    book = Book(**data)
    # 关联分类
    if category_ids:
        from models.category import Category
        categories = await db.execute(
            select(Category).where(Category.id.in_(category_ids))
        )
        book.categories = list(categories.scalars().all())

    db.add(book)
    await db.flush()
    return book


async def update_book(db: AsyncSession, book_id: int, book_data) -> Optional[Book]:
    """
    部分更新书籍（PATCH — 只更新传了的字段）
    从 BookUpdate (所有字段 Optional) 用 exclude_unset=True 实现
    """
    book = await db.get(Book, book_id)
    if book is None:
        return None

    update_dict = book_data.model_dump(exclude_unset=True)
    category_ids = update_dict.pop("category_ids", None)

    for field, value in update_dict.items():
        setattr(book, field, value)

    # 更新分类关联
    if category_ids is not None:
        from models.category import Category
        categories = await db.execute(
            select(Category).where(Category.id.in_(category_ids))
        )
        book.categories = list(categories.scalars().all())

    await db.flush()
    return book


async def delete_book(db: AsyncSession, book_id: int) -> Optional[Book]:
    """删除书籍"""
    book = await db.get(Book, book_id)
    if book is None:
        return None
    await db.delete(book)
    await db.flush()
    return book
