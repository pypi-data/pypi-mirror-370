"""
Organizational Unit (OU) management for AWS Organizations.

This module provides capabilities for setting up and managing
AWS Organizations structure following Cloud Foundations best practices.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from loguru import logger

from runbooks.base import CloudFoundationsBase, ProgressTracker
from runbooks.config import RunbooksConfig


class OUManager(CloudFoundationsBase):
    """
    Manager for AWS Organizations OU structure.

    Provides capabilities to create and manage organizational unit
    structures based on Cloud Foundations templates.
    """

    def __init__(
        self, profile: Optional[str] = None, region: Optional[str] = None, config: Optional[RunbooksConfig] = None
    ):
        """Initialize OU manager."""
        super().__init__(profile, region, config)
        self._org_client = None

    @property
    def org_client(self):
        """Get AWS Organizations client."""
        if self._org_client is None:
            self._org_client = self.get_client("organizations")
        return self._org_client

    def get_template_structure(self, template: str) -> Dict[str, Any]:
        """
        Get predefined OU structure template.

        Args:
            template: Template name ('standard', 'security', 'custom')

        Returns:
            OU structure definition
        """
        templates = {
            "standard": {
                "name": "Standard OU Structure",
                "description": "Standard Cloud Foundations OU structure",
                "organizational_units": [
                    {
                        "name": "Core",
                        "description": "Core organizational units for foundational services",
                        "children": [
                            {
                                "name": "Log Archive",
                                "description": "Centralized logging account",
                                "policies": ["LogArchivePolicy"],
                            },
                            {
                                "name": "Audit",
                                "description": "Security and compliance auditing",
                                "policies": ["AuditPolicy"],
                            },
                            {
                                "name": "Shared Services",
                                "description": "Shared infrastructure services",
                                "policies": ["SharedServicesPolicy"],
                            },
                        ],
                    },
                    {
                        "name": "Production",
                        "description": "Production workload accounts",
                        "children": [
                            {
                                "name": "Prod-WebApps",
                                "description": "Production web applications",
                                "policies": ["ProductionPolicy"],
                            },
                            {
                                "name": "Prod-Data",
                                "description": "Production data services",
                                "policies": ["ProductionPolicy", "DataPolicy"],
                            },
                        ],
                    },
                    {
                        "name": "Non-Production",
                        "description": "Development and testing accounts",
                        "children": [
                            {
                                "name": "Development",
                                "description": "Development environments",
                                "policies": ["DevelopmentPolicy"],
                            },
                            {
                                "name": "Testing",
                                "description": "Testing and staging environments",
                                "policies": ["TestingPolicy"],
                            },
                        ],
                    },
                ],
            },
            "security": {
                "name": "Security-Focused OU Structure",
                "description": "Enhanced security OU structure with additional controls",
                "organizational_units": [
                    {
                        "name": "Security",
                        "description": "Security and compliance organizational unit",
                        "children": [
                            {
                                "name": "Security-Prod",
                                "description": "Production security tools",
                                "policies": ["SecurityProdPolicy"],
                            },
                            {
                                "name": "Security-NonProd",
                                "description": "Non-production security tools",
                                "policies": ["SecurityNonProdPolicy"],
                            },
                            {
                                "name": "Log Archive",
                                "description": "Centralized security logging",
                                "policies": ["LogArchivePolicy", "SecurityLogPolicy"],
                            },
                            {
                                "name": "Audit",
                                "description": "Security auditing and compliance",
                                "policies": ["AuditPolicy", "CompliancePolicy"],
                            },
                        ],
                    },
                    {
                        "name": "Workloads",
                        "description": "Application workload accounts",
                        "children": [
                            {
                                "name": "Prod-HighSecurity",
                                "description": "High security production workloads",
                                "policies": ["HighSecurityPolicy", "ProductionPolicy"],
                            },
                            {
                                "name": "Prod-Standard",
                                "description": "Standard production workloads",
                                "policies": ["StandardSecurityPolicy", "ProductionPolicy"],
                            },
                            {
                                "name": "NonProd",
                                "description": "Non-production workloads",
                                "policies": ["NonProdPolicy"],
                            },
                        ],
                    },
                ],
            },
        }

        if template not in templates:
            raise ValueError(f"Unknown template: {template}. Available: {list(templates.keys())}")

        logger.info(f"Using OU structure template: {template}")
        return templates[template]

    def load_structure_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load OU structure from YAML file.

        Args:
            file_path: Path to YAML structure file

        Returns:
            OU structure definition
        """
        config_path = Path(file_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Structure file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                structure = yaml.safe_load(f)

            logger.info(f"Loaded OU structure from: {config_path}")
            return structure

        except Exception as e:
            logger.error(f"Failed to load structure file: {e}")
            raise

    def create_ou_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create OU structure in AWS Organizations.

        Args:
            structure: OU structure definition

        Returns:
            Creation results with OU IDs and status
        """
        logger.info(f"Creating OU structure: {structure.get('name', 'Unnamed')}")

        try:
            # Get organization root
            root_id = self._get_organization_root()

            # Create OUs
            results = {"structure_name": structure.get("name"), "root_id": root_id, "created_ous": [], "errors": []}

            organizational_units = structure.get("organizational_units", [])
            progress = ProgressTracker(len(organizational_units), "Creating organizational units")

            for ou_def in organizational_units:
                try:
                    ou_result = self._create_ou_recursive(ou_def, root_id)
                    results["created_ous"].append(ou_result)
                    progress.update(status=f"Created {ou_def['name']}")

                except Exception as e:
                    error_msg = f"Failed to create OU {ou_def['name']}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    progress.update(status=f"Failed {ou_def['name']}")

            progress.complete()

            logger.info(f"OU structure creation completed. Created {len(results['created_ous'])} OUs")
            return results

        except Exception as e:
            logger.error(f"OU structure creation failed: {e}")
            raise

    def _get_organization_root(self) -> str:
        """Get the organization root ID."""
        try:
            response = self._make_aws_call(self.org_client.list_roots)

            if not response.get("Roots"):
                raise Exception("No organization roots found")

            root_id = response["Roots"][0]["Id"]
            logger.debug(f"Found organization root: {root_id}")
            return root_id

        except Exception as e:
            logger.error(f"Failed to get organization root: {e}")
            raise

    def _create_ou_recursive(self, ou_def: Dict[str, Any], parent_id: str) -> Dict[str, Any]:
        """
        Recursively create OU and its children.

        Args:
            ou_def: OU definition
            parent_id: Parent OU ID

        Returns:
            Creation result with OU details
        """
        ou_name = ou_def["name"]
        ou_description = ou_def.get("description", "")

        logger.info(f"Creating OU: {ou_name} under parent: {parent_id}")

        # Check if OU already exists
        existing_ou = self._find_existing_ou(ou_name, parent_id)
        if existing_ou:
            logger.info(f"OU {ou_name} already exists: {existing_ou['Id']}")
            ou_id = existing_ou["Id"]
        else:
            # Create the OU
            response = self._make_aws_call(self.org_client.create_organizational_unit, ParentId=parent_id, Name=ou_name)

            ou_id = response["OrganizationalUnit"]["Id"]
            logger.info(f"Created OU {ou_name}: {ou_id}")

        result = {"name": ou_name, "id": ou_id, "parent_id": parent_id, "description": ou_description, "children": []}

        # Create child OUs
        children = ou_def.get("children", [])
        for child_def in children:
            try:
                child_result = self._create_ou_recursive(child_def, ou_id)
                result["children"].append(child_result)
            except Exception as e:
                logger.error(f"Failed to create child OU {child_def.get('name', 'Unknown')}: {e}")

        return result

    def _find_existing_ou(self, ou_name: str, parent_id: str) -> Optional[Dict[str, Any]]:
        """Find existing OU by name under a parent."""
        try:
            response = self._make_aws_call(self.org_client.list_organizational_units_for_parent, ParentId=parent_id)

            for ou in response.get("OrganizationalUnits", []):
                if ou["Name"] == ou_name:
                    return ou

            return None

        except Exception as e:
            logger.warning(f"Error checking for existing OU {ou_name}: {e}")
            return None

    def list_organizational_units(self) -> List[Dict[str, Any]]:
        """List all organizational units in the organization."""
        try:
            root_id = self._get_organization_root()
            all_ous = []

            def collect_ous(parent_id: str, level: int = 0):
                response = self._make_aws_call(self.org_client.list_organizational_units_for_parent, ParentId=parent_id)

                for ou in response.get("OrganizationalUnits", []):
                    ou["Level"] = level
                    ou["ParentId"] = parent_id
                    all_ous.append(ou)

                    # Recursively collect child OUs
                    collect_ous(ou["Id"], level + 1)

            collect_ous(root_id)

            logger.info(f"Found {len(all_ous)} organizational units")
            return all_ous

        except Exception as e:
            logger.error(f"Failed to list organizational units: {e}")
            raise

    def delete_ou(self, ou_id: str) -> bool:
        """
        Delete an organizational unit.

        Args:
            ou_id: OU ID to delete

        Returns:
            True if successful
        """
        try:
            # Check if OU has any accounts
            accounts_response = self._make_aws_call(self.org_client.list_accounts_for_parent, ParentId=ou_id)

            if accounts_response.get("Accounts"):
                raise Exception(f"Cannot delete OU {ou_id}: it contains accounts")

            # Check if OU has child OUs
            ous_response = self._make_aws_call(self.org_client.list_organizational_units_for_parent, ParentId=ou_id)

            if ous_response.get("OrganizationalUnits"):
                raise Exception(f"Cannot delete OU {ou_id}: it contains child OUs")

            # Delete the OU
            self._make_aws_call(self.org_client.delete_organizational_unit, OrganizationalUnitId=ou_id)

            logger.info(f"Deleted OU: {ou_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete OU {ou_id}: {e}")
            raise

    def run(self):
        """Implementation of abstract base method."""
        # Default operation: list current OU structure
        return self.list_organizational_units()
