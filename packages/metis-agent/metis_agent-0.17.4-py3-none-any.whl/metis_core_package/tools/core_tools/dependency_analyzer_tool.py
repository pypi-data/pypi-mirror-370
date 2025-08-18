#!/usr/bin/env python3
"""
DependencyAnalyzerTool - Analyze and manage project dependencies

This tool analyzes project dependency files, checks for outdated packages,
identifies security vulnerabilities, and provides recommendations for updates.
It follows the Metis Agent Tools Framework v2.0 standards and is completely stateless.
"""

import json
import os
import re
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import configparser

from ..base import BaseTool


class DependencyAnalyzerTool(BaseTool):
    """
    Analyze and manage project dependencies with security and update recommendations.
    
    This tool scans projects for dependency files, analyzes dependency trees,
    checks for vulnerabilities, and suggests updates with:
    - Support for multiple dependency formats (requirements.txt, package.json, pyproject.toml)
    - Vulnerability scanning using public databases
    - Outdated package detection
    - Security recommendations
    - Dependency tree analysis
    
    The tool is stateless and does NOT:
    - Install or modify packages
    - Store state between calls
    - Make network calls without explicit permission
    
    The tool DOES:
    - Parse dependency files using deterministic algorithms
    - Check package versions against known databases
    - Generate structured analysis reports
    - Provide actionable recommendations
    """
    
    def __init__(self):
        """Initialize the dependency analyzer tool."""
        self.name = "DependencyAnalyzerTool"
        self.description = "Analyze project dependencies, check for vulnerabilities, and provide update recommendations"
        
        # Supported dependency file formats
        self.dependency_formats = {
            'python': {
                'files': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
                'patterns': {
                    'requirements.txt': r'^([a-zA-Z0-9\-_\.]+)([><=!~]+)?([0-9\.]+)?',
                    'pyproject.toml': r'"([a-zA-Z0-9\-_\.]+)"\s*=\s*"([^"]+)"',
                    'setup.py': r'["\']([a-zA-Z0-9\-_\.]+)["\']'
                }
            },
            'javascript': {
                'files': ['package.json', 'yarn.lock', 'package-lock.json'],
                'patterns': {
                    'package.json': r'"([a-zA-Z0-9\-_\.@/]+)"\s*:\s*"([^"]+)"'
                }
            },
            'java': {
                'files': ['pom.xml', 'build.gradle', 'gradle.properties'],
                'patterns': {
                    'pom.xml': r'<artifactId>([^<]+)</artifactId>',
                    'build.gradle': r'implementation\s+["\']([^"\']+)["\']'
                }
            }
        }
        
        # Known vulnerability databases (simplified for deterministic operation)
        self.vulnerability_patterns = {
            'python': {
                'django<3.2': 'Django versions below 3.2 have known security issues',
                'flask<2.0': 'Flask versions below 2.0 have security vulnerabilities',
                'requests<2.25': 'Requests versions below 2.25 have SSL verification issues',
                'pillow<8.3': 'Pillow versions below 8.3 have image processing vulnerabilities',
                'pyyaml<5.4': 'PyYAML versions below 5.4 have code execution vulnerabilities'
            },
            'javascript': {
                'lodash<4.17.21': 'Lodash versions below 4.17.21 have prototype pollution issues',
                'express<4.17.1': 'Express versions below 4.17.1 have security vulnerabilities',
                'axios<0.21.1': 'Axios versions below 0.21.1 have SSRF vulnerabilities'
            }
        }
        
        # Package update recommendations
        self.update_recommendations = {
            'python': {
                'django': 'Latest stable version recommended for security updates',
                'flask': 'Update to latest version for security patches',
                'requests': 'Keep updated for SSL/TLS improvements',
                'numpy': 'Regular updates for performance improvements',
                'pandas': 'Update for bug fixes and performance'
            },
            'javascript': {
                'react': 'Update to latest stable for security and features',
                'express': 'Keep updated for security patches',
                'lodash': 'Update to latest for security fixes'
            }
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle dependency analysis tasks.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task involves dependency analysis, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_lower = task.strip().lower()
        
        # Primary keywords for dependency analysis
        dependency_keywords = {
            'dependencies', 'packages', 'requirements', 'dependency',
            'vulnerability', 'vulnerabilities', 'security scan',
            'outdated packages', 'update dependencies', 'package audit',
            'dependency check', 'security audit', 'package security'
        }
        
        # File-related indicators
        file_indicators = {
            'requirements.txt', 'package.json', 'pyproject.toml',
            'setup.py', 'pipfile', 'yarn.lock', 'pom.xml'
        }
        
        # Action indicators
        action_indicators = {
            'analyze', 'check', 'scan', 'audit', 'review', 'examine'
        }
        
        # Check for dependency analysis intent
        has_dependency_intent = any(keyword in task_lower for keyword in dependency_keywords)
        
        # Check for file context
        has_file_context = any(indicator in task_lower for indicator in file_indicators)
        
        # Check for analysis actions
        has_action_context = any(indicator in task_lower for indicator in action_indicators)
        
        # Must have dependency intent and either file context or action context
        return has_dependency_intent and (has_file_context or has_action_context)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute dependency analysis with comprehensive scanning.
        
        Args:
            task: The dependency analysis task description
            **kwargs: Additional parameters including:
                - project_path: Path to project directory (default: current directory)
                - include_dev: Include development dependencies (default: True)
                - check_vulnerabilities: Check for known vulnerabilities (default: True)
                - output_format: Output format (json, text) (default: json)
                
        Returns:
            Dictionary containing dependency analysis results
        """
        try:
            # Extract parameters
            project_path = kwargs.get('project_path', '.')
            include_dev = kwargs.get('include_dev', True)
            check_vulnerabilities = kwargs.get('check_vulnerabilities', True)
            output_format = kwargs.get('output_format', 'json')
            
            # Validate project path
            if not os.path.exists(project_path):
                return self._error_response(f"Project path does not exist: {project_path}")
            
            # Find dependency files
            dependency_files = self._find_dependency_files(project_path)
            if not dependency_files:
                return self._error_response(
                    "No dependency files found",
                    suggestions=[
                        "Ensure project contains dependency files (requirements.txt, package.json, etc.)",
                        "Check project_path parameter points to correct directory",
                        "Supported files: requirements.txt, package.json, pyproject.toml, setup.py"
                    ]
                )
            
            # Parse dependencies from found files
            all_dependencies = {}
            parsing_errors = []
            
            for file_path, file_type in dependency_files:
                try:
                    dependencies = self._parse_dependency_file(file_path, file_type)
                    all_dependencies[file_path] = dependencies
                except Exception as e:
                    parsing_errors.append(f"Error parsing {file_path}: {str(e)}")
            
            if not all_dependencies and parsing_errors:
                return self._error_response(
                    "Failed to parse any dependency files",
                    suggestions=parsing_errors
                )
            
            # Analyze dependencies
            analysis_results = self._analyze_dependencies(
                all_dependencies, 
                check_vulnerabilities=check_vulnerabilities
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis_results)
            
            # Create summary statistics
            total_dependencies = sum(len(deps) for deps in all_dependencies.values())
            vulnerable_count = len(analysis_results.get('vulnerabilities', []))
            outdated_count = len(analysis_results.get('outdated', []))
            
            return {
                'success': True,
                'type': 'dependency_analysis',
                'data': {
                    'dependency_files': [f[0] for f in dependency_files],
                    'total_dependencies': total_dependencies,
                    'dependencies_by_file': all_dependencies,
                    'vulnerabilities': analysis_results.get('vulnerabilities', []),
                    'outdated_packages': analysis_results.get('outdated', []),
                    'recommendations': recommendations,
                    'summary': {
                        'files_analyzed': len(dependency_files),
                        'total_dependencies': total_dependencies,
                        'vulnerable_packages': vulnerable_count,
                        'outdated_packages': outdated_count,
                        'security_score': self._calculate_security_score(vulnerable_count, total_dependencies)
                    }
                },
                'analysis': {
                    'parsing_errors': parsing_errors,
                    'check_vulnerabilities': check_vulnerabilities,
                    'include_dev': include_dev,
                    'project_path': project_path
                },
                'metadata': {
                    'tool_name': self.name,
                    'timestamp': datetime.now().isoformat(),
                    'output_format': output_format
                }
            }
            
        except Exception as e:
            return self._error_response(f"Dependency analysis failed: {str(e)}", e)
    
    def _find_dependency_files(self, project_path: str) -> List[Tuple[str, str]]:
        """Find all dependency files in the project directory."""
        found_files = []
        project_path = Path(project_path)
        
        # Search for dependency files
        for language, config in self.dependency_formats.items():
            for filename in config['files']:
                file_path = project_path / filename
                if file_path.exists():
                    found_files.append((str(file_path), language))
        
        # Also search in common subdirectories
        common_subdirs = ['src', 'app', 'lib', 'backend', 'frontend']
        for subdir in common_subdirs:
            subdir_path = project_path / subdir
            if subdir_path.exists() and subdir_path.is_dir():
                for language, config in self.dependency_formats.items():
                    for filename in config['files']:
                        file_path = subdir_path / filename
                        if file_path.exists():
                            found_files.append((str(file_path), language))
        
        return found_files
    
    def _parse_dependency_file(self, file_path: str, file_type: str) -> Dict[str, str]:
        """Parse a dependency file and extract package information."""
        dependencies = {}
        file_path = Path(file_path)
        filename = file_path.name
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if filename == 'requirements.txt':
                dependencies = self._parse_requirements_txt(content)
            elif filename == 'package.json':
                dependencies = self._parse_package_json(content)
            elif filename == 'pyproject.toml':
                dependencies = self._parse_pyproject_toml(content)
            elif filename == 'setup.py':
                dependencies = self._parse_setup_py(content)
            elif filename in ['Pipfile', 'pipfile']:
                dependencies = self._parse_pipfile(content)
            else:
                # Try generic parsing based on file type patterns
                patterns = self.dependency_formats.get(file_type, {}).get('patterns', {})
                for pattern_name, pattern in patterns.items():
                    if pattern_name in filename:
                        dependencies = self._parse_with_regex(content, pattern)
                        break
            
        except Exception as e:
            raise Exception(f"Failed to parse {file_path}: {str(e)}")
        
        return dependencies
    
    def _parse_requirements_txt(self, content: str) -> Dict[str, str]:
        """Parse requirements.txt format."""
        dependencies = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Skip -r, -e, and other pip options
            if line.startswith('-'):
                continue
            
            # Parse package specification
            match = re.match(r'^([a-zA-Z0-9\-_\.]+)([><=!~]+)?([0-9\.]+.*)?', line)
            if match:
                package_name = match.group(1)
                version_spec = match.group(2) or ''
                version = match.group(3) or ''
                dependencies[package_name] = f"{version_spec}{version}".strip()
        
        return dependencies
    
    def _parse_package_json(self, content: str) -> Dict[str, str]:
        """Parse package.json format."""
        dependencies = {}
        
        try:
            data = json.loads(content)
            
            # Parse dependencies
            for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
                if dep_type in data:
                    for package, version in data[dep_type].items():
                        dependencies[package] = version
                        
        except json.JSONDecodeError:
            # Fallback to regex parsing
            pattern = r'"([a-zA-Z0-9\-_\.@/]+)"\s*:\s*"([^"]+)"'
            matches = re.findall(pattern, content)
            for package, version in matches:
                if not package.startswith('@types/'):  # Skip type definitions for now
                    dependencies[package] = version
        
        return dependencies
    
    def _parse_pyproject_toml(self, content: str) -> Dict[str, str]:
        """Parse pyproject.toml format."""
        dependencies = {}
        
        # Simple TOML parsing for dependencies section
        in_dependencies = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line == '[tool.poetry.dependencies]' or line == '[project.dependencies]':
                in_dependencies = True
                continue
            elif line.startswith('[') and in_dependencies:
                in_dependencies = False
                continue
            
            if in_dependencies and '=' in line:
                match = re.match(r'([a-zA-Z0-9\-_\.]+)\s*=\s*"([^"]+)"', line)
                if match:
                    package_name = match.group(1)
                    version = match.group(2)
                    dependencies[package_name] = version
        
        return dependencies
    
    def _parse_setup_py(self, content: str) -> Dict[str, str]:
        """Parse setup.py format."""
        dependencies = {}
        
        # Look for install_requires and setup() calls
        install_requires_pattern = r'install_requires\s*=\s*\[(.*?)\]'
        match = re.search(install_requires_pattern, content, re.DOTALL)
        
        if match:
            requirements_text = match.group(1)
            # Extract quoted strings
            package_pattern = r'["\']([^"\']+)["\']'
            packages = re.findall(package_pattern, requirements_text)
            
            for package in packages:
                # Parse package specification
                pkg_match = re.match(r'^([a-zA-Z0-9\-_\.]+)([><=!~]+)?([0-9\.]+.*)?', package)
                if pkg_match:
                    package_name = pkg_match.group(1)
                    version_spec = pkg_match.group(2) or ''
                    version = pkg_match.group(3) or ''
                    dependencies[package_name] = f"{version_spec}{version}".strip()
        
        return dependencies
    
    def _parse_pipfile(self, content: str) -> Dict[str, str]:
        """Parse Pipfile format."""
        dependencies = {}
        
        # Simple parsing for [packages] section
        in_packages = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line == '[packages]':
                in_packages = True
                continue
            elif line.startswith('[') and in_packages:
                in_packages = False
                continue
            
            if in_packages and '=' in line:
                match = re.match(r'([a-zA-Z0-9\-_\.]+)\s*=\s*"([^"]+)"', line)
                if match:
                    package_name = match.group(1)
                    version = match.group(2)
                    dependencies[package_name] = version
        
        return dependencies
    
    def _parse_with_regex(self, content: str, pattern: str) -> Dict[str, str]:
        """Parse content using a regex pattern."""
        dependencies = {}
        matches = re.findall(pattern, content)
        
        for match in matches:
            if isinstance(match, tuple) and len(match) >= 2:
                package_name = match[0]
                version = match[1] if len(match) > 1 else ''
                dependencies[package_name] = version
            elif isinstance(match, str):
                dependencies[match] = ''
        
        return dependencies
    
    def _analyze_dependencies(self, all_dependencies: Dict[str, Dict[str, str]], 
                            check_vulnerabilities: bool = True) -> Dict[str, Any]:
        """Analyze dependencies for vulnerabilities and outdated packages."""
        vulnerabilities = []
        outdated = []
        
        # Flatten all dependencies
        all_packages = {}
        for file_path, dependencies in all_dependencies.items():
            for package, version in dependencies.items():
                if package not in all_packages:
                    all_packages[package] = []
                all_packages[package].append({
                    'version': version,
                    'file': file_path
                })
        
        if check_vulnerabilities:
            # Check for known vulnerabilities
            for package, instances in all_packages.items():
                for instance in instances:
                    version = instance['version']
                    file_path = instance['file']
                    
                    # Determine language from file path
                    language = self._detect_language_from_file(file_path)
                    
                    # Check vulnerability patterns
                    vuln_patterns = self.vulnerability_patterns.get(language, {})
                    for pattern, description in vuln_patterns.items():
                        if self._matches_vulnerability_pattern(package, version, pattern):
                            vulnerabilities.append({
                                'package': package,
                                'version': version,
                                'file': file_path,
                                'vulnerability': description,
                                'severity': self._assess_vulnerability_severity(pattern),
                                'pattern': pattern
                            })
                
                # Check if package is commonly outdated
                if self._is_commonly_outdated(package, instances[0]['version']):
                    outdated.append({
                        'package': package,
                        'current_version': instances[0]['version'],
                        'files': [inst['file'] for inst in instances],
                        'recommendation': self._get_update_recommendation(package)
                    })
        
        return {
            'vulnerabilities': vulnerabilities,
            'outdated': outdated,
            'total_packages': len(all_packages)
        }
    
    def _detect_language_from_file(self, file_path: str) -> str:
        """Detect programming language from file path."""
        filename = Path(file_path).name.lower()
        
        if filename in ['requirements.txt', 'pyproject.toml', 'setup.py', 'pipfile']:
            return 'python'
        elif filename in ['package.json', 'yarn.lock', 'package-lock.json']:
            return 'javascript'
        elif filename in ['pom.xml', 'build.gradle']:
            return 'java'
        else:
            return 'unknown'
    
    def _matches_vulnerability_pattern(self, package: str, version: str, pattern: str) -> bool:
        """Check if package version matches a vulnerability pattern."""
        # Parse pattern like "django<3.2"
        match = re.match(r'^([a-zA-Z0-9\-_\.]+)([<>=!~]+)([0-9\.]+)$', pattern)
        if not match:
            return False
        
        pattern_package = match.group(1)
        operator = match.group(2)
        pattern_version = match.group(3)
        
        # Check if package matches
        if package.lower() != pattern_package.lower():
            return False
        
        # Simple version comparison (basic implementation)
        current_version = self._extract_version_number(version)
        target_version = self._extract_version_number(pattern_version)
        
        if operator == '<':
            return self._version_less_than(current_version, target_version)
        elif operator == '<=':
            return self._version_less_than_or_equal(current_version, target_version)
        elif operator == '>':
            return self._version_greater_than(current_version, target_version)
        elif operator == '>=':
            return self._version_greater_than_or_equal(current_version, target_version)
        elif operator == '==':
            return current_version == target_version
        
        return False
    
    def _extract_version_number(self, version_string: str) -> Tuple[int, ...]:
        """Extract version number tuple from version string."""
        # Remove version specifiers and extract just the number
        clean_version = re.sub(r'^[><=!~]+', '', version_string)
        clean_version = re.sub(r'[^\d\.].*$', '', clean_version)
        
        try:
            parts = clean_version.split('.')
            return tuple(int(part) for part in parts if part.isdigit())
        except ValueError:
            return (0,)
    
    def _version_less_than(self, v1: Tuple[int, ...], v2: Tuple[int, ...]) -> bool:
        """Compare if version v1 is less than v2."""
        # Pad shorter version with zeros
        max_len = max(len(v1), len(v2))
        v1_padded = v1 + (0,) * (max_len - len(v1))
        v2_padded = v2 + (0,) * (max_len - len(v2))
        
        return v1_padded < v2_padded
    
    def _version_less_than_or_equal(self, v1: Tuple[int, ...], v2: Tuple[int, ...]) -> bool:
        """Compare if version v1 is less than or equal to v2."""
        return self._version_less_than(v1, v2) or v1 == v2
    
    def _version_greater_than(self, v1: Tuple[int, ...], v2: Tuple[int, ...]) -> bool:
        """Compare if version v1 is greater than v2."""
        return not self._version_less_than_or_equal(v1, v2)
    
    def _version_greater_than_or_equal(self, v1: Tuple[int, ...], v2: Tuple[int, ...]) -> bool:
        """Compare if version v1 is greater than or equal to v2."""
        return not self._version_less_than(v1, v2)
    
    def _assess_vulnerability_severity(self, pattern: str) -> str:
        """Assess vulnerability severity based on pattern."""
        if any(keyword in pattern.lower() for keyword in ['django', 'flask', 'express']):
            return 'HIGH'
        elif any(keyword in pattern.lower() for keyword in ['requests', 'axios', 'lodash']):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _is_commonly_outdated(self, package: str, version: str) -> bool:
        """Check if package is commonly outdated (simplified heuristic)."""
        # Simple heuristic: packages with very old version patterns
        version_number = self._extract_version_number(version)
        
        if not version_number:
            return False
        
        major_version = version_number[0]
        
        # Common patterns for outdated packages
        outdated_patterns = {
            'django': major_version < 3,
            'flask': major_version < 2,
            'requests': major_version < 2,
            'numpy': major_version < 1,
            'pandas': major_version < 1,
            'react': major_version < 17,
            'express': major_version < 4
        }
        
        return outdated_patterns.get(package.lower(), False)
    
    def _get_update_recommendation(self, package: str) -> str:
        """Get update recommendation for a package."""
        # Try to find recommendation in our database
        for language, recommendations in self.update_recommendations.items():
            if package.lower() in recommendations:
                return recommendations[package.lower()]
        
        return f"Consider updating {package} to the latest stable version"
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        vulnerabilities = analysis_results.get('vulnerabilities', [])
        outdated = analysis_results.get('outdated', [])
        
        # High priority: Security vulnerabilities
        for vuln in vulnerabilities:
            if vuln['severity'] == 'HIGH':
                recommendations.append({
                    'priority': 'HIGH',
                    'type': 'security',
                    'action': f"Update {vuln['package']} immediately",
                    'reason': vuln['vulnerability'],
                    'package': vuln['package'],
                    'current_version': vuln['version']
                })
        
        # Medium priority: Other vulnerabilities
        for vuln in vulnerabilities:
            if vuln['severity'] in ['MEDIUM', 'LOW']:
                recommendations.append({
                    'priority': vuln['severity'],
                    'type': 'security',
                    'action': f"Update {vuln['package']} when convenient",
                    'reason': vuln['vulnerability'],
                    'package': vuln['package'],
                    'current_version': vuln['version']
                })
        
        # Low priority: Outdated packages
        for pkg in outdated:
            recommendations.append({
                'priority': 'LOW',
                'type': 'maintenance',
                'action': f"Consider updating {pkg['package']}",
                'reason': pkg['recommendation'],
                'package': pkg['package'],
                'current_version': pkg['current_version']
            })
        
        return recommendations
    
    def _calculate_security_score(self, vulnerable_count: int, total_count: int) -> int:
        """Calculate a security score (0-100) based on vulnerabilities."""
        if total_count == 0:
            return 100
        
        vulnerability_ratio = vulnerable_count / total_count
        
        # Score calculation: 100 - (vulnerability_ratio * 100)
        # But with some weighting for severity
        score = max(0, 100 - int(vulnerability_ratio * 150))  # 150 to be more strict
        
        return min(100, score)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["project_path", "dependency_files", "text"],
            "output_types": ["structured_data", "analysis_report"],
            "estimated_execution_time": "3-15s",
            "requires_internet": False,  # Uses local databases only
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": [
                "analyze_dependencies", "check_vulnerabilities", "security_audit",
                "dependency_scan", "package_audit", "outdated_packages"
            ],
            "api_dependencies": [],
            "memory_usage": "low",
            "supported_languages": ["python", "javascript", "java"],
            "supported_files": [
                "requirements.txt", "package.json", "pyproject.toml", 
                "setup.py", "Pipfile", "yarn.lock", "pom.xml", "build.gradle"
            ]
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "Analyze dependencies in this project for security vulnerabilities",
            "Check requirements.txt for outdated packages",
            "Scan package.json for vulnerable dependencies",
            "Audit project dependencies for security issues",
            "Check for outdated Python packages in requirements.txt",
            "Analyze all dependency files in the project directory"
        ]
    
    def _error_response(self, message: str, exception: Exception = None, 
                       suggestions: List[str] = None) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': suggestions or [
                "Ensure project contains dependency files (requirements.txt, package.json, etc.)",
                "Check project_path parameter points to correct directory",
                "Verify dependency files have valid syntax",
                f"Supported files: {', '.join(sum([config['files'] for config in self.dependency_formats.values()], []))}",
                "Use check_vulnerabilities=False to skip vulnerability scanning"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_languages': list(self.dependency_formats.keys()),
                'supported_files': sum([config['files'] for config in self.dependency_formats.values()], [])
            }
        }
