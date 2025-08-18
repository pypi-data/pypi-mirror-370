"""
Enhanced Streaming Interface - Claude Code / Gemini CLI Style

This module provides a modern, Claude Code-inspired streaming interface with:
- True character-by-character streaming
- Live reasoning display
- Real-time file operations
- Modern CLI components (spinners, progress bars, live tables)
- Workspace awareness
- Interactive file editing
"""

import click
import os
import sys
import time
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, AsyncGenerator
import subprocess
import json
from dataclasses import dataclass
from enum import Enum

# Import modern CLI libraries
try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass


class StreamingMode(Enum):
    """Different streaming modes for output."""
    CHARACTER = "character"  # Character-by-character like Claude Code
    WORD = "word"           # Word-by-word like Gemini
    CHUNK = "chunk"         # Chunk-based for performance
    INSTANT = "instant"     # No streaming for debugging


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    THINKING = "thinking" 
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StreamingTask:
    """A task being executed with streaming output."""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    output: List[str] = None
    files_created: List[str] = None
    files_modified: List[str] = None
    
    def __post_init__(self):
        if self.output is None:
            self.output = []
        if self.files_created is None:
            self.files_created = []
        if self.files_modified is None:
            self.files_modified = []


class EnhancedStreamingInterface:
    """
    Claude Code / Gemini CLI-inspired streaming interface with modern features.
    """
    
    def __init__(
        self, 
        agent,
        workspace_path: str = None,
        streaming_mode: StreamingMode = StreamingMode.CHARACTER,
        tools_registry: Dict = None
    ):
        self.agent = agent
        self.workspace_path = workspace_path or os.getcwd()
        self.streaming_mode = streaming_mode
        self.tools_registry = tools_registry or {}
        
        # Rich console setup
        if RICH_AVAILABLE:
            self.console = Console(force_terminal=True, width=100)
        else:
            self.console = None
            
        # State management
        self.current_session = None
        self.active_tasks: Dict[str, StreamingTask] = {}
        self.workspace_files: List[str] = []
        self.session_context = {}
        
        # UI components
        self.live_display = None
        self.progress = None
        self.current_task_id: Optional[TaskID] = None
        
        # Performance settings
        self.char_delay = 0.01  # Delay between characters
        self.word_delay = 0.05  # Delay between words
        self.chunk_size = 5     # Characters per chunk
        
    def start_session(self, session_name: str = None):
        """Start a new interactive streaming session."""
        self.current_session = session_name or f"session_{int(time.time())}"
        self._scan_workspace()
        self._display_session_header()
        
    def _scan_workspace(self):
        """Scan current workspace for context."""
        try:
            workspace = Path(self.workspace_path)
            
            # Get all relevant files (exclude common ignore patterns)
            ignore_patterns = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.env'}
            self.workspace_files = []
            
            for file_path in workspace.rglob('*'):
                if file_path.is_file() and not any(pattern in str(file_path) for pattern in ignore_patterns):
                    rel_path = file_path.relative_to(workspace)
                    self.workspace_files.append(str(rel_path))
                    
        except Exception as e:
            self.workspace_files = []
            
    def _display_session_header(self):
        """Display session startup header."""
        if self.console:
            # Rich display
            header_table = Table.grid()
            header_table.add_column()
            header_table.add_row(f"[bold cyan]🚀 Metis Enhanced Streaming Session[/bold cyan]")
            header_table.add_row(f"Session: {self.current_session}")
            header_table.add_row(f"Workspace: {os.path.basename(self.workspace_path)}")
            header_table.add_row(f"Files: {len(self.workspace_files)} in workspace")
            
            panel = Panel(header_table, border_style="bright_blue")
            self.console.print(panel)
            
        else:
            # Fallback display
            click.echo("🚀 Metis Enhanced Streaming Session")
            click.echo(f"Session: {self.current_session}")
            click.echo(f"Workspace: {os.path.basename(self.workspace_path)}")
            click.echo(f"Files: {len(self.workspace_files)} in workspace")
            click.echo("=" * 60)

    async def stream_agent_response(self, query: str, session_id: str = None) -> AsyncGenerator[str, None]:
        """Stream agent response with real-time thinking and execution."""
        
        task_id = f"task_{int(time.time())}"
        task = StreamingTask(id=task_id, description=query)
        self.active_tasks[task_id] = task
        
        try:
            # Phase 1: Show "thinking" indicator
            task.status = TaskStatus.THINKING
            task.start_time = time.time()
            
            yield from self._show_thinking_phase(task)
            
            # Phase 2: Get agent response
            task.status = TaskStatus.EXECUTING
            response = self.agent.process_query(query, session_id=session_id or self.current_session)
            
            # Phase 3: Stream the response
            yield from self._stream_response_text(response, task)
            
            # Phase 4: Process any code blocks or file operations
            if isinstance(response, dict):
                response_text = response.get("response", str(response))
            else:
                response_text = str(response)
                
            yield from self._process_code_blocks(response_text, task)
            
            # Phase 5: Complete task
            task.status = TaskStatus.COMPLETED
            task.end_time = time.time()
            
            yield from self._show_completion_summary(task)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.end_time = time.time()
            yield f"[ERROR] {str(e)}\n"
            
    async def _show_thinking_phase(self, task: StreamingTask) -> AsyncGenerator[str, None]:
        """Show thinking phase with spinner."""
        if self.console:
            with self.console.status("[bold green]🤔 Thinking...", spinner="dots"):
                await asyncio.sleep(0.5)  # Brief pause for visual effect
        else:
            yield "🤔 Thinking...\n"
            await asyncio.sleep(0.5)
        
        yield ""  # End thinking phase
        
    async def _stream_response_text(self, response: Any, task: StreamingTask) -> AsyncGenerator[str, None]:
        """Stream response text with configurable speed."""
        
        # Extract text from response
        if isinstance(response, dict):
            text = response.get("response", str(response))
        else:
            text = str(response)
            
        # Clean text for display
        text = self._clean_text_for_streaming(text)
        
        if self.console:
            # Rich streaming
            yield from self._stream_text_rich(text)
        else:
            # Fallback streaming
            yield from self._stream_text_fallback(text)
            
        task.output.append(text)
        
    def _clean_text_for_streaming(self, text: str) -> str:
        """Clean text for streaming display."""
        try:
            # Replace problematic Unicode characters
            clean_text = text.encode('ascii', 'replace').decode('ascii')
            return clean_text
        except:
            return text
            
    async def _stream_text_rich(self, text: str) -> AsyncGenerator[str, None]:
        """Stream text using Rich console."""
        
        if self.streaming_mode == StreamingMode.INSTANT:
            self.console.print(text)
            yield text
            return
            
        # Character-by-character streaming like Claude Code
        if self.streaming_mode == StreamingMode.CHARACTER:
            current_line = ""
            for char in text:
                current_line += char
                if char == '\n':
                    self.console.print(current_line.rstrip())
                    current_line = ""
                    yield char
                else:
                    # Update current line display
                    yield char
                    if self.char_delay > 0:
                        await asyncio.sleep(self.char_delay)
                        
            # Print any remaining text
            if current_line:
                self.console.print(current_line)
                
        # Word-by-word streaming like Gemini  
        elif self.streaming_mode == StreamingMode.WORD:
            words = text.split()
            current_line = ""
            for word in words:
                current_line += word + " "
                yield word + " "
                if self.word_delay > 0:
                    await asyncio.sleep(self.word_delay)
                    
                # Handle line breaks
                if len(current_line) > 80:
                    self.console.print(current_line.strip())
                    current_line = ""
                    
            if current_line:
                self.console.print(current_line.strip())
                
        # Chunk-based streaming for performance
        elif self.streaming_mode == StreamingMode.CHUNK:
            for i in range(0, len(text), self.chunk_size):
                chunk = text[i:i + self.chunk_size]
                yield chunk
                if self.char_delay > 0:
                    await asyncio.sleep(self.char_delay)
                    
            self.console.print(text)
            
    async def _stream_text_fallback(self, text: str) -> AsyncGenerator[str, None]:
        """Fallback streaming without Rich."""
        
        if self.streaming_mode == StreamingMode.INSTANT:
            click.echo(text)
            yield text
            return
            
        # Character streaming
        if self.streaming_mode == StreamingMode.CHARACTER:
            for char in text:
                click.echo(char, nl=False)
                yield char
                if self.char_delay > 0:
                    await asyncio.sleep(self.char_delay)
            click.echo()  # Final newline
            
        # Word streaming
        elif self.streaming_mode == StreamingMode.WORD:
            words = text.split()
            line_length = 0
            for word in words:
                if line_length + len(word) > 80:
                    click.echo()
                    line_length = 0
                click.echo(word + " ", nl=False)
                line_length += len(word) + 1
                yield word + " "
                if self.word_delay > 0:
                    await asyncio.sleep(self.word_delay)
            click.echo()
            
    async def _process_code_blocks(self, text: str, task: StreamingTask) -> AsyncGenerator[str, None]:
        """Process and stream code blocks with file operations."""
        
        code_blocks = self._extract_code_blocks(text)
        
        if not code_blocks:
            yield ""
            return
            
        # Show code processing header
        if self.console:
            self.console.print(f"\n[bold yellow]📝 Processing {len(code_blocks)} code blocks...[/bold yellow]")
        else:
            yield f"\n📝 Processing {len(code_blocks)} code blocks...\n"
            
        # Process each code block
        for i, (filename, content, language) in enumerate(code_blocks, 1):
            yield from self._process_single_file(filename, content, language, i, len(code_blocks), task)
            
    async def _process_single_file(
        self, 
        filename: str, 
        content: str, 
        language: str, 
        index: int, 
        total: int,
        task: StreamingTask
    ) -> AsyncGenerator[str, None]:
        """Process a single file with streaming progress."""
        
        if self.console:
            # Rich file processing display
            progress_text = f"[{index}/{total}] {filename}"
            
            with self.console.status(f"[bold green]Creating {progress_text}...", spinner="dots"):
                await asyncio.sleep(0.2)  # Brief visual pause
                
                # Create the file
                filepath = os.path.join(self.workspace_path, filename)
                success = await self._write_file_async(filepath, content)
                
                if success:
                    self.console.print(f"✅ Created {filename} ({len(content)} chars, {language})")
                    task.files_created.append(filename)
                else:
                    self.console.print(f"❌ Failed to create {filename}")
                    
        else:
            # Fallback file processing
            yield f"[{index}/{total}] Creating {filename}...\n"
            
            filepath = os.path.join(self.workspace_path, filename)
            success = await self._write_file_async(filepath, content)
            
            if success:
                yield f"✅ Created {filename} ({len(content)} chars, {language})\n"
                task.files_created.append(filename)
            else:
                yield f"❌ Failed to create {filename}\n"
                
    async def _write_file_async(self, filepath: str, content: str) -> bool:
        """Write file asynchronously."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return True
        except Exception as e:
            return False
            
    def _extract_code_blocks(self, text: str) -> List[tuple]:
        """Extract code blocks from text."""
        import re
        
        code_blocks = []
        
        # Pattern for filename: format
        filename_pattern = r'```filename:\s*([^\n]+)\n(.*?)```'
        filename_matches = re.findall(filename_pattern, text, re.DOTALL)
        
        for filename, content in filename_matches:
            language = self._detect_language_from_filename(filename.strip())
            code_blocks.append((filename.strip(), content.strip(), language))
        
        # Pattern for regular code blocks
        code_pattern = r'```(?:([a-zA-Z]+)\n)?(.*?)```'
        all_matches = re.findall(code_pattern, text, re.DOTALL)
        
        for lang_hint, content in all_matches:
            content = content.strip()
            if not content or any(content == existing[1] for existing in code_blocks):
                continue
            
            language, filename = self._detect_language_and_filename(content, lang_hint)
            
            # Avoid duplicates
            counter = 1
            original_filename = filename
            while any(filename == existing[0] for existing in code_blocks):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                counter += 1
            
            code_blocks.append((filename, content, language))
        
        return code_blocks
        
    def _detect_language_from_filename(self, filename: str) -> str:
        """Detect language from filename."""
        ext = os.path.splitext(filename)[1].lower()
        ext_map = {
            '.py': 'python', '.js': 'javascript', '.html': 'html',
            '.css': 'css', '.json': 'json', '.txt': 'text',
            '.md': 'markdown', '.yml': 'yaml', '.yaml': 'yaml',
            '.sql': 'sql', '.sh': 'bash', '.rs': 'rust'
        }
        return ext_map.get(ext, 'text')
        
    def _detect_language_and_filename(self, content: str, lang_hint: str = "") -> tuple:
        """Detect programming language and suggest filename."""
        content_lower = content.lower()
        
        # Python detection
        if ('def ' in content or 'import ' in content or 'from ' in content or 
            'class ' in content or lang_hint == 'python'):
            if 'flask' in content_lower or 'app.run' in content:
                return 'python', 'app.py'
            elif 'requirements' in content_lower:
                return 'text', 'requirements.txt'
            else:
                return 'python', 'main.py'
        
        # HTML detection
        elif ('<html' in content_lower or '<!doctype' in content_lower or 
              '<div' in content_lower or lang_hint == 'html'):
            return 'html', 'index.html'
        
        # CSS detection
        elif ('{' in content and '}' in content and ':' in content and 
              ('color' in content_lower or 'font' in content_lower or lang_hint == 'css')):
            return 'css', 'style.css'
        
        # JavaScript detection
        elif ('function' in content or 'const ' in content or 'let ' in content or 
              'var ' in content or lang_hint == 'javascript'):
            return 'javascript', 'script.js'
        
        # JSON detection
        elif content.strip().startswith('{') and content.strip().endswith('}'):
            return 'json', 'config.json'
        
        return 'text', 'file.txt'
        
    async def _show_completion_summary(self, task: StreamingTask) -> AsyncGenerator[str, None]:
        """Show task completion summary."""
        
        duration = task.end_time - task.start_time if task.start_time and task.end_time else 0
        
        if self.console:
            # Rich completion summary
            summary_table = Table.grid()
            summary_table.add_column(style="bold green")
            summary_table.add_column()
            
            summary_table.add_row("✅", f"Task completed in {duration:.1f}s")
            
            if task.files_created:
                summary_table.add_row("📄", f"Created {len(task.files_created)} files:")
                for file in task.files_created:
                    summary_table.add_row("", f"  • {file}")
                    
            if task.files_modified:
                summary_table.add_row("✏️", f"Modified {len(task.files_modified)} files:")
                for file in task.files_modified:
                    summary_table.add_row("", f"  • {file}")
                    
            panel = Panel(summary_table, title="[bold]Task Summary[/bold]", border_style="green")
            self.console.print(panel)
            
        else:
            # Fallback summary
            yield f"\n✅ Task completed in {duration:.1f}s\n"
            
            if task.files_created:
                yield f"📄 Created {len(task.files_created)} files:\n"
                for file in task.files_created:
                    yield f"  • {file}\n"
                    
            if task.files_modified:
                yield f"✏️ Modified {len(task.files_modified)} files:\n"
                for file in task.files_modified:
                    yield f"  • {file}\n"
                    
    def run_interactive_session(self):
        """Run the interactive streaming session."""
        self.start_session()
        
        if self.console:
            self.console.print("\n[bold cyan]💬 Enter your requests (type 'exit' to quit)[/bold cyan]")
        else:
            click.echo("\n💬 Enter your requests (type 'exit' to quit)")
            
        while True:
            try:
                # Get user input
                if self.console:
                    query = self.console.input("\n[bold blue]>[/bold blue] ")
                else:
                    query = input("\n> ")
                
                if query.lower() in ['exit', 'quit', 'bye']:
                    if self.console:
                        self.console.print("Session ended.")
                    else:
                        click.echo("Session ended.")
                    break
                
                if not query.strip():
                    continue
                    
                # Process query with streaming
                asyncio.run(self._process_query_with_streaming(query))
                
            except KeyboardInterrupt:
                if self.console:
                    self.console.print("\n[yellow]Session interrupted.[/yellow]")
                else:
                    click.echo("\nSession interrupted.")
                break
            except EOFError:
                break
                
    async def _process_query_with_streaming(self, query: str):
        """Process query with full streaming experience."""
        async for chunk in self.stream_agent_response(query):
            if chunk:  # Only print non-empty chunks
                if not self.console:  # Fallback mode
                    print(chunk, end='', flush=True)
                # Rich mode handles printing internally

    def set_streaming_mode(self, mode: StreamingMode):
        """Change streaming mode."""
        self.streaming_mode = mode
        
        # Adjust delays based on mode
        if mode == StreamingMode.CHARACTER:
            self.char_delay = 0.01
        elif mode == StreamingMode.WORD:
            self.word_delay = 0.05
        elif mode == StreamingMode.CHUNK:
            self.char_delay = 0.005
        else:  # INSTANT
            self.char_delay = 0
            self.word_delay = 0


def create_enhanced_streaming_session(
    agent, 
    workspace_path: str = None,
    streaming_mode: StreamingMode = StreamingMode.CHARACTER
) -> EnhancedStreamingInterface:
    """Create a new enhanced streaming session."""
    return EnhancedStreamingInterface(
        agent=agent,
        workspace_path=workspace_path,
        streaming_mode=streaming_mode
    )


# CLI command integration
@click.command()
@click.option('--workspace', '-w', default=None, help='Workspace directory path')
@click.option('--mode', '-m', 
              type=click.Choice(['character', 'word', 'chunk', 'instant']), 
              default='character',
              help='Streaming mode')
@click.option('--session', '-s', help='Session ID')
def stream(workspace, mode, session):
    """Start enhanced streaming interface (Claude Code style)."""
    
    # Import agent
    from ..core import SingleAgent
    from ..core.agent_config import AgentConfig
    
    # Initialize agent
    config = AgentConfig()
    agent = SingleAgent(
        use_titans_memory=config.is_titans_memory_enabled(),
        llm_provider=config.get_llm_provider(),
        llm_model=config.get_llm_model(),
        enhanced_processing=True,
        config=config
    )
    
    # Create streaming interface
    streaming_mode = StreamingMode(mode)
    interface = EnhancedStreamingInterface(
        agent=agent,
        workspace_path=workspace,
        streaming_mode=streaming_mode
    )
    
    # Run interactive session
    interface.run_interactive_session()


if __name__ == "__main__":
    stream()