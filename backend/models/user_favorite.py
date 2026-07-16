"""
🔲 [第二期] 收藏模型模块
定义 UserFavorite 表 — User M:N Book（一个用户可以收藏多本书，一本书可以被多个用户收藏）
"""

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from config.db_conf import Base


class UserFavorite(Base):
    """用户收藏表（第二期）— M:N 中间表带额外元数据"""
    __tablename__ = "user_favorite"
    __table_args__ = (
        Index("uk_user_book", "user_id", "book_id", unique=True),   # 不能重复收藏
        Index("idx_user_created", "user_id", "created_at"),          # 我的收藏按时间倒序
        {"comment": "用户收藏表（第二期）"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="用户ID"
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", ondelete="CASCADE"), nullable=False, comment="书籍ID"
    )
    # created_at / updated_at 继承自 Base
