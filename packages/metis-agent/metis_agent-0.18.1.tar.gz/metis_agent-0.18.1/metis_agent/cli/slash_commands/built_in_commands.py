"""
Built-in Slash Commands for Metis Agent

Core slash commands that come with the system.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

from .registry import SlashCommand, SlashCommandRegistry


class HelpCommand(SlashCommand):
    """Show help for slash commands."""
    
    def __init__(self):
        super().__init__(
            "help", 
            "Show help for available slash commands",
            "/help [command_name]"
        )
        self.category = "General"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        
        if remaining_text:
            # Show help for specific command
            registry = context.get("registry")
            if registry and registry.has_command(remaining_text):
                command = registry.get_command(remaining_text)
                return {
                    "success": True,
                    "response": command.get_help(),
                    "type": "help"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown command: /{remaining_text}"
                }
        else:
            # Show general help - get registry from context
            registry = context.get("registry")
            if registry:
                commands = registry.get_commands_by_category()
                help_text = self._format_help(commands)
            else:
                # Fallback - create basic help
                help_text = "Available Slash Commands:\n\n"
                help_text += "General:\n"
                help_text += "  /help\n  /clear\n  /project\n  /model\n\n"
                help_text += "Development:\n"
                help_text += "  /edit\n  /read\n  /commit\n  /status\n  /review\n\n"
                help_text += "Agent Management:\n"
                help_text += "  /agent\n  /agents\n\n"
                help_text += "Use /help <command> for detailed information about a specific command."
            
            return {
                "success": True,
                "response": help_text,
                "type": "help"
            }
    
    def _format_help(self, commands: Dict[str, List[str]]) -> str:
        """Format help text with command categories."""
        help_text = "Available Slash Commands:\n\n"
        
        for category, command_list in commands.items():
            if command_list:
                help_text += f"{category}:\n"
                for cmd in sorted(command_list):
                    help_text += f"  /{cmd}\n"
                help_text += "\n"
        
        help_text += "Use /help <command> for detailed information about a specific command.\n"
        help_text += "Example: /help review"
        
        return help_text


class ClearCommand(SlashCommand):
    """Clear the screen."""
    
    def __init__(self):
        super().__init__(
            "clear",
            "Clear the terminal screen",
            "/clear"
        )
        self.category = "General"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        os.system('cls' if os.name == 'nt' else 'clear')
        return {
            "success": True,
            "response": "Screen cleared",
            "type": "action",
            "action": "clear_screen"
        }


class AgentCommand(SlashCommand):
    """Switch to a specific agent."""
    
    def __init__(self):
        super().__init__(
            "agent",
            "Switch to a specific agent",
            "/agent <agent_id>"
        )
        self.category = "Agent Management"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        agent_manager = context.get("agent_manager")
        
        if not remaining_text:
            return {
                "success": False,
                "error": "Please specify an agent ID. Usage: /agent <agent_id>"
            }
        
        if not agent_manager:
            return {
                "success": False,
                "error": "Multi-agent system not available"
            }
        
        try:
            agent = agent_manager.get_agent(remaining_text)
            if agent:
                agent_manager.switch_active_agent(remaining_text)
                agent_info = agent_manager.get_agent_info(remaining_text)
                return {
                    "success": True,
                    "response": f"Switched to agent: {remaining_text} ({agent_info.get('profile_name', 'unknown')})",
                    "type": "agent_switch",
                    "agent_id": remaining_text
                }
            else:
                return {
                    "success": False,
                    "error": f"Agent '{remaining_text}' not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error switching to agent: {e}"
            }


class AgentsCommand(SlashCommand):
    """List available agents."""
    
    def __init__(self):
        super().__init__(
            "agents",
            "List all available agents",
            "/agents"
        )
        self.category = "Agent Management"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent_manager = context.get("agent_manager")
        
        if not agent_manager:
            return {
                "success": False,
                "error": "Multi-agent system not available"
            }
        
        try:
            agents = agent_manager.list_agents()
            if agents:
                agent_list = []
                for agent_id in agents:
                    agent_info = agent_manager.get_agent_info(agent_id)
                    agent_list.append({
                        "id": agent_id,
                        "profile": agent_info.get('profile_name', 'unknown'),
                        "status": agent_info.get('status', 'unknown')
                    })
                
                return {
                    "success": True,
                    "response": "Available agents listed",
                    "type": "agent_list",
                    "agents": agent_list
                }
            else:
                return {
                    "success": True,
                    "response": "No agents found. Create agents with: metis agents create <agent_id>",
                    "type": "agent_list",
                    "agents": []
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing agents: {e}"
            }


class ReviewCommand(SlashCommand):
    """Review code or files."""
    
    def __init__(self):
        super().__init__(
            "review",
            "Review code, files, or recent changes",
            "/review [file_path | @agent_id]"
        )
        self.category = "Development"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        current_agent = context.get("current_agent")
        agent_manager = context.get("agent_manager")
        
        # Check for @agent mention
        if remaining_text.startswith('@'):
            parts = remaining_text.split(' ', 1)
            agent_id = parts[0][1:]  # Remove @
            review_target = parts[1] if len(parts) > 1 else "recent changes"
            
            if agent_manager:
                try:
                    agent = agent_manager.get_agent(agent_id)
                    if agent:
                        query = f"Please review {review_target}"
                        response = agent.process_query(query)
                        return {
                            "success": True,
                            "response": response.get("response", str(response)) if isinstance(response, dict) else str(response),
                            "type": "agent_response",
                            "agent_id": agent_id
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Agent '{agent_id}' not found"
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Error consulting agent: {e}"
                    }
            else:
                return {
                    "success": False,
                    "error": "Multi-agent system not available"
                }
        else:
            # Use current agent or default behavior
            target = remaining_text if remaining_text else "recent changes"
            query = f"Please review {target}"
            
            if current_agent:
                try:
                    response = current_agent.process_query(query)
                    return {
                        "success": True,
                        "response": response.get("response", str(response)) if isinstance(response, dict) else str(response),
                        "type": "review_response"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Error during review: {e}"
                    }
            else:
                return {
                    "success": False,
                    "error": "No agent available for review"
                }


class ProjectCommand(SlashCommand):
    """Show project status and information."""
    
    def __init__(self):
        super().__init__(
            "project",
            "Show project status and configuration",
            "/project [status | config | init]"
        )
        self.category = "Project"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        project_config = context.get("project_config", {})
        
        if remaining_text == "config":
            # Show .metis configuration
            if project_config:
                config_text = "Project Configuration (.metis):\n\n"
                for section, content in project_config.items():
                    config_text += f"{section}:\n"
                    if isinstance(content, dict):
                        for key, value in content.items():
                            config_text += f"  {key}: {value}\n"
                    else:
                        config_text += f"  {content}\n"
                    config_text += "\n"
                
                return {
                    "success": True,
                    "response": config_text,
                    "type": "project_config"
                }
            else:
                return {
                    "success": True,
                    "response": "No .metis configuration found in current directory",
                    "type": "project_config"
                }
        
        elif remaining_text == "init":
            # Initialize .metis file
            metis_file = Path.cwd() / ".metis"
            if metis_file.exists():
                return {
                    "success": False,
                    "error": ".metis file already exists in current directory"
                }
            
            # Create template .metis file
            from .metis_file_parser import MetisFileParser
            parser = MetisFileParser()
            parser.create_template(metis_file, "general")
            
            return {
                "success": True,
                "response": "Created .metis configuration file",
                "type": "project_init"
            }
        
        else:
            # Show project status (default)
            cwd = Path.cwd()
            status_info = {
                "directory": str(cwd),
                "has_metis_config": (cwd / ".metis").exists(),
                "has_git": (cwd / ".git").exists(),
                "files_count": len(list(cwd.rglob("*")))
            }
            
            status_text = f"Project Status:\n\n"
            status_text += f"Directory: {status_info['directory']}\n"
            status_text += f"Has .metis config: {'Yes' if status_info['has_metis_config'] else 'No'}\n"
            status_text += f"Git repository: {'Yes' if status_info['has_git'] else 'No'}\n"
            status_text += f"Total files: {status_info['files_count']}\n"
            
            if project_config:
                status_text += f"\nActive configuration sections: {', '.join(project_config.keys())}"
            
            return {
                "success": True,
                "response": status_text,
                "type": "project_status",
                "status": status_info
            }


class ModelCommand(SlashCommand):
    """Switch or show current model."""
    
    def __init__(self):
        super().__init__(
            "model",
            "Switch LLM model or show current model",
            "/model [model_name]"
        )
        self.category = "General"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        config = context.get("config")
        
        if not config:
            return {
                "success": False,
                "error": "Configuration not available"
            }
        
        if remaining_text:
            # Switch model
            try:
                config.set("llm_model", remaining_text)
                return {
                    "success": True,
                    "response": f"Switched to model: {remaining_text}",
                    "type": "model_switch",
                    "model": remaining_text
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error switching model: {e}"
                }
        else:
            # Show current model
            current_model = config.get_llm_model()
            current_provider = config.get_llm_provider()
            
            return {
                "success": True,
                "response": f"Current model: {current_model} (provider: {current_provider})",
                "type": "model_info",
                "model": current_model,
                "provider": current_provider
            }


class EditCommand(SlashCommand):
    """Edit a file directly."""
    
    def __init__(self):
        super().__init__(
            "edit",
            "Edit or create a file",
            "/edit <file_path> [content]"
        )
        self.category = "Development"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        current_agent = context.get("current_agent")
        
        if not remaining_text:
            return {
                "success": False,
                "error": "Please specify a file path. Usage: /edit <file_path> [content]"
            }
        
        parts = remaining_text.split(' ', 1)
        file_path = parts[0]
        content = parts[1] if len(parts) > 1 else None
        
        try:
            from pathlib import Path
            file_obj = Path(file_path)
            
            if content:
                # Write content to file
                file_obj.parent.mkdir(parents=True, exist_ok=True)
                file_obj.write_text(content, encoding='utf-8')
                return {
                    "success": True,
                    "response": f"File '{file_path}' created/updated successfully",
                    "type": "file_edit"
                }
            else:
                # Use agent to generate content for the file
                if not current_agent:
                    return {
                        "success": False,
                        "error": "No agent available to generate file content"
                    }
                
                query = f"Please create or edit the file '{file_path}'. Generate appropriate content based on the file name and extension."
                response = current_agent.process_query(query)
                response_text = response.get("response", str(response)) if isinstance(response, dict) else str(response)
                
                return {
                    "success": True,
                    "response": f"Generated content for '{file_path}':\n\n{response_text}",
                    "type": "file_generation"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error editing file: {e}"
            }


class ReadCommand(SlashCommand):
    """Read a file's contents."""
    
    def __init__(self):
        super().__init__(
            "read",
            "Read and display file contents",
            "/read <file_path>"
        )
        self.category = "Development"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        
        if not remaining_text:
            return {
                "success": False,
                "error": "Please specify a file path. Usage: /read <file_path>"
            }
        
        try:
            from pathlib import Path
            file_obj = Path(remaining_text)
            
            if not file_obj.exists():
                return {
                    "success": False,
                    "error": f"File '{remaining_text}' not found"
                }
            
            content = file_obj.read_text(encoding='utf-8')
            return {
                "success": True,
                "response": f"Contents of '{remaining_text}':\n\n{content}",
                "type": "file_read"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {e}"
            }


class CommitCommand(SlashCommand):
    """Create a git commit."""
    
    def __init__(self):
        super().__init__(
            "commit",
            "Create a git commit with optional message",
            "/commit [message]"
        )
        self.category = "Development"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        current_agent = context.get("current_agent")
        
        try:
            import subprocess
            from pathlib import Path
            
            # Check if we're in a git repository
            if not (Path.cwd() / ".git").exists():
                return {
                    "success": False,
                    "error": "Not in a git repository"
                }
            
            # Add all changes
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            # Generate commit message if not provided
            if not remaining_text:
                if current_agent:
                    # Use agent to generate commit message
                    query = "Generate a concise git commit message based on the current changes in this repository"
                    response = current_agent.process_query(query)
                    commit_message = response.get("response", "Auto-generated commit") if isinstance(response, dict) else str(response)
                    # Extract just the first line for commit message
                    commit_message = commit_message.split('\n')[0].strip()
                else:
                    commit_message = "Auto-generated commit"
            else:
                commit_message = remaining_text
            
            # Create commit
            result = subprocess.run(["git", "commit", "-m", commit_message], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "response": f"Commit created successfully: {commit_message}",
                    "type": "git_commit"
                }
            else:
                return {
                    "success": False,
                    "error": f"Git commit failed: {result.stderr}"
                }
                
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Git command failed: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating commit: {e}"
            }


class InitCommand(SlashCommand):
    """Initialize .metis file for custom instructions."""
    
    def __init__(self):
        super().__init__(
            "init",
            "Create .metis file with custom instructions template",
            "/init [project_type]"
        )
        self.category = "Project"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        remaining_text = context.get("remaining_text", "").strip()
        project_type = remaining_text if remaining_text else "general"
        
        try:
            from pathlib import Path
            metis_file = Path.cwd() / ".metis"
            
            if metis_file.exists():
                return {
                    "success": False,
                    "error": ".metis file already exists in current directory. Use '/edit .metis' to modify it."
                }
            
            # Create enhanced template with focus on custom instructions
            from .metis_file_parser import MetisFileParser
            parser = MetisFileParser()
            parser.create_enhanced_template(metis_file, project_type)
            
            return {
                "success": True,
                "response": f"✅ Created .metis file for {project_type} project\n\n" +
                           f"📝 Edit custom instructions in your IDE:\n" +
                           f"   • Open {metis_file.absolute()}\n" +
                           f"   • Add your custom instructions in the top section\n" +
                           f"   • Configure agent behavior, tools, and workflows\n\n" +
                           f"💡 Use '/edit .metis' to modify from command line\n" +
                           f"💡 Use '/project config' to view current settings",
                "type": "project_init",
                "file_path": str(metis_file.absolute())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating .metis file: {e}"
            }


class StatusCommand(SlashCommand):
    """Show git status."""
    
    def __init__(self):
        super().__init__(
            "status",
            "Show git repository status",
            "/status"
        )
        self.category = "Development"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import subprocess
            from pathlib import Path
            
            # Check if we're in a git repository
            if not (Path.cwd() / ".git").exists():
                return {
                    "success": False,
                    "error": "Not in a git repository"
                }
            
            # Get git status
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                return {
                    "success": True,
                    "response": "Working directory clean - no changes to commit",
                    "type": "git_status"
                }
            
            # Format the status output
            status_lines = result.stdout.strip().split('\n')
            formatted_status = "Git Status:\n\n"
            
            for line in status_lines:
                if line.strip():
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    if status_code == "??":
                        formatted_status += f"  Untracked: {file_path}\n"
                    elif status_code[0] == "M":
                        formatted_status += f"  Modified:  {file_path}\n"
                    elif status_code[0] == "A":
                        formatted_status += f"  Added:     {file_path}\n"
                    elif status_code[0] == "D":
                        formatted_status += f"  Deleted:   {file_path}\n"
                    else:
                        formatted_status += f"  {status_code}: {file_path}\n"
            
            return {
                "success": True,
                "response": formatted_status,
                "type": "git_status"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Git command failed: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting git status: {e}"
            }


def register_built_in_commands(registry: SlashCommandRegistry):
    """Register all built-in slash commands."""
    commands = [
        HelpCommand(),
        ClearCommand(),
        AgentCommand(),
        AgentsCommand(),
        ReviewCommand(),
        ProjectCommand(),
        ModelCommand(),
        EditCommand(),
        ReadCommand(),
        CommitCommand(),
        StatusCommand(),
        InitCommand()
    ]
    
    for command in commands:
        registry.register(command)