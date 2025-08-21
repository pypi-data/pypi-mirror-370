"""
MCP Client Implementation for Metis Agent
Handles connections and communication with MCP servers
"""

from typing import Dict, List, Any, Optional, Union
import asyncio
import json
import logging
from dataclasses import dataclass, field
import aiohttp
import websockets
from datetime import datetime

@dataclass
class MCPServer:
    """Represents an MCP server connection"""
    name: str
    uri: str
    status: str = "disconnected"
    tools: List[Dict] = field(default_factory=list)
    resources: List[Dict] = field(default_factory=list)
    last_ping: Optional[datetime] = None
    connection_attempts: int = 0
    max_retries: int = 3

class MCPClient:
    """Enhanced MCP client for Metis Agent"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.connections: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self.session = None
        self._connection_lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect_all()
        if self.session:
            await self.session.close()
    
    async def connect_to_server(self, server_uri: str, server_name: str) -> bool:
        """Connect to an MCP server"""
        async with self._connection_lock:
            try:
                # Create server entry if not exists
                if server_name not in self.servers:
                    self.servers[server_name] = MCPServer(
                        name=server_name,
                        uri=server_uri
                    )
                
                server = self.servers[server_name]
                server.connection_attempts += 1
                
                # For now, we'll use HTTP-based MCP communication
                # In a full implementation, this would use the actual MCP protocol
                if not self.session:
                    self.session = aiohttp.ClientSession()
                
                # Test connection with a simple ping
                async with self.session.get(f"{server_uri}/health") as response:
                    if response.status == 200:
                        server.status = "connected"
                        server.last_ping = datetime.now()
                        self.logger.info(f"Connected to MCP server: {server_name} at {server_uri}")
                        
                        # Discover tools and resources
                        await self._discover_server_capabilities(server_name)
                        return True
                    else:
                        raise aiohttp.ClientError(f"Server returned status {response.status}")
                        
            except Exception as e:
                server = self.servers.get(server_name)
                if server:
                    server.status = "error"
                self.logger.error(f"Failed to connect to MCP server {server_name}: {e}")
                return False
    
    async def disconnect_from_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        try:
            if server_name in self.servers:
                server = self.servers[server_name]
                server.status = "disconnected"
                
                # Close any active connections
                if server_name in self.connections:
                    connection = self.connections[server_name]
                    if hasattr(connection, 'close'):
                        await connection.close()
                    del self.connections[server_name]
                
                self.logger.info(f"Disconnected from MCP server: {server_name}")
                return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from server {server_name}: {e}")
            return False
    
    async def disconnect_all(self):
        """Disconnect from all servers"""
        for server_name in list(self.servers.keys()):
            await self.disconnect_from_server(server_name)
    
    async def _discover_server_capabilities(self, server_name: str):
        """Discover tools and resources available on a server"""
        try:
            server = self.servers[server_name]
            
            # Discover tools
            tools = await self.list_tools(server_name)
            server.tools = tools
            
            # Discover resources
            resources = await self.get_resources(server_name)
            server.resources = resources
            
            self.logger.info(f"Discovered {len(tools)} tools and {len(resources)} resources on {server_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to discover capabilities for {server_name}: {e}")
    
    async def list_tools(self, server_name: str) -> List[Dict]:
        """List available tools from a server"""
        try:
            server = self.servers.get(server_name)
            if not server or server.status != "connected":
                raise ConnectionError(f"Server {server_name} not connected")
            
            # Mock implementation - in real MCP, this would use the protocol
            async with self.session.get(f"{server.uri}/tools") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('tools', [])
                else:
                    raise aiohttp.ClientError(f"Failed to list tools: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error listing tools from {server_name}: {e}")
            return []
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict) -> Dict:
        """Execute a tool on the specified server"""
        try:
            server = self.servers.get(server_name)
            if not server or server.status != "connected":
                raise ConnectionError(f"Server {server_name} not connected")
            
            # Prepare the tool call request
            request_data = {
                'tool': tool_name,
                'arguments': arguments,
                'timestamp': datetime.now().isoformat()
            }
            
            # Make the tool call
            async with self.session.post(
                f"{server.uri}/tools/{tool_name}",
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.debug(f"Tool {tool_name} executed successfully on {server_name}")
                    return result
                else:
                    error_text = await response.text()
                    raise aiohttp.ClientError(f"Tool execution failed: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name} on {server_name}: {e}")
            return {
                'error': str(e),
                'tool': tool_name,
                'server': server_name
            }
    
    async def get_resources(self, server_name: str) -> List[Dict]:
        """Get available resources from a server"""
        try:
            server = self.servers.get(server_name)
            if not server or server.status != "connected":
                raise ConnectionError(f"Server {server_name} not connected")
            
            async with self.session.get(f"{server.uri}/resources") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('resources', [])
                else:
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error getting resources from {server_name}: {e}")
            return []
    
    async def read_resource(self, server_name: str, resource_uri: str) -> str:
        """Read content from a resource"""
        try:
            server = self.servers.get(server_name)
            if not server or server.status != "connected":
                raise ConnectionError(f"Server {server_name} not connected")
            
            async with self.session.get(
                f"{server.uri}/resources",
                params={'uri': resource_uri}
            ) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise aiohttp.ClientError(f"Failed to read resource: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error reading resource {resource_uri} from {server_name}: {e}")
            return ""
    
    async def update_resource(self, server_name: str, resource_uri: str, content: str) -> bool:
        """Update a resource on the server"""
        try:
            server = self.servers.get(server_name)
            if not server or server.status != "connected":
                raise ConnectionError(f"Server {server_name} not connected")
            
            request_data = {
                'uri': resource_uri,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            
            async with self.session.put(
                f"{server.uri}/resources",
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Error updating resource {resource_uri} on {server_name}: {e}")
            return False
    
    async def ping_server(self, server_name: str) -> bool:
        """Ping a server to check if it's alive"""
        try:
            server = self.servers.get(server_name)
            if not server:
                return False
            
            async with self.session.get(f"{server.uri}/health", timeout=5) as response:
                if response.status == 200:
                    server.last_ping = datetime.now()
                    if server.status == "error":
                        server.status = "connected"
                    return True
                else:
                    server.status = "error"
                    return False
                    
        except Exception as e:
            server = self.servers.get(server_name)
            if server:
                server.status = "error"
            self.logger.debug(f"Ping failed for {server_name}: {e}")
            return False
    
    def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get detailed status of a server"""
        server = self.servers.get(server_name)
        if not server:
            return {'status': 'not_found'}
        
        return {
            'name': server.name,
            'uri': server.uri,
            'status': server.status,
            'tools_count': len(server.tools),
            'resources_count': len(server.resources),
            'last_ping': server.last_ping.isoformat() if server.last_ping else None,
            'connection_attempts': server.connection_attempts
        }
    
    def list_servers(self) -> List[Dict[str, Any]]:
        """List all registered servers and their status"""
        return [self.get_server_status(name) for name in self.servers.keys()]
