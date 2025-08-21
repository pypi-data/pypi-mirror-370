#!/usr/bin/env python3

"""
Find and Report Unused Elastic IPs (EIPs) via AWS SES.

Author: nnthanh101@gmail.com
Date: 2025-01-07
Version: 2.0.0

Description:
    - Identifies unused Elastic IPs in AWS.
    - Sends details via email using AWS Simple Email Service (SES).

Requirements:
    - IAM Role Permissions:
        * ec2:DescribeAddresses
        * ses:SendEmail
    - Environment Variables:
        * SOURCE_EMAIL: Sender email address verified in SES.
        * DEST_EMAIL: Recipient email address.
"""

import json
import logging
import os
from typing import Dict, List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from runbooks.utils.logger import configure_logger

## ✅ Configure Logger
logger = configure_logger(__name__)


# ==============================
# AWS CLIENT INITIALIZATION
# ==============================
def get_boto3_clients():
    """
    Initializes AWS clients for EC2 and SES.

    Returns:
        Tuple[boto3.client, boto3.client]: EC2 and SES clients.
    """
    ec2_client = boto3.client("ec2")
    ses_client = boto3.client("ses")
    return ec2_client, ses_client


# ==============================
# CONFIGURATION VARIABLES
# ==============================
def load_environment_variables():
    """
    Loads and validates environment variables required for execution.

    Returns:
        Tuple[str, str]: Source and destination email addresses.
    """
    source_email = os.getenv("SOURCE_EMAIL")
    dest_email = os.getenv("DEST_EMAIL")

    if not source_email or not dest_email:
        raise ValueError("Environment variables SOURCE_EMAIL and DEST_EMAIL must be set.")

    return source_email, dest_email


# ==============================
# EIP UTILITIES
# ==============================
def get_unused_eips(ec2_client) -> List[Dict[str, str]]:
    """
    Fetches unused Elastic IPs (EIPs).

    Args:
        ec2_client (boto3.client): EC2 client.

    Returns:
        List[Dict[str, str]]: List of unused EIPs with details.
    """
    try:
        response = ec2_client.describe_addresses()
        unused_eips = []

        for address in response["Addresses"]:
            if "InstanceId" not in address:  ## Not associated with an instance
                unused_eips.append(
                    {
                        "PublicIp": address["PublicIp"],
                        "AllocationId": address["AllocationId"],
                        "Domain": address.get("Domain", "N/A"),  ## VPC or standard
                    }
                )

        logger.info(f"Found {len(unused_eips)} unused EIPs.")
        return unused_eips

    except ClientError as e:
        logger.error(f"Failed to describe addresses: {e.response['Error']['Code']} - {e}")
        raise
    except BotoCoreError as e:
        logger.error(f"BotoCore error occurred: {e}")
        raise


# ==============================
# EMAIL UTILITIES
# ==============================
def format_eip_report(eips: List[Dict[str, str]]) -> str:
    """
    Formats the EIPs data as a markdown table for email reporting.

    Args:
        eips (List[Dict[str, str]]): List of unused EIPs.

    Returns:
        str: Formatted markdown table.
    """
    if not eips:
        return "No unused EIPs found."

    ## Table Header
    table = "| Public IP | Allocation ID | Domain |\n|-----------|----------------|--------|\n"

    ## Table Rows
    for eip in eips:
        table += f"| {eip['PublicIp']} | {eip['AllocationId']} | {eip['Domain']} |\n"

    return table


def send_email_report(ses_client, source_email: str, dest_email: str, eips: List[Dict[str, str]]) -> None:
    """
    Sends an email report via AWS SES.

    Args:
        ses_client (boto3.client): SES client.
        source_email (str): Sender email address.
        dest_email (str): Recipient email address.
        eips (List[Dict[str, str]]): List of unused EIPs.
    """
    try:
        subject = "AWS Report: Unused Elastic IPs (EIPs)"
        body = format_eip_report(eips)

        logger.info(f"Sending email from {source_email} to {dest_email}...")
        ses_client.send_email(
            Source=source_email,
            Destination={"ToAddresses": [dest_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "utf-8"},
                "Body": {"Text": {"Data": body, "Charset": "utf-8"}},
            },
        )
        logger.info("Email sent successfully.")

    except ClientError as e:
        logger.error(f"Failed to send email: {e.response['Error']['Code']} - {e}")
        raise
    except BotoCoreError as e:
        logger.error(f"BotoCore error occurred: {e}")
        raise


# ==============================
# MAIN HANDLER
# ==============================
def lambda_handler(event, context):
    """
    AWS Lambda handler for reporting unused Elastic IPs.

    Args:
        event (dict): AWS event data.
        context: AWS Lambda context.
    """
    try:
        ## ✅ Load configurations
        source_email, dest_email = load_environment_variables()

        ## ✅ Initialize AWS clients
        ec2_client, ses_client = get_boto3_clients()

        ## ✅ Fetch unused EIPs
        unused_eips = get_unused_eips(ec2_client)

        ## ✅ Send email report using SES
        send_email_report(ses_client, source_email, dest_email, unused_eips)

        return {"statusCode": 200, "body": "Report sent successfully."}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}
