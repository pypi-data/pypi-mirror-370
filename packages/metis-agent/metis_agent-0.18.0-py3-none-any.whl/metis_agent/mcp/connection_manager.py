"""
MCP Connection Manager
Handles health monitoring, reconnection, and failover for MCP servers
"""

import asyncio
import logging
from typing import Dict, List, Callable, Optional
from datetime import datetime, timedelta
from .client import MCPClient, MCPServer

class MCPConnectionManager:
    """Manages MCP server connections with health monitoring and failover"""
    
    def __init__(self, client: MCPClient):
        self.client = client
        self.health_check_interval = 30  # seconds
        self.retry_attempts = 3
        self.retry_delay = 5  # seconds
        self.logger = logging.getLogger(__name__)
        self._health_monitor_task = None
        self._running = False
        self._callbacks: Dict[str, List[Callable]] = {
            'server_connected': [],
            'server_disconnected': [],
            'server_error': [],
            'server_recovered': []
        }
    
    def add_callback(self, event: str, callback: Callable):
        """Add a callback for server events"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    async def _notify_callbacks(self, event: str, server_name: str, **kwargs):
        """Notify all callbacks for an event"""
        for callback in self._callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(server_name, **kwargs)
                else:
                    callback(server_name, **kwargs)
            except Exception as e:
                self.logger.error(f"Error in callback for {event}: {e}")
    
    async def start_health_monitoring(self):
        """Start background health monitoring"""
        if self._running:
            return
        
        self._running = True
        self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
        self.logger.info("Started MCP health monitoring")
    
    async def stop_health_monitoring(self):
        """Stop background health monitoring"""
        self._running = False
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped MCP health monitoring")
    
    async def _health_monitor_loop(self):
        """Main health monitoring loop"""
        while self._running:
            try:
                await self._check_all_servers()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _check_all_servers(self):
        """Check health of all registered servers"""
        for server_name in list(self.client.servers.keys()):
            await self._check_server_health(server_name)
    
    async def _check_server_health(self, server_name: str):
        """Check health of a specific server"""
        try:
            server = self.client.servers.get(server_name)
            if not server:
                return
            
            previous_status = server.status
            is_healthy = await self.client.ping_server(server_name)
            
            # Handle status changes
            if is_healthy and previous_status in ['error', 'disconnected']:
                await self._notify_callbacks('server_recovered', server_name)
                self.logger.info(f"Server {server_name} recovered")
            elif not is_healthy and previous_status == 'connected':
                await self._notify_callbacks('server_error', server_name)
                self.logger.warning(f"Server {server_name} became unhealthy")
                
                # Attempt reconnection
                await self._attempt_reconnection(server_name)
        
        except Exception as e:
            self.logger.error(f"Error checking health of {server_name}: {e}")
    
    async def _attempt_reconnection(self, server_name: str):
        """Attempt to reconnect to a failed server"""
        server = self.client.servers.get(server_name)
        if not server:
            return
        
        for attempt in range(self.retry_attempts):
            try:
                self.logger.info(f"Reconnection attempt {attempt + 1}/{self.retry_attempts} for {server_name}")
                
                # Wait before retry
                if attempt > 0:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                
                # Attempt reconnection
                success = await self.client.connect_to_server(server.uri, server_name)
                
                if success:
                    await self._notify_callbacks('server_connected', server_name)
                    self.logger.info(f"Successfully reconnected to {server_name}")
                    return True
                    
            except Exception as e:
                self.logger.error(f"Reconnection attempt {attempt + 1} failed for {server_name}: {e}")
        
        # All reconnection attempts failed
        self.logger.error(f"Failed to reconnect to {server_name} after {self.retry_attempts} attempts")
        await self._notify_callbacks('server_disconnected', server_name)
        return False
    
    async def ensure_server_connection(self, server_name: str) -> bool:
        """Ensure a server is connected, attempting reconnection if needed"""
        server = self.client.servers.get(server_name)
        if not server:
            self.logger.error(f"Server {server_name} not registered")
            return False
        
        # Check if already connected and healthy
        if server.status == 'connected':
            is_healthy = await self.client.ping_server(server_name)
            if is_healthy:
                return True
        
        # Attempt connection/reconnection
        return await self._attempt_reconnection(server_name)
    
    async def register_server(self, server_name: str, server_uri: str, auto_connect: bool = True) -> bool:
        """Register a new server and optionally connect to it"""
        try:
            if auto_connect:
                success = await self.client.connect_to_server(server_uri, server_name)
                if success:
                    await self._notify_callbacks('server_connected', server_name)
                return success
            else:
                # Just register without connecting
                self.client.servers[server_name] = MCPServer(
                    name=server_name,
                    uri=server_uri,
                    status='registered'
                )
                return True
                
        except Exception as e:
            self.logger.error(f"Error registering server {server_name}: {e}")
            return False
    
    async def unregister_server(self, server_name: str) -> bool:
        """Unregister and disconnect from a server"""
        try:
            # Disconnect if connected
            await self.client.disconnect_from_server(server_name)
            
            # Remove from registry
            if server_name in self.client.servers:
                del self.client.servers[server_name]
            
            await self._notify_callbacks('server_disconnected', server_name)
            self.logger.info(f"Unregistered server {server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unregistering server {server_name}: {e}")
            return False
    
    def get_healthy_servers(self) -> List[str]:
        """Get list of currently healthy servers"""
        healthy = []
        for name, server in self.client.servers.items():
            if server.status == 'connected':
                healthy.append(name)
        return healthy
    
    def get_server_stats(self) -> Dict[str, Dict]:
        """Get comprehensive stats for all servers"""
        stats = {}
        for name, server in self.client.servers.items():
            stats[name] = {
                'status': server.status,
                'uri': server.uri,
                'tools_count': len(server.tools),
                'resources_count': len(server.resources),
                'connection_attempts': server.connection_attempts,
                'last_ping': server.last_ping.isoformat() if server.last_ping else None,
                'uptime_check': self._calculate_uptime(server)
            }
        return stats
    
    def _calculate_uptime(self, server: MCPServer) -> Optional[str]:
        """Calculate server uptime based on last ping"""
        if not server.last_ping or server.status != 'connected':
            return None
        
        uptime = datetime.now() - server.last_ping
        if uptime.total_seconds() < 60:
            return f"{int(uptime.total_seconds())}s"
        elif uptime.total_seconds() < 3600:
            return f"{int(uptime.total_seconds() / 60)}m"
        else:
            return f"{int(uptime.total_seconds() / 3600)}h"
    
    async def graceful_shutdown(self):
        """Gracefully shutdown all connections"""
        self.logger.info("Starting graceful MCP shutdown...")
        
        # Stop health monitoring
        await self.stop_health_monitoring()
        
        # Disconnect from all servers
        await self.client.disconnect_all()
        
        self.logger.info("MCP graceful shutdown complete")
