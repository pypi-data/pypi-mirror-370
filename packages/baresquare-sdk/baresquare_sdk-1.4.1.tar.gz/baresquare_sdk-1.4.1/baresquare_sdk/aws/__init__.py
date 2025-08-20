"""Baresquare AWS Python utilities.

This package provides AWS-specific utilities for Baresquare services.
"""

try:
    # Check if AWS dependencies are available
    import boto3  # noqa: F401

    from baresquare_sdk.aws import authentication
    from baresquare_sdk.aws import s3
    from baresquare_sdk.aws import ssm

    from baresquare_sdk.core.logger import setup_logger

    logger = setup_logger()

    __all__ = ["authentication", "s3", "ssm", "logger"]

except ImportError as e:
    raise ImportError("AWS dependencies not found. Install with: pip install baresquare-sdk[aws]") from e
