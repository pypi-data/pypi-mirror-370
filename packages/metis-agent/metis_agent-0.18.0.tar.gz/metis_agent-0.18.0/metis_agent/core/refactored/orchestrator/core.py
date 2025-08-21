"""
Core Smart Orchestrator functionality.

Main orchestrator class that coordinates all other components.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from ..models import QueryAnalysis, ExecutionResult, ExecutionStrategy, ExecutionError
from .strategies import ExecutionStrategyManager
from .analyzers import QueryAnalyzer, ComplexityAnalyzer
from .planners import TaskPlanner
from .validators import ToolValidator, ResultValidator
from .blueprint_manager import BlueprintManager
from .execution_engine import ExecutionEngine


class SmartOrchestrator:
    """
    Smart orchestrator with modular architecture.
    
    Coordinates intelligent execution using multiple strategies and components.
    """
    
    def __init__(self, tools_registry: Dict[str, Any] = None):
        """
        Initialize the orchestrator with modular components.
        
        Args:
            tools_registry: Registry of available tools (optional)
        """
        self.tools_registry = tools_registry or {}
        
        # Initialize components
        self.strategy_manager = ExecutionStrategyManager(self)
        self.query_analyzer = QueryAnalyzer(self)
        self.complexity_analyzer = ComplexityAnalyzer(self)
        self.task_planner = TaskPlanner(self)
        self.tool_validator = ToolValidator(self)
        self.result_validator = ResultValidator(self)
        self.blueprint_manager = BlueprintManager(self)
        self.execution_engine = ExecutionEngine(self)
        
        # Execution state
        self.execution_history = []
        self.current_context = {}
    
    def execute(
        self,
        query: str,
        analysis: QueryAnalysis,
        context: Dict = None,
        tools: List[str] = None,
        strategy: ExecutionStrategy = None,
        config: Any = None,
        session_id: str = None
    ) -> ExecutionResult:
        """
        Execute a query using the intelligent orchestration system.
        
        Args:
            query: The user query to execute
            analysis: Pre-analyzed query information
            context: Additional context information
            tools: List of available tools
            strategy: Preferred execution strategy
            config: Configuration object
            session_id: Session identifier
            
        Returns:
            ExecutionResult with the outcome
        """
        start_time = datetime.now()
        execution_context = {
            'query': query,
            'analysis': analysis,
            'context': context or {},
            'tools': tools or [],
            'session_id': session_id,
            'config': config,
            'start_time': start_time,
            'api_keys': self._get_api_keys(config) if config else {}
        }
        
        self.current_context = execution_context
        
        try:
            # Determine execution strategy if not provided
            if not strategy:
                strategy = self.strategy_manager.determine_strategy(analysis, execution_context)
            
            # Execute using the selected strategy
            result = self.strategy_manager.execute_strategy(
                strategy, query, analysis, execution_context
            )
            
            # Post-process result
            result = self._post_process_result(result, execution_context)
            
            # Record execution
            self._record_execution(query, analysis, strategy, result, execution_context)
            
            return result
            
        except Exception as e:
            # Handle execution errors
            error_result = ExecutionResult(
                success=False,
                result="Execution failed: " + str(e),
                error=str(e),
                execution_time=datetime.now() - start_time,
                strategy=strategy.value if strategy else "unknown",
                tools_used=[],
                metadata={'error_type': type(e).__name__}
            )
            
            self._record_execution(query, analysis, strategy, error_result, execution_context)
            return error_result
    
    def _get_api_keys(self, config: Any) -> Dict[str, str]:
        """Get all available API keys from config."""
        api_keys = {}
        if config and hasattr(config, 'get_api_key'):
            # Common API key providers
            providers = ['google', 'openai', 'groq', 'anthropic', 'firecrawl', 'GOOGLE_SEARCH_ENGINE']
            for provider in providers:
                try:
                    key = config.get_api_key(provider)
                    if key:
                        api_keys[provider] = key
                        # Also add common variations
                        if provider == 'google':
                            api_keys['google_api_key'] = key
                        elif provider == 'GOOGLE_SEARCH_ENGINE':
                            api_keys['google_search_engine'] = key
                except Exception:
                    continue  # Skip providers that fail
        
        return api_keys
    
    def _post_process_result(self, result: ExecutionResult, 
                           execution_context: Dict) -> ExecutionResult:
        """
        Post-process execution result.
        
        Args:
            result: Raw execution result
            execution_context: Execution context
            
        Returns:
            Post-processed result
        """
        # Validate result quality
        is_valid = self.result_validator.validate_result(result, execution_context)
        
        # Update metadata
        if not result.metadata:
            result.metadata = {}
        
        result.metadata.update({
            'post_processed': True,
            'validation_passed': is_valid,
            'processing_time': datetime.now(),
            'context_session_id': execution_context.get('session_id')
        })
        
        # Check for blueprint opportunities
        if result.success and self.complexity_analyzer.analyze_task_complexity(
            execution_context['query'], result
        ):
            blueprint_opportunity = self.blueprint_manager.detect_blueprint_opportunity(
                execution_context['query'], result, execution_context
            )
            
            if blueprint_opportunity:
                result.metadata['blueprint_opportunity'] = blueprint_opportunity
        
        return result
    
    def _record_execution(self, query: str, analysis: QueryAnalysis, 
                         strategy: ExecutionStrategy, result: ExecutionResult,
                         execution_context: Dict):
        """Record execution in history for analysis and improvement."""
        execution_record = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'analysis': analysis.__dict__ if hasattr(analysis, '__dict__') else str(analysis),
            'strategy': strategy.value if strategy else None,
            'success': result.success,
            'execution_time': result.execution_time,
            'tools_used': result.tools_used,
            'session_id': execution_context.get('session_id'),
            'error': result.error if result.error else None
        }
        
        self.execution_history.append(execution_record)
        
        # Maintain history size (keep last 100 executions)
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get statistics about executions."""
        if not self.execution_history:
            return {}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for record in self.execution_history if record['success'])
        
        # Strategy usage
        strategy_counts = {}
        for record in self.execution_history:
            strategy = record.get('strategy', 'unknown')
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        # Average execution time
        execution_times = [
            record.get('execution_time', 0) for record in self.execution_history
            if isinstance(record.get('execution_time'), (int, float))
        ]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Tool usage
        all_tools = []
        for record in self.execution_history:
            if record.get('tools_used'):
                all_tools.extend(record['tools_used'])
        
        tool_counts = {}
        for tool in all_tools:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': successful_executions / total_executions if total_executions > 0 else 0,
            'strategy_usage': strategy_counts,
            'average_execution_time': avg_execution_time,
            'tool_usage': tool_counts,
            'recent_executions': self.execution_history[-10:] if len(self.execution_history) > 10 else self.execution_history
        }
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get status of all orchestrator components."""
        return {
            'strategy_manager': self.strategy_manager.get_status(),
            'query_analyzer': self.query_analyzer.get_status(),
            'complexity_analyzer': self.complexity_analyzer.get_status(),
            'task_planner': self.task_planner.get_status(),
            'tool_validator': self.tool_validator.get_status(),
            'result_validator': self.result_validator.get_status(),
            'blueprint_manager': self.blueprint_manager.get_status(),
            'execution_engine': self.execution_engine.get_status(),
        }
    
    def reset_state(self):
        """Reset orchestrator state."""
        self.execution_history.clear()
        self.current_context.clear()
        
        # Reset component states
        for component in [
            self.strategy_manager, self.query_analyzer, self.complexity_analyzer,
            self.task_planner, self.tool_validator, self.result_validator,
            self.blueprint_manager, self.execution_engine
        ]:
            if hasattr(component, 'reset'):
                component.reset()
    
    def configure_component(self, component_name: str, config: Dict[str, Any]):
        """Configure a specific component."""
        component_map = {
            'strategy_manager': self.strategy_manager,
            'query_analyzer': self.query_analyzer,
            'complexity_analyzer': self.complexity_analyzer,
            'task_planner': self.task_planner,
            'tool_validator': self.tool_validator,
            'result_validator': self.result_validator,
            'blueprint_manager': self.blueprint_manager,
            'execution_engine': self.execution_engine,
        }
        
        component = component_map.get(component_name)
        if component and hasattr(component, 'configure'):
            component.configure(config)
        else:
            raise ValueError(f"Unknown component: {component_name}")
    
    def export_execution_data(self, format: str = 'json') -> str:
        """Export execution history and statistics."""
        data = {
            'statistics': self.get_execution_statistics(),
            'component_status': self.get_component_status(),
            'execution_history': self.execution_history,
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format == 'json':
            import json
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    # Legacy method aliases for backward compatibility
    def analyze_task_complexity(self, task: str, execution_result: ExecutionResult = None) -> bool:
        """Legacy method - delegate to complexity analyzer."""
        return self.complexity_analyzer.analyze_task_complexity(task, execution_result)
    
    def detect_blueprint_opportunity(self, task: str, execution_result: ExecutionResult, 
                                   context: Dict) -> Optional[Dict]:
        """Legacy method - delegate to blueprint manager."""
        return self.blueprint_manager.detect_blueprint_opportunity(task, execution_result, context)
    
    def suggest_blueprint_creation(self, opportunity: Dict, context: Dict) -> str:
        """Legacy method - delegate to blueprint manager."""
        return self.blueprint_manager.suggest_blueprint_creation(opportunity, context)
    
    def create_blueprint_from_execution(self, opportunity: Dict, context: Dict, 
                                       save_path: str = None):
        """Legacy method - delegate to blueprint manager."""
        return self.blueprint_manager.create_blueprint_from_execution(
            opportunity, context, save_path
        )