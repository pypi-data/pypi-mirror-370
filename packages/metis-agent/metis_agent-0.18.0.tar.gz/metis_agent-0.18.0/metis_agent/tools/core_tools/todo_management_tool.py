#!/usr/bin/env python3
"""
TODO Checklist Management Tool for Metis Code
Provides comprehensive task breakdown, tracking, and management similar to Claude Code.
"""

import json
import os
import re
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from ..base import BaseTool


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCategory(Enum):
    """Task categories for organization"""
    SETUP = "setup"
    CODING = "coding"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    DEBUGGING = "debugging"
    RESEARCH = "research"
    REVIEW = "review"
    MAINTENANCE = "maintenance"
    GENERAL = "general"


@dataclass
class TodoTask:
    """Individual task in the TODO system"""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory = TaskCategory.GENERAL
    parent_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: Optional[int] = None  # Minutes
    actual_effort: Optional[int] = None     # Minutes
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_to: str = "agent"
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    progress: float = 0.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert enums to strings
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['category'] = self.category.value
        # Convert datetime objects to ISO strings
        for field_name in ['created_at', 'started_at', 'completed_at']:
            if data[field_name]:
                data[field_name] = data[field_name].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoTask':
        """Create from dictionary"""
        # Convert string enums back to enums
        data['status'] = TaskStatus(data.get('status', 'pending'))
        data['priority'] = TaskPriority(data.get('priority', 'medium'))
        data['category'] = TaskCategory(data.get('category', 'general'))
        
        # Convert ISO strings back to datetime objects
        for field_name in ['created_at', 'started_at', 'completed_at']:
            if data.get(field_name):
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        return cls(**data)


@dataclass
class TodoSession:
    """Collection of tasks for a session or project"""
    id: str
    name: str
    description: str = ""
    tasks: List[TodoTask] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, completed, archived
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tasks': [task.to_dict() for task in self.tasks],
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'status': self.status,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoSession':
        """Create from dictionary"""
        tasks = [TodoTask.from_dict(task_data) for task_data in data.get('tasks', [])]
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            tasks=tasks,
            created_at=datetime.fromisoformat(data['created_at']),
            last_modified=datetime.fromisoformat(data['last_modified']),
            status=data.get('status', 'active'),
            metadata=data.get('metadata', {})
        )


class TaskDecomposer:
    """Automatically breaks down complex requests into manageable tasks"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize task decomposition patterns"""
        return {
            'web_application': [
                {'title': 'Project setup and configuration', 'category': TaskCategory.SETUP, 'effort': 30},
                {'title': 'Database schema design', 'category': TaskCategory.CODING, 'effort': 60},
                {'title': 'Backend API development', 'category': TaskCategory.CODING, 'effort': 180},
                {'title': 'Frontend user interface', 'category': TaskCategory.CODING, 'effort': 240},
                {'title': 'Authentication and authorization', 'category': TaskCategory.CODING, 'effort': 120},
                {'title': 'Testing and validation', 'category': TaskCategory.TESTING, 'effort': 90},
                {'title': 'Documentation', 'category': TaskCategory.DOCUMENTATION, 'effort': 45},
                {'title': 'Deployment setup', 'category': TaskCategory.DEPLOYMENT, 'effort': 60}
            ],
            'api_service': [
                {'title': 'API design and specification', 'category': TaskCategory.SETUP, 'effort': 45},
                {'title': 'Data models and database setup', 'category': TaskCategory.CODING, 'effort': 60},
                {'title': 'Core API endpoints', 'category': TaskCategory.CODING, 'effort': 120},
                {'title': 'Authentication middleware', 'category': TaskCategory.CODING, 'effort': 60},
                {'title': 'Error handling and validation', 'category': TaskCategory.CODING, 'effort': 45},
                {'title': 'API testing', 'category': TaskCategory.TESTING, 'effort': 60},
                {'title': 'API documentation', 'category': TaskCategory.DOCUMENTATION, 'effort': 30}
            ],
            'data_analysis': [
                {'title': 'Data collection and ingestion', 'category': TaskCategory.SETUP, 'effort': 60},
                {'title': 'Data cleaning and preprocessing', 'category': TaskCategory.CODING, 'effort': 90},
                {'title': 'Exploratory data analysis', 'category': TaskCategory.RESEARCH, 'effort': 120},
                {'title': 'Model development and training', 'category': TaskCategory.CODING, 'effort': 180},
                {'title': 'Model evaluation and validation', 'category': TaskCategory.TESTING, 'effort': 90},
                {'title': 'Results visualization', 'category': TaskCategory.CODING, 'effort': 75},
                {'title': 'Report generation', 'category': TaskCategory.DOCUMENTATION, 'effort': 45}
            ],
            'generic_development': [
                {'title': 'Requirements analysis', 'category': TaskCategory.RESEARCH, 'effort': 30},
                {'title': 'Design and architecture', 'category': TaskCategory.SETUP, 'effort': 45},
                {'title': 'Core implementation', 'category': TaskCategory.CODING, 'effort': 120},
                {'title': 'Testing and debugging', 'category': TaskCategory.TESTING, 'effort': 60},
                {'title': 'Documentation', 'category': TaskCategory.DOCUMENTATION, 'effort': 30},
                {'title': 'Code review and optimization', 'category': TaskCategory.REVIEW, 'effort': 45}
            ]
        }
    
    def analyze_request(self, request: str) -> str:
        """Analyze request to determine project type"""
        request_lower = request.lower()
        
        web_indicators = ['web app', 'website', 'frontend', 'backend', 'full stack', 'react', 'vue', 'angular']
        api_indicators = ['api', 'rest', 'graphql', 'service', 'endpoint', 'microservice']
        data_indicators = ['data analysis', 'machine learning', 'ml', 'ai', 'analytics', 'visualization', 'pandas', 'numpy']
        
        if any(indicator in request_lower for indicator in web_indicators):
            return 'web_application'
        elif any(indicator in request_lower for indicator in api_indicators):
            return 'api_service'
        elif any(indicator in request_lower for indicator in data_indicators):
            return 'data_analysis'
        else:
            return 'generic_development'
    
    def decompose_task(self, request: str, context: Dict[str, Any] = None) -> List[TodoTask]:
        """Break down a high-level request into specific tasks"""
        project_type = self.analyze_request(request)
        pattern = self.patterns.get(project_type, self.patterns['generic_development'])
        
        tasks = []
        for i, task_template in enumerate(pattern):
            task = TodoTask(
                id=str(uuid.uuid4()),
                title=task_template['title'],
                description=f"Part of: {request}",
                category=task_template['category'],
                estimated_effort=task_template['effort'],
                priority=TaskPriority.HIGH if i < 3 else TaskPriority.MEDIUM,
                metadata={'generated_from': request, 'project_type': project_type}
            )
            
            # Add dependencies (each task depends on previous one)
            if i > 0:
                task.dependencies = [tasks[i-1].id]
            
            tasks.append(task)
        
        return tasks
    
    def estimate_effort(self, task_description: str) -> int:
        """Estimate effort for a task in minutes"""
        description_lower = task_description.lower()
        
        # Base effort
        base_effort = 45
        
        # Complexity indicators
        if any(word in description_lower for word in ['complex', 'advanced', 'comprehensive']):
            base_effort *= 2
        elif any(word in description_lower for word in ['simple', 'basic', 'quick']):
            base_effort *= 0.5
        
        # Task type modifiers
        if any(word in description_lower for word in ['setup', 'config', 'install']):
            base_effort *= 0.7
        elif any(word in description_lower for word in ['test', 'debug', 'fix']):
            base_effort *= 1.2
        elif any(word in description_lower for word in ['design', 'architecture']):
            base_effort *= 1.5
        
        return max(15, int(base_effort))  # Minimum 15 minutes


class TodoDisplay:
    """Handles visual representation of TODO tasks"""
    
    def render_task_tree(self, tasks: List[TodoTask], show_completed: bool = True) -> str:
        """Render tasks as a hierarchical tree"""
        if not tasks:
            return "No tasks found."
        
        # Filter out completed tasks if requested
        if not show_completed:
            tasks = [task for task in tasks if task.status != TaskStatus.COMPLETED]
        
        # Group by parent/child relationships
        root_tasks = [task for task in tasks if not task.parent_id]
        child_tasks = {task.parent_id: [] for task in tasks if task.parent_id}
        for task in tasks:
            if task.parent_id:
                child_tasks[task.parent_id].append(task)
        
        result = []
        for task in root_tasks:
            result.append(self._render_task_line(task))
            # Render children
            if task.id in child_tasks:
                for i, child in enumerate(child_tasks[task.id]):
                    is_last = i == len(child_tasks[task.id]) - 1
                    prefix = "└─" if is_last else "├─"
                    result.append(f"    {prefix} {self._render_task_line(child)}")
        
        return "\n".join(result)
    
    def _render_task_line(self, task: TodoTask) -> str:
        """Render a single task line"""
        status_symbols = {
            TaskStatus.PENDING: "[ ]",
            TaskStatus.IN_PROGRESS: "[→]",
            TaskStatus.COMPLETED: "[✓]",
            TaskStatus.FAILED: "[✗]",
            TaskStatus.BLOCKED: "[!]",
            TaskStatus.CANCELLED: "[-]"
        }
        
        symbol = status_symbols[task.status]
        title = task.title
        
        # Add progress indicator for in-progress tasks
        if task.status == TaskStatus.IN_PROGRESS and task.progress > 0:
            progress = int(task.progress * 100)
            title += f" ({progress}%)"
        
        # Add effort estimate
        if task.estimated_effort:
            effort_hours = task.estimated_effort // 60
            effort_mins = task.estimated_effort % 60
            if effort_hours > 0:
                title += f" [~{effort_hours}h{effort_mins}m]"
            else:
                title += f" [~{effort_mins}m]"
        
        return f"{symbol} {title}"
    
    def render_progress_summary(self, tasks: List[TodoTask]) -> str:
        """Render overall progress summary"""
        if not tasks:
            return "No tasks to show."
        
        total = len(tasks)
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        in_progress = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
        failed = len([t for t in tasks if t.status == TaskStatus.FAILED])
        
        # Calculate progress percentage
        progress_pct = (completed / total * 100) if total > 0 else 0
        
        # Create progress bar
        bar_length = 20
        filled = int(progress_pct / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Estimate remaining time
        remaining_tasks = [t for t in tasks if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]
        total_estimated_effort = sum(t.estimated_effort or 0 for t in remaining_tasks)
        
        result = [
            f"Progress: [{bar}] {progress_pct:.1f}% ({completed}/{total} tasks)",
            f"Status: {completed} completed, {in_progress} in progress, {failed} failed"
        ]
        
        if total_estimated_effort > 0:
            hours = total_estimated_effort // 60
            minutes = total_estimated_effort % 60
            if hours > 0:
                result.append(f"Estimated remaining: {hours}h {minutes}m")
            else:
                result.append(f"Estimated remaining: {minutes}m")
        
        return "\n".join(result)
    
    def render_next_actions(self, tasks: List[TodoTask], limit: int = 3) -> str:
        """Render suggested next actions"""
        # Find tasks that are ready to work on (no pending dependencies)
        ready_tasks = []
        for task in tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                if not task.dependencies or all(
                    any(t.id == dep_id and t.status == TaskStatus.COMPLETED for t in tasks)
                    for dep_id in task.dependencies
                ):
                    ready_tasks.append(task)
        
        # Sort by priority and creation order
        priority_order = {TaskPriority.CRITICAL: 4, TaskPriority.HIGH: 3, TaskPriority.MEDIUM: 2, TaskPriority.LOW: 1}
        ready_tasks.sort(key=lambda t: (priority_order[t.priority], t.created_at), reverse=True)
        
        if not ready_tasks:
            return "No tasks ready to start."
        
        result = ["Next suggested actions:"]
        for i, task in enumerate(ready_tasks[:limit], 1):
            effort_str = f" (~{task.estimated_effort}m)" if task.estimated_effort else ""
            result.append(f"{i}. {task.title}{effort_str}")
        
        return "\n".join(result)


class TodoManager:
    """Core TODO management functionality"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or os.path.expanduser("~/.metis/todos"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.decomposer = TaskDecomposer()
        self.display = TodoDisplay()
        self.current_session: Optional[TodoSession] = None
    
    def create_session(self, name: str, description: str = "") -> TodoSession:
        """Create a new TODO session"""
        session = TodoSession(
            id=str(uuid.uuid4()),
            name=name,
            description=description
        )
        self.current_session = session
        self.save_session(session)
        return session
    
    def load_session(self, session_id: str) -> Optional[TodoSession]:
        """Load an existing session"""
        session_file = self.storage_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            session = TodoSession.from_dict(data)
            self.current_session = session
            return session
        except Exception:
            return None
    
    def save_session(self, session: TodoSession) -> bool:
        """Save session to storage"""
        try:
            session.last_modified = datetime.now()
            session_file = self.storage_dir / f"{session.id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions"""
        sessions = []
        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                sessions.append({
                    'id': data['id'],
                    'name': data['name'],
                    'description': data.get('description', ''),
                    'status': data.get('status', 'active'),
                    'last_modified': data['last_modified'],
                    'task_count': len(data.get('tasks', []))
                })
            except Exception:
                continue
        
        # Sort by last modified
        sessions.sort(key=lambda s: s['last_modified'], reverse=True)
        return sessions
    
    def add_task(self, title: str, description: str = "", **kwargs) -> Optional[TodoTask]:
        """Add a new task to current session"""
        if not self.current_session:
            return None
        
        task = TodoTask(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            category=kwargs.get('category', TaskCategory.GENERAL),
            priority=kwargs.get('priority', TaskPriority.MEDIUM),
            estimated_effort=kwargs.get('estimated_effort')
        )
        
        self.current_session.tasks.append(task)
        self.save_session(self.current_session)
        return task
    
    def update_task_status(self, task_id: str, status: TaskStatus, progress: float = None) -> bool:
        """Update task status"""
        if not self.current_session:
            return False
        
        for task in self.current_session.tasks:
            if task.id == task_id:
                task.status = status
                if progress is not None:
                    task.progress = progress
                
                # Update timestamps
                if status == TaskStatus.IN_PROGRESS and not task.started_at:
                    task.started_at = datetime.now()
                elif status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.now()
                    task.progress = 1.0
                    if task.started_at:
                        task.actual_effort = int((datetime.now() - task.started_at).total_seconds() / 60)
                
                self.save_session(self.current_session)
                return True
        
        return False
    
    def get_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[TodoTask]:
        """Get tasks from current session with optional filtering"""
        if not self.current_session:
            return []
        
        tasks = self.current_session.tasks
        if status_filter:
            tasks = [task for task in tasks if task.status == status_filter]
        
        return tasks
    
    def decompose_request(self, request: str) -> List[TodoTask]:
        """Automatically break down a request into tasks"""
        return self.decomposer.decompose_task(request)
    
    def suggest_next_task(self) -> Optional[TodoTask]:
        """Suggest the next task to work on"""
        tasks = self.get_tasks()
        if not tasks:
            return None
        
        # Find ready tasks (no pending dependencies)
        ready_tasks = []
        for task in tasks:
            if task.status == TaskStatus.PENDING:
                if not task.dependencies or all(
                    any(t.id == dep_id and t.status == TaskStatus.COMPLETED for t in tasks)
                    for dep_id in task.dependencies
                ):
                    ready_tasks.append(task)
        
        if not ready_tasks:
            return None
        
        # Sort by priority
        priority_order = {TaskPriority.CRITICAL: 4, TaskPriority.HIGH: 3, TaskPriority.MEDIUM: 2, TaskPriority.LOW: 1}
        ready_tasks.sort(key=lambda t: priority_order[t.priority], reverse=True)
        
        return ready_tasks[0]


class TodoManagementTool(BaseTool):
    """Main TODO management tool for Metis Code"""
    
    def __init__(self):
        self.name = "TodoManagementTool"
        self.description = "Comprehensive TODO checklist management with automatic task breakdown and progress tracking"
        self.version = "1.0.0"
        self.category = "core_tools"
        
        self.manager = TodoManager()
    
    def can_handle(self, task: str) -> bool:
        """Check if this tool can handle TODO-related tasks"""
        task_lower = task.lower()
        
        todo_keywords = [
            'todo', 'task', 'checklist', 'progress', 'breakdown',
            'create tasks', 'track progress', 'manage tasks',
            'next task', 'task status', 'complete task'
        ]
        
        return any(keyword in task_lower for keyword in todo_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute TODO management operations"""
        try:
            task_lower = task.lower()
            
            # Parse command type
            if 'create session' in task_lower or 'new session' in task_lower:
                return self._create_session(task, kwargs)
            elif 'list sessions' in task_lower or 'show sessions' in task_lower:
                return self._list_sessions()
            elif 'load session' in task_lower or 'switch session' in task_lower:
                return self._load_session(kwargs.get('session_id'))
            elif 'breakdown' in task_lower or 'decompose' in task_lower:
                return self._decompose_request(kwargs.get('request', task))
            elif 'add task' in task_lower or 'create task' in task_lower:
                return self._add_task(task, kwargs)
            elif 'update task' in task_lower or 'complete task' in task_lower:
                return self._update_task(kwargs)
            elif 'list tasks' in task_lower or 'show tasks' in task_lower:
                return self._list_tasks(kwargs)
            elif 'next task' in task_lower or 'suggest task' in task_lower:
                return self._suggest_next_task()
            elif 'progress' in task_lower or 'status' in task_lower:
                return self._show_progress()
            else:
                return self._show_help()
        
        except Exception as e:
            return self._error_response(f"TODO management failed: {str(e)}")
    
    def _create_session(self, task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Create new TODO session"""
        name = kwargs.get('name') or self._extract_session_name(task)
        description = kwargs.get('description', '')
        
        session = self.manager.create_session(name, description)
        
        return {
            'success': True,
            'type': 'todo_session_created',
            'data': {
                'session_id': session.id,
                'session_name': session.name,
                'description': session.description,
                'created_at': session.created_at.isoformat()
            },
            'message': f"Created TODO session: {session.name}"
        }
    
    def _list_sessions(self) -> Dict[str, Any]:
        """List all TODO sessions"""
        sessions = self.manager.list_sessions()
        
        return {
            'success': True,
            'type': 'todo_sessions_list',
            'data': {
                'sessions': sessions,
                'total_count': len(sessions)
            },
            'message': f"Found {len(sessions)} TODO sessions"
        }
    
    def _load_session(self, session_id: Optional[str]) -> Dict[str, Any]:
        """Load existing TODO session"""
        if not session_id:
            return self._error_response("Session ID required")
        
        session = self.manager.load_session(session_id)
        if not session:
            return self._error_response(f"Session not found: {session_id}")
        
        return {
            'success': True,
            'type': 'todo_session_loaded',
            'data': {
                'session_id': session.id,
                'session_name': session.name,
                'task_count': len(session.tasks),
                'last_modified': session.last_modified.isoformat()
            },
            'message': f"Loaded TODO session: {session.name}"
        }
    
    def _decompose_request(self, request: str) -> Dict[str, Any]:
        """Automatically decompose request into tasks"""
        tasks = self.manager.decompose_request(request)
        
        # Add tasks to current session if one exists
        if self.manager.current_session:
            self.manager.current_session.tasks.extend(tasks)
            self.manager.save_session(self.manager.current_session)
        
        return {
            'success': True,
            'type': 'todo_request_decomposed',
            'data': {
                'original_request': request,
                'generated_tasks': [task.to_dict() for task in tasks],
                'task_count': len(tasks),
                'estimated_total_effort': sum(task.estimated_effort or 0 for task in tasks)
            },
            'visual_output': self.manager.display.render_task_tree(tasks),
            'message': f"Broke down request into {len(tasks)} tasks"
        }
    
    def _add_task(self, task_description: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add new task to current session"""
        if not self.manager.current_session:
            return self._error_response("No active session. Create a session first.")
        
        title = kwargs.get('title') or self._extract_task_title(task_description)
        description = kwargs.get('description', '')
        
        task = self.manager.add_task(title, description, **kwargs)
        
        return {
            'success': True,
            'type': 'todo_task_added',
            'data': task.to_dict(),
            'message': f"Added task: {task.title}"
        }
    
    def _update_task(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Update task status"""
        task_id = kwargs.get('task_id')
        status_str = kwargs.get('status', 'completed')
        
        if not task_id:
            return self._error_response("Task ID required")
        
        try:
            status = TaskStatus(status_str)
        except ValueError:
            return self._error_response(f"Invalid status: {status_str}")
        
        success = self.manager.update_task_status(task_id, status)
        
        if success:
            return {
                'success': True,
                'type': 'todo_task_updated',
                'data': {'task_id': task_id, 'status': status_str},
                'message': f"Updated task status to: {status_str}"
            }
        else:
            return self._error_response("Failed to update task")
    
    def _list_tasks(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """List tasks in current session"""
        if not self.manager.current_session:
            return self._error_response("No active session")
        
        status_filter = kwargs.get('status')
        if status_filter:
            try:
                status_filter = TaskStatus(status_filter)
            except ValueError:
                status_filter = None
        
        tasks = self.manager.get_tasks(status_filter)
        
        return {
            'success': True,
            'type': 'todo_tasks_list',
            'data': {
                'tasks': [task.to_dict() for task in tasks],
                'task_count': len(tasks),
                'session_name': self.manager.current_session.name
            },
            'visual_output': self.manager.display.render_task_tree(tasks),
            'message': f"Found {len(tasks)} tasks"
        }
    
    def _suggest_next_task(self) -> Dict[str, Any]:
        """Suggest next task to work on"""
        if not self.manager.current_session:
            return self._error_response("No active session")
        
        next_task = self.manager.suggest_next_task()
        
        if next_task:
            return {
                'success': True,
                'type': 'todo_next_task_suggested',
                'data': next_task.to_dict(),
                'message': f"Next suggested task: {next_task.title}"
            }
        else:
            return {
                'success': True,
                'type': 'todo_no_next_task',
                'data': {},
                'message': "No tasks ready to start"
            }
    
    def _show_progress(self) -> Dict[str, Any]:
        """Show progress summary"""
        if not self.manager.current_session:
            return self._error_response("No active session")
        
        tasks = self.manager.get_tasks()
        progress_text = self.manager.display.render_progress_summary(tasks)
        next_actions_text = self.manager.display.render_next_actions(tasks)
        
        return {
            'success': True,
            'type': 'todo_progress_summary',
            'data': {
                'session_name': self.manager.current_session.name,
                'total_tasks': len(tasks),
                'completed_tasks': len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
                'in_progress_tasks': len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
            },
            'visual_output': f"{progress_text}\n\n{next_actions_text}",
            'message': "Progress summary generated"
        }
    
    def _show_help(self) -> Dict[str, Any]:
        """Show help information"""
        help_text = """
TODO Management Commands:

Session Management:
- create session "name" - Create new TODO session
- list sessions - Show all sessions
- load session <id> - Switch to session

Task Management:  
- breakdown "request" - Auto-decompose request into tasks
- add task "title" - Add new task manually
- list tasks - Show all tasks in current session
- update task <id> completed - Mark task as completed
- next task - Get suggested next task
- progress - Show progress summary

Examples:
- breakdown "create a todo app with React"
- add task "write unit tests"
- update task abc123 completed
"""
        
        return {
            'success': True,
            'type': 'todo_help',
            'data': {'commands': help_text},
            'visual_output': help_text.strip(),
            'message': "TODO management help"
        }
    
    def _extract_session_name(self, task: str) -> str:
        """Extract session name from task description"""
        # Look for quoted names first
        quoted_match = re.search(r'"([^"]+)"', task)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for "session" followed by name
        session_match = re.search(r'session\s+([^\s]+)', task, re.IGNORECASE)
        if session_match:
            return session_match.group(1)
        
        # Default name with timestamp
        return f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _extract_task_title(self, task: str) -> str:
        """Extract task title from description"""
        # Look for quoted titles
        quoted_match = re.search(r'"([^"]+)"', task)
        if quoted_match:
            return quoted_match.group(1)
        
        # Remove common prefixes
        cleaned = re.sub(r'^(add|create|make)\s+(task\s+)?', '', task, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'success': False,
            'type': 'todo_error',
            'error': message,
            'suggestions': [
                "Use 'todo help' for available commands",
                "Create a session first with 'create session \"name\"'",
                "Use breakdown for automatic task generation"
            ]
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capabilities"""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["natural_language", "structured_commands"],
            "output_types": ["task_lists", "progress_summaries", "visual_trees"],
            "features": [
                "automatic_task_breakdown",
                "progress_tracking",
                "session_management", 
                "dependency_management",
                "effort_estimation",
                "next_task_suggestions"
            ],
            "supported_project_types": [
                "web_applications",
                "api_services", 
                "data_analysis",
                "generic_development"
            ]
        }
    
    def get_examples(self) -> List[str]:
        """Get example usage patterns"""
        return [
            'Create session "My Project" for todo management',
            'Breakdown "build a REST API with authentication"',
            'Add task "write integration tests"',
            'List all pending tasks',
            'Update task abc123 to completed status',
            'Show current progress and next actions',
            'Suggest next task to work on'
        ]