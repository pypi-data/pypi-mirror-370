"""
Project CLI commands for Metis Agent.

Provides command-line interface for project analysis and context operations.
"""

import click
from ..tools.project_context import ProjectContextTool


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f}{size_names[i]}"


@click.group()
def project():
    """Project analysis and context operations."""
    pass


@project.command("analyze")
@click.option("-d", "--directory", default=".", help="Directory to analyze")
def analyze_project(directory):
    """Analyze project structure and context."""
    project_tool = ProjectContextTool()
    result = project_tool.analyze_directory(directory)
    
    if not result.get("success"):
        click.echo(click.style(f"Error: {result.get('error', 'Unknown error')}", fg="red"))
        return
    
    # Display project information
    click.echo(click.style(f"Project Analysis: {result['project_name']}", fg="blue", bold=True))
    click.echo(f"Directory: {result['directory']}")
    click.echo()
    
    # Project types
    if result["project_types"]:
        click.echo(click.style("Detected Project Types:", fg="green", bold=True))
        for pt in result["project_types"]:
            confidence_color = "green" if pt["confidence"] >= 70 else "yellow" if pt["confidence"] >= 40 else "red"
            click.echo(f"  - {pt['type']} ({click.style(f"{pt['confidence']}%", fg=confidence_color)})")
        click.echo()
    
    # Configuration files
    if result["config_files"]:
        click.echo(click.style("Configuration Files:", fg="cyan", bold=True))
        for cf in result["config_files"]:
            if "error" in cf:
                click.echo(f"  [ERROR] {cf['name']} - {cf['error']}")
            else:
                size_str = format_file_size(cf['size'])
                click.echo(f"  [FILE] {cf['name']} ({size_str}) - {cf['type']}")
                
                if "content" in cf and cf["name"] == "package.json":
                    content = cf["content"]
                    click.echo(f"     Name: {content.get('name', 'N/A')}")
                    click.echo(f"     Version: {content.get('version', 'N/A')}")
                    if content.get("scripts"):
                        click.echo(f"     Scripts: {', '.join(content['scripts'])}")
        click.echo()
    
    # Dependencies
    if result["dependencies"]:
        click.echo(click.style("Dependencies:", fg="magenta", bold=True))
        for lang, deps in result["dependencies"].items():
            click.echo(f"  {lang.title()}:")
            if lang == "javascript":
                if deps.get("production"):
                    click.echo(f"    Production: {len(deps['production'])} packages")
                if deps.get("development"):
                    click.echo(f"    Development: {len(deps['development'])} packages")
            elif lang == "python" and "requirements" in deps:
                click.echo(f"    Requirements: {len(deps['requirements'])} packages")
        click.echo()
    
    # Structure overview
    structure = result["structure"]
    click.echo(click.style("Project Structure:", fg="yellow", bold=True))
    click.echo(f"  Total files: {structure['total_files']}")
    click.echo(f"  Total directories: {structure['total_directories']}")
    
    # File types
    if structure["file_types"]:
        click.echo("  File types:")
        for ext, count in sorted(structure["file_types"].items(), key=lambda x: x[1], reverse=True):
            click.echo(f"    {ext}: {count}")
    click.echo()
    
    # Recommendations
    if result["recommendations"]:
        click.echo(click.style("Recommendations:", fg="blue", bold=True))
        for recommendation in result["recommendations"]:
            click.echo(f"  [TIP] {recommendation}")


@project.command("summary")
@click.option("-d", "--directory", default=".", help="Directory to summarize")
def project_summary(directory):
    """Get a concise project summary."""
    project_tool = ProjectContextTool()
    result = project_tool.get_project_summary(directory)
    
    if not result.get("success"):
        click.echo(click.style(f"Error: {result.get('error', 'Unknown error')}", fg="red"))
        return
    
    summary = result["summary"]
    
    click.echo(click.style(f"📊 {summary['project_name']}", fg="blue", bold=True))
    click.echo(f"Language: {summary['primary_language'] or 'Unknown'}")
    if summary['framework']:
        click.echo(f"Framework: {summary['framework']}")
    click.echo(f"Files: {summary['file_count']}")
    
    if summary['key_features']:
        click.echo(f"Features: {', '.join(summary['key_features'])}")
