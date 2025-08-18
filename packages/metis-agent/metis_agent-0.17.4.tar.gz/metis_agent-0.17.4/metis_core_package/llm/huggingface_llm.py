"""
HuggingFace LLM provider for the Metis Agent Framework.
"""

import os
from typing import List, Dict, Any, Optional, Union
import requests
from .base import BaseLLM
from ..auth.api_key_manager import APIKeyManager

class HuggingFaceLLM(BaseLLM):
    """
    HuggingFace LLM implementation.
    Uses the HuggingFace Inference API.
    """
    
    def __init__(
        self, 
        model: str = "openai-community/gpt2", 
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize the HuggingFace LLM.
        
        Args:
            model: Model name
            api_key: HuggingFace API key (if None, will try to get from APIKeyManager)
            temperature: Temperature for generation
        """
        self._model = model
        self._temperature = temperature
        
        # Get API key if not provided
        if api_key is None:
            key_manager = APIKeyManager()
            api_key = key_manager.get_key("huggingface")
            
        if api_key is None:
            raise ValueError("HuggingFace API key not found. Please provide it or set it using APIKeyManager.")
            
        # Store API key
        self.api_key = api_key
        
        # Base URL for API calls
        self.api_url = "https://api-inference.huggingface.co/models/"
        
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the HuggingFace Inference API."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # First try without wait_for_model
        response = requests.post(
            f"{self.api_url}{endpoint}",
            headers=headers,
            json=payload
        )
        
        # If model is loading (503), try again with wait_for_model
        if response.status_code == 503:
            payload["options"] = {"wait_for_model": True}
            response = requests.post(
                f"{self.api_url}{endpoint}",
                headers=headers,
                json=payload
            )
        
        response.raise_for_status()
        return response.json()
        
    def complete(self, prompt: str) -> str:
        """Generate a completion for a text prompt."""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": self._temperature,
                    "max_new_tokens": 1000,
                    "return_full_text": False
                }
            }
            
            result = self._make_request(self._model, payload)
            
            # Extract the generated text
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"].strip()
                else:
                    return str(result[0]).strip()
            else:
                return str(result).strip()
                
        except Exception as e:
            print(f"Error in HuggingFace completion: {e}")
            return f"Error: {str(e)}"
        
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response for a chat conversation."""
        try:
            # Format messages for the model
            # This is a simplified approach - different models may require different formats
            formatted_prompt = ""
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    formatted_prompt += f"<|system|>\n{content}\n"
                elif role == "user":
                    formatted_prompt += f"<|user|>\n{content}\n"
                elif role == "assistant":
                    formatted_prompt += f"<|assistant|>\n{content}\n"
            
            # Add the final assistant prompt
            formatted_prompt += "<|assistant|>\n"
            
            # Make the request
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "temperature": self._temperature,
                    "max_new_tokens": 1000,
                    "return_full_text": False
                }
            }
            
            result = self._make_request(self._model, payload)
            
            # Extract the generated text
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"].strip()
                else:
                    return str(result[0]).strip()
            else:
                return str(result).strip()
                
        except Exception as e:
            print(f"Error in HuggingFace chat: {e}")
            return f"Error: {str(e)}"
        
    def chat_with_functions(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response for a chat conversation with function calling."""
        # HuggingFace doesn't have a standard function calling API
        # For simplicity, we'll just use regular chat
        return self.chat(messages)
        
    def embed(self, text: str) -> List[float]:
        """Generate an embedding for a text."""
        try:
            # Use a sentence-transformers model for embeddings
            embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
            
            payload = {
                "inputs": text
            }
            
            result = self._make_request(embedding_model, payload)
            
            # The result should be a list of embeddings (one per input)
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            else:
                # Return a zero vector as fallback
                return [0.0] * 384  # Default embedding size for all-MiniLM-L6-v2
                
        except Exception as e:
            print(f"Error in HuggingFace embedding: {e}")
            # Return a zero vector as fallback
            return [0.0] * 384  # Default embedding size for all-MiniLM-L6-v2
        
    @property
    def provider_name(self) -> str:
        """Get the name of the LLM provider."""
        return "huggingface"
        
    @property
    def model_name(self) -> str:
        """Get the name of the model being used."""
        return self._model