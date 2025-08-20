"""Baresquare SDK for Python.

This package provides core utilities and AWS integrations for Baresquare services.
"""

# Make submodules available for import
from . import core

# Only import aws if dependencies are available
try:
    from . import aws
except ImportError:
    # AWS dependencies not installed
    aws = None

# Configuration functions
from .settings import configure, get_settings, reset_settings, _reload_settings

__all__ = ["core", "aws", "configure", "get_settings", "reset_settings", "_reload_settings"]
