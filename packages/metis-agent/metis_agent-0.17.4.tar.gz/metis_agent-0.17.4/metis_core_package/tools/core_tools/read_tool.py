#!/usr/bin/env python3
"""
ReadTool - Framework-Compliant File Reading Tool
Follows Metis Agent Tools Framework v2.0
"""

from typing import Dict, Any, Optional
from datetime import datetime
import os
import pathlib
from ..base import BaseTool
from ...utils.path_security import validate_secure_path, SecurityError


class ReadTool(BaseTool):
    """
    Production-ready file reading tool with intelligent file handling.
    
    This tool handles reading files from the filesystem with proper error handling,
    encoding detection, and security checks.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize read tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "ReadTool"  # MUST match class name exactly
        self.description = "Reads files from the filesystem with proper encoding and error handling"
        
        # Optional metadata
        self.version = "1.0.0"
        self.category = "core_tools"
        
        # Supported file types and encodings
        self.supported_encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        
        # File type detection patterns
        self.text_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml',
            '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.log',
            '.sql', '.sh', '.bat', '.ps1', '.java', '.c', '.cpp', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala'
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Intelligent file reading task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires file reading, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Direct read keywords
        read_keywords = {
            'read', 'open', 'view', 'show', 'display', 'get contents',
            'load', 'fetch', 'retrieve', 'examine', 'inspect'
        }
        
        has_read_keyword = any(keyword in task_clean for keyword in read_keywords)
        
        # Layer 2: File context indicators
        file_indicators = {
            'file', 'document', 'text', 'content', 'source', 'script',
            'config', 'log', 'data', '.txt', '.py', '.js', '.md'
        }
        
        has_file_context = any(indicator in task_clean for indicator in file_indicators)
        
        # Layer 3: Path-like patterns
        has_path_pattern = ('/' in task or '\\' in task or 
                          task_clean.startswith('c:') or 
                          any(ext in task_clean for ext in self.text_extensions))
        
        # Decision logic
        if has_read_keyword and has_file_context:
            return True
        elif has_read_keyword and has_path_pattern:
            return True
        elif 'read file' in task_clean or 'open file' in task_clean:
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute file reading task with robust error handling.
        
        Args:
            task: File reading task to perform
            **kwargs: Additional parameters (file_path, encoding, etc.)
            
        Returns:
            Structured dictionary with file contents and metadata
        """
        try:
            # Extract file path from task or kwargs
            file_path = self._extract_file_path(task, kwargs)
            
            if not file_path:
                return self._error_response("No file path found in task or parameters")
            
            # Validate and normalize path
            normalized_path = self._validate_and_normalize_path(file_path)
            
            # Check file existence and permissions
            if not os.path.exists(normalized_path):
                return self._error_response(f"File not found: {normalized_path}")
            
            if not os.path.isfile(normalized_path):
                return self._error_response(f"Path is not a file: {normalized_path}")
            
            if not os.access(normalized_path, os.R_OK):
                return self._error_response(f"No read permission for file: {normalized_path}")
            
            # Check file size
            file_size = os.path.getsize(normalized_path)
            if file_size > self.max_file_size:
                return self._error_response(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            
            # Determine encoding
            encoding = kwargs.get('encoding', 'utf-8')
            
            # Read file with proper encoding handling
            content, actual_encoding = self._read_file_with_encoding(normalized_path, encoding)
            
            # Get file metadata
            file_stats = os.stat(normalized_path)
            
            return {
                "success": True,
                "type": "read_response",
                "data": {
                    "content": content,
                    "file_path": normalized_path,
                    "encoding": actual_encoding,
                    "size_bytes": file_size,
                    "line_count": len(content.splitlines()) if content else 0,
                    "is_text_file": self._is_text_file(normalized_path)
                },
                "metadata": {
                    "tool_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "file_stats": {
                        "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                        "size": file_stats.st_size,
                        "permissions": oct(file_stats.st_mode)[-3:]
                    }
                }
            }
            
        except Exception as e:
            return self._error_response(f"File reading failed: {str(e)}", e)
    
    def _extract_file_path(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract file path from task or parameters."""
        # Check kwargs first
        if 'file_path' in kwargs:
            return kwargs['file_path']
        if 'path' in kwargs:
            return kwargs['path']
        if 'filename' in kwargs:
            return kwargs['filename']
        
        # Extract from task text
        import re
        
        # Look for quoted paths
        quoted_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'`([^`]+)`'
        ]
        
        for pattern in quoted_patterns:
            matches = re.findall(pattern, task)
            if matches:
                return matches[0]
        
        # Look for path-like patterns
        words = task.split()
        for word in words:
            if ('/' in word or '\\' in word or 
                any(word.lower().endswith(ext) for ext in self.text_extensions)):
                return word
        
        return None
    
    def _validate_and_normalize_path(self, file_path: str) -> str:
        """
        Validate and normalize file path with comprehensive security checks.
        
        This method now uses SecurePathValidator to prevent:
        - Directory traversal attacks (../, ..\)
        - Access to restricted system directories
        - Null byte injection
        - Shell injection patterns
        - Path length attacks
        """
        try:
            # Use secure path validation
            validated_path = validate_secure_path(file_path)
            return str(validated_path)
        except SecurityError as e:
            raise ValueError(f"Security validation failed: {e}")
        except Exception as e:
            raise ValueError(f"Path validation failed: {e}")
    
    def _read_file_with_encoding(self, file_path: str, preferred_encoding: str) -> tuple[str, str]:
        """Read file with encoding detection and fallback."""
        encodings_to_try = [preferred_encoding] + [enc for enc in self.supported_encodings if enc != preferred_encoding]
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, encoding
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise e
        
        # If all encodings fail, try binary mode and decode with errors='replace'
        try:
            with open(file_path, 'rb') as f:
                raw_content = f.read()
            content = raw_content.decode('utf-8', errors='replace')
            return content, 'utf-8 (with errors replaced)'
        except Exception as e:
            raise Exception(f"Could not read file with any encoding: {e}")
    
    def _is_text_file(self, file_path: str) -> bool:
        """Determine if file is likely a text file."""
        path = pathlib.Path(file_path)
        return path.suffix.lower() in self.text_extensions
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate"],
            "input_types": ["text", "file_path"],
            "output_types": ["structured_data", "file_content"],
            "estimated_execution_time": "<1s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": ["read", "open", "view", "load", "fetch"],
            "api_dependencies": [],
            "memory_usage": "low-moderate"
        }
    
    def get_examples(self) -> list:
        """Get example tasks that this tool can handle."""
        return [
            "Read the file config.json",
            "Open and show contents of /path/to/file.txt",
            "Load the Python script main.py",
            "View the contents of README.md",
            "Read file 'C:\\Users\\user\\document.txt'",
            "Show me the contents of the log file"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the file path is correct and accessible",
                "Check that the file exists and you have read permissions",
                "Verify the file is not too large (max 10MB)",
                "Try specifying the encoding if file has special characters",
                "Use absolute paths to avoid path resolution issues"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_encodings': self.supported_encodings,
                'max_file_size_mb': self.max_file_size // (1024 * 1024)
            }
        }
