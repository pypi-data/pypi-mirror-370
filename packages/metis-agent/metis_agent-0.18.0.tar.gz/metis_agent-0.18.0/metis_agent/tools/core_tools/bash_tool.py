#!/usr/bin/env python3
"""
BashTool - Framework-Compliant Command Execution Tool
Follows Metis Agent Tools Framework v2.0
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import os
import platform
import shlex
import tempfile
from ..base import BaseTool


class BashTool(BaseTool):
    """
    Production-ready command execution tool with safety features and cross-platform support.
    
    This tool handles executing shell commands with proper error handling,
    timeout management, and security restrictions.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize bash tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "BashTool"  # MUST match class name exactly
        self.description = "Executes shell commands with safety features and cross-platform support"
        
        # Optional metadata
        self.version = "1.0.0"
        self.category = "core_tools"
        
        # Safety configuration
        self.default_timeout = 30  # seconds
        self.max_timeout = 300     # 5 minutes max
        self.max_output_size = 1024 * 1024  # 1MB output limit
        
        # Platform detection
        self.is_windows = platform.system() == 'Windows'
        self.shell_executable = 'cmd.exe' if self.is_windows else '/bin/bash'
        
        # Dangerous commands to block - expanded list
        self.blocked_commands = {
            'rm -rf /', 'del /f /s /q', 'format', 'fdisk', 'mkfs',
            'dd if=', 'shutdown', 'reboot', 'halt', 'poweroff',
            'passwd', 'sudo su', 'su -', 'chmod 777', 'chown root',
            'curl', 'wget', 'nc', 'netcat', 'telnet', 'ssh', 'ftp',
            'python -c', 'perl -e', 'ruby -e', 'node -e', 'eval',
            'exec', 'system', 'os.system', '__import__', 'subprocess',
            '/bin/sh', '/bin/bash', 'cmd.exe', 'powershell'
        }
        
        # Safe command whitelist - only these base commands allowed
        self.allowed_commands = {
            'ls', 'dir', 'pwd', 'cd', 'echo', 'cat', 'type', 'head', 'tail',
            'grep', 'find', 'which', 'where', 'ps', 'tasklist', 'whoami',
            'date', 'time', 'uptime', 'df', 'du', 'free', 'top', 'htop',
            'wc', 'sort', 'uniq', 'cut', 'awk', 'sed', 'diff', 'file',
            'stat', 'basename', 'dirname', 'realpath', 'readlink'
        }
        
        # Dangerous shell operators and patterns
        self.blocked_operators = {
            ';', '&&', '||', '|', '>', '>>', '<', '<<', '&',
            '$', '`', '$(', '${', '*', '?', '[', ']', '~'
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Intelligent command execution task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires command execution, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Direct command keywords
        command_keywords = {
            'run', 'execute', 'bash', 'shell', 'command', 'cmd',
            'terminal', 'console', 'script', 'process'
        }
        
        has_command_keyword = any(keyword in task_clean for keyword in command_keywords)
        
        # Layer 2: Command-specific phrases
        command_phrases = [
            'run command', 'execute command', 'bash command',
            'shell command', 'run script', 'execute script',
            'in terminal', 'in console', 'command line'
        ]
        
        has_command_phrase = any(phrase in task_clean for phrase in command_phrases)
        
        # Layer 3: Direct command patterns (starts with allowed commands only)
        starts_with_command = any(task_clean.startswith(cmd) for cmd in self.allowed_commands)
        
        # Layer 4: Block tasks with dangerous operators
        has_dangerous_operators = any(op in task for op in self.blocked_operators)
        
        # Decision logic with security-first approach
        # Block tasks with dangerous operators immediately
        if has_dangerous_operators:
            return False
            
        # Allow if it has command keywords/phrases AND starts with safe commands
        if (has_command_keyword or has_command_phrase) and starts_with_command:
            return True
        elif starts_with_command and not has_dangerous_operators:
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute shell command with robust error handling and safety features.
        
        Args:
            task: Command execution task to perform
            **kwargs: Additional parameters (command, timeout, working_dir, etc.)
            
        Returns:
            Structured dictionary with command results and metadata
        """
        try:
            # Extract command
            command = self._extract_command(task, kwargs)
            
            if not command:
                return self._error_response("No command found in task or parameters")
            
            # Safety checks
            safety_check = self._check_command_safety(command)
            if not safety_check['safe']:
                return self._error_response(f"Command blocked for safety: {safety_check['reason']}")
            
            # Get execution parameters
            timeout = min(kwargs.get('timeout', self.default_timeout), self.max_timeout)
            working_dir = kwargs.get('working_dir', os.getcwd())
            capture_output = kwargs.get('capture_output', True)
            # SECURITY: Default to shell=False for better security
            shell = False  # Force shell=False for security
            
            # Validate working directory
            if not os.path.exists(working_dir):
                return self._error_response(f"Working directory does not exist: {working_dir}")
            
            # Prepare command for secure execution
            try:
                # Always use argument list for security (no shell=True)
                cmd_args = shlex.split(command, posix=not self.is_windows)
                
                # Additional validation on parsed arguments
                if not cmd_args:
                    return self._error_response("Command parsing resulted in empty arguments")
                
                # Resolve command path for additional security
                import shutil
                cmd_path = shutil.which(cmd_args[0])
                if not cmd_path:
                    return self._error_response(f"Command '{cmd_args[0]}' not found in system PATH")
                
                # Replace command with full path
                cmd_args[0] = cmd_path
                
            except ValueError as e:
                return self._error_response(f"Command parsing failed: {str(e)}")
            
            # Execute command securely (never with shell=True)
            start_time = datetime.now()
            
            # Create a minimal, secure environment
            secure_env = {
                'PATH': os.environ.get('PATH', ''),
                'HOME': os.environ.get('HOME', ''),
                'USER': os.environ.get('USER', ''),
                'LANG': os.environ.get('LANG', 'C'),
            }
            
            # Add Windows-specific environment variables if needed
            if self.is_windows:
                secure_env.update({
                    'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                    'TEMP': os.environ.get('TEMP', ''),
                    'TMP': os.environ.get('TMP', ''),
                })
            
            result = subprocess.run(
                cmd_args,
                shell=False,  # CRITICAL: Never use shell=True
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=working_dir,
                env=secure_env  # Use minimal secure environment
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Check output size
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n... (output truncated)"
            
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n... (error output truncated)"
            
            return {
                "success": result.returncode == 0,
                "type": "bash_response",
                "data": {
                    "command": command,
                    "return_code": result.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "execution_time_seconds": execution_time,
                    "working_directory": working_dir,
                    "platform": platform.system()
                },
                "metadata": {
                    "tool_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "execution_stats": {
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "timeout_used": timeout,
                        "stdout_length": len(result.stdout or ""),
                        "stderr_length": len(result.stderr or "")
                    }
                }
            }
            
        except subprocess.TimeoutExpired:
            return self._error_response(f"Command timed out after {timeout} seconds")
        except subprocess.CalledProcessError as e:
            return self._error_response(f"Command failed with return code {e.returncode}: {e.stderr}")
        except Exception as e:
            return self._error_response(f"Command execution failed: {str(e)}", e)
    
    def _extract_command(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract command from task or parameters."""
        # Check kwargs first
        if 'command' in kwargs:
            return kwargs['command']
        if 'cmd' in kwargs:
            return kwargs['cmd']
        
        # Extract from task text
        import re
        
        # Look for quoted commands
        quoted_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'`([^`]+)`'
        ]
        
        for pattern in quoted_patterns:
            matches = re.findall(pattern, task)
            if matches:
                return matches[0]
        
        # Look for command after keywords
        command_patterns = [
            r'(?:run|execute|bash)\s+(?:command\s+)?(.+)',
            r'(?:command|cmd):\s*(.+)',
            r'(?:shell|terminal):\s*(.+)'
        ]
        
        for pattern in command_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # If task starts with a known command, use the whole task
        if any(task.strip().lower().startswith(cmd) for cmd in self.safe_patterns):
            return task.strip()
        
        return None
    
    def _check_command_safety(self, command: str) -> Dict[str, Any]:
        """
        Comprehensive command safety validation using whitelist approach.
        
        This method implements a security-first approach by:
        1. Validating command against whitelist of allowed commands
        2. Blocking dangerous operators and patterns
        3. Preventing injection attempts
        4. Limiting command complexity
        """
        command_clean = command.strip()
        command_lower = command_clean.lower()
        
        # Input validation
        if not command_clean:
            return {'safe': False, 'reason': 'Empty command not allowed'}
        
        if len(command_clean) > 500:  # Reduced from 1000 for better security
            return {'safe': False, 'reason': 'Command too long (max 500 characters)'}
        
        # Check for blocked operators first
        for operator in self.blocked_operators:
            if operator in command_clean:
                return {
                    'safe': False,
                    'reason': f"Blocked shell operator detected: '{operator}'"
                }
        
        # Parse command to extract base command
        import shlex
        try:
            # Use shlex to properly parse the command
            parts = shlex.split(command_clean, posix=not self.is_windows)
            if not parts:
                return {'safe': False, 'reason': 'Invalid command structure'}
            
            base_command = parts[0].lower()
            
            # Windows command normalization
            if self.is_windows:
                # Remove .exe extension for comparison
                if base_command.endswith('.exe'):
                    base_command = base_command[:-4]
                
                # Handle Windows command variants
                windows_equivalents = {
                    'type': 'cat',
                    'dir': 'ls',
                    'findstr': 'grep'
                }
                base_command = windows_equivalents.get(base_command, base_command)
            
            # Whitelist validation - ONLY allow explicitly approved commands
            if base_command not in self.allowed_commands:
                return {
                    'safe': False,
                    'reason': f"Command '{base_command}' not in allowed whitelist"
                }
                
        except ValueError as e:
            return {'safe': False, 'reason': f"Command parsing failed: {str(e)}"}
        
        # Check for blocked command patterns
        for blocked in self.blocked_commands:
            if blocked in command_lower:
                return {
                    'safe': False,
                    'reason': f"Contains blocked command pattern: '{blocked}'"
                }
        
        # Additional pattern-based security checks
        import re
        dangerous_patterns = [
            r'rm\s+-rf\s*/',
            r'del\s+/[fs]\s+',
            r'>\s*/dev/',
            r'chmod\s+777',
            r'sudo\s+\w+',
            r'dd\s+if=',
            r'mkfifo',
            r'/proc/',
            r'/sys/',
            r'\\\\',  # UNC paths on Windows
            r'\$\(',  # Command substitution
            r'`[^`]*`',  # Backticks
            r'eval\s+',
            r'exec\s+',
            r'python\s+-c',
            r'perl\s+-e',
            r'ruby\s+-e',
            r'node\s+-e'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                return {
                    'safe': False,
                    'reason': f"Contains dangerous pattern matching: {pattern}"
                }
        
        # Check for suspicious argument patterns
        suspicious_args = [
            '--help', '-h',  # Allow help
            '-rf', '-r',     # Recursive operations
            '-f',            # Force operations
            '--force',       # Force flag
            '--recursive',   # Recursive flag
            '--all',         # All files flag
            '-a'             # All files short flag
        ]
        
        # Only allow basic read-only flags
        allowed_flags = {'-l', '-la', '-al', '-h', '--help', '-v', '--version', '-n'}
        
        for part in parts[1:]:  # Skip the command itself
            if part.startswith('-') and part not in allowed_flags:
                # Check if it's a dangerous flag
                if any(dangerous in part.lower() for dangerous in ['-rf', '-r', '-f', '--force', '--recursive']):
                    return {
                        'safe': False,
                        'reason': f"Dangerous flag detected: '{part}'"
                    }
        
        return {'safe': True, 'reason': 'Command passed comprehensive safety validation'}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text", "shell_command"],
            "output_types": ["structured_data", "command_output"],
            "estimated_execution_time": "1-30s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": False,  # Commands may conflict
            "resource_intensive": True,
            "supported_intents": ["run", "execute", "bash", "shell", "command"],
            "api_dependencies": [],
            "memory_usage": "low-moderate"
        }
    
    def get_examples(self) -> list:
        """Get example tasks that this tool can handle."""
        return [
            "Run command 'ls -la'",
            "Execute 'pwd' to show current directory",
            "Run 'ps aux | grep python'",
            "Execute bash command 'find . -name \"*.py\"'",
            "Run 'df -h' to check disk space",
            "Execute 'whoami' to show current user"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the command is safe and not in the blocked list",
                "Check that you have permissions to execute the command",
                "Verify the working directory exists and is accessible",
                "Use shorter commands (max 1000 characters)",
                "Consider using timeout parameter for long-running commands",
                f"Platform detected: {platform.system()}"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'platform': platform.system(),
                'max_timeout': self.max_timeout,
                'blocked_commands': list(self.blocked_commands)[:5]  # Show first 5
            }
        }
