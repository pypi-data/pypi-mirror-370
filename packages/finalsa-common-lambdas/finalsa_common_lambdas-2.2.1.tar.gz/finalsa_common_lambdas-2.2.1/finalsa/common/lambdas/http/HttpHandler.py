from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

from finalsa.common.lambdas.common.AppHandler import AppHandler
from finalsa.common.lambdas.common.constants import TIMESTAMP_HEADER
from finalsa.common.lambdas.http.get_handler_filled_args import get_handler_filled_args
from finalsa.common.lambdas.http.HttpHeaders import HttpHeaders
from finalsa.common.lambdas.http.HttpResponse import HttpResponse
from finalsa.common.lambdas.http.parse_methods import (
    get_correct_response,
    parse_body,
    parse_response,
)
from finalsa.common.lambdas.http.path_methods import get_fixed_path, get_regex_path, match_key
from finalsa.common.lambdas.types import (
    HttpEventDict,
    HttpResponseDict,
    LoggerProtocol,
)
from finalsa.common.models import HttpMeta
from finalsa.traceability import get_correlation_id, set_context_from_w3c_headers
from finalsa.traceability.functions import (
    HTTP_AUTHORIZATION_HEADER,
    HTTP_HEADER_TRACEPARENT,
    HTTP_HEADER_TRACESTATE,
)

if TYPE_CHECKING:
    pass


class HttpHandler(AppHandler):
    """Handler for HTTP events from API Gateway."""

    def __init__(
        self,
        app_name: Optional[str] = None,
        logger: Optional[LoggerProtocol] = None,
        test_mode: bool = False
    ) -> None:
        super().__init__(app_name, logger, test_mode)
        self.handlers: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.regex_expressions: Dict[str, Dict[str, str]] = {}

    def validate_handler(self, path: str, method: str) -> Dict[str, Any]:
        """Validate and prepare handler configuration."""
        fixed_path = path if path.startswith("/") else f"/{path}"
        splited_path = fixed_path.split("/")
        splited_path = list(filter(lambda x: x != "", splited_path))
        len_splited_path = len(splited_path)
        if len_splited_path < 1:
            raise ValueError("Path must have at least 1 parts")
        if len_splited_path > 5:
            raise ValueError("Path must have at most 5 parts")
        keys = []
        fixed_args = []
        for part in splited_path:
            if not part.startswith("{") or not part.endswith("}"):
                keys.append(part)
                continue
            arg_name = part[1:-1]
            keys.append(arg_name)
            fixed_args.append(arg_name)
        real_path = get_fixed_path(keys)
        if real_path in self.handlers and method in self.handlers[real_path]:
            raise ValueError("Path already has a handler")
        regex_exp = get_regex_path(keys, fixed_args)
        return {
            "path": real_path,
            "fixed_args": fixed_args,
            "regex": regex_exp
        }

    def handler(
            self,
            path: str,
            method: Optional[str] = "POST",
            headers: Optional[Dict[str, str]] = None
    ) -> Callable:
        """
        Use this fn in case the method is not the default ones
        """
        if headers is None:
            headers = {}
        params = self.validate_handler(path, method)
        methods = [method]
        if method == "POST":
            methods.append("OPTIONS")

        def decorator(handler: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Optional[Union[Dict, str]]:
                self.logger.info("Processing http event", extra={
                    "path": path,
                    "method": method
                })
                try:
                    result = handler(*args, **kwargs)
                    self.logger.info("Processed http event")
                    return result
                except Exception as e:
                    self.logger.error("Error processing http event", extra={
                        "error": e,
                    })
                    self.logger.exception(e)
                    return {
                        "message": "Internal Server Error"
                    }, 500
            real_path = params["path"]
            regex_path = params["regex"]
            for method in methods:
                self.handlers[method][real_path] = {
                    "handler": wrapper,
                    "function_args": handler.__annotations__,
                    "headers": headers or {},
                    **params
                }
                self.regex_expressions[method][regex_path] = real_path
            return wrapper
        return decorator

    def default(self, headers: Optional[Dict[str, str]] = None) -> Callable:
        return self.post("default", headers)

    def post(self, path: str, headers: Optional[Dict[str, str]] = None) -> Callable:
        if headers is None:
            headers = {}
        if "POST" not in self.handlers:
            self.handlers["POST"] = {}
            self.regex_expressions["POST"] = {}
        if "OPTIONS" not in self.handlers:
            self.handlers["OPTIONS"] = {}
            self.regex_expressions["OPTIONS"] = {}
        return self.handler(path, "POST", headers)

    def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> Callable:
        if headers is None:
            headers = {}
        if "GET" not in self.handlers:
            self.handlers["GET"] = {}
            self.regex_expressions["GET"] = {}
        return self.handler(path, "GET", headers)

    def put(self, path: str, headers: Optional[Dict[str, str]] = None) -> Callable:
        if headers is None:
            headers = {}
        if "PUT" not in self.handlers:
            self.handlers["PUT"] = {}
            self.regex_expressions["PUT"] = {}
        return self.handler(path, "PUT", headers)

    def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> Callable:
        if headers is None:
            headers = {}
        if "DELETE" not in self.handlers:
            self.handlers["DELETE"] = {}
            self.regex_expressions["DELETE"] = {}
        return self.handler(path, "DELETE", headers)

    def patch(self, path: str, headers: Optional[Dict[str, str]] = None) -> Callable:
        if headers is None:
            headers = {}
        if "PATCH" not in self.handlers:
            self.handlers["PATCH"] = {}
            self.regex_expressions["PATCH"] = {}
        return self.handler(path, "PATCH", headers)

    def options(self, path: str, headers: Optional[Dict[str, str]] = None) -> Callable:
        if headers is None:
            headers = {}
        if "OPTIONS" not in self.handlers:
            self.handlers["OPTIONS"] = {}
            self.regex_expressions["OPTIONS"] = {}
        return self.handler(path, "OPTIONS", headers)

    def set_context_and_meta(self, event: Dict, headers: HttpHeaders) -> HttpMeta:
        set_context_from_w3c_headers(
            headers.get(HTTP_HEADER_TRACEPARENT, None),
            headers.get(HTTP_HEADER_TRACESTATE, None),
            service_name=self.app_name
        )
        timestamp = headers.get(TIMESTAMP_HEADER, None)
        if self.__is_test__ and timestamp is not None:
            timestamp = datetime.fromisoformat(timestamp)
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        if not timestamp or isinstance(timestamp, str):
            timestamp = datetime.now(timezone.utc)
        return HttpMeta(
            correlation_id=get_correlation_id(),
            timestamp=timestamp,
            authorization=None if self.__is_test__ else headers.get(
                HTTP_AUTHORIZATION_HEADER, None),
            ip=event.get("requestContext", {}).get(
                "identity", {}).get("sourceIp", ""),
        )

    def process(self, event: HttpEventDict) -> HttpResponseDict:
        """Process HTTP event and return response."""
        method = event['httpMethod']
        path = event['path']
        headers = event.get('headers')
        if not headers:
            headers = {}
        headers = HttpHeaders(headers)
        meta = self.set_context_and_meta(event, headers)
        self.logger.info("Processing http event", extra={
            "httpMethod": method,
            "path": path,
        })

        real_path = path if path.startswith("/") else f"/{path}"
        real_path = real_path if real_path.endswith("/") else f"{real_path}/"
        if self.regex_expressions.get(method) is None:
            self.logger.info("Path not found", extra={
                "httpMethod": method,
                "path": path,
            })
            return parse_response(HttpResponse.not_found())
        match_result, args = match_key(
            self.regex_expressions[method], real_path)
        if match_result is None:
            self.logger.info("Path not found", extra={
                "httpMethod": method,
                "path": path,
            })
            return parse_response(HttpResponse.not_found())
        body = event.get('body', "")
        parsed_body = parse_body(headers, body)
        handler = self.handlers[method][match_result]
        try:
            filled_args = get_handler_filled_args(
                handler["function_args"],
                args,
                handler["fixed_args"],
                event.get("queryStringParameters", {}),
                headers,
                parsed_body,
                meta
            )
        except Exception as e:
            self.logger.error("Error processing http event", extra={
                "error": e,
            })
            self.logger.exception(e)
            return parse_response(HttpResponse.bad_request())
        method_handler = handler["handler"]
        response = method_handler(**filled_args)
        correct_response = get_correct_response(response)
        return parse_response(correct_response, handler["headers"])

    @classmethod
    def test(cls) -> HttpHandler:
        """Create a test instance of HttpHandler."""
        return cls("test", None, test_mode=True)

    def __merge__(self, other: HttpHandler) -> None:
        """__merge__ handlers from another HttpHandler instance."""
        for method, handlers in other.handlers.items():
            if method not in self.handlers:
                self.handlers[method] = {}
                self.regex_expressions[method] = {}
            for path, handler in handlers.items():
                if path not in self.handlers[method]:
                    self.handlers[method][path] = handler
                else:
                    raise ValueError(
                        f"Path {path} already has a handler for method {method}")

        for method, regex in other.regex_expressions.items():
            if method not in self.regex_expressions:
                self.regex_expressions[method] = {}
            for regex_path, path in regex.items():
                if regex_path not in self.regex_expressions[method]:
                    self.regex_expressions[method][regex_path] = path
