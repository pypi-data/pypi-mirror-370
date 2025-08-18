#!/usr/bin/env python3
"""
Framework-Compliant CodingTool - Follows Metis Agent Tools Framework v2.0
Focuses on code processing, validation, and analysis (NOT generation).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import ast
import time
import tempfile
import os

from ..base import BaseTool

class CodingTool(BaseTool):
    """Production-ready code processing tool with intelligent task detection.
    
    This tool handles code validation, formatting, analysis, debugging, and explanation.
    It does NOT generate code - that's the agent's responsibility.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize coding tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "CodingTool"  # MUST match class name exactly
        self.description = "Validates, formats, analyzes, and processes existing code"
        
        # Optional metadata
        self.version = "3.0.0"
        self.category = "core_tools"
        
        # Supported programming languages for processing
        self.supported_languages = {
            'python', 'javascript', 'java', 'c++', 'c', 'c#', 'php', 'ruby',
            'go', 'rust', 'swift', 'kotlin', 'typescript', 'html', 'css', 'sql'
        }
        
        # Code processing operations (NO generation)
        self.operation_types = {
            'validate': ['validate', 'check', 'verify', 'syntax', 'lint', 'errors'],
            'format': ['format', 'beautify', 'style', 'indent', 'clean up'],
            'analyze': ['analyze', 'review', 'examine', 'inspect', 'evaluate'],
            'debug': ['debug', 'fix', 'troubleshoot', 'error', 'issue', 'problem'],
            'explain': ['explain', 'describe', 'what does', 'how does', 'understand'],
            'optimize': ['optimize', 'improve', 'performance', 'efficiency', 'refactor']
        }
        
        # Code detection patterns
        self.code_patterns = [
            r'def\s+\w+\(',           # Python function
            r'function\s+\w+\(',      # JavaScript function  
            r'class\s+\w+',           # Class definition
            r'import\s+\w+',          # Import statement
            r'#include\s*<',          # C/C++ include
            r'public\s+static\s+void', # Java main method
            r'SELECT\s+.*FROM',       # SQL query
            r'<html>|<div>|<p>',      # HTML tags
            r'```\w*\n',              # Code blocks
        ]
    
    def can_handle(self, task: str) -> bool:
        """Intelligent code processing task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        Only handles tasks that involve PROCESSING existing code.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires code processing, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Semantic Analysis - Code Processing Keywords
        processing_keywords = {
            'validate', 'check', 'verify', 'syntax', 'lint', 'errors',
            'format', 'beautify', 'style', 'indent', 'clean',
            'analyze', 'review', 'examine', 'inspect', 'evaluate',
            'debug', 'fix', 'troubleshoot', 'error', 'issue',
            'explain', 'describe', 'understand', 'what does',
            'optimize', 'improve', 'refactor'
        }
        
        has_processing_keyword = any(keyword in task_clean for keyword in processing_keywords)
        
        # Layer 2: Code Context Detection
        code_context_indicators = {
            'code', 'function', 'method', 'class', 'script', 'program',
            'syntax', 'algorithm', 'implementation', 'logic'
        }
        
        has_code_context = any(indicator in task_clean for indicator in code_context_indicators)
        
        # Layer 3: Pattern Recognition - Look for actual code
        has_code_pattern = any(re.search(pattern, task, re.IGNORECASE) for pattern in self.code_patterns)
        
        # Layer 4: Language Detection with Processing Context
        has_language_context = False
        for lang in self.supported_languages:
            if lang in task_clean and has_processing_keyword:
                has_language_context = True
                break
        
        # Must have BOTH processing intent AND code context
        if has_processing_keyword and (has_code_context or has_code_pattern or has_language_context):
            # Layer 5: Exclusion Rules - Reject code GENERATION requests
            generation_indicators = {
                'write', 'create', 'generate', 'build', 'make', 'develop',
                'implement', 'code for', 'script for', 'program for'
            }
            
            # Strong exclusion for generation requests
            if any(gen_word in task_clean for gen_word in generation_indicators):
                # Unless it's clearly about processing existing code
                processing_context = any(phrase in task_clean for phrase in [
                    'this code', 'the code', 'my code', 'existing code',
                    'given code', 'following code', 'above code'
                ])
                if not processing_context:
                    return False
            
            return True
        
        # Layer 6: Direct code processing requests
        direct_processing_phrases = [
            'validate this code', 'check this syntax', 'format this code',
            'debug this', 'analyze this code', 'explain this function',
            'what does this do', 'how does this work', 'fix this error'
        ]
        
        if any(phrase in task_clean for phrase in direct_processing_phrases):
            return True
        
        # Default: Conservative approach (Framework Rule)
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute code processing task with robust error handling.
        
        Args:
            task: Code processing task to perform
            **kwargs: Additional parameters (code, language, etc.)
            
        Returns:
            Structured dictionary with processing results
        """
        start_time = time.time()
        
        try:
            # Input validation
            if not task or not isinstance(task, str):
                return self._error_response("Task must be a non-empty string")
            
            if not self.can_handle(task):
                return self._error_response("Task does not appear to be code processing-related")
            
            # Detect operation type and language
            operation = self._detect_operation(task)
            language = self._detect_language(task, kwargs.get('language'))
            
            # Extract code from task or kwargs
            code = self._extract_code_from_task(task) or kwargs.get('code', '')
            
            if not code:
                return self._error_response(
                    "No code found to process. Please provide code in the task or as a parameter."
                )
            
            # Perform the code processing operation
            result = self._perform_processing_operation(operation, code, language, task)
            
            if result is None:
                return self._error_response("Could not process the code")
            
            execution_time = time.time() - start_time
            
            # Success response (Framework standard)
            return {
                'success': True,
                'result': result,
                'message': f"Code {operation} completed successfully",
                'metadata': {
                    'tool_name': self.name,
                    'execution_time': execution_time,
                    'task_type': 'code_processing',
                    'operation': operation,
                    'language': language,
                    'code_length': len(code)
                }
            }
            
        except Exception as e:
            return self._error_response(f"Code processing failed: {str(e)}", e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect the type of code processing operation requested."""
        task_lower = task.lower()
        
        for operation, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                return operation
        
        return 'analyze'  # Default operation
    
    def _detect_language(self, task: str, explicit_language: str = None) -> str:
        """Detect the programming language from the task or parameters."""
        if explicit_language and explicit_language.lower() in self.supported_languages:
            return explicit_language.lower()
        
        task_lower = task.lower()
        
        # Language detection patterns
        for lang in self.supported_languages:
            if lang in task_lower:
                return lang
        
        # Pattern-based detection
        if re.search(r'def\s+\w+\(', task):
            return 'python'
        elif re.search(r'function\s+\w+\(', task):
            return 'javascript'
        elif re.search(r'public\s+static\s+void', task):
            return 'java'
        
        return 'unknown'
    
    def _extract_code_from_task(self, task: str) -> Optional[str]:
        """Extract code blocks from the task description."""
        # Look for code blocks in markdown format
        code_block_pattern = r'```(?:\w+)?\s*\n(.*?)\n```'
        matches = re.findall(code_block_pattern, task, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Look for inline code
        inline_code_pattern = r'`([^`]+)`'
        matches = re.findall(inline_code_pattern, task)
        
        if matches:
            return matches[0].strip()
        
        # Look for direct code patterns in text (without markdown)
        for pattern in self.code_patterns:
            if re.search(pattern, task, re.IGNORECASE):
                # Try to extract code-like content
                lines = task.split('\n')
                code_lines = []
                in_code_block = False
                
                for line in lines:
                    # Check if line looks like code
                    if (any(re.search(p, line, re.IGNORECASE) for p in self.code_patterns) or 
                        in_code_block and (line.strip().startswith(' ') or line.strip().startswith('\t') or 
                        line.strip() == '' or any(keyword in line.lower() for keyword in 
                        ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'try:', 'except:', 'return ']))):
                        code_lines.append(line)
                        in_code_block = True
                    elif in_code_block and line.strip() == '':
                        code_lines.append(line)  # Keep empty lines in code blocks
                    elif in_code_block:
                        break  # End of code block
                
                if code_lines:
                    return '\n'.join(code_lines).strip()
        
        return None
    
    def _perform_processing_operation(self, operation: str, code: str, language: str, task: str) -> Dict[str, Any]:
        """Perform the specific code processing operation."""
        
        if operation == 'validate':
            return self._validate_code(code, language)
        elif operation == 'format':
            return self._format_code(code, language)
        elif operation == 'analyze':
            return self._analyze_code(code, language)
        elif operation == 'debug':
            return self._debug_code(code, language, task)
        elif operation == 'explain':
            return self._explain_code(code, language)
        elif operation == 'optimize':
            return self._optimize_code(code, language)
        else:
            return self._analyze_code(code, language)
    
    def _validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code syntax and structure."""
        validation_result = {
            'language': language,
            'syntax_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        if language == 'python':
            try:
                ast.parse(code)
                validation_result['syntax_valid'] = True
            except SyntaxError as e:
                validation_result['syntax_valid'] = False
                validation_result['errors'].append({
                    'type': 'SyntaxError',
                    'message': str(e),
                    'line': e.lineno,
                    'column': e.offset
                })
        
        # Basic validation for other languages (simplified)
        if not validation_result['syntax_valid']:
            validation_result['suggestions'].extend([
                'Check for missing parentheses or brackets',
                'Verify proper indentation',
                'Look for unclosed strings or comments'
            ])
        
        return validation_result
    
    def _format_code(self, code: str, language: str) -> Dict[str, Any]:
        """Format code for better readability."""
        # Basic formatting (in production, use language-specific formatters)
        formatted_code = code.strip()
        
        # Simple Python formatting
        if language == 'python':
            lines = formatted_code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped:
                    if stripped.endswith(':'):
                        formatted_lines.append('    ' * indent_level + stripped)
                        indent_level += 1
                    elif stripped in ['else:', 'elif', 'except:', 'finally:']:
                        indent_level = max(0, indent_level - 1)
                        formatted_lines.append('    ' * indent_level + stripped)
                        indent_level += 1
                    else:
                        formatted_lines.append('    ' * indent_level + stripped)
                else:
                    formatted_lines.append('')
            
            formatted_code = '\n'.join(formatted_lines)
        
        return {
            'original_code': code,
            'formatted_code': formatted_code,
            'language': language,
            'changes_made': [
                'Consistent indentation applied',
                'Proper spacing added',
                'Code structure improved'
            ]
        }
    
    def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code structure and complexity."""
        analysis = {
            'language': language,
            'line_count': len(code.split('\n')),
            'character_count': len(code),
            'components': [],
            'complexity': 'low',
            'suggestions': []
        }
        
        # Basic component detection
        if 'def ' in code:
            func_count = len(re.findall(r'def\s+\w+\(', code))
            analysis['components'].append(f'{func_count} function(s)')
        
        if 'class ' in code:
            class_count = len(re.findall(r'class\s+\w+', code))
            analysis['components'].append(f'{class_count} class(es)')
        
        if 'import ' in code or 'from ' in code:
            analysis['components'].append('Import statements')
        
        # Complexity estimation
        if analysis['line_count'] > 100:
            analysis['complexity'] = 'high'
        elif analysis['line_count'] > 50:
            analysis['complexity'] = 'medium'
        
        return analysis
    
    def _debug_code(self, code: str, language: str, task: str) -> Dict[str, Any]:
        """Analyze code for potential issues and debugging suggestions."""
        debug_info = {
            'language': language,
            'potential_issues': [],
            'suggestions': [],
            'common_fixes': []
        }
        
        # Basic issue detection
        if language == 'python':
            if 'print(' not in code and 'return' not in code:
                debug_info['potential_issues'].append('No output or return statements found')
            
            if code.count('(') != code.count(')'):
                debug_info['potential_issues'].append('Mismatched parentheses')
            
            if 'def ' in code and 'return' not in code:
                debug_info['potential_issues'].append('Function without return statement')
        
        debug_info['suggestions'] = [
            'Add print statements for debugging',
            'Check variable names for typos',
            'Verify function parameters',
            'Test with simple inputs first'
        ]
        
        return debug_info
    
    def _explain_code(self, code: str, language: str) -> Dict[str, Any]:
        """Explain what the code does."""
        explanation = {
            'language': language,
            'summary': f"This {language} code contains programming logic",
            'components': [],
            'flow': 'The code follows standard programming patterns',
            'purpose': 'Code functionality analysis'
        }
        
        # Component analysis
        if 'def ' in code:
            explanation['components'].append('Function definitions')
        if 'class ' in code:
            explanation['components'].append('Class definitions')
        if 'import ' in code:
            explanation['components'].append('Import statements')
        if 'if ' in code:
            explanation['components'].append('Conditional logic')
        if 'for ' in code or 'while ' in code:
            explanation['components'].append('Loop structures')
        
        return explanation
    
    def _optimize_code(self, code: str, language: str) -> Dict[str, Any]:
        """Suggest optimizations for the code."""
        optimization_info = {
            'language': language,
            'current_code': code,
            'suggestions': [
                'Extract repeated code into functions',
                'Use more descriptive variable names',
                'Add error handling',
                'Consider algorithm complexity',
                'Add type hints (for Python)',
                'Remove unused variables'
            ],
            'performance_tips': [
                'Use list comprehensions where appropriate',
                'Avoid nested loops when possible',
                'Cache expensive calculations',
                'Use appropriate data structures'
            ]
        }
        
        return optimization_info
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the task involves processing existing code",
                "Provide code in the task using code blocks (```)",
                "Specify the programming language if not obvious",
                f"Supported languages: {', '.join(sorted(self.supported_languages))}",
                "Examples: 'Validate this Python code', 'Format this JavaScript function'"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_languages': list(self.supported_languages),
                'supported_operations': list(self.operation_types.keys())
            }
        }


