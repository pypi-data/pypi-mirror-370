"""
Natural Language CLI commands for code intelligence features.

This module provides a unified natural language interface that routes all coding tasks
through the SingleAgent instead of using multiple subcommands.
"""
import click
import glob
import os
import re
import subprocess
import random
import string
import time
from pathlib import Path
from datetime import datetime

# Try to import Rich for enhanced visuals, fallback to basic if not available
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    Panel = None
from ..core.agent import SingleAgent
from ..core.smart_orchestrator import SmartOrchestrator
from ..core.agent_config import AgentConfig

# Collaboration functions for multi-agent support
def _parse_mentions(text: str) -> tuple[str, list[str]]:
    """Parse @mentions from text and return cleaned text and list of mentioned agents."""
    import re
    
    # Find all @mentions in the text
    mentions = re.findall(r'@([a-zA-Z0-9_-]+)', text)
    
    # Handle @everyone special case
    if 'everyone' in mentions:
        # Get all available agents
        try:
            from .agent_commands import get_agent_manager
            agent_manager = get_agent_manager()
            if agent_manager:
                all_agents = agent_manager.list_agents()
                # Replace 'everyone' with all available agents
                mentions = [agent for agent in mentions if agent != 'everyone']
                mentions.extend(all_agents)
                # Remove duplicates while preserving order
                mentions = list(dict.fromkeys(mentions))
        except Exception:
            # If agent manager not available, fall back to removing 'everyone'
            mentions = [agent for agent in mentions if agent != 'everyone']
    
    # Remove @mentions from the text to get the clean query
    clean_text = re.sub(r'@[a-zA-Z0-9_-]+\s*', '', text).strip()
    
    return clean_text, mentions

def _process_multi_agent_query(mentioned_agents: list[str], query: str, agent_manager, session_id: str) -> list[tuple[str, str]]:
    """Process query with advanced multi-agent collaboration and cross-response awareness."""
    if len(mentioned_agents) == 1:
        # Single agent - use simple processing
        return _process_single_agent_response(mentioned_agents[0], query, agent_manager, session_id)
    
    # Multi-agent collaborative processing
    return _process_collaborative_discussion(mentioned_agents, query, agent_manager, session_id)

def _process_single_agent_response(agent_id: str, query: str, agent_manager, session_id: str) -> list[tuple[str, str]]:
    """Process query with a single agent."""
    try:
        agent = agent_manager.get_agent(agent_id)
        if agent:
            response = agent.process_query(query, session_id=session_id)
            response_text = response.get("response", str(response)) if isinstance(response, dict) else str(response)
            return [(agent_id, response_text)]
        else:
            return [(agent_id, f"Agent '{agent_id}' not found")]
    except Exception as e:
        return [(agent_id, f"Error from agent '{agent_id}': {e}")]

def _process_collaborative_discussion(mentioned_agents: list[str], query: str, agent_manager, session_id: str) -> list[tuple[str, str]]:
    """Advanced collaborative processing with cross-agent awareness and iterative refinement."""
    conversation_context = {
        'original_query': query,
        'participants': mentioned_agents,
        'responses': [],
        'round': 0
    }
    
    max_rounds = min(3, len(mentioned_agents))  # Scale rounds with agent count, max 3
    all_responses = []
    
    for round_num in range(max_rounds):
        conversation_context['round'] = round_num
        round_responses = []
        
        for agent_id in mentioned_agents:
            try:
                agent = agent_manager.get_agent(agent_id)
                if not agent:
                    round_responses.append((agent_id, f"Agent '{agent_id}' not found"))
                    continue
                
                # Build contextual query with previous responses
                contextual_query = _build_collaborative_context(agent_id, conversation_context)
                
                response = agent.process_query(contextual_query, session_id=session_id)
                response_text = response.get("response", str(response)) if isinstance(response, dict) else str(response)
                
                # Add response to context for next agents
                response_entry = {
                    'agent_id': agent_id,
                    'response': response_text,
                    'round': round_num
                }
                conversation_context['responses'].append(response_entry)
                round_responses.append((agent_id, response_text))
                
            except Exception as e:
                error_msg = f"Error from agent '{agent_id}': {e}"
                round_responses.append((agent_id, error_msg))
                conversation_context['responses'].append({
                    'agent_id': agent_id,
                    'response': error_msg,
                    'round': round_num
                })
        
        all_responses.extend(round_responses)
        
        # Determine if we need another round
        if round_num == 0 and len(mentioned_agents) >= 2:
            # Always do at least 2 rounds for 2+ agents to enable collaboration
            continue
        elif round_num >= 1:
            # Stop after round 2 to prevent infinite loops
            break
    
    return all_responses

def _build_collaborative_context(current_agent_id: str, conversation_context: dict) -> str:
    """Build contextual query including previous agent responses."""
    original_query = conversation_context['original_query']
    participants = conversation_context['participants']
    previous_responses = conversation_context['responses']
    round_num = conversation_context['round']
    
    other_agents = [agent for agent in participants if agent != current_agent_id]
    
    if round_num == 0:
        # First round - introduce collaboration
        context = f"""You are participating in a collaborative multi-agent discussion with the following agents: {', '.join(other_agents)}.

Query: {original_query}

This is the first round of discussion. Please provide your initial perspective, knowing that other agents will build on your response in subsequent rounds."""
    else:
        # Subsequent rounds - include previous responses
        context = f"""You are participating in a collaborative multi-agent discussion with the following agents: {', '.join(other_agents)}.

Original query: {original_query}

Previous responses from collaborating agents:

"""
        
        current_round_responses = [r for r in previous_responses if r['round'] == round_num - 1]
        other_responses = [r for r in current_round_responses if r['agent_id'] != current_agent_id]
        
        for response_entry in other_responses:
            context += f"--- {response_entry['agent_id']} ---\n"
            context += f"{response_entry['response']}\n\n"
        
        context += f"Now provide your perspective, building on or responding to the above insights:\n"
        context += f"Query: {original_query}"
    
    return context

def _display_multi_agent_responses(responses: list[tuple[str, str]], agent_manager):
    """Display responses from multiple agents with collaborative discussion flow."""
    if not responses:
        return
    
    # Determine if this is a collaborative discussion (multiple rounds)
    unique_agents = list(set(agent_id for agent_id, _ in responses))
    is_collaborative = len(responses) > len(unique_agents) or len(unique_agents) >= 2
    
    if RICH_AVAILABLE:
        console = Console()
        
        if is_collaborative:
            _display_collaborative_discussion_rich(responses, agent_manager, console)
        else:
            _display_standard_responses_rich(responses, agent_manager, console)
    else:
        if is_collaborative:
            _display_collaborative_discussion_plain(responses, agent_manager)
        else:
            _display_standard_responses_plain(responses, agent_manager)

def _display_collaborative_discussion_rich(responses: list[tuple[str, str]], agent_manager, console):
    """Display collaborative discussion with round indicators (Rich version)."""
    unique_agents = list(set(agent_id for agent_id, _ in responses))
    agents_per_round = len(unique_agents)
    
    current_round = 0
    response_index = 0
    
    while response_index < len(responses):
        # Round header
        if current_round == 0:
            console.print(f"\n[bold blue]Initial Expert Perspectives[/bold blue]", style="bold")
        else:
            console.print(f"\n[bold blue]Collaborative Round {current_round + 1} - Building on Previous Insights[/bold blue]", style="bold")
        
        console.print("─" * 60, style="dim")
        
        # Display agents for this round
        round_end = min(response_index + agents_per_round, len(responses))
        
        for i in range(response_index, round_end):
            agent_id, response_text = responses[i]
            
            try:
                agent_info = agent_manager.get_agent_info(agent_id)
                profile_name = agent_info.get('profile_name', 'unknown') if agent_info else 'unknown'
                agent_display_name = f"{agent_id} ({profile_name})"
            except:
                agent_display_name = agent_id
            
            # Different styles for different rounds
            if current_round == 0:
                border_style = "cyan"
                title_style = "bold cyan"
            else:
                border_style = "green"
                title_style = "bold green"
            
            panel = Panel(
                response_text,
                title=f"[{title_style}]Agent {agent_display_name}[/{title_style}]",
                border_style=border_style,
                padding=(0, 1)
            )
            console.print(panel)
        
        response_index = round_end
        current_round += 1
        
        if response_index < len(responses):
            console.print()

def _display_standard_responses_rich(responses: list[tuple[str, str]], agent_manager, console):
    """Display standard multi-agent responses (Rich version)."""
    for agent_id, response_text in responses:
        try:
            agent_info = agent_manager.get_agent_info(agent_id)
            profile_name = agent_info.get('profile_name', 'unknown') if agent_info else 'unknown'
            agent_display_name = f"{agent_id} ({profile_name})"
        except:
            agent_display_name = agent_id
        
        panel = Panel(
            response_text,
            title=f"[bold cyan]Agent {agent_display_name}[/bold cyan]",
            border_style="cyan",
            padding=(0, 1)
        )
        console.print(panel)
        console.print()

def _display_collaborative_discussion_plain(responses: list[tuple[str, str]], agent_manager):
    """Display collaborative discussion with round indicators (Plain version)."""
    unique_agents = list(set(agent_id for agent_id, _ in responses))
    agents_per_round = len(unique_agents)
    
    current_round = 0
    response_index = 0
    
    while response_index < len(responses):
        # Round header
        if current_round == 0:
            click.echo("\n=== Initial Expert Perspectives ===")
        else:
            click.echo(f"\n=== Collaborative Round {current_round + 1} - Building on Previous Insights ===")
        
        click.echo("-" * 60)
        
        # Display agents for this round
        round_end = min(response_index + agents_per_round, len(responses))
        
        for i in range(response_index, round_end):
            agent_id, response_text = responses[i]
            
            try:
                agent_info = agent_manager.get_agent_info(agent_id)
                profile_name = agent_info.get('profile_name', 'unknown') if agent_info else 'unknown'
                agent_display_name = f"{agent_id} ({profile_name})"
            except:
                agent_display_name = agent_id
            
            click.echo(f"\n--- Agent {agent_display_name} ---")
            click.echo(response_text)
            click.echo()
        
        response_index = round_end
        current_round += 1

def _display_standard_responses_plain(responses: list[tuple[str, str]], agent_manager):
    """Display standard multi-agent responses (Plain version)."""
    for agent_id, response_text in responses:
        try:
            agent_info = agent_manager.get_agent_info(agent_id)
            profile_name = agent_info.get('profile_name', 'unknown') if agent_info else 'unknown'
            agent_display_name = f"{agent_id} ({profile_name})"
        except:
            agent_display_name = agent_id
        
        click.echo(f"\n--- Agent {agent_display_name} ---")
        click.echo(response_text)
        click.echo()

# Safe imports with fallback for missing tools
try:
    from ..tools.core_tools.write_tool import WriteTool
except ImportError as e:
    print(f"Warning: WriteTool import failed: {e}")
    WriteTool = None

try:
    from ..tools.core_tools.project_management_tool import ProjectManagementTool
except ImportError as e:
    print(f"Warning: ProjectManagementTool import failed: {e}")
    ProjectManagementTool = None

try:
    from ..tools.core_tools.read_tool import ReadTool
except ImportError as e:
    print(f"Warning: ReadTool import failed: {e}")
    ReadTool = None

try:
    from ..tools.core_tools.grep_tool import GrepTool
except ImportError as e:
    print(f"Warning: GrepTool import failed: {e}")
    GrepTool = None

try:
    from ..tools.core_tools.filemanagertool import RobustfilemanagerTool as FileManagerTool
except ImportError as e:
    print(f"Warning: FileManagerTool import failed: {e}")
    FileManagerTool = None

try:
    from ..tools.core_tools.bash_tool import BashTool
except ImportError as e:
    print(f"Warning: BashTool import failed: {e}")
    BashTool = None

try:
    from ..tools.advanced_tools.e2b_code_sandbox import E2BCodeSandboxTool
except ImportError as e:
    print(f"Warning: E2BCodeSandboxTool import failed: {e}")
    E2BCodeSandboxTool = None

try:
    from ..tools.core_tools.project_analyzer_tool import ProjectAnalyzerTool
except ImportError as e:
    print(f"Warning: ProjectAnalyzerTool import failed: {e}")
    ProjectAnalyzerTool = None

try:
    from .todo_commands import auto_create_todos_for_request
    from .natural_todo_workflow import (
        process_natural_language_request_with_todos, 
        has_active_todo_session,
        check_and_display_todo_context,
        analyze_and_maybe_create_todos,
        enhance_request_with_todo_context,
        update_todo_progress_after_response
    )
except ImportError as e:
    print(f"Warning: TODO commands import failed: {e}")
    auto_create_todos_for_request = None
    process_natural_language_request_with_todos = None
    has_active_todo_session = None
    check_and_display_todo_context = None
    analyze_and_maybe_create_todos = None
    enhance_request_with_todo_context = None
    update_todo_progress_after_response = None

from .streaming_interface import GeminiStreamingInterface


def generate_project_name(user_request):
    """
    Generate a simple, unique project name in format: metis-project-XXXXX
    
    Args:
        user_request (str): The user's project request (not used in simple format)
        
    Returns:
        str: A unique project name in format: metis-project-XXXXX
    """
    # Generate unique 5-digit ID using timestamp + random
    timestamp_part = datetime.now().strftime('%m%d')  # MMDD format
    random_part = ''.join(random.choices(string.digits, k=1))  # 1 random digit
    unique_id = f"{timestamp_part}{random_part}"
    
    # Simple consistent naming format
    project_name = f"metis-project-{unique_id}"
    
    return project_name

def _detect_existing_project(current_dir: str) -> dict:
    """
    Detect if current directory is already a Metis project or contains project files.
    
    Args:
        current_dir (str): Current working directory
        
    Returns:
        dict: Project detection info with keys: is_project, project_type, should_continue
    """
    # Debug info for troubleshooting
    debug_info = []
    
    try:
        # Check for common project indicators
        project_indicators = {
            'package.json': 'npm/node project',
            'requirements.txt': 'python project', 
            'pyproject.toml': 'python project',
            'Cargo.toml': 'rust project',
            'pom.xml': 'java project',
            'go.mod': 'go project',
            'composer.json': 'php project',
            'Gemfile': 'ruby project',
            'yarn.lock': 'yarn project',
            'poetry.lock': 'poetry project',
            'pipfile': 'pipenv project',
            'dockerfile': 'docker project',
            'makefile': 'makefile project'
        }
        
        # Check for git repository
        is_git_repo = False
        try:
            is_git_repo = os.path.isdir(os.path.join(current_dir, '.git'))
            if is_git_repo:
                debug_info.append("Found .git directory")
        except (OSError, PermissionError):
            debug_info.append("Cannot check for .git directory (permission issue)")
        
        # Check for existing project files
        existing_files = []
        detected_type = None
        
        try:
            for indicator_file, proj_type in project_indicators.items():
                file_path = os.path.join(current_dir, indicator_file)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    existing_files.append(indicator_file)
                    if not detected_type:
                        detected_type = proj_type
                    debug_info.append(f"Found project file: {indicator_file}")
        except (OSError, PermissionError):
            debug_info.append("Cannot check project files (permission issue)")
        
        # Check for common source directories
        common_dirs = ['src', 'lib', 'app', 'components', 'pages', 'views', 'controllers', 'tests', 'test']
        has_src_structure = False
        try:
            for d in common_dirs:
                if os.path.isdir(os.path.join(current_dir, d)):
                    has_src_structure = True
                    debug_info.append(f"Found source directory: {d}")
                    break
        except (OSError, PermissionError):
            debug_info.append("Cannot check source directories (permission issue)")
        
        # Check for code files in the directory (Python, JavaScript, etc.)
        code_files = []
        has_code_files = False
        try:
            files_in_dir = os.listdir(current_dir)
            code_extensions = ('.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.cs', '.swift', '.kt')
            
            for file in files_in_dir:
                file_path = os.path.join(current_dir, file)
                if os.path.isfile(file_path) and file.lower().endswith(code_extensions):
                    code_files.append(file)
            
            has_code_files = len(code_files) > 0
            if has_code_files:
                debug_info.append(f"Found {len(code_files)} code files: {', '.join(code_files[:3])}{'...' if len(code_files) > 3 else ''}")
                
        except (OSError, PermissionError) as e:
            debug_info.append(f"Cannot list files in directory: {str(e)}")
        
        # Check for metis project naming pattern in current directory name
        dir_name = os.path.basename(current_dir)
        is_metis_project = dir_name.startswith('metis-') or 'metis' in dir_name.lower()
        if is_metis_project:
            debug_info.append(f"Directory name suggests Metis project: {dir_name}")
        
        # Determine project status
        is_project = bool(existing_files) or has_src_structure or is_git_repo or has_code_files
        should_continue = is_project  # Continue in any existing project
        
        # Log debug info for troubleshooting (only if environment variable is set)
        if os.environ.get('METIS_DEBUG_PROJECT_DETECTION'):
            print(f"[DEBUG] Project detection for {current_dir}:")
            for info in debug_info:
                print(f"[DEBUG]   - {info}")
            print(f"[DEBUG] Result: is_project={is_project}, should_continue={should_continue}")
        
        return {
            'is_project': is_project,
            'is_metis_project': is_metis_project,
            'project_type': detected_type or ('code project' if has_code_files else None),
            'existing_files': existing_files,
            'code_files': code_files,
            'has_git': is_git_repo,
            'has_src_structure': has_src_structure,
            'has_code_files': has_code_files,
            'should_continue': should_continue,
            'directory_name': dir_name,
            'debug_info': debug_info
        }
        
    except Exception as e:
        # Fallback: if detection fails completely, don't assume it's a project
        debug_info.append(f"Project detection failed: {str(e)}")
        return {
            'is_project': False,
            'is_metis_project': False,
            'project_type': None,
            'existing_files': [],
            'code_files': [],
            'has_git': False,
            'has_src_structure': False,
            'has_code_files': False,
            'should_continue': False,
            'directory_name': os.path.basename(current_dir),
            'debug_info': debug_info,
            'error': str(e)
        }


def _get_project_location(project_name: str, auto: bool = False, confirmation_level: str = 'normal') -> str:
    """Get project location with user confirmation and project detection."""
    current_dir = os.getcwd()
    
    try:
        project_info = _detect_existing_project(current_dir)
    except Exception as e:
        # If project detection completely fails, create a fallback response
        click.echo(click.style(f"[WARNING] Project detection failed: {str(e)}", fg="red"))
        project_info = {
            'should_continue': False,
            'is_project': False,
            'project_type': None,
            'error': str(e)
        }
    
    # Debug output for troubleshooting
    if os.environ.get('METIS_DEBUG_PROJECT_DETECTION'):
        click.echo(click.style(f"[DEBUG] should_continue = {project_info.get('should_continue', False)}", fg="blue"))
    
    # If we're in an existing project, work in current directory
    if project_info.get('should_continue', False):
        if auto:
            return current_dir
        
        # Show project continuation info
        try:
            if RICH_AVAILABLE:
                console = Console()
                project_table = Table.grid(padding=1)
                project_table.add_column(style="dim", min_width=15)
                project_table.add_column()
                
                project_table.add_row("Current Dir:", Text(current_dir, style="bold cyan"))
                project_table.add_row("Project Type:", Text(project_info['project_type'] or 'detected project', style="green"))
                
                if project_info['existing_files']:
                    project_table.add_row("Project Files:", Text(', '.join(project_info['existing_files']), style="dim"))
                
                if project_info['code_files']:
                    code_files_display = ', '.join(project_info['code_files'][:5])  # Show first 5 code files
                    if len(project_info['code_files']) > 5:
                        code_files_display += f" (+{len(project_info['code_files']) - 5} more)"
                    project_table.add_row("Code Files:", Text(code_files_display, style="dim"))
                
                if project_info['has_git']:
                    project_table.add_row("Git Repo:", Text("Yes", style="green"))
                
                panel = Panel(
                    project_table,
                    title="[bold yellow]Existing Project Detected[/bold yellow]",
                    title_align="left",
                    border_style="yellow",
                    padding=(0, 1)
                )
                console.print(panel)
            else:
                # Fallback display without Rich
                click.echo(click.style(f"\n[EXISTING PROJECT DETECTED]", fg="yellow", bold=True))
                click.echo(click.style(f"Current Directory: {current_dir}", fg="white"))
                click.echo(click.style(f"Project Type: {project_info['project_type'] or 'detected project'}", fg="green"))
                
                if project_info['existing_files']:
                    click.echo(click.style(f"Project Files: {', '.join(project_info['existing_files'])}", fg="white", dim=True))
                
                if project_info['code_files']:
                    code_files_display = ', '.join(project_info['code_files'][:5])
                    if len(project_info['code_files']) > 5:
                        code_files_display += f" (+{len(project_info['code_files']) - 5} more)"
                    click.echo(click.style(f"Code Files: {code_files_display}", fg="white", dim=True))
                
                if project_info['has_git']:
                    click.echo(click.style(f"Git Repository: Yes", fg="green"))
                
                # Add debug info if available
                if os.environ.get('METIS_DEBUG_PROJECT_DETECTION') and project_info.get('debug_info'):
                    click.echo(click.style("\nDebug Info:", fg="blue"))
                    for info in project_info['debug_info']:
                        click.echo(click.style(f"  - {info}", fg="blue", dim=True))
                
        except Exception as e:
            # Ultimate fallback - just show basic info
            click.echo(click.style(f"\n[PROJECT DETECTED] Working in: {current_dir}", fg="yellow"))
            click.echo(click.style(f"Note: Display error occurred: {str(e)}", fg="red", dim=True))
        
        # Smart confirmation based on level
        if confirmation_level == 'minimal':
            # Auto-continue in minimal mode
            return current_dir
        elif confirmation_level == 'verbose':
            # Enhanced verbose confirmation
            while True:
                click.echo(click.style("\nProject Location Decision:", fg="yellow", bold=True))
                click.echo("  " + click.style("(y)es", fg="green") + " - Continue working in this existing project")
                click.echo("  " + click.style("(n)ew", fg="blue") + " - Create new project in subdirectory")
                click.echo("  " + click.style("(c)ustom", fg="cyan") + " - Choose custom location")
                
                choice = click.prompt(
                    click.style("Your choice", fg="yellow"),
                    type=str,
                    default="y"
                ).lower().strip()
                
                if choice in ['y', 'yes', '']:
                    return current_dir
                elif choice in ['n', 'new', 'no']:
                    break
                elif choice in ['c', 'custom']:
                    custom_path = click.prompt(
                        click.style("Enter custom project path", fg="cyan"),
                        type=str
                    )
                    return os.path.expanduser(custom_path)
                else:
                    click.echo(click.style("Please enter 'y', 'n', or 'c'", fg="red"))
        else:
            # Normal confirmation
            while True:
                choice = click.prompt(
                    click.style("Continue working in this existing project?", fg="yellow") + " " +
                    click.style("(y)es", fg="green") + " / " +
                    click.style("(n)ew project in subdirectory", fg="blue"),
                    type=str,
                    default="y"
                ).lower().strip()
                
                if choice in ['y', 'yes', '']:
                    return current_dir
                elif choice in ['n', 'new', 'no']:
                    break
                else:
                    click.echo(click.style("Please enter 'y' to continue or 'n' for new project", fg="red"))
    
    # Create new project in subdirectory
    default_location = os.path.join(current_dir, project_name)
    
    if auto:
        # In auto mode, create new project directory
        return default_location
    
    # Show proposed location with Rich panel
    if RICH_AVAILABLE:
        console = Console()
        
        # Create project info table
        project_table = Table.grid(padding=1)
        project_table.add_column(style="dim", min_width=15)
        project_table.add_column()
        
        rel_path = os.path.relpath(default_location, current_dir) if default_location != current_dir else f"./{project_name}"
        project_table.add_row("Project Name:", Text(project_name, style="bold cyan"))
        project_table.add_row("Relative Path:", Text(rel_path, style="green"))
        project_table.add_row("Full Path:", Text(default_location, style="dim"))
        project_table.add_row("Current Dir:", Text(current_dir, style="dim"))
        
        panel = Panel(
            project_table,
            title="[bold]Project Setup[/bold]",
            title_align="left",
            border_style="bright_blue",
            padding=(0, 1)
        )
        
        console.print(panel)
    else:
        # Fallback for non-Rich environments
        click.echo(click.style(f"\n[PROJECT SETUP] {project_name}", fg="cyan", bold=True))
        click.echo(click.style("─" * 50, fg="cyan", dim=True))
        
        rel_path = os.path.relpath(default_location, current_dir) if default_location != current_dir else f"./{project_name}"
        click.echo(click.style(f"Proposed location: {rel_path}", fg="white"))
        click.echo(click.style(f"Full path: {default_location}", fg="white", dim=True))
    
    # Handle confirmation based on level
    if confirmation_level == 'minimal':
        # Auto-accept default location in minimal mode
        return default_location
    elif confirmation_level == 'verbose':
        # Enhanced verbose confirmation for location
        while True:
            click.echo(click.style("\nProject Location Confirmation:", fg="yellow", bold=True))
            click.echo(f"  Project will be created at: {default_location}")
            click.echo("  Options:")
            click.echo("    " + click.style("(y)es", fg="green") + " - Create project at default location")
            click.echo("    " + click.style("(c)ustom", fg="blue") + " - Choose custom location")
            click.echo("    " + click.style("(x)cancel", fg="red") + " - Cancel project creation")
            
            choice = click.prompt(
                click.style("Your choice", fg="yellow"),
                type=str,
                default="y"
            ).lower().strip()
            
            if choice in ['y', 'yes', '']:
                return default_location
            elif choice in ['c', 'custom']:
                custom_path = click.prompt(
                    click.style("Enter project directory path", fg="cyan"),
                    type=str
                )
                return os.path.expanduser(custom_path)
            elif choice in ['x', 'cancel']:
                click.echo(click.style("Project creation cancelled", fg="red"))
                raise click.Abort()
            else:
                click.echo(click.style("Please enter 'y', 'c', or 'x'", fg="red"))
    
    while True:
        try:
            choice = click.prompt(
                click.style("Create project here?", fg="yellow") + " " +
                click.style("(y)es", fg="green") + " / " +
                click.style("(n)o, choose location", fg="blue") + " / " +
                click.style("(c)ancel", fg="red"),
                type=str,
                show_default=False
            ).lower().strip()
            
            if choice in ['y', 'yes']:
                return default_location
            elif choice in ['n', 'no']:
                # Let user choose custom location
                custom_path = click.prompt(
                    click.style("Enter project directory", fg="blue"),
                    type=str,
                    default=current_dir
                )
                if not os.path.isabs(custom_path):
                    custom_path = os.path.join(current_dir, custom_path)
                
                full_project_path = os.path.join(custom_path, project_name)
                click.echo(click.style(f"Project will be created at: {full_project_path}", fg="cyan"))
                return full_project_path
            elif choice in ['c', 'cancel']:
                click.echo(click.style("Project creation cancelled.", fg="red"))
                raise click.Abort()
            else:
                click.echo(click.style("Please choose: y/n/c", fg="red", dim=True))
                
        except (KeyboardInterrupt, EOFError):
            click.echo(click.style("\nProject creation cancelled.", fg="red"))
            raise click.Abort()


@click.group(invoke_without_command=True)
@click.pass_context
@click.argument('request', nargs=-1, required=False)
@click.option('--session', '-s', help='Session ID for context')
@click.option('--branch', '-b', type=str, help='Create specific named feature branch')
@click.option('--no-branch', is_flag=True, help='Skip automatic branch creation')
@click.option('--auto', '-a', is_flag=True, help='Auto mode - skip prompts and execute directly')
@click.option('--fast', is_flag=True, help='Fast mode - minimal interface for simple operations')
@click.option('--stream', is_flag=True, help='Streaming mode - full interface for complex operations')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmations and use smart defaults')
@click.option('--review', is_flag=True, help='Force review mode with detailed confirmations')
@click.option('--interface', type=click.Choice(['simple', 'advanced', 'expert']), help='Set interface complexity level')
def code(ctx, request, session, branch, no_branch, auto, fast, stream, yes, review, interface):
    """Natural language coding assistant with structured subcommands.
    
    Natural Language Examples:
      metis code "analyze this project and tell me about its structure"
      metis code "create a calculator class with add and subtract methods"
      metis code "fix the syntax errors in main.py"
      metis code "generate tests for the User class"
      
    Structured Subcommands:
      metis code edit main.py "add error handling"
      metis code create component UserCard
      metis code fix --type syntax
      metis code test generate calculator.py
      metis code md prd "User Authentication System"
      
    Interactive Mode:
      metis code (starts interactive session with slash commands)
    """
    # Initialize streaming interface with tools first
    tools_registry = {}
    
    # Add tools that were successfully imported
    if WriteTool:
        tools_registry['WriteTool'] = WriteTool()
    if ProjectManagementTool:
        tools_registry['ProjectManagementTool'] = ProjectManagementTool()
    if ReadTool:
        tools_registry['ReadTool'] = ReadTool()
    if GrepTool:
        tools_registry['GrepTool'] = GrepTool()
    if FileManagerTool:
        tools_registry['FileManagerTool'] = FileManagerTool()
    if BashTool:
        tools_registry['BashTool'] = BashTool()
    if E2BCodeSandboxTool:
        tools_registry['E2BCodeSandboxTool'] = E2BCodeSandboxTool()
    if ProjectAnalyzerTool:
        tools_registry['ProjectAnalyzerTool'] = ProjectAnalyzerTool()
    
    # Convert tools registry to list for agent
    tools_list = list(tools_registry.values())
    
    # Initialize agent with config settings and tools for streaming
    config = AgentConfig()
    agent = SingleAgent(
        use_titans_memory=config.is_titans_memory_enabled(),
        llm_provider=config.get_llm_provider(),
        llm_model=config.get_llm_model(),
        enhanced_processing=False,  # Use direct processing for streaming
        config=config,
        tools=tools_list  # Pass tools to agent
    )
    
    # If no subcommand was called, handle as natural language or start interactive
    if ctx.invoked_subcommand is None:
        if request:
            request_text = ' '.join(request)
            return _handle_natural_language_request(agent, request_text, tools_registry, session, branch, no_branch, auto, fast, stream, yes, review, interface)
        else:
            # No request provided - start interactive streaming session
            return _start_interactive_streaming_session(agent, tools_registry, session, branch, no_branch, auto, fast, stream, yes, review, interface)


def _handle_natural_language_request(agent, request_text, tools_registry=None, session=None, branch=None, no_branch=False, auto=False, fast=False, stream=False, yes=False, review=False, interface=None):
    """Process a single natural language coding request with intelligent routing."""
    
    # Check for multi-agent collaboration mentions first
    clean_query, mentioned_agents = _parse_mentions(request_text)
    
    if mentioned_agents:
        # Handle multi-agent collaboration
        try:
            # Import agent manager for multi-agent processing
            from ..cli.agent_commands import get_agent_manager
            agent_manager = get_agent_manager()
            
            if len(mentioned_agents) == 1:
                if RICH_AVAILABLE:
                    console = Console()
                    console.print(f"Consulting agent: {mentioned_agents[0]}", style="dim")
                else:
                    click.echo(f"Consulting agent: {mentioned_agents[0]}")
            else:
                if RICH_AVAILABLE:
                    console = Console()
                    console.print(f"Starting collaborative discussion with {len(mentioned_agents)} agents: {', '.join(mentioned_agents)}", style="dim")
                else:
                    click.echo(f"Starting collaborative discussion with {len(mentioned_agents)} agents: {', '.join(mentioned_agents)}")
            
            # Create session ID for multi-agent context
            validated_session = session or f"code-session-{int(time.time())}"
            
            # Process with multiple agents
            responses = _process_multi_agent_query(mentioned_agents, clean_query, agent_manager, validated_session)
            _display_multi_agent_responses(responses, agent_manager)
            return
            
        except Exception as e:
            click.echo(f"Error in multi-agent processing: {e}")
            click.echo("Falling back to single agent processing...")
            # Fall through to regular processing with original request_text
    
    # Use clean query if mentions were parsed, otherwise use original
    final_query = clean_query if mentioned_agents else request_text
    
    # Create tools registry if not provided
    if tools_registry is None:
        tools_registry = {}
        # Add tools that were successfully imported
        if WriteTool:
            tools_registry['WriteTool'] = WriteTool()
        if ProjectManagementTool:
            tools_registry['ProjectManagementTool'] = ProjectManagementTool()
        if ReadTool:
            tools_registry['ReadTool'] = ReadTool()
        if GrepTool:
            tools_registry['GrepTool'] = GrepTool()
        if FileManagerTool:
            tools_registry['FileManagerTool'] = FileManagerTool()
        if BashTool:
            tools_registry['BashTool'] = BashTool()
        if E2BCodeSandboxTool:
            tools_registry['E2BCodeSandboxTool'] = E2BCodeSandboxTool()
        if ProjectAnalyzerTool:
            tools_registry['ProjectAnalyzerTool'] = ProjectAnalyzerTool()
    
    # Enhanced TODO integration - check if it can handle the request completely
    if process_natural_language_request_with_todos:
        try:
            todo_response = process_natural_language_request_with_todos(
                agent, final_query, session=session,
                branch=branch, no_branch=no_branch, auto=auto, 
                fast=fast, stream=stream, yes=yes, review=review, interface=interface
            )
            if todo_response:  # TODO system handled the request completely
                return todo_response
        except Exception as e:
            click.echo(f"Warning: Enhanced TODO integration failed: {e}")
    
    # Check for TODO context display (for active sessions)
    if check_and_display_todo_context:
        try:
            check_and_display_todo_context(final_query)
        except Exception:
            pass
    
    # Check if we should create TODOs for complex requests
    if analyze_and_maybe_create_todos:
        try:
            todo_creation = analyze_and_maybe_create_todos(final_query)
            if todo_creation:
                click.echo("Starting with first task...")
                click.echo("=" * 50)
        except Exception as e:
            # Fallback to basic TODO integration
            if auto_create_todos_for_request:
                todo_result = auto_create_todos_for_request(final_query)
                if todo_result:
                    click.echo(click.style("TODO Management", fg="cyan", bold=True))
                    click.echo(todo_result)
                    click.echo("=" * 60)
    
    # Determine operation mode, confirmation level, and interface mode
    operation_mode = _determine_operation_mode(final_query, auto, fast, stream)
    confirmation_level = _determine_confirmation_level(operation_mode, yes, review)
    interface_mode = _determine_interface_mode(interface)
    
    # First check if this should be routed to a specific subcommand
    detected_command = _detect_subcommand_from_text(final_query)
    
    if detected_command:
        subcommand, params = detected_command
        if operation_mode == 'fast':
            click.echo(click.style(f"⚡ [FAST] {subcommand.upper()}: {final_query}", fg="green", bold=True))
        else:
            click.echo(click.style(f"[SMART ROUTING] Detected '{subcommand}' operation", fg="magenta"))
            click.echo(click.style(f"Auto-routing: {final_query}", fg="blue"))
            click.echo("=" * 50)
        
        # Route to the appropriate subcommand
        try:
            return _route_to_subcommand(subcommand, params, session, operation_mode, confirmation_level)
        except Exception as e:
            click.echo(click.style(f"[ROUTING FAILED] {str(e)}", fg="yellow"))
            click.echo(click.style("Falling back to natural language processing...", fg="blue"))
    
    # Original natural language processing with mode-specific headers
    if operation_mode == 'fast':
        click.echo(click.style(f"⚡ [FAST MODE] {final_query}", fg="green", bold=True))
    elif auto:
        click.echo(click.style(f"[AUTO MODE] {final_query}", fg="yellow", bold=True))
        click.echo(click.style("[AUTO] Executing directly without prompts...", fg="yellow"))
    elif operation_mode == 'stream':
        click.echo(click.style(f"[STREAMING MODE] {final_query}", fg="blue", bold=True))
        click.echo("=" * 50)
    else:
        click.echo(click.style(f"[PROCESSING] {final_query}", fg="cyan", bold=True))
        click.echo("=" * 50)
    
    try:
        # Handle branch creation if this looks like a code generation task
        if _should_create_branch(final_query) and not no_branch:
            branch_created = _create_feature_branch(branch, auto_branch=(branch is None), description=final_query)
            if not branch_created:
                if auto or click.confirm("Continue without creating a branch?"):
                    pass  # Continue in auto mode or if user confirms
                else:
                    return
        
        # Get project context for the agent
        project_context = _get_project_context()
        
        # All requests now use streaming interface - no separate workflow
        
        # Enhance request with TODO context if available
        if enhance_request_with_todo_context:
            try:
                enhanced_request_text = enhance_request_with_todo_context(final_query)
            except Exception:
                enhanced_request_text = final_query
        else:
            enhanced_request_text = final_query

        # Create enhanced prompt with context for regular requests
        if auto:
            enhanced_prompt = f"""EXECUTE THIS TASK IMMEDIATELY IN AUTO MODE:

{enhanced_request_text}

PROJECT CONTEXT:
{project_context}

CRITICAL: You MUST actually execute the tools to complete this task. Do not just analyze or plan - EXECUTE NOW.

For file operations:
1. Identify the correct tool (EditTool for editing existing files, WriteTool for creating new files)
2. Extract the file path from the user request
3. Determine the operation type (create, edit, append, etc.)
4. Execute the tool with proper structured parameters
5. Show the results of the actual file modification

Do NOT just describe what should be done - DO IT NOW.

EXECUTE THE TOOLS NOW - DO NOT JUST ANALYZE."""
        else:
            enhanced_prompt = f"""I'm working on a coding task. Here's my request:

{enhanced_request_text}

PROJECT CONTEXT:
{project_context}

Please help me with this request. You have access to various tools including:
- ReadTool: for reading and analyzing existing files in the project
- GrepTool: for searching through files and finding specific patterns or code
- FileManagerTool: for listing directories, managing file operations, and project structure analysis
- WriteTool: for creating new files and writing code
- ProjectManagementTool: for creating projects, managing sessions, project lifecycle
- BashTool: for executing shell commands and system operations (with user confirmation)
- E2BCodeSandboxTool: for secure Python code execution in isolated cloud sandboxes (with user confirmation)
- And many other specialized tools for different tasks

IMPORTANT: When asked about existing code or files, ALWAYS use the file analysis tools first:
1. Use ReadTool to examine specific files: ReadTool.execute(task="read file", file_path="/path/to/file")
2. Use GrepTool to search for patterns: GrepTool.execute(task="search files", pattern="function_name", file_types=[".py"])
3. Use FileManagerTool to explore project structure: FileManagerTool.execute(task="list directory", path="/project/path")

Analyze my request and determine what needs to be done. Use the appropriate tools based on the task:
- To understand existing code: FIRST use ReadTool, GrepTool, or FileManagerTool to examine the files
- To analyze project structure: use FileManagerTool to list directories and ReadTool for key files
- Create/manage projects: use ProjectManagementTool
- Write new files: use WriteTool
- Search for specific code patterns: use GrepTool
- Execute shell commands: use BashTool (will ask user for confirmation)
- Run Python code securely: use E2BCodeSandboxTool (will ask user for confirmation)
- Multiple operations: break it down step by step

Be conversational and explain what you're doing. Show me the results and ask if you need clarification."""

        # Generate unique project directory in current directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = ''.join(c for c in final_query[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_').lower()
        project_name = f"{safe_name}_{timestamp}"
        
        # Get project location with user confirmation
        project_location = _get_project_location(project_name, auto, confirmation_level)
        
        # Create streaming interface with operation mode, confirmation level, and interface mode
        streaming_interface = GeminiStreamingInterface(agent, project_location, tools_registry, operation_mode, confirmation_level, interface_mode)
        
        # Confirmation preferences are now handled internally by the streaming interface
        
        # Stream response and write code blocks in real-time (like Gemini Code)
        streaming_interface.start_session()
        response_generator = streaming_interface.stream_response(enhanced_prompt, session_id=session)
        response_content = list(response_generator)
        
        # Update TODO progress after response if applicable
        if update_todo_progress_after_response:
            try:
                # Get the actual response content for progress analysis
                full_response = ' '.join(str(chunk) for chunk in response_content if chunk)
                update_todo_progress_after_response(final_query, full_response)
            except Exception:
                pass  # Silently ignore TODO update errors
        
        click.echo(click.style("\n[COMPLETE] Task completed!", fg="green", bold=True))
        
    except Exception as e:
        click.echo(click.style(f"[ERROR] {str(e)}", fg="red"))


def _start_interactive_streaming_session(agent, tools_registry=None, session=None, branch=None, no_branch=False, auto=False, fast=False, stream=False, yes=False, review=False, interface=None):
    """Start an interactive streaming session like Gemini with multi-agent support."""
    
    # Multi-agent support initialization
    current_agent = agent
    current_agent_id = None  # Default single agent
    
    # Try to import agent manager for multi-agent support
    try:
        from ..core.agent_manager import get_agent_manager
        agent_manager = get_agent_manager()
        multi_agent_available = True
    except Exception:
        agent_manager = None
        multi_agent_available = False
    
    # Create tools registry if not provided
    if tools_registry is None:
        tools_registry = {}
        # Add tools that were successfully imported
        if WriteTool:
            tools_registry['WriteTool'] = WriteTool()
        if ProjectManagementTool:
            tools_registry['ProjectManagementTool'] = ProjectManagementTool()
        if ReadTool:
            tools_registry['ReadTool'] = ReadTool()
        if GrepTool:
            tools_registry['GrepTool'] = GrepTool()
        if FileManagerTool:
            tools_registry['FileManagerTool'] = FileManagerTool()
        if BashTool:
            tools_registry['BashTool'] = BashTool()
        if E2BCodeSandboxTool:
            tools_registry['E2BCodeSandboxTool'] = E2BCodeSandboxTool()
        if ProjectAnalyzerTool:
            tools_registry['ProjectAnalyzerTool'] = ProjectAnalyzerTool()
    
    # Determine operation mode, confirmation level, and interface mode for interactive session
    operation_mode = 'fast' if fast else 'stream' if stream else 'balanced'
    confirmation_level = _determine_confirmation_level(operation_mode, yes, review)
    interface_mode = _determine_interface_mode(interface)
    
    # Generate session project location
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = f"interactive_session_{timestamp}"
    project_location = _get_project_location(project_name, auto, confirmation_level)
    
    # Initialize streaming interface with tools - use same registry as main function
    tools_registry = {}
    
    # Add tools that were successfully imported
    if WriteTool:
        tools_registry['WriteTool'] = WriteTool()
    if ProjectManagementTool:
        tools_registry['ProjectManagementTool'] = ProjectManagementTool()
    if ReadTool:
        tools_registry['ReadTool'] = ReadTool()
    if GrepTool:
        tools_registry['GrepTool'] = GrepTool()
    if FileManagerTool:
        tools_registry['FileManagerTool'] = FileManagerTool()
    if BashTool:
        tools_registry['BashTool'] = BashTool()
    if E2BCodeSandboxTool:
        tools_registry['E2BCodeSandboxTool'] = E2BCodeSandboxTool()
    if ProjectAnalyzerTool:
        tools_registry['ProjectAnalyzerTool'] = ProjectAnalyzerTool()
    
    streaming_interface = GeminiStreamingInterface(agent, project_location, tools_registry, operation_mode, confirmation_level, interface_mode)
    
    # Confirmation preferences are now handled internally by the streaming interface
    
    # Start interactive session
    streaming_interface.interactive_session()


def _start_interactive_coding_session(agent, session=None, branch=None, no_branch=False, auto=False, operation_mode='balanced', confirmation_level='normal'):
    """Start an interactive coding session with the agent."""
    click.echo(click.style("[INTERACTIVE CODING SESSION]", fg="magenta", bold=True))
    click.echo("=" * 50)
    
    # Show project status
    _show_project_status()
    
    click.echo("\nI'm your coding assistant. You can ask me to:")
    click.echo("• Analyze code or project structure")  
    click.echo("• Generate new code or modify existing code")
    click.echo("• Debug issues or explain code")
    click.echo("• Create documentation or tests")
    click.echo("• Refactor or optimize code")
    click.echo("• Manage files and directories")
    click.echo("• And much more...")
    click.echo("\nType 'help' for more examples, 'quit' to exit")
    click.echo("=" * 50)
    
    current_session = session or f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    while True:
        try:
            user_input = click.prompt(
                click.style("\n[You]", fg="green", bold=True),
                type=str, 
                show_default=False
            ).strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                click.echo(click.style("[GOODBYE] Happy coding!", fg="cyan"))
                break
                
            elif user_input.lower() == 'help':
                _show_help_examples()
                continue
                
            elif user_input.lower() in ['status', 'project']:
                _show_project_status()
                continue
            
            # Process the request through streaming interface
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = ''.join(c for c in user_input[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_').lower()
            project_name = f"{safe_name}_{timestamp}"
            
            project_location = _get_project_location(project_name, auto, confirmation_level)
            
            # Initialize streaming interface with tools - use same registry as main function
            tools_registry = {}
            
            # Add tools that were successfully imported
            if WriteTool:
                tools_registry['WriteTool'] = WriteTool()
            if ProjectManagementTool:
                tools_registry['ProjectManagementTool'] = ProjectManagementTool()
            if ReadTool:
                tools_registry['ReadTool'] = ReadTool()
            if GrepTool:
                tools_registry['GrepTool'] = GrepTool()
            if FileManagerTool:
                tools_registry['FileManagerTool'] = FileManagerTool()
            if BashTool:
                tools_registry['BashTool'] = BashTool()
            if E2BCodeSandboxTool:
                tools_registry['E2BCodeSandboxTool'] = E2BCodeSandboxTool()
            if ProjectAnalyzerTool:
                tools_registry['ProjectAnalyzerTool'] = ProjectAnalyzerTool()
            
            streaming_interface = GeminiStreamingInterface(agent, project_location, tools_registry, operation_mode, confirmation_level, interface_mode)
            
            # Enhance user input with TODO context if available
            if enhance_request_with_todo_context:
                try:
                    enhanced_user_input = enhance_request_with_todo_context(user_input)
                except Exception:
                    enhanced_user_input = user_input
            else:
                enhanced_user_input = user_input
            
            # Check and display TODO context
            if check_and_display_todo_context:
                try:
                    check_and_display_todo_context(user_input)
                except Exception:
                    pass
            
            # Stream the response
            response_generator = streaming_interface.stream_response(enhanced_user_input, session_id=current_session)
            response_content = list(response_generator)
            
            # Update TODO progress after response if applicable
            if update_todo_progress_after_response:
                try:
                    full_response = ' '.join(str(chunk) for chunk in response_content if chunk)
                    update_todo_progress_after_response(user_input, full_response)
                except Exception:
                    pass
            
        except KeyboardInterrupt:
            click.echo(click.style("\n[GOODBYE] Session interrupted. Happy coding!", fg="cyan"))
            break
        except EOFError:
            click.echo(click.style("\n[GOODBYE] Session ended. Happy coding!", fg="cyan"))
            break


def _get_project_context():
    """Get current project context for the agent."""
    current_dir = Path.cwd()
    
    context_parts = [f"Working Directory: {current_dir}"]
    
    # Get file listing using standard Python
    try:
        files = [f.name for f in current_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
        dirs = [d.name for d in current_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if files:
            context_parts.append(f"Files in current directory: {', '.join(files[:10])}")
            if len(files) > 10:
                context_parts.append(f"... and {len(files) - 10} more files")
                
        if dirs:
            context_parts.append(f"Subdirectories: {', '.join(dirs[:5])}")
    except:
        context_parts.append("Unable to read directory contents")
    
    # Check for common project files
    project_indicators = []
    common_files = ["requirements.txt", "package.json", "setup.py", "pyproject.toml", "Dockerfile", "README.md"]
    for file in common_files:
        if Path(file).exists():
            project_indicators.append(file)
    
    if project_indicators:
        context_parts.append(f"Project files detected: {', '.join(project_indicators)}")
    
    # Check git status
    try:
        result = subprocess.run(["git", "branch", "--show-current"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            context_parts.append(f"Git branch: {result.stdout.strip()}")
    except:
        pass
    
    return "\n".join(context_parts)


def _show_project_status():
    """Show current project context."""
    click.echo(click.style("[PROJECT CONTEXT]", fg="blue", bold=True))
    click.echo(_get_project_context())
    click.echo("\n" + click.style("Available Workflows:", fg="green", bold=True))
    click.echo("• Complete Project Development - Creates full applications from requirements to completion")
    click.echo("• Code Analysis & Quality Check - Analyzes existing codebases for quality and structure")
    click.echo("• Documentation Generation - Creates comprehensive project documentation")
    click.echo("\nTry: metis code 'create a todo app with Python' or metis code 'analyze this codebase'")


def _show_help_examples():
    """Show help with natural language examples."""
    click.echo(click.style("\n[HELP] Natural Language Examples", fg="yellow", bold=True))
    click.echo("=" * 40)
    
    examples = [
        "Code Analysis:",
        "  • 'analyze this project structure'",
        "  • 'show me the dependencies in requirements.txt'", 
        "  • 'what functions are in main.py?'",
        "  • 'check for syntax errors in my Python files'",
        "",
        "Code Generation:",
        "  • 'create a calculator class with basic operations'",
        "  • 'generate unit tests for the User class'",
        "  • 'write a function that validates email addresses'", 
        "  • 'create a simple REST API with FastAPI'",
        "",
        "File Operations:",
        "  • 'create a new file called config.py'",
        "  • 'read the contents of setup.py'",
        "  • 'search for all TODO comments in .py files'",
        "  • 'show me the directory tree'",
        "",
        "Code Improvement:",
        "  • 'refactor this function to be more readable'",
        "  • 'optimize the performance of data_processor.py'",
        "  • 'add proper error handling to my API endpoints'",
        "  • 'generate docstrings for all functions in utils.py'",
        "",
        "Documentation:",
        "  • 'create README documentation for this project'",
        "  • 'generate API documentation from my FastAPI code'",
        "  • 'explain what this code does in simple terms'",
    ]
    
    for example in examples:
        click.echo(example)


def _should_create_branch(request_text):
    """Determine if the request should create a new git branch."""
    request_lower = request_text.lower()
    
    # Keywords that suggest code changes
    change_keywords = [
        'create', 'generate', 'add', 'build', 'make', 'write', 'implement',
        'modify', 'update', 'change', 'fix', 'refactor', 'optimize'
    ]
    
    # Keywords that suggest read-only operations
    readonly_keywords = [
        'analyze', 'show', 'list', 'read', 'display', 'explain', 'describe',
        'check', 'review', 'examine', 'tell me about'
    ]
    
    # Check if it's clearly a read-only request
    if any(keyword in request_lower for keyword in readonly_keywords):
        return False
    
    # Check if it's clearly a change request
    if any(keyword in request_lower for keyword in change_keywords):
        return True
    
    # Default to creating branch for ambiguous cases
    return False


def _create_feature_branch(branch_name, auto_branch, description):
    """Create a feature branch for code changes."""
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return True  # Not a git repo, continue without branch
            
    except:
        return True  # Git not available, continue without branch
    
    # Generate branch name
    if branch_name:
        new_branch = branch_name
    elif auto_branch:
        safe_desc = re.sub(r'[^\w\s-]', '', description.lower())
        safe_desc = re.sub(r'\s+', '-', safe_desc.strip())[:30]
        timestamp = datetime.now().strftime("%m%d-%H%M")
        new_branch = f"feature/{safe_desc}-{timestamp}"
    else:
        return True
    
    try:
        # Create and switch to new branch
        result = subprocess.run(
            ["git", "checkout", "-b", new_branch],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            click.echo(click.style(f"[BRANCH] Created branch '{new_branch}'", fg="green"))
            return True
        else:
            # Try to switch to existing branch
            switch_result = subprocess.run(
                ["git", "checkout", new_branch],
                capture_output=True, text=True, timeout=10
            )
            if switch_result.returncode == 0:
                click.echo(click.style(f"[BRANCH] Switched to '{new_branch}'", fg="green"))
                return True
            else:
                click.echo(click.style(f"[WARNING] Could not create branch: {result.stderr.strip()}", fg="yellow"))
                return click.confirm("Continue without creating branch?")
                
    except Exception as e:
        click.echo(click.style(f"[WARNING] Branch creation failed: {str(e)}", fg="yellow"))
        return click.confirm("Continue without creating branch?")


def _handle_code_extraction(response, original_request):
    """Extract and save any code from the agent response."""
    if '```' not in response:
        return
    
    # Extract code blocks
    code_blocks = []
    parts = response.split('```')
    
    for i, part in enumerate(parts):
        if i % 2 == 1:  # Odd indices are code blocks
            lines = part.strip().split('\n')
            language = ""
            code_content = part.strip()
            
            # Check if first line is a language identifier
            if lines and lines[0].strip() in ['python', 'py', 'javascript', 'js', 'java', 'cpp', 'c', 'html', 'css']:
                language = lines[0].strip()
                code_content = '\n'.join(lines[1:])
            
            if code_content.strip():
                code_blocks.append({
                    'language': language,
                    'content': code_content
                })
    
    if not code_blocks:
        return
    
    # Ask user if they want to save the code
    if len(code_blocks) == 1:
        if click.confirm(f"\n[SAVE] Save the generated code to a file?"):
            _save_code_block(code_blocks[0], original_request)
    else:
        click.echo(f"\n[SAVE] Found {len(code_blocks)} code blocks")
        for i, block in enumerate(code_blocks):
            lang_info = f" ({block['language']})" if block['language'] else ""
            if click.confirm(f"Save code block {i+1}{lang_info}?"):
                _save_code_block(block, original_request, suffix=f"_{i+1}")


def _save_code_block(code_block, original_request, suffix=""):
    """Save a single code block to a file."""
    # Suggest filename
    filename = _suggest_filename(original_request, code_block['language']) + suffix
    
    # Ask for filename
    filename = click.prompt("Filename", default=filename)
    
    try:
        with open(filename, 'w') as f:
            f.write(code_block['content'])
        
        click.echo(click.style(f"[SAVED] Code saved to {filename}", fg="green"))
        
        # Auto-commit if in git repo
        _auto_git_commit(filename, original_request)
        
    except Exception as e:
        click.echo(click.style(f"[ERROR] Could not save file: {str(e)}", fg="red"))


def _suggest_filename(request, language):
    """Suggest a filename based on the request and language."""
    # Extract meaningful words from request
    words = re.findall(r'\b\w+\b', request.lower())
    meaningful_words = [w for w in words if w not in [
        'create', 'generate', 'add', 'build', 'make', 'write', 'the', 'a', 'an', 
        'for', 'with', 'in', 'to', 'of', 'and', 'or', 'but'
    ]]
    
    if meaningful_words:
        base_name = "_".join(meaningful_words[:3])
    else:
        base_name = "generated_code"
    
    # Determine extension
    extensions = {
        'python': '.py', 'py': '.py',
        'javascript': '.js', 'js': '.js', 
        'java': '.java',
        'cpp': '.cpp', 'c++': '.cpp',
        'c': '.c',
        'html': '.html',
        'css': '.css'
    }
    
    ext = extensions.get(language.lower(), '.py')
    return base_name + ext


def _auto_git_commit(filename, description):
    """Auto-commit the file if in a git repository."""
    try:
        subprocess.run(["git", "add", filename], capture_output=True, timeout=10)
        subprocess.run(
            ["git", "commit", "-m", f"Add: {description}"], 
            capture_output=True, timeout=10
        )
        click.echo(click.style(f"[COMMIT] Committed {filename}", fg="cyan"))
    except:
        pass  # Silent fail for git operations


def _is_project_creation_request(request_text):
    """Detect if the request is for creating a new project."""
    request_lower = request_text.lower()
    
    # Project creation indicators
    creation_indicators = [
        'create a', 'build a', 'make a', 'develop a', 'generate a',
        'create an', 'build an', 'make an', 'develop an', 'generate an',
        'new project', 'new app', 'new application', 'new website',
        'todo app', 'calculator app', 'web app', 'api', 'website',
        'mobile app', 'desktop app', 'game', 'dashboard'
    ]
    
    # Check if request contains creation indicators
    for indicator in creation_indicators:
        if indicator in request_lower:
            return True
    
    # Check for patterns like "create [something] with [technology]"
    if 'create' in request_lower and ('with' in request_lower or 'using' in request_lower):
        return True
    
    return False


def _handle_project_creation(request_text, agent):
    """Handle project creation requests."""
    click.echo(click.style("[PROJECT CREATION] Detected project creation request", fg="green", bold=True))
    
    try:
        # Initialize project manager
        project_manager = ProjectManager()
        
        # Get enhanced project details from agent
        click.echo(click.style("[AGENT] Analyzing project requirements...", fg="blue"))
        
        analysis_prompt = f"""
Analyze this project creation request: "{request_text}"

Provide a brief analysis including:
1. Project type and complexity
2. Suggested technology stack
3. Key features to implement
4. Development approach

Keep the response concise and focused on the project planning aspects.
"""
        
        agent_response = agent.process_query(analysis_prompt)
        agent_analysis = agent_response.get('response', '') if isinstance(agent_response, dict) else str(agent_response)
        
        # Create the project structure
        click.echo(click.style("[PROJECT] Creating project structure...", fg="blue"))
        project_info = project_manager.create_new_project(request_text, agent_analysis)
        
        # Display success information
        click.echo(click.style("[SUCCESS] Project created successfully!", fg="green", bold=True))
        click.echo(f"Project Name: {project_info['project_name']}")
        click.echo(f"Location: {project_info['project_dir']}")
        click.echo(f"")
        click.echo("Project Structure:")
        click.echo(f"  {project_info['project_name']}/")
        click.echo(f"  +-- Metis/           # Project management files")
        click.echo(f"  |   +-- plan.md      # Development plan")
        click.echo(f"  |   +-- tasks.md     # Task breakdown")
        click.echo(f"  |   +-- design.md    # Technical design")
        click.echo(f"  |   +-- session.json # Session tracking")
        click.echo(f"  +-- src/             # Source code directory")
        click.echo(f"  +-- README.md        # Project documentation")
        click.echo(f"")
        click.echo(click.style("Next Steps:", fg="cyan", bold=True))
        click.echo(f"1. Navigate to the project: cd '{project_info['project_dir']}'")
        click.echo(f"2. Continue development: metis code 'implement the core functionality'")
        click.echo(f"3. Check project status: metis code")
        
        # Show agent analysis if available
        if agent_analysis and len(agent_analysis.strip()) > 0:
            click.echo(f"")
            click.echo(click.style("[AGENT ANALYSIS]", fg="blue", bold=True))
            click.echo(agent_analysis)
        
        return project_info
        
    except Exception as e:
        click.echo(click.style(f"[ERROR] Failed to create project: {str(e)}", fg="red"))
        return None


# Structured subcommands for metis code

@code.command()
@click.argument('file_path', type=str)
@click.argument('description', nargs=-1, required=False)
@click.option('--line', '-l', type=int, help='Start editing at specific line number')
@click.option('--session', '-s', help='Session ID for context')
def edit(file_path, description, line, session):
    """Edit a specific file with optional description.
    
    Examples:
      metis code edit main.py \"add error handling\"
      metis code edit utils.py \"refactor the helper functions\"
      metis code edit app.py --line 50 \"fix the validation logic\"
    """
    desc_text = ' '.join(description) if description else f"edit {file_path}"
    
    # Create edit-specific request
    if line:
        request_text = f"Edit {file_path} starting at line {line}: {desc_text}"
    else:
        request_text = f"Edit {file_path}: {desc_text}"
    
    # Use the existing natural language handler with edit-optimized context
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style(f"[EDIT] {file_path}", fg="cyan", bold=True))
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


@code.command()
@click.argument('item_type', type=str)
@click.argument('name', type=str, required=False)
@click.option('--template', '-t', type=str, help='Use specific template (react, flask, etc.)')
@click.option('--session', '-s', help='Session ID for context')
def create(item_type, name, template, session):
    """Create new files, components, or projects.
    
    Examples:
      metis code create component UserCard
      metis code create project \"todo app\"
      metis code create file utils.py --template python
      metis code create api \"user management\" --template fastapi
    """
    if name:
        if template:
            request_text = f"Create a {item_type} named '{name}' using {template} template"
        else:
            request_text = f"Create a {item_type} named '{name}'"
    else:
        if template:
            request_text = f"Create a {item_type} using {template} template"
        else:
            request_text = f"Create a {item_type}"
    
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style(f"[CREATE] {item_type}" + (f" - {name}" if name else ""), fg="green", bold=True))
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


@code.command()
@click.argument('target', type=str, required=False)
@click.option('--type', '-t', type=str, help='Type of issues to fix (syntax, logic, style)')
@click.option('--pattern', '-p', type=str, help='File pattern to fix (e.g., "*.py")')
@click.option('--session', '-s', help='Session ID for context')
def fix(target, type, pattern, session):
    """Fix errors or issues in code.
    
    Examples:
      metis code fix main.py
      metis code fix --type syntax
      metis code fix --pattern \"*.py\" --type style
      metis code fix \"the login function\"
    """
    request_parts = ["Fix"]
    
    if target:
        request_parts.append(target)
    elif pattern:
        request_parts.append(f"files matching {pattern}")
    else:
        request_parts.append("issues in this project")
    
    if type:
        request_parts.append(f"(focus on {type} issues)")
    
    request_text = " ".join(request_parts)
    
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style(f"[FIX] {target or 'project issues'}", fg="yellow", bold=True))
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


@code.command()
@click.argument('action', type=str, default='generate')
@click.argument('target', type=str, required=False)
@click.option('--framework', '-f', type=str, help='Testing framework to use')
@click.option('--coverage', is_flag=True, help='Include coverage analysis')
@click.option('--session', '-s', help='Session ID for context')
def test(action, target, framework, coverage, session):
    """Generate or run tests.
    
    Examples:
      metis code test generate calculator.py
      metis code test run
      metis code test generate --framework pytest
      metis code test run --coverage
    """
    if action == 'generate':
        if target:
            request_text = f"Generate tests for {target}"
        else:
            request_text = "Generate tests for this project"
        
        if framework:
            request_text += f" using {framework}"
    
    elif action == 'run':
        request_text = "Run the test suite"
        if coverage:
            request_text += " with coverage analysis"
    
    else:
        request_text = f"Test-related task: {action}" + (f" {target}" if target else "")
    
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style(f"[TEST] {action}" + (f" {target}" if target else ""), fg="blue", bold=True))
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


@code.command()
@click.argument('action', type=str, default='generate')
@click.argument('target', type=str, required=False)
@click.option('--format', '-f', type=str, help='Documentation format (markdown, rst, html)')
@click.option('--api', is_flag=True, help='Generate API documentation')
@click.option('--session', '-s', help='Session ID for context')
def docs(action, target, format, api, session):
    """Generate or manage documentation.
    
    Examples:
      metis code docs generate
      metis code docs generate api.py --format markdown
      metis code docs generate --api
      metis code docs update README.md
    """
    if action == 'generate':
        if api:
            request_text = "Generate API documentation for this project"
        elif target:
            request_text = f"Generate documentation for {target}"
        else:
            request_text = "Generate documentation for this project"
        
        if format:
            request_text += f" in {format} format"
    
    else:
        request_text = f"Documentation task: {action}" + (f" {target}" if target else "")
    
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style(f"[DOCS] {action}" + (f" {target}" if target else ""), fg="magenta", bold=True))
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


@code.command()
def status():
    """Show current project status and context.
    
    Examples:
      metis code status
    """
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    request_text = "Show me the current project status, structure, and important information"
    
    click.echo(click.style("[STATUS] Project Overview", fg="cyan", bold=True))
    return _handle_natural_language_request(agent, request_text, None, None, False, False)


@code.command()
@click.argument('file1', type=str, required=False)
@click.argument('file2', type=str, required=False)
@click.option('--branch', '-b', type=str, help='Compare with specific branch')
@click.option('--staged', is_flag=True, help='Show staged changes')
@click.option('--session', '-s', help='Session ID for context')
def diff(file1, file2, branch, staged, session):
    """Show differences between files or versions.
    
    Examples:
      metis code diff main.py
      metis code diff main.py backup.py
      metis code diff --staged
      metis code diff --branch main
    """
    if file1 and file2:
        request_text = f"Show the differences between {file1} and {file2}"
    elif file1:
        request_text = f"Show the changes in {file1}"
    elif branch:
        request_text = f"Show the differences compared to {branch} branch"
    elif staged:
        request_text = "Show the staged changes ready for commit"
    else:
        request_text = "Show the current changes in this project"
    
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style("[DIFF] Comparing changes", fg="yellow", bold=True))
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


@code.command()
@click.argument('message', type=str, required=False)
@click.option('--auto', '-a', is_flag=True, help='Auto-generate commit message')
@click.option('--session', '-s', help='Session ID for context')
def commit(message, auto, session):
    """Create a git commit with smart message generation.
    
    Examples:
      metis code commit \"add user authentication\"
      metis code commit --auto
      metis code commit (interactive message generation)
    """
    if auto:
        request_text = "Create a git commit with an automatically generated commit message based on the current changes"
    elif message:
        request_text = f"Create a git commit with this message: '{message}'"
    else:
        request_text = "Help me create a git commit with an appropriate commit message"
    
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style("[COMMIT] Creating git commit", fg="green", bold=True))
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


@code.command()
@click.option('--help-deployment', is_flag=True, help='Show deployment guidance')
@click.option('--session', '-s', help='Session ID for context')
def deploy(help_deployment, session):
    """Get deployment assistance and guidance.
    
    Examples:
      metis code deploy
      metis code deploy --help-deployment
    """
    if help_deployment:
        request_text = "Provide comprehensive deployment guidance and options for this project"
    else:
        request_text = "Help me deploy this project - analyze it and provide deployment recommendations"
    
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style("[DEPLOY] Deployment assistance", fg="blue", bold=True))
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


@code.command()
@click.argument('template_type', type=str, required=False)
@click.argument('title', nargs=-1, required=False)
@click.option('--interactive', '-i', is_flag=True, help='Interactive template generation')
@click.option('--from-code', is_flag=True, help='Generate from existing codebase')
@click.option('--sections', '-s', type=str, help='Specific sections to include')
@click.option('--format', '-f', type=str, help='Output format (markdown, html, pdf)')
@click.option('--export', type=str, help='Export to multiple formats (e.g., "pdf,html,docx")')
@click.option('--session', help='Session ID for context')
def md(template_type, title, interactive, from_code, sections, format, export, session):
    """Generate professional markdown documents from templates.
    
    Available Templates:
      prd         - Product Requirements Document
      design      - Technical Design Document  
      api         - API Documentation
      readme      - Enhanced README
      proposal    - Feature Proposal
      roadmap     - Project Roadmap
      review      - Code Review Template
      meeting     - Meeting Notes Template
      architecture - System Architecture Doc
      specs       - Technical Specifications
    
    Examples:
      metis code md prd "User Authentication System"
      metis code md design "Database Schema" --from-code
      metis code md api --sections "endpoints,models,auth"
      metis code md readme --export pdf,html
      metis code md list (show available templates)
    """
    # Handle special commands
    if template_type in ['list', 'templates']:
        _show_markdown_templates()
        return
    
    if not template_type:
        _show_markdown_templates()
        return
    
    # Available templates
    available_templates = {
        'prd': 'Product Requirements Document',
        'design': 'Technical Design Document',
        'api': 'API Documentation',
        'readme': 'Enhanced README',
        'proposal': 'Feature Proposal',
        'roadmap': 'Project Roadmap',
        'review': 'Code Review Template',
        'meeting': 'Meeting Notes Template',
        'architecture': 'System Architecture Document',
        'specs': 'Technical Specifications'
    }
    
    if template_type not in available_templates:
        click.echo(click.style(f"❌ Unknown template: {template_type}", fg="red"))
        click.echo("Available templates:")
        for template, desc in available_templates.items():
            click.echo(f"  • {template:<12} - {desc}")
        return
    
    # Build title
    title_text = ' '.join(title) if title else f"New {template_type.title()}"
    
    # Build the request for the markdown generation
    request_parts = [f"Generate a professional {available_templates[template_type]}"]
    
    if title_text != f"New {template_type.title()}":
        request_parts.append(f"with the title '{title_text}'")
    
    if interactive:
        request_parts.append("using an interactive step-by-step process")
    
    if from_code:
        request_parts.append("based on the existing codebase analysis")
    
    if sections:
        request_parts.append(f"focusing on these sections: {sections}")
    
    if format and format != 'markdown':
        request_parts.append(f"and format it as {format}")
    
    if export:
        export_formats = export.split(',')
        request_parts.append(f"and export to these formats: {', '.join(export_formats)}")
    
    request_text = " ".join(request_parts) + f". Use the {template_type} template structure."
    
    # Add specific template guidance
    template_guidance = _get_template_guidance(template_type)
    if template_guidance:
        request_text += f"\n\nTemplate Structure Guidance:\n{template_guidance}"
    
    config = AgentConfig()
    agent = _create_agent_with_tools(config)
    
    click.echo(click.style(f"[MARKDOWN] Generating {available_templates[template_type]}", fg="magenta", bold=True))
    click.echo(click.style(f"Title: {title_text}", fg="cyan"))
    
    return _handle_natural_language_request(agent, request_text, session, None, False, False)


# Command aliases for shorter usage
@code.command('e')
@click.argument('file_path', type=str)
@click.argument('description', nargs=-1, required=False)
@click.option('--line', '-l', type=int, help='Start editing at specific line number')
@click.option('--session', '-s', help='Session ID for context')
def edit_alias(file_path, description, line, session):
    """Alias for 'edit' command.
    
    Examples:
      metis code e main.py \"add logging\"
      metis code e utils.py --line 25
    """
    # Call the original edit function
    return edit.callback(file_path, description, line, session)


@code.command('c')
@click.argument('item_type', type=str)
@click.argument('name', type=str, required=False)
@click.option('--template', '-t', type=str, help='Use specific template (react, flask, etc.)')
@click.option('--session', '-s', help='Session ID for context')
def create_alias(item_type, name, template, session):
    """Alias for 'create' command.
    
    Examples:
      metis code c component UserCard
      metis code c file utils.py
    """
    # Call the original create function
    return create.callback(item_type, name, template, session)


@code.command('f')
@click.argument('target', type=str, required=False)
@click.option('--type', '-t', type=str, help='Type of issues to fix (syntax, logic, style)')
@click.option('--pattern', '-p', type=str, help='File pattern to fix (e.g., "*.py")')
@click.option('--session', '-s', help='Session ID for context')
def fix_alias(target, type, pattern, session):
    """Alias for 'fix' command.
    
    Examples:
      metis code f main.py
      metis code f --type syntax
    """
    # Call the original fix function
    return fix.callback(target, type, pattern, session)


@code.command('t')
@click.argument('action', type=str, default='generate')
@click.argument('target', type=str, required=False)
@click.option('--framework', '-f', type=str, help='Testing framework to use')
@click.option('--coverage', is_flag=True, help='Include coverage analysis')
@click.option('--session', '-s', help='Session ID for context')
def test_alias(action, target, framework, coverage, session):
    """Alias for 'test' command.
    
    Examples:
      metis code t generate calculator.py
      metis code t run --coverage
    """
    # Call the original test function
    return test.callback(action, target, framework, coverage, session)


@code.command('d')
@click.argument('action', type=str, default='generate')
@click.argument('target', type=str, required=False)
@click.option('--format', '-f', type=str, help='Documentation format (markdown, rst, html)')
@click.option('--api', is_flag=True, help='Generate API documentation')
@click.option('--session', '-s', help='Session ID for context')
def docs_alias(action, target, format, api, session):
    """Alias for 'docs' command.
    
    Examples:
      metis code d generate
      metis code d generate api.py
    """
    # Call the original docs function
    return docs.callback(action, target, format, api, session)


@code.command('s')
def status_alias():
    """Alias for 'status' command.
    
    Examples:
      metis code s
    """
    # Call the original status function
    return status.callback()


def _detect_subcommand_from_text(request_text):
    """Detect if natural language should be routed to a specific subcommand."""
    request_lower = request_text.lower().strip()
    
    # Prevent routing if input is too short or looks like it came from routing
    if len(request_text) < 10 or request_text.startswith('Create a s named') or request_text.startswith('s '):
        return None
    
    # File editing patterns
    edit_patterns = [
        r'edit (.+\.py|.+\.js|.+\.ts|.+\.java|.+\.cpp|.+\.c|.+\.rb|.+\.php|.+\.go|.+\.rs)\s*(.+)?',
        r'modify (.+\.py|.+\.js|.+\.ts|.+\.java|.+\.cpp|.+\.c|.+\.rb|.+\.php|.+\.go|.+\.rs)\s*(.+)?',
        r'change (.+\.py|.+\.js|.+\.ts|.+\.java|.+\.cpp|.+\.c|.+\.rb|.+\.php|.+\.go|.+\.rs)\s*(.+)?',
        r'update (.+\.py|.+\.js|.+\.ts|.+\.java|.+\.cpp|.+\.c|.+\.rb|.+\.php|.+\.go|.+\.rs)\s*(.+)?',
        r'fix (.+\.py|.+\.js|.+\.ts|.+\.java|.+\.cpp|.+\.c|.+\.rb|.+\.php|.+\.go|.+\.rs)\s*(.+)?'
    ]
    
    for pattern in edit_patterns:
        import re
        match = re.search(pattern, request_lower)
        if match:
            file_path = match.group(1)
            description = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""
            return ('edit', {'file_path': file_path, 'description': description.strip()})
    
    # Create/generation patterns - be more specific to avoid over-matching
    create_patterns = [
        # Specific patterns with "called/named" should match first
        r'create (?:a |an )?(.+?) (?:called|named) ["\']?([^"\']+)["\']?',
        r'generate (?:a |an )?(.+?) (?:called|named) ["\']?([^"\']+)["\']?',
        r'make (?:a |an )?(.+?) (?:called|named) ["\']?([^"\']+)["\']?',
        r'build (?:a |an )?(.+?) (?:called|named) ["\']?([^"\']+)["\']?',
        # More specific patterns for common creatable items
        r'create (?:a |an )?(class|function|component|module|file|script|app|project|database|table) (.+)?',
        r'generate (?:a |an )?(class|function|component|module|file|script|app|project|test|docs) (.+)?',
        r'make (?:a |an )?(class|function|component|module|file|script|app|project) (.+)?',
        r'build (?:a |an )?(class|function|component|module|file|script|app|project) (.+)?'
    ]
    
    for pattern in create_patterns:
        match = re.search(pattern, request_lower)
        if match:
            item_type = match.group(1).strip()
            name = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else ""
            
            # Filter out common non-creatable items for create command
            skip_items = ['error', 'issue', 'problem', 'solution', 'plan', 'strategy', 'approach', 'simple', 'basic', 'complex']
            if item_type not in skip_items and len(item_type) > 1:
                return ('create', {'item_type': item_type, 'name': name})
    
    # Fix patterns
    fix_patterns = [
        r'fix (?:the )?(?:syntax |logic |style )?(?:error|issue|problem|bug)s?\s*(?:in\s+(.+?))?',
        r'debug (?:the )?(.+?)',
        r'resolve (?:the )?(?:issue|problem|bug)s?\s*(?:in\s+(.+?))?',
        r'correct (?:the )?(.+?)'
    ]
    
    for pattern in fix_patterns:
        match = re.search(pattern, request_lower)
        if match:
            target = match.group(1).strip() if match.group(1) else None
            fix_type = None
            
            if 'syntax' in request_lower:
                fix_type = 'syntax'
            elif 'logic' in request_lower:
                fix_type = 'logic'
            elif 'style' in request_lower:
                fix_type = 'style'
            
            return ('fix', {'target': target, 'type': fix_type})
    
    # Test patterns
    test_patterns = [
        r'(?:generate|create|write|build|make) (?:unit |integration |e2e )?tests?\s*(?:for\s+(.+?))?',
        r'test (?:the )?(.+?)',
        r'run (?:the )?tests?\s*(.+)?'
    ]
    
    for pattern in test_patterns:
        match = re.search(pattern, request_lower)
        if match:
            if 'run' in request_lower:
                action = 'run'
                target = match.group(1).strip() if match.group(1) else None
            else:
                action = 'generate'
                target = match.group(1).strip() if match.group(1) else None
            
            return ('test', {'action': action, 'target': target})
    
    # Documentation patterns
    docs_patterns = [
        r'(?:generate|create|write|build|make) (?:api )?(?:documentation|docs)\s*(?:for\s+(.+?))?',
        r'document (?:the )?(.+?)',
        r'create (?:a )?readme\s*(.+)?',
        r'generate (?:a )?readme\s*(.+)?'
    ]
    
    for pattern in docs_patterns:
        match = re.search(pattern, request_lower)
        if match:
            target = match.group(1).strip() if match.group(1) else None
            api_flag = 'api' in request_lower
            
            return ('docs', {'action': 'generate', 'target': target, 'api': api_flag})
    
    # Status/analysis patterns
    status_patterns = [
        r'show (?:me )?(?:the )?(?:project |current )?(?:status|state|info|information)',
        r'analyze (?:the )?(?:project|codebase|code)',
        r'what is (?:the )?(?:project |current )?(?:status|state)',
        r'project (?:status|overview|info|information)',
        r'current (?:status|state|info)'
    ]
    
    for pattern in status_patterns:
        match = re.search(pattern, request_lower)
        if match:
            return ('status', {})
    
    # Markdown generation patterns
    md_patterns = [
        r'(?:generate|create|write|make) (?:a |an )?(?:prd|design|api|readme|proposal|roadmap|review|meeting|architecture|specs) (?:document|doc)?\s*["\']?(.+?)["\']?',
        r'create (?:a |an )?(?:product requirements document|technical design document|api documentation)\s*["\']?(.+?)["\']?'
    ]
    
    for pattern in md_patterns:
        match = re.search(pattern, request_lower)
        if match:
            title = match.group(1).strip() if match.group(1) else ""
            
            # Determine template type
            template_type = None
            if 'prd' in request_lower or 'product requirements' in request_lower:
                template_type = 'prd'
            elif 'design' in request_lower or 'technical design' in request_lower:
                template_type = 'design'
            elif 'api' in request_lower and ('doc' in request_lower or 'documentation' in request_lower):
                template_type = 'api'
            elif 'readme' in request_lower:
                template_type = 'readme'
            elif 'proposal' in request_lower:
                template_type = 'proposal'
            elif 'roadmap' in request_lower:
                template_type = 'roadmap'
            elif 'review' in request_lower:
                template_type = 'review'
            elif 'meeting' in request_lower:
                template_type = 'meeting'
            elif 'architecture' in request_lower:
                template_type = 'architecture'
            elif 'specs' in request_lower or 'specification' in request_lower:
                template_type = 'specs'
            
            if template_type:
                return ('md', {'template_type': template_type, 'title': title})
    
    return None


def _determine_operation_mode(request_text, auto=False, fast=False, stream=False):
    """Determine the optimal operation mode based on flags and request complexity."""
    # Explicit mode flags take precedence
    if fast:
        return 'fast'
    if stream:
        return 'stream'
    if auto:
        return 'auto'
    
    # Auto-detect based on request complexity
    operation_complexity = _assess_operation_complexity(request_text)
    
    if operation_complexity <= 0.3:  # Simple operations
        return 'fast'
    elif operation_complexity >= 0.7:  # Complex operations
        return 'stream'
    else:
        return 'balanced'


def _assess_operation_complexity(request_text):
    """Assess the complexity of an operation to determine optimal mode."""
    request_lower = request_text.lower()
    complexity_score = 0.0
    
    # Simple operation indicators (reduce complexity)
    simple_indicators = [
        'edit', 'modify', 'change', 'update', 'fix', 'add', 'remove',
        'delete', 'rename', 'copy', 'move', 'format', 'lint'
    ]
    if any(indicator in request_lower for indicator in simple_indicators):
        complexity_score -= 0.2
    
    # File-specific operations are usually simple
    if any(ext in request_lower for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']):
        complexity_score -= 0.3
    
    # Complex operation indicators (increase complexity)
    complex_indicators = [
        'create project', 'build application', 'generate system', 'implement architecture',
        'design database', 'create api', 'full stack', 'microservice', 'deployment',
        'infrastructure', 'dockerize', 'kubernetes', 'ci/cd', 'pipeline'
    ]
    for indicator in complex_indicators:
        if indicator in request_lower:
            complexity_score += 0.4
    
    # Multiple components increase complexity
    component_keywords = ['and', 'with', 'including', 'plus', 'also']
    for keyword in component_keywords:
        if keyword in request_lower:
            complexity_score += 0.2
    
    # Long requests are typically more complex
    word_count = len(request_text.split())
    if word_count > 15:
        complexity_score += 0.3
    elif word_count < 6:
        complexity_score -= 0.2
    
    # Normalize to 0-1 range
    return max(0.0, min(1.0, complexity_score + 0.5))


def _determine_confirmation_level(operation_mode, yes=False, review=False):
    """Determine the confirmation level based on flags and operation mode."""
    if review:
        return 'verbose'  # Force detailed confirmations
    elif yes:
        return 'minimal'  # Skip confirmations, use smart defaults
    elif operation_mode == 'fast':
        return 'minimal'  # Fast mode defaults to minimal confirmations
    elif operation_mode == 'stream':
        return 'verbose'  # Streaming mode defaults to detailed confirmations
    else:
        return 'normal'   # Balanced confirmations


def _determine_interface_mode(interface_flag=None, user_experience_level=None):
    """Determine interface complexity level for progressive disclosure."""
    if interface_flag:
        return interface_flag  # Explicit flag overrides everything
    
    # Auto-detect based on user experience (could be enhanced with usage analytics)
    if user_experience_level:
        return user_experience_level
    
    # Default to simple for new users
    return 'simple'


def _get_interface_appropriate_help(interface_mode, command_context='general'):
    """Return help content appropriate for the user's interface level."""
    if interface_mode == 'simple':
        return _get_simple_help(command_context)
    elif interface_mode == 'advanced':
        return _get_advanced_help(command_context)
    elif interface_mode == 'expert':
        return _get_expert_help(command_context)
    else:
        return _get_simple_help(command_context)  # Default fallback


def _get_simple_help(context='general'):
    """Simple interface help - basic commands only."""
    if context == 'general':
        return """Simple Commands:
  metis code "describe what you want to do"     - Natural language requests
  metis code edit <file> "what to change"      - Edit existing files  
  metis code create <type> <name>              - Create new files/components
  metis code fix <file>                        - Fix errors in files
  
Examples:
  metis code "add a login form to my app"
  metis code edit main.py "add error handling"
  metis code create component LoginForm
  metis code fix app.py

Type --help --advanced to see more options"""
    return ""


def _get_advanced_help(context='general'):
    """Advanced interface help - includes more sophisticated commands."""
    if context == 'general':
        return """Advanced Commands:
  metis code [natural language]                - Natural language requests
  metis code edit <file> [description]         - Edit files with optional description
  metis code create <type> [name] [options]    - Create files/components/projects
  metis code fix [file/pattern] [--type TYPE]  - Fix errors with specific types
  metis code test [action] [target]            - Generate/run tests
  metis code docs [action] [target]            - Generate documentation
  metis code status                            - Show project status
  metis code md <template> [title]             - Generate markdown documents
  
Operation Modes:
  --fast     - Quick operations with minimal prompts
  --stream   - Detailed streaming interface
  --yes      - Skip confirmations
  --review   - Force detailed confirmations
  
Advanced Examples:
  metis code fix --type syntax src/
  metis code test generate calculator.py
  metis code md prd "User Authentication System"
  
Type --help --expert to see all features"""
    return ""


def _get_expert_help(context='general'):
    """Expert interface help - shows all available commands and advanced features.""" 
    if context == 'general':
        return """Expert Commands (All Features):
  metis code [natural language]                - Natural language requests
  metis code edit <file> [desc] [options]      - Advanced file editing
  metis code create <type> [name] [options]    - Full creation options
  metis code fix [pattern] [--type TYPE]       - Pattern-based fixes
  metis code test [action] [target] [options]  - Comprehensive testing
  metis code docs [action] [target] [options]  - Documentation generation
  metis code status [--detailed]               - Detailed project status
  metis code md <template> [title] [options]   - Template-based markdown
  metis code diff [file1] [file2]             - Show differences
  metis code commit [message] [options]        - Smart git commits
  metis code deploy [environment]              - Deployment assistance
  
Advanced Modes & Configuration:
  --fast / --stream / --auto                  - Operation modes
  --yes / --review                            - Confirmation levels  
  --interface simple/advanced/expert          - Interface complexity
  --session <id> --branch <name>              - Session management
  
Pattern Operations:
  metis code fix --type syntax "src/**/*.py"  - Pattern-based syntax fixes
  metis code docs --pattern "api/*.py"        - Generate docs for patterns
  metis code edit "**/*.ts" "add type safety" - Bulk edits with patterns
  
Markdown Templates:
  prd, design, api, readme, proposal, roadmap, review, meeting
  
Slash Commands (in interactive mode):
  /edit, /create, /fix, /test, /docs, /md, /commit, /status, /help, /exit
  
Expert Examples:
  metis code --fast --yes create microservice UserService
  metis code --stream --review fix "src/**/*.py" --type performance  
  metis code md api "REST API v2" --sections "endpoints,auth,errors"
  
Configuration:
  Set permanent preferences with metis config set interface_mode=expert"""
    return ""


def _route_to_subcommand(subcommand, params, session=None, operation_mode='balanced', confirmation_level='normal'):
    """Route to the appropriate subcommand based on detected intent."""
    try:
        # Store mode for subcommand use
        params['_operation_mode'] = operation_mode
        
        if subcommand == 'edit':
            file_path = params.get('file_path', '')
            description = params.get('description', '').split() if params.get('description') else []
            return _execute_with_mode(edit.callback, operation_mode, file_path, description, None, session)
        
        elif subcommand == 'create':
            item_type = params.get('item_type', '')
            name = params.get('name', '') or None
            return _execute_with_mode(create.callback, operation_mode, item_type, name, None, session)
        
        elif subcommand == 'fix':
            target = params.get('target') or None
            fix_type = params.get('type') or None
            return _execute_with_mode(fix.callback, operation_mode, target, fix_type, None, session)
        
        elif subcommand == 'test':
            action = params.get('action', 'generate')
            target = params.get('target') or None
            return _execute_with_mode(test.callback, operation_mode, action, target, None, False, session)
        
        elif subcommand == 'docs':
            action = params.get('action', 'generate')
            target = params.get('target') or None
            api_flag = params.get('api', False)
            return _execute_with_mode(docs.callback, operation_mode, action, target, None, api_flag, session)
        
        elif subcommand == 'status':
            return _execute_with_mode(status.callback, operation_mode)
        
        elif subcommand == 'md':
            template_type = params.get('template_type', '')
            title = params.get('title', '').split() if params.get('title') else []
            return _execute_with_mode(md.callback, operation_mode, template_type, title, False, False, None, None, None, session)
        
        else:
            raise ValueError(f"Unknown subcommand: {subcommand}")
    
    except Exception as e:
        raise ValueError(f"Failed to route to {subcommand}: {str(e)}")


def _execute_with_mode(callback_func, operation_mode, *args, **kwargs):
    """Execute a subcommand callback with mode-specific optimizations."""
    if operation_mode == 'fast':
        # Fast mode: minimal output, direct execution
        start_time = time.time()
        result = callback_func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time < 2.0:
            click.echo(click.style(f"✓ Completed in {execution_time:.1f}s", fg="green"))
        
        return result
    else:
        # Normal execution for other modes
        return callback_func(*args, **kwargs)


def _show_markdown_templates():
    """Show available markdown templates with descriptions."""
    if RICH_AVAILABLE:
        console = Console()
        
        template_table = Table(title="📋 Available Markdown Templates")
        template_table.add_column("Template", style="cyan", no_wrap=True)
        template_table.add_column("Description", style="white")
        template_table.add_column("Use Cases", style="dim")
        
        templates_info = [
            ("prd", "Product Requirements Document", "Feature specs, user stories, requirements"),
            ("design", "Technical Design Document", "Architecture, system design, technical specs"),
            ("api", "API Documentation", "REST APIs, endpoints, request/response formats"),
            ("readme", "Enhanced README", "Project overview, setup instructions, usage"),
            ("proposal", "Feature Proposal", "New feature requests, enhancement proposals"),
            ("roadmap", "Project Roadmap", "Development timeline, milestones, planning"),
            ("review", "Code Review Template", "PR reviews, code quality assessments"),
            ("meeting", "Meeting Notes Template", "Meeting minutes, action items, decisions"),
            ("architecture", "System Architecture Document", "High-level design, component diagrams"),
            ("specs", "Technical Specifications", "Detailed technical requirements")
        ]
        
        for template, desc, use_cases in templates_info:
            template_table.add_row(template, desc, use_cases)
        
        console.print(template_table)
        
        # Usage examples
        examples_table = Table(title="💡 Usage Examples")
        examples_table.add_column("Command", style="green")
        examples_table.add_column("Description", style="white")
        
        examples = [
            ("metis code md prd \"User Auth\"", "Generate PRD for user authentication"),
            ("metis code md design --from-code", "Create design doc from codebase"),
            ("metis code md api --sections endpoints", "API docs focusing on endpoints"),
            ("metis code md readme --export pdf,html", "README with multi-format export"),
            ("metis code md proposal --interactive", "Interactive feature proposal")
        ]
        
        for cmd, desc in examples:
            examples_table.add_row(cmd, desc)
        
        console.print(examples_table)
        
    else:
        # Fallback for non-Rich environments
        click.echo(click.style("📋 Available Markdown Templates", fg="cyan", bold=True))
        click.echo("=" * 50)
        
        templates_info = [
            ("prd", "Product Requirements Document"),
            ("design", "Technical Design Document"),
            ("api", "API Documentation"),
            ("readme", "Enhanced README"),
            ("proposal", "Feature Proposal"),
            ("roadmap", "Project Roadmap"),
            ("review", "Code Review Template"),
            ("meeting", "Meeting Notes Template"),
            ("architecture", "System Architecture Document"),
            ("specs", "Technical Specifications")
        ]
        
        for template, desc in templates_info:
            click.echo(f"  • {template:<12} - {desc}")
        
        click.echo("\n" + click.style("💡 Usage Examples:", fg="green", bold=True))
        click.echo('  metis code md prd "User Authentication System"')
        click.echo('  metis code md design "Database Schema" --from-code')
        click.echo('  metis code md api --sections "endpoints,models,auth"')
        click.echo('  metis code md readme --export pdf,html')


def _get_template_guidance(template_type):
    """Get specific guidance for each template type."""
    guidance = {
        'prd': """
# Product Requirements Document Structure:
- Executive Summary (problem statement, solution overview)
- User Stories & Use Cases 
- Functional Requirements (detailed features)
- Non-Functional Requirements (performance, security, etc.)
- Success Metrics & KPIs
- Implementation Timeline
- Risk Assessment & Mitigation
- Acceptance Criteria
""",
        'design': """
# Technical Design Document Structure:
- System Overview & Architecture
- Component Design & Interactions
- Data Models & Database Schema
- API Design & Interfaces
- Security Considerations
- Performance Requirements
- Technology Stack & Dependencies
- Implementation Plan
- Testing Strategy
""",
        'api': """
# API Documentation Structure:
- API Overview & Purpose
- Authentication & Authorization
- Endpoint Reference (with examples)
- Request/Response Schemas
- Error Handling & Status Codes
- Rate Limiting & Quotas
- SDK & Client Libraries
- Changelog & Versioning
""",
        'readme': """
# Enhanced README Structure:
- Project Title & Description
- Features & Capabilities
- Installation & Setup Instructions
- Usage Examples & Code Samples
- Configuration Options
- API Reference (if applicable)
- Contributing Guidelines
- License & Legal Information
""",
        'proposal': """
# Feature Proposal Structure:
- Problem Statement & Motivation
- Proposed Solution & Approach
- Implementation Details
- User Experience & Interface Changes
- Technical Considerations
- Testing Plan & Quality Assurance
- Timeline & Milestones
- Success Metrics & Measurement
""",
        'roadmap': """
# Project Roadmap Structure:
- Vision & Strategic Goals
- Current State Assessment
- Development Phases & Milestones
- Feature Prioritization Matrix
- Timeline & Dependencies
- Resource Allocation
- Risk Management
- Communication Plan
""",
        'review': """
# Code Review Template Structure:
- Review Summary & Overview
- Code Quality Assessment
- Architecture & Design Feedback
- Security & Performance Considerations
- Test Coverage & Quality
- Documentation Review
- Recommendations & Action Items
- Approval Status & Next Steps
""",
        'meeting': """
# Meeting Notes Structure:
- Meeting Information (date, attendees, purpose)
- Agenda Items & Discussion Points
- Key Decisions Made
- Action Items & Assignments
- Next Steps & Follow-ups
- Parking Lot Items
- Meeting Summary
- Next Meeting Details
""",
        'architecture': """
# System Architecture Document Structure:
- System Overview & Context
- High-Level Architecture Diagram
- Component Breakdown & Responsibilities
- Data Flow & Communication Patterns
- Technology Stack & Infrastructure
- Scalability & Performance Considerations
- Security Architecture
- Deployment & Operations
""",
        'specs': """
# Technical Specifications Structure:
- Specification Overview & Scope
- Detailed Requirements
- Technical Constraints & Assumptions
- System Behavior & Logic
- Interface Specifications
- Data Formats & Protocols
- Error Handling & Edge Cases
- Compliance & Standards
"""
    }
    
    return guidance.get(template_type, "")


def _create_agent_with_tools(config):
    """Create agent with all available tools."""
    # Initialize tools registry
    tools_registry = {}
    
    # Add tools that were successfully imported
    if WriteTool:
        tools_registry['WriteTool'] = WriteTool()
    if ProjectManagementTool:
        tools_registry['ProjectManagementTool'] = ProjectManagementTool()
    if ReadTool:
        tools_registry['ReadTool'] = ReadTool()
    if GrepTool:
        tools_registry['GrepTool'] = GrepTool()
    if FileManagerTool:
        tools_registry['FileManagerTool'] = FileManagerTool()
    if BashTool:
        tools_registry['BashTool'] = BashTool()
    if E2BCodeSandboxTool:
        tools_registry['E2BCodeSandboxTool'] = E2BCodeSandboxTool()
    if ProjectAnalyzerTool:
        tools_registry['ProjectAnalyzerTool'] = ProjectAnalyzerTool()
    
    # Convert tools registry to list for agent
    tools_list = list(tools_registry.values())
    
    # Initialize agent with config settings and tools
    agent = SingleAgent(
        use_titans_memory=config.is_titans_memory_enabled(),
        llm_provider=config.get_llm_provider(),
        llm_model=config.get_llm_model(),
        enhanced_processing=False,  # Use direct processing for streaming
        config=config,
        tools=tools_list  # Pass tools to agent
    )
    
    return agent


# Export the main command
def _is_complete_project_request(request_text: str) -> bool:
    """Determine if request should use complete project development blueprint."""
    request_lower = request_text.lower()
    
    # Keywords that indicate complete project development
    project_keywords = [
        'create', 'build', 'make', 'develop', 'generate'
    ]
    
    app_keywords = [
        'app', 'application', 'project', 'system', 'tool', 'website', 'service'
    ]
    
    # Check if request contains project creation keywords + app type
    has_project_keyword = any(keyword in request_lower for keyword in project_keywords)
    has_app_keyword = any(keyword in request_lower for keyword in app_keywords)
    
    # Also check for specific project types
    project_types = [
        'todo app', 'calculator', 'web app', 'api', 'dashboard', 'bot', 'game',
        'cli tool', 'desktop app', 'mobile app', 'microservice'
    ]
    
    has_project_type = any(proj_type in request_lower for proj_type in project_types)
    
    return (has_project_keyword and has_app_keyword) or has_project_type


def _handle_metis_code_workflow(agent, request_text: str, project_context: str, auto: bool = False) -> None:
    """Handle Metis Code multi-phase interactive development workflow using SingleAgent."""
    if auto:
        click.echo(click.style("[AUTO MODE] Building your app automatically...", fg="yellow", bold=True))
        click.echo("I'll create your app without asking questions - using smart defaults.")
    else:
        click.echo(click.style("Hi! I'm excited to help you build your app.", fg="cyan"))
        click.echo("Let's work together to create something amazing - I'll guide you through each step.")
    click.echo()
    
    # Generate a meaningful project name based on the user's request
    project_name = generate_project_name(request_text)
    
    try:
        # Phase 1: Design - Let the agent analyze and ask clarifying questions
        click.echo("\nFirst, let me understand what you want to build...")
        
        design_prompt = f"""
I need to help the user build an application. Here's their request: "{request_text}"

Please:
1. Analyze their request and identify what type of application they want
2. Ask 2-3 specific clarifying questions to better understand their needs
3. Suggest a technology stack and project structure
4. Create a brief project plan

Be conversational and helpful. Focus on understanding their exact requirements before we start coding.
"""
        
        click.echo("Analyzing your request...")
        design_response = agent.process_query(design_prompt)
        
        click.echo("\nMetis:")
        if isinstance(design_response, dict):
            click.echo(design_response.get("response", str(design_response)))
        else:
            click.echo(design_response)
        
        # Get user's clarifications
        click.echo("\n" + "="*50)
        if auto:
            click.echo("\nContinuing with default settings...")
            user_clarifications = ""
        else:
            try:
                user_clarifications = input("\nPlease answer the questions above (or press Enter to continue): ").strip()
            except (EOFError, KeyboardInterrupt):
                click.echo("\nContinuing with default settings...")
                user_clarifications = ""
        
        # Phase 2: Code Creation - Let the agent create the project
        if auto or click.confirm("\nShall we start building your app now?", default=True):
            click.echo("\nGreat! Now let's bring your app to life with code...")
            
            code_prompt = f"""
Now I need to create the actual application code and project structure.

Original request: "{request_text}"
User clarifications: "{user_clarifications or 'None provided'}"
Project context: {project_context}
Suggested project name: "{project_name}"

Please:
1. Create a complete project structure with all necessary files
2. Generate working code for their application
3. Include proper documentation and setup instructions
4. Show the exact file paths and what was created
5. Provide instructions on how to run the application

Use the ProjectManagementTool to create the actual project files. Use the suggested project name "{project_name}" for the project directory. Be specific about file locations and contents.

IMPORTANT: At the end of your response, clearly state the main project directory path in this format:
"PROJECT_LOCATION: [full path to project directory]"
"""
            
            click.echo("Creating your application...")
            code_response = agent.process_query(code_prompt)
            
            click.echo("\nMetis:")
            if isinstance(code_response, dict):
                click.echo(code_response.get("response", str(code_response)))
            else:
                click.echo(code_response)
            
            # Phase 3: Iteration - Let the agent improve and polish
            if auto or click.confirm("\nWould you like me to improve and polish your app?", default=True):
                click.echo("\nTime to polish and improve your app...")
                
                iteration_prompt = f"""
The application has been created. Now I need to improve and polish it.

Original request: "{request_text}"
User clarifications: "{user_clarifications or 'None provided'}"
Project name: "{project_name}"

Please:
1. Review the created project and identify areas for improvement
2. Add error handling, validation, and best practices
3. Enhance the user interface and user experience
4. Add tests if appropriate
5. Provide final setup and deployment instructions
6. Show the final project structure and how to use it

Focus on making the application production-ready and user-friendly.
"""
                
                click.echo("Polishing your application...")
                iteration_response = agent.process_query(iteration_prompt)
                
                click.echo("\nMetis:")
                if isinstance(iteration_response, dict):
                    click.echo(iteration_response.get("response", str(iteration_response)))
                else:
                    click.echo(iteration_response)
        
        # Extract project location from the agent's responses
        project_location = None
        
        # Try to find project path in the responses
        try:
            responses_to_check = []
            if 'design_response' in locals():
                responses_to_check.append(design_response)
            if 'code_response' in locals():
                responses_to_check.append(code_response)
            if 'iteration_response' in locals():
                responses_to_check.append(iteration_response)
            
            for response in responses_to_check:
                if not response:
                    continue
                    
                try:
                    if isinstance(response, dict):
                        response_text = response.get("response", "")
                    else:
                        response_text = str(response)
                    
                    # Look for common project path patterns
                    import re
                    path_patterns = [
                        r'PROJECT_LOCATION:\s*([^\n]+)',  # Our structured format
                        r'(?:Created|Project).*?(?:at|in):?\s*([C-Z]:\\[^\n\s]+)',  # Windows paths
                        r'(?:Created|Project).*?(?:at|in):?\s*(/[^\n\s]+)',  # Unix paths
                        r'(?:find all your files at|located at):?\s*([C-Z]:\\[^\n\s]+)',  # Common phrases
                        r'(?:find all your files at|located at):?\s*(/[^\n\s]+)',
                        r'([C-Z]:\\Users\\[^\\]+\\Desktop\\[^\\\s\n]+)',  # Direct Windows desktop paths
                        r'(/Users/[^/]+/Desktop/[^/\s\n]+)'  # Direct Unix desktop paths
                    ]
                    
                    for pattern in path_patterns:
                        try:
                            matches = re.findall(pattern, response_text, re.IGNORECASE)
                            if matches:
                                # Clean up the match
                                potential_path = matches[0].strip()
                                if len(potential_path) > 5 and ('\\' in potential_path or '/' in potential_path):
                                    project_location = potential_path
                                    break
                        except Exception:
                            continue
                    
                    if project_location:
                        break
                        
                except Exception:
                    continue
                    
        except Exception:
            pass  # Silently handle any extraction errors
        
        # Display completion message with project location
        click.echo(click.style("\nPerfect! Your app is complete and ready to use!", fg="green", bold=True))
        
        if project_location:
            click.echo(click.style(f"\nProject Location: {project_location}", fg="cyan", bold=True))
            click.echo(f"You can find all your files at: {project_location}")
        else:
            click.echo("Check the output above for your project location.")
        
        click.echo("\nHappy coding!")
        
    except KeyboardInterrupt:
        click.echo("\nWorkflow interrupted by user.")
    except Exception as e:
        click.echo(click.style(f"\nError in Metis Code workflow: {str(e)}", fg="red"))

def _handle_blueprint_project_development(agent, request_text: str, project_context: str) -> None:
    """Handle complete project development using enhanced blueprint workflow."""
    click.echo(click.style("[BLUEPRINT WORKFLOW] Detected complete project development request", fg="magenta", bold=True))
    click.echo("Initiating enhanced blueprint development workflow...\n")
    
    try:
        # Import and directly execute BlueprintExecutionTool
        from ..tools.core_tools.blueprint_execution_tool import BlueprintExecutionTool
        
        click.echo(click.style("[BLUEPRINT] Initializing BlueprintExecutionTool...", fg="blue"))
        blueprint_tool = BlueprintExecutionTool()
        
        # Prepare inputs for enhanced workflow
        inputs = {
            "project_request": request_text,
            "skip_questions": False,
            "auto_implement": True,
            "desktop_path": "~/Desktop"
        }
        
        click.echo(click.style(f"[BLUEPRINT] Executing enhanced 'complete_project_development' blueprint...", fg="blue"))
        click.echo(f"Project Request: {request_text}")
        click.echo("Parameters: skip_questions=False, auto_implement=True\n")
        
        # Execute blueprint
        result = blueprint_tool.execute(
            task="execute complete project development blueprint",
            blueprint_name="complete_project_development",
            inputs=inputs
        )
        
        # Display results
        if result.get('success', False):
            click.echo(click.style("[SUCCESS] Blueprint executed successfully!", fg="green", bold=True))
            
            exec_result = result.get('execution_result', {})
            if exec_result.get('success', False):
                click.echo(click.style("[BLUEPRINT COMPLETED] All workflow steps completed!", fg="green"))
                
                # Show outputs if available
                outputs = result.get('outputs', {})
                if outputs:
                    click.echo("\n" + click.style("[OUTPUTS]", fg="cyan", bold=True))
                    for key, value in outputs.items():
                        click.echo(f"  {key}: {value}")
                        
                # Show step summary
                step_results = exec_result.get('step_results', {})
                if step_results:
                    click.echo("\n" + click.style("[STEP SUMMARY]", fg="cyan", bold=True))
                    for step_id, step_result in step_results.items():
                        status = "[SUCCESS]" if step_result.get('success', False) else "[FAILED]"
                        click.echo(f"  {status} {step_id}")
                        
            else:
                click.echo(click.style("[BLUEPRINT FAILED] Workflow execution failed", fg="red", bold=True))
                error = exec_result.get('error', 'Unknown error')
                click.echo(f"Error: {error}")
                
                # Show failed steps
                step_results = exec_result.get('step_results', {})
                for step_id, step_result in step_results.items():
                    if not step_result.get('success', False):
                        click.echo(f"[FAILED] {step_id}: {step_result.get('error', 'Failed')}")
        else:
            click.echo(click.style("[ERROR] Blueprint tool execution failed", fg="red", bold=True))
            error = result.get('error', 'Unknown error')
            click.echo(f"Error: {error}")
            
    except Exception as e:
        click.echo(click.style(f"[CRITICAL ERROR] Blueprint execution failed: {str(e)}", fg="red", bold=True))
        import traceback
        click.echo(traceback.format_exc())


__all__ = ['code']