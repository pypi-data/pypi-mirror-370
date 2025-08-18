"""
Firecrawl Tool for Metis Agent.

This tool provides advanced web scraping capabilities using the Firecrawl API.
"""
from typing import Any, Dict, List, Optional
import re
import json
import requests
from ..auth.api_key_manager import APIKeyManager
from .base import BaseTool


class FirecrawlTool(BaseTool):
    """
    Provides advanced web scraping capabilities for extracting structured data from websites.
    Use for tasks that require detailed information from specific web pages.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Firecrawl tool.
        
        Args:
            api_key: Firecrawl API key (optional)
        """
        # Get API key if not provided
        if api_key is None:
            key_manager = APIKeyManager()
            api_key = key_manager.get_key("firecrawl")
            
        if api_key is None:
            raise ValueError("Firecrawl API key not found. Please provide it or set it using APIKeyManager.")
            
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v1"
        
        # Rate limiting and caching
        self.cache = {}
        self.max_cache_size = 50
        
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
        
        # Check for web scraping keywords
        scraping_keywords = {
            'scrape', 'crawl', 'extract', 'parse', 'harvest', 'gather',
            'website', 'webpage', 'web page', 'web site', 'url', 'link',
            'html', 'content', 'data', 'information', 'text', 'table',
            'firecrawl', 'web scraping', 'web crawling', 'web extraction'
        }
        
        # Check for web scraping keywords
        if any(keyword in words for keyword in scraping_keywords):
            return True
            
        # Check for web scraping phrases
        scraping_phrases = [
            'scrape website', 'extract data from', 'crawl website',
            'extract content from', 'parse website', 'extract information from',
            'gather data from website', 'extract text from', 'extract table from',
            'scrape data from', 'extract html from', 'crawl web page'
        ]
        
        if any(phrase in task_lower for phrase in scraping_phrases):
            return True
            
        # Check for URL patterns
        url_patterns = [
            r'https?://\S+',
            r'www\.\S+',
            r'\S+\.(com|org|net|edu|gov|io|co|ai)\S*'
        ]
        
        for pattern in url_patterns:
            if re.search(pattern, task_lower):
                return True
                
        return False
        
    def execute(self, task: str) -> str:
        """
        Perform web scraping based on the task description.
        
        Args:
            task: The scraping task
            
        Returns:
            Scraped data
        """
        # Extract URL and scraping parameters from task
        url, params = self._extract_parameters(task)
        
        if not url:
            return "No URL found in the task. Please provide a valid URL to scrape."
            
        # Create cache key
        cache_key = f"{url}_{json.dumps(params)}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Perform scraping
        try:
            results = self._scrape(url, params)
            
            # Format results
            formatted_results = self._format_results(results, url)
            
            # Cache results
            if len(self.cache) >= self.max_cache_size:
                # Remove oldest entry
                self.cache.pop(next(iter(self.cache)))
                
            self.cache[cache_key] = formatted_results
            
            return formatted_results
            
        except Exception as e:
            return f"Error performing web scraping: {str(e)}"
        
    def _extract_parameters(self, task: str) -> tuple:
        """
        Extract URL and scraping parameters from the task description.
        
        Args:
            task: The task description
            
        Returns:
            Tuple of (URL, parameters)
        """
        # Extract URL
        url_patterns = [
            r'https?://\S+',
            r'www\.\S+',
            r'\S+\.(com|org|net|edu|gov|io|co|ai)\S*'
        ]
        
        url = None
        for pattern in url_patterns:
            match = re.search(pattern, task)
            if match:
                url = match.group(0)
                # Clean up URL if needed
                if url.endswith('.') or url.endswith(',') or url.endswith(')'):
                    url = url[:-1]
                break
                
        # Default parameters
        params = {
            "elements": "main",
            "include_html": False,
            "include_links": True,
            "include_images": False
        }
        
        # Extract parameters from task
        if "extract table" in task.lower() or "extract tables" in task.lower():
            params["elements"] = "table"
        elif "extract image" in task.lower() or "extract images" in task.lower():
            params["elements"] = "img"
            params["include_images"] = True
        elif "extract link" in task.lower() or "extract links" in task.lower():
            params["elements"] = "a"
            params["include_links"] = True
        elif "extract html" in task.lower():
            params["include_html"] = True
            
        return url, params
        
    def _scrape(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform web scraping.
        
        Args:
            url: URL to scrape
            params: Scraping parameters
            
        Returns:
            Scraped data
        """
        # In a real implementation, this would call the Firecrawl API
        # For now, we'll simulate the response
        
        # Simulate API call
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "elements": params["elements"],
            "include_html": params["include_html"],
            "include_links": params["include_links"],
            "include_images": params["include_images"]
        }
        
        # For simulation purposes, we'll just return a mock response
        # In a real implementation, this would be:
        # response = requests.post(f"{self.base_url}/scrape", headers=headers, json=payload)
        # return response.json()
        
        # Mock response
        return {
            "success": True,
            "url": url,
            "title": f"Page title for {url}",
            "content": f"This is the extracted content from {url}. It would contain the actual scraped content in a real implementation.",
            "links": [
                {"text": "Link 1", "url": "https://example.com/link1"},
                {"text": "Link 2", "url": "https://example.com/link2"}
            ] if params["include_links"] else [],
            "images": [
                {"alt": "Image 1", "src": "https://example.com/image1.jpg"},
                {"alt": "Image 2", "src": "https://example.com/image2.jpg"}
            ] if params["include_images"] else [],
            "html": "<div>Sample HTML content</div>" if params["include_html"] else None
        }
        
    def _format_results(self, results: Dict[str, Any], url: str) -> str:
        """
        Format scraping results.
        
        Args:
            results: Scraping results
            url: Scraped URL
            
        Returns:
            Formatted results
        """
        if not results.get("success", False):
            return f"Failed to scrape {url}: {results.get('error', 'Unknown error')}"
            
        formatted = f"Scraped content from {url}:\n\n"
        
        # Add title
        if "title" in results:
            formatted += f"Title: {results['title']}\n\n"
            
        # Add content
        if "content" in results:
            formatted += f"Content:\n{results['content']}\n\n"
            
        # Add links
        if "links" in results and results["links"]:
            formatted += "Links:\n"
            for i, link in enumerate(results["links"], 1):
                formatted += f"{i}. {link.get('text', 'No text')}: {link.get('url', 'No URL')}\n"
            formatted += "\n"
            
        # Add images
        if "images" in results and results["images"]:
            formatted += "Images:\n"
            for i, image in enumerate(results["images"], 1):
                formatted += f"{i}. {image.get('alt', 'No alt text')}: {image.get('src', 'No source')}\n"
            formatted += "\n"
            
        # Add HTML
        if "html" in results and results["html"]:
            formatted += "HTML (sample):\n"
            html_sample = results["html"][:500] + "..." if len(results["html"]) > 500 else results["html"]
            formatted += f"{html_sample}\n\n"
            
        return formatted
        
    def get_examples(self) -> List[str]:
        """
        Get example tasks that this tool can handle.
        
        Returns:
            List of example tasks
        """
        return [
            "Scrape content from https://example.com",
            "Extract data from the website www.example.org",
            "Extract tables from https://example.com/data",
            "Extract links from https://example.com/resources",
            "Extract images from https://example.com/gallery",
            "Crawl website https://example.com and extract main content",
            "Parse the webpage at https://example.com/article",
            "Extract HTML from https://example.com/page",
            "Gather information from https://example.com/about",
            "Extract text content from https://example.com/blog"
        ]