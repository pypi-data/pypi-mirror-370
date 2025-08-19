from typing import Any, Dict, Union

from pydantic import BaseModel

from finalsa.common.lambdas.sqs.SqsEvent import SqsEvent
from finalsa.common.models import AsyncMeta, Meta


def get_handler_filled_args(
    attrs: Dict[str, Any],
    payload: Union[Dict, str],
    parsed_event: SqsEvent,
    meta: AsyncMeta,
) -> Dict:
    filled_args = {}
    for key, value in attrs.items():
        if key == 'return':
            continue
        if isinstance(value, type):
            if issubclass(value, SqsEvent):
                filled_args[key] = parsed_event
                continue
            if issubclass(value, AsyncMeta) or value == Meta:
                filled_args[key] = meta
                continue
            elif issubclass(value, BaseModel):
                filled_args[key] = value(**payload)
                continue
        if key == "meta":
            filled_args[key] = meta
        if key == "message":
            filled_args[key] = payload
        elif key in payload:
            filled_args[key] = payload[key]
    return filled_args
