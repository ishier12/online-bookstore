"""
🔲 [第二期] 支付模型模块
定义 Payment 表 — Order 1:1 Payment（一个订单对应一笔支付）
"""

import enum
from sqlalchemy import String, ForeignKey, DECIMAL, Enum, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from datetime import datetime
from typing import Optional
from config.db_conf import Base


class PaymentMethod(str, enum.Enum):
    """支付方式枚举"""
    ALIPAY = "alipay"
    WECHAT = "wechat"
    CARD = "card"


class PaymentStatus(str, enum.Enum):
    """支付状态枚举"""
    PENDING = "pending"      # 待支付
    SUCCESS = "success"      # 支付成功
    FAILED = "failed"        # 支付失败
    REFUNDED = "refunded"    # 已退款


class Payment(Base):
    """支付表（第二期）"""
    __tablename__ = "payment"
    __table_args__ = {"comment": "支付表（第二期）"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="支付ID")
    order_id: Mapped[int] = mapped_column(
        ForeignKey("order.id"), unique=True, nullable=False, comment="订单ID（1:1）"
    )
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 2), nullable=False, comment="支付金额"
    )
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), comment="支付方式"
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING, comment="支付状态"
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="支付完成时间"
    )
    # created_at / updated_at 继承自 Base
