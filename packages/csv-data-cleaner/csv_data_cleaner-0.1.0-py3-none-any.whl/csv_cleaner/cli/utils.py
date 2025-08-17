"""
CLI utility functions for common operations.
"""

import logging
from typing import Optional
from ..core.config import Config
from ..core.config_factory import ConfigurationFactory


def setup_logging(verbose: bool) -> None:
    """Setup logging configuration for CLI commands.

    Args:
        verbose: Enable verbose logging if True
    """
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(message)s'
        )


def handle_error(error: Exception, verbose: bool) -> None:
    """Handle errors in CLI commands.

    Args:
        error: The exception that occurred
        verbose: Enable verbose error reporting if True
    """
    if verbose:
        raise error
    else:
        import click
        click.echo(f"❌ Error: {str(error)}")
        raise click.Abort()


def load_configuration(config_file: Optional[str] = None) -> Config:
    """Load configuration from file or use defaults.

    Args:
        config_file: Path to configuration file

    Returns:
        Configuration object
    """
    return ConfigurationFactory.load_config(config_file)
