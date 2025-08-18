"""
Multi-Agent Manager for Metis Agent.

Provides centralized management of multiple agent instances with isolated memory,
shared knowledge access, and comprehensive lifecycle management.
"""
import time
import threading
import uuid
from typing import Dict, Any, List, Optional, Union, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging
import json
import os
import weakref

logger = logging.getLogger(__name__)


@dataclass
class AgentMetadata:
    """Metadata about a managed agent instance."""
    agent_id: str
    profile_name: str
    name: str
    description: str
    created_at: float
    last_active: float
    status: str  # active, idle, suspended, error
    memory_path: str
    tool_count: int
    session_count: int
    total_queries: int
    performance_stats: Dict[str, Any]
    resource_usage: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @property
    def age_seconds(self) -> float:
        """Age of the agent in seconds."""
        return time.time() - self.created_at
    
    @property
    def idle_time_seconds(self) -> float:
        """Time since last activity in seconds."""
        return time.time() - self.last_active


@dataclass
class AgentStats:
    """Aggregated statistics for all managed agents."""
    total_agents: int = 0
    active_agents: int = 0
    idle_agents: int = 0
    suspended_agents: int = 0
    error_agents: int = 0
    total_memory_mb: float = 0.0
    total_queries: int = 0
    average_response_time_ms: float = 0.0
    uptime_hours: float = 0.0
    
    def update_from_agents(self, agents_metadata: Dict[str, AgentMetadata]):
        """Update stats from agent metadata."""
        self.total_agents = len(agents_metadata)
        self.active_agents = sum(1 for m in agents_metadata.values() if m.status == 'active')
        self.idle_agents = sum(1 for m in agents_metadata.values() if m.status == 'idle')
        self.suspended_agents = sum(1 for m in agents_metadata.values() if m.status == 'suspended')
        self.error_agents = sum(1 for m in agents_metadata.values() if m.status == 'error')
        
        if agents_metadata:
            self.total_queries = sum(m.total_queries for m in agents_metadata.values())
            
            # Calculate average response time from performance stats
            response_times = [
                m.performance_stats.get('average_response_time_ms', 0)
                for m in agents_metadata.values()
                if m.performance_stats.get('average_response_time_ms', 0) > 0
            ]
            if response_times:
                self.average_response_time_ms = sum(response_times) / len(response_times)
            
            # Calculate total memory usage
            self.total_memory_mb = sum(
                m.resource_usage.get('memory_mb', 0)
                for m in agents_metadata.values()
            )
            
            # Calculate uptime (oldest agent age)
            oldest_agent = min(agents_metadata.values(), key=lambda m: m.created_at)
            self.uptime_hours = oldest_agent.age_seconds / 3600


class AgentManager:
    """
    Central coordinator for multiple agent instances.
    
    Manages agent lifecycle, resource allocation, and inter-agent coordination
    while maintaining strict isolation between agent memory and contexts.
    """
    
    def __init__(self, 
                 max_agents: int = 10,
                 shared_knowledge_enabled: bool = True,
                 auto_cleanup_idle_hours: float = 24.0):
        """
        Initialize the agent manager.
        
        Args:
            max_agents: Maximum number of concurrent agents
            shared_knowledge_enabled: Whether to enable shared knowledge base
            auto_cleanup_idle_hours: Hours of inactivity before auto-cleanup
        """
        self.max_agents = max_agents
        self.shared_knowledge_enabled = shared_knowledge_enabled
        self.auto_cleanup_idle_hours = auto_cleanup_idle_hours
        
        # Core data structures
        self.agents: Dict[str, Any] = {}  # agent_id -> SingleAgent instance
        self.agent_metadata: Dict[str, AgentMetadata] = {}  # agent_id -> metadata
        self.agent_profiles: Dict[str, Dict[str, Any]] = {}  # agent_id -> profile config
        self.active_agent: Optional[str] = None  # Currently active agent for CLI
        
        # Resource management
        self.isolation_boundaries: Dict[str, Set[str]] = defaultdict(set)
        self.shared_resources: Dict[str, Any] = {}
        self.resource_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        
        # Performance tracking
        self.stats = AgentStats()
        self.creation_order: List[str] = []  # Track agent creation order
        self.manager_start_time = time.time()
        
        # Thread safety
        self._lock = threading.RLock()
        self._cleanup_thread: Optional[threading.Thread] = None
        self._shutdown = False
        
        # Registry persistence
        self.registry_path = "memory/agent_registry.json"
        self._load_agent_registry()
        
        # Shared knowledge base (placeholder for now)
        self.shared_knowledge = None
        if shared_knowledge_enabled:
            self._initialize_shared_knowledge()
        
        # Isolated memory manager
        from ..memory.isolated_memory import get_memory_manager
        self.memory_manager = get_memory_manager("memory/agents")
        
        # Start background cleanup thread
        self._start_cleanup_thread()
        
        logger.info(f"AgentManager initialized: max_agents={max_agents}, "
                   f"shared_knowledge={shared_knowledge_enabled}")
    
    def create_agent(self, 
                    profile_name: str,
                    agent_id: Optional[str] = None,
                    profile_config: Optional[Dict[str, Any]] = None,
                    **override_config) -> str:
        """
        Create a new agent instance from profile configuration.
        
        Args:
            profile_name: Name of the agent profile to use
            agent_id: Custom agent ID (auto-generated if None)
            profile_config: Direct profile configuration (bypasses profile loading)
            **override_config: Configuration overrides
            
        Returns:
            The created agent's ID
            
        Raises:
            ValueError: If max agents exceeded or profile invalid
            RuntimeError: If agent creation fails
        """
        with self._lock:
            # Check agent limits
            if len(self.agents) >= self.max_agents:
                raise ValueError(f"Maximum agents ({self.max_agents}) already created")
            
            # Generate agent ID if not provided
            if agent_id is None:
                agent_id = f"{profile_name}_{uuid.uuid4().hex[:8]}"
            
            # Check for duplicate agent ID
            if agent_id in self.agents:
                raise ValueError(f"Agent ID '{agent_id}' already exists")
            
            try:
                # Load or use provided profile configuration
                if profile_config is None:
                    profile_config = self._load_profile_config(profile_name)
                
                # Convert profile config to dictionary format
                profile_config = self._profile_to_dict(profile_config)
                
                # Apply any overrides
                if override_config:
                    profile_config = self._merge_config(profile_config, override_config)
                
                # Validate profile configuration
                self._validate_profile_config(profile_config)
                
                # Create isolated memory for the agent
                memory_config = {
                    'type': profile_config.get('memory_type', 'sqlite'),
                    'isolation_level': profile_config.get('memory_isolation_level', 'moderate'),
                    'allowed_shared_keys': profile_config.get('allowed_shared_keys', []),
                    'restricted_keys': profile_config.get('restricted_keys', []),
                    'max_memory_mb': profile_config.get('max_memory_mb', 100.0),
                    'cross_agent_policies': profile_config.get('cross_agent_policies', {})
                }
                
                # Create isolated memory store
                isolated_memory = self.memory_manager.create_agent_memory(agent_id, memory_config)
                
                # Create isolated configuration
                memory_path = isolated_memory.memory_path
                isolated_config = self._prepare_isolated_config(agent_id, profile_config, memory_path)
                
                # Import and create the agent instance
                from ..core.agent import SingleAgent
                
                # Create SingleAgent with only the parameters it accepts
                agent_instance = SingleAgent(
                    llm_provider=isolated_config.get('llm_provider'),
                    llm_model=isolated_config.get('llm_model'),
                    memory_path=memory_path,
                    tools=None  # Will be set based on enabled_tools
                )
                
                # Create agent metadata
                metadata = AgentMetadata(
                    agent_id=agent_id,
                    profile_name=profile_name,
                    name=profile_config.get('name', f"Agent {agent_id}"),
                    description=profile_config.get('description', f"Agent created from {profile_name} profile"),
                    created_at=time.time(),
                    last_active=time.time(),
                    status='active',
                    memory_path=memory_path,
                    tool_count=len(isolated_config.get('tools', [])),
                    session_count=0,
                    total_queries=0,
                    performance_stats={},
                    resource_usage={'memory_mb': 0.0, 'cpu_percent': 0.0}
                )
                
                # Register the agent
                self.agents[agent_id] = agent_instance
                self.agent_metadata[agent_id] = metadata
                self.agent_profiles[agent_id] = profile_config
                self.creation_order.append(agent_id)
                
                # Set as active agent if this is the first one
                if self.active_agent is None:
                    self.active_agent = agent_id
                
                # Update statistics
                self._update_stats()
                
                # Save registry to disk
                self._save_agent_registry()
                
                logger.info(f"Created agent '{agent_id}' from profile '{profile_name}'")
                return agent_id
                
            except Exception as e:
                logger.error(f"Failed to create agent '{agent_id}': {e}")
                # Cleanup any partially created resources
                self._cleanup_failed_agent_creation(agent_id)
                raise RuntimeError(f"Agent creation failed: {e}")
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """
        Get a specific agent instance with lazy loading.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            The agent instance or None if not found
        """
        with self._lock:
            # Check if agent is already loaded in memory
            agent = self.agents.get(agent_id)
            if agent and agent_id in self.agent_metadata:
                # Update last active time
                self.agent_metadata[agent_id].last_active = time.time()
                self.agent_metadata[agent_id].status = 'active'
                return agent
            
            # If not in memory but exists in metadata, lazy-load it
            if agent_id in self.agent_metadata and agent_id in self.agent_profiles:
                try:
                    logger.info(f"Lazy-loading agent: {agent_id}")
                    
                    # Get stored profile config
                    profile_config = self.agent_profiles[agent_id]
                    metadata = self.agent_metadata[agent_id]
                    
                    # Create isolated memory for the agent
                    memory_config = {
                        'type': profile_config.get('memory_type', 'sqlite'),
                        'isolation_level': profile_config.get('memory_isolation_level', 'moderate'),
                        'allowed_shared_keys': profile_config.get('allowed_shared_keys', []),
                        'restricted_keys': profile_config.get('restricted_keys', []),
                        'max_memory_mb': profile_config.get('max_memory_mb', 100.0),
                        'cross_agent_policies': profile_config.get('cross_agent_policies', {})
                    }
                    
                    # Create isolated memory store
                    isolated_memory = self.memory_manager.create_agent_memory(agent_id, memory_config)
                    
                    # Create isolated configuration
                    memory_path = isolated_memory.memory_path
                    isolated_config = self._prepare_isolated_config(agent_id, profile_config, memory_path)
                    
                    # Import and create the agent instance
                    from ..core.agent import SingleAgent
                    
                    # Create SingleAgent with only the parameters it accepts
                    agent_instance = SingleAgent(
                        llm_provider=isolated_config.get('llm_provider'),
                        llm_model=isolated_config.get('llm_model'),
                        memory_path=memory_path,
                        tools=None  # Will be set based on enabled_tools
                    )
                    
                    # Store in memory
                    self.agents[agent_id] = agent_instance
                    
                    # Update last active time
                    self.agent_metadata[agent_id].last_active = time.time()
                    self.agent_metadata[agent_id].status = 'active'
                    
                    logger.info(f"Successfully lazy-loaded agent: {agent_id}")
                    return agent_instance
                    
                except Exception as e:
                    logger.error(f"Failed to lazy-load agent {agent_id}: {e}")
                    return None
            
            return None
    
    def list_agents(self) -> List[str]:
        """
        List all active agent IDs.
        
        Returns:
            List of active agent IDs
        """
        with self._lock:
            # Return agents from metadata (includes persisted agents)
            # This allows listing agents even if instances aren't loaded yet
            return list(self.agent_metadata.keys())
    
    def list_agents_detailed(self, include_metadata: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        List all active agents with their metadata.
        
        Args:
            include_metadata: Whether to include detailed metadata
            
        Returns:
            Dictionary of agent_id -> agent_info
        """
        with self._lock:
            result = {}
            for agent_id in self.agents:
                metadata = self.agent_metadata.get(agent_id)
                if metadata:
                    agent_info = {
                        'agent_id': agent_id,
                        'name': metadata.name,
                        'profile_name': metadata.profile_name,
                        'status': metadata.status,
                        'created_at': metadata.created_at,
                        'last_active': metadata.last_active
                    }
                    
                    if include_metadata:
                        agent_info.update({
                            'description': metadata.description,
                            'tool_count': metadata.tool_count,
                            'session_count': metadata.session_count,
                            'total_queries': metadata.total_queries,
                            'age_seconds': metadata.age_seconds,
                            'idle_time_seconds': metadata.idle_time_seconds,
                            'memory_path': metadata.memory_path,
                            'performance_stats': metadata.performance_stats,
                            'resource_usage': metadata.resource_usage
                        })
                    
                    result[agent_id] = agent_info
            
            return result
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get basic agent information (CLI compatibility method).
        
        Args:
            agent_id: The agent identifier
            
        Returns:
            Agent information or None if not found
        """
        with self._lock:
            metadata = self.agent_metadata.get(agent_id)
            if metadata:
                return metadata.to_dict()
        return None
    
    def switch_active_agent(self, agent_id: str) -> bool:
        """
        Switch the CLI context to a different agent.
        
        Args:
            agent_id: The agent to make active
            
        Returns:
            True if switch was successful
        """
        with self._lock:
            if agent_id not in self.agents:
                logger.error(f"Cannot switch to non-existent agent: {agent_id}")
                return False
            
            # Update metadata for old active agent
            if self.active_agent and self.active_agent in self.agent_metadata:
                self.agent_metadata[self.active_agent].status = 'idle'
            
            # Switch to new active agent
            self.active_agent = agent_id
            self.agent_metadata[agent_id].last_active = time.time()
            self.agent_metadata[agent_id].status = 'active'
            
            logger.info(f"Switched active agent to: {agent_id}")
            return True
    
    def get_active_agent(self) -> Optional[Any]:
        """
        Get the currently active agent instance.
        
        Returns:
            The active agent instance or None
        """
        if self.active_agent:
            return self.get_agent(self.active_agent)
        return None
    
    def get_active_agent_id(self) -> Optional[str]:
        """
        Get the currently active agent ID.
        
        Returns:
            The active agent ID or None
        """
        return self.active_agent
    
    def stop_agent(self, agent_id: str, force: bool = False) -> bool:
        """
        Stop an agent (alias for remove_agent for CLI compatibility).
        
        Args:
            agent_id: The agent to stop
            force: Force stop even if agent is active
            
        Returns:
            True if stop was successful
        """
        return self.remove_agent(agent_id, force)
    
    def remove_agent(self, agent_id: str, force: bool = False) -> bool:
        """
        Remove an agent and cleanup its resources.
        
        Args:
            agent_id: The agent to remove
            force: Force removal even if agent is active
            
        Returns:
            True if removal was successful
        """
        with self._lock:
            if agent_id not in self.agents:
                logger.warning(f"Attempted to remove non-existent agent: {agent_id}")
                return False
            
            # Check if agent is active and force is not set
            if agent_id == self.active_agent and not force:
                logger.error(f"Cannot remove active agent '{agent_id}' without force=True")
                return False
            
            try:
                # Get agent instance for cleanup
                agent = self.agents[agent_id]
                metadata = self.agent_metadata.get(agent_id)
                
                # Cleanup agent resources
                if hasattr(agent, 'cleanup'):
                    agent.cleanup()
                
                # Remove from data structures
                del self.agents[agent_id]
                if agent_id in self.agent_metadata:
                    del self.agent_metadata[agent_id]
                if agent_id in self.agent_profiles:
                    del self.agent_profiles[agent_id]
                if agent_id in self.creation_order:
                    self.creation_order.remove(agent_id)
                
                # Cleanup isolation boundaries
                if agent_id in self.isolation_boundaries:
                    del self.isolation_boundaries[agent_id]
                
                # Update active agent if necessary
                if self.active_agent == agent_id:
                    # Switch to most recently created agent or None
                    self.active_agent = self.creation_order[-1] if self.creation_order else None
                    if self.active_agent:
                        self.agent_metadata[self.active_agent].status = 'active'
                
                # Cleanup isolated memory
                self.memory_manager.cleanup_agent_memory(agent_id)
                
                # Update statistics
                self._update_stats()
                
                # Save registry to disk
                self._save_agent_registry()
                
                logger.info(f"Removed agent: {agent_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove agent '{agent_id}': {e}")
                return False
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive status information for an agent.
        
        Args:
            agent_id: The agent to get status for
            
        Returns:
            Detailed status information or None if agent not found
        """
        with self._lock:
            if agent_id not in self.agents:
                return None
            
            agent = self.agents[agent_id]
            metadata = self.agent_metadata[agent_id]
            profile = self.agent_profiles[agent_id]
            
            # Get current resource usage
            resource_usage = self._get_agent_resource_usage(agent_id)
            
            # Get agent-specific performance stats
            performance_stats = self._get_agent_performance_stats(agent_id)
            
            return {
                'agent_id': agent_id,
                'metadata': metadata.to_dict(),
                'profile': profile,
                'resource_usage': resource_usage,
                'performance_stats': performance_stats,
                'is_active': agent_id == self.active_agent,
                'health_status': self._check_agent_health(agent_id),
                'isolation_info': {
                    'memory_isolated': True,
                    'shared_knowledge_access': self.shared_knowledge_enabled,
                    'resource_boundaries': list(self.isolation_boundaries.get(agent_id, set()))
                }
            }
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the agent manager and all agents.
        
        Returns:
            Detailed manager and agent statistics
        """
        with self._lock:
            # Update stats from current agents
            self.stats.update_from_agents(self.agent_metadata)
            
            return {
                'manager_info': {
                    'max_agents': self.max_agents,
                    'shared_knowledge_enabled': self.shared_knowledge_enabled,
                    'auto_cleanup_idle_hours': self.auto_cleanup_idle_hours,
                    'manager_uptime_hours': (time.time() - self.manager_start_time) / 3600,
                    'active_agent_id': self.active_agent
                },
                'agent_stats': asdict(self.stats),
                'agents_overview': self.list_agents_detailed(include_metadata=False),
                'resource_usage': {
                    'total_memory_mb': self.stats.total_memory_mb,
                    'agent_count': self.stats.total_agents,
                    'shared_resources': list(self.shared_resources.keys())
                }
            }
    
    def cleanup_idle_agents(self, max_idle_hours: Optional[float] = None) -> List[str]:
        """
        Cleanup agents that have been idle for too long.
        
        Args:
            max_idle_hours: Maximum idle time before cleanup (uses default if None)
            
        Returns:
            List of agent IDs that were cleaned up
        """
        if max_idle_hours is None:
            max_idle_hours = self.auto_cleanup_idle_hours
        
        max_idle_seconds = max_idle_hours * 3600
        current_time = time.time()
        cleaned_up = []
        
        with self._lock:
            for agent_id, metadata in list(self.agent_metadata.items()):
                idle_time = current_time - metadata.last_active
                
                # Don't cleanup active agent or recently created agents
                if (agent_id != self.active_agent and 
                    idle_time > max_idle_seconds and 
                    metadata.status in ['idle', 'suspended']):
                    
                    logger.info(f"Cleaning up idle agent '{agent_id}' (idle for {idle_time/3600:.1f} hours)")
                    if self.remove_agent(agent_id, force=True):
                        cleaned_up.append(agent_id)
        
        return cleaned_up
    
    def share_knowledge_between_agents(self, 
                                     from_agent_id: str, 
                                     to_agent_id: str, 
                                     knowledge_key: str,
                                     knowledge_value: Any,
                                     metadata: Dict[str, Any] = None) -> bool:
        """
        Share knowledge between two agents.
        
        Args:
            from_agent_id: Source agent ID
            to_agent_id: Target agent ID
            knowledge_key: Key for the shared knowledge
            knowledge_value: Value to share
            metadata: Optional metadata
            
        Returns:
            True if sharing was successful
        """
        if from_agent_id not in self.agents or to_agent_id not in self.agents:
            logger.error(f"One or both agents not found: {from_agent_id}, {to_agent_id}")
            return False
        
        return self.memory_manager.share_knowledge(
            from_agent_id, to_agent_id, knowledge_key, knowledge_value, metadata
        )
    
    def get_agent_memory_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get memory statistics for a specific agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Memory statistics or None if agent not found
        """
        if agent_id not in self.agents:
            return None
        
        memory_stats = self.memory_manager.get_memory_stats(agent_id)
        return asdict(memory_stats) if memory_stats else None
    
    def get_all_memory_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get memory statistics for all agents."""
        all_stats = self.memory_manager.get_all_memory_stats()
        return {
            agent_id: asdict(stats) if stats else None
            for agent_id, stats in all_stats.items()
        }
    
    def set_cross_agent_policy(self, 
                             from_agent_id: str, 
                             to_agent_id: str, 
                             policy: str) -> bool:
        """
        Set cross-agent communication policy.
        
        Args:
            from_agent_id: Source agent ID
            to_agent_id: Target agent ID
            policy: Policy ('deny', 'read', 'write')
            
        Returns:
            True if policy was set successfully
        """
        if from_agent_id not in self.agents or to_agent_id not in self.agents:
            logger.error(f"One or both agents not found: {from_agent_id}, {to_agent_id}")
            return False
        
        try:
            self.memory_manager.set_cross_agent_policy(from_agent_id, to_agent_id, policy)
            return True
        except Exception as e:
            logger.error(f"Failed to set cross-agent policy: {e}")
            return False
    
    def get_isolation_report(self) -> Dict[str, Any]:
        """Get comprehensive memory isolation and security report."""
        return self.memory_manager.get_isolation_report()
    
    def add_shared_knowledge(self,
                           title: str,
                           content: Any,
                           category: str,
                           source_agent_id: str,
                           tags: List[str] = None,
                           access_level: str = 'public',
                           allowed_agents: Set[str] = None,
                           metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Add knowledge to the shared knowledge base.
        
        Args:
            title: Knowledge title
            content: Knowledge content
            category: Knowledge category
            source_agent_id: Agent adding the knowledge
            tags: Optional tags
            access_level: Access level (public, restricted, private)
            allowed_agents: Agents allowed to access (for restricted/private)
            metadata: Optional metadata
            
        Returns:
            Knowledge ID if successful, None otherwise
        """
        if source_agent_id not in self.agents:
            logger.error(f"Agent {source_agent_id} not found")
            return None
        
        if not self.shared_knowledge:
            logger.error("Shared knowledge base not initialized")
            return None
        
        try:
            knowledge_id = self.shared_knowledge.add_knowledge(
                title=title,
                content=content,
                category=category,
                source_agent=source_agent_id,
                tags=tags,
                access_level=access_level,
                allowed_agents=allowed_agents,
                metadata=metadata
            )
            
            logger.info(f"Agent {source_agent_id} added knowledge: {title} (ID: {knowledge_id})")
            return knowledge_id
            
        except Exception as e:
            logger.error(f"Failed to add shared knowledge: {e}")
            return None
    
    def query_shared_knowledge(self,
                             query: str = None,
                             agent_id: str = None,
                             category: str = None,
                             tags: List[str] = None,
                             limit: int = 50) -> List[Dict[str, Any]]:
        """
        Query shared knowledge base.
        
        Args:
            query: Search query
            agent_id: Agent making the request
            category: Filter by category
            tags: Filter by tags
            limit: Maximum results
            
        Returns:
            List of knowledge entries
        """
        if agent_id and agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return []
        
        if not self.shared_knowledge:
            logger.error("Shared knowledge base not initialized")
            return []
        
        try:
            return self.shared_knowledge.query_knowledge(
                query=query,
                agent_id=agent_id,
                category=category,
                tags=tags,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to query shared knowledge: {e}")
            return []
    
    def get_shared_knowledge_entry(self, knowledge_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific shared knowledge entry.
        
        Args:
            knowledge_id: Knowledge entry ID
            agent_id: Agent requesting access
            
        Returns:
            Knowledge entry or None
        """
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return None
        
        if not self.shared_knowledge:
            logger.error("Shared knowledge base not initialized")
            return None
        
        try:
            return self.shared_knowledge.get_knowledge(knowledge_id, agent_id)
        except Exception as e:
            logger.error(f"Failed to get shared knowledge: {e}")
            return None
    
    def update_shared_knowledge(self,
                              knowledge_id: str,
                              agent_id: str,
                              title: str = None,
                              content: Any = None,
                              tags: List[str] = None,
                              metadata: Dict[str, Any] = None,
                              change_summary: str = None) -> bool:
        """
        Update shared knowledge entry.
        
        Args:
            knowledge_id: Knowledge entry ID
            agent_id: Agent making the update
            title: New title
            content: New content
            tags: New tags
            metadata: New metadata
            change_summary: Summary of changes
            
        Returns:
            True if successful
        """
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        if not self.shared_knowledge:
            logger.error("Shared knowledge base not initialized")
            return False
        
        try:
            return self.shared_knowledge.update_knowledge(
                knowledge_id=knowledge_id,
                title=title,
                content=content,
                modified_by=agent_id,
                tags=tags,
                metadata=metadata,
                change_summary=change_summary
            )
        except Exception as e:
            logger.error(f"Failed to update shared knowledge: {e}")
            return False
    
    def get_knowledge_graph(self, agent_id: str, category: str = None) -> Dict[str, Any]:
        """
        Get knowledge graph for agent.
        
        Args:
            agent_id: Agent requesting the graph
            category: Optional category filter
            
        Returns:
            Knowledge graph structure
        """
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return {}
        
        if not self.shared_knowledge:
            logger.error("Shared knowledge base not initialized")
            return {}
        
        try:
            return self.shared_knowledge.get_knowledge_graph(agent_id, category)
        except Exception as e:
            logger.error(f"Failed to get knowledge graph: {e}")
            return {}
    
    def set_knowledge_permissions(self,
                                agent_id: str,
                                target_agent_id: str,
                                category: str,
                                permissions: Set[str]) -> bool:
        """
        Set knowledge permissions for an agent.
        
        Args:
            agent_id: Agent setting permissions (must have admin rights)
            target_agent_id: Agent receiving permissions
            category: Category to set permissions for
            permissions: Set of permissions ('read', 'write', 'admin')
            
        Returns:
            True if successful
        """
        if agent_id not in self.agents or target_agent_id not in self.agents:
            logger.error(f"One or both agents not found: {agent_id}, {target_agent_id}")
            return False
        
        if not self.shared_knowledge:
            logger.error("Shared knowledge base not initialized")
            return False
        
        try:
            self.shared_knowledge.set_agent_permissions(
                agent_id=target_agent_id,
                category=category,
                permissions=permissions,
                granted_by=agent_id
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set knowledge permissions: {e}")
            return False
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get shared knowledge base statistics."""
        if not self.shared_knowledge:
            return {}
        
        try:
            return self.shared_knowledge.get_statistics()
        except Exception as e:
            logger.error(f"Failed to get knowledge statistics: {e}")
            return {}
    
    def shutdown(self):
        """Shutdown the agent manager and cleanup all resources."""
        logger.info("Shutting down AgentManager...")
        
        with self._lock:
            self._shutdown = True
            
            # Stop cleanup thread
            if self._cleanup_thread and self._cleanup_thread.is_alive():
                self._cleanup_thread.join(timeout=5.0)
            
            # Cleanup all agents
            agent_ids = list(self.agents.keys())
            for agent_id in agent_ids:
                self.remove_agent(agent_id, force=True)
            
            # Cleanup shared resources
            self.shared_resources.clear()
            self.isolation_boundaries.clear()
            
            # Shutdown memory manager
            if self.memory_manager:
                self.memory_manager.shutdown()
            
            # Cleanup shared knowledge
            if self.shared_knowledge:
                self.shared_knowledge.cleanup()
            
        logger.info("AgentManager shutdown complete")
    
    # Private methods
    
    def _load_profile_config(self, profile_name: str) -> Dict[str, Any]:
        """Load profile configuration from YAML files or defaults."""
        try:
            # Import profile manager
            from ..config.agent_profiles import get_profile_manager
            
            # Get profile manager and load profile
            profile_manager = get_profile_manager("profiles")
            profile = profile_manager.load_profile(profile_name)
            
            # Convert to agent configuration
            config = profile.to_agent_config()
            
            logger.info(f"Loaded profile configuration for: {profile_name}")
            return config
            
        except Exception as e:
            logger.warning(f"Failed to load profile '{profile_name}': {e}")
            logger.info(f"Using fallback configuration for: {profile_name}")
            
            # Fallback to basic configuration
            return {
                'name': f"Agent {profile_name}",
                'description': f"Agent created from {profile_name} profile (fallback)",
                'llm_provider': 'groq',
                'llm_model': 'llama-3.1-70b-versatile',
                'llm_temperature': 0.1,
                'llm_max_tokens': 4000,
                'enabled_tools': ['CalculatorTool', 'EnhancedSearchTool'],
                'memory_type': 'sqlite',
                'max_context_tokens': 4000,
                'memory_retention_days': 30,
                'cache_enabled': True,
                'memory_monitoring': True,
                'shared_knowledge_enabled': True,
                'custom_config': {}
            }
    
    def _profile_to_dict(self, profile_config) -> Dict[str, Any]:
        """Convert AgentProfile object to dictionary format."""
        from ..config.agent_profiles import AgentProfile
        
        if isinstance(profile_config, AgentProfile):
            # Convert AgentProfile to dictionary
            config_dict = {
                'name': profile_config.name,
                'description': profile_config.description,
                'agent_id': profile_config.agent_id,
                'version': getattr(profile_config, 'version', '1.0'),
                'custom_config': profile_config.custom_config
            }
            
            # Convert LLM config
            if profile_config.llm_config:
                config_dict['llm_config'] = {
                    'provider': profile_config.llm_config.provider,
                    'model': profile_config.llm_config.model,
                    'temperature': profile_config.llm_config.temperature,
                    'max_tokens': profile_config.llm_config.max_tokens,
                    'timeout': profile_config.llm_config.timeout,
                    'api_key': profile_config.llm_config.api_key,
                    'base_url': profile_config.llm_config.base_url,
                    'custom_config': profile_config.llm_config.custom_config
                }
            
            # Convert tools config
            if profile_config.tools:
                config_dict['tools'] = {
                    'enabled': profile_config.tools.enabled,
                    'disabled': profile_config.tools.disabled,
                    'config': profile_config.tools.config
                }
            
            # Convert memory config  
            if profile_config.memory_config:
                config_dict['memory_config'] = {
                    'type': profile_config.memory_config.type,
                    'path': profile_config.memory_config.path,
                    'max_context_tokens': profile_config.memory_config.max_context_tokens,
                    'retention_days': profile_config.memory_config.retention_days,
                    'isolation': profile_config.memory_config.isolation,
                    'cache_size': profile_config.memory_config.cache_size,
                    'specialized_memory': profile_config.memory_config.specialized_memory,
                    'backup_enabled': profile_config.memory_config.backup_enabled
                }
            
            # Convert performance config
            if profile_config.performance:
                config_dict['performance'] = {
                    'cache_enabled': profile_config.performance.cache_enabled,
                    'cache_ttl': profile_config.performance.cache_ttl,
                    'memory_monitoring': profile_config.performance.memory_monitoring,
                    'max_parallel_tools': profile_config.performance.max_parallel_tools,
                    'timeout_seconds': profile_config.performance.timeout_seconds,
                    'retry_attempts': profile_config.performance.retry_attempts,
                    'lazy_loading': profile_config.performance.lazy_loading
                }
            
            # Convert permissions config
            if profile_config.permissions:
                config_dict['permissions'] = {
                    'file_access': profile_config.permissions.file_access,
                    'network_access': profile_config.permissions.network_access,
                    'system_commands': profile_config.permissions.system_commands,
                    'restricted_paths': profile_config.permissions.restricted_paths,
                    'max_file_size_mb': profile_config.permissions.max_file_size_mb
                }
            
            # Convert shared resources config
            if profile_config.shared_resources:
                config_dict['shared_resources'] = {
                    'knowledge_base': profile_config.shared_resources.knowledge_base,
                    'tool_registry': profile_config.shared_resources.tool_registry,
                    'cache_layer': profile_config.shared_resources.cache_layer,
                    'memory_sharing': profile_config.shared_resources.memory_sharing,
                    'config_sharing': profile_config.shared_resources.config_sharing
                }
            
            return config_dict
        
        # If it's already a dictionary, return as-is
        return profile_config
    
    def _merge_config(self, base_config: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configuration overrides with base configuration."""
        # Ensure base_config is a dictionary
        merged = self._profile_to_dict(base_config)
        
        def deep_merge(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
        
        deep_merge(merged, overrides)
        return merged
    
    def _validate_profile_config(self, config: Dict[str, Any]) -> None:
        """Validate profile configuration."""
        required_keys = ['name']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Validate LLM configuration (nested structure)
        llm_config = config.get('llm_config', {})
        if not llm_config:
            raise ValueError("LLM configuration is required")
        if not llm_config.get('provider'):
            raise ValueError("LLM provider is required")
        if not llm_config.get('model'):
            raise ValueError("LLM model is required")
        
        # Validate tools configuration
        tools_config = config.get('tools', {})
        if tools_config and not tools_config.get('enabled'):
            raise ValueError("At least one tool must be enabled")
    
    def _create_isolated_memory_path(self, agent_id: str) -> str:
        """Create isolated memory path for agent."""
        memory_dir = "memory/agents"
        os.makedirs(memory_dir, exist_ok=True)
        return os.path.join(memory_dir, f"{agent_id}.db")
    
    def _prepare_isolated_config(self, agent_id: str, profile_config: Dict[str, Any], memory_path: str) -> Dict[str, Any]:
        """Prepare isolated configuration for agent creation."""
        config = profile_config.copy()
        
        # Set isolated memory path
        if 'memory_config' in config:
            config['memory_config']['path'] = memory_path
        
        # Add isolation metadata
        config['agent_id'] = agent_id
        config['isolation_enabled'] = True
        
        return config
    
    def _initialize_shared_knowledge(self):
        """Initialize shared knowledge base."""
        from ..knowledge.shared_knowledge import get_shared_knowledge
        
        self.shared_knowledge = get_shared_knowledge("knowledge/shared_knowledge.db")
        
        # Set up default admin permissions for the first agent
        # This will be expanded as agents are created
        logger.info("Shared knowledge base initialized")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_worker():
            while not self._shutdown:
                try:
                    time.sleep(3600)  # Check every hour
                    if not self._shutdown:
                        self.cleanup_idle_agents()
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        logger.debug("Cleanup thread started")
    
    def _update_stats(self):
        """Update manager statistics."""
        with self._lock:
            self.stats.update_from_agents(self.agent_metadata)
    
    def _cleanup_failed_agent_creation(self, agent_id: str):
        """Cleanup resources from failed agent creation."""
        # Remove from any data structures that might have been updated
        self.agents.pop(agent_id, None)
        self.agent_metadata.pop(agent_id, None)
        self.agent_profiles.pop(agent_id, None)
        if agent_id in self.creation_order:
            self.creation_order.remove(agent_id)
    
    def _cleanup_agent_memory_path(self, memory_path: str):
        """Cleanup agent memory database file."""
        try:
            if os.path.exists(memory_path):
                os.remove(memory_path)
                logger.debug(f"Cleaned up memory file: {memory_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup memory file {memory_path}: {e}")
    
    def _get_agent_resource_usage(self, agent_id: str) -> Dict[str, Any]:
        """Get current resource usage for an agent."""
        # Placeholder - will be enhanced with actual monitoring
        return {
            'memory_mb': 50.0,
            'cpu_percent': 5.0,
            'disk_usage_mb': 10.0,
            'network_requests': 0
        }
    
    def _get_agent_performance_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get performance statistics for an agent."""
        # Placeholder - will be enhanced with actual metrics
        return {
            'average_response_time_ms': 150.0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hit_rate': 0.0
        }
    
    def _check_agent_health(self, agent_id: str) -> str:
        """Check agent health status."""
        # Placeholder health check
        try:
            agent = self.agents.get(agent_id)
            metadata = self.agent_metadata.get(agent_id)
            
            if not agent or not metadata:
                return 'error'
            
            if metadata.status == 'error':
                return 'error'
            elif metadata.idle_time_seconds > 3600:  # 1 hour
                return 'idle'
            else:
                return 'healthy'
                
        except Exception:
            return 'error'
    
    def _save_agent_registry(self):
        """Save agent registry to disk for persistence across CLI commands."""
        try:
            os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
            
            registry_data = {
                'agents': {},
                'creation_order': self.creation_order,
                'active_agent': self.active_agent,
                'manager_start_time': self.manager_start_time
            }
            
            # Save agent metadata (but not the actual agent instances)
            for agent_id, metadata in self.agent_metadata.items():
                registry_data['agents'][agent_id] = {
                    'metadata': metadata.to_dict(),
                    'profile': self.agent_profiles.get(agent_id, {}),
                    'memory_path': metadata.memory_path
                }
            
            with open(self.registry_path, 'w') as f:
                json.dump(registry_data, f, indent=2, default=str)
                
            logger.debug(f"Agent registry saved to {self.registry_path}")
            
        except Exception as e:
            logger.error(f"Failed to save agent registry: {e}")
    
    def _load_agent_registry(self):
        """Load agent registry from disk to restore agents across CLI commands."""
        try:
            if not os.path.exists(self.registry_path):
                logger.debug("No agent registry found, starting fresh")
                return
            
            with open(self.registry_path, 'r') as f:
                registry_data = json.load(f)
            
            # Restore metadata and profiles
            for agent_id, agent_data in registry_data.get('agents', {}).items():
                metadata_dict = agent_data.get('metadata', {})
                profile = agent_data.get('profile', {})
                
                # Recreate metadata object
                metadata = AgentMetadata(
                    agent_id=metadata_dict.get('agent_id', agent_id),
                    profile_name=metadata_dict.get('profile_name', 'unknown'),
                    name=metadata_dict.get('name', f'Agent {agent_id}'),
                    description=metadata_dict.get('description', ''),
                    created_at=metadata_dict.get('created_at', time.time()),
                    last_active=metadata_dict.get('last_active', time.time()),
                    status=metadata_dict.get('status', 'idle'),
                    memory_path=metadata_dict.get('memory_path', ''),
                    tool_count=metadata_dict.get('tool_count', 0),
                    session_count=metadata_dict.get('session_count', 0),
                    total_queries=metadata_dict.get('total_queries', 0),
                    performance_stats=metadata_dict.get('performance_stats', {}),
                    resource_usage=metadata_dict.get('resource_usage', {})
                )
                
                # Restore metadata and profile
                self.agent_metadata[agent_id] = metadata
                self.agent_profiles[agent_id] = profile
                
                # Note: We don't restore the actual agent instances here
                # They will be recreated lazily when needed
            
            # Restore other state
            self.creation_order = registry_data.get('creation_order', [])
            self.active_agent = registry_data.get('active_agent')
            if 'manager_start_time' in registry_data:
                self.manager_start_time = registry_data['manager_start_time']
            
            logger.debug(f"Loaded {len(self.agent_metadata)} agents from registry")
            
        except Exception as e:
            logger.error(f"Failed to load agent registry: {e}")


# Global agent manager instance
_agent_manager: Optional[AgentManager] = None


def get_agent_manager() -> AgentManager:
    """Get or create global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager


def configure_agent_manager(max_agents: int = 10,
                          shared_knowledge_enabled: bool = True,
                          auto_cleanup_idle_hours: float = 24.0) -> AgentManager:
    """Configure global agent manager with custom settings."""
    global _agent_manager
    if _agent_manager:
        _agent_manager.shutdown()
    
    _agent_manager = AgentManager(max_agents, shared_knowledge_enabled, auto_cleanup_idle_hours)
    return _agent_manager