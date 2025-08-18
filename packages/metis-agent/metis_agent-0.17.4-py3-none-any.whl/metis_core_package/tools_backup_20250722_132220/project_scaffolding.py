"""
Project Scaffolding Tool for Metis Agent CLI.

This tool provides project template creation, development environment setup,
boilerplate code generation, and tooling configuration.
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import BaseTool


class ProjectScaffoldingTool(BaseTool):
    """Tool for project scaffolding and template generation."""
    
    def __init__(self):
        super().__init__()
    
    def can_handle(self, task: str) -> bool:
        """Check if this tool can handle the given task."""
        scaffolding_keywords = [
            "create", "init", "scaffold", "template", "boilerplate", "setup",
            "new project", "initialize", "generate", "structure", "framework",
            "starter", "skeleton", "blueprint", "config", "configure"
        ]
        return any(keyword in task.lower() for keyword in scaffolding_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute project scaffolding operations."""
        try:
            cwd = kwargs.get("cwd", os.getcwd())
            project_name = kwargs.get("project_name", "new-project")
            
            task_lower = task.lower()
            
            if "python" in task_lower:
                return self._create_python_project(cwd, project_name, task)
            elif "node" in task_lower or "javascript" in task_lower:
                return self._create_node_project(cwd, project_name, task)
            elif "fastapi" in task_lower:
                return self._create_fastapi_project(cwd, project_name, task)
            elif any(word in task_lower for word in ["init", "setup", "configure"]):
                return self._setup_existing_project(cwd, task)
            else:
                return self._suggest_project_types(task)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Project scaffolding failed: {str(e)}"
            }
    
    def _create_python_project(self, cwd: str, project_name: str, task: str) -> Dict[str, Any]:
        """Create a Python project template."""
        project_path = os.path.join(cwd, project_name)
        
        if os.path.exists(project_path):
            return {"success": False, "error": f"Directory '{project_name}' already exists"}
        
        try:
            # Create project structure
            os.makedirs(project_path)
            package_name = project_name.replace("-", "_")
            os.makedirs(os.path.join(project_path, package_name))
            os.makedirs(os.path.join(project_path, "tests"))
            
            # Create files
            files = {
                f"{package_name}/__init__.py": f'"""${project_name} package."""\n\n__version__ = "0.1.0"\n',
                f"{package_name}/main.py": self._get_python_main_template(package_name),
                "requirements.txt": "# Add your dependencies here\n",
                "requirements-dev.txt": "pytest\nblack\nflake8\nmypy\n",
                f"tests/test_{package_name}.py": self._get_python_test_template(package_name),
                "README.md": self._get_readme_template(project_name),
                ".gitignore": self._get_python_gitignore(),
            }
            
            for filepath, content in files.items():
                full_path = os.path.join(project_path, filepath)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
            
            return {
                "success": True,
                "project_name": project_name,
                "project_path": project_path,
                "project_type": "Python Package",
                "files_created": list(files.keys()),
                "next_steps": [
                    f"cd {project_name}",
                    "python -m venv venv",
                    "source venv/bin/activate",
                    "pip install -r requirements-dev.txt",
                    "pytest"
                ]
            }
            
        except Exception as e:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            raise e
    
    def _create_node_project(self, cwd: str, project_name: str, task: str) -> Dict[str, Any]:
        """Create a Node.js project template."""
        project_path = os.path.join(cwd, project_name)
        
        if os.path.exists(project_path):
            return {"success": False, "error": f"Directory '{project_name}' already exists"}
        
        try:
            # Create project structure
            os.makedirs(project_path)
            os.makedirs(os.path.join(project_path, "src"))
            
            # Create package.json
            package_data = {
                "name": project_name,
                "version": "1.0.0",
                "description": f"A Node.js project: {project_name}",
                "main": "src/index.js",
                "scripts": {
                    "start": "node src/index.js",
                    "dev": "node --watch src/index.js",
                    "test": "jest"
                },
                "devDependencies": {"jest": "^29.0.0"},
                "license": "MIT"
            }
            
            files = {
                "package.json": json.dumps(package_data, indent=2),
                "src/index.js": self._get_node_main_template(),
                "README.md": self._get_readme_template(project_name, "Node.js"),
                ".gitignore": self._get_node_gitignore()
            }
            
            for filepath, content in files.items():
                full_path = os.path.join(project_path, filepath)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
            
            return {
                "success": True,
                "project_name": project_name,
                "project_path": project_path,
                "project_type": "Node.js Application",
                "files_created": list(files.keys()),
                "next_steps": [f"cd {project_name}", "npm install", "npm run dev"]
            }
            
        except Exception as e:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            raise e
    
    def _create_fastapi_project(self, cwd: str, project_name: str, task: str) -> Dict[str, Any]:
        """Create a FastAPI project template."""
        result = self._create_python_project(cwd, project_name, task)
        if not result.get("success"):
            return result
        
        project_path = result["project_path"]
        package_name = project_name.replace("-", "_")
        
        # Update for FastAPI
        with open(os.path.join(project_path, "requirements.txt"), 'w') as f:
            f.write("fastapi\nuvicorn[standard]\n")
        
        with open(os.path.join(project_path, package_name, "main.py"), 'w') as f:
            f.write(self._get_fastapi_template())
        
        result["project_type"] = "FastAPI Application"
        result["next_steps"] = [
            f"cd {project_name}",
            "pip install -r requirements.txt",
            f"uvicorn {package_name}.main:app --reload",
            "# Visit http://localhost:8000/docs"
        ]
        
        return result
    
    def _setup_existing_project(self, cwd: str, task: str) -> Dict[str, Any]:
        """Setup tooling for an existing project."""
        project_type = "python" if any(os.path.exists(os.path.join(cwd, f)) 
                                        for f in ["setup.py", "requirements.txt"]) else "unknown"
        
        if project_type == "unknown":
            return {
                "success": False,
                "error": "Could not detect project type",
                "suggestion": "Create a new project with 'metis project init <type>'"
            }
        
        files_created = []
        if not os.path.exists(os.path.join(cwd, "requirements-dev.txt")):
            with open(os.path.join(cwd, "requirements-dev.txt"), 'w') as f:
                f.write("pytest\nblack\nflake8\n")
            files_created.append("requirements-dev.txt")
        
        return {
            "success": True,
            "project_type": project_type,
            "files_created": files_created,
            "suggestions": ["pip install -r requirements-dev.txt"],
            "message": f"Enhanced {project_type} project with development tools"
        }
    
    def _suggest_project_types(self, task: str) -> Dict[str, Any]:
        """Suggest available project types."""
        return {
            "success": True,
            "available_types": [
                "python - Python package/application",
                "fastapi - FastAPI web API",
                "node - Node.js application"
            ],
            "examples": [
                "metis project init python my-package",
                "metis project init fastapi my-api",
                "metis project init node my-app"
            ],
            "message": "Specify a project type to create a new project"
        }
    
    # Template methods
    def _get_python_main_template(self, package_name: str) -> str:
        return f'''"""Main module for {package_name}."""


def main():
    """Main entry point."""
    print("Hello from {package_name}!")
    return "Hello World"


if __name__ == "__main__":
    main()
'''
    
    def _get_python_test_template(self, package_name: str) -> str:
        return f'''"""Tests for {package_name}."""

import pytest
from {package_name}.main import main


def test_main():
    """Test main function."""
    result = main()
    assert result == "Hello World"
'''
    
    def _get_readme_template(self, project_name: str, project_type: str = "Python") -> str:
        return f'''# {project_name}

A {project_type} project.

## Installation

```bash
pip install {project_name}
```

## Usage

Basic usage example here.

## Development

```bash
git clone https://github.com/yourusername/{project_name}.git
cd {project_name}
pip install -r requirements-dev.txt
pytest
```

## License

MIT License
'''
    
    def _get_python_gitignore(self) -> str:
        return '''__pycache__/
*.py[cod]
*$py.class
*.so
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
.venv/
venv/
ENV/
env/
.pytest_cache/
.coverage
htmlcov/
.DS_Store
'''
    
    def _get_node_main_template(self) -> str:
        return '''/**
 * Main application entry point
 */

function main() {
    console.log("Hello from Node.js!");
    return "Hello World";
}

if (require.main === module) {
    main();
}

module.exports = { main };
'''
    
    def _get_node_gitignore(self) -> str:
        return '''node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env
.env.local
logs
*.log
coverage/
.nyc_output
dist/
build/
.DS_Store
'''
    
    def _get_fastapi_template(self) -> str:
        return '''"""FastAPI application."""

from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello from FastAPI!", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint.""" 
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
