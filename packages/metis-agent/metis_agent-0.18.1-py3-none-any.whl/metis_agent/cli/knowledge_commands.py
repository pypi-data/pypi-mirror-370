"""
Knowledge Base CLI Commands

Provides CLI commands for managing the knowledge base system under
'metis config knowledge' command group.
"""

import os
import json
import click
from typing import List, Optional

try:
    from tabulate import tabulate
except ImportError:
    # Fallback if tabulate is not available
    def tabulate(data, headers=None, tablefmt="grid"):
        if not data:
            return "No data"
        
        # Simple table formatting fallback
        if headers:
            result = " | ".join(headers) + "\n"
            result += "-" * len(result) + "\n"
        else:
            result = ""
        
        for row in data:
            result += " | ".join(str(cell) for cell in row) + "\n"
        
        return result

from ..core.agent_config import AgentConfig
from ..knowledge.knowledge_config import KnowledgeConfig
from ..knowledge.knowledge_adapter import KnowledgeAdapter
from ..knowledge.knowledge_entry import KnowledgeEntry


@click.group(name='knowledge')
def knowledge_cli():
    """Knowledge base management commands."""
    pass


@knowledge_cli.command()
@click.option('--preset', type=click.Choice(['personal', 'business', 'academic', 'coding']), 
              help='Initialize with a preset configuration')
@click.option('--provider', type=click.Choice(['local', 'supabase', 'postgresql', 'mongodb']), 
              default='local', help='Knowledge base provider')
@click.option('--directory', default='knowledge', help='Knowledge base directory')
@click.option('--auto-learning/--no-auto-learning', default=True, 
              help='Enable automatic learning from conversations')
def init(preset: Optional[str], provider: str, directory: str, auto_learning: bool):
    """Initialize knowledge base configuration."""
    try:
        # Create knowledge configuration
        config = KnowledgeConfig(directory)
        
        # Apply preset if specified
        if preset:
            config.apply_preset(preset)
            click.echo(f"[APPLIED] {preset} preset configuration")
        
        # Update configuration
        config.provider = provider
        config.auto_learning = auto_learning
        
        # Save configuration
        config.save_config()
        
        # Update agent configuration
        agent_config = AgentConfig()
        agent_config.set_knowledge_enabled(True)
        agent_config.set_knowledge_provider(provider)
        agent_config.set_knowledge_auto_learning(auto_learning)
        agent_config.set_knowledge_dir(directory)
        agent_config.save_config()
        
        click.echo(f"[SUCCESS] Knowledge base initialized with {provider} provider")
        click.echo(f"[INFO] Directory: {directory}")
        click.echo(f"[INFO] Auto-learning: {'enabled' if auto_learning else 'disabled'}")
        
        # Create directory structure
        os.makedirs(directory, exist_ok=True)
        os.makedirs(os.path.join(directory, 'imports'), exist_ok=True)
        os.makedirs(os.path.join(directory, 'exports'), exist_ok=True)
        
        click.echo(f"[SUCCESS] Created directory structure in {directory}")
        
    except Exception as e:
        click.echo(f"[ERROR] Error initializing knowledge base: {e}", err=True)


@knowledge_cli.command()
def status():
    """Show knowledge base status and statistics."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled")
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter to get statistics
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            # Fallback for testing without full agent system
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        stats = adapter.get_statistics()
        
        # Display status
        click.echo("[STATUS] Knowledge Base Status")
        click.echo("=" * 50)
        
        # Configuration
        click.echo(f"Status: {'[ENABLED]' if stats['configuration']['enabled'] else '[DISABLED]'}")
        click.echo(f"Provider: {agent_config.get_knowledge_provider()}")
        click.echo(f"Directory: {knowledge_dir}")
        click.echo(f"Auto-learning: {'[ENABLED]' if stats['configuration']['auto_learning'] else '[DISABLED]'}")
        click.echo(f"Max context entries: {stats['configuration']['max_context_entries']}")
        click.echo(f"Similarity threshold: {stats['configuration']['similarity_threshold']}")
        
        # Statistics
        kb_stats = stats['knowledge_base']
        click.echo(f"\nTotal entries: {kb_stats.get('total_entries', 0)}")
        click.echo(f"Recent updates (7 days): {kb_stats.get('recent_updates', 0)}")
        
        # Categories
        categories = kb_stats.get('categories', {})
        if categories:
            click.echo("\nEntries by category:")
            for category, count in categories.items():
                click.echo(f"  {category}: {count}")
        
        # Sources
        sources = kb_stats.get('sources', {})
        if sources:
            click.echo("\nEntries by source:")
            for source, count in sources.items():
                click.echo(f"  {source}: {count}")
        
        # Performance metrics
        metrics = stats['adapter_metrics']
        click.echo(f"\nPerformance metrics:")
        click.echo(f"  Queries processed: {metrics['queries_processed']}")
        click.echo(f"  Knowledge retrieved: {metrics['knowledge_retrieved']}")
        click.echo(f"  AI entries created: {metrics['ai_entries_created']}")
        click.echo(f"  Average relevance: {metrics['average_relevance']:.3f}")
        
    except Exception as e:
        click.echo(f"[ERROR] Error getting knowledge base status: {e}", err=True)


@knowledge_cli.command()
@click.argument('query')
@click.option('--category', help='Filter by category')
@click.option('--tags', help='Filter by tags (comma-separated)')
@click.option('--max-results', default=10, help='Maximum number of results')
@click.option('--threshold', type=float, help='Similarity threshold (0.0-1.0)')
def search(query: str, category: Optional[str], tags: Optional[str], 
           max_results: int, threshold: Optional[float]):
    """Search knowledge base entries."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # Search
        search_kwargs = {
            'category': category,
            'tags': tag_list,
            'max_results': max_results
        }
        if threshold is not None:
            search_kwargs['similarity_threshold'] = threshold
        
        results = adapter.search_knowledge(query, **search_kwargs)
        
        if not results.entries:
            click.echo(f"No results found for: {query}")
            return
        
        # Display results
        click.echo(f"[SEARCH] Results for: {query}")
        click.echo(f"Found {results.total_count} entries (execution time: {results.execution_time:.3f}s)")
        click.echo("=" * 70)
        
        for i, entry in enumerate(results.entries):
            relevance = results.relevance_scores[i] if i < len(results.relevance_scores) else 1.0
            
            click.echo(f"\n[{i+1}] {entry.title}")
            click.echo(f"Category: {entry.category} | Tags: {', '.join(entry.tags)}")
            click.echo(f"Source: {entry.source} | Relevance: {relevance:.3f}")
            click.echo(f"Updated: {entry.updated_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Show content preview
            content_preview = entry.get_summary(200)
            click.echo(f"Content: {content_preview}")
            click.echo("-" * 50)
        
    except Exception as e:
        click.echo(f"[ERROR] Error searching knowledge base: {e}", err=True)


@knowledge_cli.command()
@click.option('--category', help='Filter by category')
@click.option('--tags', help='Filter by tags (comma-separated)')
@click.option('--limit', default=20, help='Maximum number of entries to list')
@click.option('--format', type=click.Choice(['table', 'detailed']), default='table',
              help='Output format')
def list(category: Optional[str], tags: Optional[str], limit: int, format: str):
    """List knowledge base entries."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # List entries
        entries = adapter.list_knowledge_entries(category, tag_list, limit)
        
        if not entries:
            click.echo("No entries found")
            return
        
        if format == 'table':
            # Table format
            table_data = []
            for entry in entries:
                table_data.append([
                    entry.id[:8] + "...",
                    entry.title[:30] + "..." if len(entry.title) > 30 else entry.title,
                    entry.category,
                    ", ".join(entry.tags[:2]) + ("..." if len(entry.tags) > 2 else ""),
                    entry.source,
                    entry.updated_at.strftime('%Y-%m-%d')
                ])
            
            headers = ["ID", "Title", "Category", "Tags", "Source", "Updated"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
            
        else:
            # Detailed format
            for entry in entries:
                click.echo(f"\n📄 {entry.title}")
                click.echo(f"ID: {entry.id}")
                click.echo(f"Category: {entry.category}")
                click.echo(f"Tags: {', '.join(entry.tags) if entry.tags else 'None'}")
                click.echo(f"Source: {entry.source}")
                click.echo(f"Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}")
                click.echo(f"Updated: {entry.updated_at.strftime('%Y-%m-%d %H:%M')}")
                click.echo(f"Version: {entry.version}")
                
                # Show content preview
                content_preview = entry.get_summary(300)
                click.echo(f"Content: {content_preview}")
                click.echo("-" * 60)
        
    except Exception as e:
        click.echo(f"❌ Error listing knowledge entries: {e}", err=True)


@knowledge_cli.command()
@click.argument('title')
@click.argument('content')
@click.option('--category', required=True, help='Entry category')
@click.option('--tags', help='Entry tags (comma-separated)')
def add(title: str, content: str, category: str, tags: Optional[str]):
    """Add a new knowledge entry."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # Create entry
        entry = adapter.create_knowledge_entry(title, content, category, tag_list)
        
        if entry:
            click.echo(f"[SUCCESS] Created knowledge entry: {entry.title}")
            click.echo(f"  ID: {entry.id}")
            click.echo(f"  Category: {entry.category}")
            click.echo(f"  Tags: {', '.join(entry.tags) if entry.tags else 'None'}")
        else:
            click.echo("[ERROR] Failed to create knowledge entry", err=True)
        
    except Exception as e:
        click.echo(f"[ERROR] Error adding knowledge entry: {e}", err=True)


@knowledge_cli.command()
@click.argument('entry_id')
@click.option('--title', help='New title')
@click.option('--content', help='New content')
@click.option('--tags', help='New tags (comma-separated)')
def update(entry_id: str, title: Optional[str], content: Optional[str], tags: Optional[str]):
    """Update an existing knowledge entry."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Parse tags
        tag_list = None
        if tags is not None:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # Update entry
        success = adapter.update_knowledge_entry(entry_id, title, content, tag_list)
        
        if success:
            click.echo(f"[SUCCESS] Updated knowledge entry: {entry_id}")
        else:
            click.echo(f"[ERROR] Failed to update knowledge entry: {entry_id}", err=True)
        
    except Exception as e:
        click.echo(f"[ERROR] Error updating knowledge entry: {e}", err=True)


@knowledge_cli.command()
@click.argument('entry_id')
@click.confirmation_option(prompt='Are you sure you want to delete this entry?')
def delete(entry_id: str):
    """Delete a knowledge entry."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Delete entry
        success = adapter.delete_knowledge_entry(entry_id)
        
        if success:
            click.echo(f"[SUCCESS] Deleted knowledge entry: {entry_id}")
        else:
            click.echo(f"[ERROR] Failed to delete knowledge entry: {entry_id}", err=True)
        
    except Exception as e:
        click.echo(f"[ERROR] Error deleting knowledge entry: {e}", err=True)


@knowledge_cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--category', help='Category for imported entry')
@click.option('--tags', help='Tags for imported entry (comma-separated)')
def import_file(file_path: str, category: Optional[str], tags: Optional[str]):
    """Import knowledge from a file."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # Import file
        entry = adapter.knowledge_base.import_from_file(file_path, category, tag_list)
        
        if entry:
            click.echo(f"[SUCCESS] Imported knowledge from: {file_path}")
            click.echo(f"  Title: {entry.title}")
            click.echo(f"  ID: {entry.id}")
            click.echo(f"  Category: {entry.category}")
            click.echo(f"  Tags: {', '.join(entry.tags) if entry.tags else 'None'}")
        else:
            click.echo(f"[ERROR] Failed to import from: {file_path}", err=True)
        
    except Exception as e:
        click.echo(f"[ERROR] Error importing file: {e}", err=True)


@knowledge_cli.command()
@click.argument('directory_path', type=click.Path(exists=True))
@click.option('--category', help='Category for imported entries')
@click.option('--recursive/--no-recursive', default=False, help='Search subdirectories')
def import_directory(directory_path: str, category: Optional[str], recursive: bool):
    """Import knowledge from a directory of files."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Import directory
        entries = adapter.import_knowledge_from_directory(directory_path, category, recursive)
        
        if entries:
            click.echo(f"[SUCCESS] Imported {len(entries)} entries from: {directory_path}")
            
            # Show summary by category
            categories = {}
            for entry in entries:
                categories[entry.category] = categories.get(entry.category, 0) + 1
            
            click.echo("Categories imported:")
            for cat, count in categories.items():
                click.echo(f"  {cat}: {count} entries")
        else:
            click.echo(f"[ERROR] No entries imported from: {directory_path}", err=True)
        
    except Exception as e:
        click.echo(f"[ERROR] Error importing directory: {e}", err=True)


@knowledge_cli.command()
@click.argument('entry_id')
@click.argument('file_path', type=click.Path())
@click.option('--format', type=click.Choice(['md', 'json', 'yaml']), default='md',
              help='Export format')
def export(entry_id: str, file_path: str, format: str):
    """Export a knowledge entry to file."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Export entry
        success = adapter.export_knowledge_entry(entry_id, file_path, format)
        
        if success:
            click.echo(f"[SUCCESS] Exported entry {entry_id} to: {file_path}")
        else:
            click.echo(f"[ERROR] Failed to export entry: {entry_id}", err=True)
        
    except Exception as e:
        click.echo(f"[ERROR] Error exporting entry: {e}", err=True)


@knowledge_cli.command()
def categories():
    """List all knowledge base categories."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Get categories
        categories = adapter.get_categories()
        
        if categories:
            click.echo("[CATEGORIES] Knowledge Base Categories:")
            for category in sorted(categories):
                click.echo(f"  • {category}")
        else:
            click.echo("No categories found")
        
    except Exception as e:
        click.echo(f" Error listing categories: {e}", err=True)


@knowledge_cli.command()
def tags():
    """List all knowledge base tags."""
    try:
        agent_config = AgentConfig()
        
        if not agent_config.is_knowledge_enabled():
            click.echo("[ERROR] Knowledge base is disabled", err=True)
            return
        
        # Load knowledge configuration
        knowledge_dir = agent_config.get_knowledge_dir()
        config = KnowledgeConfig(knowledge_dir)
        
        # Create adapter
        try:
            from ..core.single_agent import SingleAgent
            agent = SingleAgent()
        except ImportError:
            class MockAgent:
                def __init__(self):
                    self.config = agent_config
            agent = MockAgent()
        
        adapter = KnowledgeAdapter(agent, config)
        
        # Get tags
        all_tags = adapter.get_tags()
        
        if all_tags:
            click.echo("[TAGS] Knowledge Base Tags:")
            for tag in sorted(all_tags):
                click.echo(f"  • {tag}")
        else:
            click.echo("No tags found")
        
    except Exception as e:
        click.echo(f" Error listing tags: {e}", err=True)


@knowledge_cli.command()
@click.option('--enabled/--disabled', default=True, help='Enable or disable knowledge base')
@click.option('--provider', type=click.Choice(['local', 'supabase', 'postgresql', 'mongodb']),
              help='Knowledge base provider')
@click.option('--auto-learning/--no-auto-learning', help='Enable automatic learning')
@click.option('--max-context', type=int, help='Maximum context entries')
@click.option('--threshold', type=float, help='Similarity threshold (0.0-1.0)')
def configure(enabled: bool, provider: Optional[str], auto_learning: Optional[bool],
              max_context: Optional[int], threshold: Optional[float]):
    """Configure knowledge base settings."""
    try:
        agent_config = AgentConfig()
        
        # Update settings
        agent_config.set_knowledge_enabled(enabled)
        
        if provider:
            agent_config.set_knowledge_provider(provider)
        
        if auto_learning is not None:
            agent_config.set_knowledge_auto_learning(auto_learning)
        
        if max_context:
            agent_config.set_knowledge_max_context(max_context)
        
        if threshold:
            agent_config.set_knowledge_similarity_threshold(threshold)
        
        agent_config.save_config()
        
        click.echo("[SUCCESS] Knowledge base configuration updated")
        click.echo(f"  Enabled: {agent_config.is_knowledge_enabled()}")
        click.echo(f"  Provider: {agent_config.get_knowledge_provider()}")
        click.echo(f"  Auto-learning: {agent_config.is_knowledge_auto_learning_enabled()}")
        click.echo(f"  Max context: {agent_config.get_knowledge_max_context()}")
        click.echo(f"  Similarity threshold: {agent_config.get_knowledge_similarity_threshold()}")
        
    except Exception as e:
        click.echo(f"[ERROR] Error configuring knowledge base: {e}", err=True)
