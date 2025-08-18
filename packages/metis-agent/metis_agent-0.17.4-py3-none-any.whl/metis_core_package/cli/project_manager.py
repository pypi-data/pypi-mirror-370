"""
Project Management Module for Metis Code

This module handles full project creation and session management for the natural language
coding interface, similar to Claude Code's project workflow.
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any


class ProjectManager:
    """Manages project creation, session tracking, and project structure."""
    
    def __init__(self, desktop_path: str = None):
        """Initialize project manager with desktop path."""
        if desktop_path is None:
            # Default to user's desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.desktop_path = Path(desktop_path)
    
    def create_new_project(self, project_request: str, agent_response: str = None) -> Dict[str, Any]:
        """
        Create a new project structure based on natural language request.
        
        Args:
            project_request: Natural language description of the project
            agent_response: Optional agent response with project details
            
        Returns:
            Dict with project information and paths
        """
        # Generate project name from request
        project_name = self._generate_project_name(project_request)
        
        # Create project directory on desktop
        project_dir = self.desktop_path / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Create Metis subdirectory
        metis_dir = project_dir / "Metis"
        metis_dir.mkdir(exist_ok=True)
        
        # Create src subdirectory for source code
        src_dir = project_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Initialize Git repository
        git_initialized = self._initialize_git_repo(project_dir)
        
        # Generate session data
        session_data = self._create_session_data(project_name, project_request)
        
        # Update Git status in session data
        session_data['git']['initialized'] = git_initialized
        
        # Create planning documents
        self._create_planning_documents(metis_dir, project_request, agent_response, session_data)
        
        # Save session.json
        session_file = metis_dir / "session.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return {
            "project_name": project_name,
            "project_dir": str(project_dir),
            "metis_dir": str(metis_dir),
            "src_dir": str(src_dir),
            "session_file": str(session_file),
            "session_data": session_data
        }
    
    def _generate_project_name(self, request: str) -> str:
        """Generate a clean project name from the request."""
        # Extract meaningful words and create a clean name
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
        
        # Ensure uniqueness by checking if directory exists
        counter = 1
        project_name = base_name
        while (self.desktop_path / project_name).exists():
            project_name = f"{base_name}-{counter}"
            counter += 1
        
        return project_name
    
    def _create_session_data(self, project_name: str, request: str) -> Dict[str, Any]:
        """Create initial session data structure."""
        now = datetime.now().isoformat()
        
        # Analyze project complexity and type
        complexity = self._analyze_complexity(request)
        project_type = self._detect_project_type(request)
        
        return {
            "session_id": f"metis-{project_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
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
                "initialized": False,
                "current_branch": "main",
                "branches_created": []
            }
        }
    
    def _analyze_complexity(self, request: str) -> str:
        """Analyze project complexity from request."""
        request_lower = request.lower()
        
        # Complex indicators
        complex_indicators = [
            'api', 'database', 'authentication', 'microservice', 'distributed',
            'machine learning', 'ai', 'real-time', 'websocket', 'deployment',
            'docker', 'kubernetes', 'cloud', 'scalable', 'enterprise'
        ]
        
        # Simple indicators
        simple_indicators = [
            'simple', 'basic', 'hello world', 'calculator', 'todo', 'counter',
            'single page', 'static', 'prototype', 'demo'
        ]
        
        if any(indicator in request_lower for indicator in complex_indicators):
            return 'complex'
        elif any(indicator in request_lower for indicator in simple_indicators):
            return 'simple'
        else:
            return 'moderate'
    
    def _detect_project_type(self, request: str) -> str:
        """Detect project type from request."""
        request_lower = request.lower()
        
        type_indicators = {
            'web_app': ['web app', 'website', 'web application', 'frontend', 'backend'],
            'api': ['api', 'rest api', 'graphql', 'endpoint', 'service'],
            'mobile_app': ['mobile app', 'ios', 'android', 'react native', 'flutter'],
            'desktop_app': ['desktop', 'gui', 'tkinter', 'pyqt', 'electron'],
            'cli_tool': ['cli', 'command line', 'terminal', 'script'],
            'data_analysis': ['data analysis', 'pandas', 'numpy', 'jupyter', 'visualization'],
            'machine_learning': ['ml', 'machine learning', 'ai', 'neural network', 'model'],
            'game': ['game', 'pygame', 'unity', 'gaming'],
            'library': ['library', 'package', 'module', 'framework']
        }
        
        for project_type, indicators in type_indicators.items():
            if any(indicator in request_lower for indicator in indicators):
                return project_type
        
        return 'general'
    
    def _create_planning_documents(self, metis_dir: Path, request: str, agent_response: str, session_data: Dict):
        """Create the planning documents (plan.md, tasks.md, design.md)."""
        
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
    
    def _generate_plan_content(self, request: str, session_data: Dict) -> str:
        """Generate plan.md content."""
        project_name = session_data['project_name']
        complexity = session_data['metadata']['complexity']
        project_type = session_data['metadata']['project_type']
        
        return f"""# {project_name} - Development Plan

## Project Overview
- **Project Name:** {project_name}
- **Description:** {request}
- **Complexity Level:** {complexity.upper()}
- **Project Type:** {project_type.replace('_', ' ').title()}
- **Created:** {session_data['created_at'][:10]}

## Objectives
The main goal of this project is to {request.lower()}.

## Success Criteria
- [ ] Core functionality implemented and working
- [ ] Code is well-structured and documented
- [ ] Basic testing completed
- [ ] Project is ready for use/deployment

## Development Phases

### Phase 1: Design (Current)
- [ ] Requirements analysis
- [ ] Architecture planning
- [ ] Technology stack selection
- [ ] Project structure setup

### Phase 2: Execution
- [ ] Core implementation
- [ ] Feature development
- [ ] Integration testing
- [ ] Documentation

### Phase 3: Review
- [ ] Code review and refactoring
- [ ] Performance optimization
- [ ] Bug fixes
- [ ] Final testing

### Phase 4: Iteration
- [ ] Feedback incorporation
- [ ] Feature enhancements
- [ ] Deployment preparation
- [ ] Project completion

## Technology Stack
*To be determined based on requirements*

## Timeline
*Estimated timeline will be updated as development progresses*

## Notes
- This project was created using Metis Code natural language interface
- Session tracking is enabled for continuous development
- All project files are organized in the project directory structure

---
*Last updated: {session_data['updated_at'][:10]}*
"""
    
    def _generate_tasks_content(self, request: str, session_data: Dict) -> str:
        """Generate tasks.md content."""
        project_name = session_data['project_name']
        
        return f"""# {project_name} - Task Breakdown

## Current Phase: Design

### Design Phase Tasks
- [ ] **Requirements Gathering**
  - [ ] Analyze project requirements from: "{request}"
  - [ ] Identify core features and functionality
  - [ ] Define user stories or use cases
  - [ ] Determine technical constraints

- [ ] **Architecture Planning**
  - [ ] Choose appropriate technology stack
  - [ ] Design system architecture
  - [ ] Plan data models and structures
  - [ ] Define API interfaces (if applicable)

- [ ] **Project Setup**
  - [ ] Initialize project structure
  - [ ] Set up development environment
  - [ ] Configure version control
  - [ ] Create initial documentation

### Execution Phase Tasks (Upcoming)
- [ ] **Core Implementation**
  - [ ] Implement main functionality
  - [ ] Create user interface (if applicable)
  - [ ] Set up data persistence
  - [ ] Add error handling

- [ ] **Feature Development**
  - [ ] Implement additional features
  - [ ] Add input validation
  - [ ] Create tests
  - [ ] Optimize performance

### Review Phase Tasks (Future)
- [ ] **Quality Assurance**
  - [ ] Code review and refactoring
  - [ ] Comprehensive testing
  - [ ] Documentation review
  - [ ] Security assessment

### Iteration Phase Tasks (Future)
- [ ] **Refinement**
  - [ ] Incorporate feedback
  - [ ] Add enhancements
  - [ ] Prepare for deployment
  - [ ] Final optimization

## Progress Tracking
- **Tasks Completed:** {session_data['progress']['tasks_completed']}
- **Total Tasks:** {session_data['progress']['tasks_total']}
- **Completion:** {session_data['progress']['completion_percentage']}%

## Notes
- Tasks will be updated as the project progresses
- Use natural language commands with Metis Code to work on specific tasks
- Each completed task should be checked off and dated

---
*Last updated: {session_data['updated_at'][:10]}*
"""
    
    def _generate_design_content(self, request: str, session_data: Dict) -> str:
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

## API Design (if applicable)
*API endpoints and interfaces will be documented here*

## Database Design (if applicable)
*Database schema and relationships will be documented*

## User Interface Design (if applicable)
*UI/UX considerations and mockups will be included*

## Security Considerations
*Security measures and best practices will be documented*

## Performance Requirements
*Performance targets and optimization strategies*

## Testing Strategy
*Testing approach and coverage plans*

## Deployment Architecture
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
    
    def update_session_phase(self, session_file: Path, new_phase: str) -> Dict[str, Any]:
        """Update the current phase in session.json."""
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Update current phase
        old_phase = session_data.get('current_phase', 'design')
        session_data['current_phase'] = new_phase
        session_data['updated_at'] = datetime.now().isoformat()
        
        # Mark old phase as completed
        for phase in session_data.get('phases', []):
            if phase['name'] == old_phase:
                phase['completed'] = True
                phase['completed_at'] = session_data['updated_at']
        
        # Add to phase history
        session_data['phase_history'].append({
            "event": "phase_transition",
            "from_phase": old_phase,
            "to_phase": new_phase,
            "timestamp": session_data['updated_at'],
            "iteration": session_data.get('current_iteration', 1)
        })
        
        # Save updated session
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return session_data
    
    def start_new_iteration(self, session_file: Path) -> Dict[str, Any]:
        """Start a new iteration cycle."""
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Increment iteration
        session_data['current_iteration'] = session_data.get('current_iteration', 1) + 1
        session_data['current_phase'] = 'design'  # Reset to design phase
        session_data['updated_at'] = datetime.now().isoformat()
        
        # Reset phase completion status
        for phase in session_data.get('phases', []):
            phase['completed'] = False
            if 'completed_at' in phase:
                del phase['completed_at']
        
        # Add to phase history
        session_data['phase_history'].append({
            "event": "iteration_start",
            "phase": "design",
            "timestamp": session_data['updated_at'],
            "iteration": session_data['current_iteration']
        })
        
        # Save updated session
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return session_data
    
    def detect_project_directory(self, current_dir: Path = None) -> Optional[Dict[str, Any]]:
        """Detect if we're in a project directory by looking for Metis/session.json."""
        if current_dir is None:
            current_dir = Path.cwd()
        
        # Check current directory and parents for Metis/session.json
        max_depth = 5
        for _ in range(max_depth):
            session_file = current_dir / 'Metis' / 'session.json'
            if session_file.exists():
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    return {
                        'project_dir': current_dir,
                        'metis_dir': current_dir / 'Metis',
                        'session_file': session_file,
                        'session_data': session_data
                    }
                except Exception:
                    pass
            
            # Move up one directory
            parent = current_dir.parent
            if parent == current_dir:  # Reached root
                break
            current_dir = parent
        
        return None
    
    def _initialize_git_repo(self, project_dir: Path) -> bool:
        """Initialize a Git repository in the project directory."""
        import subprocess
        
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
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # Git not available or failed to initialize
            return False
