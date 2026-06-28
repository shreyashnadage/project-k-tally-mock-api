from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.tdml.encoding import encode_utf16le
from backend.tdml.exporters.company_export import export_companies
from backend.tdml.exporters.ledger_export import export_ledgers
from backend.tdml.exporters.stock_export import export_stock_items
from backend.tdml.exporters.voucher_export import export_vouchers
from backend.tdml.request_parser import parse_tdml_request
from backend.tdml.response_builder import build_envelope, build_error_envelope

router = APIRouter()


@router.post("/")
async def handle_tdml(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    tdml_req = parse_tdml_request(body)

    xml_content = ""

    if tdml_req.collection_id.lower() in ("list of companies", "company"):
        xml_content = export_companies(db)

    elif tdml_req.collection_type == "Ledger":
        xml_content = export_ledgers(
            tdml_req.company_name or "",
            db,
            alter_id_gt=tdml_req.filter_alter_id or 0,
        )

    elif tdml_req.collection_type == "Voucher":
        xml_content = export_vouchers(
            tdml_req.company_name or "",
            tdml_req.from_date,
            tdml_req.to_date,
            db,
            alter_id_gt=tdml_req.filter_alter_id or 0,
        )

    elif tdml_req.collection_type == "StockItem":
        xml_content = export_stock_items(
            tdml_req.company_name or "",
            db,
            alter_id_gt=tdml_req.filter_alter_id or 0,
        )

    else:
        response_xml = build_error_envelope(f"Unknown request: {tdml_req.collection_id} / {tdml_req.collection_type}")
        return Response(content=encode_utf16le(response_xml), media_type="text/xml; charset=utf-16")

    response_xml = build_envelope(xml_content)
    return Response(content=encode_utf16le(response_xml), media_type="text/xml; charset=utf-16")
