#!/usr/bin/env python3
"""
Unit tests for DependencyAnalyzerTool

Tests the dependency analysis functionality following the enhanced testing requirements
from TOOLS_RULES.MD.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

# Import the tool under test
from ..core_tools.dependency_analyzer_tool import DependencyAnalyzerTool
from ..base import QueryAnalysis


class TestDependencyAnalyzerTool:
    """Test suite for DependencyAnalyzerTool with comprehensive coverage."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.tool = DependencyAnalyzerTool()
        
        # Sample dependency file contents
        self.sample_requirements_txt = """# Sample requirements file
django>=3.0.0
flask==1.1.4
requests>=2.20.0
numpy==1.19.5
pandas>=1.2.0
# Development dependencies
pytest>=6.0.0
black==21.5b0"""
        
        self.sample_package_json = """{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "express": "4.16.4",
    "lodash": "4.17.15",
    "axios": "0.19.2",
    "react": "16.14.0"
  },
  "devDependencies": {
    "jest": "26.6.3",
    "webpack": "5.0.0"
  }
}"""
        
        self.sample_pyproject_toml = """[tool.poetry.dependencies]
python = "^3.8"
django = "^3.2.0"
requests = "^2.25.0"
fastapi = "^0.65.0"

[tool.poetry.dev-dependencies]
pytest = "^6.2.0"
black = "^21.5b0"
"""
        
        self.sample_setup_py = """from setuptools import setup, find_packages

setup(
    name="test-package",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "django>=3.0.0",
        "requests>=2.25.0",
        "numpy==1.20.0",
        "flask<2.0.0"
    ],
    extras_require={
        "dev": ["pytest>=6.0.0", "black==21.5b0"]
    }
)"""
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass
    
    # Basic functionality tests
    
    def test_tool_initialization(self):
        """Test DependencyAnalyzerTool initialization."""
        assert self.tool.name == "DependencyAnalyzerTool"
        assert "dependencies" in self.tool.description.lower()
        assert 'python' in self.tool.dependency_formats
        assert 'javascript' in self.tool.dependency_formats
        assert self.tool.vulnerability_patterns is not None
        assert self.tool.update_recommendations is not None
    
    def test_can_handle_valid_tasks(self):
        """Test can_handle method with valid dependency analysis tasks."""
        valid_tasks = [
            "Analyze dependencies for security vulnerabilities",
            "Check requirements.txt for outdated packages",
            "Scan package.json for vulnerable dependencies",
            "Audit project dependencies",
            "Check for security vulnerabilities in dependencies",
            "Analyze all dependency files in the project"
        ]
        
        for task in valid_tasks:
            assert self.tool.can_handle(task), f"Should handle: {task}"
    
    def test_can_handle_invalid_tasks(self):
        """Test can_handle method with invalid tasks."""
        invalid_tasks = [
            "Generate unit tests for this function",
            "Create a new React component",
            "Deploy the application to production",
            "Write documentation for the API",
            "Fix this bug in the code",
            ""  # Empty task
        ]
        
        for task in invalid_tasks:
            assert not self.tool.can_handle(task), f"Should not handle: {task}"
    
    def test_can_handle_edge_cases(self):
        """Test can_handle with edge cases."""
        edge_cases = [
            None,  # None input
            123,   # Non-string input
            "   ",  # Whitespace only
        ]
        
        for case in edge_cases:
            assert not self.tool.can_handle(case)
    
    # Dependency file parsing tests
    
    def test_parse_requirements_txt(self):
        """Test parsing requirements.txt format."""
        dependencies = self.tool._parse_requirements_txt(self.sample_requirements_txt)
        
        assert 'django' in dependencies
        assert 'flask' in dependencies
        assert 'requests' in dependencies
        assert 'numpy' in dependencies
        assert dependencies['django'] == '>=3.0.0'
        assert dependencies['flask'] == '==1.1.4'
        assert dependencies['numpy'] == '==1.19.5'
        # Comments and empty lines should be ignored
        assert 'pytest' in dependencies  # Should include dev dependencies
    
    def test_parse_package_json(self):
        """Test parsing package.json format."""
        dependencies = self.tool._parse_package_json(self.sample_package_json)
        
        assert 'express' in dependencies
        assert 'lodash' in dependencies
        assert 'axios' in dependencies
        assert 'react' in dependencies
        assert dependencies['express'] == '4.16.4'
        assert dependencies['lodash'] == '4.17.15'
        # Should include both dependencies and devDependencies
        assert 'jest' in dependencies
        assert 'webpack' in dependencies
    
    def test_parse_pyproject_toml(self):
        """Test parsing pyproject.toml format."""
        dependencies = self.tool._parse_pyproject_toml(self.sample_pyproject_toml)
        
        assert 'django' in dependencies
        assert 'requests' in dependencies
        assert 'fastapi' in dependencies
        assert dependencies['django'] == '^3.2.0'
        assert dependencies['requests'] == '^2.25.0'
        # Should include dev dependencies
        assert 'pytest' in dependencies
        assert 'black' in dependencies
    
    def test_parse_setup_py(self):
        """Test parsing setup.py format."""
        dependencies = self.tool._parse_setup_py(self.sample_setup_py)
        
        assert 'django' in dependencies
        assert 'requests' in dependencies
        assert 'numpy' in dependencies
        assert 'flask' in dependencies
        assert dependencies['django'] == '>=3.0.0'
        assert dependencies['numpy'] == '==1.20.0'
        assert dependencies['flask'] == '<2.0.0'
    
    def test_parse_empty_file(self):
        """Test parsing empty dependency file."""
        empty_content = ""
        dependencies = self.tool._parse_requirements_txt(empty_content)
        assert dependencies == {}
    
    def test_parse_comments_only(self):
        """Test parsing file with only comments."""
        comments_only = """# This is a comment
# Another comment
# Yet another comment"""
        dependencies = self.tool._parse_requirements_txt(comments_only)
        assert dependencies == {}
    
    # File discovery tests
    
    def test_find_dependency_files_with_temp_directory(self):
        """Test finding dependency files in a temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            req_file = Path(temp_dir) / "requirements.txt"
            pkg_file = Path(temp_dir) / "package.json"
            
            req_file.write_text("django>=3.0.0")
            pkg_file.write_text('{"dependencies": {"express": "4.0.0"}}')
            
            found_files = self.tool._find_dependency_files(temp_dir)
            
            assert len(found_files) == 2
            file_names = [Path(f[0]).name for f in found_files]
            assert "requirements.txt" in file_names
            assert "package.json" in file_names
    
    def test_find_dependency_files_empty_directory(self):
        """Test finding dependency files in empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            found_files = self.tool._find_dependency_files(temp_dir)
            assert found_files == []
    
    def test_find_dependency_files_subdirectories(self):
        """Test finding dependency files in subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create subdirectory with dependency file
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()
            req_file = src_dir / "requirements.txt"
            req_file.write_text("flask>=1.0.0")
            
            found_files = self.tool._find_dependency_files(temp_dir)
            
            assert len(found_files) == 1
            assert "requirements.txt" in found_files[0][0]
    
    # Version comparison tests
    
    def test_extract_version_number(self):
        """Test version number extraction."""
        test_cases = [
            (">=3.0.0", (3, 0, 0)),
            ("==1.1.4", (1, 1, 4)),
            ("^2.25.0", (2, 25, 0)),
            ("~1.2", (1, 2)),
            ("4.16.4", (4, 16, 4)),
            ("invalid", (0,))
        ]
        
        for version_string, expected in test_cases:
            result = self.tool._extract_version_number(version_string)
            assert result == expected, f"Failed for {version_string}: got {result}, expected {expected}"
    
    def test_version_comparison(self):
        """Test version comparison methods."""
        v1_0_0 = (1, 0, 0)
        v1_1_0 = (1, 1, 0)
        v2_0_0 = (2, 0, 0)
        
        # Test less than
        assert self.tool._version_less_than(v1_0_0, v1_1_0)
        assert self.tool._version_less_than(v1_1_0, v2_0_0)
        assert not self.tool._version_less_than(v2_0_0, v1_0_0)
        
        # Test greater than
        assert self.tool._version_greater_than(v2_0_0, v1_0_0)
        assert not self.tool._version_greater_than(v1_0_0, v2_0_0)
        
        # Test equal versions
        assert not self.tool._version_less_than(v1_0_0, v1_0_0)
        assert not self.tool._version_greater_than(v1_0_0, v1_0_0)
    
    # Vulnerability detection tests
    
    def test_matches_vulnerability_pattern(self):
        """Test vulnerability pattern matching."""
        # Test Django vulnerability pattern
        assert self.tool._matches_vulnerability_pattern("django", "2.0.0", "django<3.2")
        assert not self.tool._matches_vulnerability_pattern("django", "3.2.0", "django<3.2")
        assert not self.tool._matches_vulnerability_pattern("flask", "1.0.0", "django<3.2")
        
        # Test Flask vulnerability pattern
        assert self.tool._matches_vulnerability_pattern("flask", "1.1.4", "flask<2.0")
        assert not self.tool._matches_vulnerability_pattern("flask", "2.0.0", "flask<2.0")
    
    def test_detect_language_from_file(self):
        """Test language detection from file paths."""
        test_cases = [
            ("/path/to/requirements.txt", "python"),
            ("/path/to/package.json", "javascript"),
            ("/path/to/pyproject.toml", "python"),
            ("/path/to/pom.xml", "java"),
            ("/path/to/unknown.txt", "unknown")
        ]
        
        for file_path, expected_language in test_cases:
            result = self.tool._detect_language_from_file(file_path)
            assert result == expected_language
    
    def test_assess_vulnerability_severity(self):
        """Test vulnerability severity assessment."""
        assert self.tool._assess_vulnerability_severity("django<3.2") == "HIGH"
        assert self.tool._assess_vulnerability_severity("flask<2.0") == "HIGH"
        assert self.tool._assess_vulnerability_severity("requests<2.25") == "MEDIUM"
        assert self.tool._assess_vulnerability_severity("unknown<1.0") == "LOW"
    
    # Analysis tests
    
    def test_analyze_dependencies_with_vulnerabilities(self):
        """Test dependency analysis with known vulnerabilities."""
        test_dependencies = {
            "/test/requirements.txt": {
                "django": "2.0.0",  # Vulnerable version
                "flask": "1.0.0",   # Vulnerable version
                "requests": "2.20.0"  # Safe version
            }
        }
        
        results = self.tool._analyze_dependencies(test_dependencies, check_vulnerabilities=True)
        
        assert 'vulnerabilities' in results
        assert len(results['vulnerabilities']) >= 2  # django and flask
        
        # Check that vulnerabilities are properly identified
        vuln_packages = [v['package'] for v in results['vulnerabilities']]
        assert 'django' in vuln_packages
        assert 'flask' in vuln_packages
    
    def test_analyze_dependencies_no_vulnerabilities(self):
        """Test dependency analysis with no vulnerabilities."""
        test_dependencies = {
            "/test/requirements.txt": {
                "django": "4.0.0",  # Safe version
                "flask": "2.1.0",   # Safe version
                "requests": "2.28.0"  # Safe version
            }
        }
        
        results = self.tool._analyze_dependencies(test_dependencies, check_vulnerabilities=True)
        
        # Should find fewer or no vulnerabilities
        assert len(results['vulnerabilities']) == 0
    
    def test_calculate_security_score(self):
        """Test security score calculation."""
        # Perfect score with no vulnerabilities
        assert self.tool._calculate_security_score(0, 10) == 100
        
        # Lower score with vulnerabilities
        score_with_vulns = self.tool._calculate_security_score(2, 10)
        assert 0 <= score_with_vulns < 100
        
        # Edge case: no dependencies
        assert self.tool._calculate_security_score(0, 0) == 100
    
    # Integration tests
    
    def test_execute_with_temp_project(self):
        """Test execute method with temporary project directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a requirements.txt file
            req_file = Path(temp_dir) / "requirements.txt"
            req_file.write_text(self.sample_requirements_txt)
            
            result = self.tool.execute(
                "Analyze dependencies for vulnerabilities",
                project_path=temp_dir
            )
            
            assert result['success'] is True
            assert result['type'] == 'dependency_analysis'
            assert 'dependency_files' in result['data']
            assert 'total_dependencies' in result['data']
            assert result['data']['total_dependencies'] > 0
            assert 'vulnerabilities' in result['data']
            assert 'summary' in result['data']
    
    def test_execute_no_dependency_files(self):
        """Test execute method when no dependency files are found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.tool.execute(
                "Analyze dependencies",
                project_path=temp_dir
            )
            
            assert result['success'] is False
            assert 'No dependency files found' in result['error']
            assert 'suggestions' in result
    
    def test_execute_invalid_project_path(self):
        """Test execute method with invalid project path."""
        result = self.tool.execute(
            "Analyze dependencies",
            project_path="/nonexistent/path"
        )
        
        assert result['success'] is False
        assert 'does not exist' in result['error']
    
    def test_execute_with_multiple_file_types(self):
        """Test execute method with multiple dependency file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple dependency files
            req_file = Path(temp_dir) / "requirements.txt"
            pkg_file = Path(temp_dir) / "package.json"
            
            req_file.write_text("django>=3.0.0\nflask>=1.0.0")
            pkg_file.write_text('{"dependencies": {"express": "4.0.0"}}')
            
            result = self.tool.execute(
                "Analyze all dependencies",
                project_path=temp_dir
            )
            
            assert result['success'] is True
            assert len(result['data']['dependency_files']) == 2
            assert 'dependencies_by_file' in result['data']
    
    # Error handling tests
    
    def test_execute_with_malformed_json(self):
        """Test execute method with malformed package.json."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create malformed package.json
            pkg_file = Path(temp_dir) / "package.json"
            pkg_file.write_text('{"dependencies": {"express": "4.0.0"')  # Missing closing brace
            
            result = self.tool.execute(
                "Analyze dependencies",
                project_path=temp_dir
            )
            
            # Should handle parsing errors gracefully
            assert 'parsing_errors' in result.get('analysis', {})
    
    def test_error_response_format(self):
        """Test error response format compliance."""
        error_response = self.tool._error_response("Test error", ValueError("test"))
        
        assert error_response['success'] is False
        assert 'error' in error_response
        assert 'error_type' in error_response
        assert 'suggestions' in error_response
        assert 'metadata' in error_response
        assert error_response['error_type'] == 'ValueError'
    
    # Capability and metadata tests
    
    def test_get_capabilities(self):
        """Test get_capabilities method."""
        capabilities = self.tool.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'complexity_levels' in capabilities
        assert 'supported_intents' in capabilities
        assert 'python' in capabilities['supported_languages']
        assert 'javascript' in capabilities['supported_languages']
        assert capabilities['requires_filesystem'] is True
        assert capabilities['concurrent_safe'] is True
        assert capabilities['requires_internet'] is False
    
    def test_get_examples(self):
        """Test get_examples method."""
        examples = self.tool.get_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert all(isinstance(example, str) for example in examples)
        assert any('dependencies' in example.lower() for example in examples)
    
    # Performance and monitoring tests
    
    def test_execute_with_monitoring(self):
        """Test execute_with_monitoring method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            req_file = Path(temp_dir) / "requirements.txt"
            req_file.write_text("django>=3.0.0")
            
            result = self.tool.execute_with_monitoring(
                "Analyze dependencies",
                project_path=temp_dir
            )
            
            assert 'metadata' in result
            if 'performance' in result['metadata']:
                perf = result['metadata']['performance']
                assert 'execution_time' in perf
                assert 'memory_usage_mb' in perf
                assert isinstance(perf['execution_time'], (int, float))
    
    # Query analysis compatibility tests
    
    def test_analyze_compatibility_high_score(self):
        """Test compatibility analysis with matching query."""
        query_analysis = QueryAnalysis(
            complexity="moderate",
            intents=["analyze_dependencies", "security_audit"],
            requirements={"requires_filesystem": True},
            confidence=0.9
        )
        
        score = self.tool.analyze_compatibility(query_analysis)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high compatibility
    
    def test_analyze_compatibility_low_score(self):
        """Test compatibility analysis with non-matching query."""
        query_analysis = QueryAnalysis(
            complexity="simple",
            intents=["generate_tests", "create_documentation"],
            requirements={"requires_internet": True},
            confidence=0.8
        )
        
        score = self.tool.analyze_compatibility(query_analysis)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Should be low compatibility
    
    # Recommendation tests
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        analysis_results = {
            'vulnerabilities': [
                {
                    'package': 'django',
                    'version': '2.0.0',
                    'severity': 'HIGH',
                    'vulnerability': 'Known security issue'
                }
            ],
            'outdated': [
                {
                    'package': 'numpy',
                    'current_version': '1.19.0',
                    'recommendation': 'Update for performance improvements'
                }
            ]
        }
        
        recommendations = self.tool._generate_recommendations(analysis_results)
        
        assert len(recommendations) >= 2
        assert any(rec['priority'] == 'HIGH' for rec in recommendations)
        assert any(rec['type'] == 'security' for rec in recommendations)
        assert any(rec['type'] == 'maintenance' for rec in recommendations)
    
    # Edge cases and boundary tests
    
    def test_parse_unusual_version_formats(self):
        """Test parsing unusual version formats."""
        unusual_requirements = """package1~=1.4.2
package2!=1.5.0
package3>=1.0,<2.0
package4[extra]>=1.0.0"""
        
        dependencies = self.tool._parse_requirements_txt(unusual_requirements)
        
        assert 'package1' in dependencies
        assert 'package2' in dependencies
        assert 'package3' in dependencies
        # Should handle complex version specifiers gracefully


# Additional utility tests
def test_module_imports():
    """Test that all required modules can be imported."""
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
    
    # Test tool import
    from ..core_tools.dependency_analyzer_tool import DependencyAnalyzerTool
    from ..base import BaseTool
    
    assert DependencyAnalyzerTool
    assert BaseTool


if __name__ == "__main__":
    pytest.main([__file__])
