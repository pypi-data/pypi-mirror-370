#!/usr/bin/env python3
"""
Path Security Utilities for Metis Agent
Provides secure path validation and normalization functions.
"""

import os
import platform
import pathlib
from typing import Optional, Set, List
from pathlib import Path


class SecurePathValidator:
    """
    Secure path validation utility that prevents directory traversal attacks
    and restricts access to sensitive system directories.
    """
    
    def __init__(self):
        """Initialize with platform-specific security settings."""
        self.is_windows = platform.system() == 'Windows'
        self.is_linux = platform.system() == 'Linux'
        self.is_macos = platform.system() == 'Darwin'
        
        # Define restricted system paths by platform
        self._setup_restricted_paths()
        
        # Define allowed base directories (can be customized)
        self._setup_allowed_base_dirs()
    
    def _setup_restricted_paths(self):
        """Setup platform-specific restricted paths."""
        # Common restricted paths for all platforms
        self.restricted_paths = {
            '/etc', '/proc', '/sys', '/dev', '/boot', '/root',
            '/var/log', '/var/run', '/tmp', '/usr/bin', '/usr/sbin',
            '/bin', '/sbin', '/lib', '/lib64'
        }
        
        if self.is_windows:
            self.restricted_paths.update({
                'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)',
                'C:\\System Volume Information', 'C:\\pagefile.sys',
                'C:\\hiberfil.sys', 'C:\\swapfile.sys', 'C:\\$Recycle.Bin',
                'C:\\Recovery', 'C:\\Documents and Settings'
            })
        elif self.is_linux:
            self.restricted_paths.update({
                '/var/cache', '/var/lib', '/var/spool', '/var/tmp',
                '/run', '/media', '/mnt', '/opt', '/srv'
            })
        elif self.is_macos:
            self.restricted_paths.update({
                '/System', '/Library', '/Applications', '/private',
                '/var', '/usr', '/cores', '/dev'
            })
        
        # Convert to Path objects and resolve
        self.restricted_paths = {Path(p).resolve() for p in self.restricted_paths}
    
    def _setup_allowed_base_dirs(self):
        """Setup allowed base directories where file operations are permitted."""
        if self.is_windows:
            self.allowed_base_dirs = {
                Path.home(),  # User home directory
                Path.cwd(),   # Current working directory
                Path('C:\\Users').resolve(),
                Path('C:\\temp').resolve() if Path('C:\\temp').exists() else None,
            }
        else:
            self.allowed_base_dirs = {
                Path.home(),  # User home directory
                Path.cwd(),   # Current working directory
                Path('/tmp').resolve(),
                Path('/var/tmp').resolve(),
            }
        
        # Remove None values
        self.allowed_base_dirs = {p for p in self.allowed_base_dirs if p is not None}
    
    def validate_path(self, file_path: str, base_dir: Optional[str] = None) -> Path:
        """
        Validate and normalize a file path with security checks.
        
        Args:
            file_path: The path to validate
            base_dir: Optional base directory to restrict access to
            
        Returns:
            Validated and normalized Path object
            
        Raises:
            SecurityError: If path is invalid or restricted
            ValueError: If path is malformed
        """
        if not file_path or not isinstance(file_path, str):
            raise ValueError("Invalid file path: path must be a non-empty string")
        
        try:
            # Convert to Path object
            path = Path(file_path)
            
            # Check for suspicious patterns
            self._check_suspicious_patterns(str(path))
            
            # Resolve path (handles .., ., symlinks)
            if not path.is_absolute():
                if base_dir:
                    base = Path(base_dir).resolve()
                    path = base / path
                else:
                    path = Path.cwd() / path
            
            # Resolve to get canonical path
            try:
                resolved_path = path.resolve(strict=False)  # Don't require file to exist
            except (OSError, RuntimeError) as e:
                raise SecurityError(f"Path resolution failed: {e}")
            
            # Security validations
            self._validate_against_restricted_paths(resolved_path)
            
            if base_dir:
                self._validate_within_base_directory(resolved_path, Path(base_dir).resolve())
            else:
                self._validate_against_allowed_base_dirs(resolved_path)
            
            # Additional security checks
            self._check_symlink_security(resolved_path)
            self._validate_path_length(resolved_path)
            
            return resolved_path
            
        except Exception as e:
            if isinstance(e, (SecurityError, ValueError)):
                raise
            else:
                raise ValueError(f"Path validation failed: {e}")
    
    def _check_suspicious_patterns(self, path_str: str):
        """Check for suspicious patterns in the path string."""
        suspicious_patterns = [
            '..', '/../', '\\..\\',  # Directory traversal
            '\x00',  # Null bytes
            '|', '&', ';', '$', '`',  # Shell injection characters
            '<', '>', '"',  # Redirection and quotes
        ]
        
        for pattern in suspicious_patterns:
            if pattern in path_str:
                raise SecurityError(f"Suspicious pattern detected in path: '{pattern}'")
    
    def _validate_against_restricted_paths(self, path: Path):
        """Validate path is not in restricted system directories."""
        try:
            # Check if path starts with any restricted path
            for restricted in self.restricted_paths:
                try:
                    path.relative_to(restricted)
                    raise SecurityError(f"Access denied: path is in restricted directory '{restricted}'")
                except ValueError:
                    # path is not relative to restricted - this is good
                    continue
        except Exception as e:
            if isinstance(e, SecurityError):
                raise
            # If we can't check, err on the side of caution
            raise SecurityError(f"Unable to validate path restrictions: {e}")
    
    def _validate_within_base_directory(self, path: Path, base_dir: Path):
        """Validate path is within the specified base directory."""
        try:
            path.relative_to(base_dir)
        except ValueError:
            raise SecurityError(f"Path outside allowed base directory: '{path}' not within '{base_dir}'")
    
    def _validate_against_allowed_base_dirs(self, path: Path):
        """Validate path is within one of the allowed base directories."""
        for allowed_base in self.allowed_base_dirs:
            try:
                path.relative_to(allowed_base)
                return  # Path is within an allowed base directory
            except ValueError:
                continue
        
        # If we get here, path is not within any allowed base directory
        allowed_dirs_str = ', '.join(str(d) for d in self.allowed_base_dirs)
        raise SecurityError(f"Path not within allowed directories. Path: '{path}', Allowed: {allowed_dirs_str}")
    
    def _check_symlink_security(self, path: Path):
        """Check for symlink security issues."""
        # For now, we allow symlinks but could restrict them
        # Future enhancement: validate symlink targets
        pass
    
    def _validate_path_length(self, path: Path):
        """Validate path length to prevent buffer overflow attacks."""
        path_str = str(path)
        max_length = 260 if self.is_windows else 4096  # Windows MAX_PATH vs Linux PATH_MAX
        
        if len(path_str) > max_length:
            raise SecurityError(f"Path too long: {len(path_str)} characters (max: {max_length})")
    
    def add_allowed_base_dir(self, base_dir: str):
        """Add an additional allowed base directory."""
        base_path = Path(base_dir).resolve()
        self.allowed_base_dirs.add(base_path)
    
    def remove_allowed_base_dir(self, base_dir: str):
        """Remove an allowed base directory."""
        base_path = Path(base_dir).resolve()
        self.allowed_base_dirs.discard(base_path)


class SecurityError(Exception):
    """Exception raised for security-related path validation failures."""
    pass


# Global instance for convenience
_default_validator = SecurePathValidator()


def validate_secure_path(file_path: str, base_dir: Optional[str] = None) -> Path:
    """
    Convenience function to validate a path using the default validator.
    
    Args:
        file_path: The path to validate
        base_dir: Optional base directory to restrict access to
        
    Returns:
        Validated and normalized Path object
        
    Raises:
        SecurityError: If path is invalid or restricted
        ValueError: If path is malformed
    """
    return _default_validator.validate_path(file_path, base_dir)


def is_path_safe(file_path: str, base_dir: Optional[str] = None) -> bool:
    """
    Check if a path is safe without raising exceptions.
    
    Args:
        file_path: The path to check
        base_dir: Optional base directory to restrict access to
        
    Returns:
        True if path is safe, False otherwise
    """
    try:
        validate_secure_path(file_path, base_dir)
        return True
    except (SecurityError, ValueError):
        return False