"""
Credentials manager for the Metis Agent Framework.
"""

from typing import Dict, Any, Optional
from .api_key_manager import APIKeyManager

class CredentialsManager:
    """
    High-level interface for managing credentials for the agent.
    Handles API keys and other authentication methods.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the credentials manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.api_key_manager = APIKeyManager(config_dir)
        
    def configure_llm(self, provider: str, api_key: str):
        """
        Configure an LLM provider.
        
        Args:
            provider: LLM provider name (e.g., 'openai', 'groq', 'anthropic')
            api_key: API key for the provider
        """
        self.api_key_manager.set_key(provider, api_key)
        
    def configure_tool(self, tool_name: str, api_key: str):
        """
        Configure a tool that requires an API key.
        
        Args:
            tool_name: Tool name (e.g., 'google_search', 'firecrawl')
            api_key: API key for the tool
        """
        self.api_key_manager.set_key(tool_name, api_key)
        
    def get_llm_key(self, provider: str) -> Optional[str]:
        """
        Get an API key for an LLM provider.
        
        Args:
            provider: LLM provider name
            
        Returns:
            API key or None if not found
        """
        return self.api_key_manager.get_key(provider)
        
    def get_tool_key(self, tool_name: str) -> Optional[str]:
        """
        Get an API key for a tool.
        
        Args:
            tool_name: Tool name
            
        Returns:
            API key or None if not found
        """
        return self.api_key_manager.get_key(tool_name)
        
    def list_configured_services(self) -> Dict[str, list]:
        """
        List all configured services.
        
        Returns:
            Dictionary with lists of configured LLMs and tools
        """
        services = self.api_key_manager.list_services()
        
        # Categorize services
        llms = []
        tools = []
        
        for service in services:
            if service in ['openai', 'groq', 'anthropic', 'huggingface']:
                llms.append(service)
            else:
                tools.append(service)
                
        return {
            'llms': llms,
            'tools': tools
        }