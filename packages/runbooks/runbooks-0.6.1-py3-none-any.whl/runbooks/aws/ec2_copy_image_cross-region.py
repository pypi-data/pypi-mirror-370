#!/usr/bin/env python3
"""
EC2 Image Creation and Cross-Region Copy Script.

Author: nnthanh101@gmail.com
Date: 2025-01-08
Version: 2.0.0
"""

import json
import logging
import os
from typing import List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# ==============================
# CONFIGURATIONS
# ==============================
SOURCE_REGION = os.getenv("SOURCE_REGION", "ap-southeast-2")  ## Source AWS region
DEST_REGION = os.getenv("DEST_REGION", "us-east-1")  ## Destination AWS region
INSTANCE_IDS = os.getenv("INSTANCE_IDS", "i-0067eeaab6c8188fd").split(",")  ## Comma-separated instance IDs
IMAGE_NAME_PREFIX = os.getenv("IMAGE_NAME_PREFIX", "Demo-Boto")  ## Image name prefix
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"  ## Dry-run mode

# ==============================
# LOGGING CONFIGURATION
# ==============================
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
source_ec2 = boto3.resource("ec2", region_name=SOURCE_REGION)
source_client = boto3.client("ec2", region_name=SOURCE_REGION)
dest_client = boto3.client("ec2", region_name=DEST_REGION)


# ==============================
# VALIDATION UTILITIES
# ==============================
def validate_regions(source_region: str, dest_region: str) -> None:
    """
    Validates AWS regions.

    Args:
        source_region (str): Source AWS region.
        dest_region (str): Destination AWS region.

    Raises:
        ValueError: If regions are invalid.
    """
    session = boto3.session.Session()
    valid_regions = session.get_available_regions("ec2")

    if source_region not in valid_regions:
        raise ValueError(f"Invalid source region: {source_region}")
    if dest_region not in valid_regions:
        raise ValueError(f"Invalid destination region: {dest_region}")
    logger.info(f"Validated AWS regions: {source_region} -> {dest_region}")


# ==============================
# CREATE IMAGES
# ==============================
def create_images(instance_ids: List[str]) -> List[str]:
    """
    Creates AMI images for specified instances.

    Args:
        instance_ids (List[str]): List of EC2 instance IDs.

    Returns:
        List[str]: List of created image IDs.
    """
    image_ids = []
    for instance_id in instance_ids:
        try:
            instance = source_ec2.Instance(instance_id)
            image_name = f"{IMAGE_NAME_PREFIX}-{instance_id}"
            logger.info(f"Creating image for instance {instance_id} with name '{image_name}' ...")

            if DRY_RUN:
                logger.info(f"[DRY-RUN] Image creation for {instance_id} skipped.")
            else:
                image = instance.create_image(Name=image_name, Description=f"Image for {instance_id}")
                image_ids.append(image.id)
                logger.info(f"Created image: {image.id}")

        except ClientError as e:
            logger.error(f"Failed to create image for instance {instance_id}: {e}")
            continue

    return image_ids


# ==============================
# WAIT FOR IMAGES
# ==============================
def wait_for_images(image_ids: List[str]) -> None:
    """
    Waits until the AMIs images to be available.

    Args:
        image_ids (List[str]): List of image IDs to monitor.
    """
    try:
        logger.info("Waiting for images to be available...")
        ## Get waiter for image_available
        waiter = source_client.get_waiter("image_available")
        waiter.wait(Filters=[{"Name": "image-id", "Values": image_ids}])
        logger.info("All Images are now available.")
    except ClientError as e:
        logger.error(f"Error waiting for AMIs: {e}")
        raise


# ==============================
# COPY IMAGES TO DESTINATION
# ==============================
def copy_images(image_ids: List[str]) -> None:
    """
    Copies AMIs Images to the destination region.

    Args:
        image_ids (List[str]): List of source image IDs.
    """
    for image_id in image_ids:
        try:
            copy_name = f"{IMAGE_NAME_PREFIX}-Copy-{image_id}"
            logger.info(f"Copying image {image_id} to {DEST_REGION} with name '{copy_name}' ...")

            if DRY_RUN:
                logger.info(f"[DRY-RUN] Image copy for {image_id} skipped.")
            else:
                dest_client.copy_image(
                    Name=copy_name,
                    SourceImageId=image_id,
                    SourceRegion=SOURCE_REGION,
                    Description=f"Copy of {image_id} from {SOURCE_REGION}",
                )
                logger.info(f"Image {image_id} copied successfully.")
        except ClientError as e:
            logger.error(f"Failed to copy image {image_id}: {e}")
            continue


# ==============================
# MAIN FUNCTION
# ==============================
def main():
    """
    CLI Entry Point.
    """
    try:
        ## ✅ Validate regions
        validate_regions(SOURCE_REGION, DEST_REGION)

        ## ✅ Part 1. Create AMI Images
        image_ids = create_images(INSTANCE_IDS)
        if not image_ids:
            logger.warning("No images created. Exiting.")
            return

        ## ✅ Part 2. Wait for AMI Images to be available
        wait_for_images(image_ids)

        ## ✅ Part 3. Copy images to destination region
        copy_images(image_ids)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)


# ==============================
# LAMBDA HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda Entry Point.
    """
    try:
        main()
        return {"statusCode": 200, "body": "Process completed successfully."}

    except Exception as e:
        logger.error(f"Lambda Error: {e}")
        return {"statusCode": 500, "body": str(e)}


if __name__ == "__main__":
    main()
