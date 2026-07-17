"""
书籍 Schema 模块
定义 Book API 的请求/响应数据格式
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

from schemas.publisher import PublisherResponse


# 分类标签（flat，无 children） — 用于书籍详情页的分类展示
# 注意：不用 CategoryResponse 是因为它包含 children 字段会触发 ORM 懒加载
class CategoryTag(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None

    model_config = {"from_attributes": True}


# ====== 请求 ======

class BookCreate(BaseModel):
    """创建书籍请求"""
    book_name: str = Field(..., min_length=1, max_length=255, description="书名")
    author: str = Field(..., min_length=1, max_length=255, description="作者")
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="价格")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN")
    cover_url: Optional[str] = Field(None, max_length=500, description="封面图URL")
    description: Optional[str] = Field(None, description="简介")
    stock: int = Field(0, ge=0, description="库存")
    publisher_id: Optional[int] = Field(None, description="出版社ID")
    category_ids: list[int] = Field(default_factory=list, description="分类ID列表")


class BookUpdate(BaseModel):
    """
    部分更新书籍请求（PATCH — 所有字段可选，只更新传了的字段）

    注意：这是 PATCH 语义，不是 PUT。
    PUT = 完整替换资源（必须传所有字段）
    PATCH = 部分更新（只传要改的字段）
    """
    book_name: Optional[str] = Field(None, max_length=255, description="书名")
    author: Optional[str] = Field(None, max_length=255, description="作者")
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="价格")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN")
    cover_url: Optional[str] = Field(None, max_length=500, description="封面图URL")
    description: Optional[str] = Field(None, description="简介")
    stock: Optional[int] = Field(None, ge=0, description="库存")
    publisher_id: Optional[int] = Field(None, description="出版社ID")
    category_ids: Optional[list[int]] = Field(None, description="分类ID列表")


# ====== 响应 ======

class BookResponse(BaseModel):
    """书籍基础响应（列表用）"""
    id: int
    book_name: str
    author: str
    price: Decimal
    cover_url: Optional[str] = None
    stock: int
    publisher_name: Optional[str] = None    # 由路由层预填充（避免 N+1）
    created_at: datetime

    model_config = {"from_attributes": True}


class BookDetailResponse(BaseModel):
    """书籍详情响应（含出版社、分类、均分、评论数）"""
    id: int
    book_name: str
    author: str
    price: Decimal
    isbn: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    stock: int
    publisher: Optional[PublisherResponse] = None
    categories: list[CategoryTag] = []  # CategoryTag 无 children，避免懒加载
    avg_rating: Optional[float] = None
    review_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookPage(BaseModel):
    """分页查询结果"""
    items: list[BookResponse]
    total: int
    page: int
    page_size: int
