"""
Cloud Foundations Organizations module.

This module provides AWS Organizations management capabilities
including OU structure setup and account management.
"""

from runbooks.organizations.manager import OUManager

__all__ = [
    "OUManager",
]
