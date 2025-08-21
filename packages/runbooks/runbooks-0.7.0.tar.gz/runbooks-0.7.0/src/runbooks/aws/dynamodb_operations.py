#!/usr/bin/env python3

"""
DynamoDB Operations: Put Item, Delete Item, and Batch Write.

This script supports the following functionalities:
1. Insert or update a single item (Put Item).
2. Retrieve and delete a single item (Delete Item).
3. Batch insert multiple items efficiently (Batch Write).

Designed for usage in Python, Docker, and AWS Lambda environments.

Author: nnthanh101@gmail.com
Date: 2025-01-09
Version: 1.0.0
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
# CONFIGURATION VARIABLES
# ==============================
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("TABLE_NAME", "employees")
MAX_BATCH_ITEMS = int(os.getenv("MAX_BATCH_ITEMS", 100))


# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
try:
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(TABLE_NAME)
    logger.info(f"✅ DynamoDB Table '{TABLE_NAME}' initialized successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize DynamoDB table: {e}")
    raise


# ==============================
# FUNCTION: PUT ITEM
# ==============================
def put_item(emp_id: str, name: str, salary: int) -> None:
    """
    Inserts or updates a single item in DynamoDB.

    Args:
        emp_id (str): Employee ID.
        name (str): Employee name.
        salary (int): Employee salary.

    Raises:
        Exception: If item insertion fails.
    """
    try:
        logger.info(f"🚀 Inserting/Updating item in table '{TABLE_NAME}'...")
        table.put_item(Item={"emp_id": emp_id, "name": name, "salary": salary})
        logger.info(f"✅ Item added successfully: emp_id={emp_id}, name={name}, salary={salary}")

    except ClientError as e:
        logger.error(f"❌ AWS Client Error: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")
        raise


# ==============================
# FUNCTION: DELETE ITEM
# ==============================
def delete_item(emp_id: str) -> Dict:
    """
    Retrieves and deletes a single item from DynamoDB.

    Args:
        emp_id (str): Employee ID.

    Returns:
        Dict: Deleted item details.

    Raises:
        Exception: If retrieval or deletion fails.
    """
    try:
        ## ✅ 1. Retrieve the item
        logger.info(f"🔍 Retrieving item with emp_id={emp_id}...")
        response = table.get_item(Key={"emp_id": emp_id})

        if "Item" not in response:
            raise ValueError(f"Item with emp_id={emp_id} not found.")
        item = response["Item"]
        logger.info(f"✅ Item retrieved: {item}")

        ## ✅ 2. Delete the item
        logger.info(f"🗑️ Deleting item with emp_id={emp_id}...")
        table.delete_item(Key={"emp_id": emp_id})
        logger.info(f"✅ Item deleted successfully: emp_id={emp_id}")

        return item

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
# FUNCTION: BATCH WRITE ITEMS
# ==============================
def batch_write_items(batch_size: int = MAX_BATCH_ITEMS) -> None:
    """
    Inserts multiple items into DynamoDB using batch writer.

    Args:
        batch_size (int): Number of items to write in a batch.

    Raises:
        Exception: If batch write fails.
    """
    try:
        logger.info(f"🚀 Starting batch write with {batch_size} items...")
        with table.batch_writer() as batch:
            for i in range(batch_size):
                batch.put_item(
                    Item={
                        "emp_id": str(i),
                        "name": f"Name-{i}",
                        "salary": 50000 + i * 100,  ## Incremental salary
                    }
                )
        logger.info(f"✅ Batch write completed successfully with {batch_size} items.")

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
    Main function for CLI/Docker execution.
    """
    try:
        ## Use-Case 1: Put Item
        put_item(emp_id="2", name="John Doe", salary=75000)

        ## Use-Case 2: Delete Item
        delete_item(emp_id="2")

        ## Use-Case 3: Batch Write Items
        batch_write_items(batch_size=MAX_BATCH_ITEMS)

    except Exception as e:
        logger.error(f"❌ Error in main execution: {e}")
        raise


# ==============================
# AWS LAMBDA HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda handler for DynamoDB operations.

    Args:
        event (dict): AWS Lambda event with action details.
        context: AWS Lambda context object.

    Returns:
        dict: Status code and message.
    """
    try:
        action = event.get("action")
        emp_id = event.get("emp_id")
        name = event.get("name")
        salary = event.get("salary", 0)
        batch_size = int(event.get("batch_size", MAX_BATCH_ITEMS))

        if action == "put":
            put_item(emp_id, name, salary)
            return {"statusCode": 200, "body": f"Item {emp_id} inserted."}

        elif action == "delete":
            item = delete_item(emp_id)
            return {"statusCode": 200, "body": f"Item {item} deleted."}

        elif action == "batch_write":
            batch_write_items(batch_size)
            return {"statusCode": 200, "body": "Batch write completed."}

        else:
            raise ValueError("Invalid action. Use 'put', 'delete', or 'batch_write'.")

    except Exception as e:
        logger.error(f"❌ Lambda Error: {e}")
        return {"statusCode": 500, "body": str(e)}


# ==============================
# SCRIPT ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
