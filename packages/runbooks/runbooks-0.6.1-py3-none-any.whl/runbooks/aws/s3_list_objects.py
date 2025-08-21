#!/usr/bin/env python3

"""
List all objects inside a specified S3 bucket with logging and error handling.

Author: nnthanh101@gmail.com
Date: 2025-01-06
Version: 1.0.0

Usage:
    python list_s3_objects.py <bucket_name>
"""

import argparse
import sys
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from tabulate import tabulate

from runbooks.utils.logger import configure_logger

## ✅ Configure Logger
logger = configure_logger(__name__)


## ==============================
## AWS S3 UTILITIES
## ==============================
def s3_list_objects(
    bucket_name: str,
    prefix: Optional[str] = None,
    max_keys: int = 1000,
) -> List[Dict[str, str]]:
    """
    List objects in the specified S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        prefix (Optional[str]): Filter objects by prefix (default: None).
        max_keys (int): Maximum number of keys to retrieve per request (default: 1000).

    Returns:
        List[Dict[str, str]]: List of object details, including key, size, and last modified date.

    Raises:
        NoCredentialsError: If AWS credentials are missing.
        ClientError: If there is an issue accessing the bucket.
    """
    try:
        logger.info(f"Initializing S3 client for bucket: {bucket_name}")
        client = boto3.client("s3")

        ## ✅ Prepare Parameters
        params = {"Bucket": bucket_name, "MaxKeys": max_keys}
        if prefix:
            params["Prefix"] = prefix

        ## ✅ Fetch Objects with Pagination Support
        paginator = client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(**params)

        object_list = []
        for page in page_iterator:
            if "Contents" in page:  # Check if there are objects
                for obj in page["Contents"]:
                    object_list.append(
                        {
                            "Key": obj["Key"],
                            "Size (KB)": f"{obj['Size'] / 1024:.2f}",  # Convert bytes to KB
                            "LastModified": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

        ## ✅ Log Results
        logger.info(f"Found {len(object_list)} object(s) in bucket '{bucket_name}'.")
        return object_list

    except NoCredentialsError:
        logger.error("AWS credentials not found. Ensure ~/.aws/credentials is configured.")
        raise

    except ClientError as e:
        logger.error(f"AWS Client Error: {e}")
        raise

    except BotoCoreError as e:
        logger.error(f"BotoCore Error: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


## ==============================
## DISPLAY UTILITIES
## ==============================
def display_objects(objects: List[Dict[str, str]], bucket_name: str) -> None:
    """
    Displays S3 object details in Markdown table format.

    Args:
        objects (List[Dict[str, str]]): List of S3 object details.
        bucket_name (str): Name of the S3 bucket.
    """
    if not objects:
        print(f"No objects found in bucket: {bucket_name}")
        return

    ## ✅ Prepare Table Headers and Rows
    headers = ["Key", "Size (KB)", "Last Modified"]
    rows = [[obj["Key"], obj["Size (KB)"], obj["LastModified"]] for obj in objects]

    ## ✅ Render Markdown Table
    print(f"### S3 Objects in Bucket: `{bucket_name}`\n")
    print(tabulate(rows, headers=headers, tablefmt="github"))


## ==============================
## MAIN FUNCTION
## ==============================
def main():
    """
    Main entry point for listing S3 objects.
    """
    ## ✅ Parse Command-Line Arguments
    parser = argparse.ArgumentParser(description="List objects in an AWS S3 bucket.")
    parser.add_argument("--bucket", required=True, help="The name of the S3 bucket.")
    parser.add_argument("--prefix", default=None, help="Filter objects by prefix.")
    parser.add_argument(
        "--max-keys",
        type=int,
        default=1000,
        help="Max number of keys to fetch (default: 1000).",
    )

    args = parser.parse_args()

    try:
        ## ✅ Fetch and Display S3 Objects
        objects = s3_list_objects(
            bucket_name=args.bucket,
            prefix=args.prefix,
            max_keys=args.max_keys,
        )
        display_objects(objects, args.bucket)

    except Exception as e:
        logger.error(f"Program terminated with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
