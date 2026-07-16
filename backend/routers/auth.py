"""
认证路由模块
POST /api/v1/auth/register    注册
POST /api/v1/auth/login       登录
POST /api/v1/auth/refresh     刷新 Access Token
GET  /api/v1/auth/me          当前用户信息
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update as sql_update
from datetime import datetime

from config.db import get_database
from schemas.user import UserRegister, UserLogin, UserResponse
from crud.user import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_username_or_email,
    get_user_by_id,
)
from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from utils.response import success_response, created_response
from middleware.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register", status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_database)):
    """注册新用户 — 注册成功后自动登录，返回双 Token"""
    # 检查冲突
    if await get_user_by_username(db, data.username):
        raise HTTPException(status_code=409, detail="用户名已存在")
    if await get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="邮箱已被注册")

    # 创建用户
    user = await create_user(db, data, hash_password(data.password))

    # 自动登录：生成 Token
    token_sub = {"sub": str(user.id)}
    return created_response({
        "access_token": create_access_token(token_sub),
        "refresh_token": create_refresh_token(token_sub),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(),
    })


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_database)):
    """登录 — 支持用户名或邮箱 + 密码"""
    user = await get_user_by_username_or_email(db, data.username)
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 更新最后登录时间
    await db.execute(
        sql_update(User).where(User.id == user.id).values(last_login_at=datetime.utcnow())
    )

    # 生成双 Token
    token_sub = {"sub": str(user.id)}
    return success_response({
        "access_token": create_access_token(token_sub),
        "refresh_token": create_refresh_token(token_sub),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(),
    }, message="登录成功")


@router.post("/refresh")
async def refresh(data: dict, db: AsyncSession = Depends(get_database)):
    """
    用 Refresh Token 换取新 Access Token
    请求体：{ "refresh_token": "eyJ..." }
    """
    token_str = data.get("refresh_token")
    if not token_str:
        raise HTTPException(status_code=400, detail="缺少 refresh_token")

    payload = decode_token(token_str)
    if payload is None:
        raise HTTPException(status_code=401, detail="Refresh Token 无效或已过期")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="请使用 Refresh Token 刷新")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token 无效")

    # 验证用户仍然存在
    user = await get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")

    return success_response({
        "access_token": create_access_token({"sub": str(user.id)}),
        "token_type": "bearer",
    }, message="Token 刷新成功")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return success_response(
        UserResponse.model_validate(current_user).model_dump()
    )
