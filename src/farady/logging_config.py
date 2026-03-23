# Copyright (C) 2024  Adam Ahmed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Logging configuration for farady library.

Provides local debugging logs for inheritance calculations.
Logs are written to a local 'logs/' directory for easy inspection.

Environment Variables:
    FARADY_LOG_LEVEL: Set log level (DEBUG, INFO, WARNING, ERROR). Default: INFO
    FARADY_LOG_DIR: Set log directory. Default: logs/

Usage:
    from farady.logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("Calculation started", extra={"case": case_dict})
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

_LOG_DIR: Path | None = None
_LOGGER_CACHE: dict[str, logging.Logger] = {}


class CalculationFormatter(logging.Formatter):
    """Custom formatter for calculation logs with structured extra data."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname

        base_msg = f"[{timestamp}] {level}: {record.getMessage()}"

        extra_data: dict[str, Any] = {}
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "taskName",
            }:
                extra_data[key] = value

        if extra_data:
            extra_str = self._format_extra(extra_data)
            return f"{base_msg}\n  {extra_str}"

        return base_msg

    def _format_extra(self, data: dict[str, Any], indent: int = 2) -> str:
        """Format extra data with proper indentation."""
        lines = []
        spaces = " " * indent
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{spaces}{key}:")
                for k, v in value.items():
                    lines.append(f"{spaces}  {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"{spaces}{key}: [{', '.join(str(v) for v in value)}]")
            else:
                lines.append(f"{spaces}{key}: {value}")
        return "\n".join(lines)


def get_log_dir() -> Path:
    """Get the log directory, creating it if necessary."""
    global _LOG_DIR
    if _LOG_DIR is None:
        log_dir_env = os.environ.get("FARADY_LOG_DIR", "logs")
        _LOG_DIR = Path(log_dir_env)
        if not _LOG_DIR.is_absolute():
            import farady

            package_dir = Path(farady.__file__).parent
            _LOG_DIR = package_dir.parent.parent / log_dir_env
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
    return _LOG_DIR


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the given name.

    Args:
        name: Logger name, typically __name__ of the calling module

    Returns:
        Configured logger instance
    """
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(name)

    level_str = os.environ.get("FARADY_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    if not logger.handlers:
        log_dir = get_log_dir()
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"farady_{timestamp}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(CalculationFormatter())
        logger.addHandler(file_handler)

        # Only add console handler if not in test mode
        if not os.environ.get("FARADY_TEST_MODE"):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(CalculationFormatter())
            logger.addHandler(console_handler)

    _LOGGER_CACHE[name] = logger
    return logger


def log_calculation_start(logger: logging.Logger, case_input: dict[str, Any]) -> None:
    """Log the start of a calculation with full input case."""
    logger.info(
        "=== Calculation Started ===",
        extra={"case_input": case_input},
    )


def log_calculation_end(
    logger: logging.Logger,
    result: dict[str, Any],
) -> None:
    """Log the end of a calculation with full result."""
    logger.info(
        "=== Calculation Ended ===",
        extra={"result": result},
    )


def log_validation_error(
    logger: logging.Logger,
    field: str,
    value: Any,
    reason: str,
) -> None:
    """Log a validation error with context."""
    logger.warning(
        f"Validation error: {reason}",
        extra={"field": field, "value": str(value), "reason": reason},
    )


def log_calculation_step(
    logger: logging.Logger,
    step_name: str,
    details: dict[str, Any] | None = None,
) -> None:
    """Log a calculation step (awl, radd, taseeb, etc.)."""
    extra = {"step": step_name}
    if details:
        extra.update(details)
    logger.debug(f"Step: {step_name}", extra=extra)
