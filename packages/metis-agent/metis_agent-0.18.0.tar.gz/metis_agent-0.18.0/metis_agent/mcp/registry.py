"""
MCP Tool Registry
Manages tool discovery, registration, and execution via MCP protocol
"""

from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from .client import MCPClient
from .connection_manager import MCPConnectionManager

@dataclass
class MCPTool:
    """Represents an MCP tool"""
    name: str
    server_name: str
    description: str
    input_schema: Dict
    output_schema: Optional[Dict] = None
    category: Optional[str] = None
    version: Optional[str] = None

class MCPToolRegistry:
    """Registry for MCP-enabled tools with advanced features"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.connection_manager = MCPConnectionManager(mcp_client)
        self.tools: Dict[str, MCPTool] = {}
        self.tool_mapping: Dict[str, str] = {}  # tool_name -> server_name
        self.server_tools: Dict[str, List[str]] = {}  # server_name -> [tool_names]
        self.logger = logging.getLogger(__name__)
        self._discovery_lock = asyncio.Lock()
        self._tool_cache: Dict[str, Dict] = {}  # Cache for tool results
        self._cache_ttl = 300  # 5 minutes cache TTL
    
    async def initialize(self, server_configs: List[Dict]):
        """Initialize the registry with server configurations"""
        try:
            # Start connection manager
            await self.connection_manager.start_health_monitoring()
            
            # Register and connect to servers
            for config in server_configs:
                server_name = config['name']
                server_uri = config['uri']
                
                success = await self.connection_manager.register_server(
                    server_name, server_uri, auto_connect=True
                )
                
                if success:
                    self.logger.info(f"Successfully connected to MCP server: {server_name}")
                else:
                    self.logger.warning(f"Failed to connect to MCP server: {server_name}")
            
            # Discover all available tools
            await self.discover_all_tools()
            
            self.logger.info(f"MCP Registry initialized with {len(self.tools)} tools from {len(server_configs)} servers")
            
        except Exception as e:
            self.logger.error(f"Error initializing MCP registry: {e}")
            raise
    
    async def discover_all_tools(self) -> Dict[str, List[MCPTool]]:
        """Discover all available tools from all connected servers"""
        async with self._discovery_lock:
            discovered_tools = {}
            
            for server_name in self.connection_manager.get_healthy_servers():
                try:
                    tools = await self._discover_server_tools(server_name)
                    discovered_tools[server_name] = tools
                    
                    # Register tools in the registry
                    for tool in tools:
                        await self._register_tool(tool)
                    
                    self.logger.info(f"Discovered {len(tools)} tools from {server_name}")
                    
                except Exception as e:
                    self.logger.error(f"Error discovering tools from {server_name}: {e}")
            
            return discovered_tools
    
    async def _discover_server_tools(self, server_name: str) -> List[MCPTool]:
        """Discover tools from a specific server"""
        try:
            # Get raw tool data from server
            raw_tools = await self.mcp_client.list_tools(server_name)
            
            # Convert to MCPTool objects
            tools = []
            for tool_data in raw_tools:
                tool = MCPTool(
                    name=tool_data.get('name', 'unknown'),
                    server_name=server_name,
                    description=tool_data.get('description', ''),
                    input_schema=tool_data.get('input_schema', {}),
                    output_schema=tool_data.get('output_schema'),
                    category=tool_data.get('category'),
                    version=tool_data.get('version')
                )
                tools.append(tool)
            
            return tools
            
        except Exception as e:
            self.logger.error(f"Error discovering tools from {server_name}: {e}")
            return []
    
    async def _register_tool(self, tool: MCPTool):
        """Register a discovered tool"""
        # Store tool
        self.tools[tool.name] = tool
        
        # Update mappings
        self.tool_mapping[tool.name] = tool.server_name
        
        if tool.server_name not in self.server_tools:
            self.server_tools[tool.server_name] = []
        
        if tool.name not in self.server_tools[tool.server_name]:
            self.server_tools[tool.server_name].append(tool.name)
    
    async def execute_tool(self, tool_name: str, arguments: Dict, context: Dict = None) -> Dict:
        """Execute a tool with enhanced context and error handling"""
        try:
            # Check if tool exists
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found in registry")
            
            tool = self.tools[tool_name]
            server_name = tool.server_name
            
            # Ensure server is connected
            if not await self.connection_manager.ensure_server_connection(server_name):
                raise ConnectionError(f"Cannot connect to server '{server_name}' for tool '{tool_name}'")
            
            # Check cache first
            cache_key = self._generate_cache_key(tool_name, arguments)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.logger.debug(f"Returning cached result for {tool_name}")
                return cached_result
            
            # Prepare enhanced arguments with context
            enhanced_args = arguments.copy()
            if context:
                enhanced_args['_context'] = context
            
            # Execute the tool
            self.logger.debug(f"Executing tool '{tool_name}' on server '{server_name}'")
            result = await self.mcp_client.call_tool(server_name, tool_name, enhanced_args)
            
            # Cache the result if successful
            if not result.get('error'):
                self._cache_result(cache_key, result)
            
            # Add metadata to result
            result['_metadata'] = {
                'tool_name': tool_name,
                'server_name': server_name,
                'execution_time': datetime.now().isoformat(),
                'cached': False
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}': {e}")
            return {
                'error': str(e),
                'tool_name': tool_name,
                'server_name': self.tool_mapping.get(tool_name, 'unknown'),
                'execution_time': datetime.now().isoformat()
            }
    
    def _generate_cache_key(self, tool_name: str, arguments: Dict) -> str:
        """Generate a cache key for tool execution"""
        import hashlib
        import json
        
        # Create a deterministic string from tool name and arguments
        cache_data = {
            'tool': tool_name,
            'args': arguments
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if still valid"""
        if cache_key in self._tool_cache:
            cached_data = self._tool_cache[cache_key]
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            
            # Check if cache is still valid
            if (datetime.now() - cache_time).total_seconds() < self._cache_ttl:
                result = cached_data['result'].copy()
                result['_metadata']['cached'] = True
                return result
            else:
                # Remove expired cache entry
                del self._tool_cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Cache a tool execution result"""
        self._tool_cache[cache_key] = {
            'result': result.copy(),
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """Get tool input/output schema"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            return {
                'name': tool.name,
                'description': tool.description,
                'input_schema': tool.input_schema,
                'output_schema': tool.output_schema,
                'server': tool.server_name,
                'category': tool.category,
                'version': tool.version
            }
        return None
    
    def list_tools(self, server_name: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
        """List available tools with optional filtering"""
        tools = []
        
        for tool_name, tool in self.tools.items():
            # Apply filters
            if server_name and tool.server_name != server_name:
                continue
            if category and tool.category != category:
                continue
            
            tools.append({
                'name': tool.name,
                'description': tool.description,
                'server': tool.server_name,
                'category': tool.category,
                'version': tool.version
            })
        
        return tools
    
    def get_server_tools(self, server_name: str) -> List[str]:
        """Get list of tools available on a specific server"""
        return self.server_tools.get(server_name, [])
    
    async def refresh_tools(self, server_name: Optional[str] = None):
        """Refresh tool discovery for all servers or a specific server"""
        if server_name:
            # Refresh specific server
            if server_name in self.connection_manager.get_healthy_servers():
                tools = await self._discover_server_tools(server_name)
                
                # Remove old tools from this server
                old_tools = self.server_tools.get(server_name, [])
                for tool_name in old_tools:
                    if tool_name in self.tools:
                        del self.tools[tool_name]
                    if tool_name in self.tool_mapping:
                        del self.tool_mapping[tool_name]
                
                # Register new tools
                for tool in tools:
                    await self._register_tool(tool)
                
                self.logger.info(f"Refreshed {len(tools)} tools from {server_name}")
        else:
            # Refresh all servers
            await self.discover_all_tools()
    
    def clear_cache(self):
        """Clear the tool execution cache"""
        self._tool_cache.clear()
        self.logger.info("Tool execution cache cleared")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        healthy_servers = self.connection_manager.get_healthy_servers()
        
        stats = {
            'total_tools': len(self.tools),
            'total_servers': len(self.mcp_client.servers),
            'healthy_servers': len(healthy_servers),
            'cached_results': len(self._tool_cache),
            'tools_by_server': {
                server: len(tools) for server, tools in self.server_tools.items()
            },
            'tools_by_category': {},
            'server_status': self.connection_manager.get_server_stats()
        }
        
        # Count tools by category
        for tool in self.tools.values():
            category = tool.category or 'uncategorized'
            stats['tools_by_category'][category] = stats['tools_by_category'].get(category, 0) + 1
        
        return stats
    
    async def shutdown(self):
        """Gracefully shutdown the registry"""
        self.logger.info("Shutting down MCP tool registry...")
        
        # Clear cache
        self.clear_cache()
        
        # Shutdown connection manager
        await self.connection_manager.graceful_shutdown()
        
        # Clear registries
        self.tools.clear()
        self.tool_mapping.clear()
        self.server_tools.clear()
        
        self.logger.info("MCP tool registry shutdown complete")


class UnifiedToolRegistry:
    """Unified registry for all tools regardless of execution method
    
    This registry treats all tools equally - assuming they all implement the
    execute() method as per the new standard. Remote MCP tools are still 
    supported through the MCP client for distributed execution.
    """
    
    def __init__(self):
        self.local_tools: Dict[str, Any] = {}
        self.mcp_registry: Optional[MCPToolRegistry] = None
        self.remote_enabled: bool = False
        self.logger = logging.getLogger(__name__)
        self._execution_stats = {
            'local_success': 0,
            'local_failure': 0,
            'remote_success': 0,
            'remote_failure': 0
        }
    
    async def initialize_remote(self, server_configs: List[Dict]) -> bool:
        """Initialize remote MCP execution capabilities
        
        Args:
            server_configs: List of server configuration dictionaries
            
        Returns:
            bool: True if remote initialization successful, False otherwise
        """
        try:
            # Create MCP client
            from .client import MCPClient
            mcp_client = MCPClient()
            
            # Create and initialize MCP registry
            self.mcp_registry = MCPToolRegistry(mcp_client)
            await self.mcp_registry.initialize(server_configs)
            
            self.remote_enabled = True
            self.logger.info("Remote MCP capabilities initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize remote MCP capabilities: {e}")
            self.mcp_registry = None
            self.remote_enabled = False
            return False
    
    def register_tool(self, tool_name: str, tool_instance: Any):
        """Register a tool in the registry
        
        Args:
            tool_name: Name of the tool
            tool_instance: Tool instance implementing execute() method
        """
        if not hasattr(tool_instance, 'execute'):
            self.logger.warning(f"Tool {tool_name} does not implement execute() method")
        
        self.local_tools[tool_name] = tool_instance
        self.logger.debug(f"Registered tool: {tool_name}")
    
    async def execute_tool(self, tool_name: str, arguments: Dict, context: Dict = None) -> Dict:
        """Execute a tool by name
        
        Tool execution follows this priority:
        1. Local tool execution
        2. Remote MCP execution (if enabled and tool exists remotely)
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of arguments to pass to the tool
            context: Optional execution context
            
        Returns:
            Dict: Tool execution result
        """
        start_time = datetime.now()
        
        # Always set default context if none provided
        if context is None:
            context = {}
            
        # First try local execution
        if tool_name in self.local_tools:
            try:
                result = await self._execute_local_tool(tool_name, arguments, context)
                self._execution_stats['local_success'] += 1
                
                execution_time = (datetime.now() - start_time).total_seconds()
                result['_execution_stats'] = {
                    'method': 'local',
                    'execution_time': execution_time
                }
                return result
                
            except Exception as e:
                self._execution_stats['local_failure'] += 1
                self.logger.error(f"Local execution of {tool_name} failed: {e}")
                # Continue to remote execution if available
        
        # Try remote execution if enabled and tool exists remotely
        if self.remote_enabled and self.mcp_registry is not None:
            try:
                # Check if tool is available in MCP registry
                if tool_name in self.mcp_registry.tools:
                    self.logger.info(f"Executing {tool_name} via remote MCP")
                    result = await self.mcp_registry.execute_tool(tool_name, arguments, context)
                    self._execution_stats['remote_success'] += 1
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    result['_execution_stats'] = {
                        'method': 'remote',
                        'execution_time': execution_time
                    }
                    return result
                        
            except Exception as e:
                self._execution_stats['remote_failure'] += 1
                self.logger.error(f"Remote execution of {tool_name} failed: {e}")
        
        # No execution method available or all methods failed
        return {
            'error': f"Tool '{tool_name}' execution failed or tool not found",
            'tool_name': tool_name,
            'available_methods': {
                'local_available': tool_name in self.local_tools,
                'remote_available': self.remote_enabled and 
                                  self.mcp_registry is not None and 
                                  tool_name in self.mcp_registry.tools if self.mcp_registry else False
            }
        }
    
    async def _execute_local_tool(self, tool_name: str, arguments: Dict, context: Dict = None) -> Dict:
        """Execute a local tool
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of arguments to pass to the tool
            context: Optional execution context
            
        Returns:
            Dict: Tool execution result
        """
        tool_instance = self.local_tools[tool_name]
        
        # Extract query from arguments if present
        query = arguments.get('query', '')
        
        # Execute the tool
        if asyncio.iscoroutinefunction(tool_instance.execute):
            result = await tool_instance.execute(query, **arguments)
        else:
            result = tool_instance.execute(query, **arguments)
        
        # Normalize result format
        if isinstance(result, str):
            return {'content': result, 'status': 'success'}
        elif isinstance(result, dict):
            return result
        else:
            return {'content': str(result), 'status': 'success'}
    
    def get_available_tools(self) -> Dict[str, List[str]]:
        """Get list of available tools by location
        
        Returns:
            Dict: Dictionary of available tools by location
        """
        available = {
            'local': list(self.local_tools.keys()),
            'remote': []
        }
        
        if self.remote_enabled and self.mcp_registry:
            available['remote'] = list(self.mcp_registry.tools.keys())
        
        return available
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics
        
        Returns:
            Dict: Dictionary of execution statistics
        """
        total_executions = sum(self._execution_stats.values())
        
        if total_executions == 0:
            return self._execution_stats
        
        stats = self._execution_stats.copy()
        stats['total_executions'] = total_executions
        stats['local_success_rate'] = stats['local_success'] / max(1, stats['local_success'] + stats['local_failure'])
        stats['remote_success_rate'] = stats['remote_success'] / max(1, stats['remote_success'] + stats['remote_failure']) 
        
        return stats
    
    async def shutdown(self):
        """Gracefully shutdown the registry"""
        if self.mcp_registry:
            await self.mcp_registry.shutdown()
        
        self.local_tools.clear()
        self.logger.info("Unified tool registry shutdown complete")
