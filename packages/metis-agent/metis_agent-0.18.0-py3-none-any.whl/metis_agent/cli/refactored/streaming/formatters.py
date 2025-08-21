"""
Streaming output formatters.

Handles formatting and display of streaming content with rich formatting support.
"""
import sys
import time
from typing import Generator, Dict, Any


class StreamingFormatter:
    """Formats streaming output with rich support when available."""
    
    def __init__(self, interface):
        """Initialize with reference to main interface."""
        self.interface = interface
        self.rich_available = self._check_rich_availability()
        self.console = None
        
        if self.rich_available:
            self._initialize_rich_console()
    
    def _check_rich_availability(self) -> bool:
        """Check if Rich library is available."""
        try:
            from rich.console import Console
            return True
        except ImportError:
            return False
    
    def _initialize_rich_console(self):
        """Initialize Rich console if available."""
        if self.rich_available:
            try:
                from rich.console import Console
                self.console = Console(force_terminal=True)
            except Exception:
                self.rich_available = False
    
    def show_session_header(self, session_info: Dict[str, Any]):
        """Display session start header."""
        if self.rich_available and self.console:
            from rich.panel import Panel
            from rich.text import Text
            
            header_text = Text()
            header_text.append("🚀 Metis Streaming Session Started\n", style="bold blue")
            header_text.append(f"Session ID: {session_info['session_id']}\n")
            header_text.append(f"Project: {self.interface.project_location}\n")
            header_text.append(f"Mode: {self.interface.operation_mode}")
            
            panel = Panel(header_text, title="Streaming Interface", border_style="blue")
            self.console.print(panel)
        else:
            print("\n" + "="*60)
            print("🚀 Metis Streaming Session Started")
            print(f"Session ID: {session_info['session_id']}")
            print(f"Project: {self.interface.project_location}")
            print(f"Mode: {self.interface.operation_mode}")
            print("="*60 + "\n")
    
    def show_session_footer(self, session_stats: Dict[str, Any]):
        """Display session end footer."""
        if self.rich_available and self.console:
            from rich.panel import Panel
            from rich.text import Text
            
            footer_text = Text()
            footer_text.append("✅ Session Complete\n", style="bold green")
            footer_text.append(f"Files processed: {session_stats['files_processed']}\n")
            footer_text.append(f"Lines written: {session_stats['lines_written']}\n")
            footer_text.append(f"Duration: {session_stats['uptime_seconds']:.1f}s")
            
            panel = Panel(footer_text, title="Session Summary", border_style="green")
            self.console.print(panel)
        else:
            print("\n" + "="*60)
            print("✅ Session Complete")
            print(f"Files processed: {session_stats['files_processed']}")
            print(f"Lines written: {session_stats['lines_written']}")
            print(f"Duration: {session_stats['uptime_seconds']:.1f}s")
            print("="*60)
    
    def stream_formatted_text(self, text: str) -> Generator[str, None, None]:
        """
        Stream formatted text with rich formatting if available.
        
        Args:
            text: Text to format and stream
            
        Yields:
            Formatted text chunks
        """
        if self.rich_available and self.console:
            # Use Rich for advanced formatting
            yield from self._stream_rich_text(text)
        else:
            # Fallback to plain text streaming
            yield from self.stream_plain_text(text)
    
    def _stream_rich_text(self, text: str) -> Generator[str, None, None]:
        """Stream text with Rich formatting."""
        try:
            from rich.markdown import Markdown
            
            # Split text into paragraphs for streaming
            paragraphs = text.split('\n\n')
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Format as markdown
                    md = Markdown(paragraph)
                    
                    # Capture Rich output
                    with self.console.capture() as capture:
                        self.console.print(md)
                    
                    yield capture.get() + '\n'
                    time.sleep(0.02)  # Small delay for streaming effect
        
        except Exception:
            # Fallback to plain text
            yield from self.stream_plain_text(text)
    
    def stream_plain_text(self, text: str) -> Generator[str, None, None]:
        """
        Stream plain text with typewriter effect.
        
        Args:
            text: Text to stream
            
        Yields:
            Text chunks
        """
        # Stream text word by word for typewriter effect
        words = text.split()
        current_line = ""
        
        for word in words:
            current_line += word + " "
            
            # Stream line when it gets long enough or we hit a natural break
            if len(current_line) > 80 or word.endswith(('.', '!', '?', ':')):
                yield current_line + '\n'
                current_line = ""
                time.sleep(0.01)  # Small delay
        
        # Stream any remaining text
        if current_line.strip():
            yield current_line + '\n'
    
    def show_file_processing_header(self, filename: str, language: str,
                                   index: int, total: int) -> Generator[str, None, None]:
        """
        Show header for file processing.
        
        Args:
            filename: Name of file being processed
            language: Programming language
            index: Current file index
            total: Total number of files
            
        Yields:
            Header content
        """
        if self.rich_available and self.console:
            from rich.panel import Panel
            from rich.text import Text
            
            header_text = Text()
            header_text.append(f"📁 Processing File {index}/{total}\n", style="bold cyan")
            header_text.append(f"File: {filename}\n")
            header_text.append(f"Language: {language}")
            
            panel = Panel(header_text, border_style="cyan")
            with self.console.capture() as capture:
                self.console.print(panel)
            
            yield capture.get() + '\n'
        else:
            yield f"\n📁 Processing File {index}/{total}\n"
            yield f"File: {filename}\n"
            yield f"Language: {language}\n"
            yield "-" * 40 + '\n'
    
    def show_file_creation_success(self, filename: str, 
                                  full_path: str) -> Generator[str, None, None]:
        """
        Show success message for file creation.
        
        Args:
            filename: Filename
            full_path: Full file path
            
        Yields:
            Success message content
        """
        if self.rich_available and self.console:
            from rich.text import Text
            
            success_text = Text()
            success_text.append("✅ ", style="bold green")
            success_text.append(f"Successfully created: {filename}")
            
            with self.console.capture() as capture:
                self.console.print(success_text)
            
            yield capture.get() + '\n'
        else:
            yield f"✅ Successfully created: {filename}\n"
    
    def show_file_creation_error(self, filename: str, 
                                error: str) -> Generator[str, None, None]:
        """
        Show error message for file creation.
        
        Args:
            filename: Filename
            error: Error message
            
        Yields:
            Error message content
        """
        if self.rich_available and self.console:
            from rich.text import Text
            
            error_text = Text()
            error_text.append("❌ ", style="bold red")
            error_text.append(f"Failed to create {filename}: {error}")
            
            with self.console.capture() as capture:
                self.console.print(error_text)
            
            yield capture.get() + '\n'
        else:
            yield f"❌ Failed to create {filename}: {error}\n"
    
    def show_code_preview(self, content: str, language: str) -> Generator[str, None, None]:
        """
        Show code preview when file is not created.
        
        Args:
            content: Code content
            language: Programming language
            
        Yields:
            Code preview content
        """
        if self.rich_available and self.console:
            try:
                from rich.syntax import Syntax
                
                syntax = Syntax(content, language, theme="monokai", line_numbers=True)
                
                with self.console.capture() as capture:
                    self.console.print(syntax)
                
                yield capture.get() + '\n'
            except Exception:
                yield from self._show_plain_code_preview(content)
        else:
            yield from self._show_plain_code_preview(content)
    
    def _show_plain_code_preview(self, content: str) -> Generator[str, None, None]:
        """Show plain code preview without syntax highlighting."""
        yield "```\n"
        
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            yield f"{i:4d} | {line}\n"
            
            # Stream in chunks to avoid overwhelming output
            if i % 20 == 0:
                time.sleep(0.01)
        
        yield "```\n"
    
    def show_pause_message(self):
        """Show session pause message."""
        if self.rich_available and self.console:
            from rich.text import Text
            
            pause_text = Text("⏸️  Session paused - Type 'resume' to continue", style="yellow")
            self.console.print(pause_text)
        else:
            print("⏸️  Session paused - Type 'resume' to continue")
    
    def show_resume_message(self):
        """Show session resume message."""
        if self.rich_available and self.console:
            from rich.text import Text
            
            resume_text = Text("▶️  Session resumed", style="green")
            self.console.print(resume_text)
        else:
            print("▶️  Session resumed")
    
    def show_progress_indicator(self, operation: str, 
                               progress: float = None) -> Generator[str, None, None]:
        """
        Show progress indicator for operations.
        
        Args:
            operation: Description of operation
            progress: Progress percentage (0-100)
            
        Yields:
            Progress indicator updates
        """
        if self.rich_available and self.console:
            if progress is not None:
                from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
                ) as progress_bar:
                    task = progress_bar.add_task(operation, total=100)
                    progress_bar.update(task, completed=progress)
                    
                    # Simulate progress update
                    yield f"Progress: {operation} - {progress:.1f}%\n"
            else:
                # Simple spinner
                spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
                for char in spinner_chars:
                    yield f"\r{char} {operation}"
                    time.sleep(0.1)
        else:
            if progress is not None:
                yield f"Progress: {operation} - {progress:.1f}%\n"
            else:
                yield f"⏳ {operation}...\n"