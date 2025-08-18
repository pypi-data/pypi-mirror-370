"""
Base LLM interface for Metis Agent.

This module defines the base class that all LLM implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class BaseLLM(ABC):
    """
    Base class for LLM providers.
    Defines the interface that all LLM implementations must follow.
    """
    
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """
        Generate a completion for a text prompt.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated completion
        """
        pass
        
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response for a chat conversation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated response
        """
        pass
        
    @abstractmethod
    def chat_with_functions(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response for a chat conversation with function calling.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated response
        """
        pass
        
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Generate an embedding for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass
        
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the name of the LLM provider.
        
        Returns:
            Provider name
        """
        pass
        
    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the name of the model being used.
        
        Returns:
            Model name
        """
        pass