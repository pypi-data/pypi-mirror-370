"""
Dependency management commands for Metis Agent CLI.

Provides dependency analysis, updates, and security checking commands.
"""

import click
import os
from typing import Dict, Any

from ..tools.dependency_manager import DependencyManagerTool


@click.group()
def deps():
    """Dependency management and analysis commands."""
    pass


@deps.command()
@click.option('--cwd', default='.', help='Working directory')
def check(cwd: str):
    """Analyze project dependencies comprehensively."""
    cwd = os.path.abspath(cwd)
    
    if not os.path.exists(cwd):
        click.echo(f"Error: Directory '{cwd}' does not exist", err=True)
        return
    
    tool = DependencyManagerTool()
    result = tool.execute("analyze dependencies", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        supported_files = result.get("supported_files", [])
        if supported_files:
            click.echo(f"Supported files: {', '.join(supported_files)}")
        return
    
    click.echo(f"Dependency Analysis - {result.get('project_type', 'Unknown')}")
    click.echo("=" * 50)
    
    # Show dependency count
    total_count = result.get("total_count", 0)
    click.echo(f"Total dependencies: {total_count}")
    
    # Show dependencies if available
    dependencies = result.get("dependencies", {})
    if dependencies and len(dependencies) <= 20:  # Don't overwhelm with too many
        click.echo(f"\nDependencies:")
        for name, info in dependencies.items():
            version = info.get("version", "unknown") if isinstance(info, dict) else str(info)
            source = info.get("source", "") if isinstance(info, dict) else ""
            click.echo(f"  {name} {version} {f'({source})' if source else ''}")
    elif len(dependencies) > 20:
        click.echo(f"\n({total_count} dependencies - use 'metis deps list' to see all)")
    
    # Show insights
    insights = result.get("insights", [])
    if insights:
        click.echo(f"\nInsights:")
        for insight in insights:
            click.echo(f"  {insight}")
    
    # Show suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        click.echo(f"\nSuggestions:")
        for suggestion in suggestions:
            click.echo(f"  {suggestion}")


@deps.command()
@click.option('--cwd', default='.', help='Working directory')
def update(cwd: str):
    """Check for available dependency updates."""
    cwd = os.path.abspath(cwd)
    
    tool = DependencyManagerTool()
    result = tool.execute("check updates", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("Dependency Updates")
    click.echo("=" * 50)
    
    outdated_count = result.get("outdated_count", 0)
    updates_available = result.get("updates_available", [])
    
    if outdated_count == 0:
        click.echo("All dependencies are up to date!")
        return
    
    click.echo(f"Updates available for {outdated_count} packages:")
    click.echo()
    
    for update in updates_available:
        package = update.get("package", "unknown")
        current = update.get("current", "unknown")
        latest = update.get("latest", "unknown")
        command = update.get("command", "")
        
        click.echo(f"  {package}: {current} -> {latest}")
        if command:
            click.echo(f"    Command: {command}")
        click.echo()
    
    # Show bulk update command if available
    bulk_command = result.get("bulk_update_command")
    if bulk_command:
        click.echo(f"Bulk update command:")
        click.echo(f"  {bulk_command}")
    
    # Show insights
    insights = result.get("insights", [])
    if insights:
        click.echo(f"\nInsights:")
        for insight in insights:
            click.echo(f"  {insight}")


@deps.command()
@click.option('--cwd', default='.', help='Working directory')
def security(cwd: str):
    """Check dependencies for security vulnerabilities."""
    cwd = os.path.abspath(cwd)
    
    tool = DependencyManagerTool()
    result = tool.execute("security check", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("Security Vulnerability Scan")
    click.echo("=" * 50)
    
    scan_tool = result.get("tool", "unknown")
    click.echo(f"Scan tool: {scan_tool}")
    
    # Handle different response formats
    if "vulnerabilities_found" in result:
        # pip-audit style response
        vuln_count = result.get("vulnerabilities_found", 0)
        if vuln_count == 0:
            click.echo("No security vulnerabilities found!")
        else:
            click.echo(f"Found {vuln_count} vulnerabilities")
            vulnerabilities = result.get("vulnerabilities", [])
            for vuln in vulnerabilities[:5]:  # Show first 5
                click.echo(f"  - {vuln}")
            if len(vulnerabilities) > 5:
                click.echo(f"  ... and {len(vulnerabilities) - 5} more")
    
    elif "total_vulnerabilities" in result:
        # npm audit style response
        total_vulns = result.get("total_vulnerabilities", 0)
        if total_vulns == 0:
            click.echo("No security vulnerabilities found!")
        else:
            click.echo(f"Found {total_vulns} vulnerabilities")
            severity = result.get("severity_breakdown", {})
            for level, count in severity.items():
                if count > 0:
                    click.echo(f"  {level}: {count}")
            
            fix_command = result.get("fix_command")
            if fix_command:
                click.echo(f"\nFix command: {fix_command}")
    
    else:
        # Manual/suggestion response
        suggestion = result.get("suggestion")
        if suggestion:
            click.echo(f"Suggestion: {suggestion}")
    
    # Show insights
    insights = result.get("insights", [])
    if insights:
        click.echo(f"\nInsights:")
        for insight in insights:
            click.echo(f"  {insight}")


@deps.command()
@click.option('--cwd', default='.', help='Working directory')
def unused(cwd: str):
    """Find potentially unused dependencies."""
    cwd = os.path.abspath(cwd)
    
    tool = DependencyManagerTool()
    result = tool.execute("find unused dependencies", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("Unused Dependency Detection")
    click.echo("=" * 50)
    
    tool_suggestion = result.get("tool_suggestion")
    command = result.get("command")
    
    if tool_suggestion and command:
        click.echo(f"Recommended tool: {tool_suggestion}")
        click.echo(f"Command to run: {command}")
    
    # Show insights
    insights = result.get("insights", [])
    if insights:
        click.echo(f"\nInsights:")
        for insight in insights:
            click.echo(f"  {insight}")


@deps.command()
@click.argument('packages', nargs=-1, required=True)
@click.option('--cwd', default='.', help='Working directory')
def install(packages, cwd: str):
    """Install new packages and suggest proper commands.
    
    PACKAGES: One or more package names to install
    """
    cwd = os.path.abspath(cwd)
    
    packages_str = ' '.join(packages)
    tool = DependencyManagerTool()
    result = tool.execute(f"install {packages_str}", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("Package Installation")
    click.echo("=" * 50)
    
    project_type = result.get("project_type", "unknown")
    suggested_packages = result.get("suggested_packages", packages)
    commands = result.get("commands", [])
    
    click.echo(f"Project type: {project_type}")
    click.echo(f"Packages to install: {', '.join(suggested_packages)}")
    
    if commands:
        click.echo(f"\nSuggested commands:")
        for i, command in enumerate(commands, 1):
            click.echo(f"  {i}. {command}")


@deps.command()
@click.option('--cwd', default='.', help='Working directory')
def overview(cwd: str):
    """Get a general overview of project dependencies."""
    cwd = os.path.abspath(cwd)
    
    tool = DependencyManagerTool()
    result = tool.execute("dependency overview", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo(f"Dependency Overview - {result.get('project_type', 'Unknown')}")
    click.echo("=" * 50)
    
    dependency_count = result.get("dependency_count")
    if dependency_count is not None:
        click.echo(f"Total dependencies: {dependency_count}")
    
    # Show summary
    summary = result.get("summary", [])
    if summary:
        click.echo(f"\nSummary:")
        for item in summary:
            click.echo(f"  {item}")
    
    # Show available commands
    available_commands = result.get("available_commands", [])
    if available_commands:
        click.echo(f"\nAvailable commands:")
        for command in available_commands:
            click.echo(f"  {command}")


@deps.command()
@click.option('--cwd', default='.', help='Working directory')
def list(cwd: str):
    """List all project dependencies in detail."""
    cwd = os.path.abspath(cwd)
    
    tool = DependencyManagerTool()
    result = tool.execute("analyze dependencies", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo(f"All Dependencies - {result.get('project_type', 'Unknown')}")
    click.echo("=" * 50)
    
    dependencies = result.get("dependencies", {})
    if not dependencies:
        click.echo("No dependencies found")
        return
    
    # Group by source if available
    by_source = {}
    for name, info in dependencies.items():
        if isinstance(info, dict):
            source = info.get("source", "unknown")
            version = info.get("version", "unknown")
        else:
            source = "unknown"
            version = str(info)
        
        if source not in by_source:
            by_source[source] = []
        by_source[source].append((name, version))
    
    for source, deps in by_source.items():
        if source != "unknown":
            click.echo(f"\nFrom {source}:")
        deps.sort()
        for name, version in deps:
            click.echo(f"  {name:<30} {version}")


# Add commands to the main CLI
def add_deps_commands(cli):
    """Add dependency commands to the main CLI."""
    cli.add_command(deps)
