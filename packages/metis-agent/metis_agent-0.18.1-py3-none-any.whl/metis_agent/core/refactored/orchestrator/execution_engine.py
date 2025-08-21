"""
Execution engine for orchestrator operations.

Handles coordination of tool execution and result management.
"""
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ...tools.registry import get_tool


class ExecutionEngine:
    """Coordinates tool execution and manages execution state."""
    
    def __init__(self, orchestrator):
        """Initialize with reference to main orchestrator."""
        self.orchestrator = orchestrator
        self.active_executions = {}
        self.execution_queue = []
        self.execution_statistics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'tool_usage_counts': {},
            'error_counts': {}
        }
    
    def execute_tool(self, tool_name: str, query: str, context: Dict,
                    timeout: int = 300) -> tuple:
        """
        Execute a tool with comprehensive management.
        
        Args:
            tool_name: Name of the tool to execute
            query: Query to execute
            context: Execution context
            timeout: Maximum execution time in seconds
            
        Returns:
            Tuple of (success, result, metadata)
        """
        execution_id = f"exec_{int(time.time())}_{tool_name}"
        start_time = datetime.now()
        
        # Record execution start
        execution_record = {
            'execution_id': execution_id,
            'tool_name': tool_name,
            'query': query[:100] + "..." if len(query) > 100 else query,
            'start_time': start_time,
            'status': 'running',
            'timeout': timeout
        }
        
        self.active_executions[execution_id] = execution_record
        
        try:
            # Get tool instance
            tool_class = get_tool(tool_name)
            if not tool_class:
                return self._handle_execution_failure(
                    execution_id, f"Tool not found: {tool_name}", start_time
                )
            
            # Validate tool requirements
            is_valid, validation_error = self.orchestrator.tool_validator.validate_tool_requirements(
                tool_name, tool_class, context
            )
            
            if not is_valid:
                return self._handle_execution_failure(
                    execution_id, f"Tool validation failed: {validation_error}", start_time
                )
            
            # Execute tool with timeout
            success, result = self._execute_with_timeout(
                tool_class, query, context, timeout
            )
            
            # Calculate execution time
            execution_time = datetime.now() - start_time
            
            if success:
                return self._handle_execution_success(
                    execution_id, result, execution_time, start_time
                )
            else:
                return self._handle_execution_failure(
                    execution_id, result, start_time, execution_time
                )
        
        except Exception as e:
            execution_time = datetime.now() - start_time
            return self._handle_execution_failure(
                execution_id, f"Execution exception: {str(e)}", start_time, execution_time
            )
    
    def execute_multiple_tools(self, tool_configs: List[Dict], context: Dict,
                              parallel: bool = False) -> List[tuple]:
        """
        Execute multiple tools sequentially or in parallel.
        
        Args:
            tool_configs: List of tool configurations
            context: Execution context
            parallel: Whether to execute in parallel
            
        Returns:
            List of execution results
        """
        if parallel:
            return self._execute_tools_parallel(tool_configs, context)
        else:
            return self._execute_tools_sequential(tool_configs, context)
    
    def queue_execution(self, tool_name: str, query: str, context: Dict,
                       priority: int = 5) -> str:
        """
        Queue a tool execution for later processing.
        
        Args:
            tool_name: Name of tool to execute
            query: Query to execute
            context: Execution context
            priority: Execution priority (1-10, lower is higher priority)
            
        Returns:
            Queue ID for tracking
        """
        queue_id = f"queue_{int(time.time())}_{tool_name}"
        
        queue_item = {
            'queue_id': queue_id,
            'tool_name': tool_name,
            'query': query,
            'context': context,
            'priority': priority,
            'queued_at': datetime.now(),
            'status': 'queued'
        }
        
        # Insert into queue based on priority
        self.execution_queue.append(queue_item)
        self.execution_queue.sort(key=lambda x: (x['priority'], x['queued_at']))
        
        return queue_id
    
    def process_execution_queue(self, max_concurrent: int = 3) -> List[tuple]:
        """
        Process queued executions.
        
        Args:
            max_concurrent: Maximum concurrent executions
            
        Returns:
            List of execution results
        """
        if not self.execution_queue:
            return []
        
        # Get items to process
        items_to_process = self.execution_queue[:max_concurrent]
        self.execution_queue = self.execution_queue[max_concurrent:]
        
        results = []
        
        for item in items_to_process:
            item['status'] = 'processing'
            
            success, result, metadata = self.execute_tool(
                item['tool_name'],
                item['query'],
                item['context']
            )
            
            results.append((success, result, metadata))
        
        return results
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an active execution.
        
        Args:
            execution_id: ID of execution to cancel
            
        Returns:
            True if successfully cancelled
        """
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution['status'] = 'cancelled'
            execution['end_time'] = datetime.now()
            
            # Move to completed executions
            self._archive_execution(execution_id)
            
            return True
        
        return False
    
    def get_active_executions(self) -> Dict[str, Dict]:
        """Get currently active executions."""
        # Clean up expired executions
        self._cleanup_expired_executions()
        
        return self.active_executions.copy()
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict]:
        """Get status of a specific execution."""
        return self.active_executions.get(execution_id)
    
    def _execute_with_timeout(self, tool_class, query: str, context: Dict,
                             timeout: int) -> tuple:
        """Execute tool with timeout handling."""
        try:
            # Create tool instance
            if hasattr(tool_class, '__call__') and not hasattr(tool_class, 'run'):
                tool_instance = tool_class()
            else:
                tool_instance = tool_class
            
            # Use the orchestrator's tool validator for execution
            return self.orchestrator.tool_validator.execute_tool_with_validation(
                tool_class.__name__ if hasattr(tool_class, '__name__') else str(tool_class),
                tool_instance,
                query,
                context
            )
            
        except Exception as e:
            return False, f"Tool execution failed: {str(e)}"
    
    def _execute_tools_sequential(self, tool_configs: List[Dict], 
                                 context: Dict) -> List[tuple]:
        """Execute tools sequentially."""
        results = []
        accumulated_context = context.copy()
        
        for config in tool_configs:
            tool_name = config['tool_name']
            query = config['query']
            tool_context = config.get('context', {})
            
            # Merge contexts
            execution_context = {**accumulated_context, **tool_context}
            
            # Execute tool
            success, result, metadata = self.execute_tool(
                tool_name, query, execution_context
            )
            
            results.append((success, result, metadata))
            
            # Update context with result for next tool
            if success:
                accumulated_context[f'{tool_name}_result'] = result
                accumulated_context[f'{tool_name}_metadata'] = metadata
        
        return results
    
    def _execute_tools_parallel(self, tool_configs: List[Dict], 
                               context: Dict) -> List[tuple]:
        """Execute tools in parallel."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(tool_configs), 4)) as executor:
            # Submit all tool executions
            future_to_config = {}
            
            for config in tool_configs:
                future = executor.submit(
                    self.execute_tool,
                    config['tool_name'],
                    config['query'],
                    {**context, **config.get('context', {})}
                )
                future_to_config[future] = config
            
            # Collect results as they complete
            for future in as_completed(future_to_config):
                try:
                    result = future.result(timeout=30)  # 30 second timeout per tool
                    results.append(result)
                except Exception as e:
                    config = future_to_config[future]
                    results.append((
                        False, 
                        f"Parallel execution failed: {str(e)}", 
                        {'tool_name': config['tool_name'], 'error': str(e)}
                    ))
        
        return results
    
    def _handle_execution_success(self, execution_id: str, result: Any, 
                                 execution_time: timedelta, start_time: datetime) -> tuple:
        """Handle successful tool execution."""
        # Update execution record
        execution = self.active_executions.get(execution_id, {})
        execution.update({
            'status': 'completed',
            'success': True,
            'end_time': datetime.now(),
            'execution_time': execution_time,
            'result_size': len(str(result)) if result else 0
        })
        
        # Update statistics
        self.execution_statistics['total_executions'] += 1
        self.execution_statistics['successful_executions'] += 1
        
        tool_name = execution.get('tool_name', 'unknown')
        self.execution_statistics['tool_usage_counts'][tool_name] = \
            self.execution_statistics['tool_usage_counts'].get(tool_name, 0) + 1
        
        # Update average execution time
        self._update_average_execution_time(execution_time)
        
        # Archive execution
        self._archive_execution(execution_id)
        
        metadata = {
            'execution_id': execution_id,
            'tool_name': tool_name,
            'execution_time': execution_time,
            'start_time': start_time,
            'success': True
        }
        
        return True, result, metadata
    
    def _handle_execution_failure(self, execution_id: str, error: str, 
                                 start_time: datetime, 
                                 execution_time: timedelta = None) -> tuple:
        """Handle failed tool execution."""
        if execution_time is None:
            execution_time = datetime.now() - start_time
        
        # Update execution record
        execution = self.active_executions.get(execution_id, {})
        execution.update({
            'status': 'failed',
            'success': False,
            'end_time': datetime.now(),
            'execution_time': execution_time,
            'error': error
        })
        
        # Update statistics
        self.execution_statistics['total_executions'] += 1
        self.execution_statistics['failed_executions'] += 1
        
        tool_name = execution.get('tool_name', 'unknown')
        error_key = f"{tool_name}_errors"
        self.execution_statistics['error_counts'][error_key] = \
            self.execution_statistics['error_counts'].get(error_key, 0) + 1
        
        # Archive execution
        self._archive_execution(execution_id)
        
        metadata = {
            'execution_id': execution_id,
            'tool_name': tool_name,
            'execution_time': execution_time,
            'start_time': start_time,
            'success': False,
            'error': error
        }
        
        return False, error, metadata
    
    def _update_average_execution_time(self, execution_time: timedelta):
        """Update rolling average execution time."""
        current_avg = self.execution_statistics['average_execution_time']
        total_executions = self.execution_statistics['total_executions']
        
        # Simple rolling average
        if total_executions > 0:
            new_time = execution_time.total_seconds()
            self.execution_statistics['average_execution_time'] = \
                ((current_avg * (total_executions - 1)) + new_time) / total_executions
    
    def _archive_execution(self, execution_id: str):
        """Archive completed execution."""
        if execution_id in self.active_executions:
            # Could store in persistent storage here
            del self.active_executions[execution_id]
    
    def _cleanup_expired_executions(self):
        """Clean up executions that have been running too long."""
        current_time = datetime.now()
        expired_executions = []
        
        for execution_id, execution in self.active_executions.items():
            start_time = execution.get('start_time')
            timeout = execution.get('timeout', 300)  # 5 minutes default
            
            if start_time and (current_time - start_time).total_seconds() > timeout:
                expired_executions.append(execution_id)
        
        # Cancel expired executions
        for execution_id in expired_executions:
            self.cancel_execution(execution_id)
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics."""
        stats = self.execution_statistics.copy()
        
        # Calculate derived metrics
        total = stats['total_executions']
        if total > 0:
            stats['success_rate'] = stats['successful_executions'] / total
            stats['failure_rate'] = stats['failed_executions'] / total
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        # Add current state
        stats['active_executions'] = len(self.active_executions)
        stats['queued_executions'] = len(self.execution_queue)
        
        return stats
    
    def reset_statistics(self):
        """Reset execution statistics."""
        self.execution_statistics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'tool_usage_counts': {},
            'error_counts': {}
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get execution engine status."""
        return {
            'active_executions': len(self.active_executions),
            'queued_executions': len(self.execution_queue),
            'total_executions': self.execution_statistics['total_executions'],
            'component': 'ExecutionEngine',
            'status': 'active'
        }