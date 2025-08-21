#!/usr/bin/env python3
"""
Blueprint Class - Core Workflow Definition

This module provides the Blueprint class for defining and managing
tool workflows in the Metis Agent framework.
"""

import yaml
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import re
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    """Execution status for blueprint steps."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ErrorHandlingStrategy(Enum):
    """Error handling strategies for blueprint steps."""
    FAIL_FAST = "fail_fast"
    CONTINUE = "continue"
    RETRY = "retry"
    SKIP = "skip"


@dataclass
class BlueprintInput:
    """Blueprint input parameter definition."""
    name: str
    type: str
    required: bool = True
    default: Any = None
    description: str = ""
    validation: Optional[Dict[str, Any]] = None


@dataclass
class BlueprintOutput:
    """Blueprint output definition."""
    name: str
    type: str
    description: str = ""
    source: str = ""  # Which step/variable provides this output


@dataclass
class BlueprintStep:
    """Individual step in a blueprint workflow."""
    id: str
    tool: str
    action: str
    description: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    parallel: bool = False
    for_each: Optional[str] = None
    condition: Optional[str] = None
    error_handling: ErrorHandlingStrategy = ErrorHandlingStrategy.FAIL_FAST
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Runtime properties
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class BlueprintMetadata:
    """Blueprint metadata and configuration."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    category: str = "general"


class Blueprint:
    """
    Blueprint class for defining and managing tool workflows.
    
    A Blueprint represents a structured workflow that chains multiple tools
    together to accomplish complex tasks. It handles:
    - Workflow definition and validation
    - Step dependency resolution
    - Data flow between steps
    - Error handling and recovery
    - Execution state management
    """
    
    def __init__(self, blueprint_data: Optional[Union[Dict[str, Any], str, Path]] = None):
        """
        Initialize a Blueprint.
        
        Args:
            blueprint_data: Blueprint definition as dict, YAML string, or file path
        """
        # Core properties
        self.metadata: BlueprintMetadata = BlueprintMetadata(name="Untitled Blueprint")
        self.inputs: List[BlueprintInput] = []
        self.outputs: List[BlueprintOutput] = []
        self.steps: List[BlueprintStep] = []
        self.variables: Dict[str, Any] = {}
        self.conditions: List[Dict[str, Any]] = []
        
        # Runtime properties
        self.execution_id: Optional[str] = None
        self.execution_context: Dict[str, Any] = {}
        self.step_results: Dict[str, Any] = {}
        self.global_variables: Dict[str, Any] = {}
        
        # Load blueprint if data provided
        if blueprint_data is not None:
            self.load(blueprint_data)
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Blueprint':
        """
        Create a Blueprint instance from a file.
        
        Args:
            file_path: Path to the blueprint file (YAML, JSON, or Markdown)
            
        Returns:
            Blueprint: New Blueprint instance loaded from file
        """
        return cls(file_path)
    
    def load(self, blueprint_data: Union[Dict[str, Any], str, Path]) -> None:
        """
        Load blueprint from various sources.
        
        Args:
            blueprint_data: Blueprint definition as dict, YAML string, file path, or Markdown with frontmatter
        """
        if isinstance(blueprint_data, (str, Path)):
            path = Path(blueprint_data)
            if path.exists():
                # Load from file
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(content)
                elif path.suffix.lower() == '.json':
                    data = json.loads(content)
                elif path.suffix.lower() in ['.md', '.markdown']:
                    data = self._parse_markdown_blueprint(content)
                else:
                    raise ValueError(f"Unsupported file format: {path.suffix}. Supported: .yaml, .yml, .json, .md, .markdown")
            else:
                # Try to parse as string content
                if isinstance(blueprint_data, str):
                    # Check if it's markdown with frontmatter
                    if blueprint_data.strip().startswith('---'):
                        data = self._parse_markdown_blueprint(blueprint_data)
                    else:
                        # Try to parse as YAML string
                        try:
                            data = yaml.safe_load(blueprint_data)
                        except yaml.YAMLError:
                            raise ValueError("Invalid YAML string provided")
                else:
                    raise ValueError(f"File not found: {path}")
        elif isinstance(blueprint_data, dict):
            data = blueprint_data
        else:
            raise ValueError("Blueprint data must be dict, YAML string, file path, or Markdown with frontmatter")
        
        # Parse the blueprint data
        self._parse_blueprint(data)
    
    def _parse_blueprint(self, data: Dict[str, Any]) -> None:
        """Parse blueprint data and populate object properties."""
        blueprint_section = data.get('blueprint', data)
        
        # Parse metadata
        self.metadata = BlueprintMetadata(
            name=blueprint_section.get('name', 'Untitled Blueprint'),
            version=blueprint_section.get('version', '1.0.0'),
            description=blueprint_section.get('description', ''),
            author=blueprint_section.get('author', ''),
            tags=blueprint_section.get('tags', []),
            category=blueprint_section.get('category', 'general')
        )
        
        # Parse inputs
        self.inputs = []
        for input_data in blueprint_section.get('inputs', []):
            self.inputs.append(BlueprintInput(
                name=input_data['name'],
                type=input_data.get('type', 'string'),
                required=input_data.get('required', True),
                default=input_data.get('default'),
                description=input_data.get('description', ''),
                validation=input_data.get('validation')
            ))
        
        # Parse outputs
        self.outputs = []
        for output_data in blueprint_section.get('outputs', []):
            self.outputs.append(BlueprintOutput(
                name=output_data['name'],
                type=output_data.get('type', 'any'),
                description=output_data.get('description', ''),
                source=output_data.get('source', '')
            ))
        
        # Parse steps
        self.steps = []
        for step_data in blueprint_section.get('steps', []):
            error_handling = ErrorHandlingStrategy.FAIL_FAST
            if 'error_handling' in step_data:
                try:
                    error_handling = ErrorHandlingStrategy(step_data['error_handling'])
                except ValueError:
                    error_handling = ErrorHandlingStrategy.FAIL_FAST
            
            # Parse outputs - handle both list and dict formats
            outputs = step_data.get('outputs', {})
            if isinstance(outputs, list):
                # Convert list format to dict format
                outputs_dict = {}
                for output_item in outputs:
                    if isinstance(output_item, dict) and 'name' in output_item:
                        outputs_dict[output_item['name']] = output_item.get('source', output_item['name'])
                outputs = outputs_dict
            
            step = BlueprintStep(
                id=step_data['id'],
                tool=step_data['tool'],
                action=step_data.get('action', 'execute'),
                description=step_data.get('description'),
                inputs=step_data.get('inputs', {}),
                outputs=outputs,
                depends_on=step_data.get('depends_on', []),
                parallel=step_data.get('parallel', False),
                for_each=step_data.get('for_each'),
                condition=step_data.get('condition'),
                error_handling=error_handling,
                timeout=step_data.get('timeout'),
                max_retries=step_data.get('max_retries', 3)
            )
            self.steps.append(step)
        
        # Parse variables
        self.variables = blueprint_section.get('variables', {})
        
        # Parse conditions
        self.conditions = blueprint_section.get('conditions', [])
        
        # Validate the blueprint
        self.validate()
    
    def _parse_markdown_blueprint(self, content: str) -> Dict[str, Any]:
        """
        Parse a Markdown file with YAML frontmatter to extract blueprint data.
        
        Args:
            content: Markdown content with YAML frontmatter
            
        Returns:
            Parsed blueprint data as dictionary
            
        Raises:
            ValueError: If frontmatter is invalid or missing
        """
        # Split frontmatter and content
        parts = content.split('---', 2)
        
        if len(parts) < 3 or not content.strip().startswith('---'):
            raise ValueError("Markdown blueprint must start with YAML frontmatter delimited by '---'")
        
        # Extract frontmatter (parts[1] is the YAML between the first two ---)
        frontmatter = parts[1].strip()
        markdown_content = parts[2].strip() if len(parts) > 2 else ""
        
        if not frontmatter:
            raise ValueError("YAML frontmatter cannot be empty")
        
        try:
            # Parse YAML frontmatter
            blueprint_data = yaml.safe_load(frontmatter)
            
            if not isinstance(blueprint_data, dict):
                raise ValueError("YAML frontmatter must be a dictionary")
            
            # Add markdown content as documentation if present
            if markdown_content:
                if 'blueprint' in blueprint_data:
                    blueprint_data['blueprint']['documentation'] = markdown_content
                else:
                    blueprint_data['documentation'] = markdown_content
            
            return blueprint_data
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
    
    def validate(self) -> List[str]:
        """
        Validate the blueprint for correctness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not self.metadata.name:
            errors.append("Blueprint name is required")
        
        if not self.steps:
            errors.append("Blueprint must have at least one step")
        
        # Validate step IDs are unique
        step_ids = [step.id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("Step IDs must be unique")
        
        # Validate step dependencies
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step '{step.id}' depends on non-existent step '{dep}'")
        
        # Check for circular dependencies
        if self._has_circular_dependencies():
            errors.append("Blueprint contains circular dependencies")
        
        # Validate variable references
        for step in self.steps:
            self._validate_variable_references(step.inputs, errors, f"Step '{step.id}' inputs")
            if step.condition:
                self._validate_variable_references({'condition': step.condition}, errors, f"Step '{step.id}' condition")
        
        return errors
    
    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies in step execution order."""
        # Build dependency graph
        graph = {step.id: step.depends_on for step in self.steps}
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in graph:
            if step_id not in visited:
                if has_cycle(step_id):
                    return True
        
        return False
    
    def _validate_variable_references(self, data: Any, errors: List[str], context: str) -> None:
        """Validate variable references in data structures."""
        if isinstance(data, str):
            # Check for variable references like ${variable.path}
            var_refs = re.findall(r'\$\{([^}]+)\}', data)
            for var_ref in var_refs:
                # Basic validation - could be enhanced
                if not self._is_valid_variable_reference(var_ref):
                    errors.append(f"{context}: Invalid variable reference '${{{var_ref}}}'")
        elif isinstance(data, dict):
            for value in data.values():
                self._validate_variable_references(value, errors, context)
        elif isinstance(data, list):
            for item in data:
                self._validate_variable_references(item, errors, context)
    
    def _is_valid_variable_reference(self, var_ref: str) -> bool:
        """Check if a variable reference is potentially valid."""
        # Basic validation - could be enhanced with more sophisticated checks
        valid_prefixes = ['inputs.', 'steps.', 'variables.', 'system.', 'outputs.']
        return any(var_ref.startswith(prefix) for prefix in valid_prefixes) or var_ref in ['item', 'index']
    
    def get_execution_order(self) -> List[List[str]]:
        """
        Get the execution order of steps considering dependencies.
        
        Returns:
            List of step ID lists, where each inner list contains steps
            that can be executed in parallel
        """
        # Build dependency graph
        graph = {step.id: step.depends_on for step in self.steps}
        in_degree = {step.id: 0 for step in self.steps}
        
        # Calculate in-degrees
        for step_id, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[step_id] += 1
        
        # Topological sort with parallel execution groups
        execution_order = []
        remaining = set(step.id for step in self.steps)
        
        while remaining:
            # Find all steps with no dependencies
            ready = [step_id for step_id in remaining if in_degree[step_id] == 0]
            
            if not ready:
                # This shouldn't happen if validation passed
                raise ValueError("Cannot determine execution order - possible circular dependency")
            
            execution_order.append(ready)
            
            # Remove ready steps and update in-degrees
            for step_id in ready:
                remaining.remove(step_id)
                for other_step_id in remaining:
                    if step_id in graph[other_step_id]:
                        in_degree[other_step_id] -= 1
        
        return execution_order
    
    def get_step_by_id(self, step_id: str) -> Optional[BlueprintStep]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def set_input_values(self, input_values: Dict[str, Any]) -> None:
        """Set input values for the blueprint execution."""
        # Validate required inputs
        for input_def in self.inputs:
            if input_def.required and input_def.name not in input_values:
                if input_def.default is None:
                    raise ValueError(f"Required input '{input_def.name}' not provided")
                input_values[input_def.name] = input_def.default
        
        # Store input values in execution context
        self.execution_context['inputs'] = input_values
        self.global_variables.update(input_values)
    
    def resolve_variable(self, variable_ref: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Resolve a variable reference to its actual value.
        
        Args:
            variable_ref: Variable reference string (e.g., "inputs.project_path")
            context: Additional context for variable resolution
            
        Returns:
            Resolved variable value
        """
        if context is None:
            context = {}
        
        # Handle different variable types
        if variable_ref.startswith('inputs.'):
            key = variable_ref[7:]  # Remove 'inputs.' prefix
            return self.execution_context.get('inputs', {}).get(key)
        
        elif variable_ref.startswith('steps.'):
            # Parse step reference like "steps.step_id.outputs.result"
            parts = variable_ref.split('.')
            if len(parts) >= 4 and parts[2] == 'outputs':
                step_id = parts[1]
                output_key = parts[3]
                return self.step_results.get(step_id, {}).get('outputs', {}).get(output_key)
        
        elif variable_ref.startswith('variables.'):
            key = variable_ref[10:]  # Remove 'variables.' prefix
            return self.global_variables.get(key)
        
        elif variable_ref.startswith('system.'):
            # System variables
            key = variable_ref[7:]
            if key == 'timestamp':
                return datetime.now().isoformat()
            elif key == 'execution_id':
                return self.execution_id
        
        elif variable_ref in context:
            return context[variable_ref]
        
        return None
    
    def substitute_variables(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Substitute variable references in data structures.
        
        Args:
            data: Data structure containing variable references
            context: Additional context for variable resolution
            
        Returns:
            Data structure with variables substituted
        """
        if isinstance(data, str):
            # Replace variable references like ${variable.path}
            def replace_var(match):
                var_ref = match.group(1)
                value = self.resolve_variable(var_ref, context)
                return str(value) if value is not None else match.group(0)
            
            return re.sub(r'\$\{([^}]+)\}', replace_var, data)
        
        elif isinstance(data, dict):
            return {key: self.substitute_variables(value, context) for key, value in data.items()}
        
        elif isinstance(data, list):
            return [self.substitute_variables(item, context) for item in data]
        
        else:
            return data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert blueprint to dictionary representation."""
        return {
            'blueprint': {
                'name': self.metadata.name,
                'version': self.metadata.version,
                'description': self.metadata.description,
                'author': self.metadata.author,
                'tags': self.metadata.tags,
                'category': self.metadata.category,
                'inputs': [
                    {
                        'name': inp.name,
                        'type': inp.type,
                        'required': inp.required,
                        'default': inp.default,
                        'description': inp.description,
                        'validation': inp.validation
                    } for inp in self.inputs
                ],
                'outputs': [
                    {
                        'name': out.name,
                        'type': out.type,
                        'description': out.description,
                        'source': out.source
                    } for out in self.outputs
                ],
                'steps': [
                    {
                        'id': step.id,
                        'tool': step.tool,
                        'action': step.action,
                        'inputs': step.inputs,
                        'outputs': step.outputs,
                        'depends_on': step.depends_on,
                        'parallel': step.parallel,
                        'for_each': step.for_each,
                        'condition': step.condition,
                        'error_handling': step.error_handling.value,
                        'timeout': step.timeout,
                        'max_retries': step.max_retries
                    } for step in self.steps
                ],
                'variables': self.variables,
                'conditions': self.conditions
            }
        }
    
    def to_yaml(self) -> str:
        """Convert blueprint to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
    
    def to_json(self) -> str:
        """Convert blueprint to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_markdown(self, include_documentation: bool = True) -> str:
        """
        Convert blueprint to Markdown format with YAML frontmatter.
        
        Args:
            include_documentation: Whether to include documentation section
            
        Returns:
            Markdown formatted blueprint
        """
        # Generate YAML frontmatter
        yaml_content = self.to_yaml()
        
        # Start with frontmatter delimiter
        markdown_lines = ['---']
        
        # Add YAML content (remove the outer 'blueprint:' wrapper for cleaner frontmatter)
        blueprint_dict = self.to_dict()['blueprint']
        yaml_frontmatter = yaml.dump(blueprint_dict, default_flow_style=False, sort_keys=False)
        markdown_lines.append(yaml_frontmatter.strip())
        
        # End frontmatter
        markdown_lines.append('---')
        markdown_lines.append('')  # Empty line after frontmatter
        
        if include_documentation:
            # Add documentation section
            markdown_lines.extend([
                f'# {self.metadata.name}',
                '',
                f'**Version:** {self.metadata.version}  ',
                f'**Author:** {self.metadata.author or "Unknown"}  ',
                f'**Category:** {self.metadata.category}  ',
                '',
                f'{self.metadata.description}',
                ''
            ])
            
            # Add tags if present
            if self.metadata.tags:
                tags_str = ' '.join([f'`{tag}`' for tag in self.metadata.tags])
                markdown_lines.extend([
                    f'**Tags:** {tags_str}',
                    ''
                ])
            
            # Add inputs section
            if self.inputs:
                markdown_lines.extend([
                    '## Inputs',
                    ''
                ])
                
                for inp in self.inputs:
                    required_str = "**Required**" if inp.required else "*Optional*"
                    default_str = f" (default: `{inp.default}`)" if inp.default is not None else ""
                    markdown_lines.extend([
                        f'- **{inp.name}** (`{inp.type}`) - {required_str}{default_str}',
                        f'  {inp.description}' if inp.description else ''
                    ])
                
                markdown_lines.append('')
            
            # Add outputs section
            if self.outputs:
                markdown_lines.extend([
                    '## Outputs',
                    ''
                ])
                
                for out in self.outputs:
                    source_str = f" (from `{out.source}`)" if out.source else ""
                    markdown_lines.extend([
                        f'- **{out.name}** (`{out.type}`){source_str}',
                        f'  {out.description}' if out.description else ''
                    ])
                
                markdown_lines.append('')
            
            # Add workflow steps section
            if self.steps:
                markdown_lines.extend([
                    '## Workflow Steps',
                    ''
                ])
                
                # Group steps by execution phase
                execution_order = self.get_execution_order()
                
                for phase_idx, phase_steps in enumerate(execution_order):
                    if len(execution_order) > 1:
                        markdown_lines.extend([
                            f'### Phase {phase_idx + 1}',
                            ''
                        ])
                    
                    for step_id in phase_steps:
                        step = next(s for s in self.steps if s.id == step_id)
                        
                        # Step header
                        parallel_str = " (parallel)" if step.parallel else ""
                        condition_str = f" *if {step.condition}*" if step.condition else ""
                        
                        markdown_lines.extend([
                            f'**{step.id}**{parallel_str}{condition_str}',
                            f'- Tool: `{step.tool}`',
                            f'- Action: `{step.action}`'
                        ])
                        
                        # Dependencies
                        if step.depends_on:
                            deps_str = ', '.join([f'`{dep}`' for dep in step.depends_on])
                            markdown_lines.append(f'- Depends on: {deps_str}')
                        
                        # Inputs
                        if step.inputs:
                            markdown_lines.append('- Inputs:')
                            for key, value in step.inputs.items():
                                markdown_lines.append(f'  - `{key}`: `{value}`')
                        
                        # Outputs
                        if step.outputs:
                            markdown_lines.append('- Outputs:')
                            for key, value in step.outputs.items():
                                markdown_lines.append(f'  - `{key}` → `{value}`')
                        
                        markdown_lines.append('')  # Empty line between steps
            
            # Add usage example
            markdown_lines.extend([
                '## Usage Example',
                '',
                '```python',
                'from metis_agent.blueprints import Blueprint, BlueprintEngine',
                '',
                '# Load blueprint',
                f'blueprint = Blueprint("{self.metadata.name.lower().replace(" ", "_")}.md")',
                '',
                '# Create engine and execute',
                'engine = BlueprintEngine()',
                'result = engine.execute(blueprint, {',
            ])
            
            # Add example inputs
            for inp in self.inputs[:3]:  # Show first 3 inputs as example
                example_value = inp.default if inp.default is not None else f'"your_{inp.name}"'
                markdown_lines.append(f'    "{inp.name}": {json.dumps(example_value)},')
            
            markdown_lines.extend([
                '})',
                '',
                'print(f"Success: {result[\'success\']}")' ,
                'print(f"Outputs: {result[\'outputs\']}")' ,
                '```',
                ''
            ])
        
        return '\n'.join(markdown_lines)
    
    def save(self, file_path: Union[str, Path]) -> None:
        """Save blueprint to file."""
        path = Path(file_path)
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                f.write(self.to_yaml())
            elif path.suffix.lower() == '.json':
                f.write(self.to_json())
            elif path.suffix.lower() in ['.md', '.markdown']:
                f.write(self.to_markdown())
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}. Supported: .yaml, .yml, .json, .md, .markdown")
    
    def __str__(self) -> str:
        """String representation of the blueprint."""
        return f"Blueprint(name='{self.metadata.name}', version='{self.metadata.version}', steps={len(self.steps)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the blueprint."""
        return (f"Blueprint(name='{self.metadata.name}', version='{self.metadata.version}', "
                f"steps={len(self.steps)}, inputs={len(self.inputs)}, outputs={len(self.outputs)})")
