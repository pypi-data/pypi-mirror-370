from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from finalsa.common.lambdas.http.HttpHeaders import HttpHeaders
from finalsa.common.lambdas.http.HttpQueryParams import HttpQueryParams
from finalsa.common.models import HttpMeta, Meta


def get_handler_filled_args(
    function_args: Dict[str, Any],
    parsed_args_from_path: List[str],
    args_from_path: Dict[str, str],
    query_params: Dict[str, str],
    headers: HttpHeaders,
    body: Optional[Union[Dict, str]],
    meta: HttpMeta,
) -> Dict:
    filled_args = {}
    for arg, value in zip(args_from_path, parsed_args_from_path, strict=False):
        if arg in function_args:
            filled_args[arg] = value
    if query_params is None:
        query_params = {}
    for arg, value in query_params.items():
        if arg in function_args:
            filled_args[arg] = value
    headers = headers or {}
    for key in function_args:
        if key in filled_args:
            continue
        value = function_args[key]
        if value == HttpHeaders:
            filled_args[key] = headers
        elif value == HttpQueryParams:
            filled_args[key] = HttpQueryParams(query_params)
        elif value == datetime:
            filled_args[key] = meta.timestamp
        elif value in {Meta, HttpMeta}:
            filled_args[key] = meta
        elif issubclass(value, BaseModel):
            filled_args[key] = value(**body)
        elif key == "body":
            filled_args[key] = body
    return filled_args
