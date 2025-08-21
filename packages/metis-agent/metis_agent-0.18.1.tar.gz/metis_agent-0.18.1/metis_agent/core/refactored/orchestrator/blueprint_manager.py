"""
Blueprint management for the orchestrator.

Handles blueprint detection, creation, and management for reusable patterns.
"""
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models import ExecutionResult
from ...blueprints.core.blueprint import Blueprint, BlueprintMetadata, BlueprintInput, BlueprintOutput, BlueprintStep


class BlueprintManager:
    """Manages blueprint detection and creation for complex tasks."""
    
    def __init__(self, orchestrator):
        """Initialize with reference to main orchestrator."""
        self.orchestrator = orchestrator
        self.blueprint_opportunities = []
        self.created_blueprints = []
    
    def detect_blueprint_opportunity(self, task: str, execution_result: ExecutionResult, 
                                   context: Dict) -> Optional[Dict]:
        """
        Detect if a task execution represents a good blueprint opportunity.
        
        Args:
            task: Task description
            execution_result: Execution result
            context: Execution context
            
        Returns:
            Blueprint opportunity details or None
        """
        # Check if task is complex enough
        if not self.orchestrator.complexity_analyzer.analyze_task_complexity(task, execution_result):
            return None
        
        # Calculate reusability score
        reusability_score = self._calculate_reusability_score(task, execution_result)
        
        if reusability_score < 0.6:  # Threshold for blueprint creation
            return None
        
        # Classify blueprint type
        blueprint_type = self._classify_blueprint_type(task)
        
        # Extract tools and patterns used
        tools_used = execution_result.tools_used if execution_result else []
        
        opportunity = {
            'task': task,
            'blueprint_type': blueprint_type,
            'reusability_score': reusability_score,
            'tools_used': tools_used,
            'execution_success': execution_result.success if execution_result else False,
            'complexity_indicators': self._identify_complexity_indicators(task),
            'detected_at': datetime.now().isoformat(),
            'context_session_id': context.get('session_id')
        }
        
        # Record opportunity
        self.blueprint_opportunities.append(opportunity)
        
        return opportunity
    
    def suggest_blueprint_creation(self, opportunity: Dict, context: Dict) -> str:
        """
        Generate suggestion for blueprint creation.
        
        Args:
            opportunity: Blueprint opportunity details
            context: Execution context
            
        Returns:
            Blueprint creation suggestion text
        """
        task = opportunity['task']
        blueprint_type = opportunity['blueprint_type']
        reusability_score = opportunity['reusability_score']
        tools_used = opportunity['tools_used']
        
        suggestion = f"""
Blueprint Creation Opportunity Detected!

Task: {task}
Type: {blueprint_type.title()} Blueprint
Reusability Score: {reusability_score:.2f}/1.0

This task shows high potential for blueprint creation because:
- It uses multiple tools ({len(tools_used)} tools: {', '.join(tools_used)})
- It follows a repeatable pattern
- The complexity justifies reusable automation

Suggested Blueprint Features:
{self._generate_blueprint_features(opportunity)}

To create this blueprint, the system would:
1. Extract the execution pattern and tools used
2. Parameterize inputs and outputs
3. Generate reusable blueprint template
4. Enable one-click execution for similar tasks

Would you like to create this blueprint for future use?
"""
        
        return suggestion.strip()
    
    def create_blueprint_from_execution(self, opportunity: Dict, context: Dict, 
                                       save_path: str = None) -> Blueprint:
        """
        Create a blueprint from an execution opportunity.
        
        Args:
            opportunity: Blueprint opportunity details
            context: Execution context
            save_path: Optional path to save blueprint
            
        Returns:
            Created Blueprint instance
        """
        task = opportunity['task']
        blueprint_type = opportunity['blueprint_type']
        tools_used = opportunity['tools_used']
        
        # Generate blueprint components
        blueprint_name = self._generate_blueprint_name(blueprint_type, task)
        inputs = self._generate_blueprint_inputs(task, tools_used)
        outputs = self._generate_blueprint_outputs(task, blueprint_type)
        steps = self._generate_blueprint_steps(tools_used, task)
        
        # Create metadata
        metadata = BlueprintMetadata(
            name=blueprint_name,
            version="1.0.0",
            description=f"Blueprint for {blueprint_type} tasks similar to: {task[:100]}...",
            author="Metis Agent System",
            created_at=datetime.now().isoformat(),
            tags=[blueprint_type, "auto-generated"],
            category=blueprint_type,
            complexity="medium" if len(tools_used) <= 2 else "high"
        )
        
        # Create blueprint
        blueprint = Blueprint(
            metadata=metadata,
            inputs=inputs,
            outputs=outputs,
            steps=steps
        )
        
        # Save blueprint if path provided
        if save_path:
            blueprint.save(save_path)
        
        # Record created blueprint
        blueprint_record = {
            'blueprint_name': blueprint_name,
            'blueprint_type': blueprint_type,
            'original_task': task,
            'tools_used': tools_used,
            'created_at': datetime.now().isoformat(),
            'save_path': save_path
        }
        
        self.created_blueprints.append(blueprint_record)
        
        return blueprint
    
    def _calculate_reusability_score(self, task: str, execution_result: ExecutionResult) -> float:
        """Calculate how reusable a task pattern is."""
        score = 0.0
        task_lower = task.lower()
        
        # Multiple tools usage increases reusability
        if execution_result and execution_result.tools_used:
            tool_count = len(execution_result.tools_used)
            if tool_count >= 3:
                score += 0.3
            elif tool_count >= 2:
                score += 0.2
            else:
                score += 0.1
        
        # Successful execution increases reusability
        if execution_result and execution_result.success:
            score += 0.2
        
        # Common patterns increase reusability
        reusable_patterns = [
            'analyze and create', 'search and summarize', 'process and output',
            'validate and report', 'extract and transform', 'generate and save'
        ]
        
        pattern_matches = sum(
            1 for pattern in reusable_patterns
            if pattern in task_lower
        )
        score += min(pattern_matches * 0.15, 0.3)
        
        # Generic task types are more reusable
        generic_indicators = [
            'create', 'generate', 'analyze', 'process', 'transform',
            'extract', 'validate', 'report', 'summarize'
        ]
        
        generic_count = sum(
            1 for indicator in generic_indicators
            if indicator in task_lower
        )
        score += min(generic_count * 0.1, 0.2)
        
        # Long execution time suggests complex reusable process
        if execution_result and hasattr(execution_result, 'execution_time'):
            try:
                if hasattr(execution_result.execution_time, 'total_seconds'):
                    seconds = execution_result.execution_time.total_seconds()
                    if seconds > 10:  # More than 10 seconds
                        score += 0.1
            except Exception:
                pass
        
        return min(1.0, score)
    
    def _classify_blueprint_type(self, task: str) -> str:
        """Classify the type of blueprint based on task."""
        task_lower = task.lower()
        
        # Data processing patterns
        if any(keyword in task_lower for keyword in ['analyze', 'process', 'extract', 'transform']):
            return 'data_processing'
        
        # Content generation patterns
        elif any(keyword in task_lower for keyword in ['create', 'generate', 'write', 'build']):
            return 'content_generation'
        
        # Research patterns
        elif any(keyword in task_lower for keyword in ['search', 'research', 'find', 'investigate']):
            return 'research'
        
        # Validation patterns
        elif any(keyword in task_lower for keyword in ['validate', 'verify', 'check', 'test']):
            return 'validation'
        
        # Automation patterns
        elif any(keyword in task_lower for keyword in ['automate', 'schedule', 'batch', 'bulk']):
            return 'automation'
        
        # Default to workflow
        else:
            return 'workflow'
    
    def _identify_complexity_indicators(self, task: str) -> List[str]:
        """Identify complexity indicators in the task."""
        indicators = []
        task_lower = task.lower()
        
        complexity_patterns = {
            'multi_step': ['then', 'after', 'next', 'following', 'and then'],
            'integration': ['integrate', 'combine', 'merge', 'connect'],
            'analysis': ['analyze', 'examine', 'evaluate', 'assess'],
            'transformation': ['convert', 'transform', 'process', 'modify'],
            'generation': ['create', 'generate', 'build', 'produce'],
            'validation': ['validate', 'verify', 'check', 'confirm']
        }
        
        for category, patterns in complexity_patterns.items():
            if any(pattern in task_lower for pattern in patterns):
                indicators.append(category)
        
        return indicators
    
    def _generate_blueprint_features(self, opportunity: Dict) -> str:
        """Generate description of blueprint features."""
        features = []
        tools_used = opportunity['tools_used']
        blueprint_type = opportunity['blueprint_type']
        
        features.append(f"- Automated {blueprint_type} workflow")
        features.append(f"- Integrated use of {len(tools_used)} tools")
        
        for tool in tools_used:
            if tool == 'google_search':
                features.append("- Intelligent web search and information gathering")
            elif tool == 'calculator':
                features.append("- Mathematical computation and analysis")
            elif tool == 'textanalyzer':
                features.append("- Advanced text processing and insights")
            elif tool == 'write_tool':
                features.append("- Automated file creation and output generation")
            elif tool == 'webscrapertool':
                features.append("- Web data extraction and processing")
        
        features.append("- Parameterized inputs for customization")
        features.append("- Consistent output formatting")
        features.append("- Error handling and validation")
        
        return '\n'.join(features)
    
    def _generate_blueprint_name(self, blueprint_type: str, task: str) -> str:
        """Generate a name for the blueprint."""
        # Extract key words from task
        words = re.findall(r'\b\w+\b', task.lower())
        key_words = [word for word in words if len(word) > 3 and word not in [
            'please', 'could', 'would', 'should', 'with', 'from', 'that', 'this'
        ]]
        
        # Take first few key words
        name_parts = key_words[:3] if len(key_words) >= 3 else key_words
        
        if not name_parts:
            name_parts = [blueprint_type]
        
        # Create name
        name = '_'.join(name_parts) + '_blueprint'
        
        # Clean up name
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        return name[:50]  # Limit length
    
    def _generate_blueprint_inputs(self, task: str, tools_used: List[str]) -> List[BlueprintInput]:
        """Generate blueprint inputs based on task and tools."""
        inputs = []
        
        # Always include task description
        inputs.append(BlueprintInput(
            name="task_description",
            type="string",
            description="Description of the task to perform",
            required=True,
            default=task[:100] + "..." if len(task) > 100 else task
        ))
        
        # Tool-specific inputs
        if 'google_search' in tools_used:
            inputs.append(BlueprintInput(
                name="search_query",
                type="string",
                description="Query for web search",
                required=True
            ))
        
        if 'calculator' in tools_used:
            inputs.append(BlueprintInput(
                name="calculation_expression",
                type="string",
                description="Mathematical expression to calculate",
                required=False
            ))
        
        if 'write_tool' in tools_used:
            inputs.append(BlueprintInput(
                name="output_filename",
                type="string",
                description="Name of the output file to create",
                required=False,
                default="output.txt"
            ))
        
        # Generic configuration
        inputs.append(BlueprintInput(
            name="output_format",
            type="string",
            description="Desired output format",
            required=False,
            default="text",
            choices=["text", "json", "markdown"]
        ))
        
        return inputs
    
    def _generate_blueprint_outputs(self, task: str, blueprint_type: str) -> List[BlueprintOutput]:
        """Generate blueprint outputs based on task type."""
        outputs = []
        
        # Main result output
        outputs.append(BlueprintOutput(
            name="result",
            type="string",
            description=f"Main result of the {blueprint_type} operation"
        ))
        
        # Metadata output
        outputs.append(BlueprintOutput(
            name="metadata",
            type="object",
            description="Execution metadata including tools used and timing"
        ))
        
        # Type-specific outputs
        if blueprint_type == 'research':
            outputs.append(BlueprintOutput(
                name="sources",
                type="array",
                description="List of sources used in research"
            ))
        
        elif blueprint_type == 'data_processing':
            outputs.append(BlueprintOutput(
                name="processed_data",
                type="object",
                description="Processed data results"
            ))
        
        elif blueprint_type == 'content_generation':
            outputs.append(BlueprintOutput(
                name="generated_content",
                type="string",
                description="Generated content output"
            ))
        
        return outputs
    
    def _generate_blueprint_steps(self, tools_used: List[str], task: str) -> List[BlueprintStep]:
        """Generate blueprint steps based on tools used."""
        steps = []
        step_id = 1
        
        # Initial validation step
        steps.append(BlueprintStep(
            id=f"step_{step_id}",
            name="validate_inputs",
            description="Validate input parameters",
            tool="validator",
            inputs={"task_description": "{{ inputs.task_description }}"},
            outputs=["validation_result"]
        ))
        step_id += 1
        
        # Tool-specific steps
        for tool in tools_used:
            if tool == 'google_search':
                steps.append(BlueprintStep(
                    id=f"step_{step_id}",
                    name="web_search",
                    description="Search for relevant information",
                    tool="google_search",
                    inputs={"query": "{{ inputs.search_query or inputs.task_description }}"},
                    outputs=["search_results"]
                ))
            
            elif tool == 'calculator':
                steps.append(BlueprintStep(
                    id=f"step_{step_id}",
                    name="calculate",
                    description="Perform calculations",
                    tool="calculator",
                    inputs={"expression": "{{ inputs.calculation_expression }}"},
                    outputs=["calculation_result"]
                ))
            
            elif tool == 'textanalyzer':
                steps.append(BlueprintStep(
                    id=f"step_{step_id}",
                    name="analyze_text",
                    description="Analyze text content",
                    tool="textanalyzer",
                    inputs={"text": "{{ previous_step.result }}"},
                    outputs=["analysis_result"]
                ))
            
            elif tool == 'write_tool':
                steps.append(BlueprintStep(
                    id=f"step_{step_id}",
                    name="write_output",
                    description="Write results to file",
                    tool="write_tool",
                    inputs={
                        "filename": "{{ inputs.output_filename }}",
                        "content": "{{ previous_step.result }}"
                    },
                    outputs=["file_path"]
                ))
            
            step_id += 1
        
        # Final aggregation step
        steps.append(BlueprintStep(
            id=f"step_{step_id}",
            name="aggregate_results",
            description="Combine and format final results",
            tool="aggregator",
            inputs={"all_results": "{{ all_previous_outputs }}"},
            outputs=["final_result", "metadata"]
        ))
        
        return steps
    
    def get_blueprint_statistics(self) -> Dict[str, Any]:
        """Get statistics about blueprint opportunities and creation."""
        return {
            'opportunities_detected': len(self.blueprint_opportunities),
            'blueprints_created': len(self.created_blueprints),
            'blueprint_types': self._get_blueprint_type_distribution(),
            'recent_opportunities': self.blueprint_opportunities[-5:] if len(self.blueprint_opportunities) > 5 else self.blueprint_opportunities
        }
    
    def _get_blueprint_type_distribution(self) -> Dict[str, int]:
        """Get distribution of blueprint types."""
        type_counts = {}
        
        for opportunity in self.blueprint_opportunities:
            blueprint_type = opportunity.get('blueprint_type', 'unknown')
            type_counts[blueprint_type] = type_counts.get(blueprint_type, 0) + 1
        
        return type_counts
    
    def get_status(self) -> Dict[str, Any]:
        """Get blueprint manager status."""
        return {
            'opportunities_detected': len(self.blueprint_opportunities),
            'blueprints_created': len(self.created_blueprints),
            'component': 'BlueprintManager',
            'status': 'active'
        }