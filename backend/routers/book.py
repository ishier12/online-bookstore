"""
书籍路由模块
RESTful API — 所有端点前缀 /api/v1/books
CRUD 层负责 eager loading（joinedload/selectinload/refresh），确保 ORM 属性已加载
Router 层用 model_validate 安全转换 ORM→Pydantic
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_database
from middleware.auth import get_current_user
from config.redis import get_redis
from crud.book import (
    get_books, get_book_with_relations, create_book, update_book, delete_book,
)
from crud.review import get_book_avg_rating
from schemas.book import BookCreate, BookUpdate, BookResponse, BookDetailResponse
from schemas.publisher import PublisherResponse
from utils.cache import get_cache, set_cache, delete_cache, build_cache_key
from utils.response import success_response, created_response, paginated_response

router = APIRouter(prefix="/api/v1/books", tags=["书籍"])

CACHE_TTL = 300


@router.get("/")
async def read_books(
    db: AsyncSession = Depends(get_database),
    keyword: Optional[str] = Query(None, description="搜索关键字（书名/作者/简介）"),
    category_id: Optional[int] = Query(None, description="分类ID筛选"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
    sort: str = Query("created_at_desc", description="排序"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=50, description="每页条数"),
):
    """书籍列表 — 搜索结果缓存 300s"""
    redis = get_redis()
    cache_key = build_cache_key(
        "books:list", keyword, category_id, min_price, max_price, sort, page, page_size
    )

    cached = await get_cache(redis, cache_key)
    if cached:
        return JSONResponse(content=json.loads(cached), headers={"X-Cache": "HIT"})

    items, total = await get_books(
        db, keyword=keyword, category_id=category_id,
        min_price=min_price, max_price=max_price,
        sort=sort, page=page, page_size=page_size,
    )

    result = paginated_response(items, total, page, page_size)
    # jsonable_encoder 处理 Decimal → json 兼容类型（Python 标准 json.dumps 不认识 Decimal）
    serializable = jsonable_encoder(result)
    await set_cache(redis, cache_key, json.dumps(serializable), ttl=CACHE_TTL)
    return JSONResponse(content=serializable, headers={"X-Cache": "MISS"})


@router.get("/{book_id}")
async def get_book(book_id: int, db: AsyncSession = Depends(get_database)):
    """书籍详情 — 含出版社、分类、均分、评论数，缓存 300s"""
    redis = get_redis()
    cache_key = build_cache_key("book", book_id)

    cached = await get_cache(redis, cache_key)
    if cached:
        return JSONResponse(content=json.loads(cached), headers={"X-Cache": "HIT"})

    # publisher + categories 已通过 joinedload/selectinload 预加载
    # categories 使用 CategoryTag（无 children），model_validate 不触发懒加载
    book = await get_book_with_relations(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="书籍不存在")

    avg_rating, review_count = await get_book_avg_rating(db, book_id)

    result = BookDetailResponse.model_validate(book).model_dump()
    result["publisher"] = (
        PublisherResponse.model_validate(book.publisher).model_dump()
        if book.publisher else None
    )
    result["avg_rating"] = avg_rating
    result["review_count"] = review_count

    response_data = success_response(result)
    serializable = jsonable_encoder(response_data)
    await set_cache(redis, cache_key, json.dumps(serializable), ttl=CACHE_TTL)
    return JSONResponse(content=serializable, headers={"X-Cache": "MISS"})


@router.post("/", status_code=201)
async def create_new_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user),
):
    """新增书籍 — 淘汰列表缓存"""
    book = await create_book(db, book_data)

    redis = get_redis()
    await delete_cache(redis, "books:list*")

    return created_response(
        BookResponse.model_validate(book).model_dump(), message="书籍创建成功"
    )


@router.patch("/{book_id}")
async def update_existing_book(
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user),
):
    """
    部分更新书籍（PATCH — 只更新传了的字段）

    注意：这里用的是 PATCH 而非 PUT。
    PUT = 完整替换（客户端必须传所有字段）
    PATCH = 部分更新（客户端只传要改的字段）
    本项目的 BookUpdate 所有字段均为 Optional，语义上属于 PATCH。
    """
    book = await update_book(db, book_id, book_data)
    if book is None:
        raise HTTPException(status_code=404, detail="书籍不存在")

    redis = get_redis()
    await delete_cache(redis, build_cache_key("book", book_id))
    await delete_cache(redis, "books:list*")

    return success_response(
        BookResponse.model_validate(book).model_dump(), message="更新成功"
    )


@router.delete("/{book_id}", status_code=204)
async def delete_existing_book(
    book_id: int,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user),
):
    """
    删除书籍 — 返回 204 No Content

    注意：之前声明了 response_model=BookResponse 但又返回 Response(status_code=204)，
    二者冲突。204 表示「成功但不返回任何内容」，不应该声明 response_model。
    修复方式：去掉 response_model，装饰器中设置 status_code=204，return 留空。
    """
    book = await delete_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="书籍不存在")

    redis = get_redis()
    await delete_cache(redis, build_cache_key("book", book_id))
    await delete_cache(redis, "books:list*")

    return Response(status_code=204)
