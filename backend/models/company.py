from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    formal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(Text, default="")
    state: Mapped[str] = mapped_column(String(50), default="Maharashtra")
    pincode: Mapped[str] = mapped_column(String(10), default="")
    gst_number: Mapped[str] = mapped_column(String(20), default="")
    pan_number: Mapped[str] = mapped_column(String(10), default="")
    financial_year_from: Mapped[date] = mapped_column(Date, nullable=False)
    financial_year_to: Mapped[date] = mapped_column(Date, nullable=False)
    books_from: Mapped[date] = mapped_column(Date, nullable=False)
    currency_name: Mapped[str] = mapped_column(String(10), default="₹")
    alter_id: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ledger_groups = relationship("LedgerGroup", back_populates="company", cascade="all, delete-orphan")
    ledgers = relationship("Ledger", back_populates="company", cascade="all, delete-orphan")
    stock_groups = relationship("StockGroup", back_populates="company", cascade="all, delete-orphan")
    stock_items = relationship("StockItem", back_populates="company", cascade="all, delete-orphan")
    vouchers = relationship("Voucher", back_populates="company", cascade="all, delete-orphan")
    cost_centers = relationship("CostCenter", back_populates="company", cascade="all, delete-orphan")
