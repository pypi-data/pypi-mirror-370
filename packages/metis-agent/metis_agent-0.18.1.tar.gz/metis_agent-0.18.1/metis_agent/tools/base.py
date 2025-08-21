"""
Enhanced Base Tool interface for Metis Agent.

This module defines the enhanced base class with capabilities metadata,
performance monitoring, and composition support.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, AsyncIterator
import time
import os
import json
import asyncio
import logging
from dataclasses import dataclass
from ..utils.input_validator import validate_input, ValidationError
from ..core.cache_manager import get_cache_manager, CachePolicy
from ..core.memory_monitor import get_memory_monitor

# Optional dependency - graceful fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class QueryAnalysis:
    """
    Data class for query analysis results.
    """
    complexity: str  # simple, moderate, complex
    intents: List[str]  # List of detected intents
    requirements: Dict[str, Any]  # Resource requirements
    confidence: float  # Confidence in analysis (0-1)
    entities: List[str] = None  # Extracted entities
    sentiment: str = "neutral"  # positive, negative, neutral


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    All tools must implement the can_handle and execute methods.
    Enhanced with caching capabilities for performance optimization.
    """
    
    def __init__(self):
        """Initialize base tool with caching and memory monitoring."""
        self._cache_enabled = True
        self._cache_policy = CachePolicy.CONSERVATIVE
        self._custom_ttl = None
        self._memory_tracking_enabled = True
        self._setup_cache_policy()
        self._setup_memory_tracking()
    
    @abstractmethod
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle the given task.
        
        Args:
            task: The task to check
            
        Returns:
            True if the tool can handle the task, False otherwise
        """
        pass
        
    @abstractmethod
    def execute(self, task: str) -> Any:
        """
        Execute the task using this tool.
        
        Args:
            task: The task to execute
            
        Returns:
            The result of executing the task
        """
        pass
    
    async def execute_async(self, task: str) -> Any:
        """
        Execute the task asynchronously using this tool.
        
        Default implementation runs the synchronous execute method in a thread pool.
        Tools can override this for true async implementation.
        
        Args:
            task: The task to execute
            
        Returns:
            The result of executing the task
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, task)
    
    async def execute_stream_async(self, task: str) -> AsyncIterator[Any]:
        """
        Execute the task and stream results asynchronously.
        
        Default implementation yields the final result.
        Tools can override this for true streaming implementation.
        
        Args:
            task: The task to execute
            
        Yields:
            Partial or complete results as they become available
        """
        result = await self.execute_async(task)
        yield result
    
    def supports_async(self) -> bool:
        """
        Check if this tool supports true async execution.
        
        Returns:
            True if the tool overrides execute_async with a true async implementation
        """
        # Check if the tool has overridden execute_async
        return (
            hasattr(self, 'execute_async') and 
            getattr(self.execute_async, '__func__', None) is not BaseTool.execute_async.__func__
        )
    
    def supports_streaming(self) -> bool:
        """
        Check if this tool supports streaming results.
        
        Returns:
            True if the tool overrides execute_stream_async
        """
        return (
            hasattr(self, 'execute_stream_async') and 
            getattr(self.execute_stream_async, '__func__', None) is not BaseTool.execute_stream_async.__func__
        )
    
    # Cache-Enhanced Execution Methods
    
    def execute_with_cache(self, task: str, **kwargs) -> Any:
        """
        Execute task with intelligent caching support.
        
        Args:
            task: The task to execute
            **kwargs: Additional parameters
            
        Returns:
            Result from cache or fresh execution
        """
        if not self._cache_enabled:
            return self.execute(task, **kwargs)
        
        # Try to get from cache first
        cache_manager = get_cache_manager()
        tool_name = self.__class__.__name__
        
        cached_result = cache_manager.get(tool_name, task, **kwargs)
        if cached_result is not None:
            return self._wrap_cached_result(cached_result, from_cache=True)
        
        # Execute and cache result
        result = self.execute(task, **kwargs)
        
        # Cache the result if it's cacheable
        if self._should_cache_result(result):
            cache_manager.set(tool_name, task, result, **kwargs)
        
        return self._wrap_cached_result(result, from_cache=False)
    
    async def execute_async_with_cache(self, task: str, **kwargs) -> Any:
        """
        Execute task asynchronously with caching support.
        
        Args:
            task: The task to execute
            **kwargs: Additional parameters
            
        Returns:
            Result from cache or fresh async execution
        """
        if not self._cache_enabled:
            return await self.execute_async(task, **kwargs)
        
        # Try to get from cache first
        cache_manager = get_cache_manager()
        tool_name = self.__class__.__name__
        
        cached_result = cache_manager.get(tool_name, task, **kwargs)
        if cached_result is not None:
            return self._wrap_cached_result(cached_result, from_cache=True)
        
        # Execute async and cache result
        result = await self.execute_async(task, **kwargs)
        
        # Cache the result if it's cacheable
        if self._should_cache_result(result):
            cache_manager.set(tool_name, task, result, **kwargs)
        
        return self._wrap_cached_result(result, from_cache=False)
    
    # Cache Configuration Methods
    
    def configure_cache(self, 
                       enabled: bool = True, 
                       policy: CachePolicy = CachePolicy.CONSERVATIVE,
                       ttl: Optional[float] = None):
        """
        Configure caching behavior for this tool.
        
        Args:
            enabled: Whether caching is enabled
            policy: Cache policy to use
            ttl: Custom TTL in seconds (overrides policy default)
        """
        self._cache_enabled = enabled
        self._cache_policy = policy
        self._custom_ttl = ttl
        
        # Update cache manager policy
        if enabled:
            cache_manager = get_cache_manager()
            cache_manager.set_tool_policy(
                self.__class__.__name__,
                policy=policy,
                ttl=ttl,
                cache_enabled=enabled
            )
    
    def invalidate_cache(self):
        """Invalidate all cached results for this tool."""
        cache_manager = get_cache_manager()
        cache_manager.invalidate_tool(self.__class__.__name__)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for this tool."""
        cache_manager = get_cache_manager()
        all_stats = cache_manager.get_stats()
        
        # Filter for this tool if possible (simplified for now)
        return {
            "tool_name": self.__class__.__name__,
            "cache_enabled": self._cache_enabled,
            "cache_policy": self._cache_policy.value if self._cache_policy else None,
            "custom_ttl": self._custom_ttl,
            "global_cache_stats": all_stats
        }
    
    # Cache Helper Methods
    
    def _setup_cache_policy(self):
        """Setup default cache policy for this tool."""
        # Can be overridden by subclasses for tool-specific defaults
        tool_name = self.__class__.__name__
        
        # Set default policies for common tools
        if "Search" in tool_name or "Grep" in tool_name:
            self._cache_policy = CachePolicy.AGGRESSIVE
            self._custom_ttl = 1800  # 30 minutes for search results
        elif "Calculator" in tool_name or "Math" in tool_name:
            self._cache_policy = CachePolicy.AGGRESSIVE
            self._custom_ttl = 7200  # 2 hours for calculations
        elif "Web" in tool_name or "Scraper" in tool_name:
            self._cache_policy = CachePolicy.CONSERVATIVE
            self._custom_ttl = 900   # 15 minutes for web content
        elif "Code" in tool_name or "Generation" in tool_name:
            self._cache_policy = CachePolicy.CONSERVATIVE
            self._custom_ttl = 3600  # 1 hour for generated code
    
    def _should_cache_result(self, result: Any) -> bool:
        """
        Determine if a result should be cached.
        
        Args:
            result: The result to evaluate
            
        Returns:
            True if result should be cached
        """
        # Don't cache errors or None results
        if result is None:
            return False
        
        # Don't cache error responses
        if isinstance(result, dict) and result.get('success') is False:
            return False
        
        # Don't cache very large results (>1MB estimated)
        try:
            if hasattr(result, '__sizeof__'):
                size = result.__sizeof__()
            else:
                size = len(str(result).encode('utf-8'))
            
            if size > 1024 * 1024:  # 1MB limit
                return False
        except:
            pass  # If size estimation fails, proceed with caching
        
        return True
    
    def _wrap_cached_result(self, result: Any, from_cache: bool) -> Any:
        """
        Wrap result with cache metadata.
        
        Args:
            result: The result to wrap
            from_cache: Whether result came from cache
            
        Returns:
            Result with cache metadata
        """
        # If result is already a dict with metadata, update it
        if isinstance(result, dict) and "metadata" in result:
            if "cache" not in result["metadata"]:
                result["metadata"]["cache"] = {}
            result["metadata"]["cache"]["from_cache"] = from_cache
            result["metadata"]["cache"]["tool_name"] = self.__class__.__name__
            return result
        
        # If result is a dict but no metadata, add it
        elif isinstance(result, dict):
            result["metadata"] = {
                "cache": {
                    "from_cache": from_cache,
                    "tool_name": self.__class__.__name__
                }
            }
            return result
        
        # For non-dict results, return as-is to maintain compatibility
        return result
    
    # Memory Tracking Methods
    
    def execute_with_monitoring(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute task with comprehensive performance and memory monitoring.
        
        Args:
            task: The task to execute
            **kwargs: Additional parameters
            
        Returns:
            Result with performance and memory metadata
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Get memory tracker for this tool
        if self._memory_tracking_enabled:
            memory_monitor = get_memory_monitor()
            memory_tracker = memory_monitor.get_tracker(self.__class__.__name__)
            
            # Estimate task memory requirement
            task_memory_estimate = self._estimate_task_memory(task, **kwargs)
            memory_tracker.record_allocation(task_memory_estimate, {
                "task_type": "execution",
                "task_preview": task[:100] if isinstance(task, str) else str(task)[:100]
            })
        
        try:
            # Use cache-enabled execution
            result = self.execute_with_cache(task, **kwargs)
            execution_time = time.time() - start_time
            end_memory = self._get_memory_usage()
            memory_used = end_memory - start_memory
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                result = {"data": result, "success": True}
            
            # Add comprehensive monitoring metadata
            if "metadata" not in result:
                result["metadata"] = {}
            
            result["metadata"]["monitoring"] = {
                "execution_time": round(execution_time, 4),
                "memory_used_mb": round(memory_used, 3),
                "memory_start_mb": round(start_memory, 3),
                "memory_end_mb": round(end_memory, 3),
                "tool_name": self.__class__.__name__,
                "memory_tracking_enabled": self._memory_tracking_enabled
            }
            
            # Record memory deallocation if tracking enabled
            if self._memory_tracking_enabled and hasattr(memory_tracker, 'record_deallocation'):
                # Estimate memory released (conservative estimate)
                memory_released = max(0, task_memory_estimate - memory_used)
                memory_tracker.record_deallocation(memory_released)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record deallocation for failed execution
            if self._memory_tracking_enabled:
                memory_tracker.record_deallocation(task_memory_estimate)
            
            return self._handle_execution_error(e, execution_time)
    
    async def execute_async_with_monitoring(self, task: str, **kwargs) -> Any:
        """
        Execute task asynchronously with comprehensive monitoring.
        
        Args:
            task: The task to execute
            **kwargs: Additional parameters
            
        Returns:
            Result with performance and memory metadata
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Get memory tracker for this tool
        if self._memory_tracking_enabled:
            memory_monitor = get_memory_monitor()
            memory_tracker = memory_monitor.get_tracker(f"{self.__class__.__name__}_async")
            
            # Estimate task memory requirement
            task_memory_estimate = self._estimate_task_memory(task, **kwargs)
            memory_tracker.record_allocation(task_memory_estimate, {
                "task_type": "async_execution",
                "task_preview": task[:100] if isinstance(task, str) else str(task)[:100]
            })
        
        try:
            # Use cache-enabled async execution
            result = await self.execute_async_with_cache(task, **kwargs)
            execution_time = time.time() - start_time
            end_memory = self._get_memory_usage()
            memory_used = end_memory - start_memory
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                result = {"data": result, "success": True}
            
            # Add comprehensive monitoring metadata
            if "metadata" not in result:
                result["metadata"] = {}
            
            result["metadata"]["async_monitoring"] = {
                "execution_time": round(execution_time, 4),
                "memory_used_mb": round(memory_used, 3),
                "memory_start_mb": round(start_memory, 3),
                "memory_end_mb": round(end_memory, 3),
                "tool_name": self.__class__.__name__,
                "async_execution": True,
                "memory_tracking_enabled": self._memory_tracking_enabled
            }
            
            # Record memory deallocation if tracking enabled
            if self._memory_tracking_enabled:
                memory_released = max(0, task_memory_estimate - memory_used)
                memory_tracker.record_deallocation(memory_released)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record deallocation for failed execution
            if self._memory_tracking_enabled:
                memory_tracker.record_deallocation(task_memory_estimate)
            
            return self._handle_execution_error(e, execution_time)
    
    def configure_memory_tracking(self, enabled: bool = True):
        """
        Configure memory tracking for this tool.
        
        Args:
            enabled: Whether memory tracking is enabled
        """
        self._memory_tracking_enabled = enabled
        logger.info(f"Memory tracking {'enabled' if enabled else 'disabled'} for {self.__class__.__name__}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this tool."""
        if not self._memory_tracking_enabled:
            return {
                "tool_name": self.__class__.__name__,
                "memory_tracking_enabled": False,
                "message": "Memory tracking is disabled for this tool"
            }
        
        try:
            memory_monitor = get_memory_monitor()
            sync_tracker = memory_monitor.component_trackers.get(self.__class__.__name__)
            async_tracker = memory_monitor.component_trackers.get(f"{self.__class__.__name__}_async")
            
            stats = {
                "tool_name": self.__class__.__name__,
                "memory_tracking_enabled": True,
                "current_memory_mb": self._get_memory_usage(),
                "sync_execution": sync_tracker.get_stats() if sync_tracker else None,
                "async_execution": async_tracker.get_stats() if async_tracker else None
            }
            
            return stats
            
        except Exception as e:
            return {
                "tool_name": self.__class__.__name__,
                "memory_tracking_enabled": True,
                "error": f"Failed to get memory stats: {str(e)}"
            }
    
    def _setup_memory_tracking(self):
        """Setup memory tracking for this tool."""
        # Initialize memory tracker for this tool
        if self._memory_tracking_enabled:
            try:
                memory_monitor = get_memory_monitor()
                # This will create trackers when first used
                logger.debug(f"Memory tracking initialized for {self.__class__.__name__}")
            except Exception as e:
                logger.warning(f"Failed to setup memory tracking for {self.__class__.__name__}: {e}")
                self._memory_tracking_enabled = False
    
    def _estimate_task_memory(self, task: str, **kwargs) -> float:
        """
        Estimate memory requirements for a task.
        
        Args:
            task: The task to estimate
            **kwargs: Additional parameters
            
        Returns:
            Estimated memory usage in MB
        """
        # Basic estimation based on task complexity and tool type
        base_memory = 1.0  # 1MB base
        
        # Adjust based on task size
        if isinstance(task, str):
            task_complexity = len(task) / 1000  # 1KB = small increase
            base_memory += task_complexity
        
        # Adjust based on tool type
        tool_name = self.__class__.__name__.lower()
        if "search" in tool_name or "grep" in tool_name:
            base_memory *= 2.0  # Search operations use more memory
        elif "math" in tool_name or "calculator" in tool_name:
            base_memory *= 0.5  # Math operations are lightweight
        elif "web" in tool_name or "scraper" in tool_name:
            base_memory *= 3.0  # Web operations can use significant memory
        elif "code" in tool_name or "generation" in tool_name:
            base_memory *= 2.5  # Code generation uses moderate memory
        
        # Adjust for parameters
        param_count = len(kwargs)
        base_memory += param_count * 0.1  # Small increase per parameter
        
        return max(0.1, base_memory)  # Minimum 0.1MB
        
    def get_description(self) -> str:
        """
        Get a description of this tool.
        
        Returns:
            Tool description
        """
        # Default to using the class docstring
        return self.__doc__ or f"{self.__class__.__name__} Tool"
        
    def get_examples(self) -> list:
        """
        Get example tasks that this tool can handle.
        
        Returns:
            List of example tasks
        """
        # Default to empty list, should be overridden by subclasses
        return []
        
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.__class__.__name__}"
        
    def __repr__(self) -> str:
        """Detailed string representation of the tool."""
        return f"{self.__class__.__name__}()"
    
    # Input Validation Helper Methods
    
    def _validate_task_input(self, task: str, context: str = "general") -> str:
        """
        Validate task input for security and format.
        
        Args:
            task: Task string to validate
            context: Context for validation (general, command, path, etc.)
            
        Returns:
            Validated and sanitized task string
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            return validate_input(task, "string", max_length=10000, context=context)
        except ValidationError as e:
            raise ValidationError(f"Task validation failed in {self.__class__.__name__}: {e}")
    
    def _validate_kwargs_input(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate keyword arguments for security.
        
        Args:
            kwargs: Keyword arguments to validate
            
        Returns:
            Validated keyword arguments
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            return validate_input(kwargs, "dict")
        except ValidationError as e:
            raise ValidationError(f"Kwargs validation failed in {self.__class__.__name__}: {e}")
    
    def _validate_string_param(self, value: Any, param_name: str, 
                              max_length: int = 1000, context: str = "general") -> str:
        """
        Validate a string parameter.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter (for error messages)
            max_length: Maximum allowed length
            context: Validation context
            
        Returns:
            Validated string
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            return validate_input(value, "string", max_length=max_length, context=context)
        except ValidationError as e:
            raise ValidationError(f"Parameter '{param_name}' validation failed: {e}")
    
    def _validate_integer_param(self, value: Any, param_name: str, 
                               min_val: int = None, max_val: int = None) -> int:
        """
        Validate an integer parameter.
        
        Args:
            value: Value to validate
            param_name: Name of the parameter
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Validated integer
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            return validate_input(value, "integer", min_val=min_val, max_val=max_val)
        except ValidationError as e:
            raise ValidationError(f"Parameter '{param_name}' validation failed: {e}")
    
    # Enhanced functionality methods
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return detailed capability metadata for analysis engine.
        
        Returns:
            Dictionary containing tool capabilities and requirements
        """
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text"],
            "output_types": ["structured_data"],
            "estimated_execution_time": "1-5s",
            "requires_internet": False,
            "requires_filesystem": False,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": [],
            "api_dependencies": [],
            "memory_usage": "low"
        }
    
    def analyze_compatibility(self, query_analysis: 'QueryAnalysis') -> float:
        """
        Return compatibility score (0-1) for this query analysis.
        
        Args:
            query_analysis: Analysis of the user query
            
        Returns:
            Compatibility score between 0 and 1
        """
        capabilities = self.get_capabilities()
        score = 0.0
        
        # Check complexity compatibility
        if hasattr(query_analysis, 'complexity') and query_analysis.complexity in capabilities.get("complexity_levels", []):
            score += 0.4
        
        # Check intent alignment
        if hasattr(query_analysis, 'intents'):
            supported_intents = capabilities.get("supported_intents", [])
            if any(intent in supported_intents for intent in query_analysis.intents):
                score += 0.4
        
        # Check resource requirements
        if hasattr(query_analysis, 'requirements'):
            if self._can_meet_resource_requirements(query_analysis.requirements):
                score += 0.2
        else:
            score += 0.2  # Default if no specific requirements
        
        return min(score, 1.0)
    
    def _can_meet_resource_requirements(self, requirements: Dict[str, Any]) -> bool:
        """
        Check if tool can meet specified resource requirements.
        
        Args:
            requirements: Dictionary of resource requirements
            
        Returns:
            True if requirements can be met
        """
        capabilities = self.get_capabilities()
        
        # Check internet requirement
        if requirements.get("requires_internet", False) and not capabilities.get("requires_internet", False):
            return False
        
        # Check filesystem requirement
        if requirements.get("requires_filesystem", False) and not capabilities.get("requires_filesystem", False):
            return False
        
        # Check if tool is resource intensive when low resource usage is required
        if requirements.get("low_resource", False) and capabilities.get("resource_intensive", False):
            return False
        
        return True
    
    def execute_with_monitoring(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute task with performance monitoring.
        
        Args:
            task: The task to execute
            **kwargs: Additional parameters
            
        Returns:
            Result with performance metadata
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        api_calls_before = self._get_api_call_count()
        
        try:
            result = self.execute(task, **kwargs)
            execution_time = time.time() - start_time
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                result = {"data": result, "success": True}
            
            # Add performance metadata
            if "metadata" not in result:
                result["metadata"] = {}
            
            result["metadata"]["performance"] = {
                "execution_time": round(execution_time, 4),
                "memory_usage_mb": self._get_memory_usage() - start_memory,
                "api_calls_made": self._get_api_call_count() - api_calls_before,
                "tool_name": self.__class__.__name__
            }
            
            return result
            
        except Exception as e:
            return self._handle_execution_error(e, time.time() - start_time)
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Memory usage in megabytes
        """
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    def _get_api_call_count(self) -> int:
        """
        Get number of API calls made (to be overridden by tools that make API calls).
        
        Returns:
            Number of API calls made
        """
        return 0
    
    def _handle_execution_error(self, error: Exception, execution_time: float) -> Dict[str, Any]:
        """
        Handle execution errors with performance data.
        
        Args:
            error: The exception that occurred
            execution_time: Time taken before error
            
        Returns:
            Error response with metadata
        """
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
            "metadata": {
                "tool_name": self.__class__.__name__,
                "performance": {
                    "execution_time": round(execution_time, 4),
                    "failed": True
                }
            }
        }


class ComposableTool(BaseTool):
    """
    Base class for tools that can be composed in pipelines.
    
    Provides schema validation and tool chaining capabilities.
    """
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for input validation.
        
        Returns:
            JSON schema dictionary for input validation
        """
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task to execute"
                }
            },
            "required": ["task"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for output validation.
        
        Returns:
            JSON schema dictionary for output validation
        """
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the operation was successful"
                },
                "data": {
                    "type": "object",
                    "description": "The result data"
                },
                "metadata": {
                    "type": "object",
                    "description": "Operation metadata"
                }
            },
            "required": ["success"]
        }
    
    def can_chain_with(self, other_tool: 'BaseTool') -> bool:
        """
        Check if this tool's output is compatible with another tool's input.
        
        Args:
            other_tool: The tool to check compatibility with
            
        Returns:
            True if tools can be chained
        """
        if not isinstance(other_tool, ComposableTool):
            return False
        
        return self._schemas_compatible(
            self.get_output_schema(),
            other_tool.get_input_schema()
        )
    
    def _schemas_compatible(self, output_schema: Dict[str, Any], input_schema: Dict[str, Any]) -> bool:
        """
        Check if output schema is compatible with input schema.
        
        Args:
            output_schema: Schema of output data
            input_schema: Schema of required input data
            
        Returns:
            True if schemas are compatible
        """
        # Basic compatibility check
        # In a full implementation, this would do deep schema validation
        
        output_props = output_schema.get("properties", {})
        input_props = input_schema.get("properties", {})
        input_required = input_schema.get("required", [])
        
        # Check if all required input properties are available in output
        for required_prop in input_required:
            if required_prop not in output_props:
                return False
        
        return True
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against input schema.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if data is valid
        """
        schema = self.get_input_schema()
        required_fields = schema.get("required", [])
        
        # Basic validation - check required fields
        for field in required_fields:
            if field not in data:
                return False
        
        return True
    
    def validate_output(self, data: Dict[str, Any]) -> bool:
        """
        Validate output data against output schema.
        
        Args:
            data: Output data to validate
            
        Returns:
            True if data is valid
        """
        schema = self.get_output_schema()
        required_fields = schema.get("required", [])
        
        # Basic validation - check required fields
        for field in required_fields:
            if field not in data:
                return False
        
        return True