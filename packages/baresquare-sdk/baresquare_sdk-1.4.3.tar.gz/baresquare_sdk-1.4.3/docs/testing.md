# Testing Guide

This document describes the testing structure and approach for the Baresquare SDK.

## Test Configuration

### Global Fixtures (`conftest.py`)

- **`reset_sdk_settings`**: Automatically resets SDK settings before and after each test to ensure test isolation

### Environment Setup

Tests extensively use `@patch.dict(os.environ, {...}, clear=True)` to:
- Set required environment variables (`PL_ENV`, `PL_SERVICE`, `PL_REGION`)
- Clear existing environment to avoid test pollution
- Ensure consistent test conditions

## Testing Approach

### Unit Testing with Mocking

All tests use comprehensive mocking to avoid external dependencies:

- **HTTP calls**: Mocked using `unittest.mock.patch`
- **AWS services**: Mocked to avoid real AWS API calls
- **File system operations**: Isolated using temporary files/directories
- **Environment variables**: Controlled via `patch.dict`

### Key Test Categories

#### 1. Settings Tests (`test_settings.py`)
- Validation of required fields (`pl_env`, `pl_service`, `pl_region`)
- Environment variable loading
- Global settings management
- Configuration validation rules

#### 2. Authentication Tests (`test_authentication.py`)
- JWT token verification with Auth0
- Token expiration checking
- SSM token caching
- Error handling for invalid tokens
- Security exception handling

#### 3. AWS Integration Tests
- **S3 operations**: Upload, download, listing
- **SSM operations**: Parameter retrieval and storage
- Credential management and profiles

#### 4. Logging Tests (`test_logger.py`)
- JSON log formatting
- Secret sanitization
- Request context integration
- Exception logging
- Environment-specific behavior

## Running Tests

### Prerequisites
Ensure you have pytest installed:
```bash
pip install pytest
```

### Running All Tests
```bash
pytest
```

### Running Specific Test Modules
```bash
pytest tests/test_settings.py
pytest tests/test_aws/
pytest tests/test_core/
```

### Running with Coverage
```bash
pytest --cov=src/baresquare_sdk --cov-report=html
```

## Test Best Practices

### 1. Test Isolation
- Each test resets SDK settings via `reset_sdk_settings` fixture
- Environment variables are cleared and set explicitly per test
- No shared state between tests

### 2. Comprehensive Mocking
- All external dependencies are mocked
- HTTP requests, AWS API calls, and file operations are isolated
- Tests focus on logic rather than integration

### 3. Security Testing
- Secrets are never exposed in test outputs
- Authentication flows are thoroughly tested
- Error conditions are validated

### 4. Error Testing
- Each module tests both success and failure scenarios
- Exception handling is validated
- Edge cases are covered

## Test Data Management

### Environment Variables
Tests consistently use these environment variables:
- `PL_ENV`: Environment name (`dev`, `staging`, `prod`, `test`)
- `PL_SERVICE`: Service identifier
- `PL_REGION`: AWS region

### Mock Data
- JWT tokens: Use realistic but fake token structures
- AWS responses: Mirror actual AWS API response formats
- Configuration data: Use realistic but non-sensitive values

## Adding New Tests

When adding new functionality:

1. **Create corresponding test file** following the `test_*.py` naming convention
2. **Use the existing mocking patterns** for external dependencies
3. **Test both success and error paths**
4. **Include environment variable setup** using `@patch.dict`
5. **Validate security aspects** if handling sensitive data
6. **Follow the existing class structure** with descriptive test class names

## Integration Tests

### Overview

The integration tests found in `tests/integration/`:
- do not use mocking; they perform CRUD operations on AWS
- are only for testing from local and do not run in the CI (via pytest markers)
- take care to avoid conflicts with existing AWS resources
- clean up after themselves

### Running Integration Tests

1. **AWS credentials** configured via `~/aws_cli_mfa.py -u <username> -t <totp>`
   
2. **Required environment variables**:
   ```bash
   export AWS_PROFILE=bsq-test-us
   export PL_ENV=test
   export PL_SERVICE=my-service
   export PL_REGION=us-east-1
   export TEST_S3_BUCKET=baresquare.us-east-1.test.test-bucket 
   ```

3. Run **only integration tests**:
   ```bash
   pytest -m integration tests/integration/
   ```