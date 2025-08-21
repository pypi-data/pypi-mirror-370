#!/usr/bin/env python3

"""
Script to delete EBS snapshots older than the specified retention period.

Author: nnthanh101@gmail.com
Date: 2025-01-09
Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from runbooks.utils.logger import configure_logger

## ✅ Configure Logger
logger = configure_logger(__name__)

# ==============================
# CONFIGURATIONS
# ==============================
## ✅ Default Environment Variables
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", 30))  ## Default retention: 30 days
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"  ## Dry run mode
OWNER_ID = os.getenv("OWNER_ID", "self")  ## Default Owner ID (current AWS account)


# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
ec2 = boto3.resource("ec2")


# ==============================
# UTILITY FUNCTIONS
# ==============================
def get_old_snapshots(retention_days: int, owner_id: str) -> List[Dict[str, str]]:
    """
    Retrieves EBS snapshots older than the retention period.

    Args:
        retention_days (int): Number of days to retain snapshots.
        owner_id (str): AWS account ID for snapshot filtering.

    Returns:
        List[Dict[str, str]]: List of snapshots metadata.
    """
    try:
        logger.info(f"Retrieving snapshots owned by '{owner_id}' older than {retention_days} days ...")
        cutoff_time = datetime.now(tz=timezone.utc) - timedelta(days=retention_days)

        ## ✅ Fetch snapshots
        snapshots = ec2.snapshots.filter(OwnerIds=[owner_id])

        ## ✅ Filter old snapshots
        old_snapshots = [
            {
                "SnapshotId": snap.snapshot_id,
                "StartTime": str(snap.start_time),
                "State": snap.state,
                "VolumeId": snap.volume_id,
                "Description": snap.description,
            }
            for snap in snapshots
            if snap.start_time < cutoff_time
        ]

        logger.info(f"Found {len(old_snapshots)} snapshots older than {retention_days} days.")
        return old_snapshots

    except (BotoCoreError, ClientError) as e:
        logger.error(f"AWS Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def delete_snapshots(snapshots: List[Dict[str, str]], dry_run: bool) -> None:
    """
    Deletes specified snapshots based on dry-run mode.

    Args:
        snapshots (List[Dict[str, str]]): List of snapshots to delete.
        dry_run (bool): If true, no actual deletion will be performed.
    """
    for snap in snapshots:
        try:
            snapshot = ec2.Snapshot(snap["SnapshotId"])
            if dry_run:
                logger.info(f"[DRY-RUN] Snapshot {snap['SnapshotId']} would be deleted.")
            else:
                snapshot.delete()
                logger.info(f"Deleted snapshot: {snap['SnapshotId']} - Created on {snap['StartTime']}")

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to delete snapshot {snap['SnapshotId']}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for snapshot {snap['SnapshotId']}: {e}")


def output_snapshots(snapshots: List[Dict[str, str]], format_type: str = "table") -> None:
    """
    Displays snapshots in either markdown table or JSON format.

    Args:
        snapshots (List[Dict[str, str]]): Snapshots to display.
        format_type (str): Output format ('table' or 'json').
    """
    if format_type == "json":
        print(json.dumps(snapshots, indent=4))
    else:
        print(
            "| Snapshot ID       | Volume ID        | Created At              | State      | Description              |"
        )
        print(
            "|-------------------|------------------|-------------------------|------------|--------------------------|"
        )
        for snap in snapshots:
            print(
                f"| {snap['SnapshotId']:18} | {snap['VolumeId']:16} | {snap['StartTime']:23} "
                f"| {snap['State']:10} | {snap['Description'][:25]:25} |"
            )


# ==============================
# MAIN FUNCTION
# ==============================
def main():
    """
    Main function for CLI usage.
    """
    try:
        ## ✅ Fetch Old Snapshots
        old_snapshots = get_old_snapshots(RETENTION_DAYS, OWNER_ID)

        ## ✅ Display Snapshots
        output_format = sys.argv[1] if len(sys.argv) > 1 else "table"
        output_snapshots(old_snapshots, format_type=output_format)

        ## ✅ Delete Snapshots
        delete_snapshots(old_snapshots, dry_run=DRY_RUN)

    except Exception as e:
        logger.error(f"Failed to execute script: {e}")
        sys.exit(1)


# ==============================
# LAMBDA HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda handler for deleting EBS snapshots.

    Args:
        event (dict): Input event data.
        context: Lambda execution context.
    """
    try:
        retention_days = int(event.get("retention_days", RETENTION_DAYS))
        dry_run = event.get("dry_run", DRY_RUN)
        output_format = event.get("output_format", "json")

        ## ✅ Fetch and Display Snapshots
        old_snapshots = get_old_snapshots(retention_days, OWNER_ID)
        output_snapshots(old_snapshots, format_type=output_format)

        ## ✅ Delete Snapshots
        delete_snapshots(old_snapshots, dry_run=dry_run)

        return {"statusCode": 200, "body": json.dumps({"deleted": len(old_snapshots)})}

    except Exception as e:
        logger.error(f"Lambda Error: {e}")
        return {"statusCode": 500, "body": str(e)}


if __name__ == "__main__":
    main()
