from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from baresquare_sdk.aws.authentication import UnauthorizedException
from baresquare_sdk.core import logger


class S3Client:
    def __init__(self, profile_name: str | None = None):
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
            self.client = session.client("s3")
        else:
            self.client = boto3.client("s3")

    def download_file(self, bucket: str, key: str, local_path: Path) -> bool:
        """Download a file from S3 to a local path.
        Returns True if successful, False otherwise.
        """
        try:
            self.client.download_file(bucket, key, str(local_path))
            return True
        except ClientError as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            return False

    def upload_file(self, local_path: Path, bucket: str, key: str) -> bool:
        """Upload a file to S3 from a local path.
        Returns True if successful, False otherwise.
        """
        try:
            self.client.upload_file(str(local_path), bucket, key)
            return True
        except ClientError as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return False

    def delete_file(self, bucket: str, key: str) -> bool:
        """Delete a file from S3.
        Returns True if successful, False otherwise.
        """
        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting from S3: {str(e)}")
            return False

    def list_files(self, bucket: str, prefix: str) -> list[str]:
        """List files in an S3 bucket.
        Returns a list of file keys.
        """
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

            file_keys = []
            for page in pages:
                if "Contents" in page:
                    file_keys.extend([obj["Key"] for obj in page["Contents"]])

            return file_keys
        except ClientError as e:
            logger.error(f"Error listing files in S3: {str(e)}")
            return []

    def list_buckets(self) -> list[str]:
        """List all buckets in the S3 service.
        Returns a list of bucket names.
        """
        try:
            response = self.client.list_buckets()
            return [bucket["Name"] for bucket in response["Buckets"]]
        except ClientError as e:
            logger.error(f"Error listing buckets in S3: {str(e)}")
            return []

    def bucket_exists(self, bucket: str) -> bool:
        """Check if a bucket exists in the S3 service.
        Returns True if the bucket exists, False otherwise.
        Raises UnauthorizedException if you don't have access to it.
        """
        try:
            self.client.head_bucket(Bucket=bucket)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                return False
            if error_code == "403":
                raise UnauthorizedException(f"You don't have access to bucket {bucket}")
            logger.error(f"Error checking if bucket exists in S3: {str(e)}")
            return False
