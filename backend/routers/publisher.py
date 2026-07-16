"""
出版社路由模块
GET /api/v1/publishers  出版社列表（只读，结果缓存 600s）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_database
from crud.publisher import get_publishers
from schemas.publisher import PublisherResponse
from utils.response import success_response

router = APIRouter(prefix="/api/v1/publishers", tags=["出版社"])


@router.get("/")
async def list_publishers(db: AsyncSession = Depends(get_database)):
    """出版社列表"""
    publishers = await get_publishers(db)
    return success_response([
        PublisherResponse.model_validate(p).model_dump() for p in publishers
    ])
