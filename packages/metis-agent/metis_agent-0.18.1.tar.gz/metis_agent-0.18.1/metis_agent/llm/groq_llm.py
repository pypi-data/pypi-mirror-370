"""
Groq LLM provider for the Metis Agent Framework.
"""

import os
from typing import List, Dict, Any, Optional, Union
from groq import Groq
from .base import BaseLLM
from ..auth.api_key_manager import APIKeyManager

class GroqLLM(BaseLLM):
    """
    Groq LLM implementation.
    """
    
    def __init__(
        self, 
        model: str = "openai/gpt-oss-20b", 
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize the Groq LLM.
        
        Args:
            model: Model name
            api_key: Groq API key (if None, will try to get from APIKeyManager)
            temperature: Temperature for generation
        """
        self._model = model
        self._temperature = temperature
        
        # Get API key if not provided
        if api_key is None:
            key_manager = APIKeyManager()
            api_key = key_manager.get_key("groq")
            
        if api_key is None:
            raise ValueError("Groq API key not found. Please provide it or set it using APIKeyManager.")
            
        # Initialize client
        self.client = Groq(api_key=api_key)
        
    def complete(self, prompt: str) -> str:
        """Generate a completion for a text prompt."""
        try:
            # Groq doesn't have a completions endpoint, so we use chat
            response = self.client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature
            )
            content = response.choices[0].message.content
            if content is None:
                return "Error: Received empty response from Groq"
            return content.strip()
        except Exception as e:
            print(f"Error in Groq completion: {e}")
            return f"Error: {str(e)}"
        
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response for a chat conversation."""
        try:
            response = self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature
            )
            content = response.choices[0].message.content
            if content is None:
                return "Error: Received empty response from Groq"
            return content.strip()
        except Exception as e:
            print(f"Error in Groq chat: {e}")
            return f"Error: {str(e)}"
        
    def chat_with_functions(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response for a chat conversation with function calling."""
        # Groq doesn't support function calling yet, so we use regular chat
        return self.chat(messages)
        
    def embed(self, text: str) -> List[float]:
        """Generate an embedding for a text."""
        # Groq doesn't have an embeddings endpoint yet, so we return a dummy embedding
        # In a real implementation, you might want to use another provider for embeddings
        raise NotImplementedError("Groq does not support embeddings yet")
        
    @property
    def provider_name(self) -> str:
        """Get the name of the LLM provider."""
        return "groq"
        
    @property
    def model_name(self) -> str:
        """Get the name of the model being used."""
        return self._model