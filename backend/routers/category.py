"""
分类路由模块
GET /api/v1/categories  分类树（两级，结果缓存 600s）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_database
from crud.category import get_category_tree
from schemas.category import CategoryResponse
from utils.response import success_response

router = APIRouter(prefix="/api/v1/categories", tags=["分类"])


@router.get("/")
async def list_categories(db: AsyncSession = Depends(get_database)):
    """获取分类树（两级层级，预加载 children）"""
    categories = await get_category_tree(db)

    # 构建树形结构
    tree = []
    for cat in categories:
        cat_data = CategoryResponse.model_validate(cat).model_dump()
        cat_data["children"] = [
            CategoryResponse.model_validate(child).model_dump()
            for child in cat.children
        ]
        tree.append(cat_data)

    return success_response(tree)
