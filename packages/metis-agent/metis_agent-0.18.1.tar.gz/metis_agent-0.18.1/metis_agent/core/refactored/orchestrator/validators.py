"""
Tool validation and result verification components.

Handles validation of tools and verification of execution results.
"""
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ...tools.registry import get_tool


class ToolValidator:
    """Validates tool requirements and execution."""
    
    def __init__(self, orchestrator):
        """Initialize with reference to main orchestrator."""
        self.orchestrator = orchestrator
        self.validation_history = []
    
    def validate_tool_requirements(self, tool_name: str, tool_instance, 
                                  context: Dict) -> Tuple[bool, str]:
        """
        Validate tool requirements before execution.
        
        Args:
            tool_name: Name of the tool
            tool_instance: Tool instance or class
            context: Execution context
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if tool instance is valid
            if not tool_instance:
                return False, f"Tool {tool_name} not found or failed to load"
            
            # Check API key requirements
            api_keys = context.get('api_keys', {})
            required_keys = self._get_required_api_keys(tool_name)
            
            for key_name in required_keys:
                if key_name not in api_keys or not api_keys[key_name]:
                    return False, f"Tool {tool_name} requires API key: {key_name}"
            
            # Check file system permissions if needed
            if self._requires_file_access(tool_name):
                if not self._check_file_permissions(context):
                    return False, f"Tool {tool_name} requires file system access permissions"
            
            # Check network access if needed
            if self._requires_network_access(tool_name):
                if not self._check_network_connectivity():
                    return False, f"Tool {tool_name} requires network access"
            
            # Tool-specific validations
            validation_result = self._perform_tool_specific_validation(
                tool_name, tool_instance, context
            )
            
            if not validation_result[0]:
                return validation_result
            
            # Record successful validation
            self.validation_history.append({
                'tool_name': tool_name,
                'validation_result': True,
                'timestamp': datetime.now().isoformat(),
                'context_session_id': context.get('session_id')
            })
            
            return True, "Validation successful"
            
        except Exception as e:
            error_msg = f"Tool validation failed: {str(e)}"
            
            # Record failed validation
            self.validation_history.append({
                'tool_name': tool_name,
                'validation_result': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat(),
                'context_session_id': context.get('session_id')
            })
            
            return False, error_msg
    
    def execute_tool_with_validation(self, tool_name: str, tool, query: str, 
                                    context: Dict) -> Tuple[bool, Any]:
        """
        Execute tool with validation and error handling.
        
        Args:
            tool_name: Name of the tool
            tool: Tool instance
            query: Query to execute
            context: Execution context
            
        Returns:
            Tuple of (success, result)
        """
        try:
            # Create tool instance if needed
            if not hasattr(tool, 'run') and hasattr(tool, '__call__'):
                tool_instance = tool()
            else:
                tool_instance = tool
            
            # Execute tool
            result = tool_instance.run(query)
            
            # Validate result
            is_valid_result = self._is_tool_result_valid(result)
            
            if is_valid_result:
                return True, result
            else:
                return False, f"Tool {tool_name} returned invalid result"
                
        except Exception as e:
            formatted_error = self._format_tool_error(tool_name, e)
            return False, formatted_error
    
    def _get_required_api_keys(self, tool_name: str) -> List[str]:
        """Get required API keys for a tool."""
        api_key_requirements = {
            'google_search': ['google_api_key', 'google'],
            'firecrawl': ['firecrawl'],
            'webscrapertool': [],  # No API key required
            'calculator': [],      # No API key required
            'textanalyzer': [],   # No API key required
            'datavalidator': [],  # No API key required
            'write_tool': [],     # No API key required
            'read_tool': [],      # No API key required
            'edit_tool': [],      # No API key required
            'bash_tool': [],      # No API key required
            'e2b_code_sandbox': ['e2b_api_key', 'e2b'],
        }
        
        return api_key_requirements.get(tool_name.lower(), [])
    
    def _requires_file_access(self, tool_name: str) -> bool:
        """Check if tool requires file system access."""
        file_tools = [
            'write_tool', 'read_tool', 'edit_tool', 'project_management_tool',
            'filemanagertool', 'grep_tool'
        ]
        return tool_name.lower() in file_tools
    
    def _requires_network_access(self, tool_name: str) -> bool:
        """Check if tool requires network access."""
        network_tools = [
            'google_search', 'webscrapertool', 'firecrawl', 'e2b_code_sandbox'
        ]
        return tool_name.lower() in network_tools
    
    def _check_file_permissions(self, context: Dict) -> bool:
        """Check if file system permissions are available."""
        try:
            # Try to create a temporary file
            test_dir = context.get('project_location', '.')
            test_file = os.path.join(test_dir, '.metis_permission_test')
            
            with open(test_file, 'w') as f:
                f.write('test')
            
            os.remove(test_file)
            return True
            
        except Exception:
            return False
    
    def _check_network_connectivity(self) -> bool:
        """Check if network connectivity is available."""
        try:
            import urllib.request
            urllib.request.urlopen('http://google.com', timeout=1)
            return True
        except Exception:
            return False
    
    def _perform_tool_specific_validation(self, tool_name: str, tool_instance, 
                                         context: Dict) -> Tuple[bool, str]:
        """Perform tool-specific validation checks."""
        tool_name_lower = tool_name.lower()
        
        # Google Search validation
        if tool_name_lower == 'google_search':
            api_keys = context.get('api_keys', {})
            if 'google_api_key' in api_keys and 'google_search_engine' in api_keys:
                return True, "Google Search API configured"
            else:
                return False, "Google Search requires both API key and search engine ID"
        
        # E2B Code Sandbox validation
        elif tool_name_lower == 'e2b_code_sandbox':
            api_keys = context.get('api_keys', {})
            if 'e2b_api_key' in api_keys or 'e2b' in api_keys:
                return True, "E2B API key configured"
            else:
                return False, "E2B Code Sandbox requires API key"
        
        # File tools validation
        elif tool_name_lower in ['write_tool', 'read_tool', 'edit_tool']:
            project_location = context.get('project_location')
            if project_location and os.path.exists(project_location):
                return True, "Project location accessible"
            else:
                return False, f"Project location not accessible: {project_location}"
        
        # Default validation - tool exists and has run method
        if hasattr(tool_instance, 'run') or callable(tool_instance):
            return True, "Tool interface validation passed"
        else:
            return False, "Tool does not have required interface"
    
    def _is_tool_result_valid(self, result) -> bool:
        """Check if tool result is valid."""
        # Null result check
        if result is None:
            return False
        
        # Empty string/list/dict check
        if isinstance(result, (str, list, dict)) and not result:
            return False
        
        # Error indicators in string results
        if isinstance(result, str):
            error_indicators = [
                'error:', 'failed:', 'exception:', 'traceback',
                'could not', 'unable to', 'permission denied'
            ]
            result_lower = result.lower()
            if any(indicator in result_lower for indicator in error_indicators):
                return False
        
        return True
    
    def _format_tool_error(self, tool_name: str, error: Exception) -> str:
        """Format tool execution error for user display."""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Common error translations
        if 'permission' in error_message.lower():
            return f"Permission error in {tool_name}: Check file/directory permissions"
        elif 'network' in error_message.lower() or 'connection' in error_message.lower():
            return f"Network error in {tool_name}: Check internet connectivity"
        elif 'api' in error_message.lower() or 'key' in error_message.lower():
            return f"API error in {tool_name}: Check API key configuration"
        elif 'timeout' in error_message.lower():
            return f"Timeout error in {tool_name}: Operation took too long"
        else:
            return f"{tool_name} error ({error_type}): {error_message[:100]}"
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics."""
        if not self.validation_history:
            return {'validations_performed': 0}
        
        total_validations = len(self.validation_history)
        successful_validations = sum(
            1 for v in self.validation_history if v['validation_result']
        )
        
        # Tool usage stats
        tool_usage = {}
        for validation in self.validation_history:
            tool_name = validation['tool_name']
            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        return {
            'validations_performed': total_validations,
            'successful_validations': successful_validations,
            'validation_success_rate': successful_validations / total_validations,
            'tool_validation_counts': tool_usage,
            'recent_validations': self.validation_history[-5:] if len(self.validation_history) > 5 else self.validation_history
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get tool validator status."""
        return {
            'validations_performed': len(self.validation_history),
            'component': 'ToolValidator',
            'status': 'active'
        }


class ResultValidator:
    """Validates execution results for quality and completeness."""
    
    def __init__(self, orchestrator):
        """Initialize with reference to main orchestrator."""
        self.orchestrator = orchestrator
        self.result_validations = []
    
    def validate_result(self, result, context: Dict) -> bool:
        """
        Validate execution result quality.
        
        Args:
            result: ExecutionResult to validate
            context: Execution context
            
        Returns:
            True if result is valid and high quality
        """
        validation_score = 0.0
        validation_details = {}
        
        try:
            # Basic success check
            if result.success:
                validation_score += 0.3
                validation_details['success_check'] = True
            else:
                validation_details['success_check'] = False
            
            # Result content quality check
            content_score = self._validate_content_quality(result.result)
            validation_score += content_score * 0.4
            validation_details['content_score'] = content_score
            
            # Tool usage appropriateness
            tools_score = self._validate_tool_usage(result.tools_used, context)
            validation_score += tools_score * 0.2
            validation_details['tools_score'] = tools_score
            
            # Execution time reasonableness
            time_score = self._validate_execution_time(result.execution_time)
            validation_score += time_score * 0.1
            validation_details['time_score'] = time_score
            
            # Overall validation result
            is_valid = validation_score >= 0.7
            
            # Record validation
            validation_record = {
                'validation_score': validation_score,
                'is_valid': is_valid,
                'details': validation_details,
                'timestamp': datetime.now().isoformat(),
                'context_session_id': context.get('session_id')
            }
            
            self.result_validations.append(validation_record)
            
            return is_valid
            
        except Exception as e:
            # Validation failed - assume result is invalid
            validation_record = {
                'validation_score': 0.0,
                'is_valid': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'context_session_id': context.get('session_id')
            }
            
            self.result_validations.append(validation_record)
            return False
    
    def _validate_content_quality(self, content) -> float:
        """Validate the quality of result content."""
        if not content:
            return 0.0
        
        content_str = str(content)
        score = 0.0
        
        # Length check (not too short, not excessively long)
        length = len(content_str)
        if 10 <= length <= 10000:
            score += 0.3
        elif length > 5:
            score += 0.1
        
        # Meaningful content indicators
        meaningful_indicators = [
            'result', 'output', 'answer', 'data', 'information',
            'completed', 'successful', 'created', 'found'
        ]
        
        content_lower = content_str.lower()
        meaningful_count = sum(
            1 for indicator in meaningful_indicators
            if indicator in content_lower
        )
        
        if meaningful_count > 0:
            score += min(meaningful_count * 0.1, 0.3)
        
        # Error indicators (reduce score)
        error_indicators = ['error', 'failed', 'exception', 'traceback']
        error_count = sum(
            1 for indicator in error_indicators
            if indicator in content_lower
        )
        
        score -= error_count * 0.2
        
        # Structure quality (for code or formatted content)
        if self._has_good_structure(content_str):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _validate_tool_usage(self, tools_used: List[str], context: Dict) -> float:
        """Validate appropriateness of tool usage."""
        if not tools_used:
            return 0.5  # Neutral score for no tools
        
        query = context.get('query', '').lower()
        score = 0.0
        
        # Check tool-query alignment
        appropriate_tools = 0
        total_tools = len(tools_used)
        
        for tool in tools_used:
            tool_lower = tool.lower()
            
            if 'search' in query and 'search' in tool_lower:
                appropriate_tools += 1
            elif 'calculate' in query and 'calculator' in tool_lower:
                appropriate_tools += 1
            elif 'write' in query and 'write' in tool_lower:
                appropriate_tools += 1
            elif 'analyze' in query and 'analyzer' in tool_lower:
                appropriate_tools += 1
            elif 'code' in query and 'sandbox' in tool_lower:
                appropriate_tools += 1
            else:
                # Give partial credit for any tool usage
                appropriate_tools += 0.5
        
        if total_tools > 0:
            score = appropriate_tools / total_tools
        
        return min(1.0, score)
    
    def _validate_execution_time(self, execution_time) -> float:
        """Validate execution time reasonableness."""
        try:
            if hasattr(execution_time, 'total_seconds'):
                seconds = execution_time.total_seconds()
            elif isinstance(execution_time, (int, float)):
                seconds = execution_time
            else:
                return 0.5  # Unknown time format, neutral score
            
            # Ideal execution time ranges
            if 0.1 <= seconds <= 60:  # 0.1 seconds to 1 minute
                return 1.0
            elif seconds <= 300:  # Up to 5 minutes
                return 0.8
            elif seconds <= 1800:  # Up to 30 minutes
                return 0.6
            else:  # Very long execution
                return 0.3
                
        except Exception:
            return 0.5  # Error in time validation, neutral score
    
    def _has_good_structure(self, content: str) -> bool:
        """Check if content has good structure."""
        # Check for various structure indicators
        structure_indicators = [
            '\n',  # Line breaks
            ':',   # Colons (key-value pairs)
            '{',   # JSON/dict structure
            '<',   # HTML/XML structure
            '#',   # Markdown headers
            '-',   # Lists
            '|',   # Tables
        ]
        
        indicator_count = sum(
            1 for indicator in structure_indicators
            if indicator in content
        )
        
        return indicator_count >= 2
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get result validation statistics."""
        if not self.result_validations:
            return {'validations_performed': 0}
        
        total_validations = len(self.result_validations)
        valid_results = sum(
            1 for v in self.result_validations if v['is_valid']
        )
        
        avg_score = sum(
            v['validation_score'] for v in self.result_validations
        ) / total_validations
        
        return {
            'validations_performed': total_validations,
            'valid_results': valid_results,
            'validation_success_rate': valid_results / total_validations,
            'average_validation_score': avg_score,
            'recent_validations': self.result_validations[-5:] if len(self.result_validations) > 5 else self.result_validations
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get result validator status."""
        return {
            'validations_performed': len(self.result_validations),
            'component': 'ResultValidator',
            'status': 'active'
        }