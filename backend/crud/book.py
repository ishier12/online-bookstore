"""
书籍数据访问模块
所有查询在 session 内完成 eager loading，返回 ORM 对象供 Router 用 model_validate 转换
"""

from typing import Optional
from sqlalchemy import select, func
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

    搜索策略（三阶段演进）：
      阶段一 — LIKE '%keyword%'（全表扫描）   ← 当前
      阶段二 — FULLTEXT 索引（倒排索引）
      阶段三 — Elasticsearch（专用搜索引擎）
    """
    conditions = []

    # 阶段一：LIKE 模糊匹配
    if keyword and keyword.strip():
        kw = f"%{keyword.strip()}%"
        conditions.append(
            (Book.book_name.like(kw)) |
            (Book.author.like(kw)) |
            (Book.description.like(kw))
        )

    # 分类筛选（父分类自动包含子分类）
    if category_id is not None:
        children_ids = (await db.execute(
            select(Category.id).where(Category.parent_id == category_id)
        )).scalars().all()
        filter_ids = [category_id] + list(children_ids) if children_ids else [category_id]
        conditions.append(
            Book.id.in_(
                select(book_category.c.book_id).where(
                    book_category.c.category_id.in_(filter_ids)
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

    # 排序
    sort_map = {
        "created_at_desc": Book.created_at.desc(),
        "price_asc": Book.price.asc(),
        "price_desc": Book.price.desc(),
        "title_asc": Book.book_name.asc(),
    }
    order_by = sort_map.get(sort, Book.created_at.desc())

    # 总数
    count_query = select(func.count()).select_from(Book)
    if conditions:
        count_query = count_query.where(*conditions)
    total = (await db.execute(count_query)).scalar()

    # 分页数据 — joinedload 预加载 publisher，避免 Router model_validate 时 N+1 懒加载
    offset = (page - 1) * page_size
    data_query = (
        select(Book)
        .options(joinedload(Book.publisher))
        .order_by(order_by)
        .offset(offset)
        .limit(page_size)
    )
    if conditions:
        data_query = data_query.where(*conditions)

    result = await db.execute(data_query)
    return list(result.scalars().all()), total


async def get_book_by_id(db: AsyncSession, book_id: int) -> Optional[Book]:
    """根据 ID 获取 ORM 对象（用于内部检查）"""
    return await db.get(Book, book_id)


async def get_book_with_relations(db: AsyncSession, book_id: int) -> Optional[Book]:
    """
    获取书籍详情 — 预加载 publisher + categories，确保 Router model_validate 不触发懒加载
    """
    result = await db.execute(
        select(Book)
        .where(Book.id == book_id)
        .options(
            joinedload(Book.publisher),     # 预加载出版社
            selectinload(Book.categories),   # 预加载分类（详情页用 flat dict，不触发 children）
        )
    )
    return result.scalar_one_or_none()


async def create_book(db: AsyncSession, book_data) -> Book:
    """新增书籍"""
    data = book_data.model_dump()
    category_ids = data.pop("category_ids", [])

    book = Book(**data)
    if category_ids:
        categories = await db.execute(
            select(Category).where(Category.id.in_(category_ids))
        )
        book.categories = list(categories.scalars().all())

    db.add(book)
    await db.flush()
    # refresh 加载服务端默认值（created_at），避免 Router model_validate 时 MissingGreenlet
    await db.refresh(book)
    return book


async def update_book(db: AsyncSession, book_id: int, book_data) -> Optional[Book]:
    """
    部分更新书籍（PATCH — 只更新传了的字段）
    BookUpdate 所有字段 Optional，配合 exclude_unset=True 实现 PATCH 语义
    """
    book = await db.get(Book, book_id)
    if book is None:
        return None

    update_dict = book_data.model_dump(exclude_unset=True)
    category_ids = update_dict.pop("category_ids", None)

    for field, value in update_dict.items():
        setattr(book, field, value)

    if category_ids is not None:
        categories = await db.execute(
            select(Category).where(Category.id.in_(category_ids))
        )
        book.categories = list(categories.scalars().all())

    await db.flush()
    await db.refresh(book)
    return book


async def delete_book(db: AsyncSession, book_id: int) -> Optional[Book]:
    """删除书籍"""
    book = await db.get(Book, book_id)
    if book is None:
        return None
    await db.delete(book)
    await db.flush()
    return book
