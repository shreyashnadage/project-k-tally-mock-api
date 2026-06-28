def build_envelope(collection_xml: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-16"?>
<ENVELOPE>
 <BODY>
  <DATA>
   <COLLECTION>
{collection_xml}
   </COLLECTION>
  </DATA>
 </BODY>
</ENVELOPE>"""


def build_error_envelope(message: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-16"?>
<ENVELOPE>
 <BODY>
  <DATA>
   <LINEERROR>{message}</LINEERROR>
  </DATA>
 </BODY>
</ENVELOPE>"""
