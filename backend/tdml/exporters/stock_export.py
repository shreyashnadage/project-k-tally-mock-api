from xml.sax.saxutils import escape

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.stock import StockItem


def export_stock_items(company_name: str, db: Session, alter_id_gt: int = 0) -> str:
    company = db.query(Company).filter(Company.name == company_name).first()
    if not company:
        return ""

    query = db.query(StockItem).filter(StockItem.company_id == company.id)
    if alter_id_gt > 0:
        query = query.filter(StockItem.alter_id > alter_id_gt)
    items = query.order_by(StockItem.alter_id).all()

    parts = []
    for si in items:
        parts.append(f"""    <STOCKITEM NAME="{escape(si.name)}" RESERVEDNAME="">
     <GUID>{si.guid}</GUID>
     <ALTERID>{si.alter_id}</ALTERID>
     <NAME>{escape(si.name)}</NAME>
     <PARENT>{escape(si.group_name)}</PARENT>
     <BASEUNITS>{escape(si.unit)}</BASEUNITS>
     <OPENINGBALANCE>{float(si.opening_quantity):.2f} {escape(si.unit)}</OPENINGBALANCE>
     <OPENINGRATE>{float(si.opening_rate):.2f}/{escape(si.unit)}</OPENINGRATE>
     <OPENINGVALUE>{float(si.opening_value):.2f}</OPENINGVALUE>
     <GSTRATE>{float(si.gst_rate):.2f}</GSTRATE>
     <HSNCODE>{si.hsn_code}</HSNCODE>
    </STOCKITEM>""")
    return "\n".join(parts)
