"""
CLI command decorators for common boilerplate patterns.
"""

import functools
import logging
from typing import Optional, Callable, Any
from ..core.config import Config
from ..core.cleaner import CSVCleaner
from .utils import setup_logging, handle_error, load_configuration


def cli_command(func: Callable) -> Callable:
    """Decorator to handle common CLI command boilerplate.

    Handles:
    - Logging setup
    - Configuration loading
    - CSVCleaner initialization
    - Error handling

    Args:
        func: The CLI command function to decorate

    Returns:
        Decorated function with boilerplate handled
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        verbose = kwargs.get('verbose', False)
        config_file = kwargs.get('config_file', None)

        setup_logging(verbose)

        try:
            # Load configuration
            config = load_configuration(config_file)

            # Call original function with config
            return func(*args, config=config, **kwargs)

        except Exception as e:
            handle_error(e, verbose)

    return wrapper


def cli_command_with_cleaner(func: Callable) -> Callable:
    """Decorator to handle CLI command boilerplate with CSVCleaner initialization.

    Handles:
    - Logging setup
    - Configuration loading
    - CSVCleaner initialization
    - Error handling

    Args:
        func: The CLI command function to decorate

    Returns:
        Decorated function with boilerplate handled
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        verbose = kwargs.get('verbose', False)
        config_file = kwargs.get('config_file', None)

        setup_logging(verbose)

        try:
            # Load configuration
            config = load_configuration(config_file)

            # Initialize cleaner
            cleaner = CSVCleaner(config)

            # Call original function with config and cleaner
            return func(*args, config=config, cleaner=cleaner, **kwargs)

        except Exception as e:
            handle_error(e, verbose)

    return wrapper
