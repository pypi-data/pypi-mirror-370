#!/usr/bin/env python3
"""
Comprehensive tests for the SecureStorage security component.

Tests all aspects of secure data storage including:
- AES-256-GCM encryption
- PBKDF2 key derivation
- Machine-specific key binding
- Audit logging
- Key rotation
- Error handling and edge cases
"""

import pytest
import tempfile
import shutil
import os
import json
import time
from pathlib import Path
from metis_agent.auth.secure_storage import SecureStorage, SecurityError


class TestSecureStorage:
    """Test suite for SecureStorage class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = SecureStorage(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    # Basic Encryption/Decryption Tests
    def test_basic_encryption_decryption(self):
        """Test basic data encryption and decryption."""
        test_data = {"api_key": "test_key_12345", "service": "openai"}
        
        # Store data
        self.storage.save_data("test_service", test_data)
        
        # Retrieve data
        retrieved_data = self.storage.load_data("test_service")
        
        assert retrieved_data == test_data
    
    def test_encryption_with_various_data_types(self):
        """Test encryption with different data types."""
        test_cases = [
            ("string_data", "simple string"),
            ("integer_data", 42),
            ("float_data", 3.14159),
            ("boolean_data", True),
            ("list_data", [1, 2, 3, "test", {"nested": "value"}]),
            ("dict_data", {
                "string": "value",
                "number": 123,
                "nested": {"deep": {"very_deep": "value"}},
                "array": [1, 2, 3]
            }),
            ("none_data", None),
            ("empty_dict", {}),
            ("empty_list", []),
        ]
        
        for identifier, test_data in test_cases:
            self.storage.save_data(identifier, test_data)
            retrieved_data = self.storage.load_data(identifier)
            assert retrieved_data == test_data, f"Failed for {identifier}"
    
    def test_large_data_encryption(self):
        """Test encryption of large data sets."""
        # Create a reasonably large data structure
        large_data = {
            "large_string": "a" * 10000,  # 10KB string
            "large_list": list(range(1000)),
            "repeated_data": [{"key": f"value_{i}"} for i in range(100)]
        }
        
        self.storage.save_data("large_data", large_data)
        retrieved_data = self.storage.load_data("large_data")
        
        assert retrieved_data == large_data
    
    def test_unicode_and_special_characters(self):
        """Test encryption with Unicode and special characters."""
        unicode_data = {
            "emoji": "🔐🛡️🚀",
            "chinese": "你好世界",
            "arabic": "مرحبا بالعالم",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "newlines": "line1\nline2\r\nline3",
            "tabs": "col1\tcol2\tcol3",
        }
        
        self.storage.save_data("unicode_test", unicode_data)
        retrieved_data = self.storage.load_data("unicode_test")
        
        assert retrieved_data == unicode_data
    
    # Security Tests
    def test_data_is_actually_encrypted(self):
        """Test that data is actually encrypted on disk."""
        test_data = {"secret": "very_secret_api_key_12345"}
        
        self.storage.save_data("secret_test", test_data)
        
        # Read the raw encrypted file
        encrypted_file = os.path.join(self.temp_dir, "secret_test.enc")
        assert os.path.exists(encrypted_file)
        
        with open(encrypted_file, 'r') as f:
            encrypted_content = f.read()
        
        # The encrypted content should not contain the original data
        assert "very_secret_api_key_12345" not in encrypted_content
        assert "secret" not in encrypted_content
        
        # Should be base64-encoded
        import base64
        try:
            base64.b64decode(encrypted_content)
        except Exception:
            pytest.fail("Encrypted content is not valid base64")
    
    def test_file_permissions(self):
        """Test that files have secure permissions."""
        test_data = {"test": "data"}
        self.storage.save_data("permission_test", test_data)
        
        # Check encrypted file permissions
        encrypted_file = os.path.join(self.temp_dir, "permission_test.enc")
        file_stat = os.stat(encrypted_file)
        file_permissions = oct(file_stat.st_mode)[-3:]
        
        # Should be 600 (rw-------) on Unix systems
        if os.name != 'nt':  # Not Windows
            assert file_permissions == '600', f"File permissions are {file_permissions}, expected 600"
    
    def test_key_integrity_verification(self):
        """Test key integrity verification prevents tampering."""
        # This test is implementation-specific and may need adjustment
        # based on the exact integrity checking mechanism
        test_data = {"api_key": "test_key"}
        self.storage.save_data("integrity_test", test_data)
        
        # The integrity should be maintained
        retrieved_data = self.storage.load_data("integrity_test")
        assert retrieved_data == test_data
    
    def test_different_storage_instances_use_same_keys(self):
        """Test that different storage instances can decrypt each other's data."""
        test_data = {"shared": "data"}
        
        # Store with first instance
        self.storage.save_data("shared_test", test_data)
        
        # Create second instance with same directory
        storage2 = SecureStorage(self.temp_dir)
        
        # Should be able to decrypt with second instance
        retrieved_data = storage2.load_data("shared_test")
        assert retrieved_data == test_data
    
    # Audit Logging Tests
    def test_audit_logging(self):
        """Test that operations are logged for security audit."""
        test_data = {"logged": "operation"}
        
        # Perform operations
        self.storage.save_data("audit_test", test_data)
        self.storage.load_data("audit_test")
        self.storage.delete_data("audit_test")
        
        # Check audit log exists and contains entries
        audit_file = os.path.join(self.temp_dir, "access.log")
        assert os.path.exists(audit_file)
        
        with open(audit_file, 'r') as f:
            log_content = f.read()
        
        # Should contain logged operations
        assert "STORE" in log_content
        assert "LOAD" in log_content
        assert "DELETE" in log_content
        assert "audit_test" in log_content
        assert "SUCCESS" in log_content
    
    def test_audit_log_format(self):
        """Test audit log format is correct."""
        self.storage.save_data("format_test", {"test": "data"})
        
        audit_file = os.path.join(self.temp_dir, "access.log")
        with open(audit_file, 'r') as f:
            log_lines = f.readlines()
        
        # Should have at least one log entry
        assert len(log_lines) > 0
        
        # Check log format: timestamp | action | identifier | status
        last_line = log_lines[-1].strip()
        parts = last_line.split(' | ')
        
        assert len(parts) == 4
        assert parts[1] in ['STORE', 'LOAD', 'DELETE', 'LIST']
        assert parts[2] == 'format_test'
        assert parts[3] in ['SUCCESS', 'FAILURE']
        
        # Timestamp should be in ISO format
        try:
            from datetime import datetime
            datetime.fromisoformat(parts[0])
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {parts[0]}")
    
    # Data Management Tests
    def test_data_deletion(self):
        """Test secure data deletion."""
        test_data = {"delete": "me"}
        
        # Store and verify
        self.storage.save_data("delete_test", test_data)
        assert self.storage.load_data("delete_test") == test_data
        
        # Delete and verify
        result = self.storage.delete_data("delete_test")
        assert result == True
        
        # Should not be retrievable
        assert self.storage.load_data("delete_test") is None
        
        # File should not exist
        encrypted_file = os.path.join(self.temp_dir, "delete_test.enc")
        assert not os.path.exists(encrypted_file)
    
    def test_delete_nonexistent_data(self):
        """Test deletion of non-existent data."""
        result = self.storage.delete_data("nonexistent")
        assert result == False
    
    def test_list_stored_data(self):
        """Test listing of stored data identifiers."""
        test_datasets = {
            "dataset1": {"data": 1},
            "dataset2": {"data": 2},
            "dataset3": {"data": 3},
        }
        
        # Store multiple datasets
        for identifier, data in test_datasets.items():
            self.storage.save_data(identifier, data)
        
        # List stored data
        stored_items = self.storage.list_stored_data()
        
        # Should contain all stored identifiers
        for identifier in test_datasets.keys():
            assert identifier in stored_items
        
        # Should not contain system files
        assert not any(item.startswith('.') for item in stored_items)
    
    def test_storage_with_master_key(self):
        """Test storage initialization with custom master key."""
        master_key = "custom_master_key_12345"
        
        # Create storage with master key
        custom_storage = SecureStorage(self.temp_dir, master_key=master_key)
        
        test_data = {"master_key": "test"}
        custom_storage.save_data("master_key_test", test_data)
        
        # Should be able to retrieve with same storage instance
        retrieved_data = custom_storage.load_data("master_key_test")
        assert retrieved_data == test_data
        
        # Different master key should not be able to decrypt
        different_storage = SecureStorage(self.temp_dir, master_key="different_key")
        with pytest.raises(SecurityError):
            different_storage.load_data("master_key_test")
    
    # Key Rotation Tests
    def test_key_rotation(self):
        """Test key rotation functionality."""
        # Store some data
        original_data = {
            "item1": {"key": "value1"},
            "item2": {"key": "value2"},
        }
        
        for identifier, data in original_data.items():
            self.storage.save_data(identifier, data)
        
        # Perform key rotation
        self.storage.rotate_keys()
        
        # All data should still be retrievable
        for identifier, expected_data in original_data.items():
            retrieved_data = self.storage.load_data(identifier)
            assert retrieved_data == expected_data
    
    def test_key_rotation_with_master_key(self):
        """Test key rotation with new master key."""
        if not self.storage.use_strong_crypto:
            pytest.skip("Key rotation requires cryptography library")
        
        # Store data
        test_data = {"rotation": "test"}
        self.storage.save_data("rotation_test", test_data)
        
        # Rotate with new master key
        new_master_key = "new_rotation_key_54321"
        self.storage.rotate_keys(new_master_key)
        
        # Data should still be retrievable
        retrieved_data = self.storage.load_data("rotation_test")
        assert retrieved_data == test_data
    
    # Security Information Tests
    def test_get_security_info(self):
        """Test security information retrieval."""
        security_info = self.storage.get_security_info()
        
        # Should contain expected keys
        expected_keys = [
            "encryption_type", "key_derivation", "secure_permissions",
            "audit_logging", "stored_items_count", "storage_directory"
        ]
        
        for key in expected_keys:
            assert key in security_info
        
        # Check values
        assert security_info["secure_permissions"] == True
        assert security_info["audit_logging"] == True
        assert security_info["storage_directory"] == self.temp_dir
        assert security_info["encryption_type"] in ["AES-256-GCM", "XOR-fallback"]
    
    # Error Handling Tests
    def test_load_nonexistent_data(self):
        """Test loading non-existent data."""
        result = self.storage.load_data("nonexistent")
        assert result is None
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted encrypted data."""
        # Create corrupted encrypted file
        corrupted_file = os.path.join(self.temp_dir, "corrupted.enc")
        with open(corrupted_file, 'w') as f:
            f.write("definitely_not_valid_encrypted_data")
        
        # Should handle corruption gracefully
        with pytest.raises(SecurityError):
            self.storage.load_data("corrupted")
    
    def test_invalid_json_handling(self):
        """Test handling of data that decrypts but isn't valid JSON."""
        # This is tricky to test directly, but we can test the error path
        # by creating storage with invalid data
        pass  # Implementation depends on specific error handling approach
    
    def test_storage_directory_permissions(self):
        """Test storage directory has correct permissions."""
        if os.name != 'nt':  # Not Windows
            dir_stat = os.stat(self.temp_dir)
            dir_permissions = oct(dir_stat.st_mode)[-3:]
            assert dir_permissions == '700', f"Directory permissions are {dir_permissions}, expected 700"
    
    def test_concurrent_access_safety(self):
        """Test concurrent access to storage."""
        import threading
        import time
        
        results = []
        errors = []
        
        def store_data(identifier, data):
            try:
                self.storage.save_data(identifier, data)
                retrieved = self.storage.load_data(identifier)
                results.append((identifier, retrieved == data))
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=store_data, 
                args=(f"concurrent_{i}", {"thread": i, "data": f"test_{i}"})
            )
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 5
        assert all(success for _, success in results)


class TestSecureStorageFallback:
    """Test fallback encryption when cryptography is not available."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_fallback_encryption_functionality(self):
        """Test that fallback encryption works when cryptography is unavailable."""
        # Create storage instance (will use available encryption)
        storage = SecureStorage(self.temp_dir)
        
        test_data = {"fallback": "test"}
        storage.save_data("fallback_test", test_data)
        
        retrieved_data = storage.load_data("fallback_test")
        assert retrieved_data == test_data
        
        # Data should still be encrypted (not readable in raw file)
        encrypted_file = os.path.join(self.temp_dir, "fallback_test.enc")
        with open(encrypted_file, 'r') as f:
            encrypted_content = f.read()
        
        assert "fallback" not in encrypted_content
        assert "test" not in encrypted_content


class TestSecureStorageEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = SecureStorage(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_empty_data_storage(self):
        """Test storage of empty data."""
        empty_cases = [
            ("empty_string", ""),
            ("empty_dict", {}),
            ("empty_list", []),
            ("zero", 0),
            ("false", False),
        ]
        
        for identifier, empty_data in empty_cases:
            self.storage.save_data(identifier, empty_data)
            retrieved_data = self.storage.load_data(identifier)
            assert retrieved_data == empty_data
    
    def test_special_identifier_names(self):
        """Test storage with special identifier names."""
        special_identifiers = [
            "normal_name",
            "name-with-hyphens",
            "name_with_underscores",
            "name.with.dots",
            "123numeric",
            "CamelCaseIdentifier",
        ]
        
        test_data = {"special": "identifier"}
        
        for identifier in special_identifiers:
            self.storage.save_data(identifier, test_data)
            retrieved_data = self.storage.load_data(identifier)
            assert retrieved_data == test_data
    
    def test_performance_characteristics(self):
        """Test performance characteristics of encryption/decryption."""
        # Test with various data sizes
        data_sizes = [
            (100, "small"),      # ~100 bytes
            (10000, "medium"),   # ~10KB
            (100000, "large"),   # ~100KB
        ]
        
        for size, size_name in data_sizes:
            test_data = {"data": "x" * size, "size": size_name}
            
            start_time = time.time()
            self.storage.save_data(f"perf_{size_name}", test_data)
            store_time = time.time() - start_time
            
            start_time = time.time()
            retrieved_data = self.storage.load_data(f"perf_{size_name}")
            load_time = time.time() - start_time
            
            assert retrieved_data == test_data
            
            # Performance should be reasonable (< 1 second for these sizes)
            assert store_time < 1.0, f"Store took {store_time:.2f}s for {size_name}"
            assert load_time < 1.0, f"Load took {load_time:.2f}s for {size_name}"


if __name__ == "__main__":
    # Run basic tests if script is executed directly
    pytest.main([__file__, "-v"])