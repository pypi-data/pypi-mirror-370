from typing import Any, Dict, Optional

from pydantic import BaseModel


class HttpResponse(BaseModel):
    status_code: Optional[int] = 200
    body: Optional[Any] = None
    headers: Optional[Dict[str, str]] = None

    @classmethod
    def bad_request(cls, body: Optional[Any] = None) -> "HttpResponse":
        if body is None:
            body = {"message": "Bad Request"}
        return cls(status_code=400, body=body)

    @classmethod
    def not_found(cls, body: Optional[Any] = None) -> "HttpResponse":
        if body is None:
            body = {"message": "Not Found"}
        return cls(status_code=404, body=body)

    @classmethod
    def internal_server_error(cls, body: Optional[Any] = None) -> "HttpResponse":
        if body is None:
            body = {"message": "Internal Server Error"}
        return cls(status_code=500, body=body)
