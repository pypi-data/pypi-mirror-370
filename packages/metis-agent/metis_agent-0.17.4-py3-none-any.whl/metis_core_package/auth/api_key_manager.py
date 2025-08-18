"""
API key manager for the Metis Agent Framework.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from .secure_storage import SecureStorage, SecurityError

class APIKeyManager:
    """
    Manages API keys for various services used by the agent.
    Provides secure storage and retrieval of keys.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the API key manager.
        
        Args:
            config_dir: Directory to store configuration files. If None, uses ~/.metis_agent
        """
        if config_dir is None:
            self.config_dir = os.path.expanduser("~/.metis_agent")
        else:
            self.config_dir = config_dir
            
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Initialize secure storage
        self.secure_storage = SecureStorage(self.config_dir)
        
        # Load existing keys
        self.keys = self._load_keys()
    
    def _hash_key(self, key: str) -> str:
        """Generate a hash of the key for integrity verification."""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()
        
    def _load_keys(self) -> Dict[str, Any]:
        """Load API keys from secure storage"""
        try:
            return self.secure_storage.load_data("api_keys") or {}
        except Exception as e:
            print(f"Warning: Could not load API keys: {e}")
            return {}
            
    def _save_keys(self):
        """Save API keys to secure storage"""
        try:
            self.secure_storage.save_data("api_keys", self.keys)
        except Exception as e:
            print(f"Warning: Could not save API keys: {e}")
            
    def set_key(self, service: str, key: str):
        """
        Set an API key for a service with metadata tracking.
        
        Args:
            service: Service name (e.g., 'openai', 'groq', 'google')
            key: API key
            
        Raises:
            SecurityError: If key storage fails
        """
        if not key or not isinstance(key, str):
            raise ValueError("API key must be a non-empty string")
        
        if not service or not isinstance(service, str):
            raise ValueError("Service name must be a non-empty string")
        
        # Store key with metadata
        key_data = {
            "key": key,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "key_hash": self._hash_key(key)  # For integrity verification
        }
        
        self.keys[service] = key_data
        self._save_keys()
        
    def get_key(self, service: str) -> Optional[str]:
        """
        Get an API key for a service with usage tracking.
        
        Args:
            service: Service name
            
        Returns:
            API key or None if not found
        """
        # First check environment variables (these take precedence)
        env_var = f"{service.upper()}_API_KEY"
        if env_var in os.environ:
            return os.environ[env_var]
        
        # Then check stored keys
        key_data = self.keys.get(service)
        if key_data:
            # Handle both old format (string) and new format (dict with metadata)
            if isinstance(key_data, str):
                # Legacy format - upgrade to new format
                upgraded_data = {
                    "key": key_data,
                    "created_at": datetime.now().isoformat(),
                    "last_used": None,
                    "usage_count": 0,
                    "key_hash": self._hash_key(key_data)
                }
                self.keys[service] = upgraded_data
                self._save_keys()
                key_data = upgraded_data
            
            # Verify key integrity
            stored_hash = key_data.get("key_hash")
            current_hash = self._hash_key(key_data["key"])
            if stored_hash != current_hash:
                raise SecurityError(f"Key integrity verification failed for service: {service}")
            
            # Update usage statistics
            key_data["last_used"] = datetime.now().isoformat()
            key_data["usage_count"] = key_data.get("usage_count", 0) + 1
            self._save_keys()
            
            return key_data["key"]
        
        return None
        
    def has_key(self, service: str) -> bool:
        """
        Check if an API key exists for a service.
        
        Args:
            service: Service name
            
        Returns:
            True if key exists, False otherwise
        """
        return self.get_key(service) is not None
        
    def list_services(self) -> list:
        """
        List all services with stored API keys.
        
        Returns:
            List of service names
        """
        return list(self.keys.keys())
        
    def remove_key(self, service: str):
        """
        Remove an API key for a service.
        
        Args:
            service: Service name
        """
        if service in self.keys:
            del self.keys[service]
            self._save_keys()
    
    def get_key_info(self, service: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata information about a stored API key.
        
        Args:
            service: Service name
            
        Returns:
            Dictionary with key metadata (without the actual key) or None
        """
        key_data = self.keys.get(service)
        if key_data and isinstance(key_data, dict):
            # Return metadata without the actual key for security
            return {
                "service": service,
                "created_at": key_data.get("created_at"),
                "last_used": key_data.get("last_used"),
                "usage_count": key_data.get("usage_count", 0),
                "has_key": True,
                "key_length": len(key_data.get("key", "")),
                "key_prefix": key_data.get("key", "")[:8] + "..." if key_data.get("key") else ""
            }
        elif key_data:  # Legacy string format
            return {
                "service": service,
                "created_at": "unknown",
                "last_used": "unknown", 
                "usage_count": 0,
                "has_key": True,
                "key_length": len(key_data),
                "key_prefix": key_data[:8] + "..." if key_data else "",
                "legacy_format": True
            }
        return None
    
    def list_services_with_info(self) -> List[Dict[str, Any]]:
        """
        List all services with their metadata.
        
        Returns:
            List of dictionaries with service information
        """
        services_info = []
        for service in self.keys.keys():
            info = self.get_key_info(service)
            if info:
                services_info.append(info)
        return services_info
    
    def rotate_keys(self):
        """
        Rotate the encryption keys for all stored API keys.
        This re-encrypts all keys with new encryption keys.
        
        Raises:
            SecurityError: If key rotation fails
        """
        try:
            self.secure_storage.rotate_keys()
        except Exception as e:
            raise SecurityError(f"Key rotation failed: {e}")
    
    def get_security_info(self) -> Dict[str, Any]:
        """
        Get security information about the key storage system.
        
        Returns:
            Dictionary with security configuration details
        """
        storage_info = self.secure_storage.get_security_info()
        
        return {
            **storage_info,
            "total_services": len(self.keys),
            "services": [info["service"] for info in self.list_services_with_info()],
            "config_directory": self.config_dir
        }
    
    def validate_all_keys(self) -> Dict[str, bool]:
        """
        Validate integrity of all stored keys.
        
        Returns:
            Dictionary mapping service names to validation results
        """
        validation_results = {}
        
        for service, key_data in self.keys.items():
            try:
                if isinstance(key_data, dict):
                    stored_hash = key_data.get("key_hash")
                    current_hash = self._hash_key(key_data["key"])
                    validation_results[service] = (stored_hash == current_hash)
                else:
                    # Legacy format - always consider valid
                    validation_results[service] = True
            except Exception:
                validation_results[service] = False
        
        return validation_results
    
    def cleanup_legacy_keys(self):
        """
        Upgrade all legacy string-format keys to the new metadata format.
        """
        updated = False
        
        for service, key_data in self.keys.items():
            if isinstance(key_data, str):
                # Convert to new format
                upgraded_data = {
                    "key": key_data,
                    "created_at": datetime.now().isoformat(),
                    "last_used": None,
                    "usage_count": 0,
                    "key_hash": self._hash_key(key_data)
                }
                self.keys[service] = upgraded_data
                updated = True
        
        if updated:
            self._save_keys()