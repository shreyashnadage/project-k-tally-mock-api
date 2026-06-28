import random

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.ledger import Ledger
from backend.simulator.company_gen import INDIAN_STATES, STATE_CODES, _generate_gstin, _generate_pan
from backend.simulator.guid_factory import generate_guid
from backend.simulator.schemas import SimulationParams
from backend.simulator.sector_templates import SectorTemplate


def generate_ledgers(
    company: Company,
    params: SimulationParams,
    template: SectorTemplate,
    db: Session,
    rng: random.Random,
) -> list[Ledger]:
    seed = str(params.seed or params.company_name)
    ledgers: list[Ledger] = []
    idx = 0

    customer_names = list(template.customer_names)
    rng.shuffle(customer_names)
    for i in range(min(params.customer_count, len(customer_names))):
        cust_state = rng.choice(INDIAN_STATES)
        state_code = STATE_CODES.get(cust_state, "27")
        opening = round(rng.uniform(10000, 200000), 2) if rng.random() > 0.3 else 0
        ledger = Ledger(
            guid=generate_guid("ledger", idx, seed),
            company_id=company.id,
            name=customer_names[i],
            group_name="Sundry Debtors",
            opening_balance=-opening,  # debit balance = negative in Tally convention
            state=cust_state,
            gst_number=_generate_gstin(state_code, rng),
            pan_number=_generate_pan(rng),
            credit_period=params.payment_terms_days,
            alter_id=idx + 1,
        )
        db.add(ledger)
        ledgers.append(ledger)
        idx += 1

    vendor_names = list(template.vendor_names)
    rng.shuffle(vendor_names)
    for i in range(min(params.vendor_count, len(vendor_names))):
        vend_state = rng.choice(INDIAN_STATES)
        state_code = STATE_CODES.get(vend_state, "27")
        opening = round(rng.uniform(5000, 100000), 2) if rng.random() > 0.3 else 0
        ledger = Ledger(
            guid=generate_guid("ledger", idx, seed),
            company_id=company.id,
            name=vendor_names[i],
            group_name="Sundry Creditors",
            opening_balance=opening,  # credit balance = positive
            state=vend_state,
            gst_number=_generate_gstin(state_code, rng),
            pan_number=_generate_pan(rng),
            credit_period=params.payment_terms_days,
            alter_id=idx + 1,
        )
        db.add(ledger)
        ledgers.append(ledger)
        idx += 1

    system_ledgers = [
        ("HDFC Bank Current A/c", "Bank Accounts", 0),
        ("Cash", "Cash-in-Hand", 0),
        ("Sales Account", "Sales Accounts", 0),
        ("Purchase Account", "Purchase Accounts", 0),
        ("CGST", "Duties & Taxes", 0),
        ("SGST", "Duties & Taxes", 0),
        ("IGST", "Duties & Taxes", 0),
        ("Rent Expense", "Indirect Expenses", 0),
        ("Salary Expense", "Indirect Expenses", 0),
        ("Office Expenses", "Indirect Expenses", 0),
        ("Interest Received", "Indirect Incomes", 0),
        ("Round Off", "Indirect Expenses", 0),
    ]
    for name, group, opening in system_ledgers:
        ledger = Ledger(
            guid=generate_guid("ledger", idx, seed),
            company_id=company.id,
            name=name,
            group_name=group,
            opening_balance=opening,
            state=params.state,
            alter_id=idx + 1,
        )
        db.add(ledger)
        ledgers.append(ledger)
        idx += 1

    db.flush()
    return ledgers
