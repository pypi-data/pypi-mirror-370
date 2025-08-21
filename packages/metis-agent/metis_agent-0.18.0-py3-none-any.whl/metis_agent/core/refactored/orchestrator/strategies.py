"""
Execution strategy management and implementation.

Handles different execution strategies: direct, sequential, parallel, iterative.
"""
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..models import QueryAnalysis, ExecutionResult, ExecutionStrategy, ToolExecutionResult
from ..llm_interface import get_llm
from ...tools.registry import get_tool


class ExecutionStrategyManager:
    """Manages different execution strategies for the orchestrator."""
    
    def __init__(self, orchestrator):
        """Initialize with reference to main orchestrator."""
        self.orchestrator = orchestrator
        self.strategy_implementations = {
            ExecutionStrategy.DIRECT: self._direct_response,
            ExecutionStrategy.SINGLE_TOOL: self._single_tool_execution,
            ExecutionStrategy.SEQUENTIAL: self._sequential_execution,
            ExecutionStrategy.PARALLEL: self._parallel_execution,
            ExecutionStrategy.ITERATIVE: self._iterative_execution,
        }
    
    def determine_strategy(self, analysis: QueryAnalysis, context: Dict) -> ExecutionStrategy:
        """
        Determine the best execution strategy based on analysis.
        
        Args:
            analysis: Query analysis results
            context: Execution context
            
        Returns:
            Recommended execution strategy
        """
        # Check for direct response scenarios
        if self._should_use_direct_response(analysis, context):
            return ExecutionStrategy.DIRECT
        
        # Check tool requirements
        tools_needed = getattr(analysis, 'tools_required', [])
        
        if not tools_needed:
            return ExecutionStrategy.DIRECT
        elif len(tools_needed) == 1:
            return ExecutionStrategy.SINGLE_TOOL
        elif self._should_use_parallel(analysis, tools_needed):
            return ExecutionStrategy.PARALLEL
        elif self._should_use_iterative(analysis, tools_needed):
            return ExecutionStrategy.ITERATIVE
        else:
            return ExecutionStrategy.SEQUENTIAL
    
    def execute_strategy(self, strategy: ExecutionStrategy, query: str, 
                        analysis: QueryAnalysis, context: Dict) -> ExecutionResult:
        """
        Execute using the specified strategy.
        
        Args:
            strategy: Execution strategy to use
            query: User query
            analysis: Query analysis
            context: Execution context
            
        Returns:
            Execution result
        """
        implementation = self.strategy_implementations.get(strategy)
        if not implementation:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        start_time = datetime.now()
        
        try:
            result = implementation(query, analysis, context)
            
            # Ensure result has required fields
            if not hasattr(result, 'execution_time'):
                result.execution_time = datetime.now() - start_time
            if not hasattr(result, 'strategy'):
                result.strategy = strategy.value
                
            return result
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                result=f"Strategy execution failed: {str(e)}",
                error=str(e),
                execution_time=datetime.now() - start_time,
                strategy=strategy.value,
                tools_used=[],
                metadata={'error_type': type(e).__name__}
            )
    
    def _should_use_direct_response(self, analysis: QueryAnalysis, context: Dict) -> bool:
        """Check if direct response is appropriate."""
        # Use direct response for simple questions or when no tools are available
        query = context.get('query', '').lower()
        
        question_indicators = ['what is', 'who is', 'when was', 'where is', 'why', 'how', 'explain', 'define']
        is_question = any(indicator in query for indicator in question_indicators)
        
        has_tools = bool(getattr(analysis, 'tools_required', []))
        
        return is_question and not has_tools
    
    def _should_use_parallel(self, analysis: QueryAnalysis, tools_needed: List[str]) -> bool:
        """Check if parallel execution is appropriate."""
        # Use parallel for independent operations
        if len(tools_needed) < 2:
            return False
        
        # Check for independent tools that can run in parallel
        independent_tools = {
            'google_search', 'firecrawl', 'calculator', 'textanalyzer',
            'datavalidator', 'webscrapertool'
        }
        
        return all(tool.lower() in independent_tools for tool in tools_needed)
    
    def _should_use_iterative(self, analysis: QueryAnalysis, tools_needed: List[str]) -> bool:
        """Check if iterative execution is appropriate."""
        # Use iterative for complex, multi-step processes
        complexity_indicators = getattr(analysis, 'complexity', 'medium')
        
        return (complexity_indicators in ['high', 'complex'] or 
                len(tools_needed) > 3 or
                'project' in str(analysis).lower())
    
    def _direct_response(self, query: str, analysis: QueryAnalysis, context: Dict) -> ExecutionResult:
        """Execute direct response strategy."""
        start_time = datetime.now()
        
        try:
            llm = get_llm()
            if not llm:
                return ExecutionResult(
                    success=False,
                    result="No LLM available for direct response",
                    error="LLM not configured",
                    execution_time=datetime.now() - start_time,
                    strategy=ExecutionStrategy.DIRECT.value,
                    tools_used=[]
                )
            
            # Generate direct response
            response = llm.generate_response(query)
            
            return ExecutionResult(
                success=True,
                result=response,
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.DIRECT.value,
                tools_used=[],
                metadata={'response_type': 'direct_llm'}
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                result=f"Direct response failed: {str(e)}",
                error=str(e),
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.DIRECT.value,
                tools_used=[]
            )
    
    def _single_tool_execution(self, query: str, analysis: QueryAnalysis, 
                              context: Dict) -> ExecutionResult:
        """Execute single tool strategy."""
        start_time = datetime.now()
        tools_used = []
        
        try:
            tools_required = getattr(analysis, 'tools_required', [])
            if not tools_required:
                return ExecutionResult(
                    success=False,
                    result="No tools specified for single tool execution",
                    error="Missing tool specification",
                    execution_time=datetime.now() - start_time,
                    strategy=ExecutionStrategy.SINGLE_TOOL.value,
                    tools_used=[]
                )
            
            tool_name = tools_required[0]
            tools_used.append(tool_name)
            
            # Get and execute tool
            tool_class = get_tool(tool_name)
            if not tool_class:
                return ExecutionResult(
                    success=False,
                    result=f"Tool not found: {tool_name}",
                    error=f"Tool '{tool_name}' not available",
                    execution_time=datetime.now() - start_time,
                    strategy=ExecutionStrategy.SINGLE_TOOL.value,
                    tools_used=tools_used
                )
            
            # Validate tool and execute
            is_valid, validation_error = self.orchestrator.tool_validator.validate_tool_requirements(
                tool_name, tool_class, context
            )
            
            if not is_valid:
                return ExecutionResult(
                    success=False,
                    result=f"Tool validation failed: {validation_error}",
                    error=validation_error,
                    execution_time=datetime.now() - start_time,
                    strategy=ExecutionStrategy.SINGLE_TOOL.value,
                    tools_used=tools_used
                )
            
            # Execute tool
            success, tool_result = self.orchestrator.tool_validator.execute_tool_with_validation(
                tool_name, tool_class, query, context
            )
            
            return ExecutionResult(
                success=success,
                result=tool_result if success else f"Tool execution failed: {tool_result}",
                error=None if success else str(tool_result),
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.SINGLE_TOOL.value,
                tools_used=tools_used,
                metadata={'tool_name': tool_name}
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                result=f"Single tool execution failed: {str(e)}",
                error=str(e),
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.SINGLE_TOOL.value,
                tools_used=tools_used
            )
    
    def _sequential_execution(self, query: str, analysis: QueryAnalysis, 
                             context: Dict) -> ExecutionResult:
        """Execute sequential strategy."""
        start_time = datetime.now()
        tools_used = []
        results = []
        accumulated_context = context.copy()
        
        try:
            tools_required = getattr(analysis, 'tools_required', [])
            
            for tool_name in tools_required:
                tools_used.append(tool_name)
                
                # Get tool
                tool_class = get_tool(tool_name)
                if not tool_class:
                    results.append(f"Tool not found: {tool_name}")
                    continue
                
                # Execute tool with accumulated context
                success, tool_result = self.orchestrator.tool_validator.execute_tool_with_validation(
                    tool_name, tool_class, query, accumulated_context
                )
                
                if success:
                    results.append(f"{tool_name}: {tool_result}")
                    # Update context with result for next tool
                    accumulated_context[f'{tool_name}_result'] = tool_result
                else:
                    results.append(f"{tool_name}: ERROR - {tool_result}")
                
                # Small delay between tools
                time.sleep(0.1)
            
            # Combine results
            final_result = "\n\n".join(results)
            success = any("ERROR" not in result for result in results)
            
            return ExecutionResult(
                success=success,
                result=final_result,
                error=None if success else "Some tools failed execution",
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.SEQUENTIAL.value,
                tools_used=tools_used,
                metadata={'tool_count': len(tools_used)}
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                result=f"Sequential execution failed: {str(e)}",
                error=str(e),
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.SEQUENTIAL.value,
                tools_used=tools_used
            )
    
    def _parallel_execution(self, query: str, analysis: QueryAnalysis, 
                           context: Dict) -> ExecutionResult:
        """Execute parallel strategy."""
        start_time = datetime.now()
        tools_used = []
        
        try:
            tools_required = getattr(analysis, 'tools_required', [])
            tools_used = tools_required.copy()
            
            # Execute tools in parallel
            with ThreadPoolExecutor(max_workers=min(len(tools_required), 4)) as executor:
                future_to_tool = {}
                
                for tool_name in tools_required:
                    tool_class = get_tool(tool_name)
                    if tool_class:
                        future = executor.submit(
                            self._execute_tool_safely, 
                            tool_name, tool_class, query, context
                        )
                        future_to_tool[future] = tool_name
                
                # Collect results
                results = []
                for future in as_completed(future_to_tool):
                    tool_name = future_to_tool[future]
                    try:
                        success, result = future.result(timeout=30)  # 30 second timeout
                        if success:
                            results.append(f"{tool_name}: {result}")
                        else:
                            results.append(f"{tool_name}: ERROR - {result}")
                    except Exception as e:
                        results.append(f"{tool_name}: TIMEOUT/ERROR - {str(e)}")
            
            # Combine results
            final_result = "\n\n".join(results)
            success = any("ERROR" not in result and "TIMEOUT" not in result for result in results)
            
            return ExecutionResult(
                success=success,
                result=final_result,
                error=None if success else "Some parallel tools failed",
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.PARALLEL.value,
                tools_used=tools_used,
                metadata={'parallel_tools': len(tools_used)}
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                result=f"Parallel execution failed: {str(e)}",
                error=str(e),
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.PARALLEL.value,
                tools_used=tools_used
            )
    
    def _iterative_execution(self, query: str, analysis: QueryAnalysis, 
                            context: Dict) -> ExecutionResult:
        """Execute iterative strategy with planning and feedback."""
        start_time = datetime.now()
        tools_used = []
        iterations = []
        max_iterations = 5
        
        try:
            # Generate initial plan
            planning_files = self.orchestrator.task_planner.generate_planning_files(
                query, analysis, context.get('session_id')
            )
            
            current_context = context.copy()
            current_context.update({
                'planning_files': planning_files,
                'iterations': iterations,
                'max_iterations': max_iterations
            })
            
            for iteration in range(max_iterations):
                # Get next task
                next_task = self.orchestrator.task_planner.get_next_task(current_context)
                if not next_task or next_task.lower() in ['complete', 'done', 'finished']:
                    break
                
                # Determine tools needed for this iteration
                iteration_tools = self._determine_iteration_tools(next_task, analysis)
                
                if not iteration_tools:
                    iterations.append(f"Iteration {iteration + 1}: No tools needed - {next_task}")
                    continue
                
                # Execute iteration
                iteration_results = []
                for tool_name in iteration_tools:
                    if tool_name not in tools_used:
                        tools_used.append(tool_name)
                    
                    tool_class = get_tool(tool_name)
                    if tool_class:
                        success, result = self.orchestrator.tool_validator.execute_tool_with_validation(
                            tool_name, tool_class, next_task, current_context
                        )
                        
                        if success:
                            iteration_results.append(f"{tool_name}: {result}")
                            current_context[f'iteration_{iteration}_{tool_name}'] = result
                        else:
                            iteration_results.append(f"{tool_name}: ERROR - {result}")
                
                iteration_summary = f"Iteration {iteration + 1}: {next_task}\n" + "\n".join(iteration_results)
                iterations.append(iteration_summary)
                
                # Update progress
                self.orchestrator.task_planner.update_task_progress(
                    current_context, next_task, "completed"
                )
                
                # Check if we have sufficient information
                if self._has_sufficient_information(query, current_context):
                    break
            
            # Combine all iteration results
            final_result = "\n\n".join(iterations)
            success = bool(iterations) and not all("ERROR" in iteration for iteration in iterations)
            
            return ExecutionResult(
                success=success,
                result=final_result,
                error=None if success else "Iterative execution encountered errors",
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.ITERATIVE.value,
                tools_used=tools_used,
                metadata={
                    'iterations_completed': len(iterations),
                    'planning_used': bool(planning_files)
                }
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                result=f"Iterative execution failed: {str(e)}",
                error=str(e),
                execution_time=datetime.now() - start_time,
                strategy=ExecutionStrategy.ITERATIVE.value,
                tools_used=tools_used
            )
    
    def _execute_tool_safely(self, tool_name: str, tool_class, query: str, 
                           context: Dict) -> tuple:
        """Safely execute a tool (used in parallel execution)."""
        try:
            return self.orchestrator.tool_validator.execute_tool_with_validation(
                tool_name, tool_class, query, context
            )
        except Exception as e:
            return False, f"Tool execution failed: {str(e)}"
    
    def _determine_iteration_tools(self, task: str, analysis: QueryAnalysis) -> List[str]:
        """Determine which tools are needed for a specific iteration task."""
        task_lower = task.lower()
        available_tools = getattr(analysis, 'tools_required', [])
        
        # Simple heuristics for tool selection
        needed_tools = []
        
        if 'search' in task_lower or 'find' in task_lower:
            if 'google_search' in available_tools:
                needed_tools.append('google_search')
            elif 'webscrapertool' in available_tools:
                needed_tools.append('webscrapertool')
        
        if 'calculate' in task_lower or 'compute' in task_lower:
            if 'calculator' in available_tools:
                needed_tools.append('calculator')
        
        if 'analyze' in task_lower or 'process' in task_lower:
            if 'textanalyzer' in available_tools:
                needed_tools.append('textanalyzer')
        
        if 'write' in task_lower or 'create' in task_lower:
            if 'write_tool' in available_tools:
                needed_tools.append('write_tool')
        
        # If no specific tools identified, use first available tool
        if not needed_tools and available_tools:
            needed_tools = [available_tools[0]]
        
        return needed_tools
    
    def _has_sufficient_information(self, query: str, context: Dict) -> bool:
        """Check if we have sufficient information to answer the query."""
        # Simple heuristic - check if we have results from multiple iterations
        iteration_results = [
            key for key in context.keys() 
            if key.startswith('iteration_') and not key.endswith('_error')
        ]
        
        return len(iteration_results) >= 2 or len(str(context)) > 1000
    
    def get_status(self) -> Dict[str, Any]:
        """Get strategy manager status."""
        return {
            'available_strategies': [strategy.value for strategy in ExecutionStrategy],
            'implemented_strategies': len(self.strategy_implementations),
            'component': 'ExecutionStrategyManager',
            'status': 'active'
        }