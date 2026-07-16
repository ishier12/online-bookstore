"""
书评模型模块
定义 Review 表 — User 和 Book 之间的关联表
- User 1:N Review（一个用户可以写多条书评）
- Book 1:N Review（一本书可以有多条书评）
- UNIQUE(user_id, book_id)：每人每书限一条评论
"""

from sqlalchemy import String, Text, SmallInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from config.db_conf import Base

if TYPE_CHECKING:
    from models.user import User
    from models.book import Book


class Review(Base):
    """书评表"""
    __tablename__ = "review"
    __table_args__ = (
        Index("uk_user_book", "user_id", "book_id", unique=True),  # 每人每书限一条
        Index("idx_book_created", "book_id", "created_at"),       # 某书书评按时间排序
        Index("fk_user_id", "user_id"),                            # 外键索引→JOIN user
        {"comment": "书评表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="书评ID")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="评价人ID"
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", ondelete="CASCADE"), nullable=False, comment="书籍ID"
    )
    rating: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="评分 1~5"
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="评价内容"
    )

    # ====== 关系 ======
    user: Mapped["User"] = relationship("User", backref="reviews")
    book: Mapped["Book"] = relationship("Book", backref="reviews")
    # created_at / updated_at 继承自 Base
