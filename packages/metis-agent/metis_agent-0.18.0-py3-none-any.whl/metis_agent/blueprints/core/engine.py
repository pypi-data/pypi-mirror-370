#!/usr/bin/env python3
"""
Blueprint Engine - Workflow Execution Engine

This module provides the BlueprintEngine class for executing
blueprint workflows in the Metis Agent framework.
"""

import uuid
import time
import asyncio
import concurrent.futures
from typing import Dict, List, Any, Optional, Union
import yaml
import json
import importlib
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
from .blueprint import Blueprint, BlueprintStep, StepStatus, ErrorHandlingStrategy


class ExecutionContext:
    """
    Execution context for blueprint runs.
    
    Manages the state and data flow during blueprint execution.
    """
    
    def __init__(self, execution_id: str, blueprint: Blueprint, inputs: Dict[str, Any]):
        """Initialize execution context."""
        self.execution_id = execution_id
        self.blueprint = blueprint
        self.inputs = inputs
        self.step_results: Dict[str, Dict[str, Any]] = {}
        self.global_variables: Dict[str, Any] = {}
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.status = "running"
        self.error: Optional[str] = None
        
        # Initialize global variables with inputs
        self.global_variables.update(inputs)
        
        # Set blueprint execution context
        blueprint.execution_id = execution_id
        blueprint.execution_context = {'inputs': inputs}
        blueprint.global_variables = self.global_variables


class BlueprintEngine:
    """
    Blueprint execution engine.
    
    This class handles the execution of blueprint workflows,
    managing step execution, data flow, and error handling.
    """
    
    def __init__(self, tool_registry=None):
        """Initialize the blueprint engine."""
        self.name = "BlueprintEngine"
        self.version = "1.0.0"
        self.tool_registry = tool_registry
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.interactive_callbacks = {}  # For user interaction callbacks
    
    def set_tool_registry(self, tool_registry):
        """Set the tool registry for tool resolution."""
        self.tool_registry = tool_registry
    
    def execute(self, blueprint: Blueprint, inputs: Dict[str, Any] = None, 
                parallel: bool = True, max_workers: int = 4) -> Dict[str, Any]:
        """
        Execute a blueprint with support for parallel execution.
        
        Args:
            blueprint: Blueprint to execute
            inputs: Input values for the blueprint
            parallel: Whether to enable parallel execution for independent steps
            max_workers: Maximum number of parallel workers
            
        Returns:
            Execution result with status, outputs, and metadata
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Initialize execution context
            context = {
                'inputs': inputs or {},
                'steps': {},
                'variables': blueprint.variables.copy() if blueprint.variables else {},
                'system': {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'execution_id': execution_id
                },
                '_lock': threading.Lock()  # For thread-safe context updates
            }
            
            # Get execution order
            execution_order = blueprint.get_execution_order()
            
            # Execute steps in phases (parallel within phases, sequential between phases)
            step_results = {}
            
            for phase_idx, phase in enumerate(execution_order):
                if parallel and len(phase) > 1:
                    # Execute phase steps in parallel
                    phase_results = self._execute_phase_parallel(phase, blueprint, context, max_workers)
                else:
                    # Execute phase steps sequentially
                    phase_results = self._execute_phase_sequential(phase, blueprint, context)
                
                # Update step results and context
                step_results.update(phase_results)
                
                # Check for phase-level failures
                failed_steps = [sid for sid, result in phase_results.items() if not result.get('success', False)]
                if failed_steps:
                    # Handle failures based on blueprint-level error strategy
                    error_strategy = getattr(blueprint, 'error_handling', 'fail_fast')
                    if error_strategy == 'fail_fast':
                        raise Exception(f"Phase {phase_idx + 1} failed. Failed steps: {failed_steps}")
            
            # Extract final outputs
            outputs = self._extract_outputs(blueprint, context)
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'status': 'completed',
                'execution_id': execution_id,
                'execution_time': execution_time,
                'outputs': outputs,
                'step_results': step_results,
                'metadata': {
                    'total_steps': len(blueprint.steps),
                    'steps_executed': len([r for r in step_results.values() if r.get('success')]),
                    'execution_order': execution_order,
                    'parallel_execution': parallel,
                    'phases_executed': len(execution_order)
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'status': 'failed',
                'execution_id': execution_id,
                'execution_time': execution_time,
                'error': str(e),
                'traceback': str(e),
                'step_results': step_results,
                'metadata': {
                    'total_steps': len(blueprint.steps),
                    'steps_executed': len([r for r in step_results.values() if r.get('success')]),
                    'failure_point': len(step_results)
                }
            }
        finally:
            # Clean up
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    def execute_interactive(self, blueprint: Blueprint, inputs: Dict[str, Any] = None, 
                           current_phase: str = None, interaction_callback=None) -> Dict[str, Any]:
        """
        Execute a blueprint with interactive phase-based execution.
        
        This method supports Claude Code-like workflows where execution pauses
        between phases for user interaction and confirmation.
        
        Args:
            blueprint: Blueprint to execute
            inputs: Input values for the blueprint
            current_phase: Specific phase to execute (if None, executes all applicable phases)
            interaction_callback: Callback function for user interaction
            
        Returns:
            Execution result with status, outputs, phase info, and interaction requirements
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Initialize execution context
            context = {
                'inputs': inputs or {},
                'steps': {},
                'variables': blueprint.variables.copy() if blueprint.variables else {},
                'system': {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'execution_id': execution_id
                },
                '_lock': threading.Lock(),
                'current_phase': current_phase
            }
            
            # Filter steps based on current phase if specified
            if current_phase:
                applicable_steps = self._get_phase_steps(blueprint, current_phase, context)
            else:
                applicable_steps = blueprint.steps
            
            # Execute applicable steps
            step_results = {}
            interaction_points = []
            
            for step in applicable_steps:
                # Check if step should be executed based on conditions
                if not self._should_execute_step(step, context):
                    continue
                
                # Check for interaction points (ConversationManagerTool)
                if self._is_interaction_step(step):
                    interaction_result = self._handle_interaction_step(step, context, interaction_callback)
                    step_results[step.id] = interaction_result
                    if interaction_result.get('requires_user_input'):
                        interaction_points.append({
                            'step_id': step.id,
                            'questions': interaction_result.get('questions', []),
                            'context': interaction_result.get('context', {})
                        })
                else:
                    # Execute regular step
                    result = self._execute_step_interactive(step, context, blueprint)
                    step_results[step.id] = result
                    
                    # Update context with step results
                    context['steps'][step.id] = {
                        'outputs': self._process_step_outputs(step, result),
                        'status': 'completed' if result.get('success') else 'failed'
                    }
            
            # Determine next phase and interaction requirements
            next_phase = self._determine_next_phase(blueprint, current_phase, context)
            requires_interaction = len(interaction_points) > 0 or next_phase is not None
            
            # Extract outputs
            outputs = self._extract_outputs(blueprint, context)
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'status': 'phase_completed' if requires_interaction else 'completed',
                'execution_id': execution_id,
                'execution_time': execution_time,
                'current_phase': current_phase,
                'next_phase': next_phase,
                'outputs': outputs,
                'step_results': step_results,
                'interaction_points': interaction_points,
                'requires_user_interaction': requires_interaction,
                'metadata': {
                    'total_steps': len(applicable_steps),
                    'steps_executed': len([r for r in step_results.values() if r.get('success')]),
                    'phase_execution': True,
                    'interaction_points_count': len(interaction_points)
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'status': 'failed',
                'execution_id': execution_id,
                'execution_time': execution_time,
                'current_phase': current_phase,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'step_results': step_results if 'step_results' in locals() else {},
                'metadata': {
                    'failure_point': current_phase,
                    'phase_execution': True
                }
            }
        finally:
            # Clean up
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    def _get_phase_steps(self, blueprint: Blueprint, phase: str, context: Dict[str, Any]) -> List[BlueprintStep]:
        """
        Get steps that belong to a specific phase.
        
        Filters steps based on phase-specific conditions or naming conventions.
        """
        phase_steps = []
        
        for step in blueprint.steps:
            # Check if step belongs to current phase based on condition
            if hasattr(step, 'condition') and step.condition:
                # Evaluate condition to see if it matches current phase
                phase_condition = f"current_phase == '{phase}'"
                if phase_condition in step.condition:
                    if self._evaluate_step_condition(step.condition, context):
                        phase_steps.append(step)
                elif step.condition and self._evaluate_step_condition(step.condition, context):
                    # Also include steps with other conditions that evaluate to true
                    phase_steps.append(step)
            elif step.id.startswith(f"{phase}_"):
                # Include steps that start with phase name
                phase_steps.append(step)
        
        return phase_steps
    
    def _should_execute_step(self, step: BlueprintStep, context: Dict[str, Any]) -> bool:
        """
        Determine if a step should be executed based on its conditions.
        """
        if not hasattr(step, 'condition') or not step.condition:
            return True
        
        return self._evaluate_step_condition(step.condition, context)
    
    def _is_interaction_step(self, step: BlueprintStep) -> bool:
        """
        Check if a step requires user interaction.
        """
        return (hasattr(step, 'tool') and 
                step.tool in ['ConversationManagerTool', 'InteractionTool']) or \
               (hasattr(step, 'action') and 
                step.action in ['interactive_questions', 'user_input', 'confirmation'])
    
    def _handle_interaction_step(self, step: BlueprintStep, context: Dict[str, Any], 
                                callback=None) -> Dict[str, Any]:
        """
        Handle steps that require user interaction.
        """
        try:
            # Get the tool for interaction
            tool = self._get_tool(step.tool)
            if not tool:
                return {
                    'success': False,
                    'error': f"Tool '{step.tool}' not found for interaction step",
                    'requires_user_input': False
                }
            
            # Resolve step inputs
            resolved_inputs = self._resolve_step_inputs(step, context, None)
            
            # Execute the interaction tool
            result = tool.execute(task="", **resolved_inputs)
            
            # Check if this requires actual user input
            if isinstance(result, dict) and result.get('questions'):
                # This step generated questions - requires user interaction
                return {
                    'success': True,
                    'requires_user_input': True,
                    'questions': result.get('questions', []),
                    'context': resolved_inputs,
                    'tool_result': result
                }
            else:
                # Step completed without user interaction needed
                return {
                    'success': True,
                    'requires_user_input': False,
                    'tool_result': result
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'requires_user_input': False
            }
    
    def _execute_step_interactive(self, step: BlueprintStep, context: Dict[str, Any], 
                                 blueprint: Blueprint) -> Dict[str, Any]:
        """
        Execute a single step in interactive mode.
        """
        try:
            # Get the tool
            tool = self._get_tool(step.tool)
            if not tool:
                return {
                    'success': False,
                    'error': f"Tool '{step.tool}' not found"
                }
            
            # Resolve step inputs
            resolved_inputs = self._resolve_step_inputs(step, context, blueprint)
            
            # Execute the tool
            task_description = getattr(step, 'description', f"Execute {step.tool} {getattr(step, 'action', 'operation')}")
            if hasattr(step, 'action') and step.action:
                result = tool.execute(task=task_description, action=step.action, **resolved_inputs)
            else:
                result = tool.execute(task=task_description, **resolved_inputs)
            
            return result if isinstance(result, dict) else {'success': True, 'result': result}
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def _determine_next_phase(self, blueprint: Blueprint, current_phase: str, 
                             context: Dict[str, Any]) -> Optional[str]:
        """
        Determine the next phase to execute based on blueprint metadata and current state.
        """
        # Check if blueprint has phase transition information
        if hasattr(blueprint, 'metadata') and blueprint.metadata:
            phases = getattr(blueprint.metadata, 'phases', None)
            if phases and current_phase:
                try:
                    current_idx = phases.index(current_phase)
                    if current_idx + 1 < len(phases):
                        return phases[current_idx + 1]
                except (ValueError, IndexError):
                    pass
        
        # Fallback: determine next phase based on step naming conventions
        if current_phase == 'design':
            return 'code_creation'
        elif current_phase == 'code_creation':
            return 'iteration'
        elif current_phase == 'iteration':
            return None  # No more phases
        
        return None
    
    def _validate_inputs(self, blueprint: Blueprint, inputs: Dict[str, Any]) -> None:
        """Validate input parameters against blueprint requirements."""
        for input_def in blueprint.inputs:
            if input_def.required and input_def.name not in inputs:
                if input_def.default is None:
                    raise ValueError(f"Required input '{input_def.name}' not provided")
                inputs[input_def.name] = input_def.default
    
    def _execute_phase(self, context: ExecutionContext, step_ids: List[str]) -> None:
        """Execute a phase of steps (potentially in parallel)."""
        # For now, execute sequentially within each phase
        # TODO: Implement parallel execution
        
        for step_id in step_ids:
            step = context.blueprint.get_step_by_id(step_id)
            if step is None:
                continue
            
            try:
                self._execute_step(context, step)
            except Exception as e:
                self._handle_step_error(context, step, e)
                
                # Check if we should stop execution
                if step.error_handling == ErrorHandlingStrategy.FAIL_FAST:
                    context.status = "failed"
                    context.error = f"Step '{step_id}' failed: {str(e)}"
                    break
    
    def _execute_step(self, context: ExecutionContext, step: BlueprintStep) -> None:
        """Execute a single blueprint step."""
        step.status = StepStatus.RUNNING
        step.start_time = datetime.now()
        
        try:
            # Check condition if specified
            if step.condition and not self._evaluate_condition(context, step.condition):
                step.status = StepStatus.SKIPPED
                step.end_time = datetime.now()
                return
            
            # Handle for_each loops
            if step.for_each:
                self._execute_step_for_each(context, step)
            else:
                self._execute_single_step(context, step)
            
            step.status = StepStatus.COMPLETED
            step.end_time = datetime.now()
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.end_time = datetime.now()
            step.error = str(e)
            raise
    
    def _execute_single_step(self, context: ExecutionContext, step: BlueprintStep) -> None:
        """Execute a single step instance."""
        # Resolve step inputs
        resolved_inputs = context.blueprint.substitute_variables(step.inputs)
        
        # Get the tool
        tool = self._get_tool(step.tool)
        if tool is None:
            raise ValueError(f"Tool '{step.tool}' not found in registry")
        
        # Prepare tool execution parameters
        tool_params = {
            'task': f"Execute {step.action} operation",
            **resolved_inputs
        }
        
        # Execute the tool
        result = tool.execute(**tool_params)
        
        # Store step result
        step_result = {
            'step_id': step.id,
            'tool': step.tool,
            'action': step.action,
            'inputs': resolved_inputs,
            'outputs': {},
            'result': result,
            'success': result.get('success', False),
            'execution_time': (step.end_time - step.start_time).total_seconds() if step.end_time and step.start_time else 0
        }
        
        # Extract outputs based on step configuration
        if result.get('success', False):
            for output_key, output_path in step.outputs.items():
                # Extract data from tool result
                output_value = self._extract_output_value(result, output_key)
                step_result['outputs'][output_key] = output_value
                
                # Store in blueprint step results for variable resolution
                if step.id not in context.blueprint.step_results:
                    context.blueprint.step_results[step.id] = {'outputs': {}}
                context.blueprint.step_results[step.id]['outputs'][output_key] = output_value
        
        # Store complete step result
        context.step_results[step.id] = step_result
        step.result = step_result
    
    def _execute_step_for_each(self, context: ExecutionContext, step: BlueprintStep) -> None:
        """Execute a step for each item in a collection."""
        # Resolve the for_each expression
        collection = context.blueprint.resolve_variable(step.for_each.replace('${', '').replace('}', ''))
        
        if not isinstance(collection, list):
            raise ValueError(f"for_each expression '{step.for_each}' did not resolve to a list")
        
        results = []
        
        for index, item in enumerate(collection):
            # Create context for this iteration
            iteration_context = {'item': item, 'index': index}
            
            # Resolve inputs with iteration context
            resolved_inputs = context.blueprint.substitute_variables(step.inputs, iteration_context)
            
            # Get and execute tool
            tool = self._get_tool(step.tool)
            if tool is None:
                if step.error_handling == ErrorHandlingStrategy.CONTINUE:
                    continue
                raise ValueError(f"Tool '{step.tool}' not found in registry")
            
            try:
                tool_params = {
                    'task': f"Execute {step.action} operation (iteration {index})",
                    **resolved_inputs
                }
                
                result = tool.execute(**tool_params)
                results.append({
                    'index': index,
                    'item': item,
                    'result': result,
                    'success': result.get('success', False)
                })
                
            except Exception as e:
                if step.error_handling == ErrorHandlingStrategy.CONTINUE:
                    results.append({
                        'index': index,
                        'item': item,
                        'result': None,
                        'success': False,
                        'error': str(e)
                    })
                else:
                    raise
        
        # Aggregate results
        step_result = {
            'step_id': step.id,
            'tool': step.tool,
            'action': step.action,
            'for_each': step.for_each,
            'iterations': len(results),
            'results': results,
            'outputs': {},
            'success': any(r['success'] for r in results)
        }
        
        # Extract aggregated outputs
        for output_key, output_path in step.outputs.items():
            aggregated_output = [r['result'] for r in results if r['success'] and r['result']]
            step_result['outputs'][output_key] = aggregated_output
            
            # Store for variable resolution
            if step.id not in context.blueprint.step_results:
                context.blueprint.step_results[step.id] = {'outputs': {}}
            context.blueprint.step_results[step.id]['outputs'][output_key] = aggregated_output
        
        context.step_results[step.id] = step_result
        step.result = step_result
    
    def _get_tool(self, tool_name: str):
        """Get a tool instance from the registry."""
        if self.tool_registry is None:
            # Try to import and get tool dynamically
            try:
                if tool_name == "FileSystemTool":
                    from ...tools.core_tools.filesystem_tool import FileSystemTool
                    return FileSystemTool()
                elif tool_name == "ReadTool":
                    from ...tools.core_tools.read_tool import ReadTool
                    return ReadTool()
                elif tool_name == "WriteTool":
                    from ...tools.core_tools.write_tool import WriteTool
                    return WriteTool()
                elif tool_name == "GrepTool":
                    from ...tools.core_tools.grep_tool import GrepTool
                    return GrepTool()
                elif tool_name == "CodingTool":
                    from ...tools.core_tools.coding_tool import CodingTool
                    return CodingTool()
                elif tool_name == "ContentGenerationTool":
                    from ...tools.core_tools.content_gen_tool import ContentGenerationTool
                    return ContentGenerationTool()
                elif tool_name == "BashTool":
                    from ...tools.core_tools.bash_tool import BashTool
                    return BashTool()
                else:
                    return None
            except ImportError:
                return None
        else:
            # Use registry if available
            return self.tool_registry.get_tool(tool_name)
    
    def _extract_output_value(self, result: Dict[str, Any], output_key: str) -> Any:
        """Extract output value from tool result."""
        # Try different common result structures
        if 'data' in result and isinstance(result['data'], dict):
            if output_key in result['data']:
                return result['data'][output_key]
            # Try to return the entire data if no specific key
            return result['data']
        
        # Return the entire result if no data section
        return result
    
    def _evaluate_condition(self, context: ExecutionContext, condition: str) -> bool:
        """Evaluate a condition expression."""
        # Simple condition evaluation - could be enhanced
        try:
            # Substitute variables in condition
            resolved_condition = context.blueprint.substitute_variables(condition)
            
            # Basic evaluation (this is simplified - could use a proper expression evaluator)
            if '!=' in resolved_condition:
                left, right = resolved_condition.split('!=')
                return left.strip() != right.strip()
            elif '==' in resolved_condition:
                left, right = resolved_condition.split('==')
                return left.strip() == right.strip()
            elif 'null' in resolved_condition.lower():
                return 'null' not in resolved_condition.lower()
            
            # Default to True if can't evaluate
            return True
            
        except Exception:
            # Default to True if evaluation fails
            return True
    
    def _handle_step_error(self, context: ExecutionContext, step: BlueprintStep, error: Exception) -> None:
        """Handle step execution errors based on error handling strategy."""
        error_msg = str(error)
        
        if step.error_handling == ErrorHandlingStrategy.RETRY and step.retry_count < step.max_retries:
            step.retry_count += 1
            # TODO: Implement retry logic
            pass
        elif step.error_handling == ErrorHandlingStrategy.CONTINUE:
            # Log error but continue execution
            step.status = StepStatus.FAILED
            step.error = error_msg
        elif step.error_handling == ErrorHandlingStrategy.SKIP:
            step.status = StepStatus.SKIPPED
        else:  # FAIL_FAST
            step.status = StepStatus.FAILED
            step.error = error_msg
            raise
    
    def _extract_outputs(self, blueprint: Blueprint, context: ExecutionContext) -> Dict[str, Any]:
        """Extract final outputs from blueprint execution."""
        outputs = {}
        
        for output_def in blueprint.outputs:
            if output_def.source:
                # Extract from specified source
                try:
                    value = blueprint.resolve_variable(output_def.source.replace('${', '').replace('}', ''))
                    outputs[output_def.name] = value
                except Exception:
                    outputs[output_def.name] = None
            else:
                # Try to find in step results
                outputs[output_def.name] = None
        
        return outputs
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a running execution."""
        if execution_id in self.active_executions:
            context = self.active_executions[execution_id]
            return {
                "execution_id": execution_id,
                "status": context.status,
                "start_time": context.start_time.isoformat(),
                "blueprint_name": context.blueprint.metadata.name,
                "completed_steps": len([s for s in context.blueprint.steps if s.status == StepStatus.COMPLETED]),
                "total_steps": len(context.blueprint.steps)
            }
        return None
    
    def _execute_phase_parallel(self, step_ids: List[str], blueprint: 'Blueprint', 
                               context: Dict[str, Any], max_workers: int) -> Dict[str, Any]:
        """Execute a phase of steps in parallel."""
        phase_results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all steps in the phase
            future_to_step = {}
            for step_id in step_ids:
                step = next(s for s in blueprint.steps if s.id == step_id)
                future = executor.submit(self._execute_step_thread_safe, step, context, blueprint)
                future_to_step[future] = step_id
            
            # Collect results as they complete
            for future in as_completed(future_to_step):
                step_id = future_to_step[future]
                try:
                    result = future.result()
                    phase_results[step_id] = result
                    
                    # Thread-safe context update
                    with context['_lock']:
                        context['steps'][step_id] = {
                            'outputs': result.get('outputs', {}),
                            'success': result.get('success', False)
                        }
                except Exception as e:
                    phase_results[step_id] = {
                        'success': False,
                        'error': str(e),
                        'tool': 'unknown',
                        'execution_time': 0
                    }
        
        return phase_results
    
    def _execute_phase_sequential(self, step_ids: List[str], blueprint: 'Blueprint', 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a phase of steps sequentially."""
        phase_results = {}
        
        for step_id in step_ids:
            step = next(s for s in blueprint.steps if s.id == step_id)
            result = self._execute_step(step, context, blueprint)
            phase_results[step_id] = result
            
            # Update context
            context['steps'][step_id] = {
                'outputs': result.get('outputs', {}),
                'success': result.get('success', False)
            }
        
        return phase_results
    
    def _execute_step_thread_safe(self, step, context: Dict[str, Any], blueprint: 'Blueprint') -> Dict[str, Any]:
        """Execute a step in a thread-safe manner."""
        # Create a local copy of context for thread safety
        with context['_lock']:
            local_context = {
                'inputs': context['inputs'].copy(),
                'steps': context['steps'].copy(),
                'variables': context['variables'].copy(),
                'system': context['system'].copy()
            }
        
        return self._execute_step(step, local_context, blueprint)
    
    def _execute_step(self, step, context: Dict[str, Any], blueprint: 'Blueprint') -> Dict[str, Any]:
        """Execute a single step with enhanced error handling and retry logic."""
        step_start_time = time.time()
        max_retries = getattr(step, 'max_retries', 3)
        retry_delay = getattr(step, 'retry_delay', 1.0)
        
        for attempt in range(max_retries + 1):
            try:
                # Check conditions if specified
                if hasattr(step, 'condition') and step.condition:
                    if not self._evaluate_step_condition(step.condition, context):
                        return {
                            'success': True,
                            'skipped': True,
                            'tool': step.tool,
                            'execution_time': time.time() - step_start_time,
                            'outputs': {},
                            'message': 'Step skipped due to condition'
                        }
                
                # Resolve tool
                tool = self._get_tool(step.tool)
                if not tool:
                    raise Exception(f"Tool '{step.tool}' not found")
                
                # Prepare inputs with variable substitution
                resolved_inputs = self._resolve_step_inputs(step, context, blueprint)
                
                # Execute tool
                if hasattr(tool, 'execute'):
                    result = tool.execute(resolved_inputs)
                else:
                    result = tool.run(resolved_inputs)
                
                # Process outputs
                outputs = self._process_step_outputs(step, result)
                
                execution_time = time.time() - step_start_time
                
                return {
                    'success': True,
                    'tool': step.tool,
                    'execution_time': execution_time,
                    'outputs': outputs,
                    'result': result,
                    'attempt': attempt + 1
                }
                
            except Exception as e:
                if attempt < max_retries:
                    # Retry with delay
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    # Final failure
                    execution_time = time.time() - step_start_time
                    return {
                        'success': False,
                        'tool': step.tool,
                        'execution_time': execution_time,
                        'error': str(e),
                        'attempts': attempt + 1,
                        'outputs': {}
                    }
    
    def _evaluate_step_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a step condition."""
        try:
            # Simple variable substitution and evaluation
            resolved_condition = self._substitute_variables(condition, context)
            
            # Basic condition evaluation
            if '==' in resolved_condition:
                left, right = resolved_condition.split('==', 1)
                return left.strip().strip('"\'') == right.strip().strip('"\'')
            elif '!=' in resolved_condition:
                left, right = resolved_condition.split('!=', 1)
                return left.strip().strip('"\'') != right.strip().strip('"\'')
            elif '>' in resolved_condition:
                left, right = resolved_condition.split('>', 1)
                return float(left.strip()) > float(right.strip())
            elif '<' in resolved_condition:
                left, right = resolved_condition.split('<', 1)
                return float(left.strip()) < float(right.strip())
            
            # Default to True if can't evaluate
            return True
            
        except Exception:
            return True
    
    def _resolve_step_inputs(self, step, context: Dict[str, Any], blueprint: 'Blueprint') -> Dict[str, Any]:
        """Resolve step inputs with variable substitution."""
        resolved_inputs = {}
        
        for key, value in step.inputs.items():
            if isinstance(value, str):
                resolved_inputs[key] = self._substitute_variables(value, context)
            else:
                resolved_inputs[key] = value
        
        return resolved_inputs
    
    def _substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Substitute variables in text using context."""
        if not isinstance(text, str):
            return text
        
        import re
        
        # Find all variable references ${...}
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_path = match.group(1)
            try:
                # Handle different variable sources
                if var_path.startswith('inputs.'):
                    key = var_path[7:]  # Remove 'inputs.'
                    return str(context['inputs'].get(key, ''))
                elif var_path.startswith('steps.'):
                    # Parse steps.step_id.outputs.output_key
                    parts = var_path.split('.')
                    if len(parts) >= 4 and parts[2] == 'outputs':
                        step_id = parts[1]
                        output_key = parts[3]
                        if step_id in context['steps']:
                            return str(context['steps'][step_id]['outputs'].get(output_key, ''))
                elif var_path.startswith('variables.'):
                    key = var_path[10:]  # Remove 'variables.'
                    return str(context['variables'].get(key, ''))
                elif var_path.startswith('system.'):
                    key = var_path[7:]  # Remove 'system.'
                    return str(context['system'].get(key, ''))
                
                return match.group(0)  # Return original if can't resolve
            except Exception:
                return match.group(0)  # Return original on error
        
        return re.sub(pattern, replace_var, text)
    
    def _process_step_outputs(self, step, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process step outputs from tool result."""
        outputs = {}
        
        if hasattr(step, 'outputs') and step.outputs:
            for output_key, output_mapping in step.outputs.items():
                # Extract value from result based on mapping
                if isinstance(result, dict):
                    if output_mapping in result:
                        outputs[output_key] = result[output_mapping]
                    elif 'result' in result and isinstance(result['result'], dict):
                        outputs[output_key] = result['result'].get(output_mapping, result)
                    else:
                        outputs[output_key] = result
                else:
                    outputs[output_key] = result
        else:
            # If no output mapping specified, return the entire result
            outputs = result if isinstance(result, dict) else {'result': result}
        
        return outputs
    
    def _extract_outputs(self, blueprint: 'Blueprint', context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract final blueprint outputs."""
        outputs = {}
        
        for output_def in blueprint.outputs:
            if hasattr(output_def, 'source') and output_def.source:
                # Resolve output from source
                value = self._substitute_variables(output_def.source, context)
                outputs[output_def.name] = value
            else:
                # Try to find in step results
                outputs[output_def.name] = None
        
        return outputs
