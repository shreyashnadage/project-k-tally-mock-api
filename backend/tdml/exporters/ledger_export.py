from xml.sax.saxutils import escape

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.ledger import Ledger


def export_ledgers(company_name: str, db: Session, alter_id_gt: int = 0) -> str:
    company = db.query(Company).filter(Company.name == company_name).first()
    if not company:
        return ""

    query = db.query(Ledger).filter(Ledger.company_id == company.id)
    if alter_id_gt > 0:
        query = query.filter(Ledger.alter_id > alter_id_gt)
    ledgers = query.order_by(Ledger.alter_id).all()

    parts = []
    for l in ledgers:
        ob = f"{float(l.opening_balance):.2f}"
        cb = f"{float(l.closing_balance):.2f}"
        parts.append(f"""    <LEDGER NAME="{escape(l.name)}" RESERVEDNAME="">
     <GUID>{l.guid}</GUID>
     <ALTERID>{l.alter_id}</ALTERID>
     <NAME>{escape(l.name)}</NAME>
     <PARENT>{escape(l.group_name)}</PARENT>
     <OPENINGBALANCE>{ob}</OPENINGBALANCE>
     <CLOSINGBALANCE>{cb}</CLOSINGBALANCE>
     <COUNTRYOFRESIDENCE>India</COUNTRYOFRESIDENCE>
     <GSTREGISTRATIONTYPE>{escape(l.gst_registration_type)}</GSTREGISTRATIONTYPE>
     <PARTYGSTIN>{l.gst_number}</PARTYGSTIN>
     <LEDSTATENAME>{escape(l.state)}</LEDSTATENAME>
     <ISBILLWISEON>{"Yes" if l.is_bill_wise else "No"}</ISBILLWISEON>
     <CREDITPERIOD>{l.credit_period}</CREDITPERIOD>
    </LEDGER>""")
    return "\n".join(parts)
