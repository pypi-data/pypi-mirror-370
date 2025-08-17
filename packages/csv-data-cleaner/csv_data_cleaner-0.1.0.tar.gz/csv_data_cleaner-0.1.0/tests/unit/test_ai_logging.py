"""
Unit tests for AI logging functionality.
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch

from csv_cleaner.core.ai_logging import AILoggingManager, AILogEntry
from csv_cleaner.core.config import Config
from csv_cleaner.core.llm_providers import LLMResponse


class TestAILoggingManager:
    """Test AI logging manager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.config.ai_logging_enabled = True
        self.config.ai_log_mask_sensitive_data = True

        # Create temporary log file
        self.temp_dir = tempfile.mkdtemp()
        self.config.ai_log_file = str(Path(self.temp_dir) / "test_ai.log")

        self.logging_manager = AILoggingManager(self.config)

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, 'logging_manager'):
            self.logging_manager.shutdown()

        # Clean up temporary files
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test AI logging manager initialization."""
        assert self.logging_manager.config == self.config
        assert self.logging_manager.log_file_path == Path(self.config.ai_log_file)
        assert self.logging_manager.log_thread is not None

    def test_generate_correlation_id(self):
        """Test correlation ID generation."""
        correlation_id = self.logging_manager.generate_correlation_id()
        assert correlation_id.startswith("ai_")
        assert len(correlation_id) > 10

    def test_mask_sensitive_data(self):
        """Test sensitive data masking."""
        # Test API key masking
        text_with_key = "Here is my API key: sk-1234567890abcdef1234567890abcdef12345678"
        masked_text = self.logging_manager.mask_sensitive_data(text_with_key)
        assert "sk-***MASKED***" in masked_text
        assert "sk-1234567890abcdef1234567890abcdef12345678" not in masked_text

        # Test with no sensitive data
        normal_text = "This is normal text without any sensitive data"
        masked_text = self.logging_manager.mask_sensitive_data(normal_text)
        assert masked_text == normal_text

    def test_log_ai_interaction(self):
        """Test AI interaction logging."""
        # Create mock response
        mock_response = Mock(spec=LLMResponse)
        mock_response.content = "This is a test response"
        mock_response.model = "gpt-3.5-turbo"
        mock_response.tokens_used = 100
        mock_response.cost_usd = 0.002
        mock_response.response_time_seconds = 1.5
        mock_response.success = True
        mock_response.error_message = None

        # Test logging
        prompt = "Test prompt"
        context = {
            'operation_type': 'test_operation',
            'metadata': {'test_key': 'test_value'}
        }

        correlation_id = self.logging_manager.log_ai_interaction(prompt, mock_response, context)
        assert correlation_id != ""

        # Wait for log to be written
        time.sleep(0.1)

        # Check if log file was created and contains entry
        assert self.logging_manager.log_file_path.exists()

        with open(self.logging_manager.log_file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0

            # Parse the last log entry
            log_entry = json.loads(lines[-1])
            assert log_entry['correlation_id'] == correlation_id
            assert log_entry['prompt'] == prompt
            assert log_entry['response'] == mock_response.content
            assert log_entry['operation_type'] == 'test_operation'
            assert log_entry['metadata']['test_key'] == 'test_value'

    def test_log_ai_interaction_disabled(self):
        """Test AI interaction logging when disabled."""
        self.config.ai_logging_enabled = False
        logging_manager = AILoggingManager(self.config)

        mock_response = Mock(spec=LLMResponse)
        mock_response.content = "Test response"
        mock_response.model = "gpt-3.5-turbo"
        mock_response.tokens_used = 100
        mock_response.cost_usd = 0.002
        mock_response.response_time_seconds = 1.5
        mock_response.success = True
        mock_response.error_message = None

        correlation_id = logging_manager.log_ai_interaction("Test prompt", mock_response, {})
        assert correlation_id == ""

        logging_manager.shutdown()

    def test_get_ai_logs_summary(self):
        """Test AI logs summary generation."""
        # Add some test log entries
        mock_response = Mock(spec=LLMResponse)
        mock_response.content = "Test response 1"
        mock_response.model = "gpt-3.5-turbo"
        mock_response.tokens_used = 100
        mock_response.cost_usd = 0.002
        mock_response.response_time_seconds = 1.0
        mock_response.success = True
        mock_response.error_message = None

        context = {
            'operation_type': 'test_operation',
            'metadata': {}
        }

        self.logging_manager.log_ai_interaction("Test prompt 1", mock_response, context)

        # Add another entry
        mock_response2 = Mock(spec=LLMResponse)
        mock_response2.content = "Test response 2"
        mock_response2.model = "gpt-4"
        mock_response2.tokens_used = 200
        mock_response2.cost_usd = 0.004
        mock_response2.response_time_seconds = 2.0
        mock_response2.success = True
        mock_response2.error_message = None

        self.logging_manager.log_ai_interaction("Test prompt 2", mock_response2, context)

        # Wait for logs to be written
        time.sleep(0.1)

        # Get summary
        summary = self.logging_manager.get_ai_logs_summary(days=7)

        assert summary['total_interactions'] >= 2
        assert summary['total_cost_usd'] >= 0.006
        assert summary['total_tokens_used'] >= 300
        assert summary['success_rate'] == 1.0
        assert summary['average_response_time'] >= 1.0

    def test_cleanup_old_logs(self):
        """Test cleanup of old log entries."""
        # This test would require more complex setup with time manipulation
        # For now, just test that the method doesn't crash
        self.logging_manager.cleanup_old_logs(retention_days=1)
        # Should not raise any exceptions

    def test_shutdown(self):
        """Test graceful shutdown."""
        self.logging_manager.shutdown()
        # Should not raise any exceptions


class TestAILogEntry:
    """Test AI log entry dataclass."""

    def test_ai_log_entry_creation(self):
        """Test AILogEntry creation."""
        entry = AILogEntry(
            correlation_id="test_id",
            timestamp=time.time(),
            operation_type="test_operation",
            prompt="Test prompt",
            response="Test response",
            provider="openai",
            model="gpt-3.5-turbo",
            tokens_used=100,
            cost_usd=0.002,
            response_time_seconds=1.5,
            success=True,
            error_message=None,
            metadata={'test': 'value'}
        )

        assert entry.correlation_id == "test_id"
        assert entry.operation_type == "test_operation"
        assert entry.prompt == "Test prompt"
        assert entry.response == "Test response"
        assert entry.provider == "openai"
        assert entry.model == "gpt-3.5-turbo"
        assert entry.tokens_used == 100
        assert entry.cost_usd == 0.002
        assert entry.response_time_seconds == 1.5
        assert entry.success is True
        assert entry.error_message is None
        assert entry.metadata['test'] == 'value'
