"""
LLM Factory for Metis Agent.

This module provides a factory for creating LLM instances.
"""
from typing import Optional, Dict, Any
from .base import BaseLLM


class LLMFactory:
    """
    Factory for creating LLM instances.
    """
    
    @staticmethod
    def create(
        provider: str, 
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseLLM:
        """
        Create an LLM instance.
        
        Args:
            provider: LLM provider name
            model: Model name (if None, uses default for provider)
            api_key: API key (if None, tries to get from APIKeyManager)
            **kwargs: Additional arguments for the LLM
            
        Returns:
            LLM instance
        """
        provider = provider.lower()
        
        if provider == "openai":
            from .openai_llm import OpenAILLM
            return OpenAILLM(model=model or "gpt-4o", api_key=api_key, **kwargs)
        elif provider == "groq":
            from .groq_llm import GroqLLM
            return GroqLLM(model=model or "openai/gpt-oss-20b", api_key=api_key, **kwargs)
        elif provider == "anthropic":
            from .anthropic_llm import AnthropicLLM
            return AnthropicLLM(model=model or "claude-3-opus-20240229", api_key=api_key, **kwargs)
        elif provider == "huggingface":
            from .local_huggingface_llm import LocalHuggingFaceLLM
            # Extract HuggingFace-specific config from kwargs if available
            device = kwargs.get("device", "auto")
            quantization = kwargs.get("quantization", "none")
            max_length = kwargs.get("max_length", 512)
            
            # Convert quantization setting to boolean flags
            load_in_8bit = quantization == "8bit"
            load_in_4bit = quantization == "4bit"
            
            return LocalHuggingFaceLLM(
                model=model or "microsoft/DialoGPT-small", 
                device=device,
                load_in_8bit=load_in_8bit,
                load_in_4bit=load_in_4bit,
                max_length=max_length,
                **{k: v for k, v in kwargs.items() if k not in ["device", "quantization", "max_length"]}
            )
        elif provider == "ollama":
            from .ollama_llm import OllamaLLM
            base_url = kwargs.get("base_url", "http://localhost:11434")
            return OllamaLLM(model=model or "tinydolphin", base_url=base_url, **kwargs)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}. Supported providers: openai, groq, anthropic, huggingface, ollama")