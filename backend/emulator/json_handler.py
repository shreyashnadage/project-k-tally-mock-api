"""
Handles the JSON API protocol used by the tally agent for all entities
except vouchers (Company, Ledger, Group, StockItem, StockGroup).

Headers the agent sends:
  version: 1
  tallyrequest: export
  type: collection | object
  subtype: Company | Ledger | Group | StockItem | StockGroup
  id: <subtype> (for collection) | <entity_name> (for object)

Body:
  {"static_variables": [{"name": "svCurrentCompany", "value": "<name>"}, ...],
   "fetch_list": [...]}

Response (collection):
  {"status": "1", "data": {"collection": [{"metadata": {"name": "..."}, "<field>": {"type": "...", "value": "..."}, ...}]}}

Response (object):
  {"tallymessage": [{"metadata": {"name": "..."}, ...}]}
"""

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.ledger import Ledger, LedgerGroup
from backend.models.simulation import Simulation
from backend.models.stock import StockGroup, StockItem


def _field(type_: str, value) -> dict:
    return {"type": type_, "value": str(value) if value is not None else ""}


def _find_company(sim_id: int, db: Session) -> Company | None:
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim or not sim.company_id:
        return None
    return db.query(Company).filter(Company.id == sim.company_id).first()


# ── Company ──────────────────────────────────────────────────────────────────

def handle_company_collection(sim_id: int, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"status": "1", "data": {"collection": []}}
    return {
        "status": "1",
        "data": {
            "collection": [{"metadata": {"name": company.name}}]
        },
    }


def handle_company_object(sim_id: int, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"tallymessage": []}
    return {
        "tallymessage": [
            {
                "metadata": {"name": company.name},
                "guid": _field("String", company.guid),
                "formalname": _field("String", company.formal_name),
                "startingfrom": _field("Date", company.financial_year_from.strftime("%Y%m%d")),
                "booksfrom": _field("Date", company.books_from.strftime("%Y%m%d")),
                "basiccurrencyname": _field("String", "INR"),
                "statename": _field("String", company.state),
                "gstnumber": _field("String", company.gst_number),
            }
        ]
    }


# ── Ledger ────────────────────────────────────────────────────────────────────

def _ledger_record(l: Ledger, idx: int) -> dict:
    return {
        "metadata": {"name": l.name},
        "guid": _field("String", l.guid),
        "parent": _field("String", l.group_name),
        "ledgtype": _field("String", ""),
        "ledopeningbalance": _field("Amount", f"{float(l.opening_balance):.2f}"),
        "tbalopening": _field("Amount", f"{float(l.opening_balance):.2f}"),
        "closingbalance": _field("Amount", f"{float(l.closing_balance):.2f}"),
        "masterid": _field("Number", str(l.id)),
    }


def handle_ledger_collection(sim_id: int, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"status": "1", "data": {"collection": []}}
    ledgers = db.query(Ledger).filter(Ledger.company_id == company.id).order_by(Ledger.name).all()
    return {
        "status": "1",
        "data": {"collection": [_ledger_record(l, i) for i, l in enumerate(ledgers)]},
    }


def handle_ledger_object(sim_id: int, ledger_name: str, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"tallymessage": []}
    l = db.query(Ledger).filter(Ledger.company_id == company.id, Ledger.name == ledger_name).first()
    if not l:
        return {"tallymessage": []}
    return {"tallymessage": [_ledger_record(l, 0)]}


# ── Group ─────────────────────────────────────────────────────────────────────

def _group_record(g: LedgerGroup) -> dict:
    return {
        "metadata": {"name": g.name},
        "guid": _field("String", g.guid),
        "parent": _field("String", g.parent_name or ""),
        "isrevenueitem": _field("Logical", "Yes" if g.is_revenue else "No"),
        "masterid": _field("Number", str(g.id)),
    }


def handle_group_collection(sim_id: int, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"status": "1", "data": {"collection": []}}
    groups = db.query(LedgerGroup).filter(LedgerGroup.company_id == company.id).order_by(LedgerGroup.name).all()
    return {
        "status": "1",
        "data": {"collection": [_group_record(g) for g in groups]},
    }


def handle_group_object(sim_id: int, group_name: str, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"tallymessage": []}
    g = db.query(LedgerGroup).filter(LedgerGroup.company_id == company.id, LedgerGroup.name == group_name).first()
    if not g:
        return {"tallymessage": []}
    return {"tallymessage": [_group_record(g)]}


# ── StockItem ─────────────────────────────────────────────────────────────────

def _stock_item_record(si: StockItem) -> dict:
    return {
        "metadata": {"name": si.name},
        "guid": _field("String", si.guid),
        "parent": _field("String", si.group_name or ""),
        "baseunits": _field("String", si.unit),
        "openingbalance": _field("Amount", f"{float(si.opening_value):.2f}"),
        "closingbalance": _field("Amount", "0.00"),
        "hsncode": _field("String", si.hsn_code),
        "gstrate": _field("Rate", f"{float(si.gst_rate):.2f}"),
        "masterid": _field("Number", str(si.id)),
    }


def handle_stock_item_collection(sim_id: int, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"status": "1", "data": {"collection": []}}
    items = db.query(StockItem).filter(StockItem.company_id == company.id).order_by(StockItem.name).all()
    return {
        "status": "1",
        "data": {"collection": [_stock_item_record(si) for si in items]},
    }


def handle_stock_item_object(sim_id: int, item_name: str, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"tallymessage": []}
    si = db.query(StockItem).filter(StockItem.company_id == company.id, StockItem.name == item_name).first()
    if not si:
        return {"tallymessage": []}
    return {"tallymessage": [_stock_item_record(si)]}


# ── StockGroup ────────────────────────────────────────────────────────────────

def _stock_group_record(sg: StockGroup) -> dict:
    return {
        "metadata": {"name": sg.name},
        "guid": _field("String", sg.guid),
        "parent": _field("String", sg.parent_name or ""),
        "masterid": _field("Number", str(sg.id)),
    }


def handle_stock_group_collection(sim_id: int, db: Session) -> dict:
    company = _find_company(sim_id, db)
    if not company:
        return {"status": "1", "data": {"collection": []}}
    groups = db.query(StockGroup).filter(StockGroup.company_id == company.id).order_by(StockGroup.name).all()
    return {
        "status": "1",
        "data": {"collection": [_stock_group_record(sg) for sg in groups]},
    }


# ── Router ────────────────────────────────────────────────────────────────────

HANDLERS = {
    ("collection", "company"): handle_company_collection,
    ("object", "company"): handle_company_object,
    ("collection", "ledger"): handle_ledger_collection,
    ("object", "ledger"): handle_ledger_object,
    ("collection", "group"): handle_group_collection,
    ("object", "group"): handle_group_object,
    ("collection", "stockitem"): handle_stock_item_collection,
    ("object", "stockitem"): handle_stock_item_object,
    ("collection", "stockgroup"): handle_stock_group_collection,
}


def route_json_request(
    req_type: str,
    subtype: str,
    entity_id: str,
    sim_id: int,
    db: Session,
) -> dict:
    key = (req_type.lower(), subtype.lower())
    handler = HANDLERS.get(key)
    if not handler:
        return {"status": "0", "error": f"Unknown subtype: {subtype}"}

    # Object requests need the entity name for all types except Company
    if req_type.lower() == "object" and subtype.lower() != "company":
        return handler(sim_id, entity_id, db)
    return handler(sim_id, db)
