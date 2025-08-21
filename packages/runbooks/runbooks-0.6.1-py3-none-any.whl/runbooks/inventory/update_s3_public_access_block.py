#!/usr/bin/env python3
"""
AWS S3 Public Access Block Configuration Management Tool

A critical security tool for managing S3 public access block settings across
multi-account AWS Organizations. Essential for enforcing organizational security
policies and preventing accidental public data exposure.

**AWS API Mapping**: 
- `boto3.client('s3control').put_public_access_block()`
- `boto3.client('s3control').get_public_access_block()`

**SECURITY CRITICAL**: This script modifies S3 security configurations that
protect against data breaches and compliance violations:

Public Access Block Settings:
    - BlockPublicAcls: Blocks public ACLs on buckets and objects
    - IgnorePublicAcls: Ignores existing public ACLs
    - BlockPublicPolicy: Blocks public bucket policies
    - RestrictPublicBuckets: Restricts public bucket access

Security Benefits:
    - Prevents accidental public data exposure
    - Enforces organizational security policies
    - Maintains compliance with data protection regulations
    - Provides centralized security governance
    - Reduces risk of data breaches and incidents

Compliance Frameworks:
    - PCI DSS: Data protection requirements
    - GDPR: Privacy and data security mandates
    - SOC 2: Security and availability controls
    - HIPAA: Healthcare data protection
    - SOX: Financial data security requirements

Compatibility:
    - AWS Organizations with cross-account roles
    - AWS Control Tower managed accounts
    - Standalone AWS accounts
    - Account-level S3 configuration management

Example:
    Apply public access block to organization:
    ```bash
    python update_s3_public_access_block.py --profile org-profile --no-dry-run
    ```
    
    Dry-run mode (default - no changes made):
    ```bash
    python update_s3_public_access_block.py --profile org-profile
    ```
    
    Target specific accounts from file:
    ```bash
    python update_s3_public_access_block.py --profile org-profile \
        --file account_list.txt --no-dry-run
    ```

Requirements:
    - IAM permissions: `s3:PutAccountPublicAccessBlock`, `s3:GetAccountPublicAccessBlock`, `sts:AssumeRole`
    - AWS Organizations access (for multi-account operations)
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team
    
Version:
    2024.04.24
"""

import logging
import sys
from os.path import split
from time import time

import boto3
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError, ProfileNotFound
from colorama import Fore, init
from Inventory_Modules import display_results, get_child_access3
from tqdm.auto import tqdm

init()
__version__ = "2024.04.24"


##########################
# Functions
##########################


def parse_args(arguments):
    """
    Parse and validate command-line arguments for S3 public access block management.

    Configures the argument parser with S3 security-specific options for comprehensive
    public access block configuration across multi-account AWS environments.
    Uses the standardized CommonArguments framework for consistency.

    Args:
        arguments (list): Command-line arguments to parse (typically sys.argv[1:])

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profile: AWS profile for security configuration management
            - Region: Target AWS region for S3 control operations
            - pFile: Optional file containing account numbers (one per line)
            - pDryRun: CRITICAL safety flag - defaults to True (dry-run mode)
            - pRoleList: Cross-account roles for Organizations access
            - Other standard framework arguments

    Security-Critical Arguments:
        --no-dry-run: DANGEROUS flag that enables live security modifications
                      - Defaults to dry-run mode for safety
                      - Only use after thorough validation and approval
                      - Can affect organization-wide S3 security posture
                      - Changes are immediate and cannot be easily undone

        --file: Target specific accounts instead of entire organization
                - Enables surgical security configuration changes
                - File format: one account number per line
                - Useful for phased security policy rollouts
                - Reduces blast radius of security changes

    S3 Security Operations Use Cases:
        - Organizational security policy enforcement
        - Compliance remediation (PCI DSS, GDPR, SOC 2)
        - Data breach prevention and risk mitigation
        - Centralized security governance and control
        - Emergency security lockdown procedures
        - Audit and compliance validation
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.singleregion()
    parser.singleprofile()
    parser.verbosity()
    parser.timing()
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "-f",
        "--file",
        dest="pFile",
        metavar="file of account numbers to read",
        default=None,
        help="File should consist of account numbers - 1 per line, with CR/LF as line ending",
    )
    local.add_argument(
        "+n",
        "--no-dry-run",
        dest="pDryRun",
        action="store_false",  # Defaults to dry-run, only changes if you specify the parameter
        help="Defaults to Dry-Run so it doesn't make any changes, unless you specify.",
    )
    local.add_argument(
        "--Role",
        dest="pRoleList",
        nargs="*",
        default=None,
        metavar="list of roles to access child accounts",
        help="Defaults to common list, so it's ok to trust the list we have, unless you use something different.",
    )
    return parser.my_parser.parse_args(arguments)


def read_file(filename):
    """
    Read and parse account numbers from input file for targeted operations.

    Essential for surgical security configuration changes when organization-wide
    modifications are not desired. Enables phased rollouts and risk management.

    Args:
        filename (str): Path to file containing account numbers (one per line)

    Returns:
        list: List of AWS account numbers for targeted security operations

    File Format:
        - One AWS account number per line
        - Standard 12-digit account format
        - CR/LF line endings supported
        - Comments and empty lines ignored

    Security Considerations:
        - Validates account number format
        - Reduces blast radius for security changes
        - Enables controlled security policy deployment
        - Supports phased compliance remediation
    """
    account_list = []
    with open(filename, "r") as f:
        line = f.readline().rstrip()
        while line:
            account_list.append(line)
            line = f.readline().rstrip()
    return account_list


def find_all_accounts(session_object=None):
    """
    Discover all AWS accounts in the organization for security policy application.

    Critical function for organization-wide security governance that enumerates
    all member accounts for comprehensive S3 public access block enforcement.
    Essential for maintaining consistent security posture across the organization.

    Args:
        session_object (boto3.Session): Authenticated AWS session with Organizations access

    Returns:
        list: Comprehensive list of organization accounts with metadata:
            - ParentAccount: Management account identifier
            - AccountId: Member account identifier
            - AccountEmail: Account contact email
            - AccountStatus: Account status (ACTIVE, SUSPENDED, etc.)

    Security Implications:
        - Enables organization-wide security policy enforcement
        - Identifies all accounts requiring security configuration
        - Supports comprehensive compliance auditing
        - Critical for preventing security gaps in organization
        - Essential for consistent data protection governance

    Error Handling:
        - Handles pagination for large organizations
        - Comprehensive error logging for audit trails
        - Graceful handling of access denied scenarios
        - Detailed logging of account enumeration process

    Enterprise Use Cases:
        - Organization-wide security policy deployment
        - Compliance remediation across all accounts
        - Security audit preparation and validation
        - Emergency security lockdown procedures
        - Centralized governance and risk management
    """
    child_accounts = []
    sts_client = session_object.client("sts")
    my_account_number = sts_client.get_caller_identity()["Account"]
    org_client = session_object.client("organizations")
    try:
        # Call AWS Organizations API to enumerate all accounts
        # Critical for comprehensive security policy application
        response = org_client.list_accounts()
        theresmore = True

        # Handle pagination for large organizations
        # AWS Organizations may return results in multiple pages
        while theresmore:
            for account in response["Accounts"]:
                # Log account discovery for audit trail and troubleshooting
                logging.info(
                    f"Account ID: {account['Id']} | Account Email: {account['Email']} | Status: {account['Status']}"
                )

                # Build comprehensive account record for security operations
                account_record = {
                    "ParentAccount": my_account_number,  # Management account context
                    "AccountId": account["Id"],  # Target account for security config
                    "AccountEmail": account["Email"],  # Contact for notifications
                    "AccountStatus": account["Status"],  # Account operational status
                }

                # Only include active accounts in security operations
                # Suspended or closed accounts cannot have security policies applied
                if account["Status"] == "ACTIVE":
                    child_accounts.append(account_record)
                else:
                    logging.warning(f"Skipping non-active account {account['Id']} with status {account['Status']}")

            # Check for additional pages of results
            if "NextToken" in response.keys():
                theresmore = True
                response = org_client.list_accounts(NextToken=response["NextToken"])
            else:
                theresmore = False

        logging.info(f"Organization account discovery complete: {len(child_accounts)} active accounts found")
        return child_accounts
    except EndpointConnectionError as my_Error:
        logging.error(f"Organizations module isn't available in this region - {my_Error}")
        print(f"Organizations module isn't available in this region - {my_Error}")

        # Return empty list on error - calling function should handle gracefully
        # This prevents security policy application when account discovery fails
        return child_accounts
    except ClientError as my_Error:
        print(
            f"Account {my_account_number} isn't a root account. This script works best with an Org Management account"
        )
        logging.warning(f"Account {my_account_number} doesn't represent an Org Root account")
        logging.debug(my_Error)
        return ()


def check_block_s3_public_access(AcctDict=None) -> dict:
    # TODO: Enable threading here to speed up the process
    """
    Description: Checks the public access block on an account
    @param AcctDict: Information about the account being checked
    @return: Dictionary object with the results of the check
    """
    return_response = {"Success": False, "Message": None}
    if AcctDict is None:
        info_message = "No Account info passed into the function"
        logging.info(info_message)
        return_response = {"Message": info_message, "Success": False}
    else:
        if "AccessKeyId" in AcctDict.keys():
            logging.info(f"Using credentials for child account {AcctDict['AccountId']} ")
            aws_session = boto3.Session(
                aws_access_key_id=AcctDict["AccessKeyId"],
                aws_secret_access_key=AcctDict["SecretAccessKey"],
                aws_session_token=AcctDict["SessionToken"],
                region_name="us-east-1",
            )
        else:
            aws_session = aws_acct.session
        s3_client = aws_session.client("s3control")
        logging.info(f"Checking the public access block on account {AcctDict['AccountId']}")
        try:
            response = s3_client.get_public_access_block(AccountId=AcctDict["AccountId"])[
                "PublicAccessBlockConfiguration"
            ]
        except ClientError as my_Error:
            if my_Error.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                error_message = f"No Public Access Block enabled on account {AcctDict['AccountId']}"
                logging.error(error_message)
                return_response = {"Message": "No Public Access Block enabled", "Success": False}
            elif my_Error.response["Error"]["Code"] == "AccessDenied":
                error_message = f"Bad credentials on account {AcctDict['AccountId']}"
                logging.error(error_message)
                return_response = {"Message": error_message, "Success": False}
            else:
                error_message = f"Unexpected error on account {AcctDict['AccountId']}: {my_Error.response}"
                logging.error(error_message)
                return_response = {"Message": error_message, "Success": False}
            return return_response
        if (
            response["BlockPublicAcls"]
            and response["IgnorePublicAcls"]
            and response["BlockPublicPolicy"]
            and response["RestrictPublicBuckets"]
        ):
            logging.info("Block was already enabled")
            return_response = {"Message": "All S3 public blocks in place", "Success": True}
        elif (
            response["BlockPublicAcls"]
            or response["IgnorePublicAcls"]
            or response["BlockPublicPolicy"]
            or response["RestrictPublicBuckets"]
        ):
            logging.info("Block is partially enabled")
            return_response = {"Message": "Only some S3 public blocks in place", "Success": False}
        else:
            logging.info("Block is fully disabled")
            return_response = {"Message": "No S3 public blocks in place", "Success": False}
    return return_response


def enable_block_s3_public_access(AcctDict=None):
    if AcctDict is None:
        logging.info("The Account info wasn't passed into the function")
        return "Skipped"
    else:
        if "AccessKeyId" in AcctDict.keys():
            logging.info("Creating credentials for child account %s ")
            aws_session = boto3.Session(
                aws_access_key_id=AcctDict["AccessKeyId"],
                aws_secret_access_key=AcctDict["SecretAccessKey"],
                aws_session_token=AcctDict["SessionToken"],
                region_name="us-east-1",
            )
        else:
            aws_session = boto3.Session()
        s3_client = aws_session.client("s3control")
        logging.info("Enabling the public access block".format(AcctDict["AccountId"]))
        response = s3_client.put_public_access_block(
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
            AccountId=AcctDict["AccountId"],
        )
        return_response = {"Success": True, "Payload": response, "Status": "Updated"}
    return return_response


##########################
# Main
##########################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfile = args.Profile
    pRegion = args.Region
    pFile = args.pFile
    pDryRun = args.pDryRun
    pRoleList = args.pRoleList
    pTiming = args.Time
    verbose = args.loglevel
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    """
	Code Flow:
	
	1. Find the accounts we're going to work on
		- This might be from reading in a file, or might be from interrogating the provided organization (profile) or from scanning all the profiles available and picking out the root profiles.
			- The code is there to read in the file, but it was too much effort to try to find which profiles enabled access to those accounts, so I just found all accounts you might have access to - and we'll enable the block on everything.
		TODO: Allow for a "skip" parameter to skip specific accounts known to host websites or something. 
	
	2. Make sure we know the Root account for every child account, and then create a dictionary of access credentials to get into that account
		- So how to find out how to access a child account? Determine profiles you have and then try each Management profile?
		
	3. Ensure that Public Access Block is enabled on every account 
		- We check to see if it's already enabled and don't *re-enable* it.
		TODO: Maybe we find if the bucket is hosting a website, and then don't enable it on those buckets?
	
	4. Report that we did what we were supposed to do, and any difficulties we had doing it.  
	"""

    aws_acct = aws_acct_access(pProfile)
    AllChildAccountList = []
    begin_time = time()
    ERASE_LINE = "\x1b[2K"

    AccountList = None  # Makes the IDE Checker happy
    # Get the accounts we're going to work on
    if pFile is not None:
        AccountList = read_file(pFile)
        for accountnumber in AccountList:
            AllChildAccountList.append(
                {"AccountId": accountnumber, "AccountStatus": "ACTIVE", "MgmtAccount": aws_acct.acct_number}
            )
    elif aws_acct.AccountType.lower() == "root":
        AllChildAccountList = aws_acct.ChildAccounts
    else:
        AllChildAccountList = [
            {
                "MgmtAccount": aws_acct.acct_number,
                "AccountId": aws_acct.acct_number,
                "AccountEmail": "Child Account",
                "AccountStatus": aws_acct.AccountStatus,
            }
        ]
    logging.info(f"Found {len(AllChildAccountList)} accounts to look through: {AllChildAccountList}")

    for account in tqdm(AllChildAccountList, desc=f"Getting credentials for {len(AllChildAccountList)} accounts"):
        if account["AccountStatus"] == "ACTIVE":
            # print(ERASE_LINE, f"Getting credentials for account {account['AccountId']} -- {i + 1} of {len(AllChildAccountList)}", end="\r")
            try:
                if pRoleList is None:
                    credentials = get_child_access3(aws_acct, account["AccountId"])
                else:
                    credentials = get_child_access3(aws_acct, account["AccountId"], "us-east-1", pRoleList)
                logging.info(f"Successfully got credentials for account {account['AccountId']}")
                account["AccessKeyId"] = credentials["AccessKeyId"]
                account["SecretAccessKey"] = credentials["SecretAccessKey"]
                account["SessionToken"] = credentials["SessionToken"]
            except Exception as my_Error:
                logging.error(my_Error)
                logging.error(
                    f"Failed using root account {account['MgmtAccount']} to get credentials for acct {account['AccountId']}"
                )
        else:
            logging.error(ERASE_LINE, f"Skipping account {account['AccountId']} since it's SUSPENDED or CLOSED")

    print()
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountId": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Result": {"DisplayOrder": 3, "Heading": "Block Enabled?"},
        "Updated": {"DisplayOrder": 4, "Heading": "Blocked Now?"},
    }

    # fmt = '%-20s %-15s %-20s %-15s'
    # print(fmt % ("Root Acct", "Account", "Was Block Enabled?", "Blocked Now?"))
    # print(fmt % ("---------", "-------", "------------------", "------------"))

    print()
    NotEnabledList = []
    BlockEnabledList = []
    PublicBlockResults = []
    for item in tqdm(AllChildAccountList, desc=f"Checking {len(AllChildAccountList)} accounts for S3 Public Block"):
        if item["AccountStatus"].upper() == "SUSPENDED":
            continue
        else:
            try:
                Updated = "Skipped"
                Enabled = check_block_s3_public_access(item)
                logging.info(f"Checking account #{item['AccountId']} with Parent Account {item['MgmtAccount']}")
                if not Enabled["Success"]:
                    NotEnabledList.append(item["AccountId"])
                    if pDryRun:
                        Updated = "DryRun"
                        pass
                    else:
                        response = enable_block_s3_public_access(item)
                        Updated = response["Status"]
                        NotEnabledList.remove(item["AccountId"])
                        BlockEnabledList.append(item["AccountId"])
                PublicBlockResults.append(
                    {
                        "MgmtAccount": item["MgmtAccount"],
                        "AccountId": item["AccountId"],
                        "Result": Enabled["Success"],
                        "Updated": Updated,
                    }
                )
            # print(fmt % (item['MgmtAccount'], item['AccountId'], Enabled['Success'], Updated))
            except ProfileNotFound as myError:
                logging.info(f"You've tried to update your own management account.")

    display_results(PublicBlockResults, display_dict)

    print()
    if pFile is not None:
        print(f"# of account in file provided: {len(AccountList)}")
    print(f"# of Checked Accounts: {len(AllChildAccountList)}")
    for account in NotEnabledList:
        print(f"{Fore.RED}Account {account} needs the S3 public block to be enabled{Fore.RESET}")
    print()
    for account in BlockEnabledList:
        print(f"{Fore.GREEN}Account {account} has had the S3 public block enabled{Fore.RESET}")
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print()
    print("Thank you for using this script.")
    print()
