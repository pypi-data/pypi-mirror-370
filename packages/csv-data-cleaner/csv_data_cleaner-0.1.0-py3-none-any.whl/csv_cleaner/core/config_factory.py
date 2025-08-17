"""
Configuration factory for centralized configuration management.
"""

from typing import Optional
from .config import Config, ConfigurationManager


class ConfigurationFactory:
    """Factory for creating and loading configuration objects."""

    @staticmethod
    def load_config(config_file: Optional[str] = None) -> Config:
        """Load configuration from file or use defaults.

        Args:
            config_file: Path to configuration file

        Returns:
            Configuration object
        """
        if config_file:
            config_manager = ConfigurationManager(config_file)
            return config_manager.load_config()
        return Config()

    @staticmethod
    def create_default_config() -> Config:
        """Create a default configuration object.

        Returns:
            Default configuration object
        """
        return Config()

    @staticmethod
    def create_config_from_dict(config_dict: dict) -> Config:
        """Create configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Configuration object
        """
        config = Config()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
