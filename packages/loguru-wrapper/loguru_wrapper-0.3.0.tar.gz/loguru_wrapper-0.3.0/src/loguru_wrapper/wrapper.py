"""
Lazy logging wrapper for loguru with caller context detection.

This module provides a wrapper around loguru that enables lazy evaluation of log
messages and automatically captures caller context (function name and line number).

Features:
    - Lazy evaluation: Log message arguments are only evaluated if the log level is enabled
    - Automatic caller detection: Shows the actual calling function and line number
    - Format conversion: Converts %s format strings to {} format for loguru compatibility
    - Full loguru support: All log levels (debug, info, success, warning, error, critical)
    - Type safety: Proper type hints with TYPE_CHECKING imports

Example:
    Basic usage with automatic caller detection:

        def my_function():
            logger().debug("User: {}", get_username)  # Lazy evaluation
            logger().info("Processing %s items", item_count)  # Format conversion

    The output will show:
        2024-01-01 12:00:00.000 | DEBUG    | my_function:123 | User: john_doe
        2024-01-01 12:00:00.000 | INFO     | my_function:124 | Processing 5 items

Classes:
    LoggerWrapper: Main wrapper class with lazy evaluation support

Functions:
    logger: Factory function that creates LoggerWrapper with caller context

Notes:
    - Uses inspect.currentframe() to automatically detect calling function and line
    - Non-callable arguments are automatically wrapped in lambdas for lazy evaluation
    - Callable arguments are passed through unchanged for maximum flexibility
    - Custom loguru format shows caller context instead of internal wrapper functions
"""
# standard library imports
from __future__ import annotations
import re
import sys
from typing import TYPE_CHECKING
import traceback

# 3rd party imports
from loguru import logger as loguru_logger
try:
    from loguru_wrapper.loguru_config import LoguruConfig
except ImportError:
    from .loguru_config import LoguruConfig

if TYPE_CHECKING:
    from loguru import Logger


class LoguruWrapper:
    """Wrapper class for loguru logger with lazy evaluation support.

    Provides convenient access to loguru logging methods with automatic
    lazy evaluation of log message parameters.
    """
    __config: LoguruConfig
    __cached_logger: Logger | None

    def __init__(self, frame_info=None, config: LoguruConfig = LoguruConfig()):
        self.__frame_info = frame_info or {}
        self.__cached_logger = None
        self.__config = config

    def caller_name(self) -> str:
        """Get the name of the calling function.

        Returns:
            The name of the calling function or "Unknown" if not available.
        """
        return self.__frame_info.get("caller_name", "Unknown")

    def caller_line(self) -> int:
        """Get the line number of the calling function.

        Returns:
            The line number of the calling function or 0 if not available.
        """
        return self.__frame_info.get("caller_line", 0)

    def module_name(self) -> str:
        """Get the module name of the calling function.

        Returns:
            The module name of the calling function or "Unknown" if not available.
        """
        return self.__frame_info.get("module_name", "Unknown")

    @property
    def loguru_logger(self) -> Logger:
        """Get the raw loguru logger instance.

        Returns:
            The global loguru logger instance.
        """
        return loguru_logger

    def lazy_logger(self) -> Logger:
        """Returns a logger instance with lazy evaluation enabled.

        This allows for lazy evaluation of log messages, meaning the message is only
        evaluated if the log level is enabled.
        """
        if self.__cached_logger is None:
            logger_instance = self.loguru_logger
            logger_instance.remove()  # Remove default sink
            logger_instance.add(
                self.__config.sink,
                format=self.__config.format_string,
                level=self.__config.ns_log_level,
            )

            if self.__config.enable_lazy:
                self.__cached_logger = logger_instance.opt(lazy=True)
            else:
                self.__cached_logger = logger_instance

        return self.__cached_logger
        # return self.loguru_logger.opt(lazy=True)

    def make_lambda(self, value):
        """Creates a lambda function that returns the given value.

        This is useful for lazy evaluation in logging, where you want to delay the evaluation of the value until it's actually needed.

        Args:
            value: The value to be wrapped in a lambda function.

        Returns:
            A lambda function that returns the provided value.
        """
        return lambda: value

    def transform_args(self, args):
        """Transforms arguments for lazy evaluation in loguru."""
        return [arg if callable(arg) else self.make_lambda(arg) for arg in args]

    def debug(self, *args, **kwargs):
        """Lazy log a debug message."""
        return self.do_log(*args, **kwargs, method_name="debug")

    def info(self, *args, **kwargs):
        """Lazy log an info message."""
        return self.do_log(*args, **kwargs, method_name="info")

    def success(self, *args, **kwargs):
        """Lazy log a success message."""
        return self.do_log(*args, **kwargs, method_name="success")

    def warning(self, *args, **kwargs):
        """Lazy log a warning message."""
        return self.do_log(*args, **kwargs, method_name="warning")

    def error(self, *args, **kwargs):
        """Lazy log an error message."""
        return self.do_log(*args, **kwargs, method_name="error")

    def critical(self, *args, **kwargs):
        """Lazy log a critical message."""
        return self.do_log(*args, **kwargs, method_name="critical")

    def structured(self, event: str, **kwargs):
        """Log structured data with consistent format.

        Usage:
            log.structured("user_login", user_id=123, ip="192.168.1.1", success=True)
        """
        structured_msg = f"EVENT={event}"
        if kwargs:
            params = " ".join(f"{k}={v}" for k, v in kwargs.items())
            structured_msg += f" {params}"
        return self.info(structured_msg)

    def exception(self, message: str, exc: BaseException | None = None, **kwargs):
        """Log an exception with full traceback."""

        if exc is None:
            # Get current exception if in except block
            exc_type, exc_value, exc_traceback = sys.exc_info()  # pylint: disable=unused-variable
            if exc_type is not None:
                exc = exc_value

        msg = f"{message}\nKwargs: {kwargs}\n"
        if exc:
            tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
            self.error(
                msg + f"Exception:{exc}\nTraceback:\n{''.join(tb)}")
        else:
            self.error(msg)

    def do_log(self, *args, **kwargs):
        """Log a debug message with lazy evaluation.

        Transforms arguments for loguru supported format.

        1. If the message contains %s, it replaces them with curly braces.
        2. If the values are callable, it uses them directly.
        3. If the values are not callable, it wraps them in a lambda for lazy evaluation.

        Args:
            message (str): The message to log.
            values (positional arguments): The values to format the message with.

        Keyword Args:
            method_name (str): The loguru method to use (e.g., "debug", "info", ...)

        Returns:
            loguru logline with lazy evaluation.

        Example:
            debug("message: {}", value())
            debug("message: {}", value)
            debug("message: %s", value)
            debug("message: %s", value())
        """
        message = args[0] if args else kwargs.get("message", "")
        method_name = kwargs.get("method_name", "debug")

        if not message:
            raise ValueError("Message must be provided for logging")

        if not isinstance(message, str):
            raise TypeError("Message must be a string")

        transformed_args = self.transform_args(args[1:]) if len(args) > 1 else []
        # Transform the message to use curly braces instead of %s
        message = re.sub(r"%s", "{}", message)
        # return lazy_logger().debug(message, *transformed_args)

        logger_instance = self.lazy_logger()

        bound_logger = logger_instance.bind(
            caller_name=self.caller_name(),
            caller_line=self.caller_line(),
            module_name=self.module_name(),
        )

        # Map method names to actual logger methods
        method_map = {
            "debug": bound_logger.debug,
            "info": bound_logger.info,
            "success": bound_logger.success,
            "warning": bound_logger.warning,
            "error": bound_logger.error,
            "critical": bound_logger.critical,
        }

        if method_name not in method_map:
            raise ValueError(f"Method '{method_name}' is not a valid loguru method")

        return method_map[method_name](message, *transformed_args)
