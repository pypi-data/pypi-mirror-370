#!/usr/bin/env python3
"""
AWS S3 Bucket Object Deletion and Bucket Management Tool

A specialized utility for safely emptying and optionally deleting S3 buckets,
including all object versions and delete markers. Essential for bucket lifecycle
management and compliance with data retention policies.

**AWS API Mapping**:
- `boto3.resource('s3').Bucket.object_versions.delete()`
- `boto3.resource('s3').Bucket.delete()`

**SECURITY WARNING**: This script performs DESTRUCTIVE operations:
- Permanently deletes ALL objects and versions from specified bucket
- Can delete the bucket itself with --force-delete flag
- Cannot be undone - ensure proper backups before execution
- May affect compliance with data retention requirements

Features:
    - Complete object version deletion (including delete markers)
    - Interactive bucket deletion confirmation
    - Force deletion mode for automation scenarios
    - Comprehensive error handling and logging
    - Single-bucket targeted operation for safety

Security Controls:
    - Requires explicit bucket name parameter
    - Interactive confirmation for bucket deletion
    - Force flag available for automated scenarios
    - Detailed logging of all destructive operations

Compliance Considerations:
    - Verify data retention policy compliance before execution
    - Ensure proper backup procedures are in place
    - Document destruction for audit trails
    - Consider legal hold and litigation requirements

Example:
    Empty bucket but keep it:
    ```bash
    python delete_s3_buckets_objects.py --profile my-profile --bucket my-bucket
    ```

    Empty and delete bucket with confirmation:
    ```bash
    python delete_s3_buckets_objects.py --profile my-profile --bucket my-bucket +delete
    ```

Requirements:
    - IAM permissions: `s3:DeleteObject`, `s3:DeleteObjectVersion`, `s3:DeleteBucket`
    - Bucket must be in accessible region
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team

Version:
    2023.05.04
"""

import logging

from account_class import aws_acct_access
from ArgumentsClass import CommonArguments

__version__ = "2023.05.04"

parser = CommonArguments()
parser.singleprofile()
parser.singleregion()
parser.verbosity()
parser.version(__version__)
parser.my_parser.add_argument(
    "-b",
    "--bucket",
    dest="pBucketName",
    metavar="bucket to empty and delete",
    required=True,
    help="To specify a bucket, use this parameter.",
)
parser.my_parser.add_argument(
    "+delete",
    "+force-delete",
    help="Whether or not to delete the bucket after it's been emptied",
    action="store_const",
    dest="pForceQuit",
    const=True,
    default=False,
)
args = parser.my_parser.parse_args()

pProfile = args.Profile
pRegion = args.Region
pBucketDelete = args.pForceQuit
pBucketName = args.pBucketName
verbose = args.loglevel
logging.basicConfig(level=args.loglevel, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

# Establish AWS session and S3 resource connection
# Uses the specified profile to access S3 services
aws_acct = aws_acct_access(pProfile)
s3 = aws_acct.session.resource(service_name="s3")

# CRITICAL WARNING: Display destructive operation warning
# This ensures users understand the irreversible nature of this operation
print()
print(f"This script is about to delete all versions of all objects from bucket {pBucketName}")
print()

# Create S3 bucket resource for the specified bucket
# This provides access to bucket operations and object management
bucket = s3.Bucket(pBucketName)

try:
    # DESTRUCTIVE OPERATION: Delete all object versions and delete markers
    # This includes:
    # - All current object versions
    # - All historical object versions (if versioning enabled)
    # - All delete markers
    # - Cannot be undone once executed
    logging.info(f"Starting deletion of all object versions in bucket {pBucketName}")
    bucket.object_versions.delete()
    logging.info(f"Successfully deleted all object versions from bucket {pBucketName}")

except Exception as my_Error:
    # Handle S3 API errors during object deletion
    # Common errors: AccessDenied, NoSuchBucket, InvalidBucketState
    logging.error(f"Failed to delete objects from bucket {pBucketName}: {my_Error}")
    print(f"Error message: {my_Error}")

# Handle bucket deletion with safety controls
# Provides both automated and interactive deletion modes
DeleteBucket = False

if pBucketDelete:
    # Force deletion mode: Delete bucket without additional confirmation
    # Used for automated scenarios where confirmation is handled externally
    print(f"As per your request, we're deleting the bucket {pBucketName}")
    logging.warning(f"Force deleting bucket {pBucketName} as requested")

    try:
        bucket.delete()
        print(f"Bucket: {pBucketName} has been deleted")
        logging.info(f"Successfully deleted bucket {pBucketName}")
    except Exception as delete_error:
        logging.error(f"Failed to delete bucket {pBucketName}: {delete_error}")
        print(f"Failed to delete bucket: {delete_error}")

else:
    # Interactive deletion mode: Prompt user for confirmation
    # Provides additional safety control for manual operations
    DeleteBucket = input("Now that the bucket is empty, do you want to delete the bucket? (y/n): ") in ["y", "Y"]

    if DeleteBucket:
        try:
            bucket.delete()
            print(f"Bucket: {pBucketName} has been deleted")
            logging.info(f"User confirmed deletion of bucket {pBucketName}")
        except Exception as delete_error:
            logging.error(f"Failed to delete bucket {pBucketName}: {delete_error}")
            print(f"Failed to delete bucket: {delete_error}")
    else:
        print(f"Bucket: {pBucketName} has NOT been deleted")
        logging.info(f"User chose to preserve bucket {pBucketName}")
# Operation completion notification
print()
print("Thanks for using this script...")
logging.info("S3 bucket operation completed successfully")
print()
