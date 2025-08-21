"""
Enhanced Status Management System for Metis Code
Provides visual feedback, loading states, and progress tracking for improved UX.
"""

import time
import threading
from enum import Enum
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
    from rich.live import Live
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class StatusLevel(Enum):
    """Status levels with color coding"""
    INACTIVE = ("gray", "○")     # Inactive/Disabled
    READY = ("green", "●")       # Ready/Success  
    WORKING = ("yellow", "●")    # Working/In Progress
    ERROR = ("red", "●")         # Error/Failed
    INFO = ("blue", "●")         # Info/Waiting


@dataclass
class ActivityEntry:
    """Single activity log entry"""
    timestamp: datetime
    component: str
    message: str
    level: StatusLevel


class StatusLight:
    """Individual status indicator for system components"""
    
    def __init__(self, name: str, initial_status: StatusLevel = StatusLevel.INACTIVE):
        self.name = name
        self.status = initial_status
        self.message = ""
        self.progress = None  # (current, total) tuple
        self.last_updated = datetime.now()
    
    def update(self, status: StatusLevel, message: str = "", progress: Optional[Tuple[int, int]] = None):
        """Update status light with new information"""
        self.status = status
        self.message = message
        self.progress = progress
        self.last_updated = datetime.now()
    
    def render_compact(self) -> str:
        """Render compact status representation"""
        color, symbol = self.status.value
        status_text = f"{symbol} {self.name}"
        
        if self.progress:
            current, total = self.progress
            percentage = int((current / total) * 100) if total > 0 else 0
            status_text += f" [{percentage}%]"
        
        return status_text
    
    def render_detailed(self) -> str:
        """Render detailed status with message"""
        color, symbol = self.status.value
        status_text = f"{symbol} {self.name:<12}"
        
        if self.progress:
            current, total = self.progress
            progress_bar = self._create_progress_bar(current, total, width=20)
            status_text += f" {progress_bar} {current}/{total}"
        else:
            status_text += f" [{self.status.name:<8}]"
        
        if self.message:
            status_text += f" {self.message}"
            
        return status_text
    
    def _create_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """Create ASCII progress bar"""
        if total == 0:
            return "[" + "░" * width + "]"
        
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"


class ProgressTracker:
    """Tracks progress of multi-step operations"""
    
    def __init__(self):
        self.operations = {}
        self.active_operation = None
    
    def start_operation(self, operation_id: str, title: str, total_steps: int):
        """Start tracking a new operation"""
        self.operations[operation_id] = {
            'title': title,
            'total_steps': total_steps,
            'current_step': 0,
            'steps': [],
            'started_at': datetime.now(),
            'completed': False
        }
        self.active_operation = operation_id
    
    def update_step(self, operation_id: str, step_name: str, completed: bool = False):
        """Update current step in operation"""
        if operation_id not in self.operations:
            return
        
        op = self.operations[operation_id]
        if completed and op['current_step'] < op['total_steps']:
            op['current_step'] += 1
        
        # Add or update step
        step_found = False
        for i, step in enumerate(op['steps']):
            if step['name'] == step_name:
                step['completed'] = completed
                step['updated_at'] = datetime.now()
                step_found = True
                break
        
        if not step_found:
            op['steps'].append({
                'name': step_name,
                'completed': completed,
                'started_at': datetime.now(),
                'updated_at': datetime.now()
            })
    
    def complete_operation(self, operation_id: str):
        """Mark operation as completed"""
        if operation_id in self.operations:
            self.operations[operation_id]['completed'] = True
            self.operations[operation_id]['completed_at'] = datetime.now()
    
    def get_operation_status(self, operation_id: str) -> Optional[Dict]:
        """Get current status of an operation"""
        return self.operations.get(operation_id)
    
    def render_operation_progress(self, operation_id: str) -> str:
        """Render progress for a specific operation"""
        if operation_id not in self.operations:
            return ""
        
        op = self.operations[operation_id]
        progress = f"{op['current_step']}/{op['total_steps']}"
        percentage = int((op['current_step'] / op['total_steps']) * 100) if op['total_steps'] > 0 else 0
        
        # Create progress bar
        width = 30
        filled = int((op['current_step'] / op['total_steps']) * width) if op['total_steps'] > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        
        result = f"{op['title']}:\n"
        result += f"[{bar}] {percentage}% ({progress})\n"
        
        # Add step details
        for step in op['steps']:
            status_symbol = "✓" if step['completed'] else "▶" if step == op['steps'][-1] else "⧖"
            result += f"├─ {status_symbol} {step['name']}\n"
        
        return result.rstrip()


class ActivityFeed:
    """Manages activity log and real-time updates"""
    
    def __init__(self, max_entries: int = 50):
        self.entries = []
        self.max_entries = max_entries
        self._lock = threading.Lock()
    
    def add_entry(self, component: str, message: str, level: StatusLevel = StatusLevel.INFO):
        """Add new activity entry"""
        with self._lock:
            entry = ActivityEntry(
                timestamp=datetime.now(),
                component=component,
                message=message,
                level=level
            )
            self.entries.append(entry)
            
            # Keep only recent entries
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[-self.max_entries:]
    
    def get_recent_entries(self, count: int = 10) -> List[ActivityEntry]:
        """Get most recent activity entries"""
        with self._lock:
            return self.entries[-count:] if self.entries else []
    
    def render_feed(self, count: int = 10) -> str:
        """Render activity feed as text"""
        entries = self.get_recent_entries(count)
        if not entries:
            return "No recent activity"
        
        result = "ACTIVITY FEED".center(40, "─") + "\n"
        for entry in entries:
            time_str = entry.timestamp.strftime("%H:%M:%S")
            _, symbol = entry.level.value
            result += f"│ {time_str} [{entry.component}] {entry.message}\n"
        
        result += "─" * 40
        return result


class MetisStatusManager:
    """Main status management system for Metis Code"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console() if RICH_AVAILABLE else None
        
        # Core components
        self.status_lights = {
            'llm': StatusLight('LLM Engine'),
            'tools': StatusLight('Tool Registry'), 
            'files': StatusLight('File System'),
            'git': StatusLight('Git Status'),
            'operation': StatusLight('Operation'),
            'confirm': StatusLight('Confirmations')
        }
        
        self.progress_tracker = ProgressTracker()
        self.activity_feed = ActivityFeed()
        
        # Current state
        self.operation_mode = 'balanced'
        self.confirmation_level = 'normal'
        self.interface_mode = 'advanced'
        
        # Display settings
        self.show_dashboard = False
        self.dashboard_style = 'compact'  # compact, detailed, mini
        self.live_display = None
        
    def update_component_status(self, component: str, status: StatusLevel, 
                              message: str = "", progress: Optional[Tuple[int, int]] = None):
        """Update status of a system component"""
        if component in self.status_lights:
            self.status_lights[component].update(status, message, progress)
            self.activity_feed.add_entry(component.upper(), message, status)
    
    def set_operation_mode(self, mode: str, confirmation_level: str = None, interface_mode: str = None):
        """Set current operation modes"""
        self.operation_mode = mode
        if confirmation_level:
            self.confirmation_level = confirmation_level
        if interface_mode:
            self.interface_mode = interface_mode
            
        # Update status lights
        mode_msg = f"Mode: {mode.upper()}"
        self.update_component_status('operation', StatusLevel.INFO, mode_msg)
        
        confirm_msg = f"Level: {self.confirmation_level.upper()}"
        self.update_component_status('confirm', StatusLevel.INFO, confirm_msg)
    
    def render_mode_indicators(self) -> str:
        """Render operation mode indicators"""
        mode_badge = f"[{self.operation_mode.upper()}]"
        if self.operation_mode == 'fast':
            mode_badge += " Quick operations"
        elif self.operation_mode == 'stream':
            mode_badge += " Detailed interface"
        else:
            mode_badge += " Balanced mode"
            
        confirm_badge = f"[{self.confirmation_level.upper()}]"
        if self.confirmation_level == 'minimal':
            confirm_badge += " Auto-confirming"
        elif self.confirmation_level == 'verbose':
            confirm_badge += " Detailed confirmations" 
        else:
            confirm_badge += " Normal confirmations"
            
        return f"Operation: {mode_badge}\nConfirmations: {confirm_badge}"
    
    def render_compact_status(self) -> str:
        """Render compact status bar"""
        status_items = []
        for component, light in self.status_lights.items():
            status_items.append(light.render_compact())
        
        # Group into sections
        core_status = " | ".join(status_items[:4])  # LLM, Tools, Files, Git
        mode_status = " | ".join(status_items[4:])  # Operation, Confirmations
        
        result = "┌─ STATUS " + "─" * 50 + "┐\n"
        result += f"│ {core_status:<56} │\n"
        result += f"│ {mode_status:<56} │\n"
        result += "└" + "─" * 58 + "┘"
        
        return result
    
    def render_detailed_dashboard(self) -> str:
        """Render detailed command center dashboard"""
        result = "┌─ METIS COMMAND CENTER " + "─" * 35 + "┐\n"
        result += "│" + " " * 58 + "│\n"
        
        for component, light in self.status_lights.items():
            status_line = f"│  {light.render_detailed():<54} │"
            result += status_line + "\n"
        
        result += "│" + " " * 58 + "│\n"
        
        # Add session stats
        stats_line = "│  Session: Files created/modified, Operations completed"
        result += f"{stats_line:<59}│\n"
        result += "└" + "─" * 58 + "┘"
        
        return result
    
    def render_mini_dashboard(self) -> str:
        """Render mini status dashboard"""
        result = "┌─ STATUS ──┐\n"
        
        # Show only key components
        key_components = ['llm', 'tools', 'files', 'git']
        for comp in key_components:
            if comp in self.status_lights:
                light = self.status_lights[comp]
                _, symbol = light.status.value
                short_name = comp.upper()[:4]
                result += f"│ {short_name} [{symbol}] │\n"
        
        result += "└──────────┘"
        return result
    
    def start_live_dashboard(self, style: str = 'compact'):
        """Start live updating dashboard"""
        if not RICH_AVAILABLE:
            return
            
        self.dashboard_style = style
        self.show_dashboard = True
        
        # Implementation for Rich live display would go here
        # This is a placeholder for the live updating functionality
    
    def stop_live_dashboard(self):
        """Stop live dashboard updates"""
        self.show_dashboard = False
        if self.live_display:
            self.live_display.stop()
            self.live_display = None
    
    def show_loading_spinner(self, message: str, component: str = 'operation') -> 'LoadingSpinner':
        """Show loading spinner with context"""
        return LoadingSpinner(message, self, component)
    
    def get_activity_summary(self) -> str:
        """Get recent activity summary"""
        return self.activity_feed.render_feed()


class LoadingSpinner:
    """Context manager for loading operations with spinners"""
    
    def __init__(self, message: str, status_manager: MetisStatusManager, component: str = 'operation'):
        self.message = message
        self.status_manager = status_manager
        self.component = component
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.status_manager.update_component_status(
            self.component, StatusLevel.WORKING, self.message
        )
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            # Success
            self.status_manager.update_component_status(
                self.component, StatusLevel.READY, f"Completed in {elapsed:.1f}s"
            )
        else:
            # Error
            self.status_manager.update_component_status(
                self.component, StatusLevel.ERROR, f"Failed: {str(exc_val)}"
            )
    
    def update_message(self, message: str):
        """Update spinner message"""
        self.message = message
        self.status_manager.update_component_status(
            self.component, StatusLevel.WORKING, message
        )


# Module-level status manager instance
_global_status_manager = None

def get_status_manager() -> MetisStatusManager:
    """Get global status manager instance"""
    global _global_status_manager
    if _global_status_manager is None:
        _global_status_manager = MetisStatusManager()
    return _global_status_manager