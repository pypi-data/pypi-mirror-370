from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from finalsa.common.lambdas.types import LoggerProtocol

if TYPE_CHECKING:
    pass


class AppHandler:
    """Base class for application handlers."""

    def __init__(
        self,
        app_name: Optional[str] = None,
        logger: Optional[LoggerProtocol] = None,
        test_mode: bool = False
    ) -> None:
        self.app_name = app_name
        self.logger = logger or logging.getLogger(app_name or "root")
        self.__is_test__: bool = test_mode

    def set_app_name(self, app_name: str) -> None:
        """Set the application name."""
        self.app_name = app_name

    def __set_test_mode__(self) -> None:
        """Enable test mode."""
        self.__is_test__ = True

    @classmethod
    def test(cls) -> AppHandler:
        """Create a test instance."""
        return cls("test", logging.getLogger("test"), test_mode=True)
