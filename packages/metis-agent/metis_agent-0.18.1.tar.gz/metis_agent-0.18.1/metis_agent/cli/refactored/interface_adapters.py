"""
Interface adapters for different CLI interaction modes.

Handles adaptation between different interface complexity levels.
"""
from typing import Dict, Any, Optional, Union
from enum import Enum


class InterfaceMode(Enum):
    """Available interface modes."""
    SIMPLE = "simple"
    BALANCED = "balanced"  # Default
    ADVANCED = "advanced"
    EXPERT = "expert"
    STREAMING = "streaming"


class InterfaceAdapter:
    """Adapts CLI interactions based on interface mode."""
    
    def __init__(self):
        self.mode_configs = self._initialize_mode_configs()
    
    def _initialize_mode_configs(self) -> Dict[str, Dict]:
        """Initialize configuration for each interface mode."""
        return {
            'simple': {
                'confirmations': 'minimal',
                'output_verbosity': 'low',
                'show_progress': False,
                'auto_execute': True,
                'max_output_lines': 10,
                'use_rich_formatting': False,
                'show_context': False,
                'interactive_prompts': False
            },
            'balanced': {
                'confirmations': 'normal',
                'output_verbosity': 'medium',
                'show_progress': True,
                'auto_execute': False,
                'max_output_lines': 50,
                'use_rich_formatting': True,
                'show_context': True,
                'interactive_prompts': True
            },
            'advanced': {
                'confirmations': 'detailed',
                'output_verbosity': 'high',
                'show_progress': True,
                'auto_execute': False,
                'max_output_lines': 100,
                'use_rich_formatting': True,
                'show_context': True,
                'interactive_prompts': True
            },
            'expert': {
                'confirmations': 'minimal',
                'output_verbosity': 'high',
                'show_progress': True,
                'auto_execute': True,
                'max_output_lines': -1,  # No limit
                'use_rich_formatting': True,
                'show_context': True,
                'interactive_prompts': False
            },
            'streaming': {
                'confirmations': 'normal',
                'output_verbosity': 'high',
                'show_progress': True,
                'auto_execute': False,
                'max_output_lines': -1,  # No limit
                'use_rich_formatting': True,
                'show_context': True,
                'interactive_prompts': True,
                'streaming': True
            }
        }
    
    def determine_mode(self, explicit_interface: Optional[str] = None,
                      fast: bool = False, stream: bool = False, 
                      auto: bool = False, review: bool = False) -> str:
        """
        Determine the appropriate interface mode.
        
        Args:
            explicit_interface: Explicitly requested interface mode
            fast: Fast mode flag
            stream: Streaming mode flag
            auto: Auto mode flag
            review: Review mode flag
            
        Returns:
            Interface mode string
        """
        # Explicit interface mode takes precedence
        if explicit_interface:
            if explicit_interface in self.mode_configs:
                return explicit_interface
        
        # Flag-based mode determination
        if stream:
            return 'streaming'
        
        if fast:
            return 'simple'
        
        if review:
            return 'advanced'
        
        if auto:
            # Auto can be simple or expert depending on context
            return 'expert'  # Assume expert for auto mode
        
        # Default mode
        return 'balanced'
    
    def get_mode_config(self, mode: str) -> Dict[str, Any]:
        """Get configuration for a specific mode."""
        return self.mode_configs.get(mode, self.mode_configs['balanced']).copy()
    
    def adapt_output(self, content: str, mode: str, 
                    content_type: str = 'general') -> str:
        """
        Adapt output content based on interface mode.
        
        Args:
            content: Content to adapt
            mode: Interface mode
            content_type: Type of content (general, error, success, progress)
            
        Returns:
            Adapted content
        """
        config = self.get_mode_config(mode)
        
        # Apply output verbosity filtering
        if config['output_verbosity'] == 'low':
            content = self._reduce_verbosity(content)
        elif config['output_verbosity'] == 'high':
            content = self._enhance_verbosity(content, content_type)
        
        # Apply line limits
        if config['max_output_lines'] > 0:
            lines = content.split('\n')
            if len(lines) > config['max_output_lines']:
                content = '\n'.join(lines[:config['max_output_lines']]) + '\n... (output truncated)'
        
        # Apply rich formatting if available and enabled
        if config.get('use_rich_formatting', False):
            content = self._apply_rich_formatting(content, content_type)
        
        return content
    
    def _reduce_verbosity(self, content: str) -> str:
        """Reduce content verbosity for simple mode."""
        lines = content.split('\n')
        
        # Keep only essential lines
        essential_lines = []
        for line in lines:
            # Skip debug/verbose lines
            if any(marker in line.lower() for marker in ['debug:', 'verbose:', 'info:']):
                continue
            
            # Keep errors, warnings, and results
            if any(marker in line.lower() for marker in ['error:', 'warning:', 'success:', 'result:']):
                essential_lines.append(line)
            elif line.strip() and not line.startswith(' '):
                # Keep non-indented non-empty lines
                essential_lines.append(line)
        
        return '\n'.join(essential_lines[:10])  # Limit to 10 lines max
    
    def _enhance_verbosity(self, content: str, content_type: str) -> str:
        """Enhance content verbosity for advanced modes."""
        timestamp = "  # " + str(hash(content) % 10000)  # Simple timestamp simulation
        
        enhanced_content = f"[{content_type.upper()}] {timestamp}\n{content}"
        
        if content_type == 'error':
            enhanced_content += "\n\nFor more details, check the logs or use --verbose flag."
        elif content_type == 'success':
            enhanced_content += "\n\nOperation completed successfully."
        
        return enhanced_content
    
    def _apply_rich_formatting(self, content: str, content_type: str) -> str:
        """Apply rich formatting if available."""
        # This would integrate with Rich library when available
        
        formatting_map = {
            'error': '[red]{}[/red]',
            'success': '[green]{}[/green]',
            'warning': '[yellow]{}[/yellow]',
            'progress': '[blue]{}[/blue]',
            'general': '{}'
        }
        
        format_template = formatting_map.get(content_type, '{}')
        return format_template.format(content)
    
    def should_confirm(self, action: str, mode: str, risk_level: str = 'medium') -> bool:
        """
        Determine if confirmation is needed for an action.
        
        Args:
            action: Action being performed
            mode: Interface mode
            risk_level: Risk level (low, medium, high)
            
        Returns:
            Whether confirmation is needed
        """
        config = self.get_mode_config(mode)
        confirmation_level = config['confirmations']
        
        # High risk actions always need confirmation except in expert mode
        if risk_level == 'high' and mode != 'expert':
            return True
        
        # Mode-specific confirmation logic
        if confirmation_level == 'minimal':
            return risk_level == 'high'
        elif confirmation_level == 'normal':
            return risk_level in ['medium', 'high']
        elif confirmation_level == 'detailed':
            return True  # Confirm everything
        
        return False
    
    def format_prompt(self, prompt: str, mode: str, options: list = None) -> str:
        """
        Format a prompt based on interface mode.
        
        Args:
            prompt: Base prompt text
            mode: Interface mode
            options: Optional list of options
            
        Returns:
            Formatted prompt
        """
        config = self.get_mode_config(mode)
        
        if not config.get('interactive_prompts', True):
            return prompt  # Return as-is for non-interactive modes
        
        # Add formatting based on mode
        if mode == 'simple':
            if options:
                formatted_options = ' | '.join(options)
                return f"{prompt} ({formatted_options}): "
            return f"{prompt}: "
        
        elif mode in ['advanced', 'expert']:
            formatted_prompt = f"\n{'='*60}\n{prompt}\n{'='*60}\n"
            if options:
                formatted_prompt += "Available options:\n"
                for i, option in enumerate(options, 1):
                    formatted_prompt += f"  {i}. {option}\n"
                formatted_prompt += "\nYour choice: "
            return formatted_prompt
        
        else:  # balanced mode
            if options:
                formatted_prompt = f"{prompt}\nOptions: {', '.join(options)}\n> "
            else:
                formatted_prompt = f"{prompt}\n> "
            return formatted_prompt
    
    def get_progress_style(self, mode: str) -> Dict[str, Any]:
        """Get progress reporting style for mode."""
        config = self.get_mode_config(mode)
        
        if not config.get('show_progress', True):
            return {'enabled': False}
        
        styles = {
            'simple': {
                'enabled': False  # No progress in simple mode
            },
            'balanced': {
                'enabled': True,
                'style': 'bar',
                'show_percentage': True,
                'show_eta': False
            },
            'advanced': {
                'enabled': True,
                'style': 'detailed',
                'show_percentage': True,
                'show_eta': True,
                'show_steps': True
            },
            'expert': {
                'enabled': True,
                'style': 'minimal',
                'show_percentage': False,
                'show_eta': False,
                'show_raw_data': True
            },
            'streaming': {
                'enabled': True,
                'style': 'live',
                'show_percentage': True,
                'show_eta': True,
                'real_time_updates': True
            }
        }
        
        return styles.get(mode, styles['balanced'])