"""
书评路由模块
GET  /api/v1/books/{book_id}/reviews   某书的书评列表（分页）
POST /api/v1/books/{book_id}/reviews   写书评（需登录，每人每书限一条）
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from config.db import get_database
from crud.review import (
    get_reviews_for_book,
    create_review,
    get_user_review_for_book,
)
from schemas.review import ReviewCreate, ReviewResponse
from utils.response import success_response, created_response, paginated_response
from middleware.auth import get_current_user, get_optional_user
from models.user import User

router = APIRouter(prefix="/api/v1/books", tags=["书评"])


@router.get("/{book_id}/reviews")
async def list_reviews(
    book_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
    db: AsyncSession = Depends(get_database),
):
    """获取某书的书评列表（含用户名，按时间倒序）"""
    reviews, total = await get_reviews_for_book(db, book_id, page, page_size)

    items = []
    for r in reviews:
        data = ReviewResponse.model_validate(r).model_dump()
        data["username"] = r.user.username if r.user else "匿名"
        items.append(data)

    return paginated_response(items, total, page, page_size)


@router.post("/{book_id}/reviews", status_code=201)
async def create_new_review(
    book_id: int,
    data: ReviewCreate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    写书评（需登录）
    - 每人每书限一条，重复提交返回 409
    - rating 范围 1~5（Pydantic 层已校验）
    """
    # 检查是否已评价
    existing = await get_user_review_for_book(db, current_user.id, book_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="你已经评价过这本书了，每人每书限一条书评",
        )

    # 检查书籍是否存在
    from crud.book import get_book_by_id
    book = await get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="书籍不存在")

    try:
        review = await create_review(db, current_user.id, book_id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="你已经评价过这本书了",
        )

    result = ReviewResponse.model_validate(review).model_dump()
    result["username"] = current_user.username

    return created_response(result, message="书评发表成功")
