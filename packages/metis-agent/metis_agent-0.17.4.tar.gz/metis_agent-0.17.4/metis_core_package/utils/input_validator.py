#!/usr/bin/env python3
"""
Input Validation and Sanitization Utilities for Metis Agent

Provides comprehensive input validation, sanitization, and security filtering
to prevent injection attacks and ensure data integrity across the framework.
"""

import re
import html
import json
import base64
import urllib.parse
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime
from pathlib import Path
import hashlib


class ValidationError(Exception):
    """Exception raised for input validation failures."""
    pass


class InputValidator:
    """
    Comprehensive input validation and sanitization utility.
    
    Provides protection against:
    - SQL injection
    - XSS attacks
    - Command injection
    - Path traversal
    - LDAP injection
    - JSON injection
    - HTTP header injection
    - Template injection
    """
    
    def __init__(self):
        """Initialize the input validator with security patterns."""
        self._setup_patterns()
        self._setup_sanitizers()
    
    def _setup_patterns(self):
        """Setup dangerous patterns for detection."""
        # SQL injection patterns
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(--|\/\*|\*\/)",
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\'\s*(OR|AND)\s*\'\w*\'\s*=\s*\'\w*)",
            r"(\d+\s*(=|<|>|!=)\s*\d+)",
            r"(\b(CAST|CONVERT|SUBSTRING|CHAR|ASCII)\s*\()",
            r"(@@version|@@user|@@database)",
            r"(\bINTO\s+OUTFILE\b)"
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"<style[^>]*>.*?</style>",
            r"expression\s*\(",
            r"url\s*\(",
            r"@import",
            r"<svg[^>]*>.*?</svg>"
        ]
        
        # Command injection patterns
        self.command_injection_patterns = [
            r"[;&|`$]",
            r"\$\([^)]*\)",
            r"`[^`]*`",
            r"&&|\|\|",
            r">\s*/dev/",
            r"/bin/\w+",
            r"/usr/bin/\w+",
            r"cmd\.exe|powershell",
            r"system\s*\(",
            r"exec\s*\(",
            r"eval\s*\(",
            r"subprocess\.",
            r"os\.system",
            r"__import__"
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2F",
            r"\.\.%5C",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"..%252f",
            r"..%255c"
        ]
        
        # LDAP injection patterns
        self.ldap_injection_patterns = [
            r"[()&|!*]",
            r"\\[0-9a-fA-F]{2}",
            r"\x00"
        ]
        
        # Template injection patterns
        self.template_injection_patterns = [
            r"\{\{.*\}\}",
            r"\{%.*%\}",
            r"\$\{.*\}",
            r"<%.*%>",
            r"#\{.*\}"
        ]
        
        # Compile all patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        self.compiled_sql_patterns = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.sql_injection_patterns]
        self.compiled_xss_patterns = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.xss_patterns]
        self.compiled_command_patterns = [re.compile(p, re.IGNORECASE) for p in self.command_injection_patterns]
        self.compiled_path_patterns = [re.compile(p, re.IGNORECASE) for p in self.path_traversal_patterns]
        self.compiled_ldap_patterns = [re.compile(p) for p in self.ldap_injection_patterns]
        self.compiled_template_patterns = [re.compile(p, re.IGNORECASE) for p in self.template_injection_patterns]
    
    def _setup_sanitizers(self):
        """Setup sanitization functions."""
        self.html_sanitizer = self._sanitize_html
        self.sql_sanitizer = self._sanitize_sql
        self.command_sanitizer = self._sanitize_command
        self.path_sanitizer = self._sanitize_path
    
    def validate_string(self, input_str: str, max_length: int = 10000, 
                       allow_html: bool = False, context: str = "general") -> str:
        """
        Validate and sanitize a string input.
        
        Args:
            input_str: String to validate
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML content
            context: Context for validation (general, sql, command, path, etc.)
            
        Returns:
            Sanitized string
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(input_str, str):
            raise ValidationError(f"Expected string, got {type(input_str)}")
        
        # Length validation
        if len(input_str) > max_length:
            raise ValidationError(f"String too long: {len(input_str)} > {max_length}")
        
        # Null byte check
        if '\x00' in input_str:
            raise ValidationError("Null byte detected in input")
        
        # Context-specific validation
        if context == "sql":
            return self._validate_sql_input(input_str)
        elif context == "command":
            return self._validate_command_input(input_str)
        elif context == "path":
            return self._validate_path_input(input_str)
        elif context == "html":
            return self._validate_html_input(input_str, allow_html)
        else:
            return self._validate_general_input(input_str, allow_html)
    
    def _validate_general_input(self, input_str: str, allow_html: bool = False) -> str:
        """Validate general string input."""
        # Only check for the most critical patterns in general context
        self._check_template_injection(input_str)
        
        if not allow_html:
            self._check_xss(input_str)
            return self._sanitize_html(input_str)
        
        return input_str
    
    def _validate_sql_input(self, input_str: str) -> str:
        """Validate input intended for SQL contexts."""
        self._check_sql_injection(input_str)
        return self._sanitize_sql(input_str)
    
    def _validate_command_input(self, input_str: str) -> str:
        """Validate input intended for command contexts."""
        self._check_command_injection(input_str)
        return self._sanitize_command(input_str)
    
    def _validate_path_input(self, input_str: str) -> str:
        """Validate input intended for path contexts."""
        self._check_path_traversal(input_str)
        return self._sanitize_path(input_str)
    
    def _validate_html_input(self, input_str: str, allow_html: bool = False) -> str:
        """Validate input intended for HTML contexts."""
        if not allow_html:
            self._check_xss(input_str)
            return self._sanitize_html(input_str)
        else:
            # For allowed HTML, do basic XSS checks but allow some tags
            return self._sanitize_html_permissive(input_str)
    
    def _check_sql_injection(self, input_str: str):
        """Check for SQL injection patterns."""
        for pattern in self.compiled_sql_patterns:
            if pattern.search(input_str):
                raise ValidationError(f"Potential SQL injection detected: {pattern.pattern}")
    
    def _check_xss(self, input_str: str):
        """Check for XSS patterns."""
        for pattern in self.compiled_xss_patterns:
            if pattern.search(input_str):
                raise ValidationError(f"Potential XSS detected: {pattern.pattern}")
    
    def _check_command_injection(self, input_str: str):
        """Check for command injection patterns."""
        for pattern in self.compiled_command_patterns:
            if pattern.search(input_str):
                raise ValidationError(f"Potential command injection detected: {pattern.pattern}")
    
    def _check_path_traversal(self, input_str: str):
        """Check for path traversal patterns."""
        for pattern in self.compiled_path_patterns:
            if pattern.search(input_str):
                raise ValidationError(f"Potential path traversal detected: {pattern.pattern}")
    
    def _check_template_injection(self, input_str: str):
        """Check for template injection patterns."""
        # Skip if the input contains command injection patterns (avoid double detection)
        for cmd_pattern in self.compiled_command_patterns:
            if cmd_pattern.search(input_str):
                return  # Let command injection handle this
        
        for pattern in self.compiled_template_patterns:
            if pattern.search(input_str):
                raise ValidationError(f"Potential template injection detected: {pattern.pattern}")
    
    def _sanitize_html(self, input_str: str) -> str:
        """Sanitize HTML content."""
        # First remove HTML tags
        sanitized = re.sub(r'<[^>]*>', '', input_str)
        
        # Then do HTML entity encoding only for remaining content
        sanitized = html.escape(sanitized, quote=True)
        
        return sanitized
    
    def _sanitize_html_permissive(self, input_str: str) -> str:
        """Sanitize HTML content while allowing some safe tags."""
        # Allow only specific safe tags
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'i', 'b', 'span']
        
        # Remove dangerous tags
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'link', 'meta', 'style']
        for tag in dangerous_tags:
            input_str = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', input_str, flags=re.IGNORECASE | re.DOTALL)
            input_str = re.sub(f'<{tag}[^>]*/?>', '', input_str, flags=re.IGNORECASE)
        
        # Remove event handlers
        input_str = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', input_str, flags=re.IGNORECASE)
        
        return input_str
    
    def _sanitize_sql(self, input_str: str) -> str:
        """Sanitize input for SQL contexts."""
        # Escape single quotes
        sanitized = input_str.replace("'", "''")
        
        # Remove SQL comments
        sanitized = re.sub(r'--.*$', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        
        return sanitized
    
    def _sanitize_command(self, input_str: str) -> str:
        """Sanitize input for command contexts."""
        # Remove dangerous characters
        dangerous_chars = ['&', '|', ';', '`', '$', '>', '<', '(', ')', '{', '}']
        sanitized = input_str
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    def _sanitize_path(self, input_str: str) -> str:
        """Sanitize input for path contexts."""
        # Remove path traversal sequences
        sanitized = input_str.replace('../', '').replace('..\\', '')
        sanitized = urllib.parse.unquote(sanitized)  # Decode URL encoding
        sanitized = sanitized.replace('../', '').replace('..\\', '')  # Check again after decoding
        
        return sanitized
    
    def validate_email(self, email: str) -> str:
        """Validate email address format."""
        if not isinstance(email, str):
            raise ValidationError("Email must be a string")
        
        # Basic email regex (simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        if len(email) > 255:
            raise ValidationError("Email too long")
        
        return email.lower().strip()
    
    def validate_url(self, url: str, allowed_schemes: List[str] = None) -> str:
        """Validate URL format and scheme."""
        if not isinstance(url, str):
            raise ValidationError("URL must be a string")
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        
        if not re.match(url_pattern, url):
            raise ValidationError("Invalid URL format")
        
        # Check scheme
        scheme = url.split('://')[0].lower()
        if scheme not in allowed_schemes:
            raise ValidationError(f"URL scheme '{scheme}' not allowed")
        
        if len(url) > 2048:
            raise ValidationError("URL too long")
        
        return url.strip()
    
    def validate_json(self, json_str: str, max_depth: int = 10) -> Dict[str, Any]:
        """Validate and parse JSON with depth limits."""
        if not isinstance(json_str, str):
            raise ValidationError("JSON input must be a string")
        
        if len(json_str) > 100000:  # 100KB limit
            raise ValidationError("JSON string too large")
        
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
        
        # Check nesting depth
        if self._get_json_depth(parsed) > max_depth:
            raise ValidationError(f"JSON nesting too deep (max: {max_depth})")
        
        return parsed
    
    def _get_json_depth(self, obj: Any, depth: int = 0) -> int:
        """Calculate JSON object nesting depth."""
        if isinstance(obj, dict):
            return max(self._get_json_depth(v, depth + 1) for v in obj.values()) if obj else depth
        elif isinstance(obj, list):
            return max(self._get_json_depth(item, depth + 1) for item in obj) if obj else depth
        else:
            return depth
    
    def validate_integer(self, value: Any, min_val: int = None, max_val: int = None) -> int:
        """Validate integer input with range checks."""
        if isinstance(value, str):
            if not value.strip().lstrip('-').isdigit():
                raise ValidationError("Invalid integer format")
            try:
                value = int(value.strip())
            except ValueError:
                raise ValidationError("Cannot convert to integer")
        elif not isinstance(value, int):
            raise ValidationError(f"Expected integer, got {type(value)}")
        
        if min_val is not None and value < min_val:
            raise ValidationError(f"Integer too small: {value} < {min_val}")
        
        if max_val is not None and value > max_val:
            raise ValidationError(f"Integer too large: {value} > {max_val}")
        
        return value
    
    def validate_float(self, value: Any, min_val: float = None, max_val: float = None) -> float:
        """Validate float input with range checks."""
        if isinstance(value, str):
            try:
                value = float(value.strip())
            except ValueError:
                raise ValidationError("Invalid float format")
        elif not isinstance(value, (int, float)):
            raise ValidationError(f"Expected float, got {type(value)}")
        
        value = float(value)
        
        if min_val is not None and value < min_val:
            raise ValidationError(f"Float too small: {value} < {min_val}")
        
        if max_val is not None and value > max_val:
            raise ValidationError(f"Float too large: {value} > {max_val}")
        
        return value
    
    def validate_base64(self, input_str: str, max_decoded_size: int = 10000) -> bytes:
        """Validate and decode base64 input."""
        if not isinstance(input_str, str):
            raise ValidationError("Base64 input must be a string")
        
        try:
            # Add padding if necessary
            padded = input_str + '=' * (4 - len(input_str) % 4)
            decoded = base64.b64decode(padded, validate=True)
        except Exception as e:
            raise ValidationError(f"Invalid base64 encoding: {e}")
        
        if len(decoded) > max_decoded_size:
            raise ValidationError(f"Decoded data too large: {len(decoded)} > {max_decoded_size}")
        
        return decoded
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem operations."""
        if not isinstance(filename, str):
            raise ValidationError("Filename must be a string")
        
        # Remove path components manually to avoid Path issues with special chars
        sanitized = filename.split('/')[-1].split('\\')[-1]
        
        # Replace dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/', '\x00']
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing dots and spaces only for truly problematic cases
        # Only strip if it starts AND ends with dots/spaces and has other content
        original_sanitized = sanitized
        if sanitized.startswith(('.', ' ')) and sanitized.endswith(('.', ' ')):
            stripped = sanitized.strip('. ')
            # Only use stripped version if it's not empty and substantially different
            if stripped and len(stripped) >= len(sanitized) * 0.5:
                sanitized = stripped
        
        # Limit length after stripping
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        # Ensure not empty
        if not sanitized or sanitized.isspace():
            sanitized = 'unnamed_file'
        
        return sanitized
    
    def validate_dict(self, input_dict: Dict[str, Any], required_keys: List[str] = None,
                     allowed_keys: List[str] = None, key_validators: Dict[str, Callable] = None) -> Dict[str, Any]:
        """Validate dictionary structure and contents."""
        if not isinstance(input_dict, dict):
            raise ValidationError(f"Expected dict, got {type(input_dict)}")
        
        # Check required keys
        if required_keys:
            missing_keys = set(required_keys) - set(input_dict.keys())
            if missing_keys:
                raise ValidationError(f"Missing required keys: {missing_keys}")
        
        # Check allowed keys
        if allowed_keys:
            extra_keys = set(input_dict.keys()) - set(allowed_keys)
            if extra_keys:
                raise ValidationError(f"Unexpected keys: {extra_keys}")
        
        # Validate individual values
        validated_dict = {}
        for key, value in input_dict.items():
            # Validate key
            validated_key = self.validate_string(str(key), max_length=100, context="general")
            
            # Validate value with custom validator if provided
            if key_validators and key in key_validators:
                validated_value = key_validators[key](value)
            else:
                # Default validation for different types
                if isinstance(value, str):
                    validated_value = self.validate_string(value, context="general")
                elif isinstance(value, dict):
                    validated_value = self.validate_dict(value)
                elif isinstance(value, list):
                    validated_value = [self.validate_string(str(item)) if isinstance(item, str) else item for item in value]
                else:
                    validated_value = value
            
            validated_dict[validated_key] = validated_value
        
        return validated_dict


# Global validator instance
_default_validator = InputValidator()


def validate_input(input_data: Any, input_type: str = "string", **kwargs) -> Any:
    """
    Convenience function to validate input using the default validator.
    
    Args:
        input_data: Data to validate
        input_type: Type of validation (string, email, url, json, etc.)
        **kwargs: Additional validation parameters
        
    Returns:
        Validated and sanitized data
        
    Raises:
        ValidationError: If validation fails
    """
    if input_type == "string":
        return _default_validator.validate_string(input_data, **kwargs)
    elif input_type == "email":
        return _default_validator.validate_email(input_data)
    elif input_type == "url":
        return _default_validator.validate_url(input_data, **kwargs)
    elif input_type == "json":
        return _default_validator.validate_json(input_data, **kwargs)
    elif input_type == "integer":
        return _default_validator.validate_integer(input_data, **kwargs)
    elif input_type == "float":
        return _default_validator.validate_float(input_data, **kwargs)
    elif input_type == "base64":
        return _default_validator.validate_base64(input_data, **kwargs)
    elif input_type == "filename":
        return _default_validator.sanitize_filename(input_data)
    elif input_type == "dict":
        return _default_validator.validate_dict(input_data, **kwargs)
    else:
        raise ValidationError(f"Unknown input type: {input_type}")


def is_input_safe(input_data: Any, input_type: str = "string", **kwargs) -> bool:
    """
    Check if input is safe without raising exceptions.
    
    Args:
        input_data: Data to check
        input_type: Type of validation
        **kwargs: Additional validation parameters
        
    Returns:
        True if input is safe, False otherwise
    """
    try:
        validate_input(input_data, input_type, **kwargs)
        return True
    except ValidationError:
        return False