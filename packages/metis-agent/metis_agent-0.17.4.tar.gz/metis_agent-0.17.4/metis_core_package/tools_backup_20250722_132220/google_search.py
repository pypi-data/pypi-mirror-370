"""
Google Search Tool for Metis Agent.

This tool provides web search capabilities using the Google Custom Search API.
"""
from typing import Any, Dict, List, Optional
import re
import json
import requests
from ..auth.api_key_manager import APIKeyManager
from .base import BaseTool


class GoogleSearchTool(BaseTool):
    """
    Performs web searches to gather information, research topics, and find relevant data.
    Use for any task that involves research, investigating, exploring, or collecting information.
    """
    
    def __init__(self, api_key: Optional[str] = None, cx: Optional[str] = None):
        """
        Initialize the Google search tool.
        
        Args:
            api_key: Google API key (optional)
            cx: Google Custom Search Engine ID (optional)
        """
        # Get API key if not provided
        if api_key is None:
            key_manager = APIKeyManager()
            api_key = key_manager.get_key("google")
            
        if api_key is None:
            raise ValueError("Google API key not found. Please provide it or set it using APIKeyManager.")
            
        self.api_key = api_key
        
        # Get Custom Search Engine ID if not provided
        if cx is None:
            key_manager = APIKeyManager()
            cx = key_manager.get_key("google_cx")
            
        # Use default CX if not found
        if cx is None:
            cx = "017576662512468239146:omuauf_lfve"  # Default public CSE
            
        self.cx = cx
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # Rate limiting and caching
        self.cache = {}
        self.max_cache_size = 100
        
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle the given task.
        
        Args:
            task: The task to check
            
        Returns:
            True if the tool can handle the task, False otherwise
        """
        task_lower = task.lower()
        words = set(re.findall(r'\b\w+\b', task_lower))
        
        # Check for research keywords
        research_keywords = {
            'search', 'find', 'research', 'look up', 'investigate', 'explore',
            'gather information', 'collect data', 'discover', 'locate',
            'information', 'data', 'facts', 'details', 'sources', 'references',
            'articles', 'papers', 'publications', 'news', 'current', 'recent',
            'latest', 'trends', 'developments', 'advancements', 'breakthroughs'
        }
        
        # Check for research keywords
        if any(keyword in words for keyword in research_keywords):
            return True
            
        # Check for research phrases
        research_phrases = [
            'search for', 'find information', 'research about', 'look up',
            'gather information', 'collect data', 'find out', 'learn about',
            'investigate', 'explore', 'discover', 'locate', 'find sources',
            'find references', 'find articles', 'find papers', 'find publications'
        ]
        
        if any(phrase in task_lower for phrase in research_phrases):
            return True
            
        return False
        
    def execute(self, task: str) -> str:
        """
        Perform a Google search based on the task description.
        
        Args:
            task: The search task
            
        Returns:
            Search results
        """
        # Extract search query from task
        query = self._extract_query(task)
        
        # Check cache first
        if query in self.cache:
            return self.cache[query]
            
        # Perform search
        try:
            results = self._search(query)
            
            # Format results
            formatted_results = self._format_results(results, query)
            
            # Cache results
            if len(self.cache) >= self.max_cache_size:
                # Remove oldest entry
                self.cache.pop(next(iter(self.cache)))
                
            self.cache[query] = formatted_results
            
            return formatted_results
            
        except Exception as e:
            return f"Error performing search: {str(e)}"
        
    def _extract_query(self, task: str) -> str:
        """
        Extract the search query from the task description.
        
        Args:
            task: The task description
            
        Returns:
            Search query
        """
        # Extract query from common patterns
        patterns = [
            r"search for (.+)",
            r"find information about (.+)",
            r"research about (.+)",
            r"look up (.+)",
            r"find (.+)",
            r"search (.+)",
            r"investigate (.+)",
            r"explore (.+)",
            r"gather information about (.+)",
            r"collect data on (.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        # If no pattern matches, use the whole task
        return task
        
    def _search(self, query: str) -> Dict[str, Any]:
        """
        Perform a Google search.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": 10  # Number of results
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Search failed with status code {response.status_code}: {response.text}")
            
        return response.json()
        
    def _format_results(self, results: Dict[str, Any], query: str) -> str:
        """
        Format search results.
        
        Args:
            results: Search results
            query: Search query
            
        Returns:
            Formatted results
        """
        if "items" not in results:
            return f"No results found for '{query}'."
            
        items = results["items"]
        
        formatted = f"Search results for '{query}':\n\n"
        
        for i, item in enumerate(items, 1):
            title = item.get("title", "No title")
            link = item.get("link", "No link")
            snippet = item.get("snippet", "No description")
            
            formatted += f"{i}. {title}\n"
            formatted += f"   URL: {link}\n"
            formatted += f"   Description: {snippet}\n\n"
            
        return formatted
        
    def get_examples(self) -> List[str]:
        """
        Get example tasks that this tool can handle.
        
        Returns:
            List of example tasks
        """
        return [
            "Research existing AI architectures",
            "Find information about cognitive science models",
            "Search for recent papers on machine learning",
            "Investigate current trends in natural language processing",
            "Explore approaches to knowledge representation",
            "Gather information about inference engines",
            "Look up best practices for AI testing",
            "Find examples of AI systems that demonstrate creative thinking",
            "Research benchmarks for evaluating AI cognition",
            "Collect data on AI implementation challenges"
        ]