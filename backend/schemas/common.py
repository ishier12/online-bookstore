"""
通用 Schema 模块
定义 API 响应的通用包装类型（供 OpenAPI 文档生成用）
"""

from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """统一成功响应"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PaginatedData(BaseModel, Generic[T]):
    """分页数据结构"""
    items: list[T]
    total: int
    page: int
    page_size: int


class ErrorDetail(BaseModel):
    """校验错误详情"""
    field: str
    message: str


class ValidationErrorData(BaseModel):
    """422 校验错误数据"""
    errors: list[ErrorDetail]
