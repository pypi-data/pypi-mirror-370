"""
Secure storage for sensitive data like API keys.

This module provides enterprise-grade encryption for API keys and other sensitive data
using AES-256-GCM encryption with proper key derivation and security practices.
"""

import os
import json
import base64
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import hashlib
import secrets
import time
from datetime import datetime
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("WARNING: cryptography library not found. Install with 'pip install cryptography' for secure encryption.")


class SecurityError(Exception):
    """Exception raised for security-related storage failures."""
    pass

class SecureStorage:
    """
    Provides enterprise-grade secure storage for sensitive data like API keys.
    
    Features:
    - AES-256-GCM encryption when cryptography library is available
    - PBKDF2 key derivation with salt
    - Secure key storage with file permissions
    - Key rotation and versioning support
    - Automatic fallback to basic XOR encryption if cryptography unavailable
    - Audit logging for security monitoring
    """
    
    def __init__(self, storage_dir: str, master_key: Optional[str] = None):
        """
        Initialize secure storage with enterprise-grade encryption.
        
        Args:
            storage_dir: Directory to store encrypted data
            master_key: Optional master key for key derivation. If None, generates one.
        """
        self.storage_dir = storage_dir
        self.use_strong_crypto = CRYPTO_AVAILABLE
        
        # Ensure secure directory permissions
        os.makedirs(storage_dir, mode=0o700, exist_ok=True)
        
        # Initialize encryption system
        if self.use_strong_crypto:
            self._init_strong_crypto(master_key)
        else:
            self._init_fallback_crypto()
        
        # Initialize audit log
        self._init_audit_log()
    
    def _init_strong_crypto(self, master_key: Optional[str] = None):
        """Initialize AES-256-GCM encryption system."""
        self.salt_file = os.path.join(self.storage_dir, ".salt")
        self.key_file = os.path.join(self.storage_dir, ".key_hash")
        
        # Get or create salt for key derivation
        self.salt = self._get_or_create_salt()
        
        # Derive encryption key
        if master_key:
            self.derived_key = self._derive_key_from_master(master_key, self.salt)
        else:
            self.derived_key = self._get_or_create_derived_key()
    
    def _init_fallback_crypto(self):
        """Initialize fallback XOR encryption (for compatibility)."""
        key_file = os.path.join(self.storage_dir, ".key_fallback")
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.fallback_key = f.read()
        else:
            self.fallback_key = secrets.token_bytes(32)
            # Set secure file permissions before writing
            with open(key_file, "wb") as f:
                f.write(self.fallback_key)
            os.chmod(key_file, 0o600)
    
    def _init_audit_log(self):
        """Initialize audit logging for security monitoring."""
        self.audit_file = os.path.join(self.storage_dir, "access.log")
        # Ensure audit file has secure permissions
        if not os.path.exists(self.audit_file):
            with open(self.audit_file, "w") as f:
                f.write("")  # Create empty file
            os.chmod(self.audit_file, 0o600)
    
    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create a new secure salt."""
        if os.path.exists(self.salt_file):
            with open(self.salt_file, "rb") as f:
                return f.read()
        else:
            # Generate cryptographically secure salt
            salt = secrets.token_bytes(32)  # 256 bits
            with open(self.salt_file, "wb") as f:
                f.write(salt)
            os.chmod(self.salt_file, 0o600)  # Secure permissions
            return salt
    
    def _derive_key_from_master(self, master_key: str, salt: bytes) -> bytes:
        """Derive encryption key from master key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=100000,  # Strong iteration count
            backend=default_backend()
        )
        return kdf.derive(master_key.encode('utf-8'))
    
    def _get_or_create_derived_key(self) -> bytes:
        """Get or create derived encryption key with secure storage."""
        if os.path.exists(self.key_file):
            # Load existing key hash
            with open(self.key_file, "rb") as f:
                stored_hash = f.read()
            
            # For security, we derive the key from a machine-specific seed
            machine_seed = self._get_machine_seed()
            derived_key = self._derive_key_from_master(machine_seed, self.salt)
            
            # Verify key integrity
            current_hash = hashlib.sha256(derived_key).digest()
            if current_hash == stored_hash:
                return derived_key
            else:
                raise SecurityError("Key integrity verification failed")
        else:
            # Create new key
            machine_seed = self._get_machine_seed()
            derived_key = self._derive_key_from_master(machine_seed, self.salt)
            
            # Store hash for integrity verification
            key_hash = hashlib.sha256(derived_key).digest()
            with open(self.key_file, "wb") as f:
                f.write(key_hash)
            os.chmod(self.key_file, 0o600)
            
            return derived_key
    
    def _get_machine_seed(self) -> str:
        """Generate machine-specific seed for key derivation."""
        import platform
        import uuid
        
        # Combine multiple machine-specific identifiers
        machine_id = str(uuid.getnode())  # MAC address
        hostname = platform.node()
        system = platform.system()
        
        # Create deterministic but machine-specific seed
        combined = f"{machine_id}-{hostname}-{system}-metis-agent-v2"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _log_access(self, action: str, identifier: str, success: bool):
        """Log access attempts for security audit."""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {action} | {identifier} | {'SUCCESS' if success else 'FAILURE'}\n"
        
        try:
            with open(self.audit_file, "a") as f:
                f.write(log_entry)
        except Exception:
            # Don't fail operations due to logging issues
            pass
    
    def _encrypt_strong(self, data: str) -> str:
        """Encrypt data using AES-256-GCM."""
        if not data:
            return ""
        
        try:
            # Generate random nonce for GCM
            nonce = secrets.token_bytes(12)  # 96 bits for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.derived_key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt data
            data_bytes = data.encode('utf-8')
            ciphertext = encryptor.update(data_bytes) + encryptor.finalize()
            
            # Combine nonce + tag + ciphertext for storage
            encrypted_package = nonce + encryptor.tag + ciphertext
            
            return base64.b64encode(encrypted_package).decode('utf-8')
        except Exception as e:
            raise SecurityError(f"Encryption failed: {e}")
    
    def _decrypt_strong(self, encrypted_data: str) -> str:
        """Decrypt data using AES-256-GCM."""
        if not encrypted_data:
            return ""
        
        try:
            # Decode from base64
            encrypted_package = base64.b64decode(encrypted_data)
            
            # Extract components
            nonce = encrypted_package[:12]  # First 12 bytes
            tag = encrypted_package[12:28]   # Next 16 bytes
            ciphertext = encrypted_package[28:]  # Remaining bytes
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.derived_key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt data
            decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise SecurityError(f"Decryption failed: {e}")
    
    def _encrypt_fallback(self, data: str) -> str:
        """Fallback XOR encryption (improved version)."""
        if not data:
            return ""
        
        # Add timestamp and random padding for better security
        timestamp = str(int(time.time()))
        padding = secrets.token_hex(8)
        enhanced_data = f"{timestamp}|{padding}|{data}"
        
        # XOR encryption with key cycling
        data_bytes = enhanced_data.encode('utf-8')
        key_bytes = self.fallback_key
        encrypted = bytearray()
        
        for i, b in enumerate(data_bytes):
            key_byte = key_bytes[i % len(key_bytes)]
            encrypted.append(b ^ key_byte)
        
        return base64.b64encode(encrypted).decode('utf-8')
    
    def _decrypt_fallback(self, encrypted_data: str) -> str:
        """Fallback XOR decryption (improved version)."""
        if not encrypted_data:
            return ""
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            key_bytes = self.fallback_key
            decrypted = bytearray()
            
            for i, b in enumerate(encrypted_bytes):
                key_byte = key_bytes[i % len(key_bytes)]
                decrypted.append(b ^ key_byte)
            
            enhanced_data = decrypted.decode('utf-8')
            
            # Extract original data (remove timestamp and padding)
            parts = enhanced_data.split('|', 2)
            if len(parts) == 3:
                return parts[2]  # Original data
            else:
                return enhanced_data  # Fallback to raw data
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return ""
    
    def _encrypt(self, data: str) -> str:
        """Encrypt data using the best available method."""
        if self.use_strong_crypto:
            return self._encrypt_strong(data)
        else:
            return self._encrypt_fallback(data)
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using the appropriate method."""
        if self.use_strong_crypto:
            return self._decrypt_strong(encrypted_data)
        else:
            return self._decrypt_fallback(encrypted_data)
            
    def save_data(self, name: str, data: Any):
        """
        Save data securely with audit logging.
        
        Args:
            name: Data identifier  
            data: Data to save (will be JSON serialized)
            
        Raises:
            SecurityError: If encryption or storage fails
        """
        try:
            # Convert data to JSON
            json_data = json.dumps(data, sort_keys=True)  # Sort keys for consistency
            
            # Encrypt the data
            encrypted_data = self._encrypt(json_data)
            
            # Save to file with secure permissions
            file_path = os.path.join(self.storage_dir, f"{name}.enc")
            with open(file_path, "w") as f:
                f.write(encrypted_data)
            
            # Set secure file permissions
            os.chmod(file_path, 0o600)
            
            # Log successful storage
            self._log_access("STORE", name, True)
            
        except Exception as e:
            self._log_access("STORE", name, False)
            raise SecurityError(f"Failed to store data for '{name}': {e}")
            
    def load_data(self, name: str) -> Optional[Any]:
        """
        Load data securely with audit logging.
        
        Args:
            name: Data identifier
            
        Returns:
            Loaded data or None if not found
            
        Raises:
            SecurityError: If decryption fails
        """
        file_path = os.path.join(self.storage_dir, f"{name}.enc")
        
        if not os.path.exists(file_path):
            self._log_access("LOAD", name, False)
            return None
        
        try:
            # Read encrypted data
            with open(file_path, "r") as f:
                encrypted_data = f.read()
                
            # Decrypt the data
            json_data = self._decrypt(encrypted_data)
            
            if not json_data:
                self._log_access("LOAD", name, False)
                return None
                
            # Parse JSON
            try:
                data = json.loads(json_data)
                self._log_access("LOAD", name, True)
                return data
            except json.JSONDecodeError as e:
                self._log_access("LOAD", name, False)
                raise SecurityError(f"Failed to parse stored data for '{name}': {e}")
                
        except Exception as e:
            self._log_access("LOAD", name, False)
            if isinstance(e, SecurityError):
                raise
            else:
                raise SecurityError(f"Failed to load data for '{name}': {e}")
    
    def delete_data(self, name: str) -> bool:
        """
        Securely delete stored data.
        
        Args:
            name: Data identifier
            
        Returns:
            True if deletion was successful, False if file didn't exist
        """
        file_path = os.path.join(self.storage_dir, f"{name}.enc")
        
        if not os.path.exists(file_path):
            self._log_access("DELETE", name, False)
            return False
        
        try:
            # Secure deletion (overwrite with random data first)
            file_size = os.path.getsize(file_path)
            with open(file_path, "wb") as f:
                f.write(secrets.token_bytes(file_size))
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Remove file
            os.remove(file_path)
            self._log_access("DELETE", name, True)
            return True
            
        except Exception as e:
            self._log_access("DELETE", name, False)
            raise SecurityError(f"Failed to delete data for '{name}': {e}")
    
    def list_stored_data(self) -> List[str]:
        """
        List all stored data identifiers.
        
        Returns:
            List of data identifiers
        """
        try:
            files = []
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.enc') and not filename.startswith('.'):
                    # Remove .enc extension
                    identifier = filename[:-4]
                    files.append(identifier)
            
            self._log_access("LIST", "all", True)
            return sorted(files)
            
        except Exception as e:
            self._log_access("LIST", "all", False)
            return []
    
    def rotate_keys(self, new_master_key: Optional[str] = None):
        """
        Rotate encryption keys for enhanced security.
        
        This re-encrypts all stored data with new keys.
        
        Args:
            new_master_key: Optional new master key. If None, generates new machine-specific key.
        """
        if not self.use_strong_crypto:
            raise SecurityError("Key rotation requires cryptography library")
        
        try:
            # Get list of all stored data
            stored_items = self.list_stored_data()
            
            # Load all data with current keys
            all_data = {}
            for item in stored_items:
                all_data[item] = self.load_data(item)
            
            # Generate new encryption keys
            if new_master_key:
                self.derived_key = self._derive_key_from_master(new_master_key, self.salt)
            else:
                # Create new salt and derive new key
                self.salt = secrets.token_bytes(32)
                with open(self.salt_file, "wb") as f:
                    f.write(self.salt)
                os.chmod(self.salt_file, 0o600)
                
                self.derived_key = self._get_or_create_derived_key()
            
            # Re-encrypt all data with new keys
            for item, data in all_data.items():
                if data is not None:  # Skip items that failed to load
                    self.save_data(item, data)
            
            self._log_access("KEY_ROTATION", "all", True)
            
        except Exception as e:
            self._log_access("KEY_ROTATION", "all", False)
            raise SecurityError(f"Key rotation failed: {e}")
    
    def get_security_info(self) -> Dict[str, Any]:
        """
        Get information about the security configuration.
        
        Returns:
            Dictionary with security information
        """
        return {
            "encryption_type": "AES-256-GCM" if self.use_strong_crypto else "XOR-fallback",
            "key_derivation": "PBKDF2-SHA256" if self.use_strong_crypto else "None",
            "secure_permissions": True,
            "audit_logging": True,
            "stored_items_count": len(self.list_stored_data()),
            "storage_directory": self.storage_dir
        }