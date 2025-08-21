#!/usr/bin/env python3
"""
AWS EC2 Describe Instances Tool.

Lists EC2 instances based on optional filters. Supports Python CLI, Docker, and AWS Lambda.

Author: nnthanh101@gmail.com
Date: 2025-01-08
Version: 1.0.0
"""

import json
import os
import sys
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from runbooks.utils.logger import configure_logger

## ✅ Configure Logger
logger = configure_logger(__name__)

# ==============================
# CONFIGURATIONS
# ==============================
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")  # Default Region
DEFAULT_TAG_KEY = os.getenv("DEFAULT_TAG_KEY", "Env")  # Default Tag Key
DEFAULT_TAG_VALUE = os.getenv("DEFAULT_TAG_VALUE", "Prod")  # Default Tag Value

# AWS Client
ec2_client = boto3.client("ec2", region_name=AWS_REGION)


# ==============================
# EC2 UTILITIES
# ==============================
def describe_instances(filters: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
    """
    Describes EC2 instances based on the provided filters.

    Args:
        filters (List[Dict[str, str]], optional): List of filters for querying EC2 instances.

    Returns:
        List[Dict[str, str]]: List of EC2 instance details.
    """
    try:
        ## ✅ Apply Default Filter if None Provided
        filters = filters or [{"Name": f"tag:{DEFAULT_TAG_KEY}", "Values": [DEFAULT_TAG_VALUE]}]
        logger.info(f"🔍 Querying EC2 instances with filters: {filters}")

        instances = []
        paginator = ec2_client.get_paginator("describe_instances")

        ## ✅ Paginate Results
        for page in paginator.paginate(Filters=filters):
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append(
                        {
                            "InstanceId": instance["InstanceId"],
                            "State": instance["State"]["Name"],
                            "InstanceType": instance["InstanceType"],
                            "LaunchTime": str(instance["LaunchTime"]),
                            "Tags": instance.get("Tags", []),
                        }
                    )

        ## ✅ Log Results
        logger.info(f"✅ Found {len(instances)} instance(s).")
        return instances

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
# DISPLAY UTILITIES
# ==============================
def display_instances(instances: List[Dict[str, str]]) -> None:
    """
    Displays instance details in Markdown table format.

    Args:
        instances (List[Dict[str, str]]): List of EC2 instance details.
    """
    if not instances:
        print("No instances found.")
        return

    ## ✅ Markdown Table Header
    table_header = (
        "| Instance ID     | State      | Type       | Launch Time             | Tags                           |"
    )
    table_divider = (
        "|----------------|------------|------------|--------------------------|--------------------------------|"
    )
    print(table_header)
    print(table_divider)

    ## ✅ Print Each Instance Row
    for instance in instances:
        tags = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in instance.get("Tags", [])])
        print(
            f"| {instance['InstanceId']:15} | {instance['State']:10} | {instance['InstanceType']:10} | "
            f"{instance['LaunchTime']:24} | {tags:30} |"
        )


def display_instances_json(instances: List[Dict[str, str]]) -> None:
    """
    Displays instance details in JSON format for automation tools.

    Args:
        instances (List[Dict[str, str]]): List of EC2 instance details.
    """
    (print(json.dumps(instances, indent=4)) if instances else print("No instances found."))


# ==============================
# CLI HANDLER
# ==============================
def main():
    """
    Main function for CLI execution.
    """
    try:
        ## ✅ Parse Command-Line Arguments
        tag_key = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TAG_KEY
        tag_value = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TAG_VALUE

        ## ✅ Construct Filters
        filters = [{"Name": f"tag:{tag_key}", "Values": [tag_value]}]

        ## ✅ Fetch and Display Instances
        instances = describe_instances(filters)
        ## ✅ Display Instances: Default to markdown table format
        # display_instances_json(instances)
        display_instances(instances)

    except Exception as e:
        logger.error(f"❌ Fatal Error: {e}")
        sys.exit(1)


# ==============================
# AWS LAMBDA HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda Handler for describing EC2 instances.

    Args:
        event (dict): AWS event data.
        context: AWS Lambda context.
    """
    try:
        ## ✅ Extract Inputs from Event
        tag_key = event.get("tag_key", DEFAULT_TAG_KEY)
        tag_value = event.get("tag_value", DEFAULT_TAG_VALUE)
        output_format = event.get("output_format", "table")  ## Supports 'table' or 'json'

        ## ✅ Construct Filters
        filters = [{"Name": f"tag:{tag_key}", "Values": [tag_value]}]

        ## ✅ Fetch EC2 Instances
        instances = describe_instances(filters)

        ## ✅ Return Lambda Response: Generate Output
        if output_format == "json":
            return {"statusCode": 200, "body": json.dumps(instances, indent=4)}
        else:
            table_output = []
            for instance in instances:
                tags = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in instance.get("Tags", [])])
                table_output.append(
                    f"| {instance['InstanceId']:15} | {instance['State']:10} | {instance['InstanceType']:10} | "
                    f"{instance['LaunchTime']:24} | {tags:30} |"
                )
            return {"statusCode": 200, "body": "\n".join(table_output)}

    except Exception as e:
        logger.error(f"❌ Lambda Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# ==============================
# SCRIPT ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
