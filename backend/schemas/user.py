"""
用户 Schema 模块
定义用户相关 API 的请求/响应数据格式
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., min_length=5, max_length=100, description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserLogin(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=100, description="用户名或邮箱")
    password: str = Field(..., min_length=1, max_length=128, description="密码")


class UserResponse(BaseModel):
    """用户信息响应（不含密码）"""
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """登录/刷新后返回的 Token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
