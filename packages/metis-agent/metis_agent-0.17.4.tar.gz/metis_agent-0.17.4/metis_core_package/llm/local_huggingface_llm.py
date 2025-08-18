"""
Local HuggingFace LLM implementation for Metis Agent.

This module provides integration with locally downloaded HuggingFace models
using the transformers library for inference.
"""
import os
import torch
from typing import List, Dict, Any, Optional
from .base import BaseLLM

try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        AutoModelForSeq2SeqLM,
        pipeline,
        BitsAndBytesConfig
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class LocalHuggingFaceLLM(BaseLLM):
    """
    Local HuggingFace LLM provider for running downloaded models locally.
    
    Supports running models locally using the transformers library.
    """
    
    def __init__(
        self, 
        model: str = "microsoft/DialoGPT-small", 
        api_key: Optional[str] = None,  # Not used but kept for interface compatibility
        device: str = "auto",
        load_in_8bit: bool = False,
        load_in_4bit: bool = False,
        max_length: int = 512,
        temperature: float = 0.7,
        **kwargs
    ):
        """
        Initialize Local HuggingFace LLM.
        
        Args:
            model: Model name or path (e.g., "microsoft/DialoGPT-small", "./my-model")
            api_key: Not used for local models but kept for compatibility
            device: Device to run on ("auto", "cpu", "cuda", "mps")
            load_in_8bit: Whether to load model in 8-bit precision
            load_in_4bit: Whether to load model in 4-bit precision
            max_length: Maximum sequence length for generation
            temperature: Temperature for generation
            **kwargs: Additional arguments
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers library is required for local HuggingFace models. "
                "Install with: pip install transformers torch"
            )
        
        self._model_name = model
        self.device = self._get_device(device)
        self.load_in_8bit = load_in_8bit
        self.load_in_4bit = load_in_4bit
        self.max_length = max_length
        self.temperature = temperature
        self._provider_name = "local_huggingface"
        
        # Initialize model and tokenizer
        self._load_model()
    
    def _get_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            print(f"Loading local HuggingFace model: {self._model_name}")
            
            # Configure quantization if requested
            quantization_config = None
            if self.load_in_4bit:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif self.load_in_8bit:
                quantization_config = BitsAndBytesConfig(load_in_8bit=True)
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self._model_name,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add pad token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Try to load as causal LM first (most common for chat models)
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self._model_name,
                    quantization_config=quantization_config,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if self.device in ["cuda", "mps"] else torch.float32,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                self.model_type = "causal"
            except Exception as e:
                print(f"Failed to load as causal LM, trying seq2seq: {e}")
                # Try seq2seq model
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self._model_name,
                    quantization_config=quantization_config,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if self.device in ["cuda", "mps"] else torch.float32,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                self.model_type = "seq2seq"
            
            # Move to device if not using device_map
            if self.device != "cuda" or quantization_config is None:
                self.model = self.model.to(self.device)
            
            self.model.eval()
            print(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model {self.model_name}: {e}")
    
    def _generate_text(self, prompt: str, max_new_tokens: int = 100) -> str:
        """Generate text using the loaded model."""
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=self.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode output
            if self.model_type == "causal":
                # For causal models, remove the input tokens
                generated_tokens = outputs[0][inputs.shape[1]:]
                response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            else:
                # For seq2seq models, decode the full output
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            return f"Error generating text: {e}"
    
    def complete(self, prompt: str) -> str:
        """
        Generate a completion for a text prompt.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated completion
        """
        return self._generate_text(prompt, max_new_tokens=200)
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response for a chat conversation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated response
        """
        try:
            # Format messages into a single prompt
            # This is a simple approach - more sophisticated models might need special formatting
            formatted_prompt = ""
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    formatted_prompt += f"System: {content}\n"
                elif role == "user":
                    formatted_prompt += f"User: {content}\n"
                elif role == "assistant":
                    formatted_prompt += f"Assistant: {content}\n"
            
            # Add the final assistant prompt
            formatted_prompt += "Assistant:"
            
            return self._generate_text(formatted_prompt, max_new_tokens=300)
            
        except Exception as e:
            return f"Error in chat: {e}"
    
    def chat_with_functions(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response for a chat conversation with function calling.
        Note: Most local models don't support function calling, falls back to regular chat.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated response
        """
        # Most local models don't support function calling, use regular chat
        return self.chat(messages)
    
    def embed(self, text: str) -> List[float]:
        """
        Generate an embedding for a text.
        Note: This requires a separate embedding model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # For now, return a simple hash-based embedding as fallback
            # In a real implementation, you'd want to use a dedicated embedding model
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            hash_hex = hash_obj.hexdigest()
            
            # Convert hex to float values (simple approach)
            embedding = []
            for i in range(0, len(hash_hex), 2):
                hex_pair = hash_hex[i:i+2]
                embedding.append(int(hex_pair, 16) / 255.0)
            
            # Pad to standard embedding size
            while len(embedding) < 384:
                embedding.append(0.0)
            
            return embedding[:384]
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 384
    
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
        return self._model_name
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        try:
            num_parameters = sum(p.numel() for p in self.model.parameters())
            return {
                "model_name": self._model_name,
                "model_type": self.model_type,
                "device": self.device,
                "num_parameters": num_parameters,
                "quantization": "4-bit" if self.load_in_4bit else "8-bit" if self.load_in_8bit else "none"
            }
        except Exception as e:
            return {"error": str(e)}
