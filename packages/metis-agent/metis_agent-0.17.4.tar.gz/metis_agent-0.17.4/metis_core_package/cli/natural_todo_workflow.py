"""
Natural TODO Workflow Integration
Seamlessly integrates TODO management into the natural language code workflow
"""

import click
from typing import Optional, Dict, Any, Tuple
from .enhanced_todo_integration import enhanced_todo_integration

# Try to import Rich for enhanced visuals
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


def process_natural_language_request_with_todos(
    agent, 
    request_text: str, 
    session: Optional[str] = None,
    **kwargs
) -> Optional[str]:
    """
    Enhanced natural language processing with seamless TODO integration.
    Returns response if TODO processing handles the request, None if should fall back to normal processing.
    """
    
    # Step 1: Check for active TODO session
    active_session = enhanced_todo_integration.check_active_todo_session()
    
    if active_session:
        return _handle_todo_aware_request(agent, request_text, active_session, session, **kwargs)
    
    # Step 2: Analyze request complexity 
    complexity_analysis = enhanced_todo_integration.analyze_request_complexity(request_text)
    
    if complexity_analysis.should_create_todos:
        return _handle_complex_project_request(agent, request_text, complexity_analysis, session, **kwargs)
    
    # Step 3: Return None to indicate normal processing should continue
    return None


def check_and_display_todo_context(request_text: str) -> Optional[str]:
    """
    Check for TODO context and display it, but don't process the request.
    Returns context info if TODO context exists, None otherwise.
    """
    active_session = enhanced_todo_integration.check_active_todo_session()
    
    if active_session:
        related_task = enhanced_todo_integration.find_related_task(request_text, active_session)
        _display_todo_context(active_session, related_task, request_text)
        return f"TODO context: {active_session.get('name', 'Active Project')}"
    
    return None


def analyze_and_maybe_create_todos(request_text: str) -> Optional[str]:
    """
    Analyze request and create TODOs if needed, but don't process the request.
    Returns TODO creation result if TODOs were created, None otherwise.
    """
    complexity_analysis = enhanced_todo_integration.analyze_request_complexity(request_text)
    
    if complexity_analysis.should_create_todos:
        _display_complexity_analysis(complexity_analysis, request_text)
        
        todo_creation_result = enhanced_todo_integration.create_smart_todo_session(request_text, complexity_analysis)
        
        if todo_creation_result:
            _display_project_planning_result(todo_creation_result)
            return todo_creation_result
    
    return None


def _handle_todo_aware_request(
    agent, 
    request_text: str, 
    active_session: Dict[str, Any], 
    session: Optional[str] = None,
    **kwargs
) -> str:
    """
    Process request in context of active TODO session
    """
    # Find related task
    related_task = enhanced_todo_integration.find_related_task(request_text, active_session)
    
    # Show TODO context
    _display_todo_context(active_session, related_task, request_text)
    
    # Create enhanced request with TODO context
    enhanced_request = _create_todo_aware_prompt(request_text, active_session, related_task)
    
    # Process the request
    response = agent.process_query(enhanced_request, session_id=session)
    
    # Update task progress automatically
    if related_task:
        task_updated = enhanced_todo_integration.update_task_progress_from_response(related_task, response)
        if task_updated:
            _show_task_progress_update(related_task)
    
    # Show next task suggestion
    _show_next_task_suggestion(active_session)
    
    return response


def _handle_complex_project_request(
    agent, 
    request_text: str, 
    complexity_analysis, 
    session: Optional[str] = None,
    **kwargs
) -> str:
    """
    Handle complex requests that need TODO breakdown
    """
    # Show complexity analysis
    _display_complexity_analysis(complexity_analysis, request_text)
    
    # Create TODO session and breakdown
    todo_creation_result = enhanced_todo_integration.create_smart_todo_session(request_text, complexity_analysis)
    
    if todo_creation_result:
        _display_project_planning_result(todo_creation_result)
        
        # Process the first task
        first_task_prompt = _create_first_task_prompt(request_text, complexity_analysis)
        response = agent.process_query(first_task_prompt, session_id=session)
        
        # Show completion of first phase
        _show_first_task_completion()
        
        return response
    else:
        # Fallback to regular processing if TODO creation fails
        return _handle_simple_request(agent, request_text, session, **kwargs)


def _handle_simple_request(
    agent, 
    request_text: str, 
    session: Optional[str] = None,
    **kwargs
) -> str:
    """
    Handle simple requests that don't need TODO breakdown
    """
    return agent.process_query(request_text, session_id=session)


def _display_todo_context(active_session: Dict[str, Any], related_task: Optional[Dict[str, Any]], request_text: str):
    """Display current TODO context to user"""
    if RICH_AVAILABLE:
        console = Console()
        
        # Create context table
        context_table = Table.grid()
        context_table.add_row(f"[bold]Project:[/bold] [cyan]{active_session.get('name', 'Active Project')}[/cyan]")
        
        if related_task:
            context_table.add_row(f"[bold]Current Task:[/bold] [yellow]{related_task['title']}[/yellow]")
            context_table.add_row(f"[bold]Status:[/bold] [green]{related_task['status']}[/green]")
        else:
            context_table.add_row(f"[bold]Mode:[/bold] [yellow]General development[/yellow]")
        
        console.print(Panel(context_table, title="TODO Context", border_style="cyan"))
    else:
        click.echo(f"Working on: {active_session.get('name', 'Active Project')}")
        if related_task:
            click.echo(f"Current task: {related_task['title']} ({related_task['status']})")
        click.echo("=" * 50)


def _display_complexity_analysis(complexity_analysis, request_text: str):
    """Display complexity analysis to user"""
    if RICH_AVAILABLE:
        console = Console()
        
        # Create analysis table
        analysis_table = Table.grid()
        analysis_table.add_row(f"[bold]Request:[/bold] [white]{request_text}[/white]")
        analysis_table.add_row(f"[bold]Project Type:[/bold] [cyan]{complexity_analysis.project_type.replace('_', ' ').title()}[/cyan]")
        analysis_table.add_row(f"[bold]Complexity:[/bold] [yellow]{complexity_analysis.complexity_score:.1f}/5[/yellow]")
        analysis_table.add_row(f"[bold]Estimated Duration:[/bold] [green]{complexity_analysis.estimated_duration_hours:.1f} hours[/green]")
        
        if complexity_analysis.key_components:
            components = ", ".join(complexity_analysis.key_components[:3])
            analysis_table.add_row(f"[bold]Key Components:[/bold] [magenta]{components}[/magenta]")
        
        console.print(Panel(analysis_table, title="AI Analysis", border_style="blue"))
        console.print(f"{complexity_analysis.reasoning}\n")
    else:
        click.echo(f"Analyzing: {request_text}")
        click.echo(f"Project type: {complexity_analysis.project_type.replace('_', ' ').title()}")
        click.echo(f"Estimated duration: {complexity_analysis.estimated_duration_hours:.1f} hours")
        click.echo(f"Complexity score: {complexity_analysis.complexity_score:.1f}/5")
        click.echo("=" * 50)


def _display_project_planning_result(todo_creation_result: str):
    """Display the project planning result"""
    if RICH_AVAILABLE:
        console = Console()
        
        # Split the result into parts for better formatting
        lines = todo_creation_result.split('\n')
        
        # Find the breakdown section
        breakdown_lines = []
        in_breakdown = False
        
        for line in lines:
            if 'Breakdown for' in line:
                in_breakdown = True
            if in_breakdown:
                breakdown_lines.append(line)
        
        if breakdown_lines:
            breakdown_text = '\n'.join(breakdown_lines)
            console.print(Panel(breakdown_text, title="Project Plan", border_style="green"))
        else:
            console.print(todo_creation_result)
    else:
        click.echo(todo_creation_result)
        click.echo("=" * 50)


def _create_todo_aware_prompt(request_text: str, active_session: Dict[str, Any], related_task: Optional[Dict[str, Any]]) -> str:
    """Create an enhanced prompt with TODO context"""
    context_parts = [
        f"Project Context: I'm working on '{active_session.get('name', 'Active Project')}'",
    ]
    
    if related_task:
        context_parts.extend([
            f"Current Task: {related_task['title']}",
            f"Task Status: {related_task['status']}",
            "This request relates to the current task."
        ])
    else:
        context_parts.append("This is general development work for the project.")
    
    context_parts.extend([
        "",
        f"User Request: {request_text}",
        "",
        "Please execute this request keeping the project context in mind.",
        "If this completes or significantly advances any project tasks, mention that in your response.",
        "Focus on delivering working, complete solutions."
    ])
    
    return "\n".join(context_parts)


def _create_first_task_prompt(request_text: str, complexity_analysis) -> str:
    """Create prompt for executing the first task of a project"""
    return f"""
Project Planning Complete! Starting development.

Original Request: {request_text}
Project Type: {complexity_analysis.project_type.replace('_', ' ').title()}
Estimated Duration: {complexity_analysis.estimated_duration_hours:.1f} hours

I've broken this down into manageable tasks. Let's start with the first phase:

{request_text}

Please begin by setting up the project foundation. Focus on:
1. Project structure and initial setup
2. Core configuration files
3. Basic framework/dependencies
4. Initial code structure

Provide working, complete solutions that I can build upon.
"""


def _show_task_progress_update(related_task: Dict[str, Any]):
    """Show task progress update"""
    if RICH_AVAILABLE:
        console = Console()
        console.print(f"[green]Task Progress Updated:[/green] [yellow]{related_task['title']}[/yellow]")
    else:
        click.echo(f"Task updated: {related_task['title']}")


def _show_next_task_suggestion(active_session: Dict[str, Any]):
    """Show suggestion for next task"""
    next_suggestion = enhanced_todo_integration.get_next_task_suggestion(active_session)
    if next_suggestion:
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"\n{next_suggestion}")
        else:
            click.echo(f"\n{next_suggestion}")


def _show_first_task_completion():
    """Show completion of first task phase"""
    if RICH_AVAILABLE:
        console = Console()
        console.print("\n[green]Project foundation established![/green]")
        console.print("Ready for next development phase. Use 'metis todo next' to see upcoming tasks.")
    else:
        click.echo("\nProject foundation established!")
        click.echo("Ready for next development phase. Use 'metis todo next' to see upcoming tasks.")


def get_todo_progress_summary() -> Optional[str]:
    """Get current TODO progress summary"""
    active_session = enhanced_todo_integration.check_active_todo_session()
    if active_session:
        return enhanced_todo_integration.get_progress_summary(active_session)
    return None


def has_active_todo_session() -> bool:
    """Check if there's an active TODO session"""
    return enhanced_todo_integration.check_active_todo_session() is not None


def enhance_request_with_todo_context(request_text: str) -> str:
    """Enhance request with TODO context if active session exists"""
    active_session = enhanced_todo_integration.check_active_todo_session()
    
    if active_session:
        related_task = enhanced_todo_integration.find_related_task(request_text, active_session)
        
        if related_task:
            return f"""
Project Context: Working on '{active_session.get('name', 'Active Project')}'
Current Task: {related_task['title']} (Status: {related_task['status']})

User Request: {request_text}

Please execute this request keeping the project and task context in mind.
If this completes or advances the current task, mention that in your response.
"""
        else:
            return f"""
Project Context: Working on '{active_session.get('name', 'Active Project')}'
Mode: General development for the project

User Request: {request_text}

Please execute this request keeping the project context in mind.
"""
    
    return request_text


def update_todo_progress_after_response(request_text: str, response: str) -> None:
    """Update TODO progress after agent response"""
    active_session = enhanced_todo_integration.check_active_todo_session()
    
    if active_session:
        related_task = enhanced_todo_integration.find_related_task(request_text, active_session)
        
        if related_task:
            task_updated = enhanced_todo_integration.update_task_progress_from_response(related_task, response)
            if task_updated:
                _show_task_progress_update(related_task)
                _show_next_task_suggestion(active_session)