"""Settings management for Baresquare SDK.

This module provides centralized settings with automatic environment variable
loading, validation, and type safety using Pydantic BaseSettings.
"""

from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for Baresquare SDK.

    All settings can be provided via environment variables or set explicitly.
    Environment variables are automatically loaded by Pydantic.
    """

    # Platform settings (required)
    pl_env: str
    pl_service: str
    pl_region: str

    # Auth0 settings
    auth0_domain: Optional[str] = None
    auth0_api_audience: Optional[str] = None

    # AWS settings
    aws_profile: Optional[str] = None

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    @field_validator("pl_env")
    @classmethod
    def validate_env(cls, v):
        """Validate that pl_env is one of the allowed values."""
        if v not in ["dev", "staging", "prod", "test", "production"]:
            raise ValueError("pl_env must be one of: dev, staging, prod, test, production")
        return v

    @field_validator("pl_region")
    @classmethod
    def validate_region(cls, v):
        """Ensure region is not empty."""
        if not v or not v.strip():
            raise ValueError("pl_region cannot be empty")
        return v.strip()


# Global settings instance
_global_settings: Optional[Settings] = None


def configure(**kwargs) -> Settings:
    """Configure the SDK globally.

    Args:
        **kwargs: Settings parameters to override defaults or environment variables.

    Returns:
        Settings: The configured instance.

    Example:
        >>> from baresquare_sdk import configure
        >>> configure(pl_env="prod", auth0_domain="mycompany.auth0.com")
    """
    global _global_settings
    _global_settings = Settings(**kwargs)
    return _global_settings


def get_settings() -> Settings:
    """Get the current global settings.

    If no settings have been set explicitly, creates one from environment variables.

    Returns:
        Settings: The current settings instance.
    """
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings()
    return _global_settings


def reset_settings():
    """Reset global settings to None.

    Useful for testing to ensure clean state.
    """
    global _global_settings
    _global_settings = None


def _reload_settings():
    """Force reload settings from environment.

    Internal function used by tests to reload settings after environment changes.
    """
    global _global_settings
    _global_settings = Settings()
