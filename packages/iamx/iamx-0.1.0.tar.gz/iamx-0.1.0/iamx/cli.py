"""Command-line interface for iamx."""

import json
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.analyzer import PolicyAnalyzer
from .core.models import AnalysisConfig, Severity
from .reports import MarkdownReporter, JsonReporter


console = Console()


@click.group()
@click.version_option()
def main():
    """IAM Policy Explainer - Local-first IAM policy analyzer."""
    pass


@main.command()
@click.argument('policy_files', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for report')
@click.option('--format', 'output_format', type=click.Choice(['cli', 'markdown', 'json']), 
              default='cli', help='Output format')
@click.option('--fail-on', type=click.Choice(['critical', 'high', 'medium', 'low']), 
              default='high', help='Minimum severity level that causes failure')
@click.option('--include-info', is_flag=True, default=False, 
              help='Include informational findings')
@click.option('--max-findings', type=int, default=10, 
              help='Maximum findings per category')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(policy_files, output, output_format, fail_on, include_info, max_findings, verbose):
    """Analyze IAM policy files for security risks."""
    if not policy_files:
        console.print("[red]Error: No policy files specified[/red]")
        sys.exit(1)
    
    # Convert severity string to enum
    severity_map = {
        'critical': Severity.CRITICAL,
        'high': Severity.HIGH,
        'medium': Severity.MEDIUM,
        'low': Severity.LOW,
    }
    
    # Create analysis configuration
    config = AnalysisConfig(
        fail_on_severity=severity_map[fail_on],
        include_info=include_info,
        max_findings_per_category=max_findings,
    )
    
    # Initialize analyzer
    analyzer = PolicyAnalyzer(config)
    
    # Analyze policies
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing policies...", total=len(policy_files))
        
        if len(policy_files) == 1:
            # Single file analysis
            try:
                result = analyzer.analyze_file(policy_files[0])
                progress.update(task, advance=1)
            except Exception as e:
                console.print(f"[red]Error analyzing {policy_files[0]}: {str(e)}[/red]")
                sys.exit(1)
        else:
            # Multiple file analysis
            try:
                result = analyzer.analyze_multiple_files(list(policy_files))
                progress.update(task, advance=len(policy_files))
            except Exception as e:
                console.print(f"[red]Error during bulk analysis: {str(e)}[/red]")
                sys.exit(1)
    
    # Generate output
    if output_format == 'cli':
        display_cli_results(result, verbose)
    elif output_format == 'markdown':
        reporter = MarkdownReporter()
        report = reporter.generate_report(result)
        if output:
            with open(output, 'w') as f:
                f.write(report)
            console.print(f"[green]Report saved to {output}[/green]")
        else:
            console.print(report)
    elif output_format == 'json':
        reporter = JsonReporter()
        report = reporter.generate_report(result)
        if output:
            with open(output, 'w') as f:
                f.write(report)
            console.print(f"[green]Report saved to {output}[/green]")
        else:
            console.print(report)
    
    # Exit with appropriate code
    if hasattr(result, 'passed'):
        # Single result
        if not result.passed:
            sys.exit(1)
    else:
        # Bulk result
        if result.failed_policies > 0:
            sys.exit(1)


@main.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=8081, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def web(host, port, reload):
    """Start the web interface."""
    try:
        from .web.app_fixed import create_app
        import uvicorn
        
        app = create_app()
        
        console.print(f"[green]Starting iamx web interface at http://{host}:{port}[/green]")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info" if reload else "warning",
        )
    except ImportError:
        console.print("[red]Error: Web dependencies not installed. Install with: pip install iamx[web][/red]")
        sys.exit(1)


def display_cli_results(result, verbose: bool):
    """Display analysis results in CLI format."""
    if hasattr(result, 'passed'):
        # Single result
        display_single_result(result, verbose)
    else:
        # Bulk result
        display_bulk_result(result, verbose)


def display_single_result(result, verbose: bool):
    """Display a single analysis result."""
    # Header
    filename = result.metadata.filename or "Policy"
    console.print(f"\n[bold blue]🔍 Analyzing IAM Policy: {filename}[/bold blue]")
    
    # Summary
    summary_table = Table(title="Analysis Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")
    
    summary_table.add_row("Risk Score", f"{result.risk_score}/10.0")
    summary_table.add_row("Status", "✅ PASSED" if result.passed else "❌ FAILED")
    summary_table.add_row("Total Findings", str(result.total_findings))
    summary_table.add_row("Statements", str(result.metadata.statement_count))
    summary_table.add_row("Actions", str(result.metadata.action_count))
    summary_table.add_row("Resources", str(result.metadata.resource_count))
    
    console.print(summary_table)
    
    # Findings by severity
    if result.findings:
        severity_colors = {
            Severity.CRITICAL: "red",
            Severity.HIGH: "yellow",
            Severity.MEDIUM: "orange",
            Severity.LOW: "blue",
            Severity.INFO: "green",
        }
        
        severity_icons = {
            Severity.CRITICAL: "❌",
            Severity.HIGH: "⚠️",
            Severity.MEDIUM: "🔶",
            Severity.LOW: "ℹ️",
            Severity.INFO: "✅",
        }
        
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            severity_findings = [f for f in result.findings if f.severity == severity]
            if severity_findings:
                console.print(f"\n[bold {severity_colors[severity]}]{severity_icons[severity]} {severity.value.upper()}: {len(severity_findings)} findings[/bold {severity_colors[severity]}]")
                
                for finding in severity_findings:
                    display_finding(finding, verbose, severity_colors[severity])
    else:
        console.print("\n[green]✅ No security issues found![/green]")


def display_bulk_result(result, verbose: bool):
    """Display bulk analysis results."""
    console.print(f"\n[bold blue]🔍 Bulk Analysis Results[/bold blue]")
    
    # Summary table
    summary_table = Table(title="Bulk Analysis Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")
    
    summary_table.add_row("Total Policies", str(result.total_policies))
    summary_table.add_row("Failed Policies", str(result.failed_policies))
    summary_table.add_row("Overall Risk Score", f"{result.overall_risk_score}/10.0")
    
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
        count = result.summary.get(severity.value, 0)
        if count > 0:
            summary_table.add_row(f"{severity.value.title()} Findings", str(count))
    
    console.print(summary_table)
    
    # Individual results
    if verbose:
        for policy_result in result.results:
            console.print(f"\n[bold]Policy: {policy_result.metadata.filename or 'Unknown'}[/bold]")
            console.print(f"  Risk Score: {policy_result.risk_score}/10.0")
            console.print(f"  Status: {'✅ PASSED' if policy_result.passed else '❌ FAILED'}")
            console.print(f"  Findings: {policy_result.total_findings}")


def display_finding(finding, verbose: bool, color: str):
    """Display a single finding."""
    # Title and description
    title_text = Text(finding.title, style=f"bold {color}")
    console.print(f"\n{title_text}")
    console.print(f"   {finding.description}")
    
    # Statement info
    if finding.statement_index is not None:
        console.print(f"   [dim]Statement {finding.statement_index}[/dim]")
    
    # Patterns
    if finding.action_pattern:
        console.print(f"   [dim]Actions: {finding.action_pattern}[/dim]")
    if finding.resource_pattern:
        console.print(f"   [dim]Resources: {finding.resource_pattern}[/dim]")
    
    # Recommendation
    if finding.recommendation:
        console.print(f"   [bold]Recommendation:[/bold] {finding.recommendation}")
    
    # Examples
    if finding.examples and verbose:
        console.print("   [bold]Examples:[/bold]")
        for example in finding.examples:
            console.print(f"     • {example}")
    
    # References
    if finding.references and verbose:
        console.print("   [bold]References:[/bold]")
        for ref in finding.references:
            console.print(f"     • {ref}")


if __name__ == '__main__':
    main()
