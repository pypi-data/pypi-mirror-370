"""
Natural language coding assistant - like Claude Code.

This module provides a single natural language interface for all coding tasks:
- Project creation and management
- Code generation and analysis
- Session management and phase transitions
"""
import click
import json
import os
from pathlib import Path
from ..core.agent import SingleAgent
from ..core.agent_config import AgentConfig


@click.command()
@click.argument('request', nargs=-1, required=False)
def code(request):
    """Natural language coding assistant - like Claude Code."""
    
    # Initialize agent with config settings
    config = AgentConfig()
    agent = SingleAgent(
        use_titans_memory=config.is_titans_memory_enabled(),
        llm_provider=config.get_llm_provider(),
        llm_model=config.get_llm_model(),
        enhanced_processing=True,
        config=config
    )
    
    # Handle natural language request
    if request:
        request_text = ' '.join(request)
        return _handle_natural_language_coding_request(agent, request_text)
    else:
        # No request provided - check for project context or show help
        project_info = _detect_project_directory()
        if project_info:
            _show_project_session_status(project_info)
        else:
            click.echo("Metis Code - Natural Language Coding Assistant")
            click.echo("Usage: metis code 'describe what you want to build or do'")
            click.echo("")
            click.echo("Examples:")
            click.echo("  metis code 'create a todo app with React and Node.js'")
            click.echo("  metis code 'show project status'")
            click.echo("  metis code 'move to next phase'")
            click.echo("  metis code 'start new iteration'")
            click.echo("  metis code 'analyze this codebase'")
            click.echo("  metis code 'generate a Python function to sort a list'")


def _handle_natural_language_coding_request(agent, request_text):
    """Handle natural language coding requests using the agent."""
    try:
        # Check if we're in a project context
        project_info = _detect_project_directory()
        project_context = ""
        
        if project_info:
            try:
                with open(project_info['session_file'], 'r') as f:
                    session_data = json.load(f)
                project_context = f"""
Current Project Context:
- Project: {session_data.get('project_name', 'Unknown')}
- Phase: {session_data.get('current_phase', 'Unknown')}
- Iteration: {session_data.get('current_iteration', 1)}
- Directory: {project_info['project_dir']}
"""
            except Exception:
                project_context = f"Project directory: {project_info['project_dir']}"
        
        # Enhance the request with coding context
        enhanced_request = f"""You are Metis Code, a natural language coding assistant similar to Claude Code.

User Request: "{request_text}"
{project_context}

Please analyze the user's intent and respond appropriately. Common intents include:

1. PROJECT CREATION: "create/build/make a new [type] project/app"
   - Create proper project structure with Metis/ directory
   - Generate planning documents (plan.md, tasks.md, design.md)
   - Initialize session.json with phases and iteration tracking
   - Create src/ directory for source code

2. PROJECT MANAGEMENT: "status/next phase/iterate/progress"
   - Show current project status and phase
   - Transition to next phase or start new iteration
   - Update session tracking

3. CODE GENERATION: "write/create/generate [specific code]"
   - Generate actual code files
   - Follow project patterns and context
   - Save to appropriate locations

4. CODE ANALYSIS: "analyze/review/examine [code/project]"
   - Analyze existing codebase
   - Provide insights and suggestions
   - Review code quality and structure

5. FILE OPERATIONS: "read/write/modify [files]"
   - Handle file system operations
   - Maintain project organization

Be conversational, helpful, and proactive. If you need clarification, ask questions.
Always provide concrete, actionable responses with actual file creation when appropriate.
"""
        
        # Get response from agent
        response = agent.process_query(enhanced_request)
        
        # Display the response
        if isinstance(response, dict):
            click.echo(response.get("response", str(response)))
        else:
            click.echo(response)
            
    except Exception as e:
        click.echo(f"Error processing request: {e}")


def _detect_project_directory():
    """Check if we're in a project directory by looking for Metis/session.json."""
    current_dir = Path(os.getcwd())
    
    # Check current directory and parents for Metis/session.json
    max_depth = 5  # Don't go up too many levels
    for _ in range(max_depth):
        session_file = current_dir / 'Metis' / 'session.json'
        if session_file.exists():
            return {
                'project_dir': current_dir,
                'session_file': session_file
            }
        
        # Move up one directory
        parent = current_dir.parent
        if parent == current_dir:  # Reached root
            break
        current_dir = parent
    
    return None


def _show_project_session_status(project_info):
    """Display project session status in a readable format."""
    try:
        with open(project_info['session_file'], 'r') as f:
            session_data = json.load(f)
        
        click.echo(f"Project: {session_data.get('project_name', 'Unknown')}")
        click.echo(f"Current phase: {session_data.get('current_phase', 'Unknown')}")
        click.echo(f"Current iteration: {session_data.get('current_iteration', 1)}")
        click.echo(f"Directory: {project_info['project_dir']}")
        
        # Show git info if available
        if 'git' in session_data:
            git_info = session_data['git']
            if git_info.get('initialized', False):
                click.echo(f"Git branch: {git_info.get('current_branch', 'Unknown')}")
        
        # Show phase information
        phases = session_data.get('phases', [])
        if phases:
            click.echo("\nPhases:")
            for phase in phases:
                if phase['name'] == session_data.get('current_phase'):
                    status = 'Current'
                elif phase.get('completed'):
                    status = 'Completed'
                else:
                    status = 'Pending'
                click.echo(f"  {phase['name']}: {status}")
        
        click.echo("\nTry: metis code 'move to next phase' or metis code 'start new iteration'")
    
    except Exception as e:
        click.echo(f"Error reading session file: {e}")


# Export the command
__all__ = ['code']
