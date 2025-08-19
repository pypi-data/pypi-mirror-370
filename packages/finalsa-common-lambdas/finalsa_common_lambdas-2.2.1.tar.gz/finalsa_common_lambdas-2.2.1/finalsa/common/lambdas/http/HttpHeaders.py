from typing import Dict, Optional

from finalsa.traceability.functions import (
    HTTP_HEADER_TRACEPARENT,
    HTTP_HEADER_TRACESTATE,
)


class HttpHeaders:

    def __init__(self, headers: Dict[str, str]) -> None:
        self.headers = headers

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.headers.get(key, default)

    def get_content_type(self) -> Optional[str]:
        return self.get("Content-Type", "")

    def get_trace_state(self) -> Optional[str]:
        return self.get(HTTP_HEADER_TRACESTATE)

    def get_trace_parent(self) -> Optional[str]:
        return self.get(HTTP_HEADER_TRACEPARENT)
