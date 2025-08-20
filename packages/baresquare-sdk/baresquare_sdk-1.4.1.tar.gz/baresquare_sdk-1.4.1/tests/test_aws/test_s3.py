"""Tests for S3 functionality using mocking."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from baresquare_sdk.aws.s3 import S3Client


class TestS3Client:
    """Test suite for S3Client class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_bucket = "test-bucket"
        self.test_key = "test/file.txt"
        self.test_local_path = Path("/tmp/test_file.txt")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_s3_client_initialization_default(self, mock_boto3_client):
        """Test that S3Client initializes with default boto3 client."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Act
        s3_client = S3Client()

        # Assert
        mock_boto3_client.assert_called_once_with("s3")
        assert s3_client.client == mock_client

    @patch("baresquare_sdk.aws.s3.boto3.Session")
    def test_s3_client_initialization_with_profile(self, mock_session):
        """Test that S3Client initializes with specified profile."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_client = MagicMock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        # Act
        s3_client = S3Client(profile_name="test-profile")

        # Assert
        mock_session.assert_called_once_with(profile_name="test-profile")
        mock_session_instance.client.assert_called_once_with("s3")
        assert s3_client.client == mock_client

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_download_file_success(self, mock_boto3_client):
        """Test successful file download from S3."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.download_file.return_value = None  # Success returns None

        s3_client = S3Client()

        # Act
        result = s3_client.download_file(self.test_bucket, self.test_key, self.test_local_path)

        # Assert
        assert result is True
        mock_client.download_file.assert_called_once_with(self.test_bucket, self.test_key, str(self.test_local_path))

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_download_file_client_error(self, mock_boto3_client):
        """Test download file handles ClientError gracefully."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.download_file.side_effect = ClientError(
            error_response={"Error": {"Code": "NoSuchBucket", "Message": "The specified bucket does not exist"}},
            operation_name="download_file",
        )

        s3_client = S3Client()

        # Act
        result = s3_client.download_file(self.test_bucket, self.test_key, self.test_local_path)

        # Assert
        assert result is False
        mock_client.download_file.assert_called_once_with(self.test_bucket, self.test_key, str(self.test_local_path))

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch("baresquare_sdk.aws.s3.logger")
    def test_download_file_logs_error(self, mock_logger, mock_boto3_client):
        """Test that download file logs errors when ClientError occurs."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            operation_name="download_file",
        )
        mock_client.download_file.side_effect = error

        s3_client = S3Client()

        # Act
        result = s3_client.download_file(self.test_bucket, self.test_key, self.test_local_path)

        # Assert
        assert result is False
        mock_logger.error.assert_called_once_with(f"Error downloading from S3: {str(error)}")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_upload_file_success(self, mock_boto3_client):
        """Test successful file upload to S3."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.upload_file.return_value = None  # Success returns None

        s3_client = S3Client()

        # Act
        result = s3_client.upload_file(self.test_local_path, self.test_bucket, self.test_key)

        # Assert
        assert result is True
        mock_client.upload_file.assert_called_once_with(str(self.test_local_path), self.test_bucket, self.test_key)

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_upload_file_client_error(self, mock_boto3_client):
        """Test upload file handles ClientError gracefully."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.upload_file.side_effect = ClientError(
            error_response={"Error": {"Code": "InvalidBucketName", "Message": "The specified bucket is not valid"}},
            operation_name="upload_file",
        )

        s3_client = S3Client()

        # Act
        result = s3_client.upload_file(self.test_local_path, self.test_bucket, self.test_key)

        # Assert
        assert result is False
        mock_client.upload_file.assert_called_once_with(str(self.test_local_path), self.test_bucket, self.test_key)

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch("baresquare_sdk.aws.s3.logger")
    def test_upload_file_logs_error(self, mock_logger, mock_boto3_client):
        """Test that upload file logs errors when ClientError occurs."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "NoSuchBucket", "Message": "Bucket not found"}},
            operation_name="upload_file",
        )
        mock_client.upload_file.side_effect = error

        s3_client = S3Client()

        # Act
        result = s3_client.upload_file(self.test_local_path, self.test_bucket, self.test_key)

        # Assert
        assert result is False
        mock_logger.error.assert_called_once_with(f"Error uploading to S3: {str(error)}")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_delete_file_success(self, mock_boto3_client):
        """Test successful file deletion from S3."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.delete_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 204}}

        s3_client = S3Client()

        # Act
        result = s3_client.delete_file(self.test_bucket, self.test_key)

        # Assert
        assert result is True
        mock_client.delete_object.assert_called_once_with(Bucket=self.test_bucket, Key=self.test_key)

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_delete_file_client_error(self, mock_boto3_client):
        """Test delete file handles ClientError gracefully."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.delete_object.side_effect = ClientError(
            error_response={"Error": {"Code": "NoSuchKey", "Message": "The specified key does not exist"}},
            operation_name="delete_object",
        )

        s3_client = S3Client()

        # Act
        result = s3_client.delete_file(self.test_bucket, self.test_key)

        # Assert
        assert result is False
        mock_client.delete_object.assert_called_once_with(Bucket=self.test_bucket, Key=self.test_key)

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch("baresquare_sdk.aws.s3.logger")
    def test_delete_file_logs_error(self, mock_logger, mock_boto3_client):
        """Test that delete file logs errors when ClientError occurs."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            operation_name="delete_object",
        )
        mock_client.delete_object.side_effect = error

        s3_client = S3Client()

        # Act
        result = s3_client.delete_file(self.test_bucket, self.test_key)

        # Assert
        assert result is False
        mock_logger.error.assert_called_once_with(f"Error deleting from S3: {str(error)}")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_list_files_success(self, mock_boto3_client):
        """Test successful file listing from S3."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator

        mock_pages = [
            {"Contents": [{"Key": "folder/file1.txt"}, {"Key": "folder/file2.txt"}]},
            {"Contents": [{"Key": "folder/file3.txt"}]},
        ]
        mock_paginator.paginate.return_value = mock_pages

        s3_client = S3Client()

        # Act
        result = s3_client.list_files(self.test_bucket, "folder/")

        # Assert
        expected_files = ["folder/file1.txt", "folder/file2.txt", "folder/file3.txt"]
        assert result == expected_files
        mock_client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_paginator.paginate.assert_called_once_with(Bucket=self.test_bucket, Prefix="folder/")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_list_files_empty_result(self, mock_boto3_client):
        """Test file listing when no files are found."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator

        mock_pages = [{"Contents": []}, {}]  # Empty results
        mock_paginator.paginate.return_value = mock_pages

        s3_client = S3Client()

        # Act
        result = s3_client.list_files(self.test_bucket, "empty-folder/")

        # Assert
        assert result == []
        mock_client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_paginator.paginate.assert_called_once_with(Bucket=self.test_bucket, Prefix="empty-folder/")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_list_files_client_error(self, mock_boto3_client):
        """Test list files handles ClientError gracefully."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.get_paginator.side_effect = ClientError(
            error_response={"Error": {"Code": "NoSuchBucket", "Message": "Bucket not found"}},
            operation_name="list_objects_v2",
        )

        s3_client = S3Client()

        # Act
        result = s3_client.list_files(self.test_bucket, "folder/")

        # Assert
        assert result == []

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch("baresquare_sdk.aws.s3.logger")
    def test_list_files_logs_error(self, mock_logger, mock_boto3_client):
        """Test that list files logs errors when ClientError occurs."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            operation_name="list_objects_v2",
        )
        mock_client.get_paginator.side_effect = error

        s3_client = S3Client()

        # Act
        result = s3_client.list_files(self.test_bucket, "folder/")

        # Assert
        assert result == []
        mock_logger.error.assert_called_once_with(f"Error listing files in S3: {str(error)}")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_list_buckets_success(self, mock_boto3_client):
        """Test successful bucket listing."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.list_buckets.return_value = {
            "Buckets": [
                {"Name": "bucket1"},
                {"Name": "bucket2"},
                {"Name": "bucket3"},
            ]
        }

        s3_client = S3Client()

        # Act
        result = s3_client.list_buckets()

        # Assert
        expected_buckets = ["bucket1", "bucket2", "bucket3"]
        assert result == expected_buckets
        mock_client.list_buckets.assert_called_once()

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_list_buckets_empty_result(self, mock_boto3_client):
        """Test bucket listing when no buckets exist."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.list_buckets.return_value = {"Buckets": []}

        s3_client = S3Client()

        # Act
        result = s3_client.list_buckets()

        # Assert
        assert result == []
        mock_client.list_buckets.assert_called_once()

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_list_buckets_client_error(self, mock_boto3_client):
        """Test list buckets handles ClientError gracefully."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.list_buckets.side_effect = ClientError(
            error_response={"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            operation_name="list_buckets",
        )

        s3_client = S3Client()

        # Act
        result = s3_client.list_buckets()

        # Assert
        assert result == []

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch("baresquare_sdk.aws.s3.logger")
    def test_list_buckets_logs_error(self, mock_logger, mock_boto3_client):
        """Test that list buckets logs errors when ClientError occurs."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            operation_name="list_buckets",
        )
        mock_client.list_buckets.side_effect = error

        s3_client = S3Client()

        # Act
        result = s3_client.list_buckets()

        # Assert
        assert result == []
        mock_logger.error.assert_called_once_with(f"Error listing buckets in S3: {str(error)}")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_bucket_exists_true(self, mock_boto3_client):
        """Test bucket exists when bucket is found."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.head_bucket.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        s3_client = S3Client()

        # Act
        result = s3_client.bucket_exists(self.test_bucket)

        # Assert
        assert result is True
        mock_client.head_bucket.assert_called_once_with(Bucket=self.test_bucket)

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_bucket_exists_false(self, mock_boto3_client):
        """Test bucket exists when bucket is not found."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.head_bucket.side_effect = ClientError(
            error_response={"Error": {"Code": "404", "Message": "Not Found"}},
            operation_name="head_bucket",
        )

        s3_client = S3Client()

        # Act
        result = s3_client.bucket_exists(self.test_bucket)

        # Assert
        assert result is False
        mock_client.head_bucket.assert_called_once_with(Bucket=self.test_bucket)

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_bucket_exists_raises_unauthorized_exception(self, mock_boto3_client):
        """Test that bucket exists raises UnauthorizedException for 403 errors."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "403", "Message": "Access Denied"}},
            operation_name="head_bucket",
        )
        mock_client.head_bucket.side_effect = error

        s3_client = S3Client()

        # Act & Assert
        from baresquare_sdk.aws.authentication import UnauthorizedException

        with pytest.raises(UnauthorizedException) as exc_info:
            s3_client.bucket_exists(self.test_bucket)

        assert str(exc_info.value) == f"403: You don't have access to bucket {self.test_bucket}"

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch("baresquare_sdk.aws.s3.logger")
    def test_bucket_exists_logs_error_for_other_errors(self, mock_logger, mock_boto3_client):
        """Test that bucket exists logs errors for non-404/403 ClientError."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        error = ClientError(
            error_response={"Error": {"Code": "InternalError", "Message": "Internal Server Error"}},
            operation_name="head_bucket",
        )
        mock_client.head_bucket.side_effect = error

        s3_client = S3Client()

        # Act
        result = s3_client.bucket_exists(self.test_bucket)

        # Assert
        assert result is False
        mock_logger.error.assert_called_once_with(f"Error checking if bucket exists in S3: {str(error)}")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_path_conversion_download(self, mock_boto3_client):
        """Test that Path objects are converted to strings in download_file."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        # Act
        s3_client.download_file(self.test_bucket, self.test_key, self.test_local_path)

        # Assert - verify string conversion happened
        mock_client.download_file.assert_called_once_with(
            self.test_bucket,
            self.test_key,
            str(self.test_local_path),  # Should be converted to string
        )

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_path_conversion_upload(self, mock_boto3_client):
        """Test that Path objects are converted to strings in upload_file."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        # Act
        s3_client.upload_file(self.test_local_path, self.test_bucket, self.test_key)

        # Assert - verify string conversion happened
        mock_client.upload_file.assert_called_once_with(
            str(self.test_local_path),  # Should be converted to string
            self.test_bucket,
            self.test_key,
        )

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_multiple_operations_use_same_client(self, mock_boto3_client):
        """Test that multiple operations on same S3Client instance use the same boto3 client."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        # Act
        s3_client.download_file(self.test_bucket, "file1.txt", Path("/tmp/file1.txt"))
        s3_client.upload_file(Path("/tmp/file2.txt"), self.test_bucket, "file2.txt")
        s3_client.delete_file(self.test_bucket, "file3.txt")
        s3_client.list_files(self.test_bucket, "folder/")

        # Assert
        # boto3.client should only be called once during initialization
        mock_boto3_client.assert_called_once_with("s3")

        # All operations should use the same mock client
        assert mock_client.download_file.call_count == 1
        assert mock_client.upload_file.call_count == 1
        assert mock_client.delete_object.call_count == 1
        assert mock_client.get_paginator.call_count == 1


class TestS3ClientProfileInitialization:
    """Test suite for S3Client profile-based initialization."""

    @patch("baresquare_sdk.aws.s3.boto3.client")
    @patch.dict(os.environ, {"AWS_PROFILE": "env-profile"})
    def test_initialization_default_with_env_profile_set(self, mock_boto3_client):
        """Test that S3Client uses default boto3 client even when AWS_PROFILE is set in environment."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        # Act
        s3_client = S3Client()

        # Assert - should use default client since S3Client doesn't check AWS_PROFILE
        mock_boto3_client.assert_called_once_with("s3")
        assert s3_client.client == mock_client

    @patch("baresquare_sdk.aws.s3.boto3.Session")
    @patch.dict(os.environ, {"AWS_PROFILE": "env-profile"})
    def test_profile_parameter_overrides_env(self, mock_session):
        """Test that explicit profile parameter overrides environment variable."""
        # Arrange
        mock_session_instance = MagicMock()
        mock_client = MagicMock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance

        # Act
        s3_client = S3Client(profile_name="explicit-profile")

        # Assert
        mock_session.assert_called_once_with(profile_name="explicit-profile")
        mock_session_instance.client.assert_called_once_with("s3")
        assert s3_client.client == mock_client


# Additional test for edge cases and error scenarios
class TestS3ClientEdgeCases:
    """Test edge cases and unusual scenarios."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_bucket = "test-bucket"
        self.test_key = "test/file.txt"
        self.test_local_path = Path("/tmp/test_file.txt")

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_empty_strings_handled(self, mock_boto3_client):
        """Test that empty strings are handled without crashing."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        # Act & Assert - should not raise exceptions
        result = s3_client.download_file("", "", Path(""))
        assert result is True  # Assuming boto3 handles empty strings

        result = s3_client.upload_file(Path(""), "", "")
        assert result is True

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_special_characters_in_paths(self, mock_boto3_client):
        """Test handling of special characters in bucket names and keys."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        s3_client = S3Client()

        special_bucket = "test-bucket-with-dashes"
        special_key = "folder/subfolder/file with spaces & symbols!.txt"
        special_path = Path("/tmp/file with spaces.txt")

        # Act
        s3_client.download_file(special_bucket, special_key, special_path)

        # Assert
        mock_client.download_file.assert_called_once_with(special_bucket, special_key, str(special_path))

    @patch("baresquare_sdk.aws.s3.boto3.client")
    def test_list_files_with_empty_prefix(self, mock_boto3_client):
        """Test list files with empty prefix (should list all files)."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator

        mock_pages = [{"Contents": [{"Key": "file1.txt"}, {"Key": "file2.txt"}]}]
        mock_paginator.paginate.return_value = mock_pages

        s3_client = S3Client()

        # Act
        result = s3_client.list_files(self.test_bucket, "")

        # Assert
        expected_files = ["file1.txt", "file2.txt"]
        assert result == expected_files
        mock_paginator.paginate.assert_called_once_with(Bucket=self.test_bucket, Prefix="")
