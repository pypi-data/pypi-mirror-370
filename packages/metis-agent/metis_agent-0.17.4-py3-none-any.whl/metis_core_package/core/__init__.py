"""
Core package for Metis Agent.

This package provides the core components of the agent.
"""
from .agent import SingleAgent
from .llm_interface import get_llm, configure_llm, BaseLLM, LLMFactory

# Enhanced components (now the main architecture)
from .models import QueryComplexity, ExecutionStrategy, QueryAnalysis, ExecutionResult
from .advanced_analyzer import AdvancedQueryAnalyzer
from .smart_orchestrator import SmartOrchestrator
from .response_synthesizer import ResponseSynthesizer

__all__ = [
    # Core components
    'SingleAgent',  # Now uses enhanced architecture by default
    
    # LLM interface
    'get_llm',
    'configure_llm',
    'BaseLLM',
    'LLMFactory',
    
    # Enhanced components
    'QueryComplexity',
    'ExecutionStrategy', 
    'QueryAnalysis',
    'ExecutionResult',
    'AdvancedQueryAnalyzer',
    'SmartOrchestrator',
    'ResponseSynthesizer'
]