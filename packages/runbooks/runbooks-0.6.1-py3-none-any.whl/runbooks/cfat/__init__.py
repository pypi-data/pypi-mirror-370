"""
Cloud Foundations Assessment Tool (CFAT) - Enterprise CloudOps Assessment.

This module provides comprehensive AWS account assessment capabilities
following Cloud Foundations best practices with enterprise-grade
features including:

- Multi-format reporting (HTML, CSV, JSON, Markdown)
- Parallel assessment execution
- Customizable check configurations
- Compliance framework alignment
- Advanced scoring and risk analysis

The CFAT module is designed for DevOps and SRE teams to automate
compliance validation, security assessment, and operational
readiness evaluation across AWS environments.

Example:
    ```python
    from runbooks.cfat import AssessmentRunner, Severity

    # Initialize and configure assessment
    runner = AssessmentRunner(profile="prod", region="us-east-1")
    runner.set_min_severity(Severity.WARNING)

    # Run assessment
    report = runner.run_assessment()

    # Export results
    report.to_html("assessment_report.html")
    report.to_json("findings.json")

    print(f"Compliance Score: {report.summary.compliance_score}/100")
    print(f"Critical Issues: {report.summary.critical_issues}")
    ```

Version: 0.5.0 (Enhanced with enterprise features)
"""

# Core assessment engine
# Enhanced data models
from runbooks.cfat.models import (
    AssessmentConfig,
    # Core models
    AssessmentReport,
    AssessmentResult,
    AssessmentSummary,
    CheckConfig,
    CheckStatus,
    # Enums
    Severity,
)
from runbooks.cfat.runner import AssessmentRunner

# Version info
__version__ = "0.5.0"
__author__ = "CloudOps Runbooks Team"

# Public API exports
__all__ = [
    # Core functionality
    "AssessmentRunner",
    # Data models
    "AssessmentReport",
    "AssessmentResult",
    "AssessmentSummary",
    "AssessmentConfig",
    "CheckConfig",
    # Enums
    "Severity",
    "CheckStatus",
    # Metadata
    "__version__",
]
