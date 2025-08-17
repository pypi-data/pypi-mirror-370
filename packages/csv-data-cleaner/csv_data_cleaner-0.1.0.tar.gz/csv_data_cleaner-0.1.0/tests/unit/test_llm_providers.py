"""
TEST SUITE: llm_providers.py
PURPOSE: Test LLM provider system with multiple providers and fallback logic
SCOPE: LLMResponse, BaseLLMProvider, OpenAIProvider, AnthropicProvider, LocalProvider, LLMProviderManager
DEPENDENCIES: Mock OpenAI/Anthropic clients, time module, AI logging manager
"""

import pytest
import time
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from csv_cleaner.core.llm_providers import (
    LLMResponse, BaseLLMProvider, OpenAIProvider, AnthropicProvider,
    LocalProvider, LLMProviderManager
)


class TestLLMResponse:
    """Test LLMResponse dataclass functionality."""

    def test_llm_response_creation_valid(self):
        """Test creating LLMResponse with valid parameters."""
        response = LLMResponse(
            content="Test response",
            model="gpt-3.5-turbo",
            tokens_used=100,
            cost_usd=0.002,
            response_time_seconds=1.5
        )

        assert response.content == "Test response"
        assert response.model == "gpt-3.5-turbo"
        assert response.tokens_used == 100
        assert response.cost_usd == 0.002
        assert response.response_time_seconds == 1.5
        assert response.success is True
        assert response.error_message is None

    def test_llm_response_creation_with_error(self):
        """Test creating LLMResponse with error information."""
        response = LLMResponse(
            content="",
            model="gpt-3.5-turbo",
            tokens_used=0,
            cost_usd=0.0,
            response_time_seconds=0.5,
            success=False,
            error_message="API rate limit exceeded"
        )

        assert response.content == ""
        assert response.success is False
        assert response.error_message == "API rate limit exceeded"
        assert response.tokens_used == 0
        assert response.cost_usd == 0.0


class TestBaseLLMProvider:
    """Test BaseLLMProvider abstract class functionality."""

    def test_base_provider_initialization(self):
        """Test BaseLLMProvider initialization."""
        # Create a concrete implementation for testing
        class TestProvider(BaseLLMProvider):
            def generate(self, prompt: str, **kwargs):
                return LLMResponse(
                    content="test",
                    model="test",
                    tokens_used=10,
                    cost_usd=0.001,
                    response_time_seconds=0.1
                )

            def is_available(self) -> bool:
                return True

        test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
        provider = TestProvider(api_key=test_api_key, test_param="value")

        assert provider.api_key == test_api_key
        assert provider.config["test_param"] == "value"
        assert provider.total_tokens_used == 0
        assert provider.total_cost_usd == 0.0
        assert provider.request_count == 0

    def test_get_cost_summary(self):
        """Test cost summary generation."""
        class TestProvider(BaseLLMProvider):
            def generate(self, prompt: str, **kwargs):
                return LLMResponse(
                    content="test",
                    model="test",
                    tokens_used=10,
                    cost_usd=0.001,
                    response_time_seconds=0.1
                )

            def is_available(self) -> bool:
                return True

        provider = TestProvider()
        provider.total_tokens_used = 100
        provider.total_cost_usd = 0.01
        provider.request_count = 5

        summary = provider.get_cost_summary()

        assert summary["total_tokens_used"] == 100
        assert summary["total_cost_usd"] == 0.01
        assert summary["request_count"] == 5
        assert summary["average_cost_per_request"] == 0.002

    def test_get_cost_summary_zero_requests(self):
        """Test cost summary with zero requests."""
        class TestProvider(BaseLLMProvider):
            def generate(self, prompt: str, **kwargs):
                return LLMResponse(
                    content="test",
                    model="test",
                    tokens_used=10,
                    cost_usd=0.001,
                    response_time_seconds=0.1
                )

            def is_available(self) -> bool:
                return True

        provider = TestProvider()

        summary = provider.get_cost_summary()

        assert summary["average_cost_per_request"] == 0.0


class TestOpenAIProvider:
    """Test OpenAIProvider functionality."""

    def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization."""
        test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
        provider = OpenAIProvider(api_key=test_api_key)
        assert provider.api_key == test_api_key
        assert provider.model == "gpt-4o-mini"  # New default

    def test_openai_provider_with_custom_model(self):
        """Test OpenAI provider with custom model."""
        test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
        provider = OpenAIProvider(api_key=test_api_key, model="gpt-4o")
        assert provider.model == "gpt-4o"

    def test_openai_generate_success(self):
        """Test successful OpenAI generation."""
        # Mock the OpenAI import at the module level
        with patch('csv_cleaner.core.llm_providers.OpenAI', create=True) as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response

            # Mock the cost estimator
            with patch('csv_cleaner.core.ai_utils.AICostEstimator') as mock_cost_estimator_class:
                mock_cost_estimator = MagicMock()
                mock_cost_estimator.estimate_cost.return_value = 0.01
                mock_cost_estimator_class.return_value = mock_cost_estimator

                # Create provider after mocking
                test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
                provider = OpenAIProvider(api_key=test_api_key)
                # Manually set the client to our mock
                provider.client = mock_client
                response = provider.generate("Test prompt")

                assert response.content == "Test response"
                assert response.model == "gpt-4o-mini"  # New default
                assert response.tokens_used == 100
                assert response.success is True

    def test_openai_generate_not_available(self):
        """Test OpenAI generation when not available."""
        provider = OpenAIProvider()  # No API key
        response = provider.generate("Test prompt")

        assert response.success is False
        assert response.error_message == "OpenAI provider not available"
        assert response.model == "gpt-4o-mini"  # New default

    def test_openai_generate_api_error(self):
        """Test OpenAI generation with API error."""
        with patch('builtins.__import__') as mock_import:
            # Mock the OpenAI import
            mock_openai = MagicMock()
            mock_client = MagicMock()
            mock_openai.OpenAI.return_value = mock_client

            def side_effect(name, *args, **kwargs):
                if name == 'openai':
                    return mock_openai
                return __import__(name, *args, **kwargs)
            mock_import.side_effect = side_effect

            # Mock API error
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
            provider = OpenAIProvider(api_key=test_api_key)
            response = provider.generate("Test prompt")

            assert response.success is False
            assert "API Error" in response.error_message
            assert response.model == "gpt-4o-mini"  # New default

    def test_openai_generate_custom_parameters(self):
        """Test OpenAI generation with custom parameters."""
        # Mock the OpenAI import at the module level
        with patch('csv_cleaner.core.llm_providers.OpenAI', create=True) as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response

            # Mock the cost estimator
            with patch('csv_cleaner.core.ai_utils.AICostEstimator') as mock_cost_estimator_class:
                mock_cost_estimator = MagicMock()
                mock_cost_estimator.estimate_cost.return_value = 0.01
                mock_cost_estimator_class.return_value = mock_cost_estimator

                # Create provider after mocking
                test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
                provider = OpenAIProvider(api_key=test_api_key, model="gpt-4o")
                # Manually set the client to our mock
                provider.client = mock_client
                response = provider.generate("Test prompt", temperature=0.5, max_tokens=500)

                assert response.content == "Test response"
                assert response.model == "gpt-4o"
                assert response.success is True

                # Verify custom parameters were passed
                mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['temperature'] == 0.5
            assert call_args[1]['max_tokens'] == 500


class TestAnthropicProvider:
    """Test AnthropicProvider functionality."""

    def test_anthropic_provider_initialization(self):
        """Test Anthropic provider initialization."""
        test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
        provider = AnthropicProvider(api_key=test_api_key)
        assert provider.api_key == test_api_key
        assert provider.model == "claude-3-5-sonnet-20241022"  # New default

    def test_anthropic_provider_with_custom_model(self):
        """Test Anthropic provider with custom model."""
        test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
        provider = AnthropicProvider(api_key=test_api_key, model="claude-3-haiku-20240307")
        assert provider.model == "claude-3-haiku-20240307"

    def test_anthropic_generate_success(self):
        """Test successful Anthropic generation."""
        with patch('csv_cleaner.core.llm_providers.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.Anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Test response"
            mock_response.usage.input_tokens = 50
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response

            test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
            provider = AnthropicProvider(api_key=test_api_key)
            response = provider.generate("Test prompt")

            assert response.content == "Test response"
            assert response.model == "claude-3-5-sonnet-20241022"  # New default
            assert response.tokens_used == 100
            assert response.success is True

    @patch('builtins.__import__')
    def test_anthropic_provider_initialization_no_key(self, mock_import):
        """Test Anthropic provider initialization without API key."""
        def side_effect(name, *args, **kwargs):
            if name == 'anthropic':
                raise ImportError("anthropic not installed")
            return __import__(name, *args, **kwargs)
        mock_import.side_effect = side_effect

        provider = AnthropicProvider()

        assert provider.api_key is None
        assert provider.client is None
        assert provider.is_available() is False

    def test_anthropic_generate_success(self):
        """Test successful Anthropic generation."""
        # Mock the anthropic import at the module level
        with patch('csv_cleaner.core.llm_providers.anthropic', create=True) as mock_anthropic:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "Generated response"
            mock_response.usage.input_tokens = 50
            mock_response.usage.output_tokens = 100
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client

            # Mock the cost estimator
            with patch('csv_cleaner.core.ai_utils.AICostEstimator') as mock_cost_estimator_class:
                mock_cost_estimator = MagicMock()
                mock_cost_estimator.estimate_cost.return_value = 0.01
                mock_cost_estimator_class.return_value = mock_cost_estimator

                # Create provider after mocking
                test_api_key = os.getenv("TEST_API_KEY", "test-key-for-testing-only")
                provider = AnthropicProvider(api_key=test_api_key)
                # Manually set the client to our mock
                provider.client = mock_client

                with patch('time.time', side_effect=[100.0, 101.2]):
                    response = provider.generate("Test prompt")

                assert response.content == "Generated response"
                assert response.model == "claude-3-5-sonnet-20241022"
                assert response.tokens_used == 150
                assert response.response_time_seconds == pytest.approx(1.2)
                assert response.success is True


class TestLocalProvider:
    """Test LocalProvider functionality."""

    def test_local_provider_initialization(self):
        """Test Local provider initialization."""
        provider = LocalProvider()
        assert provider.model == "llama3.1:8b"  # New default

    def test_local_provider_with_custom_model(self):
        """Test Local provider with custom model."""
        provider = LocalProvider(model="llama3.1:70b")
        assert provider.model == "llama3.1:70b"

    def test_local_provider_availability(self):
        """Test Local provider availability check."""
        # Mock the ollama import at the module level
        with patch('csv_cleaner.core.llm_providers.ollama', create=True) as mock_ollama:
            mock_ollama.list.return_value = {'models': [{'name': 'llama3.1:8b'}]}

            # Create provider after mocking
            provider = LocalProvider()
            # Manually set the client to our mock
            provider.client = mock_ollama
            assert provider.model == "llama3.1:8b"
            assert provider.is_available() is True

    def test_local_generate_success(self):
        """Test successful Local generation."""
        # Mock the ollama import at the module level
        with patch('csv_cleaner.core.llm_providers.ollama', create=True) as mock_ollama:
            mock_ollama.list.return_value = {'models': [{'name': 'llama3.1:8b'}]}
            mock_ollama.generate.return_value = {'response': 'Test response'}

            # Create provider after mocking
            provider = LocalProvider()
            # Manually set the client to our mock
            provider.client = mock_ollama
            response = provider.generate("Test prompt")

            assert response.content == "Test response"
            assert response.model == "llama3.1:8b"  # New default
            assert response.success is True


class TestLLMProviderManager:
    """Test LLMProviderManager functionality."""

    def test_provider_manager_initialization(self):
        """Test LLM provider manager initialization."""
        config = {
            'default_llm_provider': 'openai',
            'ai_api_keys': {'openai': 'test-key'},
            'ai_openai_model': 'gpt-4o-mini',
            'ai_anthropic_model': 'claude-3-5-sonnet-20241022',
            'ai_local_model': 'llama3.1:8b'
        }

        manager = LLMProviderManager(config)
        assert manager.default_provider == 'openai'
        assert 'openai' in manager.providers

    def test_manager_initialization_no_providers(self):
        """Test manager initialization with no available providers."""
        config = {
            'default_llm_provider': 'openai',
            'ai_api_keys': {},
            'ai_openai_model': 'gpt-4o-mini',
            'ai_anthropic_model': 'claude-3-5-sonnet-20241022',
            'ai_local_model': 'llama3.1:8b'
        }

        manager = LLMProviderManager(config)
        assert manager.get_available_providers() == []

    def test_manager_generate_with_openai(self):
        """Test manager generation with OpenAI provider."""
        config = {
            'default_llm_provider': 'openai',
            'ai_api_keys': {'openai': 'test-key'},
            'ai_openai_model': 'gpt-4o-mini',
            'ai_anthropic_model': 'claude-3-5-sonnet-20241022',
            'ai_local_model': 'llama3.1:8b'
        }

        # Mock the OpenAI import at the module level
        with patch('csv_cleaner.core.llm_providers.OpenAI', create=True) as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response

            manager = LLMProviderManager(config)
            # Manually set the client for the OpenAI provider
            if 'openai' in manager.providers:
                manager.providers['openai'].client = mock_client
            response = manager.generate("Test prompt")

            assert response.content == "Test response"
            assert response.model == "gpt-4o-mini"
            assert response.success is True

    def test_manager_initialization_with_anthropic(self):
        """Test manager initialization with Anthropic provider."""
        config = {
            'default_llm_provider': 'anthropic',
            'ai_api_keys': {'anthropic': 'test-key'},
            'ai_openai_model': 'gpt-4o-mini',
            'ai_anthropic_model': 'claude-3-5-sonnet-20241022',
            'ai_local_model': 'llama3.1:8b'
        }

        # Mock the anthropic import at the module level
        with patch('csv_cleaner.core.llm_providers.anthropic', create=True) as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.Anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Test response"
            mock_response.usage.input_tokens = 50
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response

            manager = LLMProviderManager(config)
            # Manually set the client for the Anthropic provider
            if 'anthropic' in manager.providers:
                manager.providers['anthropic'].client = mock_client
            response = manager.generate("Test prompt")

            assert response.content == "Test response"
            assert response.model == "claude-3-5-sonnet-20241022"
            assert response.success is True

    def test_manager_generate_with_fallback(self):
        """Test manager generation with fallback logic."""
        config = {
            'default_llm_provider': 'openai',
            'ai_api_keys': {'openai': 'test-key', 'anthropic': 'test-key'},
            'ai_openai_model': 'gpt-4o-mini',
            'ai_anthropic_model': 'claude-3-5-sonnet-20241022',
            'ai_local_model': 'llama3.1:8b'
        }

        # Mock the OpenAI and anthropic imports at the module level
        with patch('csv_cleaner.core.llm_providers.OpenAI', create=True) as mock_openai, \
             patch('csv_cleaner.core.llm_providers.anthropic', create=True) as mock_anthropic:

            # Mock OpenAI failure
            mock_openai.side_effect = Exception("OpenAI failed")

            # Mock Anthropic success
            mock_client = MagicMock()
            mock_anthropic.Anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Fallback response"
            mock_response.usage.input_tokens = 50
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response

            manager = LLMProviderManager(config)
            # Manually set the client for the Anthropic provider
            if 'anthropic' in manager.providers:
                manager.providers['anthropic'].client = mock_client
            response = manager.generate("Test prompt")

            assert response.content == "Fallback response"
            assert response.model == "claude-3-5-sonnet-20241022"
            assert response.success is True

    def test_manager_generate_with_fallback_logic(self):
        """Test generation with fallback logic when primary provider fails."""
        config = {
            'default_llm_provider': 'openai',
            'ai_api_keys': {'openai': 'test-key', 'anthropic': 'test-key2'},
            'ai_openai_model': 'gpt-4o-mini',
            'ai_anthropic_model': 'claude-3-5-sonnet-20241022',
            'ai_local_model': 'llama3.1:8b'
        }

        with patch('csv_cleaner.core.llm_providers.OpenAIProvider') as mock_openai_class, \
             patch('csv_cleaner.core.llm_providers.AnthropicProvider') as mock_anthropic_class:

            # Primary provider fails
            mock_openai_provider = Mock()
            mock_openai_provider.is_available.return_value = True
            mock_openai_provider.generate.return_value = LLMResponse(
                content="",
                model="gpt-4o-mini",
                tokens_used=0,
                cost_usd=0.0,
                response_time_seconds=0.5,
                success=False,
                error_message="Rate limit exceeded"
            )
            mock_openai_class.return_value = mock_openai_provider

            # Fallback provider succeeds
            mock_anthropic_provider = Mock()
            mock_anthropic_provider.is_available.return_value = True
            mock_anthropic_provider.generate.return_value = LLMResponse(
                content="Fallback success",
                model="claude-3-5-sonnet-20241022",
                tokens_used=100,
                cost_usd=0.002,
                response_time_seconds=1.0
            )
            mock_anthropic_class.return_value = mock_anthropic_provider

            manager = LLMProviderManager(config)

            response = manager.generate("Test prompt")

            assert response.success is True
            assert response.content == "Fallback success"

    def test_manager_get_cost_summary(self):
        """Test cost summary across all providers."""
        config = {
            'default_llm_provider': 'openai',
            'ai_api_keys': {'openai': 'test-key', 'anthropic': 'test-key2'},
            'ai_openai_model': 'gpt-4o-mini',
            'ai_anthropic_model': 'claude-3-5-sonnet-20241022',
            'ai_local_model': 'llama3.1:8b'
        }

        with patch('csv_cleaner.core.llm_providers.OpenAIProvider') as mock_openai_class, \
             patch('csv_cleaner.core.llm_providers.AnthropicProvider') as mock_anthropic_class:

            mock_openai_provider = Mock()
            mock_openai_provider.get_cost_summary.return_value = {
                'total_tokens_used': 100,
                'total_cost_usd': 0.002,
                'request_count': 2,
                'average_cost_per_request': 0.001
            }
            mock_openai_class.return_value = mock_openai_provider

            mock_anthropic_provider = Mock()
            mock_anthropic_provider.get_cost_summary.return_value = {
                'total_tokens_used': 150,
                'total_cost_usd': 0.003,
                'request_count': 1,
                'average_cost_per_request': 0.003
            }
            mock_anthropic_class.return_value = mock_anthropic_provider

            manager = LLMProviderManager(config)

            summary = manager.get_cost_summary()

            assert summary['total_tokens_used'] == 250
            assert summary['total_cost_usd'] == 0.005
            assert summary['total_requests'] == 3
            assert 'openai' in summary['providers']
            assert 'anthropic' in summary['providers']
