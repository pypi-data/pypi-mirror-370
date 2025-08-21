#!/usr/bin/env python3
"""
Framework-Compliant WebScraperTool - Follows Metis Agent Tools Framework v2.0
Robust web scraping with intelligent content extraction and API integration.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re
import time
import json
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser
import hashlib

from ..base import BaseTool


class WebScraperTool(BaseTool):
    """
    Production-ready web scraping tool with intelligent content extraction.
    
    This tool handles web scraping, content extraction, API interaction,
    robots.txt compliance, rate limiting, and structured data extraction.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize web scraper tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "WebScraperTool"  # MUST match class name exactly
        self.description = "Robust web scraping with intelligent content extraction and API integration"
        
        # Optional metadata
        self.version = "2.0.0"
        self.category = "core_tools"
        
        # Web scraping configuration
        self.default_timeout = 30
        self.max_retries = 3
        self.rate_limit_delay = 1.0  # seconds between requests
        self.max_content_size = 10 * 1024 * 1024  # 10MB limit
        self.max_redirects = 10
        
        # User agents for different scenarios
        self.user_agents = {
            'desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'bot': 'Mozilla/5.0 (compatible; MetisBot/1.0; +https://metis-agent.com/bot)'
        }
        
        # Scraping operation types
        self.operation_types = {
            'scrape': ['scrape', 'extract', 'fetch', 'get', 'download', 'retrieve'],
            'parse': ['parse', 'analyze', 'process', 'structure', 'format'],
            'monitor': ['monitor', 'watch', 'track', 'observe', 'check'],
            'api': ['api', 'endpoint', 'json', 'rest', 'graphql'],
            'search': ['search', 'find', 'locate', 'discover', 'query']
        }
        
        # Content type handlers
        self.content_handlers = {
            'html': self._handle_html_content,
            'json': self._handle_json_content,
            'xml': self._handle_xml_content,
            'text': self._handle_text_content,
            'csv': self._handle_csv_content
        }
        
        # Common selectors for structured data
        self.structured_selectors = {
            'title': ['title', 'h1', '.title', '#title', '[data-title]'],
            'description': ['meta[name="description"]', '.description', '.summary'],
            'author': ['.author', '.by-author', '[data-author]', '.byline'],
            'date': ['.date', '.published', '[datetime]', 'time'],
            'content': ['.content', '.article-body', '.post-content', 'main'],
            'links': ['a[href]'],
            'images': ['img[src]'],
            'price': ['.price', '.cost', '[data-price]'],
            'rating': ['.rating', '.score', '[data-rating]']
        }
    
    def can_handle(self, task: str) -> bool:
        """Intelligent web scraping task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        Handles web scraping, content extraction, and API interaction tasks.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires web scraping, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Web scraping keywords
        web_keywords = {
            'scrape', 'scraping', 'extract', 'fetch', 'download', 'crawl',
            'parse', 'website', 'webpage', 'url', 'html', 'web', 'api',
            'endpoint', 'json', 'xml', 'content', 'data', 'information'
        }
        
        has_web_keyword = any(keyword in task_clean for keyword in web_keywords)
        
        # Layer 2: Operation detection
        has_operation = any(
            any(op_word in task_clean for op_word in op_words)
            for op_words in self.operation_types.values()
        )
        
        # Layer 3: URL detection
        url_pattern = r'https?://[^\s]+'
        has_url = bool(re.search(url_pattern, task, re.IGNORECASE))
        
        # Layer 4: Domain/website mentions
        domain_patterns = [
            r'\b\w+\.(com|org|net|edu|gov|io|co)\b',
            r'from\s+\w+\.(com|org|net)',
            r'website\s+\w+'
        ]
        has_domain = any(re.search(pattern, task_clean) for pattern in domain_patterns)
        
        # Layer 5: Exclusion filters
        exclusion_patterns = [
            'create website', 'build website', 'design website',
            'make website', 'develop website', 'host website'
        ]
        
        has_exclusion = any(pattern in task_clean for pattern in exclusion_patterns)
        
        # Decision logic
        if has_exclusion:
            return False
        
        return (has_web_keyword and has_operation) or has_url or has_domain
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute web scraping task with robust error handling.
        
        Args:
            task: Web scraping task to perform
            **kwargs: Additional parameters (url, selectors, headers, etc.)
            
        Returns:
            Structured dictionary with scraping results
        """
        start_time = time.time()
        
        try:
            # Extract parameters
            url = kwargs.get('url', '')
            selectors = kwargs.get('selectors', {})
            headers = kwargs.get('headers', {})
            user_agent_type = kwargs.get('user_agent', 'desktop')
            follow_redirects = kwargs.get('follow_redirects', True)
            respect_robots = kwargs.get('respect_robots', True)
            extract_type = kwargs.get('extract_type', 'auto')
            
            # Detect operation type
            operation = self._detect_operation(task)
            
            # Extract URL from task if not provided
            if not url:
                url = self._extract_url_from_task(task)
            
            if not url:
                return self._error_response("No URL found in task or parameters")
            
            # Validate and normalize URL
            url = self._normalize_url(url)
            
            # Check robots.txt if requested
            if respect_robots and not self._check_robots_txt(url):
                return self._error_response(f"Robots.txt disallows scraping {url}")
            
            # Perform the scraping operation
            result = self._perform_scraping_operation(
                operation, url, selectors, headers, user_agent_type, 
                follow_redirects, extract_type, task
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Return success response
            return {
                'success': True,
                'type': 'web_scraping_response',
                'data': result,
                'metadata': {
                    'tool_name': self.name,
                    'timestamp': datetime.now().isoformat(),
                    'execution_time': f"{execution_time:.3f}s",
                    'operation': operation,
                    'url': url,
                    'respect_robots': respect_robots
                }
            }
            
        except Exception as e:
            return self._error_response(f"Web scraping failed: {str(e)}", e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect the type of web scraping operation requested."""
        task_lower = task.lower()
        
        for operation, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                return operation
        
        return 'scrape'  # Default operation
    
    def _extract_url_from_task(self, task: str) -> str:
        """Extract URL from the task description."""
        # Look for URLs in the task
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, task)
        
        if urls:
            return urls[0].rstrip('.,;!?')
        
        # Look for domain mentions
        domain_pattern = r'(?:from|scrape|visit)\s+(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        domain_match = re.search(domain_pattern, task, re.IGNORECASE)
        
        if domain_match:
            domain = domain_match.group(1)
            return f"https://{domain}"
        
        return ''
    
    def _normalize_url(self, url: str) -> str:
        """Normalize and validate URL."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        return url
    
    def _check_robots_txt(self, url: str) -> bool:
        """Check if robots.txt allows scraping this URL."""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            user_agent = self.user_agents.get('bot', '*')
            return rp.can_fetch(user_agent, url)
        except Exception:
            # If we can't check robots.txt, assume it's allowed
            return True
    
    def _perform_scraping_operation(self, operation: str, url: str, selectors: Dict[str, Any],
                                  headers: Dict[str, str], user_agent_type: str,
                                  follow_redirects: bool, extract_type: str, task: str) -> Dict[str, Any]:
        """Perform the specific web scraping operation."""
        
        if operation == 'scrape':
            return self._scrape_content(url, selectors, headers, user_agent_type, follow_redirects, extract_type)
        elif operation == 'api':
            return self._handle_api_request(url, headers, user_agent_type)
        elif operation == 'monitor':
            return self._monitor_changes(url, headers, user_agent_type)
        elif operation == 'search':
            return self._search_content(url, task, headers, user_agent_type)
        else:
            return self._scrape_content(url, selectors, headers, user_agent_type, follow_redirects, extract_type)
    
    def _scrape_content(self, url: str, selectors: Dict[str, Any], headers: Dict[str, str],
                       user_agent_type: str, follow_redirects: bool, extract_type: str) -> Dict[str, Any]:
        """Scrape content from a web page."""
        try:
            import requests
        except ImportError:
            raise ImportError("requests library is required. Install with: pip install requests")
        
        # Prepare headers
        request_headers = {
            'User-Agent': self.user_agents.get(user_agent_type, self.user_agents['desktop']),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        request_headers.update(headers)
        
        # Configure session
        session = requests.Session()
        session.headers.update(request_headers)
        
        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                response = session.get(
                    url,
                    timeout=self.default_timeout,
                    allow_redirects=follow_redirects,
                    stream=True
                )
                
                # Check content size
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.max_content_size:
                    raise ValueError(f"Content too large: {content_length} bytes")
                
                response.raise_for_status()
                break
                
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(self.rate_limit_delay * (attempt + 1))
        
        # Process response based on content type
        content_type = response.headers.get('content-type', '').lower()
        
        # Determine handler
        handler = None
        for content_key, content_handler in self.content_handlers.items():
            if content_key in content_type:
                handler = content_handler
                break
        
        if not handler:
            handler = self._handle_text_content
        
        # Extract content
        extracted_data = handler(response, selectors)
        
        return {
            'url': url,
            'status_code': response.status_code,
            'content_type': content_type,
            'headers': dict(response.headers),
            'extracted_data': extracted_data,
            'response_time': response.elapsed.total_seconds(),
            'final_url': response.url,  # After redirects
            'encoding': response.encoding
        }
    
    def _handle_html_content(self, response, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML content extraction."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("beautifulsoup4 library is required. Install with: pip install beautifulsoup4")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        extracted = {}
        
        # Use custom selectors if provided
        if selectors:
            for key, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    if len(elements) == 1:
                        extracted[key] = elements[0].get_text(strip=True)
                    else:
                        extracted[key] = [elem.get_text(strip=True) for elem in elements]
        else:
            # Use default structured selectors
            for data_type, selector_list in self.structured_selectors.items():
                for selector in selector_list:
                    elements = soup.select(selector)
                    if elements:
                        if data_type in ['links', 'images']:
                            if data_type == 'links':
                                extracted[data_type] = [elem.get('href') for elem in elements if elem.get('href')][:20]
                            else:
                                extracted[data_type] = [elem.get('src') for elem in elements if elem.get('src')][:10]
                        else:
                            extracted[data_type] = elements[0].get_text(strip=True)
                        break
        
        # Additional metadata
        extracted['meta'] = {
            'title': soup.title.string if soup.title else None,
            'description': None,
            'keywords': None
        }
        
        # Extract meta tags
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            extracted['meta']['description'] = meta_desc.get('content')
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            extracted['meta']['keywords'] = meta_keywords.get('content')
        
        # Extract structured data (JSON-LD)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            structured_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured_data.append(data)
                except json.JSONDecodeError:
                    continue
            if structured_data:
                extracted['structured_data'] = structured_data
        
        return extracted
    
    def _handle_json_content(self, response, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON content extraction."""
        try:
            data = response.json()
            
            if selectors:
                # Extract specific fields using selectors
                extracted = {}
                for key, path in selectors.items():
                    value = self._extract_json_path(data, path)
                    if value is not None:
                        extracted[key] = value
                return extracted
            else:
                return data
                
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON: {str(e)}', 'raw_content': response.text[:1000]}
    
    def _handle_xml_content(self, response, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Handle XML content extraction."""
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.text)
            
            extracted = {}
            
            if selectors:
                for key, xpath in selectors.items():
                    elements = root.findall(xpath)
                    if elements:
                        if len(elements) == 1:
                            extracted[key] = elements[0].text
                        else:
                            extracted[key] = [elem.text for elem in elements]
            else:
                # Basic XML structure extraction
                extracted = self._xml_to_dict(root)
            
            return extracted
            
        except ET.ParseError as e:
            return {'error': f'Invalid XML: {str(e)}', 'raw_content': response.text[:1000]}
    
    def _handle_text_content(self, response, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Handle plain text content."""
        text = response.text
        
        extracted = {
            'content': text,
            'length': len(text),
            'lines': len(text.splitlines()),
            'words': len(text.split())
        }
        
        # Extract patterns if selectors provided
        if selectors:
            for key, pattern in selectors.items():
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    extracted[key] = matches
        
        return extracted
    
    def _handle_csv_content(self, response, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CSV content extraction."""
        try:
            import csv
            import io
            
            csv_data = []
            reader = csv.DictReader(io.StringIO(response.text))
            
            for row in reader:
                csv_data.append(row)
                if len(csv_data) >= 1000:  # Limit rows
                    break
            
            return {
                'data': csv_data,
                'columns': reader.fieldnames if reader.fieldnames else [],
                'row_count': len(csv_data)
            }
            
        except Exception as e:
            return {'error': f'CSV parsing failed: {str(e)}', 'raw_content': response.text[:1000]}
    
    def _handle_api_request(self, url: str, headers: Dict[str, str], user_agent_type: str) -> Dict[str, Any]:
        """Handle API endpoint requests."""
        try:
            import requests
        except ImportError:
            raise ImportError("requests library is required. Install with: pip install requests")
        
        request_headers = {
            'User-Agent': self.user_agents.get(user_agent_type, self.user_agents['bot']),
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        }
        request_headers.update(headers)
        
        response = requests.get(url, headers=request_headers, timeout=self.default_timeout)
        response.raise_for_status()
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {'raw_response': response.text}
        
        return {
            'api_response': data,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'response_time': response.elapsed.total_seconds()
        }
    
    def _monitor_changes(self, url: str, headers: Dict[str, str], user_agent_type: str) -> Dict[str, Any]:
        """Monitor a webpage for changes."""
        # This is a simplified version - in production, you'd store previous states
        current_data = self._scrape_content(url, {}, headers, user_agent_type, True, 'auto')
        
        # Generate content hash for change detection
        content_hash = hashlib.md5(str(current_data.get('extracted_data', '')).encode()).hexdigest()
        
        return {
            'current_state': current_data,
            'content_hash': content_hash,
            'timestamp': datetime.now().isoformat(),
            'monitoring_url': url
        }
    
    def _search_content(self, url: str, task: str, headers: Dict[str, str], user_agent_type: str) -> Dict[str, Any]:
        """Search for specific content within a webpage."""
        # Extract search terms from task
        search_terms = self._extract_search_terms(task)
        
        # Scrape the content
        scraped_data = self._scrape_content(url, {}, headers, user_agent_type, True, 'auto')
        
        # Search within the extracted content
        search_results = []
        extracted_data = scraped_data.get('extracted_data', {})
        
        for term in search_terms:
            for key, value in extracted_data.items():
                if isinstance(value, str) and term.lower() in value.lower():
                    search_results.append({
                        'term': term,
                        'found_in': key,
                        'context': value[:200] + '...' if len(value) > 200 else value
                    })
        
        return {
            'search_terms': search_terms,
            'results': search_results,
            'total_matches': len(search_results),
            'scraped_data': scraped_data
        }
    
    def _extract_search_terms(self, task: str) -> List[str]:
        """Extract search terms from the task description."""
        # Look for quoted terms
        quoted_terms = re.findall(r'["\']([^"\]+)["\']', task)
        
        # Look for "search for" or "find" patterns
        search_patterns = [
            r'search for ([^\n.]+)',
            r'find ([^\n.]+)',
            r'look for ([^\n.]+)',
            r'locate ([^\n.]+)'
        ]
        
        terms = quoted_terms[:]
        
        for pattern in search_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            terms.extend(matches)
        
        # Clean and deduplicate terms
        cleaned_terms = []
        for term in terms:
            cleaned = term.strip().lower()
            if cleaned and cleaned not in cleaned_terms:
                cleaned_terms.append(cleaned)
        
        return cleaned_terms
    
    def _extract_json_path(self, data: Any, path: str) -> Any:
        """Extract value from JSON using dot notation path."""
        try:
            keys = path.split('.')
            current = data
            
            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list) and key.isdigit():
                    index = int(key)
                    current = current[index] if 0 <= index < len(current) else None
                else:
                    return None
                
                if current is None:
                    return None
            
            return current
        except (KeyError, IndexError, TypeError):
            return None
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Add children
        children = {}
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in children:
                if not isinstance(children[child.tag], list):
                    children[child.tag] = [children[child.tag]]
                children[child.tag].append(child_data)
            else:
                children[child.tag] = child_data
        
        result.update(children)
        return result
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text", "url", "selectors", "headers"],
            "output_types": ["structured_data", "json_data", "html_content"],
            "estimated_execution_time": "<30s",
            "requires_internet": True,
            "requires_filesystem": False,
            "concurrent_safe": True,
            "resource_intensive": True,
            "supported_intents": [
                "scrape", "extract", "fetch", "download", "parse",
                "monitor", "api", "search", "crawl"
            ],
            "api_dependencies": ["requests", "beautifulsoup4"],
            "memory_usage": "moderate",
            "web_operations": list(self.operation_types.keys()),
            "supported_content_types": list(self.content_handlers.keys()),
            "max_content_size": f"{self.max_content_size // (1024*1024)}MB",
            "default_timeout": f"{self.default_timeout}s"
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "Scrape the title and content from https://example.com",
            "Extract all links from the Wikipedia homepage",
            "Fetch JSON data from the API endpoint https://api.example.com/data",
            "Parse the product information from an e-commerce page",
            "Monitor changes on a news website",
            "Search for specific keywords in a webpage",
            "Extract structured data from a recipe website",
            "Scrape contact information from a business directory",
            "Download and parse CSV data from a data portal",
            "Extract metadata and images from a blog post"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        error_type = type(exception).__name__ if exception else 'ValidationError'
        
        suggestions = [
            "Ensure the task contains a valid URL or website reference",
            "Check that the website is accessible and not blocking requests",
            "Verify internet connectivity for web scraping tasks",
            "Install required dependencies: pip install requests beautifulsoup4",
            "Consider using custom headers or user agents for blocked sites",
            "Check robots.txt compliance if scraping is disallowed"
        ]
        
        # Add specific suggestions based on error type
        if 'timeout' in message.lower():
            suggestions.append(f"Request timed out after {self.default_timeout} seconds - try a faster connection")
        elif 'robots' in message.lower():
            suggestions.append("Set respect_robots=False to bypass robots.txt restrictions (use responsibly)")
        elif 'import' in message.lower():
            suggestions.append("Install missing dependencies with: pip install requests beautifulsoup4 lxml")
        
        return {
            'success': False,
            'error': message,
            'error_type': error_type,
            'suggestions': suggestions,
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_operations': list(self.operation_types.keys()),
                'max_content_size': self.max_content_size,
                'default_timeout': self.default_timeout
            }
        }
