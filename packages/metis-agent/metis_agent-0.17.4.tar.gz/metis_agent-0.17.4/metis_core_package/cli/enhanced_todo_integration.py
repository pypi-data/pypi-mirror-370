"""
Enhanced TODO Integration for Metis Code
Provides seamless, natural language TODO management without flags
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

try:
    from .todo_commands import TodoCLI, auto_create_todos_for_request
    from ..tools.core_tools.todo_management_tool import TodoManagementTool, TaskStatus, TaskPriority
except ImportError:
    TodoCLI = None
    TodoManagementTool = None
    auto_create_todos_for_request = None


@dataclass
class ComplexityAnalysis:
    """Analysis of request complexity for TODO planning"""
    complexity_score: float
    should_create_todos: bool
    project_type: str
    estimated_duration_hours: float
    key_components: List[str]
    technical_stack: List[str]
    reasoning: str


class EnhancedTodoIntegration:
    """Enhanced TODO integration for natural language processing"""
    
    def __init__(self):
        self.todo_cli = TodoCLI() if TodoCLI else None
        self.todo_tool = TodoManagementTool() if TodoManagementTool else None
        self.complexity_patterns = self._initialize_complexity_patterns()
        self.project_type_patterns = self._initialize_project_patterns()
        
    def _initialize_complexity_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for detecting request complexity"""
        return {
            'high_complexity_indicators': {
                'patterns': [
                    r'full.?stack',
                    r'end.?to.?end',
                    r'complete\s+(application|system|platform)',
                    r'microservices?',
                    r'authentication\s+and\s+authorization',
                    r'database\s+and\s+api',
                    r'frontend\s+and\s+backend',
                    r'deployment\s+pipeline',
                    r'ci/cd',
                    r'scalable\s+system'
                ],
                'weight': 3.0
            },
            'medium_complexity_indicators': {
                'patterns': [
                    r'web\s+application',
                    r'api\s+service',
                    r'rest\s+api',
                    r'graphql\s+api',
                    r'react\s+app',
                    r'vue\s+app',
                    r'angular\s+app',
                    r'fastapi\s+backend',
                    r'flask\s+app',
                    r'django\s+app',
                    r'node\.?js\s+server',
                    r'machine\s+learning\s+model',
                    r'data\s+pipeline',
                    r'dashboard',
                    r'crud\s+operations'
                ],
                'weight': 2.0
            },
            'component_indicators': {
                'patterns': [
                    r'authentication',
                    r'user\s+management',
                    r'database\s+schema',
                    r'api\s+endpoints',
                    r'frontend\s+components',
                    r'testing\s+suite',
                    r'deployment\s+setup',
                    r'documentation',
                    r'error\s+handling',
                    r'validation',
                    r'security'
                ],
                'weight': 1.0
            },
            'technology_stack_indicators': {
                'patterns': [
                    r'react|vue|angular|svelte',
                    r'node\.?js|express|fastapi|flask|django',
                    r'postgresql|mysql|mongodb|sqlite',
                    r'redis|elasticsearch|kafka',
                    r'docker|kubernetes|aws|azure|gcp',
                    r'typescript|javascript|python|java|go'
                ],
                'weight': 0.5
            }
        }
    
    def _initialize_project_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for project type detection"""
        return {
            'full_stack_web_app': {
                'indicators': ['full stack', 'web application', 'frontend and backend', 'react', 'vue', 'angular'],
                'estimated_hours': 15,
                'key_phases': ['setup', 'backend', 'frontend', 'integration', 'deployment']
            },
            'api_service': {
                'indicators': ['api', 'rest api', 'graphql', 'microservice', 'backend service'],
                'estimated_hours': 8,
                'key_phases': ['design', 'implementation', 'testing', 'documentation']
            },
            'data_analysis_project': {
                'indicators': ['machine learning', 'data analysis', 'data pipeline', 'ml model', 'analytics'],
                'estimated_hours': 12,
                'key_phases': ['data collection', 'preprocessing', 'analysis', 'modeling', 'visualization']
            },
            'frontend_application': {
                'indicators': ['react app', 'vue app', 'angular app', 'frontend', 'ui', 'dashboard'],
                'estimated_hours': 10,
                'key_phases': ['setup', 'components', 'state management', 'styling', 'testing']
            },
            'automation_script': {
                'indicators': ['script', 'automation', 'tool', 'utility', 'cli'],
                'estimated_hours': 4,
                'key_phases': ['planning', 'implementation', 'testing', 'documentation']
            }
        }
    
    def analyze_request_complexity(self, request_text: str) -> ComplexityAnalysis:
        """
        Analyze request complexity to determine if TODO breakdown is needed
        """
        request_lower = request_text.lower()
        complexity_score = 0.0
        key_components = []
        technical_stack = []
        reasoning_parts = []
        
        # Analyze complexity indicators
        for category, data in self.complexity_patterns.items():
            patterns = data['patterns']
            weight = data['weight']
            matches = []
            
            for pattern in patterns:
                if re.search(pattern, request_lower):
                    matches.append(pattern)
                    complexity_score += weight
                    
                    if category == 'component_indicators':
                        key_components.append(pattern.replace(r'\s+', ' ').replace(r'\.?\?', ''))
                    elif category == 'technology_stack_indicators':
                        technical_stack.append(pattern.replace(r'\s+', ' ').replace(r'\.?\?', ''))
            
            if matches:
                reasoning_parts.append(f"{category}: {len(matches)} matches")
        
        # Determine project type
        project_type = self._detect_project_type(request_lower)
        
        # Estimate duration based on project type and complexity
        estimated_hours = self._estimate_duration(project_type, complexity_score)
        
        # Decision threshold for TODO creation (more restrictive)
        should_create_todos = complexity_score >= 2.5 or estimated_hours >= 8.0
        
        reasoning = f"Complexity score: {complexity_score:.1f}, Estimated duration: {estimated_hours}h. " + "; ".join(reasoning_parts)
        
        return ComplexityAnalysis(
            complexity_score=complexity_score,
            should_create_todos=should_create_todos,
            project_type=project_type,
            estimated_duration_hours=estimated_hours,
            key_components=key_components,
            technical_stack=technical_stack,
            reasoning=reasoning
        )
    
    def _detect_project_type(self, request_lower: str) -> str:
        """Detect the type of project from request"""
        best_match = 'general_development'
        max_matches = 0
        
        for project_type, data in self.project_type_patterns.items():
            matches = sum(1 for indicator in data['indicators'] if indicator in request_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = project_type
        
        return best_match
    
    def _estimate_duration(self, project_type: str, complexity_score: float) -> float:
        """Estimate project duration in hours"""
        base_hours = self.project_type_patterns.get(project_type, {}).get('estimated_hours', 6)
        
        # Adjust based on complexity score
        complexity_multiplier = min(1.0 + (complexity_score * 0.2), 2.0)
        
        return base_hours * complexity_multiplier
    
    def check_active_todo_session(self) -> Optional[Dict[str, Any]]:
        """Check if there's an active TODO session"""
        if not self.todo_cli:
            return None
            
        try:
            # Get list of sessions and check if any are active
            sessions_result = self.todo_cli.handle_command('list sessions')
            
            # Parse the result to find active sessions
            # This is a simplified check - in reality you'd parse the actual session data
            if 'active' in sessions_result.lower():
                return {'name': 'Active Session', 'has_active': True}
        except Exception:
            pass
            
        return None
    
    def find_related_task(self, request_text: str, active_session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find task in active session related to current request"""
        if not self.todo_cli:
            return None
            
        try:
            # Get current tasks
            tasks_result = self.todo_cli.handle_command('list tasks')
            
            # Simple keyword matching - in reality you'd do more sophisticated matching
            request_keywords = request_text.lower().split()
            common_keywords = ['authentication', 'database', 'frontend', 'backend', 'testing', 'deployment']
            
            for keyword in common_keywords:
                if keyword in request_text.lower() and keyword in tasks_result.lower():
                    return {
                        'title': f'Task related to {keyword}',
                        'id': 'task-001',
                        'status': 'pending'
                    }
        except Exception:
            pass
            
        return None
    
    def create_smart_todo_session(self, request_text: str, analysis: ComplexityAnalysis) -> Optional[str]:
        """Create TODO session with smart naming and breakdown"""
        if not self.todo_cli:
            return None
            
        try:
            # Generate smart session name
            session_name = self._generate_session_name(request_text, analysis)
            
            # Create session
            session_result = self.todo_cli.handle_command(
                'create session',
                name=session_name,
                description=f"Auto-generated from: {request_text}\nProject type: {analysis.project_type}\nEstimated duration: {analysis.estimated_duration_hours:.1f}h"
            )
            
            if 'Created TODO session' in session_result:
                # Create breakdown
                breakdown_result = self.todo_cli.handle_command(
                    'breakdown request',
                    request=request_text
                )
                
                return f"""🗂️  PROJECT PLANNING

{session_result}

📋 Breakdown for "{analysis.project_type.replace('_', ' ').title()}" project:
{breakdown_result}

🚀 Starting with the first task..."""
                
        except Exception as e:
            print(f"Error creating TODO session: {e}")
            
        return None
    
    def _generate_session_name(self, request_text: str, analysis: ComplexityAnalysis) -> str:
        """Generate a smart session name"""
        # Extract key terms from request
        words = request_text.split()
        important_words = []
        
        # Common important words for project naming
        key_terms = ['app', 'application', 'system', 'service', 'platform', 'tool', 'dashboard', 'api', 'website']
        
        for word in words:
            if (word.lower() in key_terms or 
                len(word) > 6 or 
                word.lower() in analysis.technical_stack):
                important_words.append(word.title())
        
        if important_words:
            return ' '.join(important_words[:3])
        else:
            return f"{analysis.project_type.replace('_', ' ').title()} Project"
    
    def update_task_progress_from_response(self, task_info: Dict[str, Any], response: str) -> bool:
        """Update task progress based on agent response"""
        if not self.todo_cli or not task_info:
            return False
            
        # Analyze response for completion indicators
        completion_indicators = [
            'completed', 'finished', 'done', 'implemented', 'created',
            'successfully', 'working', 'ready', 'set up', 'configured'
        ]
        
        progress_indicators = [
            'started', 'began', 'initiated', 'in progress', 'working on'
        ]
        
        response_lower = response.lower()
        
        # Check for completion
        completion_score = sum(1 for indicator in completion_indicators if indicator in response_lower)
        progress_score = sum(1 for indicator in progress_indicators if indicator in response_lower)
        
        try:
            if completion_score >= 2:  # High confidence of completion
                self.todo_cli.handle_command(
                    'update task',
                    task_id=task_info['id'],
                    status='completed'
                )
                return True
            elif progress_score >= 1 or completion_score >= 1:  # Some progress
                self.todo_cli.handle_command(
                    'update task',
                    task_id=task_info['id'],
                    status='in_progress'
                )
                return True
        except Exception:
            pass
            
        return False
    
    def get_next_task_suggestion(self, active_session: Dict[str, Any]) -> Optional[str]:
        """Get suggestion for next task"""
        if not self.todo_cli:
            return None
            
        try:
            next_result = self.todo_cli.handle_command('next task')
            if next_result and 'No tasks ready' not in next_result:
                return f"🎯 Next suggested task: {next_result}"
        except Exception:
            pass
            
        return None
    
    def get_progress_summary(self, active_session: Dict[str, Any]) -> Optional[str]:
        """Get progress summary for active session"""
        if not self.todo_cli:
            return None
            
        try:
            progress_result = self.todo_cli.handle_command('progress')
            return f"📊 Progress: {progress_result}"
        except Exception:
            pass
            
        return None


# Global instance for easy import
enhanced_todo_integration = EnhancedTodoIntegration()