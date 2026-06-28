from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class StockGroup(Base):
    __tablename__ = "stock_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    alter_id: Mapped[int] = mapped_column(Integer, default=1)

    company = relationship("Company", back_populates="stock_groups")


class StockItem(Base):
    __tablename__ = "stock_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    group_name: Mapped[str] = mapped_column(String(200), default="")
    unit: Mapped[str] = mapped_column(String(20), default="Nos")
    opening_quantity: Mapped[float] = mapped_column(Numeric(15, 3), default=0)
    opening_rate: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    opening_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    gst_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=18.0)
    hsn_code: Mapped[str] = mapped_column(String(10), default="")
    alter_id: Mapped[int] = mapped_column(Integer, default=1)

    company = relationship("Company", back_populates="stock_items")
