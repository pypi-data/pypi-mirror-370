"""
File System Tool for directory and file operations.

Provides comprehensive file system operations including:
- Reading and writing files
- Directory listing and navigation
- File search and pattern matching
- File metadata retrieval
- Safe file operations with backups
"""

import os
import shutil
import glob
import fnmatch
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base import BaseTool


class FileSystemTool(BaseTool):
    """Tool for file system operations and directory exploration."""
    
    def __init__(self, max_file_size: int = 1024 * 1024):  # 1MB default
        """Initialize FileSystemTool.
        
        Args:
            max_file_size: Maximum file size to read in bytes
        """
        self.max_file_size = max_file_size
    
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle the given task.
        
        Args:
            task: Task description
            
        Returns:
            Boolean indicating if the task can be handled
        """
        task_lower = task.lower().strip()
        
        # File and directory operations
        file_ops = ['read', 'write', 'create', 'delete', 'list', 'search', 'find']
        file_keywords = ['file', 'directory', 'folder', 'path', 'txt', 'py', 'json', 'csv']
        
        # Project generation keywords
        project_keywords = [
            'project structure', 'project requirements', 'filesystemtool',
            'create all', 'create files', 'create directories', 'project based on',
            'i need you to create', 'must create', 'write_file', 'create_directory'
        ]
        
        # Check if task mentions file operations
        for op in file_ops:
            if op in task_lower:
                return True
        
        # Check if task mentions file-related keywords
        for keyword in file_keywords:
            if keyword in task_lower:
                return True
                
        # Check if task mentions project generation keywords
        for keyword in project_keywords:
            if keyword in task_lower:
                return True
        
        return False
    
    def execute(self, task: str) -> Any:
        """Execute file system operations based on the task.
        
        Args:
            task: The task description
            
        Returns:
            Result of the file system operation
        """
        task_lower = task.lower()
        
        # Check if this is a complex project generation task
        if self._is_project_generation_task(task):
            return self._handle_project_generation(task)
        
        if 'list' in task_lower or 'ls' in task_lower:
            pattern = '*'
            if 'pattern' in task_lower:
                # Try to extract pattern from task
                words = task.split()
                for i, word in enumerate(words):
                    if word.lower() in ['pattern', 'matching'] and i + 1 < len(words):
                        pattern = words[i + 1]
                        break
            return self.list_files(pattern=pattern)
        
        elif 'read' in task_lower or 'cat' in task_lower:
            # Try to extract filename from task
            words = task.split()
            for word in words:
                if '.' in word and not word.startswith('.'):
                    return self.read_file(word)
            return {"error": "No filename specified in task"}
        
        elif 'tree' in task_lower:
            return self.get_tree()
        
        elif 'search' in task_lower or 'find' in task_lower:
            # Try to extract search term
            if 'for' in task_lower:
                parts = task_lower.split('for', 1)
                if len(parts) > 1:
                    search_term = parts[1].strip().strip('"\'')
                    return self.search_files(content=search_term)
            return {"error": "No search term specified"}
        
        elif 'write' in task_lower or 'create' in task_lower or 'add' in task_lower or 'modify' in task_lower:
            # Handle file writing operations with natural language parsing
            return self._handle_write_operation(task)
        
        else:
            # Default to listing files
            return self.list_files()
    
    def list_files(self, directory: str = ".", pattern: str = "*", show_hidden: bool = False, recursive: bool = False) -> Dict[str, Any]:
        """
        List files and directories.
        
        Args:
            directory: Directory to list (default: current directory)
            pattern: File pattern to match (default: all files)
            show_hidden: Include hidden files (default: False)
            recursive: List files recursively (default: False)
            
        Returns:
            Dictionary with files, directories, and metadata
        """
        try:
            dir_path = Path(directory).resolve()
            if not dir_path.exists():
                return {"error": f"Directory '{directory}' does not exist"}
            
            if not dir_path.is_dir():
                return {"error": f"'{directory}' is not a directory"}
            
            files = []
            directories = []
            
            # Get items based on recursive flag
            if recursive:
                items = dir_path.rglob(pattern)
            else:
                items = dir_path.glob(pattern)
            
            for item in items:
                # Skip hidden files if not requested
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                stat_info = item.stat()
                item_info = {
                    "name": item.name,
                    "path": str(item.relative_to(dir_path)),
                    "size": stat_info.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "permissions": oct(stat_info.st_mode)[-3:],
                    "is_directory": item.is_dir()
                }
                
                if item.is_file():
                    files.append(item_info)
                elif item.is_dir():
                    # Count contents for directories
                    try:
                        contents_count = len(list(item.iterdir()))
                        item_info["contents_count"] = contents_count
                    except PermissionError:
                        item_info["contents_count"] = "Permission denied"
                    directories.append(item_info)
            
            return {
                "success": True,
                "directory": str(dir_path),
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories)
            }
            
        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}
    
    def read_file(self, filepath: str, encoding: str = "utf-8", max_size: int = 1024*1024) -> Dict[str, Any]:
        """
        Read file contents with safety checks.
        
        Args:
            filepath: Path to the file to read
            encoding: File encoding (default: utf-8)
            max_size: Maximum file size to read in bytes (default: 1MB)
            
        Returns:
            Dictionary with file contents and metadata
        """
        try:
            file_path = Path(filepath).resolve()
            
            if not file_path.exists():
                return {"error": f"File '{filepath}' does not exist"}
            
            if not file_path.is_file():
                return {"error": f"'{filepath}' is not a file"}
            
            stat_info = file_path.stat()
            
            # Check file size
            if stat_info.st_size > max_size:
                return {
                    "error": f"File too large ({stat_info.st_size} bytes). Maximum size: {max_size} bytes",
                    "size": stat_info.st_size,
                    "max_size": max_size
                }
            
            # Try to read with specified encoding
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    
                return {
                    "success": True,
                    "filepath": str(file_path),
                    "content": content,
                    "encoding": encoding,
                    "size": stat_info.st_size,
                    "lines": len(content.splitlines()),
                    "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                }
                
            except UnicodeDecodeError:
                # Try binary mode for non-text files
                with open(file_path, 'rb') as f:
                    content = f.read()
                    
                return {
                    "success": True,
                    "filepath": str(file_path),
                    "content": f"<Binary file: {len(content)} bytes>",
                    "encoding": "binary",
                    "size": stat_info.st_size,
                    "is_binary": True,
                    "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                }
                
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    def write_file(self, filepath: str, content: str, encoding: str = "utf-8", backup: bool = True) -> Dict[str, Any]:
        """
        Write content to a file with optional backup.
        
        Args:
            filepath: Path to the file to write
            content: Content to write
            encoding: File encoding (default: utf-8)
            backup: Create backup if file exists (default: True)
            
        Returns:
            Dictionary with operation result
        """
        try:
            file_path = Path(filepath).resolve()
            
            # Create backup if file exists and backup is requested
            backup_path = None
            if file_path.exists() and backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
                shutil.copy2(file_path, backup_path)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the content
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            stat_info = file_path.stat()
            
            return {
                "success": True,
                "filepath": str(file_path),
                "size": stat_info.st_size,
                "lines": len(content.splitlines()),
                "encoding": encoding,
                "backup_created": str(backup_path) if backup_path else None,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}
    
    def search_files(self, pattern: str, directory: str = ".", content_search: bool = False, 
                    case_sensitive: bool = False, file_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search for files by name or content.
        
        Args:
            pattern: Search pattern (glob for names, regex for content)
            directory: Directory to search in (default: current)
            content_search: Search inside file contents (default: False)
            case_sensitive: Case sensitive search (default: False)
            file_types: List of file extensions to search (default: all)
            
        Returns:
            Dictionary with search results
        """
        try:
            dir_path = Path(directory).resolve()
            if not dir_path.exists() or not dir_path.is_dir():
                return {"error": f"Directory '{directory}' does not exist or is not a directory"}
            
            results = []
            
            if content_search:
                # Search file contents
                flags = 0 if case_sensitive else re.IGNORECASE
                regex = re.compile(pattern, flags)
                
                for file_path in dir_path.rglob("*"):
                    if not file_path.is_file():
                        continue
                    
                    # Filter by file types if specified
                    if file_types and file_path.suffix.lower() not in [f".{ext.lower()}" for ext in file_types]:
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            matches = list(regex.finditer(content))
                            
                            if matches:
                                # Get line numbers for matches
                                lines = content.splitlines()
                                match_info = []
                                
                                for match in matches:
                                    line_num = content[:match.start()].count('\n') + 1
                                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                                    
                                    match_info.append({
                                        "line": line_num,
                                        "content": line_content.strip(),
                                        "start": match.start(),
                                        "end": match.end(),
                                        "matched_text": match.group()
                                    })
                                
                                results.append({
                                    "file": str(file_path.relative_to(dir_path)),
                                    "matches": match_info,
                                    "match_count": len(matches)
                                })
                                
                    except (UnicodeDecodeError, PermissionError):
                        # Skip binary files or files we can't read
                        continue
            else:
                # Search by filename
                if not case_sensitive:
                    pattern = pattern.lower()
                
                for file_path in dir_path.rglob("*"):
                    filename = file_path.name
                    if not case_sensitive:
                        filename = filename.lower()
                    
                    if fnmatch.fnmatch(filename, pattern):
                        stat_info = file_path.stat()
                        results.append({
                            "file": str(file_path.relative_to(dir_path)),
                            "name": file_path.name,
                            "size": stat_info.st_size if file_path.is_file() else None,
                            "type": "directory" if file_path.is_dir() else "file",
                            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                        })
            
            return {
                "success": True,
                "pattern": pattern,
                "directory": str(dir_path),
                "search_type": "content" if content_search else "filename",
                "results": results,
                "total_matches": len(results)
            }
            
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
    
    def get_tree(self, directory: str = ".", max_depth: int = 3, show_hidden: bool = False) -> Dict[str, Any]:
        """
        Generate a tree structure of the directory.
        
        Args:
            directory: Directory to generate tree for
            max_depth: Maximum depth to traverse
            show_hidden: Include hidden files and directories
            
        Returns:
            Dictionary with tree structure
        """
        try:
            dir_path = Path(directory).resolve()
            if not dir_path.exists() or not dir_path.is_dir():
                return {"error": f"Directory '{directory}' does not exist or is not a directory"}
            
            def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
                if current_depth >= max_depth:
                    return {"name": path.name, "type": "directory", "truncated": True}
                
                try:
                    children = []
                    for item in sorted(path.iterdir()):
                        # Skip hidden files if not requested
                        if not show_hidden and item.name.startswith('.'):
                            continue
                        
                        if item.is_dir():
                            children.append(build_tree(item, current_depth + 1))
                        else:
                            stat_info = item.stat()
                            children.append({
                                "name": item.name,
                                "type": "file",
                                "size": stat_info.st_size
                            })
                    
                    return {
                        "name": path.name,
                        "type": "directory",
                        "children": children,
                        "child_count": len(children)
                    }
                    
                except PermissionError:
                    return {
                        "name": path.name,
                        "type": "directory",
                        "error": "Permission denied"
                    }
            
            tree = build_tree(dir_path)
            tree["name"] = str(dir_path)  # Use full path for root
            
            return {
                "success": True,
                "directory": str(dir_path),
                "max_depth": max_depth,
                "tree": tree
            }
            
        except Exception as e:
            return {"error": f"Failed to generate tree: {str(e)}"}
    
    def perform_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a file system operation with structured parameters.
        
        Args:
            action: The action to perform (list, read, write, search, tree)
            **kwargs: Action-specific parameters
            
        Returns:
            Dictionary with operation result
        """
        action_map = {
            "list": self.list_files,
            "read": self.read_file,
            "write": self.write_file,
            "search": self.search_files,
            "tree": self.get_tree
        }
        
        if action not in action_map:
            return {
                "error": f"Unknown action '{action}'. Available actions: {list(action_map.keys())}"
            }
        
        try:
            return action_map[action](**kwargs)
        except TypeError as e:
            return {"error": f"Invalid parameters for action '{action}': {str(e)}"}
    
    def _handle_write_operation(self, task: str) -> Dict[str, Any]:
        """Parse natural language write operations and execute them.
        
        Args:
            task: Natural language task description
            
        Returns:
            Result of the write operation
        """
        import re
        
        task_lower = task.lower().strip()
        
        # Try to extract filename from common patterns
        filename = None
        content = None
        
        # Pattern 1: "Create file X with content Y"
        file_pattern = r'(?:create|write|add to)\s+(?:file\s+)?([\w.-]+\.\w+)\s+with\s+(.+)'
        match = re.search(file_pattern, task_lower, re.IGNORECASE | re.DOTALL)
        if match:
            filename = match.group(1)
            content_desc = match.group(2)
            
        # Pattern 2: "Add function X to Y.py" 
        elif 'add' in task_lower and '.py' in task_lower:
            py_match = re.search(r'([\w.-]+\.py)', task_lower)
            if py_match:
                filename = py_match.group(1)
                if 'function' in task_lower:
                    func_match = re.search(r'(?:function|method)\s+([\w_]+)', task_lower)
                    if func_match:
                        func_name = func_match.group(1)
                        content = f"def {func_name}():\n    \"\"\"TODO: Implement {func_name}\"\"\"\n    pass\n"
        
        # Pattern 3: "Create X.py" (filename only)
        elif re.search(r'create\s+([\w.-]+\.[\w]+)', task_lower):
            filename_match = re.search(r'create\s+([\w.-]+\.[\w]+)', task_lower)
            if filename_match:
                filename = filename_match.group(1)
                ext = filename.split('.')[-1].lower()
                if ext == 'py':
                    content = f"\"\"\"\nGenerated Python file.\n\"\"\"\n\n# TODO: Add implementation\n"
                else:
                    content = f"# Generated file: {filename}\n# TODO: Add content\n"
        
        if filename:
            if not content:
                # Generate basic content based on file extension
                ext = filename.split('.')[-1].lower() if '.' in filename else 'txt'
                if ext == 'py':
                    content = f"\"\"\"\n{filename} - Generated by Metis Agent\n\"\"\"\n\n# TODO: Add implementation\n"
                else:
                    content = f"Generated by Metis Agent\nTODO: Add content for {filename}\n"
            
            # Use the existing write_file method
            result = self.write_file(filename, content)
            if result.get('success'):
                return {
                    "success": True,
                    "action": "file_created",
                    "filepath": filename,
                    "message": f"Successfully created {filename}",
                    "details": result
                }
            else:
                return result
        
        # If we can't parse the request, provide helpful guidance
        return {
            "error": "Could not parse write operation",
            "task_received": task,
            "guidance": "Try requests like: 'Create file test.py with sample code' or 'Add function calculate to utils.py'",
            "supported_patterns": [
                "Create file [filename] with [content description]",
                "Add function [name] to [filename]",
                "Create [filename]"
            ]
        }
    
    def _is_project_generation_task(self, task: str) -> bool:
        """Check if this is a complex project generation task requiring multiple files.
        
        Args:
            task: Task description
            
        Returns:
            True if this is a project generation task
        """
        task_lower = task.lower().strip()
        
        # Project generation indicators
        project_indicators = [
            'project requirements:', 'project name:', 'location:',
            'create all necessary files', 'create files and directories',
            'use the filesystemtool', 'write_file()', 'create_directory()',
            'project structure', 'complete project', 'project based on',
            'i need you to create a complete project'
        ]
        
        return any(indicator in task_lower for indicator in project_indicators)
    
    def _handle_project_generation(self, task: str) -> Dict[str, Any]:
        """Handle complex project generation by parsing the task and creating multiple files.
        
        Args:
            task: Project generation task description
            
        Returns:
            Result of project generation
        """
        import re
        import os
        from pathlib import Path
        
        created_files = []
        created_dirs = []
        errors = []
        
        try:
            # Extract project location if specified
            location_match = re.search(r'location:\s*([^\n]+)', task, re.IGNORECASE)
            base_path = Path.cwd()
            if location_match:
                base_path = Path(location_match.group(1).strip())
                
            # Look for specific file creation patterns in the task
            # Pattern: filename with content
            file_patterns = [
                # fs.write_file("path/file.ext", "content")
                r'fs\.write_file\(["\']([^"\')]+)["\'],\s*["\']([^"\')]*)["\']',
                r'write_file\(["\']([^"\')]+)["\'],\s*["\']([^"\')]*)["\']',
                # create_file "path" with "content"
                r'create[_ ]file[_ ]["\']([^"\')]+)["\'][_ ]with[_ ]["\']([^"\')]*)["\']',
                # **filename** content block
                r'\*\*`([^`]+)`\*\*[\s\S]*?```[\w]*\n([\s\S]*?)```'
            ]
            
            for pattern in file_patterns:
                matches = re.findall(pattern, task, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                for match in matches:
                    if len(match) >= 2:
                        filepath = match[0].strip()
                        content = match[1].strip() if match[1] else '# Generated file\n'
                        
                        # Clean up content (remove excessive newlines, etc.)
                        content = re.sub(r'\n{3,}', '\n\n', content)
                        
                        # Create directory structure if needed
                        full_path = base_path / filepath
                        if full_path.parent != base_path:
                            try:
                                full_path.parent.mkdir(parents=True, exist_ok=True)
                                if str(full_path.parent) not in created_dirs:
                                    created_dirs.append(str(full_path.parent))
                            except Exception as e:
                                errors.append(f"Failed to create directory {full_path.parent}: {e}")
                                continue
                        
                        # Create the file
                        try:
                            result = self.write_file(str(full_path), content)
                            if result.get('success'):
                                created_files.append(str(full_path))
                            else:
                                errors.append(f"Failed to create {filepath}: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            errors.append(f"Failed to create {filepath}: {e}")
            
            # Return comprehensive result
            return {
                "success": len(created_files) > 0,
                "action": "project_generation",
                "created_files": created_files,
                "created_directories": created_dirs,
                "errors": errors,
                "message": f"Project generation completed. Created {len(created_files)} files" + 
                          (f" and {len(created_dirs)} directories" if created_dirs else "") +
                          (f" with {len(errors)} errors" if errors else ""),
                "details": {
                    "files_created": len(created_files),
                    "directories_created": len(created_dirs),
                    "errors_encountered": len(errors)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Project generation failed: {e}",
                "created_files": created_files,
                "created_directories": created_dirs,
                "partial_errors": errors
            }
