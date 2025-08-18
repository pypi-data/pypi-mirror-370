"""
LLM interface for the Metis Agent Framework.
Provides a unified interface to multiple LLM providers.
"""
from typing import Optional, Dict, Any, List
from ..llm.factory import LLMFactory
from ..llm.base import BaseLLM
from ..auth.api_key_manager import APIKeyManager

# Global LLM instance
_llm_instance = None

def configure_llm(
    provider: str, 
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
):
    """
    Configure the global LLM instance.
    
    Args:
        provider: LLM provider name
        model: Model name
        api_key: API key
        **kwargs: Additional arguments for the LLM
    """
    global _llm_instance
    _llm_instance = LLMFactory.create(provider, model, api_key, **kwargs)
    
def get_llm(config=None) -> BaseLLM:
    """
    Get the global LLM instance.
    If not configured, tries to create one using available API keys or config.
    
    Args:
        config: Optional AgentConfig instance to get provider preferences
    
    Returns:
        LLM instance
    """
    global _llm_instance
    
    if _llm_instance is None:
        key_manager = APIKeyManager()
        
        # Get provider preference from config if available
        preferred_provider = None
        preferred_model = None
        
        if config:
            preferred_provider = config.get("llm_provider", "groq")
            preferred_model = config.get("llm_model")
        
        # Try preferred provider first if specified and has key (or is ollama/huggingface)
        if preferred_provider and (key_manager.has_key(preferred_provider) or preferred_provider in ["ollama", "huggingface"]):
            try:
                kwargs = {}
                if preferred_provider == "ollama" and config:
                    kwargs["base_url"] = config.get("ollama_base_url", "http://localhost:11434")
                elif preferred_provider == "huggingface" and config:
                    kwargs["device"] = config.get("huggingface_device", "auto")
                    kwargs["quantization"] = config.get("huggingface_quantization", "none")
                    kwargs["max_length"] = config.get("huggingface_max_length", 512)
                _llm_instance = LLMFactory.create(preferred_provider, preferred_model, **kwargs)
                print(f"+ Using configured LLM: {preferred_provider}")
                return _llm_instance
            except Exception as e:
                print(f"Warning: Could not create configured {preferred_provider} LLM: {e}")
        
        # Try providers in order of preference
        providers = ["groq", "anthropic", "huggingface", "openai", "ollama"]
        if preferred_provider and preferred_provider not in providers:
            providers.insert(0, preferred_provider)
            
        for provider in providers:
            if key_manager.has_key(provider) or provider in ["ollama", "huggingface"]:
                try:
                    kwargs = {}
                    if provider == "ollama" and config:
                        kwargs["base_url"] = config.get("ollama_base_url", "http://localhost:11434")
                    elif provider == "huggingface" and config:
                        kwargs["device"] = config.get("huggingface_device", "auto")
                        kwargs["quantization"] = config.get("huggingface_quantization", "none")
                        kwargs["max_length"] = config.get("huggingface_max_length", 512)
                    _llm_instance = LLMFactory.create(provider, **kwargs)
                    print(f"+ Using available LLM: {provider}")
                    break
                except Exception as e:
                    print(f"Warning: Could not create {provider} LLM: {e}")
                    
        if _llm_instance is None:
            # No LLM could be configured - provide helpful error message
            error_msg = (
                "No LLM provider configured. Please set up an API key or local model:\n\n"
                "For cloud providers:\n"
                "  metis auth set groq <your-groq-api-key>\n"
                "  metis auth set anthropic <your-anthropic-api-key>\n"
                "  metis auth set openai <your-openai-api-key>\n"
                "  metis auth set huggingface <your-hf-api-key>\n\n"
                "For local models:\n"
                "  Ollama:\n"
                "    1. Install Ollama: https://ollama.ai\n"
                "    2. Pull a model: ollama pull tinydolphin\n"
                "    3. Configure: metis config set llm_provider ollama\n"
                "    4. Set model: metis config set llm_model tinydolphin\n\n"
                "  HuggingFace (local):\n"
                "    1. Install: pip install transformers torch\n"
                "    2. Configure: metis config set llm_provider huggingface\n"
                "    3. Set model: metis config set llm_model microsoft/DialoGPT-small\n\n"
                "You can get API keys from:\n"
                "  - Groq: https://console.groq.com/keys\n"
                "  - Anthropic: https://console.anthropic.com/\n"
                "  - OpenAI: https://platform.openai.com/api-keys\n"
                "  - HuggingFace: https://huggingface.co/settings/tokens"
            )
            raise ValueError(error_msg)
            
    return _llm_instance


def reset_llm():
    """
    Reset the global LLM instance to force reconfiguration.
    Useful when configuration changes.
    """
    global _llm_instance
    _llm_instance = None