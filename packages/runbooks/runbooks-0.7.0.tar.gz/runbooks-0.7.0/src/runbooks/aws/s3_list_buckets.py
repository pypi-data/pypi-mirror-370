#!/usr/bin/env python3

"""
AWS S3 Bucket Listing Utility with logging and error handling.

Author: nnthanh101@gmail.com
Date: 2025-01-05
Version: 1.0.0

Description:
    This script lists all S3 buckets in the AWS account using the Boto3 library.
    It implements robust error handling, logging, and modularization for high standards.

Usage:
    python list_s3_buckets.py
"""

import json
import os
from typing import Dict, List

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from tabulate import tabulate

from runbooks.utils.logger import configure_logger

## Initialize Logger
logger = configure_logger("list_s3_buckets")


def get_s3_client(region: str = None) -> boto3.client:
    """
    Initializes and returns a Boto3 S3 client with optional region support.

    Args:
        region (str, optional): AWS region. Defaults to None (uses environment or AWS config).

    Returns:
        boto3.client: Configured S3 client.

    Raises:
        NoCredentialsError: Raised if AWS credentials are missing.
        PartialCredentialsError: Raised if AWS credentials are incomplete.
    """
    try:
        ## ✅ Allow region override if specified
        session = boto3.Session(region_name=region) if region else boto3.Session()
        client = session.client("s3")
        logger.info("S3 client initialized successfully.")
        return client
    except (NoCredentialsError, PartialCredentialsError) as e:
        # logger.error("Please configure them using AWS CLI or environment variables.")
        logger.error(f"AWS Credentials Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


def list_s3_buckets(client: boto3.client) -> List[Dict[str, str]]:
    """
    Lists all S3 buckets in the AWS account.

    Args:
        client (boto3.client): Pre-configured S3 client.

    Returns:
        List[Dict[str, str]]: List of bucket details including name and creation date.

    Raises:
        ClientError: For API errors returned by AWS.
    """
    try:
        ## ✅ Call AWS API to list buckets
        response = client.list_buckets()

        ## ✅ Extract bucket names and creation dates
        # bucket_list = [{"Name": bucket['Name'], "CreationDate": str(bucket['CreationDate'])} for bucket in buckets]
        bucket_list = [
            {
                "Name": bucket["Name"],
                "CreationDate": bucket["CreationDate"].strftime("%Y-%m-%d %H:%M:%S"),
                "Owner": {
                    "DisplayName": response["Owner"].get("DisplayName", "N/A"),
                    # "ID": response['Owner'].get('ID', 'N/A')
                },
            }
            for bucket in response.get("Buckets", [])
        ]

        ## ✅ Log the number of buckets found
        if not bucket_list:
            logger.warning("No buckets found.")
        else:
            logger.info(f"Found {len(bucket_list)} S3 bucket(s).")

        return bucket_list
    except ClientError as e:
        logger.error(f"Failed to list buckets: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


def display_buckets(buckets: List[Dict[str, str]]) -> None:
    """
    Displays bucket details in JSON format for readability.

    Args:
        buckets (List[Dict[str, str]]): List of bucket details.
    """

    # print(json.dumps(buckets, indent=4)) if buckets else print("No buckets found.")
    ## ✅ Prepare Table Headers and Rows
    headers = ["Name", "Creation Date", "Owner Display Name", "Owner ID"]
    rows = [
        # [bucket["Name"], bucket["CreationDate"], bucket["Owner"]["DisplayName"], bucket["Owner"]["ID"]]
        [bucket["Name"], bucket["CreationDate"], bucket["Owner"]["DisplayName"]]
        for bucket in buckets
    ]

    ## ✅ Render Markdown Table
    print("### AWS S3 Buckets\n")
    ## Creating & printing the Markdown Table
    table = tabulate(rows, headers=headers, tablefmt="github", missingval="N/A")
    print(table)


## ==============================
## MAIN FUNCTION
## ==============================
def main() -> None:
    """
    Main entry point for listing S3 buckets.
    """
    try:
        ## ✅ Load AWS region dynamically (fallback to default)
        region = os.getenv("AWS_REGION", "us-east-1")
        ## ✅ Initialize S3 client
        client = get_s3_client(region)
        ## ✅ Retrieve bucket list
        buckets = list_s3_buckets(client)
        ## ✅ Display results
        display_buckets(buckets)
    except Exception as e:
        logger.error(f"Program terminated with error: {str(e)}")


if __name__ == "__main__":
    main()
