from xml.sax.saxutils import escape

from sqlalchemy.orm import Session

from backend.models.company import Company


def _fmt_date(d) -> str:
    return d.strftime("%Y%m%d") if d else ""


def export_companies(db: Session) -> str:
    companies = db.query(Company).all()
    parts = []
    for c in companies:
        parts.append(f"""    <COMPANY>
     <NAME>{escape(c.name)}</NAME>
     <GUID>{c.guid}</GUID>
     <FORMALNAME>{escape(c.formal_name)}</FORMALNAME>
     <STARTINGFROM>{_fmt_date(c.financial_year_from)}</STARTINGFROM>
     <ENDINGAT>{_fmt_date(c.financial_year_to)}</ENDINGAT>
     <BOOKSFROM>{_fmt_date(c.books_from)}</BOOKSFROM>
     <CURRENCYNAME>{escape(c.currency_name)}</CURRENCYNAME>
     <ADDRESS>{escape(c.address)}</ADDRESS>
     <STATENAME>{escape(c.state)}</STATENAME>
     <PINCODE>{c.pincode}</PINCODE>
     <GSTIN>{c.gst_number}</GSTIN>
     <PANNO>{c.pan_number}</PANNO>
     <ALTERID>{c.alter_id}</ALTERID>
    </COMPANY>""")
    return "\n".join(parts)
