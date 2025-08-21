#!/usr/bin/env python3
"""
AWS S3 Bucket Creator Script.

Author: nnthanh101@gmail.com
Date: 2025-01-09
Version: 1.0.0
"""

import os
import sys
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from runbooks.utils.logger import configure_logger  # # Import reusable logger

## Initialize Logger
logger = configure_logger("list_s3_buckets")

# ==============================
# CONFIGURATION VARIABLES
# ==============================
DEFAULT_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "1cloudops")  # Default bucket name
DEFAULT_REGION = os.getenv("AWS_REGION", "ap-southeast-2")  # Default AWS region


# ==============================
# VALIDATION UTILITIES
# ==============================
def validate_bucket_name(bucket_name: str) -> None:
    """
    Validates an S3 bucket name based on AWS naming rules.

    Args:
        bucket_name (str): The bucket name to validate.

    Raises:
        ValueError: If the bucket name is invalid.
    """
    import re

    ## ✅ AWS Bucket Naming Rules
    if len(bucket_name) < 3 or len(bucket_name) > 63:
        raise ValueError("Bucket name must be between 3 and 63 characters long.")

    if not re.match(r"^[a-z0-9.-]+$", bucket_name):
        raise ValueError("Bucket name can only contain lowercase letters, numbers, hyphens (-), and periods (.).")

    if bucket_name.startswith(".") or bucket_name.endswith("."):
        raise ValueError("Bucket name cannot start or end with a period (.)")

    if ".." in bucket_name:
        raise ValueError("Bucket name cannot contain consecutive periods (..).")

    logger.info(f"✅ Bucket name '{bucket_name}' is valid.")


# ==============================
# CORE FUNCTION: CREATE BUCKET
# ==============================
def create_s3_bucket(bucket_name: str, region: str) -> Optional[str]:
    """
    Creates an S3 bucket in the specified AWS region.

    Args:
        bucket_name (str): The name of the S3 bucket to create.
        region (str): The AWS region where the bucket will be created.

    Returns:
        Optional[str]: The location of the created bucket if successful, None otherwise.

    Raises:
        Exception: Raises error if bucket creation fails.
    """
    ## ✅ Initialize S3 Client
    try:
        s3_client = boto3.client("s3", region_name=region)
        logger.info(f"Creating bucket '{bucket_name}' in region '{region}'...")

        ## ✅ Create bucket with LocationConstraint
        if region == "us-east-1":  ## Special case: us-east-1 doesn't require LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                ACL="private",  ## Set access control to private
            )
        else:
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                ACL="private",
                CreateBucketConfiguration={"LocationConstraint": region},
            )

        logger.info(f"✅ Bucket '{bucket_name}' created successfully at {response['Location']}.")
        return response["Location"]

    except ClientError as e:
        logger.error(f"❌ AWS Client Error: {e}")
        raise

    except BotoCoreError as e:
        logger.error(f"❌ BotoCore Error: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise


# ==============================
# MAIN FUNCTION
# ==============================
def main() -> None:
    """
    Main entry point for script execution.
    """
    try:
        ## ✅ Parse Arguments or Use Environment Variables
        bucket_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BUCKET_NAME
        region = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_REGION

        ## ✅ Validate Input
        validate_bucket_name(bucket_name)

        ## ✅ Create S3 Bucket
        create_s3_bucket(bucket_name, region)

    except ValueError as e:
        logger.error(f"❌ Input Validation Error: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Fatal Error: {e}")
        sys.exit(1)


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
