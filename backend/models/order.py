"""
🔲 [第二期] 订单模型模块
定义 Order + OrderItem 表
User 1:N Order（一个用户可以有多个订单）
Order 1:N OrderItem（一个订单包含多个商品明细）
"""

import enum
from sqlalchemy import String, ForeignKey, Integer, DECIMAL, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from typing import List, TYPE_CHECKING
from config.db_conf import Base

if TYPE_CHECKING:
    from models.user import User
    from models.book import Book
    from models.address import Address


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"          # 待支付
    PAID = "paid"                # 已支付
    SHIPPED = "shipped"          # 已发货
    DELIVERED = "delivered"      # 已签收
    CANCELLED = "cancelled"      # 已取消


class Order(Base):
    """订单表（第二期）"""
    __tablename__ = "order"
    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
        Index("idx_status", "status"),
        {"comment": "订单表（第二期）"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="订单ID")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, comment="下单用户ID"
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey("address.id"), nullable=False, comment="收货地址ID（地址快照）"
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING, comment="订单状态"
    )
    total_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 2), nullable=False, comment="订单总金额"
    )

    # 关系
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )
    # created_at / updated_at 继承自 Base


class OrderItem(Base):
    """订单明细表（第二期）"""
    __tablename__ = "order_item"
    __table_args__ = (
        Index("fk_order_id", "order_id"),
        {"comment": "订单明细表（第二期）"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="明细ID")
    order_id: Mapped[int] = mapped_column(
        ForeignKey("order.id", ondelete="CASCADE"), nullable=False, comment="订单ID"
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id"), nullable=False, comment="书籍ID"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="购买数量"
    )
    price: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="购买时单价（价格快照）"
    )

    # 关系
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    book: Mapped["Book"] = relationship("Book")
    # created_at / updated_at 继承自 Base
