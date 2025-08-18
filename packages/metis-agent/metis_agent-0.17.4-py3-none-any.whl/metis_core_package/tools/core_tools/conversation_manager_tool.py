"""
Conversation Manager Tool for Metis Agent.

This tool handles interactive conversations, multi-turn dialogs, and question-answer sessions.
"""
import json
from typing import Any, Dict, List, Optional

from ..base import BaseTool
import click


class ConversationManagerTool(BaseTool):
    """
    Tool for managing interactive conversations and question-answer sessions.
    
    This tool handles:
    - Interactive question prompts to users
    - Multi-turn conversation management
    - Response validation and collection
    - Conversation context maintenance
    """
    
    def __init__(self):
        """Initialize the conversation manager tool."""
        self.name = "ConversationManagerTool"
        self.description = "Manages interactive conversations and question-answer sessions"
        
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle conversation management tasks.
        
        Args:
            task: The task description
            
        Returns:
            True if task involves interactive conversations or questions
        """
        task_lower = task.lower()
        
        # Conversation keywords
        conversation_keywords = [
            'interactive_questions', 'ask questions', 'gather responses',
            'user input', 'clarification', 'conversation', 'dialog',
            'prompt user', 'collect answers', 'interactive session'
        ]
        
        return any(keyword in task_lower for keyword in conversation_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute conversation management operations.
        
        Args:
            task: The task description
            **kwargs: Additional parameters including:
                - questions: List of questions to ask
                - context: Context for the conversation
                - validation: Response validation rules
                
        Returns:
            Dict containing conversation results and responses
        """
        try:
            action = kwargs.get('action', 'interactive_questions')
            
            if action == 'interactive_questions':
                return self._handle_interactive_questions(**kwargs)
            elif action == 'validate_responses':
                return self._validate_responses(**kwargs)
            elif action == 'format_conversation':
                return self._format_conversation(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown conversation action: {action}",
                    "supported_actions": [
                        "interactive_questions", "validate_responses", "format_conversation"
                    ]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Conversation management failed: {str(e)}",
                "task": task
            }
    
    def _handle_interactive_questions(self, **kwargs) -> Dict[str, Any]:
        """Handle interactive question-answer session."""
        questions = kwargs.get('questions', [])
        context = kwargs.get('context', 'Information gathering')
        
        if not questions:
            return {
                "success": False,
                "error": "No questions provided for interactive session"
            }
        
        # Display context
        click.echo(click.style(f"\n[{context.upper()}]", fg="cyan", bold=True))
        click.echo("I need some additional information to better understand your requirements.\n")
        
        responses = {}
        
        for i, question_data in enumerate(questions, 1):
            if isinstance(question_data, dict):
                question = question_data.get('question', str(question_data))
                key = question_data.get('key', f'question_{i}')
                options = question_data.get('options', [])
                default = question_data.get('default')
            else:
                question = str(question_data)
                key = f'question_{i}'
                options = []
                default = None
            
            # Format question with options
            if options:
                click.echo(f"{i}. {question}")
                for j, option in enumerate(options, 1):
                    click.echo(f"   {j}) {option}")
                
                # Get user choice
                while True:
                    try:
                        choice = click.prompt("Enter your choice (number)", type=int)
                        if 1 <= choice <= len(options):
                            responses[key] = options[choice - 1]
                            break
                        else:
                            click.echo(f"Please enter a number between 1 and {len(options)}")
                    except (ValueError, click.Abort):
                        click.echo("Please enter a valid number")
            else:
                # Free text response
                prompt_text = f"{i}. {question}"
                if default:
                    prompt_text += f" (default: {default})"
                
                response = click.prompt(prompt_text, default=default or "", show_default=bool(default))
                responses[key] = response
            
            click.echo()  # Add spacing
        
        return {
            "success": True,
            "operation": "interactive_questions",
            "responses": responses,
            "questions_asked": len(questions),
            "context": context
        }
    
    def _validate_responses(self, **kwargs) -> Dict[str, Any]:
        """Validate conversation responses."""
        responses = kwargs.get('responses', {})
        validation_rules = kwargs.get('validation', {})
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        for key, rules in validation_rules.items():
            if key not in responses:
                if rules.get('required', False):
                    validation_results["errors"].append(f"Required response missing: {key}")
                    validation_results["valid"] = False
                continue
            
            value = responses[key]
            
            # Check type validation
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                validation_results["errors"].append(f"Invalid type for {key}: expected {expected_type.__name__}")
                validation_results["valid"] = False
            
            # Check value constraints
            min_length = rules.get('min_length')
            if min_length and len(str(value)) < min_length:
                validation_results["errors"].append(f"Response too short for {key}: minimum {min_length} characters")
                validation_results["valid"] = False
            
            max_length = rules.get('max_length')
            if max_length and len(str(value)) > max_length:
                validation_results["warnings"].append(f"Response very long for {key}: {len(str(value))} characters")
        
        return {
            "success": True,
            "operation": "validate_responses",
            "validation": validation_results,
            "responses": responses
        }
    
    def _format_conversation(self, **kwargs) -> Dict[str, Any]:
        """Format conversation data for storage or display."""
        conversation_data = kwargs.get('conversation_data', {})
        format_type = kwargs.get('format', 'summary')
        
        if format_type == 'summary':
            summary = {
                "timestamp": conversation_data.get('timestamp'),
                "context": conversation_data.get('context'),
                "questions_count": len(conversation_data.get('questions', [])),
                "responses_count": len(conversation_data.get('responses', {})),
                "key_responses": conversation_data.get('responses', {})
            }
            
            return {
                "success": True,
                "operation": "format_conversation",
                "formatted_data": summary,
                "format_type": format_type
            }
        
        elif format_type == 'detailed':
            return {
                "success": True,
                "operation": "format_conversation",
                "formatted_data": conversation_data,
                "format_type": format_type
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown format type: {format_type}",
                "supported_formats": ["summary", "detailed"]
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate"],
            "input_types": ["structured_data", "questions"],
            "output_types": ["user_responses", "conversation_data"],
            "estimated_execution_time": "varies (user-dependent)",
            "requires_internet": False,
            "requires_filesystem": False,
            "concurrent_safe": False,  # Interactive, requires user attention
            "resource_intensive": False,
            "supported_intents": [
                "interactive_questions", "gather_clarifications", "user_input",
                "conversation_management", "response_validation"
            ],
            "api_dependencies": [],
            "memory_usage": "low"
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "ask interactive questions to clarify requirements",
            "gather user responses for project specifications",
            "conduct question-answer session for feature clarification",
            "collect user preferences through interactive dialog",
            "validate and format conversation responses"
        ]
