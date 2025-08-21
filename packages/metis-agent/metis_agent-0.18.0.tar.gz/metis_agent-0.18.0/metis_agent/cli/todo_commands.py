#!/usr/bin/env python3
"""
TODO Checklist CLI Commands for Metis Code
Provides command-line interface for comprehensive task management.
"""

import click
import json
from pathlib import Path
from typing import Optional
from ..tools.core_tools.todo_management_tool import TodoManagementTool, TaskStatus, TaskPriority


class TodoCLI:
    """CLI interface for TODO management"""
    
    def __init__(self):
        self.tool = TodoManagementTool()
    
    def format_output(self, result: dict) -> str:
        """Format tool output for CLI display"""
        if not result.get('success'):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        # Show visual output if available
        if 'visual_output' in result:
            output = result['visual_output']
            if result.get('message'):
                output = f"{result['message']}\n\n{output}"
            return output
        
        # Default to message
        return result.get('message', 'Operation completed')
    
    def handle_command(self, command: str, **kwargs) -> str:
        """Handle TODO command and return formatted output"""
        try:
            result = self.tool.execute(command, **kwargs)
            return self.format_output(result)
        except Exception as e:
            return f"Error: {str(e)}"


# Create CLI instance
todo_cli = TodoCLI()


@click.group(name='todo')
@click.pass_context
def todo_group(ctx):
    """TODO checklist management for complex tasks"""
    if ctx.obj is None:
        ctx.obj = {}


@todo_group.command()
@click.argument('name')
@click.option('--description', '-d', help='Session description')
def create(name: str, description: Optional[str]):
    """Create a new TODO session"""
    result = todo_cli.handle_command(
        'create session',
        name=name,
        description=description or ''
    )
    click.echo(result)


@todo_group.command()
def sessions():
    """List all TODO sessions"""
    result = todo_cli.handle_command('list sessions')
    click.echo(result)


@todo_group.command()
@click.argument('session_id')
def load(session_id: str):
    """Load an existing TODO session"""
    result = todo_cli.handle_command('load session', session_id=session_id)
    click.echo(result)


@todo_group.command()
@click.argument('request')
def breakdown(request: str):
    """Automatically break down a request into tasks"""
    result = todo_cli.handle_command('breakdown request', request=request)
    click.echo(result)


@todo_group.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--priority', '-p', 
              type=click.Choice(['low', 'medium', 'high', 'critical']),
              default='medium', help='Task priority')
@click.option('--effort', '-e', type=int, help='Estimated effort in minutes')
def add(title: str, description: Optional[str], priority: str, effort: Optional[int]):
    """Add a new task to current session"""
    result = todo_cli.handle_command(
        'add task',
        title=title,
        description=description or '',
        priority=TaskPriority(priority),
        estimated_effort=effort
    )
    click.echo(result)


@todo_group.command()
@click.option('--status', '-s', 
              type=click.Choice(['pending', 'in_progress', 'completed', 'failed']),
              help='Filter by task status')
def list(status: Optional[str]):
    """List tasks in current session"""
    kwargs = {}
    if status:
        kwargs['status'] = status
    
    result = todo_cli.handle_command('list tasks', **kwargs)
    click.echo(result)


@todo_group.command()
@click.argument('task_id')
@click.argument('status', type=click.Choice(['pending', 'in_progress', 'completed', 'failed', 'blocked', 'cancelled']))
def update(task_id: str, status: str):
    """Update task status"""
    result = todo_cli.handle_command(
        'update task',
        task_id=task_id,
        status=status
    )
    click.echo(result)


@todo_group.command()
@click.argument('task_id')
def complete(task_id: str):
    """Mark task as completed"""
    result = todo_cli.handle_command(
        'update task',
        task_id=task_id,
        status='completed'
    )
    click.echo(result)


@todo_group.command()
def next():
    """Get suggested next task to work on"""
    result = todo_cli.handle_command('next task')
    click.echo(result)


@todo_group.command()
def progress():
    """Show progress summary and next actions"""
    result = todo_cli.handle_command('progress')
    click.echo(result)


@todo_group.command()
def help():
    """Show detailed help for TODO commands"""
    result = todo_cli.handle_command('help')
    click.echo(result)


# Convenience commands for common workflows
@todo_group.command()
@click.argument('project_request')
def start(project_request: str):
    """Quick start: create session and breakdown request"""
    # Extract project name from request
    project_name = project_request.split()[0:3]  # First 3 words
    session_name = ' '.join(project_name).title()
    
    # Create session
    session_result = todo_cli.handle_command(
        'create session',
        name=session_name,
        description=f"Auto-generated from: {project_request}"
    )
    click.echo(session_result)
    
    # Breakdown request
    if 'success' in session_result.lower():
        click.echo("\nBreaking down request into tasks...\n")
        breakdown_result = todo_cli.handle_command(
            'breakdown request',
            request=project_request
        )
        click.echo(breakdown_result)


@todo_group.command()
def status():
    """Show current session status and ready tasks"""
    # Show progress
    progress_result = todo_cli.handle_command('progress')
    click.echo(progress_result)
    
    click.echo("\n" + "="*50)
    
    # Show next task
    next_result = todo_cli.handle_command('next task')
    if 'No tasks ready' not in next_result:
        click.echo("\n" + next_result)


# Integration with existing metis commands
def integrate_with_code_command():
    """Integration point for metis code commands"""
    # This function can be called by other CLI modules
    # to automatically create TODO breakdowns for complex requests
    pass


def auto_create_todos_for_request(request: str) -> Optional[str]:
    """
    Automatically create TODOs for complex requests.
    Returns session info if TODOs were created, None otherwise.
    """
    # Check if request is complex enough to warrant TODO breakdown
    complexity_indicators = [
        'create', 'build', 'develop', 'implement', 'design',
        'full stack', 'application', 'system', 'project',
        'api', 'frontend', 'backend', 'database'
    ]
    
    request_lower = request.lower()
    complexity_score = sum(1 for indicator in complexity_indicators if indicator in request_lower)
    
    if complexity_score >= 2:  # Threshold for auto-TODO creation
        try:
            # Create session with auto-generated name
            session_name = f"Auto: {' '.join(request.split()[:4])}"
            session_result = todo_cli.handle_command(
                'create session',
                name=session_name,
                description=f"Auto-generated from request: {request}"
            )
            
            if 'Created TODO session' in session_result:
                # Breakdown the request
                breakdown_result = todo_cli.handle_command(
                    'breakdown request',
                    request=request
                )
                
                return f"""
Automatically created TODO breakdown for your request:

{session_result}

{breakdown_result}

Use 'metis todo status' to see progress and next actions.
Use 'metis todo next' to get the next recommended task.
"""
        except Exception:
            pass
    
    return None


if __name__ == '__main__':
    todo_group()