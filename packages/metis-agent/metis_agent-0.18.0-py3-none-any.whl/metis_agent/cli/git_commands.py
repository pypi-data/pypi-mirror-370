"""
Git commands for Metis Agent CLI.

Provides git integration commands for version control operations.
"""

import click
import os
from typing import Dict, Any

from ..tools.git_integration import GitIntegrationTool


@click.group()
def git():
    """Git integration commands for version control operations."""
    pass


@git.command()
@click.option('--cwd', default='.', help='Working directory')
def status(cwd: str):
    """Show git repository status with AI insights."""
    cwd = os.path.abspath(cwd)
    
    if not os.path.exists(cwd):
        click.echo(f"Error: Directory '{cwd}' does not exist", err=True)
        return
    
    tool = GitIntegrationTool()
    result = tool.execute("git status", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo(f"Git Status - {result.get('branch', 'unknown branch')}")
    click.echo("=" * 50)
    
    # Show staged files
    staged = result.get("staged_files", [])
    if staged:
        click.echo(f"\n+ Staged files ({len(staged)}):")
        for file in staged:
            click.echo(f"  + {file}")
    
    # Show unstaged files
    unstaged = result.get("unstaged_files", [])
    if unstaged:
        click.echo(f"\n- Unstaged files ({len(unstaged)}):")
        for file in unstaged:
            click.echo(f"  - {file}")
    
    # Show untracked files
    untracked = result.get("untracked_files", [])
    if untracked:
        click.echo(f"\n? Untracked files ({len(untracked)}):")
        for file in untracked:
            click.echo(f"  ? {file}")
    
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


@git.command()
@click.option('--cwd', default='.', help='Working directory')
@click.option('--count', default=5, help='Number of commits to show')
def history(cwd: str, count: int):
    """Show recent commit history with analysis."""
    cwd = os.path.abspath(cwd)
    
    tool = GitIntegrationTool()
    result = tool.execute(f"git history {count}", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo(f"Recent Commits ({count})")
    click.echo("=" * 50)
    
    commits = result.get("commits", [])
    for commit in commits:
        click.echo(f"\nCommit: {commit.get('hash', 'unknown')}")
        click.echo(f"Author: {commit.get('author', 'unknown')}")
        click.echo(f"Date: {commit.get('date', 'unknown')}")
        click.echo(f"Message: {commit.get('message', 'unknown')}")
    
    # Show insights
    insights = result.get("insights", [])
    if insights:
        click.echo(f"\nHistory Analysis:")
        for insight in insights:
            click.echo(f"  {insight}")


@git.command()
@click.option('--cwd', default='.', help='Working directory')
@click.option('--message', '-m', help='Custom commit message')
def commit(cwd: str, message: str):
    """Generate AI-powered commit message and commit staged changes."""
    cwd = os.path.abspath(cwd)
    
    tool = GitIntegrationTool()
    
    if message:
        # Use provided message
        click.echo(f"Committing with message: '{message}'")
        # Note: This would require actual git commit execution
        click.echo("Note: Actual commit execution not implemented in this demo")
        return
    
    # Generate AI commit message
    result = tool.execute("generate commit message", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    suggested_message = result.get("suggested_message")
    if not suggested_message:
        click.echo("No staged changes found for commit message generation", err=True)
        return
    
    click.echo(f"Suggested commit message:")
    click.echo(f"'{suggested_message}'")
    click.echo()
    
    if click.confirm("Use this commit message?"):
        click.echo("Committing changes...")
        # Note: Actual git commit would be executed here
        click.echo("Note: Actual commit execution not implemented in this demo")
    else:
        click.echo("Commit cancelled")


@git.command()
@click.option('--cwd', default='.', help='Working directory')
def diff(cwd: str):
    """Show diff summary and analysis."""
    cwd = os.path.abspath(cwd)
    
    tool = GitIntegrationTool()
    result = tool.execute("git diff", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("Git Diff Analysis")
    click.echo("=" * 50)
    
    # Show file changes
    files_changed = result.get("files_changed", [])
    if files_changed:
        click.echo(f"\nFiles changed ({len(files_changed)}):")
        for file_info in files_changed:
            if isinstance(file_info, dict):
                file_name = file_info.get("file", "unknown")
                additions = file_info.get("additions", 0)
                deletions = file_info.get("deletions", 0)
                click.echo(f"  {file_name} (+{additions} -{deletions})")
            else:
                click.echo(f"  {file_info}")
    
    # Show insights
    insights = result.get("insights", [])
    if insights:
        click.echo(f"\nDiff Analysis:")
        for insight in insights:
            click.echo(f"  {insight}")
    
    # Show suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        click.echo(f"\nSuggestions:")
        for suggestion in suggestions:
            click.echo(f"  {suggestion}")


@git.command()
@click.option('--cwd', default='.', help='Working directory')
def review(cwd: str):
    """Perform AI-assisted code review of staged changes."""
    cwd = os.path.abspath(cwd)
    
    tool = GitIntegrationTool()
    result = tool.execute("code review", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("AI Code Review")
    click.echo("=" * 50)
    
    # Show review insights
    insights = result.get("insights", [])
    if insights:
        click.echo("\nReview Analysis:")
        for insight in insights:
            click.echo(f"  {insight}")
    
    # Show suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        click.echo(f"\nRecommendations:")
        for suggestion in suggestions:
            click.echo(f"  {suggestion}")
    
    # Show quality score if available
    quality_score = result.get("quality_score")
    if quality_score:
        click.echo(f"\nCode Quality Score: {quality_score}/10")


@git.command()
@click.option('--cwd', default='.', help='Working directory')
def info(cwd: str):
    """Show general git repository information."""
    cwd = os.path.abspath(cwd)
    
    tool = GitIntegrationTool()
    result = tool.execute("git info", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("Git Repository Information")
    click.echo("=" * 50)
    
    # Show basic info
    info_items = [
        ("Repository", result.get("repository_path")),
        ("Current Branch", result.get("branch")),
        ("Remote Origin", result.get("remote_origin")),
        ("Total Commits", result.get("total_commits")),
        ("Contributors", result.get("contributors"))
    ]
    
    for label, value in info_items:
        if value:
            click.echo(f"{label}: {value}")
    
    # Show insights
    insights = result.get("insights", [])
    if insights:
        click.echo(f"\nRepository Insights:")
        for insight in insights:
            click.echo(f"  {insight}")


@git.command('create-branch')
@click.argument('branch_name', required=False)
@click.option('--cwd', default='.', help='Working directory')
def create_branch(branch_name, cwd):
    """Create a new feature branch for development work."""
    from ..tools.git_integration import GitIntegrationTool
    
    tool = GitIntegrationTool()
    
    # Construct task string
    if branch_name:
        task = f"create branch {branch_name}"
    else:
        task = "create feature branch"
    
    result = tool.execute(task, cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        if suggestion := result.get('suggestion'):
            click.echo(f"Suggestion: {suggestion}")
        return
    
    click.echo(result.get('message'))
    
    # Show suggestions
    suggestions = result.get('suggestions', [])
    if suggestions:
        click.echo("\nNext Steps:")
        for suggestion in suggestions:
            click.echo(f"  {suggestion}")


@git.command('switch')
@click.argument('branch_name')
@click.option('--cwd', default='.', help='Working directory')
def switch_branch(branch_name, cwd):
    """Switch to a different branch."""
    from ..tools.git_integration import GitIntegrationTool
    
    tool = GitIntegrationTool()
    task = f"switch branch {branch_name}"
    
    result = tool.execute(task, cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        if suggestion := result.get('suggestion'):
            click.echo(f"Suggestion: {suggestion}")
        return
    
    click.echo(result.get('message'))
    
    # Show suggestions
    suggestions = result.get('suggestions', [])
    if suggestions:
        click.echo("\nNext Steps:")
        for suggestion in suggestions:
            click.echo(f"  {suggestion}")


@git.command('branches')
@click.option('--cwd', default='.', help='Working directory')
def list_branches(cwd):
    """List all git branches."""
    from ..tools.git_integration import GitIntegrationTool
    
    tool = GitIntegrationTool()
    result = tool.execute("list branches", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("Git Branches")
    click.echo("=" * 30)
    
    branches = result.get('branches', [])
    current_branch = result.get('current_branch')
    
    for branch in branches:
        name = branch.get('name', '')
        if branch.get('current'):
            click.echo(f"* {name} (current)")
        else:
            click.echo(f"  {name}")
    
    click.echo(f"\nTotal branches: {result.get('total_branches', 0)}")


# Add commands to the main CLI
def add_git_commands(cli):
    """Add git commands to the main CLI."""
    cli.add_command(git)
