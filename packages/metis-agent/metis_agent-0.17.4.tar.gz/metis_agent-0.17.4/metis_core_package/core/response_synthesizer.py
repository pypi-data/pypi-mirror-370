"""
Response Synthesizer for Metis Agent.

This module provides intelligent response formatting and synthesis
using the existing LLM interface for context-aware output.
"""
import json
from typing import Dict, List, Any, Optional

from .models import ExecutionResult, QueryAnalysis
from .llm_interface import get_llm


class ResponseSynthesizer:
    """Enhanced response synthesizer using LLM for intelligent formatting."""
    
    def __init__(self):
        """Initialize the synthesizer."""
        pass
    
    def synthesize_response(
        self,
        query: str,
        analysis: QueryAnalysis,
        execution_result: ExecutionResult,
        llm = None,
        memory_context: str = "",
        context: Dict = None,
        format_type: str = "default",
        system_message: str = None
    ) -> Dict[str, Any]:
        """
        Synthesize and format the final response.
        
        Args:
            query: Original user query
            execution_result: Result from orchestrator
            analysis: Original query analysis
            context: Additional context
            format_type: Type of formatting (default, web, cli, api)
            
        Returns:
            Formatted response dictionary
        """
        context = context or {}
        
        # Base response structure
        response_data = {
            "response": execution_result.response,
            "metadata": {
                "query": query,
                "analysis": {
                    "complexity": analysis.complexity.value,
                    "strategy": analysis.strategy.value,
                    "confidence": analysis.confidence,
                    "user_intent": analysis.user_intent,
                    "reasoning": analysis.reasoning
                },
                "execution": {
                    "strategy_used": execution_result.strategy_used,
                    "tools_used": execution_result.tools_used,
                    "execution_time": execution_result.execution_time,
                    "confidence": execution_result.confidence
                }
            }
        }
        
        # Add error information if present
        if execution_result.error:
            response_data["metadata"]["error"] = {
                "occurred": True,
                "message": execution_result.error
            }
        
        # Format based on type
        if format_type == "web":
            return self._format_for_web(response_data)
        elif format_type == "cli":
            return self._format_for_cli(response_data)
        elif format_type == "api":
            return self._format_for_api(response_data)
        else:
            return self._format_default(response_data)
    
    def enhance_response_with_context(
        self,
        response: str,
        context: Dict,
        enhancement_type: str = "clarity"
    ) -> str:
        """
        Enhance response using LLM for better clarity or formatting.
        
        Args:
            response: Original response
            context: Context for enhancement
            enhancement_type: Type of enhancement (clarity, formatting, detail)
            
        Returns:
            Enhanced response
        """
        llm = get_llm()
        
        if enhancement_type == "clarity":
            system_prompt = """You are an expert at making responses clearer and more understandable. 
            Improve the given response while maintaining all important information."""
            
            user_prompt = f"""
            Original response: {response}
            Context: {json.dumps(context, indent=2)}
            
            Make this response clearer and more user-friendly while preserving all key information.
            """
            
        elif enhancement_type == "formatting":
            system_prompt = """You are an expert at formatting responses for better readability.
            Improve the structure and presentation of the given response."""
            
            user_prompt = f"""
            Original response: {response}
            Context: {json.dumps(context, indent=2)}
            
            Improve the formatting and structure of this response for better readability.
            Use appropriate headings, bullet points, and organization.
            """
            
        elif enhancement_type == "detail":
            system_prompt = """You are an expert at adding helpful details to responses.
            Enhance the given response with additional relevant information."""
            
            user_prompt = f"""
            Original response: {response}
            Context: {json.dumps(context, indent=2)}
            
            Add helpful details to make this response clearer and more useful
            while keeping it concise and focused.
            """
            
        else:
            return response  # No enhancement
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            enhanced_response = llm.chat(messages)
            return enhanced_response
        except Exception as e:
            print(f"Response enhancement failed: {e}")
            return response  # Return original if enhancement fails
    
    def _format_for_web(self, response_data: Dict) -> Dict[str, Any]:
        """Format response for web frontend."""
        return {
            "success": not response_data["metadata"].get("error", {}).get("occurred", False),
            "data": {
                "answer": response_data["response"],
                "confidence": response_data["metadata"]["execution"]["confidence"],
                "execution_time": response_data["metadata"]["execution"]["execution_time"],
                "strategy": response_data["metadata"]["execution"]["strategy_used"],
                "tools_used": response_data["metadata"]["execution"]["tools_used"]
            },
            "metadata": {
                "complexity": response_data["metadata"]["analysis"]["complexity"],
                "intent": response_data["metadata"]["analysis"]["user_intent"]
            },
            "error": response_data["metadata"].get("error")
        }
    
    def _format_for_cli(self, response_data: Dict) -> Dict[str, Any]:
        """Format response for CLI interface."""
        cli_output = []
        
        # Main response
        cli_output.append(f"Response: {response_data['response']}")
        
        # Metadata
        analysis = response_data["metadata"]["analysis"]
        execution = response_data["metadata"]["execution"]
        
        cli_output.append(f"Strategy: {execution['strategy_used']} (confidence: {execution['confidence']:.2f})")
        cli_output.append(f"Complexity: {analysis['complexity']}")
        cli_output.append(f"Execution time: {execution['execution_time']:.2f}s")
        
        if execution['tools_used']:
            cli_output.append(f"Tools used: {', '.join(execution['tools_used'])}")
        
        return {
            "formatted_output": "\n".join(cli_output),
            "raw_data": response_data
        }
    
    def _format_for_api(self, response_data: Dict) -> Dict[str, Any]:
        """Format response for API consumption."""
        return {
            "status": "success" if not response_data["metadata"].get("error") else "error",
            "response": response_data["response"],
            "analysis": response_data["metadata"]["analysis"],
            "execution": response_data["metadata"]["execution"],
            "timestamp": response_data["metadata"].get("timestamp"),
            "error": response_data["metadata"].get("error")
        }
    
    def _format_default(self, response_data: Dict) -> Dict[str, Any]:
        """Default formatting - return as-is with minimal processing."""
        return response_data
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from response text.
        
        Args:
            text: Text containing potential code blocks
            
        Returns:
            List of code block dictionaries with language and code
        """
        import re
        
        # Pattern to match code blocks with language specification
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for match in matches:
            language = match[0] if match[0] else 'text'
            code = match[1].strip()
            code_blocks.append({
                'language': language,
                'code': code
            })
        
        return code_blocks
    
    def extract_tasks(self, text: str) -> List[str]:
        """
        Extract task items from response text.
        
        Args:
            text: Text containing potential task items
            
        Returns:
            List of task strings
        """
        import re
        
        # Pattern to match task-like items (bullet points, numbered lists, etc.)
        patterns = [
            r'^\s*[-*+]\s+(.+)$',  # Bullet points
            r'^\s*\d+\.\s+(.+)$',  # Numbered lists
            r'^\s*\[\s*\]\s+(.+)$',  # Checkboxes
            r'^\s*TODO:\s*(.+)$',  # TODO items
        ]
        
        tasks = []
        lines = text.split('\n')
        
        for line in lines:
            for pattern in patterns:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    tasks.append(match.group(1).strip())
                    break
        
        return tasks
