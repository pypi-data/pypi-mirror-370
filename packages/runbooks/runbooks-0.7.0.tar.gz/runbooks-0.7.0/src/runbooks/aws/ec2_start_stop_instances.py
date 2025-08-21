#!/usr/bin/env python3

"""
EC2 Instance Scheduler for Start/Stop Based on Tags.

Author: nnthanh101@gmail.com
Date: 2025-01-07
Version: 1.0.0

Description:
    - Start or Stop EC2 instances tagged with "AutoStart" = "True".
    - Works in both AWS Lambda and Python environments.

Requirements:
    - IAM Permissions:
        * ec2:DescribeInstances
        * ec2:StartInstances
        * ec2:StopInstances

Environment Variables (Optional):
    - LOG_LEVEL: Logging verbosity (default: INFO)

Usage (Python CLI):
    python ec2_instance_scheduler.py --action=start

Usage (Lambda):
    Trigger event with: {"action": "start"} or {"action": "stop"}
"""

import argparse  # # For CLI mode support
import json
import os
import sys
from typing import Dict, List

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)

from runbooks.utils.logger import configure_logger

## ✅ Configure Logger
logger = configure_logger(__name__)


# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
def get_ec2_client():
    """
    Initializes the EC2 client.

    Returns:
        boto3.client: EC2 client.
    """
    try:
        return boto3.client("ec2")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"AWS credentials not found or incomplete: {e}")
        sys.exit(1)


# ==============================
# INSTANCE OPERATIONS
# ==============================
def fetch_instances(client, tag_key: str, tag_value: str) -> List[str]:
    """
    Fetches instance IDs based on tags.

    Args:
        client (boto3.client): EC2 client.
        tag_key (str): Tag key to filter instances.
        tag_value (str): Tag value to filter instances.

    Returns:
        List[str]: List of instance IDs.
    """
    try:
        logger.info("Fetching instances with tag: %s=%s", tag_key, tag_value)

        ## Filter instances based on the tag
        response = client.describe_instances(
            # Filters=[{'Name': f"tag:AutoStart", 'Values': ['True']}]
            Filters=[{"Name": f"tag:{tag_key}", "Values": [tag_value]}]
        )

        ## Extract list of Instance IDs
        instance_ids = [
            instance["InstanceId"] for reservation in response["Reservations"] for instance in reservation["Instances"]
        ]

        if not instance_ids:
            logger.warning("No matching instances found.")
        else:
            logger.info("Found instances: %s", instance_ids)

        return instance_ids

    except ClientError as e:
        logger.error(f"AWS Client Error: {e}")
        raise
    except BotoCoreError as e:
        logger.error(f"BotoCore Error: {e}")
        raise


def perform_action(client, instance_ids: List[str], action: str) -> None:
    """
    Performs the specified action (start/stop) on the instances.

    Args:
        client (boto3.client): EC2 client.
        instance_ids (List[str]): List of instance IDs.
        action (str): The action to perform ("start" or "stop").
    """
    if not instance_ids:
        logger.warning("No instances to process for action: %s", action)
        return

    try:
        if action == "start":
            logger.info("Starting instances: %s", instance_ids)
            response = client.start_instances(InstanceIds=instance_ids)
        elif action == "stop":
            logger.info("Stopping instances: %s", instance_ids)
            response = client.stop_instances(InstanceIds=instance_ids)
        else:
            raise ValueError(f"Invalid action: {action}")

        logger.info("Action '%s' completed successfully.", action)
        logger.debug("Response: %s", response)

    except ClientError as e:
        logger.error(f"AWS Client Error during '{action}': {e}")
        raise
    except BotoCoreError as e:
        logger.error(f"BotoCore Error during '{action}': {e}")
        raise


# ==============================
# MAIN HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda handler for EC2 start/stop scheduler.

    Args:
        event (dict): AWS event data.
        context: AWS Lambda context.
    """
    try:
        ## ✅ Parse Action from Event
        action = event.get("action")
        if action not in ["start", "stop"]:
            raise ValueError("Invalid action. Supported actions: 'start' or 'stop'.")

        ## ✅ Initialize AWS Client
        ec2_client = get_ec2_client()

        # ✅ Fetch Instances and Perform Action
        instance_ids = fetch_instances(ec2_client, tag_key="AutoStart", tag_value="True")
        perform_action(ec2_client, instance_ids, action)

        return {
            "statusCode": 200,
            "body": json.dumps(f"Action '{action}' completed successfully."),
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}


def main():
    """
    CLI Entry Point for Python Usage.
    """
    parser = argparse.ArgumentParser(description="EC2 Scheduler Script")
    parser.add_argument(
        "--action",
        choices=["start", "stop"],
        required=True,
        help="Action to perform (start/stop).",
    )
    args = parser.parse_args()

    try:
        ## ✅ CLI Execution
        action = args.action
        ec2_client = get_ec2_client()
        instance_ids = fetch_instances(ec2_client, tag_key="AutoStart", tag_value="True")
        perform_action(ec2_client, instance_ids, action)
        logger.info(f"Action '{action}' completed successfully.")
    except Exception as e:
        logger.error(f"Failed to execute action: {e}")
        sys.exit(1)


# ==============================
# SCRIPT ENTRY POINT
# ==============================
if __name__ == "__main__":
    # Detect environment
    if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
        lambda_handler({}, None)  # Placeholder event/context for Lambda testing
    else:
        main()
