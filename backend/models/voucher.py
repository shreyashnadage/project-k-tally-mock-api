from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Voucher(Base):
    __tablename__ = "vouchers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    voucher_type: Mapped[str] = mapped_column(String(30), nullable=False)
    voucher_number: Mapped[str] = mapped_column(String(30), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    party_ledger_name: Mapped[str] = mapped_column(String(200), default="")
    amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    is_invoice: Mapped[bool] = mapped_column(Boolean, default=True)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    narration: Mapped[str] = mapped_column(Text, default="")
    place_of_supply: Mapped[str] = mapped_column(String(50), default="")
    reference_number: Mapped[str] = mapped_column(String(50), default="")
    reference_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    alter_id: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="vouchers")
    line_items = relationship("VoucherLineItem", back_populates="voucher", cascade="all, delete-orphan")
    inventory_items = relationship("VoucherInventoryItem", back_populates="voucher", cascade="all, delete-orphan")


class VoucherLineItem(Base):
    __tablename__ = "voucher_line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    voucher_id: Mapped[int] = mapped_column(ForeignKey("vouchers.id"), nullable=False)
    ledger_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    is_deemed_positive: Mapped[bool] = mapped_column(Boolean, default=True)

    voucher = relationship("Voucher", back_populates="line_items")


class VoucherInventoryItem(Base):
    __tablename__ = "voucher_inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    voucher_id: Mapped[int] = mapped_column(ForeignKey("vouchers.id"), nullable=False)
    stock_item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), default=0)
    rate: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    voucher = relationship("Voucher", back_populates="inventory_items")
