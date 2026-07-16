"""
出版社 Schema 模块
"""

from pydantic import BaseModel
from datetime import datetime


class PublisherResponse(BaseModel):
    """出版社信息"""
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
