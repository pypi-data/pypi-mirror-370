# User Guide

## Installation

```shell
# Core functionality only
pip install baresquare-sdk

# With AWS integrations
pip install baresquare-sdk[aws]
```

## Configuration

Before using the SDK, configure it with your service settings:

```python
from baresquare_sdk import configure

# Configure SDK globally
settings = Settings()
configure(
    pl_env=settings.pl_env,
    pl_service=settings.pl_service,
    pl_region=settings.pl_region,
    aws_profile=settings.aws_profile
)
```

## Usage

### Import Styles

The SDK supports flexible import patterns optimized for readability:

```python
# Top-level modules: namespace improves clarity
from baresquare_sdk import aws
aws.s3.some_function()  # Clear that this is AWS S3

# Nested modules: direct import reduces verbosity 
from baresquare_sdk.core import middleware
middleware.cors  # Better than core.middleware.cors

# Frequently used utilities: direct import for convenience
from baresquare_sdk.core import logger, exceptions
logger.info('message')  # Better than core.logger.info
```

### Core Features

**Logger:**

```python
from baresquare_sdk.core import logger

logger.info('Service started')
logger.error('Something went wrong')
logger.warn('Deprecated feature used')
```

**Middleware:**

```python
from baresquare_sdk.core import middleware

# Use middleware components in your FastAPI/Flask applications
middleware.cors
middleware.compression
middleware.request_info
```

**Exceptions:**

```python
from baresquare_sdk import core

# Use custom exception classes
core.exceptions
```

### AWS Features

**Note:** Requires installing with `[aws]` extra.

```python
from baresquare_sdk import aws

# AWS S3 operations
aws.s3

# AWS Systems Manager Parameter Store
aws.ssm

# AWS authentication utilities
aws.authentication
```