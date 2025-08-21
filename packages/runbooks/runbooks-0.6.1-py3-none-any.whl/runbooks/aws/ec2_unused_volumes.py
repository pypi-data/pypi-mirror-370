#!/usr/bin/env python3
"""
AWS EC2 Unused Volume Checker with SNS Notification.

Finds unattached EBS volumes and sends the details via SNS notification.

Author: nnthanh101@gmail.com
Date: 2025-01-08
Version: 1.0.0
"""

import json
import logging
import os
import sys
from typing import Dict, List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from runbooks.utils.logger import configure_logger  # Reusable logger utility

## ✅ Configure Logger
logger = configure_logger(__name__)

# ==============================
# CONFIGURATION VARIABLES
# ==============================
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:ap-southeast-2:999999999999:1cloudops")

# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
ec2_client = boto3.client("ec2", region_name=AWS_REGION)
sns_client = boto3.client("sns", region_name=AWS_REGION)


# ==============================
# VALIDATION UTILITIES
# ==============================
def validate_sns_arn(arn: str) -> None:
    """
    Validates the format of the SNS Topic ARN.

    Args:
        arn (str): SNS Topic ARN.

    Raises:
        ValueError: If the ARN format is invalid.
    """
    if not arn.startswith("arn:aws:sns:"):
        raise ValueError(f"Invalid SNS Topic ARN: {arn}")
    logger.info(f"✅ Valid SNS ARN: {arn}")


# ==============================
# CORE FUNCTION: FIND UNUSED VOLUMES
# ==============================
def find_unused_volumes() -> List[Dict[str, str]]:
    """
    Identifies unused (unattached) EBS volumes in the AWS account.

    Returns:
        List[Dict[str, str]]: List of unused volumes with details.
    """
    try:
        ## ✅ Retrieve all volumes
        logger.info("🔍 Fetching all EBS volumes...")
        response = ec2_client.describe_volumes()

        ## ✅ Initialize Unused Volumes List
        unused_volumes = []

        ## ✅ Enhanced Loop with Debug Logs
        for vol in response["Volumes"]:
            if len(vol.get("Attachments", [])) == 0:  ## Unattached volumes
                ## Log detailed info for debugging
                logger.debug(f"Unattached Volume: {json.dumps(vol, default=str)}")

                ## Append Volume Details
                unused_volumes.append(
                    {
                        "VolumeId": vol["VolumeId"],
                        "Size": vol["Size"],
                        "State": vol["State"],
                        "Encrypted": vol.get("Encrypted", False),
                        "VolumeType": vol.get("VolumeType", "unknown"),
                        "CreateTime": str(vol["CreateTime"]),
                    }
                )

        logger.info(f"✅ Found {len(unused_volumes)} unused volumes.")
        return unused_volumes

    except ClientError as e:
        logger.error(f"❌ AWS Client Error: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise


# ==============================
# NOTIFICATION FUNCTION: SEND EMAIL
# ==============================
def send_sns_notification(unused_volumes: List[Dict[str, str]]) -> None:
    """
    Sends unused EBS volume details via SNS notification.

    Args:
        unused_volumes (List[Dict[str, str]]): List of unused volumes.

    Raises:
        Exception: If SNS publish fails.
    """
    try:
        ## ✅ Prepare Email Body (Markdown for Readability)
        email_body = "### Unused EBS Volumes Report 📊\n\n"
        email_body += "| VolumeId | Size (GiB) | State | Encrypted | VolumeType | CreateTime |\n"
        email_body += "|----------|------------|-------|-----------|------------|------------|\n"
        for vol in unused_volumes:
            email_body += f"| {vol['VolumeId']} | {vol['Size']} | {vol['State']} | {vol['Encrypted']} | {vol['VolumeType']} | {vol['CreateTime']} |\n"

        ## ✅ Publish to SNS
        logger.info(f"Sending notification to SNS topic: {SNS_TOPIC_ARN}...")
        logger.info(f"📤 Sending SNS notification to SNS topic: {SNS_TOPIC_ARN}")
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Unused EBS Volumes Report",
            Message=email_body,
        )
        logger.info("✅ SNS notification sent successfully.")

    except ClientError as e:
        logger.error(f"❌ SNS Client Error: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected error while sending SNS notification: {e}")
        raise


# ==============================
# MAIN FUNCTION
# ==============================
def main() -> None:
    """
    Main function to find unused volumes and send notifications.
    """
    try:
        ## ✅ Validate Inputs/Configuration
        validate_sns_arn(SNS_TOPIC_ARN)

        ## ✅ Find Unused Volumes
        unused_volumes = find_unused_volumes()

        if unused_volumes:
            ## ✅ Send SNS Notification if unused volumes exist
            send_sns_notification(unused_volumes)
        else:
            logger.info("⚠️ No unused volumes found. Exiting without notification.")

    except Exception as e:
        logger.error(f"❌ Fatal Error: {e}")
        sys.exit(1)


# ==============================
# LAMBDA HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda Handler for unused EBS volume detection and notification.

    Args:
        event (dict): AWS Lambda event.
        context: AWS Lambda context.
    """
    main()  # Reuse the main function for Lambda


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
