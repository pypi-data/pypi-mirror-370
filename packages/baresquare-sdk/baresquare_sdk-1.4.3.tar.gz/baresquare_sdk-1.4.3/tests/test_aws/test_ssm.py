"""Tests for SSM functionality using mocking."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from baresquare_sdk.aws import ssm
from baresquare_sdk.core.exceptions import ExceptionInfo


class TestGetSSMClient:
    """Test suite for get_client function."""

    def teardown_method(self):
        """Clean up global ssm_client after each test."""
        # Reset the global ssm_client to ensure clean state
        if hasattr(ssm, "ssm_client"):
            delattr(ssm, "ssm_client")

    @patch("baresquare_sdk.aws.ssm.boto3.client")
    @patch.dict(os.environ, {"PL_ENV": "test", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"}, clear=True)
    def test_get_client_no_profile(self, mock_boto3_client):
        """Test SSM client creation without AWS profile."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Act
        client = ssm.get_client()

        # Assert
        mock_boto3_client.assert_called_once_with(service_name="ssm", region_name="us-east-1")
        assert client == mock_client

    @patch("baresquare_sdk.aws.ssm.boto3.client")
    @patch("baresquare_sdk.aws.ssm.boto3.Session")
    @patch.dict(
        os.environ,
        {"AWS_PROFILE": "test-profile", "PL_ENV": "test", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"},
        clear=True,
    )
    def test_get_client_with_profile(self, mock_session, mock_boto3_client):
        """Test SSM client creation with AWS profile."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_client = MagicMock()
        mock_session_instance.client.return_value = mock_client

        # Act
        client = ssm.get_client()

        # Assert
        mock_session.assert_called_once_with(profile_name="test-profile")
        mock_session_instance.client.assert_called_once_with(service_name="ssm", region_name="us-east-1")
        assert client == mock_client

    @patch("baresquare_sdk.aws.ssm.boto3.client")
    @patch.dict(os.environ, {"PL_REGION": "eu-west-1", "PL_ENV": "test", "PL_SERVICE": "test-service"}, clear=True)
    def test_get_client_with_region(self, mock_boto3_client):
        """Test SSM client creation with custom region."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Act
        _client = ssm.get_client()

        # Assert
        mock_boto3_client.assert_called_once_with(service_name="ssm", region_name="eu-west-1")

    @patch("baresquare_sdk.aws.ssm.boto3.client")
    @patch.dict(os.environ, {"PL_ENV": "test", "PL_SERVICE": "test-service", "PL_REGION": "us-east-1"})
    def test_get_client_singleton_behavior(self, mock_boto3_client):
        """Test that get_client returns same instance (singleton pattern)."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Act
        client1 = ssm.get_client()
        client2 = ssm.get_client()

        # Assert
        assert client1 == client2
        # Should only create client once
        mock_boto3_client.assert_called_once()


class TestGetSSMParameter:
    """Test suite for get_parameter function."""

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_get_parameter_success(self, mock_get_client):
        """Test successful parameter retrieval."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_parameter.return_value = {"Parameter": {"Value": "test-value"}}

        # Act
        result = ssm.get_parameter("/test/param")

        # Assert
        assert result == "test-value"
        mock_client.get_parameter.assert_called_once_with(Name="/test/param", WithDecryption=True)

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_get_parameter_json_success(self, mock_get_client):
        """Test successful parameter retrieval with JSON parsing."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        test_json = {"key": "value", "number": 42}
        mock_client.get_parameter.return_value = {"Parameter": {"Value": json.dumps(test_json)}}

        # Act
        result = ssm.get_parameter("/test/param", return_json=True)

        # Assert
        assert result == test_json
        mock_client.get_parameter.assert_called_once_with(Name="/test/param", WithDecryption=True)

    @patch("baresquare_sdk.aws.ssm.get_client")
    @patch("baresquare_sdk.aws.ssm.logger")
    def test_get_parameter_client_error(self, mock_logger, mock_get_client):
        """Test parameter retrieval with ClientError."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        error = ClientError(error_response={"Error": {"Code": "ParameterNotFound"}}, operation_name="get_parameter")
        mock_client.get_parameter.side_effect = error

        # Act & Assert
        with pytest.raises(ExceptionInfo) as exc_info:
            ssm.get_parameter("/test/param")

        assert "Failed to retrieve SSM param from /test/param" in str(exc_info.value)
        assert exc_info.value.data["ssm_parameter_name"] == "/test/param"
        mock_logger.warning.assert_called_once_with("Failed to retrieve SSM param from /test/param")

    @patch("baresquare_sdk.aws.ssm.get_client")
    @patch("baresquare_sdk.aws.ssm.logger")
    def test_get_parameter_logs_debug(self, mock_logger, mock_get_client):
        """Test that parameter retrieval logs debug message."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_parameter.return_value = {"Parameter": {"Value": "test-value"}}

        # Act
        ssm.get_parameter("/test/param")

        # Assert
        mock_logger.debug.assert_called_once_with("Retrieving SSM param /test/param")


class TestGetSSMParameters:
    """Test suite for get_parameters function."""

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_get_parameters_success(self, mock_get_client):
        """Test successful bulk parameter retrieval."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        parameters_mapping = {
            "/auth0/domain": {"env_var": "AUTH0_DOMAIN", "is_json": False},
            "/auth0/api/audiences": {"env_var": "AUTH0_API_AUDIENCES", "is_json": True},
        }

        mock_client.get_parameters.return_value = {
            "Parameters": [
                {"Name": "/auth0/domain", "Value": "example.auth0.com"},
                {"Name": "/auth0/api/audiences", "Value": '{"service1": "aud1", "service2": "aud2"}'},
            ]
        }

        # Act
        result = ssm.get_parameters(parameters_mapping)

        # Assert
        expected = {
            "AUTH0_DOMAIN": "example.auth0.com",
            "AUTH0_API_AUDIENCES": {"service1": "aud1", "service2": "aud2"},
        }
        assert result == expected
        mock_client.get_parameters.assert_called_once_with(
            Names=["/auth0/domain", "/auth0/api/audiences"], WithDecryption=True
        )

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_get_parameters_batching(self, mock_get_client):
        """Test that large parameter lists are batched correctly."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Create 15 parameters to force batching (batch size is 10)
        parameters_mapping = {}
        mock_parameters = []

        for i in range(15):
            param_name = f"/test/param{i}"
            parameters_mapping[param_name] = {"env_var": f"TEST_PARAM_{i}", "is_json": False}
            mock_parameters.append({"Name": param_name, "Value": f"value{i}"})

        # Mock returns for two batches
        mock_client.get_parameters.side_effect = [
            {"Parameters": mock_parameters[:10]},  # First batch
            {"Parameters": mock_parameters[10:]},  # Second batch
        ]

        # Act
        result = ssm.get_parameters(parameters_mapping)

        # Assert
        assert len(result) == 15
        assert mock_client.get_parameters.call_count == 2

        # Check first batch call
        first_call_args = mock_client.get_parameters.call_args_list[0]
        assert len(first_call_args[1]["Names"]) == 10

        # Check second batch call
        second_call_args = mock_client.get_parameters.call_args_list[1]
        assert len(second_call_args[1]["Names"]) == 5

    @patch("baresquare_sdk.aws.ssm.get_client")
    @patch("baresquare_sdk.aws.ssm.logger")
    def test_get_parameters_client_error(self, mock_logger, mock_get_client):
        """Test bulk parameter retrieval with ClientError."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        error = ClientError(error_response={"Error": {"Code": "InvalidParameterName"}}, operation_name="get_parameters")
        mock_client.get_parameters.side_effect = error

        parameters_mapping = {"/test/param": {"env_var": "TEST_PARAM", "is_json": False}}

        # Act & Assert
        with pytest.raises(ExceptionInfo) as exc_info:
            ssm.get_parameters(parameters_mapping)

        assert "Failed to retrieve SSM parameters" in str(exc_info.value)
        assert exc_info.value.data["parameter_names"] == ["/test/param"]


class TestPutSSMParameter:
    """Test suite for put_parameter function."""

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_put_parameter_success(self, mock_get_client):
        """Test successful parameter storage."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.put_parameter.return_value = {"Version": 1, "Tier": "Standard"}

        # Act
        result = ssm.put_parameter("/test/param", "test-value", True)

        # Assert
        assert result is None  # Function doesn't return the response
        mock_client.put_parameter.assert_called_once_with(
            Name="/test/param", Value="test-value", Type="SecureString", Overwrite=True
        )

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_put_parameter_custom_type(self, mock_get_client):
        """Test parameter storage with custom type."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Act
        ssm.put_parameter("/test/param", "test-value", False, "String")

        # Assert
        mock_client.put_parameter.assert_called_once_with(
            Name="/test/param", Value="test-value", Type="String", Overwrite=False
        )

    @patch("baresquare_sdk.aws.ssm.get_client")
    @patch("baresquare_sdk.aws.ssm.logger")
    def test_put_parameter_client_error(self, mock_logger, mock_get_client):
        """Test parameter storage with ClientError."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "ParameterAlreadyExists"}}, operation_name="put_parameter"
        )
        mock_client.put_parameter.side_effect = error

        # Act & Assert
        with pytest.raises(ExceptionInfo):
            ssm.put_parameter("/test/param", "test-value", False)

        mock_logger.error.assert_called_once_with("Failed to put SSM param /test/param")

    @patch("baresquare_sdk.aws.ssm.get_client")
    @patch("baresquare_sdk.aws.ssm.logger")
    def test_put_parameter_logs_debug(self, mock_logger, mock_get_client):
        """Test that parameter storage logs debug message."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Act
        ssm.put_parameter("/test/param", "test-value", True)

        # Assert
        mock_logger.debug.assert_called_once_with("Putting SSM param /test/param")


class TestSSMEdgeCases:
    """Test edge cases and unusual scenarios."""

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_empty_parameters_mapping(self, mock_get_client):
        """Test get_parameters with empty mapping."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Act
        result = ssm.get_parameters({})

        # Assert
        assert result == {}
        mock_client.get_parameters.assert_not_called()

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_get_parameter_with_extra_kwargs(self, mock_get_client):
        """Test that extra kwargs are ignored in get_parameter."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_parameter.return_value = {"Parameter": {"Value": "test-value"}}

        # Act
        result = ssm.get_parameter("/test/param", return_json=False, extra_arg="ignored")

        # Assert
        assert result == "test-value"
        mock_client.get_parameter.assert_called_once_with(Name="/test/param", WithDecryption=True)

    @patch("baresquare_sdk.aws.ssm.get_client")
    def test_json_parameter_with_complex_data(self, mock_get_client):
        """Test JSON parameter with complex nested data."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        complex_json = {"nested": {"deeply": {"value": 42}}, "array": [1, 2, 3], "boolean": True, "null_value": None}
        mock_client.get_parameter.return_value = {"Parameter": {"Value": json.dumps(complex_json)}}

        # Act
        result = ssm.get_parameter("/test/param", return_json=True)

        # Assert
        assert result == complex_json
