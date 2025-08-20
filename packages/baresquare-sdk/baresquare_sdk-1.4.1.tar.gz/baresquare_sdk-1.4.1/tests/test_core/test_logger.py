"""Tests for Logger functionality using mocking."""

import json
import logging
import os
import sys
from io import StringIO
from unittest.mock import MagicMock, call, patch

from baresquare_sdk.core.logger import (
    JSONFormatter,
    JSONLogger,
    get_request_context,
    sanitise_secret,
    sanitise_secrets,
    setup_logger,
)


class TestGetRequestContext:
    """Test suite for get_request_context function."""

    @patch("baresquare_sdk.core.logger.sys.modules")
    def test_get_request_context_success(self, mock_modules):
        """Test successful request context retrieval."""
        # Arrange
        mock_main_module = MagicMock()
        mock_context = {"user_id": "123", "request_id": "abc-456"}
        mock_main_module.request_context.get.return_value = mock_context
        mock_modules.get.return_value = mock_main_module

        # Act
        result = get_request_context()

        # Assert
        assert result == mock_context
        mock_modules.get.assert_called_once_with("app.main")
        mock_main_module.request_context.get.assert_called_once()

    @patch("baresquare_sdk.core.logger.sys.modules")
    def test_get_request_context_no_main_module(self, mock_modules):
        """Test request context when app.main module doesn't exist."""
        # Arrange
        mock_modules.get.return_value = None

        # Act
        result = get_request_context()

        # Assert
        assert result == {}

    @patch("baresquare_sdk.core.logger.sys.modules")
    def test_get_request_context_no_request_context_attr(self, mock_modules):
        """Test request context when main module lacks request_context attribute."""
        # Arrange
        mock_main_module = MagicMock()
        del mock_main_module.request_context  # Remove the attribute
        mock_modules.get.return_value = mock_main_module

        # Act
        result = get_request_context()

        # Assert
        assert result == {}

    @patch("baresquare_sdk.core.logger.sys.modules")
    def test_get_request_context_lookup_error(self, mock_modules):
        """Test request context when context.get() raises LookupError."""
        # Arrange
        mock_main_module = MagicMock()
        mock_main_module.request_context.get.side_effect = LookupError("No context")
        mock_modules.get.return_value = mock_main_module

        # Act
        result = get_request_context()

        # Assert
        assert result == {}

    @patch("baresquare_sdk.core.logger.sys.modules")
    def test_get_request_context_none_value(self, mock_modules):
        """Test request context when context.get() returns None."""
        # Arrange
        mock_main_module = MagicMock()
        mock_main_module.request_context.get.return_value = None
        mock_modules.get.return_value = mock_main_module

        # Act
        result = get_request_context()

        # Assert
        assert result == {}

    @patch("baresquare_sdk.core.logger.sys.modules")
    def test_get_request_context_generic_exception(self, mock_modules):
        """Test request context when an unexpected exception occurs."""
        # Arrange
        mock_modules.get.side_effect = Exception("Unexpected error")

        # Act
        result = get_request_context()

        # Assert
        assert result == {}


class TestSanitiseSecret:
    """Test suite for sanitise_secret function."""

    def test_sanitise_authentication(self):
        """Test sanitization of authentication field."""
        result = sanitise_secret("authentication", "bearer-token-123")
        assert result == "*REDACTED*"

    def test_sanitise_authorization(self):
        """Test sanitization of authorization field."""
        result = sanitise_secret("authorization", "Bearer token-12345")
        assert result == "*REDACTED*345"  # Shows last 3 chars

    def test_sanitise_authorisation_british_spelling(self):
        """Test sanitization of authorisation field (British spelling)."""
        result = sanitise_secret("authorisation", "Bearer token-12345")
        assert result == "*REDACTED*345"

    def test_sanitise_client_secret(self):
        """Test sanitization of client_secret field."""
        result = sanitise_secret("client_secret", "super-secret-key")
        assert result == "*REDACTED*"

    def test_sanitise_password(self):
        """Test sanitization of password field."""
        result = sanitise_secret("password", "my-password-123")
        assert result == "*REDACTED*"

    def test_sanitise_case_insensitive(self):
        """Test that sanitization is case insensitive."""
        test_cases = [
            ("AUTHENTICATION", "value"),
            ("Authorization", "value123"),
            ("CLIENT_SECRET", "secret"),
            ("Password", "pass123"),
        ]

        for key, value in test_cases:
            result = sanitise_secret(key, value)
            if key.lower() == "authorization":
                assert result == "*REDACTED*123"
            else:
                assert result == "*REDACTED*"

    def test_sanitise_non_secret_field(self):
        """Test that non-secret fields are not sanitized."""
        result = sanitise_secret("username", "john.doe")
        assert result == "john.doe"

    def test_sanitise_empty_values(self):
        """Test sanitization with empty values."""
        assert sanitise_secret("password", "") == "*REDACTED*"
        assert sanitise_secret("authorization", "") == "*REDACTED*"
        assert sanitise_secret("normal_field", "") == ""


class TestSanitiseSecrets:
    """Test suite for sanitise_secrets function."""

    def test_sanitise_secrets_dict(self):
        """Test sanitization of dictionary with secrets."""
        input_dict = {
            "username": "john",
            "password": "secret123",
            "authorization": "Bearer token-12345",
            "normal_field": "normal_value",
        }

        result = sanitise_secrets(input_dict)

        expected = {
            "username": "john",
            "password": "*REDACTED*",
            "authorization": "*REDACTED*345",
            "normal_field": "normal_value",
        }
        assert result == expected
        # Ensure original is not modified
        assert input_dict["password"] == "secret123"

    def test_sanitise_secrets_nested_dict(self):
        """Test sanitization of nested dictionary."""
        input_dict = {"user": {"name": "john", "password": "secret123"}, "auth": {"client_secret": "super-secret"}}

        result = sanitise_secrets(input_dict)

        expected = {"user": {"name": "john", "password": "*REDACTED*"}, "auth": {"client_secret": "*REDACTED*"}}
        assert result == expected

    def test_sanitise_secrets_list(self):
        """Test sanitization of list containing dictionaries."""
        input_list = [
            {"username": "john", "password": "secret1"},
            {"username": "jane", "client_secret": "secret2"},
            "plain_string",
        ]

        result = sanitise_secrets(input_list)

        expected = [
            {"username": "john", "password": "*REDACTED*"},
            {"username": "jane", "client_secret": "*REDACTED*"},
            "plain_string",
        ]
        assert result == expected

    def test_sanitise_secrets_mixed_structure(self):
        """Test sanitization of complex mixed data structure."""
        input_data = {
            "config": {
                "database": {"host": "localhost", "password": "db-secret"},
                "apis": [
                    {"name": "auth0", "client_secret": "auth-secret"},
                    {"name": "stripe", "authorization": "Bearer sk-test-123"},
                ],
            },
            "normal_list": [1, 2, 3],
        }

        result = sanitise_secrets(input_data)

        expected = {
            "config": {
                "database": {"host": "localhost", "password": "*REDACTED*"},
                "apis": [
                    {"name": "auth0", "client_secret": "*REDACTED*"},
                    {"name": "stripe", "authorization": "*REDACTED*123"},
                ],
            },
            "normal_list": [1, 2, 3],
        }
        assert result == expected

    def test_sanitise_secrets_primitive_types(self):
        """Test sanitization of primitive types (should return unchanged)."""
        assert sanitise_secrets("string") == "string"
        assert sanitise_secrets(123) == 123
        assert sanitise_secrets(True)
        assert sanitise_secrets(None) is None

    def test_sanitise_secrets_empty_structures(self):
        """Test sanitization of empty structures."""
        assert sanitise_secrets({}) == {}
        assert sanitise_secrets([]) == []


class TestJSONFormatter:
    """Test suite for JSONFormatter class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.formatter = JSONFormatter()

    @patch("baresquare_sdk.core.logger.get_request_context")
    @patch.dict(
        os.environ, {"PL_ENV": "production", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True
    )
    def test_format_basic_log_record(self, mock_get_context):
        """Test formatting of basic log record."""
        # Arrange
        mock_get_context.return_value = {}
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.filename = "file.py"

        # Act
        result = self.formatter.format(record)
        parsed = json.loads(result)

        # Assert
        assert parsed["level"] == "INFO"
        assert parsed["env"] == "production"
        assert parsed["service"] == "test-service"
        assert parsed["file"] == "file.py"

    @patch("baresquare_sdk.core.logger.get_request_context")
    @patch.dict(os.environ, {"PL_ENV": "dev", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True)
    def test_format_dev_environment(self, mock_get_context):
        """Test that dev environment doesn't include env/service fields."""
        # Arrange
        mock_get_context.return_value = {}
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.filename = "file.py"

        # Act
        result = self.formatter.format(record)
        parsed = json.loads(result)

        # Assert
        assert parsed["level"] == "INFO"
        assert parsed["file"] == "file.py"
        assert "env" not in parsed
        assert "service" not in parsed

    @patch("baresquare_sdk.core.logger.get_request_context")
    @patch.dict(
        os.environ, {"PL_ENV": "production", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True
    )
    def test_format_with_exception_info(self, mock_get_context):
        """Test formatting of log record with exception information."""
        # Arrange
        mock_get_context.return_value = {}

        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )
        record.filename = "file.py"

        # Act
        result = self.formatter.format(record)
        parsed = json.loads(result)

        # Assert
        assert parsed["level"] == "ERROR"
        assert "exception" in parsed
        assert "ValueError: Test exception" in parsed["exception"]

    @patch("baresquare_sdk.core.logger.get_request_context")
    @patch.dict(
        os.environ, {"PL_ENV": "production", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True
    )
    def test_format_with_request_context(self, mock_get_context):
        """Test formatting with request context data."""
        # Arrange
        context_data = {"user_id": "123", "request_id": "abc-456", "endpoint_path": "/api/users"}
        mock_get_context.return_value = context_data

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.filename = "file.py"

        # Act
        result = self.formatter.format(record)
        parsed = json.loads(result)

        # Assert
        assert parsed["user_id"] == "123"
        assert parsed["request_id"] == "abc-456"
        assert parsed["endpoint_path"] == "/api/users"

    @patch("baresquare_sdk.core.logger.get_request_context")
    @patch.dict(
        os.environ, {"PL_ENV": "production", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True
    )
    def test_format_with_extra_fields(self, mock_get_context):
        """Test formatter with extra fields provided during initialization."""
        # Arrange
        extra_fields = {"app_version": "1.2.3", "team": "platform"}
        formatter = JSONFormatter(extra_fields=extra_fields)
        mock_get_context.return_value = {}

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.filename = "file.py"

        # Act
        result = formatter.format(record)
        parsed = json.loads(result)

        # Assert
        assert parsed["app_version"] == "1.2.3"
        assert parsed["team"] == "platform"

    @patch("baresquare_sdk.core.logger.get_request_context")
    @patch("baresquare_sdk.core.logger.sanitise_secrets")
    @patch.dict(
        os.environ, {"PL_ENV": "production", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True
    )
    def test_format_calls_sanitise_secrets(self, mock_sanitise, mock_get_context):
        """Test that format method calls sanitise_secrets."""
        # Arrange
        mock_get_context.return_value = {}
        mock_sanitise.side_effect = lambda x: x  # Return input unchanged

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.filename = "file.py"
        record.password = "secret123"  # Add secret field

        # Act
        self.formatter.format(record)

        # Assert
        assert mock_sanitise.call_count >= 1

    @patch("baresquare_sdk.core.logger.get_request_context")
    @patch.dict(
        os.environ, {"PL_ENV": "production", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True
    )
    def test_format_with_non_serializable_data(self, mock_get_context):
        """Test formatting with non-JSON-serializable data."""
        # Arrange
        mock_get_context.return_value = {}

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.filename = "file.py"
        record.non_serializable = object()  # Non-serializable object

        # Act
        result = self.formatter.format(record)
        parsed = json.loads(result)

        # Assert
        # Should convert to string
        assert "non_serializable" in parsed
        assert isinstance(parsed["non_serializable"], str)


class TestSetupLogger:
    """Test suite for setup_logger function."""

    def setup_method(self):
        """Set up clean logging state before each test."""
        # Clear all existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Clear all existing loggers
        for logger_name in list(logging.root.manager.loggerDict.keys()):
            logging.root.manager.loggerDict.pop(logger_name, None)

    def teardown_method(self):
        """Clean up logging state after each test."""
        # Reset logging to default state
        logging.root.handlers.clear()
        logging.root.setLevel(logging.WARNING)

    def test_setup_logger_basic(self):
        """Test basic logger setup."""
        # Act
        logger = setup_logger()

        # Assert
        assert logger.level == logging.INFO
        assert len(logging.root.handlers) == 1
        assert isinstance(logging.root.handlers[0].formatter, JSONFormatter)

    def test_setup_logger_with_extra_fields(self):
        """Test logger setup with extra fields."""
        # Arrange
        extra_fields = {"version": "1.0.0"}

        # Act
        _logger = setup_logger(extra_fields)

        # Assert
        formatter = logging.root.handlers[0].formatter
        assert formatter.extra_fields == extra_fields

    def test_setup_logger_removes_existing_handlers(self):
        """Test that setup_logger removes existing handlers."""
        # Arrange
        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        initial_count = len(logging.root.handlers)
        logging.root.addHandler(dummy_handler)
        assert len(logging.root.handlers) == initial_count + 1

        # Act
        setup_logger()

        # Assert
        # Should have removed all previous handlers and added exactly one new one
        assert len(logging.root.handlers) == 1
        assert logging.root.handlers[0] != dummy_handler
        assert isinstance(logging.root.handlers[0].formatter, JSONFormatter)

    @patch("baresquare_sdk.core.logger.logging.getLogger")
    def test_setup_logger_configures_other_loggers(self, mock_get_logger):
        """Test that setup_logger configures other existing loggers."""
        # Arrange
        mock_other_logger = MagicMock()
        mock_other_logger.handlers = [MagicMock()]

        # Simulate existing loggers in manager
        logging.root.manager.loggerDict = {"requests": mock_other_logger, "urllib3": mock_other_logger}
        mock_get_logger.return_value = mock_other_logger

        # Act
        setup_logger()

        # Assert
        # Should set WARNING level for other loggers
        expected_calls = [call("requests"), call("urllib3")]
        mock_get_logger.assert_has_calls(expected_calls, any_order=True)

    def test_setup_logger_sets_json_logger_class(self):
        """Test that setup_logger sets JSONLogger as the logger class."""
        # Act
        setup_logger()

        # Assert
        # Create a new logger and check its class
        test_logger = logging.getLogger("test_logger")
        assert isinstance(test_logger, JSONLogger)


class TestJSONLogger:
    """Test suite for JSONLogger class."""

    def setup_method(self):
        """Set up test logger."""
        logging.setLoggerClass(JSONLogger)
        self.logger = logging.getLogger("test_json_logger")

    def test_json_logger_inheritance(self):
        """Test that JSONLogger inherits from logging.Logger."""
        assert isinstance(self.logger, logging.Logger)
        assert isinstance(self.logger, JSONLogger)

    def test_json_logger_log_method_with_extra(self):
        """Test JSONLogger _log method with extra parameters."""
        # Arrange
        handler = logging.StreamHandler(StringIO())
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Act
        self.logger.info("Test message", extra={"custom_field": "custom_value"})

        # Assert
        # Should not raise any exceptions
        # The actual formatting is tested in JSONFormatter tests


class TestLoggerIntegration:
    """Integration tests for the complete logging system."""

    def setup_method(self):
        """Set up clean logging state."""
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    @patch.dict(os.environ, {"PL_ENV": "test", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True)
    def test_complete_logging_flow(self):
        """Test complete logging flow with real log output."""
        # Arrange
        string_io = StringIO()

        # Act
        logger = setup_logger({"version": "1.0.0"})

        # Replace the handler with our test handler
        logging.root.handlers[0] = logging.StreamHandler(string_io)
        logging.root.handlers[0].setFormatter(JSONFormatter({"version": "1.0.0"}))

        logger.info("Test message", extra={"request_id": "123"})

        # Assert
        output = string_io.getvalue()
        parsed = json.loads(output.strip())

        assert parsed["level"] == "INFO"
        assert parsed["env"] == "test"
        assert parsed["service"] == "test-service"
        assert parsed["version"] == "1.0.0"
        assert parsed["request_id"] == "123"

    @patch.dict(
        os.environ, {"PL_ENV": "production", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True
    )
    def test_secret_sanitization_integration(self):
        """Test that secrets are properly sanitized in real log output."""
        # Arrange
        string_io = StringIO()
        logger = setup_logger()

        # Replace handler for testing
        logging.root.handlers[0] = logging.StreamHandler(string_io)
        logging.root.handlers[0].setFormatter(JSONFormatter())

        # Act
        logger.info(
            "Login attempt", extra={"username": "john", "password": "secret123", "authorization": "Bearer token-456"}
        )

        # Assert
        output = string_io.getvalue()
        parsed = json.loads(output.strip())

        assert parsed["username"] == "john"
        assert parsed["password"] == "*REDACTED*"
        assert parsed["authorization"] == "*REDACTED*456"
