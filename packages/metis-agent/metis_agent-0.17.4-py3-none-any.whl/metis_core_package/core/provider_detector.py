"""
Provider Detection System for Metis Agent

Automatically detects available API providers based on configured keys
and provides smart fallbacks for agent creation.
"""

import os
from typing import Dict, List, Optional, Set
from ..auth.api_key_manager import APIKeyManager


class ProviderDetector:
    """
    Detects available LLM providers based on configured API keys
    and provides intelligent fallback recommendations.
    """
    
    # Define provider requirements and capabilities
    PROVIDER_INFO = {
        "groq": {
            "requires_key": True,
            "env_vars": ["GROQ_API_KEY"],
            "default_model": "llama-3.1-70b-versatile",
            "capabilities": ["coding", "research", "general"],
            "speed": "fast",
            "cost": "free_tier"
        },
        "openai": {
            "requires_key": True,
            "env_vars": ["OPENAI_API_KEY"],
            "default_model": "gpt-4o",
            "capabilities": ["coding", "research", "general", "advanced"],
            "speed": "medium", 
            "cost": "paid"
        },
        "anthropic": {
            "requires_key": True,
            "env_vars": ["ANTHROPIC_API_KEY"],
            "default_model": "claude-3-5-sonnet-20241022",
            "capabilities": ["coding", "research", "general", "reasoning"],
            "speed": "medium",
            "cost": "paid"
        },
        "huggingface": {
            "requires_key": False,  # Optional for many models
            "env_vars": ["HUGGINGFACE_API_KEY", "HF_TOKEN"],
            "default_model": "microsoft/DialoGPT-small",
            "capabilities": ["general", "specialized"],
            "speed": "variable",
            "cost": "free_many"
        },
        "ollama": {
            "requires_key": False,
            "env_vars": [],
            "default_model": "tinydolphin",
            "capabilities": ["coding", "general", "local"],
            "speed": "variable",
            "cost": "free_local"
        }
    }
    
    def __init__(self):
        """Initialize the provider detector."""
        self.api_key_manager = APIKeyManager()
        
    def get_available_providers(self) -> Dict[str, Dict]:
        """
        Get all available providers based on API keys and environment.
        
        Returns:
            Dictionary of available providers with their info
        """
        available = {}
        
        for provider, info in self.PROVIDER_INFO.items():
            if self._is_provider_available(provider):
                available[provider] = {
                    **info,
                    "source": self._get_key_source(provider)
                }
                
        return available
    
    def _is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available."""
        info = self.PROVIDER_INFO.get(provider)
        if not info:
            return False
            
        # Providers that don't require keys are always available
        if not info["requires_key"]:
            return True
            
        # Check API key manager
        if self.api_key_manager.get_key(provider):
            return True
            
        # Check environment variables
        for env_var in info["env_vars"]:
            if os.getenv(env_var):
                return True
                
        return False
    
    def _get_key_source(self, provider: str) -> str:
        """Determine where the API key comes from."""
        if self.api_key_manager.get_key(provider):
            return "key_manager"
            
        info = self.PROVIDER_INFO.get(provider, {})
        for env_var in info.get("env_vars", []):
            if os.getenv(env_var):
                return f"env:{env_var}"
                
        return "no_key_required"
    
    def get_recommended_provider(self, profile_type: str = "general") -> Optional[str]:
        """
        Get the best available provider for a given profile type.
        
        Args:
            profile_type: Type of profile (coding, research, general, etc.)
            
        Returns:
            Recommended provider name or None
        """
        available = self.get_available_providers()
        
        if not available:
            return None
            
        # Priority order based on profile type
        priority_maps = {
            "coding": ["groq", "openai", "anthropic", "ollama", "huggingface"],
            "research": ["openai", "anthropic", "groq", "huggingface", "ollama"],
            "general": ["groq", "openai", "anthropic", "ollama", "huggingface"],
            "data_science": ["anthropic", "openai", "groq", "huggingface", "ollama"]
        }
        
        priority = priority_maps.get(profile_type, priority_maps["general"])
        
        # Return first available provider from priority list
        for provider in priority:
            if provider in available:
                return provider
                
        # Fallback to any available provider
        return list(available.keys())[0] if available else None
    
    def get_fallback_config(self, original_provider: str, profile_type: str = "general") -> Optional[Dict]:
        """
        Get fallback configuration when original provider is unavailable.
        
        Args:
            original_provider: The originally requested provider
            profile_type: Type of profile needing fallback
            
        Returns:
            Fallback configuration or None
        """
        if self._is_provider_available(original_provider):
            return None  # No fallback needed
            
        recommended = self.get_recommended_provider(profile_type)
        if not recommended:
            return None
            
        return {
            "original_provider": original_provider,
            "fallback_provider": recommended,
            "fallback_model": self.PROVIDER_INFO[recommended]["default_model"],
            "reason": f"API key not found for {original_provider}"
        }
    
    def validate_provider_requirements(self, provider: str) -> Dict[str, any]:
        """
        Validate if all requirements are met for a provider.
        
        Args:
            provider: Provider to validate
            
        Returns:
            Validation result with status and details
        """
        result = {
            "valid": False,
            "provider": provider,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        if provider not in self.PROVIDER_INFO:
            result["errors"].append(f"Unknown provider: {provider}")
            available = list(self.get_available_providers().keys())
            if available:
                result["suggestions"].append(f"Available providers: {', '.join(available)}")
            return result
            
        info = self.PROVIDER_INFO[provider]
        
        if info["requires_key"]:
            has_key = self.api_key_manager.get_key(provider)
            has_env = any(os.getenv(var) for var in info["env_vars"])
            
            if not has_key and not has_env:
                result["errors"].append(f"No API key found for {provider}")
                result["suggestions"].extend([
                    f"Set API key: metis auth set {provider} YOUR_KEY",
                    f"Or set environment variable: {info['env_vars'][0]}"
                ])
                
                # Suggest alternatives
                alternatives = self.get_available_providers()
                if alternatives:
                    alt_names = list(alternatives.keys())
                    result["suggestions"].append(f"Available alternatives: {', '.join(alt_names)}")
                return result
        
        result["valid"] = True
        result["key_source"] = self._get_key_source(provider)
        return result
    
    def list_providers_with_status(self) -> Dict[str, Dict]:
        """
        List all providers with their availability status.
        
        Returns:
            Dictionary with provider status information
        """
        status = {}
        
        for provider, info in self.PROVIDER_INFO.items():
            validation = self.validate_provider_requirements(provider)
            status[provider] = {
                "available": validation["valid"],
                "info": info,
                "validation": validation
            }
            
        return status


def get_provider_detector() -> ProviderDetector:
    """Get global provider detector instance."""
    return ProviderDetector()