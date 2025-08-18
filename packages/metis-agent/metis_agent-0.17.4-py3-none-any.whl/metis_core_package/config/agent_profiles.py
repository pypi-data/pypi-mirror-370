"""
Agent Profile System for Metis Agent.

Provides YAML-based configuration profiles for different agent types with
validation, inheritance, and dynamic configuration management.
"""
import os
import yaml
import time
import logging
from typing import Dict, Any, List, Optional, Union, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from copy import deepcopy
import threading

logger = logging.getLogger(__name__)


@dataclass
class ToolConfig:
    """Configuration for agent tools."""
    enabled: List[str]
    disabled: List[str] = None
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.disabled is None:
            self.disabled = []
        if self.config is None:
            self.config = {}


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    provider: str
    model: str
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    custom_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_config is None:
            self.custom_config = {}


@dataclass
class MemoryConfig:
    """Configuration for agent memory."""
    type: str = "sqlite"
    path: Optional[str] = None
    max_context_tokens: int = 4000
    retention_days: int = 30
    isolation: bool = True
    cache_size: int = 1000
    specialized_memory: Optional[str] = None
    backup_enabled: bool = False
    
    def validate(self) -> List[str]:
        """Validate memory configuration."""
        errors = []
        
        if self.type not in ["sqlite", "titans", "redis", "memory"]:
            errors.append(f"Invalid memory type: {self.type}")
            
        if self.max_context_tokens <= 0:
            errors.append("max_context_tokens must be positive")
            
        if self.retention_days <= 0:
            errors.append("retention_days must be positive")
            
        return errors


@dataclass
class PerformanceConfig:
    """Configuration for agent performance settings."""
    cache_enabled: bool = True
    cache_ttl: int = 3600
    memory_monitoring: bool = True
    max_parallel_tools: int = 3
    timeout_seconds: int = 30
    retry_attempts: int = 3
    lazy_loading: bool = True
    
    def validate(self) -> List[str]:
        """Validate performance configuration."""
        errors = []
        
        if self.cache_ttl <= 0:
            errors.append("cache_ttl must be positive")
            
        if self.max_parallel_tools <= 0:
            errors.append("max_parallel_tools must be positive")
            
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
            
        return errors


@dataclass
class PermissionsConfig:
    """Configuration for agent permissions."""
    file_access: List[str] = None
    network_access: bool = True
    system_commands: List[str] = None
    restricted_paths: List[str] = None
    max_file_size_mb: int = 100
    
    def __post_init__(self):
        if self.file_access is None:
            self.file_access = []
        if self.system_commands is None:
            self.system_commands = []
        if self.restricted_paths is None:
            self.restricted_paths = []


@dataclass
class SharedResourcesConfig:
    """Configuration for shared resources access."""
    knowledge_base: bool = True
    tool_registry: bool = True
    cache_layer: bool = False
    memory_sharing: bool = False
    config_sharing: bool = True


class AgentProfile:
    """
    Agent profile with YAML-based configuration and validation.
    """
    
    def __init__(self, 
                 name: str,
                 description: str = "",
                 agent_id: Optional[str] = None,
                 llm_config: Union[LLMConfig, Dict[str, Any]] = None,
                 tools: Union[ToolConfig, Dict[str, Any]] = None,
                 memory_config: Union[MemoryConfig, Dict[str, Any]] = None,
                 performance: Union[PerformanceConfig, Dict[str, Any]] = None,
                 permissions: Union[PermissionsConfig, Dict[str, Any]] = None,
                 shared_resources: Union[SharedResourcesConfig, Dict[str, Any]] = None,
                 custom_config: Dict[str, Any] = None,
                 base_profile: Optional[str] = None):
        """
        Initialize agent profile.
        
        Args:
            name: Agent name
            description: Agent description  
            agent_id: Optional agent ID
            llm_config: LLM configuration
            tools: Tool configuration
            memory_config: Memory configuration
            performance: Performance configuration
            permissions: Permissions configuration
            shared_resources: Shared resources configuration
            custom_config: Custom configuration dictionary
            base_profile: Base profile to inherit from
        """
        self.name = name
        self.description = description
        self.agent_id = agent_id
        self.base_profile = base_profile
        self.custom_config = custom_config or {}
        self.created_at = time.time()
        self.version = "1.0"
        
        # Convert dictionaries to dataclasses if needed
        if isinstance(llm_config, dict):
            self.llm_config = LLMConfig(**llm_config)
        else:
            self.llm_config = llm_config or LLMConfig(provider="groq", model="llama-3.1-70b-versatile")
            
        if isinstance(tools, dict):
            self.tools = ToolConfig(**tools)
        else:
            self.tools = tools or ToolConfig(enabled=[])
            
        if isinstance(memory_config, dict):
            self.memory_config = MemoryConfig(**memory_config)
        else:
            self.memory_config = memory_config or MemoryConfig()
            
        if isinstance(performance, dict):
            self.performance = PerformanceConfig(**performance)
        else:
            self.performance = performance or PerformanceConfig()
            
        if isinstance(permissions, dict):
            self.permissions = PermissionsConfig(**permissions)
        else:
            self.permissions = permissions or PermissionsConfig()
            
        if isinstance(shared_resources, dict):
            self.shared_resources = SharedResourcesConfig(**shared_resources)
        else:
            self.shared_resources = shared_resources or SharedResourcesConfig()
    
    @classmethod
    def from_yaml(cls, profile_path: str) -> 'AgentProfile':
        """
        Load profile from YAML file.
        
        Args:
            profile_path: Path to YAML profile file
            
        Returns:
            AgentProfile instance
            
        Raises:
            FileNotFoundError: If profile file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            ValueError: If profile format is invalid
        """
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile file not found: {profile_path}")
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'agent_profile' not in data:
                raise ValueError("Invalid profile format: missing 'agent_profile' section")
            
            profile_data = data['agent_profile']
            
            # Extract configuration sections
            name = profile_data.get('name', 'Unknown Agent')
            description = profile_data.get('description', '')
            agent_id = profile_data.get('agent_id')
            base_profile = profile_data.get('base_profile')
            
            # Create profile with configurations
            profile = cls(
                name=name,
                description=description,
                agent_id=agent_id,
                llm_config=profile_data.get('llm_config', {}),
                tools=profile_data.get('tools', {}),
                memory_config=profile_data.get('memory_config', {}),
                performance=profile_data.get('performance', {}),
                permissions=profile_data.get('permissions', {}),
                shared_resources=profile_data.get('shared_resources', {}),
                custom_config=profile_data.get('custom_config', {}),
                base_profile=base_profile
            )
            
            logger.info(f"Loaded agent profile: {name} from {profile_path}")
            return profile
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse YAML file {profile_path}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load profile from {profile_path}: {e}")
    
    def to_yaml(self, output_path: str):
        """
        Save profile to YAML file.
        
        Args:
            output_path: Path to save YAML file
        """
        profile_data = {
            'agent_profile': {
                'name': self.name,
                'description': self.description,
                'agent_id': self.agent_id,
                'base_profile': self.base_profile,
                'version': self.version,
                'created_at': self.created_at,
                
                'llm_config': asdict(self.llm_config),
                'tools': {
                    'enabled': self.tools.enabled,
                    'disabled': self.tools.disabled,
                    'config': self.tools.config
                },
                'memory_config': asdict(self.memory_config),
                'performance': asdict(self.performance),
                'permissions': asdict(self.permissions),
                'shared_resources': asdict(self.shared_resources),
                'custom_config': self.custom_config
            }
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(profile_data, f, default_flow_style=False, indent=2)
        
        logger.info(f"Saved agent profile: {self.name} to {output_path}")
    
    def validate(self) -> List[str]:
        """
        Validate profile configuration.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate required fields
        if not self.name or not self.name.strip():
            errors.append("Agent name is required")
        
        # Validate LLM configuration
        if not self.llm_config.provider:
            errors.append("LLM provider is required")
        if not self.llm_config.model:
            errors.append("LLM model is required")
        if not (0.0 <= self.llm_config.temperature <= 2.0):
            errors.append("LLM temperature must be between 0.0 and 2.0")
        
        # Validate memory configuration
        errors.extend(self.memory_config.validate())
        
        # Validate performance configuration
        errors.extend(self.performance.validate())
        
        # Validate tools configuration
        if not self.tools.enabled:
            errors.append("At least one tool must be enabled")
        
        # Check for tool conflicts
        enabled_set = set(self.tools.enabled)
        disabled_set = set(self.tools.disabled)
        conflicts = enabled_set & disabled_set
        if conflicts:
            errors.append(f"Tools cannot be both enabled and disabled: {conflicts}")
        
        return errors
    
    def to_agent_config(self) -> Dict[str, Any]:
        """
        Convert profile to agent initialization configuration.
        
        Returns:
            Dictionary suitable for agent initialization
        """
        config = {
            'name': self.name,
            'description': self.description,
            'agent_id': self.agent_id,
            
            # LLM configuration
            'llm_provider': self.llm_config.provider,
            'llm_model': self.llm_config.model,
            'llm_temperature': self.llm_config.temperature,
            'llm_max_tokens': self.llm_config.max_tokens,
            'llm_timeout': self.llm_config.timeout,
            
            # Tools configuration
            'enabled_tools': self.tools.enabled,
            'disabled_tools': self.tools.disabled,
            'tool_config': self.tools.config,
            
            # Memory configuration
            'memory_type': self.memory_config.type,
            'memory_path': self.memory_config.path,
            'max_context_tokens': self.memory_config.max_context_tokens,
            'memory_retention_days': self.memory_config.retention_days,
            'memory_isolation': self.memory_config.isolation,
            
            # Performance configuration
            'cache_enabled': self.performance.cache_enabled,
            'cache_ttl': self.performance.cache_ttl,
            'memory_monitoring': self.performance.memory_monitoring,
            'max_parallel_tools': self.performance.max_parallel_tools,
            'timeout_seconds': self.performance.timeout_seconds,
            
            # Permissions and security
            'file_access_paths': self.permissions.file_access,
            'network_access': self.permissions.network_access,
            'allowed_commands': self.permissions.system_commands,
            'restricted_paths': self.permissions.restricted_paths,
            
            # Shared resources
            'shared_knowledge_enabled': self.shared_resources.knowledge_base,
            'shared_tools_enabled': self.shared_resources.tool_registry,
            'shared_cache_enabled': self.shared_resources.cache_layer,
            
            # Custom configuration
            'custom_config': self.custom_config
        }
        
        return config
    
    def merge_with_base(self, base_profile: 'AgentProfile') -> 'AgentProfile':
        """
        Merge this profile with a base profile (inheritance).
        
        Args:
            base_profile: Base profile to inherit from
            
        Returns:
            New merged profile
        """
        # Start with a copy of the base profile
        merged_profile = AgentProfile(
            name=self.name or base_profile.name,
            description=self.description or base_profile.description,
            agent_id=self.agent_id or base_profile.agent_id,
            base_profile=base_profile.name,
            custom_config=deepcopy(base_profile.custom_config)
        )
        
        # Merge LLM config
        merged_profile.llm_config = deepcopy(base_profile.llm_config)
        if self.llm_config:
            # Override with current profile's LLM settings
            if self.llm_config.provider != "groq":  # Only override if explicitly set
                merged_profile.llm_config.provider = self.llm_config.provider
            if self.llm_config.model != "llama-3.1-70b-versatile":  # Only override if explicitly set
                merged_profile.llm_config.model = self.llm_config.model
            merged_profile.llm_config.temperature = self.llm_config.temperature
            merged_profile.llm_config.max_tokens = self.llm_config.max_tokens
            merged_profile.llm_config.timeout = self.llm_config.timeout
        
        # Merge tools (start with base tools, add current enabled, remove current disabled)
        base_enabled = set(base_profile.tools.enabled) if base_profile.tools.enabled else set()
        current_enabled = set(self.tools.enabled) if self.tools.enabled else set()
        current_disabled = set(self.tools.disabled) if self.tools.disabled else set()
        
        # Final enabled tools = (base enabled + current enabled) - current disabled
        final_enabled = (base_enabled | current_enabled) - current_disabled
        merged_profile.tools = ToolConfig(
            enabled=list(final_enabled),
            disabled=self.tools.disabled or [],
            config={**base_profile.tools.config, **self.tools.config}
        )
        
        # Merge memory config (current overrides base)
        merged_profile.memory_config = deepcopy(base_profile.memory_config)
        if self.memory_config:
            for attr in ['type', 'max_context_tokens', 'retention_days', 'specialized_memory']:
                if hasattr(self.memory_config, attr) and getattr(self.memory_config, attr) is not None:
                    setattr(merged_profile.memory_config, attr, getattr(self.memory_config, attr))
        
        # Merge performance config (current overrides base)
        merged_profile.performance = deepcopy(base_profile.performance)
        if self.performance:
            for attr in ['cache_enabled', 'cache_ttl', 'memory_monitoring', 'max_parallel_tools', 'timeout_seconds']:
                if hasattr(self.performance, attr) and getattr(self.performance, attr) is not None:
                    setattr(merged_profile.performance, attr, getattr(self.performance, attr))
        
        # Merge permissions (current overrides base)
        merged_profile.permissions = deepcopy(base_profile.permissions)
        if self.permissions:
            for attr in ['file_access', 'network_access', 'system_commands', 'max_file_size_mb']:
                if hasattr(self.permissions, attr) and getattr(self.permissions, attr) is not None:
                    setattr(merged_profile.permissions, attr, getattr(self.permissions, attr))
        
        # Merge shared resources (current overrides base)
        merged_profile.shared_resources = deepcopy(base_profile.shared_resources)
        if self.shared_resources:
            for attr in ['knowledge_base', 'tool_registry', 'cache_layer', 'memory_sharing']:
                if hasattr(self.shared_resources, attr) and getattr(self.shared_resources, attr) is not None:
                    setattr(merged_profile.shared_resources, attr, getattr(self.shared_resources, attr))
        
        # Merge custom config
        merged_profile.custom_config.update(self.custom_config)
        
        return merged_profile
    
    def clone(self, new_name: str, new_agent_id: Optional[str] = None) -> 'AgentProfile':
        """
        Clone profile with new name and ID.
        
        Args:
            new_name: New profile name
            new_agent_id: New agent ID
            
        Returns:
            Cloned profile
        """
        cloned = AgentProfile(
            name=new_name,
            description=self.description,
            agent_id=new_agent_id,
            llm_config=deepcopy(self.llm_config),
            tools=deepcopy(self.tools),
            memory_config=deepcopy(self.memory_config),
            performance=deepcopy(self.performance),
            permissions=deepcopy(self.permissions),
            shared_resources=deepcopy(self.shared_resources),
            custom_config=deepcopy(self.custom_config),
            base_profile=self.base_profile
        )
        
        cloned.created_at = time.time()
        return cloned


class ProfileManager:
    """
    Manages agent profiles with caching, validation, and inheritance support.
    """
    
    def __init__(self, profiles_directory: str = "profiles"):
        """
        Initialize profile manager.
        
        Args:
            profiles_directory: Directory containing profile YAML files
        """
        self.profiles_directory = Path(profiles_directory)
        self.profiles_directory.mkdir(exist_ok=True)
        
        # Profile cache
        self._profile_cache: Dict[str, AgentProfile] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_lock = threading.RLock()
        
        # Default profiles
        self._default_profiles: Dict[str, AgentProfile] = {}
        
        # Initialize default profiles
        self._initialize_default_profiles()
        
        logger.info(f"ProfileManager initialized with directory: {self.profiles_directory}")
    
    def load_profile(self, name: str, use_cache: bool = True) -> AgentProfile:
        """
        Load profile by name.
        
        Args:
            name: Profile name
            use_cache: Whether to use cached version if available
            
        Returns:
            AgentProfile instance
            
        Raises:
            FileNotFoundError: If profile doesn't exist
            ValueError: If profile is invalid
        """
        with self._cache_lock:
            # Check cache first
            if use_cache and name in self._profile_cache:
                profile_path = self.profiles_directory / f"{name}.yaml"
                
                # Check if file has been modified
                if profile_path.exists():
                    file_mtime = profile_path.stat().st_mtime
                    cache_time = self._cache_timestamps.get(name, 0)
                    
                    if file_mtime <= cache_time:
                        logger.debug(f"Using cached profile: {name}")
                        return self._profile_cache[name]
            
            # Load from file or use default
            profile = self._load_profile_from_file_or_default(name)
            
            # Handle inheritance if base profile is specified
            if profile.base_profile:
                base_profile = self.load_profile(profile.base_profile)
                profile = profile.merge_with_base(base_profile)
            
            # Validate profile
            errors = profile.validate()
            if errors:
                raise ValueError(f"Profile '{name}' validation failed: {errors}")
            
            # Cache the profile
            self._profile_cache[name] = profile
            self._cache_timestamps[name] = time.time()
            
            logger.info(f"Loaded profile: {name}")
            return profile
    
    def create_profile(self, config: Dict[str, Any], save_to_file: bool = True) -> AgentProfile:
        """
        Create new profile from configuration.
        
        Args:
            config: Profile configuration dictionary
            save_to_file: Whether to save profile to YAML file
            
        Returns:
            Created AgentProfile
        """
        # Extract basic information
        name = config.get('name', 'custom_agent')
        
        # Create profile
        profile = AgentProfile(**config)
        
        # Validate profile
        errors = profile.validate()
        if errors:
            raise ValueError(f"Profile creation failed: {errors}")
        
        # Save to file if requested
        if save_to_file:
            profile_path = self.profiles_directory / f"{name}.yaml"
            profile.to_yaml(str(profile_path))
        
        # Cache the profile
        with self._cache_lock:
            self._profile_cache[name] = profile
            self._cache_timestamps[name] = time.time()
        
        logger.info(f"Created profile: {name}")
        return profile
    
    def save_profile(self, profile: AgentProfile, name: Optional[str] = None):
        """
        Save profile to YAML file.
        
        Args:
            profile: Profile to save
            name: Custom name for file (uses profile.name if None)
        """
        profile_name = name or profile.name
        profile_path = self.profiles_directory / f"{profile_name}.yaml"
        
        profile.to_yaml(str(profile_path))
        
        # Update cache
        with self._cache_lock:
            self._profile_cache[profile_name] = profile
            self._cache_timestamps[profile_name] = time.time()
        
        logger.info(f"Saved profile: {profile_name}")
    
    def list_profiles(self, include_defaults: bool = True) -> List[str]:
        """
        List available profiles.
        
        Args:
            include_defaults: Whether to include default profiles
            
        Returns:
            List of profile names
        """
        profiles = set()
        
        # Add file-based profiles
        for yaml_file in self.profiles_directory.glob("*.yaml"):
            profiles.add(yaml_file.stem)
        
        # Add default profiles
        if include_defaults:
            profiles.update(self._default_profiles.keys())
        
        return sorted(list(profiles))
    
    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile.
        
        Args:
            name: Profile name to delete
            
        Returns:
            True if profile was deleted
        """
        profile_path = self.profiles_directory / f"{name}.yaml"
        
        # Remove from cache
        with self._cache_lock:
            self._profile_cache.pop(name, None)
            self._cache_timestamps.pop(name, None)
        
        # Remove file if it exists
        if profile_path.exists():
            profile_path.unlink()
            logger.info(f"Deleted profile file: {name}")
            return True
        
        # Remove from defaults if it exists
        if name in self._default_profiles:
            del self._default_profiles[name]
            logger.info(f"Deleted default profile: {name}")
            return True
        
        return False
    
    def validate_profile(self, name: str) -> List[str]:
        """
        Validate a profile without loading it into cache.
        
        Args:
            name: Profile name to validate
            
        Returns:
            List of validation errors
        """
        try:
            profile = self._load_profile_from_file_or_default(name)
            return profile.validate()
        except Exception as e:
            return [f"Failed to load profile: {e}"]
    
    def get_profile_info(self, name: str) -> Dict[str, Any]:
        """
        Get profile information without fully loading it.
        
        Args:
            name: Profile name
            
        Returns:
            Profile information dictionary
        """
        profile_path = self.profiles_directory / f"{name}.yaml"
        
        info = {
            'name': name,
            'exists': False,
            'is_default': name in self._default_profiles,
            'file_path': str(profile_path),
            'cached': name in self._profile_cache
        }
        
        if profile_path.exists():
            info['exists'] = True
            stat = profile_path.stat()
            info['file_size'] = stat.st_size
            info['modified_time'] = stat.st_mtime
        
        return info
    
    def clear_cache(self):
        """Clear profile cache."""
        with self._cache_lock:
            self._profile_cache.clear()
            self._cache_timestamps.clear()
        
        logger.info("Cleared profile cache")
    
    def _load_profile_from_file_or_default(self, name: str) -> AgentProfile:
        """Load profile from file or return default profile."""
        profile_path = self.profiles_directory / f"{name}.yaml"
        
        # Try to load from file first
        if profile_path.exists():
            return AgentProfile.from_yaml(str(profile_path))
        
        # Try default profiles
        if name in self._default_profiles:
            return deepcopy(self._default_profiles[name])
        
        raise FileNotFoundError(f"Profile '{name}' not found in {self.profiles_directory} or defaults")
    
    def _initialize_default_profiles(self):
        """Initialize default agent profiles."""
        # General Purpose Agent
        self._default_profiles['general'] = AgentProfile(
            name="General Purpose Agent",
            description="Versatile agent for general tasks and conversations",
            llm_config=LLMConfig(
                provider="groq",
                model="llama-3.1-70b-versatile",
                temperature=0.1
            ),
            tools=ToolConfig(
                enabled=[
                    "CalculatorTool",
                    "EnhancedSearchTool",
                    "ContentGenerationTool",
                    "DataAnalysisTool"
                ]
            ),
            memory_config=MemoryConfig(
                type="sqlite",
                max_context_tokens=4000,
                retention_days=30
            ),
            performance=PerformanceConfig(
                cache_enabled=True,
                memory_monitoring=True,
                max_parallel_tools=3
            )
        )
        
        # Developer Agent
        self._default_profiles['developer'] = AgentProfile(
            name="Developer Agent",
            description="Optimized for software development tasks",
            llm_config=LLMConfig(
                provider="groq",
                model="llama-3.1-70b-versatile",
                temperature=0.1
            ),
            tools=ToolConfig(
                enabled=[
                    "PythonCodeTool",
                    "GitIntegrationTool",
                    "EditTool",
                    "EnhancedSearchTool",
                    "UnitTestGeneratorTool",
                    "E2BCodeSandboxTool"
                ],
                disabled=[
                    "ContentGenerationTool",
                    "WebScraperTool"
                ]
            ),
            memory_config=MemoryConfig(
                type="sqlite",
                max_context_tokens=8000,
                retention_days=30
            ),
            performance=PerformanceConfig(
                cache_enabled=True,
                memory_monitoring=True,
                max_parallel_tools=3
            ),
            permissions=PermissionsConfig(
                file_access=["./src/", "./tests/", "./docs/"],
                network_access=False,
                system_commands=["git", "pytest", "black", "isort"]
            )
        )
        
        # Research Agent
        self._default_profiles['research'] = AgentProfile(
            name="Research Agent",
            description="Specialized for research and information gathering",
            llm_config=LLMConfig(
                provider="openai",
                model="gpt-4",
                temperature=0.3
            ),
            tools=ToolConfig(
                enabled=[
                    "GoogleSearchTool",
                    "WebScraperTool",
                    "DeepResearchTool",
                    "ContentGenerationTool",
                    "DataAnalysisTool",
                    "EnhancedSearchTool"
                ]
            ),
            memory_config=MemoryConfig(
                type="titans",
                max_context_tokens=12000,
                retention_days=90
            ),
            performance=PerformanceConfig(
                cache_enabled=True,
                cache_ttl=7200,  # Longer cache for research
                memory_monitoring=True,
                max_parallel_tools=5
            ),
            permissions=PermissionsConfig(
                network_access=True,
                file_access=["./research/", "./data/"]
            )
        )
        
        logger.info(f"Initialized {len(self._default_profiles)} default profiles")


# Global profile manager instance
_profile_manager: Optional[ProfileManager] = None


def get_profile_manager(profiles_directory: str = "profiles") -> ProfileManager:
    """Get or create global profile manager."""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager(profiles_directory)
    return _profile_manager


def configure_profile_manager(profiles_directory: str = "profiles") -> ProfileManager:
    """Configure global profile manager with custom settings."""
    global _profile_manager
    _profile_manager = ProfileManager(profiles_directory)
    return _profile_manager