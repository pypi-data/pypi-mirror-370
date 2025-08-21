"""
Ollama LLM implementation for Metis Agent.

This module provides integration with Ollama for running local LLM models.
"""
import requests
import json
from typing import List, Dict, Any, Optional
from .base import BaseLLM


class OllamaLLM(BaseLLM):
    """
    Ollama LLM provider for local model inference.
    
    Supports running local models through Ollama API.
    """
    
    def __init__(
        self, 
        model: str = "tinydolphin", 
        base_url: str = "http://localhost:11434",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Ollama LLM.
        
        Args:
            model: Model name (e.g., "tinydolphin", "llama2", "codellama", "mistral")
            base_url: Ollama server URL
            api_key: Not used for Ollama but kept for interface compatibility
            **kwargs: Additional arguments
        """
        self.model = model
        self.base_url = base_url.rstrip('/')
        self._provider_name = "ollama"
        
        # Test connection
        try:
            self._test_connection()
        except Exception as e:
            raise ConnectionError(f"Could not connect to Ollama at {base_url}: {e}")
    
    def _test_connection(self):
        """Test connection to Ollama server."""
        response = requests.get(f"{self.base_url}/api/tags", timeout=5)
        response.raise_for_status()
        
        # Check if model is available
        models = response.json().get("models", [])
        model_names = [m["name"].split(":")[0] for m in models]
        
        if self.model not in model_names:
            available = ", ".join(model_names) if model_names else "none"
            raise ValueError(
                f"Model '{self.model}' not found in Ollama. "
                f"Available models: {available}. "
                f"Pull the model with: ollama pull {self.model}"
            )
    
    def complete(self, prompt: str) -> str:
        """
        Generate a completion for a text prompt.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated completion
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response for a chat conversation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated response
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
    def chat_with_functions(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response for a chat conversation with function calling.
        Note: Ollama doesn't support function calling, falls back to regular chat.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated response
        """
        # Ollama doesn't support function calling, use regular chat
        return self.chat(messages)
    
    def embed(self, text: str) -> List[float]:
        """
        Generate an embedding for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
        except requests.exceptions.RequestException as e:
            # If embeddings fail, return empty list
            print(f"Warning: Ollama embedding failed: {e}")
            return []
    
    @property
    def provider_name(self) -> str:
        """
        Get the name of the LLM provider.
        
        Returns:
            Provider name
        """
        return self._provider_name
    
    @property
    def model_name(self) -> str:
        """
        Get the name of the model being used.
        
        Returns:
            Model name
        """
        return self.model
    
    def list_models(self) -> List[str]:
        """
        List available models in Ollama.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not list Ollama models: {e}")
            return []
