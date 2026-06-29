"""
Minimal FastAPI app that runs on port 9000 and emulates TallyPrime's HTTP API.
Handles both the JSON API (companies/ledgers/groups/stock) and XML DayBook protocol.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from backend.database import SessionLocal
from backend.emulator import json_handler, xml_handler
from backend.emulator.state import get_active_simulation_id

emulator_app = FastAPI(title="Tally Emulator", docs_url=None, redoc_url=None)


@emulator_app.post("/")
async def tally_emulator(request: Request):
    content_type = request.headers.get("content-type", "").lower()
    sim_id = get_active_simulation_id()

    # ── JSON API (companies, ledgers, groups, stock items/groups) ──────────────
    if "application/json" in content_type:
        req_type = request.headers.get("type", "collection").lower()
        subtype = request.headers.get("subtype", "").lower()
        entity_id = request.headers.get("id", "")

        if sim_id is None:
            if req_type == "object":
                return JSONResponse({"tallymessage": []})
            return JSONResponse({"status": "1", "data": {"collection": []}})

        db = SessionLocal()
        try:
            result = json_handler.route_json_request(req_type, subtype, entity_id, sim_id, db)
        finally:
            db.close()

        return JSONResponse(result)

    # ── XML protocol (DayBook vouchers, health check) ──────────────────────────
    body_bytes = await request.body()
    # Agent sends UTF-8 XML
    try:
        xml_body = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        xml_body = body_bytes.decode("latin-1")

    db = SessionLocal()
    try:
        xml_response = xml_handler.handle_xml_request(xml_body, sim_id, db)
    finally:
        db.close()

    return PlainTextResponse(xml_response, media_type="text/xml; charset=utf-8")
