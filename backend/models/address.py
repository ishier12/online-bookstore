"""
🔲 [第二期] 收货地址模型模块
定义 Address 表 — User 1:N Address（一个用户可以有多个收货地址）
"""

from sqlalchemy import String, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from config.db_conf import Base

if TYPE_CHECKING:
    from models.user import User


class Address(Base):
    """收货地址表（第二期）"""
    __tablename__ = "address"
    __table_args__ = (
        Index("idx_user_default", "user_id", "is_default"),
        {"comment": "收货地址表（第二期）"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="地址ID")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="用户ID"
    )
    recipient_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="收件人姓名"
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="联系电话"
    )
    province: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="省"
    )
    city: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="市"
    )
    district: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="区"
    )
    detail: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="详细地址"
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否默认地址"
    )

    # 关系
    user: Mapped["User"] = relationship("User")
    # created_at / updated_at 继承自 Base
