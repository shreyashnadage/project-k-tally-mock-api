from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.emulator.state import get_active_simulation_id, set_active_simulation_id
from backend.models.company import Company
from backend.models.simulation import Simulation

router = APIRouter()


class EmulatorState(BaseModel):
    active_simulation_id: int | None
    company_name: str | None
    company_guid: str | None
    gst_number: str | None
    financial_year_from: str | None
    financial_year_to: str | None
    emulator_port: int = 9000


class ActivateRequest(BaseModel):
    simulation_id: int | None


@router.get("/emulator/state", response_model=EmulatorState)
def get_emulator_state(db: Session = Depends(get_db)):
    sim_id = get_active_simulation_id()
    if sim_id is None:
        return EmulatorState(
            active_simulation_id=None,
            company_name=None,
            company_guid=None,
            gst_number=None,
            financial_year_from=None,
            financial_year_to=None,
        )

    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim or not sim.company_id:
        set_active_simulation_id(None)
        return EmulatorState(
            active_simulation_id=None,
            company_name=None,
            company_guid=None,
            gst_number=None,
            financial_year_from=None,
            financial_year_to=None,
        )

    company = db.query(Company).filter(Company.id == sim.company_id).first()
    return EmulatorState(
        active_simulation_id=sim_id,
        company_name=company.name if company else None,
        company_guid=company.guid if company else None,
        gst_number=company.gst_number if company else None,
        financial_year_from=company.financial_year_from.isoformat() if company else None,
        financial_year_to=company.financial_year_to.isoformat() if company else None,
    )


@router.post("/emulator/activate")
def activate_simulation(body: ActivateRequest, db: Session = Depends(get_db)):
    if body.simulation_id is None:
        set_active_simulation_id(None)
        return {"status": "deactivated"}

    sim = db.query(Simulation).filter(Simulation.id == body.simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    if sim.status != "completed":
        raise HTTPException(status_code=400, detail="Simulation not completed yet")

    set_active_simulation_id(body.simulation_id)
    return {"status": "activated", "simulation_id": body.simulation_id}
