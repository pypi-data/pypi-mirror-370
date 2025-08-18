#!/usr/bin/env python3
"""
UnitTestGeneratorTool - Generates comprehensive unit tests for code

This tool analyzes code and generates appropriate unit tests with proper test cases,
edge cases, and error scenarios. It follows the Metis Agent Tools Framework v2.0
standards and is completely stateless.
"""

import ast
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from ..base import BaseTool


class UnitTestGeneratorTool(BaseTool):
    """
    Generate comprehensive unit tests for code with intelligent analysis.
    
    This tool analyzes code structure, identifies functions and classes,
    and generates appropriate unit tests with:
    - Basic functionality tests
    - Edge case testing
    - Error condition testing
    - Mock usage where appropriate
    - Proper test structure and naming
    
    The tool is stateless and does NOT:
    - Initialize LLM instances
    - Store state between calls
    - Execute the generated tests
    
    The tool DOES:
    - Analyze code structure using AST
    - Generate test files with proper naming
    - Include comprehensive test scenarios
    - Follow testing best practices
    """
    
    def __init__(self):
        """Initialize the unit test generator tool."""
        self.name = "UnitTestGeneratorTool"
        self.description = "Generate comprehensive unit tests for Python code with intelligent analysis and best practices"
        
        # Supported programming languages for test generation
        self.supported_languages = {
            'python': {
                'extensions': ['.py'],
                'test_framework': 'pytest',
                'test_prefix': 'test_',
                'test_suffix': '_test.py'
            }
        }
        
        # Test generation patterns
        self.test_patterns = {
            'function': {
                'basic': 'test_{function_name}',
                'edge_case': 'test_{function_name}_edge_cases',
                'error': 'test_{function_name}_error_conditions',
                'parametrized': 'test_{function_name}_parametrized'
            },
            'class': {
                'init': 'test_{class_name}_init',
                'methods': 'test_{class_name}_{method_name}',
                'properties': 'test_{class_name}_{property_name}_property'
            }
        }
        
        # Common test scenarios
        self.test_scenarios = {
            'edge_cases': [
                'empty_input', 'none_input', 'zero_value', 'negative_value',
                'large_value', 'special_characters', 'unicode_input'
            ],
            'error_conditions': [
                'invalid_type', 'invalid_value', 'missing_parameter',
                'file_not_found', 'permission_error', 'network_error'
            ]
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle unit test generation tasks.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task involves unit test generation, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_lower = task.strip().lower()
        
        # Primary keywords for unit test generation
        test_keywords = {
            'generate tests', 'create tests', 'unit tests', 'test cases',
            'write tests', 'test generation', 'test coverage', 'testing',
            'pytest', 'unittest', 'test suite', 'test file'
        }
        
        # Code-related context indicators
        code_indicators = {
            'function', 'class', 'method', 'code', 'python', 'module',
            'script', 'file', 'implementation'
        }
        
        # Check for test generation intent
        has_test_intent = any(keyword in task_lower for keyword in test_keywords)
        
        # Check for code context
        has_code_context = any(indicator in task_lower for indicator in code_indicators)
        
        # Look for actual code patterns in the task
        has_code_patterns = bool(
            re.search(r'def\s+\w+\(', task) or  # Python function
            re.search(r'class\s+\w+', task) or  # Python class
            re.search(r'```python', task) or    # Code block
            re.search(r'\.py', task)            # Python file reference
        )
        
        # Must have test intent and either code context or actual code
        return has_test_intent and (has_code_context or has_code_patterns)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute unit test generation with comprehensive analysis.
        
        Args:
            task: The test generation task description
            **kwargs: Additional parameters including:
                - code: Code to generate tests for (optional)
                - file_path: Path to code file (optional)
                - test_framework: Testing framework to use (default: pytest)
                - include_mocks: Whether to include mock usage (default: True)
                - coverage_target: Target test coverage percentage (default: 90)
                
        Returns:
            Dictionary containing generated tests and analysis
        """
        try:
            # Extract parameters
            code_content = kwargs.get('code', '')
            file_path = kwargs.get('file_path', '')
            test_framework = kwargs.get('test_framework', 'pytest')
            include_mocks = kwargs.get('include_mocks', True)
            coverage_target = kwargs.get('coverage_target', 90)
            
            # Extract code from task if not provided in kwargs
            if not code_content and not file_path:
                code_content = self._extract_code_from_task(task)
            
            # Read code from file if file path provided
            if file_path and not code_content:
                code_content = self._read_code_file(file_path)
            
            if not code_content:
                return self._error_response(
                    "No code provided for test generation",
                    suggestions=[
                        "Provide code directly in the task using code blocks (```python)",
                        "Specify a file_path parameter pointing to a Python file",
                        "Include code in the 'code' parameter",
                        "Example: 'Generate tests for this function: def add(a, b): return a + b'"
                    ]
                )
            
            # Analyze code structure
            code_analysis = self._analyze_code_structure(code_content)
            if not code_analysis['success']:
                return code_analysis
            
            # Generate test cases
            test_generation_result = self._generate_test_cases(
                code_analysis['data'],
                test_framework=test_framework,
                include_mocks=include_mocks,
                coverage_target=coverage_target
            )
            
            # Create test file content
            test_file_content = self._create_test_file_content(
                test_generation_result,
                original_code=code_content,
                file_path=file_path
            )
            
            # Generate test file name
            test_file_name = self._generate_test_file_name(file_path or 'code')
            
            return {
                'success': True,
                'type': 'unit_test_generation',
                'data': {
                    'test_file_name': test_file_name,
                    'test_file_content': test_file_content,
                    'test_cases_generated': len(test_generation_result['test_cases']),
                    'functions_tested': len(code_analysis['data']['functions']),
                    'classes_tested': len(code_analysis['data']['classes']),
                    'estimated_coverage': test_generation_result['estimated_coverage']
                },
                'analysis': {
                    'code_structure': code_analysis['data'],
                    'test_strategy': test_generation_result['strategy'],
                    'framework_used': test_framework,
                    'mocks_included': include_mocks
                },
                'metadata': {
                    'tool_name': self.name,
                    'timestamp': datetime.now().isoformat(),
                    'language': 'python',
                    'test_framework': test_framework
                }
            }
            
        except Exception as e:
            return self._error_response(f"Test generation failed: {str(e)}", e)
    
    def _extract_code_from_task(self, task: str) -> str:
        """Extract Python code from task description."""
        # Look for code blocks
        code_block_pattern = r'```python\s*\n(.*?)\n```'
        matches = re.findall(code_block_pattern, task, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        # Look for inline code patterns
        function_pattern = r'(def\s+\w+\([^)]*\):[^}]+?)(?=\n\n|\n[A-Za-z]|\Z)'
        class_pattern = r'(class\s+\w+[^:]*:[^}]+?)(?=\n\n|\n[A-Za-z]|\Z)'
        
        functions = re.findall(function_pattern, task, re.DOTALL)
        classes = re.findall(class_pattern, task, re.DOTALL)
        
        if functions or classes:
            return '\n\n'.join(functions + classes)
        
        return ''
    
    def _read_code_file(self, file_path: str) -> str:
        """Read code content from file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return ''
            
            if path.suffix not in ['.py']:
                return ''
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ''
    
    def _analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """Analyze code structure using AST."""
        try:
            tree = ast.parse(code)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': self._get_return_type(node),
                        'docstring': ast.get_docstring(node),
                        'is_method': False,
                        'line_number': node.lineno
                    }
                    functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'args': [arg.arg for arg in item.args.args],
                                'returns': self._get_return_type(item),
                                'docstring': ast.get_docstring(item),
                                'is_method': True,
                                'line_number': item.lineno
                            }
                            class_methods.append(method_info)
                    
                    class_info = {
                        'name': node.name,
                        'methods': class_methods,
                        'docstring': ast.get_docstring(node),
                        'line_number': node.lineno
                    }
                    classes.append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            return {
                'success': True,
                'data': {
                    'functions': functions,
                    'classes': classes,
                    'imports': imports,
                    'total_functions': len(functions),
                    'total_classes': len(classes)
                }
            }
            
        except SyntaxError as e:
            return {
                'success': False,
                'error': f"Code syntax error: {str(e)}",
                'suggestions': [
                    "Check code syntax for Python compatibility",
                    "Ensure proper indentation",
                    "Verify all brackets and parentheses are closed"
                ]
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Code analysis failed: {str(e)}"
            }
    
    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if available."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None
    
    def _generate_test_cases(self, code_structure: Dict[str, Any], 
                           test_framework: str = 'pytest',
                           include_mocks: bool = True,
                           coverage_target: int = 90) -> Dict[str, Any]:
        """Generate comprehensive test cases for the analyzed code."""
        test_cases = []
        strategy = {
            'framework': test_framework,
            'include_mocks': include_mocks,
            'coverage_target': coverage_target,
            'test_types': ['basic', 'edge_cases', 'error_conditions']
        }
        
        # Generate tests for functions
        for func in code_structure['functions']:
            if not func['is_method']:  # Standalone functions
                test_cases.extend(self._generate_function_tests(func, include_mocks))
        
        # Generate tests for classes
        for cls in code_structure['classes']:
            test_cases.extend(self._generate_class_tests(cls, include_mocks))
        
        # Estimate coverage
        total_testable_items = (
            len(code_structure['functions']) + 
            sum(len(cls['methods']) for cls in code_structure['classes'])
        )
        estimated_coverage = min(95, (len(test_cases) / max(1, total_testable_items)) * 30)
        
        return {
            'test_cases': test_cases,
            'strategy': strategy,
            'estimated_coverage': round(estimated_coverage, 1)
        }
    
    def _generate_function_tests(self, func_info: Dict[str, Any], include_mocks: bool) -> List[Dict[str, Any]]:
        """Generate test cases for a function."""
        tests = []
        func_name = func_info['name']
        args = func_info['args']
        
        # Basic functionality test
        tests.append({
            'type': 'basic',
            'name': f"test_{func_name}",
            'description': f"Test basic functionality of {func_name}",
            'test_code': self._generate_basic_function_test(func_info)
        })
        
        # Edge cases test
        if args:
            tests.append({
                'type': 'edge_cases',
                'name': f"test_{func_name}_edge_cases",
                'description': f"Test edge cases for {func_name}",
                'test_code': self._generate_edge_case_test(func_info)
            })
        
        # Error conditions test
        tests.append({
            'type': 'error_conditions',
            'name': f"test_{func_name}_error_conditions",
            'description': f"Test error conditions for {func_name}",
            'test_code': self._generate_error_test(func_info)
        })
        
        # Parametrized test if appropriate
        if len(args) > 0:
            tests.append({
                'type': 'parametrized',
                'name': f"test_{func_name}_parametrized",
                'description': f"Parametrized tests for {func_name}",
                'test_code': self._generate_parametrized_test(func_info)
            })
        
        return tests
    
    def _generate_class_tests(self, class_info: Dict[str, Any], include_mocks: bool) -> List[Dict[str, Any]]:
        """Generate test cases for a class."""
        tests = []
        class_name = class_info['name']
        
        # Test class initialization
        tests.append({
            'type': 'init',
            'name': f"test_{class_name.lower()}_init",
            'description': f"Test {class_name} initialization",
            'test_code': self._generate_class_init_test(class_info)
        })
        
        # Test each method
        for method in class_info['methods']:
            if method['name'] != '__init__':
                tests.extend(self._generate_method_tests(class_info, method, include_mocks))
        
        return tests
    
    def _generate_method_tests(self, class_info: Dict[str, Any], method_info: Dict[str, Any], 
                              include_mocks: bool) -> List[Dict[str, Any]]:
        """Generate test cases for a class method."""
        tests = []
        class_name = class_info['name']
        method_name = method_info['name']
        
        # Basic method test
        tests.append({
            'type': 'method',
            'name': f"test_{class_name.lower()}_{method_name}",
            'description': f"Test {class_name}.{method_name} method",
            'test_code': self._generate_method_test(class_info, method_info)
        })
        
        return tests
    
    def _generate_basic_function_test(self, func_info: Dict[str, Any]) -> str:
        """Generate basic test code for a function."""
        func_name = func_info['name']
        args = func_info['args']
        
        # Create sample arguments
        sample_args = []
        for arg in args:
            if arg == 'self':
                continue
            sample_args.append(self._get_sample_value(arg))
        
        args_str = ', '.join(sample_args)
        
        return f'''def test_{func_name}():
    """Test basic functionality of {func_name}."""
    # Arrange
    {self._generate_arrange_section(args, sample_args)}
    
    # Act
    result = {func_name}({args_str})
    
    # Assert
    assert result is not None
    # Add specific assertions based on expected behavior'''
    
    def _generate_edge_case_test(self, func_info: Dict[str, Any]) -> str:
        """Generate edge case test code."""
        func_name = func_info['name']
        
        return f'''@pytest.mark.parametrize("input_value,expected", [
    (None, None),  # None input
    ("", ""),      # Empty string
    (0, 0),        # Zero value
    (-1, -1),      # Negative value
])
def test_{func_name}_edge_cases(input_value, expected):
    """Test edge cases for {func_name}."""
    # This is a template - adjust parameters based on actual function signature
    result = {func_name}(input_value)
    # Add appropriate assertions'''
    
    def _generate_error_test(self, func_info: Dict[str, Any]) -> str:
        """Generate error condition test code."""
        func_name = func_info['name']
        
        return f'''def test_{func_name}_error_conditions():
    """Test error conditions for {func_name}."""
    # Test invalid input types
    with pytest.raises((TypeError, ValueError)):
        {func_name}("invalid_input")
    
    # Test missing parameters (if applicable)
    with pytest.raises(TypeError):
        {func_name}()'''
    
    def _generate_parametrized_test(self, func_info: Dict[str, Any]) -> str:
        """Generate parametrized test code."""
        func_name = func_info['name']
        
        return f'''@pytest.mark.parametrize("test_input,expected", [
    # Add test cases here based on function requirements
    ("test1", "expected1"),
    ("test2", "expected2"),
    ("test3", "expected3"),
])
def test_{func_name}_parametrized(test_input, expected):
    """Parametrized tests for {func_name}."""
    result = {func_name}(test_input)
    assert result == expected'''
    
    def _generate_class_init_test(self, class_info: Dict[str, Any]) -> str:
        """Generate class initialization test."""
        class_name = class_info['name']
        
        return f'''def test_{class_name.lower()}_init():
    """Test {class_name} initialization."""
    # Arrange & Act
    instance = {class_name}()
    
    # Assert
    assert isinstance(instance, {class_name})
    # Add assertions for initial state'''
    
    def _generate_method_test(self, class_info: Dict[str, Any], method_info: Dict[str, Any]) -> str:
        """Generate method test code."""
        class_name = class_info['name']
        method_name = method_info['name']
        
        return f'''def test_{class_name.lower()}_{method_name}():
    """Test {class_name}.{method_name} method."""
    # Arrange
    instance = {class_name}()
    
    # Act
    result = instance.{method_name}()
    
    # Assert
    assert result is not None
    # Add specific assertions'''
    
    def _generate_arrange_section(self, args: List[str], sample_args: List[str]) -> str:
        """Generate the arrange section for tests."""
        if not args or len(args) <= 1:  # No args or just 'self'
            return "# No setup required"
        
        arrange_lines = []
        for i, arg in enumerate(args):
            if arg != 'self' and i < len(sample_args):
                arrange_lines.append(f"{arg} = {sample_args[i]}")
        
        return '\n    '.join(arrange_lines) if arrange_lines else "# No setup required"
    
    def _get_sample_value(self, arg_name: str) -> str:
        """Get a sample value for an argument based on its name."""
        arg_lower = arg_name.lower()
        
        if 'name' in arg_lower or 'text' in arg_lower or 'str' in arg_lower:
            return '"test_string"'
        elif 'num' in arg_lower or 'count' in arg_lower or 'size' in arg_lower:
            return '42'
        elif 'list' in arg_lower or 'items' in arg_lower:
            return '[1, 2, 3]'
        elif 'dict' in arg_lower or 'data' in arg_lower:
            return '{"key": "value"}'
        elif 'bool' in arg_lower or 'flag' in arg_lower:
            return 'True'
        else:
            return '"test_value"'
    
    def _create_test_file_content(self, test_generation_result: Dict[str, Any], 
                                 original_code: str, file_path: str = '') -> str:
        """Create the complete test file content."""
        test_cases = test_generation_result['test_cases']
        
        # File header
        header = f'''#!/usr/bin/env python3
"""
Unit tests generated by UnitTestGeneratorTool
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{f"Source file: {file_path}" if file_path else "Source: provided code"}

This file contains comprehensive unit tests including:
- Basic functionality tests
- Edge case testing
- Error condition testing
- Parametrized tests where appropriate
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the source directory to the path if needed
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module under test
# from your_module import YourClass, your_function


'''
        
        # Test class wrapper
        test_class_name = "TestGeneratedCode"
        test_class_header = f'''class {test_class_name}:
    """Test suite for the analyzed code."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        pass
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass

'''
        
        # Generate test methods
        test_methods = []
        for test_case in test_cases:
            test_method = f'''    {test_case["test_code"].replace(chr(10), chr(10) + "    ")}
'''
            test_methods.append(test_method)
        
        # Additional utility tests
        utility_tests = '''

# Additional utility tests
def test_module_imports():
    """Test that all required modules can be imported."""
    # Add import tests here
    pass


if __name__ == "__main__":
    pytest.main([__file__])
'''
        
        return header + test_class_header + '\n'.join(test_methods) + utility_tests
    
    def _generate_test_file_name(self, source_name: str) -> str:
        """Generate appropriate test file name."""
        if source_name.endswith('.py'):
            base_name = source_name[:-3]
        else:
            base_name = source_name
        
        # Clean the base name
        base_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        
        return f"test_{base_name}.py"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["code", "file_path", "text"],
            "output_types": ["test_file", "structured_data"],
            "estimated_execution_time": "2-10s",
            "requires_internet": False,
            "requires_filesystem": True,  # For reading source files
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": [
                "generate_tests", "create_tests", "unit_testing",
                "test_generation", "test_coverage", "testing"
            ],
            "api_dependencies": [],
            "memory_usage": "low",
            "supported_languages": ["python"],
            "test_frameworks": ["pytest", "unittest"]
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "Generate unit tests for this function: def add(a, b): return a + b",
            "Create comprehensive tests for the Calculator class",
            "Generate pytest tests for the code in utils.py",
            "Write unit tests with edge cases for this Python function",
            "Create test cases for this class with mocking",
            "Generate tests with 90% coverage for this module"
        ]
    
    def _error_response(self, message: str, exception: Exception = None, 
                       suggestions: List[str] = None) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': suggestions or [
                "Provide Python code using code blocks (```python)",
                "Ensure code has valid Python syntax",
                "Specify file_path parameter for existing files",
                "Include functions or classes to test",
                f"Supported languages: {', '.join(self.supported_languages.keys())}",
                "Examples: 'Generate tests for def calculate(x, y): return x + y'"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_languages': list(self.supported_languages.keys()),
                'supported_frameworks': ['pytest', 'unittest']
            }
        }
