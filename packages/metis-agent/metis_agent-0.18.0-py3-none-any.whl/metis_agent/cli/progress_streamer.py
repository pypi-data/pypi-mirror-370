"""
Real-time Progress Streaming System for Claude-like Experience.

This module provides streaming progress updates during blueprint execution,
creating a seamless, interactive experience similar to Claude Code.
"""
import time
import threading
from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass


class ProgressStatus(Enum):
    """Status of a progress step."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProgressStep:
    """A single progress step."""
    id: str
    title: str
    description: str = ""
    status: ProgressStatus = ProgressStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    substeps: List['ProgressStep'] = None
    
    def __post_init__(self):
        if self.substeps is None:
            self.substeps = []


class ProgressStreamer:
    """
    Real-time progress streaming system that provides Claude-like experience
    with beautiful CLI formatting and live updates.
    """
    
    def __init__(self, output_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the progress streamer.
        
        Args:
            output_callback: Function to call for output (defaults to print)
        """
        self.output_callback = output_callback or print
        self.steps: Dict[str, ProgressStep] = {}
        self.current_step: Optional[str] = None
        self.lock = threading.Lock()
        
        # Icons and formatting
        self.icons = {
            ProgressStatus.PENDING: "⏳",
            ProgressStatus.RUNNING: "🔄", 
            ProgressStatus.COMPLETED: "✅",
            ProgressStatus.FAILED: "❌"
        }
        
        self.phase_icons = {
            "analyze": "🔍",
            "setup": "🏗️",
            "generate": "📝",
            "test": "🧪",
            "finalize": "🚀"
        }
    
    def add_step(self, step_id: str, title: str, description: str = "", phase: str = "") -> None:
        """Add a new progress step."""
        with self.lock:
            icon = self.phase_icons.get(phase, "📋")
            formatted_title = f"{icon} {title}"
            
            self.steps[step_id] = ProgressStep(
                id=step_id,
                title=formatted_title,
                description=description
            )
    
    def add_substep(self, parent_id: str, substep_id: str, title: str, description: str = "") -> None:
        """Add a substep to an existing step."""
        with self.lock:
            if parent_id in self.steps:
                substep = ProgressStep(
                    id=substep_id,
                    title=title,
                    description=description
                )
                self.steps[parent_id].substeps.append(substep)
    
    def start_step(self, step_id: str) -> None:
        """Start executing a step."""
        with self.lock:
            if step_id in self.steps:
                step = self.steps[step_id]
                step.status = ProgressStatus.RUNNING
                step.start_time = time.time()
                self.current_step = step_id
                self._display_step_start(step)
    
    def complete_step(self, step_id: str, result_message: str = "") -> None:
        """Mark a step as completed."""
        with self.lock:
            if step_id in self.steps:
                step = self.steps[step_id]
                step.status = ProgressStatus.COMPLETED
                step.end_time = time.time()
                self._display_step_complete(step, result_message)
    
    def fail_step(self, step_id: str, error_message: str = "") -> None:
        """Mark a step as failed."""
        with self.lock:
            if step_id in self.steps:
                step = self.steps[step_id]
                step.status = ProgressStatus.FAILED
                step.end_time = time.time()
                self._display_step_failed(step, error_message)
    
    def update_substep(self, parent_id: str, substep_id: str, status: ProgressStatus, message: str = "") -> None:
        """Update a substep status."""
        with self.lock:
            if parent_id in self.steps:
                parent = self.steps[parent_id]
                for substep in parent.substeps:
                    if substep.id == substep_id:
                        substep.status = status
                        if status == ProgressStatus.RUNNING:
                            substep.start_time = time.time()
                        elif status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED]:
                            substep.end_time = time.time()
                        
                        self._display_substep_update(substep, message)
                        break
    
    def _display_step_start(self, step: ProgressStep) -> None:
        """Display step start."""
        self.output_callback(f"\n{step.title}")
        if step.description:
            self.output_callback(f"   └─ {step.description}")
    
    def _display_step_complete(self, step: ProgressStep, result_message: str) -> None:
        """Display step completion."""
        duration = ""
        if step.start_time and step.end_time:
            duration = f" ({step.end_time - step.start_time:.1f}s)"
        
        if result_message:
            self.output_callback(f"   └─ ✅ {result_message}{duration}")
        
        # Display completed substeps
        for substep in step.substeps:
            if substep.status == ProgressStatus.COMPLETED:
                icon = self.icons[substep.status]
                self.output_callback(f"   ├─ {icon} {substep.title}")
    
    def _display_step_failed(self, step: ProgressStep, error_message: str) -> None:
        """Display step failure."""
        if error_message:
            self.output_callback(f"   └─ ❌ {error_message}")
    
    def _display_substep_update(self, substep: ProgressStep, message: str) -> None:
        """Display substep update."""
        icon = self.icons[substep.status]
        display_message = message or substep.title
        self.output_callback(f"   ├─ {icon} {display_message}")
    
    def display_summary(self) -> None:
        """Display final summary of all steps."""
        with self.lock:
            completed = sum(1 for step in self.steps.values() if step.status == ProgressStatus.COMPLETED)
            failed = sum(1 for step in self.steps.values() if step.status == ProgressStatus.FAILED)
            total = len(self.steps)
            
            if failed == 0:
                self.output_callback(f"\n🎉 All steps completed successfully! ({completed}/{total})")
            else:
                self.output_callback(f"\n⚠️  Completed with {failed} failed steps ({completed}/{total})")


class BlueprintProgressStreamer(ProgressStreamer):
    """
    Specialized progress streamer for blueprint execution with predefined
    phases that match the Claude Code Enhancement Plan.
    """
    
    def __init__(self, blueprint_name: str, output_callback: Optional[Callable[[str], None]] = None):
        """Initialize blueprint progress streamer."""
        super().__init__(output_callback)
        self.blueprint_name = blueprint_name
        self._setup_blueprint_phases()
    
    def _setup_blueprint_phases(self) -> None:
        """Set up standard blueprint execution phases."""
        self.add_step(
            "analyze", 
            "Analyzing requirements", 
            "Understanding project requirements and features",
            "analyze"
        )
        
        self.add_step(
            "setup", 
            "Setting up project structure", 
            "Creating directories and management files",
            "setup"
        )
        
        self.add_step(
            "generate", 
            "Generating application code", 
            "Creating complete, working application files",
            "generate"
        )
        
        self.add_step(
            "test", 
            "Creating tests", 
            "Generating unit tests and validation",
            "test"
        )
        
        self.add_step(
            "finalize", 
            "Finalizing project", 
            "Setting up dependencies and documentation",
            "finalize"
        )
    
    def start_blueprint_execution(self) -> None:
        """Start blueprint execution with initial message."""
        self.output_callback(f"\n[BLUEPRINT] Executing '{self.blueprint_name}' blueprint...\n")
    
    def complete_blueprint_execution(self, project_path: str) -> None:
        """Complete blueprint execution with final instructions."""
        self.display_summary()
        self.output_callback(f"\n🚀 Project ready! Run your application:")
        self.output_callback(f"   cd {project_path}")
        self.output_callback(f"   python app.py")
        self.output_callback(f"\n   Then open: http://localhost:5000")


# Global progress streamer instance for easy access
_global_streamer: Optional[ProgressStreamer] = None


def get_progress_streamer() -> Optional[ProgressStreamer]:
    """Get the global progress streamer instance."""
    return _global_streamer


def set_progress_streamer(streamer: ProgressStreamer) -> None:
    """Set the global progress streamer instance."""
    global _global_streamer
    _global_streamer = streamer


def clear_progress_streamer() -> None:
    """Clear the global progress streamer instance."""
    global _global_streamer
    _global_streamer = None
