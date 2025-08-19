from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from finalsa.common.lambdas.http.HttpHandler import HttpHandler
from finalsa.common.lambdas.sqs.SqsHandler import SqsHandler
from finalsa.common.lambdas.types import (
    HttpEventDict,
    LambdaContext,
    LambdaEvent,
    LambdaResponse,
    LoggerProtocol,
    SqsEventDict,
)
from finalsa.sqs.client import SqsServiceTest

if TYPE_CHECKING:
    pass


class AppEntry:
    """
    Base class for Lambda application entries.

    Provides common functionality for handling both HTTP and SQS events.
    """

    def __init__(
        self,
        app_name: Optional[str] = None,
        logger: Optional[LoggerProtocol] = None
    ) -> None:
        self.app_name = app_name
        if logger is None:
            logger = logging.getLogger(app_name or "root")
        self.logger = logger
        self.__is_test__: bool = False
        self.sqs = SqsHandler(self.app_name, self.logger)
        self.http = HttpHandler(self.app_name, self.logger)

    def set_app_name(self, app_name: str) -> None:
        """Set the application name for this entry."""
        self.app_name = app_name
        self.sqs.set_app_name(app_name)
        self.http.set_app_name(app_name)

    def _sqs_execution(self, event: SqsEventDict) -> List[Optional[Dict[str, Any]]]:
        """Execute SQS event processing."""
        return self.sqs.process(event)

    def _http_execution(self, event: HttpEventDict) -> Dict[str, Any]:
        """Execute HTTP event processing."""
        return self.http.process(event)

    def execute(
        self,
        event: LambdaEvent,
        context: Optional[LambdaContext] = None
    ) -> LambdaResponse:
        """
        Execute the appropriate handler based on event type.

        Args:
            event: The Lambda event to process
            context: Optional Lambda context object
        Returns:
            Response from the appropriate handler
        """
        if context is None:
            context = {}

        # Check if this is an SQS event
        is_sqs = event.get("Records", None) is not None
        if is_sqs:
            return self._sqs_execution(event)
        return self._http_execution(event)

    def __set_test_mode__(self) -> None:
        """Enable test mode for this entry."""
        self.__is_test__ = True
        self.sqs.get_sqs_client(default=SqsServiceTest)
        self.http.__set_test_mode__()
        self.sqs.__set_test_mode__()
