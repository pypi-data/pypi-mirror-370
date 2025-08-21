"""Logging utilities for Genesis MCP Core SDK."""

import logging
import sys
from typing import Any, Dict, Optional
import structlog
from ..core.config import LoggingConfig


def setup_logging(config: LoggingConfig) -> None:
    """Set up structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if config.format == "dev" 
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, config.level.upper()),
        format="%(message)s",
        stream=sys.stdout,
    )
    
    # Set logging levels for external libraries
    logging.getLogger("uvicorn").setLevel(
        logging.INFO if config.enable_access_logs else logging.WARNING
    )
    logging.getLogger("uvicorn.access").setLevel(
        logging.INFO if config.enable_access_logs else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str, **context: Any) -> structlog.BoundLogger:
    """Get a logger instance with optional context."""
    logger = structlog.get_logger(name)
    if context:
        logger = logger.bind(**context)
    return logger


class ContextualLogger:
    """A logger that maintains context throughout the application."""
    
    def __init__(self, name: str, **initial_context: Any) -> None:
        self._logger = structlog.get_logger(name)
        self._context: Dict[str, Any] = initial_context
        
    def bind(self, **context: Any) -> "ContextualLogger":
        """Create a new logger with additional context."""
        new_context = {**self._context, **context}
        return ContextualLogger(self._logger.name, **new_context)
        
    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        """Internal logging method."""
        combined_context = {**self._context, **kwargs}
        getattr(self._logger.bind(**combined_context), level)(message)
        
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log("debug", message, **kwargs)
        
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log("info", message, **kwargs)
        
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log("warning", message, **kwargs)
        
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log("error", message, **kwargs)
        
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._log("critical", message, **kwargs)