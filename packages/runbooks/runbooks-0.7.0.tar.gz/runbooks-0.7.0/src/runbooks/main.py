"""
CloudOps Runbooks - Main CLI entry point for all runbook commands.

This module provides the command-line interface for CloudOps automation,
integrating AWS Cloud Foundations best practices with operational runbooks.

Following KISS principle: this is the main entry point combining both CLI logic and main execution.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from loguru import logger

try:
    from rich.console import Console
    from rich.table import Table

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

    # Simple fallback console
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

        def status(self, message):
            print(f"Status: {message}")
            return self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class Table:
        def __init__(self, title=""):
            self.title = title
            self.columns = []
            self.rows = []

        def add_column(self, name, style=""):
            self.columns.append(name)

        def add_row(self, *args):
            self.rows.append(args)

        def __str__(self):
            if not self.columns:
                return ""

            # Simple text table
            output = f"\n{self.title}\n" + "=" * len(self.title) + "\n"
            output += " | ".join(self.columns) + "\n"
            output += "-" * (len(" | ".join(self.columns))) + "\n"

            for row in self.rows:
                output += " | ".join(str(cell) for cell in row) + "\n"

            return output


from runbooks import __version__
from runbooks.cfat.runner import AssessmentRunner
from runbooks.config import load_config, save_config
from runbooks.inventory.core.collector import InventoryCollector
from runbooks.organizations.manager import OUManager
from runbooks.utils import setup_logging

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--profile", default="default", help="AWS profile to use")
@click.option("--region", help="AWS region (overrides profile region)")
@click.option("--config", type=click.Path(), help="Configuration file path")
@click.pass_context
def main(ctx, debug, profile, region, config):
    """
    CloudOps Runbooks - Enterprise CloudOps Automation Toolkit.

    This tool provides comprehensive AWS automation capabilities including:
    - Cloud Foundations Assessment Tool (CFAT)
    - Multi-account resource inventory
    - Organization management
    - Control Tower automation
    - Identity and access management
    - Centralized logging setup

    Use 'runbooks COMMAND --help' for more information on specific commands.
    """
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["profile"] = profile
    ctx.obj["region"] = region

    # Setup logging
    setup_logging(debug=debug)

    # Load configuration
    config_path = Path(config) if config else Path.home() / ".runbooks" / "config.yaml"
    ctx.obj["config"] = load_config(config_path)

    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ============================================================================
# CFAT Commands
# ============================================================================


@main.group()
@click.pass_context
def cfat(ctx):
    """Cloud Foundations Assessment Tool - Assess AWS account configuration."""
    pass


@cfat.command()
@click.option(
    "--output",
    type=click.Choice(["console", "html", "csv", "json", "markdown", "all"]),
    default="console",
    help="Output format (use 'all' for multiple formats)",
)
@click.option("--output-file", type=click.Path(), help="Output file path (auto-generated if not specified)")
@click.option("--checks", multiple=True, help="Specific checks to run")
@click.option("--skip-checks", multiple=True, help="Checks to skip")
@click.option("--categories", multiple=True, help="Assessment categories to include")
@click.option("--skip-categories", multiple=True, help="Assessment categories to exclude")
@click.option("--severity", type=click.Choice(["INFO", "WARNING", "CRITICAL"]), help="Minimum severity level to report")
@click.option("--parallel/--sequential", default=True, help="Enable/disable parallel execution")
@click.option("--max-workers", type=int, default=10, help="Maximum parallel workers")
@click.option("--compliance-framework", help="Target compliance framework (SOC2, PCI-DSS, HIPAA)")
@click.option("--export-jira", type=click.Path(), help="Export findings to Jira CSV format")
@click.option("--export-asana", type=click.Path(), help="Export findings to Asana CSV format")
@click.option("--export-servicenow", type=click.Path(), help="Export findings to ServiceNow JSON format")
@click.option("--serve-web", is_flag=True, help="Start web server for interactive reports")
@click.option("--web-port", type=int, default=8080, help="Port for web server")
@click.pass_context
def assess(
    ctx,
    output,
    output_file,
    checks,
    skip_checks,
    categories,
    skip_categories,
    severity,
    parallel,
    max_workers,
    compliance_framework,
    export_jira,
    export_asana,
    export_servicenow,
    serve_web,
    web_port,
):
    """
    Run enhanced Cloud Foundations assessment with enterprise features.

    This command performs a comprehensive assessment of your AWS account
    configuration against Cloud Foundations best practices with advanced
    features including multi-format reporting, parallel execution,
    compliance framework alignment, and project management integration.

    Examples:
        # Basic assessment with HTML report
        runbooks cfat assess --output html --output-file report.html

        # Target specific categories and severity
        runbooks cfat assess --categories iam,cloudtrail --severity CRITICAL

        # Parallel execution with custom workers
        runbooks cfat assess --parallel --max-workers 5

        # Compliance framework assessment
        runbooks cfat assess --compliance-framework SOC2 --output all

        # Export to project management tools
        runbooks cfat assess --export-jira jira_tasks.csv --export-asana asana_tasks.csv

        # Interactive web report
        runbooks cfat assess --serve-web --web-port 8080
    """
    logger.info(f"Starting enhanced Cloud Foundations assessment for profile: {ctx.obj['profile']}")

    with console.status("[bold green]Running enhanced assessment checks...") as status:
        try:
            # Initialize enhanced assessment runner
            runner = AssessmentRunner(profile=ctx.obj["profile"], region=ctx.obj["region"])

            # Configure assessment parameters
            if checks:
                runner.set_checks(list(checks))
            if skip_checks:
                runner.skip_checks(list(skip_checks))
            if severity:
                runner.set_min_severity(severity)

            # Configure categories
            if categories:
                runner.assessment_config.included_categories = list(categories)
            if skip_categories:
                runner.assessment_config.excluded_categories = list(skip_categories)

            # Configure execution settings
            runner.assessment_config.parallel_execution = parallel
            runner.assessment_config.max_workers = max_workers

            # Set compliance framework
            if compliance_framework:
                runner.assessment_config.compliance_framework = compliance_framework

            status.update("[bold green]Executing assessment checks...")

            # Run assessment
            report = runner.run_assessment()

            status.update("[bold green]Generating reports...")

            # Display console summary
            display_assessment_results(report)

            # Generate output files
            generated_files = []

            if output == "all":
                # Generate all formats
                timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
                base_name = f"cfat_report_{timestamp}"

                report.to_html(f"{base_name}.html")
                generated_files.append(f"{base_name}.html")

                report.to_json(f"{base_name}.json")
                generated_files.append(f"{base_name}.json")

                report.to_csv(f"{base_name}.csv")
                generated_files.append(f"{base_name}.csv")

                report.to_markdown(f"{base_name}.md")
                generated_files.append(f"{base_name}.md")

            elif output != "console":
                # Generate specific format
                if not output_file:
                    timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
                    output_file = f"cfat_report_{timestamp}.{output}"

                if output == "html":
                    report.to_html(output_file)
                elif output == "csv":
                    report.to_csv(output_file)
                elif output == "json":
                    report.to_json(output_file)
                elif output == "markdown":
                    report.to_markdown(output_file)

                generated_files.append(output_file)

            # Export to project management tools
            if export_jira:
                from runbooks.cfat.reporting.exporters import JiraExporter

                exporter = JiraExporter()
                exporter.export(report, export_jira)
                generated_files.append(export_jira)

            if export_asana:
                from runbooks.cfat.reporting.exporters import AsanaExporter

                exporter = AsanaExporter()
                exporter.export(report, export_asana)
                generated_files.append(export_asana)

            if export_servicenow:
                from runbooks.cfat.reporting.exporters import ServiceNowExporter

                exporter = ServiceNowExporter()
                exporter.export(report, export_servicenow)
                generated_files.append(export_servicenow)

            # Start web server if requested
            if serve_web:
                start_web_server(report, web_port)

            # Display success message
            if generated_files:
                console.print(f"\n[green]✓ Assessment completed successfully![/green]")
                console.print(f"[green]✓ Generated files:[/green]")
                for file in generated_files:
                    console.print(f"  • {file}")

            # Display summary statistics
            console.print(f"\n[bold]Assessment Summary:[/bold]")
            console.print(f"• Compliance Score: [bold]{report.summary.compliance_score}/100[/bold]")
            console.print(f"• Risk Level: [bold]{report.summary.risk_level}[/bold]")
            console.print(f"• Critical Issues: [bold red]{report.summary.critical_issues}[/bold red]")
            console.print(f"• Total Checks: {report.summary.total_checks}")
            console.print(f"• Pass Rate: {report.summary.pass_rate:.1f}%")

        except Exception as e:
            logger.error(f"Assessment failed: {e}")
            console.print(f"[red]✗ Assessment failed: {e}[/red]")
            sys.exit(1)


def start_web_server(report, port: int = 8080):
    """
    Start interactive web server for assessment results.

    Args:
        report: Assessment report to serve
        port: Port number for web server
    """
    try:
        import os
        import tempfile
        import threading
        import webbrowser
        from http.server import HTTPServer, SimpleHTTPRequestHandler

        # Generate HTML report in temporary directory
        temp_dir = tempfile.mkdtemp()
        html_file = os.path.join(temp_dir, "assessment_report.html")
        report.to_html(html_file)

        # Change to temp directory for serving
        os.chdir(temp_dir)

        # Start web server in background thread
        def serve():
            httpd = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)
            console.print(f"[green]🌐 Web server started at http://localhost:{port}[/green]")
            console.print(f"[yellow]Press Ctrl+C to stop the server[/yellow]")
            httpd.serve_forever()

        server_thread = threading.Thread(target=serve, daemon=True)
        server_thread.start()

        # Open browser
        webbrowser.open(f"http://localhost:{port}/assessment_report.html")

        # Keep main thread alive
        try:
            server_thread.join()
        except KeyboardInterrupt:
            console.print(f"\n[yellow]Web server stopped[/yellow]")

    except ImportError:
        console.print(f"[red]Web server functionality requires additional dependencies[/red]")
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        console.print(f"[red]Failed to start web server: {e}[/red]")


def display_assessment_results(report):
    """
    Display enhanced assessment results in formatted tables.

    Args:
        report: Assessment report to display
    """
    # Display executive summary first
    console.print(f"\n[bold blue]📊 Cloud Foundations Assessment Results[/bold blue]")
    console.print(f"[dim]Account: {report.account_id} | Region: {report.region} | Profile: {report.profile}[/dim]")

    # Summary metrics table
    summary_table = Table(title="Assessment Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="cyan", width=20)
    summary_table.add_column("Value", style="bold", width=15)
    summary_table.add_column("Status", width=15)

    # Add summary rows with enhanced formatting
    summary_table.add_row(
        "Compliance Score",
        f"{report.summary.compliance_score}/100",
        f"[{'green' if report.summary.compliance_score >= 80 else 'yellow' if report.summary.compliance_score >= 60 else 'red'}]{report.summary.risk_level}[/]",
    )
    summary_table.add_row("Total Checks", str(report.summary.total_checks), "✓ Completed")
    summary_table.add_row(
        "Pass Rate",
        f"{report.summary.pass_rate:.1f}%",
        f"[{'green' if report.summary.pass_rate >= 80 else 'yellow' if report.summary.pass_rate >= 60 else 'red'}]{'Good' if report.summary.pass_rate >= 80 else 'Fair' if report.summary.pass_rate >= 60 else 'Poor'}[/]",
    )
    summary_table.add_row(
        "Critical Issues",
        str(report.summary.critical_issues),
        f"[{'red' if report.summary.critical_issues > 0 else 'green'}]{'Action Required' if report.summary.critical_issues > 0 else 'None'}[/]",
    )
    summary_table.add_row(
        "Execution Time",
        f"{report.summary.total_execution_time:.1f}s",
        f"[dim]{report.summary.avg_execution_time:.2f}s avg[/dim]",
    )

    console.print(summary_table)

    # Category breakdown
    if report.results:
        console.print(f"\n[bold]📋 Results by Category[/bold]")
        category_summary = report.get_category_summary()

        category_table = Table(show_header=True, header_style="bold magenta")
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Total", justify="center")
        category_table.add_column("Passed", justify="center", style="green")
        category_table.add_column("Failed", justify="center", style="red")
        category_table.add_column("Critical", justify="center", style="bold red")
        category_table.add_column("Pass Rate", justify="center")

        for category, stats in category_summary.items():
            pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            pass_rate_color = "green" if pass_rate >= 80 else "yellow" if pass_rate >= 60 else "red"

            category_table.add_row(
                category.upper(),
                str(stats["total"]),
                str(stats["passed"]),
                str(stats["failed"]),
                str(stats["critical"]),
                f"[{pass_rate_color}]{pass_rate:.1f}%[/{pass_rate_color}]",
            )

        console.print(category_table)

    # Show failed checks if any
    failed_results = report.get_failed_results()
    if failed_results:
        console.print(f"\n[bold red]🚨 Failed Checks ({len(failed_results)})[/bold red]")

        failed_table = Table(show_header=True, header_style="bold magenta")
        failed_table.add_column("Finding ID", style="cyan", width=12)
        failed_table.add_column("Check", style="bold", width=25)
        failed_table.add_column("Severity", width=10)
        failed_table.add_column("Message", style="dim", width=50)

        for result in failed_results[:10]:  # Show first 10 failed checks
            severity_color = {"INFO": "blue", "WARNING": "yellow", "CRITICAL": "red"}.get(
                result.severity.value, "white"
            )

            failed_table.add_row(
                result.finding_id,
                result.check_name,
                f"[{severity_color}]{result.severity.value}[/{severity_color}]",
                result.message[:47] + "..." if len(result.message) > 50 else result.message,
            )

        if len(failed_results) > 10:
            console.print(f"[dim]... and {len(failed_results) - 10} more failed checks[/dim]")

        console.print(failed_table)

    # Show critical findings if any
    critical_results = report.get_critical_results()
    if critical_results:
        console.print(f"\n[bold red]⚠️  Critical Findings Requiring Immediate Action[/bold red]")
        for i, result in enumerate(critical_results[:3], 1):  # Show first 3 critical
            console.print(f"[red]{i}. {result.finding_id}[/red]: {result.message}")
            if result.recommendations:
                console.print(f"   [yellow]→ {result.recommendations[0]}[/yellow]")

        if len(critical_results) > 3:
            console.print(f"   [dim]... and {len(critical_results) - 3} more critical findings[/dim]")

    # Final recommendations
    console.print(f"\n[bold]📝 Next Steps[/bold]")
    if report.summary.critical_issues > 0:
        console.print(f"[red]• Address {report.summary.critical_issues} critical security issues immediately[/red]")
    if report.summary.failed_checks > 0:
        console.print(f"[yellow]• Review and remediate {report.summary.failed_checks} failed checks[/yellow]")
    if report.summary.pass_rate < 80:
        console.print(
            f"[yellow]• Improve overall compliance score (currently {report.summary.compliance_score}/100)[/yellow]"
        )
    else:
        console.print(f"[green]• Maintain current security posture and continue monitoring[/green]")


# ============================================================================
# Inventory Commands
# ============================================================================


@main.group()
@click.pass_context
def inventory(ctx):
    """Multi-account resource inventory and discovery."""
    pass


@inventory.command()
@click.option("--resources", "-r", multiple=True, help="Resource types to inventory (ec2, rds, lambda, etc.)")
@click.option("--all-resources", is_flag=True, help="Inventory all resource types")
@click.option("--accounts", "-a", multiple=True, help="Account IDs to inventory")
@click.option("--all-accounts", is_flag=True, help="Inventory all organization accounts")
@click.option("--output", type=click.Choice(["table", "csv", "json", "excel"]), default="table", help="Output format")
@click.option("--output-file", type=click.Path(), help="Output file path")
@click.option("--include-costs", is_flag=True, help="Include cost information")
@click.option("--parallel", is_flag=True, default=True, help="Run in parallel")
@click.pass_context
def collect(ctx, resources, all_resources, accounts, all_accounts, output, output_file, include_costs, parallel):
    """
    Collect inventory of AWS resources across accounts.

    Examples:
        runbooks inventory collect --all-resources --output excel
        runbooks inventory collect -r ec2 -r rds --accounts 123456789012
        runbooks inventory collect --all-accounts --include-costs
    """
    logger.info("Starting resource inventory collection")

    with console.status("[bold green]Collecting inventory...") as status:
        try:
            # Initialize inventory collector
            collector = InventoryCollector(profile=ctx.obj["profile"], region=ctx.obj["region"], parallel=parallel)

            # Configure resources
            if all_resources:
                resource_types = collector.get_all_resource_types()
            elif resources:
                resource_types = list(resources)
            else:
                resource_types = ["ec2", "rds", "s3", "lambda"]  # Default set

            # Configure accounts
            if all_accounts:
                account_ids = collector.get_organization_accounts()
            elif accounts:
                account_ids = list(accounts)
            else:
                account_ids = [collector.get_current_account_id()]

            # Collect inventory
            results = collector.collect_inventory(
                resource_types=resource_types, account_ids=account_ids, include_costs=include_costs
            )

            # Generate output
            if output == "table":
                display_inventory_results(results)
            else:
                from runbooks.inventory.core.formatter import InventoryFormatter

                formatter = InventoryFormatter(results)

                if not output_file:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"inventory_{timestamp}.{output}"

                if output == "csv":
                    formatter.to_csv(output_file)
                elif output == "json":
                    formatter.to_json(output_file)
                elif output == "excel":
                    formatter.to_excel(output_file)

                console.print(f"[green]✓ Inventory saved to: {output_file}[/green]")

        except Exception as e:
            logger.error(f"Inventory collection failed: {e}")
            console.print(f"[red]✗ Collection failed: {e}[/red]")
            sys.exit(1)


# ============================================================================
# Organizations Commands
# ============================================================================


@main.group()
@click.pass_context
def org(ctx):
    """AWS Organizations management and automation."""
    pass


@org.command()
@click.option(
    "--template",
    type=click.Choice(["standard", "security", "custom"]),
    default="standard",
    help="OU structure template",
)
@click.option("--config-file", type=click.Path(exists=True), help="Custom OU structure configuration file")
@click.option("--dry-run", is_flag=True, help="Show what would be created")
@click.pass_context
def setup_ous(ctx, template, config_file, dry_run):
    """
    Set up organizational unit structure.

    Creates a best-practice OU structure for AWS Organizations
    based on Cloud Foundations recommendations.

    Examples:
        runbooks org setup-ous --template security
        runbooks org setup-ous --config-file ou_structure.yaml --dry-run
    """
    logger.info(f"Setting up OU structure with template: {template}")

    try:
        manager = OUManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        if config_file:
            structure = manager.load_structure_from_file(config_file)
        else:
            structure = manager.get_template_structure(template)

        if dry_run:
            console.print("[yellow]DRY RUN - No changes will be made[/yellow]\n")
            display_ou_structure(structure)
        else:
            with console.status("[bold green]Creating OU structure..."):
                results = manager.create_ou_structure(structure)
                display_creation_results(results)

    except Exception as e:
        logger.error(f"OU setup failed: {e}")
        console.print(f"[red]✗ Setup failed: {e}[/red]")
        sys.exit(1)


def display_inventory_results(results):
    """Display inventory results in a formatted table."""
    from runbooks.inventory.core.formatter import InventoryFormatter

    formatter = InventoryFormatter(results)
    console_output = formatter.format_console_table()
    console.print(console_output)


def display_ou_structure(structure):
    """Display OU structure in a formatted view."""
    table = Table(title=f"OU Structure: {structure.get('name', 'Unnamed')}")
    table.add_column("OU Name", style="cyan")
    table.add_column("Description", style="dim")
    table.add_column("Level", style="bold")

    def add_ou_to_table(ou_def, level=0):
        indent = "  " * level
        table.add_row(f"{indent}{ou_def['name']}", ou_def.get("description", ""), str(level))

        for child in ou_def.get("children", []):
            add_ou_to_table(child, level + 1)

    for ou in structure.get("organizational_units", []):
        add_ou_to_table(ou)

    console.print(table)


def display_creation_results(results):
    """Display OU creation results."""
    table = Table(title="OU Creation Results")
    table.add_column("OU Name", style="cyan")
    table.add_column("OU ID", style="bold")
    table.add_column("Parent ID", style="dim")
    table.add_column("Status", style="green")

    def add_results_to_table(ou_result, level=0):
        indent = "  " * level
        table.add_row(f"{indent}{ou_result['name']}", ou_result["id"], ou_result["parent_id"], "✓ Created")

        for child in ou_result.get("children", []):
            add_results_to_table(child, level + 1)

    for ou_result in results.get("created_ous", []):
        add_results_to_table(ou_result)

    console.print(table)

    if results.get("errors"):
        console.print("\n[red]Errors:[/red]")
        for error in results["errors"]:
            console.print(f"  [red]✗ {error}[/red]")


# ============================================================================
# FinOps Commands
# ============================================================================


@main.group(invoke_without_command=True)
@click.option(
    "--config-file",
    "-C",
    help="Path to a TOML, YAML, or JSON configuration file.",
    type=str,
)
@click.option(
    "--profiles",
    "-p",
    multiple=True,
    help="Specific AWS profiles to use (repeat option to pass multiple)",
    type=str,
)
@click.option(
    "--regions",
    "-r",
    multiple=True,
    help="AWS regions to check for EC2 instances (repeat option to pass multiple)",
    type=str,
)
@click.option("--all", "-a", is_flag=True, help="Use all available AWS profiles")
@click.option(
    "--combine",
    "-c",
    is_flag=True,
    help="Combine profiles from the same AWS account",
)
@click.option(
    "--report-name",
    "-n",
    help="Specify the base name for the report file (without extension)",
    default=None,
    type=str,
)
@click.option(
    "--report-type",
    "-y",
    multiple=True,
    type=click.Choice(["csv", "json", "pdf"]),
    help="Specify one or more report types (repeat option): csv, json, pdf",
    default=("csv",),
)
@click.option(
    "--dir",
    "-d",
    help="Directory to save the report files (default: current directory)",
    type=str,
)
@click.option(
    "--time-range",
    "-t",
    help="Time range for cost data in days (default: current month). Examples: 7, 30, 90",
    type=int,
)
@click.option(
    "--tag",
    "-g",
    multiple=True,
    help="Cost allocation tag filter(s), e.g., --tag Team=DevOps (repeat for multiple)",
    type=str,
)
@click.option(
    "--trend",
    is_flag=True,
    help="Display a trend report as bars for the past 6 months time range",
)
@click.option(
    "--audit",
    is_flag=True,
    help="Display an audit report with cost anomalies, stopped EC2 instances, unused EBS volumes, budget alerts, and more",
)
@click.pass_context
def finops(ctx, **kwargs):
    """AWS FinOps Dashboard - Cost and Resource Monitoring."""
    if ctx.invoked_subcommand is None:
        import argparse

        from runbooks.finops.dashboard_runner import run_dashboard

        args = argparse.Namespace(**kwargs)
        run_dashboard(args)


# ============================================================================
# Security Commands
# ============================================================================


@main.group(invoke_without_command=True)
@click.option(
    "--profile",
    default="default",
    help="AWS IAM profile to use for authentication (default: 'default')"
)
@click.option(
    "--language",
    type=click.Choice(["EN", "JP", "KR", "VN"]),
    default="EN",
    help="Language for security reports (default: 'EN')"
)
@click.option(
    "--output",
    help="Custom output directory for reports (default: ./results)"
)
@click.pass_context
def security(ctx, profile, language, output):
    """AWS Security Baseline Assessment Tool.
    
    Comprehensive security baseline testing with multilingual reporting
    and enterprise-grade assessment features.
    
    Examples:
        runbooks security assess --profile prod --language EN
        runbooks security assess --language KR --output /reports
        runbooks security check root-mfa --profile production
    """
    if ctx.invoked_subcommand is None:
        from runbooks.security import run_security_script
        
        # Create mock args namespace for backward compatibility
        import argparse
        args = argparse.Namespace(
            profile=profile,
            language=language,
            output=output
        )
        
        # Import and run the main security function
        from runbooks.security.security_baseline_tester import SecurityBaselineTester
        
        try:
            console.print(f"[blue]🔒 AWS Security Baseline Assessment[/blue]")
            console.print(f"[dim]Profile: {profile} | Language: {language} | Output: {output or './results'}[/dim]")
            
            tester = SecurityBaselineTester(profile, language, output)
            tester.run()
            
            console.print(f"[green]✅ Security assessment completed successfully![/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error running security assessment: {e}[/red]")
            raise click.ClickException(str(e))


@security.command()
@click.option(
    "--profile",
    default="default",
    help="AWS IAM profile to use for authentication"
)
@click.option(
    "--language",
    type=click.Choice(["EN", "JP", "KR", "VN"]),
    default="EN",
    help="Language for security reports"
)
@click.option(
    "--output",
    help="Custom output directory for reports"
)
@click.option(
    "--checks",
    multiple=True,
    help="Specific security checks to run (repeat for multiple)"
)
@click.option(
    "--format",
    type=click.Choice(["html", "json", "console"]),
    default="html",
    help="Output format for results"
)
@click.pass_context
def assess(ctx, profile, language, output, checks, format):
    """Run comprehensive security baseline assessment.
    
    Evaluates AWS account against security best practices and generates
    detailed reports with findings and remediation guidance.
    
    Examples:
        runbooks security assess --profile prod
        runbooks security assess --language KR --format json
        runbooks security assess --checks root_mfa --checks iam_password_policy
    """
    try:
        from runbooks.security.security_baseline_tester import SecurityBaselineTester
        
        console.print(f"[blue]🔒 Running Security Baseline Assessment[/blue]")
        console.print(f"[dim]Profile: {profile} | Language: {language} | Format: {format}[/dim]")
        
        if checks:
            console.print(f"[dim]Specific checks: {', '.join(checks)}[/dim]")
        
        # Initialize and run security assessment
        tester = SecurityBaselineTester(profile, language, output)
        
        # TODO: Add support for specific checks filtering
        # For now, run all checks
        tester.run()
        
        console.print(f"[green]✅ Security assessment completed![/green]")
        
        # Display results summary
        console.print(f"\n[bold]📊 Assessment Summary:[/bold]")
        console.print(f"[green]• Report generated in {format.upper()} format[/green]")
        console.print(f"[yellow]• Output directory: {output or './results'}[/yellow]")
        console.print(f"[blue]• Language: {language}[/blue]")
        
    except Exception as e:
        console.print(f"[red]❌ Error running security assessment: {e}[/red]")
        raise click.ClickException(str(e))


@security.command()
@click.argument("check_name")
@click.option(
    "--profile",
    default="default",
    help="AWS IAM profile to use"
)
@click.option(
    "--language",
    type=click.Choice(["EN", "JP", "KR", "VN"]),
    default="EN",
    help="Language for output"
)
@click.pass_context
def check(ctx, check_name, profile, language):
    """Run a specific security check.
    
    Available checks:
        root_mfa, root_usage, root_access_key, iam_user_mfa,
        iam_password_policy, direct_attached_policy, alternate_contacts,
        trail_enabled, multi_region_trail, account_level_bucket_public_access,
        bucket_public_access, cloudwatch_alarm_configuration,
        multi_region_instance_usage, guardduty_enabled, trusted_advisor
    
    Examples:
        runbooks security check root_mfa --profile prod
        runbooks security check iam_password_policy --language KR
    """
    try:
        console.print(f"[blue]🔍 Running security check: {check_name}[/blue]")
        console.print(f"[dim]Profile: {profile} | Language: {language}[/dim]")
        
        # TODO: Implement individual check execution
        # For now, show available checks
        available_checks = [
            "root_mfa", "root_usage", "root_access_key", "iam_user_mfa",
            "iam_password_policy", "direct_attached_policy", "alternate_contacts",
            "trail_enabled", "multi_region_trail", "account_level_bucket_public_access",
            "bucket_public_access", "cloudwatch_alarm_configuration",
            "multi_region_instance_usage", "guardduty_enabled", "trusted_advisor"
        ]
        
        if check_name not in available_checks:
            console.print(f"[red]❌ Unknown check: {check_name}[/red]")
            console.print(f"[yellow]Available checks:[/yellow]")
            for check in available_checks:
                console.print(f"  • {check}")
            raise click.ClickException(f"Invalid check name: {check_name}")
        
        console.print(f"[yellow]⚠️ Individual check execution not yet implemented[/yellow]")
        console.print(f"[blue]💡 Use 'runbooks security assess' to run all checks[/blue]")
        
    except Exception as e:
        console.print(f"[red]❌ Error running security check: {e}[/red]")
        raise click.ClickException(str(e))


@security.command()
@click.pass_context
def list_checks(ctx):
    """List all available security checks."""
    console.print(f"[blue]📋 Available Security Checks[/blue]")
    console.print(f"[dim]These checks evaluate AWS account security against best practices[/dim]\n")
    
    checks = {
        "root_mfa": "Check if MFA is enabled for root account",
        "root_usage": "Check root account usage patterns", 
        "root_access_key": "Check for root account access keys",
        "iam_user_mfa": "Check MFA settings for IAM users",
        "iam_password_policy": "Evaluate IAM password policy",
        "direct_attached_policy": "Check for directly attached IAM policies",
        "alternate_contacts": "Verify alternate contact information",
        "trail_enabled": "Check if CloudTrail is enabled",
        "multi_region_trail": "Check for multi-region CloudTrail",
        "account_level_bucket_public_access": "Check S3 account-level public access",
        "bucket_public_access": "Check individual S3 bucket public access",
        "cloudwatch_alarm_configuration": "Verify CloudWatch alarm configuration",
        "multi_region_instance_usage": "Check multi-region EC2 usage",
        "guardduty_enabled": "Check if GuardDuty is enabled",
        "trusted_advisor": "Check Trusted Advisor configuration"
    }
    
    for check_name, description in checks.items():
        console.print(f"[cyan]{check_name:35}[/cyan] {description}")
    
    console.print(f"\n[yellow]💡 Run individual checks:[/yellow]")
    console.print(f"   runbooks security check <check_name>")
    console.print(f"\n[yellow]💡 Run all checks:[/yellow]")
    console.print(f"   runbooks security assess")


# ============================================================================
# Main entry point - KISS principle: everything in one file
# ============================================================================

if __name__ == "__main__":
    main()
