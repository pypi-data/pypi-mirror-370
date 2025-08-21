from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re
import time
import json
import requests
from urllib.parse import urlparse, urljoin
from collections import defaultdict
from ..base import BaseTool

class FirecrawlTool(BaseTool):
    """Production-ready web scraping tool with intelligent content extraction.
    
    This tool provides advanced web scraping capabilities using the Firecrawl API
    for extracting structured data, content, links, images, and tables from websites
    with intelligent parsing and content optimization.
    """
    
    def __init__(self):
        """Initialize Firecrawl tool with required attributes."""
        # Required attributes
        self.name = "FirecrawlTool"
        self.description = "Advanced web scraping and content extraction from websites using Firecrawl API"
        
        # Optional metadata
        self.version = "2.0.0"
        self.category = "advanced_tools"
        
        # Firecrawl API configuration
        self.base_url = "https://api.firecrawl.dev/v1"
        
        # Supported extraction types
        self.extraction_types = {
            'content': {
                'keywords': ['content', 'text', 'article', 'main content', 'body'],
                'firecrawl_mode': 'scrape',
                'elements': ['main', 'article', 'content', '.content'],
                'include_html': False
            },
            'table': {
                'keywords': ['table', 'tables', 'data table', 'tabular data'],
                'firecrawl_mode': 'scrape',
                'elements': ['table', 'tbody', 'tr', 'td'],
                'include_html': True
            },
            'links': {
                'keywords': ['links', 'urls', 'references', 'hyperlinks', 'anchors'],
                'firecrawl_mode': 'scrape',
                'elements': ['a', 'link'],
                'include_links': True
            },
            'images': {
                'keywords': ['images', 'pictures', 'photos', 'graphics', 'media'],
                'firecrawl_mode': 'scrape',
                'elements': ['img', 'picture', 'figure'],
                'include_images': True
            },
            'metadata': {
                'keywords': ['metadata', 'meta', 'title', 'description', 'seo'],
                'firecrawl_mode': 'scrape',
                'elements': ['head', 'meta', 'title'],
                'include_html': True
            },
            'full_page': {
                'keywords': ['full page', 'entire page', 'complete', 'everything', 'full content', 'whole page'],
                'firecrawl_mode': 'scrape',
                'elements': ['*'],
                'include_html': True
            }
        }
        
        # Scraping operation types
        self.operation_types = {
            'scrape': ['scrape', 'extract', 'get', 'fetch', 'retrieve', 'collect'],
            'crawl': ['crawl', 'spider', 'traverse', 'explore', 'index'],
            'parse': ['parse', 'analyze', 'process', 'decode', 'interpret'],
            'monitor': ['monitor', 'watch', 'track', 'observe', 'check']
        }
        
        # URL validation patterns
        self.url_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*'
        ]
        
        # Content format options
        self.format_options = {
            'text': 'plain text extraction',
            'html': 'HTML structure preservation',
            'markdown': 'markdown formatted content',
            'json': 'structured JSON data'
        }
        
        # Rate limiting and caching
        self.request_cache = {}
        self.max_cache_size = 100
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
    
    def can_handle(self, task: str) -> bool:
        """Intelligent web scraping task detection.
        
        Uses multi-layer analysis to determine if a task requires
        web scraping capabilities.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires web scraping, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_lower = task.strip().lower()
        
        # Layer 0: Early Exclusion Rules (filter out clearly non-scraping tasks)
        non_scraping_patterns = [
            r'send\s+(?:an\s+)?email',
            r'email\s+(?:to|someone)',
            r'calculate\s+\d',
            r'what.*weather',
            r'create\s+(?:a\s+)?(?:function|class|code)',
            r'write\s+(?:a\s+)?(?:blog|article|story)',
            r'debug\s+(?:this\s+)?code',
            r'translate\s+text',
            r'play\s+music',
            r'book\s+(?:a\s+)?flight'
        ]
        
        # Early exclusion for clearly non-scraping tasks
        if any(re.search(pattern, task_lower) for pattern in non_scraping_patterns):
            return False
        
        # Layer 1: Direct Scraping Keywords
        scraping_keywords = {
            'scrape', 'crawl', 'extract', 'parse', 'harvest', 'gather',
            'fetch', 'retrieve', 'collect', 'mine', 'spider'
        }
        
        if any(keyword in task_lower for keyword in scraping_keywords):
            return True
        
        # Layer 2: Web Content Keywords
        web_content_keywords = {
            'website', 'webpage', 'web page', 'web site', 'url', 'link',
            'html', 'content', 'data', 'information', 'text', 'table',
            'firecrawl', 'web scraping', 'web crawling', 'web extraction'
        }
        
        if any(keyword in task_lower for keyword in web_content_keywords):
            # Check if combined with extraction context
            extraction_context = any(word in task_lower for word in [
                'extract', 'get', 'scrape', 'fetch', 'retrieve', 'collect'
            ])
            if extraction_context:
                return True
        
        # Layer 3: Extraction Type Detection
        for extraction_type, info in self.extraction_types.items():
            if any(keyword in task_lower for keyword in info['keywords']):
                # Check if combined with web context
                web_context = any(word in task_lower for word in [
                    'website', 'web', 'url', 'page', 'site', 'from'
                ])
                if web_context:
                    return True
        
        # Layer 4: URL Pattern Recognition
        if any(re.search(pattern, task) for pattern in self.url_patterns):
            return True
        
        # Layer 5: Web Scraping Phrases
        scraping_phrases = [
            r'scrape\s+(website|web\s*page|url|site)',
            r'extract\s+(data|content|information)\s+from',
            r'crawl\s+(website|web\s*page|site)',
            r'get\s+(content|data)\s+from\s+(website|url)',
            r'fetch\s+(information|data)\s+from',
            r'parse\s+(website|web\s*page|html)',
            r'harvest\s+(data|content)\s+from'
        ]
        
        if any(re.search(phrase, task_lower) for phrase in scraping_phrases):
            return True
        
        # Layer 6: Domain and Web Technology Indicators
        web_indicators = {
            'html', 'css', 'javascript', 'dom', 'xpath', 'selector',
            'browser', 'chrome', 'firefox', 'headless'
        }
        
        if any(indicator in task_lower for indicator in web_indicators):
            # Check if combined with data extraction
            data_context = any(word in task_lower for word in [
                'extract', 'scrape', 'get', 'fetch', 'data', 'content'
            ])
            if data_context:
                return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute web scraping with robust error handling.
        
        Args:
            task: Web scraping task to perform
            **kwargs: Additional parameters (api_key, url, extraction_type, format, etc.)
            
        Returns:
            Structured dictionary with scraping results
        """
        start_time = time.time()
        
        try:
            # Input validation
            if not task or not isinstance(task, str):
                return self._error_response("Task must be a non-empty string")
            
            if not self.can_handle(task):
                return self._error_response("Task does not appear to be web scraping related")
            
            # Check for required API key
            api_key = kwargs.get("firecrawl_api_key") or kwargs.get("api_key")
            if not api_key:
                return self._error_response("Firecrawl API key required for web scraping operations")
            
            # Extract scraping parameters
            url = self._extract_url(task, kwargs.get('url'))
            extraction_type = self._detect_extraction_type(task, kwargs.get('extraction_type'))
            operation = self._detect_operation(task)
            output_format = self._detect_format(task, kwargs.get('format', 'text'))
            
            # Validate URL
            if not url:
                return self._error_response("No valid URL found in task or parameters")
            
            if not self._is_valid_url(url):
                return self._error_response(f"Invalid URL format: {url}")
            
            # Check cache first
            cache_key = self._generate_cache_key(url, extraction_type, output_format)
            if cache_key in self.request_cache:
                cached_result = self.request_cache[cache_key]
                cached_result['metadata']['cache_hit'] = True
                return cached_result
            
            # Rate limiting
            self._apply_rate_limiting()
            
            # Perform web scraping
            scraping_result = self._perform_scraping(url, extraction_type, operation, api_key, kwargs)
            
            if not scraping_result or not scraping_result.get('success'):
                error_msg = scraping_result.get('error', 'Web scraping operation failed') if scraping_result else 'Web scraping operation failed'
                return self._error_response(error_msg)
            
            # Format results
            formatted_result = self._format_scraping_results(scraping_result, output_format)
            
            execution_time = time.time() - start_time
            
            # Generate comprehensive scraping report
            scraping_report = {
                'scraping_info': {
                    'url': url,
                    'extraction_type': extraction_type,
                    'operation': operation,
                    'format': output_format,
                    'status': 'success'
                },
                'extracted_data': formatted_result['data'],
                'content_analysis': {
                    'content_length': len(str(formatted_result['data'])),
                    'data_type': formatted_result['data_type'],
                    'elements_found': formatted_result.get('elements_count', 0),
                    'quality_score': self._assess_content_quality(formatted_result)
                },
                'technical_details': {
                    'response_time': scraping_result.get('response_time', 0),
                    'content_size': scraping_result.get('content_size', 0),
                    'encoding': scraping_result.get('encoding', 'unknown'),
                    'status_code': scraping_result.get('status_code', 200)
                },
                'metadata': scraping_result.get('metadata', {})
            }
            
            # Cache successful results
            result = {
                'success': True,
                'result': scraping_report,
                'message': f"Successfully scraped {extraction_type} from {url}",
                'metadata': {
                    'tool_name': self.name,
                    'execution_time': execution_time,
                    'task_type': 'web_scraping',
                    'extraction_type': extraction_type,
                    'operation': operation,
                    'url': url,
                    'content_length': scraping_report['content_analysis']['content_length'],
                    'cache_hit': False
                }
            }
            
            self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            return self._error_response(f"Web scraping failed: {str(e)}", e)
    
    def _extract_url(self, task: str, explicit_url: str = None) -> Optional[str]:
        """Extract URL from task or use provided URL."""
        if explicit_url:
            return explicit_url
        
        # Try to extract URL from task
        for pattern in self.url_patterns:
            matches = re.findall(pattern, task)
            if matches:
                url = matches[0]
                # Clean up URL
                url = url.rstrip('.,;)]}')
                # Add protocol if missing
                if not url.startswith(('http://', 'https://')):
                    if url.startswith('www.'):
                        url = 'https://' + url
                    else:
                        url = 'https://' + url
                return url
        
        return None
    
    def _detect_extraction_type(self, task: str, explicit_type: str = None) -> str:
        """Detect the type of content to extract."""
        if explicit_type and explicit_type in self.extraction_types:
            return explicit_type
        
        task_lower = task.lower()
        
        # Check for specific multi-word patterns first
        if 'full page' in task_lower or ('full' in task_lower and 'page' in task_lower):
            return 'full_page'
        
        # Score each extraction type based on keyword matches
        scores = {}
        for extraction_type, info in self.extraction_types.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in task_lower:
                    # Give higher score for exact multi-word matches
                    if ' ' in keyword and keyword in task_lower:
                        score += 2
                    else:
                        score += 1
            scores[extraction_type] = score
        
        # Return highest scoring type
        if scores and max(scores.values()) > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Default based on common patterns
        if any(word in task_lower for word in ['table', 'data']):
            return 'table'
        elif any(word in task_lower for word in ['link', 'url']):
            return 'links'
        elif any(word in task_lower for word in ['image', 'photo']):
            return 'images'
        else:
            return 'content'  # Default
    
    def _detect_operation(self, task: str) -> str:
        """Detect the scraping operation type."""
        task_lower = task.lower()
        
        for operation, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                return operation
        
        return 'scrape'  # Default operation
    
    def _detect_format(self, task: str, explicit_format: str = None) -> str:
        """Detect the desired output format."""
        if explicit_format and explicit_format in self.format_options:
            return explicit_format
        
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['json', 'structured']):
            return 'json'
        elif any(word in task_lower for word in ['html', 'markup']):
            return 'html'
        elif any(word in task_lower for word in ['markdown', 'md']):
            return 'markdown'
        else:
            return 'text'
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and accessibility."""
        try:
            result = urlparse(url)
            # Only accept HTTP and HTTPS schemes
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False
    
    def _generate_cache_key(self, url: str, extraction_type: str, output_format: str) -> str:
        """Generate cache key for request."""
        return f"{url}_{extraction_type}_{output_format}"
    
    def _apply_rate_limiting(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _perform_scraping(self, url: str, extraction_type: str, operation: str, 
                         api_key: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the actual web scraping operation."""
        try:
            # Get extraction configuration
            config = self.extraction_types[extraction_type]
            
            # Prepare Firecrawl request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Build request payload
            payload = {
                "url": url,
                "formats": ["markdown", "html"] if config.get('include_html') else ["markdown"],
                "includeTags": config.get('elements', []),
                "excludeTags": kwargs.get('exclude_tags', []),
                "onlyMainContent": extraction_type == 'content',
                "includeLinks": config.get('include_links', False),
                "includeImages": config.get('include_images', False)
            }
            
            # Add additional options
            if kwargs.get('wait_for'):
                payload["waitFor"] = kwargs["wait_for"]
            
            if kwargs.get('timeout'):
                payload["timeout"] = kwargs["timeout"]
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/scrape",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"API request failed with status {response.status_code}: {response.text}"
                }
            
            api_result = response.json()
            
            if not api_result.get('success', False):
                return {
                    'success': False,
                    'error': api_result.get('error', 'Unknown API error')
                }
            
            # Process API response
            data = api_result.get('data', {})
            
            return {
                'success': True,
                'content': data.get('markdown', ''),
                'html': data.get('html', ''),
                'links': data.get('links', []),
                'images': data.get('images', []),
                'metadata': {
                    'title': data.get('title', ''),
                    'description': data.get('description', ''),
                    'language': data.get('language', ''),
                    'sourceURL': data.get('sourceURL', url),
                    'statusCode': data.get('statusCode', 200)
                },
                'response_time': response.elapsed.total_seconds(),
                'content_size': len(response.content),
                'encoding': response.encoding or 'utf-8',
                'status_code': response.status_code
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Scraping error: {str(e)}"
            }
    
    def _format_scraping_results(self, scraping_result: Dict[str, Any], output_format: str) -> Dict[str, Any]:
        """Format scraping results based on requested format."""
        data = {}
        data_type = 'unknown'
        elements_count = 0
        
        try:
            if output_format == 'json':
                # Structure data as JSON
                data = {
                    'url': scraping_result['metadata']['sourceURL'],
                    'title': scraping_result['metadata']['title'],
                    'description': scraping_result['metadata']['description'],
                    'content': scraping_result['content'],
                    'links': scraping_result.get('links', []),
                    'images': scraping_result.get('images', []),
                    'metadata': scraping_result['metadata']
                }
                data_type = 'structured_json'
                elements_count = len(data.get('links', [])) + len(data.get('images', []))
                
            elif output_format == 'html':
                # Return HTML content
                data = scraping_result.get('html', scraping_result['content'])
                data_type = 'html_markup'
                elements_count = len(re.findall(r'<[^>]+>', str(data)))
                
            elif output_format == 'markdown':
                # Return markdown content
                data = scraping_result['content']
                data_type = 'markdown_text'
                elements_count = len(re.findall(r'(?:^|\n)#+\s', str(data)))  # Count headers
                
            else:  # text format
                # Clean text content
                content = scraping_result['content']
                # Remove markdown formatting for plain text
                content = re.sub(r'[#*_`]', '', content)
                content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # Convert links to text
                data = content.strip()
                data_type = 'plain_text'
                elements_count = len(data.split('\n')) if data else 0
            
            return {
                'data': data,
                'data_type': data_type,
                'elements_count': elements_count,
                'original_format': output_format
            }
            
        except Exception as e:
            return {
                'data': scraping_result.get('content', ''),
                'data_type': 'fallback_text',
                'elements_count': 0,
                'original_format': output_format,
                'format_error': str(e)
            }
    
    def _assess_content_quality(self, formatted_result: Dict[str, Any]) -> float:
        """Assess the quality of extracted content."""
        try:
            data = formatted_result.get('data', '')
            
            if not data:
                return 0.0
            
            # Quality factors
            factors = []
            
            # Content length factor
            content_length = len(str(data))
            if content_length > 1000:
                factors.append(1.0)
            elif content_length > 500:
                factors.append(0.8)
            elif content_length > 100:
                factors.append(0.6)
            else:
                factors.append(0.3)
            
            # Structure factor
            elements_count = formatted_result.get('elements_count', 0)
            if elements_count > 10:
                factors.append(1.0)
            elif elements_count > 5:
                factors.append(0.8)
            elif elements_count > 0:
                factors.append(0.6)
            else:
                factors.append(0.4)
            
            # Data type factor
            data_type = formatted_result.get('data_type', 'unknown')
            if data_type in ['structured_json', 'html_markup']:
                factors.append(1.0)
            elif data_type in ['markdown_text']:
                factors.append(0.8)
            else:
                factors.append(0.6)
            
            return sum(factors) / len(factors)
            
        except Exception:
            return 0.5  # Default quality score
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache successful scraping results."""
        if len(self.request_cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.request_cache))
            del self.request_cache[oldest_key]
        
        self.request_cache[cache_key] = result
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the task contains a valid URL to scrape",
                "Provide a valid Firecrawl API key",
                "Specify extraction type if needed (content, table, links, images, metadata)",
                "Check URL accessibility and format",
                "Examples: 'Scrape content from https://example.com', 'Extract tables from website.com'",
                f"Supported extraction types: {', '.join(self.extraction_types.keys())}",
                "Supported formats: text, html, markdown, json"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_extraction_types': list(self.extraction_types.keys()),
                'supported_operations': list(self.operation_types.keys()),
                'supported_formats': list(self.format_options.keys())
            }
        }