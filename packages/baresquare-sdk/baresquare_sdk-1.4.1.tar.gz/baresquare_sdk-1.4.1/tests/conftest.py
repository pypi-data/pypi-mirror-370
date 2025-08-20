"""Test settings and fixtures for baresquare_sdk tests."""

import pytest

from baresquare_sdk.settings import reset_settings


@pytest.fixture(autouse=True)
def reset_sdk_settings():
    """Reset SDK settings before and after each test."""
    reset_settings()
    yield
    reset_settings()
