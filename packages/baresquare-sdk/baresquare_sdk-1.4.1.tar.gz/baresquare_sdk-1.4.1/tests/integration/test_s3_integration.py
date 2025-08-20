"""Integration tests for S3 functionality.

These tests require:
1. AWS credentials configured (profile, environment variables, or IAM role)
2. An S3 bucket for testing
3. Proper permissions for S3 operations

Run with: pytest -m integration tests/integration/
Skip with: pytest -m "not integration" tests/
"""

import logging
import os
import tempfile
from pathlib import Path

import pytest

from baresquare_sdk import aws, configure


@pytest.mark.integration
class TestS3Integration:
    """Integration tests for S3 operations with real AWS."""

    @pytest.fixture(autouse=True)
    def setup_sdk(self):
        """Configure SDK for integration tests."""
        # Check for required environment variables
        required_vars = ["AWS_PROFILE", "TEST_S3_BUCKET", "PL_ENV", "PL_SERVICE", "PL_REGION"]
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

        self.test_bucket = os.getenv("TEST_S3_BUCKET")
        self.test_prefix = "integration-tests/"
        self.s3_client = aws.s3.S3Client()

    def test_upload_and_download_file(self):
        """Test uploading and downloading a file to/from S3."""
        # Create a temporary file with test content
        test_content = "This is test content for S3 integration test"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Upload file to S3
            s3_key = f"{self.test_prefix}test-upload.txt"

            result = self.s3_client.upload_file(local_path=Path(temp_file_path), bucket=self.test_bucket, key=s3_key)

            assert result is True, "File upload should succeed"

            # Download file from S3
            download_path = tempfile.mktemp(suffix=".txt")

            success = self.s3_client.download_file(bucket=self.test_bucket, key=s3_key, local_path=Path(download_path))

            assert success is True, "File download should succeed"

            # Verify content matches
            with open(download_path, "r") as f:
                downloaded_content = f.read()

            assert downloaded_content == test_content, "Downloaded content should match uploaded content"

        finally:
            # Cleanup local files
            Path(temp_file_path).unlink(missing_ok=True)
            Path(download_path).unlink(missing_ok=True)

            # Cleanup S3 object
            try:
                self.s3_client.delete_file(bucket=self.test_bucket, key=s3_key)
            except Exception as e:
                logging.warning(f"Failed to clean up S3 object {s3_key}: {e}")

    def test_file_upload_with_invalid_bucket(self):
        """Test uploading to a non-existent bucket fails gracefully."""
        test_content = "Test content"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Try to upload to non-existent bucket - should raise exception
            with pytest.raises(Exception):  # Should raise S3UploadFailedError or similar
                self.s3_client.upload_file(
                    local_path=Path(temp_file_path), bucket="non-existent-bucket-12345", key="test.txt"
                )

        finally:
            Path(temp_file_path).unlink(missing_ok=True)
