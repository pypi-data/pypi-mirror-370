"""
AWS Security Baseline Testing Module.

This module provides comprehensive AWS security baseline testing capabilities
with multilingual reporting and enterprise-grade assessment features.

The security module evaluates AWS accounts against security best practices
and generates detailed HTML reports with findings and remediation guidance.

Features:
    - Comprehensive security checklist validation
    - Multilingual report generation (EN, JP, KR, VN)
    - Parallel execution for performance
    - Enterprise-ready HTML reporting
    - CLI integration with runbooks
    - AWS Organizations and multi-account support

Example:
    ```python
    from runbooks.security import SecurityBaselineTester
    
    # Initialize security tester
    tester = SecurityBaselineTester(
        profile="prod",
        lang_code="EN", 
        output_dir="./security-reports"
    )
    
    # Run security assessment
    tester.run()
    ```

CLI Usage:
    ```bash
    # Run security assessment
    runbooks security assess --profile prod --language EN
    
    # Generate Korean language report
    runbooks security assess --language KR --output /reports
    
    # Run specific security checks
    runbooks security check root-mfa --profile production
    ```

Author: CloudOps Runbooks Team
Version: 1.1.0
"""

from .report_generator import ReportGenerator, generate_html_report
from .run_script import main as run_security_script, parse_arguments
from .security_baseline_tester import SecurityBaselineTester

# Version info
__version__ = "1.1.0"
__author__ = "CloudOps Runbooks Team"

# Public API
__all__ = [
    # Core functionality
    "SecurityBaselineTester",
    "ReportGenerator", 
    "generate_html_report",
    
    # CLI functions
    "run_security_script",
    "parse_arguments",
    
    # Metadata
    "__version__",
    "__author__",
]
