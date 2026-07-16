"""
分类 Schema 模块
支持两级树形结构：顶级分类包含 children 子分类列表
"""

from pydantic import BaseModel
from typing import Optional


class CategoryResponse(BaseModel):
    """分类信息（树形）"""
    id: int
    name: str
    parent_id: Optional[int] = None
    children: list["CategoryResponse"] = []

    model_config = {"from_attributes": True}
