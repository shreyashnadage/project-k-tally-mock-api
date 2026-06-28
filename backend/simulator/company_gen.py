import random
import string

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.ledger import LedgerGroup
from backend.simulator.guid_factory import generate_guid
from backend.simulator.schemas import SimulationParams

INDIAN_STATES = [
    "Maharashtra", "Gujarat", "Karnataka", "Tamil Nadu", "Delhi",
    "Uttar Pradesh", "Rajasthan", "West Bengal", "Telangana", "Kerala",
    "Madhya Pradesh", "Punjab", "Haryana", "Andhra Pradesh", "Bihar",
]

STATE_CODES = {
    "Maharashtra": "27", "Gujarat": "24", "Karnataka": "29", "Tamil Nadu": "33",
    "Delhi": "07", "Uttar Pradesh": "09", "Rajasthan": "08", "West Bengal": "19",
    "Telangana": "36", "Kerala": "32", "Madhya Pradesh": "23", "Punjab": "03",
    "Haryana": "06", "Andhra Pradesh": "37", "Bihar": "10",
}

STANDARD_GROUPS = [
    ("Capital Account", None, False, True),
    ("Current Assets", None, False, True),
    ("Bank Accounts", "Current Assets", False, True),
    ("Cash-in-Hand", "Current Assets", False, True),
    ("Sundry Debtors", "Current Assets", False, True),
    ("Stock-in-Hand", "Current Assets", False, True),
    ("Current Liabilities", None, False, False),
    ("Sundry Creditors", "Current Liabilities", False, False),
    ("Duties & Taxes", "Current Liabilities", False, False),
    ("Direct Expenses", None, False, True),
    ("Purchase Accounts", "Direct Expenses", False, True),
    ("Direct Incomes", None, True, False),
    ("Sales Accounts", "Direct Incomes", True, False),
    ("Indirect Expenses", None, False, True),
    ("Indirect Incomes", None, True, False),
    ("Fixed Assets", None, False, True),
    ("Investments", None, False, True),
    ("Loans (Liability)", None, False, False),
    ("Branch / Divisions", None, False, True),
    ("Suspense A/c", None, False, True),
]


def _generate_gstin(state_code: str, rng: random.Random) -> str:
    pan = "".join(rng.choices(string.ascii_uppercase, k=5)) + "".join(rng.choices(string.digits, k=4)) + rng.choice(string.ascii_uppercase)
    entity_num = str(rng.randint(1, 9))
    check = rng.choice(string.ascii_uppercase + string.digits)
    return f"{state_code}{pan}{entity_num}Z{check}"


def _generate_pan(rng: random.Random) -> str:
    return "".join(rng.choices(string.ascii_uppercase, k=5)) + "".join(rng.choices(string.digits, k=4)) + rng.choice(string.ascii_uppercase)


def generate_company(params: SimulationParams, db: Session, rng: random.Random) -> Company:
    seed = str(params.seed or params.company_name)
    state_code = STATE_CODES.get(params.state, "27")

    company = Company(
        guid=generate_guid("company", 0, seed),
        name=params.company_name,
        formal_name=params.company_name,
        address=f"123, Industrial Area\n{params.state}, India",
        state=params.state,
        pincode=f"{rng.randint(400000, 600000)}",
        gst_number=_generate_gstin(state_code, rng),
        pan_number=_generate_pan(rng),
        financial_year_from=params.date_from,
        financial_year_to=params.date_to,
        books_from=params.date_from,
    )
    db.add(company)
    db.flush()

    for i, (name, parent, is_rev, is_pos) in enumerate(STANDARD_GROUPS):
        group = LedgerGroup(
            guid=generate_guid("ledger_group", i, seed),
            company_id=company.id,
            name=name,
            parent_name=parent,
            is_revenue=is_rev,
            is_deemed_positive=is_pos,
            alter_id=i + 1,
        )
        db.add(group)

    db.flush()
    return company
