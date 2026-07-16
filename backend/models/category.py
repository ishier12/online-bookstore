"""
分类模型模块
定义 Category 表 — Book 的 M:N 关系中的一端
- 自引用 parent_id 实现两级分类（parent_id = NULL 表示顶级分类）
- 通过 book_category 中间表与 Book 建立 M:N 关系
"""

from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from config.db_conf import Base

if TYPE_CHECKING:
    from models.book import Book


class Category(Base):
    """分类表（自引用，支持两级层级）"""
    __tablename__ = "category"
    __table_args__ = (
        Index("idx_parent_id", "parent_id"),
        {"comment": "书籍分类表（两级层级：顶级 → 子分类）"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="分类名称"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"),
        nullable=True,
        comment="父分类ID（NULL=顶级分类）",
    )

    # ====== 自引用关系 ======
    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side="Category.id", back_populates="children"
    )
    children: Mapped[List["Category"]] = relationship(
        "Category", back_populates="parent", lazy="selectin"
    )

    # ====== M:N → Book ======
    books: Mapped[List["Book"]] = relationship(
        "Book",
        secondary="book_category",
        back_populates="categories",
        lazy="selectin",
    )
    # created_at / updated_at 继承自 Base
