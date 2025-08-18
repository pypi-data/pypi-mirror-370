"""
Project handling functionality for CLI commands.

Handles project creation, detection, validation and management.
"""
import os
import glob
import random
import string
from pathlib import Path
from typing import Dict, Optional, Tuple


class ProjectHandler:
    """Handles project-related operations."""
    
    def generate_project_name(self, user_request: str) -> str:
        """
        Generate a project name from user request.
        
        Args:
            user_request: The user's natural language request
            
        Returns:
            Generated project name
        """
        # Convert to lowercase and replace spaces/special chars with hyphens
        name = user_request.lower()
        name = ''.join(c if c.isalnum() else '-' for c in name)
        
        # Remove multiple consecutive hyphens
        while '--' in name:
            name = name.replace('--', '-')
        
        # Remove leading/trailing hyphens
        name = name.strip('-')
        
        # Limit length and ensure it's valid
        name = name[:50] if len(name) > 50 else name
        
        if not name or name == '-':
            # Generate random name if processing failed
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            name = f"project-{suffix}"
        
        return name
    
    def detect_existing_project(self, current_dir: str) -> Dict:
        """
        Detect existing project in the current directory.
        
        Args:
            current_dir: Directory to check
            
        Returns:
            Dictionary with project detection results
        """
        project_info = {
            'detected': False,
            'type': None,
            'files': [],
            'structure': {}
        }
        
        current_path = Path(current_dir)
        
        # Check for common project indicators
        project_indicators = {
            'python': ['setup.py', 'pyproject.toml', 'requirements.txt', 'environment.yml', 'Pipfile'],
            'javascript': ['package.json', 'yarn.lock', 'package-lock.json', '.nvmrc'],
            'java': ['pom.xml', 'build.gradle', 'gradlew', 'build.xml'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'go': ['go.mod', 'go.sum'],
            'ruby': ['Gemfile', 'Rakefile', '.ruby-version'],
            'php': ['composer.json', 'composer.lock'],
            'csharp': ['*.csproj', '*.sln', 'packages.config'],
            'cpp': ['CMakeLists.txt', 'Makefile', 'configure.ac'],
            'generic': ['.git', '.gitignore', 'README.md', 'README.txt', 'LICENSE']
        }
        
        detected_types = []
        found_files = []
        
        for project_type, indicators in project_indicators.items():
            for indicator in indicators:
                if '*' in indicator:
                    # Handle glob patterns
                    matches = list(current_path.glob(indicator))
                    if matches:
                        detected_types.append(project_type)
                        found_files.extend([f.name for f in matches])
                        break
                else:
                    # Handle exact file names
                    if (current_path / indicator).exists():
                        detected_types.append(project_type)
                        found_files.append(indicator)
                        break
        
        if detected_types:
            project_info['detected'] = True
            project_info['type'] = detected_types[0] if detected_types else 'generic'
            project_info['files'] = found_files
            project_info['structure'] = self._analyze_project_structure(current_path)
        
        return project_info
    
    def _analyze_project_structure(self, project_path: Path) -> Dict:
        """Analyze the structure of a detected project."""
        structure = {
            'directories': [],
            'code_files': [],
            'config_files': [],
            'documentation': [],
            'tests': []
        }
        
        try:
            for item in project_path.iterdir():
                if item.is_dir():
                    structure['directories'].append(item.name)
                elif item.is_file():
                    name = item.name
                    suffix = item.suffix.lower()
                    
                    # Categorize files
                    if suffix in ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php']:
                        if 'test' in name.lower():
                            structure['tests'].append(name)
                        else:
                            structure['code_files'].append(name)
                    elif suffix in ['.json', '.toml', '.yaml', '.yml', '.xml', '.ini', '.cfg']:
                        structure['config_files'].append(name)
                    elif suffix in ['.md', '.txt', '.rst'] or name.upper() in ['README', 'LICENSE', 'CHANGELOG']:
                        structure['documentation'].append(name)
        
        except (PermissionError, OSError):
            pass  # Skip directories we can't read
        
        return structure
    
    def get_project_location(self, project_name: str, auto: bool = False, 
                           confirmation_level: str = 'normal') -> str:
        """
        Determine where to create or find the project.
        
        Args:
            project_name: Name of the project
            auto: Whether to use automatic mode
            confirmation_level: Level of confirmation required
            
        Returns:
            Path where project should be located
        """
        current_dir = os.getcwd()
        
        # Check if we're already in a project
        existing_project = self.detect_existing_project(current_dir)
        
        if existing_project['detected']:
            return current_dir
        
        # Check for existing project directory
        project_dir = os.path.join(current_dir, project_name)
        if os.path.exists(project_dir):
            return project_dir
        
        # Default to creating in current directory
        if auto or confirmation_level == 'minimal':
            return project_dir
        
        # In normal/detailed mode, we'd prompt user here
        # For now, return the default location
        return project_dir
    
    def validate_project_setup(self, project_path: str) -> Tuple[bool, str]:
        """
        Validate that a project is properly set up.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not os.path.exists(project_path):
            return False, f"Project path does not exist: {project_path}"
        
        if not os.path.isdir(project_path):
            return False, f"Project path is not a directory: {project_path}"
        
        # Check if directory is empty
        if not any(Path(project_path).iterdir()):
            return True, "Empty directory - ready for new project"
        
        # Check if it's a recognized project type
        project_info = self.detect_existing_project(project_path)
        if project_info['detected']:
            return True, f"Detected {project_info['type']} project"
        
        # Has files but not recognized as project
        return True, "Directory contains files - will work with existing content"