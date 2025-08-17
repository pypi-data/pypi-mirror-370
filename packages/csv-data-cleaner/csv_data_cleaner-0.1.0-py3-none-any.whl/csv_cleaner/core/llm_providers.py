"""
LLM Provider system for AI integration.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

from .ai_logging import AILoggingManager

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    model: str
    tokens_used: int
    cost_usd: float
    response_time_seconds: float
    success: bool = True
    error_message: Optional[str] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the LLM provider.

        Args:
            api_key: API key for the provider.
            **kwargs: Additional provider-specific configuration.
        """
        self.api_key = api_key
        self.config = kwargs
        self.total_tokens_used = 0
        self.total_cost_usd = 0.0
        self.request_count = 0

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            prompt: The input prompt.
            **kwargs: Additional generation parameters.

        Returns:
            LLMResponse with the generated content.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured.

        Returns:
            True if the provider is available.
        """
        pass

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary for this provider.

        Returns:
            Dictionary with cost statistics.
        """
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_cost_usd": self.total_cost_usd,
            "request_count": self.request_count,
            "average_cost_per_request": self.total_cost_usd
            / max(self.request_count, 1),
        }


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", **kwargs
    ):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key.
            model: Model name to use (default: gpt-4o-mini).
            **kwargs: Additional configuration.
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not provided")
        except ImportError as e:
            logger.warning(f"OpenAI library not installed: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None and self.api_key is not None

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response using OpenAI GPT.

        Args:
            prompt: The input prompt.
            **kwargs: Additional generation parameters.

        Returns:
            LLMResponse with the generated content.
        """
        if not self.is_available():
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                cost_usd=0.0,
                response_time_seconds=0.0,
                success=False,
                error_message="OpenAI provider not available",
            )

        start_time = time.time()

        try:
            # Use configured model or override from kwargs
            model = kwargs.get("model", self.model)
            max_tokens = kwargs.get("max_tokens", 1000)
            temperature = kwargs.get("temperature", 0.7)

            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            response_time = time.time() - start_time

            # Calculate cost using centralized cost estimator
            from .ai_utils import AICostEstimator

            cost_estimator = AICostEstimator()
            cost_usd = cost_estimator.estimate_cost(
                model, tokens_used, 0
            )  # Approximate

            # Update statistics
            self.total_tokens_used += tokens_used
            self.total_cost_usd += cost_usd
            self.request_count += 1

            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                response_time_seconds=response_time,
            )

        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"OpenAI generation failed: {e}")
            return LLMResponse(
                content="",
                model=kwargs.get("model", self.model),
                tokens_used=0,
                cost_usd=0.0,
                response_time_seconds=response_time,
                success=False,
                error_message=str(e),
            )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs,
    ):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key.
            model: Model name to use (default: claude-3-5-sonnet-20241022).
            **kwargs: Additional configuration.
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Anthropic client."""
        try:
            import anthropic

            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Anthropic client initialized successfully")
            else:
                logger.warning("Anthropic API key not provided")
        except ImportError:
            logger.warning("Anthropic library not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")

    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return self.client is not None and self.api_key is not None

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response using Anthropic Claude.

        Args:
            prompt: The input prompt.
            **kwargs: Additional generation parameters.

        Returns:
            LLMResponse with the generated content.
        """
        if not self.is_available():
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                cost_usd=0.0,
                response_time_seconds=0.0,
                success=False,
                error_message="Anthropic provider not available",
            )

        start_time = time.time()

        try:
            # Use configured model or override from kwargs
            model = kwargs.get("model", self.model)
            max_tokens = kwargs.get("max_tokens", 1000)

            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            response_time = time.time() - start_time

            # Calculate cost using centralized cost estimator
            from .ai_utils import AICostEstimator

            cost_estimator = AICostEstimator()
            cost_usd = cost_estimator.estimate_cost(
                model, response.usage.input_tokens, response.usage.output_tokens
            )

            # Update statistics
            self.total_tokens_used += tokens_used
            self.total_cost_usd += cost_usd
            self.request_count += 1

            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                response_time_seconds=response_time,
            )

        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Anthropic generation failed: {e}")
            return LLMResponse(
                content="",
                model=kwargs.get("model", self.model),
                tokens_used=0,
                cost_usd=0.0,
                response_time_seconds=response_time,
                success=False,
                error_message=str(e),
            )


class LocalProvider(BaseLLMProvider):
    """Local model provider using Ollama."""

    def __init__(self, model: str = "llama3.1:8b", **kwargs):
        """Initialize local provider.

        Args:
            model: Name of the local model to use (default: llama3.1:8b).
            **kwargs: Additional configuration.
        """
        super().__init__(**kwargs)
        self.model = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Ollama client."""
        try:
            import ollama

            self.client = ollama
            logger.info(f"Ollama client initialized with model: {self.model}")
        except ImportError:
            logger.warning("Ollama library not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")

    def is_available(self) -> bool:
        """Check if local provider is available."""
        if self.client is None:
            return False

        try:
            # Check if model is available
            models = self.client.list()
            return any(model["name"] == self.model for model in models["models"])
        except Exception:
            return False

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response using local model.

        Args:
            prompt: The input prompt.
            **kwargs: Additional generation parameters.

        Returns:
            LLMResponse with the generated content.
        """
        if not self.is_available():
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                cost_usd=0.0,
                response_time_seconds=0.0,
                success=False,
                error_message="Local provider not available",
            )

        start_time = time.time()

        try:
            response = self.client.generate(model=self.model, prompt=prompt, **kwargs)

            content = response["response"]
            response_time = time.time() - start_time

            # Local models have no cost
            cost_usd = 0.0
            tokens_used = len(prompt.split()) + len(content.split())  # Approximate

            # Update statistics
            self.total_tokens_used += tokens_used
            self.total_cost_usd += cost_usd
            self.request_count += 1

            return LLMResponse(
                content=content,
                model=self.model,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                response_time_seconds=response_time,
            )

        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Local model generation failed: {e}")
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                cost_usd=0.0,
                response_time_seconds=response_time,
                success=False,
                error_message=str(e),
            )


class LLMProviderManager:
    """Manages multiple LLM providers with fallback logic."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the provider manager.

        Args:
            config: Configuration dictionary with provider settings.
        """
        self.providers = {}
        self.default_provider = config.get("default_llm_provider", "openai")
        self.ai_logging_manager = None
        self._initialize_providers(config)
        self._initialize_ai_logging(config)

    def _initialize_providers(self, config: Dict[str, Any]) -> None:
        """Initialize available providers."""
        ai_api_keys = config.get("ai_api_keys", {})

        # Initialize OpenAI
        if "openai" in ai_api_keys:
            try:
                model = config.get("ai_openai_model", "gpt-4o-mini")
                self.providers["openai"] = OpenAIProvider(
                    api_key=ai_api_keys["openai"], model=model
                )
                logger.info(f"OpenAI provider initialized with model: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {e}")

        # Initialize Anthropic
        if "anthropic" in ai_api_keys:
            try:
                model = config.get("ai_anthropic_model", "claude-3-5-sonnet-20241022")
                self.providers["anthropic"] = AnthropicProvider(
                    api_key=ai_api_keys["anthropic"], model=model
                )
                logger.info(f"Anthropic provider initialized with model: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic provider: {e}")

        # Initialize Local provider
        try:
            model = config.get("ai_local_model", "llama3.1:8b")
            self.providers["local"] = LocalProvider(model=model)
            logger.info(f"Local provider initialized with model: {model}")
        except Exception as e:
            logger.warning(f"Failed to initialize Local provider: {e}")

    def _initialize_ai_logging(self, config: Dict[str, Any]) -> None:
        """Initialize AI logging manager.

        Args:
            config: Configuration dictionary.
        """
        try:
            # Create a Config object for AI logging
            from .config import Config

            config_obj = Config()

            # Update config with AI logging settings
            if "ai_logging_enabled" in config:
                config_obj.ai_logging_enabled = config["ai_logging_enabled"]
            if "ai_log_file" in config:
                config_obj.ai_log_file = config["ai_log_file"]
            if "ai_log_level" in config:
                config_obj.ai_log_level = config["ai_log_level"]
            if "ai_log_retention_days" in config:
                config_obj.ai_log_retention_days = config["ai_log_retention_days"]
            if "ai_log_mask_sensitive_data" in config:
                config_obj.ai_log_mask_sensitive_data = config[
                    "ai_log_mask_sensitive_data"
                ]

            self.ai_logging_manager = AILoggingManager(config_obj)
            logger.info("AI logging manager initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize AI logging manager: {e}")

    def get_available_providers(self) -> List[str]:
        """Get list of available providers.

        Returns:
            List of available provider names.
        """
        return [
            name for name, provider in self.providers.items() if provider.is_available()
        ]

    def generate(
        self, prompt: str, provider_name: Optional[str] = None, **kwargs
    ) -> LLMResponse:
        """Generate response using specified or fallback provider.

        Args:
            prompt: The input prompt.
            provider_name: Name of the provider to use. If None, uses default or fallback.
            **kwargs: Additional generation parameters.

        Returns:
            LLMResponse with the generated content.
        """
        available_providers = self.get_available_providers()

        if not available_providers:
            return LLMResponse(
                content="",
                model="none",
                tokens_used=0,
                cost_usd=0.0,
                response_time_seconds=0.0,
                success=False,
                error_message="No LLM providers available",
            )

        # Determine which provider to use
        if provider_name and provider_name in available_providers:
            target_provider = provider_name
        elif self.default_provider in available_providers:
            target_provider = self.default_provider
        else:
            target_provider = available_providers[0]

        # Prepare context for AI logging
        context = {
            "operation_type": kwargs.get("operation_type", "unknown"),
            "metadata": kwargs.get("metadata", {}),
        }

        # Try the target provider
        response = self.providers[target_provider].generate(prompt, **kwargs)

        # If failed and we have other providers, try fallback
        if not response.success and len(available_providers) > 1:
            for fallback_provider in available_providers:
                if fallback_provider != target_provider:
                    logger.info(f"Trying fallback provider: {fallback_provider}")
                    response = self.providers[fallback_provider].generate(
                        prompt, **kwargs
                    )
                    if response.success:
                        break

        # Log AI interaction if logging is enabled
        if self.ai_logging_manager:
            try:
                self.ai_logging_manager.log_ai_interaction(prompt, response, context)
            except Exception as e:
                logger.warning(f"Failed to log AI interaction: {e}")

        return response

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary across all providers.

        Returns:
            Dictionary with cost statistics for all providers.
        """
        summary = {
            "total_cost_usd": 0.0,
            "total_tokens_used": 0,
            "total_requests": 0,
            "providers": {},
        }

        for name, provider in self.providers.items():
            provider_summary = provider.get_cost_summary()
            summary["providers"][name] = provider_summary
            summary["total_cost_usd"] += provider_summary["total_cost_usd"]
            summary["total_tokens_used"] += provider_summary["total_tokens_used"]
            summary["total_requests"] += provider_summary["request_count"]

        return summary
