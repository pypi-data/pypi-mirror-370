"""
Google Search Tool - MCP-compliant web search functionality.

Provides web search capabilities using the Google Custom Search API.
Follows MCP standards: stateless, no LLM dependencies, structured I/O.
"""

from typing import Any, Dict, List
import re
import requests
import datetime
from ..base import BaseTool


class GoogleSearchTool(BaseTool):
    """
    Performs web searches to gather information and research topics.
    
    This tool demonstrates MCP architecture:
    - Stateless operation (API keys provided by client)
    - No LLM dependencies
    - Structured input/output
    - Comprehensive error handling
    """
    
    def __init__(self):
        """Initialize Google search tool."""
        self.name = "Google Search"
        self.description = "Perform web searches using Google Custom Search API"
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.default_cx = "017576662512468239146:omuauf_lfve"  # Public CSE
    
    def can_handle(self, task: str) -> bool:
        """Check if task is a web search request."""
        if not task or not task.strip():
            return False
        
        task_lower = task.lower().strip()
        
        # Check for search keywords
        search_keywords = [
            "search", "find", "research", "look up", "investigate", "explore",
            "gather information", "collect data", "discover", "locate",
            "information", "data", "facts", "details", "sources", "references",
            "articles", "papers", "publications", "news", "current", "recent",
            "latest", "trends", "developments", "web search", "google"
        ]
        
        if any(keyword in task_lower for keyword in search_keywords):
            return True
        
        # Check for search phrases
        search_phrases = [
            "search for", "find information", "research about", "look up",
            "gather information", "collect data", "find out", "learn about",
            "investigate", "explore", "discover", "locate", "find sources",
            "find references", "find articles", "find papers", "web search"
        ]
        
        if any(phrase in task_lower for phrase in search_phrases):
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute web search."""
        if not task or not task.strip():
            return self._format_error_response(
                "Task cannot be empty",
                "INVALID_INPUT",
                ["Provide a search query or research request"]
            )
        
        # Extract API credentials from kwargs
        api_key = kwargs.get("google_api_key") or kwargs.get("api_key")
        cx = kwargs.get("google_cx") or kwargs.get("cx") or self.default_cx
        
        if not api_key:
            return self._format_error_response(
                "Google API key required",
                "MISSING_API_KEY",
                ["Provide google_api_key parameter", "Set up Google Custom Search API credentials"]
            )
        
        try:
            # Extract search query from task
            query = self._extract_query(task)
            
            if not query:
                return self._format_error_response(
                    "No valid search query found",
                    "NO_QUERY",
                    ["Provide a clear search term or question"]
                )
            
            # Perform search
            results = self._search(query, api_key, cx)
            
            # Format results
            formatted_results = self._format_results(results, query)
            
            return self._format_success_response({
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results.get("items", [])),
                "search_info": results.get("searchInformation", {})
            })
            
        except requests.RequestException as e:
            return self._format_error_response(
                f"Network error during search: {str(e)}",
                "NETWORK_ERROR",
                ["Check internet connection", "Verify API endpoint availability"]
            )
        except Exception as e:
            return self._format_error_response(
                f"Search error: {str(e)}",
                "SEARCH_ERROR",
                ["Check API key validity", "Verify search query format"]
            )
    
    def _extract_query(self, task: str) -> str:
        """Extract search query from task description."""
        # Remove common search prefixes
        task = task.strip()
        
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
            r"collect data on (.+)",
            r"web search (.+)",
            r"google (.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, use the whole task
        return task
    
    def _search(self, query: str, api_key: str, cx: str) -> Dict[str, Any]:
        """Perform Google Custom Search API request."""
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "num": 10,  # Number of results
            "safe": "active"  # Safe search
        }
        
        response = requests.get(self.base_url, params=params, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Search API failed with status {response.status_code}: {response.text}")
        
        return response.json()
    
    def _format_results(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Format search results into structured format."""
        if "items" not in results:
            return {
                "query": query,
                "items": [],
                "message": f"No results found for '{query}'"
            }
        
        items = results["items"]
        formatted_items = []
        
        for i, item in enumerate(items, 1):
            formatted_item = {
                "rank": i,
                "title": item.get("title", "No title"),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "No description"),
                "display_link": item.get("displayLink", ""),
                "formatted_url": item.get("formattedUrl", "")
            }
            formatted_items.append(formatted_item)
        
        return {
            "query": query,
            "items": formatted_items,
            "total_results": results.get("searchInformation", {}).get("totalResults", "0"),
            "search_time": results.get("searchInformation", {}).get("searchTime", "0")
        }
    
    def get_examples(self) -> List[str]:
        """Return example search queries."""
        return [
            "search for latest AI developments",
            "find information about machine learning trends",
            "research quantum computing breakthroughs",
            "look up Python best practices",
            "investigate climate change solutions",
            "explore renewable energy technologies",
            "find articles about space exploration",
            "search for cybersecurity best practices"
        ]
    
    def _format_success_response(self, data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a successful response."""
        return {
            "success": True,
            "type": "search_response",
            "data": data,
            "metadata": {
                "tool_name": self.__class__.__name__,
                "timestamp": datetime.datetime.now().isoformat(),
                **(metadata or {})
            }
        }
    
    def _format_error_response(self, error: str, error_code: str, suggestions: List[str] = None) -> Dict[str, Any]:
        """Format an error response."""
        return {
            "success": False,
            "error": error,
            "error_code": error_code,
            "suggestions": suggestions or [],
            "metadata": {
                "tool_name": self.__class__.__name__,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
