"""
CloudOps Runbooks - Enterprise CloudOps Automation Toolkit

Provides comprehensive AWS automation capabilities including:
- Cloud Foundations Assessment Tool (CFAT)
- Multi-account resource inventory
- Organization management
- Control Tower automation
- Identity and access management
- Centralized logging setup
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

# Keep package version in sync with distribution metadata
try:
    __version__ = _pkg_version("runbooks")
except Exception:
    # Fallback if metadata is unavailable during editable installs
    __version__ = "0.6.1"

# Core module exports
from runbooks.config import RunbooksConfig, load_config, save_config
from runbooks.utils import ensure_directory, setup_logging, validate_aws_profile

# Cloud Foundations exports - using direct structure
try:
    from runbooks.cfat.runner import AssessmentRunner
    from runbooks.inventory.core.collector import InventoryCollector
    from runbooks.organizations.manager import OUManager

    __all__ = [
        "__version__",
        "setup_logging",
        "load_config",
        "save_config",
        "RunbooksConfig",
        "AssessmentRunner",
        "InventoryCollector",
        "OUManager",
        "ensure_directory",
        "validate_aws_profile",
    ]
except ImportError as e:
    # Graceful degradation if dependencies aren't available
    __all__ = [
        "__version__",
        "setup_logging",
        "load_config",
        "save_config",
        "RunbooksConfig",
        "ensure_directory",
        "validate_aws_profile",
    ]

# FinOps exports
from runbooks.finops import get_cost_data, get_trend, run_dashboard

__all__ = [
    "__version__",
    "setup_logging",
    "load_config",
    "save_config",
    "RunbooksConfig",
    "AssessmentRunner",
    "InventoryCollector",
    "OUManager",
    "ensure_directory",
    "validate_aws_profile",
    # FinOps
    "run_dashboard",
    "get_cost_data",
    "get_trend",
]
