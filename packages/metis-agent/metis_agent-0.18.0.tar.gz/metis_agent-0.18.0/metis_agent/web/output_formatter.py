"""
Output formatter for Metis Agent web server.

This module provides functions for formatting agent output for the web interface.
"""
from typing import Dict, Any, List, Optional, Union


def format_response_for_frontend(response: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format a response for the frontend.
    
    Args:
        response: Response from the agent
        
    Returns:
        Formatted response
    """
    # If response is a string, convert to dict
    if isinstance(response, str):
        formatted = {
            'content': response,
            'content_type': 'markdown'
        }
    else:
        formatted = response.copy() if isinstance(response, dict) else {'content': str(response)}
        
        # Ensure content field exists
        if 'content' not in formatted:
            if 'result' in formatted:
                formatted['content'] = formatted['result']
            else:
                formatted['content'] = "No content available."
                
        # Set default content type
        if 'content_type' not in formatted:
            formatted['content_type'] = 'markdown'
            
    return formatted


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown text.
    
    Args:
        text: Markdown text
        
    Returns:
        List of code blocks with language and code
    """
    import re
    
    # Pattern to match code blocks
    pattern = r'```(\w*)\n(.*?)```'
    
    # Find all code blocks
    matches = re.finditer(pattern, text, re.DOTALL)
    
    code_blocks = []
    for match in matches:
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        
        code_blocks.append({
            'language': language,
            'code': code
        })
        
    return code_blocks


def extract_tasks(text: str) -> List[Dict[str, str]]:
    """
    Extract tasks from markdown text.
    
    Args:
        text: Markdown text
        
    Returns:
        List of tasks with text and status
    """
    import re
    
    # Pattern to match tasks
    pattern = r'- \[([ x])\] (.*)'
    
    # Find all tasks
    matches = re.finditer(pattern, text, re.MULTILINE)
    
    tasks = []
    for match in matches:
        status = 'completed' if match.group(1) == 'x' else 'pending'
        task_text = match.group(2).strip()
        
        tasks.append({
            'text': task_text,
            'status': status
        })
        
    return tasks