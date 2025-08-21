"""
File System Tool - MCP-compliant file and directory operations.

Provides comprehensive file system operations including reading, writing,
listing, and searching files and directories.
"""

import os
import json
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional
import datetime
import re
from ..base import BaseTool
from ...utils.path_security import validate_secure_path, SecurityError


class FileSystemTool(BaseTool):
    """
    Tool for file system operations and directory exploration.
    
    This tool demonstrates MCP architecture:
    - Stateless operation
    - No LLM dependencies  
    - Structured input/output
    - Safe file operations
    """
    
    def __init__(self):
        """Initialize file system tool."""
        self.name = "File System"
        self.description = "Perform file and directory operations"
        self.max_file_size = 1024 * 1024  # 1MB default
        self.safe_extensions = {
            '.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', 
            '.csv', '.xml', '.html', '.css', '.sql', '.sh', '.bat'
        }
    
    def can_handle(self, task: str) -> bool:
        """Check if task is a file system operation."""
        if not task or not task.strip():
            return False
        
        task_lower = task.lower().strip()
        
        # File operations
        file_operations = [
            "read", "write", "create", "delete", "list", "search", "find",
            "ls", "cat", "tree", "mkdir", "rmdir", "copy", "move"
        ]
        
        # File-related keywords
        file_keywords = [
            "file", "directory", "folder", "path", "txt", "py", "json", 
            "csv", "yaml", "xml", "html", "css", "js", "md", "readme"
        ]
        
        # Check for file operations
        if any(op in task_lower for op in file_operations):
            return True
        
        # Check for file keywords
        if any(keyword in task_lower for keyword in file_keywords):
            return True
        
        # Check for file paths (contains . or /)
        if re.search(r'[./\\]', task) and not task.startswith('http'):
            return True
        
        return False
    
    def _validate_secure_path(self, path_str: str) -> Path:
        """
        Validate path using secure path validation.
        
        Args:
            path_str: The path string to validate
            
        Returns:
            Validated Path object
            
        Raises:
            SecurityError: If path is invalid or restricted
        """
        try:
            validated_path = validate_secure_path(path_str)
            return validated_path
        except SecurityError as e:
            raise SecurityError(f"Path security validation failed: {e}")
        except Exception as e:
            raise ValueError(f"Path validation failed: {e}")

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute file system operation."""
        if not task or not task.strip():
            return self._format_error_response(
                "Task cannot be empty",
                "INVALID_INPUT",
                ["Provide a file system operation request"]
            )
        
        try:
            task_lower = task.lower().strip()
            
            # Determine operation type
            if any(word in task_lower for word in ["list", "ls", "show files"]):
                return self._handle_list_operation(task, **kwargs)
            elif any(word in task_lower for word in ["read", "cat", "show content"]):
                return self._handle_read_operation(task, **kwargs)
            elif any(word in task_lower for word in ["write", "create file", "save"]):
                return self._handle_write_operation(task, **kwargs)
            elif any(word in task_lower for word in ["search", "find"]):
                return self._handle_search_operation(task, **kwargs)
            elif "tree" in task_lower:
                return self._handle_tree_operation(task, **kwargs)
            else:
                # Try to infer operation from context
                return self._handle_generic_operation(task, **kwargs)
                
        except SecurityError as e:
            return self._format_error_response(
                f"Security validation failed: {str(e)}",
                "SECURITY_ERROR",
                ["Path access denied for security reasons", "Use allowed directories only"]
            )
        except Exception as e:
            return self._format_error_response(
                f"File system operation failed: {str(e)}",
                "OPERATION_ERROR",
                ["Check file paths and permissions", "Verify operation syntax"]
            )
    
    def _handle_list_operation(self, task: str, **kwargs) -> Dict[str, Any]:
        """Handle directory listing operations."""
        directory = kwargs.get("directory", ".")
        pattern = kwargs.get("pattern", "*")
        show_hidden = kwargs.get("show_hidden", False)
        
        # Try to extract directory from task
        dir_match = re.search(r'list\s+([^\s]+)', task, re.IGNORECASE)
        if dir_match:
            directory = dir_match.group(1)
        
        try:
            path = self._validate_secure_path(directory)
            if not path.exists():
                return self._format_error_response(
                    f"Directory does not exist: {directory}",
                    "DIRECTORY_NOT_FOUND",
                    ["Check directory path", "Use absolute or relative path"]
                )
            
            if not path.is_dir():
                return self._format_error_response(
                    f"Path is not a directory: {directory}",
                    "NOT_A_DIRECTORY",
                    ["Specify a valid directory path"]
                )
            
            items = []
            for item in path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                if not fnmatch.fnmatch(item.name, pattern):
                    continue
                
                item_info = {
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                items.append(item_info)
            
            # Sort by type (directories first) then by name
            items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
            return self._format_success_response({
                "directory": str(path),
                "pattern": pattern,
                "items": items,
                "total_items": len(items)
            })
            
        except PermissionError:
            return self._format_error_response(
                f"Permission denied accessing: {directory}",
                "PERMISSION_DENIED",
                ["Check directory permissions", "Run with appropriate privileges"]
            )
    
    def _handle_read_operation(self, task: str, **kwargs) -> Dict[str, Any]:
        """Handle file reading operations."""
        filepath = kwargs.get("filepath") or kwargs.get("file")
        encoding = kwargs.get("encoding", "utf-8")
        max_size = kwargs.get("max_size", self.max_file_size)
        
        # Try to extract filepath from task
        if not filepath:
            file_match = re.search(r'read\s+([^\s]+)', task, re.IGNORECASE)
            if file_match:
                filepath = file_match.group(1)
            else:
                # Look for file extensions in the task
                ext_match = re.search(r'(\S+\.\w+)', task)
                if ext_match:
                    filepath = ext_match.group(1)
        
        if not filepath:
            return self._format_error_response(
                "No file path specified",
                "MISSING_FILEPATH",
                ["Specify a file path to read", "Use format: read filename.ext"]
            )
        
        try:
            path = self._validate_secure_path(filepath)
            if not path.exists():
                return self._format_error_response(
                    f"File does not exist: {filepath}",
                    "FILE_NOT_FOUND",
                    ["Check file path", "Verify file exists"]
                )
            
            if not path.is_file():
                return self._format_error_response(
                    f"Path is not a file: {filepath}",
                    "NOT_A_FILE",
                    ["Specify a valid file path"]
                )
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > max_size:
                return self._format_error_response(
                    f"File too large: {file_size} bytes (max: {max_size})",
                    "FILE_TOO_LARGE",
                    ["Use a smaller max_size parameter", "Read file in chunks"]
                )
            
            # Check if file extension is safe to read
            if path.suffix.lower() not in self.safe_extensions:
                return self._format_error_response(
                    f"Unsafe file type: {path.suffix}",
                    "UNSAFE_FILE_TYPE",
                    [f"Supported types: {', '.join(self.safe_extensions)}"]
                )
            
            # Read file content
            content = path.read_text(encoding=encoding)
            
            return self._format_success_response({
                "filepath": str(path),
                "content": content,
                "size": file_size,
                "encoding": encoding,
                "lines": len(content.splitlines()),
                "modified": datetime.datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            })
            
        except UnicodeDecodeError:
            return self._format_error_response(
                f"Cannot decode file with encoding: {encoding}",
                "ENCODING_ERROR",
                ["Try different encoding (e.g., 'latin-1', 'cp1252')", "File may be binary"]
            )
        except PermissionError:
            return self._format_error_response(
                f"Permission denied reading: {filepath}",
                "PERMISSION_DENIED",
                ["Check file permissions"]
            )
    
    def _handle_write_operation(self, task: str, **kwargs) -> Dict[str, Any]:
        """Handle file writing operations."""
        filepath = kwargs.get("filepath") or kwargs.get("file")
        content = kwargs.get("content", "")
        encoding = kwargs.get("encoding", "utf-8")
        create_dirs = kwargs.get("create_dirs", True)
        
        # Try to extract filepath and content from task
        if not filepath:
            write_match = re.search(r'write\s+([^\s]+)', task, re.IGNORECASE)
            if write_match:
                filepath = write_match.group(1)
        
        if not filepath:
            return self._format_error_response(
                "No file path specified",
                "MISSING_FILEPATH",
                ["Specify a file path to write", "Use format: write filename.ext"]
            )
        
        try:
            path = self._validate_secure_path(filepath)
            
            # Create parent directories if needed
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            path.write_text(content, encoding=encoding)
            
            return self._format_success_response({
                "filepath": str(path),
                "content_length": len(content),
                "encoding": encoding,
                "created": not path.existed_before if hasattr(path, 'existed_before') else True,
                "modified": datetime.datetime.now().isoformat()
            })
            
        except PermissionError:
            return self._format_error_response(
                f"Permission denied writing: {filepath}",
                "PERMISSION_DENIED",
                ["Check directory permissions", "Verify write access"]
            )
    
    def _handle_search_operation(self, task: str, **kwargs) -> Dict[str, Any]:
        """Handle file search operations."""
        pattern = kwargs.get("pattern", "*")
        directory = kwargs.get("directory", ".")
        content_search = kwargs.get("content_search", False)
        
        # Extract search pattern from task
        search_match = re.search(r'search\s+for\s+([^\s]+)', task, re.IGNORECASE)
        if search_match:
            pattern = search_match.group(1)
        
        try:
            path = Path(directory).resolve()
            if not path.exists() or not path.is_dir():
                return self._format_error_response(
                    f"Invalid search directory: {directory}",
                    "INVALID_DIRECTORY",
                    ["Specify a valid directory path"]
                )
            
            matches = []
            
            if content_search:
                # Search file contents
                for file_path in path.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in self.safe_extensions:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            if pattern.lower() in content.lower():
                                matches.append({
                                    "path": str(file_path),
                                    "type": "content_match",
                                    "size": file_path.stat().st_size
                                })
                        except (UnicodeDecodeError, PermissionError):
                            continue
            else:
                # Search filenames
                for file_path in path.rglob(pattern):
                    matches.append({
                        "path": str(file_path),
                        "type": "directory" if file_path.is_dir() else "file",
                        "size": file_path.stat().st_size if file_path.is_file() else None
                    })
            
            return self._format_success_response({
                "pattern": pattern,
                "directory": str(path),
                "search_type": "content" if content_search else "filename",
                "matches": matches,
                "total_matches": len(matches)
            })
            
        except Exception as e:
            return self._format_error_response(
                f"Search failed: {str(e)}",
                "SEARCH_ERROR",
                ["Check search pattern and directory"]
            )
    
    def _handle_tree_operation(self, task: str, **kwargs) -> Dict[str, Any]:
        """Handle directory tree operations."""
        directory = kwargs.get("directory", ".")
        max_depth = kwargs.get("max_depth", 3)
        
        try:
            path = Path(directory).resolve()
            if not path.exists() or not path.is_dir():
                return self._format_error_response(
                    f"Invalid directory: {directory}",
                    "INVALID_DIRECTORY",
                    ["Specify a valid directory path"]
                )
            
            def build_tree(current_path: Path, current_depth: int = 0) -> Dict[str, Any]:
                if current_depth >= max_depth:
                    return {"name": current_path.name, "type": "directory", "truncated": True}
                
                tree_node = {
                    "name": current_path.name,
                    "path": str(current_path),
                    "type": "directory",
                    "children": []
                }
                
                try:
                    for item in sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                        if item.name.startswith('.'):
                            continue
                        
                        if item.is_dir():
                            tree_node["children"].append(build_tree(item, current_depth + 1))
                        else:
                            tree_node["children"].append({
                                "name": item.name,
                                "path": str(item),
                                "type": "file",
                                "size": item.stat().st_size
                            })
                except PermissionError:
                    tree_node["error"] = "Permission denied"
                
                return tree_node
            
            tree = build_tree(path)
            
            return self._format_success_response({
                "directory": str(path),
                "max_depth": max_depth,
                "tree": tree
            })
            
        except Exception as e:
            return self._format_error_response(
                f"Tree generation failed: {str(e)}",
                "TREE_ERROR",
                ["Check directory path and permissions"]
            )
    
    def _handle_generic_operation(self, task: str, **kwargs) -> Dict[str, Any]:
        """Handle generic file system operations."""
        # Try to determine what the user wants to do
        task_lower = task.lower()
        
        if "current directory" in task_lower or "pwd" in task_lower:
            return self._format_success_response({
                "current_directory": str(Path.cwd()),
                "operation": "get_current_directory"
            })
        
        # Default to listing current directory
        return self._handle_list_operation("list current directory", **kwargs)
    
    def get_examples(self) -> List[str]:
        """Return example file system operations."""
        return [
            "list files in current directory",
            "read config.json",
            "write hello.txt with content",
            "search for *.py files",
            "show directory tree",
            "find files containing 'import'",
            "create new file data.csv"
        ]
    
    def _format_success_response(self, data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a successful response."""
        return {
            "success": True,
            "type": "filesystem_response",
            "data": data,
            "metadata": {
                "tool_name": self.__class__.__name__,
                "timestamp": datetime.datetime.now().isoformat(),
                **(metadata or {})
            }
        }
    
    def _format_error_response(self, error: str, error_code: str, suggestions: List[str] = None) -> Dict[str, Any]:
        """Format an error response."""
        return {
            "success": False,
            "error": error,
            "error_code": error_code,
            "suggestions": suggestions or [],
            "metadata": {
                "tool_name": self.__class__.__name__,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
        
    def __call__(self, arguments: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make the tool callable for UnifiedOrchestrator.
        
        This method implements the callable interface required by the UnifiedOrchestrator.
        
        Args:
            arguments: Dictionary of arguments for tool execution
            context: Optional execution context information
            
        Returns:
            Dictionary with execution results
        """
        task = arguments.get('task', '')
        if not task:
            task = arguments.get('query', '')
        
        # Extract any additional arguments
        kwargs = {}
        for key, value in arguments.items():
            if key not in ['task', 'query']:
                kwargs[key] = value
        
        # Execute the tool with the provided task
        result = self.execute(task, **kwargs)
        
        # Add execution metadata
        if context and isinstance(context, dict):
            result.setdefault('metadata', {}).update({
                'execution_context': context,
                'execution_timestamp': datetime.datetime.now().isoformat()
            })
            
        return result
