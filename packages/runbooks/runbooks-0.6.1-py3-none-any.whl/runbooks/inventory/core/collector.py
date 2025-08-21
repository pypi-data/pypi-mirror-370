"""
Inventory collector for AWS resources.

This module provides the main inventory collection orchestration,
leveraging existing inventory scripts and extending them with
cloud foundations best practices.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from loguru import logger

from runbooks.base import CloudFoundationsBase, ProgressTracker
from runbooks.config import RunbooksConfig


class InventoryCollector(CloudFoundationsBase):
    """
    Main inventory collector for AWS resources.

    Orchestrates resource discovery across multiple accounts and regions,
    providing comprehensive inventory capabilities.
    """

    def __init__(
        self,
        profile: Optional[str] = None,
        region: Optional[str] = None,
        config: Optional[RunbooksConfig] = None,
        parallel: bool = True,
    ):
        """Initialize inventory collector."""
        super().__init__(profile, region, config)
        self.parallel = parallel
        self._resource_collectors = self._initialize_collectors()

    def _initialize_collectors(self) -> Dict[str, str]:
        """Initialize available resource collectors."""
        # Map resource types to their collector modules
        collectors = {
            "ec2": "EC2Collector",
            "rds": "RDSCollector",
            "s3": "S3Collector",
            "lambda": "LambdaCollector",
            "iam": "IAMCollector",
            "vpc": "VPCCollector",
            "cloudformation": "CloudFormationCollector",
            "costs": "CostCollector",
        }

        logger.debug(f"Initialized {len(collectors)} resource collectors")
        return collectors

    def get_all_resource_types(self) -> List[str]:
        """Get list of all available resource types."""
        return list(self._resource_collectors.keys())

    def get_organization_accounts(self) -> List[str]:
        """Get list of accounts in AWS Organization."""
        try:
            organizations_client = self.get_client("organizations")
            response = self._make_aws_call(organizations_client.list_accounts)

            accounts = []
            for account in response.get("Accounts", []):
                if account["Status"] == "ACTIVE":
                    accounts.append(account["Id"])

            logger.info(f"Found {len(accounts)} active accounts in organization")
            return accounts

        except Exception as e:
            logger.warning(f"Could not list organization accounts: {e}")
            # Fallback to current account
            return [self.get_account_id()]

    def get_current_account_id(self) -> str:
        """Get current AWS account ID."""
        return self.get_account_id()

    def collect_inventory(
        self, resource_types: List[str], account_ids: List[str], include_costs: bool = False
    ) -> Dict[str, Any]:
        """
        Collect inventory across specified resources and accounts.

        Args:
            resource_types: List of resource types to collect
            account_ids: List of account IDs to scan
            include_costs: Whether to include cost information

        Returns:
            Dictionary containing inventory results
        """
        logger.info(
            f"Starting inventory collection for {len(resource_types)} resource types across {len(account_ids)} accounts"
        )

        start_time = datetime.now()
        results = {
            "metadata": {
                "collection_time": start_time.isoformat(),
                "account_ids": account_ids,
                "resource_types": resource_types,
                "include_costs": include_costs,
                "collector_profile": self.profile,
                "collector_region": self.region,
            },
            "resources": {},
            "summary": {},
            "errors": [],
        }

        try:
            if self.parallel:
                resource_data = self._collect_parallel(resource_types, account_ids, include_costs)
            else:
                resource_data = self._collect_sequential(resource_types, account_ids, include_costs)

            results["resources"] = resource_data
            results["summary"] = self._generate_summary(resource_data)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            results["metadata"]["duration_seconds"] = duration

            logger.info(f"Inventory collection completed in {duration:.1f}s")
            return results

        except Exception as e:
            logger.error(f"Inventory collection failed: {e}")
            results["errors"].append(str(e))
            return results

    def _collect_parallel(
        self, resource_types: List[str], account_ids: List[str], include_costs: bool
    ) -> Dict[str, Any]:
        """Collect inventory in parallel."""
        results = {}
        total_tasks = len(resource_types) * len(account_ids)
        progress = ProgressTracker(total_tasks, "Collecting inventory")

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit collection tasks
            future_to_params = {}

            for resource_type in resource_types:
                for account_id in account_ids:
                    future = executor.submit(
                        self._collect_resource_for_account, resource_type, account_id, include_costs
                    )
                    future_to_params[future] = (resource_type, account_id)

            # Collect results
            for future in as_completed(future_to_params):
                resource_type, account_id = future_to_params[future]
                try:
                    resource_data = future.result()

                    if resource_type not in results:
                        results[resource_type] = {}

                    results[resource_type][account_id] = resource_data
                    progress.update(status=f"Completed {resource_type} for {account_id}")

                except Exception as e:
                    logger.error(f"Failed to collect {resource_type} for account {account_id}: {e}")
                    progress.update(status=f"Failed {resource_type} for {account_id}")

        progress.complete()
        return results

    def _collect_sequential(
        self, resource_types: List[str], account_ids: List[str], include_costs: bool
    ) -> Dict[str, Any]:
        """Collect inventory sequentially."""
        results = {}
        total_tasks = len(resource_types) * len(account_ids)
        progress = ProgressTracker(total_tasks, "Collecting inventory")

        for resource_type in resource_types:
            results[resource_type] = {}

            for account_id in account_ids:
                try:
                    resource_data = self._collect_resource_for_account(resource_type, account_id, include_costs)
                    results[resource_type][account_id] = resource_data
                    progress.update(status=f"Completed {resource_type} for {account_id}")

                except Exception as e:
                    logger.error(f"Failed to collect {resource_type} for account {account_id}: {e}")
                    results[resource_type][account_id] = {"error": str(e)}
                    progress.update(status=f"Failed {resource_type} for {account_id}")

        progress.complete()
        return results

    def _collect_resource_for_account(self, resource_type: str, account_id: str, include_costs: bool) -> Dict[str, Any]:
        """
        Collect specific resource type for an account.

        This is a mock implementation. In a full implementation,
        this would delegate to specific resource collectors.
        """
        # Mock implementation - replace with actual collectors
        import random
        import time

        # Simulate collection time
        time.sleep(random.uniform(0.1, 0.5))

        # Generate mock data based on resource type
        if resource_type == "ec2":
            return {
                "instances": [
                    {
                        "instance_id": f"i-{random.randint(100000000000, 999999999999):012x}",
                        "instance_type": random.choice(["t3.micro", "t3.small", "m5.large"]),
                        "state": random.choice(["running", "stopped"]),
                        "region": self.region or "us-east-1",
                        "account_id": account_id,
                        "tags": {"Environment": random.choice(["dev", "staging", "prod"])},
                    }
                    for _ in range(random.randint(0, 5))
                ],
                "count": random.randint(0, 5),
            }
        elif resource_type == "rds":
            return {
                "instances": [
                    {
                        "db_instance_identifier": f"db-{random.randint(1000, 9999)}",
                        "engine": random.choice(["mysql", "postgres", "aurora"]),
                        "instance_class": random.choice(["db.t3.micro", "db.t3.small"]),
                        "status": "available",
                        "account_id": account_id,
                    }
                    for _ in range(random.randint(0, 3))
                ],
                "count": random.randint(0, 3),
            }
        elif resource_type == "s3":
            return {
                "buckets": [
                    {
                        "name": f"bucket-{account_id}-{random.randint(1000, 9999)}",
                        "creation_date": datetime.now().isoformat(),
                        "region": self.region or "us-east-1",
                        "account_id": account_id,
                    }
                    for _ in range(random.randint(1, 10))
                ],
                "count": random.randint(1, 10),
            }
        else:
            return {"resources": [], "count": 0, "resource_type": resource_type, "account_id": account_id}

    def _generate_summary(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from collected data."""
        summary = {
            "total_resources": 0,
            "resources_by_type": {},
            "resources_by_account": {},
            "collection_status": "completed",
        }

        for resource_type, accounts_data in resource_data.items():
            type_count = 0

            for account_id, account_data in accounts_data.items():
                if "error" in account_data:
                    continue

                # Count resources based on type
                if resource_type == "ec2":
                    account_count = account_data.get("count", 0)
                elif resource_type == "rds":
                    account_count = account_data.get("count", 0)
                elif resource_type == "s3":
                    account_count = account_data.get("count", 0)
                else:
                    account_count = account_data.get("count", 0)

                type_count += account_count

                if account_id not in summary["resources_by_account"]:
                    summary["resources_by_account"][account_id] = 0
                summary["resources_by_account"][account_id] += account_count

            summary["resources_by_type"][resource_type] = type_count
            summary["total_resources"] += type_count

        return summary

    def run(self):
        """Implementation of abstract base method."""
        # Default inventory collection
        resource_types = ["ec2", "rds", "s3"]
        account_ids = [self.get_current_account_id()]
        return self.collect_inventory(resource_types, account_ids)
