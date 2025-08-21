"""
Refactored Smart Orchestrator module.

This package contains the modular orchestrator components:
- core: Core orchestration logic and main interface
- strategies: Different execution strategies (direct, sequential, parallel, iterative)
- analyzers: Query analysis and complexity assessment
- planners: Task planning and file generation
- validators: Tool validation and result verification
- blueprint_manager: Blueprint detection and creation
- execution_engine: Tool execution and coordination
"""

from .core import SmartOrchestrator
from .strategies import ExecutionStrategyManager
from .analyzers import QueryAnalyzer, ComplexityAnalyzer
from .planners import TaskPlanner, PlanningFileGenerator
from .validators import ToolValidator, ResultValidator
from .blueprint_manager import BlueprintManager
from .execution_engine import ExecutionEngine

# Factory function for backward compatibility
def create_orchestrator(tools_registry=None):
    """Create a smart orchestrator with the new modular architecture."""
    return SmartOrchestrator(tools_registry)

__all__ = [
    'SmartOrchestrator',
    'ExecutionStrategyManager',
    'QueryAnalyzer',
    'ComplexityAnalyzer', 
    'TaskPlanner',
    'PlanningFileGenerator',
    'ToolValidator',
    'ResultValidator',
    'BlueprintManager',
    'ExecutionEngine',
    'create_orchestrator'
]