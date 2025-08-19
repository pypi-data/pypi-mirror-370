"""Baresquare Core Python utilities.

This package provides core utilities and functionality used across Baresquare Python services.
"""

from . import exceptions
from . import middleware
from . import logger as logger_module

from .logger import setup_logger

logger = logger_module.logger

__all__ = ["exceptions", "middleware", "logger_module", "setup_logger", "logger"]
