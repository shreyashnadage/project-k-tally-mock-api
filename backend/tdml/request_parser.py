import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date

from backend.tdml.encoding import decode_request_body


@dataclass
class TdmlRequest:
    request_type: str = ""
    data_type: str = ""
    collection_id: str = ""
    company_name: str | None = None
    from_date: date | None = None
    to_date: date | None = None
    fetch_fields: list[str] = field(default_factory=list)
    filter_alter_id: int | None = None
    collection_type: str | None = None


def _parse_tally_date(s: str) -> date | None:
    s = s.strip()
    if len(s) == 8 and s.isdigit():
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    return None


def parse_tdml_request(body: bytes) -> TdmlRequest:
    text = decode_request_body(body)
    if text.startswith("﻿"):
        text = text[1:]

    root = ET.fromstring(text)
    req = TdmlRequest()

    header = root.find("HEADER")
    if header is not None:
        req.request_type = (header.findtext("TALLYREQUEST") or "").strip()
        req.data_type = (header.findtext("TYPE") or "").strip()
        req.collection_id = (header.findtext("ID") or "").strip()

    body_el = root.find("BODY")
    if body_el is None:
        return req

    desc = body_el.find("DESC")
    if desc is None:
        return req

    static = desc.find("STATICVARIABLES")
    if static is not None:
        req.company_name = static.findtext("SVCURRENTCOMPANY")
        from_str = static.findtext("SVFROMDATE")
        to_str = static.findtext("SVTODATE")
        if from_str:
            req.from_date = _parse_tally_date(from_str)
        if to_str:
            req.to_date = _parse_tally_date(to_str)

    tdl = desc.find("TDL")
    if tdl is not None:
        msg = tdl.find("TDLMESSAGE")
        if msg is not None:
            for coll in msg.iter("COLLECTION"):
                coll_type = coll.findtext("TYPE")
                if coll_type:
                    req.collection_type = coll_type.strip()

                fetch = coll.findtext("FETCH")
                if fetch:
                    req.fetch_fields = [f.strip() for f in fetch.split(",")]

                for sys_el in coll.iter("SYSTEM"):
                    formula = sys_el.get("FORMULA", "")
                    text_val = (sys_el.text or "").strip()
                    if "ALTERID" in formula.upper() or "ALTERID" in text_val.upper():
                        parts = text_val.replace("$ALTERID", "").replace(">", "").strip().split()
                        for p in parts:
                            if p.isdigit():
                                req.filter_alter_id = int(p)

    return req
