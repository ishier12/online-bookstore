"""
🔲 [第二期] 购物车模型模块
定义 Cart + CartItem 表 — 用户和书籍之间的购物车关系
User 1:1 Cart（一个用户一个购物车）
Cart 1:N CartItem（一个购物车有多个商品项）
Book 1:N CartItem（一本书可以出现在多个购物车里）
"""

from sqlalchemy import ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from config.db_conf import Base

if TYPE_CHECKING:
    from models.user import User
    from models.book import Book


class Cart(Base):
    """购物车表（第二期）"""
    __tablename__ = "cart"
    __table_args__ = {"comment": "购物车表（第二期）"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="购物车ID")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False,
        comment="用户ID（1:1）"
    )

    # 关系
    items: Mapped[List["CartItem"]] = relationship(
        "CartItem", back_populates="cart", lazy="selectin", cascade="all, delete-orphan"
    )
    # created_at / updated_at 继承自 Base


class CartItem(Base):
    """购物车明细表（第二期）"""
    __tablename__ = "cart_item"
    __table_args__ = (
        Index("uk_cart_book", "cart_id", "book_id", unique=True),
        {"comment": "购物车明细表（第二期）"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="明细ID")
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("cart.id", ondelete="CASCADE"), nullable=False, comment="购物车ID"
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", ondelete="CASCADE"), nullable=False, comment="书籍ID"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, comment="数量"
    )

    # 关系
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    book: Mapped["Book"] = relationship("Book")
    # created_at / updated_at 继承自 Base
