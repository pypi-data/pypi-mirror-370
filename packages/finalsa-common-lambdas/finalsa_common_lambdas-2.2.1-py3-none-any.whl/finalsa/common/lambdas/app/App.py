from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from finalsa.common.lambdas.app.AppEntry import AppEntry
from finalsa.common.lambdas.types import LambdaContext, LambdaEvent, LambdaResponse, LoggerProtocol

if TYPE_CHECKING:
    pass


class App(AppEntry):
    """
    Main application class that manages Lambda function execution.

    This class serves as the primary entry point for Lambda functions,
    handling both HTTP and SQS events through registered AppEntry instances.

    Args:
        app_name: Optional name for the application
        logger: Optional logger instance for the application
        test_mode: Whether to run in test mode (disables external services)
    """

    def __init__(
        self,
        app_name: Optional[str] = None,
        logger: Optional[LoggerProtocol] = None,
        test_mode: bool = False
    ) -> None:
        if logger is None:
            logger = logging.getLogger(app_name or self.__class__.__name__)

        super().__init__(app_name, logger)
        self.__is_test__: bool = test_mode

    def register(self, app_entry: AppEntry) -> None:
        """
        Register an AppEntry with this application.

        Args:
            app_entry: The AppEntry instance to register

        Raises:
            TypeError: If app_entry is not an AppEntry instance
            RuntimeError: If registration fails
        """
        if not isinstance(app_entry, AppEntry):
            raise TypeError(f"Expected AppEntry, got {type(app_entry).__name__}")

        try:
            app_entry.set_app_name(self.app_name)
            if self.__is_test__:
                app_entry.__set_test_mode__()

            self.sqs.__merge__(app_entry.sqs)
            self.http.__merge__(app_entry.http)

        except Exception as e:
            self.logger.error(f"Failed to register app entry: {e}")
            raise RuntimeError(f"Registration failed: {e}") from e

    def __set_test_mode__(self) -> None:
        """Enable test mode for the application."""
        self.__is_test__ = True
        super().__set_test_mode__()

    @property
    def is_test_mode(self) -> bool:
        """Check if application is in test mode."""
        return self.__is_test__

    def execute(
        self,
        event: LambdaEvent,
        context: Optional[LambdaContext] = None
    ) -> LambdaResponse:
        """
        Execute the Lambda function with the given event and context.

        Args:
            event: The Lambda event to process
            context: Optional Lambda context object

        Returns:
            The response from the appropriate handler

        Raises:
            ValueError: If event format is invalid
            RuntimeError: If execution fails
        """
        try:
            return super().execute(event, context)
        except Exception as e:
            self.logger.exception(f"Execution failed: {e}")
            raise RuntimeError(f"Lambda execution failed: {e}") from e
