"""
Blueprint Execution Tool for Metis Agent.

This tool executes blueprint workflows and manages blueprint-based operations.
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

from ...blueprints.core.blueprint import Blueprint
from ...blueprints.core.engine import BlueprintEngine
from ...tools.registry import initialize_tools
# Removed progress_streamer import to avoid circular imports
# Progress streaming will be handled by the CLI layer

from ..base import BaseTool


class ToolRegistryWrapper:
    """Wrapper to make tool instances dict compatible with BlueprintEngine."""
    
    def __init__(self, tool_instances: Dict[str, Any]):
        self.tool_instances = tool_instances
    
    def get_tool(self, tool_name: str):
        """Get a tool instance by name."""
        return self.tool_instances.get(tool_name)


class BlueprintExecutionTool(BaseTool):
    """
    Tool for executing blueprint workflows.
    
    This tool handles:
    - Blueprint loading and validation
    - Blueprint execution with input parameters
    - Progress tracking and result collection
    - Error handling and recovery
    """
    
    def __init__(self):
        """Initialize the blueprint execution tool."""
        self.name = "BlueprintExecutionTool"
        self.description = "Executes blueprint workflows and manages blueprint-based operations"
        self.tool_registry = None
        
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle blueprint execution tasks.
        
        Args:
            task: The task description
            
        Returns:
            True if task involves blueprint execution or workflow management
        """
        task_lower = task.lower()
        
        # Blueprint keywords
        blueprint_keywords = [
            'blueprint', 'workflow', 'execute workflow', 'run blueprint',
            'complete project development', 'project workflow', 'multi-step',
            'orchestrate', 'pipeline', 'automated workflow'
        ]
        
        return any(keyword in task_lower for keyword in blueprint_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute blueprint operations.
        
        Args:
            task: The task description
            **kwargs: Additional parameters including:
                - blueprint_name: Name of blueprint to execute
                - blueprint_path: Path to blueprint file
                - inputs: Input parameters for blueprint
                - execution_mode: sync or async execution
                
        Returns:
            Dict containing execution results and status
        """
        try:
            action = kwargs.get('action', 'execute')
            
            if action == 'execute':
                return self._execute_blueprint(**kwargs)
            elif action == 'list_blueprints':
                return self._list_available_blueprints(**kwargs)
            elif action == 'validate_blueprint':
                return self._validate_blueprint(**kwargs)
            elif action == 'get_blueprint_info':
                return self._get_blueprint_info(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown blueprint action: {action}",
                    "supported_actions": [
                        "execute", "list_blueprints", "validate_blueprint", "get_blueprint_info"
                    ]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Blueprint execution failed: {str(e)}",
                "task": task
            }
    
    def _execute_blueprint(self, **kwargs) -> Dict[str, Any]:
        """Execute a blueprint workflow."""
        blueprint_name = kwargs.get('blueprint_name')
        blueprint_path = kwargs.get('blueprint_path')
        inputs = kwargs.get('inputs', {})
        execution_mode = kwargs.get('execution_mode', 'sync')
        
        # Progress streaming will be handled by CLI layer
        print(f"[BLUEPRINT] Executing '{blueprint_name}' blueprint...")
        
        try:
            # Load blueprint
            if blueprint_path:
                blueprint = Blueprint.from_file(blueprint_path)
            elif blueprint_name:
                blueprint_path = self._find_blueprint_by_name(blueprint_name)
                if not blueprint_path:
                    print(f"[ERROR] Blueprint '{blueprint_name}' not found")
                    return {
                        "success": False,
                        "error": f"Blueprint '{blueprint_name}' not found",
                        "outputs": {}
                    }
                blueprint = Blueprint.from_file(blueprint_path)
            else:
                print(f"[ERROR] Either blueprint_name or blueprint_path must be provided")
                return {
                    "success": False,
                    "error": "Either blueprint_name or blueprint_path must be provided",
                    "outputs": {}
                }
        
        except Exception as e:
            print(f"[ERROR] Failed to load blueprint: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to load blueprint: {str(e)}",
                "outputs": {}
            }
        
        try:
            # Initialize blueprint engine with tool registry
            tool_instances = initialize_tools()
            tool_registry = ToolRegistryWrapper(tool_instances)
            engine = BlueprintEngine(tool_registry)
            
            # Check if this is an interactive blueprint (has phases)
            current_phase = kwargs.get('current_phase')
            if current_phase or self._is_interactive_blueprint(blueprint):
                # Suppress technical messages for better user experience
                # print(f"[BLUEPRINT] Starting interactive execution with {len(tool_instances)} tools...")
                # print(f"[BLUEPRINT] Current phase: {current_phase or 'auto-detect'}")
                
                # Use interactive execution
                result = engine.execute_interactive(
                    blueprint=blueprint,
                    inputs=inputs,
                    current_phase=current_phase
                )
            else:
                # Use standard execution
                # print(f"[BLUEPRINT] Starting standard execution with {len(tool_instances)} tools...")
                if execution_mode == 'sync':
                    result = engine.execute(blueprint, inputs)
                else:
                    # For async execution, we'd need to implement async support
                    result = engine.execute(blueprint, inputs)
            
            return {
                "success": True,
                "operation": "execute_blueprint",
                "blueprint_name": blueprint.metadata.name,
                "execution_result": result,
                "outputs": self._extract_outputs(blueprint, result)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Blueprint execution failed: {str(e)}",
                "blueprint_name": blueprint.metadata.name
            }
    
    def _is_interactive_blueprint(self, blueprint) -> bool:
        """
        Determine if a blueprint supports interactive execution.
        
        Interactive blueprints have phases or interaction steps.
        """
        # Check if blueprint metadata indicates phases
        if hasattr(blueprint, 'metadata') and blueprint.metadata:
            if hasattr(blueprint.metadata, 'phases') and blueprint.metadata.phases:
                return True
            if hasattr(blueprint.metadata, 'requires_user_interaction') and blueprint.metadata.requires_user_interaction:
                return True
        
        # Check if blueprint has phase-named steps
        phase_prefixes = ['design_', 'code_creation_', 'iteration_']
        for step in blueprint.steps:
            if any(step.id.startswith(prefix) for prefix in phase_prefixes):
                return True
        
        # Check if blueprint has interaction steps
        for step in blueprint.steps:
            if hasattr(step, 'tool') and step.tool in ['ConversationManagerTool', 'InteractionTool']:
                return True
            if hasattr(step, 'action') and step.action in ['interactive_questions', 'user_input']:
                return True
        
        return False
    
    def _extract_outputs(self, blueprint: Blueprint, result: Dict) -> Dict[str, Any]:
        """Extract output values from blueprint execution result."""
        outputs = {}
        
        for output_def in blueprint.outputs:
            if output_def.source:
                # Parse source reference like "steps.step_id.outputs.key"
                source_parts = output_def.source.split('.')
                if len(source_parts) >= 3 and source_parts[0] == 'steps':
                    step_id = source_parts[1]
                    output_key = '.'.join(source_parts[3:])  # Skip "steps", step_id, "outputs"
                    
                    step_results = result.get('step_results', {})
                    if step_id in step_results:
                        step_result = step_results[step_id]
                        if 'outputs' in step_result and output_key in step_result['outputs']:
                            outputs[output_def.name] = step_result['outputs'][output_key]
        
        return outputs
    
    def _find_blueprint_by_name(self, name: str) -> Optional[Path]:
        """Find blueprint file by name."""
        # Look in the templates/examples directory
        templates_dir = Path(__file__).parent.parent.parent / 'blueprints' / 'templates' / 'examples'
        
        # Try different file extensions
        for ext in ['.yaml', '.yml', '.json']:
            # Try exact name match
            blueprint_path = templates_dir / f"{name}{ext}"
            if blueprint_path.exists():
                return blueprint_path
            
            # Try name with underscores replaced by hyphens
            alt_name = name.replace('_', '-')
            blueprint_path = templates_dir / f"{alt_name}{ext}"
            if blueprint_path.exists():
                return blueprint_path
            
            # Try name with spaces replaced by underscores
            alt_name = name.replace(' ', '_')
            blueprint_path = templates_dir / f"{alt_name}{ext}"
            if blueprint_path.exists():
                return blueprint_path
        
        return None
    
    def _get_available_blueprint_names(self) -> List[str]:
        """Get list of available blueprint names."""
        templates_dir = Path(__file__).parent.parent.parent / 'blueprints' / 'templates' / 'examples'
        
        if not templates_dir.exists():
            return []
        
        blueprint_names = []
        for file_path in templates_dir.glob('*.yaml'):
            blueprint_names.append(file_path.stem)
        for file_path in templates_dir.glob('*.yml'):
            blueprint_names.append(file_path.stem)
        for file_path in templates_dir.glob('*.json'):
            blueprint_names.append(file_path.stem)
        
        return sorted(blueprint_names)
    
    def _list_available_blueprints(self, **kwargs) -> Dict[str, Any]:
        """List all available blueprints."""
        templates_dir = Path(__file__).parent.parent.parent / 'blueprints' / 'templates' / 'examples'
        
        blueprints = []
        
        if templates_dir.exists():
            for file_path in templates_dir.glob('*.yaml'):
                try:
                    blueprint = Blueprint.from_file(file_path)
                    blueprints.append({
                        "name": blueprint.metadata.name,
                        "file_name": file_path.name,
                        "description": blueprint.metadata.description,
                        "category": blueprint.metadata.category,
                        "version": blueprint.metadata.version,
                        "tags": blueprint.metadata.tags
                    })
                except Exception as e:
                    blueprints.append({
                        "name": file_path.stem,
                        "file_name": file_path.name,
                        "error": f"Failed to load: {str(e)}"
                    })
        
        return {
            "success": True,
            "operation": "list_blueprints",
            "blueprints": blueprints,
            "count": len(blueprints)
        }
    
    def _validate_blueprint(self, **kwargs) -> Dict[str, Any]:
        """Validate a blueprint without executing it."""
        blueprint_name = kwargs.get('blueprint_name')
        blueprint_path = kwargs.get('blueprint_path')
        
        # Load blueprint
        if blueprint_path:
            blueprint = Blueprint.from_file(blueprint_path)
        elif blueprint_name:
            blueprint_path = self._find_blueprint_by_name(blueprint_name)
            if not blueprint_path:
                return {
                    "success": False,
                    "error": f"Blueprint not found: {blueprint_name}"
                }
            blueprint = Blueprint.from_file(blueprint_path)
        else:
            return {
                "success": False,
                "error": "Either blueprint_name or blueprint_path must be provided"
            }
        
        # Validate blueprint
        validation_errors = blueprint.validate()
        
        return {
            "success": True,
            "operation": "validate_blueprint",
            "blueprint_name": blueprint.metadata.name,
            "valid": len(validation_errors) == 0,
            "validation_errors": validation_errors,
            "metadata": {
                "name": blueprint.metadata.name,
                "version": blueprint.metadata.version,
                "description": blueprint.metadata.description,
                "steps_count": len(blueprint.steps),
                "inputs_count": len(blueprint.inputs),
                "outputs_count": len(blueprint.outputs)
            }
        }
    
    def _get_blueprint_info(self, **kwargs) -> Dict[str, Any]:
        """Get detailed information about a blueprint."""
        blueprint_name = kwargs.get('blueprint_name')
        blueprint_path = kwargs.get('blueprint_path')
        
        # Load blueprint
        if blueprint_path:
            blueprint = Blueprint.from_file(blueprint_path)
        elif blueprint_name:
            blueprint_path = self._find_blueprint_by_name(blueprint_name)
            if not blueprint_path:
                return {
                    "success": False,
                    "error": f"Blueprint not found: {blueprint_name}"
                }
            blueprint = Blueprint.from_file(blueprint_path)
        else:
            return {
                "success": False,
                "error": "Either blueprint_name or blueprint_path must be provided"
            }
        
        # Extract blueprint information
        info = {
            "metadata": {
                "name": blueprint.metadata.name,
                "version": blueprint.metadata.version,
                "description": blueprint.metadata.description,
                "author": blueprint.metadata.author,
                "category": blueprint.metadata.category,
                "tags": blueprint.metadata.tags
            },
            "inputs": [
                {
                    "name": inp.name,
                    "type": inp.type,
                    "required": inp.required,
                    "default": inp.default,
                    "description": inp.description
                }
                for inp in blueprint.inputs
            ],
            "outputs": [
                {
                    "name": out.name,
                    "type": out.type,
                    "description": out.description,
                    "source": out.source
                }
                for out in blueprint.outputs
            ],
            "steps": [
                {
                    "id": step.id,
                    "tool": step.tool,
                    "action": step.action,
                    "depends_on": step.depends_on,
                    "parallel": step.parallel
                }
                for step in blueprint.steps
            ],
            "execution_order": blueprint.get_execution_order()
        }
        
        return {
            "success": True,
            "operation": "get_blueprint_info",
            "blueprint_info": info
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["moderate", "complex"],
            "input_types": ["blueprint_specification", "workflow_parameters"],
            "output_types": ["execution_results", "workflow_status"],
            "estimated_execution_time": "varies (depends on blueprint)",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": True,  # Can coordinate multiple tools
            "supported_intents": [
                "execute_blueprint", "workflow_orchestration", "multi_step_automation",
                "blueprint_management", "workflow_validation"
            ],
            "api_dependencies": [],
            "memory_usage": "moderate"
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "execute complete project development workflow",
            "run blueprint for automated testing pipeline",
            "orchestrate multi-step code analysis workflow",
            "execute documentation generation blueprint",
            "run project setup and validation workflow",
            "list available blueprint workflows",
            "validate blueprint before execution"
        ]
