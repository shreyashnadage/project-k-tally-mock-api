from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class SimulationParams(BaseModel):
    name: str = "Default Simulation"
    company_name: str = "Sharma Traders Pvt Ltd"
    sector: Literal["retail", "manufacturing", "trading", "services", "pharma", "fmcg"] = "trading"
    business_size: Literal["micro", "small", "medium"] = "small"
    date_from: date = date(2024, 4, 1)
    date_to: date = date(2025, 3, 31)
    enable_seasonality: bool = True
    monthly_revenue_min: int = Field(default=500_000, ge=10_000)
    monthly_revenue_max: int = Field(default=2_000_000, ge=10_000)
    customer_count: int = Field(default=20, ge=1, le=200)
    vendor_count: int = Field(default=10, ge=1, le=100)
    product_count: int = Field(default=15, ge=1, le=200)
    payment_terms_days: int = Field(default=30, ge=1, le=180)
    bad_debt_pct: float = Field(default=5.0, ge=0, le=50)
    cash_sale_pct: float = Field(default=20.0, ge=0, le=100)
    gst_rate: float = Field(default=18.0, ge=0, le=28)
    gross_margin_pct: float = Field(default=25.0, ge=5, le=80)
    growth_trend: Literal["flat", "growing", "declining"] = "flat"
    growth_rate_pct: float = Field(default=10.0, ge=0, le=100)
    state: str = "Maharashtra"
    seed: int | None = None


class SimulationResult(BaseModel):
    simulation_id: int
    company_name: str
    companies: int = 1
    ledger_groups: int = 0
    ledgers: int = 0
    stock_groups: int = 0
    stock_items: int = 0
    vouchers: int = 0
    total_sales: float = 0
    total_purchases: float = 0
    total_receipts: float = 0
    total_payments: float = 0
