"""
出版社模型模块
定义 Publisher 表 — Book 的 1:N 关系中的「1」端
一个出版社可以出版多本书
"""

from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from config.db_conf import Base

if TYPE_CHECKING:
    from models.book import Book


class Publisher(Base):
    """出版社表"""
    __tablename__ = "publisher"
    __table_args__ = (
        Index("uk_name", "name", unique=True),
        {"comment": "出版社表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="出版社ID")
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="出版社名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="出版社简介"
    )

    # ====== 关系 ======
    # 1:N → Book（一个出版社有多本书）
    books: Mapped[List["Book"]] = relationship(
        "Book", back_populates="publisher", lazy="selectin"
    )
    # created_at / updated_at 继承自 Base
