"""
Configuration for connecting to the Unified MCP Server
"""

import os
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Base server configuration
BASE_MCP_SERVER_CONFIG = {
    "name": "metis_dynamic",
    "url": os.getenv("MCP_UNIFIED_SERVER_URL", "https://metismcp-server.onrender.com"),
    "tools": [],  # Will be populated dynamically
    "last_updated": None,
    "cache_duration": 300  # 5 minutes cache
}

# Cache for dynamic configuration
_config_cache = {}
_last_fetch = {}


async def fetch_server_tools(server_url: str) -> List[Dict[str, Any]]:
    """Fetch available tools from MCP server dynamically"""
    try:
        async with aiohttp.ClientSession() as session:
            # First check health
            async with session.get(f"{server_url}/health", timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"Server health check failed: {response.status}")
                    return []
            
            # Get resources (tools)
            async with session.get(f"{server_url}/resources", timeout=10) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch resources: {response.status}")
                    return []
                
                data = await response.json()
                resources = data.get('resources', [])
                
                # Convert resources to tool format
                tools = []
                for resource in resources:
                    tool_name = resource.get('name', '').lower().replace(' ', '_')
                    tool_endpoint = f"/tools/{tool_name.lower()}"
                    
                    # Build tool configuration
                    tool_config = {
                        "name": tool_name,
                        "endpoint": tool_endpoint,
                        "description": resource.get('description', ''),
                        "parameters": {
                            "task": {
                                "type": "string", 
                                "required": True, 
                                "description": "Task description for the tool"
                            }
                        }
                    }
                    
                    # Add kwargs parameter if needed (for tools that require it)
                    if any(param in tool_name for param in ['project', 'git', 'dependency', 'scaffolding']):
                        tool_config["parameters"]["kwargs"] = {
                            "type": "object",
                            "required": False,
                            "description": "Additional parameters"
                        }
                    
                    tools.append(tool_config)
                
                logger.info(f"Discovered {len(tools)} tools from server: {[t['name'] for t in tools]}")
                return tools
                
    except Exception as e:
        logger.error(f"Failed to fetch tools from {server_url}: {e}")
        return []


def is_cache_valid(server_url: str) -> bool:
    """Check if cached configuration is still valid"""
    if server_url not in _last_fetch:
        return False
    
    last_fetch_time = _last_fetch[server_url]
    cache_duration = BASE_MCP_SERVER_CONFIG["cache_duration"]
    
    return (datetime.now() - last_fetch_time).total_seconds() < cache_duration


async def get_dynamic_config(server_url: Optional[str] = None) -> Dict[str, Any]:
    """Get dynamic configuration with caching"""
    if server_url is None:
        server_url = BASE_MCP_SERVER_CONFIG["url"]
    
    # Check cache first
    if server_url in _config_cache and is_cache_valid(server_url):
        logger.debug(f"Using cached configuration for {server_url}")
        return _config_cache[server_url]
    
    # Fetch fresh configuration
    logger.info(f"Fetching fresh configuration from {server_url}")
    tools = await fetch_server_tools(server_url)
    
    # Build configuration
    config = BASE_MCP_SERVER_CONFIG.copy()
    config["url"] = server_url
    config["tools"] = tools
    config["last_updated"] = datetime.now().isoformat()
    
    # Update cache
    _config_cache[server_url] = config
    _last_fetch[server_url] = datetime.now()
    
    return config


def get_config_sync(server_url: Optional[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for getting dynamic configuration"""
    try:
        # Try to use existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, we can't use asyncio.run()
            # Return cached config or fallback
            if server_url is None:
                server_url = BASE_MCP_SERVER_CONFIG["url"]
            
            if server_url in _config_cache and is_cache_valid(server_url):
                return _config_cache[server_url]
            else:
                logger.warning("No valid cache available in async context, using fallback")
                return get_fallback_config(server_url)
        else:
            # We can create a new event loop
            return asyncio.run(get_dynamic_config(server_url))
    except Exception as e:
        logger.error(f"Failed to get dynamic config: {e}")
        return get_fallback_config(server_url)


def get_fallback_config(server_url: Optional[str] = None) -> Dict[str, Any]:
    """Fallback configuration with common Metis tools"""
    if server_url is None:
        server_url = BASE_MCP_SERVER_CONFIG["url"]
    
    fallback_tools = [
        {
            "name": "code_analysis",
            "endpoint": "/tools/codeanalysistool",
            "description": "Analyze code structure, patterns, and dependencies",
            "parameters": {
                "task": {"type": "string", "required": True, "description": "Analysis task description"}
            }
        },
        {
            "name": "project_context",
            "endpoint": "/tools/projectcontexttool",
            "description": "Analyze project structure and context",
            "parameters": {
                "task": {"type": "string", "required": True, "description": "Context analysis task"},
                "kwargs": {"type": "object", "required": False, "description": "Additional parameters"}
            }
        },
        {
            "name": "git_integration",
            "endpoint": "/tools/gitintegrationtool",
            "description": "Git operations and analysis",
            "parameters": {
                "task": {"type": "string", "required": True, "description": "Git task description"},
                "kwargs": {"type": "object", "required": False, "description": "Additional parameters"}
            }
        },
        {
            "name": "dependency_manager",
            "endpoint": "/tools/dependencymanagertool",
            "description": "Manage project dependencies",
            "parameters": {
                "task": {"type": "string", "required": True, "description": "Dependency task description"},
                "kwargs": {"type": "object", "required": False, "description": "Additional parameters"}
            }
        },
        {
            "name": "project_scaffolding",
            "endpoint": "/tools/projectscaffoldingtool",
            "description": "Generate project templates and scaffolding",
            "parameters": {
                "task": {"type": "string", "required": True, "description": "Scaffolding task description"},
                "kwargs": {"type": "object", "required": False, "description": "Additional parameters"}
            }
        },
        {
            "name": "context_aware_generator",
            "endpoint": "/tools/contextawarecodegenerator",
            "description": "Generate context-aware code",
            "parameters": {
                "task": {"type": "string", "required": True, "description": "Code generation task description"}
            }
        }
    ]
    
    config = BASE_MCP_SERVER_CONFIG.copy()
    config["url"] = server_url
    config["tools"] = fallback_tools
    config["last_updated"] = datetime.now().isoformat()
    config["fallback"] = True
    
    return config

# Production server URLs
PRODUCTION_SERVERS = {
    "render": "https://metismcp-server.onrender.com",
    "heroku": "https://your-app.herokuapp.com", 
    "railway": "https://your-app.railway.app",
    "fly": "https://your-app.fly.dev"
}

def get_unified_server_config(environment: str = "local") -> Dict[str, Any]:
    """
    Get unified server configuration for different environments
    
    Args:
        environment: 'local', 'render', 'heroku', 'railway', 'fly', or custom URL
    
    Returns:
        Server configuration dictionary
    """
    config = UNIFIED_MCP_SERVER_CONFIG.copy()
    
    if environment == "local":
        config["url"] = "http://localhost:8000"
    elif environment in PRODUCTION_SERVERS:
        config["url"] = PRODUCTION_SERVERS[environment]
    elif environment.startswith("http"):
        # Custom URL provided
        config["url"] = environment
    else:
        # Default to environment variable or local
        config["url"] = os.getenv("MCP_UNIFIED_SERVER_URL", "http://localhost:8000")
    
    return config


def get_unified_server_config() -> Dict[str, Any]:
    """Get the unified MCP server configuration (dynamic)"""
    return get_config_sync()


def get_tool_mapping() -> Dict[str, str]:
    """Get mapping of legacy tool names to MCP tool names (dynamic)"""
    try:
        config = get_config_sync()
        tools = config.get('tools', [])
        
        # Build dynamic mapping
        mapping = {}
        
        for tool in tools:
            tool_name = tool.get('name', '')
            
            # Add direct mapping
            mapping[tool_name] = tool_name
            
            # Add class name mappings (convert snake_case to CamelCase)
            class_name = ''.join(word.capitalize() for word in tool_name.split('_'))
            if not class_name.endswith('Tool'):
                class_name += 'Tool'
            mapping[class_name] = tool_name
            
            # Add specific legacy mappings
            legacy_mappings = {
                'code_analysis': ['CodeAnalysisTool', 'CodeAnalysis'],
                'project_context': ['ProjectContextTool', 'ProjectContext'],
                'git_integration': ['GitIntegrationTool', 'GitIntegration'],
                'dependency_manager': ['DependencyManagerTool', 'DependencyManager'],
                'project_scaffolding': ['ProjectScaffoldingTool', 'ProjectScaffolding'],
                'context_aware_generator': ['ContextAwareCodeGenerator', 'ContextAwareGenerator']
            }
            
            if tool_name in legacy_mappings:
                for legacy_name in legacy_mappings[tool_name]:
                    mapping[legacy_name] = tool_name
        
        logger.debug(f"Built dynamic tool mapping with {len(mapping)} entries")
        return mapping
        
    except Exception as e:
        logger.error(f"Failed to build dynamic tool mapping: {e}")
        # Fallback to static mapping
        return {
            "CodeAnalysisTool": "code_analysis",
            "ProjectContextTool": "project_context", 
            "GitIntegrationTool": "git_integration",
            "DependencyManagerTool": "dependency_manager",
            "ProjectScaffoldingTool": "project_scaffolding",
            "ContextAwareCodeGenerator": "context_aware_generator",
            "code_analysis": "code_analysis",
            "project_context": "project_context",
            "git_integration": "git_integration", 
            "dependency_manager": "dependency_manager",
            "project_scaffolding": "project_scaffolding",
            "context_aware_generator": "context_aware_generator"
        }


def clear_config_cache():
    """Clear the configuration cache to force fresh fetch"""
    global _config_cache, _last_fetch
    _config_cache.clear()
    _last_fetch.clear()
    logger.info("Configuration cache cleared")


def get_cache_status() -> Dict[str, Any]:
    """Get current cache status for debugging"""
    status = {
        "cached_servers": list(_config_cache.keys()),
        "cache_entries": len(_config_cache),
        "last_fetch_times": {}
    }
    
    for server_url, fetch_time in _last_fetch.items():
        status["last_fetch_times"][server_url] = {
            "time": fetch_time.isoformat(),
            "age_seconds": (datetime.now() - fetch_time).total_seconds(),
            "valid": is_cache_valid(server_url)
        }
    
    return status


async def test_server_connection(server_url: Optional[str] = None) -> Dict[str, Any]:
    """Test connection to MCP server and return status"""
    if server_url is None:
        server_url = BASE_MCP_SERVER_CONFIG["url"]
    
    result = {
        "server_url": server_url,
        "healthy": False,
        "tools_count": 0,
        "tools": [],
        "error": None,
        "response_time": None
    }
    
    start_time = datetime.now()
    
    try:
        tools = await fetch_server_tools(server_url)
        result["healthy"] = True
        result["tools_count"] = len(tools)
        result["tools"] = [tool.get('name', '') for tool in tools]
        result["response_time"] = (datetime.now() - start_time).total_seconds()
        
    except Exception as e:
        result["error"] = str(e)
        result["response_time"] = (datetime.now() - start_time).total_seconds()
    
    return result


def get_deployment_instructions() -> Dict[str, str]:
    """
    Get deployment instructions for different platforms
    
    Returns:
        Dictionary with deployment instructions for each platform
    """
    return {
        "render": """
        1. Create new Web Service on Render
        2. Connect your GitHub repository
        3. Set build command: pip install -r requirements.txt
        4. Set start command: python server.py
        5. Add environment variables:
           - GROQ_API_KEY=your_groq_api_key
           - GOOGLE_API_KEY=your_google_api_key (optional)
           - GOOGLE_CSE_ID=your_google_cse_id (optional)
        6. Deploy and get your URL
        """,
        
        "heroku": """
        1. Create new Heroku app
        2. Connect GitHub repository or use Heroku CLI
        3. Add environment variables in Settings > Config Vars:
           - GROQ_API_KEY=your_groq_api_key
           - GOOGLE_API_KEY=your_google_api_key (optional)
           - GOOGLE_CSE_ID=your_google_cse_id (optional)
        4. Deploy from GitHub or push to Heroku git
        """,
        
        "railway": """
        1. Create new project on Railway
        2. Connect GitHub repository
        3. Add environment variables:
           - GROQ_API_KEY=your_groq_api_key
           - GOOGLE_API_KEY=your_google_api_key (optional)
           - GOOGLE_CSE_ID=your_google_cse_id (optional)
        4. Deploy automatically
        """,
        
        "docker": """
        1. Build image: docker build -t metis-mcp-server .
        2. Run container: 
           docker run -p 8000:8000 \\
             -e GROQ_API_KEY=your_key \\
             -e GOOGLE_API_KEY=your_key \\
             -e GOOGLE_CSE_ID=your_id \\
             metis-mcp-server
        """
    }

# Environment-specific configurations
ENVIRONMENT_CONFIGS = {
    "development": {
        "url": "http://localhost:8000",
        "timeout": 30,
        "retry_attempts": 3,
        "log_level": "DEBUG"
    },
    "staging": {
        "url": os.getenv("MCP_STAGING_URL", "https://staging-mcp.example.com"),
        "timeout": 60,
        "retry_attempts": 5,
        "log_level": "INFO"
    },
    "production": {
        "url": os.getenv("MCP_PRODUCTION_URL", "https://mcp.example.com"),
        "timeout": 120,
        "retry_attempts": 10,
        "log_level": "WARNING"
    }
}
