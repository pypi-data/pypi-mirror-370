"""
Project Management Tool for Metis Agent.

This tool handles project creation, session management, and project structure
following the tool architecture principles.
"""
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import BaseTool
# Code generators removed - using simple project structure creation


class ProjectManagementTool(BaseTool):
    """
    Tool for creating and managing project structures with session tracking.
    
    This tool handles:
    - Project creation with proper directory structure
    - Session tracking with JSON metadata
    - Git repository initialization
    - Planning document generation
    - Project lifecycle management
    """
    
    def __init__(self):
        """Initialize the project management tool."""
        self.name = "ProjectManagementTool"
        self.description = "Creates and manages project structures with session tracking"
        
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle project management tasks.
        
        Args:
            task: The task description
            
        Returns:
            True if task involves project creation or management
        """
        task_lower = task.lower()
        
        # Project creation keywords
        creation_keywords = [
            'create project', 'new project', 'start project', 'build project',
            'make project', 'generate project', 'setup project', 'scaffold project',
            'initialize project', 'create app', 'new app', 'build app',
            'make app', 'develop app', 'create application'
        ]
        
        # Project management keywords
        management_keywords = [
            'project status', 'session info', 'project info',
            'update phase', 'new iteration', 'project lifecycle'
        ]
        
        return any(keyword in task_lower for keyword in creation_keywords + management_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute project management operations.
        
        Args:
            task: The task description
            **kwargs: Additional parameters including:
                - desktop_path: Custom desktop path (optional)
                - project_name: Custom project name (optional)
                - no_git: Skip Git initialization (optional)
                
        Returns:
            Dict containing operation results and project information
        """
        try:
            task_lower = task.lower()
            
            # Determine operation type
            if any(keyword in task_lower for keyword in [
                'create', 'new', 'start', 'build', 'make', 'generate', 
                'setup', 'scaffold', 'initialize', 'develop'
            ]):
                return self._create_project(task, **kwargs)
            elif 'status' in task_lower or 'info' in task_lower:
                return self._get_project_status(**kwargs)
            elif 'phase' in task_lower:
                return self._update_project_phase(task, **kwargs)
            elif 'iteration' in task_lower:
                return self._start_new_iteration(**kwargs)
            else:
                return {
                    "success": False,
                    "error": "Unknown project management operation",
                    "supported_operations": [
                        "create project", "project status", "update phase", "new iteration"
                    ]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Project management operation failed: {str(e)}",
                "task": task
            }
    
    def _create_project(self, task: str, **kwargs) -> Dict[str, Any]:
        """Create a new project structure."""
        # Get desktop path
        desktop_path = kwargs.get('desktop_path')
        if not desktop_path:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            # Expand ~ in provided path
            desktop_path = os.path.expanduser(desktop_path)
        desktop_path = Path(desktop_path)
        
        # Generate project name
        project_name = kwargs.get('project_name') or self._generate_project_name(task)
        
        # Create project directory
        project_dir = desktop_path / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        metis_dir = project_dir / "Metis"
        metis_dir.mkdir(exist_ok=True)
        
        src_dir = project_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Initialize Git repository (unless disabled)
        git_initialized = False
        if not kwargs.get('no_git', False):
            git_initialized = self._initialize_git_repo(project_dir)
        
        # Create session data
        session_data = self._create_session_data(project_name, task, git_initialized)
        
        # Create planning documents
        self._create_planning_documents(metis_dir, task, session_data)
        
        # Generate project code files based on project type
        code_files = self._create_project_code_files(project_dir, task, session_data)
        
        # Create virtual environment if Python project
        venv_created = self._create_virtual_environment(project_dir, session_data)
        
        # Install dependencies if requirements.txt exists
        deps_installed = self._install_dependencies(project_dir)
        
        # Save session.json
        session_file = metis_dir / "session.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "operation": "project_creation",
            "project_name": project_name,
            "project_dir": str(project_dir),
            "metis_dir": str(metis_dir),
            "src_dir": str(src_dir),
            "session_file": str(session_file),
            "git_initialized": git_initialized,
            "venv_created": venv_created,
            "dependencies_installed": deps_installed,
            "code_files_created": code_files,
            "session_data": session_data,
            "message": f"Project '{project_name}' created successfully at {project_dir}"
        }
    
    def _generate_project_name(self, request: str) -> str:
        """Generate a clean project name from the request."""
        # Extract meaningful words
        words = re.findall(r'\b\w+\b', request.lower())
        
        # Filter out common words
        stop_words = {
            'create', 'build', 'make', 'develop', 'generate', 'write', 'add',
            'the', 'a', 'an', 'for', 'with', 'using', 'that', 'this', 'and', 'or'
        }
        
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Take first 4 meaningful words
        project_words = meaningful_words[:4]
        
        if not project_words:
            project_words = ['new', 'project']
        
        # Create clean name
        base_name = '-'.join(project_words)
        
        # Ensure uniqueness
        desktop_path = Path(os.path.join(os.path.expanduser("~"), "Desktop"))
        counter = 1
        project_name = base_name
        while (desktop_path / project_name).exists():
            project_name = f"{base_name}-{counter}"
            counter += 1
        
        return project_name
    
    def _create_session_data(self, project_name: str, request: str, git_initialized: bool) -> Dict[str, Any]:
        """Create initial session data structure."""
        now = datetime.now().isoformat()
        
        # Analyze project type and complexity
        project_type = self._analyze_project_type(request)
        complexity = self._analyze_complexity(request)
        
        return {
            "session_id": f"metis-{project_name.lower()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "project_name": project_name.replace('-', ' ').title(),
            "project_description": request,
            "current_phase": "design",
            "current_iteration": 1,
            "created_at": now,
            "updated_at": now,
            "phases": [
                {"name": "design", "completed": False, "started_at": now},
                {"name": "execution", "completed": False},
                {"name": "review", "completed": False},
                {"name": "iteration", "completed": False}
            ],
            "phase_history": [
                {
                    "event": "project_created",
                    "phase": "design",
                    "timestamp": now,
                    "iteration": 1,
                    "description": f"Project created: {request}"
                }
            ],
            "progress": {
                "tasks_completed": 0,
                "tasks_total": 0,
                "completion_percentage": 0
            },
            "metadata": {
                "project_type": project_type,
                "complexity": complexity,
                "confidence": 0.8,
                "original_request": request
            },
            "git": {
                "initialized": git_initialized,
                "current_branch": "main",
                "branches_created": []
            }
        }
    
    def _analyze_project_type(self, request: str) -> str:
        """Analyze project type from request."""
        request_lower = request.lower()
        
        if any(keyword in request_lower for keyword in ['web', 'website', 'flask', 'django', 'fastapi', 'api']):
            return 'web_application'
        elif any(keyword in request_lower for keyword in ['mobile', 'app', 'android', 'ios', 'react native']):
            return 'mobile_application'
        elif any(keyword in request_lower for keyword in ['desktop', 'gui', 'tkinter', 'qt', 'electron']):
            return 'desktop_application'
        elif any(keyword in request_lower for keyword in ['data', 'analysis', 'ml', 'ai', 'machine learning']):
            return 'data_science'
        elif any(keyword in request_lower for keyword in ['game', 'pygame', 'unity']):
            return 'game'
        elif any(keyword in request_lower for keyword in ['script', 'automation', 'tool']):
            return 'script_tool'
        else:
            return 'general_application'
    
    def _analyze_complexity(self, request: str) -> str:
        """Analyze project complexity from request."""
        request_lower = request.lower()
        
        # Complex indicators
        complex_keywords = [
            'authentication', 'database', 'user management', 'admin panel',
            'payment', 'api integration', 'real-time', 'websocket',
            'microservice', 'deployment', 'docker', 'kubernetes'
        ]
        
        # Simple indicators
        simple_keywords = [
            'simple', 'basic', 'minimal', 'quick', 'prototype',
            'demo', 'example', 'learning', 'tutorial'
        ]
        
        if any(keyword in request_lower for keyword in complex_keywords):
            return 'complex'
        elif any(keyword in request_lower for keyword in simple_keywords):
            return 'simple'
        else:
            return 'medium'
    
    def _analyze_project_requirements(self, request: str) -> Dict[str, Any]:
        """Analyze project requirements from natural language request."""
        request_lower = request.lower()
        
        # Detect application features
        features = []
        if any(word in request_lower for word in ['todo', 'task', 'list', 'manage']):
            features.append('todo_management')
        if any(word in request_lower for word in ['blog', 'post', 'article', 'content']):
            features.append('blog_system')
        if any(word in request_lower for word in ['user', 'auth', 'login', 'register']):
            features.append('user_authentication')
        if any(word in request_lower for word in ['api', 'rest', 'endpoint']):
            features.append('api_endpoints')
        if any(word in request_lower for word in ['dashboard', 'admin', 'panel']):
            features.append('admin_dashboard')
        if any(word in request_lower for word in ['database', 'data', 'store', 'save']):
            features.append('data_persistence')
        if any(word in request_lower for word in ['search', 'filter', 'find']):
            features.append('search_functionality')
        if any(word in request_lower for word in ['upload', 'file', 'image']):
            features.append('file_upload')
        
        # Detect UI preferences
        ui_style = 'modern'
        if any(word in request_lower for word in ['bootstrap', 'material', 'tailwind']):
            ui_style = 'framework_based'
        elif any(word in request_lower for word in ['simple', 'minimal', 'clean']):
            ui_style = 'minimal'
        elif any(word in request_lower for word in ['responsive', 'mobile']):
            ui_style = 'responsive'
        
        # Detect database preferences
        database_type = 'sqlite'  # Default for simplicity
        if any(word in request_lower for word in ['postgres', 'postgresql']):
            database_type = 'postgresql'
        elif any(word in request_lower for word in ['mysql']):
            database_type = 'mysql'
        elif any(word in request_lower for word in ['mongodb', 'mongo']):
            database_type = 'mongodb'
        
        # Detect deployment preferences
        deployment_target = None
        if any(word in request_lower for word in ['heroku']):
            deployment_target = 'heroku'
        elif any(word in request_lower for word in ['netlify']):
            deployment_target = 'netlify'
        elif any(word in request_lower for word in ['vercel']):
            deployment_target = 'vercel'
        elif any(word in request_lower for word in ['docker']):
            deployment_target = 'docker'
        
        return {
            'features': features,
            'ui_style': ui_style,
            'database_type': database_type,
            'deployment_target': deployment_target,
            'complexity': self._analyze_complexity(request),
            'project_type': self._analyze_project_type(request)
        }
    
    def _create_planning_documents(self, metis_dir: Path, request: str, session_data: Dict[str, Any]):
        """Create planning documents (plan.md, tasks.md, design.md)."""
        # Create plan.md
        plan_content = self._generate_plan_content(request, session_data)
        with open(metis_dir / "plan.md", 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        # Create tasks.md
        tasks_content = self._generate_tasks_content(request, session_data)
        with open(metis_dir / "tasks.md", 'w', encoding='utf-8') as f:
            f.write(tasks_content)
        
        # Create design.md
        design_content = self._generate_design_content(request, session_data)
        with open(metis_dir / "design.md", 'w', encoding='utf-8') as f:
            f.write(design_content)
    
    def _generate_plan_content(self, request: str, session_data: Dict[str, Any]) -> str:
        """Generate plan.md content."""
        project_name = session_data['project_name']
        project_type = session_data['metadata']['project_type']
        complexity = session_data['metadata']['complexity']
        
        return f"""# {project_name} - Development Plan

## Project Overview
- **Project:** {project_name}
- **Type:** {project_type.replace('_', ' ').title()}
- **Complexity:** {complexity.upper()}
- **Request:** {request}

## Development Phases

### Phase 1: Design
- [ ] Requirements analysis
- [ ] Architecture planning
- [ ] Technology stack selection
- [ ] UI/UX wireframes (if applicable)

### Phase 2: Execution
- [ ] Core functionality implementation
- [ ] Feature development
- [ ] Integration testing
- [ ] Documentation

### Phase 3: Review
- [ ] Code review
- [ ] Testing and debugging
- [ ] Performance optimization
- [ ] Security review

### Phase 4: Iteration
- [ ] User feedback collection
- [ ] Feature refinement
- [ ] Bug fixes
- [ ] Next iteration planning

## Success Criteria
- Functional implementation meeting requirements
- Clean, maintainable code
- Comprehensive documentation
- Successful testing

---
*Last updated: {session_data['updated_at'][:10]}*
"""
    
    def _generate_tasks_content(self, request: str, session_data: Dict[str, Any]) -> str:
        """Generate tasks.md content."""
        project_name = session_data['project_name']
        project_type = session_data['metadata']['project_type']
        
        return f"""# {project_name} - Task Breakdown

## Current Phase: {session_data['current_phase'].title()}

### Immediate Tasks
- [ ] Set up development environment
- [ ] Create project structure
- [ ] Initialize version control
- [ ] Define core requirements

### Design Phase Tasks
- [ ] Analyze requirements in detail
- [ ] Choose appropriate technology stack
- [ ] Design system architecture
- [ ] Create development timeline

### Implementation Tasks
- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Write unit tests
- [ ] Create user documentation

### Testing & Review Tasks
- [ ] Perform integration testing
- [ ] Code review and refactoring
- [ ] Performance testing
- [ ] Security assessment

## Task Progress
- **Completed:** {session_data['progress']['tasks_completed']}
- **Total:** {session_data['progress']['tasks_total']}
- **Progress:** {session_data['progress']['completion_percentage']}%

---
*Last updated: {session_data['updated_at'][:10]}*
"""
    
    def _generate_design_content(self, request: str, session_data: Dict[str, Any]) -> str:
        """Generate design.md content."""
        project_name = session_data['project_name']
        project_type = session_data['metadata']['project_type']
        complexity = session_data['metadata']['complexity']
        
        return f"""# {project_name} - Technical Design

## Project Specification
- **Project:** {project_name}
- **Type:** {project_type.replace('_', ' ').title()}
- **Complexity:** {complexity.upper()}
- **Request:** {request}

## Architecture Overview
*Architecture will be defined based on project requirements*

### System Components
*To be determined during design phase*

### Data Models
*Data structures will be designed based on project needs*

### Technology Decisions
*Technology stack will be selected based on:*
- Project requirements
- Complexity level
- Performance needs
- Development timeline

## Design Patterns
*Appropriate design patterns will be identified and documented*

## Security Considerations
*Security requirements and implementation approach*

## Performance Requirements
*Performance targets and optimization strategy*

## Deployment Strategy
*Deployment strategy and infrastructure requirements*

## Development Guidelines
- Follow clean code principles
- Implement proper error handling
- Include comprehensive documentation
- Write maintainable and scalable code
- Use version control effectively

## File Structure
```
{session_data['project_name'].lower().replace(' ', '-')}/
├── Metis/              # Project management files
│   ├── plan.md
│   ├── tasks.md
│   ├── design.md
│   └── session.json
├── src/                # Source code
└── README.md           # Project documentation
```

## Next Steps
1. Complete requirements analysis
2. Finalize technology stack selection
3. Create detailed implementation plan
4. Begin development phase

---
*Last updated: {session_data['updated_at'][:10]}*
"""
    
    def _initialize_git_repo(self, project_dir: Path) -> bool:
        """Initialize a Git repository in the project directory."""
        try:
            # Initialize git repository
            subprocess.run(['git', 'init'], cwd=project_dir, check=True, 
                         capture_output=True, text=True)
            
            # Create initial .gitignore
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
PIPFILE.lock

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment variables
.env
.env.local
.env.*.local
"""
            gitignore_file = project_dir / '.gitignore'
            with open(gitignore_file, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            # Add initial files
            subprocess.run(['git', 'add', '.'], cwd=project_dir, check=True,
                         capture_output=True, text=True)
            
            # Initial commit
            subprocess.run(['git', 'commit', '-m', 'Initial project setup'], 
                         cwd=project_dir, check=True, capture_output=True, text=True)
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git not available or failed to initialize
            return False
    
    def _get_project_status(self, **kwargs) -> Dict[str, Any]:
        """Get current project status."""
        # This would detect project directory and return status
        # Implementation would be similar to detect_project_directory
        return {
            "success": True,
            "operation": "status_check",
            "message": "Project status functionality not yet implemented"
        }
    
    def _update_project_phase(self, task: str, **kwargs) -> Dict[str, Any]:
        """Update project phase."""
        return {
            "success": True,
            "operation": "phase_update",
            "message": "Phase update functionality not yet implemented"
        }
    
    def _start_new_iteration(self, **kwargs) -> Dict[str, Any]:
        """Start a new project iteration."""
        return {
            "success": True,
            "operation": "new_iteration",
            "message": "New iteration functionality not yet implemented"
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text", "natural_language"],
            "output_types": ["structured_data", "file_system_operations"],
            "estimated_execution_time": "2-5s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": [
                "create_project", "project_management", "scaffolding",
                "session_tracking", "git_initialization"
            ],
            "api_dependencies": [],
            "memory_usage": "low"
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "create a simple todo app with Python and Flask",
            "start a new web application project",
            "build a data analysis project",
            "create a desktop application with GUI",
            "initialize a new mobile app project",
            "get project status",
            "update project phase to execution",
            "start new iteration"
        ]
    
    def _create_project_code_files(self, project_dir: Path, task: str, session_data: Dict[str, Any]) -> List[str]:
        """Create project structure based on project type (agent will generate actual code)."""
        project_type = session_data['metadata']['project_type']
        project_name = session_data['project_name']
        created_files = []
        
        if project_type == 'web_application':
            created_files.extend(self._create_web_structure(project_dir, project_name, task))
        elif project_type == 'desktop_application':
            created_files.extend(self._create_desktop_structure(project_dir, project_name, task))
        elif project_type == 'script_tool':
            created_files.extend(self._create_cli_structure(project_dir, project_name, task))
        elif project_type == 'data_science':
            created_files.extend(self._create_data_science_structure(project_dir, project_name, task))
        else:
            # Create basic project structure
            created_files.extend(self._create_basic_structure(project_dir, project_name, task))
        
        return created_files
    
    def _create_web_structure(self, project_dir: Path, project_name: str, task: str) -> List[str]:
        """Create web application structure (directories only - agent will generate code)."""
        created_files = []
        
        # Create web application structure (framework-agnostic)
        templates_dir = project_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)
        
        static_dir = project_dir / 'static'
        static_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for static files
        (static_dir / 'css').mkdir(exist_ok=True)
        (static_dir / 'js').mkdir(exist_ok=True)
        (static_dir / 'images').mkdir(exist_ok=True)
        
        # Create tests directory
        tests_dir = project_dir / 'tests'
        tests_dir.mkdir(exist_ok=True)
        
        # Create basic requirements.txt (agent will determine specific frameworks)
        requirements_content = '''# Web framework dependencies will be determined by agent
# Based on project requirements and chosen framework
'''
        with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files.append('requirements.txt')
        
        # Create placeholder main.py (agent will generate actual application code)
        placeholder_content = f'''# {project_name} - Web Application
# This file will be generated by the agent based on requirements
# Agent will determine appropriate framework (Flask, FastAPI, Django, etc.)
'''
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        created_files.append('main.py')
        
        return created_files
    
    def _create_fastapi_files(self, project_dir: Path, project_name: str, task: str) -> List[str]:
        """Create FastAPI application files."""
        created_files = []
        
        # Create main.py
        main_content = f'''"""\n{project_name} - FastAPI Application\n"""\n\nfrom fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel\nfrom typing import List, Optional\n\napp = FastAPI(\n    title="{project_name}",\n    description="A FastAPI application created with Metis Agent",\n    version="1.0.0"\n)\n\nclass Item(BaseModel):\n    id: Optional[int] = None\n    name: str\n    description: Optional[str] = None\n\n# In-memory storage (replace with database in production)\nitems = []\n\n@app.get("/")\nasync def root():\n    return {{"message": "Welcome to {project_name}!"}}\n\n@app.get("/items", response_model=List[Item])\nasync def get_items():\n    return items\n\n@app.post("/items", response_model=Item)\nasync def create_item(item: Item):\n    item.id = len(items) + 1\n    items.append(item)\n    return item\n\n@app.get("/items/{{item_id}}", response_model=Item)\nasync def get_item(item_id: int):\n    for item in items:\n        if item.id == item_id:\n            return item\n    raise HTTPException(status_code=404, detail="Item not found")\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run(app, host="0.0.0.0", port=8000)\n'''
        
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(main_content)
        created_files.append('main.py')
        
        # Create requirements.txt
        requirements_content = '''fastapi>=0.104.0\nuvicorn>=0.24.0\npydantic>=2.0.0\n'''
        with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files.append('requirements.txt')
        
        return created_files
    
    def _create_cli_files(self, project_dir: Path, project_name: str, task: str) -> List[str]:
        """Create CLI application files."""
        created_files = []
        
        # Create main.py
        main_content = f'''"""\n{project_name} - Command Line Tool\n"""\n\nimport click\n\n@click.group()\n@click.version_option(version='1.0.0')\ndef cli():\n    """\n    {project_name} - A CLI tool created with Metis Agent\n    """\n    pass\n\n@cli.command()\n@click.option('--name', default='World', help='Name to greet')\ndef hello(name):\n    """Say hello to someone."""\n    click.echo(f'Hello {{name}}!')\n\n@cli.command()\ndef info():\n    """Show information about this tool."""\n    click.echo(f'{project_name} v1.0.0')\n    click.echo('A command line tool created with Metis Agent')\n\nif __name__ == '__main__':\n    cli()\n'''
        
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(main_content)
        created_files.append('main.py')
        
        # Create requirements.txt
        requirements_content = '''click>=8.0.0\nrich>=13.0.0\n'''
        with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files.append('requirements.txt')
        
        return created_files
    
    def _create_desktop_structure(self, project_dir: Path, project_name: str, task: str) -> List[str]:
        """Create desktop application structure (agent will generate actual code)."""
        created_files = []
        
        # Create placeholder main.py (agent will generate actual desktop application code)
        placeholder_content = f'''# {project_name} - Desktop Application
# This file will be generated by the agent based on requirements
# Agent will determine appropriate GUI framework (tkinter, PyQt, etc.)
'''
        
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        created_files.append('main.py')
        
        # Create requirements.txt (agent will determine GUI framework dependencies)
        requirements_content = '''# GUI framework dependencies will be determined by agent
# Based on project requirements and chosen framework
'''
        with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files.append('requirements.txt')
        
        return created_files
    
    def _create_basic_structure(self, project_dir: Path, project_name: str, task: str) -> List[str]:
        """Create basic project structure (agent will generate actual code)."""
        created_files = []
        
        # Create placeholder main.py (agent will generate actual application code)
        placeholder_content = f'''# {project_name}
# This file will be generated by the agent based on requirements
# Agent will determine appropriate structure and dependencies
'''
        
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        created_files.append('main.py')
        
        # Create requirements.txt (agent will determine dependencies)
        requirements_content = '''# Project dependencies will be determined by agent
# Based on project requirements and functionality
'''
        with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files.append('requirements.txt')
        
        return created_files
    
    def _create_cli_structure(self, project_dir: Path, project_name: str, task: str) -> List[str]:
        """Create CLI application structure (agent will generate actual code)."""
        created_files = []
        
        # Create placeholder main.py (agent will generate actual CLI code)
        placeholder_content = f'''# {project_name} - CLI Tool
# This file will be generated by the agent based on requirements
# Agent will determine appropriate CLI framework (argparse, click, etc.)
'''
        
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        created_files.append('main.py')
        
        # Create requirements.txt (agent will determine CLI dependencies)
        requirements_content = '''# CLI framework dependencies will be determined by agent
# Based on project requirements and chosen framework
'''
        with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files.append('requirements.txt')
        
        return created_files
    
    def _create_data_science_structure(self, project_dir: Path, project_name: str, task: str) -> List[str]:
        """Create data science project structure (agent will generate actual code)."""
        created_files = []
        
        # Create data directory
        data_dir = project_dir / 'data'
        data_dir.mkdir(exist_ok=True)
        (data_dir / 'raw').mkdir(exist_ok=True)
        (data_dir / 'processed').mkdir(exist_ok=True)
        
        # Create notebooks directory
        notebooks_dir = project_dir / 'notebooks'
        notebooks_dir.mkdir(exist_ok=True)
        
        # Create src directory
        src_dir = project_dir / 'src'
        src_dir.mkdir(exist_ok=True)
        
        # Create placeholder main.py (agent will generate actual data science code)
        placeholder_content = f'''# {project_name} - Data Science Project
# This file will be generated by the agent based on requirements
# Agent will determine appropriate libraries (pandas, numpy, sklearn, etc.)
'''
        
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        created_files.append('main.py')
        
        # Create requirements.txt (agent will determine data science dependencies)
        requirements_content = '''# Data science dependencies will be determined by agent
# Based on project requirements (pandas, numpy, sklearn, etc.)
'''
        with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        created_files.append('requirements.txt')
        
        return created_files
    
    def _create_virtual_environment(self, project_dir: Path, session_data: Dict[str, Any]) -> bool:
        """Create Python virtual environment."""
        try:
            subprocess.run(['python', '-m', 'venv', 'venv'], cwd=project_dir, check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _install_dependencies(self, project_dir: Path) -> bool:
        """Install project dependencies."""
        requirements_file = project_dir / 'requirements.txt'
        if not requirements_file.exists():
            return False
        
        try:
            # Try to use virtual environment pip if it exists
            venv_pip = project_dir / 'venv' / 'Scripts' / 'pip.exe'
            if venv_pip.exists():
                subprocess.run([str(venv_pip), 'install', '-r', 'requirements.txt'], 
                             cwd=project_dir, check=True, capture_output=True)
            else:
                subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                             cwd=project_dir, check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
