"""
Query analysis and complexity assessment components.

Handles analysis of user queries and task complexity evaluation.
"""
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models import QueryAnalysis, ExecutionResult


class QueryAnalyzer:
    """Analyzes user queries to determine execution requirements."""
    
    def __init__(self, orchestrator):
        """Initialize with reference to main orchestrator."""
        self.orchestrator = orchestrator
        self.analysis_history = []
    
    def analyze_query(self, query: str, context: Dict = None) -> QueryAnalysis:
        """
        Analyze a user query to determine execution requirements.
        
        Args:
            query: User query to analyze
            context: Additional context information
            
        Returns:
            QueryAnalysis with requirements and metadata
        """
        analysis = QueryAnalysis()
        query_lower = query.lower().strip()
        
        # Basic query classification
        analysis.query_type = self._classify_query_type(query_lower)
        analysis.complexity = self._assess_complexity(query_lower)
        analysis.tools_required = self._identify_required_tools(query_lower)
        analysis.parameters = self._extract_parameters(query, context or {})
        analysis.confidence = self._calculate_confidence(query, analysis)
        
        # Additional metadata
        analysis.metadata = {
            'query_length': len(query),
            'word_count': len(query.split()),
            'has_questions': '?' in query,
            'has_code_request': self._has_code_request(query_lower),
            'has_file_operations': self._has_file_operations(query_lower),
            'urgency': self._assess_urgency(query_lower),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Record analysis
        self.analysis_history.append({
            'query': query,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
        return analysis
    
    def _classify_query_type(self, query_lower: str) -> str:
        """Classify the type of query."""
        # Question patterns
        question_starters = ['what', 'who', 'when', 'where', 'why', 'how', 'which', 'can you']
        if any(query_lower.startswith(starter) for starter in question_starters) or '?' in query_lower:
            return 'question'
        
        # Command patterns
        command_verbs = ['create', 'make', 'build', 'generate', 'write', 'implement', 'develop']
        if any(verb in query_lower for verb in command_verbs):
            return 'command'
        
        # Request patterns
        request_patterns = ['please', 'could you', 'would you', 'can you help', 'i need', 'i want']
        if any(pattern in query_lower for pattern in request_patterns):
            return 'request'
        
        # Analysis patterns
        analysis_verbs = ['analyze', 'examine', 'review', 'check', 'evaluate', 'assess']
        if any(verb in query_lower for verb in analysis_verbs):
            return 'analysis'
        
        return 'general'
    
    def _assess_complexity(self, query_lower: str) -> str:
        """Assess the complexity of the query."""
        complexity_indicators = {
            'simple': ['what is', 'who is', 'when was', 'define', 'explain simply'],
            'medium': ['how to', 'create a', 'make a', 'build a', 'analyze', 'compare'],
            'complex': ['implement', 'develop', 'architecture', 'system', 'integrate', 'optimize']
        }
        
        # Count indicators
        scores = {}
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in query_lower)
            if score > 0:
                scores[level] = score
        
        if not scores:
            # Fallback to word count and sentence complexity
            word_count = len(query_lower.split())
            if word_count < 5:
                return 'simple'
            elif word_count < 15:
                return 'medium'
            else:
                return 'complex'
        
        # Return highest scoring complexity level
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _identify_required_tools(self, query_lower: str) -> List[str]:
        """Identify tools required for the query."""
        tools_needed = []
        
        # Tool identification patterns
        tool_patterns = {
            'calculator': ['calculate', 'compute', 'math', 'arithmetic', 'sum', 'multiply', 'divide'],
            'google_search': ['search', 'find information', 'look up', 'research'],
            'webscrapertool': ['scrape', 'extract from website', 'get data from', 'website content'],
            'firecrawl': ['crawl website', 'get all pages', 'site content', 'web crawl'],
            'write_tool': ['write file', 'create file', 'save to file', 'output to file'],
            'read_tool': ['read file', 'open file', 'view file', 'file content'],
            'edit_tool': ['edit file', 'modify file', 'update file', 'change file'],
            'textanalyzer': ['analyze text', 'text analysis', 'sentiment', 'extract keywords'],
            'datavalidator': ['validate data', 'check data', 'verify data', 'data validation'],
            'bash_tool': ['run command', 'execute', 'terminal', 'command line', 'shell'],
            'project_management_tool': ['project', 'manage project', 'project structure'],
            'e2b_code_sandbox': ['run code', 'execute code', 'test code', 'code sandbox'],
        }
        
        for tool_name, patterns in tool_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                tools_needed.append(tool_name)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(tools_needed))
    
    def _extract_parameters(self, query: str, context: Dict) -> Dict[str, Any]:
        """Extract parameters from the query."""
        parameters = {}
        
        # Extract file paths
        file_patterns = [
            r'[\'"]([^\'\"]*\.[a-zA-Z]{2,4})[\'"]',  # Quoted file paths
            r'(?:file|path|document):\s*([^\s]+)',   # file: path
            r'([a-zA-Z0-9_/\\.-]+\.[a-zA-Z]{2,4})'   # Unquoted file paths
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, query)
            if matches:
                parameters['file_paths'] = matches
                break
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+|www\.[^\s]+'
        urls = re.findall(url_pattern, query)
        if urls:
            parameters['urls'] = urls
        
        # Extract numbers
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, query)
        if numbers:
            parameters['numbers'] = [float(n) if '.' in n else int(n) for n in numbers]
        
        # Extract quoted strings
        quoted_pattern = r'[\'"]([^\'"]+)[\'"]'
        quoted_strings = re.findall(quoted_pattern, query)
        if quoted_strings:
            parameters['quoted_strings'] = quoted_strings
        
        # Extract programming languages
        language_pattern = r'\b(python|javascript|java|cpp|c\+\+|go|rust|ruby|php)\b'
        languages = re.findall(language_pattern, query.lower())
        if languages:
            parameters['languages'] = languages
        
        # Context-based parameters
        if context:
            parameters['context_session_id'] = context.get('session_id')
            parameters['context_project'] = context.get('project_location')
        
        return parameters
    
    def _calculate_confidence(self, query: str, analysis: QueryAnalysis) -> float:
        """Calculate confidence in the analysis."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for clear patterns
        if analysis.tools_required:
            confidence += 0.2
        
        if analysis.query_type in ['question', 'command']:
            confidence += 0.2
        
        if analysis.parameters:
            confidence += 0.1
        
        # Reduce confidence for ambiguous queries
        ambiguous_words = ['thing', 'stuff', 'something', 'anything', 'it', 'this', 'that']
        query_lower = query.lower()
        ambiguous_count = sum(1 for word in ambiguous_words if word in query_lower)
        confidence -= ambiguous_count * 0.05
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))
    
    def _has_code_request(self, query_lower: str) -> bool:
        """Check if query involves code generation or manipulation."""
        code_indicators = [
            'write code', 'generate code', 'create function', 'implement',
            'code example', 'programming', 'script', 'algorithm'
        ]
        return any(indicator in query_lower for indicator in code_indicators)
    
    def _has_file_operations(self, query_lower: str) -> bool:
        """Check if query involves file operations."""
        file_indicators = [
            'file', 'read', 'write', 'save', 'load', 'open',
            'create file', 'delete file', 'modify file'
        ]
        return any(indicator in query_lower for indicator in file_indicators)
    
    def _assess_urgency(self, query_lower: str) -> str:
        """Assess the urgency of the query."""
        urgent_indicators = ['urgent', 'asap', 'immediately', 'quickly', 'fast', 'now']
        normal_indicators = ['when possible', 'eventually', 'later']
        
        if any(indicator in query_lower for indicator in urgent_indicators):
            return 'high'
        elif any(indicator in query_lower for indicator in normal_indicators):
            return 'low'
        else:
            return 'normal'
    
    def get_status(self) -> Dict[str, Any]:
        """Get analyzer status."""
        return {
            'queries_analyzed': len(self.analysis_history),
            'component': 'QueryAnalyzer',
            'status': 'active'
        }


class ComplexityAnalyzer:
    """Analyzes task complexity for blueprint and optimization opportunities."""
    
    def __init__(self, orchestrator):
        """Initialize with reference to main orchestrator."""
        self.orchestrator = orchestrator
        self.complexity_assessments = []
    
    def analyze_task_complexity(self, task: str, execution_result: ExecutionResult = None) -> bool:
        """
        Analyze if a task is complex enough for blueprint creation.
        
        Args:
            task: Task description
            execution_result: Optional execution result
            
        Returns:
            True if task is complex enough for blueprint creation
        """
        complexity_score = self._calculate_complexity_score(task, execution_result)
        
        # Record assessment
        assessment = {
            'task': task,
            'complexity_score': complexity_score,
            'is_complex': complexity_score >= 0.7,
            'timestamp': datetime.now().isoformat()
        }
        
        if execution_result:
            assessment.update({
                'execution_success': execution_result.success,
                'tools_used_count': len(execution_result.tools_used),
                'execution_time': str(execution_result.execution_time)
            })
        
        self.complexity_assessments.append(assessment)
        
        return complexity_score >= 0.7
    
    def _calculate_complexity_score(self, task: str, execution_result: ExecutionResult = None) -> float:
        """Calculate complexity score for a task."""
        score = 0.0
        task_lower = task.lower()
        
        # Task description complexity
        word_count = len(task.split())
        if word_count > 20:
            score += 0.2
        elif word_count > 10:
            score += 0.1
        
        # Multi-step indicators
        step_indicators = ['then', 'after', 'next', 'following', 'subsequently', 'and']
        step_count = sum(1 for indicator in step_indicators if indicator in task_lower)
        score += min(step_count * 0.15, 0.3)
        
        # Technical complexity indicators
        complex_terms = [
            'integrate', 'architecture', 'system', 'framework', 'optimize',
            'algorithm', 'database', 'api', 'microservice', 'deployment'
        ]
        complex_count = sum(1 for term in complex_terms if term in task_lower)
        score += min(complex_count * 0.1, 0.3)
        
        # Execution result factors
        if execution_result:
            # Multiple tools used
            tool_count = len(execution_result.tools_used)
            if tool_count > 3:
                score += 0.2
            elif tool_count > 1:
                score += 0.1
            
            # Long execution time
            if hasattr(execution_result, 'execution_time'):
                exec_time = execution_result.execution_time
                if hasattr(exec_time, 'total_seconds'):
                    seconds = exec_time.total_seconds()
                    if seconds > 30:
                        score += 0.2
                    elif seconds > 10:
                        score += 0.1
            
            # Complex result (long output)
            if execution_result.result and len(str(execution_result.result)) > 500:
                score += 0.1
        
        return min(score, 1.0)
    
    def get_complexity_statistics(self) -> Dict[str, Any]:
        """Get statistics about complexity assessments."""
        if not self.complexity_assessments:
            return {'assessments_count': 0}
        
        total_assessments = len(self.complexity_assessments)
        complex_tasks = sum(1 for assessment in self.complexity_assessments if assessment['is_complex'])
        
        avg_complexity_score = sum(
            assessment['complexity_score'] for assessment in self.complexity_assessments
        ) / total_assessments
        
        return {
            'assessments_count': total_assessments,
            'complex_tasks_count': complex_tasks,
            'complexity_rate': complex_tasks / total_assessments,
            'average_complexity_score': avg_complexity_score,
            'recent_assessments': self.complexity_assessments[-5:] if len(self.complexity_assessments) > 5 else self.complexity_assessments
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get complexity analyzer status."""
        return {
            'assessments_performed': len(self.complexity_assessments),
            'component': 'ComplexityAnalyzer',
            'status': 'active'
        }