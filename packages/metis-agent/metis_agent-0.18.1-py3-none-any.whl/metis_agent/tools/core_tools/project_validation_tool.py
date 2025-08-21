"""
Project Validation Tool for Metis Agent.

This tool validates project completeness, code quality, and implementation status.
"""
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import BaseTool


class ProjectValidationTool(BaseTool):
    """
    Tool for validating project completeness and quality.
    
    This tool handles:
    - Project structure validation
    - Code syntax and quality checks
    - Implementation completeness verification
    - Test execution and validation
    - Completion percentage calculation
    """
    
    def __init__(self):
        """Initialize the project validation tool."""
        self.name = "ProjectValidationTool"
        self.description = "Validates project completeness, code quality, and implementation status"
        
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle project validation tasks.
        
        Args:
            task: The task description
            
        Returns:
            True if task involves project validation or quality checks
        """
        task_lower = task.lower()
        
        # Validation keywords
        validation_keywords = [
            'validate', 'check', 'verify', 'quality', 'completeness',
            'test', 'syntax', 'structure', 'implementation status',
            'completion percentage', 'project health', 'code quality'
        ]
        
        return any(keyword in task_lower for keyword in validation_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute project validation operations.
        
        Args:
            task: The task description
            **kwargs: Additional parameters including:
                - project_path: Path to the project directory
                - requirements: Project requirements for validation
                - implementation_plan: Expected implementation plan
                - validation_type: Type of validation to perform
                
        Returns:
            Dict containing validation results and reports
        """
        try:
            action = kwargs.get('action', 'validate')
            
            if action == 'validate':
                return self._validate_project(**kwargs)
            elif action == 'check_syntax':
                return self._check_syntax(**kwargs)
            elif action == 'run_tests':
                return self._run_tests(**kwargs)
            elif action == 'calculate_completion':
                return self._calculate_completion(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown validation action: {action}",
                    "supported_actions": [
                        "validate", "check_syntax", "run_tests", "calculate_completion"
                    ]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Project validation failed: {str(e)}",
                "task": task
            }
    
    def _validate_project(self, **kwargs) -> Dict[str, Any]:
        """Perform comprehensive project validation."""
        project_path = Path(kwargs.get('project_path', '.'))
        requirements = kwargs.get('requirements', {})
        implementation_plan = kwargs.get('implementation_plan', {})
        
        if not project_path.exists():
            return {
                "success": False,
                "error": f"Project path does not exist: {project_path}"
            }
        
        validation_report = {
            "project_path": str(project_path),
            "validation_timestamp": self._get_timestamp(),
            "structure_check": self._validate_structure(project_path),
            "file_check": self._validate_files(project_path, implementation_plan),
            "syntax_check": self._check_project_syntax(project_path),
            "requirements_check": self._validate_requirements(project_path, requirements),
            "completion_percentage": 0,
            "overall_status": "unknown",
            "recommendations": []
        }
        
        # Calculate completion percentage
        completion_data = self._calculate_project_completion(validation_report)
        validation_report["completion_percentage"] = completion_data["percentage"]
        validation_report["completion_details"] = completion_data["details"]
        
        # Determine overall status
        if validation_report["completion_percentage"] >= 90:
            validation_report["overall_status"] = "complete"
        elif validation_report["completion_percentage"] >= 70:
            validation_report["overall_status"] = "mostly_complete"
        elif validation_report["completion_percentage"] >= 40:
            validation_report["overall_status"] = "in_progress"
        else:
            validation_report["overall_status"] = "incomplete"
        
        # Generate recommendations
        validation_report["recommendations"] = self._generate_recommendations(validation_report)
        
        return {
            "success": True,
            "operation": "project_validation",
            "validation_report": validation_report
        }
    
    def _validate_structure(self, project_path: Path) -> Dict[str, Any]:
        """Validate project directory structure."""
        structure_check = {
            "valid": True,
            "missing_directories": [],
            "missing_files": [],
            "extra_items": [],
            "score": 0
        }
        
        # Expected directories
        expected_dirs = ['src', 'Metis']
        optional_dirs = ['tests', 'docs', 'config']
        
        # Check required directories
        for dir_name in expected_dirs:
            dir_path = project_path / dir_name
            if not dir_path.exists():
                structure_check["missing_directories"].append(dir_name)
                structure_check["valid"] = False
        
        # Check for common project files
        expected_files = ['README.md', '.gitignore']
        for file_name in expected_files:
            file_path = project_path / file_name
            if not file_path.exists():
                structure_check["missing_files"].append(file_name)
        
        # Calculate structure score
        total_expected = len(expected_dirs) + len(expected_files)
        missing_count = len(structure_check["missing_directories"]) + len(structure_check["missing_files"])
        structure_check["score"] = max(0, (total_expected - missing_count) / total_expected * 100)
        
        return structure_check
    
    def _validate_files(self, project_path: Path, implementation_plan: Dict) -> Dict[str, Any]:
        """Validate expected files exist and have content."""
        file_check = {
            "files_found": [],
            "files_missing": [],
            "empty_files": [],
            "file_sizes": {},
            "score": 0
        }
        
        # Get expected files from implementation plan
        expected_files = implementation_plan.get('expected_files', [])
        if not expected_files:
            # Default expected files
            expected_files = [
                'src/main.py',
                'src/app.py',
                'requirements.txt',
                'README.md'
            ]
        
        for file_path in expected_files:
            full_path = project_path / file_path
            if full_path.exists():
                file_check["files_found"].append(file_path)
                file_size = full_path.stat().st_size
                file_check["file_sizes"][file_path] = file_size
                
                if file_size == 0:
                    file_check["empty_files"].append(file_path)
            else:
                file_check["files_missing"].append(file_path)
        
        # Calculate file score
        if expected_files:
            found_count = len(file_check["files_found"])
            file_check["score"] = (found_count / len(expected_files)) * 100
        
        return file_check
    
    def _check_project_syntax(self, project_path: Path) -> Dict[str, Any]:
        """Check syntax of Python files in the project."""
        syntax_check = {
            "valid": True,
            "files_checked": [],
            "syntax_errors": [],
            "warnings": [],
            "score": 100
        }
        
        # Find all Python files
        python_files = list(project_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try to compile the code
                compile(content, str(py_file), 'exec')
                syntax_check["files_checked"].append(str(py_file.relative_to(project_path)))
                
            except SyntaxError as e:
                syntax_check["valid"] = False
                syntax_check["syntax_errors"].append({
                    "file": str(py_file.relative_to(project_path)),
                    "line": e.lineno,
                    "error": str(e)
                })
            except Exception as e:
                syntax_check["warnings"].append({
                    "file": str(py_file.relative_to(project_path)),
                    "warning": f"Could not check syntax: {str(e)}"
                })
        
        # Calculate syntax score
        if python_files:
            error_count = len(syntax_check["syntax_errors"])
            total_files = len(python_files)
            syntax_check["score"] = max(0, (total_files - error_count) / total_files * 100)
        
        return syntax_check
    
    def _validate_requirements(self, project_path: Path, requirements: Dict) -> Dict[str, Any]:
        """Validate project meets specified requirements."""
        req_check = {
            "requirements_met": [],
            "requirements_missing": [],
            "partial_requirements": [],
            "score": 0
        }
        
        if not requirements:
            req_check["score"] = 100  # No requirements to check
            return req_check
        
        # Check technical requirements
        tech_requirements = requirements.get('technical_specs', {})
        for req_name, req_value in tech_requirements.items():
            if self._check_requirement_met(project_path, req_name, req_value):
                req_check["requirements_met"].append(req_name)
            else:
                req_check["requirements_missing"].append(req_name)
        
        # Check feature requirements
        feature_requirements = requirements.get('features', [])
        for feature in feature_requirements:
            if self._check_feature_implemented(project_path, feature):
                req_check["requirements_met"].append(f"feature_{feature}")
            else:
                req_check["requirements_missing"].append(f"feature_{feature}")
        
        # Calculate requirements score
        total_reqs = len(req_check["requirements_met"]) + len(req_check["requirements_missing"])
        if total_reqs > 0:
            req_check["score"] = (len(req_check["requirements_met"]) / total_reqs) * 100
        else:
            req_check["score"] = 100
        
        return req_check
    
    def _check_requirement_met(self, project_path: Path, req_name: str, req_value: Any) -> bool:
        """Check if a specific requirement is met."""
        # Basic requirement checking - can be enhanced
        if req_name == 'framework':
            return self._check_framework_used(project_path, req_value)
        elif req_name == 'database':
            return self._check_database_used(project_path, req_value)
        elif req_name == 'ui_type':
            return self._check_ui_type(project_path, req_value)
        else:
            return True  # Unknown requirement, assume met
    
    def _check_framework_used(self, project_path: Path, framework: str) -> bool:
        """Check if specified framework is used."""
        requirements_file = project_path / 'requirements.txt'
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                content = f.read().lower()
                return framework.lower() in content
        return False
    
    def _check_database_used(self, project_path: Path, database: str) -> bool:
        """Check if specified database is used."""
        # Look for database-related files or imports
        python_files = list(project_path.rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if database.lower() in content:
                        return True
            except:
                continue
        return False
    
    def _check_ui_type(self, project_path: Path, ui_type: str) -> bool:
        """Check if specified UI type is implemented."""
        if ui_type.lower() == 'web':
            # Look for HTML templates or web framework usage
            html_files = list(project_path.rglob("*.html"))
            return len(html_files) > 0
        elif ui_type.lower() == 'cli':
            # Look for CLI-related code
            python_files = list(project_path.rglob("*.py"))
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'click' in content or 'argparse' in content or 'input(' in content:
                            return True
                except:
                    continue
        return False
    
    def _check_feature_implemented(self, project_path: Path, feature: str) -> bool:
        """Check if a specific feature is implemented."""
        # Basic feature checking - look for related keywords in code
        python_files = list(project_path.rglob("*.py"))
        feature_keywords = feature.lower().split()
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in feature_keywords):
                        return True
            except:
                continue
        return False
    
    def _calculate_project_completion(self, validation_report: Dict) -> Dict[str, Any]:
        """Calculate overall project completion percentage."""
        scores = {
            'structure': validation_report['structure_check']['score'],
            'files': validation_report['file_check']['score'],
            'syntax': validation_report['syntax_check']['score'],
            'requirements': validation_report['requirements_check']['score']
        }
        
        # Weighted average
        weights = {
            'structure': 0.2,
            'files': 0.3,
            'syntax': 0.3,
            'requirements': 0.2
        }
        
        weighted_score = sum(scores[key] * weights[key] for key in scores)
        
        return {
            "percentage": round(weighted_score, 1),
            "details": scores,
            "weights": weights
        }
    
    def _generate_recommendations(self, validation_report: Dict) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Structure recommendations
        structure = validation_report['structure_check']
        if structure['missing_directories']:
            recommendations.append(f"Create missing directories: {', '.join(structure['missing_directories'])}")
        if structure['missing_files']:
            recommendations.append(f"Create missing files: {', '.join(structure['missing_files'])}")
        
        # File recommendations
        file_check = validation_report['file_check']
        if file_check['files_missing']:
            recommendations.append(f"Implement missing files: {', '.join(file_check['files_missing'])}")
        if file_check['empty_files']:
            recommendations.append(f"Add content to empty files: {', '.join(file_check['empty_files'])}")
        
        # Syntax recommendations
        syntax = validation_report['syntax_check']
        if syntax['syntax_errors']:
            recommendations.append(f"Fix syntax errors in {len(syntax['syntax_errors'])} files")
        
        # Requirements recommendations
        req_check = validation_report['requirements_check']
        if req_check['requirements_missing']:
            recommendations.append(f"Implement missing requirements: {', '.join(req_check['requirements_missing'])}")
        
        # General recommendations
        completion = validation_report['completion_percentage']
        if completion < 50:
            recommendations.append("Project is in early stages - focus on core implementation")
        elif completion < 80:
            recommendations.append("Project is progressing well - add remaining features and tests")
        elif completion < 95:
            recommendations.append("Project is nearly complete - focus on polish and documentation")
        
        return recommendations
    
    def _run_tests(self, **kwargs) -> Dict[str, Any]:
        """Run project tests if available."""
        project_path = Path(kwargs.get('project_path', '.'))
        
        test_results = {
            "tests_found": False,
            "tests_run": False,
            "test_results": {},
            "success": False
        }
        
        # Look for test files
        test_files = list(project_path.rglob("test_*.py")) + list(project_path.rglob("*_test.py"))
        
        if test_files:
            test_results["tests_found"] = True
            
            try:
                # Try to run pytest if available
                result = subprocess.run(
                    ['python', '-m', 'pytest', str(project_path), '-v'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                test_results["tests_run"] = True
                test_results["test_results"] = {
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                test_results["success"] = result.returncode == 0
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                test_results["test_results"] = {
                    "error": "Could not run tests - pytest not available or timeout"
                }
        
        return {
            "success": True,
            "operation": "run_tests",
            "test_results": test_results
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["project_path", "requirements", "implementation_plan"],
            "output_types": ["validation_report", "completion_status"],
            "estimated_execution_time": "5-30s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": [
                "validate_project", "check_completeness", "quality_check",
                "syntax_validation", "test_execution", "completion_calculation"
            ],
            "api_dependencies": [],
            "memory_usage": "low"
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "validate project completeness and quality",
            "check project structure and required files",
            "verify code syntax and implementation",
            "calculate project completion percentage",
            "run tests and validate functionality",
            "generate project improvement recommendations"
        ]
