"""Base authentication module for OpenAPI Scanner.

This module defines the base class for all authentication implementations.
It provides a common interface for authentication, header generation, and cookie management.
"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class BaseAuth(ABC):
    """Base class for all authentication implementations.

    This abstract base class defines the interface that all authentication
    implementations must follow. It provides methods for authentication,
    header generation, and cookie management.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the authentication instance.

        Args:
            **kwargs: Configuration parameters for the authentication instance
        """
        logger.debug('Initializing base authentication')
        self._validate_kwargs(kwargs)

    @abstractmethod
    def authenticate(self, base_url: str) -> None:
        """Authenticate with the API.

        This method should implement the authentication logic, such as
        obtaining tokens or establishing sessions.

        Args:
            base_url: Base URL of the API

        Raises:
            Exception: If authentication fails
        """

    @abstractmethod
    def get_headers(self, base_url: str) -> dict[str, str]:
        """Get authentication headers.

        This method should return the headers required for authenticated
        requests, such as Authorization headers.

        Args:
            base_url: Base URL of the API

        Returns:
            Dictionary of header names and values
        """

    @abstractmethod
    def get_cookies(self, base_url: str) -> dict[str, str]:
        """Get authentication cookies.

        This method should return the cookies required for authenticated
        requests, such as session cookies.

        Args:
            base_url: Base URL of the API

        Returns:
            Dictionary of cookie names and values
        """

    def _validate_kwargs(self, kwargs: dict[str, Any]) -> None:
        """Validate configuration parameters.

        This method can be overridden by subclasses to validate their
        specific configuration parameters.

        Args:
            kwargs: Configuration parameters to validate

        Raises:
            ValueError: If any required parameters are missing or invalid
        """
        logger.debug('Validating configuration parameters')
        # Base class does no validation by default
