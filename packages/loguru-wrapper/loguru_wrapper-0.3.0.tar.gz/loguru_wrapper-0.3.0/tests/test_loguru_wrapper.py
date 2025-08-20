"""
Generated unittests for generated utility methods.
"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
from loguru import logger as loguru_logger

from loguru_wrapper import loguru
from loguru_wrapper.wrapper import LoguruWrapper
from loguru_wrapper.loguru_config import LoguruConfig


class TestLoguruWrapper(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for generated utility methods."""

    def test_logger_returns_loguru_wrapper_instance(self):
        """Test that loguru() returns a LoguruWrapper instance."""
        result = loguru()
        self.assertIsInstance(result, LoguruWrapper)

    def test_logger_with_custom_offset(self):
        """Test that loguru() accepts custom offset parameter."""
        result = loguru(offset=3)
        self.assertIsInstance(result, LoguruWrapper)

    def test_logger_with_custom_config(self):
        """Test that loguru() accepts custom LoguruConfig parameter."""
        config = LoguruConfig(default_level="DEBUG")
        result = loguru(config=config)
        self.assertIsInstance(result, LoguruWrapper)

    def test_loguru_wrapper_caller_info_methods(self):
        """Test LoguruWrapper caller information methods."""
        frame_info = {
            "caller_name": "test_function",
            "caller_line": 42,
            "module_name": "test_module"
        }
        wrapper = LoguruWrapper(frame_info=frame_info)

        self.assertEqual(wrapper.caller_name(), "test_function")
        self.assertEqual(wrapper.caller_line(), 42)
        self.assertEqual(wrapper.module_name(), "test_module")

    def test_loguru_wrapper_caller_info_defaults(self):
        """Test LoguruWrapper caller information methods with empty frame_info."""
        wrapper = LoguruWrapper()

        self.assertEqual(wrapper.caller_name(), "Unknown")
        self.assertEqual(wrapper.caller_line(), 0)
        self.assertEqual(wrapper.module_name(), "Unknown")

    def test_loguru_wrapper_loguru_logger_property(self):
        """Test LoguruWrapper loguru_logger property returns loguru logger."""
        wrapper = LoguruWrapper()
        self.assertEqual(wrapper.loguru_logger, loguru_logger)

    def test_make_lambda_creates_callable(self):
        """Test make_lambda creates a callable that returns the value."""
        wrapper = LoguruWrapper()
        test_value = "test_string"
        lambda_func = wrapper.make_lambda(test_value)

        self.assertTrue(callable(lambda_func))
        self.assertEqual(lambda_func(), test_value)

    def test_transform_args_with_callables(self):
        """Test transform_args preserves callable arguments."""
        wrapper = LoguruWrapper()
        def test_func(): return "test"  # pylint: disable=multiple-statements

        result = wrapper.transform_args([test_func])
        self.assertEqual(len(result), 1)
        self.assertTrue(callable(result[0]))
        self.assertEqual(result[0](), "test")

    def test_transform_args_with_non_callables(self):
        """Test transform_args wraps non-callable arguments in lambdas."""
        wrapper = LoguruWrapper()
        test_value = "test_string"

        result = wrapper.transform_args([test_value])
        self.assertEqual(len(result), 1)
        self.assertTrue(callable(result[0]))
        self.assertEqual(result[0](), test_value)

    def test_transform_args_mixed(self):
        """Test transform_args with mixed callable and non-callable arguments."""
        wrapper = LoguruWrapper()
        def test_func(): return "func_result"  # pylint: disable=multiple-statements
        test_value = "string_value"

        result = wrapper.transform_args([test_func, test_value])
        self.assertEqual(len(result), 2)
        self.assertTrue(callable(result[0]))
        self.assertTrue(callable(result[1]))
        self.assertEqual(result[0](), "func_result")
        self.assertEqual(result[1](), "string_value")

    @patch('loguru_wrapper.loguru')
    def test_lazy_logger_caching(self, mock_loguru):
        """Test that lazy_logger caches the logger instance."""
        mock_logger_instance = MagicMock()
        mock_logger_instance.opt.return_value = mock_logger_instance
        mock_loguru.return_value = mock_logger_instance

        wrapper = LoguruWrapper()

        # First call should create and cache the logger
        result1 = wrapper.lazy_logger()
        # Second call should return the cached logger
        result2 = wrapper.lazy_logger()

        self.assertIs(result1, result2)

    @patch('loguru_wrapper.loguru')
    def test_debug_method(self, mock_loguru):  # pylint: disable=unused-argument
        """Test debug logging method."""
        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'do_log') as mock_do_log:
            wrapper.debug("test message", "arg1")
            mock_do_log.assert_called_once_with(
                "test message", "arg1", method_name="debug")

    @patch('loguru_wrapper.loguru')
    def test_info_method(self, mock_loguru):  # pylint: disable=unused-argument
        """Test info logging method."""
        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'do_log') as mock_do_log:
            wrapper.info("test message", "arg1")
            mock_do_log.assert_called_once_with(
                "test message", "arg1", method_name="info")

    @patch('loguru_wrapper.loguru')
    def test_success_method(self, mock_loguru):  # pylint: disable=unused-argument
        """Test success logging method."""
        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'do_log') as mock_do_log:
            wrapper.success("test message", "arg1")
            mock_do_log.assert_called_once_with(
                "test message", "arg1", method_name="success")

    @patch('loguru_wrapper.loguru')
    def test_warning_method(self, mock_loguru):  # pylint: disable=unused-argument
        """Test warning logging method."""
        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'do_log') as mock_do_log:
            wrapper.warning("test message", "arg1")
            mock_do_log.assert_called_once_with(
                "test message", "arg1", method_name="warning")

    @patch('loguru_wrapper.loguru')
    def test_error_method(self, mock_loguru):  # pylint: disable=unused-argument
        """Test error logging method."""
        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'do_log') as mock_do_log:
            wrapper.error("test message", "arg1")
            mock_do_log.assert_called_once_with(
                "test message", "arg1", method_name="error")

    @patch('loguru_wrapper.loguru')
    def test_critical_method(self, mock_loguru):  # pylint: disable=unused-argument
        """Test critical logging method."""
        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'do_log') as mock_do_log:
            wrapper.critical("test message", "arg1")
            mock_do_log.assert_called_once_with(
                "test message", "arg1", method_name="critical")

    def test_structured_logging(self):
        """Test structured logging method."""
        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'info') as mock_info:
            wrapper.structured("user_login", user_id=123, success=True)
            mock_info.assert_called_once_with(
                "EVENT=user_login user_id=123 success=True")

    def test_structured_logging_no_kwargs(self):
        """Test structured logging method without kwargs."""
        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'info') as mock_info:
            wrapper.structured("user_logout")
            mock_info.assert_called_once_with("EVENT=user_logout")

    @patch('sys.exc_info')
    def test_exception_with_current_exception(self, mock_exc_info):
        """Test exception logging with current exception context."""
        test_exc = ValueError("test error")
        mock_exc_info.return_value = (type(test_exc), test_exc, test_exc.__traceback__)

        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'error') as mock_error:
            wrapper.exception("Something went wrong", key="value")

            mock_error.assert_called_once()
            args = mock_error.call_args[0]
            self.assertIn("Something went wrong", args[0])
            self.assertIn("Kwargs: {'key': 'value'}", args[0])
            self.assertIn("Exception:test error", args[0])

    def test_exception_with_provided_exception(self):
        """Test exception logging with provided exception."""
        test_exc = RuntimeError("runtime error")

        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'error') as mock_error:
            wrapper.exception("Something went wrong", exc=test_exc, key="value")

            mock_error.assert_called_once()
            args = mock_error.call_args[0]
            self.assertIn("Something went wrong", args[0])
            self.assertIn("Kwargs: {'key': 'value'}", args[0])
            self.assertIn("Exception:runtime error", args[0])

    @patch('sys.exc_info')
    def test_exception_no_exception_context(self, mock_exc_info):
        """Test exception logging without exception context."""
        mock_exc_info.return_value = (None, None, None)

        wrapper = LoguruWrapper()
        with patch.object(wrapper, 'error') as mock_error:
            wrapper.exception("Something went wrong", key="value")

            mock_error.assert_called_once()
            args = mock_error.call_args[0]
            self.assertIn("Something went wrong", args[0])
            self.assertIn("Kwargs: {'key': 'value'}", args[0])
            self.assertNotIn("Exception:", args[0])

    def test_do_log_empty_message_raises_error(self):
        """Test do_log raises ValueError for empty message."""
        wrapper = LoguruWrapper()

        with self.assertRaises(ValueError) as context:
            wrapper.do_log("", method_name="debug")
        self.assertIn("Message must be provided", str(context.exception))

    def test_do_log_non_string_message_raises_error(self):
        """Test do_log raises TypeError for non-string message."""
        wrapper = LoguruWrapper()

        with self.assertRaises(TypeError) as context:
            wrapper.do_log(123, method_name="debug")
        self.assertIn("Message must be a string", str(context.exception))

    def test_do_log_invalid_method_name_raises_error(self):
        """Test do_log raises ValueError for invalid method name."""
        wrapper = LoguruWrapper()

        with patch.object(wrapper, 'lazy_logger') as mock_lazy_logger:
            mock_logger = MagicMock()
            mock_lazy_logger.return_value = mock_logger

            with self.assertRaises(ValueError) as context:
                wrapper.do_log("test message", method_name="invalid_method")
            self.assertIn(
                "Method 'invalid_method' is not a valid loguru method", str(context.exception))

    def test_do_log_format_string_conversion(self):
        """Test do_log converts %s to {} format."""
        wrapper = LoguruWrapper()

        with patch.object(wrapper, 'lazy_logger') as mock_lazy_logger:
            mock_logger = MagicMock()
            mock_bound_logger = MagicMock()
            mock_logger.bind.return_value = mock_bound_logger
            mock_lazy_logger.return_value = mock_logger

            wrapper.do_log("test %s message %s", "arg1", "arg2", method_name="info")

            # Check that the bound logger's info method was called
            mock_bound_logger.info.assert_called_once()
            # The first argument should be the converted message
            args, _ = mock_bound_logger.info.call_args
            self.assertEqual(args[0], "test {} message {}")

    def test_logger_config_defaults(self):
        """Test LoguruConfig default values."""
        config = LoguruConfig()

        self.assertIn("time:YYYY-MM-DD HH:mm:ss.SSS", config.format_string)
        self.assertEqual(config.default_level, "DEBUG")
        self.assertTrue(config.enable_lazy)
        self.assertEqual(config.sink, sys.stderr)

    def test_logger_config_custom_values(self):
        """Test LoguruConfig with custom values."""
        custom_format = "<level>{level}</level> | {message}"
        config = LoguruConfig(
            format_string=custom_format,
            default_level="DEBUG",
            enable_lazy=False
        )

        self.assertEqual(config.format_string, custom_format)
        self.assertEqual(config.default_level, "DEBUG")
        self.assertFalse(config.enable_lazy)

    def test_logger_prints_multiple_times(self):
        """Test that logger prints multiple times for different log levels."""
        def get_username():
            return "john_doe"
        item_count = 5

        # 1. properties must be patched with PropertyMock
        # 2. patch.object is class level patching, before instance
        with patch.object(LoguruConfig, "ns_log_level", new_callable=PropertyMock) as mock_level:
            mock_level.return_value = "WARNING"
            config = LoguruConfig()
            assert config.ns_log_level == "WARNING"

            loguru().debug("User: {}", get_username)  # Lazy evaluation
            loguru().info("Processing %s items", item_count)  # Format conversion

    def test_should_crash_if_wrong_log_level(self):
        """Test that an invalid log level raises a TypeError."""
        with patch.object(LoguruConfig, "ns_log_level", new_callable=PropertyMock) as mock_level:
            mock_level.return_value = "WOW"
            config = LoguruConfig()
            assert config.ns_log_level == "WOW"
            with self.assertRaises(ValueError):
                loguru().debug("User: testi")


if __name__ == '__main__':
    unittest.main()
