"""
Handles XML protocol requests from the tally agent:
  - Trial Balance (health check) → returns HTTP 200 with empty XML
  - DayBook → returns VOUCHER elements with line items, filtered by date range
"""

import re
from datetime import date, datetime

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.simulation import Simulation
from backend.models.voucher import Voucher, VoucherLineItem

_EMPTY_XML = '<?xml version="1.0" encoding="utf-8"?><ENVELOPE><BODY><DATA></DATA></BODY></ENVELOPE>'


def _parse_tally_date(s: str) -> date | None:
    s = s.strip()
    try:
        return datetime.strptime(s, "%Y%m%d").date()
    except ValueError:
        return None


def _extract_tag(xml: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", xml, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def _find_company(sim_id: int, db: Session) -> Company | None:
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim or not sim.company_id:
        return None
    return db.query(Company).filter(Company.id == sim.company_id).first()


def handle_xml_request(xml_body: str, sim_id: int | None, db: Session) -> str:
    # Health check — agent doesn't parse the response, just checks HTTP 200
    if "Trial Balance" in xml_body or "trialbalance" in xml_body.lower():
        return _EMPTY_XML

    if "DayBook" in xml_body or "daybook" in xml_body.lower():
        return _build_daybook(xml_body, sim_id, db)

    # Any other XML request — return empty OK response
    return _EMPTY_XML


def _build_daybook(xml_body: str, sim_id: int | None, db: Session) -> str:
    if sim_id is None:
        return _EMPTY_XML

    company = _find_company(sim_id, db)
    if not company:
        return _EMPTY_XML

    from_str = _extract_tag(xml_body, "SVFROMDATE")
    to_str = _extract_tag(xml_body, "SVTODATE")

    from_date = _parse_tally_date(from_str)
    to_date = _parse_tally_date(to_str)

    query = db.query(Voucher).filter(Voucher.company_id == company.id)
    if from_date:
        query = query.filter(Voucher.date >= from_date)
    if to_date:
        query = query.filter(Voucher.date <= to_date)

    vouchers = query.order_by(Voucher.date, Voucher.id).all()

    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             "<ENVELOPE><BODY><DATA><TALLYMESSAGE>"]

    for v in vouchers:
        date_str = v.date.strftime("%Y%m%d")
        narration = _xml_escape(v.narration or "")
        party = _xml_escape(v.party_ledger_name or "")
        vnum = _xml_escape(v.voucher_number or "")
        vtype = _xml_escape(v.voucher_type or "")
        guid = _xml_escape(v.guid or "")

        lines.append(f'<VOUCHER VCHTYPE="{vtype}" REMOTEID="{guid}">')
        lines.append(f"<DATE>{date_str}</DATE>")
        lines.append(f"<VOUCHERNUMBER>{vnum}</VOUCHERNUMBER>")
        lines.append(f"<NARRATION>{narration}</NARRATION>")
        lines.append(f"<PARTYLEDGERNAME>{party}</PARTYLEDGERNAME>")

        # Emit actual line items if available
        line_items = (
            db.query(VoucherLineItem)
            .filter(VoucherLineItem.voucher_id == v.id)
            .all()
        )

        if line_items:
            for li in line_items:
                ledger = _xml_escape(li.ledger_name)
                amt = f"{float(li.amount):.2f}"
                lines.append("<LEDGERENTRIES.LIST>")
                lines.append(f"<LEDGERNAME>{ledger}</LEDGERNAME>")
                lines.append(f"<AMOUNT>{amt}</AMOUNT>")
                lines.append("</LEDGERENTRIES.LIST>")
        else:
            # Fallback: two entries (party + contra account)
            amt = float(v.amount)
            contra = _contra_account(v.voucher_type)
            lines.append("<LEDGERENTRIES.LIST>")
            lines.append(f"<LEDGERNAME>{party}</LEDGERNAME>")
            lines.append(f"<AMOUNT>{-amt:.2f}</AMOUNT>")
            lines.append("</LEDGERENTRIES.LIST>")
            lines.append("<LEDGERENTRIES.LIST>")
            lines.append(f"<LEDGERNAME>{_xml_escape(contra)}</LEDGERNAME>")
            lines.append(f"<AMOUNT>{amt:.2f}</AMOUNT>")
            lines.append("</LEDGERENTRIES.LIST>")

        lines.append("</VOUCHER>")

    lines.append("</TALLYMESSAGE></DATA></BODY></ENVELOPE>")
    return "\n".join(lines)


def _contra_account(voucher_type: str) -> str:
    mapping = {
        "Sales": "Sales Account",
        "Purchase": "Purchase Account",
        "Receipt": "Cash",
        "Payment": "Cash",
        "Journal": "Suspense Account",
        "Contra": "Cash",
        "Credit Note": "Sales Returns",
        "Debit Note": "Purchase Returns",
    }
    return mapping.get(voucher_type, "Suspense Account")


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )
