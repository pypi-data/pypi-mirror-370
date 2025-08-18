"""
Tool Generator Tool for Metis Agent.

This tool allows the agent to create new tools dynamically following the established
tool rules and patterns. It generates complete tool implementations and registers
them with the tool registry.
"""

import os
import re
import ast
import inspect
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime

from ..base import BaseTool
from ..registry import register_tool, get_available_tools


class ToolGeneratorTool(BaseTool):
    """
    Generate new tools dynamically based on specifications.
    
    This tool can create new tool implementations following the established
    tool rules and patterns, including:
    - Proper inheritance from BaseTool or ComposableTool
    - Stateless architecture
    - Required method implementations
    - Capability metadata
    - Automatic registration with the tool registry
    """
    
    def __init__(self):
        """Initialize the tool generator."""
        self.name = "ToolGeneratorTool"
        self.description = "Generate new tools dynamically based on specifications"
        
        # Common patterns for different tool types
        self.tool_patterns = {
            'data_processing': {
                'keywords': ['process', 'transform', 'convert', 'parse', 'format'],
                'capabilities': {
                    'complexity_levels': ['simple', 'moderate'],
                    'input_types': ['text', 'structured_data'],
                    'output_types': ['structured_data'],
                    'requires_filesystem': False,
                    'requires_internet': False
                }
            },
            'file_operations': {
                'keywords': ['file', 'directory', 'read', 'write', 'create', 'delete'],
                'capabilities': {
                    'complexity_levels': ['simple', 'moderate'],
                    'input_types': ['text', 'file_path'],
                    'output_types': ['structured_data', 'file_content'],
                    'requires_filesystem': True,
                    'requires_internet': False
                }
            },
            'web_operations': {
                'keywords': ['web', 'http', 'api', 'request', 'fetch', 'download'],
                'capabilities': {
                    'complexity_levels': ['moderate', 'complex'],
                    'input_types': ['text', 'url'],
                    'output_types': ['structured_data', 'web_content'],
                    'requires_filesystem': False,
                    'requires_internet': True
                }
            },
            'analysis': {
                'keywords': ['analyze', 'examine', 'inspect', 'evaluate', 'assess'],
                'capabilities': {
                    'complexity_levels': ['moderate', 'complex'],
                    'input_types': ['text', 'structured_data'],
                    'output_types': ['analysis_results', 'structured_data'],
                    'requires_filesystem': False,
                    'requires_internet': False
                }
            }
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Check if this tool can handle tool generation tasks.
        
        Args:
            task: The task description
            
        Returns:
            True if this is a tool generation task
        """
        task_lower = task.lower()
        
        # Tool generation indicators
        generation_keywords = [
            'create tool', 'generate tool', 'build tool', 'make tool',
            'new tool', 'tool for', 'implement tool', 'develop tool',
            'create a tool', 'generate a tool', 'build a tool'
        ]
        
        return any(keyword in task_lower for keyword in generation_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a new tool based on the task specification.
        
        Args:
            task: Tool specification and requirements
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with tool generation results
        """
        try:
            # Parse the tool specification
            spec = self._parse_tool_specification(task)
            
            # Validate the specification
            validation_result = self._validate_specification(spec)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Invalid specification: {validation_result['errors']}",
                    'spec_parsed': spec
                }
            
            # Generate the tool code
            tool_code = self._generate_tool_code(spec)
            
            # Create the tool file
            file_path = self._create_tool_file(spec['name'], tool_code)
            
            # Register the tool dynamically
            registration_result = self._register_generated_tool(spec['name'], tool_code)
            
            return {
                'success': True,
                'tool_name': spec['name'],
                'tool_class': spec['class_name'],
                'file_path': str(file_path),
                'registered': registration_result['success'],
                'capabilities': spec['capabilities'],
                'code_preview': tool_code[:500] + "..." if len(tool_code) > 500 else tool_code,
                'message': f"Successfully generated and registered {spec['name']} tool"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Tool generation failed: {str(e)}",
                'task': task
            }
    
    def _parse_tool_specification(self, task: str) -> Dict[str, Any]:
        """Parse the tool specification from the task description."""
        spec = {
            'name': None,
            'class_name': None,
            'description': None,
            'purpose': None,
            'tool_type': 'base',
            'category': 'general',
            'capabilities': {},
            'examples': []
        }
        
        # Extract tool name
        name_patterns = [
            r'(?:called|named)\s+([A-Za-z][A-Za-z0-9_]*Tool)',
            r'create\s+(?:a\s+)?tool\s+(?:called\s+|named\s+)?["\']?([A-Za-z][A-Za-z0-9_]*)["\']?',
            r'generate\s+(?:a\s+)?["\']?([A-Za-z][A-Za-z0-9_]*)["\']?\s+tool',
            r'build\s+(?:a\s+)?([A-Za-z][A-Za-z0-9_]*Tool)',
            r'tool\s+for\s+([a-zA-Z][a-zA-Z0-9_\s]+)',
            r'([A-Za-z][A-Za-z0-9_]*Tool)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                raw_name = match.group(1).strip()
                spec['name'] = self._clean_tool_name(raw_name)
                spec['class_name'] = self._to_class_name(spec['name'])
                break
        
        # If no name found, generate one based on purpose
        if not spec['name']:
            spec['name'] = self._generate_tool_name(task)
            spec['class_name'] = self._to_class_name(spec['name'])
        
        # Extract description and purpose
        spec['description'] = self._extract_description(task)
        spec['purpose'] = self._extract_purpose(task)
        
        # Determine tool category
        spec['category'] = self._determine_category(task)
        
        # Generate capabilities based on category
        spec['capabilities'] = self._generate_capabilities(spec['category'], task)
        
        # Extract examples if mentioned
        spec['examples'] = self._extract_examples(task)
        
        return spec
    
    def _clean_tool_name(self, name: str) -> str:
        """Clean and format tool name."""
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        cleaned = re.sub(r'_+', '_', cleaned).strip('_')
        if not cleaned.lower().endswith('tool'):
            cleaned += '_tool'
        return cleaned.lower()
    
    def _to_class_name(self, tool_name: str) -> str:
        """Convert tool name to class name."""
        if tool_name.lower().endswith('tool'):
            # If name already ends with 'tool', capitalize properly
            base_name = tool_name[:-4]  # Remove 'tool'
            class_name = ''.join(word.capitalize() for word in base_name.split('_')) + 'Tool'
        else:
            # Add Tool suffix
            class_name = ''.join(word.capitalize() for word in tool_name.split('_')) + 'Tool'
        return class_name
    
    def _generate_tool_name(self, task: str) -> str:
        """Generate a tool name based on task description."""
        action_words = []
        for word in task.lower().split():
            if word in ['create', 'generate', 'build', 'process', 'analyze', 'convert']:
                action_words.append(word)
        
        if action_words:
            base_name = '_'.join(action_words[:2])
        else:
            base_name = 'custom'
        
        return f"{base_name}_tool"
    
    def _extract_description(self, task: str) -> str:
        """Extract tool description from task."""
        description = task.strip()
        
        patterns_to_remove = [
            r'create\s+(?:a\s+)?tool\s+(?:that\s+|to\s+)?',
            r'generate\s+(?:a\s+)?tool\s+(?:that\s+|to\s+)?',
            r'build\s+(?:a\s+)?tool\s+(?:that\s+|to\s+)?'
        ]
        
        for pattern in patterns_to_remove:
            description = re.sub(pattern, '', description, flags=re.IGNORECASE)
        
        description = description.strip()
        if description:
            description = description[0].upper() + description[1:]
        
        return description or "Custom tool for specific functionality"
    
    def _extract_purpose(self, task: str) -> str:
        """Extract the main purpose of the tool."""
        purpose_patterns = [
            r'(?:that\s+|to\s+)(.+?)(?:\.|$)',
            r'for\s+(.+?)(?:\.|$)',
            r'which\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in purpose_patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return self._extract_description(task)
    
    def _determine_category(self, task: str) -> str:
        """Determine tool category based on task description."""
        task_lower = task.lower()
        
        for category, pattern_info in self.tool_patterns.items():
            keywords = pattern_info['keywords']
            if any(keyword in task_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _generate_capabilities(self, category: str, task: str) -> Dict[str, Any]:
        """Generate capabilities metadata for the tool."""
        base_capabilities = self.tool_patterns.get(category, {}).get('capabilities', {})
        capabilities = base_capabilities.copy()
        
        # Add default values
        capabilities.setdefault('estimated_execution_time', '1-5s')
        capabilities.setdefault('concurrent_safe', True)
        capabilities.setdefault('resource_intensive', False)
        capabilities.setdefault('memory_usage', 'low')
        capabilities.setdefault('api_dependencies', [])
        capabilities.setdefault('supported_intents', [])
        
        return capabilities
    
    def _extract_examples(self, task: str) -> List[str]:
        """Extract example use cases from task description."""
        examples = []
        
        example_patterns = [
            r'(?:for example|such as|like)\s+(.+?)(?:\.|,|$)',
            r'examples?\s*:\s*(.+?)(?:\.|$)'
        ]
        
        for pattern in example_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            examples.extend(match.strip() for match in matches)
        
        if not examples:
            purpose = self._extract_purpose(task)
            examples = [f"Example usage: {purpose}"]
        
        return examples[:3]
    
    def _validate_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the tool specification."""
        errors = []
        
        if not spec.get('name'):
            errors.append("Tool name is required")
        
        if not spec.get('class_name'):
            errors.append("Tool class name is required")
        
        if not spec.get('description'):
            errors.append("Tool description is required")
        
        if spec.get('name') and not re.match(r'^[a-z][a-z0-9_]*$', spec['name']):
            errors.append("Tool name must be lowercase with underscores")
        
        if spec.get('class_name') and not re.match(r'^[A-Z][a-zA-Z0-9]*$', spec['class_name']):
            errors.append("Class name must be PascalCase")
        
        existing_tools = get_available_tools()
        if spec.get('class_name') in existing_tools:
            errors.append(f"Tool {spec['class_name']} already exists")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _generate_tool_code(self, spec: Dict[str, Any]) -> str:
        """Generate the complete tool code."""
        template = self._get_tool_template()
        
        # Determine the directory for import path calculation
        temp_code = template.format(
            description=spec['description'],
            timestamp=datetime.now().isoformat(),
            class_name=spec['class_name'],
            purpose=spec['purpose'],
            tool_name=spec['name'],
            can_handle_logic='',
            execute_logic='',
            capabilities='',
            examples=''
        )
        
        target_directory = self._determine_tool_directory(temp_code)
        
        # Update template with correct import based on directory
        if target_directory == 'core_tools':
            import_statement = 'from ..base import BaseTool'
        elif target_directory == 'advanced_tools':
            import_statement = 'from ..base import BaseTool'
        elif target_directory == 'utility_tools':
            import_statement = 'from ..base import BaseTool'
        else:
            import_statement = 'from ..base import BaseTool'
        
        # Template already uses 'from ..base import BaseTool' which is correct for subdirectories
        # No replacement needed since all subdirectories use the same relative import
        
        code = template.format(
            class_name=spec['class_name'],
            tool_name=spec['name'],
            description=spec['description'],
            purpose=spec['purpose'],
            capabilities=self._format_capabilities(spec['capabilities']),
            examples=self._format_examples(spec['examples']),
            can_handle_logic=self._generate_can_handle_logic(spec),
            execute_logic=self._generate_execute_logic(spec),
            timestamp=datetime.now().isoformat()
        )
        
        return code
    
    def _format_capabilities(self, capabilities: Dict[str, Any]) -> str:
        """Format capabilities dictionary for code generation."""
        lines = []
        for key, value in capabilities.items():
            if isinstance(value, str):
                lines.append(f'            "{key}": "{value}",')
            elif isinstance(value, bool):
                lines.append(f'            "{key}": {str(value)},')
            elif isinstance(value, list):
                formatted_list = '[' + ', '.join(f'"{item}"' for item in value) + ']'
                lines.append(f'            "{key}": {formatted_list},')
            else:
                lines.append(f'            "{key}": {repr(value)},')
        
        return '\n'.join(lines)
    
    def _format_examples(self, examples: List[str]) -> str:
        """Format examples list for code generation."""
        if not examples:
            return '            # No examples provided'
        
        formatted_examples = []
        for example in examples:
            formatted_examples.append(f'            "{example}",')
        
        return '\n'.join(formatted_examples)
    
    def _generate_can_handle_logic(self, spec: Dict[str, Any]) -> str:
        """Generate can_handle method logic."""
        category = spec['category']
        keywords = self.tool_patterns.get(category, {}).get('keywords', [])
        
        purpose_words = spec['purpose'].lower().split()
        custom_keywords = [word for word in purpose_words if len(word) > 3]
        
        all_keywords = list(set(keywords + custom_keywords))
        keywords_str = ', '.join(f'"{keyword}"' for keyword in all_keywords)
        
        return f"""        task_lower = task.lower()
        
        # Keywords that indicate this tool can handle the task
        keywords = [{keywords_str}]
        
        return any(keyword in task_lower for keyword in keywords)"""
    
    def _generate_execute_logic(self, spec: Dict[str, Any]) -> str:
        """Generate robust execute method logic based on tool category."""
        category = spec.get('category', 'general')
        purpose = spec.get('purpose', '').lower()
        
        if category == 'web_operations' or 'web' in purpose or 'scraping' in purpose or 'api' in purpose:
            return self._generate_web_operations_logic(spec)
        elif category == 'file_operations' or 'file' in purpose or 'directory' in purpose:
            return self._generate_file_operations_logic(spec)
        elif category == 'data_processing' or 'data' in purpose or 'process' in purpose or 'validate' in purpose:
            return self._generate_data_processing_logic(spec)
        elif category == 'analysis' or 'analyze' in purpose or 'sentiment' in purpose:
            return self._generate_analysis_logic(spec)
        else:
            return self._generate_general_logic(spec)
    
    def _generate_web_operations_logic(self, spec: Dict[str, Any]) -> str:
        """Generate web operations specific logic."""
        return """        try:
            import requests
            from urllib.parse import urljoin, urlparse
            import re
            
            # Extract URL from task if present
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, task)
            
            if urls:
                url = urls[0]
            else:
                # Default to a test URL or extract from kwargs
                url = kwargs.get('url', 'https://httpbin.org/get')
            
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Make the request
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Process the response
            content_type = response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                data = response.json()
            elif 'html' in content_type:
                # Basic HTML parsing
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract common elements
                data = {
                    'title': soup.title.string if soup.title else None,
                    'links': [a.get('href') for a in soup.find_all('a', href=True)][:10],
                    'text_content': soup.get_text()[:1000],
                    'images': [img.get('src') for img in soup.find_all('img', src=True)][:5]
                }
            else:
                data = {'content': response.text[:1000]}
            
            return {
                'success': True,
                'url': url,
                'status_code': response.status_code,
                'content_type': content_type,
                'data': data,
                'message': f"Successfully scraped data from {url}"
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'task': task
            }
        except ImportError as e:
            return {
                'success': False,
                'error': f"Missing required library: {str(e)}. Install with: pip install requests beautifulsoup4",
                'task': task
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task': task
            }"""
    
    def _generate_file_operations_logic(self, spec: Dict[str, Any]) -> str:
        """Generate file operations specific logic."""
        return """        try:
            import os
            import shutil
            from pathlib import Path
            import json
            
            # Extract file path from task or kwargs
            file_path = kwargs.get('file_path') or kwargs.get('path')
            
            if not file_path:
                # Try to extract path from task description
                import re
                path_patterns = [r'"([^"]+)"', r"'([^']+)'", r'\b([A-Za-z]:[\\\w\s\.\-]+)\b']
                for pattern in path_patterns:
                    matches = re.findall(pattern, task)
                    if matches:
                        file_path = matches[0]
                        break
            
            if not file_path:
                file_path = kwargs.get('default_path', './test_file.txt')
            
            path_obj = Path(file_path)
            operation = kwargs.get('operation', 'info')
            
            # Determine operation from task
            task_lower = task.lower()
            if 'create' in task_lower or 'make' in task_lower:
                operation = 'create'
            elif 'delete' in task_lower or 'remove' in task_lower:
                operation = 'delete'
            elif 'copy' in task_lower:
                operation = 'copy'
            elif 'move' in task_lower:
                operation = 'move'
            elif 'list' in task_lower or 'show' in task_lower:
                operation = 'list'
            elif 'read' in task_lower:
                operation = 'read'
            
            result = {}
            
            if operation == 'create':
                if path_obj.suffix:
                    # Create file
                    path_obj.parent.mkdir(parents=True, exist_ok=True)
                    content = kwargs.get('content', f'File created by {self.name} at {datetime.now()}')
                    path_obj.write_text(content)
                    result = {'action': 'file_created', 'path': str(path_obj), 'size': path_obj.stat().st_size}
                else:
                    # Create directory
                    path_obj.mkdir(parents=True, exist_ok=True)
                    result = {'action': 'directory_created', 'path': str(path_obj)}
            
            elif operation == 'delete':
                if path_obj.exists():
                    if path_obj.is_file():
                        path_obj.unlink()
                        result = {'action': 'file_deleted', 'path': str(path_obj)}
                    else:
                        shutil.rmtree(path_obj)
                        result = {'action': 'directory_deleted', 'path': str(path_obj)}
                else:
                    result = {'action': 'not_found', 'path': str(path_obj)}
            
            elif operation == 'list':
                if path_obj.is_dir():
                    items = [{'name': item.name, 'type': 'dir' if item.is_dir() else 'file', 
                             'size': item.stat().st_size if item.is_file() else None} 
                            for item in path_obj.iterdir()]
                    result = {'action': 'directory_listed', 'path': str(path_obj), 'items': items}
                else:
                    result = {'action': 'not_directory', 'path': str(path_obj)}
            
            elif operation == 'read':
                if path_obj.is_file():
                    content = path_obj.read_text()[:1000]  # Limit to first 1000 chars
                    result = {'action': 'file_read', 'path': str(path_obj), 'content': content}
                else:
                    result = {'action': 'not_file', 'path': str(path_obj)}
            
            else:
                # Default info operation
                if path_obj.exists():
                    stat = path_obj.stat()
                    result = {
                        'action': 'file_info',
                        'path': str(path_obj),
                        'exists': True,
                        'type': 'dir' if path_obj.is_dir() else 'file',
                        'size': stat.st_size if path_obj.is_file() else None,
                        'modified': stat.st_mtime
                    }
                else:
                    result = {'action': 'file_info', 'path': str(path_obj), 'exists': False}
            
            return {
                'success': True,
                'operation': operation,
                'result': result,
                'message': f"File operation '{operation}' completed successfully"
            }
            
        except PermissionError as e:
            return {
                'success': False,
                'error': f"Permission denied: {str(e)}",
                'task': task
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task': task
            }"""
    
    def _generate_data_processing_logic(self, spec: Dict[str, Any]) -> str:
        """Generate data processing specific logic."""
        return """        try:
            import json
            import csv
            import re
            from io import StringIO
            
            # Get data from kwargs or try to parse from task
            data = kwargs.get('data')
            data_format = kwargs.get('format', 'auto')
            
            if not data:
                # Try to extract data from task description
                if '{' in task and '}' in task:
                    # Looks like JSON
                    json_match = re.search(r'\{.*\}', task, re.DOTALL)
                    if json_match:
                        try:
                            data = json.loads(json_match.group())
                            data_format = 'json'
                        except json.JSONDecodeError:
                            pass
                
                if not data:
                    # Create sample data for demonstration
                    data = {
                        'sample_field': 'sample_value',
                        'numbers': [1, 2, 3, 4, 5],
                        'timestamp': str(datetime.now())
                    }
                    data_format = 'json'
            
            result = {}
            
            # Determine operation
            task_lower = task.lower()
            if 'validate' in task_lower:
                # Data validation
                if isinstance(data, dict):
                    validation_result = {
                        'valid': True,
                        'type': 'object',
                        'fields': len(data),
                        'field_types': {k: type(v).__name__ for k, v in data.items()}
                    }
                elif isinstance(data, list):
                    validation_result = {
                        'valid': True,
                        'type': 'array',
                        'length': len(data),
                        'item_types': list(set(type(item).__name__ for item in data))
                    }
                else:
                    validation_result = {
                        'valid': True,
                        'type': type(data).__name__,
                        'value': str(data)[:100]
                    }
                result['validation'] = validation_result
            
            elif 'convert' in task_lower or 'transform' in task_lower:
                # Data conversion
                target_format = kwargs.get('target_format', 'json')
                
                if target_format == 'json':
                    result['converted_data'] = json.dumps(data, indent=2)
                elif target_format == 'csv':
                    if isinstance(data, list) and data and isinstance(data[0], dict):
                        output = StringIO()
                        writer = csv.DictWriter(output, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                        result['converted_data'] = output.getvalue()
                    else:
                        result['converted_data'] = str(data)
                else:
                    result['converted_data'] = str(data)
                
                result['target_format'] = target_format
            
            elif 'clean' in task_lower or 'sanitize' in task_lower:
                # Data cleaning
                if isinstance(data, dict):
                    cleaned_data = {k: v for k, v in data.items() if v is not None and v != ''}
                elif isinstance(data, list):
                    cleaned_data = [item for item in data if item is not None and item != '']
                elif isinstance(data, str):
                    cleaned_data = re.sub(r'\s+', ' ', data.strip())
                else:
                    cleaned_data = data
                
                result['cleaned_data'] = cleaned_data
                result['original_size'] = len(str(data))
                result['cleaned_size'] = len(str(cleaned_data))
            
            else:
                # Default processing - analyze data
                if isinstance(data, dict):
                    analysis = {
                        'type': 'object',
                        'field_count': len(data),
                        'fields': list(data.keys()),
                        'sample_values': {k: str(v)[:50] for k, v in list(data.items())[:3]}
                    }
                elif isinstance(data, list):
                    analysis = {
                        'type': 'array',
                        'length': len(data),
                        'sample_items': data[:3],
                        'item_types': list(set(type(item).__name__ for item in data))
                    }
                else:
                    analysis = {
                        'type': type(data).__name__,
                        'length': len(str(data)),
                        'preview': str(data)[:100]
                    }
                
                result['analysis'] = analysis
            
            return {
                'success': True,
                'input_format': data_format,
                'processed_data': result,
                'message': f"Data processing completed successfully"
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"JSON parsing error: {str(e)}",
                'task': task
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task': task
            }"""
    
    def _generate_analysis_logic(self, spec: Dict[str, Any]) -> str:
        """Generate analysis specific logic."""
        return """        try:
            import re
            from collections import Counter
            
            # Get text to analyze
            text = kwargs.get('text') or kwargs.get('content')
            
            if not text:
                # Try to extract text from task
                text_patterns = [r'"([^"]+)"', r"'([^']+)'"]
                for pattern in text_patterns:
                    matches = re.findall(pattern, task)
                    if matches:
                        text = ' '.join(matches)
                        break
            
            if not text:
                text = task  # Use the task itself as text to analyze
            
            # Basic text analysis
            words = re.findall(r'\b\w+\b', text.lower())
            sentences = re.split(r'[.!?]+', text)
            
            # Word frequency analysis
            word_freq = Counter(words)
            common_words = word_freq.most_common(10)
            
            # Basic sentiment analysis (simple keyword-based)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                            'love', 'like', 'happy', 'pleased', 'satisfied', 'perfect']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 
                            'angry', 'frustrated', 'disappointed', 'poor', 'worst']
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            if positive_count > negative_count:
                sentiment = 'positive'
                confidence = min(0.9, (positive_count - negative_count) / len(words) * 10)
            elif negative_count > positive_count:
                sentiment = 'negative'
                confidence = min(0.9, (negative_count - positive_count) / len(words) * 10)
            else:
                sentiment = 'neutral'
                confidence = 0.5
            
            # Extract key phrases (simple n-gram approach)
            bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
            key_phrases = [phrase for phrase, count in Counter(bigrams).most_common(5) if count > 1]
            
            analysis_result = {
                'text_stats': {
                    'character_count': len(text),
                    'word_count': len(words),
                    'sentence_count': len([s for s in sentences if s.strip()]),
                    'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
                },
                'sentiment': {
                    'label': sentiment,
                    'confidence': round(confidence, 2),
                    'positive_indicators': positive_count,
                    'negative_indicators': negative_count
                },
                'keywords': {
                    'most_common_words': common_words[:5],
                    'key_phrases': key_phrases,
                    'unique_words': len(set(words))
                },
                'text_preview': text[:200] + '...' if len(text) > 200 else text
            }
            
            return {
                'success': True,
                'analysis': analysis_result,
                'message': f"Text analysis completed. Analyzed {len(words)} words with {sentiment} sentiment."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task': task
            }"""
    
    def _generate_general_logic(self, spec: Dict[str, Any]) -> str:
        """Generate general purpose logic."""
        return """        try:
            # General purpose tool execution
            task_lower = task.lower()
            
            # Analyze the task and provide appropriate response
            if 'help' in task_lower or 'info' in task_lower:
                result = {
                    'tool_info': {
                        'name': self.name,
                        'description': self.description,
                        'capabilities': self.get_capabilities(),
                        'examples': self.get_examples()
                    }
                }
            elif 'test' in task_lower:
                result = {
                    'test_result': 'Tool is working correctly',
                    'timestamp': str(datetime.now()),
                    'status': 'operational'
                }
            else:
                # Process the task generically
                result = {
                    'task_processed': True,
                    'input_task': task,
                    'parameters': kwargs,
                    'processing_time': str(datetime.now()),
                    'note': 'This is a general purpose response. For specific functionality, provide more detailed task descriptions.'
                }
            
            return {
                'success': True,
                'result': result,
                'message': f"Task processed successfully: {task[:50]}..."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task': task
            }"""
    
    def _create_tool_file(self, tool_name: str, tool_code: str) -> Path:
        """Create the tool file in the appropriate categorized directory."""
        # Determine the appropriate directory based on tool complexity and type
        category_dir = self._determine_tool_directory(tool_code)
        
        tools_base_dir = Path(__file__).parent.parent
        target_dir = tools_base_dir / category_dir
        target_dir.mkdir(exist_ok=True)
        
        file_path = target_dir / f"{tool_name}.py"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(tool_code)
        
        return file_path
    
    def _determine_tool_directory(self, tool_code: str) -> str:
        """Determine the appropriate directory for the generated tool."""
        
        # Analyze tool complexity and functionality to categorize
        code_lower = tool_code.lower()
        
        # Advanced tools - complex functionality, external dependencies, specialized operations
        advanced_indicators = [
            'api', 'http', 'request', 'web', 'scraping', 'crawl', 'git', 'repository',
            'database', 'sql', 'mongodb', 'redis', 'elasticsearch', 'docker', 'kubernetes',
            'machine learning', 'ml', 'ai', 'neural', 'model', 'training', 'prediction',
            'cloud', 'aws', 'azure', 'gcp', 'deployment', 'cicd', 'pipeline',
            'security', 'encryption', 'authentication', 'oauth', 'jwt', 'ssl',
            'blockchain', 'cryptocurrency', 'smart contract', 'ethereum',
            'image processing', 'computer vision', 'opencv', 'pillow',
            'natural language', 'nlp', 'sentiment', 'classification', 'deep',
            'research', 'analysis', 'complex', 'advanced', 'sophisticated'
        ]
        
        # Utility tools - helper functions, simple operations, formatting
        utility_indicators = [
            'format', 'convert', 'transform', 'validate', 'check', 'verify',
            'clean', 'sanitize', 'normalize', 'parse', 'extract', 'utility',
            'helper', 'simple', 'basic', 'text processing', 'string',
            'date', 'time', 'math', 'calculation', 'hash', 'encode', 'decode',
            'json', 'xml', 'csv', 'yaml', 'config', 'settings'
        ]
        
        # Core tools - fundamental operations, file system, basic I/O
        core_indicators = [
            'file', 'directory', 'read', 'write', 'create', 'delete', 'copy', 'move',
            'search', 'find', 'grep', 'list', 'browse', 'navigate',
            'execute', 'run', 'command', 'shell', 'bash', 'terminal',
            'edit', 'modify', 'update', 'replace', 'insert',
            'core', 'fundamental', 'basic', 'essential', 'primary'
        ]
        
        # Count indicators for each category
        advanced_score = sum(1 for indicator in advanced_indicators if indicator in code_lower)
        utility_score = sum(1 for indicator in utility_indicators if indicator in code_lower)
        core_score = sum(1 for indicator in core_indicators if indicator in code_lower)
        
        # Determine category based on highest score
        if advanced_score > max(utility_score, core_score):
            return 'advanced_tools'
        elif utility_score > core_score:
            return 'utility_tools'
        else:
            return 'core_tools'
    
    def _register_generated_tool(self, tool_name: str, tool_code: str) -> Dict[str, Any]:
        """Register the generated tool with the registry."""
        try:
            # Import ComposableTool for namespace
            from ..base import ComposableTool
            
            # Replace relative import with absolute import for exec
            modified_code = tool_code.replace(
                'from ..base import BaseTool',
                'from metis_agent.tools.base import BaseTool'
            ).replace(
                'from .base import BaseTool',
                'from metis_agent.tools.base import BaseTool'
            )
            
            namespace = {}
            namespace['BaseTool'] = BaseTool
            namespace['ComposableTool'] = ComposableTool
            namespace['Dict'] = Dict
            namespace['Any'] = Any
            namespace['List'] = List
            namespace['Optional'] = Optional
            namespace['datetime'] = datetime
            
            exec(modified_code, namespace)
            
            tool_class = None
            for name, obj in namespace.items():
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseTool) and 
                    obj != BaseTool and
                    obj != ComposableTool):
                    tool_class = obj
                    break
            
            if tool_class:
                register_tool(tool_class.__name__, tool_class)
                return {
                    'success': True,
                    'class_name': tool_class.__name__,
                    'message': f"Tool {tool_class.__name__} registered successfully"
                }
            else:
                return {
                    'success': False,
                    'error': "No valid tool class found in generated code"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to register tool: {str(e)}"
            }
    
    def _get_tool_template(self) -> str:
        """Get the tool template."""
        return '''"""
{description}

This tool was automatically generated by ToolGeneratorTool.
Generated on: {timestamp}
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base import BaseTool


class {class_name}(BaseTool):
    """
    {description}
    
    Purpose: {purpose}
    
    This tool follows the Metis Agent tool rules:
    - Stateless architecture (no LLM dependencies)
    - Single responsibility principle
    - Standardized interface with can_handle() and execute()
    """
    
    def __init__(self):
        """Initialize the tool."""
        self.name = "{tool_name}"
        self.description = "{description}"
    
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle the given task.
        
        Args:
            task: The task description
            
        Returns:
            True if tool can handle the task, False otherwise
        """
{can_handle_logic}
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool's functionality.
        
        Args:
            task: The primary task description
            **kwargs: Additional parameters
            
        Returns:
            Structured dictionary with results
        """
{execute_logic}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {{
{capabilities}
        }}
    
    def get_examples(self) -> List[str]:
        """Get example tasks that this tool can handle."""
        return [
{examples}
        ]
'''
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["moderate", "complex"],
            "input_types": ["text", "tool_specification"],
            "output_types": ["generated_tool", "tool_code"],
            "estimated_execution_time": "5-15s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": ["create", "generate", "build"],
            "api_dependencies": [],
            "memory_usage": "low"
        }
    
    def get_examples(self) -> List[str]:
        """Get example tasks that this tool can handle."""
        return [
            "Create a tool for processing CSV files",
            "Generate a tool that analyzes text sentiment",
            "Build a tool for web scraping",
            "Create a tool called DataValidatorTool",
            "Generate a tool to convert JSON to XML"
        ]
