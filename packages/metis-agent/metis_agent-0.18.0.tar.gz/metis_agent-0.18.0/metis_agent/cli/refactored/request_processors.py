"""
Natural language request processing for CLI commands.

Handles parsing, routing, and processing of natural language requests.
"""
import os
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime


class RequestProcessor:
    """Processes natural language requests and routes them to appropriate handlers."""
    
    def __init__(self):
        self.request_patterns = self._initialize_patterns()
        self.context_cache = {}
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize request pattern recognition."""
        return {
            'create_project': [
                r'create\s+(?:a\s+)?(?:new\s+)?project',
                r'start\s+(?:a\s+)?(?:new\s+)?project', 
                r'initialize\s+(?:a\s+)?project',
                r'setup\s+(?:a\s+)?(?:new\s+)?project',
                r'build\s+(?:a\s+)?(?:new\s+)?(?:application|app|tool)'
            ],
            'modify_code': [
                r'(?:add|modify|update|change|edit|fix)\s+.*(?:function|method|class|code)',
                r'refactor.*(?:code|function|method|class)',
                r'implement.*(?:function|method|feature)',
                r'debug.*(?:issue|problem|error|bug)',
                r'optimize.*(?:code|performance|function)'
            ],
            'analyze_code': [
                r'(?:analyze|review|examine|check|inspect)\s+.*(?:code|file|project)',
                r'(?:find|search\s+for|look\s+for)\s+.*(?:function|method|class|pattern)',
                r'(?:explain|describe|document)\s+.*(?:code|function|how.*works)',
                r'(?:test|validate|verify)\s+.*(?:code|function|feature)'
            ],
            'file_operations': [
                r'(?:read|open|view|show)\s+.*(?:file|directory)',
                r'(?:write|create|make|generate)\s+.*(?:file|script)',
                r'(?:delete|remove|move|copy)\s+.*(?:file|directory)',
                r'(?:list|show|display)\s+.*(?:files|contents|directory)'
            ],
            'git_operations': [
                r'(?:commit|push|pull|merge|branch|checkout)',
                r'(?:git|version\s+control)',
                r'(?:create|switch\s+to|delete)\s+.*branch',
                r'(?:merge|rebase)\s+.*branch'
            ]
        }
    
    def process_request(self, request_text: str, session: Optional[str] = None,
                       branch: Optional[str] = None, no_branch: bool = False,
                       auto: bool = False, interface_mode: str = 'balanced') -> Dict[str, Any]:
        """
        Process a natural language request.
        
        Args:
            request_text: The user's natural language request
            session: Optional session ID
            branch: Optional branch name
            no_branch: Skip branch creation
            auto: Auto mode flag
            interface_mode: Interface mode to use
            
        Returns:
            Processing result dictionary
        """
        # Analyze the request
        analysis = self._analyze_request(request_text)
        
        # Extract entities and parameters
        entities = self._extract_entities(request_text, analysis)
        
        # Determine processing strategy
        strategy = self._determine_strategy(analysis, entities, auto, interface_mode)
        
        # Prepare context
        context = self._prepare_context(
            request_text, analysis, entities, session, branch, no_branch
        )
        
        return {
            'request_text': request_text,
            'analysis': analysis,
            'entities': entities,
            'strategy': strategy,
            'context': context,
            'processing_mode': interface_mode,
            'requires_agent': True,
            'estimated_complexity': self._estimate_complexity(request_text, analysis)
        }
    
    def _analyze_request(self, request_text: str) -> Dict[str, Any]:
        """Analyze the request to determine intent and complexity."""
        request_lower = request_text.lower()
        
        analysis = {
            'primary_intent': None,
            'secondary_intents': [],
            'confidence': 0.0,
            'complexity': 'medium',
            'requires_context': False,
            'involves_files': False,
            'involves_git': False,
            'is_question': False,
            'is_command': True
        }
        
        # Pattern matching for intent detection
        max_confidence = 0.0
        for intent, patterns in self.request_patterns.items():
            for pattern in patterns:
                if re.search(pattern, request_lower):
                    confidence = self._calculate_pattern_confidence(pattern, request_lower)
                    if confidence > max_confidence:
                        analysis['primary_intent'] = intent
                        max_confidence = confidence
                    elif confidence > 0.5:
                        analysis['secondary_intents'].append(intent)
        
        analysis['confidence'] = max_confidence
        
        # Additional analysis
        analysis['is_question'] = any(
            request_text.strip().endswith(q) or request_text.strip().startswith(q)
            for q in ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        )
        
        analysis['involves_files'] = bool(re.search(
            r'(?:file|\.py|\.js|\.java|\.cpp|\.c|\.go|\.rs|\.rb|\.php|\.md|\.txt|\.json)',
            request_lower
        ))
        
        analysis['involves_git'] = bool(re.search(
            r'(?:git|commit|push|pull|merge|branch|checkout|repository|repo)',
            request_lower
        ))
        
        analysis['requires_context'] = any([
            'this' in request_lower,
            'current' in request_lower,
            'existing' in request_lower,
            analysis['involves_files']
        ])
        
        # Complexity estimation
        complexity_indicators = {
            'simple': ['show', 'list', 'read', 'view', 'display'],
            'medium': ['create', 'add', 'modify', 'update', 'fix', 'implement'],
            'complex': ['refactor', 'optimize', 'analyze', 'migrate', 'integrate', 'architecture']
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in request_lower for indicator in indicators):
                analysis['complexity'] = complexity
                break
        
        return analysis
    
    def _calculate_pattern_confidence(self, pattern: str, text: str) -> float:
        """Calculate confidence score for pattern match."""
        match = re.search(pattern, text)
        if not match:
            return 0.0
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on match quality
        match_length = len(match.group(0))
        text_length = len(text)
        
        # Longer matches in shorter text = higher confidence
        length_ratio = match_length / text_length
        confidence += min(length_ratio * 0.3, 0.3)
        
        return min(confidence, 1.0)
    
    def _extract_entities(self, request_text: str, analysis: Dict) -> Dict[str, Any]:
        """Extract entities and parameters from the request."""
        entities = {
            'file_paths': [],
            'file_types': [],
            'programming_languages': [],
            'functions_methods': [],
            'technologies': [],
            'actions': [],
            'modifiers': []
        }
        
        # Extract file paths and types
        file_patterns = [
            r'[a-zA-Z_][a-zA-Z0-9_/\\.-]*\.[a-zA-Z]{1,4}',  # file.ext
            r'[a-zA-Z_][a-zA-Z0-9_/\\.-]*/',  # directory/
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, request_text)
            entities['file_paths'].extend(matches)
        
        # Extract programming languages
        languages = ['python', 'javascript', 'java', 'cpp', 'c++', 'go', 'rust', 'ruby', 'php']
        for lang in languages:
            if lang.lower() in request_text.lower():
                entities['programming_languages'].append(lang)
        
        # Extract function/method names
        function_patterns = [
            r'(?:function|method)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, request_text)
            entities['functions_methods'].extend(matches)
        
        # Extract action verbs
        action_patterns = [
            r'(?:^|\s)(create|add|modify|update|delete|remove|implement|build|generate|write|read|analyze|test|debug|fix|refactor|optimize)(?:\s|$)',
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, request_text.lower())
            entities['actions'].extend(matches)
        
        return entities
    
    def _determine_strategy(self, analysis: Dict, entities: Dict, auto: bool, 
                          interface_mode: str) -> Dict[str, Any]:
        """Determine the processing strategy based on analysis."""
        strategy = {
            'approach': 'interactive',
            'tools_needed': [],
            'confirmation_required': True,
            'streaming_recommended': False,
            'batch_processing': False
        }
        
        # Determine approach based on complexity and mode
        if auto or interface_mode == 'simple':
            strategy['approach'] = 'direct'
            strategy['confirmation_required'] = False
        elif analysis['complexity'] == 'complex' or interface_mode == 'streaming':
            strategy['approach'] = 'streaming'
            strategy['streaming_recommended'] = True
        elif interface_mode == 'expert':
            strategy['approach'] = 'advanced'
            strategy['confirmation_required'] = False
        
        # Determine tools needed based on intent
        intent_tools = {
            'create_project': ['WriteTool', 'FileManagerTool', 'ProjectManagementTool'],
            'modify_code': ['ReadTool', 'WriteTool', 'GrepTool'],
            'analyze_code': ['ReadTool', 'GrepTool', 'ProjectAnalyzerTool'],
            'file_operations': ['ReadTool', 'WriteTool', 'FileManagerTool'],
            'git_operations': ['BashTool']
        }
        
        if analysis['primary_intent'] in intent_tools:
            strategy['tools_needed'] = intent_tools[analysis['primary_intent']]
        
        # Additional tools based on entities
        if entities['file_paths']:
            strategy['tools_needed'].extend(['ReadTool', 'WriteTool'])
        
        if 'test' in analysis.get('primary_intent', '') or 'test' in entities.get('actions', []):
            strategy['tools_needed'].append('BashTool')
        
        # Remove duplicates
        strategy['tools_needed'] = list(set(strategy['tools_needed']))
        
        return strategy
    
    def _prepare_context(self, request_text: str, analysis: Dict, entities: Dict,
                        session: Optional[str], branch: Optional[str], 
                        no_branch: bool) -> Dict[str, Any]:
        """Prepare context for request processing."""
        context = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session,
            'branch_requested': branch,
            'skip_branch': no_branch,
            'working_directory': os.getcwd(),
            'project_context': self._get_project_context(),
            'file_context': {},
            'git_context': {}
        }
        
        # Add file context if specific files mentioned
        if entities['file_paths']:
            context['file_context'] = self._gather_file_context(entities['file_paths'])
        
        # Add git context if git operations involved
        if analysis['involves_git']:
            context['git_context'] = self._gather_git_context()
        
        return context
    
    def _estimate_complexity(self, request_text: str, analysis: Dict) -> Dict[str, Any]:
        """Estimate the complexity and resource requirements of the request."""
        return {
            'level': analysis['complexity'],
            'estimated_time': self._estimate_time(analysis),
            'resource_intensive': analysis['complexity'] == 'complex',
            'requires_user_input': analysis['requires_context'] and 'this' in request_text.lower(),
            'multi_step': bool(re.search(r'(?:and|then|after|next|also)', request_text.lower()))
        }
    
    def _estimate_time(self, analysis: Dict) -> str:
        """Estimate time required for request."""
        time_map = {
            'simple': '< 30 seconds',
            'medium': '30 seconds - 2 minutes', 
            'complex': '2+ minutes'
        }
        return time_map.get(analysis['complexity'], 'unknown')
    
    def _get_project_context(self) -> Dict:
        """Get current project context."""
        # This would integrate with project_handlers
        return {
            'current_directory': os.getcwd(),
            'has_files': bool(os.listdir(os.getcwd())) if os.path.exists(os.getcwd()) else False
        }
    
    def _gather_file_context(self, file_paths: List[str]) -> Dict:
        """Gather context about mentioned files."""
        file_context = {}
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                file_context[file_path] = {
                    'exists': True,
                    'is_file': os.path.isfile(file_path),
                    'is_directory': os.path.isdir(file_path),
                    'size': os.path.getsize(file_path) if os.path.isfile(file_path) else None
                }
            else:
                file_context[file_path] = {'exists': False}
        
        return file_context
    
    def _gather_git_context(self) -> Dict:
        """Gather git context information."""
        git_context = {'available': False}
        
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                git_context.update({
                    'available': True,
                    'has_changes': bool(result.stdout.strip()),
                    'clean': not bool(result.stdout.strip())
                })
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        
        return git_context