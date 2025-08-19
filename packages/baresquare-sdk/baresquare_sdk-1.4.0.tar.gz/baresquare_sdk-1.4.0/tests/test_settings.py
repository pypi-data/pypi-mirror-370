"""Tests for the settings module."""

import os
from unittest.mock import patch

import pytest
from pydantic_core._pydantic_core import ValidationError

from baresquare_sdk.settings import Settings, configure, get_settings, reset_settings


class TestSettings:
    """Test Settings class validation and behavior."""

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_with_all_required_fields(self):
        """Test settings creation when all required fields are provided."""
        settings = Settings(pl_env="prod", pl_service="api-service", pl_region="eu-west-1")
        assert settings.pl_env == "prod"
        assert settings.pl_service == "api-service"
        assert settings.pl_region == "eu-west-1"
        assert settings.auth0_domain is None
        assert settings.auth0_api_audience is None
        assert settings.aws_profile is None

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_missing_pl_env_raises_validation_error(self):
        """Test settings creation fails when pl_env is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(pl_service="api-service", pl_region="eu-west-1")

        assert "pl_env" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_missing_pl_service_raises_validation_error(self):
        """Test settings creation fails when pl_service is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(pl_env="prod", pl_region="eu-west-1")

        assert "pl_service" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_missing_pl_region_raises_validation_error(self):
        """Test settings creation fails when pl_region is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(pl_env="prod", pl_service="api-service")

        assert "pl_region" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_missing_all_required_fields_raises_validation_error(self):
        """Test settings creation fails when all required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value)
        assert "pl_env" in error_str
        assert "pl_service" in error_str
        assert "pl_region" in error_str
        assert "Field required" in error_str

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_invalid_pl_env_raises_validation_error(self):
        """Test settings creation fails with invalid pl_env value."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(pl_env="invalid", pl_service="api-service", pl_region="eu-west-1")

        assert "pl_env must be one of: dev, staging, prod, test, production" in str(exc_info.value)

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_empty_pl_region_raises_validation_error(self):
        """Test settings creation fails with empty pl_region."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(pl_env="prod", pl_service="api-service", pl_region="")

        assert "pl_region cannot be empty" in str(exc_info.value)

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_with_optional_fields(self):
        """Test settings creation with optional fields provided."""
        settings = Settings(
            pl_env="prod",
            pl_service="api-service",
            pl_region="eu-west-1",
            auth0_domain="company.auth0.com",
            auth0_api_audience="api-audience",
            aws_profile="production",
        )
        assert settings.auth0_domain == "company.auth0.com"
        assert settings.auth0_api_audience == "api-audience"
        assert settings.aws_profile == "production"


class TestSettingsFunctions:
    """Test global settings functions."""

    def setup_method(self):
        """Reset config before each test."""
        reset_settings()

    def teardown_method(self):
        """Clean up after each test."""
        reset_settings()

    @patch.dict(os.environ, {"PL_ENV": "prod", "PL_SERVICE": "test-service", "PL_REGION": "us-west-2"}, clear=True)
    def test_get_settings_reads_from_environment(self):
        """Test get_settings reads from environment variables."""
        settings = get_settings()
        assert settings.pl_env == "prod"
        assert settings.pl_service == "test-service"
        assert settings.pl_region == "us-west-2"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_settings_fails_without_required_env_vars(self):
        """Test get_settings fails when required environment variables are missing."""
        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        error_str = str(exc_info.value)
        assert "pl_env" in error_str
        assert "pl_service" in error_str
        assert "pl_region" in error_str

    def test_configure_with_explicit_values(self):
        """Test configure function with explicit values."""
        settings = configure(pl_env="staging", pl_service="my-service", pl_region="ap-south-1")
        assert settings.pl_env == "staging"
        assert settings.pl_service == "my-service"
        assert settings.pl_region == "ap-south-1"

    def test_configure_fails_with_missing_required_fields(self):
        """Test configure fails when required fields are missing."""
        with pytest.raises(ValidationError):
            configure(pl_env="prod")  # Missing pl_service and pl_region

    def test_get_settings_returns_same_instance_after_configure(self):
        """Test get_settings returns the configured instance."""
        settings1 = configure(pl_env="prod", pl_service="api", pl_region="eu-central-1")
        settings2 = get_settings()
        assert settings1 is settings2
        assert settings2.pl_env == "prod"
        assert settings2.pl_service == "api"
        assert settings2.pl_region == "eu-central-1"
