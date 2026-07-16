"""
用户模型模块
定义 User 表对应的 ORM 模型类
"""

from sqlalchemy import String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from config.db_conf import Base


class User(Base):
    """用户表"""
    __tablename__ = "user"
    __table_args__ = (
        Index("uk_username", "username", unique=True),
        Index("uk_email", "email", unique=True),
        {"comment": "用户表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="用户名（登录用）"
    )
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="邮箱"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="bcrypt 哈希后的密码"
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="显示昵称"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="头像URL"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="是否启用（软删除标识）"
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否管理员（后续管理后台用）"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后登录时间"
    )
    # created_at / updated_at 继承自 Base
