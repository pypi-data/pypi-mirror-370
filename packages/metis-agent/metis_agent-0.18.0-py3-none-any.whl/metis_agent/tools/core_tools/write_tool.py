#!/usr/bin/env python3
"""
WriteTool - Framework-Compliant File Writing Tool
Follows Metis Agent Tools Framework v2.0
"""

from typing import Dict, Any, Optional
from datetime import datetime
import os
import pathlib
import tempfile
import shutil
from ..base import BaseTool
from ...utils.path_security import validate_secure_path, SecurityError


class WriteTool(BaseTool):
    """
    Production-ready file writing tool with safety features and backup support.
    
    This tool handles writing files to the filesystem with proper error handling,
    encoding support, backup creation, and security checks.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize write tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "WriteTool"  # MUST match class name exactly
        self.description = "Writes files to the filesystem with safety features and backup support"
        
        # Optional metadata
        self.version = "1.0.0"
        self.category = "core_tools"
        
        # Safety and configuration
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        self.create_backups = True
        self.backup_suffix = '.backup'
        
        # Supported encodings
        self.supported_encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
        
        # Write modes
        self.write_modes = {
            'write': 'w',      # Overwrite existing file
            'append': 'a',     # Append to existing file
            'create': 'x'      # Create new file (fail if exists)
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Intelligent file writing task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires file writing, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Direct write keywords
        write_keywords = {
            'write', 'save', 'create', 'store', 'output', 'export',
            'generate', 'produce', 'make', 'build', 'append'
        }
        
        has_write_keyword = any(keyword in task_clean for keyword in write_keywords)
        
        # Layer 2: File context indicators
        file_indicators = {
            'file', 'document', 'text', 'content', 'script', 'config',
            'log', 'data', 'to file', 'into file', '.txt', '.py', '.js', '.md'
        }
        
        has_file_context = any(indicator in task_clean for indicator in file_indicators)
        
        # Layer 3: Write-specific phrases
        write_phrases = [
            'write to', 'save to', 'create file', 'write file',
            'save file', 'output to', 'store in', 'append to'
        ]
        
        has_write_phrase = any(phrase in task_clean for phrase in write_phrases)
        
        # Decision logic
        if has_write_keyword and has_file_context:
            return True
        elif has_write_phrase:
            return True
        elif 'content' in task_clean and ('file' in task_clean or 'path' in task_clean):
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute file writing task with robust error handling and safety features.
        
        Args:
            task: File writing task to perform
            **kwargs: Additional parameters (file_path, content, mode, encoding, etc.)
            
        Returns:
            Structured dictionary with write results and metadata
        """
        try:
            # Extract parameters
            file_path = self._extract_file_path(task, kwargs)
            content = self._extract_content(task, kwargs)
            mode = kwargs.get('mode', 'write').lower()
            encoding = kwargs.get('encoding', 'utf-8')
            create_backup = kwargs.get('create_backup', self.create_backups)
            
            # Validate inputs
            if not file_path:
                return self._error_response("No file path found in task or parameters")
            
            if content is None:
                return self._error_response("No content found in task or parameters")
            
            if mode not in self.write_modes:
                return self._error_response(f"Invalid mode '{mode}'. Supported: {list(self.write_modes.keys())}")
            
            if encoding not in self.supported_encodings:
                return self._error_response(f"Unsupported encoding '{encoding}'. Supported: {self.supported_encodings}")
            
            # Validate and normalize path
            normalized_path = self._validate_and_normalize_path(file_path)
            
            # Check content size
            content_size = len(content.encode(encoding))
            if content_size > self.max_file_size:
                return self._error_response(f"Content too large: {content_size} bytes (max: {self.max_file_size})")
            
            # Check directory permissions
            parent_dir = os.path.dirname(normalized_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            if not os.access(parent_dir, os.W_OK):
                return self._error_response(f"No write permission for directory: {parent_dir}")
            
            # Handle existing file
            file_existed = os.path.exists(normalized_path)
            backup_path = None
            
            if file_existed:
                if mode == 'create':
                    return self._error_response(f"File already exists and mode is 'create': {normalized_path}")
                
                # Create backup if requested
                if create_backup and mode == 'write':
                    backup_path = self._create_backup(normalized_path)
            
            # Write the file
            write_mode = self.write_modes[mode]
            bytes_written = self._write_file(normalized_path, content, write_mode, encoding)
            
            # Get file metadata
            file_stats = os.stat(normalized_path)
            
            return {
                "success": True,
                "type": "write_response",
                "data": {
                    "file_path": normalized_path,
                    "bytes_written": bytes_written,
                    "encoding": encoding,
                    "mode": mode,
                    "file_existed": file_existed,
                    "backup_created": backup_path is not None,
                    "backup_path": backup_path,
                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                },
                "metadata": {
                    "tool_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "file_stats": {
                        "size": file_stats.st_size,
                        "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "permissions": oct(file_stats.st_mode)[-3:]
                    }
                }
            }
            
        except Exception as e:
            return self._error_response(f"File writing failed: {str(e)}", e)
    
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
        
        # Look for "to file" or "save to" patterns
        to_patterns = [
            r'(?:to|into|save to|write to|create)\s+(?:file\s+)?([^\s]+)',
            r'(?:file|path):\s*([^\s]+)'
        ]
        
        for pattern in to_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_content(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract content to write from task or parameters."""
        # Check kwargs first
        if 'content' in kwargs:
            return str(kwargs['content'])
        if 'data' in kwargs:
            return str(kwargs['data'])
        if 'text' in kwargs:
            return str(kwargs['text'])
        
        # Extract from task - look for content after keywords
        import re
        
        # Look for quoted content
        quoted_patterns = [
            r'content[:\s]+"([^"]+)"',
            r'text[:\s]+"([^"]+)"',
            r'write[:\s]+"([^"]+)"'
        ]
        
        for pattern in quoted_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0]
        
        # Look for content blocks
        if '```' in task:
            # Extract code blocks
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', task, re.DOTALL)
            if code_blocks:
                return code_blocks[0]
        
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
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of existing file."""
        backup_path = file_path + self.backup_suffix
        
        # If backup already exists, add timestamp
        if os.path.exists(backup_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.{timestamp}{self.backup_suffix}"
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _write_file(self, file_path: str, content: str, mode: str, encoding: str) -> int:
        """Write content to file and return bytes written."""
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        return len(content.encode(encoding))
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate"],
            "input_types": ["text", "file_path", "content"],
            "output_types": ["structured_data", "file_operation_result"],
            "estimated_execution_time": "<2s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": ["write", "save", "create", "store", "append"],
            "api_dependencies": [],
            "memory_usage": "low-moderate"
        }
    
    def get_examples(self) -> list:
        """Get example tasks that this tool can handle."""
        return [
            "Write 'Hello World' to file hello.txt",
            "Save the content to config.json",
            "Create a new file script.py with the code",
            "Append data to log.txt",
            "Write content to /path/to/output.txt",
            "Store the text in 'C:\\Users\\user\\document.txt'"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure you have write permissions for the target directory",
                "Check that the file path is valid and accessible",
                "Verify the content is not too large (max 50MB)",
                "Use supported encodings: " + ", ".join(self.supported_encodings),
                "Specify content using 'content' parameter or in task description",
                "Use mode='append' to add to existing files"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_modes': list(self.write_modes.keys()),
                'supported_encodings': self.supported_encodings,
                'max_file_size_mb': self.max_file_size // (1024 * 1024)
            }
        }
