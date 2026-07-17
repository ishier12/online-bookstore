"""
分类路由模块
GET /api/v1/categories  分类树（两级，结果缓存 600s）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_database
from crud.category import get_category_tree
from utils.response import success_response

router = APIRouter(prefix="/api/v1/categories", tags=["分类"])


@router.get("/")
async def list_categories(db: AsyncSession = Depends(get_database)):
    """获取分类树（两级层级，预加载 children）"""
    categories = await get_category_tree(db)

    # 手动构建树形结构，避免 Pydantic model_validate 触发 children 懒加载
    tree = []
    for cat in categories:
        children = []
        # cat.children 已被 selectinload 预加载，直接访问不会触发懒加载
        for child in cat.children:
            # 手动构建子分类 dict，不访问 child.children 避免懒加载
            children.append({
                "id": child.id,
                "name": child.name,
                "parent_id": child.parent_id,
                "children": [],  # 子分类的 children 永远为空（最多两级）
            })
        tree.append({
            "id": cat.id,
            "name": cat.name,
            "parent_id": cat.parent_id,
            "children": children,
        })

    return success_response(tree)
