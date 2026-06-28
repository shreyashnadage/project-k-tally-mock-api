BOM_UTF16_LE = b"\xff\xfe"


def encode_utf16le(xml_string: str) -> bytes:
    return BOM_UTF16_LE + xml_string.encode("utf-16-le")


def decode_request_body(body: bytes) -> str:
    if body[:2] == BOM_UTF16_LE:
        return body[2:].decode("utf-16-le")
    if body[:2] == b"\xfe\xff":
        return body[2:].decode("utf-16-be")
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError:
        return body.decode("utf-16-le", errors="replace")
