from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.ledger import Ledger
from backend.models.simulation import Simulation
from backend.models.stock import StockItem
from backend.models.voucher import Voucher

router = APIRouter()


class LedgerOut(BaseModel):
    id: int
    name: str
    group_name: str
    opening_balance: float
    closing_balance: float
    state: str
    gst_number: str
    credit_period: int


class StockItemOut(BaseModel):
    id: int
    name: str
    group_name: str
    unit: str
    opening_quantity: float
    opening_rate: float
    opening_value: float
    gst_rate: float
    hsn_code: str


class VoucherOut(BaseModel):
    id: int
    voucher_type: str
    voucher_number: str
    date: str
    party_ledger_name: str
    amount: float
    narration: str
    is_cancelled: bool


@router.get("/{sim_id}/ledgers")
def list_ledgers(
    sim_id: int,
    group: str | None = None,
    db: Session = Depends(get_db),
) -> list[LedgerOut]:
    company_id = _get_company_id(sim_id, db)
    query = db.query(Ledger).filter(Ledger.company_id == company_id)
    if group:
        query = query.filter(Ledger.group_name == group)
    ledgers = query.order_by(Ledger.name).all()
    return [
        LedgerOut(
            id=l.id, name=l.name, group_name=l.group_name,
            opening_balance=float(l.opening_balance), closing_balance=float(l.closing_balance),
            state=l.state, gst_number=l.gst_number, credit_period=l.credit_period,
        )
        for l in ledgers
    ]


@router.get("/{sim_id}/stock-items")
def list_stock_items(sim_id: int, db: Session = Depends(get_db)) -> list[StockItemOut]:
    company_id = _get_company_id(sim_id, db)
    items = db.query(StockItem).filter(StockItem.company_id == company_id).order_by(StockItem.name).all()
    return [
        StockItemOut(
            id=si.id, name=si.name, group_name=si.group_name, unit=si.unit,
            opening_quantity=float(si.opening_quantity), opening_rate=float(si.opening_rate),
            opening_value=float(si.opening_value), gst_rate=float(si.gst_rate), hsn_code=si.hsn_code,
        )
        for si in items
    ]


@router.get("/{sim_id}/vouchers")
def list_vouchers(
    sim_id: int,
    voucher_type: str | None = None,
    month: str | None = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[VoucherOut]:
    company_id = _get_company_id(sim_id, db)
    query = db.query(Voucher).filter(Voucher.company_id == company_id)
    if voucher_type:
        query = query.filter(Voucher.voucher_type == voucher_type)
    if month:
        from datetime import date
        parts = month.split("-")
        if len(parts) == 2:
            y, m = int(parts[0]), int(parts[1])
            start = date(y, m, 1)
            if m == 12:
                end = date(y + 1, 1, 1)
            else:
                end = date(y, m + 1, 1)
            query = query.filter(Voucher.date >= start, Voucher.date < end)

    vouchers = query.order_by(Voucher.date).offset(offset).limit(limit).all()
    return [
        VoucherOut(
            id=v.id, voucher_type=v.voucher_type, voucher_number=v.voucher_number,
            date=v.date.isoformat(), party_ledger_name=v.party_ledger_name,
            amount=float(v.amount), narration=v.narration, is_cancelled=v.is_cancelled,
        )
        for v in vouchers
    ]


def _get_company_id(sim_id: int, db: Session) -> int:
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim or not sim.company_id:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim.company_id
