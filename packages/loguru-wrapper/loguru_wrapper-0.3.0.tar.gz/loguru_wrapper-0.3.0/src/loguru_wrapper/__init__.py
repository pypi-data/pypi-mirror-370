"""
loguru_wrapper
"""
# standard library imports
import importlib.metadata

# 3rd party imports
from typing import TYPE_CHECKING
from stackwalker import stackwalker

# 1st party imports
from loguru_wrapper.wrapper import LoguruWrapper
from loguru_wrapper.loguru_config import LoguruConfig

try:
    __version_number__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version_number__ = "0.0.0"


def loguru(offset: int = 2, config: LoguruConfig = LoguruConfig()) -> LoguruWrapper:
    """Create a LoggerWrapper instance with automatic caller context detection.

    This factory function creates a LoggerWrapper that automatically captures
    the calling context (module name, function name, and line number) by
    inspecting the call stack at the specified offset.

    Args:
        offset (int, optional): Number of stack frames to skip when detecting
            the caller context. Defaults to 2.
            - 0: Returns info about this logger() function itself
            - 1: Returns info about the immediate caller of logger() (LoggerWrapper)
            - 2: Returns info about the caller's caller (typical use case)
            - Higher values: Skip more intermediate function calls

    Returns:
        LoggerWrapper: A configured logger instance with caller context that
            provides lazy evaluation logging methods (debug, info, success,
            warning, error, critical).

    Example:
        Basic usage (offset=2 is usually correct):

            def my_function():
                log = logger()  # Will show my_function:line_number in output
                log.info("Processing user: {}", username)

        Custom offset for wrapper functions:

            def logging_helper():
                return logger(offset=3)  # Skip one extra frame

            def business_logic():
                log = logging_helper()  # Will show business_logic:line_number
                log.debug("Starting process")

    Note:
        The offset parameter is crucial for showing the correct caller in log
        output. If your logs show internal wrapper function names instead of
        your actual calling function, try increasing the offset value.
    """
    frame_info = stackwalker.get_frame_by_name(
        module_name='stackwalker.stackwalker',
        caller_name='get_frame_by_name',
        offset=offset
    )
    return LoguruWrapper(frame_info=frame_info, config=config)


def get_frame_name_list():
    """Debug function to print frame names for debugging purposes."""
    return stackwalker.get_frame_name_list()


if __name__ == "__main__":

    # Example usage of the logger
    def my_function():
        """Example function demonstrating lazy logging with caller context."""
        def get_username():
            return "john_doe"
        item_count = 5
        loguru().debug("User: {}", get_username)  # Lazy evaluation
        loguru().info("Processing %s items", item_count)  # Format conversion
        loguru().structured("user_login", user_id=123, success=True)

    def my_function2():
        """Another example function to show different log levels."""
        log = loguru()
        log.debug("This is a debug message with value: {}", 42)
        log.info("This is an info message with value: {}", "test")
        log.warning("This is a warning message with value: {}", [1, 2, 3])
        log.error("This is an error message with value: {}", {"key": "value"})
        log.critical("This is a critical message with value: {}", None)

        log.structured('Something', key1='value1', key2=42, key3=True)

        try:
            raise ValueError("An example exception")
        except ValueError as e:
            log.exception("An error occurred", extra_info='additional context', exc=e)

    my_function()
