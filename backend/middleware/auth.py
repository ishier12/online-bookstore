"""
认证依赖模块
提供 FastAPI 依赖注入：
- get_current_user：必须登录，否则返回 401
- get_optional_user：可选登录，未登录时 user=None（用于「登录后显示额外信息」的场景）
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_database
from crud.user import get_user_by_id
from utils.security import decode_token

# HTTP Bearer Token 提取器（从 Authorization 头中提取 Token 字符串）
security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_database),
):
    """
    从请求的 Authorization 头中提取 JWT，解码后查询用户信息
    - Token 无效或过期 → 401
    - 用户不存在或已禁用 → 401
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )

    # 确保是 access token（防止用 refresh token 来鉴权）
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请使用 Access Token 进行鉴权",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 中缺少用户标识",
        )

    user = await get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用",
        )

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_database),
):
    """
    可选认证：用户可以不登录访问
    - 登录了且 Token 有效 → 返回 User 对象
    - 未登录或 Token 无效 → 返回 None
    用于书籍详情页等场景：未登录也能看，登录后显示「你是否已评价」
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    user = await get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        return None

    return user
