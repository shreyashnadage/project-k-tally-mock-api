from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.simulation import Simulation

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    sim_count = db.query(Simulation).filter(Simulation.status == "completed").count()
    return {
        "status": "ok",
        "service": "tally-data-simulator",
        "tdml_port": 9001,
        "simulations_count": sim_count,
    }
