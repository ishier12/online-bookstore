"""
书籍模型模块
定义 Book 表、book_category 中间表（M:N 关系）
Book 1:N ← Publisher（一本书属于一个出版社）
Book M:N ← Category（一本书可以有多个分类）
"""

from sqlalchemy import (
    String, Text, DECIMAL, Integer, ForeignKey,
    Table, Column, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from config.db_conf import Base

if TYPE_CHECKING:
    from models.publisher import Publisher
    from models.category import Category

# ====== M:N 中间表（纯 Table 对象，不创建 Model 类）======
book_category = Table(
    "book_category",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("book.id", ondelete="CASCADE"), primary_key=True, comment="书籍ID"),
    Column("category_id", Integer, ForeignKey("category.id", ondelete="CASCADE"), primary_key=True, comment="分类ID"),
    # 复合主键自动创建覆盖索引 (book_id, category_id)
    Index("idx_category_book", "category_id", "book_id"),  # 反向查询：某分类下的书
    comment="书籍-分类中间表（M:N）",
)


class Book(Base):
    """书籍表（商品）"""
    __tablename__ = "book"
    __table_args__ = (
        Index("fk_publisher_id", "publisher_id"),         # 外键索引 — JOIN publisher
        Index("idx_price", "price"),                       # 价格范围筛选
        Index("idx_created_at", "created_at"),             # 默认排序
        Index("idx_book_price", "book_name", "price"),     # 复合索引：书名= + 价格范围（最左前缀演示）
        # MySQL 全文索引 — ngram 分词器支持中文（搜索演进：LIKE → FULLTEXT → Elasticsearch）
        Index("ft_book", "book_name", "author", "description",
              mysql_prefix="FULLTEXT", mysql_with_parser="ngram"),
        {"comment": "书籍表（商品）"},
    )

    # ====== 基本字段 ======
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="书籍ID")
    book_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="书名"
    )
    author: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="作者"
    )
    price: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="价格（精确到两位小数）"
    )

    # ====== 新增字段（替换原来的 publisher 字符串） ======
    isbn: Mapped[Optional[str]] = mapped_column(
        String(20), unique=True, nullable=True, comment="ISBN 书号"
    )
    cover_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="封面图片URL"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="书籍简介"
    )
    stock: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="库存数量"
    )

    # ====== 外键 ======
    publisher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("publisher.id", ondelete="SET NULL"),
        nullable=True,
        comment="出版社ID（1:N 关系中的外键）",
    )

    # ====== ORM 关系 ======
    # 1:N ← Publisher
    publisher: Mapped[Optional["Publisher"]] = relationship(
        "Publisher", back_populates="books", lazy="selectin"
    )
    # M:N ← Category（通过 book_category 中间表）
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        secondary=book_category,
        back_populates="books",
        lazy="selectin",
    )
    # created_at / updated_at 继承自 Base
