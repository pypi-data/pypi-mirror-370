"""
Task planning and planning file generation components.

Handles iterative execution planning and task management.
"""
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..models import QueryAnalysis


class TaskPlanner:
    """Handles task planning for complex executions."""
    
    def __init__(self, orchestrator):
        """Initialize with reference to main orchestrator."""
        self.orchestrator = orchestrator
        self.planning_sessions = {}
        self.file_generator = PlanningFileGenerator(self)
    
    def generate_planning_files(self, query: str, analysis: QueryAnalysis, 
                               session_id: str = None) -> Tuple[str, str, str]:
        """
        Generate planning files for iterative execution.
        
        Args:
            query: User query
            analysis: Query analysis
            session_id: Session identifier
            
        Returns:
            Tuple of (execution_plan, task_list, progress_file) paths
        """
        return self.file_generator.generate_planning_files(query, analysis, session_id)
    
    def get_next_task(self, context: Dict) -> str:
        """
        Get the next task to execute from the planning context.
        
        Args:
            context: Execution context with planning files
            
        Returns:
            Next task description or 'complete' if done
        """
        planning_files = context.get('planning_files')
        if not planning_files:
            return 'complete'
        
        execution_plan, task_list, progress_file = planning_files
        
        # Read current progress
        try:
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
            else:
                progress = {'completed_tasks': [], 'current_step': 0}
            
            # Read task list
            with open(task_list, 'r') as f:
                task_content = f.read()
            
            # Parse tasks from file
            tasks = self._parse_tasks_from_file(task_content)
            
            # Find next uncompleted task
            current_step = progress.get('current_step', 0)
            completed_tasks = set(progress.get('completed_tasks', []))
            
            for i, task in enumerate(tasks):
                if i >= current_step and task not in completed_tasks:
                    return task
            
            return 'complete'
            
        except Exception as e:
            # Fallback to simple task progression
            return self._generate_fallback_task(context)
    
    def update_task_progress(self, context: Dict, task_description: str, 
                           status: str = "completed"):
        """
        Update task progress in planning files.
        
        Args:
            context: Execution context
            task_description: Task that was completed
            status: Status of the task
        """
        planning_files = context.get('planning_files')
        if not planning_files:
            return
        
        _, _, progress_file = planning_files
        
        try:
            # Read current progress
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
            else:
                progress = {'completed_tasks': [], 'current_step': 0}
            
            # Update progress
            if task_description not in progress['completed_tasks']:
                progress['completed_tasks'].append(task_description)
            
            progress['current_step'] = progress.get('current_step', 0) + 1
            progress['last_updated'] = datetime.now().isoformat()
            progress['status'] = status
            
            # Save progress
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
                
        except Exception as e:
            # Progress tracking failed, but don't break execution
            pass
    
    def update_planning_status(self, context: Dict, status: str, details: str = ""):
        """
        Update overall planning status.
        
        Args:
            context: Execution context
            status: Status update
            details: Additional details
        """
        planning_files = context.get('planning_files')
        if not planning_files:
            return
        
        _, _, progress_file = planning_files
        
        try:
            # Read current progress
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
            else:
                progress = {}
            
            # Update status
            progress['overall_status'] = status
            progress['status_details'] = details
            progress['status_updated'] = datetime.now().isoformat()
            
            # Save progress
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
                
        except Exception:
            pass  # Status update failed, but don't break execution
    
    def reference_planning_file(self, context: Dict, current_step: str) -> str:
        """
        Get reference to planning file content for current step.
        
        Args:
            context: Execution context
            current_step: Current execution step
            
        Returns:
            Planning file reference content
        """
        planning_files = context.get('planning_files')
        if not planning_files:
            return f"Executing step: {current_step}"
        
        execution_plan, task_list, progress_file = planning_files
        
        try:
            # Read relevant planning content
            plan_content = ""
            
            if os.path.exists(execution_plan):
                with open(execution_plan, 'r') as f:
                    plan_content = f.read()[:500]  # First 500 chars
            
            reference = f"""
Planning Context for: {current_step}

Execution Plan (excerpt):
{plan_content}...

Current step being executed: {current_step}
"""
            return reference.strip()
            
        except Exception:
            return f"Executing step: {current_step}"
    
    def _parse_tasks_from_file(self, task_content: str) -> List[str]:
        """Parse tasks from task list file content."""
        tasks = []
        
        # Look for numbered tasks
        import re
        numbered_tasks = re.findall(r'^\d+\.\s*(.+)$', task_content, re.MULTILINE)
        if numbered_tasks:
            return numbered_tasks
        
        # Look for bullet points
        bullet_tasks = re.findall(r'^[-*]\s*(.+)$', task_content, re.MULTILINE)
        if bullet_tasks:
            return bullet_tasks
        
        # Split by lines as fallback
        lines = [line.strip() for line in task_content.split('\n') if line.strip()]
        return lines[:10]  # Limit to 10 tasks
    
    def _generate_fallback_task(self, context: Dict) -> str:
        """Generate fallback task when planning files are not available."""
        iterations = context.get('iterations', [])
        max_iterations = context.get('max_iterations', 5)
        
        if len(iterations) >= max_iterations:
            return 'complete'
        
        query = context.get('query', '')
        
        # Simple fallback task generation
        if 'search' in query.lower():
            return 'Search for relevant information'
        elif 'analyze' in query.lower():
            return 'Analyze the provided data'
        elif 'create' in query.lower() or 'generate' in query.lower():
            return 'Create the requested content'
        else:
            return f'Process query: {query[:50]}...'
    
    def get_planning_statistics(self) -> Dict[str, Any]:
        """Get statistics about planning sessions."""
        return {
            'active_sessions': len(self.planning_sessions),
            'component': 'TaskPlanner',
            'status': 'active'
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get task planner status."""
        return self.get_planning_statistics()


class PlanningFileGenerator:
    """Generates planning files for iterative execution."""
    
    def __init__(self, planner):
        """Initialize with reference to task planner."""
        self.planner = planner
    
    def generate_planning_files(self, query: str, analysis: QueryAnalysis, 
                               session_id: str = None) -> Tuple[str, str, str]:
        """
        Generate all planning files for a query.
        
        Args:
            query: User query
            analysis: Query analysis
            session_id: Session identifier
            
        Returns:
            Tuple of (execution_plan, task_list, progress_file) paths
        """
        # Create session directory
        session_id = session_id or f"session_{int(datetime.now().timestamp())}"
        session_dir = f"planning_sessions/{session_id}"
        os.makedirs(session_dir, exist_ok=True)
        
        # Generate file paths
        execution_plan = os.path.join(session_dir, "execution_plan.md")
        task_list = os.path.join(session_dir, "task_list.md")
        progress_file = os.path.join(session_dir, "progress.json")
        
        # Generate files
        self._generate_execution_plan(analysis, execution_plan)
        self._generate_task_list(analysis, task_list)
        self._initialize_progress_file(progress_file)
        
        return execution_plan, task_list, progress_file
    
    def _generate_execution_plan(self, analysis: QueryAnalysis, file_path: str):
        """Generate execution plan file."""
        plan_content = f"""# Execution Plan

## Analysis Summary
- Query Type: {getattr(analysis, 'query_type', 'unknown')}
- Complexity: {getattr(analysis, 'complexity', 'medium')}
- Tools Required: {', '.join(getattr(analysis, 'tools_required', []))}

## Execution Strategy
{self._generate_execution_steps(analysis)}

## Expected Outcomes
{self._generate_expected_outcomes(analysis)}

## Success Criteria
{self._generate_success_criteria(analysis)}

Generated: {datetime.now().isoformat()}
"""
        
        with open(file_path, 'w') as f:
            f.write(plan_content)
    
    def _generate_task_list(self, analysis: QueryAnalysis) -> str:
        """Generate task breakdown for execution."""
        tools_required = getattr(analysis, 'tools_required', [])
        complexity = getattr(analysis, 'complexity', 'medium')
        
        tasks = []
        
        if complexity == 'simple':
            tasks.append("1. Execute primary task")
            tasks.append("2. Validate results")
        elif complexity == 'medium':
            tasks.append("1. Analyze requirements")
            tasks.append("2. Execute main operations")
            tasks.append("3. Review and validate output")
        else:  # complex
            tasks.append("1. Break down complex requirements")
            tasks.append("2. Execute prerequisite tasks")
            tasks.append("3. Perform main operations")
            tasks.append("4. Integrate results")
            tasks.append("5. Final validation and cleanup")
        
        # Add tool-specific tasks
        if 'google_search' in tools_required:
            tasks.append("- Search for relevant information")
        if 'calculator' in tools_required:
            tasks.append("- Perform calculations")
        if 'write_tool' in tools_required:
            tasks.append("- Create output files")
        if 'textanalyzer' in tools_required:
            tasks.append("- Analyze text content")
        
        return '\n'.join(tasks)
    
    def _generate_execution_steps(self, analysis: QueryAnalysis) -> str:
        """Generate detailed execution steps."""
        tools_required = getattr(analysis, 'tools_required', [])
        
        if not tools_required:
            return "Direct response execution - provide answer based on knowledge."
        
        steps = []
        
        for i, tool in enumerate(tools_required, 1):
            if tool == 'google_search':
                steps.append(f"{i}. Search for relevant information using Google Search")
            elif tool == 'calculator':
                steps.append(f"{i}. Perform mathematical calculations")
            elif tool == 'webscrapertool':
                steps.append(f"{i}. Extract data from specified websites")
            elif tool == 'textanalyzer':
                steps.append(f"{i}. Analyze text content for insights")
            elif tool == 'write_tool':
                steps.append(f"{i}. Create and save output files")
            else:
                steps.append(f"{i}. Execute {tool} for required functionality")
        
        return '\n'.join(steps)
    
    def _generate_expected_outcomes(self, analysis: QueryAnalysis) -> str:
        """Generate expected outcomes description."""
        query_type = getattr(analysis, 'query_type', 'general')
        tools_required = getattr(analysis, 'tools_required', [])
        
        if query_type == 'question':
            return "Comprehensive answer to the user's question with supporting evidence."
        elif query_type == 'command':
            return "Successful execution of the requested command with confirmation."
        elif 'write_tool' in tools_required:
            return "Generated files with requested content saved to specified locations."
        elif 'calculator' in tools_required:
            return "Accurate mathematical results with step-by-step calculations."
        else:
            return "Successful completion of requested task with relevant output."
    
    def _generate_success_criteria(self, analysis: QueryAnalysis) -> str:
        """Generate success criteria for the execution."""
        criteria = [
            "✓ All required tools execute successfully",
            "✓ Output meets user requirements", 
            "✓ No critical errors encountered"
        ]
        
        tools_required = getattr(analysis, 'tools_required', [])
        
        if 'google_search' in tools_required:
            criteria.append("✓ Relevant search results obtained")
        if 'calculator' in tools_required:
            criteria.append("✓ Calculations completed accurately")
        if 'write_tool' in tools_required:
            criteria.append("✓ Files created and saved successfully")
        if 'textanalyzer' in tools_required:
            criteria.append("✓ Text analysis provides meaningful insights")
        
        return '\n'.join(criteria)
    
    def _initialize_progress_file(self, file_path: str):
        """Initialize progress tracking file."""
        progress = {
            'session_started': datetime.now().isoformat(),
            'current_step': 0,
            'completed_tasks': [],
            'overall_status': 'initialized',
            'errors': []
        }
        
        with open(file_path, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def _generate_task_list_file(self, analysis: QueryAnalysis, file_path: str):
        """Generate task list file."""
        task_content = f"""# Task List

{self._generate_task_list(analysis)}

## Tool Requirements
{self._generate_tool_requirements(analysis)}

Generated: {datetime.now().isoformat()}
"""
        
        with open(file_path, 'w') as f:
            f.write(task_content)
    
    def _generate_tool_requirements(self, analysis: QueryAnalysis) -> str:
        """Generate tool requirements section."""
        tools_required = getattr(analysis, 'tools_required', [])
        
        if not tools_required:
            return "No specific tools required - direct response."
        
        requirements = []
        for tool in tools_required:
            if tool == 'google_search':
                requirements.append("- Google Search: API key required for web search")
            elif tool == 'calculator':
                requirements.append("- Calculator: Mathematical computation capability")
            elif tool == 'webscrapertool':
                requirements.append("- Web Scraper: Website content extraction")
            elif tool == 'textanalyzer':
                requirements.append("- Text Analyzer: Natural language processing")
            elif tool == 'write_tool':
                requirements.append("- Write Tool: File creation and writing permissions")
            else:
                requirements.append(f"- {tool}: Specialized functionality")
        
        return '\n'.join(requirements)