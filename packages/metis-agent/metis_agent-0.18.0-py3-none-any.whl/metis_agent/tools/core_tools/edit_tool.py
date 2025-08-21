#!/usr/bin/env python3
"""
EditTool - Framework-Compliant File Editing Tool
Follows Metis Agent Tools Framework v2.0
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import os
import pathlib
import shutil
import re
from ..base import BaseTool


class EditTool(BaseTool):
    """
    Production-ready file editing tool with precise line-based modifications.
    
    This tool handles editing files with line-based operations, backup creation,
    and various editing modes including replace, insert, delete, and append.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize edit tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "EditTool"  # MUST match class name exactly
        self.description = "Edits files with precise line-based modifications and backup support"
        
        # Optional metadata
        self.version = "1.0.0"
        self.category = "core_tools"
        
        # Safety and configuration
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        self.create_backups = True
        self.backup_suffix = '.backup'
        
        # Supported encodings
        self.supported_encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
        
        # Edit operations
        self.edit_operations = {
            'replace': 'Replace specific lines or text',
            'insert': 'Insert new lines at specific position',
            'delete': 'Delete specific lines',
            'append': 'Append lines to end of file',
            'prepend': 'Insert lines at beginning of file',
            'substitute': 'Find and replace text patterns'
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Intelligent file editing task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires file editing, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Direct edit keywords
        edit_keywords = {
            'edit', 'modify', 'change', 'update', 'replace', 'insert',
            'delete', 'remove', 'append', 'prepend', 'substitute'
        }
        
        has_edit_keyword = any(keyword in task_clean for keyword in edit_keywords)
        
        # Layer 2: File context indicators
        file_indicators = {
            'file', 'line', 'lines', 'text', 'content', 'in file',
            'at line', 'line number', 'replace in', 'modify file'
        }
        
        has_file_context = any(indicator in task_clean for indicator in file_indicators)
        
        # Layer 3: Edit-specific phrases
        edit_phrases = [
            'edit file', 'modify file', 'change line', 'replace line',
            'insert line', 'delete line', 'update file', 'edit line'
        ]
        
        has_edit_phrase = any(phrase in task_clean for phrase in edit_phrases)
        
        # Layer 4: Line number patterns
        has_line_numbers = bool(re.search(r'line\s+\d+', task_clean))
        
        # Decision logic
        if has_edit_keyword and has_file_context:
            return True
        elif has_edit_phrase:
            return True
        elif has_edit_keyword and has_line_numbers:
            return True
        elif 'sed' in task_clean or 'awk' in task_clean:  # Unix editing commands
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute file editing task with robust error handling and safety features.
        
        Args:
            task: File editing task to perform
            **kwargs: Additional parameters (file_path, operation, content, etc.)
            
        Returns:
            Structured dictionary with edit results and metadata
        """
        try:
            # Extract parameters
            file_path = self._extract_file_path(task, kwargs)
            operation = self._extract_operation(task, kwargs)
            
            if not file_path:
                return self._error_response("No file path found in task or parameters")
            
            if not operation:
                return self._error_response("No edit operation found in task or parameters")
            
            # Validate and normalize path
            normalized_path = self._validate_and_normalize_path(file_path)
            
            # Check file existence and permissions
            if not os.path.exists(normalized_path):
                return self._error_response(f"File not found: {normalized_path}")
            
            if not os.path.isfile(normalized_path):
                return self._error_response(f"Path is not a file: {normalized_path}")
            
            if not os.access(normalized_path, os.R_OK | os.W_OK):
                return self._error_response(f"No read/write permission for file: {normalized_path}")
            
            # Check file size
            file_size = os.path.getsize(normalized_path)
            if file_size > self.max_file_size:
                return self._error_response(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            
            # Create backup
            backup_path = None
            if self.create_backups:
                backup_path = self._create_backup(normalized_path)
            
            # Read current file content
            original_content, encoding = self._read_file_with_encoding(normalized_path)
            original_lines = original_content.splitlines()
            
            # Perform edit operation
            edit_result = self._perform_edit_operation(
                operation, original_lines, task, kwargs
            )
            
            if not edit_result['success']:
                return self._error_response(edit_result['error'])
            
            # Write modified content
            modified_lines = edit_result['modified_lines']
            modified_content = '\n'.join(modified_lines)
            
            self._write_file(normalized_path, modified_content, encoding)
            
            # Calculate changes
            changes = self._calculate_changes(original_lines, modified_lines)
            
            return {
                "success": True,
                "type": "edit_response",
                "data": {
                    "file_path": normalized_path,
                    "operation": operation,
                    "backup_created": backup_path is not None,
                    "backup_path": backup_path,
                    "encoding": encoding,
                    "changes": changes,
                    "lines_before": len(original_lines),
                    "lines_after": len(modified_lines),
                    "preview": {
                        "before": original_lines[:5] if original_lines else [],
                        "after": modified_lines[:5] if modified_lines else []
                    }
                },
                "metadata": {
                    "tool_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "file_stats": {
                        "size_before": len(original_content),
                        "size_after": len(modified_content),
                        "modified_time": datetime.now().isoformat()
                    }
                }
            }
            
        except Exception as e:
            return self._error_response(f"File editing failed: {str(e)}", e)
    
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
                # Check if it looks like a file path
                candidate = matches[0]
                if ('/' in candidate or '\\' in candidate or 
                    '.' in candidate or candidate.endswith(('.py', '.txt', '.js', '.md'))):
                    return candidate
        
        # Look for file patterns
        file_patterns = [
            r'(?:file|in)\s+([^\s]+\.[a-zA-Z0-9]+)',
            r'([^\s]+\.[a-zA-Z0-9]+)',
            r'(?:edit|modify)\s+([^\s]+)'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, task)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_operation(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract edit operation from task or parameters."""
        # Check kwargs first
        if 'operation' in kwargs:
            return kwargs['operation']
        if 'op' in kwargs:
            return kwargs['op']
        
        task_lower = task.lower()
        
        # Check for operation keywords
        for operation in self.edit_operations.keys():
            if operation in task_lower:
                return operation
        
        # Infer operation from context
        if 'line' in task_lower and any(word in task_lower for word in ['change', 'modify', 'update']):
            return 'replace'
        elif 'add' in task_lower or 'insert' in task_lower:
            return 'insert'
        elif 'remove' in task_lower or 'delete' in task_lower:
            return 'delete'
        elif 'end' in task_lower or 'bottom' in task_lower:
            return 'append'
        elif 'beginning' in task_lower or 'top' in task_lower:
            return 'prepend'
        elif 'find' in task_lower and 'replace' in task_lower:
            return 'substitute'
        
        return 'replace'  # Default operation
    
    def _perform_edit_operation(self, operation: str, lines: List[str], 
                               task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the specified edit operation."""
        try:
            if operation == 'replace':
                return self._replace_operation(lines, task, kwargs)
            elif operation == 'insert':
                return self._insert_operation(lines, task, kwargs)
            elif operation == 'delete':
                return self._delete_operation(lines, task, kwargs)
            elif operation == 'append':
                return self._append_operation(lines, task, kwargs)
            elif operation == 'prepend':
                return self._prepend_operation(lines, task, kwargs)
            elif operation == 'substitute':
                return self._substitute_operation(lines, task, kwargs)
            else:
                return {'success': False, 'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'success': False, 'error': f'Operation failed: {str(e)}'}
    
    def _replace_operation(self, lines: List[str], task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Replace specific lines or content."""
        line_number = self._extract_line_number(task, kwargs)
        new_content = self._extract_new_content(task, kwargs)
        
        if line_number is None:
            return {'success': False, 'error': 'No line number specified for replace operation'}
        
        if new_content is None:
            return {'success': False, 'error': 'No new content specified for replace operation'}
        
        if line_number < 1 or line_number > len(lines):
            return {'success': False, 'error': f'Line number {line_number} out of range (1-{len(lines)})'}
        
        modified_lines = lines.copy()
        modified_lines[line_number - 1] = new_content
        
        return {'success': True, 'modified_lines': modified_lines}
    
    def _insert_operation(self, lines: List[str], task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Insert new lines at specific position."""
        line_number = self._extract_line_number(task, kwargs)
        new_content = self._extract_new_content(task, kwargs)
        
        if line_number is None:
            line_number = len(lines) + 1  # Default to end
        
        if new_content is None:
            return {'success': False, 'error': 'No content specified for insert operation'}
        
        if line_number < 1 or line_number > len(lines) + 1:
            return {'success': False, 'error': f'Line number {line_number} out of range (1-{len(lines) + 1})'}
        
        modified_lines = lines.copy()
        modified_lines.insert(line_number - 1, new_content)
        
        return {'success': True, 'modified_lines': modified_lines}
    
    def _delete_operation(self, lines: List[str], task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Delete specific lines."""
        line_number = self._extract_line_number(task, kwargs)
        
        if line_number is None:
            return {'success': False, 'error': 'No line number specified for delete operation'}
        
        if line_number < 1 or line_number > len(lines):
            return {'success': False, 'error': f'Line number {line_number} out of range (1-{len(lines)})'}
        
        modified_lines = lines.copy()
        del modified_lines[line_number - 1]
        
        return {'success': True, 'modified_lines': modified_lines}
    
    def _append_operation(self, lines: List[str], task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Append lines to end of file."""
        new_content = self._extract_new_content(task, kwargs)
        
        if new_content is None:
            return {'success': False, 'error': 'No content specified for append operation'}
        
        modified_lines = lines.copy()
        modified_lines.append(new_content)
        
        return {'success': True, 'modified_lines': modified_lines}
    
    def _prepend_operation(self, lines: List[str], task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Insert lines at beginning of file."""
        new_content = self._extract_new_content(task, kwargs)
        
        if new_content is None:
            return {'success': False, 'error': 'No content specified for prepend operation'}
        
        modified_lines = [new_content] + lines
        
        return {'success': True, 'modified_lines': modified_lines}
    
    def _substitute_operation(self, lines: List[str], task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Find and replace text patterns."""
        find_text = kwargs.get('find', self._extract_find_text(task))
        replace_text = kwargs.get('replace', self._extract_replace_text(task))
        
        if find_text is None:
            return {'success': False, 'error': 'No find text specified for substitute operation'}
        
        if replace_text is None:
            replace_text = ''  # Default to empty string
        
        modified_lines = []
        for line in lines:
            modified_line = line.replace(find_text, replace_text)
            modified_lines.append(modified_line)
        
        return {'success': True, 'modified_lines': modified_lines}
    
    def _extract_line_number(self, task: str, kwargs: Dict[str, Any]) -> Optional[int]:
        """Extract line number from task or parameters."""
        if 'line_number' in kwargs:
            return int(kwargs['line_number'])
        if 'line' in kwargs:
            return int(kwargs['line'])
        
        # Extract from task text
        import re
        line_patterns = [
            r'line\s+(\d+)',
            r'at\s+line\s+(\d+)',
            r'line\s*:\s*(\d+)',
            r'(\d+)\s*:'
        ]
        
        for pattern in line_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return int(matches[0])
        
        return None
    
    def _extract_new_content(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract new content from task or parameters."""
        # Prioritize explicitly provided content parameters
        if 'content' in kwargs and kwargs['content'] and kwargs['content'].strip():
            return kwargs['content']
        if 'text' in kwargs and kwargs['text'] and kwargs['text'].strip():
            return kwargs['text']
        if 'new_content' in kwargs and kwargs['new_content'] and kwargs['new_content'].strip():
            return kwargs['new_content']
        
        # Extract from task - look for quoted content
        import re
        quoted_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'`([^`]+)`'
        ]
        
        for pattern in quoted_patterns:
            matches = re.findall(pattern, task)
            if matches:
                return matches[-1]  # Take the last match as new content
        
        return None
    
    def _extract_find_text(self, task: str) -> Optional[str]:
        """Extract find text for substitute operation."""
        import re
        patterns = [
            r'find\s+"([^"]+)"',
            r"find\s+'([^']+)'",
            r'replace\s+"([^"]+)"\s+with',
            r"replace\s+'([^']+)'\s+with"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_replace_text(self, task: str) -> Optional[str]:
        """Extract replace text for substitute operation."""
        import re
        patterns = [
            r'with\s+"([^"]+)"',
            r"with\s+'([^']+)'",
            r'replace\s+.+\s+with\s+"([^"]+)"',
            r"replace\s+.+\s+with\s+'([^']+)'"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _validate_and_normalize_path(self, file_path: str) -> str:
        """Validate and normalize file path."""
        path = pathlib.Path(file_path)
        
        if not path.is_absolute():
            path = pathlib.Path.cwd() / path
        
        return str(path.resolve())
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of existing file."""
        backup_path = file_path + self.backup_suffix
        
        if os.path.exists(backup_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.{timestamp}{self.backup_suffix}"
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _read_file_with_encoding(self, file_path: str) -> Tuple[str, str]:
        """Read file with encoding detection."""
        for encoding in self.supported_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, encoding
            except UnicodeDecodeError:
                continue
        
        # Fallback with error replacement
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return content, 'utf-8 (with errors replaced)'
    
    def _write_file(self, file_path: str, content: str, encoding: str):
        """Write content to file."""
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    def _calculate_changes(self, original_lines: List[str], modified_lines: List[str]) -> Dict[str, Any]:
        """Calculate changes between original and modified content."""
        return {
            'lines_added': len(modified_lines) - len(original_lines),
            'lines_removed': max(0, len(original_lines) - len(modified_lines)),
            'total_changes': abs(len(modified_lines) - len(original_lines))
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text", "file_path", "line_number"],
            "output_types": ["structured_data", "file_modification_result"],
            "estimated_execution_time": "<2s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": False,  # File editing is not concurrent safe
            "resource_intensive": False,
            "supported_intents": ["edit", "modify", "change", "update", "replace"],
            "api_dependencies": [],
            "memory_usage": "low-moderate"
        }
    
    def get_examples(self) -> list:
        """Get example tasks that this tool can handle."""
        return [
            "Edit file config.py and replace line 5 with 'DEBUG = True'",
            "Insert 'import os' at line 1 in script.py",
            "Delete line 10 from data.txt",
            "Append 'End of file' to log.txt",
            "Replace 'old_value' with 'new_value' in settings.json",
            "Modify file.py: change line 3 to 'print(\"Hello World\")'"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the file exists and you have read/write permissions",
                "Check that line numbers are within valid range (1-based)",
                "Specify content for insert/replace operations",
                "Use quotes around content with spaces or special characters",
                "Backup files are created automatically for safety",
                f"Maximum file size: {self.max_file_size // (1024*1024)}MB"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_operations': list(self.edit_operations.keys()),
                'supported_encodings': self.supported_encodings,
                'creates_backups': self.create_backups
            }
        }
