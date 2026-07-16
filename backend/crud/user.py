"""
用户数据访问模块
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from schemas.user import UserRegister


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根据 ID 获取用户"""
    return await db.get(User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username_or_email(db: AsyncSession, login: str) -> Optional[User]:
    """根据用户名或邮箱获取用户（登录时用）"""
    result = await db.execute(
        select(User).where(
            (User.username == login) | (User.email == login)
        )
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserRegister, hashed_password: str) -> User:
    """创建新用户"""
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_password,
        nickname=data.nickname,
    )
    db.add(user)
    await db.flush()
    return user
