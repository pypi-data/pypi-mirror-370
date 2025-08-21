"""Authentication factory module for OpenAPI Scanner.

This module provides a factory for creating authentication instances based on class paths.
It supports both module paths and direct file paths for authentication classes.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import structlog

from specphp_scanner.auth.base import BaseAuth


logger = structlog.get_logger(__name__)


class AuthFactory:
    """Factory class for creating authentication instances.

    This class provides methods to create authentication instances from either
    module paths or direct file paths. It ensures that the created instances
    inherit from BaseAuth and are properly initialized.
    """

    @staticmethod
    def create(auth_path: str, **kwargs: Any) -> BaseAuth:
        """Create an authentication instance from a class path.

        Args:
            auth_path: Path to the authentication class, can be either:
                - Full Python module path (e.g. 'examples.koel.auth.KoelAuth')
                - Path to Python file (e.g. './examples/koel/auth.py')
            **kwargs: Arguments to pass to the authentication class constructor

        Returns:
            Instance of the authentication class

        Raises:
            ValueError: If the class cannot be loaded or is invalid
        """
        logger.info(f"Creating auth instance from path: {auth_path}")

        # Check if path is a file
        auth_file = Path(auth_path)
        if auth_file.is_file():
            logger.debug(f"Loading auth class from file: {auth_file}")
            return AuthFactory._create_from_file(auth_file, **kwargs)
        else:
            logger.debug(f"Loading auth class from module path: {auth_path}")
            return AuthFactory._create_from_module(auth_path, **kwargs)

    @staticmethod
    def _create_from_file(file_path: Path, **kwargs: Any) -> BaseAuth:
        """Create an authentication instance from a Python file.

        Args:
            file_path: Path to the Python file containing the auth class
            **kwargs: Arguments to pass to the authentication class constructor

        Returns:
            Instance of the authentication class

        Raises:
            ValueError: If the class cannot be loaded or is invalid
        """
        try:
            # Load the module from file
            spec = importlib.util.spec_from_file_location(
                'auth_module', file_path,
            )
            if not spec or not spec.loader:
                raise ValueError(
                    f"Could not load module from file: {file_path}",
                )

            module = importlib.util.module_from_spec(spec)
            sys.modules['auth_module'] = module
            spec.loader.exec_module(module)

            # Find the first class that inherits from BaseAuth
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and
                    issubclass(attr, BaseAuth) and
                    attr != BaseAuth
                ):
                    logger.info(f"Found auth class: {attr_name}")
                    return attr(**kwargs)

            raise ValueError(f"No valid auth class found in file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to load auth class from file: {e}")
            raise ValueError(f"Failed to load auth class from file: {e}")

    @staticmethod
    def _create_from_module(module_path: str, **kwargs: Any) -> BaseAuth:
        """Create an authentication instance from a module path.

        Args:
            module_path: Full Python module path to the auth class
            **kwargs: Arguments to pass to the authentication class constructor

        Returns:
            Instance of the authentication class

        Raises:
            ValueError: If the class cannot be loaded or is invalid
        """
        try:
            # Split module path into module and class name
            module_name, class_name = module_path.rsplit('.', 1)

            # Import the module
            module = importlib.import_module(module_name)

            # Get the class
            auth_class = getattr(module, class_name)

            # Verify it's a valid auth class
            if not isinstance(auth_class, type) or not issubclass(auth_class, BaseAuth):
                raise ValueError(f"Invalid auth class: {class_name}")

            logger.info(f"Creating instance of auth class: {class_name}")
            return auth_class(**kwargs)

        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load auth class from module: {e}")
            raise ValueError(f"Failed to load auth class from module: {e}")
