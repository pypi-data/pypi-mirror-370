from __future__ import annotations

from datetime import datetime, timezone
from time import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

from finalsa.common.lambdas.common.AppHandler import AppHandler
from finalsa.common.lambdas.common.constants import TIMESTAMP_HEADER
from finalsa.common.lambdas.sqs.get_handler_filled_args import get_handler_filled_args
from finalsa.common.lambdas.sqs.SqsEvent import SqsEvent
from finalsa.common.lambdas.types import LoggerProtocol, SqsHandlerFunc
from finalsa.common.models import AsyncMeta
from finalsa.sqs.client import SqsService, SqsServiceImpl
from finalsa.traceability import get_correlation_id, set_context_from_w3c_headers
from finalsa.traceability.functions import (
    HTTP_HEADER_TRACEPARENT,
    HTTP_HEADER_TRACESTATE,
)

if TYPE_CHECKING:
    pass


class SqsHandler(AppHandler):
    """Handler for SQS events."""

    def __init__(
        self,
        app_name: Optional[str] = None,
        logger: Optional[LoggerProtocol] = None,
        test_mode: bool = False
    ) -> None:
        super().__init__(app_name, logger, test_mode)
        self.handlers: Dict[str, SqsHandlerFunc] = {}
        self.handlers_args: Dict[str, Dict[str, Any]] = {}
        self.retries: Dict[str, int] = {}
        self.sqs_client: Optional[SqsService] = None
        self.sqs_urls_cache: Dict[str, str] = {}

    def get_sqs_client(self, default=SqsServiceImpl) -> SqsService:
        """Get SQS client instance."""
        if self.sqs_client is None:
            self.sqs_client = default()
        return self.sqs_client

    def __get_handler__(self, topic: str) -> Optional[SqsHandlerFunc]:
        """Get handler for the given topic."""
        if topic not in self.handlers:
            return self.handlers.get("default")
        return self.handlers.get(topic)

    def __get_retries__(self, topic: str) -> int:
        """Get retry count for the given topic."""
        if topic not in self.retries:
            return self.retries.get("default", 0)
        return self.retries.get(topic)

    def __try_excecution_str__(
        self,
        message: SqsEvent,
        meta: AsyncMeta,
    ) -> Tuple[Optional[Union[Dict, str]], bool]:
        try:
            handler = self.__get_handler__("default")
            handler_attrs = self.handlers_args["default"]
            filled_args = get_handler_filled_args(
                handler_attrs, {}, message, meta)
            response = handler(**filled_args)
            return response, True
        except Exception as e:
            self.logger.error("Error processing sqs event", extra={
                "error": e,
            })
            return None, False

    def __try_excecution_dict__(
            self,
            payload: Dict,
            message: SqsEvent,
            meta : AsyncMeta,
            handler: Optional[Callable] = None,
            retries: Optional[int] = None
    ) -> Tuple[Optional[Union[Dict, str]], bool]:
        topic = message.topic
        if topic not in self.handlers:
            topic = "default"
        if retries is None:
            retries = self.__get_retries__(topic)
        if handler is None:
            handler = self.__get_handler__(topic)
        try:
            handler = self.__get_handler__(topic)
            handler_attrs = self.handlers_args[topic]
            filled_args = get_handler_filled_args(
                handler_attrs, payload, message, meta)
            response = handler(**filled_args)
            return response, True
        except Exception as e:
            if retries > 0:
                self.logger.error("Error processing sqs event", extra={
                    "error": e,
                    "retries": retries
                })
                return self.__try_excecution_dict__(payload, message, meta, handler, retries - 1)
            else:
                self.logger.error("Error processing sqs event", extra={
                    "error": e,
                    "retries": retries
                })
                return None, False

    def __set_context_and_get_meta__(self, message: SqsEvent) -> AsyncMeta:
        trace_state = message.message_attributes.get(
            HTTP_HEADER_TRACESTATE,
        )
        trace_parent = message.message_attributes.get(
            HTTP_HEADER_TRACEPARENT,
        )
        timestamp = message.message_attributes.get(
            TIMESTAMP_HEADER,
            None
        )
        set_context_from_w3c_headers(
            trace_parent,
            trace_state,
            self.app_name
        )
        if self.__is_test__ and timestamp is not None:
            timestamp = datetime.fromisoformat(timestamp)
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        if not timestamp or isinstance(timestamp, str):
            timestamp = datetime.now(timezone.utc)
        return AsyncMeta(
            correlation_id=get_correlation_id(),
            timestamp=timestamp,
            topic=message.topic,
        )

    def __try_excution__(
        self,
        message: SqsEvent
    ) -> Tuple[Optional[Union[Dict, str]], bool]:
        content = message.get_payload()
        meta = self.__set_context_and_get_meta__(message)
        if isinstance(content, dict):
            return self.__try_excecution_dict__(content, message, meta)
        if isinstance(content, str):
            return self.__try_excecution_str__(message, meta)
        return None, False

    def __get_sqs_url__(self, sqs_name: str) -> str:
        if sqs_name in self.sqs_urls_cache:
            return self.sqs_urls_cache[sqs_name]
        sqs_url = self.get_sqs_client().get_queue_url(sqs_name)
        self.sqs_urls_cache[sqs_name] = sqs_url
        return sqs_url

    def __delete_message__(self, message: SqsEvent) -> None:
        sqs_arn = message.event_source_arn
        receipt_handle = message.receipt_handle
        sqs_name = sqs_arn.split(":")[-1]
        sqs_url = self.__get_sqs_url__(sqs_name)
        self.get_sqs_client().delete_message(sqs_url, receipt_handle)

    def process(self, event: Dict) -> List[Dict]:
        records = event['Records']
        responses = []
        for record in records:
            message = SqsEvent.from_sqs_lambda_event(record)
            response, is_sucess = self.__try_excution__(message)
            if is_sucess:
                self.__delete_message__(message)
            responses.append(response)
        return responses

    def handler(self, topic: str, retries: Optional[int] = 0) -> Callable:
        if retries < 0:
            raise ValueError("Retries must be greater or equal than 0")
        if topic in self.handlers:
            raise ValueError("Topic already has a handler")
        self.retries[topic] = retries

        def decorator(handler: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Optional[Union[Dict, str]]:
                self.logger.info("Processing sqs event", extra={
                    "topic": topic,
                    "retries": retries
                })
                start = time()
                result = handler(*args, **kwargs)
                end = time()
                self.logger.info("Processed sqs event", extra={
                    "result": result,
                    "topic": topic,
                    "retries": retries,
                    "duration": end - start
                })
                return result
            self.handlers_args[topic] = handler.__annotations__
            self.handlers[topic] = wrapper
            return wrapper
        return decorator

    def default(self, retries: Optional[int] = 1) -> Callable:
        return self.handler("default", retries)

    @classmethod
    def test(cls) -> SqsHandler:
        """Create a test instance of SqsHandler."""
        return cls("test", None, test_mode=True)

    def __merge__(self, other: SqsHandler) -> None:
        for topic, handler in other.handlers.items():
            if topic in self.handlers:
                raise ValueError("Topic already has a handler")
            self.handlers[topic] = handler
            self.handlers_args[topic] = other.handlers_args[topic]
        for topic, retries in other.retries.items():
            if topic in self.retries:
                raise ValueError("Topic already has a handler")
            self.retries[topic] = retries
