"""
Cache management CLI commands for Metis Agent.

Provides commands to interact with the caching system, monitor performance,
and configure cache policies.
"""
import json
from typing import Dict, Any
from ..core.cache_manager import get_cache_manager, CachePolicy, configure_cache
from ..tools.registry import get_tool_registry


def cache_stats_command() -> Dict[str, Any]:
    """Get comprehensive cache statistics."""
    cache_manager = get_cache_manager()
    stats = cache_manager.get_stats()
    
    return {
        "success": True,
        "data": {
            "cache_performance": {
                "hit_rate": f"{stats['metrics']['hit_rate']:.1f}%",
                "miss_rate": f"{stats['metrics']['miss_rate']:.1f}%",
                "total_hits": stats['metrics']['hits'],
                "total_misses": stats['metrics']['misses'],
                "total_operations": stats['metrics']['hits'] + stats['metrics']['misses']
            },
            "memory_usage": {
                "current_mb": f"{stats['memory_usage_mb']:.2f}",
                "max_mb": f"{stats['max_memory_mb']:.2f}",
                "utilization": f"{(stats['memory_usage_mb'] / stats['max_memory_mb'] * 100):.1f}%"
            },
            "cache_size": {
                "current_entries": stats['size'],
                "max_entries": stats['max_size'],
                "utilization": f"{(stats['size'] / stats['max_size'] * 100):.1f}%"
            },
            "maintenance": {
                "evictions": stats['metrics']['evictions'],
                "expired_removals": stats['metrics']['expired_removals'],
                "stale_entries": stats['stale_entries'],
                "oldest_entry_age_minutes": f"{stats['oldest_entry_age'] / 60:.1f}"
            },
            "tool_policies": stats.get('tool_policies', {})
        }
    }


def cache_clear_command() -> Dict[str, Any]:
    """Clear all cache entries."""
    cache_manager = get_cache_manager()
    cache_manager.clear()
    
    return {
        "success": True,
        "message": "Cache cleared successfully",
        "data": {"entries_removed": "all"}
    }


def cache_cleanup_command() -> Dict[str, Any]:
    """Force cleanup of expired cache entries."""
    cache_manager = get_cache_manager()
    removed = cache_manager.force_cleanup()
    
    return {
        "success": True,
        "message": f"Cache cleanup completed - removed {removed} expired entries",
        "data": {"expired_entries_removed": removed}
    }


def cache_configure_command(max_size: int = 1000, max_memory_mb: int = 100, default_ttl: int = 3600) -> Dict[str, Any]:
    """Configure global cache settings."""
    try:
        cache_manager = configure_cache(
            max_size=max_size,
            max_memory_mb=max_memory_mb,
            default_ttl=default_ttl
        )
        
        return {
            "success": True,
            "message": "Cache configuration updated",
            "data": {
                "max_size": max_size,
                "max_memory_mb": max_memory_mb,
                "default_ttl": default_ttl
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to configure cache: {str(e)}"
        }


def cache_tool_policy_command(tool_name: str, policy: str = "conservative", ttl: int = None, enabled: bool = True) -> Dict[str, Any]:
    """Set cache policy for a specific tool."""
    try:
        # Validate policy
        try:
            cache_policy = CachePolicy(policy.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid policy '{policy}'. Must be one of: {[p.value for p in CachePolicy]}"
            }
        
        # Get cache manager and set policy
        cache_manager = get_cache_manager()
        cache_manager.set_tool_policy(
            tool_name=tool_name,
            policy=cache_policy,
            ttl=ttl,
            cache_enabled=enabled
        )
        
        return {
            "success": True,
            "message": f"Cache policy set for {tool_name}",
            "data": {
                "tool_name": tool_name,
                "policy": policy,
                "ttl": ttl,
                "enabled": enabled
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to set tool policy: {str(e)}"
        }


def cache_invalidate_tool_command(tool_name: str) -> Dict[str, Any]:
    """Invalidate cache for a specific tool."""
    try:
        cache_manager = get_cache_manager()
        cache_manager.invalidate_tool(tool_name)
        
        return {
            "success": True,
            "message": f"Cache invalidated for {tool_name}",
            "data": {"tool_name": tool_name}
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to invalidate cache: {str(e)}"
        }


def cache_test_command(iterations: int = 10) -> Dict[str, Any]:
    """Test cache performance with sample operations."""
    try:
        from ..tools.core_tools.calculator_tool import CalculatorTool
        
        calc_tool = CalculatorTool()
        cache_manager = get_cache_manager()
        
        # Clear cache for clean test
        cache_manager.clear()
        
        # Test operations
        operations = [
            "calculate: 2 + 2",
            "calculate: 5 * 5", 
            "calculate: 2 + 2",     # Duplicate
            "calculate: sqrt(16)",
            "calculate: 5 * 5",     # Duplicate
            "calculate: 2 + 2",     # Duplicate
        ]
        
        results = []
        for i in range(iterations):
            for op in operations:
                result = calc_tool.execute_with_cache(op)
                from_cache = result.get('metadata', {}).get('cache', {}).get('from_cache', False)
                results.append({"operation": op, "from_cache": from_cache})
        
        # Get final stats
        stats = cache_manager.get_stats()
        
        return {
            "success": True,
            "message": f"Cache test completed with {len(results)} operations",
            "data": {
                "test_results": results[-10:],  # Show last 10 results
                "performance": {
                    "hit_rate": f"{stats['metrics']['hit_rate']:.1f}%",
                    "total_operations": stats['metrics']['hits'] + stats['metrics']['misses'],
                    "cache_entries": stats['size']
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Cache test failed: {str(e)}"
        }


def list_available_tools_command() -> Dict[str, Any]:
    """List all available tools for cache policy configuration."""
    try:
        registry = get_tool_registry()
        tools = registry.list_tools()
        
        tool_info = []
        for tool_name in tools:
            try:
                tool_instance = registry.get_tool(tool_name)
                if hasattr(tool_instance, 'get_cache_stats'):
                    cache_stats = tool_instance.get_cache_stats()
                    tool_info.append({
                        "name": tool_name,
                        "cache_enabled": cache_stats.get("cache_enabled", False),
                        "cache_policy": cache_stats.get("cache_policy", "unknown"),
                        "custom_ttl": cache_stats.get("custom_ttl", None)
                    })
                else:
                    tool_info.append({
                        "name": tool_name,
                        "cache_enabled": False,
                        "cache_policy": "not_supported",
                        "custom_ttl": None
                    })
            except:
                tool_info.append({
                    "name": tool_name,
                    "cache_enabled": "unknown",
                    "cache_policy": "unknown",
                    "custom_ttl": "unknown"
                })
        
        return {
            "success": True,
            "data": {
                "total_tools": len(tool_info),
                "cache_enabled_tools": len([t for t in tool_info if t["cache_enabled"] is True]),
                "tools": tool_info
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tools: {str(e)}"
        }


# Command mapping for CLI integration
CACHE_COMMANDS = {
    "cache_stats": cache_stats_command,
    "cache_clear": cache_clear_command,
    "cache_cleanup": cache_cleanup_command,
    "cache_configure": cache_configure_command,
    "cache_tool_policy": cache_tool_policy_command,
    "cache_invalidate_tool": cache_invalidate_tool_command,
    "cache_test": cache_test_command,
    "list_tools": list_available_tools_command
}


def handle_cache_command(command: str, **kwargs) -> Dict[str, Any]:
    """Handle cache-related CLI commands."""
    if command not in CACHE_COMMANDS:
        return {
            "success": False,
            "error": f"Unknown cache command: {command}",
            "available_commands": list(CACHE_COMMANDS.keys())
        }
    
    try:
        return CACHE_COMMANDS[command](**kwargs)
    except Exception as e:
        return {
            "success": False,
            "error": f"Command execution failed: {str(e)}"
        }