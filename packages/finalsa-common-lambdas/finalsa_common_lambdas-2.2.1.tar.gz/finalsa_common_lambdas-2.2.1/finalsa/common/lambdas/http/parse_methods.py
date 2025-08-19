from typing import Any, Dict

from orjson import dumps, loads
from pydantic import BaseModel

from finalsa.common.lambdas.http.HttpResponse import HttpResponse


def parse_body(headers: Dict, body: str) -> Any:
    if body == "" or body is None:
        return {}
    content_type = headers.get("Content-Type", "")
    if "application/json" in content_type:
        return loads(body)
    if 'text/plain' in content_type:
        return body
    try:
        return loads(body)
    except Exception:
        return body


def parse_response(http_response: HttpResponse, default_headers: Dict = None) -> Dict:
    body = http_response.body
    headers = http_response.headers or {}
    if isinstance(body, str):
        body = body
        headers["Content-Type"] = "text/plain"
    if isinstance(body, dict):
        body = dumps(body).decode("utf-8")
        headers["Content-Type"] = "application/json"
    if isinstance(body, BaseModel):
        body = body.model_dump_json()
        headers["Content-Type"] = "application/json"
    if not default_headers:
        default_headers = {}
    for key, value in default_headers.items():
        headers[key] = value
    return {
        "statusCode": http_response.status_code,
        "headers": headers,
        "body": body
    }


def get_correct_response(response: Any) -> HttpResponse:
    if isinstance(response, HttpResponse):
        return response
    http_response = HttpResponse(status_code=200, body=response)
    if response is None:
        http_response.body = {
            "message": "Not Found"
        }
        http_response.status_code = 404
    if isinstance(response, tuple):
        body_response, status_code = response
        http_response.body = body_response
        http_response.status_code = status_code
    return http_response
