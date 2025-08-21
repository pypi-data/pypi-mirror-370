"""
Advanced Query Analyzer for Metis Agent.

This module provides intelligent query analysis using Groq for determining
query complexity and optimal execution strategies.
"""
import json
import re
from typing import Dict, Any, List
from .models import QueryAnalysis, QueryComplexity, ExecutionStrategy, AnalysisError
from .llm_interface import get_llm


class AdvancedQueryAnalyzer:
    """Enhanced query analyzer using LLM for intelligent analysis."""
    
    def __init__(self):
        """
        Initialize the analyzer.
        Uses the global LLM instance from llm_interface.
        """
        pass
        
    def analyze_query(self, query: str, context: Dict = None, available_tools: List[str] = None, tools_registry: Dict = None) -> QueryAnalysis:
        """
        Comprehensive query analysis using LLM reasoning capabilities.
        
        Args:
            query: User query to analyze
            context: Additional context for analysis
            
        Returns:
            QueryAnalysis with complexity, strategy, and metadata
        """
        # Build available tools list and check which can handle the query
        tools_list = available_tools or []
        capable_tools = []
        
        # Check which tools can actually handle this query
        if tools_registry:
            for tool_name in tools_list:
                if tool_name in tools_registry:
                    tool = tools_registry[tool_name]
                    if hasattr(tool, 'can_handle') and callable(tool.can_handle):
                        try:
                            if tool.can_handle(query):
                                capable_tools.append(tool_name)
                        except Exception as e:
                            # If can_handle fails, skip this tool
                            continue
        
        # Select the most relevant tools using scoring
        selected_tools = self._select_best_tools(capable_tools, query, tools_registry) if capable_tools else []
        
        # Build tools info with relevance indication
        if selected_tools:
            tools_info = "\n".join([f"- {tool} {'(HIGHLY RELEVANT)' if tool in selected_tools else '(capable but less relevant)'}" for tool in tools_list])
            tools_constraint = f"\nRECOMMENDED TOOLS: {selected_tools}\nOnly use these tools if they are truly necessary for the query. Prefer direct response when possible."
        else:
            tools_info = "\n".join([f"- {tool}" for tool in tools_list]) if tools_list else "- No specific tools available"
            tools_constraint = "\nNo tools are highly relevant for this query. Strongly consider direct response."
        
        system_prompt = f"""You are an expert AI system analyzer. Your job is to analyze user queries and determine the optimal processing strategy.

You must classify queries into complexity levels and execution strategies:

COMPLEXITY LEVELS:
- TRIVIAL: Simple math, basic facts (e.g., "What's 2+2?", "Capital of France?")
- SIMPLE: Single file operations, basic edits (e.g., "create utils.py", "edit main.py")
- MODERATE: Requires some reasoning or tool use (e.g., "Find recent AI news")
- COMPLEX: Multi-step problems (e.g., "Compare cloud providers and recommend one")
- RESEARCH: Deep analysis needed (e.g., "Analyze market trends and create strategy")

EXECUTION STRATEGIES:
- DIRECT_RESPONSE: Answer directly from knowledge
- SINGLE_TOOL: Use one tool (search, calculator, file operations, etc.)
- SEQUENTIAL: Multiple tools in sequence
- PARALLEL: Multiple tools simultaneously
- ITERATIVE: ReAct pattern with reasoning loops

IMPORTANT FILE OPERATION RULES:
- Queries like "create [filename]", "edit [filename]", "write [filename]" should be SIMPLE complexity
- File operations should use SINGLE_TOOL strategy with WriteTool or EditTool
- Only use SEQUENTIAL strategy if multiple distinct operations are needed

AVAILABLE TOOLS:
{tools_info}{tools_constraint}

When selecting required_tools, ONLY use tool names from the available tools list above.
If no suitable tools are available, use an empty list [].

Always respond in JSON format with:
{{
  "complexity": "one of the complexity levels",
  "strategy": "one of the execution strategies", 
  "confidence": float between 0-1,
  "required_tools": ["exact tool names from available tools list"],
  "estimated_steps": integer,
  "user_intent": "what user wants to achieve",
  "reasoning": "why you chose this classification"
}}"""

        analysis_prompt = f"""
        Analyze this query: "{query}"
        
        Context: {context or "No additional context"}
        
        Consider:
        1. What is the user actually trying to accomplish?
        2. How complex is this cognitively?
        3. What tools/capabilities would be needed?
        4. What's the most efficient execution strategy?
        5. How confident are you in this analysis?
        
        Provide detailed analysis in the specified JSON format.
        """
        
        try:
            # Use LLM for analysis
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = self._get_llm_response(messages)
            result = self._parse_analysis_response(response)
            
            # Get LLM suggested tools and filter them through our relevance scoring
            llm_suggested_tools = result.get('required_tools', [])
            
            # Filter to only include tools from our selected best tools
            final_required_tools = []
            if llm_suggested_tools and selected_tools:
                # Prefer our selected tools over LLM suggestions
                final_required_tools = [tool for tool in llm_suggested_tools if tool in selected_tools]
                # If LLM didn't suggest any of our selected tools, use the highest scoring one
                if not final_required_tools and selected_tools:
                    final_required_tools = [selected_tools[0]]
            elif selected_tools:
                # Use our selected tools if LLM didn't suggest any
                final_required_tools = selected_tools[:1]  # Use only the best tool
            
            # Use our improved strategy determination
            strategy = self._determine_execution_strategy(query, final_required_tools)
            
            return QueryAnalysis(
                complexity=QueryComplexity(result.get('complexity', 'simple').lower()),
                strategy=strategy,
                confidence=float(result.get('confidence', 0.7)),
                required_tools=final_required_tools,
                estimated_steps=max(1, len(final_required_tools)),
                user_intent=result.get('user_intent', 'Unknown'),
                reasoning=result.get('reasoning', 'Analysis completed') + f" [Strategy: {strategy.value}, Tools: {final_required_tools}]"
            )
            
        except Exception as e:
            print(f"Analysis error: {e}")
            # Fallback to heuristic analysis
            return self._fallback_analysis(query)
    
    def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM."""
        try:
            llm = get_llm()
            return llm.chat(messages)
        except Exception as e:
            raise AnalysisError(f"LLM communication failed: {e}")
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM with robust error handling."""
        try:
            # Try to extract JSON from response - look for complete JSON objects
            json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            
            for json_candidate in json_matches:
                try:
                    # Clean control characters and common issues
                    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_candidate)
                    # Fix common JSON issues
                    json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                    json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                    # Try to parse this candidate
                    parsed = json.loads(json_str)
                    # Validate it has expected fields
                    if isinstance(parsed, dict) and ('complexity' in parsed or 'strategy' in parsed):
                        return parsed
                except json.JSONDecodeError:
                    continue
            
            # If no valid JSON found, try simpler extraction
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                return json.loads(json_str)
            else:
                # If no JSON found, return basic structure
                return {"response": response}
                
        except json.JSONDecodeError as e:
            # Log the problematic response for debugging
            print(f"JSON parsing failed for response: {response[:200]}...")
            raise AnalysisError(f"Failed to parse LLM response: {e}")
    
    def _score_tool_relevance(self, tool_name: str, query: str, tool_instance) -> float:
        """Score how relevant a tool is for this specific query (0.0 to 1.0)"""
        
        # Get tool's own confidence score if it has one
        base_score = 0.5
        if hasattr(tool_instance, 'relevance_score'):
            try:
                base_score = tool_instance.relevance_score(query)
            except Exception:
                pass
        
        # Apply query-specific scoring
        query_lower = query.lower()
        
        # High relevance tools for specific patterns
        if tool_name == 'GoogleSearchTool':
            if any(word in query_lower for word in ['search', 'find', 'recent', 'current', 'latest', 'news', 'web']):
                return min(base_score + 0.4, 1.0)
            elif any(word in query_lower for word in ['what is', 'who is', 'when', 'where']):
                return min(base_score + 0.2, 1.0)
        
        elif tool_name == 'WriteTool':
            if any(word in query_lower for word in ['create', 'write', 'new file', 'generate file']):
                return min(base_score + 0.4, 1.0)
        
        elif tool_name == 'EditTool':
            if any(word in query_lower for word in ['edit', 'modify', 'update', 'change', 'add to']):
                return min(base_score + 0.4, 1.0)
        
        elif tool_name == 'ReadTool':
            if any(word in query_lower for word in ['read', 'view', 'show', 'display', 'content of']):
                return min(base_score + 0.3, 1.0)
        
        elif tool_name == 'CodingTool':
            if any(word in query_lower for word in ['code', 'program', 'script', 'function', 'class']):
                return min(base_score + 0.3, 1.0)
        
        # Reduce score for commonly over-used tools
        elif tool_name in ['GitIntegrationTool', 'E2BCodeSandboxTool', 'FirecrawlTool']:
            if tool_name == 'GitIntegrationTool' and not any(word in query_lower for word in ['git', 'commit', 'branch', 'repository', 'version control']):
                return base_score * 0.2
            elif tool_name == 'E2BCodeSandboxTool' and not any(word in query_lower for word in ['execute', 'run code', 'sandbox', 'test']):
                return base_score * 0.2
            elif tool_name == 'FirecrawlTool' and not any(word in query_lower for word in ['scrape', 'crawl', 'website', 'url']):
                return base_score * 0.2
        
        # Reduce score for advanced tools on simple queries
        simple_query_indicators = ['what is', 'how to', 'explain', 'define']
        if any(indicator in query_lower for indicator in simple_query_indicators):
            if tool_name in ['E2BCodeSandboxTool', 'GitIntegrationTool', 'FirecrawlTool', 'AdvancedMathTool']:
                return base_score * 0.1
        
        # Heavily reduce CalculatorTool score for conversational/opinion queries
        if tool_name == 'CalculatorTool':
            conversational_indicators = [
                'think about', 'opinion', 'future of', 'thoughts about', 
                'artificial intelligence', 'machine learning', 'your view',
                'do you feel', 'believe that', 'philosophy', 'perspective'
            ]
            if any(indicator in query_lower for indicator in conversational_indicators):
                return 0.1  # Very low score for conversational queries
        
        return base_score
    
    def _select_best_tools(self, capable_tools: List[str], query: str, tools_registry: Dict) -> List[str]:
        """Select the most relevant tools, not all capable ones"""
        if not capable_tools:
            return []
        
        tool_scores = []
        for tool_name in capable_tools:
            tool_instance = tools_registry.get(tool_name)
            if tool_instance:
                score = self._score_tool_relevance(tool_name, query, tool_instance)
                tool_scores.append((tool_name, score))
        
        # Sort by score and take top tools with minimum threshold
        tool_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select tools with score > 0.7, maximum 2 tools
        selected_tools = []
        for tool_name, score in tool_scores:
            if score > 0.7 and len(selected_tools) < 2:
                selected_tools.append(tool_name)
        
        # Only include the highest scoring tool if it's above 0.6 (raised threshold)
        if not selected_tools and tool_scores and tool_scores[0][1] > 0.6:
            selected_tools.append(tool_scores[0][0])
        
        print(f"Tool relevance scores: {[(name, f'{score:.2f}') for name, score in tool_scores[:5]]}")
        print(f"Selected tools: {selected_tools}")
        
        return selected_tools
    
    def _determine_execution_strategy(self, query: str, required_tools: List[str]) -> ExecutionStrategy:
        """More conservative strategy selection"""
        
        query_lower = query.lower()
        
        # Direct response for knowledge questions
        knowledge_indicators = ['what is', 'explain', 'how does', 'why', 'define', 'describe', 'tell me about']
        if any(indicator in query_lower for indicator in knowledge_indicators):
            return ExecutionStrategy.DIRECT_RESPONSE
        
        # Direct response for conversational/opinion questions
        conversational_indicators = [
            'what do you think', 'your opinion', 'do you believe', 'your thoughts',
            'how do you feel', 'your perspective', 'what are your views'
        ]
        if any(indicator in query_lower for indicator in conversational_indicators):
            return ExecutionStrategy.DIRECT_RESPONSE
        
        # Direct response for conceptual questions
        if any(word in query_lower for word in ['concept', 'theory', 'principle', 'meaning', 'difference between']):
            return ExecutionStrategy.DIRECT_RESPONSE
        
        # Single tool for clear tool-specific requests
        if len(required_tools) == 1:
            return ExecutionStrategy.SINGLE_TOOL
        
        # Sequential only for clearly multi-step tasks
        multi_step_indicators = ['analyze and create', 'search and summarize', 'find and compare', 'read and modify', 'create and edit']
        if len(required_tools) > 1 and any(indicator in query_lower for indicator in multi_step_indicators):
            return ExecutionStrategy.SEQUENTIAL
        
        # For multiple tools but no clear multi-step indicators, try single tool with best one
        if len(required_tools) > 1:
            return ExecutionStrategy.SINGLE_TOOL  # Use highest scoring tool only
        
        # Default to direct response when uncertain
        return ExecutionStrategy.DIRECT_RESPONSE
    
    def _fallback_analysis(self, query: str) -> QueryAnalysis:
        """
        Fallback analysis using heuristics when LLM fails.
        
        Args:
            query: User query
            
        Returns:
            QueryAnalysis based on simple heuristics
        """
        word_count = len(query.split())
        has_question = '?' in query
        query_lower = query.lower()
        
        # File operation patterns
        file_create_patterns = ['create', 'new file', 'write', 'writetool']
        file_edit_patterns = ['edit', 'modify', 'update', 'change', 'edittool']
        file_extensions = ['.py', '.js', '.html', '.css', '.md', '.txt', '.json']
        
        # Check for simple file operations first
        is_file_create = any(pattern in query_lower for pattern in file_create_patterns) and any(ext in query_lower for ext in file_extensions)
        is_file_edit = any(pattern in query_lower for pattern in file_edit_patterns) and any(ext in query_lower for ext in file_extensions)
        
        # Simple file operations should be SIMPLE complexity with SINGLE_TOOL strategy
        if is_file_create or is_file_edit:
            if is_file_create:
                required_tools = ['WriteTool']
                user_intent = "Create a new file"
            else:
                required_tools = ['EditTool']
                user_intent = "Edit an existing file"
            
            return QueryAnalysis(
                complexity=QueryComplexity.SIMPLE,
                strategy=ExecutionStrategy.SINGLE_TOOL,
                confidence=0.8,  # High confidence for clear file operations
                required_tools=required_tools,
                estimated_steps=1,
                user_intent=user_intent,
                reasoning=f"Detected simple file operation: {user_intent.lower()}"
            )
        
        # Original logic for other patterns
        action_words = ['create', 'build', 'analyze', 'compare', 'research', 'generate']
        tool_words = ['search', 'find', 'calculate', 'compute', 'scrape', 'get']
        
        # Determine complexity
        if word_count <= 5 and has_question:
            complexity = QueryComplexity.TRIVIAL
        elif any(word in query_lower for word in action_words):
            if word_count > 15:
                complexity = QueryComplexity.COMPLEX
            else:
                complexity = QueryComplexity.MODERATE
        elif any(word in query_lower for word in tool_words):
            complexity = QueryComplexity.MODERATE
        else:
            complexity = QueryComplexity.SIMPLE
        
        # Determine strategy
        if complexity == QueryComplexity.TRIVIAL:
            strategy = ExecutionStrategy.DIRECT_RESPONSE
        elif any(word in query_lower for word in tool_words):
            strategy = ExecutionStrategy.SINGLE_TOOL
        elif complexity in [QueryComplexity.COMPLEX, QueryComplexity.RESEARCH]:
            strategy = ExecutionStrategy.SEQUENTIAL
        else:
            strategy = ExecutionStrategy.DIRECT_RESPONSE
        
        # Determine required tools
        required_tools = []
        if 'search' in query_lower or 'find' in query_lower:
            required_tools.append('web_search')
        if any(word in query_lower for word in ['calculate', 'compute', 'math']):
            required_tools.append('calculator')
        if any(word in query_lower for word in ['code', 'program', 'script']):
            required_tools.append('code_generator')
        
        return QueryAnalysis(
            complexity=complexity,
            strategy=strategy,
            confidence=0.6,  # Lower confidence for fallback
            required_tools=required_tools,
            estimated_steps=len(required_tools) if required_tools else 1,
            user_intent="Fallback analysis - intent unclear",
            reasoning="Used fallback heuristics due to LLM analysis failure"
        )
