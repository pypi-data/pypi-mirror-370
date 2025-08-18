"""
Lazy Loading Registry System for Metis Agent.

Provides on-demand tool loading, parallel initialization, and optimized
startup performance through intelligent dependency management and caching.
"""
import time
import threading
import asyncio
import importlib
import inspect
import weakref
from typing import Dict, Any, List, Optional, Callable, Type, Union, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import logging
import json
import os

logger = logging.getLogger(__name__)


class LoadingStrategy(Enum):
    """Tool loading strategies."""
    EAGER = "eager"          # Load immediately
    LAZY = "lazy"            # Load on first use
    PRELOAD = "preload"      # Load during idle time
    ON_DEMAND = "on_demand"  # Load only when explicitly requested


class InitializationPriority(Enum):
    """Initialization priority levels."""
    CRITICAL = 1    # Must load first (core dependencies)
    HIGH = 2        # Important tools (frequently used)
    NORMAL = 3      # Standard tools
    LOW = 4         # Optional tools (rarely used)
    DEFERRED = 5    # Background loading


@dataclass
class ToolMetadata:
    """Metadata about a tool for lazy loading."""
    name: str
    module_path: str
    class_name: str
    priority: InitializationPriority
    strategy: LoadingStrategy
    dependencies: List[str]
    estimated_load_time_ms: float
    memory_estimate_mb: float
    description: str
    category: str
    lazy_loaded: bool = False
    load_count: int = 0
    last_loaded: Optional[float] = None
    initialization_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert enums to strings for JSON serialization
        data['priority'] = self.priority.value if hasattr(self.priority, 'value') else str(self.priority)
        data['strategy'] = self.strategy.value if hasattr(self.strategy, 'value') else str(self.strategy)
        return data


@dataclass
class LoadingStats:
    """Statistics about loading performance."""
    total_tools: int = 0
    eager_loaded: int = 0
    lazy_loaded: int = 0
    preloaded: int = 0
    failed_loads: int = 0
    total_load_time_ms: float = 0.0
    average_load_time_ms: float = 0.0
    startup_time_ms: float = 0.0
    memory_saved_mb: float = 0.0
    
    def update_stats(self, tools: Dict[str, ToolMetadata]):
        """Update statistics from tool metadata."""
        self.total_tools = len(tools)
        self.eager_loaded = sum(1 for t in tools.values() if t.strategy == LoadingStrategy.EAGER and t.lazy_loaded)
        self.lazy_loaded = sum(1 for t in tools.values() if t.strategy == LoadingStrategy.LAZY and t.lazy_loaded)
        self.preloaded = sum(1 for t in tools.values() if t.strategy == LoadingStrategy.PRELOAD and t.lazy_loaded)
        
        loaded_tools = [t for t in tools.values() if t.initialization_time_ms is not None]
        if loaded_tools:
            self.total_load_time_ms = sum(t.initialization_time_ms for t in loaded_tools)
            self.average_load_time_ms = self.total_load_time_ms / len(loaded_tools)
        
        # Estimate memory saved by lazy loading
        unloaded_tools = [t for t in tools.values() if not t.lazy_loaded]
        self.memory_saved_mb = sum(t.memory_estimate_mb for t in unloaded_tools)


class DependencyResolver:
    """Resolves tool dependencies for optimal loading order."""
    
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.resolved_order: List[str] = []
        
    def add_dependency(self, tool: str, dependency: str):
        """Add a dependency relationship."""
        self.dependency_graph[tool].add(dependency)
    
    def resolve_loading_order(self, tools: Dict[str, ToolMetadata]) -> List[str]:
        """
        Resolve optimal loading order considering dependencies and priorities.
        
        Returns:
            List of tool names in optimal loading order
        """
        # Build dependency graph
        for tool_name, metadata in tools.items():
            for dep in metadata.dependencies:
                self.add_dependency(tool_name, dep)
        
        # Topological sort with priority consideration
        visited = set()
        temp_visited = set()
        loading_order = []
        
        def visit(tool_name: str):
            if tool_name in temp_visited:
                logger.warning(f"Circular dependency detected involving {tool_name}")
                return
            if tool_name in visited:
                return
            
            temp_visited.add(tool_name)
            
            # Visit dependencies first
            for dep in self.dependency_graph.get(tool_name, []):
                if dep in tools:  # Only consider dependencies that are registered tools
                    visit(dep)
            
            temp_visited.remove(tool_name)
            visited.add(tool_name)
            loading_order.append(tool_name)
        
        # Sort tools by priority before processing
        tools_by_priority = sorted(
            tools.keys(),
            key=lambda name: (tools[name].priority.value, tools[name].estimated_load_time_ms)
        )
        
        # Visit all tools in priority order
        for tool_name in tools_by_priority:
            visit(tool_name)
        
        self.resolved_order = loading_order
        return loading_order


class LazyToolRegistry:
    """
    Advanced tool registry with lazy loading, parallel initialization,
    and intelligent dependency management.
    """
    
    def __init__(self, max_workers: int = 4, preload_on_startup: bool = True):
        """
        Initialize lazy tool registry.
        
        Args:
            max_workers: Maximum number of parallel loading threads
            preload_on_startup: Whether to preload high-priority tools on startup
        """
        self.max_workers = max_workers
        self.preload_on_startup = preload_on_startup
        
        # Core data structures
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.loaded_tools: Dict[str, Any] = {}  # Actual tool instances
        self.tool_classes: Dict[str, Type] = {}  # Cached tool classes
        self.loading_futures: Dict[str, asyncio.Future] = {}
        
        # Performance tracking
        self.stats = LoadingStats()
        self.dependency_resolver = DependencyResolver()
        
        # Threading and async support
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.RLock()
        self._startup_complete = False
        self._initialization_callbacks: List[Callable] = []
        
        # Configuration cache
        self._config_cache: Dict[str, Any] = {}
        self._config_cache_file = "tool_registry_cache.json"
        
        logger.info(f"LazyToolRegistry initialized: max_workers={max_workers}, "
                   f"preload_on_startup={preload_on_startup}")
    
    def register_tool(self, 
                     name: str,
                     module_path: str,
                     class_name: str,
                     priority: InitializationPriority = InitializationPriority.NORMAL,
                     strategy: LoadingStrategy = LoadingStrategy.LAZY,
                     dependencies: List[str] = None,
                     estimated_load_time_ms: float = 100.0,
                     memory_estimate_mb: float = 5.0,
                     description: str = "",
                     category: str = "general"):
        """
        Register a tool for lazy loading.
        
        Args:
            name: Tool name
            module_path: Python module path
            class_name: Class name within module
            priority: Loading priority
            strategy: Loading strategy
            dependencies: List of dependency tool names
            estimated_load_time_ms: Estimated loading time
            memory_estimate_mb: Estimated memory usage
            description: Tool description
            category: Tool category
        """
        metadata = ToolMetadata(
            name=name,
            module_path=module_path,
            class_name=class_name,
            priority=priority,
            strategy=strategy,
            dependencies=dependencies or [],
            estimated_load_time_ms=estimated_load_time_ms,
            memory_estimate_mb=memory_estimate_mb,
            description=description,
            category=category
        )
        
        with self._lock:
            self.tool_metadata[name] = metadata
            
            # If strategy is EAGER, load immediately
            if strategy == LoadingStrategy.EAGER and not self._startup_complete:
                self._load_tool_sync(name)
        
        logger.debug(f"Registered tool: {name} ({strategy.value}, priority={priority.value})")
    
    def get_tool(self, name: str, timeout: float = 30.0) -> Optional[Any]:
        """
        Get a tool instance, loading it if necessary.
        
        Args:
            name: Tool name
            timeout: Maximum time to wait for loading
            
        Returns:
            Tool instance or None if failed
        """
        with self._lock:
            # Return if already loaded
            if name in self.loaded_tools:
                metadata = self.tool_metadata.get(name)
                if metadata:
                    metadata.load_count += 1
                    metadata.last_loaded = time.time()
                return self.loaded_tools[name]
            
            # Check if tool is registered
            if name not in self.tool_metadata:
                logger.error(f"Tool '{name}' not registered")
                return None
        
        # Load the tool
        return self._load_tool_sync(name, timeout)
    
    async def get_tool_async(self, name: str, timeout: float = 30.0) -> Optional[Any]:
        """
        Get a tool instance asynchronously.
        
        Args:
            name: Tool name
            timeout: Maximum time to wait for loading
            
        Returns:
            Tool instance or None if failed
        """
        with self._lock:
            # Return if already loaded
            if name in self.loaded_tools:
                metadata = self.tool_metadata.get(name)
                if metadata:
                    metadata.load_count += 1
                    metadata.last_loaded = time.time()
                return self.loaded_tools[name]
            
            # Check if tool is registered
            if name not in self.tool_metadata:
                logger.error(f"Tool '{name}' not registered")
                return None
            
            # Check if loading is already in progress
            if name in self.loading_futures:
                try:
                    return await asyncio.wait_for(self.loading_futures[name], timeout=timeout)
                except asyncio.TimeoutError:
                    logger.error(f"Timeout loading tool '{name}'")
                    return None
        
        # Start async loading
        return await self._load_tool_async(name, timeout)
    
    def list_tools(self, category: str = None, loaded_only: bool = False) -> List[str]:
        """
        List available tools.
        
        Args:
            category: Filter by category
            loaded_only: Only return loaded tools
            
        Returns:
            List of tool names
        """
        with self._lock:
            tools = self.tool_metadata.keys()
            
            if category:
                tools = [name for name in tools if self.tool_metadata[name].category == category]
            
            if loaded_only:
                tools = [name for name in tools if name in self.loaded_tools]
            
            return list(tools)
    
    def preload_tools(self, tool_names: List[str] = None) -> Dict[str, bool]:
        """
        Preload specified tools or all PRELOAD strategy tools.
        
        Args:
            tool_names: Specific tools to preload, or None for all PRELOAD tools
            
        Returns:
            Dictionary of tool_name -> success_status
        """
        if tool_names is None:
            # Find all tools marked for preloading
            tool_names = [
                name for name, metadata in self.tool_metadata.items()
                if metadata.strategy == LoadingStrategy.PRELOAD
            ]
        
        logger.info(f"Preloading {len(tool_names)} tools: {tool_names}")
        
        # Load tools in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_tool = {
                executor.submit(self._load_tool_sync, name): name
                for name in tool_names
            }
            
            for future in as_completed(future_to_tool):
                tool_name = future_to_tool[future]
                try:
                    tool_instance = future.result()
                    results[tool_name] = tool_instance is not None
                except Exception as e:
                    logger.error(f"Failed to preload tool '{tool_name}': {e}")
                    results[tool_name] = False
        
        return results
    
    async def initialize_startup(self) -> Dict[str, Any]:
        """
        Initialize the registry and perform startup optimizations.
        
        Returns:
            Startup performance statistics
        """
        startup_start = time.time()
        logger.info("Starting lazy registry initialization...")
        
        # Load configuration cache
        self._load_config_cache()
        
        # Resolve loading order
        loading_order = self.dependency_resolver.resolve_loading_order(self.tool_metadata)
        logger.info(f"Resolved loading order: {loading_order[:5]}... (showing first 5)")
        
        # Load EAGER and CRITICAL priority tools first
        critical_tools = [
            name for name in loading_order
            if self.tool_metadata[name].priority == InitializationPriority.CRITICAL
            or self.tool_metadata[name].strategy == LoadingStrategy.EAGER
        ]
        
        if critical_tools:
            logger.info(f"Loading {len(critical_tools)} critical tools...")
            critical_results = self.preload_tools(critical_tools)
            logger.info(f"Critical tools loaded: {sum(critical_results.values())}/{len(critical_tools)}")
        
        # Start preloading high-priority tools if enabled
        if self.preload_on_startup:
            preload_tools = [
                name for name in loading_order
                if self.tool_metadata[name].strategy == LoadingStrategy.PRELOAD
                or self.tool_metadata[name].priority == InitializationPriority.HIGH
            ]
            
            if preload_tools:
                logger.info(f"Starting background preload of {len(preload_tools)} tools...")
                # Start background preloading (don't wait for completion)
                asyncio.create_task(self._background_preload(preload_tools))
        
        # Mark startup as complete
        self._startup_complete = True
        startup_time = (time.time() - startup_start) * 1000
        self.stats.startup_time_ms = startup_time
        
        # Update statistics
        self.stats.update_stats(self.tool_metadata)
        
        # Save configuration cache
        self._save_config_cache()
        
        # Notify initialization callbacks
        for callback in self._initialization_callbacks:
            try:
                callback(self)
            except Exception as e:
                logger.error(f"Error in initialization callback: {e}")
        
        logger.info(f"Lazy registry initialization completed in {startup_time:.2f}ms")
        
        return {
            "startup_time_ms": startup_time,
            "critical_tools_loaded": len(critical_tools) if critical_tools else 0,
            "tools_registered": len(self.tool_metadata),
            "memory_saved_mb": self.stats.memory_saved_mb,
            "loading_order": loading_order
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        with self._lock:
            self.stats.update_stats(self.tool_metadata)
            
            loaded_count = len(self.loaded_tools)
            total_count = len(self.tool_metadata)
            
            # Calculate loading efficiency
            if total_count > 0:
                loading_efficiency = (loaded_count / total_count) * 100
            else:
                loading_efficiency = 0
            
            # Tool usage statistics
            usage_stats = {}
            for name, metadata in self.tool_metadata.items():
                usage_stats[name] = {
                    "load_count": metadata.load_count,
                    "last_loaded": metadata.last_loaded,
                    "strategy": metadata.strategy.value,
                    "loaded": name in self.loaded_tools
                }
            
            return {
                "performance": asdict(self.stats),
                "loading_efficiency_percent": round(loading_efficiency, 2),
                "loaded_tools": loaded_count,
                "total_tools": total_count,
                "memory_usage": {
                    "estimated_loaded_mb": sum(
                        self.tool_metadata[name].memory_estimate_mb
                        for name in self.loaded_tools.keys()
                    ),
                    "estimated_total_mb": sum(
                        metadata.memory_estimate_mb
                        for metadata in self.tool_metadata.values()
                    ),
                    "memory_saved_mb": self.stats.memory_saved_mb
                },
                "tool_usage": usage_stats,
                "startup_complete": self._startup_complete
            }
    
    def add_initialization_callback(self, callback: Callable):
        """Add callback to be called after initialization."""
        self._initialization_callbacks.append(callback)
    
    def unload_tool(self, name: str) -> bool:
        """
        Unload a tool to free memory.
        
        Args:
            name: Tool name to unload
            
        Returns:
            True if successfully unloaded
        """
        with self._lock:
            if name in self.loaded_tools:
                del self.loaded_tools[name]
                
                # Update metadata
                if name in self.tool_metadata:
                    self.tool_metadata[name].lazy_loaded = False
                
                logger.info(f"Unloaded tool: {name}")
                return True
            
            return False
    
    def reload_tool(self, name: str) -> Optional[Any]:
        """
        Reload a tool (useful for development).
        
        Args:
            name: Tool name to reload
            
        Returns:
            Reloaded tool instance
        """
        # Unload first
        self.unload_tool(name)
        
        # Clear class cache
        if name in self.tool_classes:
            del self.tool_classes[name]
        
        # Reload
        return self.get_tool(name)
    
    def shutdown(self):
        """Shutdown the registry and cleanup resources."""
        logger.info("Shutting down lazy tool registry...")
        
        # Cancel any pending loading futures
        with self._lock:
            for future in self.loading_futures.values():
                if not future.done():
                    future.cancel()
            self.loading_futures.clear()
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        # Save final configuration cache
        self._save_config_cache()
        
        logger.info("Lazy tool registry shutdown complete")
    
    # Private methods
    
    def _load_tool_sync(self, name: str, timeout: float = 30.0) -> Optional[Any]:
        """Synchronously load a tool."""
        start_time = time.time()
        
        try:
            metadata = self.tool_metadata.get(name)
            if not metadata:
                return None
            
            # Load dependencies first
            for dep_name in metadata.dependencies:
                if dep_name in self.tool_metadata and dep_name not in self.loaded_tools:
                    logger.debug(f"Loading dependency {dep_name} for {name}")
                    self._load_tool_sync(dep_name, timeout)
            
            # Import module and get class
            if name not in self.tool_classes:
                module = importlib.import_module(metadata.module_path)
                tool_class = getattr(module, metadata.class_name)
                self.tool_classes[name] = tool_class
            else:
                tool_class = self.tool_classes[name]
            
            # Create instance
            tool_instance = tool_class()
            
            # Store in registry
            with self._lock:
                self.loaded_tools[name] = tool_instance
                metadata.lazy_loaded = True
                metadata.load_count += 1
                metadata.last_loaded = time.time()
                metadata.initialization_time_ms = (time.time() - start_time) * 1000
            
            logger.debug(f"Loaded tool '{name}' in {metadata.initialization_time_ms:.2f}ms")
            return tool_instance
            
        except Exception as e:
            self.stats.failed_loads += 1
            logger.error(f"Failed to load tool '{name}': {e}")
            return None
    
    async def _load_tool_async(self, name: str, timeout: float = 30.0) -> Optional[Any]:
        """Asynchronously load a tool."""
        # Create future for this loading operation
        future = asyncio.Future()
        self.loading_futures[name] = future
        
        try:
            # Run synchronous loading in thread pool
            loop = asyncio.get_event_loop()
            tool_instance = await loop.run_in_executor(
                self.executor, 
                self._load_tool_sync, 
                name, 
                timeout
            )
            
            future.set_result(tool_instance)
            return tool_instance
            
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # Clean up future
            with self._lock:
                self.loading_futures.pop(name, None)
    
    async def _background_preload(self, tool_names: List[str]):
        """Background preloading of tools."""
        logger.info(f"Starting background preload of {len(tool_names)} tools")
        
        # Load tools in parallel batches
        batch_size = self.max_workers
        for i in range(0, len(tool_names), batch_size):
            batch = tool_names[i:i + batch_size]
            
            # Load batch in parallel
            tasks = [self._load_tool_async(name) for name in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            successful = sum(1 for result in results if not isinstance(result, Exception))
            logger.info(f"Background preload batch {i//batch_size + 1}: {successful}/{len(batch)} tools loaded")
            
            # Brief pause between batches to avoid overwhelming system
            await asyncio.sleep(0.1)
        
        logger.info("Background preload completed")
    
    def _load_config_cache(self):
        """Load configuration cache from disk."""
        try:
            if os.path.exists(self._config_cache_file):
                with open(self._config_cache_file, 'r') as f:
                    self._config_cache = json.load(f)
                logger.debug(f"Loaded configuration cache with {len(self._config_cache)} entries")
        except Exception as e:
            logger.warning(f"Failed to load configuration cache: {e}")
            self._config_cache = {}
    
    def _save_config_cache(self):
        """Save configuration cache to disk."""
        try:
            cache_data = {
                "stats": asdict(self.stats),
                "tool_metadata": {
                    name: metadata.to_dict() 
                    for name, metadata in self.tool_metadata.items()
                },
                "last_updated": time.time()
            }
            
            with open(self._config_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug("Saved configuration cache")
        except Exception as e:
            logger.warning(f"Failed to save configuration cache: {e}")


# Global lazy registry instance
_lazy_registry: Optional[LazyToolRegistry] = None


def get_lazy_registry() -> LazyToolRegistry:
    """Get or create global lazy tool registry."""
    global _lazy_registry
    if _lazy_registry is None:
        _lazy_registry = LazyToolRegistry()
    return _lazy_registry


def configure_lazy_registry(max_workers: int = 4, 
                          preload_on_startup: bool = True) -> LazyToolRegistry:
    """Configure global lazy tool registry."""
    global _lazy_registry
    if _lazy_registry:
        _lazy_registry.shutdown()
    
    _lazy_registry = LazyToolRegistry(max_workers, preload_on_startup)
    return _lazy_registry