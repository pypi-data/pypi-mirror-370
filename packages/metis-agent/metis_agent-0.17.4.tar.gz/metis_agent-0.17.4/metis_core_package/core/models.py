"""
Enhanced data models for Metis Agent analysis-driven architecture.

This module provides the core data structures for query analysis and execution.
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class QueryComplexity(Enum):
    """Classification of query complexity levels."""
    TRIVIAL = "trivial"      # Simple math, basic facts
    SIMPLE = "simple"        # Single concept questions
    MODERATE = "moderate"    # Requires some reasoning or tool use
    COMPLEX = "complex"      # Multi-step problems
    RESEARCH = "research"    # Deep analysis needed


class ExecutionStrategy(Enum):
    """Execution strategies for query processing."""
    DIRECT_RESPONSE = "direct_response"  # Answer directly from knowledge
    SINGLE_TOOL = "single_tool"          # Use one tool
    SEQUENTIAL = "sequential"            # Multiple tools in sequence
    PARALLEL = "parallel"                # Multiple tools simultaneously
    ITERATIVE = "iterative"              # ReAct pattern with reasoning loops


@dataclass
class QueryAnalysis:
    """Result of query analysis containing execution plan."""
    complexity: QueryComplexity
    strategy: ExecutionStrategy
    confidence: float
    required_tools: List[str]
    estimated_steps: int
    user_intent: str
    reasoning: str


@dataclass
class ExecutionResult:
    """Result of query execution with metadata."""
    response: str
    strategy_used: str
    tools_used: List[str]
    execution_time: float
    confidence: float
    metadata: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class ToolExecutionResult:
    """Result of individual tool execution."""
    tool_name: str
    query: str
    result: str
    execution_time: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class AnalysisError(Exception):
    """Exception raised during query analysis."""
    pass


class ExecutionError(Exception):
    """Exception raised during query execution."""
    pass
