#!/usr/bin/env python3

"""
S3 Object Operations: Upload and Delete Objects in Amazon S3.

This script provides functionality to:
1. Upload a file to an S3 bucket.
2. Delete a file from an S3 bucket.

Designed for usage in Python (pip), Docker, and AWS Lambda environments.

Author: nnthanh101@gmail.com
Date: 2025-01-08
Version: 1.0.0
"""

import logging
import os
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# ==============================
# CONFIGURATION VARIABLES
# ==============================
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "my-default-bucket")
S3_KEY = os.getenv("S3_KEY", "default-key.txt")
LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH", "default.txt")
ACL = os.getenv("ACL", "private")  ## Options: 'private', 'public-read', etc.

# ==============================
# LOGGING CONFIGURATION
# ==============================
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
try:
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    logger.info("✅ S3 client initialized successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize S3 client: {e}")
    raise


# ==============================
# UPLOAD FUNCTION
# ==============================
def put_object(bucket: str, key: str, file_path: str, acl: str = "private") -> None:
    """
    Uploads a file to an S3 bucket.

    Args:
        bucket (str): The name of the S3 bucket.
        key (str): The object key in S3.
        file_path (str): Local file path to be uploaded.
        acl (str): Access control list (default: 'private').

    Raises:
        Exception: Any upload failure.
    """
    try:
        # ✅ Check if the file exists locally
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")

        logger.info(f"🚀 Uploading '{file_path}' to bucket '{bucket}' with key '{key}'...")
        with open(file_path, "rb") as file_reader:
            s3_client.put_object(ACL=acl, Body=file_reader, Bucket=bucket, Key=key)
        logger.info(f"✅ File '{file_path}' uploaded successfully to '{bucket}/{key}'.")

    except FileNotFoundError as e:
        logger.error(f"❌ File Not Found: {e}")
        raise

    except ClientError as e:
        logger.error(f"❌ AWS Client Error: {e}")
        raise

    except BotoCoreError as e:
        logger.error(f"❌ BotoCore Error: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")
        raise


# ==============================
# DELETE FUNCTION
# ==============================
def delete_object(bucket: str, key: str) -> None:
    """
    Deletes an object from an S3 bucket.

    Args:
        bucket (str): The name of the S3 bucket.
        key (str): The object key to delete.

    Raises:
        Exception: Any deletion failure.
    """
    try:
        logger.info(f"🗑️ Deleting object '{key}' from bucket '{bucket}'...")
        s3_client.delete_object(Bucket=bucket, Key=key)
        logger.info(f"✅ Object '{key}' deleted successfully from '{bucket}'.")

    except ClientError as e:
        logger.error(f"❌ AWS Client Error: {e}")
        raise

    except BotoCoreError as e:
        logger.error(f"❌ BotoCore Error: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")
        raise


# ==============================
# MAIN FUNCTION (CLI/DOCKER)
# ==============================
def main():
    """
    Main entry point for CLI/Docker execution.
    """
    try:
        # ✅ Upload Object
        put_object(S3_BUCKET, S3_KEY, LOCAL_FILE_PATH, ACL)

        # ✅ Delete Object (Uncomment if needed)
        # delete_object(S3_BUCKET, S3_KEY)

    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise


# ==============================
# AWS LAMBDA HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda handler for S3 object operations.

    Args:
        event (dict): AWS Lambda event payload with 'action', 'bucket', 'key', and 'file_path'.
        context: AWS Lambda context object.

    Returns:
        dict: Status code and message.
    """
    try:
        action = event.get("action")  # 'upload' or 'delete'
        bucket = event.get("bucket", S3_BUCKET)
        key = event.get("key", S3_KEY)
        file_path = event.get("file_path", LOCAL_FILE_PATH)
        acl = event.get("acl", ACL)

        if action == "upload":
            put_object(bucket, key, file_path, acl)
            return {"statusCode": 200, "body": f"File '{key}' uploaded to '{bucket}'."}
        elif action == "delete":
            delete_object(bucket, key)
            return {"statusCode": 200, "body": f"File '{key}' deleted from '{bucket}'."}
        else:
            raise ValueError("Invalid action. Supported actions: 'upload', 'delete'.")

    except Exception as e:
        logger.error(f"❌ Lambda Error: {e}")
        return {"statusCode": 500, "body": str(e)}


# ==============================
# SCRIPT ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
