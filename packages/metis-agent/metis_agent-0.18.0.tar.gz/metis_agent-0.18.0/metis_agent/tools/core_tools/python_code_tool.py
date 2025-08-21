#!/usr/bin/env python3
"""
Framework-Compliant PythonCodeTool - Follows Metis Agent Tools Framework v2.0
Specialized for Python code execution, testing, and development tasks.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re
import ast
import time
import tempfile
import os
import sys
import subprocess
import traceback
import io
import contextlib

from ..base import BaseTool


class PythonCodeTool(BaseTool):
    """Production-ready Python code execution and development tool.
    
    This tool handles Python code execution, testing, package management,
    virtual environment operations, and Python-specific development tasks.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize Python code tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "PythonCodeTool"  # MUST match class name exactly
        self.description = "Executes Python code, runs tests, manages packages, and handles Python development tasks"
        
        # Optional metadata
        self.version = "1.0.0"
        self.category = "core_tools"
        
        # Python-specific capabilities
        self.python_operations = {
            'execute': ['run', 'execute', 'exec', 'python', 'script'],
            'test': ['test', 'pytest', 'unittest', 'check', 'verify'],
            'install': ['install', 'pip', 'package', 'dependency', 'requirements'],
            'format': ['format', 'black', 'autopep8', 'style', 'lint'],
            'analyze': ['analyze', 'profile', 'performance', 'memory', 'time'],
            'debug': ['debug', 'trace', 'error', 'exception', 'traceback'],
            'environment': ['venv', 'virtualenv', 'conda', 'environment', 'activate']
        }
        
        # Security settings for code execution
        self.execution_timeout = 30  # seconds
        self.max_output_length = 10000  # characters
        self.restricted_imports = {
            'os.system', 'subprocess.call', 'eval', 'exec', '__import__',
            'open', 'file', 'input', 'raw_input'
        }
        
        # Python code patterns
        self.python_patterns = [
            r'def\s+\w+\(',           # Function definition
            r'class\s+\w+',           # Class definition
            r'import\s+\w+',          # Import statement
            r'from\s+\w+\s+import',   # From import
            r'if\s+__name__\s*==\s*["\']__main__["\']', # Main block
            r'print\s*\(',            # Print statement
            r'return\s+',             # Return statement
            r'for\s+\w+\s+in',        # For loop
            r'while\s+',              # While loop
            r'try\s*:',               # Try block
            r'except\s+',             # Exception handling
        ]
        
        # Supported Python versions
        self.supported_versions = ['3.8', '3.9', '3.10', '3.11', '3.12']
        
    def can_handle(self, task: str) -> bool:
        """Intelligent Python task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        Handles Python-specific development and execution tasks.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires Python operations, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Python-specific keywords
        python_keywords = {
            'python', 'py', 'script', 'execute', 'run', 'test', 'pytest',
            'pip', 'install', 'package', 'venv', 'virtualenv', 'conda',
            'black', 'flake8', 'pylint', 'mypy', 'unittest', 'debug'
        }
        
        has_python_keyword = any(keyword in task_clean for keyword in python_keywords)
        
        # Layer 2: Operation detection
        has_operation = any(
            any(op_word in task_clean for op_word in op_words)
            for op_words in self.python_operations.values()
        )
        
        # Layer 3: Python code pattern detection
        has_python_code = any(
            re.search(pattern, task, re.IGNORECASE | re.MULTILINE)
            for pattern in self.python_patterns
        )
        
        # Layer 4: File extension detection
        has_py_extension = '.py' in task_clean or 'python file' in task_clean
        
        # Layer 5: Exclusion filters
        exclusion_patterns = [
            'create', 'generate', 'write new', 'build from scratch',
            'design', 'architect', 'plan'
        ]
        
        has_exclusion = any(pattern in task_clean for pattern in exclusion_patterns)
        
        # Decision logic
        if has_exclusion:
            return False
        
        return (has_python_keyword and has_operation) or has_python_code or has_py_extension
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute Python development task with robust error handling.
        
        Args:
            task: Python task to perform
            **kwargs: Additional parameters (code, file_path, packages, etc.)
            
        Returns:
            Structured dictionary with execution results
        """
        start_time = time.time()
        
        try:
            # Extract parameters
            code = kwargs.get('code', '')
            file_path = kwargs.get('file_path', '')
            packages = kwargs.get('packages', [])
            test_file = kwargs.get('test_file', '')
            environment = kwargs.get('environment', '')
            
            # Detect operation type
            operation = self._detect_operation(task)
            
            # Extract code from task if not provided
            if not code and not file_path:
                code = self._extract_python_code(task)
            
            # Perform the operation
            result = self._perform_python_operation(
                operation, task, code, file_path, packages, test_file, environment
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Return success response
            return {
                'success': True,
                'type': 'python_execution_response',
                'data': result,
                'metadata': {
                    'tool_name': self.name,
                    'timestamp': datetime.now().isoformat(),
                    'execution_time': f"{execution_time:.3f}s",
                    'operation': operation,
                    'python_version': sys.version.split()[0]
                }
            }
            
        except Exception as e:
            return self._error_response(f"Python operation failed: {str(e)}", e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect the type of Python operation requested."""
        task_lower = task.lower()
        
        for operation, keywords in self.python_operations.items():
            if any(keyword in task_lower for keyword in keywords):
                return operation
        
        return 'execute'  # Default operation
    
    def _extract_python_code(self, task: str) -> str:
        """Extract Python code blocks from the task description."""
        # Look for code blocks
        code_block_pattern = r'```(?:python|py)?\s*\n(.*?)\n```'
        matches = re.findall(code_block_pattern, task, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # Look for code after colon (common pattern)
        colon_pattern = r'(?:code|python|execute|run)\s*:\s*(.+?)(?:\n|$)'
        colon_matches = re.findall(colon_pattern, task, re.IGNORECASE | re.MULTILINE)
        
        if colon_matches:
            code_candidate = colon_matches[0].strip()
            # Check if it looks like Python code
            if any(keyword in code_candidate.lower() for keyword in ['print(', 'def ', 'import ', 'return ', '=', 'if ', 'for ']):
                return code_candidate
        
        # Look for inline code
        inline_pattern = r'`([^`]+)`'
        inline_matches = re.findall(inline_pattern, task)
        
        if inline_matches:
            # Check if it looks like Python code
            for match in inline_matches:
                if any(pattern in match for pattern in ['def ', 'import ', 'print(', 'return ']):
                    return match.strip()
        
        # Look for quoted code (simplified pattern)
        if '"' in task or "'" in task:
            # Simple extraction for quoted strings containing Python keywords
            for quote_char in ['"', "'"]:
                if quote_char in task:
                    parts = task.split(quote_char)
                    for part in parts:
                        if any(keyword in part.lower() for keyword in ['print(', 'def ', 'import ', 'return ', '=']):
                            return part.strip()
        
        return ''
    
    def _perform_python_operation(self, operation: str, task: str, code: str, 
                                file_path: str, packages: List[str], 
                                test_file: str, environment: str) -> Dict[str, Any]:
        """Perform the specific Python operation."""
        
        if operation == 'execute':
            return self._execute_python_code(code, file_path)
        elif operation == 'test':
            return self._run_python_tests(test_file, code)
        elif operation == 'install':
            return self._install_packages(packages or self._extract_packages(task))
        elif operation == 'format':
            return self._format_python_code(code, file_path)
        elif operation == 'analyze':
            return self._analyze_python_code(code, file_path)
        elif operation == 'debug':
            return self._debug_python_code(code, file_path, task)
        elif operation == 'environment':
            return self._manage_environment(environment or self._extract_env_name(task))
        else:
            return {'error': f'Unknown operation: {operation}'}
    
    def _execute_python_code(self, code: str, file_path: str = '') -> Dict[str, Any]:
        """Execute Python code safely with output capture."""
        if file_path and os.path.exists(file_path):
            # Execute file
            try:
                result = subprocess.run(
                    [sys.executable, file_path],
                    capture_output=True,
                    text=True,
                    timeout=self.execution_timeout
                )
                
                return {
                    'execution_type': 'file',
                    'file_path': file_path,
                    'stdout': result.stdout[:self.max_output_length],
                    'stderr': result.stderr[:self.max_output_length],
                    'return_code': result.returncode,
                    'success': result.returncode == 0
                }
            except subprocess.TimeoutExpired:
                return {'error': f'Execution timed out after {self.execution_timeout} seconds'}
            except Exception as e:
                return {'error': f'File execution failed: {str(e)}'}
        
        elif code:
            # Execute code string
            return self._execute_code_string(code)
        
        else:
            return {'error': 'No code or file path provided'}
    
    def _execute_code_string(self, code: str) -> Dict[str, Any]:
        """Execute Python code string with output capture."""
        # Security check
        if self._has_restricted_operations(code):
            return {'error': 'Code contains restricted operations for security'}
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Compile code first to check syntax
            compiled_code = compile(code, '<string>', 'exec')
            
            # Execute with output capture
            with contextlib.redirect_stdout(stdout_capture), \
                 contextlib.redirect_stderr(stderr_capture):
                
                # Create execution namespace
                exec_globals = {
                    '__builtins__': __builtins__,
                    '__name__': '__main__'
                }
                exec_locals = {}
                
                # Execute the code
                exec(compiled_code, exec_globals, exec_locals)
            
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()
            
            return {
                'execution_type': 'string',
                'stdout': stdout_content[:self.max_output_length],
                'stderr': stderr_content[:self.max_output_length],
                'variables': {k: str(v) for k, v in exec_locals.items() if not k.startswith('_')},
                'success': len(stderr_content) == 0
            }
            
        except SyntaxError as e:
            return {
                'error': f'Syntax error: {str(e)}',
                'line_number': e.lineno,
                'error_type': 'SyntaxError'
            }
        except Exception as e:
            return {
                'error': f'Runtime error: {str(e)}',
                'traceback': traceback.format_exc(),
                'error_type': type(e).__name__
            }
        finally:
            stdout_capture.close()
            stderr_capture.close()
    
    def _has_restricted_operations(self, code: str) -> bool:
        """Check if code contains restricted operations."""
        for restricted in self.restricted_imports:
            if restricted in code:
                return True
        return False
    
    def _run_python_tests(self, test_file: str, code: str = '') -> Dict[str, Any]:
        """Run Python tests using pytest or unittest."""
        if test_file and os.path.exists(test_file):
            # Run test file
            try:
                # Try pytest first
                result = subprocess.run(
                    [sys.executable, '-m', 'pytest', test_file, '-v'],
                    capture_output=True,
                    text=True,
                    timeout=self.execution_timeout
                )
                
                if result.returncode != 0:
                    # Fallback to unittest
                    result = subprocess.run(
                        [sys.executable, '-m', 'unittest', test_file],
                        capture_output=True,
                        text=True,
                        timeout=self.execution_timeout
                    )
                
                return {
                    'test_type': 'file',
                    'test_file': test_file,
                    'stdout': result.stdout[:self.max_output_length],
                    'stderr': result.stderr[:self.max_output_length],
                    'return_code': result.returncode,
                    'tests_passed': result.returncode == 0
                }
                
            except subprocess.TimeoutExpired:
                return {'error': f'Test execution timed out after {self.execution_timeout} seconds'}
            except Exception as e:
                return {'error': f'Test execution failed: {str(e)}'}
        
        elif code:
            # Run inline test code
            return self._execute_code_string(code)
        
        else:
            return {'error': 'No test file or test code provided'}
    
    def _install_packages(self, packages: List[str]) -> Dict[str, Any]:
        """Install Python packages using pip."""
        if not packages:
            return {'error': 'No packages specified'}
        
        results = {}
        
        for package in packages:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=120  # Longer timeout for package installation
                )
                
                results[package] = {
                    'success': result.returncode == 0,
                    'stdout': result.stdout[:1000],  # Truncate for readability
                    'stderr': result.stderr[:1000]
                }
                
            except subprocess.TimeoutExpired:
                results[package] = {'error': 'Installation timed out'}
            except Exception as e:
                results[package] = {'error': str(e)}
        
        return {
            'operation': 'package_installation',
            'packages': packages,
            'results': results,
            'overall_success': all(r.get('success', False) for r in results.values())
        }
    
    def _extract_packages(self, task: str) -> List[str]:
        """Extract package names from task description."""
        # Look for common patterns
        patterns = [
            r'install\s+([a-zA-Z0-9_-]+)',
            r'pip\s+install\s+([a-zA-Z0-9_-]+)',
            r'package\s+([a-zA-Z0-9_-]+)',
            r'requirements?\s*:\s*([a-zA-Z0-9_,\s-]+)'
        ]
        
        packages = []
        for pattern in patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            packages.extend(matches)
        
        # Clean and split package names
        cleaned_packages = []
        for pkg in packages:
            if ',' in pkg:
                cleaned_packages.extend([p.strip() for p in pkg.split(',')])
            else:
                cleaned_packages.append(pkg.strip())
        
        return [pkg for pkg in cleaned_packages if pkg and pkg.isidentifier()]
    
    def _format_python_code(self, code: str, file_path: str = '') -> Dict[str, Any]:
        """Format Python code using available formatters."""
        if file_path and os.path.exists(file_path):
            # Format file
            try:
                # Try black first
                result = subprocess.run(
                    [sys.executable, '-m', 'black', '--diff', file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    'formatter': 'black',
                    'file_path': file_path,
                    'diff': result.stdout,
                    'success': result.returncode == 0,
                    'errors': result.stderr
                }
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return {'error': 'Black formatter not available or timed out'}
            except Exception as e:
                return {'error': f'Formatting failed: {str(e)}'}
        
        elif code:
            # Basic code formatting
            try:
                # Parse and reformat using ast
                tree = ast.parse(code)
                formatted = ast.unparse(tree) if hasattr(ast, 'unparse') else code
                
                return {
                    'formatter': 'ast',
                    'original_code': code,
                    'formatted_code': formatted,
                    'success': True
                }
                
            except SyntaxError as e:
                return {'error': f'Syntax error in code: {str(e)}'}
            except Exception as e:
                return {'error': f'Formatting failed: {str(e)}'}
        
        else:
            return {'error': 'No code or file path provided'}
    
    def _analyze_python_code(self, code: str, file_path: str = '') -> Dict[str, Any]:
        """Analyze Python code for complexity, structure, and metrics."""
        target_code = code
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    target_code = f.read()
            except Exception as e:
                return {'error': f'Could not read file: {str(e)}'}
        
        if not target_code:
            return {'error': 'No code to analyze'}
        
        try:
            tree = ast.parse(target_code)
            
            analysis = {
                'lines_of_code': len(target_code.splitlines()),
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity_metrics': {},
                'structure_analysis': {}
            }
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line_number': node.lineno,
                        'args_count': len(node.args.args),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line_number': node.lineno,
                        'methods_count': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    else:
                        analysis['imports'].append(f"{node.module}")
            
            # Calculate metrics
            analysis['complexity_metrics'] = {
                'total_functions': len(analysis['functions']),
                'total_classes': len(analysis['classes']),
                'total_imports': len(analysis['imports']),
                'avg_function_args': sum(f['args_count'] for f in analysis['functions']) / max(len(analysis['functions']), 1),
                'documented_functions': sum(1 for f in analysis['functions'] if f['has_docstring']),
                'documented_classes': sum(1 for c in analysis['classes'] if c['has_docstring'])
            }
            
            return analysis
            
        except SyntaxError as e:
            return {'error': f'Syntax error in code: {str(e)}'}
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _debug_python_code(self, code: str, file_path: str = '', task: str = '') -> Dict[str, Any]:
        """Debug Python code and provide suggestions."""
        target_code = code
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    target_code = f.read()
            except Exception as e:
                return {'error': f'Could not read file: {str(e)}'}
        
        if not target_code:
            return {'error': 'No code to debug'}
        
        debug_info = {
            'syntax_check': {},
            'potential_issues': [],
            'suggestions': [],
            'common_fixes': []
        }
        
        # Syntax check
        try:
            ast.parse(target_code)
            debug_info['syntax_check'] = {'valid': True, 'message': 'Syntax is valid'}
        except SyntaxError as e:
            debug_info['syntax_check'] = {
                'valid': False,
                'error': str(e),
                'line_number': e.lineno,
                'offset': e.offset
            }
        
        # Common issue detection
        lines = target_code.splitlines()
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for common issues
            if line_stripped.endswith(':') and not line_stripped.startswith(('#', '"""', "'''")):
                next_line = lines[i] if i < len(lines) else ''
                if not next_line.strip():
                    debug_info['potential_issues'].append(f'Line {i}: Empty block after colon')
            
            if 'print(' in line and not line.strip().startswith('#'):
                debug_info['potential_issues'].append(f'Line {i}: Debug print statement found')
            
            if line.count('(') != line.count(')'):
                debug_info['potential_issues'].append(f'Line {i}: Mismatched parentheses')
            
            if line.count('[') != line.count(']'):
                debug_info['potential_issues'].append(f'Line {i}: Mismatched brackets')
        
        # General suggestions
        debug_info['suggestions'] = [
            'Add print statements to track variable values',
            'Use a debugger (pdb) for step-by-step execution',
            'Check variable types with type() function',
            'Verify function parameters and return values',
            'Add try-except blocks for error handling',
            'Use logging instead of print for debugging'
        ]
        
        debug_info['common_fixes'] = [
            'Check indentation (Python uses 4 spaces)',
            'Verify all imports are correct',
            'Ensure all variables are defined before use',
            'Check for typos in variable and function names',
            'Verify file paths and permissions'
        ]
        
        return debug_info
    
    def _manage_environment(self, env_name: str) -> Dict[str, Any]:
        """Manage Python virtual environments."""
        if not env_name:
            return {'error': 'No environment name provided'}
        
        try:
            # Check if environment exists
            venv_path = os.path.join(os.getcwd(), env_name)
            
            if os.path.exists(venv_path):
                return {
                    'environment': env_name,
                    'path': venv_path,
                    'exists': True,
                    'status': 'Environment already exists',
                    'activation_command': f'source {venv_path}/bin/activate' if os.name != 'nt' else f'{venv_path}\\Scripts\\activate'
                }
            else:
                # Create new environment
                result = subprocess.run(
                    [sys.executable, '-m', 'venv', env_name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                return {
                    'environment': env_name,
                    'path': venv_path,
                    'created': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'activation_command': f'source {venv_path}/bin/activate' if os.name != 'nt' else f'{venv_path}\\Scripts\\activate'
                }
                
        except subprocess.TimeoutExpired:
            return {'error': 'Environment creation timed out'}
        except Exception as e:
            return {'error': f'Environment management failed: {str(e)}'}
    
    def _extract_env_name(self, task: str) -> str:
        """Extract environment name from task description."""
        patterns = [
            r'environment\s+([a-zA-Z0-9_-]+)',
            r'venv\s+([a-zA-Z0-9_-]+)',
            r'virtualenv\s+([a-zA-Z0-9_-]+)',
            r'create\s+([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return 'new_env'  # Default name
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text", "python_code", "file_path", "package_names"],
            "output_types": ["structured_data", "execution_results", "analysis_data"],
            "estimated_execution_time": "<30s",
            "requires_internet": True,  # For package installation
            "requires_filesystem": True,
            "concurrent_safe": False,  # Code execution can have side effects
            "resource_intensive": True,  # Code execution can be resource intensive
            "supported_intents": [
                "execute", "run", "test", "install", "format", "analyze", 
                "debug", "environment", "python", "script"
            ],
            "api_dependencies": ["pip", "python"],
            "memory_usage": "moderate-high",
            "python_operations": list(self.python_operations.keys()),
            "supported_python_versions": self.supported_versions
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "Execute this Python code: print('Hello, World!')",
            "Run the Python script at /path/to/script.py",
            "Install the requests package using pip",
            "Format this Python code using black",
            "Analyze the complexity of this Python function",
            "Debug this Python code and find the error",
            "Create a virtual environment called myproject",
            "Run pytest on the test_module.py file",
            "Check the syntax of this Python code",
            "Execute Python code and capture the output"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        error_type = type(exception).__name__ if exception else 'ValidationError'
        
        suggestions = [
            "Ensure the task involves Python code execution or development",
            "Provide Python code using code blocks (```python)",
            "Specify file paths for Python scripts to execute",
            "For package installation, list package names clearly",
            "Check that Python code syntax is valid",
            "Ensure file paths exist and are accessible"
        ]
        
        # Add specific suggestions based on error type
        if 'timeout' in message.lower():
            suggestions.append(f"Code execution is limited to {self.execution_timeout} seconds")
        elif 'syntax' in message.lower():
            suggestions.append("Check Python code syntax and indentation")
        elif 'package' in message.lower():
            suggestions.append("Verify package names and internet connectivity")
        
        return {
            'success': False,
            'error': message,
            'error_type': error_type,
            'suggestions': suggestions,
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_operations': list(self.python_operations.keys()),
                'python_version': sys.version.split()[0],
                'execution_timeout': self.execution_timeout
            }
        }
