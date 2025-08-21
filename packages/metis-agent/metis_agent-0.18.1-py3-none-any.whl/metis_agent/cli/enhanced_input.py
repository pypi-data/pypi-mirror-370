"""
Enhanced Input System for Metis CLI

Provides Claude Code-style keyboard shortcuts and enhanced input handling.
"""

import os
import sys
import time
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path

try:
    import readline
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.shortcuts import CompleteStyle
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False


class MetisCompleter(Completer):
    """Custom completer for Metis commands and agents."""
    
    def __init__(self, slash_commands: List[str] = None, agents: List[str] = None):
        self.slash_commands = slash_commands or []
        self.agents = agents or []
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        # Slash command completion
        if text.startswith('/'):
            command_part = text[1:]
            for command in self.slash_commands:
                if command.startswith(command_part):
                    yield Completion(command, start_position=-len(command_part))
        
        # Agent mention completion
        elif '@' in text:
            # Find the last @ symbol
            at_pos = text.rfind('@')
            if at_pos >= 0:
                agent_part = text[at_pos + 1:]
                for agent in self.agents:
                    if agent.startswith(agent_part):
                        yield Completion(agent, start_position=-len(agent_part))


class EnhancedInputHandler:
    """Enhanced input handler with keyboard shortcuts and history."""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.history_file = self._get_history_file()
        self.multiline_mode = False
        self.completer = MetisCompleter()
        
        # Initialize based on available libraries
        if HAS_PROMPT_TOOLKIT:
            self._init_prompt_toolkit()
        elif HAS_READLINE:
            self._init_readline()
        else:
            self._init_basic()
    
    def _get_history_file(self) -> Path:
        """Get history file path for current working directory."""
        # Create .metis_sessions directory in current working directory
        metis_dir = Path.cwd() / ".metis_sessions"
        metis_dir.mkdir(exist_ok=True)
        
        return metis_dir / f"history_{self.session_id}.txt"
    
    def _init_prompt_toolkit(self):
        """Initialize prompt_toolkit for enhanced input."""
        self.input_method = "prompt_toolkit"
        
        # Set up key bindings
        self.bindings = KeyBindings()
        
        # Ctrl+L - Clear screen
        @self.bindings.add(Keys.ControlL)
        def clear_screen(event):
            os.system('cls' if os.name == 'nt' else 'clear')
        
        # Ctrl+@ - Quick agent mention (Changed from Ctrl+M which conflicts with Enter)
        @self.bindings.add('c-@')
        def agent_mention(event):
            event.app.current_buffer.insert_text('@')
        
        # Alt+Enter - Multiline mode (Shift+Enter may not work on all terminals)
        @self.bindings.add('escape', 'enter')
        def multiline_toggle(event):
            self.multiline_mode = not self.multiline_mode
            if self.multiline_mode:
                event.app.current_buffer.insert_text('\n')
        
        # Setup history
        try:
            self.history = FileHistory(str(self.history_file))
        except Exception:
            self.history = None
    
    def _init_readline(self):
        """Initialize readline for basic enhanced input."""
        self.input_method = "readline"
        
        try:
            # Load history
            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
            
            # Set history length
            readline.set_history_length(1000)
            
            # Enable tab completion
            readline.parse_and_bind("tab: complete")
            
        except Exception:
            pass
    
    def _init_basic(self):
        """Initialize basic input fallback."""
        self.input_method = "basic"
    
    def get_input(self, prompt_text: str = "> ") -> str:
        """Get user input with enhanced features."""
        try:
            if self.input_method == "prompt_toolkit":
                return self._get_prompt_toolkit_input(prompt_text)
            elif self.input_method == "readline":
                return self._get_readline_input(prompt_text)
            else:
                return self._get_basic_input(prompt_text)
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception:
            # Fallback to basic input on any error
            return input(prompt_text)
    
    def _get_prompt_toolkit_input(self, prompt_text: str) -> str:
        """Get input using prompt_toolkit."""
        return prompt(
            prompt_text,
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
            key_bindings=self.bindings,
            multiline=self.multiline_mode
        )
    
    def _get_readline_input(self, prompt_text: str) -> str:
        """Get input using readline."""
        try:
            result = input(prompt_text)
            
            # Save to history
            if result.strip():
                readline.add_history(result)
                try:
                    readline.write_history_file(str(self.history_file))
                except Exception:
                    pass
            
            return result
        except Exception:
            return input(prompt_text)
    
    def _get_basic_input(self, prompt_text: str) -> str:
        """Basic input fallback."""
        return input(prompt_text)
    
    def update_completions(self, slash_commands: List[str], agents: List[str]):
        """Update command and agent completions."""
        if hasattr(self, 'completer'):
            self.completer.slash_commands = slash_commands
            self.completer.agents = agents
    
    def clear_history(self):
        """Clear input history."""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            
            if self.input_method == "readline" and HAS_READLINE:
                readline.clear_history()
        except Exception:
            pass
    
    def set_multiline_mode(self, enabled: bool):
        """Enable or disable multiline input mode."""
        self.multiline_mode = enabled
    
    def get_history(self) -> List[str]:
        """Get command history."""
        history = []
        
        try:
            if self.input_method == "readline" and HAS_READLINE:
                length = readline.get_current_history_length()
                for i in range(1, length + 1):
                    history.append(readline.get_history_item(i))
            elif self.history_file.exists():
                history = self.history_file.read_text().strip().split('\n')
        except Exception:
            pass
        
        return [h for h in history if h.strip()]
    
    def search_history(self, query: str) -> List[str]:
        """Search command history."""
        history = self.get_history()
        return [item for item in history if query.lower() in item.lower()]


class KeyboardShortcuts:
    """Keyboard shortcuts manager for Metis CLI."""
    
    # Define shortcut mappings
    SHORTCUTS = {
        'ctrl+l': 'clear_screen',
        'ctrl+c': 'interrupt',
        'ctrl+d': 'exit',
        'ctrl+r': 'search_history',
        'ctrl+@': 'agent_mention',
        'shift+enter': 'multiline_mode',
        'tab': 'autocomplete',
        'ctrl+a': 'beginning_of_line',
        'ctrl+e': 'end_of_line',
        'ctrl+k': 'kill_line',
        'ctrl+u': 'kill_whole_line'
    }
    
    @classmethod
    def get_help_text(cls) -> str:
        """Get help text for keyboard shortcuts."""
        help_text = "Keyboard Shortcuts:\n\n"
        
        shortcuts_desc = {
            'ctrl+l': 'Clear screen',
            'ctrl+c': 'Interrupt current input',
            'ctrl+d': 'Exit Metis',
            'ctrl+r': 'Search command history',
            'ctrl+@': 'Insert @ for agent mention',
            'shift+enter': 'Toggle multiline input mode',
            'tab': 'Auto-complete commands/agents',
            'ctrl+a': 'Move to beginning of line',
            'ctrl+e': 'Move to end of line',
            'ctrl+k': 'Delete from cursor to end of line',
            'ctrl+u': 'Delete entire line'
        }
        
        for shortcut, description in shortcuts_desc.items():
            help_text += f"  {shortcut:<15} - {description}\n"
        
        help_text += "\nNote: Availability depends on your terminal capabilities."
        
        return help_text


def create_enhanced_input(session_id: str = "default") -> EnhancedInputHandler:
    """Create an enhanced input handler."""
    return EnhancedInputHandler(session_id)