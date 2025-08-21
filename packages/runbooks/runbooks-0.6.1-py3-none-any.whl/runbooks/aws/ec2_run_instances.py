#!/usr/bin/env python3

"""
AWS EC2 Instance Launcher.

Author: nnthanh101@gmail.com
Date: 2025-01-07
Version: 1.0.0

Description:
    - Launches EC2 instances in a VPC with specified configurations using AWS Boto3.
    - Works with both Python runtime and AWS Lambda.
    - Supports environment-based configuration for scalability.

IAM Role Permissions:
    - ec2:RunInstances
    - ec2:CreateTags
    - ec2:DescribeSecurityGroups
    - ec2:DescribeInstances
"""

import json
import os
from typing import Dict, List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from runbooks.utils.logger import configure_logger

## ✅ Configure Logger
logger = configure_logger(__name__)

# ==============================
# CONFIGURATION
# ==============================
DEFAULT_AMI_ID = os.getenv(
    "AMI_ID", "ami-03f052ebc3f436d52"
)  ## Default Red Hat Enterprise Linux 9 (HVM), SSD Volume Type
DEFAULT_INSTANCE_TYPE = os.getenv("INSTANCE_TYPE", "t2.micro")  ## Default instance type
DEFAULT_MIN_COUNT = int(os.getenv("MIN_COUNT", "1"))  ## Min EC2 instances
DEFAULT_MAX_COUNT = int(os.getenv("MAX_COUNT", "1"))  ## Max EC2 instances
KEY_NAME = os.getenv("KEY_NAME", "EC2Test")  ## SSH Key Pair Name: my-key = EC2Test
## VPC Security Group IDs
# SECURITY_GROUPS = os.getenv('SECURITY_GROUPS', 'default,vpc_endpoint_security_group').split(',')
SECURITY_GROUP_IDS = os.getenv("SECURITY_GROUP_IDS", "sg-0b0ee7b0b75210174,sg-0b056d8059a91607d").split(",")
SUBNET_ID = os.getenv("SUBNET_ID", "subnet-094569c6e3ccaa04d")  ## Required Subnet-ID for VPC-based deployment
TAGS = os.getenv("TAGS", '{"Project":"CloudOps", "Environment":"Dev"}')  ## Default tags

## ✅ Block Device Mappings Configuration
OS_BlockDeviceMappings = [
    {
        "DeviceName": "/dev/xvda",  ## Root volume device
        "Ebs": {
            "DeleteOnTermination": True,  ## Clean up after instance termination
            "VolumeSize": 20,  ## Set volume size in GB
            "VolumeType": "gp3",  ## Modern, faster storage
            "Encrypted": True,  ## Encrypt the EBS volume
        },
    },
]
OS_Monitoring = {"Enabled": False}


# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
def get_ec2_client():
    """
    Initializes AWS EC2 client.
    """
    return boto3.client("ec2")


# ==============================
# EC2 INSTANCE LAUNCH FUNCTION
# ==============================
def launch_ec2_instances(
    ec2_client,
    ami_id: str,
    instance_type: str,
    min_count: int,
    max_count: int,
    key_name: str,
    subnet_id: str,
    security_group_ids: List[str],
    tags: Dict[str, str] = None,
) -> List[str]:
    """
    Launches EC2 instances and applies tags.

    Args:
        ec2_client: EC2 boto3 client.
        ami_id (str): AMI ID for the instance.
        instance_type (str): EC2 instance type.
        min_count (int): Minimum number of instances.
        max_count (int): Maximum number of instances.
        key_name (str): SSH key pair name.
        subnet_id (str): Subnet ID for launching in a VPC.
        security_group_ids (List[str]): Security group IDs for VPC.
        tags (Dict[str, str]): Tags to apply to instances.

    Returns:
        List[str]: List of launched instance IDs.
    """
    try:
        logger.info("Validates required environment variables for launching EC2 instances.")
        if not SUBNET_ID:
            raise ValueError("❌ Missing required SUBNET_ID environment variable.")
        if not SECURITY_GROUP_IDS or SECURITY_GROUP_IDS == [""]:
            raise ValueError("❌ Missing required SECURITY_GROUP_IDS environment variable.")
        logger.info("✅ Environment variables validated successfully.")

        logger.info(f"Launching {min_count}-{max_count} instances of type {instance_type} with AMI {ami_id}...")

        ## ✅ Construct parameters
        params = {
            "BlockDeviceMappings": OS_BlockDeviceMappings,
            "ImageId": ami_id,
            "InstanceType": instance_type,
            "MinCount": min_count,
            "MaxCount": max_count,
            "Monitoring": OS_Monitoring,
            "KeyName": key_name,
            "SubnetId": subnet_id,  ## VPC subnet
            "SecurityGroupIds": security_group_ids,  ## VPC Security Group IDs
        }

        ## ✅ Launch Instances
        response = ec2_client.run_instances(**params)

        ## ✅ Extract Instance IDs
        instance_ids = [instance["InstanceId"] for instance in response["Instances"]]
        logger.info(f"Launched Instances: {instance_ids}")

        ## ✅ Apply Tags
        if tags:
            ec2_client.create_tags(
                Resources=instance_ids,
                Tags=[{"Key": k, "Value": v} for k, v in tags.items()],
            )
            logger.info(f"Applied tags: {tags}")

        return instance_ids

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
# MAIN HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda Handler for launching EC2 instances.

    Args:
        event (dict): AWS event data.
        context: AWS Lambda context.
    """
    try:
        ## ✅ Initialize EC2 Client
        ec2_client = get_ec2_client()

        ## Parse tags from environment variable
        tags = json.loads(TAGS)
        ## ✅ Launch EC2 Instances
        instance_ids = launch_ec2_instances(
            ec2_client=ec2_client,
            ami_id=DEFAULT_AMI_ID,
            instance_type=DEFAULT_INSTANCE_TYPE,
            min_count=DEFAULT_MIN_COUNT,
            max_count=DEFAULT_MAX_COUNT,
            key_name=KEY_NAME,
            subnet_id=SUBNET_ID,
            security_group_ids=SECURITY_GROUP_IDS,
            tags=tags,
        )

        ## ✅ Return Success Response
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Instances launched", "InstanceIDs": instance_ids}),
        }
    except Exception as e:
        logger.error(f"Lambda Handler Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


if __name__ == "__main__":
    # ✅ CLI Execution for Python Runtime
    ec2_client = get_ec2_client()
    tags = json.loads(TAGS)

    instance_ids = launch_ec2_instances(
        ec2_client=ec2_client,
        ami_id=DEFAULT_AMI_ID,
        instance_type=DEFAULT_INSTANCE_TYPE,
        min_count=DEFAULT_MIN_COUNT,
        max_count=DEFAULT_MAX_COUNT,
        key_name=KEY_NAME,
        subnet_id=SUBNET_ID,
        security_group_ids=SECURITY_GROUP_IDS,
        tags=tags,
    )
    print(f"Launched Instances: {instance_ids}")
