"""
Anthropic LLM provider for the Metis Agent Framework.
"""

import os
from typing import List, Dict, Any, Optional, Union
import anthropic
from .base import BaseLLM
from ..auth.api_key_manager import APIKeyManager

class AnthropicLLM(BaseLLM):
    """
    Anthropic LLM implementation.
    """
    
    def __init__(
        self, 
        model: str = "claude-3-opus-20240229", 
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize the Anthropic LLM.
        
        Args:
            model: Model name
            api_key: Anthropic API key (if None, will try to get from APIKeyManager)
            temperature: Temperature for generation
        """
        self._model = model
        self._temperature = temperature
        
        # Get API key if not provided
        if api_key is None:
            key_manager = APIKeyManager()
            api_key = key_manager.get_key("anthropic")
            
        if api_key is None:
            raise ValueError("Anthropic API key not found. Please provide it or set it using APIKeyManager.")
            
        # Initialize client
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def complete(self, prompt: str) -> str:
        """Generate a completion for a text prompt."""
        try:
            # Anthropic doesn't have a completions endpoint, so we use messages
            response = self.client.messages.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
                max_tokens=1000
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error in Anthropic completion: {e}")
            return f"Error: {str(e)}"
        
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response for a chat conversation."""
        try:
            # Convert messages to Anthropic format if needed
            anthropic_messages = []
            for msg in messages:
                role = msg["role"]
                # Map OpenAI roles to Anthropic roles
                if role == "system":
                    # For system messages, we'll add them as a user message with a special prefix
                    anthropic_messages.append({
                        "role": "user",
                        "content": f"<system>{msg['content']}</system>"
                    })
                elif role == "assistant":
                    anthropic_messages.append({
                        "role": "assistant",
                        "content": msg["content"]
                    })
                else:  # user or any other role
                    anthropic_messages.append({
                        "role": "user",
                        "content": msg["content"]
                    })
            
            response = self.client.messages.create(
                model=self._model,
                messages=anthropic_messages,
                temperature=self._temperature,
                max_tokens=1000
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error in Anthropic chat: {e}")
            return f"Error: {str(e)}"
        
    def chat_with_functions(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response for a chat conversation with function calling."""
        # Anthropic has tool use capabilities but with a different API
        # For simplicity, we'll just use regular chat for now
        return self.chat(messages)
        
    def embed(self, text: str) -> List[float]:
        """Generate an embedding for a text."""
        try:
            response = self.client.embeddings.create(
                model="claude-3-sonnet-20240229-embedding",
                input=text
            )
            return response.embedding
        except Exception as e:
            print(f"Error in Anthropic embedding: {e}")
            # Return a zero vector as fallback
            return [0.0] * 1024  # Default embedding size for Claude embeddings
        
    @property
    def provider_name(self) -> str:
        """Get the name of the LLM provider."""
        return "anthropic"
        
    @property
    def model_name(self) -> str:
        """Get the name of the model being used."""
        return self._model