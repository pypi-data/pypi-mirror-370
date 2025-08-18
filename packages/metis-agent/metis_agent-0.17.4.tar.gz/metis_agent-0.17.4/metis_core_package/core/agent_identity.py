"""
Agent Identity Module for Metis Agent.

This module provides a sophisticated identity system that gives each agent:
- Unique Agent ID
- Mythical-inspired Agent Name
- Layered System Message Architecture
- Identity Persistence
"""
import uuid
import random
from datetime import datetime
from typing import Optional, Dict, Any


class AgentIdentity:
    """
    Manages agent identity including ID, name, and layered system messages.
    """
    
    # Mythical names for agent identity
    MYTHICAL_NAMES = [
        # Greek Mythology
        "Athena", "Apollo", "Hermes", "Artemis", "Hephaestus", "Demeter",
        "Dionysus", "Ares", "Aphrodite", "Hestia", "Poseidon", "Hades",
        
        # Roman Mythology
        "Minerva", "Mercury", "Diana", "Vulcan", "Ceres", "Bacchus",
        "Mars", "Venus", "Vesta", "Neptune", "Pluto", "Janus",
        
        # Norse Mythology
        "Odin", "Thor", "Freya", "Loki", "Balder", "Frigg",
        "Tyr", "Heimdall", "Vidar", "Vali", "Bragi", "Hodr",
        
        # Celtic Mythology
        "Brigid", "Lugh", "Morrigan", "Dagda", "Nuada", "Dian",
        "Manannan", "Aengus", "Boann", "Epona", "Cernunnos", "Taranis",
        
        # Egyptian Mythology
        "Thoth", "Isis", "Anubis", "Horus", "Bastet", "Sekhmet",
        "Ptah", "Khnum", "Sobek", "Taweret", "Nephthys", "Hathor",
        
        # Wisdom & Knowledge Themed
        "Sage", "Oracle", "Mentor", "Guide", "Scholar", "Scribe",
        "Codex", "Lexicon", "Archive", "Cipher", "Nexus", "Vector"
    ]
    
    def __init__(self, config=None):
        """
        Initialize agent identity.
        
        Args:
            config: Optional AgentConfig instance for persistence
        """
        self.config = config
        self._load_or_generate_identity()
    
    def _load_or_generate_identity(self):
        """Load existing identity from config or generate new one."""
        if self.config and self.config.get("agent_identity"):
            # Load existing identity
            identity_data = self.config.get("agent_identity")
            self.agent_id = identity_data.get("agent_id")
            self.agent_name = identity_data.get("agent_name")
            self.creation_timestamp = identity_data.get("creation_timestamp")
            self.base_system_message = identity_data.get("base_system_message")
            self.custom_system_message = identity_data.get("custom_system_message", "")
            
            # Validate loaded data
            if not self.agent_id or not self.agent_name:
                self._generate_new_identity()
        else:
            # Generate new identity
            self._generate_new_identity()
    
    def _generate_new_identity(self):
        """Generate a new agent identity."""
        self.agent_id = self._generate_agent_id()
        self.agent_name = self._generate_agent_name()
        self.creation_timestamp = datetime.now().isoformat()
        self.base_system_message = self._get_default_base_system_message()
        self.custom_system_message = ""
        
        # Save to config if available
        self._save_to_config()
    
    def _generate_agent_id(self) -> str:
        """Generate a unique agent ID."""
        # Create a short, readable ID based on UUID
        full_uuid = str(uuid.uuid4())
        # Take first 8 characters and make it more readable
        short_id = full_uuid[:8]
        return f"metis-{short_id}"
    
    def _generate_agent_name(self) -> str:
        """Generate a mythical agent name."""
        return random.choice(self.MYTHICAL_NAMES)
    
    def _get_default_base_system_message(self) -> str:
        """Get the default base system message."""
        return f"""You are {self.agent_name}, an advanced AI agent with ID {self.agent_id}.

You are an intelligent, capable, and helpful assistant designed to assist users with a wide variety of tasks including:
- Code generation, analysis, and debugging
- Research and information gathering
- Content creation and writing
- Project planning and management
- Problem-solving and decision support
- Technical documentation and explanations

Your core principles:
- Be accurate, helpful, and honest
- Provide clear, practical solutions
- Ask clarifying questions when needed
- Admit when you don't know something
- Focus on being genuinely useful to the user

## TOOL USAGE STRATEGY

You have access to various specialized tools that you should use strategically to provide higher quality responses:

**For Code Generation Tasks:**
1. **CodingTool**: Use this to validate, format, analyze, and debug code you generate
   - After generating code, validate it with CodingTool to ensure syntax correctness
   - Use it to format code for better readability
   - Analyze code complexity and suggest optimizations
   - Debug potential issues before presenting to users

2. **GoogleSearchTool**: Research current best practices, libraries, and solutions
   - Search for latest documentation and examples
   - Find current best practices for the technology stack
   - Research libraries and frameworks that could help

3. **ContentGenerationTool**: Generate comprehensive documentation and comments
   - Create detailed code documentation
   - Generate README files and usage examples
   - Create comprehensive code comments

**Tool Usage Principles:**
- Use tools to ENHANCE your responses, not replace your reasoning
- Combine multiple tools when beneficial (e.g., search + validate + document)
- Always validate generated code with CodingTool before presenting
- Use tools to provide more accurate, up-to-date, and comprehensive solutions
- Tools are stateless - use them to process and improve your outputs

**Example Workflow for Code Generation:**
1. Understand the user's requirements
2. Research best practices (GoogleSearchTool if needed)
3. Generate the initial code solution
4. Validate and format the code (CodingTool)
5. Create documentation (ContentGenerationTool if needed)
6. Present the complete, validated solution

Remember: Tools help you deliver higher quality, more reliable solutions. Use them strategically to exceed user expectations."""
    
    def get_full_system_message(self) -> str:
        """
        Compose the full system message from all layers.
        
        Returns:
            Complete system message combining all layers
        """
        layers = []
        
        # Layer 1: Base system message (identity + core capabilities)
        if self.base_system_message:
            layers.append(self.base_system_message.strip())
        
        # Layer 2: Custom system message (user-defined personality/role)
        if self.custom_system_message and self.custom_system_message.strip():
            layers.append(self.custom_system_message.strip())
        
        # Combine layers with proper spacing
        return "\n\n".join(layers)
    
    def update_name(self, name: str):
        """
        Update the agent name.
        
        Args:
            name: New agent name
        """
        old_name = self.agent_name
        self.agent_name = name.strip()
        
        # Update base system message to reflect new name
        if self.base_system_message:
            self.base_system_message = self.base_system_message.replace(
                f"You are {old_name},", 
                f"You are {self.agent_name},"
            )
        
        self._save_to_config()
    
    def update_custom_system_message(self, message: str):
        """
        Update the custom system message layer.
        
        Args:
            message: New custom system message
        """
        self.custom_system_message = message.strip()
        self._save_to_config()
    
    def update_base_system_message(self, message: str):
        """
        Update the base system message layer.
        
        Args:
            message: New base system message
        """
        self.base_system_message = message.strip()
        self._save_to_config()
    
    def regenerate_identity(self):
        """
        Generate a completely new identity (new ID and name).
        Preserves custom system message.
        """
        custom_msg = self.custom_system_message  # Preserve custom message
        self._generate_new_identity()
        self.custom_system_message = custom_msg  # Restore custom message
        self._save_to_config()
    
    def get_identity_info(self) -> Dict[str, Any]:
        """
        Get complete identity information.
        
        Returns:
            Dictionary with all identity data
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "creation_timestamp": self.creation_timestamp,
            "base_system_message": self.base_system_message,
            "custom_system_message": self.custom_system_message,
            "full_system_message": self.get_full_system_message()
        }
    
    def _save_to_config(self):
        """Save identity data to config."""
        if self.config:
            identity_data = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "creation_timestamp": self.creation_timestamp,
                "base_system_message": self.base_system_message,
                "custom_system_message": self.custom_system_message
            }
            self.config.set("agent_identity", identity_data)
    
    def __str__(self) -> str:
        """String representation of the agent identity."""
        return f"Agent {self.agent_name} (ID: {self.agent_id})"
    
    def __repr__(self) -> str:
        """Detailed representation of the agent identity."""
        return f"AgentIdentity(id='{self.agent_id}', name='{self.agent_name}', created='{self.creation_timestamp}')"


def create_agent_identity(config=None) -> AgentIdentity:
    """
    Factory function to create an AgentIdentity instance.
    
    Args:
        config: Optional AgentConfig instance
        
    Returns:
        AgentIdentity instance
    """
    return AgentIdentity(config=config)
