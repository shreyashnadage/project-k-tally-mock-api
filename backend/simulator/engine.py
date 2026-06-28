import json
import random
from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.simulation import Simulation
from backend.models.sync_state import AlterIdTracker
from backend.simulator.company_gen import generate_company
from backend.simulator.ledger_gen import generate_ledgers
from backend.simulator.schemas import SimulationParams, SimulationResult
from backend.simulator.sector_templates import get_template
from backend.simulator.stock_gen import generate_stock_items
from backend.simulator.voucher_gen import generate_vouchers


class SimulatorEngine:
    def __init__(self, db: Session):
        self.db = db

    def run(self, params: SimulationParams) -> SimulationResult:
        rng = random.Random(params.seed or hash(params.company_name))
        template = get_template(params.sector)

        sim = Simulation(
            name=params.name,
            params_json=json.dumps(params.model_dump(), default=str),
            status="running",
        )
        self.db.add(sim)
        self.db.flush()

        company = generate_company(params, self.db, rng)
        sim.company_id = company.id

        ledgers = generate_ledgers(company, params, template, self.db, rng)
        stock_items = generate_stock_items(company, params, template, self.db, rng)
        vouchers_by_type = generate_vouchers(company, params, ledgers, stock_items, self.db, rng)

        total_sales = sum(abs(float(v.amount)) for v in vouchers_by_type.get("Sales", []))
        total_purchases = sum(abs(float(v.amount)) for v in vouchers_by_type.get("Purchase", []))
        total_receipts = sum(abs(float(v.amount)) for v in vouchers_by_type.get("Receipt", []))
        total_payments = sum(abs(float(v.amount)) for v in vouchers_by_type.get("Payment", []))

        total_vouchers = sum(len(v) for v in vouchers_by_type.values())

        for entity_type, count in [("ledger", len(ledgers)), ("voucher", total_vouchers), ("stock_item", len(stock_items))]:
            tracker = AlterIdTracker(
                company_id=company.id,
                entity_type=entity_type,
                last_alter_id=count,
            )
            self.db.add(tracker)

        sim.status = "completed"
        sim.completed_at = datetime.utcnow()
        self.db.commit()

        return SimulationResult(
            simulation_id=sim.id,
            company_name=company.name,
            ledger_groups=len(company.ledger_groups),
            ledgers=len(ledgers),
            stock_groups=len(company.stock_groups),
            stock_items=len(stock_items),
            vouchers=total_vouchers,
            total_sales=round(total_sales, 2),
            total_purchases=round(total_purchases, 2),
            total_receipts=round(total_receipts, 2),
            total_payments=round(total_payments, 2),
        )
