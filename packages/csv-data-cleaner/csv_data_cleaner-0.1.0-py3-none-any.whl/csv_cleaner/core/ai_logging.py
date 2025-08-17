"""
AI Logging Manager for comprehensive prompt and response logging.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import threading
from queue import Queue, Empty
import re

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class AILogEntry:
    """Represents a single AI interaction log entry."""

    correlation_id: str
    timestamp: float
    operation_type: str  # 'suggestion', 'analysis', 'library_selection', etc.
    prompt: str
    response: str
    provider: str
    model: str
    tokens_used: int
    cost_usd: float
    response_time_seconds: float
    success: bool
    error_message: Optional[str]
    metadata: Dict[str, Any]  # Dataset info, operation context, etc.


class AILoggingManager:
    """Manages AI interaction logging with structured metadata."""

    def __init__(self, config: Config):
        """Initialize the AI logging manager.

        Args:
            config: Configuration object with AI logging settings.
        """
        self.config = config
        self.log_queue = Queue(maxsize=1000)
        self.log_thread = None
        self.log_file_path = self._get_log_file_path()
        self._start_logging_thread()

    def _get_log_file_path(self) -> Path:
        """Get the AI log file path.

        Returns:
            Path to the AI log file.
        """
        if self.config.ai_log_file:
            log_path = Path(self.config.ai_log_file)
        else:
            # Default to user's home directory
            log_dir = Path.home() / ".csv-cleaner" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "ai_interactions.log"

        return log_path

    def _start_logging_thread(self) -> None:
        """Start the background logging thread."""
        if self.config.ai_logging_enabled:
            self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
            self.log_thread.start()

    def _log_worker(self) -> None:
        """Background worker for writing log entries."""
        while True:
            try:
                entry = self.log_queue.get(timeout=1.0)
                if entry is None:  # Shutdown signal
                    break
                self._write_log_entry(entry)
                self.log_queue.task_done()
            except Empty:
                # Timeout is expected when no entries are available
                continue
            except Exception as e:
                logger.error(f"Error in AI logging worker: {e}")

    def _write_log_entry(self, entry: AILogEntry) -> None:
        """Write a log entry to the log file.

        Args:
            entry: The log entry to write.
        """
        try:
            # Ensure log directory exists
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert entry to dictionary and format as JSON
            entry_dict = asdict(entry)
            entry_dict["timestamp_iso"] = datetime.fromtimestamp(
                entry.timestamp
            ).isoformat()

            log_line = json.dumps(entry_dict, ensure_ascii=False)

            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")

        except Exception as e:
            logger.error(f"Failed to write AI log entry: {e}")

    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for AI interactions.

        Returns:
            Unique correlation ID string.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"ai_{timestamp}_{unique_id}"

    def mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text.

        Args:
            text: Text to mask.

        Returns:
            Text with sensitive data masked.
        """
        if not self.config.ai_log_mask_sensitive_data:
            return text

        # Mask API keys (common patterns)
        text = re.sub(r"sk-[a-zA-Z0-9]{20,}", "sk-***MASKED***", text)
        text = re.sub(r"pk-[a-zA-Z0-9]{20,}", "pk-***MASKED***", text)

        # Mask other potential sensitive patterns
        text = re.sub(
            r'api_key["\']?\s*[:=]\s*["\'][^"\']{20,}["\']',
            'api_key: "***MASKED***"',
            text,
        )

        return text

    def log_ai_interaction(
        self, prompt: str, response: Any, context: Dict[str, Any]
    ) -> str:
        """Log an AI interaction with structured metadata.

        Args:
            prompt: The input prompt sent to the AI.
            response: The AI response object (LLMResponse).
            context: Additional context about the interaction.

        Returns:
            Correlation ID for the interaction.
        """
        if not self.config.ai_logging_enabled:
            return ""

        try:
            # Generate correlation ID
            correlation_id = self.generate_correlation_id()

            # Extract response data
            response_content = getattr(response, "content", str(response))
            provider = getattr(response, "model", "unknown")
            model = getattr(response, "model", "unknown")
            tokens_used = getattr(response, "tokens_used", 0)
            cost_usd = getattr(response, "cost_usd", 0.0)
            response_time = getattr(response, "response_time_seconds", 0.0)
            success = getattr(response, "success", True)
            error_message = getattr(response, "error_message", None)

            # Mask sensitive data
            masked_prompt = self.mask_sensitive_data(prompt)
            masked_response = self.mask_sensitive_data(response_content)

            # Create log entry
            entry = AILogEntry(
                correlation_id=correlation_id,
                timestamp=time.time(),
                operation_type=context.get("operation_type", "unknown"),
                prompt=masked_prompt,
                response=masked_response,
                provider=provider,
                model=model,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                response_time_seconds=response_time,
                success=success,
                error_message=error_message,
                metadata=context.get("metadata", {}),
            )

            # Add to logging queue
            if not self.log_queue.full():
                self.log_queue.put(entry)
            else:
                logger.warning("AI log queue is full, dropping log entry")

            return correlation_id

        except Exception as e:
            logger.error(f"Failed to log AI interaction: {e}")
            return ""

    def get_ai_logs_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of AI logs for the specified number of days.

        Args:
            days: Number of days to include in summary.

        Returns:
            Dictionary with AI usage summary.
        """
        if not self.log_file_path.exists():
            return {
                "total_interactions": 0,
                "total_cost_usd": 0.0,
                "total_tokens_used": 0,
                "success_rate": 0.0,
                "average_response_time": 0.0,
                "providers_used": {},
                "operation_types": {},
            }

        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)

            total_interactions = 0
            total_cost_usd = 0.0
            total_tokens_used = 0
            successful_interactions = 0
            total_response_time = 0.0
            providers_used = {}
            operation_types = {}

            with open(self.log_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry_data = json.loads(line.strip())

                        # Check if entry is within time range
                        if entry_data.get("timestamp", 0) < cutoff_time:
                            continue

                        total_interactions += 1
                        total_cost_usd += entry_data.get("cost_usd", 0.0)
                        total_tokens_used += entry_data.get("tokens_used", 0)
                        total_response_time += entry_data.get(
                            "response_time_seconds", 0.0
                        )

                        if entry_data.get("success", False):
                            successful_interactions += 1

                        # Track providers
                        provider = entry_data.get("provider", "unknown")
                        providers_used[provider] = providers_used.get(provider, 0) + 1

                        # Track operation types
                        op_type = entry_data.get("operation_type", "unknown")
                        operation_types[op_type] = operation_types.get(op_type, 0) + 1

                    except json.JSONDecodeError:
                        continue

            return {
                "total_interactions": total_interactions,
                "total_cost_usd": total_cost_usd,
                "total_tokens_used": total_tokens_used,
                "success_rate": successful_interactions / max(total_interactions, 1),
                "average_response_time": total_response_time
                / max(total_interactions, 1),
                "providers_used": providers_used,
                "operation_types": operation_types,
            }

        except Exception as e:
            logger.error(f"Failed to get AI logs summary: {e}")
            return {
                "total_interactions": 0,
                "total_cost_usd": 0.0,
                "total_tokens_used": 0,
                "success_rate": 0.0,
                "average_response_time": 0.0,
                "providers_used": {},
                "operation_types": {},
                "error": str(e),
            }

    def cleanup_old_logs(self, retention_days: Optional[int] = None) -> None:
        """Clean up old log entries based on retention policy.

        Args:
            retention_days: Number of days to retain logs. Uses config if None.
        """
        if retention_days is None:
            retention_days = self.config.ai_log_retention_days

        if not self.log_file_path.exists():
            return

        try:
            cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
            temp_file = self.log_file_path.with_suffix(".tmp")

            with open(self.log_file_path, "r", encoding="utf-8") as f_in, open(
                temp_file, "w", encoding="utf-8"
            ) as f_out:
                for line in f_in:
                    try:
                        entry_data = json.loads(line.strip())
                        if entry_data.get("timestamp", 0) >= cutoff_time:
                            f_out.write(line)
                    except json.JSONDecodeError:
                        continue

            # Replace original file with filtered version
            temp_file.replace(self.log_file_path)
            logger.info(f"Cleaned up AI logs older than {retention_days} days")

        except Exception as e:
            logger.error(f"Failed to cleanup old AI logs: {e}")

    def shutdown(self) -> None:
        """Shutdown the logging manager gracefully."""
        if self.log_thread and self.log_thread.is_alive():
            self.log_queue.put(None)  # Shutdown signal
            self.log_thread.join(timeout=5.0)
