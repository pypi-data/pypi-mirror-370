"""
Project commands for Metis Agent CLI.

Provides project scaffolding and management commands.
"""

import click
import os
from typing import Dict, Any

from ..tools.project_scaffolding import ProjectScaffoldingTool
from ..core.agent import SingleAgent
from ..tools.filesystem import FileSystemTool
from ..tools.git_integration import GitIntegrationTool


@click.group()
def project():
    """Project scaffolding and management commands."""
    pass


@project.command()
@click.argument('project_type')
@click.argument('project_name')
@click.option('--cwd', default='.', help='Directory to create project in')
def init(project_type: str, project_name: str, cwd: str):
    """Initialize a new project with the specified type and name.
    
    PROJECT_TYPE: python, node, fastapi, etc.
    PROJECT_NAME: Name of the project to create
    """
    cwd = os.path.abspath(cwd)
    
    if not os.path.exists(cwd):
        click.echo(f"Error: Directory '{cwd}' does not exist", err=True)
        return
    
    tool = ProjectScaffoldingTool()
    task = f"create {project_type} project"
    result = tool.execute(task, cwd=cwd, project_name=project_name)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo(f"Successfully created {result.get('project_type', 'project')}: {project_name}")
    click.echo(f"Location: {result.get('project_path', 'unknown')}")
    
    # Show created files
    files_created = result.get("files_created", [])
    if files_created:
        click.echo(f"\nFiles created ({len(files_created)}):")
        for file in files_created:
            click.echo(f"  + {file}")
    
    # Show next steps
    next_steps = result.get("next_steps", [])
    if next_steps:
        click.echo(f"\nNext steps:")
        for i, step in enumerate(next_steps, 1):
            click.echo(f"  {i}. {step}")


@project.command()
@click.option('--cwd', default='.', help='Working directory')
def setup(cwd: str):
    """Setup development tooling for an existing project."""
    cwd = os.path.abspath(cwd)
    
    if not os.path.exists(cwd):
        click.echo(f"Error: Directory '{cwd}' does not exist", err=True)
        return
    
    tool = ProjectScaffoldingTool()
    result = tool.execute("setup existing project", cwd=cwd)
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        if result.get("suggestion"):
            click.echo(f"Suggestion: {result.get('suggestion')}")
        return
    
    click.echo(result.get("message", "Project setup completed"))
    
    # Show created files
    files_created = result.get("files_created", [])
    if files_created:
        click.echo(f"\nFiles created/updated:")
        for file in files_created:
            click.echo(f"  + {file}")
    
    # Show suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        click.echo(f"\nRecommended next steps:")
        for suggestion in suggestions:
            click.echo(f"  - {suggestion}")


@project.command()
def types():
    """List available project types and examples."""
    tool = ProjectScaffoldingTool()
    result = tool.execute("list project types")
    
    if not result.get("success"):
        click.echo(f"Error: {result.get('error')}", err=True)
        return
    
    click.echo("Available Project Types")
    click.echo("=" * 50)
    
    available_types = result.get("available_types", [])
    for project_type in available_types:
        click.echo(f"  {project_type}")
    
    click.echo(f"\nExamples:")
    examples = result.get("examples", [])
    for example in examples:
        click.echo(f"  {example}")


@project.command()
@click.argument('template_name')
@click.argument('project_name')
@click.option('--cwd', default='.', help='Directory to create project in')
def create(template_name: str, project_name: str, cwd: str):
    """Create a project from a specific template.
    
    TEMPLATE_NAME: Template to use (python, fastapi, node, etc.)
    PROJECT_NAME: Name of the project to create
    """
    # This is an alias for the init command
    ctx = click.get_current_context()
    ctx.invoke(init, project_type=template_name, project_name=project_name, cwd=cwd)


@project.command()
@click.option('--cwd', default='.', help='Working directory')
def info(cwd: str):
    """Show information about the current project."""
    cwd = os.path.abspath(cwd)
    
    if not os.path.exists(cwd):
        click.echo(f"Error: Directory '{cwd}' does not exist", err=True)
        return
    
    # Detect project type and show information
    project_files = {
        "Python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
        "Node.js": ["package.json"],
        "Git": [".git"]
    }
    
    detected_types = []
    for project_type, files in project_files.items():
        for file in files:
            if os.path.exists(os.path.join(cwd, file)):
                detected_types.append(project_type)
                break
    
    click.echo(f"Project Information")
    click.echo("=" * 50)
    click.echo(f"Directory: {cwd}")
    
    if detected_types:
        click.echo(f"Detected types: {', '.join(detected_types)}")
    else:
        click.echo("No known project types detected")
    
    # Show directory contents
    try:
        contents = os.listdir(cwd)
        important_files = [f for f in contents if f in [
            "README.md", "requirements.txt", "package.json", "setup.py", 
            "pyproject.toml", ".gitignore", "Makefile", ".git"
        ]]
        
        if important_files:
            click.echo(f"\nImportant files found:")
            for file in important_files:
                click.echo(f"  + {file}")
        
        # Count files and directories
        files = [f for f in contents if os.path.isfile(os.path.join(cwd, f))]
        dirs = [f for f in contents if os.path.isdir(os.path.join(cwd, f)) and not f.startswith('.')]
        
        click.echo(f"\nDirectory structure:")
        click.echo(f"  Files: {len(files)}")
        click.echo(f"  Directories: {len(dirs)}")
        
    except PermissionError:
        click.echo("\nUse 'metis project info' from within a project directory to see more details.")


@project.command()
@click.argument('description')
@click.option('--name', '-n', type=str, help='Project name (auto-generated if not provided)')
@click.option('--dir', '-d', type=str, help='Directory to create project in (default: current directory)')
@click.option('--no-git', is_flag=True, help='Skip git repository initialization')
def generate(description: str, name: str = None, dir: str = None, no_git: bool = False):
    """Generate any type of project from natural language description.
    
    Examples:
        metis project generate "FastAPI backend with PostgreSQL and authentication"
        metis project generate "React frontend with TypeScript and Tailwind CSS"
        metis project generate "Python data analysis project with Jupyter notebooks"
        metis project generate "Discord bot with slash commands" --name my-bot
    """
    
    # Set working directory
    work_dir = os.path.abspath(dir) if dir else os.getcwd()
    
    if not os.path.exists(work_dir):
        click.echo(f"Error: Directory '{work_dir}' does not exist", err=True)
        return
        
    click.echo(click.style(f"[PROJECT GENERATION] Creating project from description...", fg="cyan", bold=True))
    click.echo(f"Description: {description}")
    click.echo(f"Location: {work_dir}")
    
    # Initialize the agent
    agent = SingleAgent()
    
    # Generate project name if not provided
    if not name:
        click.echo(click.style("[ANALYZING] Generating project name from description...", fg="yellow"))
        name_prompt = f"""Based on this project description: "{description}"
        
Generate a good project name that is:
        - Descriptive and clear
        - Uses kebab-case (lowercase with hyphens)
        - Professional and appropriate
        - Maximum 30 characters
        
Just respond with the project name only, no explanation."""
        
        name_response = agent.process_query(name_prompt)
        # Extract just the name from response
        import re
        name_match = re.search(r'([a-z0-9-]+)', name_response.lower())
        if name_match:
            name = name_match.group(1)
        else:
            name = "generated-project"
            
        click.echo(f"Generated name: {name}")
    
    # Create project directory
    project_path = os.path.join(work_dir, name)
    if os.path.exists(project_path):
        if not click.confirm(f"Directory '{name}' already exists. Continue?"):
            return
    else:
        os.makedirs(project_path, exist_ok=True)
    
    # Generate the project using the agent
    click.echo(click.style("[GENERATING] Agent creating project structure and files...", fg="green", bold=True))
    
    generation_prompt = f"""I need you to create a complete project based on this description: "{description}"
    
Project Requirements:
    - Project name: {name}
    - Location: {project_path}
    - Create all necessary files and directories
    - Include proper project structure and best practices
    - Add configuration files, dependencies, and documentation
    - Create example/starter code where appropriate
    
    IMPORTANT: You MUST use the FileSystemTool to actually create all files and directories.
    Do not just describe what should be created - actually create the files!
    
    Use write_file() calls to create each file with its content.
    Use create_directory() calls to create the directory structure.
    
    Focus on:
    1. Creating the proper directory structure
    2. Adding all necessary configuration files (package.json, requirements.txt, etc.)
    3. Creating starter/example code
    4. Adding a comprehensive README.md
    5. Including appropriate .gitignore
    6. Setting up any build/development scripts
    
    Current working directory is: {project_path}
    
    Please start by creating the directory structure, then create each file with proper content.
    """
    
    # Set the agent's working directory to the project path
    os.chdir(project_path)
    
    result = agent.process_query(generation_prompt)
    
    click.echo(click.style("[AGENT RESPONSE]", fg="blue", bold=True))
    click.echo(result)
    
    # Also directly create essential files if agent didn't create them
    essential_files = {
        'README.md': f"# {name}\n\n{description}\n\n## Getting Started\n\n1. Clone the repository\n2. Install dependencies\n3. Run the application\n",
        '.gitignore': "*.pyc\n__pycache__/\n.env\nnode_modules/\n.DS_Store\n",
    }
    
    for filename, content in essential_files.items():
        filepath = os.path.join(project_path, filename)
        if not os.path.exists(filepath):
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                click.echo(f"[CREATED] {filename}")
            except Exception as e:
                click.echo(f"[ERROR] Could not create {filename}: {e}")
    
    # Initialize git repository by default
    if not no_git:
        click.echo(click.style("\n[GIT] Initializing repository...", fg="magenta"))
        
        try:
            import subprocess
            
            # Initialize git repo with proper master branch setup
            result = subprocess.run(["git", "init"], cwd=project_path, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                click.echo(click.style("[GIT] Repository initialized", fg="green"))
                
                # Set up initial branch as master (ensuring compatibility)
                subprocess.run(["git", "config", "init.defaultBranch", "master"], cwd=project_path, capture_output=True, timeout=10)
                
                # Add all generated files
                subprocess.run(["git", "add", "."], cwd=project_path, capture_output=True, timeout=10)
                
                # Create initial commit on master
                commit_result = subprocess.run(
                    ["git", "commit", "-m", f"Initial project setup: {description}"],
                    cwd=project_path, capture_output=True, text=True, timeout=10
                )
                
                if commit_result.returncode == 0:
                    click.echo(click.style("[GIT] Initial commit created on master branch", fg="green"))
                    
                    # Verify current branch
                    branch_result = subprocess.run(["git", "branch", "--show-current"], cwd=project_path, capture_output=True, text=True, timeout=10)
                    if branch_result.returncode == 0 and branch_result.stdout.strip():
                        current_branch = branch_result.stdout.strip()
                        click.echo(click.style(f"[GIT] Ready on '{current_branch}' branch", fg="cyan"))
                else:
                    click.echo(click.style("[GIT] Warning: Could not create initial commit", fg="yellow"))
            else:
                click.echo(click.style(f"[GIT] Warning: Repository initialization failed", fg="yellow"))
                
        except Exception as e:
            click.echo(click.style(f"[GIT] Warning: Git setup failed: {str(e)}", fg="yellow"))
    
    click.echo(click.style(f"\n[COMPLETE] Project '{name}' generated successfully!", fg="green", bold=True))
    click.echo(f"Location: {project_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {name}")
    if not no_git:
        click.echo(f"  # Git repository ready for development")
        click.echo(f"  # Create feature branches with: metis code generate '<description>'")
    else:
        click.echo(f"  git init  # Initialize git repository if needed")
    click.echo(f"  # Start developing!")


# Add commands to the main CLI
def add_project_commands(cli):
    """Add project commands to the main CLI."""
    cli.add_command(project)
