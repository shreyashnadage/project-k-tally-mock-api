from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class LedgerGroup(Base):
    __tablename__ = "ledger_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_revenue: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deemed_positive: Mapped[bool] = mapped_column(Boolean, default=True)
    alter_id: Mapped[int] = mapped_column(Integer, default=1)

    company = relationship("Company", back_populates="ledger_groups")


class Ledger(Base):
    __tablename__ = "ledgers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    group_name: Mapped[str] = mapped_column(String(200), nullable=False)
    opening_balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    closing_balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    address: Mapped[str] = mapped_column(Text, default="")
    state: Mapped[str] = mapped_column(String(50), default="")
    gst_number: Mapped[str] = mapped_column(String(20), default="")
    pan_number: Mapped[str] = mapped_column(String(10), default="")
    credit_period: Mapped[int] = mapped_column(Integer, default=30)
    is_bill_wise: Mapped[bool] = mapped_column(Boolean, default=True)
    gst_registration_type: Mapped[str] = mapped_column(String(20), default="Regular")
    alter_id: Mapped[int] = mapped_column(Integer, default=1)

    company = relationship("Company", back_populates="ledgers")
