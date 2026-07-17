"""
出版社路由模块
GET /api/v1/publishers         出版社列表（只读）
GET /api/v1/publishers/{id}/books  某出版社的书籍
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_database
from crud.publisher import get_publishers
from crud.book import get_books
from schemas.publisher import PublisherResponse
from schemas.book import BookResponse
from utils.response import success_response, paginated_response

router = APIRouter(prefix="/api/v1/publishers", tags=["出版社"])


@router.get("/")
async def list_publishers(db: AsyncSession = Depends(get_database)):
    """出版社列表"""
    publishers = await get_publishers(db)
    return success_response([
        PublisherResponse.model_validate(p).model_dump() for p in publishers
    ])


@router.get("/{publisher_id}/books")
async def list_publisher_books(
    publisher_id: int,
    db: AsyncSession = Depends(get_database),
    sort: str = Query("created_at_desc", description="排序方式"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=50, description="每页条数"),
):
    """某出版社的书籍列表（支持排序和分页）"""
    books, total = await get_books(
        db, publisher_id=publisher_id, sort=sort, page=page, page_size=page_size
    )
    items = []
    for b in books:
        item = BookResponse.model_validate(b).model_dump()
        item["publisher_name"] = b.publisher.name if b.publisher else None
        items.append(item)
    return paginated_response(items, total, page, page_size)
