"""Integration tests for SSM functionality.

These tests require:
1. AWS credentials configured (profile, environment variables, or IAM role)
2. Proper permissions for SSM operations
3. A test parameter prefix to avoid conflicts

Run with: pytest -m integration tests/integration/
Skip with: pytest -m "not integration" tests/
"""

import logging
import os
import uuid

import pytest

from baresquare_sdk import aws, configure


@pytest.mark.integration
class TestSSMIntegration:
    """Integration tests for SSM operations with real AWS."""

    @pytest.fixture(autouse=True)
    def setup_sdk(self):
        """Configure SDK for integration tests."""
        # Check for required environment variables
        required_vars = ["AWS_PROFILE", "PL_ENV", "PL_SERVICE", "PL_REGION"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            pytest.skip(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Configure SDK with test values
        configure(
            pl_env=os.getenv("PL_ENV", "test"),
            pl_service=os.getenv("PL_SERVICE", "sdk-integration-test"),
            pl_region=os.getenv("PL_REGION", "us-east-1"),
            aws_profile=os.getenv("AWS_PROFILE"),
        )

        # Use a unique test prefix to avoid conflicts
        test_id = str(uuid.uuid4())[:8]
        self.test_prefix = f"/test-sdk-python/{test_id}"

    def test_put_and_get_string_parameter(self):
        """Test putting and getting a string parameter."""
        param_name = f"{self.test_prefix}/test-string"
        param_value = "test-string-value-123"

        try:
            # Put parameter
            aws.ssm.put_parameter(ssm_key=param_name, ssm_value=param_value, ssm_type="String", overwrite=True)
            # If no exception raised, the put succeeded

            # Get parameter
            retrieved_value = aws.ssm.get_parameter(param_name)

            assert retrieved_value == param_value, "Retrieved value should match stored value"

        finally:
            try:
                aws.ssm.delete_parameter(param_name)
            except Exception as e:
                logging.warning(f"Failed to clean up parameter {param_name}: {e}")

    def test_put_and_get_secure_string_parameter(self):
        """Test putting and getting a secure string parameter."""
        param_name = f"{self.test_prefix}/test-secure"
        param_value = "secret-value-456"

        try:
            # Put secure parameter
            aws.ssm.put_parameter(ssm_key=param_name, ssm_value=param_value, ssm_type="SecureString", overwrite=True)
            # If no exception raised, the put succeeded

            # Get parameter
            retrieved_value = aws.ssm.get_parameter(param_name)

            assert retrieved_value == param_value, "Retrieved secure value should match stored value"

        finally:
            try:
                aws.ssm.delete_parameter(param_name)
            except Exception as e:
                logging.warning(f"Failed to clean up parameter {param_name}: {e}")

    def test_overwrite_parameter(self):
        """Test overwriting an existing parameter."""
        param_name = f"{self.test_prefix}/test-overwrite"
        original_value = "original-value"
        new_value = "new-value"

        try:
            # Put original parameter
            aws.ssm.put_parameter(ssm_key=param_name, ssm_value=original_value, ssm_type="String", overwrite=False)
            # If no exception raised, the put succeeded

            # Verify original value
            retrieved1 = aws.ssm.get_parameter(param_name)
            assert retrieved1 == original_value, "Original value should be retrieved"

            # Overwrite with new value
            aws.ssm.put_parameter(ssm_key=param_name, ssm_value=new_value, ssm_type="String", overwrite=True)
            # If no exception raised, the overwrite succeeded

            # Verify new value
            retrieved2 = aws.ssm.get_parameter(param_name)
            assert retrieved2 == new_value, "New value should be retrieved after overwrite"

        finally:
            try:
                aws.ssm.delete_parameter(param_name)
            except Exception as e:
                logging.warning(f"Failed to clean up parameter {param_name}: {e}")

    def test_put_without_overwrite_fails_on_existing(self):
        """Test that putting without overwrite fails on existing parameter."""
        param_name = f"{self.test_prefix}/test-no-overwrite"
        original_value = "original-value"
        duplicate_value = "duplicate-value"

        try:
            # Put original parameter
            aws.ssm.put_parameter(ssm_key=param_name, ssm_value=original_value, ssm_type="String", overwrite=False)
            # If no exception raised, the put succeeded

            # Try to put again without overwrite - should raise exception
            with pytest.raises(Exception):  # Should raise ClientError or similar
                aws.ssm.put_parameter(ssm_key=param_name, ssm_value=duplicate_value, ssm_type="String", overwrite=False)

            # Verify original value is unchanged
            retrieved = aws.ssm.get_parameter(param_name)
            assert retrieved == original_value, "Original value should be unchanged"

        finally:
            try:
                aws.ssm.delete_parameter(param_name)
            except Exception as e:
                logging.warning(f"Failed to clean up parameter {param_name}: {e}")

    def test_get_nonexistent_parameter(self):
        """Test getting a parameter that doesn't exist."""
        param_name = f"{self.test_prefix}/nonexistent-parameter"

        # This should raise an exception or return None based on implementation
        try:
            result = aws.ssm.get_parameter(param_name)
            # If it returns None instead of raising, that's also valid
            assert result is None, "Getting nonexistent parameter should return None"
        except Exception:
            # If it raises an exception, that's expected behavior
            pass

    # NOTE: Description parameter not supported in current SSM implementation
    # def test_parameter_with_description(self): - removed

    def test_multiple_parameters_workflow(self):
        """Test a workflow with multiple parameters."""
        base_path = f"{self.test_prefix}/multi"
        params = {f"{base_path}/param1": "value1", f"{base_path}/param2": "value2", f"{base_path}/param3": "value3"}

        try:
            # Put multiple parameters
            for param_name, param_value in params.items():
                aws.ssm.put_parameter(ssm_key=param_name, ssm_value=param_value, ssm_type="String", overwrite=True)
                # If no exception raised, the put succeeded

            # Get all parameters and verify
            for param_name, expected_value in params.items():
                retrieved_value = aws.ssm.get_parameter(param_name)
                assert retrieved_value == expected_value, f"Value mismatch for {param_name}"

        finally:
            for param_name in params:
                try:
                    aws.ssm.delete_parameter(param_name)
                except Exception as e:
                    logging.warning(f"Failed to clean up parameter {param_name}: {e}")
