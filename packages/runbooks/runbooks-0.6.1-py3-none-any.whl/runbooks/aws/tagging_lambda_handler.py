#!/usr/bin/env python3

"""
AWS Lambda Function for Auto-Tagging EC2 Instances Based on S3 Configuration.

Author: nnthanh101@gmail.com
Date: 2025-01-07
Version: 1.0.0

Description:
    - Fetches tagging configuration from an S3 bucket.
    - Applies tags dynamically to an EC2 instance when triggered by AWS CloudTrail events.

Requirements:
    - IAM Role Permissions:
        * s3:GetObject
        * ec2:CreateTags
        * sts:GetCallerIdentity
    - Environment Variables:
        * S3_BUCKET: Name of the S3 bucket storing tags.json
        * S3_OBJECT_KEY: Key for the tags.json file
"""

import json
import os
import re
from typing import Dict, List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from runbooks.utils.logger import configure_logger

## ✅ Configure Logger
logger = configure_logger(__name__)

## ✅ Initialize AWS Clients
s3 = boto3.client("s3")
ec2 = boto3.client("ec2")

# ==============================
# CONFIGURATIONS: dafault S3 bucket and object key
# ==============================
BUCKET_NAME = os.getenv("S3_BUCKET", "os-auto-tagging")  ## Default S3 bucket name
OBJECT_KEY = os.getenv("S3_OBJECT_KEY", "tags.json")  ## Default S3 object key
LOCAL_FILE_PATH = "/tmp/tags.json"  ## Local Temp file path

# ==============================
# VALIDATION CONFIGURATIONS
# ==============================
REQUIRED_TAGS = [
    "Account Name",
    "Functional Area",
    "WBS Code",
    "Business Unit",
    "Managed by",
    "CostGroup",
    "TechOwner",
]

TAG_VALUE_REGEX = r"^[a-zA-Z0-9\s\-_@]+$"  ## Allowed characters for tag values


def validate_tags(tags: List[Dict[str, str]]) -> None:
    """
    Validates that all required tags are present in the tag key-value list.

    Args:
        tags (List[Dict[str, str]]): List of tags to validate.

    Raises:
        ValueError: If any required tag is missing.
    """
    tag_keys = {tag["Key"] for tag in tags}  ## Extract tag keys
    missing_tags = [tag for tag in REQUIRED_TAGS if tag not in tag_keys]

    if missing_tags:
        raise ValueError(f"Missing required tags: {', '.join(missing_tags)}")

    ## Validate tag values
    for tag in tags:
        if not re.match(TAG_VALUE_REGEX, tag["Value"]):
            raise ValueError(f"Invalid value '{tag['Value']}' for tag '{tag['Key']}'.")

    logger.info("All required tags are validated and meet constraints.")


# ==============================
# S3 UTILITIES
# ==============================
def download_tags_from_s3(bucket: str, key: str, local_path: str) -> List[Dict[str, str]]:
    """
    Downloads the tagging configuration file from S3 and parses it.

    Args:
        bucket (str): The S3 bucket name.
        key (str): The object key in the bucket.
        local_path (str): The local path to store the file.

    Returns:
        List[Dict[str, str]]: List of tags.
    """
    try:
        ## ✅ Download tags.json File from S3
        logger.info(f"Downloading '{key}' from bucket '{bucket}'...")
        s3.download_file(bucket, key, local_path)
        logger.info(f"File downloaded successfully to {local_path}.")

        ## ✅ Parse the tags.json file
        with open(local_path, "r") as file:
            ## Load tags as a list of dictionaries
            tags = json.load(file)

        validate_tags(tags)  ## Validate required tags
        return tags

    except FileNotFoundError:
        logger.error("Local file not found after download.")
        raise

    except ClientError as e:
        logger.error(f"S3 Client Error: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error while downloading tags: {e}")
        raise


# ==============================
# EC2 UTILITIES
# ==============================
def apply_tags_to_instance(instance_id: str, tags: List[Dict[str, str]]) -> None:
    """
    Applies tags to the specified EC2 instance.

    Args:
        instance_id (str): The ID of the EC2 instance.
        tags (List[Dict[str, str]]): Tags to apply.

    Raises:
        Exception: Any AWS tagging errors.
    """
    try:
        logger.info(f"Applying tags to EC2 instance: {instance_id}")
        ec2.create_tags(Resources=[instance_id], Tags=tags)
        logger.info(f"Tags successfully applied to instance {instance_id}: {tags}")

    except ClientError as e:
        logger.error(f"EC2 Client Error: {e}")
        raise


# ==============================
# MAIN HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda Handler for applying tags to EC2 instances.

    Args:
        event (dict): AWS event data.
        context: AWS Lambda context.
    """
    try:
        ## ✅ Extract instance ID from the event
        instance_id = event["detail"]["responseElements"]["instancesSet"]["items"][0]["instanceId"]
        logger.info(f"Processing instance ID: {instance_id}")

        ## ✅ Download and Parse Tags
        tags = download_tags_from_s3(BUCKET_NAME, OBJECT_KEY, LOCAL_FILE_PATH)

        ## ✅ Apply Tags to Instance
        apply_tags_to_instance(instance_id, tags)

        ## ✅ Success Response
        return {
            "statusCode": 200,
            "body": json.dumps(f"Tags successfully applied to instance {instance_id}"),
        }
    except Exception as e:
        logger.error(f"Error during tagging process: {e}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
