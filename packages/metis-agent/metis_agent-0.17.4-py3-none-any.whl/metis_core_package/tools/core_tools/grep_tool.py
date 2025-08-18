#!/usr/bin/env python3
"""
GrepTool - Framework-Compliant Text Search Tool
Follows Metis Agent Tools Framework v2.0
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import re
import pathlib
import fnmatch
from ..base import BaseTool


class GrepTool(BaseTool):
    """
    Production-ready text search tool with regex support and file filtering.
    
    This tool searches for text patterns in files with support for regular expressions,
    recursive directory search, file pattern filtering, and comprehensive result formatting.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize grep tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "GrepTool"  # MUST match class name exactly
        self.description = "Searches for text patterns in files with regex support and filtering"
        
        # Optional metadata
        self.version = "1.0.0"
        self.category = "core_tools"
        
        # Configuration
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        self.max_results = 1000  # Maximum search results
        self.supported_encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
        
        # Binary file detection patterns
        self.binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
            '.zip', '.tar', '.gz', '.rar', '.7z', '.pdf'
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Intelligent text search task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires text searching, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Direct search keywords
        search_keywords = {
            'grep', 'search', 'find', 'look', 'locate', 'match', 'pattern'
        }
        
        has_search_keyword = any(keyword in task_clean for keyword in search_keywords)
        
        # Layer 2: File context indicators
        file_indicators = {
            'in file', 'in files', 'in directory', 'in folder',
            'text', 'content', 'line', 'lines'
        }
        
        has_file_context = any(indicator in task_clean for indicator in file_indicators)
        
        # Layer 3: Search-specific phrases
        search_phrases = [
            'search for', 'find text', 'look for', 'grep for',
            'search in', 'find in', 'locate in', 'match in'
        ]
        
        has_search_phrase = any(phrase in task_clean for phrase in search_phrases)
        
        # Layer 4: Pattern indicators
        has_quotes = '"' in task or "'" in task or '`' in task
        has_regex = any(char in task for char in ['*', '+', '?', '[', ']', '(', ')', '|'])
        
        # Decision logic
        if has_search_keyword and has_file_context:
            return True
        elif has_search_phrase:
            return True
        elif has_search_keyword and (has_quotes or has_regex):
            return True
        elif 'grep' in task_clean:  # Direct grep command
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute text search task with comprehensive pattern matching.
        
        Args:
            task: Text search task to perform
            **kwargs: Additional parameters (pattern, path, recursive, etc.)
            
        Returns:
            Structured dictionary with search results and metadata
        """
        try:
            # Extract parameters
            pattern = self._extract_pattern(task, kwargs)
            search_path = self._extract_search_path(task, kwargs)
            
            if not pattern:
                return self._error_response("No search pattern found in task or parameters")
            
            if not search_path:
                search_path = os.getcwd()  # Default to current directory
            
            # Extract options
            recursive = kwargs.get('recursive', True)
            case_sensitive = kwargs.get('case_sensitive', False)
            use_regex = kwargs.get('regex', False)
            file_pattern = kwargs.get('file_pattern', '*')
            max_results = min(kwargs.get('max_results', self.max_results), self.max_results)
            include_line_numbers = kwargs.get('include_line_numbers', True)
            
            # Validate search path
            search_path = self._validate_and_normalize_path(search_path)
            
            if not os.path.exists(search_path):
                return self._error_response(f"Search path does not exist: {search_path}")
            
            # Compile regex pattern
            regex_flags = 0 if case_sensitive else re.IGNORECASE
            
            try:
                if use_regex:
                    compiled_pattern = re.compile(pattern, regex_flags)
                else:
                    # Escape special regex characters for literal search
                    escaped_pattern = re.escape(pattern)
                    compiled_pattern = re.compile(escaped_pattern, regex_flags)
            except re.error as e:
                return self._error_response(f"Invalid regex pattern: {e}")
            
            # Perform search
            search_results = self._search_files(
                compiled_pattern, search_path, recursive, 
                file_pattern, max_results, include_line_numbers
            )
            
            # Format results
            total_matches = sum(len(result['matches']) for result in search_results)
            total_files = len(search_results)
            
            return {
                "success": True,
                "type": "grep_response",
                "data": {
                    "pattern": pattern,
                    "search_path": search_path,
                    "files": search_results,
                    "matches": search_results,  # For backward compatibility
                    "total_matches": total_matches,
                    "total_files_with_matches": total_files,
                    "search_options": {
                        "case_sensitive": case_sensitive,
                        "regex": use_regex,
                        "recursive": recursive,
                        "file_pattern": file_pattern,
                        "max_results": max_results
                    }
                },
                "metadata": {
                    "tool_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "search_stats": {
                        "files_searched": self._count_files_searched(search_path, recursive, file_pattern),
                        "pattern_type": "regex" if use_regex else "literal",
                        "truncated": total_matches >= max_results
                    }
                }
            }
            
        except Exception as e:
            return self._error_response(f"Search failed: {str(e)}", e)
    
    def _extract_pattern(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract search pattern from task or parameters."""
        # Check kwargs first
        if 'pattern' in kwargs:
            return kwargs['pattern']
        if 'search' in kwargs:
            return kwargs['search']
        if 'text' in kwargs:
            return kwargs['text']
        
        # Extract from task text
        task_clean = task.strip()
        
        # Look for quoted patterns
        quoted_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'`([^`]+)`'
        ]
        
        for pattern in quoted_patterns:
            matches = re.findall(pattern, task_clean)
            if matches:
                return matches[0]
        
        # Look for pattern after keywords
        pattern_keywords = [
            r'(?:grep|search|find|look)\s+(?:for\s+)?(.+?)(?:\s+in|\s+from|$)',
            r'pattern[:\s]+(.+?)(?:\s+in|\s+from|$)',
            r'text[:\s]+(.+?)(?:\s+in|\s+from|$)'
        ]
        
        for pattern in pattern_keywords:
            matches = re.findall(pattern, task_clean, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None
    
    def _extract_search_path(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract search path from task or parameters."""
        # Check kwargs first
        if 'path' in kwargs:
            return kwargs['path']
        if 'directory' in kwargs:
            return kwargs['directory']
        if 'file_path' in kwargs:
            return kwargs['file_path']
        
        # Extract from task text
        path_patterns = [
            r'in\s+(?:file\s+|directory\s+|folder\s+)?["\']?([^"\'\s]+)["\']?',
            r'from\s+(?:file\s+|directory\s+|folder\s+)?["\']?([^"\'\s]+)["\']?'
        ]
        
        for pattern in path_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _validate_and_normalize_path(self, search_path: str) -> str:
        """Validate and normalize search path."""
        path = pathlib.Path(search_path)
        
        if not path.is_absolute():
            path = pathlib.Path.cwd() / path
        
        return str(path.resolve())
    
    def _search_files(self, pattern: re.Pattern, search_path: str, 
                     recursive: bool, file_pattern: str, max_results: int,
                     include_line_numbers: bool) -> List[Dict[str, Any]]:
        """Search for pattern in files."""
        results = []
        total_matches = 0
        
        if os.path.isfile(search_path):
            # Single file search
            if self._should_process_file(search_path, file_pattern):
                file_result = self._search_in_file(pattern, search_path, include_line_numbers)
                if file_result['matches']:
                    results.append(file_result)
        else:
            # Directory search
            files_to_search = self._get_files_to_search(search_path, recursive, file_pattern)
            
            for file_path in files_to_search:
                if total_matches >= max_results:
                    break
                
                file_result = self._search_in_file(pattern, file_path, include_line_numbers)
                if file_result['matches']:
                    results.append(file_result)
                    total_matches += len(file_result['matches'])
        
        return results
    
    def _get_files_to_search(self, search_path: str, recursive: bool, file_pattern: str) -> List[str]:
        """Get list of files to search based on criteria."""
        files = []
        
        if recursive:
            for root, dirs, filenames in os.walk(search_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if self._should_process_file(file_path, file_pattern):
                        files.append(file_path)
        else:
            try:
                for item in os.listdir(search_path):
                    file_path = os.path.join(search_path, item)
                    if os.path.isfile(file_path) and self._should_process_file(file_path, file_pattern):
                        files.append(file_path)
            except PermissionError:
                pass
        
        return files
    
    def _should_process_file(self, file_path: str, file_pattern: str) -> bool:
        """Check if file should be processed based on pattern and type."""
        # Check file pattern
        if file_pattern != '*' and not fnmatch.fnmatch(os.path.basename(file_path), file_pattern):
            return False
        
        # Skip binary files
        if self._is_binary_file(file_path):
            return False
        
        # Check file size
        try:
            if os.path.getsize(file_path) > self.max_file_size:
                return False
        except OSError:
            return False
        
        return True
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Check if file is binary based on extension and content."""
        # Check extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in self.binary_extensions:
            return True
        
        # Check content (sample first 1024 bytes)
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:  # Null bytes indicate binary
                    return True
        except (OSError, PermissionError):
            return True  # Assume binary if can't read
        
        return False
    
    def _search_in_file(self, pattern: re.Pattern, file_path: str, 
                       include_line_numbers: bool = True) -> Dict[str, Any]:
        """Search for pattern in a single file."""
        matches = []
        
        try:
            # Try to read file with different encodings
            content = None
            encoding_used = None
            
            for encoding in self.supported_encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    encoding_used = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return {
                    'file_path': file_path,
                    'matches': [],
                    'error': 'Could not decode file with supported encodings'
                }
            
            # Search line by line
            lines = content.splitlines()
            
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    match_info = {
                        'line': line,
                        'line_number': line_num if include_line_numbers else None
                    }
                    matches.append(match_info)
            
            return {
                'file_path': file_path,
                'matches': matches,
                'encoding': encoding_used,
                'total_lines': len(lines)
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'matches': [],
                'error': str(e)
            }
    
    def _count_files_searched(self, search_path: str, recursive: bool, file_pattern: str) -> int:
        """Count total files that would be searched."""
        return len(self._get_files_to_search(search_path, recursive, file_pattern))
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text", "pattern", "file_path", "directory_path"],
            "output_types": ["structured_data", "search_results"],
            "estimated_execution_time": "<5s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": ["search", "find", "grep", "locate", "match"],
            "api_dependencies": [],
            "memory_usage": "low-moderate"
        }
    
    def get_examples(self) -> list:
        """Get example tasks that this tool can handle."""
        return [
            "Search for 'TODO' in all Python files",
            "Find 'import os' in file script.py",
            "Grep for pattern 'def.*test' in tests directory",
            "Look for 'error' in log files recursively",
            "Search for 'class MyClass' in project folder",
            "Find text 'Hello World' in current directory"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the search path exists and is accessible",
                "Check that the pattern is valid (use regex=True for regex patterns)",
                "Verify file permissions for the search directory",
                "Use quotes around patterns with spaces or special characters",
                "Try case_sensitive=False for case-insensitive search",
                f"Maximum file size: {self.max_file_size // (1024*1024)}MB",
                f"Maximum results: {self.max_results}"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_encodings': self.supported_encodings,
                'binary_extensions_skipped': list(self.binary_extensions)
            }
        }
