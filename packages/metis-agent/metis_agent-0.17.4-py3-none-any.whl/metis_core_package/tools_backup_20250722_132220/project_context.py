"""
Project Context Tool for understanding project structure and type.

Analyzes directories to understand:
- Project type (Python, JavaScript, etc.)
- Framework detection
- Key configuration files
- Project structure and organization
- Dependencies and build systems
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
try:
    import toml
except ImportError:
    toml = None

try:
    import yaml
except ImportError:
    yaml = None

from .base import BaseTool


class ProjectContextTool(BaseTool):
    """Tool for analyzing and understanding project context."""
    
    def __init__(self):
        # Project type indicators
        self.project_indicators = {
            "python": {
                "files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "poetry.lock"],
                "directories": ["__pycache__", ".venv", "venv", "env"],
                "extensions": [".py"]
            },
            "javascript": {
                "files": ["package.json", "yarn.lock", "package-lock.json"],
                "directories": ["node_modules", "dist", "build"],
                "extensions": [".js", ".jsx"]
            },
            "typescript": {
                "files": ["tsconfig.json", "package.json"],
                "directories": ["node_modules", "dist", "build"],
                "extensions": [".ts", ".tsx"]
            },
            "react": {
                "files": ["package.json"],
                "directories": ["public", "src", "build"],
                "keywords": ["react", "react-dom", "react-scripts"]
            },
            "next": {
                "files": ["next.config.js", "package.json"],
                "directories": ["pages", "public", ".next"],
                "keywords": ["next"]
            },
            "vue": {
                "files": ["vue.config.js", "package.json"],
                "directories": ["src", "dist"],
                "keywords": ["vue"]
            },
            "go": {
                "files": ["go.mod", "go.sum"],
                "extensions": [".go"]
            },
            "rust": {
                "files": ["Cargo.toml", "Cargo.lock"],
                "directories": ["src", "target"],
                "extensions": [".rs"]
            },
            "java": {
                "files": ["pom.xml", "build.gradle", "gradle.properties"],
                "directories": ["src", "target", "build"],
                "extensions": [".java"]
            },
            "csharp": {
                "files": [".csproj", ".sln"],
                "directories": ["bin", "obj"],
                "extensions": [".cs"]
            },
            "flutter": {
                "files": ["pubspec.yaml"],
                "directories": ["lib", "android", "ios"],
                "extensions": [".dart"]
            }
        }
    
    def can_handle(self, task: str) -> bool:
        """Check if this tool can handle the given task.
        
        This tool handles PROJECT ANALYSIS/CONTEXT tasks, NOT project creation.
        
        Args:
            task: The task description
            
        Returns:
            True if task is related to project analysis
        """
        task_lower = task.lower()
        
        # EXCLUDE project creation/generation tasks
        creation_indicators = [
            'create project', 'generate project', 'build project', 'new project',
            'create a project', 'make a project', 'setup project',
            'initialize project', 'scaffold project', 'project from scratch',
            'create a complete project', 'create complete project', 
            'complete project based on', 'project based on',
            'need you to create', 'create all necessary files',
            'create directories', 'project structure and files'
        ]
        
        if any(indicator in task_lower for indicator in creation_indicators):
            print(f"[ProjectContextTool] REJECTING creation task: found indicator in '{task[:60]}...'")
            return False
        
        # Only handle analysis/context tasks
        analysis_keywords = [
            'analyze project', 'project analysis', 'project structure',
            'project context', 'project overview', 'project summary',
            'understand project', 'explain project', 'describe project',
            'project dependencies', 'tech stack', 'framework detection',
            'repository analysis', 'codebase analysis'
        ]
        
        result = any(keyword in task_lower for keyword in analysis_keywords)
        if result:
            print(f"[ProjectContextTool] ACCEPTING analysis task: '{task[:60]}...'")
        else:
            print(f"[ProjectContextTool] REJECTING task: no analysis keywords in '{task[:60]}...'")
        return result
    
    def execute(self, task: str) -> Any:
        """Execute project analysis based on the task.
        
        Args:
            task: The task description
            
        Returns:
            Result of the project analysis
        """
        task_lower = task.lower()
        
        if 'summary' in task_lower or 'overview' in task_lower:
            return self.get_project_summary(".")
        elif 'analyze' in task_lower or 'structure' in task_lower:
            return self.analyze_directory(".")
        else:
            # Default to project summary
            return self.get_project_summary(".")
    
    def analyze_directory(self, directory: str = ".") -> Dict[str, Any]:
        """
        Analyze a directory to understand project structure and context.
        
        Args:
            directory: Directory to analyze (default: current directory)
            
        Returns:
            Dictionary with project analysis
        """
        try:
            dir_path = Path(directory).resolve()
            if not dir_path.exists() or not dir_path.is_dir():
                return {"error": f"Directory '{directory}' does not exist or is not a directory"}
            
            analysis = {
                "success": True,
                "directory": str(dir_path),
                "project_name": dir_path.name,
                "project_types": [],
                "frameworks": [],
                "config_files": [],
                "key_directories": [],
                "dependencies": {},
                "structure": {},
                "recommendations": []
            }
            
            # Get all files and directories in the project
            all_files = []
            all_dirs = []
            
            for item in dir_path.rglob("*"):
                if item.is_file():
                    all_files.append(item.relative_to(dir_path))
                elif item.is_dir():
                    all_dirs.append(item.relative_to(dir_path))
            
            # Detect project types
            detected_types = self._detect_project_types(dir_path, all_files, all_dirs)
            analysis["project_types"] = detected_types
            
            # Analyze configuration files
            config_files = self._analyze_config_files(dir_path)
            analysis["config_files"] = config_files
            
            # Extract dependencies
            dependencies = self._extract_dependencies(dir_path, detected_types)
            analysis["dependencies"] = dependencies
            
            # Analyze project structure
            structure = self._analyze_structure(dir_path, all_files, all_dirs, detected_types)
            analysis["structure"] = structure
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis)
            analysis["recommendations"] = recommendations
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze directory: {str(e)}"}
    
    def _detect_project_types(self, dir_path: Path, files: List[Path], dirs: List[Path]) -> List[str]:
        """Detect project types based on files and directories."""
        detected_types = []
        file_names = [f.name for f in files]
        dir_names = [d.name for d in dirs]
        file_extensions = set(f.suffix for f in files if f.suffix)
        
        for project_type, indicators in self.project_indicators.items():
            score = 0
            
            # Check for indicator files
            if "files" in indicators:
                for indicator_file in indicators["files"]:
                    if indicator_file in file_names:
                        score += 2
            
            # Check for indicator directories
            if "directories" in indicators:
                for indicator_dir in indicators["directories"]:
                    if indicator_dir in dir_names:
                        score += 1
            
            # Check for file extensions
            if "extensions" in indicators:
                for ext in indicators["extensions"]:
                    if ext in file_extensions:
                        score += 1
            
            # Check for keywords in package.json or other config files
            if "keywords" in indicators and "package.json" in file_names:
                package_json_path = dir_path / "package.json"
                try:
                    with open(package_json_path, 'r') as f:
                        package_data = json.load(f)
                        dependencies = {**package_data.get("dependencies", {}), 
                                      **package_data.get("devDependencies", {})}
                        
                        for keyword in indicators["keywords"]:
                            if any(keyword in dep for dep in dependencies.keys()):
                                score += 2
                except:
                    pass
            
            if score > 0:
                detected_types.append({"type": project_type, "confidence": min(score * 10, 100)})
        
        # Sort by confidence
        detected_types.sort(key=lambda x: x["confidence"], reverse=True)
        return detected_types
    
    def _analyze_config_files(self, dir_path: Path) -> List[Dict[str, Any]]:
        """Analyze configuration files in the project."""
        config_files = []
        
        common_config_files = [
            "package.json", "requirements.txt", "setup.py", "pyproject.toml",
            "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "tsconfig.json",
            ".gitignore", "README.md", "LICENSE", "Dockerfile", ".env",
            "config.yaml", "config.json", "settings.ini"
        ]
        
        for config_file in common_config_files:
            file_path = dir_path / config_file
            if file_path.exists():
                try:
                    stat_info = file_path.stat()
                    config_info = {
                        "name": config_file,
                        "size": stat_info.st_size,
                        "type": self._get_file_type(config_file)
                    }
                    
                    # Try to parse content for key files
                    if config_file == "package.json":
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            config_info["content"] = {
                                "name": data.get("name"),
                                "version": data.get("version"),
                                "description": data.get("description"),
                                "scripts": list(data.get("scripts", {}).keys()),
                                "dependency_count": len(data.get("dependencies", {})),
                                "dev_dependency_count": len(data.get("devDependencies", {}))
                            }
                    elif config_file == "requirements.txt":
                        with open(file_path, 'r') as f:
                            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
                            config_info["content"] = {
                                "dependency_count": len(lines)
                            }
                    
                    config_files.append(config_info)
                    
                except Exception:
                    config_files.append({
                        "name": config_file,
                        "error": "Could not parse file"
                    })
        
        return config_files
    
    def _extract_dependencies(self, dir_path: Path, project_types: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract project dependencies."""
        dependencies = {}
        
        # JavaScript/Node.js dependencies
        package_json = dir_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    dependencies["javascript"] = {
                        "production": data.get("dependencies", {}),
                        "development": data.get("devDependencies", {})
                    }
            except:
                pass
        
        # Python dependencies
        requirements_txt = dir_path / "requirements.txt"
        if requirements_txt.exists():
            try:
                with open(requirements_txt, 'r') as f:
                    lines = [line.strip() for line in f.readlines() 
                           if line.strip() and not line.startswith("#")]
                    dependencies["python"] = {"requirements": lines}
            except:
                pass
        
        # Go dependencies
        go_mod = dir_path / "go.mod"
        if go_mod.exists():
            try:
                with open(go_mod, 'r') as f:
                    content = f.read()
                    dependencies["go"] = {"go_mod": content}
            except:
                pass
        
        return dependencies
    
    def _analyze_structure(self, dir_path: Path, files: List[Path], dirs: List[Path], 
                          project_types: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze the project structure."""
        structure = {
            "total_files": len(files),
            "total_directories": len(dirs),
            "file_types": {},
            "directory_structure": {},
            "large_files": [],
            "deep_paths": []
        }
        
        # Analyze file types
        for file_path in files:
            ext = file_path.suffix.lower() if file_path.suffix else "no_extension"
            if ext not in structure["file_types"]:
                structure["file_types"][ext] = 0
            structure["file_types"][ext] += 1
        
        # Find large files (>1MB)
        for file_path in files:
            try:
                full_path = dir_path / file_path
                size = full_path.stat().st_size
                if size > 1024 * 1024:  # 1MB
                    structure["large_files"].append({
                        "path": str(file_path),
                        "size": size
                    })
            except:
                pass
        
        # Find deep paths (>5 levels)
        for path in files + dirs:
            if len(path.parts) > 5:
                structure["deep_paths"].append(str(path))
        
        # Analyze directory structure patterns
        common_dirs = ["src", "lib", "tests", "docs", "examples", "scripts", "config"]
        structure["directory_structure"] = {
            dir_name: dir_name in [d.name for d in dirs] 
            for dir_name in common_dirs
        }
        
        return structure
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Check for missing important files
        config_file_names = [cf["name"] for cf in analysis["config_files"]]
        
        if ".gitignore" not in config_file_names:
            recommendations.append("Consider adding a .gitignore file to exclude unnecessary files from version control")
        
        if "README.md" not in config_file_names:
            recommendations.append("Consider adding a README.md file to document your project")
        
        # Project-specific recommendations
        project_types = [pt["type"] for pt in analysis["project_types"]]
        
        if "python" in project_types:
            if "requirements.txt" not in config_file_names and "pyproject.toml" not in config_file_names:
                recommendations.append("Consider adding requirements.txt or pyproject.toml to manage Python dependencies")
            
            if not analysis["structure"]["directory_structure"].get("tests"):
                recommendations.append("Consider adding a tests directory for unit tests")
        
        if "javascript" in project_types or "typescript" in project_types:
            package_json = next((cf for cf in analysis["config_files"] if cf["name"] == "package.json"), None)
            if package_json and "scripts" in package_json.get("content", {}):
                if not package_json["content"]["scripts"]:
                    recommendations.append("Consider adding npm scripts for common tasks (build, test, start)")
        
        # Structure recommendations
        if analysis["structure"]["total_files"] > 100 and not analysis["structure"]["directory_structure"].get("src"):
            recommendations.append("For large projects, consider organizing code in a 'src' directory")
        
        if len(analysis["structure"]["large_files"]) > 0:
            recommendations.append(f"Found {len(analysis['structure']['large_files'])} large files. Consider using Git LFS for large assets")
        
        return recommendations
    
    def _get_file_type(self, filename: str) -> str:
        """Determine the type of a configuration file."""
        type_map = {
            "package.json": "Node.js package configuration",
            "requirements.txt": "Python requirements",
            "setup.py": "Python package setup",
            "pyproject.toml": "Python project configuration",
            "Cargo.toml": "Rust package configuration",
            "go.mod": "Go module definition",
            "pom.xml": "Maven project configuration",
            "build.gradle": "Gradle build script",
            "tsconfig.json": "TypeScript configuration",
            ".gitignore": "Git ignore rules",
            "README.md": "Project documentation",
            "LICENSE": "Project license",
            "Dockerfile": "Docker container configuration",
            ".env": "Environment variables"
        }
        return type_map.get(filename, "Configuration file")
    
    def get_project_summary(self, directory: str = ".") -> Dict[str, Any]:
        """Get a concise project summary."""
        analysis = self.analyze_directory(directory)
        
        if "error" in analysis:
            return analysis
        
        # Create a concise summary
        summary = {
            "project_name": analysis["project_name"],
            "primary_language": None,
            "framework": None,
            "file_count": analysis["structure"]["total_files"],
            "key_features": []
        }
        
        # Determine primary language
        if analysis["project_types"]:
            summary["primary_language"] = analysis["project_types"][0]["type"]
        
        # Determine framework
        frameworks = ["react", "vue", "next", "flutter"]
        for project_type in analysis["project_types"]:
            if project_type["type"] in frameworks:
                summary["framework"] = project_type["type"]
                break
        
        # Key features
        if analysis["dependencies"]:
            summary["key_features"].append("Has dependencies managed")
        if any(cf["name"] == ".gitignore" for cf in analysis["config_files"]):
            summary["key_features"].append("Version controlled")
        if any(cf["name"] == "README.md" for cf in analysis["config_files"]):
            summary["key_features"].append("Documented")
        if analysis["structure"]["directory_structure"].get("tests"):
            summary["key_features"].append("Has tests")
        
        return {"success": True, "summary": summary}
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a project context operation.
        
        Args:
            action: The action to perform (analyze, summary)
            **kwargs: Action-specific parameters
            
        Returns:
            Dictionary with operation result
        """
        action_map = {
            "analyze": self.analyze_directory,
            "summary": self.get_project_summary
        }
        
        if action not in action_map:
            return {
                "error": f"Unknown action '{action}'. Available actions: {list(action_map.keys())}"
            }
        
        try:
            return action_map[action](**kwargs)
        except TypeError as e:
            return {"error": f"Invalid parameters for action '{action}': {str(e)}"}
