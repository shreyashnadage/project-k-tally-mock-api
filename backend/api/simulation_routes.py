import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.company import Company
from backend.models.ledger import Ledger, LedgerGroup
from backend.models.simulation import Simulation
from backend.models.stock import StockGroup, StockItem
from backend.models.voucher import Voucher, VoucherInventoryItem, VoucherLineItem
from backend.models.cost_center import CostCenter
from backend.models.sync_state import AlterIdTracker
from backend.simulator.engine import SimulatorEngine
from backend.simulator.schemas import SimulationParams, SimulationResult

router = APIRouter()


class SimulationSummary(BaseModel):
    id: int
    name: str
    status: str
    company_name: str | None = None
    created_at: str
    completed_at: str | None = None
    params: dict | None = None


@router.get("")
def list_simulations(db: Session = Depends(get_db)) -> list[SimulationSummary]:
    sims = db.query(Simulation).order_by(Simulation.created_at.desc()).all()
    results = []
    for s in sims:
        company = db.query(Company).filter(Company.id == s.company_id).first() if s.company_id else None
        results.append(SimulationSummary(
            id=s.id,
            name=s.name,
            status=s.status,
            company_name=company.name if company else None,
            created_at=s.created_at.isoformat() if s.created_at else "",
            completed_at=s.completed_at.isoformat() if s.completed_at else None,
            params=json.loads(s.params_json) if s.params_json else None,
        ))
    return results


@router.post("", status_code=201)
def create_simulation(params: SimulationParams, db: Session = Depends(get_db)) -> SimulationResult:
    engine = SimulatorEngine(db)
    return engine.run(params)


@router.get("/{sim_id}")
def get_simulation(sim_id: int, db: Session = Depends(get_db)) -> SimulationSummary:
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    company = db.query(Company).filter(Company.id == sim.company_id).first() if sim.company_id else None
    return SimulationSummary(
        id=sim.id,
        name=sim.name,
        status=sim.status,
        company_name=company.name if company else None,
        created_at=sim.created_at.isoformat() if sim.created_at else "",
        completed_at=sim.completed_at.isoformat() if sim.completed_at else None,
        params=json.loads(sim.params_json) if sim.params_json else None,
    )


@router.delete("/{sim_id}", status_code=204)
def delete_simulation(sim_id: int, db: Session = Depends(get_db)):
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if sim.company_id:
        company = db.query(Company).filter(Company.id == sim.company_id).first()
        if company:
            db.query(VoucherInventoryItem).filter(
                VoucherInventoryItem.voucher_id.in_(
                    db.query(Voucher.id).filter(Voucher.company_id == company.id)
                )
            ).delete(synchronize_session=False)
            db.query(VoucherLineItem).filter(
                VoucherLineItem.voucher_id.in_(
                    db.query(Voucher.id).filter(Voucher.company_id == company.id)
                )
            ).delete(synchronize_session=False)
            db.query(Voucher).filter(Voucher.company_id == company.id).delete()
            db.query(Ledger).filter(Ledger.company_id == company.id).delete()
            db.query(LedgerGroup).filter(LedgerGroup.company_id == company.id).delete()
            db.query(StockItem).filter(StockItem.company_id == company.id).delete()
            db.query(StockGroup).filter(StockGroup.company_id == company.id).delete()
            db.query(CostCenter).filter(CostCenter.company_id == company.id).delete()
            db.query(AlterIdTracker).filter(AlterIdTracker.company_id == company.id).delete()
            db.delete(company)

    db.delete(sim)
    db.commit()


class MonthlySummary(BaseModel):
    month: str
    sales: float
    purchases: float
    receipts: float
    payments: float


@router.get("/{sim_id}/monthly-summary")
def get_monthly_summary(sim_id: int, db: Session = Depends(get_db)) -> list[MonthlySummary]:
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim or not sim.company_id:
        raise HTTPException(status_code=404, detail="Simulation not found")

    vouchers = db.query(Voucher).filter(Voucher.company_id == sim.company_id).all()

    monthly: dict[str, dict[str, float]] = {}
    for v in vouchers:
        key = v.date.strftime("%Y-%m")
        if key not in monthly:
            monthly[key] = {"sales": 0, "purchases": 0, "receipts": 0, "payments": 0}
        amount = abs(float(v.amount))
        vtype = v.voucher_type.lower()
        if vtype == "sales":
            monthly[key]["sales"] += amount
        elif vtype == "purchase":
            monthly[key]["purchases"] += amount
        elif vtype == "receipt":
            monthly[key]["receipts"] += amount
        elif vtype == "payment":
            monthly[key]["payments"] += amount

    return [
        MonthlySummary(month=k, **{k2: round(v2, 2) for k2, v2 in v.items()})
        for k, v in sorted(monthly.items())
    ]
