"""
Progress Display Utilities for Metis Code
Handles visual feedback for operations without Rich dependency.
"""

import sys
import time
import threading
from typing import Optional, List, Dict, Any


class SimpleSpinner:
    """Simple text-based spinner for operations"""
    
    SPINNER_CHARS = ['|', '/', '-', '\\']
    
    def __init__(self, message: str = "Processing..."):
        self.message = message
        self.running = False
        self.thread = None
        self._char_index = 0
    
    def start(self):
        """Start the spinner animation"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
    
    def stop(self, final_message: str = None):
        """Stop the spinner and show final message"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        # Clear the line and show final message
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        if final_message:
            sys.stdout.write(final_message + '\n')
        sys.stdout.flush()
    
    def update_message(self, message: str):
        """Update spinner message"""
        self.message = message
    
    def _spin(self):
        """Internal spinner animation loop"""
        while self.running:
            char = self.SPINNER_CHARS[self._char_index % len(self.SPINNER_CHARS)]
            sys.stdout.write(f'\r[{char}] {self.message}')
            sys.stdout.flush()
            self._char_index += 1
            time.sleep(0.1)


class SimpleProgressBar:
    """Simple text-based progress bar"""
    
    def __init__(self, total: int, width: int = 40, title: str = "Progress"):
        self.total = total
        self.width = width
        self.title = title
        self.current = 0
    
    def update(self, current: int, message: str = ""):
        """Update progress bar"""
        self.current = current
        percentage = int((current / self.total) * 100) if self.total > 0 else 0
        filled = int((current / self.total) * self.width) if self.total > 0 else 0
        
        bar = '█' * filled + '░' * (self.width - filled)
        progress_text = f"{self.title}: [{bar}] {percentage}% ({current}/{self.total})"
        
        if message:
            progress_text += f" - {message}"
        
        # Clear line and print progress
        sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
        sys.stdout.write(progress_text)
        sys.stdout.flush()
    
    def complete(self, message: str = "Complete"):
        """Mark progress as complete"""
        self.update(self.total, message)
        sys.stdout.write('\n')
        sys.stdout.flush()


class MultiStepProgress:
    """Progress tracker for multi-step operations"""
    
    def __init__(self, title: str):
        self.title = title
        self.steps: List[Dict[str, Any]] = []
        self.current_step = 0
    
    def add_step(self, name: str, description: str = ""):
        """Add a new step to track"""
        self.steps.append({
            'name': name,
            'description': description,
            'completed': False,
            'started': False,
            'start_time': None,
            'end_time': None
        })
    
    def start_step(self, step_index: int):
        """Mark step as started"""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]['started'] = True
            self.steps[step_index]['start_time'] = time.time()
            self.current_step = step_index
            self._display()
    
    def complete_step(self, step_index: int, message: str = ""):
        """Mark step as completed"""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]['completed'] = True
            self.steps[step_index]['end_time'] = time.time()
            if message:
                self.steps[step_index]['description'] = message
            self._display()
    
    def _display(self):
        """Display current progress"""
        completed = sum(1 for step in self.steps if step['completed'])
        total = len(self.steps)
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        print(f"\n{self.title}:")
        
        # Progress bar
        width = 40
        filled = int((completed / total) * width) if total > 0 else 0
        bar = '█' * filled + '░' * (width - filled)
        print(f"[{bar}] {percentage}% ({completed}/{total})")
        
        # Step details
        for i, step in enumerate(self.steps):
            if step['completed']:
                status = '✓'
            elif step['started']:
                status = '▶'
            else:
                status = '⧖'
            
            name = step['name']
            desc = step['description']
            line = f"├─ {status} {name}"
            if desc:
                line += f" - {desc}"
            print(line)
        
        print()  # Empty line for spacing


class TokenCounter:
    """Display live token counting for LLM operations"""
    
    def __init__(self, estimated_total: int = None):
        self.estimated_total = estimated_total
        self.current_tokens = 0
        self.start_time = time.time()
    
    def update(self, tokens: int):
        """Update token count"""
        self.current_tokens = tokens
        elapsed = time.time() - self.start_time
        tokens_per_sec = tokens / elapsed if elapsed > 0 else 0
        
        if self.estimated_total:
            percentage = int((tokens / self.estimated_total) * 100)
            progress_text = f"[THINKING] {tokens}/{self.estimated_total} tokens ({percentage}%) | {elapsed:.1f}s | {tokens_per_sec:.1f} tok/s"
        else:
            progress_text = f"[THINKING] {tokens} tokens | {elapsed:.1f}s | {tokens_per_sec:.1f} tok/s"
        
        # Update display
        sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
        sys.stdout.write(progress_text)
        sys.stdout.flush()
    
    def complete(self):
        """Complete token counting"""
        elapsed = time.time() - self.start_time
        avg_speed = self.current_tokens / elapsed if elapsed > 0 else 0
        final_message = f"[COMPLETE] {self.current_tokens} tokens in {elapsed:.1f}s (avg {avg_speed:.1f} tok/s)"
        
        sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
        sys.stdout.write(final_message + '\n')
        sys.stdout.flush()


class StatusIndicator:
    """Simple status indicator without Rich"""
    
    def __init__(self):
        self.components = {
            'llm': {'status': 'inactive', 'message': ''},
            'tools': {'status': 'inactive', 'message': ''},
            'files': {'status': 'inactive', 'message': ''},
            'git': {'status': 'inactive', 'message': ''}
        }
    
    def update(self, component: str, status: str, message: str = ""):
        """Update component status"""
        if component in self.components:
            self.components[component]['status'] = status
            self.components[component]['message'] = message
    
    def display_compact(self):
        """Display compact status line"""
        status_symbols = {
            'inactive': '○',
            'ready': '●',
            'working': '●',
            'error': '●',
            'info': '●'
        }
        
        status_line = "STATUS: "
        for name, info in self.components.items():
            symbol = status_symbols.get(info['status'], '○')
            status_line += f"{name.upper()}: {symbol} "
        
        print(status_line)
    
    def display_detailed(self):
        """Display detailed status"""
        print("┌─ METIS STATUS " + "─" * 40 + "┐")
        
        for name, info in self.components.items():
            status = info['status'].upper()
            message = info['message']
            line = f"│ {name.upper():<8} [{status:<8}]"
            if message:
                line += f" {message}"
            line += " " * (55 - len(line)) + "│"
            print(line)
        
        print("└" + "─" * 56 + "┘")


class OperationContext:
    """Context manager for operations with visual feedback"""
    
    def __init__(self, operation_name: str, use_spinner: bool = True, 
                 estimated_duration: float = None):
        self.operation_name = operation_name
        self.use_spinner = use_spinner
        self.estimated_duration = estimated_duration
        self.spinner = None
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        
        if self.use_spinner:
            message = f"{self.operation_name}..."
            if self.estimated_duration:
                message += f" (est. {self.estimated_duration:.1f}s)"
            
            self.spinner = SimpleSpinner(message)
            self.spinner.start()
        else:
            print(f"[START] {self.operation_name}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        if self.spinner:
            if exc_type is None:
                self.spinner.stop(f"[COMPLETE] {self.operation_name} ({elapsed:.1f}s)")
            else:
                self.spinner.stop(f"[ERROR] {self.operation_name} failed: {str(exc_val)}")
        else:
            if exc_type is None:
                print(f"[COMPLETE] {self.operation_name} ({elapsed:.1f}s)")
            else:
                print(f"[ERROR] {self.operation_name} failed: {str(exc_val)}")
    
    def update_message(self, message: str):
        """Update operation message"""
        if self.spinner:
            self.spinner.update_message(f"{self.operation_name} - {message}")


def show_loading_states_demo():
    """Demo function to show various loading states"""
    print("=== Metis Code Loading States Demo ===\n")
    
    # Simple spinner
    print("1. Simple Spinner:")
    with OperationContext("Analyzing request complexity"):
        time.sleep(2)
    
    # Progress bar
    print("\n2. Progress Bar:")
    progress = SimpleProgressBar(10, title="Loading tools")
    for i in range(11):
        progress.update(i, f"Loading tool {i}")
        time.sleep(0.3)
    progress.complete("All tools loaded")
    
    # Multi-step progress
    print("\n3. Multi-Step Operation:")
    multi_step = MultiStepProgress("Creating Flask API Project")
    multi_step.add_step("Project setup", "Initializing directory structure")
    multi_step.add_step("Database models", "Creating SQLAlchemy models")
    multi_step.add_step("API routes", "Setting up Flask blueprints")
    multi_step.add_step("Tests", "Generating unit tests")
    
    for i in range(4):
        multi_step.start_step(i)
        time.sleep(1)
        multi_step.complete_step(i, "Completed successfully")
    
    # Token counter
    print("\n4. Token Counter:")
    token_counter = TokenCounter(estimated_total=1000)
    for tokens in range(0, 1001, 50):
        token_counter.update(tokens)
        time.sleep(0.1)
    token_counter.complete()
    
    # Status indicator
    print("\n5. Status Indicator:")
    status = StatusIndicator()
    status.update('llm', 'working', 'GPT-4 processing...')
    status.update('tools', 'ready', '36 tools loaded')
    status.update('files', 'working', 'Writing 3 files...')
    status.update('git', 'ready', 'Branch: main')
    status.display_detailed()
    
    print("\nDemo complete!")


if __name__ == "__main__":
    show_loading_states_demo()