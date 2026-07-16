"""
书评 Schema 模块
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewCreate(BaseModel):
    """写书评请求"""
    rating: int = Field(..., ge=1, le=5, description="评分 1~5")
    content: Optional[str] = Field(None, max_length=2000, description="评价内容")


class ReviewResponse(BaseModel):
    """书评信息"""
    id: int
    user_id: int
    book_id: int
    rating: int
    content: Optional[str] = None
    username: str = ""       # 由路由层额外填充
    created_at: datetime

    model_config = {"from_attributes": True}
