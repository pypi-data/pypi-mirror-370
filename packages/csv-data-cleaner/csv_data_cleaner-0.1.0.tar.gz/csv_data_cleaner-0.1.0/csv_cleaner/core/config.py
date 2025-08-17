"""
Configuration management for CSV Data Cleaner.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from ..feature_gate import FeatureGate


@dataclass
class Config:
    """Configuration settings for CSV Data Cleaner."""

    # Core settings
    default_encoding: str = "utf-8"
    max_memory_usage: int = 1024 * 1024 * 1024  # 1GB
    chunk_size: int = 10000
    parallel_processing: bool = True
    max_workers: int = 4

    # AI settings
    ai_enabled: bool = False
    default_llm_provider: str = "openai"
    ai_api_keys: Dict[str, str] = field(default_factory=dict)
    ai_cost_limit: float = 10.0  # USD per operation
    ai_suggestion_cache_size: int = 100  # Number of cached suggestions
    ai_learning_enabled: bool = True  # Enable learning from user feedback
    ai_explanation_enabled: bool = True  # Enable AI explanations
    ai_auto_suggest: bool = False  # Auto-suggest operations
    ai_model_parameters: Dict[str, Any] = field(
        default_factory=lambda: {"temperature": 0.7, "max_tokens": 1000, "top_p": 1.0}
    )
    # AI Model Configuration (Simple)
    ai_openai_model: str = "gpt-4o-mini"  # OpenAI model
    ai_anthropic_model: str = "claude-3-5-sonnet-20241022"  # Anthropic model
    ai_local_model: str = "llama3.1:8b"  # Local model

    # AI logging settings
    ai_logging_enabled: bool = True  # Enable AI interaction logging
    ai_log_file: Optional[str] = None  # Custom AI log file path
    ai_log_level: str = "INFO"  # AI logging level
    ai_log_retention_days: int = 30  # Days to retain AI logs
    ai_log_mask_sensitive_data: bool = True  # Mask sensitive data in logs

    # File settings
    backup_enabled: bool = True
    backup_suffix: str = ".backup"
    output_format: str = "csv"

    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Progress tracking
    progress_tracking: bool = True

    # Performance settings
    max_memory_gb: float = 2.0
    enable_chunked_processing: bool = True
    enable_parallel_processing: bool = True
    performance_monitoring: bool = True
    auto_optimize_chunk_size: bool = True

    # Validation settings
    enable_validation: bool = True
    validation_schema_file: Optional[str] = None
    quality_threshold: float = 0.8

    # Deduplication settings
    dedupe_threshold: float = 0.5
    dedupe_sample_size: int = 1000
    dedupe_training_file: Optional[str] = None

    # Default operations
    default_operations: List[str] = field(
        default_factory=lambda: ["remove_duplicates", "clean_names", "handle_missing"]
    )

    # Temp file management settings
    temp_directory: Optional[str] = None
    temp_file_cleanup_interval: int = 3600  # seconds (1 hour)
    temp_file_max_age_hours: int = 24  # hours
    temp_file_max_size_mb: int = 1024  # MB
    temp_file_cleanup_enabled: bool = True
    temp_file_secure_mode: bool = True
    temp_file_auto_cleanup: bool = True

    # Package version settings
    package_version: str = "basic"  # "basic" or "pro"
    feature_gate_enabled: bool = True

    # Feature gate settings
    show_upgrade_prompts: bool = True
    upgrade_prompt_frequency: int = 3  # Show every N premium feature attempts

    def __post_init__(self):
        """Post-initialization to detect package version."""
        from ..feature_gate import detect_package_version
        self.package_version = detect_package_version()


class ConfigurationManager:
    """Manages configuration loading, saving, and environment variables."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional path to configuration file.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self.load_config()

        # Initialize feature gate
        self.feature_gate = FeatureGate(self.config.package_version)

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        config_dir = Path.home() / ".csv-cleaner"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.yaml")

    def load_config(self) -> Config:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
                return self._dict_to_config(config_data)
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")

        # Return default configuration
        return Config()

    def save_config(self, config: Config) -> None:
        """Save configuration to file.

        Args:
            config: Configuration object to save.
        """
        config_data = self._config_to_dict(config)

        # Ensure directory exists
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

    def _config_to_dict(self, config: Config) -> Dict[str, Any]:
        """Convert Config object to dictionary."""
        return {
            "default_encoding": config.default_encoding,
            "max_memory_usage": config.max_memory_usage,
            "chunk_size": config.chunk_size,
            "parallel_processing": config.parallel_processing,
            "max_workers": config.max_workers,
            "ai_enabled": config.ai_enabled,
            "default_llm_provider": config.default_llm_provider,
            "ai_api_keys": config.ai_api_keys,
            "ai_cost_limit": config.ai_cost_limit,
            "ai_suggestion_cache_size": config.ai_suggestion_cache_size,
            "ai_learning_enabled": config.ai_learning_enabled,
            "ai_explanation_enabled": config.ai_explanation_enabled,
            "ai_auto_suggest": config.ai_auto_suggest,
            "ai_model_parameters": config.ai_model_parameters,
            "ai_openai_model": config.ai_openai_model,
            "ai_anthropic_model": config.ai_anthropic_model,
            "ai_local_model": config.ai_local_model,
            "ai_logging_enabled": config.ai_logging_enabled,
            "ai_log_file": config.ai_log_file,
            "ai_log_level": config.ai_log_level,
            "ai_log_retention_days": config.ai_log_retention_days,
            "ai_log_mask_sensitive_data": config.ai_log_mask_sensitive_data,
            "backup_enabled": config.backup_enabled,
            "backup_suffix": config.backup_suffix,
            "output_format": config.output_format,
            "log_level": config.log_level,
            "log_file": config.log_file,
            "progress_tracking": config.progress_tracking,
            "max_memory_gb": config.max_memory_gb,
            "enable_chunked_processing": config.enable_chunked_processing,
            "enable_parallel_processing": config.enable_parallel_processing,
            "performance_monitoring": config.performance_monitoring,
            "auto_optimize_chunk_size": config.auto_optimize_chunk_size,
            "enable_validation": config.enable_validation,
            "validation_schema_file": config.validation_schema_file,
            "quality_threshold": config.quality_threshold,
            "dedupe_threshold": config.dedupe_threshold,
            "dedupe_sample_size": config.dedupe_sample_size,
            "dedupe_training_file": config.dedupe_training_file,
            "default_operations": config.default_operations,
        }

    def _dict_to_config(self, config_data: Dict[str, Any]) -> Config:
        """Convert dictionary to Config object."""
        return Config(
            default_encoding=config_data.get("default_encoding", "utf-8"),
            max_memory_usage=config_data.get("max_memory_usage", 1024 * 1024 * 1024),
            chunk_size=config_data.get("chunk_size", 10000),
            parallel_processing=config_data.get("parallel_processing", True),
            max_workers=config_data.get("max_workers", 4),
            ai_enabled=config_data.get("ai_enabled", False),
            default_llm_provider=config_data.get("default_llm_provider", "openai"),
            ai_api_keys=config_data.get("ai_api_keys", {}),
            ai_cost_limit=config_data.get("ai_cost_limit", 10.0),
            ai_suggestion_cache_size=config_data.get("ai_suggestion_cache_size", 100),
            ai_learning_enabled=config_data.get("ai_learning_enabled", True),
            ai_explanation_enabled=config_data.get("ai_explanation_enabled", True),
            ai_auto_suggest=config_data.get("ai_auto_suggest", False),
            ai_model_parameters=config_data.get(
                "ai_model_parameters",
                {"temperature": 0.7, "max_tokens": 1000, "top_p": 1.0},
            ),
            ai_openai_model=config_data.get("ai_openai_model", "gpt-4o-mini"),
            ai_anthropic_model=config_data.get(
                "ai_anthropic_model", "claude-3-5-sonnet-20241022"
            ),
            ai_local_model=config_data.get("ai_local_model", "llama3.1:8b"),
            ai_logging_enabled=config_data.get("ai_logging_enabled", True),
            ai_log_file=config_data.get("ai_log_file"),
            ai_log_level=config_data.get("ai_log_level", "INFO"),
            ai_log_retention_days=config_data.get("ai_log_retention_days", 30),
            ai_log_mask_sensitive_data=config_data.get(
                "ai_log_mask_sensitive_data", True
            ),
            backup_enabled=config_data.get("backup_enabled", True),
            backup_suffix=config_data.get("backup_suffix", ".backup"),
            output_format=config_data.get("output_format", "csv"),
            log_level=config_data.get("log_level", "INFO"),
            log_file=config_data.get("log_file"),
            progress_tracking=config_data.get("progress_tracking", True),
            max_memory_gb=config_data.get("max_memory_gb", 2.0),
            enable_chunked_processing=config_data.get(
                "enable_chunked_processing", True
            ),
            enable_parallel_processing=config_data.get(
                "enable_parallel_processing", True
            ),
            performance_monitoring=config_data.get("performance_monitoring", True),
            auto_optimize_chunk_size=config_data.get("auto_optimize_chunk_size", True),
            enable_validation=config_data.get("enable_validation", True),
            validation_schema_file=config_data.get("validation_schema_file"),
            quality_threshold=config_data.get("quality_threshold", 0.8),
            dedupe_threshold=config_data.get("dedupe_threshold", 0.5),
            dedupe_sample_size=config_data.get("dedupe_sample_size", 1000),
            dedupe_training_file=config_data.get("dedupe_training_file"),
            default_operations=config_data.get(
                "default_operations",
                ["remove_duplicates", "clean_names", "handle_missing"],
            ),
        )

    def get_env_config(self) -> Dict[str, str]:
        """Get configuration from environment variables."""
        env_config = {}

        # Map environment variables to config keys
        env_mapping = {
            "CSV_CLEANER_DEFAULT_ENCODING": "default_encoding",
            "CSV_CLEANER_CHUNK_SIZE": "chunk_size",
            "CSV_CLEANER_MAX_WORKERS": "max_workers",
            "CSV_CLEANER_AI_ENABLED": "ai_enabled",
            "CSV_CLEANER_DEFAULT_LLM_PROVIDER": "default_llm_provider",
            "CSV_CLEANER_AI_COST_LIMIT": "ai_cost_limit",
            "CSV_CLEANER_AI_LEARNING_ENABLED": "ai_learning_enabled",
            "CSV_CLEANER_AI_EXPLANATION_ENABLED": "ai_explanation_enabled",
            "CSV_CLEANER_AI_AUTO_SUGGEST": "ai_auto_suggest",
            "CSV_CLEANER_AI_OPENAI_MODEL": "ai_openai_model",
            "CSV_CLEANER_AI_ANTHROPIC_MODEL": "ai_anthropic_model",
            "CSV_CLEANER_AI_LOCAL_MODEL": "ai_local_model",
            "CSV_CLEANER_AI_LOGGING_ENABLED": "ai_logging_enabled",
            "CSV_CLEANER_AI_LOG_FILE": "ai_log_file",
            "CSV_CLEANER_AI_LOG_LEVEL": "ai_log_level",
            "CSV_CLEANER_AI_LOG_RETENTION_DAYS": "ai_log_retention_days",
            "CSV_CLEANER_AI_LOG_MASK_SENSITIVE_DATA": "ai_log_mask_sensitive_data",
            "CSV_CLEANER_LOG_LEVEL": "log_level",
            "CSV_CLEANER_LOG_FILE": "log_file",
        }

        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                env_config[config_key] = os.environ[env_var]

        # Handle AI API keys
        for provider in ["openai", "anthropic"]:
            env_key = f"CSV_CLEANER_{provider.upper()}_API_KEY"
            if env_key in os.environ:
                if "ai_api_keys" not in env_config:
                    env_config["ai_api_keys"] = {}
                env_config["ai_api_keys"][provider] = os.environ[env_key]

        return env_config

    def update_from_env(self) -> None:
        """Update configuration from environment variables."""
        env_config = self.get_env_config()
        if env_config:
            # Update config with environment values
            config_data = self._config_to_dict(self.config)
            config_data.update(env_config)
            self.config = self._dict_to_config(config_data)

    def create_default_config_file(self) -> None:
        """Create default configuration file."""
        default_config = Config()
        self.save_config(default_config)

    def get_config_path(self) -> str:
        """Get the current configuration file path."""
        return self.config_path

    def validate_ai_config(self) -> Dict[str, Any]:
        """Validate AI configuration settings.

        Returns:
            Dictionary with validation results.
        """
        validation_results = {
            "ai_enabled": self.config.ai_enabled,
            "providers_available": [],
            "api_keys_configured": [],
            "issues": [],
            "warnings": [],
        }

        # Check if AI is enabled
        if not self.config.ai_enabled:
            validation_results["warnings"].append("AI is disabled in configuration")
            return validation_results

        # Check available providers
        available_providers = ["openai", "anthropic", "local"]
        for provider in available_providers:
            if (
                provider in self.config.ai_api_keys
                and self.config.ai_api_keys[provider]
            ):
                validation_results["providers_available"].append(provider)
                validation_results["api_keys_configured"].append(provider)
            elif provider == "local":
                # Local provider doesn't need API key
                validation_results["providers_available"].append(provider)
            else:
                validation_results["warnings"].append(
                    f"No API key configured for {provider}"
                )

        # Validate cost limit
        if self.config.ai_cost_limit <= 0:
            validation_results["issues"].append("AI cost limit must be greater than 0")

        # Validate cache size
        if self.config.ai_suggestion_cache_size <= 0:
            validation_results["issues"].append(
                "AI suggestion cache size must be greater than 0"
            )

        # Validate model parameters
        if not isinstance(self.config.ai_model_parameters, dict):
            validation_results["issues"].append(
                "AI model parameters must be a dictionary"
            )
        else:
            required_params = ["temperature", "max_tokens"]
            for param in required_params:
                if param not in self.config.ai_model_parameters:
                    validation_results["issues"].append(
                        f"Missing required AI model parameter: {param}"
                    )

        return validation_results

    def set_ai_api_key(self, provider: str, api_key: str) -> None:
        """Set AI API key for a specific provider.

        Args:
            provider: Provider name (openai, anthropic, etc.).
            api_key: API key for the provider.
        """
        if not hasattr(self.config, "ai_api_keys"):
            self.config.ai_api_keys = {}

        self.config.ai_api_keys[provider] = api_key
        self.save_config(self.config)

    def get_ai_api_key(self, provider: str) -> Optional[str]:
        """Get AI API key for a specific provider.

        Args:
            provider: Provider name.

        Returns:
            API key if configured, None otherwise.
        """
        return self.config.ai_api_keys.get(provider)

    def remove_ai_api_key(self, provider: str) -> None:
        """Remove AI API key for a specific provider.

        Args:
            provider: Provider name.
        """
        if provider in self.config.ai_api_keys:
            del self.config.ai_api_keys[provider]
            self.save_config(self.config)

    def get_ai_cost_summary(self) -> Dict[str, Any]:
        """Get AI cost summary from configuration.

        Returns:
            Dictionary with AI cost information.
        """
        return {
            "cost_limit": self.config.ai_cost_limit,
            "providers_configured": list(self.config.ai_api_keys.keys()),
            "default_provider": self.config.default_llm_provider,
            "model_parameters": self.config.ai_model_parameters,
        }

    def get_feature_gate(self) -> "FeatureGate":
        """Get the feature gate instance.

        Returns:
            FeatureGate instance for the current configuration.
        """
        return self.feature_gate
