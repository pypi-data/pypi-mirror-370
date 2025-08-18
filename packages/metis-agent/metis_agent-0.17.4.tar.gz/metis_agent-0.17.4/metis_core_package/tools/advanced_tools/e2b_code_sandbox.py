"""
E2B Code Sandbox Execution Tool

This tool provides secure code execution capabilities using E2B's cloud-based sandboxes.
Supports Python code execution with real-time output, file operations, and visualization.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re
import json
import os
import time
import traceback
from ..base import BaseTool


class E2BCodeSandboxTool(BaseTool):
    """
    Production-ready code execution tool using E2B sandboxes.
    
    This tool provides secure Python code execution in isolated cloud environments
    with support for data analysis, visualization, file operations, and package installation.
    
    Key Features:
    - Secure isolated execution environment
    - Real-time stdout/stderr capture
    - File system operations
    - Package installation support
    - Visualization and chart generation
    - Long-running sandbox sessions
    """
    
    def __init__(self):
        """Initialize E2B Code Sandbox tool with required attributes."""
        # Required attributes following TOOLS_RULES.MD
        self.name = "E2BCodeSandboxTool"
        self.description = "Secure Python code execution in isolated E2B cloud sandboxes with visualization support"
        
        # Optional metadata
        self.version = "1.0.0"
        self.category = "advanced_tools"
        
        # Code execution patterns for can_handle detection
        self.code_patterns = [
            r'execute.*?(?:python\s+)?code',
            r'run.*?(?:python\s+)?code',
            r'python\s+script',
            r'code\s+execution',
            r'sandbox\s+execution',
            r'execute.*?sandbox',
            r'run.*?sandbox',
            r'data\s+analysis',
            r'create\s+chart',
            r'generate\s+plot',
            r'visualization',
            r'matplotlib',
            r'pandas',
            r'numpy',
            r'seaborn'
        ]
        
        # Supported code types
        self.supported_languages = ['python', 'py']
        
        # Common data science and visualization packages
        self.common_packages = [
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
            'scipy', 'scikit-learn', 'requests', 'beautifulsoup4',
            'pillow', 'opencv-python', 'tensorflow', 'torch'
        ]
        
        # Execution timeout settings
        self.default_timeout = 30  # seconds
        self.max_timeout = 300     # 5 minutes max
        
        # Sandbox session management
        self.active_sandboxes = {}
        self.max_sandboxes = 5
        
    def can_handle(self, task: str) -> bool:
        """
        Intelligent code execution task detection.
        
        Uses pattern matching to determine if a task requires code execution
        in a secure sandbox environment.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires code execution, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
            
        task_lower = task.lower().strip()
        
        # Direct code execution indicators
        if any(re.search(pattern, task_lower) for pattern in self.code_patterns):
            return True
            
        # Code block detection
        if '```python' in task_lower or '```py' in task_lower:
            return True
            
        # Data science keywords
        data_science_keywords = [
            'analyze data', 'process data', 'clean data',
            'machine learning', 'deep learning', 'neural network',
            'regression', 'classification', 'clustering',
            'statistics', 'statistical analysis'
        ]
        
        if any(keyword in task_lower for keyword in data_science_keywords):
            return True
            
        # Programming task indicators
        programming_keywords = [
            'write python', 'python function', 'python script',
            'algorithm', 'implement', 'calculate using python',
            'python solution', 'code solution'
        ]
        
        if any(keyword in task_lower for keyword in programming_keywords):
            return True
            
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Python code in a secure E2B sandbox.
        
        Args:
            task: Code execution task description
            **kwargs: Additional parameters including:
                - e2b_api_key: E2B API key (optional, uses auth manager if not provided)
                - code: Python code to execute (optional, extracted from task if not provided)
                - timeout: Execution timeout in seconds (default: 30)
                - install_packages: List of packages to install (optional)
                - sandbox_id: Existing sandbox ID to reuse (optional)
                - files: Dictionary of files to create in sandbox (optional)
                
        Returns:
            Structured dictionary with execution results
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not task or not task.strip():
                return self._error_response(
                    "Task cannot be empty",
                    error_code="INVALID_INPUT"
                )
            
            # Get API key
            api_key = self._get_api_key(kwargs)
            if not api_key:
                return self._error_response(
                    "E2B API key is required",
                    error_code="MISSING_API_KEY",
                    suggestions=[
                        "Provide e2b_api_key parameter",
                        "Set E2B_API_KEY environment variable",
                        "Configure API key in auth manager"
                    ]
                )
            
            # Extract code from task or kwargs
            code = self._extract_code(task, kwargs.get('code'))
            if not code:
                return self._error_response(
                    "No Python code found to execute",
                    error_code="NO_CODE_FOUND",
                    suggestions=[
                        "Include Python code in the task description",
                        "Use code blocks with ```python",
                        "Provide code parameter explicitly"
                    ]
                )
            
            # Get execution parameters
            timeout = min(kwargs.get('timeout', self.default_timeout), self.max_timeout)
            install_packages = kwargs.get('install_packages', [])
            sandbox_id = kwargs.get('sandbox_id')
            files = kwargs.get('files', {})
            
            # Execute code in sandbox
            execution_result = self._execute_in_sandbox(
                code=code,
                api_key=api_key,
                timeout=timeout,
                install_packages=install_packages,
                sandbox_id=sandbox_id,
                files=files
            )
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            
            # Format successful response
            return {
                "success": True,
                "type": "e2b_code_execution_response",
                "data": {
                    "code": code,
                    "output": execution_result.get('output', ''),
                    "stdout": execution_result.get('stdout', ''),
                    "stderr": execution_result.get('stderr', ''),
                    "error": execution_result.get('error'),
                    "results": execution_result.get('results', []),
                    "files_created": execution_result.get('files_created', []),
                    "sandbox_id": execution_result.get('sandbox_id'),
                    "execution_status": execution_result.get('status', 'completed')
                },
                "metadata": {
                    "tool_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "code_length": len(code),
                    "packages_installed": len(install_packages),
                    "timeout_used": timeout,
                    "sandbox_reused": bool(sandbox_id)
                },
                "performance": {
                    "execution_time": execution_time,
                    "memory_usage_mb": execution_result.get('memory_usage', 0),
                    "api_calls_made": 1,
                    "tool_name": self.name
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._error_response(
                f"Code execution failed: {str(e)}",
                exception=e,
                error_code="EXECUTION_FAILED",
                performance_data={
                    "execution_time": execution_time,
                    "memory_usage_mb": 0,
                    "api_calls_made": 0,
                    "tool_name": self.name
                }
            )
    
    def _get_api_key(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract E2B API key from kwargs with fallback to auth manager."""
        # Check kwargs first
        api_key = kwargs.get('e2b_api_key') or kwargs.get('api_key')
        if api_key:
            return api_key
            
        # Check environment variable
        api_key = os.getenv('E2B_API_KEY')
        if api_key:
            return api_key
            
        # Check auth manager
        try:
            from ...auth.api_key_manager import APIKeyManager
            manager = APIKeyManager()
            return manager.get_key('e2b')
        except Exception:
            return None
    
    def _extract_code(self, task: str, explicit_code: Optional[str] = None) -> Optional[str]:
        """Extract Python code from task description or use explicit code."""
        if explicit_code:
            return explicit_code.strip()
            
        # Look for code blocks
        code_block_patterns = [
            r'```python\s*\n(.*?)\n```',
            r'```py\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```'
        ]
        
        for pattern in code_block_patterns:
            matches = re.findall(pattern, task, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Look for inline code patterns
        inline_patterns = [
            r'execute.*?code[:\s]+(.+?)(?:\n|$)',
            r'run.*?code[:\s]+(.+?)(?:\n|$)',
            r'python\s+code[:\s]+(.+?)(?:\n|$)'
        ]
        
        for pattern in inline_patterns:
            match = re.search(pattern, task, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # If task looks like direct code, return it
        if self._looks_like_code(task):
            return task.strip()
            
        return None
    
    def _looks_like_code(self, text: str) -> bool:
        """Heuristic to determine if text looks like Python code."""
        code_indicators = [
            'import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ',
            'print(', 'return ', '= ', '==', '!=', 'True', 'False', 'None'
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in code_indicators if indicator.lower() in text_lower)
        
        # If multiple code indicators present, likely code
        # OR if it's a simple print statement or import statement, also consider it code
        return (indicator_count >= 2 or 
                'print(' in text_lower or 
                text_lower.strip().startswith('import ') or
                text_lower.strip().startswith('from '))
    
    def _execute_in_sandbox(
        self,
        code: str,
        api_key: str,
        timeout: int,
        install_packages: List[str],
        sandbox_id: Optional[str],
        files: Dict[str, str]
    ) -> Dict[str, Any]:
        """Execute code in E2B sandbox with comprehensive error handling."""
        try:
            # Import E2B SDK
            try:
                from e2b_code_interpreter import Sandbox
            except ImportError:
                return {
                    "error": "E2B SDK not installed. Run: pip install e2b-code-interpreter",
                    "status": "failed",
                    "output": "",
                    "stdout": "",
                    "stderr": "ImportError: e2b_code_interpreter module not found"
                }
            
            # Create or reuse sandbox
            if sandbox_id and sandbox_id in self.active_sandboxes:
                sandbox = self.active_sandboxes[sandbox_id]
            else:
                sandbox = Sandbox(api_key=api_key)
                if len(self.active_sandboxes) < self.max_sandboxes:
                    new_id = f"sandbox_{len(self.active_sandboxes)}_{int(time.time())}"
                    self.active_sandboxes[new_id] = sandbox
                    sandbox_id = new_id
            
            # Create files if provided
            files_created = []
            for filename, content in files.items():
                try:
                    sandbox.files.write(filename, content)
                    files_created.append(filename)
                except Exception as e:
                    print(f"Warning: Could not create file {filename}: {e}")
            
            # Install packages if requested
            if install_packages:
                for package in install_packages:
                    try:
                        install_result = sandbox.run_code(f"!pip install {package}")
                        if install_result.error:
                            print(f"Warning: Could not install {package}: {install_result.error}")
                    except Exception as e:
                        print(f"Warning: Package installation failed for {package}: {e}")
            
            # Execute the main code
            execution = sandbox.run_code(code)
            
            # Extract results
            results = []
            if hasattr(execution, 'results') and execution.results:
                for result in execution.results:
                    if hasattr(result, 'text'):
                        results.append({"type": "text", "data": result.text})
                    elif hasattr(result, 'png'):
                        results.append({"type": "image", "format": "png", "data": result.png})
                    elif hasattr(result, 'svg'):
                        results.append({"type": "image", "format": "svg", "data": result.svg})
                    elif hasattr(result, 'html'):
                        results.append({"type": "html", "data": result.html})
                    else:
                        results.append({"type": "unknown", "data": str(result)})
            
            # Get output logs
            stdout = ""
            stderr = ""
            if hasattr(execution, 'logs'):
                raw_stdout = execution.logs.stdout if hasattr(execution.logs, 'stdout') else ""
                raw_stderr = execution.logs.stderr if hasattr(execution.logs, 'stderr') else ""
                
                # Handle both string and list formats
                if isinstance(raw_stdout, list):
                    stdout = ''.join(raw_stdout)
                else:
                    stdout = str(raw_stdout) if raw_stdout else ""
                    
                if isinstance(raw_stderr, list):
                    stderr = ''.join(raw_stderr)
                else:
                    stderr = str(raw_stderr) if raw_stderr else ""
            
            return {
                "output": stdout + stderr,
                "stdout": stdout,
                "stderr": stderr,
                "error": execution.error if hasattr(execution, 'error') else None,
                "results": results,
                "files_created": files_created,
                "sandbox_id": sandbox_id,
                "status": "completed" if not execution.error else "error",
                "memory_usage": 0  # E2B doesn't provide memory usage info
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "output": "",
                "stdout": "",
                "stderr": str(e),
                "results": [],
                "files_created": [],
                "sandbox_id": sandbox_id,
                "memory_usage": 0
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata following TOOLS_RULES.MD."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text", "python_code", "data_analysis_request"],
            "output_types": ["structured_data", "execution_results", "visualizations"],
            "estimated_execution_time": "5-30s",
            "requires_internet": True,
            "requires_filesystem": False,
            "concurrent_safe": True,
            "resource_intensive": True,
            "supported_intents": [
                "execute_code", "run_python", "data_analysis", "visualization",
                "machine_learning", "statistical_analysis", "code_testing"
            ],
            "api_dependencies": ["e2b"],
            "memory_usage": "medium"
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "Execute this Python code: print('Hello, World!')",
            "Run data analysis on a CSV file using pandas",
            "Create a matplotlib chart showing sales data",
            "Execute machine learning model training code",
            "Run statistical analysis using scipy",
            "Generate a visualization with seaborn",
            "Execute code in sandbox: import numpy as np; print(np.array([1,2,3]))",
            "Analyze data and create plots using Python",
            "Run Python script for data processing",
            "Execute code with package installation: pandas, matplotlib"
        ]
    
    def _error_response(
        self,
        message: str,
        exception: Exception = None,
        error_code: str = "EXECUTION_ERROR",
        suggestions: List[str] = None,
        performance_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate standardized error response following TOOLS_RULES.MD."""
        default_suggestions = [
            "Ensure the task contains valid Python code",
            "Provide a valid E2B API key",
            "Check code syntax and imports",
            "Verify package names for installation",
            "Use code blocks with ```python for clarity",
            f"Supported languages: {', '.join(self.supported_languages)}",
            "Example: 'Execute this code: print(\"Hello World\")'"
        ]
        
        return {
            "success": False,
            "error": message,
            "error_code": error_code,
            "error_type": type(exception).__name__ if exception else "ValidationError",
            "details": str(exception) if exception else message,
            "suggestions": suggestions or default_suggestions,
            "metadata": {
                "tool_name": self.name,
                "error_timestamp": datetime.now().isoformat(),
                "supported_languages": self.supported_languages,
                "common_packages": self.common_packages[:10],  # First 10 for brevity
                "max_timeout": self.max_timeout,
                "traceback": traceback.format_exc() if exception else None
            },
            "performance": performance_data or {
                "execution_time": 0,
                "memory_usage_mb": 0,
                "api_calls_made": 0,
                "tool_name": self.name
            }
        }
    
    def cleanup_sandboxes(self):
        """Clean up active sandbox sessions."""
        for sandbox_id, sandbox in self.active_sandboxes.items():
            try:
                if hasattr(sandbox, 'close'):
                    sandbox.close()
            except Exception as e:
                print(f"Warning: Could not close sandbox {sandbox_id}: {e}")
        
        self.active_sandboxes.clear()
    
    def __del__(self):
        """Cleanup when tool is destroyed."""
        try:
            self.cleanup_sandboxes()
        except Exception:
            pass  # Ignore cleanup errors during destruction
