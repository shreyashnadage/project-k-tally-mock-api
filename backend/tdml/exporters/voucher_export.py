from datetime import date
from xml.sax.saxutils import escape

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.voucher import Voucher


def _fmt_date(d) -> str:
    return d.strftime("%Y%m%d") if d else ""


def export_vouchers(
    company_name: str,
    from_date: date | None,
    to_date: date | None,
    db: Session,
    alter_id_gt: int = 0,
) -> str:
    company = db.query(Company).filter(Company.name == company_name).first()
    if not company:
        return ""

    query = db.query(Voucher).filter(Voucher.company_id == company.id)
    if from_date:
        query = query.filter(Voucher.date >= from_date)
    if to_date:
        query = query.filter(Voucher.date <= to_date)
    if alter_id_gt > 0:
        query = query.filter(Voucher.alter_id > alter_id_gt)

    vouchers = query.order_by(Voucher.date, Voucher.alter_id).all()

    parts = []
    for v in vouchers:
        ledger_entries = ""
        for li in v.line_items:
            deemed = "Yes" if li.is_deemed_positive else "No"
            ledger_entries += f"""     <ALLLEDGERENTRIES.LIST>
      <LEDGERNAME>{escape(li.ledger_name)}</LEDGERNAME>
      <ISDEEMEDPOSITIVE>{deemed}</ISDEEMEDPOSITIVE>
      <AMOUNT>{float(li.amount):.2f}</AMOUNT>
     </ALLLEDGERENTRIES.LIST>
"""

        inventory_entries = ""
        for ie in v.inventory_items:
            inventory_entries += f"""     <ALLINVENTORYENTRIES.LIST>
      <STOCKITEMNAME>{escape(ie.stock_item_name)}</STOCKITEMNAME>
      <ACTUALQTY>{float(ie.quantity):.0f} {escape(ie.stock_item_name.split()[-1] if ie.stock_item_name else "Nos")}</ACTUALQTY>
      <BILLEDQTY>{float(ie.quantity):.0f}</BILLEDQTY>
      <RATE>{float(ie.rate):.2f}</RATE>
      <AMOUNT>{float(ie.amount):.2f}</AMOUNT>
      <DISCOUNT>{float(ie.discount):.2f}</DISCOUNT>
     </ALLINVENTORYENTRIES.LIST>
"""

        ref_date_xml = f"\n     <REFERENCEDATE>{_fmt_date(v.reference_date)}</REFERENCEDATE>" if v.reference_date else ""

        parts.append(f"""    <VOUCHER VCHTYPE="{escape(v.voucher_type)}" REMOTEID="{v.guid}" VCHKEY="{v.guid}">
     <GUID>{v.guid}</GUID>
     <ALTERID>{v.alter_id}</ALTERID>
     <DATE>{_fmt_date(v.date)}</DATE>
     <VOUCHERTYPENAME>{escape(v.voucher_type)}</VOUCHERTYPENAME>
     <VOUCHERNUMBER>{escape(v.voucher_number)}</VOUCHERNUMBER>
     <PARTYLEDGERNAME>{escape(v.party_ledger_name)}</PARTYLEDGERNAME>
     <AMOUNT>{float(v.amount):.2f}</AMOUNT>
     <NARRATION>{escape(v.narration)}</NARRATION>
     <PLACEOFSUPPLY>{escape(v.place_of_supply)}</PLACEOFSUPPLY>
     <REFERENCENUMBER>{escape(v.reference_number)}</REFERENCENUMBER>{ref_date_xml}
     <ISINVOICE>{"Yes" if v.is_invoice else "No"}</ISINVOICE>
     <ISCANCELLED>{"Yes" if v.is_cancelled else "No"}</ISCANCELLED>
{ledger_entries}{inventory_entries}    </VOUCHER>""")

    return "\n".join(parts)
