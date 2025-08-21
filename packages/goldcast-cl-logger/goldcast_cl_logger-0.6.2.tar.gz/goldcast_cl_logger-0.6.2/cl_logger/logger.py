"""
Core logging functionality for CL Logger
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Union

from .trace_context import get_trace_id, get_trace_metadata


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging with trace support"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace ID if available
        trace_id = get_trace_id()
        if trace_id:
            log_data["trace_id"] = trace_id

        # Add trace metadata if available
        trace_metadata = get_trace_metadata()
        if trace_metadata:
            log_data["trace_metadata"] = trace_metadata

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class CLLogger:
    """
    A flexible logger that can switch between normal and JSON logging.

    Example:
        logger = CLLogger("my_app")
        logger.info("Application started")

        # With extra context
        logger.info("User action", extra={"user_id": 123, "action": "login"})

        # Switch to normal logging
        logger.set_json_logging(False)
    """

    def __init__(
        self,
        name: str,
        level: Union[str, int] = logging.INFO,
        json_logging: Optional[bool] = None,
        log_to_file: Optional[str] = None,
    ):
        """
        Initialize the logger.

        Args:
            name: Logger name (typically __name__)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            json_logging: Enable JSON logging (if None, checks CL_JSON_LOGGING env var,
            defaults to True)
            log_to_file: Optional file path for logging to file
        """
        # Create a standard logger as fallback
        self.fallback_logger = logging.getLogger(f"{name}.fallback")
        self.fallback_logger.setLevel(level)
        # Prevent duplicate logs by stopping propagation to root
        self.fallback_logger.propagate = False

        # Set up the main logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Clear any existing handlers
        # Prevent duplicate logs by stopping propagation to root
        self.logger.propagate = False

        # Check environment variable if json_logging not explicitly set
        # Default to True (JSON logging) if not specified
        if json_logging is None:
            json_logging = os.getenv("CL_JSON_LOGGING", "true").lower() != "false"

        self.json_logging = json_logging
        self._setup_handlers(log_to_file)

    def _setup_handlers(self, log_to_file: Optional[str] = None):
        """Set up logging handlers based on configuration"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)

        if self.json_logging:
            console_handler.setFormatter(JsonFormatter())
        else:
            # Standard format for human-readable logs (includes trace ID)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s"
            )
            console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

        # File handler if specified
        if log_to_file:
            file_handler = logging.FileHandler(log_to_file)
            if self.json_logging:
                file_handler.setFormatter(JsonFormatter())
            else:
                file_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - "
                    "[%(trace_id)s] - %(message)s"
                )
                file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def set_json_logging(self, enabled: bool):
        """Toggle between JSON and normal logging"""
        self.json_logging = enabled
        # Recreate handlers with new format
        handlers = self.logger.handlers.copy()
        log_to_file = None
        for handler in handlers:
            if isinstance(handler, logging.FileHandler):
                log_to_file = handler.baseFilename
        self.logger.handlers = []
        self._setup_handlers(log_to_file)

    def set_level(self, level: Union[str, int]):
        """Change the logging level"""
        self.logger.setLevel(level)

    def _safe_log(self, level: int, msg: str, *args, **kwargs):
        """Safely log a message using the fallback logger if custom logging fails"""
        try:
            # Try to use the standard logger's log method directly
            self.logger.log(level, msg, *args, **kwargs)
        except Exception as e:
            # If that fails, use the fallback logger with minimal processing
            try:
                # Ensure we have a valid message
                if not isinstance(msg, str):
                    msg = str(msg)

                # Create a minimal kwargs dict with only essential fields
                fallback_kwargs = {
                    "exc_info": kwargs.get("exc_info", False),
                    "stack_info": kwargs.get("stack_info", False),
                }

                # Log with fallback logger
                self.fallback_logger.log(level, msg, *args, **fallback_kwargs)

                # Also log the error that caused the fallback
                self.fallback_logger.error(
                    "CL Logger error, falling back to standard logging",
                    extra={"error": str(e), "original_message": msg},
                    exc_info=True,
                )
            except Exception:
                # Last resort: log the raw message without any processing
                self.fallback_logger.log(level, str(msg))

    def _log_with_extra(
        self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Internal method to log with extra fields and trace context"""
        # First, ensure we have a valid message
        if not isinstance(msg, str):
            msg = str(msg)

        # Create a minimal kwargs dict with only essential fields
        fallback_kwargs = {
            "exc_info": kwargs.get("exc_info", False),
            "stack_info": kwargs.get("stack_info", False),
        }

        # Process extra parameter immediately
        processed_extra = None
        if extra is not None:
            if isinstance(extra, dict):
                if extra:  # Only use non-empty dicts
                    processed_extra = extra
            else:
                # If extra is not a dict, convert it to a dict with a generic key
                processed_extra = {"extra_value": extra}

        try:
            # Handle %-formatting first if there are %s in the message
            if "%" in msg and "args" in kwargs:
                args = kwargs.pop("args", ())
                if not isinstance(args, tuple):
                    args = (args,)
                try:
                    msg = msg % args
                except Exception as e:
                    # If %-formatting fails, log it and continue with raw message
                    self.fallback_logger.warning(
                        "Failed to format message with %-formatting",
                        extra={"error": str(e), "original_message": msg, "args": args},
                        exc_info=True,
                    )

            # Add trace_id to the record for normal formatter
            if not self.json_logging:
                kwargs.setdefault("extra", {})
                kwargs["extra"]["trace_id"] = get_trace_id() or "no-trace"

            # Handle extra fields if we have processed them successfully
            if processed_extra is not None:
                try:
                    if self.json_logging:
                        # Store extra fields in the record for JSON formatter
                        kwargs["extra"] = {"extra_fields": processed_extra}
                    else:
                        # For normal logging, append extra fields to message
                        try:
                            # At this point, processed_extra is guaranteed to be a dict
                            extra_str = " | ".join(
                                f"{k}={v}" for k, v in processed_extra.items()
                            )
                            msg = f"{msg} | {extra_str}"
                        except Exception as e:
                            # If extra formatting fails, log it and continue without extra
                            self.fallback_logger.warning(
                                "Failed to format extra fields",
                                extra={
                                    "error": str(e),
                                    "extra_type": str(type(processed_extra)),
                                },
                                exc_info=True,
                            )
                except Exception as e:
                    # If anything goes wrong with extra handling, log it and continue
                    # without extra
                    self.fallback_logger.warning(
                        "Failed to handle extra fields",
                        extra={
                            "error": str(e),
                            "extra_type": str(type(processed_extra)),
                        },
                        exc_info=True,
                    )

            # Handle f-strings
            if "{" in msg and "}" in msg:
                try:
                    # Check if this is a simple f-string (no complex expressions)
                    import re

                    f_string_exprs = re.findall(r"\{([^{}]+)\}", msg)
                    if all(
                        re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", expr)
                        for expr in f_string_exprs
                    ):
                        # Create a mapping of variable names to their values
                        extra_fields = {}
                        for expr in f_string_exprs:
                            try:
                                # Try to get value from extra first, then from kwargs
                                value = kwargs.get("extra", {}).get(expr)
                                if value is None:
                                    # If not in extra, try to evaluate in the current
                                    # scope
                                    value = eval(expr, kwargs.get("extra", {}))
                                extra_fields[expr] = value
                            except (NameError, SyntaxError):
                                continue

                        if extra_fields:
                            # Update extra with the extracted fields
                            if processed_extra is None:
                                processed_extra = {}
                            processed_extra.update(extra_fields)
                            # Replace the f-string expressions with their values
                            for expr, value in extra_fields.items():
                                msg = msg.replace(f"{{{expr}}}", str(value))
                except Exception as e:
                    # If f-string parsing fails, log it and continue
                    self.fallback_logger.warning(
                        "Failed to process f-string expressions",
                        extra={"error": str(e), "original_message": msg},
                        exc_info=True,
                    )

            # Handle exception info properly
            if kwargs.get("exc_info") and not kwargs.get("exception"):
                try:
                    exc_info = sys.exc_info()
                    if (
                        exc_info[0] is not None
                    ):  # Only set if there's an actual exception
                        kwargs["exc_info"] = exc_info
                except Exception as e:
                    # If exception info handling fails, log it and continue
                    self.fallback_logger.warning(
                        "Failed to process exception info",
                        extra={"error": str(e)},
                        exc_info=True,
                    )
                    kwargs["exc_info"] = None

            # Try to log with the main logger
            try:
                # Remove 'args' from kwargs if it exists to avoid conflict with
                # logger.log() parameter
                clean_kwargs = {k: v for k, v in kwargs.items() if k != "args"}
                self.logger.log(level, msg, **clean_kwargs)
            except Exception as e:
                # If main logging fails, use fallback logger
                self.fallback_logger.error(
                    "CL Logger error, falling back to standard logging",
                    extra={"error": str(e), "original_message": msg},
                    exc_info=True,
                )
                # Use fallback logger with minimal processing
                self.fallback_logger.log(level, msg, **fallback_kwargs)

        except Exception as e:
            # If anything goes wrong at the top level, use fallback logger with minimal
            # processing
            try:
                self.fallback_logger.error(
                    "CL Logger critical error, using fallback logger",
                    extra={"error": str(e), "original_message": msg},
                    exc_info=True,
                )
                # Last resort: log the raw message without any processing
                self.fallback_logger.log(level, msg, **fallback_kwargs)
            except Exception:
                # Absolute last resort: try to log just the message as a string
                try:
                    self.fallback_logger.log(level, str(msg))
                except Exception:
                    # If even that fails, print to stderr as a last resort
                    print(f"CRITICAL LOGGING FAILURE: {msg}", file=sys.stderr)

    def debug(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message"""
        kwargs["args"] = args
        self._log_with_extra(logging.DEBUG, msg, extra, **kwargs)

    def info(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message"""
        kwargs["args"] = args
        self._log_with_extra(logging.INFO, msg, extra, **kwargs)

    def warning(
        self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Log warning message"""
        kwargs["args"] = args
        self._log_with_extra(logging.WARNING, msg, extra, **kwargs)

    def warn(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message (deprecated alias for warning)"""
        self.warning(msg, *args, extra=extra, **kwargs)

    def error(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message with stack trace by default"""
        # Only set exc_info if not explicitly provided and no exception is being logged
        if "exc_info" not in kwargs and "exception" not in kwargs:
            kwargs["exc_info"] = True
        kwargs["args"] = args
        self._log_with_extra(logging.ERROR, msg, extra, **kwargs)

    def critical(
        self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Log critical message with stack trace by default"""
        # Only set exc_info if not explicitly provided and no exception is being logged
        if "exc_info" not in kwargs and "exception" not in kwargs:
            kwargs["exc_info"] = True
        kwargs["args"] = args
        self._log_with_extra(logging.CRITICAL, msg, extra, **kwargs)

    def exception(
        self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Log exception with traceback (alias for error with exc_info=True)"""
        # This is now an alias for error() since error() includes exc_info by default
        self.error(msg, *args, extra=extra, **kwargs)

    def log(self, level: Union[str, int], msg: str, *args, **kwargs):
        """
        Log a message with the specified level.

        Args:
            level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            msg: The message to log
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        if isinstance(level, str):
            level = getattr(logging, level.upper())

        if level == logging.DEBUG:
            self.debug(msg, *args, **kwargs)
        elif level == logging.INFO:
            self.info(msg, *args, **kwargs)
        elif level == logging.WARNING:
            self.warning(msg, *args, **kwargs)
        elif level == logging.ERROR:
            self.error(msg, *args, **kwargs)
        elif level == logging.CRITICAL:
            self.critical(msg, *args, **kwargs)
        else:
            # For any other level, use the standard logger's log method
            self._safe_log(level, msg, *args, **kwargs)


# Singleton pattern for easy access
_loggers: Dict[str, CLLogger] = {}


def get_logger(name: str, **kwargs) -> CLLogger:
    """
    Get or create a logger instance.

    This function maintains a singleton pattern, returning the same logger
    instance for a given name.

    Args:
        name: Logger name (typically __name__)
        **kwargs: Additional arguments passed to CLLogger constructor

    Returns:
        CLLogger instance
    """
    if name not in _loggers:
        _loggers[name] = CLLogger(name, **kwargs)
    return _loggers[name]
