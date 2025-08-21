#!/usr/bin/env python3

"""
Terminate EC2 Instances Script.

This script provides a robust and production-grade solution to terminate EC2 instances.
It supports execution as a standalone Python script, within Docker containers, or as an AWS Lambda function.

Author: CloudOps DevOps Engineer
Date: 2025-01-08
Version: 1.0.0
"""

import logging
import os
from typing import List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# ==============================
# CONFIGURATION
# ==============================
REGION = os.getenv("AWS_REGION", "us-east-1")
INSTANCE_IDS = os.getenv("INSTANCE_IDS", "").split(",")  ## Example: 'i-0158ab7a03bb6a954,i-04a8f37b92b7c1a78'
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# ==============================
# LOGGING CONFIGURATION
# ==============================
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
ec2_client = boto3.client("ec2", region_name=REGION)


# ==============================
# FUNCTION: Terminate EC2 Instances
# ==============================
def terminate_instances(instance_ids: List[str]) -> List[str]:
    """
    Terminates specified EC2 instances.

    Args:
        instance_ids (List[str]): List of EC2 instance IDs to terminate.

    Returns:
        List[str]: List of successfully terminated instance IDs.
    """
    try:
        if not instance_ids or instance_ids == [""]:
            logger.error("No instance IDs provided for termination.")
            raise ValueError("Instance IDs cannot be empty.")

        logger.info(f"Terminating instances: {', '.join(instance_ids)} in region {REGION}...")
        if DRY_RUN:
            logger.info("[DRY-RUN] No actual termination performed.")
            return []

        # Perform termination
        response = ec2_client.terminate_instances(InstanceIds=instance_ids)

        terminated_instances = [instance["InstanceId"] for instance in response["TerminatingInstances"]]
        for instance in response["TerminatingInstances"]:
            logger.info(f"Instance {instance['InstanceId']} state changed to {instance['CurrentState']['Name']}.")
        return terminated_instances

    except ClientError as e:
        logger.error(f"AWS Client Error: {e}")
        raise

    except BotoCoreError as e:
        logger.error(f"BotoCore Error: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


# ==============================
# MAIN FUNCTION (for CLI/Docker)
# ==============================
def main():
    """
    Main entry point for standalone execution (CLI or Docker).
    """
    try:
        # Ensure instance IDs are provided
        if not INSTANCE_IDS or INSTANCE_IDS == [""]:
            logger.error("No instance IDs provided. Set INSTANCE_IDS environment variable.")
            raise ValueError("Instance IDs are required to terminate EC2 instances.")

        # Terminate instances
        terminated_instances = terminate_instances(INSTANCE_IDS)
        if terminated_instances:
            logger.info(f"Successfully terminated instances: {', '.join(terminated_instances)}")
        else:
            logger.info("No instances terminated (Dry-Run mode or empty list).")

    except Exception as e:
        logger.error(f"Error during instance termination: {e}")
        raise


# ==============================
# AWS LAMBDA HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda handler for terminating EC2 instances.

    Args:
        event (dict): AWS Lambda event payload. Expected to include instance IDs.
        context: AWS Lambda context object.
    """
    try:
        instance_ids = event.get("instance_ids", INSTANCE_IDS)
        if not instance_ids or instance_ids == [""]:
            logger.error("No instance IDs provided in the Lambda event or environment.")
            raise ValueError("Instance IDs are required to terminate EC2 instances.")

        terminated_instances = terminate_instances(instance_ids)
        return {
            "statusCode": 200,
            "body": {
                "message": "Instances terminated successfully.",
                "terminated_instances": terminated_instances,
            },
        }
    except Exception as e:
        logger.error(f"Lambda function failed: {e}")
        return {"statusCode": 500, "body": {"message": str(e)}}


# ==============================
# SCRIPT ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
