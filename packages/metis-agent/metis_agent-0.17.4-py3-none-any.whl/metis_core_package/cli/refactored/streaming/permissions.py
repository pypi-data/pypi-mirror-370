"""
Permission management for streaming operations.

Handles user permissions for file creation, modification, and other operations.
"""
import os
from typing import Dict, Any, Set


class PermissionManager:
    """Manages permissions for streaming operations."""
    
    def __init__(self, interface):
        """Initialize with reference to main interface."""
        self.interface = interface
        self.granted_permissions: Set[str] = set()
        self.denied_permissions: Set[str] = set()
        self.permission_cache: Dict[str, bool] = {}
    
    def get_write_permission(self, filename: str, content: str) -> bool:
        """
        Get permission to write/create a file.
        
        Args:
            filename: Name of file to create/modify
            content: Content to write
            
        Returns:
            True if permission granted
        """
        if not filename:
            return False
        
        # Check cache first
        cache_key = f"write:{filename}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
        
        # Determine if this is a create or modify operation
        full_path = self._get_full_path(filename)
        is_existing = os.path.exists(full_path)
        
        # Get permission based on confirmation level
        permission = self._request_permission(
            filename, content, 'modify' if is_existing else 'create'
        )
        
        # Cache the result
        self.permission_cache[cache_key] = permission
        
        if permission:
            self.granted_permissions.add(filename)
        else:
            self.denied_permissions.add(filename)
        
        return permission
    
    def get_edit_permission(self, filename: str, operation_type: str, 
                           instructions: str = "") -> bool:
        """
        Get permission to edit a file.
        
        Args:
            filename: Name of file to edit
            operation_type: Type of edit (replace, append, insert, etc.)
            instructions: Edit instructions
            
        Returns:
            True if permission granted
        """
        if not filename:
            return False
        
        cache_key = f"edit:{filename}:{operation_type}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
        
        # Get permission
        permission = self._request_edit_permission(filename, operation_type, instructions)
        
        # Cache the result
        self.permission_cache[cache_key] = permission
        
        return permission
    
    def _request_permission(self, filename: str, content: str, 
                           operation: str) -> bool:
        """
        Request permission from user based on confirmation level.
        
        Args:
            filename: Filename
            content: File content
            operation: Operation type (create/modify)
            
        Returns:
            True if permission granted
        """
        confirmation_level = self.interface.confirmation_level
        
        # Auto-approve in minimal confirmation mode
        if confirmation_level == 'minimal':
            return True
        
        # Auto-approve for certain safe operations
        if self._is_safe_operation(filename, content, operation):
            if confirmation_level != 'detailed':
                return True
        
        # Check for dangerous operations
        risk_level = self._assess_risk_level(filename, content, operation)
        
        if risk_level == 'low' and confirmation_level == 'normal':
            return True
        
        # Request user confirmation
        return self._prompt_user_confirmation(filename, content, operation, risk_level)
    
    def _request_edit_permission(self, filename: str, operation_type: str, 
                                instructions: str) -> bool:
        """Request permission for file editing operations."""
        confirmation_level = self.interface.confirmation_level
        
        # Auto-approve safe edits in minimal mode
        if confirmation_level == 'minimal' and self._is_safe_edit(operation_type):
            return True
        
        # Assess risk
        risk_level = self._assess_edit_risk(filename, operation_type, instructions)
        
        if risk_level == 'low' and confirmation_level == 'normal':
            return True
        
        return self._prompt_edit_confirmation(filename, operation_type, instructions, risk_level)
    
    def _is_safe_operation(self, filename: str, content: str, operation: str) -> bool:
        """Check if operation is considered safe."""
        # Consider operations safe if:
        # 1. Creating new files (not modifying existing)
        # 2. Working with common development file types
        # 3. Content appears to be code/documentation
        
        if operation == 'create':
            return True
        
        safe_extensions = {'.py', '.js', '.md', '.txt', '.json', '.yaml', '.yml'}
        if any(filename.endswith(ext) for ext in safe_extensions):
            return True
        
        # Check if content looks like code
        if self._looks_like_code(content):
            return True
        
        return False
    
    def _is_safe_edit(self, operation_type: str) -> bool:
        """Check if edit operation is safe."""
        safe_operations = {'append', 'insert', 'format', 'comment'}
        return operation_type in safe_operations
    
    def _assess_risk_level(self, filename: str, content: str, operation: str) -> str:
        """Assess risk level of operation."""
        risk_indicators = {
            'high': [
                'rm -rf', 'del /s', 'format c:', 'sudo', 'chmod 777',
                'DROP TABLE', 'DELETE FROM', 'TRUNCATE',
                'exec(', 'eval(', '__import__', 'subprocess',
                'os.system', 'shell=True'
            ],
            'medium': [
                'import os', 'import subprocess', 'import sys',
                'open(', 'write(', 'file(', 'input(',
                'password', 'secret', 'token', 'api_key'
            ]
        }
        
        content_lower = content.lower()
        
        # Check for high risk indicators
        if any(indicator in content_lower for indicator in risk_indicators['high']):
            return 'high'
        
        # Check for medium risk indicators
        if any(indicator in content_lower for indicator in risk_indicators['medium']):
            return 'medium'
        
        # Check if modifying system files
        if self._is_system_file(filename):
            return 'high'
        
        return 'low'
    
    def _assess_edit_risk(self, filename: str, operation_type: str, 
                         instructions: str) -> str:
        """Assess risk level of edit operation."""
        if operation_type in {'replace', 'delete'}:
            return 'medium'
        
        if self._is_system_file(filename):
            return 'high'
        
        return 'low'
    
    def _is_system_file(self, filename: str) -> bool:
        """Check if filename refers to a system file."""
        system_files = {
            '/etc/', '/bin/', '/usr/bin/', '/system/', 'c:\\windows\\',
            '.bashrc', '.zshrc', '.profile', 'hosts', 'passwd'
        }
        
        filename_lower = filename.lower()
        return any(sys_file in filename_lower for sys_file in system_files)
    
    def _looks_like_code(self, content: str) -> bool:
        """Check if content looks like code."""
        code_indicators = [
            'def ', 'function ', 'class ', 'import ', 'from ',
            'if ', 'for ', 'while ', 'return ', '{\n', '}\n',
            ');', '{\n', '# ', '//', '<!-- ', '<html', '<body'
        ]
        
        return any(indicator in content for indicator in code_indicators)
    
    def _prompt_user_confirmation(self, filename: str, content: str, 
                                 operation: str, risk_level: str) -> bool:
        """
        Prompt user for confirmation.
        
        Args:
            filename: Filename
            content: Content to write
            operation: Operation type
            risk_level: Risk level assessment
            
        Returns:
            True if user confirms
        """
        # In automated modes, apply default policies
        if self.interface.interface_mode in ['simple', 'expert']:
            return risk_level != 'high'
        
        # Show confirmation prompt
        risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
        
        print(f"\n{risk_emoji.get(risk_level, '⚪')} Permission Request ({risk_level} risk)")
        print(f"Operation: {operation.title()} file")
        print(f"Filename: {filename}")
        print(f"Content size: {len(content)} characters")
        
        if risk_level == 'high':
            print("⚠️  HIGH RISK: This operation may be dangerous!")
            print("Please review the content carefully.")
        
        # Show content preview for small files
        if len(content) < 500:
            print(f"\nContent preview:")
            print("-" * 40)
            print(content[:200] + ("..." if len(content) > 200 else ""))
            print("-" * 40)
        
        while True:
            try:
                response = input(f"\nProceed with {operation}? [y/N/v(iew)/q(uit)]: ").strip().lower()
                
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no', '']:
                    return False
                elif response in ['v', 'view']:
                    self._show_full_content(content)
                    continue
                elif response in ['q', 'quit']:
                    raise KeyboardInterrupt()
                else:
                    print("Please enter 'y' for yes, 'n' for no, 'v' to view content, or 'q' to quit.")
            
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                return False
            except EOFError:
                return False
    
    def _prompt_edit_confirmation(self, filename: str, operation_type: str, 
                                 instructions: str, risk_level: str) -> bool:
        """Prompt user for edit confirmation."""
        if self.interface.interface_mode in ['simple', 'expert']:
            return risk_level != 'high'
        
        risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
        
        print(f"\n{risk_emoji.get(risk_level, '⚪')} Edit Permission Request ({risk_level} risk)")
        print(f"File: {filename}")
        print(f"Operation: {operation_type}")
        if instructions:
            print(f"Instructions: {instructions}")
        
        while True:
            try:
                response = input(f"\nProceed with edit? [y/N/q(uit)]: ").strip().lower()
                
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no', '']:
                    return False
                elif response in ['q', 'quit']:
                    raise KeyboardInterrupt()
                else:
                    print("Please enter 'y' for yes, 'n' for no, or 'q' to quit.")
            
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                return False
            except EOFError:
                return False
    
    def _show_full_content(self, content: str):
        """Show full content with paging."""
        lines = content.splitlines()
        
        print("\n" + "="*60)
        print("FULL CONTENT")
        print("="*60)
        
        for i, line in enumerate(lines, 1):
            print(f"{i:4d} | {line}")
            
            # Pause every 20 lines
            if i % 20 == 0 and i < len(lines):
                try:
                    input(f"--- Press Enter to continue ({i}/{len(lines)} lines shown) ---")
                except KeyboardInterrupt:
                    break
        
        print("="*60)
    
    def _get_full_path(self, filename: str) -> str:
        """Get full path for filename."""
        if os.path.isabs(filename):
            return filename
        return os.path.join(self.interface.project_location, filename)
    
    def clear_cache(self):
        """Clear permission cache."""
        self.permission_cache.clear()
    
    def get_permission_stats(self) -> Dict[str, Any]:
        """Get permission statistics."""
        return {
            'granted_count': len(self.granted_permissions),
            'denied_count': len(self.denied_permissions),
            'cached_decisions': len(self.permission_cache),
            'granted_files': list(self.granted_permissions),
            'denied_files': list(self.denied_permissions)
        }