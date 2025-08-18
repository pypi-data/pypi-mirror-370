"""
OpenAI LLM implementation for Metis Agent.

This module provides an implementation of the BaseLLM interface for OpenAI.
"""
import os
from typing import List, Dict, Any, Optional, Union
from .base import BaseLLM
from ..auth.api_key_manager import APIKeyManager


class OpenAILLM(BaseLLM):
    """
    OpenAI LLM implementation.
    """
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize the OpenAI LLM.
        
        Args:
            model: Model name
            api_key: OpenAI API key (if None, will try to get from APIKeyManager)
            temperature: Temperature for generation
        """
        self._model = model
        self._temperature = temperature
        
        # Get API key if not provided
        if api_key is None:
            key_manager = APIKeyManager()
            api_key = key_manager.get_key("openai")
            
        if api_key is None:
            # For testing purposes, use a mock implementation
            self._use_mock = True
            print("- OpenAI API key not found. Using mock implementation.")
        else:
            self._use_mock = False
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
            except ImportError:
                print("- OpenAI package not found. Using mock implementation.")
                self._use_mock = True
        
    def complete(self, prompt: str) -> str:
        """Generate a completion for a text prompt."""
        if self._use_mock:
            return self._mock_complete(prompt)
            
        response = self.client.completions.create(
            model=self._model,
            prompt=prompt,
            temperature=self._temperature,
            max_tokens=1000
        )
        return response.choices[0].text.strip()
        
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response for a chat conversation."""
        if self._use_mock:
            return self._mock_chat(messages)
            
        response = self.client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature
        )
        return response.choices[0].message.content.strip()
        
    def chat_with_functions(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response for a chat conversation with function calling."""
        if self._use_mock:
            return self._mock_chat(messages)
            
        response = self.client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature
        )
        return response.choices[0].message.content.strip()
        
    def embed(self, text: str) -> List[float]:
        """Generate an embedding for a text."""
        if self._use_mock:
            return self._mock_embed(text)
            
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
        
    @property
    def provider_name(self) -> str:
        """Get the name of the LLM provider."""
        return "openai"
        
    @property
    def model_name(self) -> str:
        """Get the name of the model being used."""
        return self._model
        
    def _mock_complete(self, prompt: str) -> str:
        """Mock implementation of complete for testing."""
        if "classify" in prompt.lower():
            if "?" in prompt:
                return "question"
            else:
                return "task"
                
        elif "break down" in prompt.lower():
            # Simple task breakdown example for testing
            return """
            Research current market trends
            Compile key statistics
            Summarize findings in a report
            """
            
        return f"Mock response to: {prompt[:50]}..."
        
    def _mock_chat(self, messages: List[Dict[str, str]]) -> str:
        """Mock implementation of chat for testing."""
        # Extract the last user message
        user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')
        return self._mock_complete(user_message)
        
    def _mock_embed(self, text: str) -> List[float]:
        """Mock implementation of embed for testing."""
        # Return a fixed-size vector of zeros
        return [0.0] * 1536