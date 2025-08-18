"""
Project Analysis Tool for Metis Agent.

This tool provides intelligent project analysis capabilities including:
- Automatic code file analysis
- Project structure understanding
- Code summary generation
- Project type detection with detailed insights
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from ..base import BaseTool


class ProjectAnalyzerTool(BaseTool):
    """
    Tool for comprehensive project analysis and understanding.
    
    Provides intelligent analysis of codebases including:
    - Code file analysis and summarization
    - Project structure mapping
    - Dependency analysis
    - Technology stack detection
    """
    
    def __init__(self):
        self.name = "ProjectAnalyzerTool"
        self.description = "Analyzes projects to provide intelligent context and summaries of codebases"
        self.version = "1.0.0"
        self.category = "core_tools"
    
    def can_handle(self, task: str) -> bool:
        """Check if this tool can handle project analysis tasks."""
        task_lower = task.lower()
        
        analysis_keywords = [
            'analyze project', 'tell me about project', 'project summary',
            'what is this project', 'analyze code', 'understand project',
            'project overview', 'code analysis', 'project description',
            'analyze codebase', 'explain project', 'project details'
        ]
        
        return any(keyword in task_lower for keyword in analysis_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute project analysis operations."""
        try:
            project_path = kwargs.get('project_path', os.getcwd())
            
            # Perform comprehensive project analysis
            analysis_results = self._analyze_project(project_path)
            
            return {
                'success': True,
                'type': 'project_analysis',
                'data': analysis_results,
                'summary': self._generate_project_summary(analysis_results),
                'message': f"Analyzed project at {project_path}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'type': 'project_analysis_error',
                'error': str(e),
                'message': f"Failed to analyze project: {str(e)}"
            }
    
    def _analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Perform comprehensive project analysis."""
        analysis = {
            'project_path': project_path,
            'project_name': os.path.basename(project_path),
            'project_type': None,
            'technologies': [],
            'code_files': {},
            'structure': {},
            'dependencies': [],
            'readme_content': None,
            'total_lines': 0,
            'file_counts': {},
            'main_files': []
        }
        
        # Get all files in project
        all_files = self._get_project_files(project_path)
        
        # Categorize files by type
        analysis['file_counts'] = self._categorize_files(all_files)
        
        # Detect project type and technologies
        analysis['project_type'], analysis['technologies'] = self._detect_technologies(all_files)
        
        # Analyze code files
        code_files = self._filter_code_files(all_files)
        for file_path in code_files[:10]:  # Limit to prevent overwhelming analysis
            file_analysis = self._analyze_code_file(file_path)
            if file_analysis:
                relative_path = os.path.relpath(file_path, project_path)
                analysis['code_files'][relative_path] = file_analysis
                analysis['total_lines'] += file_analysis.get('lines', 0)
        
        # Find and read README
        analysis['readme_content'] = self._find_and_read_readme(project_path)
        
        # Identify main/entry files
        analysis['main_files'] = self._identify_main_files(code_files, project_path)
        
        # Analyze project structure
        analysis['structure'] = self._analyze_structure(project_path)
        
        # Analyze dependencies
        analysis['dependencies'] = self._analyze_dependencies(project_path)
        
        return analysis
    
    def _get_project_files(self, project_path: str) -> List[str]:
        """Get all files in the project directory."""
        files = []
        try:
            for root, dirs, filenames in os.walk(project_path):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env', 'dist', 'build']]
                
                for filename in filenames:
                    if not filename.startswith('.'):
                        files.append(os.path.join(root, filename))
        except (OSError, PermissionError):
            pass
        
        return files
    
    def _categorize_files(self, files: List[str]) -> Dict[str, int]:
        """Categorize files by extension."""
        categories = {}
        for file_path in files:
            ext = Path(file_path).suffix.lower()
            if ext:
                categories[ext] = categories.get(ext, 0) + 1
        return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))
    
    def _detect_technologies(self, files: List[str]) -> Tuple[str, List[str]]:
        """Detect project type and technologies based on files."""
        technologies = set()
        project_type = "unknown"
        
        # Check for specific files that indicate technology
        file_basenames = [os.path.basename(f).lower() for f in files]
        file_extensions = [Path(f).suffix.lower() for f in files]
        
        # Python project detection
        if any(name in file_basenames for name in ['requirements.txt', 'setup.py', 'pyproject.toml']) or '.py' in file_extensions:
            project_type = "python"
            technologies.add("Python")
            
            # Check for specific Python frameworks
            if 'app.py' in file_basenames or 'main.py' in file_basenames:
                technologies.add("Python Application")
            if any('flask' in str(f).lower() for f in files):
                technologies.add("Flask")
            if any('django' in str(f).lower() for f in files):
                technologies.add("Django")
            if any('fastapi' in str(f).lower() for f in files):
                technologies.add("FastAPI")
        
        # JavaScript/Node.js
        if 'package.json' in file_basenames or '.js' in file_extensions:
            project_type = "javascript" if project_type == "unknown" else project_type
            technologies.add("JavaScript")
            
            if '.ts' in file_extensions or '.tsx' in file_extensions:
                technologies.add("TypeScript")
            if '.jsx' in file_extensions or '.tsx' in file_extensions:
                technologies.add("React")
            if 'next.config' in ' '.join(file_basenames):
                technologies.add("Next.js")
        
        # Game development
        if any('pygame' in self._read_file_safely(f) for f in files if f.endswith('.py')):
            technologies.add("Pygame")
            project_type = "game"
        
        # Data science/visualization
        if any(lib in ' '.join([self._read_file_safely(f) for f in files if f.endswith('.py')]) 
               for lib in ['matplotlib', 'numpy', 'pandas', 'seaborn']):
            technologies.add("Data Science")
            if 'matplotlib' in ' '.join([self._read_file_safely(f) for f in files if f.endswith('.py')]):
                technologies.add("Matplotlib")
        
        return project_type, list(technologies)
    
    def _filter_code_files(self, files: List[str]) -> List[str]:
        """Filter to only code files."""
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.cs'}
        return [f for f in files if Path(f).suffix.lower() in code_extensions]
    
    def _analyze_code_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single code file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            analysis = {
                'lines': len(content.splitlines()),
                'size': len(content),
                'functions': [],
                'classes': [],
                'imports': [],
                'description': None
            }
            
            # Python-specific analysis
            if file_path.endswith('.py'):
                analysis.update(self._analyze_python_file(content))
            
            # JavaScript-specific analysis
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                analysis.update(self._analyze_javascript_file(content))
            
            # Generate description
            analysis['description'] = self._generate_file_description(file_path, content, analysis)
            
            return analysis
        
        except Exception:
            return None
    
    def _analyze_python_file(self, content: str) -> Dict[str, Any]:
        """Analyze Python file specifically."""
        analysis = {'functions': [], 'classes': [], 'imports': []}
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports'].append(node.module)
        
        except SyntaxError:
            # If parsing fails, try to extract with regex
            analysis['functions'] = re.findall(r'def\s+(\w+)', content)
            analysis['classes'] = re.findall(r'class\s+(\w+)', content)
            analysis['imports'] = re.findall(r'import\s+(\w+)', content)
        
        return analysis
    
    def _analyze_javascript_file(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file."""
        analysis = {'functions': [], 'classes': [], 'imports': []}
        
        # Extract functions
        analysis['functions'] = re.findall(r'function\s+(\w+)', content)
        analysis['functions'].extend(re.findall(r'const\s+(\w+)\s*=\s*\(.*?\)\s*=>', content))
        
        # Extract classes
        analysis['classes'] = re.findall(r'class\s+(\w+)', content)
        
        # Extract imports
        analysis['imports'] = re.findall(r'import.*?from\s+["\']([^"\']+)["\']', content)
        analysis['imports'].extend(re.findall(r'import\s+["\']([^"\']+)["\']', content))
        
        return analysis
    
    def _generate_file_description(self, file_path: str, content: str, analysis: Dict[str, Any]) -> str:
        """Generate a description of what the file does."""
        filename = os.path.basename(file_path)
        
        # Check for docstrings or comments at the top
        lines = content.strip().split('\n')
        description_parts = []
        
        # Look for file-level docstring or comments
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if line.startswith('"""') or line.startswith("'''"):
                # Multi-line docstring
                docstring_lines = [line]
                for j in range(i + 1, min(i + 10, len(lines))):
                    docstring_lines.append(lines[j])
                    if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                        break
                description_parts.append(' '.join(docstring_lines))
                break
            elif line.startswith('#'):
                description_parts.append(line[1:].strip())
        
        # If no description found, infer from filename and content
        if not description_parts:
            if 'game' in filename.lower():
                description_parts.append("Game implementation")
            elif 'api' in filename.lower():
                description_parts.append("API implementation")
            elif 'main' in filename.lower():
                description_parts.append("Main application entry point")
            elif filename.lower() in ['app.py', 'server.py']:
                description_parts.append("Application server")
            elif 'test' in filename.lower():
                description_parts.append("Test file")
            else:
                # Infer from imports and functions
                imports = analysis.get('imports', [])
                if 'pygame' in imports:
                    description_parts.append("Pygame-based application")
                elif 'matplotlib' in imports:
                    description_parts.append("Data visualization script")
                elif 'flask' in imports:
                    description_parts.append("Flask web application")
                elif analysis.get('functions'):
                    description_parts.append(f"Module with {len(analysis['functions'])} functions")
        
        return ' '.join(description_parts) if description_parts else f"Code file: {filename}"
    
    def _find_and_read_readme(self, project_path: str) -> Optional[str]:
        """Find and read README file."""
        readme_files = ['README.md', 'README.txt', 'README', 'readme.md', 'readme.txt']
        
        for readme_name in readme_files:
            readme_path = os.path.join(project_path, readme_name)
            if os.path.exists(readme_path):
                return self._read_file_safely(readme_path)
        
        return None
    
    def _read_file_safely(self, file_path: str) -> str:
        """Safely read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ""
    
    def _identify_main_files(self, code_files: List[str], project_path: str) -> List[str]:
        """Identify main/entry point files."""
        main_files = []
        
        for file_path in code_files:
            filename = os.path.basename(file_path).lower()
            if filename in ['main.py', 'app.py', 'server.py', 'index.js', 'index.ts', 'app.js']:
                main_files.append(os.path.relpath(file_path, project_path))
        
        return main_files
    
    def _analyze_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project directory structure."""
        structure = {'directories': [], 'depth': 0}
        
        try:
            for root, dirs, files in os.walk(project_path):
                level = root.replace(project_path, '').count(os.sep)
                structure['depth'] = max(structure['depth'], level)
                
                if level <= 2:  # Only analyze up to 2 levels deep
                    rel_path = os.path.relpath(root, project_path)
                    if rel_path != '.':
                        structure['directories'].append({
                            'path': rel_path,
                            'level': level,
                            'file_count': len(files)
                        })
        except Exception:
            pass
        
        return structure
    
    def _analyze_dependencies(self, project_path: str) -> List[str]:
        """Analyze project dependencies."""
        dependencies = []
        
        # Check requirements.txt
        req_path = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(req_path):
            content = self._read_file_safely(req_path)
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name before version specifiers
                    package = re.split(r'[>=<!=]', line)[0].strip()
                    if package:
                        dependencies.append(package)
        
        # Check package.json
        pkg_path = os.path.join(project_path, 'package.json')
        if os.path.exists(pkg_path):
            try:
                import json
                with open(pkg_path, 'r') as f:
                    pkg_data = json.load(f)
                dependencies.extend(pkg_data.get('dependencies', {}).keys())
                dependencies.extend(pkg_data.get('devDependencies', {}).keys())
            except Exception:
                pass
        
        return dependencies
    
    def _generate_project_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable project summary."""
        summary_parts = []
        
        # Project overview
        project_name = analysis['project_name']
        project_type = analysis['project_type']
        technologies = analysis['technologies']
        
        summary_parts.append(f"## {project_name}")
        summary_parts.append(f"**Type:** {project_type.title()} Project")
        
        if technologies:
            summary_parts.append(f"**Technologies:** {', '.join(technologies)}")
        
        # File statistics
        total_files = len(analysis['code_files'])
        total_lines = analysis['total_lines']
        summary_parts.append(f"**Code Files:** {total_files} files, {total_lines:,} total lines")
        
        # Main files
        if analysis['main_files']:
            summary_parts.append(f"**Entry Points:** {', '.join(analysis['main_files'])}")
        
        # File breakdown
        file_counts = analysis['file_counts']
        if file_counts:
            top_extensions = list(file_counts.items())[:5]
            ext_summary = ', '.join([f"{ext} ({count})" for ext, count in top_extensions])
            summary_parts.append(f"**File Types:** {ext_summary}")
        
        # Code file descriptions
        if analysis['code_files']:
            summary_parts.append("\n### Code Files:")
            for file_path, file_analysis in list(analysis['code_files'].items())[:5]:
                description = file_analysis.get('description', 'No description')
                lines = file_analysis.get('lines', 0)
                summary_parts.append(f"- **{file_path}** ({lines} lines): {description}")
        
        # Dependencies
        if analysis['dependencies']:
            deps_str = ', '.join(analysis['dependencies'][:10])
            if len(analysis['dependencies']) > 10:
                deps_str += f" (and {len(analysis['dependencies']) - 10} more)"
            summary_parts.append(f"\n**Dependencies:** {deps_str}")
        
        # README content
        if analysis['readme_content']:
            readme_lines = analysis['readme_content'].split('\n')[:5]
            readme_preview = '\n'.join(readme_lines)
            if len(analysis['readme_content'].split('\n')) > 5:
                readme_preview += "\n..."
            summary_parts.append(f"\n**README Preview:**\n```\n{readme_preview}\n```")
        
        return '\n'.join(summary_parts)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capabilities."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["natural_language", "project_path"],
            "output_types": ["structured_analysis", "project_summary", "code_insights"],
            "supported_languages": ["python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"],
            "features": [
                "automatic_project_detection",
                "code_file_analysis", 
                "dependency_analysis",
                "project_structure_mapping",
                "technology_stack_detection",
                "entry_point_identification"
            ]
        }
    
    def get_examples(self) -> List[str]:
        """Return example usage patterns."""
        return [
            "Analyze this project and tell me what it does",
            "Give me an overview of the current codebase", 
            "What technologies are used in this project?",
            "Summarize the main files in this project",
            "Analyze the project structure",
            "Tell me about the dependencies in this project"
        ]