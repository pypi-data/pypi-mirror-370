"""
Multi-Agent Management CLI Commands

Provides comprehensive command-line interface for managing multi-agent systems,
including agent creation, knowledge management, memory isolation, and collaboration.
"""
import os
import json
import time
import click
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from ..core.agent_manager import get_agent_manager, configure_agent_manager
from ..memory.isolated_memory import get_memory_manager, configure_memory_manager
from ..knowledge.shared_knowledge import get_shared_knowledge, configure_shared_knowledge
from ..config.agent_profiles import ProfileManager
from ..core.provider_detector import get_provider_detector

# Try to import Rich for enhanced visuals
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.status import Status
    from rich.text import Text
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


def rich_print(text: str, style: str = None):
    """Print with Rich formatting if available, fallback to plain print."""
    if RICH_AVAILABLE and console:
        if style:
            console.print(text, style=style)
        else:
            console.print(text)
    else:
        print(text)


def create_table(title: str, columns: List[str]) -> Any:
    """Create a Rich table if available, return None otherwise."""
    if RICH_AVAILABLE:
        table = Table(title=title, show_header=True, header_style="bold magenta")
        for column in columns:
            table.add_column(column)
        return table
    return None


@click.group(name='agents')
def agent_group():
    """Multi-agent system management commands."""
    pass


@agent_group.command()
@click.option('--max-agents', '-m', default=10, help='Maximum number of concurrent agents')
@click.option('--shared-knowledge', '-k', is_flag=True, help='Enable shared knowledge base')
@click.option('--memory-isolation', '-i', is_flag=True, help='Enable memory isolation')
@click.option('--config-file', '-c', help='Configuration file path')
def init(max_agents: int, shared_knowledge: bool, memory_isolation: bool, config_file: str):
    """Initialize the multi-agent system."""
    rich_print("🚀 Initializing Multi-Agent System", "bold blue")
    
    try:
        # Initialize agent manager
        with Status("Setting up Agent Manager...") if RICH_AVAILABLE else None:
            agent_manager = configure_agent_manager(
                max_agents=max_agents,
                shared_knowledge_enabled=shared_knowledge
            )
        
        # Initialize shared knowledge if enabled
        if shared_knowledge:
            with Status("Setting up Shared Knowledge Base...") if RICH_AVAILABLE else None:
                configure_shared_knowledge("knowledge/shared_knowledge.db")
            rich_print("✅ Shared Knowledge Base initialized", "green")
        
        # Initialize memory isolation if enabled
        if memory_isolation:
            with Status("Setting up Memory Isolation...") if RICH_AVAILABLE else None:
                configure_memory_manager("memory/agents")
            rich_print("✅ Memory Isolation initialized", "green")
        
        rich_print(f"✅ Multi-Agent System initialized with max {max_agents} agents", "green")
        
        # Display system info
        if RICH_AVAILABLE:
            panel = Panel.fit(
                f"[bold]Multi-Agent System Ready[/bold]\n\n"
                f"Max Agents: {max_agents}\n"
                f"Shared Knowledge: {'Enabled' if shared_knowledge else 'Disabled'}\n"
                f"Memory Isolation: {'Enabled' if memory_isolation else 'Disabled'}\n"
                f"Initialized at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                title="System Status",
                border_style="green"
            )
            console.print(panel)
        
    except Exception as e:
        rich_print(f"❌ Failed to initialize multi-agent system: {e}", "red")


@agent_group.command()
@click.argument('agent_id')
@click.option('--profile', '-p', default='developer', help='Agent profile name (developer, research, data_science)')
@click.option('--provider', '--llm', help='Override LLM provider (groq, openai, anthropic, ollama, huggingface)')
@click.option('--model', help='Override model name for the provider')
@click.option('--memory-limit', '-m', default=100.0, help='Memory limit in MB')
@click.option('--isolation-level', '-l', 
              type=click.Choice(['strict', 'moderate', 'permissive']), 
              default='moderate', help='Memory isolation level')
@click.option('--allowed-categories', '-c', multiple=True, help='Allowed knowledge categories')
@click.option('--auto-fallback/--no-auto-fallback', default=True, help='Automatically fallback to available providers')
def create(agent_id: str, profile: str, provider: Optional[str], model: Optional[str], 
           memory_limit: float, isolation_level: str, allowed_categories: tuple, auto_fallback: bool):
    """Create a new agent."""
    rich_print(f"🤖 Creating agent: {agent_id}", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            rich_print("❌ Agent manager not initialized. Run 'agents init' first.", "red")
            return
        
        # Initialize provider detector
        detector = get_provider_detector()
        
        # Load profile and handle provider override/fallback
        rich_print(f"Loading profile: {profile}", "cyan")
        profile_manager = ProfileManager()
        profile_config = profile_manager.load_profile(profile)
        
        if not profile_config:
            rich_print(f"❌ Profile '{profile}' not found", "red")
            return
        
        # Determine which provider to use
        original_provider = profile_config.llm_config.provider if profile_config.llm_config else None
        final_provider = provider or original_provider
        final_model = model
        
        # Validate provider availability
        if final_provider:
            validation = detector.validate_provider_requirements(final_provider)
            
            if not validation['valid']:
                rich_print(f"⚠️  Provider '{final_provider}' not available:", "yellow")
                for error in validation['errors']:
                    rich_print(f"   • {error}", "red")
                
                if auto_fallback:
                    # Get fallback recommendation
                    profile_type = profile if profile in ['coding', 'research', 'general', 'data_science'] else 'general'
                    fallback_provider = detector.get_recommended_provider(profile_type)
                    
                    if fallback_provider:
                        rich_print(f"🔄 Auto-fallback to available provider: {fallback_provider}", "cyan")
                        final_provider = fallback_provider
                        if not final_model:
                            final_model = detector.PROVIDER_INFO[fallback_provider]['default_model']
                    else:
                        rich_print("❌ No available providers found", "red")
                        rich_print("💡 Available setup options:", "blue")
                        rich_print("   • metis auth set groq YOUR_GROQ_KEY", "cyan")
                        rich_print("   • metis auth set openai YOUR_OPENAI_KEY", "cyan")
                        rich_print("   • Install Ollama for local models", "cyan")
                        return
                else:
                    rich_print("💡 Solutions:", "blue")
                    for suggestion in validation['suggestions']:
                        rich_print(f"   • {suggestion}", "cyan")
                    return
        
        # Override provider in profile config if specified
        if final_provider and final_provider != original_provider:
            if profile_config.llm_config:
                profile_config.llm_config.provider = final_provider
            else:
                from ..config.agent_profiles import LLMConfig
                profile_config.llm_config = LLMConfig(provider=final_provider, model="default")
            rich_print(f"🔧 Using provider: {final_provider}", "green")
        
        # Override model if specified
        if final_model:
            if profile_config.llm_config:
                profile_config.llm_config.model = final_model
            else:
                from ..config.agent_profiles import LLMConfig
                profile_config.llm_config = LLMConfig(provider=final_provider or "groq", model=final_model)
            rich_print(f"🔧 Using model: {final_model}", "green")
        
        # Create agent using the profile system correctly
        # The AgentManager should handle loading the YAML profile
        agent_id_result = agent_manager.create_agent(
            profile_name=profile,  # This should load from profiles/{profile}.yaml
            agent_id=agent_id,
            profile_config=profile_config,  # Pass modified config with provider overrides
            max_memory_mb=memory_limit,
            memory_isolation_level=isolation_level,
            allowed_shared_keys=[f'shared.{cat}' for cat in allowed_categories],
            restricted_keys=['sensitive.*', 'private.*']
        )
        
        if agent_id_result:
            rich_print(f"✅ Agent '{agent_id}' created successfully", "green")
            
            # Display agent info
            if RICH_AVAILABLE:
                table = create_table(f"Agent: {agent_id}", ["Property", "Value"])
                table.add_row("Profile", profile or "Default")
                table.add_row("Memory Limit", f"{memory_limit} MB")
                table.add_row("Isolation Level", isolation_level)
                table.add_row("Allowed Categories", ", ".join(allowed_categories) or "None")
                table.add_row("Status", "Active")
                console.print(table)
        else:
            rich_print(f"❌ Failed to create agent '{agent_id}'", "red")
            
    except Exception as e:
        rich_print(f"❌ Error creating agent: {e}", "red")
        # Debug: Show more details
        rich_print(f"[DEBUG] Exception type: {type(e).__name__}", "yellow")
        rich_print(f"[DEBUG] Full error: {repr(e)}", "yellow")
        import traceback
        traceback.print_exc()


@agent_group.command()
def list():
    """List all active agents."""
    rich_print("📋 Active Agents", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            rich_print("❌ Agent manager not initialized", "red")
            return
        
        agents = agent_manager.list_agents()
        
        if not agents:
            rich_print("No active agents found", "yellow")
            return
        
        if RICH_AVAILABLE:
            table = create_table("Active Agents", [
                "Agent ID", "Profile", "Status", "Memory Usage", "Tasks", "Last Active"
            ])
            
            for agent_id in agents:
                agent_info = agent_manager.get_agent_info(agent_id)
                memory_stats = agent_manager.get_agent_memory_stats(agent_id)
                
                memory_usage = f"{memory_stats.get('memory_size_mb', 0):.1f} MB" if memory_stats else "N/A"
                last_active = agent_info.get('last_active', 'Never')
                if isinstance(last_active, (int, float)):
                    last_active = datetime.fromtimestamp(last_active).strftime('%H:%M:%S')
                
                table.add_row(
                    agent_id,
                    agent_info.get('profile_name', 'Default'),
                    agent_info.get('status', 'Unknown'),
                    memory_usage,
                    str(agent_info.get('total_queries', 0)),
                    last_active
                )
            
            console.print(table)
        else:
            for agent_id in agents:
                print(f"- {agent_id}")
                
    except Exception as e:
        rich_print(f"❌ Error listing agents: {e}", "red")




@agent_group.command()
def providers():
    """Show available LLM providers and their status."""
    rich_print("🔍 Checking LLM Provider Availability", "bold blue")
    
    detector = get_provider_detector()
    status_info = detector.list_providers_with_status()
    
    if RICH_AVAILABLE:
        table = create_table("LLM Provider Status", ["Provider", "Status", "Model", "Key Source", "Notes"])
        
        for provider, info in status_info.items():
            status = "✅ Available" if info['available'] else "❌ Unavailable"
            model = info['info']['default_model']
            
            if info['available']:
                key_source = info['validation'].get('key_source', 'unknown')
                notes = f"Speed: {info['info']['speed']}, Cost: {info['info']['cost']}"
            else:
                key_source = "No API key"
                notes = "Missing API key" if info['info']['requires_key'] else "Local setup required"
            
            table.add_row(provider, status, model, key_source, notes)
        
        console.print(table)
    else:
        for provider, info in status_info.items():
            status = "Available" if info['available'] else "Unavailable"
            print(f"{provider}: {status} ({info['info']['default_model']})")
    
    # Show setup instructions for unavailable providers
    unavailable = [p for p, info in status_info.items() if not info['available'] and info['info']['requires_key']]
    if unavailable:
        rich_print("\n💡 To enable unavailable providers:", "blue")
        for provider in unavailable:
            rich_print(f"   metis auth set {provider} YOUR_{provider.upper()}_API_KEY", "cyan")

@agent_group.command()
@click.argument('agent_id')
@click.option('--force', '-f', is_flag=True, help='Force stop without cleanup')
def stop(agent_id: str, force: bool):
    """Stop an agent."""
    rich_print(f"🛑 Stopping agent: {agent_id}", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            rich_print("❌ Agent manager not initialized", "red")
            return
        
        success = agent_manager.stop_agent(agent_id, force=force)
        
        if success:
            rich_print(f"✅ Agent '{agent_id}' stopped successfully", "green")
        else:
            rich_print(f"❌ Failed to stop agent '{agent_id}'", "red")
            
    except Exception as e:
        rich_print(f"❌ Error stopping agent: {e}", "red")


@agent_group.command()
@click.argument('agent_id')
def status(agent_id: str):
    """Get detailed status of an agent."""
    rich_print(f"📊 Agent Status: {agent_id}", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            rich_print("❌ Agent manager not initialized", "red")
            return
        
        if agent_id not in agent_manager.list_agents():
            rich_print(f"❌ Agent '{agent_id}' not found", "red")
            return
        
        # Get comprehensive agent info
        agent_info = agent_manager.get_agent_info(agent_id)
        memory_stats = agent_manager.get_agent_memory_stats(agent_id)
        
        if RICH_AVAILABLE:
            # Agent basic info
            info_table = create_table(f"Agent: {agent_id}", ["Property", "Value"])
            # Format timestamps for display
            created_at = agent_info.get('created_at', 'Unknown')
            if isinstance(created_at, (int, float)):
                created_at = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')
            
            last_active = agent_info.get('last_active', 'Never')
            if isinstance(last_active, (int, float)):
                last_active = datetime.fromtimestamp(last_active).strftime('%Y-%m-%d %H:%M:%S')
            
            info_table.add_row("Status", agent_info.get('status', 'Unknown'))
            info_table.add_row("Profile", agent_info.get('profile_name', 'Default'))
            info_table.add_row("Created", str(created_at))
            info_table.add_row("Last Active", str(last_active))
            info_table.add_row("Task Count", str(agent_info.get('total_queries', 0)))
            
            console.print(info_table)
            
            # Memory statistics
            if memory_stats:
                memory_table = create_table("Memory Statistics", ["Metric", "Value"])
                memory_table.add_row("Memory Usage", f"{memory_stats.get('memory_size_mb', 0):.2f} MB")
                memory_table.add_row("Entries", str(memory_stats.get('entry_count', 0)))
                memory_table.add_row("Access Count", str(memory_stats.get('access_count', 0)))
                memory_table.add_row("Cache Hit Rate", f"{memory_stats.get('cache_hit_rate', 0):.1%}")
                memory_table.add_row("Shared Accesses", str(memory_stats.get('shared_accesses', 0)))
                
                console.print(memory_table)
        else:
            print(f"Agent: {agent_id}")
            print(f"Status: {agent_info.get('status', 'Unknown')}")
            print(f"Memory Usage: {memory_stats.get('memory_size_mb', 0):.2f} MB" if memory_stats else "Memory: N/A")
            
    except Exception as e:
        rich_print(f"❌ Error getting agent status: {e}", "red")


@agent_group.command()
@click.argument('from_agent')
@click.argument('to_agent') 
@click.argument('knowledge_key')
@click.argument('knowledge_data')
@click.option('--metadata', '-m', help='JSON metadata for the knowledge')
def share(from_agent: str, to_agent: str, knowledge_key: str, knowledge_data: str, metadata: str):
    """Share knowledge between agents."""
    rich_print(f"🔄 Sharing knowledge: {from_agent} → {to_agent}", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        memory_manager = get_memory_manager()
        
        if not agent_manager or not memory_manager:
            rich_print("❌ System not initialized", "red")
            return
        
        # Parse knowledge data
        try:
            if knowledge_data.startswith('{') or knowledge_data.startswith('['):
                data = json.loads(knowledge_data)
            else:
                data = knowledge_data
        except json.JSONDecodeError:
            data = knowledge_data
        
        # Parse metadata
        meta = {}
        if metadata:
            try:
                meta = json.loads(metadata)
            except json.JSONDecodeError:
                rich_print("❌ Invalid JSON metadata", "red")
                return
        
        # Share knowledge
        success = memory_manager.share_knowledge(
            from_agent, to_agent, knowledge_key, data, meta
        )
        
        if success:
            rich_print(f"✅ Knowledge '{knowledge_key}' shared successfully", "green")
        else:
            rich_print(f"❌ Failed to share knowledge", "red")
            
    except Exception as e:
        rich_print(f"❌ Error sharing knowledge: {e}", "red")


@agent_group.command()
@click.option('--category', '-c', help='Filter by knowledge category')
@click.option('--agent', '-a', help='Filter by agent access')
@click.option('--limit', '-l', default=20, help='Maximum number of results')
def knowledge(category: str, agent: str, limit: int):
    """List shared knowledge entries."""
    rich_print("🧠 Shared Knowledge Base", "bold blue")
    
    try:
        shared_kb = get_shared_knowledge()
        if not shared_kb:
            rich_print("❌ Shared knowledge base not initialized", "red")
            return
        
        # Query knowledge
        results = shared_kb.query_knowledge(
            category=category,
            agent_id=agent,
            limit=limit
        )
        
        if not results:
            rich_print("No knowledge entries found", "yellow")
            return
        
        if RICH_AVAILABLE:
            table = create_table("Knowledge Entries", [
                "Title", "Category", "Source Agent", "Version", "Access Level", "Usage"
            ])
            
            for entry in results:
                table.add_row(
                    entry.get('title', 'Unknown')[:30],
                    entry.get('category', 'Unknown'),
                    entry.get('source_agent', 'Unknown'),
                    str(entry.get('version', 1)),
                    entry.get('access_level', 'public'),
                    str(entry.get('usage_count', 0))
                )
            
            console.print(table)
        else:
            for entry in results:
                print(f"- {entry.get('title', 'Unknown')} ({entry.get('category', 'Unknown')})")
                
    except Exception as e:
        rich_print(f"❌ Error listing knowledge: {e}", "red")


@agent_group.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'summary']), 
              default='summary', help='Output format')
def system(format: str):
    """Show multi-agent system status."""
    rich_print("🖥️  Multi-Agent System Status", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        memory_manager = get_memory_manager()
        shared_kb = get_shared_knowledge()
        
        if not agent_manager:
            rich_print("❌ Agent manager not initialized", "red")
            return
        
        # Get system statistics
        agents = agent_manager.list_agents()
        isolation_report = memory_manager.get_isolation_report() if memory_manager else {}
        kb_stats = shared_kb.get_statistics() if shared_kb else {}
        
        if RICH_AVAILABLE:
            # System overview panel
            overview = Panel.fit(
                f"[bold]System Overview[/bold]\n\n"
                f"Active Agents: {len(agents)}\n"
                f"Total Memory: {isolation_report.get('total_memory_mb', 0):.1f} MB\n"
                f"Knowledge Entries: {kb_stats.get('total_entries', 0)}\n"
                f"24h Access Count: {kb_stats.get('access_count_24h', 0)}",
                title="Multi-Agent System",
                border_style="blue"
            )
            console.print(overview)
            
            # Agent summary table
            if agents:
                agent_table = create_table("Agent Summary", [
                    "Agent ID", "Status", "Memory (MB)", "Tasks", "Last Active"
                ])
                
                for agent_id in agents:
                    info = agent_manager.get_agent_info(agent_id)
                    memory_stats = agent_manager.get_agent_memory_stats(agent_id)
                    
                    # Format last active timestamp
                    last_active = info.get('last_active', 'Never')
                    if isinstance(last_active, (int, float)):
                        last_active = datetime.fromtimestamp(last_active).strftime('%H:%M:%S')
                    
                    agent_table.add_row(
                        agent_id,
                        info.get('status', 'Unknown'),
                        f"{memory_stats.get('memory_size_mb', 0):.1f}" if memory_stats else "0.0",
                        str(info.get('total_queries', 0)),
                        str(last_active)
                    )
                
                console.print(agent_table)
        else:
            print(f"Active Agents: {len(agents)}")
            print(f"Total Memory: {isolation_report.get('total_memory_mb', 0):.1f} MB")
            print(f"Knowledge Entries: {kb_stats.get('total_entries', 0)}")
            
    except Exception as e:
        rich_print(f"❌ Error getting system status: {e}", "red")


@agent_group.command()
@click.option('--agents', '-a', is_flag=True, help='Cleanup agent data')
@click.option('--memory', '-m', is_flag=True, help='Cleanup memory data')
@click.option('--knowledge', '-k', is_flag=True, help='Cleanup knowledge data')
@click.option('--all', '-A', is_flag=True, help='Cleanup all data')
@click.option('--force', '-f', is_flag=True, help='Force cleanup without confirmation')
def cleanup(agents: bool, memory: bool, knowledge: bool, all: bool, force: bool):
    """Cleanup multi-agent system data."""
    if all:
        agents = memory = knowledge = True
    
    if not any([agents, memory, knowledge]):
        rich_print("❌ Specify what to cleanup with --agents, --memory, --knowledge, or --all", "red")
        return
    
    if not force:
        items = []
        if agents: items.append("agents")
        if memory: items.append("memory")
        if knowledge: items.append("knowledge")
        
        confirmation = click.confirm(f"This will cleanup {', '.join(items)} data. Continue?")
        if not confirmation:
            rich_print("Cleanup cancelled", "yellow")
            return
    
    rich_print("🧹 Cleaning up multi-agent system", "bold blue")
    
    try:
        if agents:
            agent_manager = get_agent_manager()
            if agent_manager:
                agent_manager.shutdown()
                rich_print("✅ Agent data cleaned up", "green")
        
        if memory:
            memory_manager = get_memory_manager()
            if memory_manager:
                memory_manager.shutdown()
                rich_print("✅ Memory data cleaned up", "green")
        
        if knowledge:
            shared_kb = get_shared_knowledge()
            if shared_kb:
                shared_kb.cleanup()
                rich_print("✅ Knowledge data cleaned up", "green")
        
        rich_print("✅ Cleanup completed successfully", "green")
        
    except Exception as e:
        rich_print(f"❌ Error during cleanup: {e}", "red")


if __name__ == '__main__':
    agent_group()