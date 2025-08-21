"""
Unified Smart Orchestrator
Enhanced SmartOrchestrator with unified tool execution and remote capabilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .smart_orchestrator import SmartOrchestrator
from .models import ExecutionResult
from ..mcp.registry import UnifiedToolRegistry
from ..mcp.client import MCPClient

class UnifiedOrchestrator(SmartOrchestrator):
    """Enhanced SmartOrchestrator with unified tool execution and remote capabilities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unified_registry = UnifiedToolRegistry()
        self.remote_enabled = False
        self.remote_initialization_attempted = False
        self.logger = logging.getLogger(__name__)
        
        # Remote server configuration
        self.server_configs = [
            {"name": "filesystem", "uri": "http://localhost:3001"}
        ]
    
    async def initialize_remote(self, server_configs: List[Dict] = None):
        """Initialize remote execution capabilities"""
        if self.remote_initialization_attempted:
            return self.remote_enabled
        
        self.remote_initialization_attempted = True
        
        if server_configs is None:
            server_configs = self.server_configs
        
        try:
            # Register local tools first
            self._register_local_tools()
            
            # Initialize remote capabilities
            success = await self.unified_registry.initialize_remote(server_configs)
            self.remote_enabled = success
            
            # Get execution stats
            stats = self.unified_registry.get_execution_stats()
            available_tools = self.unified_registry.get_available_tools()
            
            self.logger.info(f"[REMOTE] Initialization {'successful' if success else 'failed'}!")
            self.logger.info(f"[TOOLS] Available tools: {len(available_tools['local'])} local, {len(available_tools['remote'])} remote")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"[REMOTE] Initialization failed, using local tools only: {e}")
            self.remote_enabled = False
            return False
    
    def _register_local_tools(self, tools_dict=None):
        """Register local tools in the unified registry"""
        # Get tools from parameter first, then parent class registry
        tools_to_register = tools_dict or getattr(self, 'tools_registry', {})
        
        if tools_to_register:
            for tool_name, tool_instance in tools_to_register.items():
                self.unified_registry.register_tool(tool_name, tool_instance)
                self.logger.debug(f"[TOOLS] Registered local tool: {tool_name}")
        else:
            self.logger.warning("[TOOLS] No tools found to register")
    
    def execute_query(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Enhanced execute with unified tool execution"""
        start_time = datetime.now()
        
        # Initialize remote capabilities if not already done (non-blocking)
        if not self.remote_initialization_attempted:
            try:
                # Run remote initialization in background
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.initialize_remote())
                loop.close()
            except Exception as e:
                self.logger.debug(f"[REMOTE] Background initialization failed: {e}")
        
        # Use the parent class's process_query method instead of execute
        # since execute expects an analysis object, not a query string
        try:
            from ..core.agent import SingleAgent
            
            # Create a temporary agent to process the query
            agent = SingleAgent()
            result = agent.process_query(query, session_id=session_id)
            
            # Extract response from result
            if isinstance(result, dict):
                response = result.get('response', str(result))
            else:
                response = str(result)
            
            return {
                'response': response,
                'status': 'success',
                'execution_method': 'unified_agent',
                'remote_enabled': self.remote_enabled,
                'execution_stats': self.get_execution_stats() if self.remote_enabled else None,
                'execution_time': (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            self.logger.error(f"[UNIFIED] Execution failed: {e}")
            return {
                'response': f'Execution failed: {str(e)}',
                'status': 'error',
                'error': str(e),
                'execution_method': 'failed',
                'remote_enabled': self.remote_enabled,
                'execution_time': (datetime.now() - start_time).total_seconds()
            }
    
    async def _execute_tool(self, tool_name: str, query: str, context: Dict) -> Dict:
        """Execute tool with unified tool registry"""
        try:
            # Prepare execution context
            exec_context = {
                'query': query,
                'session_id': context.get('session_id'),
                'execution_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'orchestrator': 'unified_orchestrator'
                }
            }
            
            # Add planning guidance if available
            if context.get('task_tracker'):
                exec_context.update({
                    'planning_guidance': self._reference_planning_file(context),
                    'task_status': self._get_next_task(context),
                    'completed_tasks': context['task_tracker'].get('completed_tasks', [])
                })

            # Convert query to arguments format expected by tools
            arguments = {'query': query}
            
            # Add any additional context needed for execution
            if 'session_id' in context:
                arguments['session_id'] = context['session_id']
            
            # Execute via unified registry
            result = await self.unified_registry.execute_tool(tool_name, arguments, context)
            
            # Check for execution stats
            execution_method = 'unknown'
            if '_execution_stats' in result:
                execution_method = result['_execution_stats'].get('method', 'unknown')
                # Remove execution stats from result to avoid leaking implementation details
                del result['_execution_stats']
            
            return {
                'result': result,
                'execution_method': execution_method
            }
            
        except Exception as e:
            self.logger.error(f"Tool execution failed for {tool_name}: {e}")
            return {
                'result': {
                    'error': f"Tool execution failed: {str(e)}",
                    'tool_name': tool_name
                },
                'execution_method': 'failed',
                'error': str(e)
            }
    
    def _single_tool_execution(self, query: str, analysis, context: Dict) -> ExecutionResult:
        """Execute a single tool with unified tool registry"""
        tool_name = analysis.required_tools[0] if analysis.required_tools else None
        
        if not tool_name:
            return self._direct_response(query, analysis, context)
        
        # Register tools from context if not already registered
        if context.get('tools'):
            self._register_local_tools(context['tools'])
        
        results = []
        
        # Execute tool with unified registry
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self._execute_tool(tool_name, query, context)
            )
        finally:
            loop.close()
        
        results.append({
            'tool': tool_name,
            'result': result['result'],
            'execution_method': result.get('execution_method', 'unified')
        })
        
        # Synthesize results with LLM
        prompt = f"""The user asked: {query}
        
        The tool {tool_name} returned this result:
        {result['result']}
        
        Please provide a helpful and clear response to the user's query."""
        
        # Use LLM for synthesis
        llm = context.get('llm')
        if llm:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that synthesizes tool results into clear responses."},
                {"role": "user", "content": prompt}
            ]
            synthesis_result = llm.chat(messages)
        else:
            synthesis_result = f"Tool {tool_name} result: {result['result']}"
        
        return ExecutionResult(
            response=synthesis_result,
            strategy_used='single_tool',
            tools_used=[tool_name],
            execution_time=0.0,
            confidence=getattr(analysis, 'confidence', 0.8),
            metadata={
                'tool_results': results,
                'execution_method': 'single_tool',
                'remote_enabled': self.remote_enabled
            }
        )
    
    def _sequential_execution(self, query: str, analysis, context: Dict) -> ExecutionResult:
        """Enhanced sequential execution with unified tool execution"""
        results = []
        
        for i, tool_name in enumerate(analysis.required_tools):
            try:
                # Update task progress: start
                if context.get('task_tracker'):
                    self._update_task_progress(context, f"Execute {tool_name}", "started")
                
                # Execute tool with unified registry
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self._execute_tool(tool_name, query, context)
                    )
                finally:
                    loop.close()
                
                results.append({
                    'tool': tool_name,
                    'result': result['result'],
                    'execution_method': result.get('execution_method', 'unified')
                })
                
                # Update task progress: complete
                if context.get('task_tracker'):
                    self._update_task_progress(context, f"Execute {tool_name}", "completed")
                    self._update_task_progress(context, f"Process {tool_name} results", "completed")
                
            except Exception as e:
                error_msg = f"Error executing {tool_name}: {str(e)}"
                self.logger.error(f"[ORCHESTRATOR] {error_msg}")
                
                results.append({
                    'tool': tool_name,
                    'result': error_msg,
                    'error': True,
                    'execution_method': 'failed'
                })
                
                # Update task progress: failed
                if context.get('task_tracker'):
                    self._update_task_progress(context, f"Execute {tool_name}", "failed", error_msg)
        
        # Final synthesis with MCP context
        if context.get('task_tracker'):
            self._update_task_progress(context, "Integrate multiple tool outputs", "started")
        
        try:
            # Synthesize results with LLM
            llm = context.get('llm')
            if llm and results:
                # Create synthesis prompt
                tool_summaries = []
                for result in results:
                    tool_name = result.get('tool', 'Unknown')
                    tool_result = result.get('result', 'No result')
                    tool_summaries.append(f"- {tool_name}: {tool_result}")
                
                prompt = f"""The user asked: {query}
                
Multiple tools were executed with these results:
{chr(10).join(tool_summaries)}
                
Please provide a clear, focused response that addresses the user's query using these tool results."""
                
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that synthesizes multiple tool results into clear, focused responses."},
                    {"role": "user", "content": prompt}
                ]
                synthesis_result = llm.chat(messages)
            else:
                synthesis_result = f"Executed {len(results)} tools but synthesis failed"
            
            if context.get('task_tracker'):
                self._update_task_progress(context, "Integrate multiple tool outputs", "completed")
                self._update_task_progress(context, "Generate final response", "completed")
                self._update_task_progress(context, "Quality check and validation", "completed")
        
        except Exception as e:
            synthesis_result = f"Error in synthesis: {str(e)}"
            if context.get('task_tracker'):
                self._update_task_progress(context, "Integrate multiple tool outputs", "failed", str(e))
        
        return ExecutionResult(
            response=synthesis_result,
            strategy_used='sequential',
            tools_used=[result['tool'] for result in results if 'tool' in result],
            execution_time=0.0,
            confidence=getattr(analysis, 'confidence', 0.8),
            metadata={
                'tool_results': results,
                'execution_method': 'unified',
                'remote_enabled': self.remote_enabled,
                'execution_stats': self.get_execution_stats() if self.remote_enabled else None
            }
        )
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.remote_enabled:
            return {'remote_enabled': False}
        
        try:
            stats = self.unified_registry.get_execution_stats()
            available_tools = self.unified_registry.get_available_tools()
            
            return {
                'remote_enabled': True,
                'execution_stats': stats,
                'available_tools': available_tools,
                'remote_registry_stats': self.unified_registry.get_remote_registry_stats() if hasattr(self.unified_registry, 'get_remote_registry_stats') else None
            }
        except Exception as e:
            return {'remote_enabled': True, 'stats_error': str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        base_status = {
            'orchestrator': 'UnifiedOrchestrator',
            'remote_initialization_attempted': self.remote_initialization_attempted,
            'remote_enabled': self.remote_enabled,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.remote_enabled:
            base_status.update(self.get_execution_stats())
        
        return base_status
    
    async def shutdown(self):
        """Gracefully shutdown all components"""
        if self.unified_registry:
            await self.unified_registry.shutdown()
        self.logger.info("[UNIFIED] Orchestrator shutdown complete")

# Convenience function to create unified orchestrator
def create_unified_orchestrator(**kwargs) -> UnifiedOrchestrator:
    """Create and return a unified orchestrator"""
    return UnifiedOrchestrator(**kwargs)
