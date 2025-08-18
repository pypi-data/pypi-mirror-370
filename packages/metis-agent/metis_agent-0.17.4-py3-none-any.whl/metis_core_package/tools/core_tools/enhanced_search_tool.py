#!/usr/bin/env python3
"""
Enhanced Search Tool - Next-Generation File and Code Search
Provides semantic understanding, fuzzy matching, and intelligent search capabilities.
"""

from typing import Dict, Any, Optional, List, Tuple, Generator, Union
from datetime import datetime
import os
import re
import ast
import pathlib
import fnmatch
import threading
import time
import json
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..base import BaseTool

# Try to import optional dependencies for enhanced features
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from difflib import SequenceMatcher
    DIFFLIB_AVAILABLE = True
except ImportError:
    DIFFLIB_AVAILABLE = False


@dataclass
class SearchResult:
    """Structured search result with metadata"""
    file_path: str
    matches: List[Dict[str, Any]]
    relevance_score: float = 0.0
    context_type: str = "text"  # text, code, comment, docstring
    language: Optional[str] = None
    encoding: str = "utf-8"
    total_lines: int = 0
    error: Optional[str] = None


@dataclass
class SearchQuery:
    """Structured search query with analysis"""
    original_query: str
    processed_pattern: str
    intent: str  # literal, regex, semantic, fuzzy
    confidence: float
    suggested_corrections: List[str]
    context_hints: List[str]


class CodeAnalyzer:
    """Analyzes code structure for semantic search"""
    
    LANGUAGE_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.cs': 'csharp',
        '.html': 'html',
        '.css': 'css',
        '.sql': 'sql',
        '.sh': 'bash',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.md': 'markdown'
    }
    
    def __init__(self):
        self.ast_cache = {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze file structure and extract semantic information"""
        ext = pathlib.Path(file_path).suffix.lower()
        language = self.LANGUAGE_EXTENSIONS.get(ext, 'text')
        
        analysis = {
            'language': language,
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': [],
            'comments': [],
            'docstrings': [],
            'complexity': 'low'
        }
        
        try:
            if language == 'python':
                analysis.update(self._analyze_python_file(file_path))
            elif language in ['javascript', 'typescript']:
                analysis.update(self._analyze_js_file(file_path))
            # Add more language analyzers as needed
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze Python file using AST"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': [],
            'docstrings': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append({
                                'module': alias.name,
                                'alias': alias.asname,
                                'line': node.lineno
                            })
                    else:  # ImportFrom
                        for alias in node.names:
                            analysis['imports'].append({
                                'module': node.module,
                                'name': alias.name,
                                'alias': alias.asname,
                                'line': node.lineno
                            })
                
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            analysis['variables'].append({
                                'name': target.id,
                                'line': node.lineno
                            })
        
        except SyntaxError:
            # File has syntax errors, skip AST analysis
            pass
        except Exception:
            # Other errors, skip analysis
            pass
        
        return analysis
    
    def _analyze_js_file(self, file_path: str) -> Dict[str, Any]:
        """Basic JavaScript/TypeScript file analysis"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex patterns for JS/TS analysis
            function_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:\([^)]*\)\s*)?=>|(\w+)\s*:\s*(?:\([^)]*\)\s*)?=>)'
            class_pattern = r'class\s+(\w+)'
            import_pattern = r'import\s+(?:\{([^}]+)\}|\*\s+as\s+(\w+)|(\w+))\s+from\s+["\']([^"\']+)["\']'
            export_pattern = r'export\s+(?:default\s+)?(?:function\s+(\w+)|class\s+(\w+)|const\s+(\w+))'
            
            for match in re.finditer(function_pattern, content):
                func_name = match.group(1) or match.group(2) or match.group(3)
                if func_name:
                    line_num = content[:match.start()].count('\n') + 1
                    analysis['functions'].append({
                        'name': func_name,
                        'line': line_num
                    })
            
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                analysis['classes'].append({
                    'name': class_name,
                    'line': line_num
                })
            
            for match in re.finditer(import_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                analysis['imports'].append({
                    'imports': match.group(1) or match.group(2) or match.group(3),
                    'module': match.group(4),
                    'line': line_num
                })
            
        except Exception:
            pass
        
        return analysis


class FuzzyMatcher:
    """Fuzzy string matching with configurable similarity thresholds"""
    
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold
    
    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        if not DIFFLIB_AVAILABLE:
            # Fallback to simple character-based similarity
            return self._simple_similarity(a, b)
        
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _simple_similarity(self, a: str, b: str) -> float:
        """Simple character-based similarity calculation"""
        a, b = a.lower(), b.lower()
        if not a or not b:
            return 0.0
        
        # Count common characters
        common = sum(1 for char in set(a) if char in b)
        total = len(set(a) | set(b))
        
        return common / total if total > 0 else 0.0
    
    def find_matches(self, query: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """Find fuzzy matches in candidate list"""
        matches = []
        
        for candidate in candidates:
            score = self.similarity(query, candidate)
            if score >= self.threshold:
                matches.append((candidate, score))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def suggest_corrections(self, query: str, vocabulary: List[str]) -> List[str]:
        """Suggest corrections for potential typos"""
        matches = self.find_matches(query, vocabulary)
        return [match[0] for match in matches[:5]]  # Top 5 suggestions


class SemanticSearchEngine:
    """Core semantic search engine with code understanding"""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.fuzzy_matcher = FuzzyMatcher()
        self.pattern_cache = {}
        self.vocabulary_cache = {}
    
    def analyze_query(self, query: str, context: Dict[str, Any] = None) -> SearchQuery:
        """Analyze search query and determine intent"""
        original_query = query.strip()
        
        # Extract the actual search pattern from the query
        extracted_pattern = self._extract_search_pattern(original_query, context)
        if not extracted_pattern:
            extracted_pattern = original_query
        
        # Determine query intent
        intent, confidence = self._determine_intent(original_query)
        
        # Process pattern based on intent
        if intent == 'regex':
            processed_pattern = extracted_pattern
        elif intent == 'fuzzy':
            processed_pattern = self._prepare_fuzzy_pattern(extracted_pattern)
        elif intent == 'semantic':
            processed_pattern = self._prepare_semantic_pattern(extracted_pattern)
        else:  # literal
            processed_pattern = extracted_pattern  # Don't escape here, do it during search
        
        # Generate suggestions
        suggestions = self._generate_suggestions(original_query, context)
        context_hints = self._generate_context_hints(original_query, context)
        
        return SearchQuery(
            original_query=original_query,
            processed_pattern=processed_pattern,
            intent=intent,
            confidence=confidence,
            suggested_corrections=suggestions,
            context_hints=context_hints
        )
    
    def _determine_intent(self, query: str) -> Tuple[str, float]:
        """Determine the intent of the search query"""
        # Check for regex patterns
        regex_indicators = ['.*', '.+', '\\d', '\\w', '[', ']', '(', ')', '|', '^', '$']
        if any(indicator in query for indicator in regex_indicators):
            return 'regex', 0.9
        
        # Check for fuzzy search indicators
        if query.startswith('~') or 'similar to' in query.lower():
            return 'fuzzy', 0.8
        
        # Check for semantic search indicators
        semantic_indicators = ['function', 'class', 'method', 'variable', 'import', 'definition']
        if any(indicator in query.lower() for indicator in semantic_indicators):
            return 'semantic', 0.7
        
        # Default to literal search
        return 'literal', 0.6
    
    def _prepare_fuzzy_pattern(self, query: str) -> str:
        """Prepare pattern for fuzzy matching"""
        # Remove fuzzy indicators
        clean_query = query.lstrip('~').replace('similar to', '').strip()
        return clean_query
    
    def _prepare_semantic_pattern(self, query: str) -> str:
        """Prepare pattern for semantic search"""
        # Extract meaningful parts from semantic query
        query_lower = query.lower()
        
        # Handle "function named X" or "class X"
        if 'function' in query_lower and 'named' in query_lower:
            match = re.search(r'function.*named\s+(\w+)', query_lower)
            if match:
                return f"def {match.group(1)}"
        
        if 'class' in query_lower:
            match = re.search(r'class\s+(\w+)', query_lower)
            if match:
                return f"class {match.group(1)}"
        
        return query
    
    def _generate_suggestions(self, query: str, context: Dict[str, Any] = None) -> List[str]:
        """Generate spelling and pattern suggestions"""
        if not context:
            return []
        
        # Build vocabulary from context
        vocabulary = self._build_vocabulary(context)
        
        # Get fuzzy suggestions
        return self.fuzzy_matcher.suggest_corrections(query, vocabulary)
    
    def _generate_context_hints(self, query: str, context: Dict[str, Any] = None) -> List[str]:
        """Generate contextual hints for better searching"""
        hints = []
        
        if not context:
            return hints
        
        # Analyze query for potential improvements
        query_lower = query.lower()
        
        if 'function' in query_lower and context.get('language') == 'python':
            hints.append("Try 'def function_name' for Python function definitions")
        
        if 'class' in query_lower:
            hints.append("Use 'class ClassName' to find class definitions")
        
        if 'import' in query_lower:
            hints.append("Search 'import module_name' or 'from module import'")
        
        return hints
    
    def _build_vocabulary(self, context: Dict[str, Any]) -> List[str]:
        """Build search vocabulary from context"""
        vocabulary = []
        
        # Add common programming terms
        vocabulary.extend([
            'function', 'class', 'method', 'variable', 'import', 'export',
            'return', 'if', 'else', 'for', 'while', 'try', 'catch', 'throw'
        ])
        
        # Add language-specific terms
        if context.get('language') == 'python':
            vocabulary.extend([
                'def', 'class', 'import', 'from', 'as', 'with', 'lambda',
                'yield', 'async', 'await', 'except', 'finally'
            ])
        
        return vocabulary
    
    def _extract_search_pattern(self, query: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Extract the actual search pattern from natural language query or structured format"""
        query_clean = query.strip()
        
        # Check for structured format first: Search(pattern: "text", ...)
        structured_match = re.search(r'(?:search|find|grep)\s*\(([^)]+)\)', query_clean, re.IGNORECASE)
        if structured_match:
            args_str = structured_match.group(1)
            
            # Extract pattern parameter
            pattern_match = re.search(r'pattern\s*:\s*["\']([^"\']+)["\']', args_str, re.IGNORECASE)
            if pattern_match:
                return pattern_match.group(1)
        
        # Look for quoted patterns
        quoted_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'`([^`]+)`'
        ]
        
        for pattern in quoted_patterns:
            matches = re.findall(pattern, query)
            if matches:
                return matches[0]
        
        # Look for patterns after keywords
        pattern_keywords = [
            r'(?:search|find|grep|look)\s+(?:for\s+)?(.+?)(?:\s+in|\s+from|$)',
            r'pattern[:\s]+(.+?)(?:\s+in|\s+from|$)',
            r'text[:\s]+(.+?)(?:\s+in|\s+from|$)',
            r'(?:containing|with)\s+(.+?)(?:\s+in|\s+from|$)'
        ]
        
        for pattern in pattern_keywords:
            matches = re.findall(pattern, query_clean, re.IGNORECASE)
            if matches:
                extracted = matches[0].strip()
                # Remove common trailing words
                extracted = re.sub(r'\s+(?:in|from|under|within).*$', '', extracted)
                return extracted
        
        # If no specific pattern found, return the whole query
        return None


class ResultStreamer:
    """Streams search results in real-time"""
    
    def __init__(self, max_concurrent: int = 4):
        self.max_concurrent = max_concurrent
        self.is_cancelled = threading.Event()
        self.results_queue = []
        self.lock = threading.Lock()
    
    def search_stream(self, search_func, file_list: List[str]) -> Generator[SearchResult, None, None]:
        """Stream search results as they are found"""
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit all file search tasks
            future_to_file = {
                executor.submit(search_func, file_path): file_path
                for file_path in file_list
            }
            
            # Yield results as they complete
            for future in as_completed(future_to_file):
                if self.is_cancelled.is_set():
                    break
                
                try:
                    result = future.result()
                    if result and result.matches:
                        yield result
                except Exception as e:
                    # Handle individual file errors
                    file_path = future_to_file[future]
                    yield SearchResult(
                        file_path=file_path,
                        matches=[],
                        error=str(e)
                    )
    
    def cancel(self):
        """Cancel ongoing search operation"""
        self.is_cancelled.set()


class EnhancedSearchTool(BaseTool):
    """
    Enhanced search tool with semantic understanding and intelligent matching.
    
    Provides next-generation file and code search capabilities including:
    - Semantic code understanding
    - Fuzzy pattern matching
    - Real-time result streaming
    - Natural language query processing
    """
    
    def __init__(self):
        """Initialize enhanced search tool"""
        super().__init__()  # Initialize caching
        # Required attributes
        self.name = "EnhancedSearchTool"
        self.description = "Advanced file and code search with semantic understanding and fuzzy matching"
        
        # Configuration
        self.version = "1.0.0"
        self.category = "core_tools"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_results = 1000
        self.supported_encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
        
        # Initialize engines
        self.semantic_engine = SemanticSearchEngine()
        self.result_streamer = ResultStreamer()
        self.code_analyzer = CodeAnalyzer()
        
        # Caching
        self.analysis_cache = {}
        self.pattern_cache = {}
        
        # Binary file detection
        self.binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
            '.zip', '.tar', '.gz', '.rar', '.7z', '.pdf'
        }
    
    def can_handle(self, task: str) -> bool:
        """Enhanced task detection with semantic understanding"""
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Enhanced keyword detection
        search_keywords = {
            'search', 'find', 'grep', 'look', 'locate', 'match', 'pattern',
            'fuzzy', 'similar', 'semantic', 'code', 'function', 'class'
        }
        
        # Structured search patterns (Search(), Find(), etc.)
        structured_patterns = [
            r'search\s*\(',
            r'find\s*\(',
            r'grep\s*\(',
            r'pattern\s*:',
            r'glob\s*:',
            r'output_mode\s*:',
            r'path\s*:',
        ]
        
        # Natural language patterns
        search_patterns = [
            r'find.*(?:function|class|method|variable)',
            r'search.*(?:for|in|containing)',
            r'look.*(?:for|in|containing)',
            r'grep.*(?:for|in)',
            r'similar.*to',
            r'fuzzy.*match'
        ]
        
        # Check structured patterns first
        for pattern in structured_patterns:
            if re.search(pattern, task_clean):
                return True
        
        # Check keywords
        if any(keyword in task_clean for keyword in search_keywords):
            return True
        
        # Check patterns
        if any(re.search(pattern, task_clean) for pattern in search_patterns):
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute enhanced search with semantic understanding"""
        try:
            # Get current time for performance tracking
            start_time = time.time()
            
            # Analyze query
            query = self.semantic_engine.analyze_query(task, kwargs)
            
            # Extract parameters
            search_path = self._extract_search_path(task, kwargs)
            if not search_path:
                search_path = os.getcwd()
            
            # Validate search path
            search_path = self._validate_path(search_path)
            if not os.path.exists(search_path):
                return self._error_response(f"Search path does not exist: {search_path}")
            
            # Extract search options
            options = self._extract_options(kwargs, task)
            
            # Get files to search
            file_list = self._get_files_to_search(search_path, options)
            
            # Execute search based on query intent
            if options.get('stream', False):
                return self._execute_streaming_search(query, file_list, options)
            else:
                return self._execute_batch_search(query, file_list, options, start_time)
        
        except Exception as e:
            return self._error_response(f"Search failed: {str(e)}", e)
    
    def _execute_batch_search(self, query: SearchQuery, file_list: List[str], 
                            options: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Execute traditional batch search"""
        results = []
        
        # Create search function based on intent
        if query.intent == 'semantic':
            search_func = lambda path: self._semantic_search_file(path, query, options)
        elif query.intent == 'fuzzy':
            search_func = lambda path: self._fuzzy_search_file(path, query, options)
        else:
            search_func = lambda path: self._literal_search_file(path, query, options)
        
        # Search files
        for file_path in file_list[:options['max_files']]:
            result = search_func(file_path)
            if result and result.matches:
                results.append(result)
            
            if len(results) >= options['max_results']:
                break
        
        # Calculate performance metrics
        end_time = time.time()
        search_duration = end_time - start_time
        
        # Sort results by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return {
            "success": True,
            "type": "enhanced_search_response",
            "data": {
                "query": asdict(query),
                "results": [asdict(r) for r in results],
                "total_matches": sum(len(r.matches) for r in results),
                "total_files_searched": len(file_list),
                "files_with_matches": len(results),
                "search_options": options
            },
            "metadata": {
                "tool_name": self.name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "performance": {
                    "search_duration": search_duration,
                    "files_processed": len(file_list),
                    "avg_time_per_file": search_duration / len(file_list) if file_list else 0
                },
                "query_analysis": {
                    "intent": query.intent,
                    "confidence": query.confidence,
                    "suggestions": query.suggested_corrections
                }
            }
        }
    
    def _execute_streaming_search(self, query: SearchQuery, file_list: List[str], 
                                options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute streaming search (placeholder for streaming implementation)"""
        # For now, fall back to batch search
        # In a full implementation, this would yield results in real-time
        return self._execute_batch_search(query, file_list, options, time.time())
    
    def _semantic_search_file(self, file_path: str, query: SearchQuery, 
                            options: Dict[str, Any]) -> Optional[SearchResult]:
        """Search file using semantic understanding"""
        try:
            # Get or create file analysis
            if file_path not in self.analysis_cache:
                self.analysis_cache[file_path] = self.code_analyzer.analyze_file(file_path)
            
            analysis = self.analysis_cache[file_path]
            
            # Search in structured code elements
            matches = []
            
            # Search in functions
            for func in analysis.get('functions', []):
                if self._semantic_match(query.processed_pattern, func['name'], 'function'):
                    matches.append({
                        'line': func.get('line', 1),
                        'content': f"def {func['name']}",
                        'context_type': 'function',
                        'metadata': func
                    })
            
            # Search in classes
            for cls in analysis.get('classes', []):
                if self._semantic_match(query.processed_pattern, cls['name'], 'class'):
                    matches.append({
                        'line': cls.get('line', 1),
                        'content': f"class {cls['name']}",
                        'context_type': 'class',
                        'metadata': cls
                    })
            
            # Also perform text search as fallback
            text_result = self._literal_search_file(file_path, query, options)
            if text_result and text_result.matches:
                matches.extend(text_result.matches)
            
            if matches:
                relevance = self._calculate_semantic_relevance(matches, query)
                return SearchResult(
                    file_path=file_path,
                    matches=matches,
                    relevance_score=relevance,
                    context_type='semantic',
                    language=analysis.get('language'),
                    total_lines=sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
                )
        
        except Exception as e:
            return SearchResult(
                file_path=file_path,
                matches=[],
                error=str(e)
            )
        
        return None
    
    def _fuzzy_search_file(self, file_path: str, query: SearchQuery, 
                         options: Dict[str, Any]) -> Optional[SearchResult]:
        """Search file using fuzzy matching"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            matches = []
            pattern = query.processed_pattern.lower()
            
            for line_num, line in enumerate(lines, 1):
                line_clean = line.strip()
                if not line_clean:
                    continue
                
                # Calculate fuzzy similarity
                similarity = self.semantic_engine.fuzzy_matcher.similarity(pattern, line_clean.lower())
                
                if similarity >= options.get('fuzzy_threshold', 0.6):
                    matches.append({
                        'line': line_num,
                        'content': line_clean,
                        'similarity': similarity,
                        'context_type': 'fuzzy_match'
                    })
            
            if matches:
                # Sort by similarity
                matches.sort(key=lambda m: m['similarity'], reverse=True)
                
                # Calculate overall relevance
                relevance = sum(m['similarity'] for m in matches) / len(matches)
                
                return SearchResult(
                    file_path=file_path,
                    matches=matches,
                    relevance_score=relevance,
                    context_type='fuzzy',
                    total_lines=len(lines)
                )
        
        except Exception as e:
            return SearchResult(
                file_path=file_path,
                matches=[],
                error=str(e)
            )
        
        return None
    
    def _literal_search_file(self, file_path: str, query: SearchQuery, 
                           options: Dict[str, Any]) -> Optional[SearchResult]:
        """Search file using literal/regex matching"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.splitlines()
            matches = []
            
            # Compile pattern
            flags = 0 if options.get('case_sensitive', False) else re.IGNORECASE
            
            try:
                if query.intent == 'regex':
                    pattern = re.compile(query.processed_pattern, flags)
                else:
                    pattern = re.compile(re.escape(query.processed_pattern), flags)
            except re.error:
                # Invalid regex, fall back to literal search
                pattern = re.compile(re.escape(query.original_query), flags)
            
            # Search line by line
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    matches.append({
                        'line': line_num,
                        'content': line.strip(),
                        'context_type': 'text_match'
                    })
            
            if matches:
                return SearchResult(
                    file_path=file_path,
                    matches=matches,
                    relevance_score=1.0,  # Literal matches get full relevance
                    context_type='literal',
                    total_lines=len(lines)
                )
        
        except Exception as e:
            return SearchResult(
                file_path=file_path,
                matches=[],
                error=str(e)
            )
        
        return None
    
    def _semantic_match(self, pattern: str, target: str, context_type: str) -> bool:
        """Check if pattern semantically matches target"""
        pattern_lower = pattern.lower()
        target_lower = target.lower()
        
        # Direct match
        if pattern_lower in target_lower:
            return True
        
        # Context-aware matching
        if context_type == 'function':
            if pattern_lower.startswith('def '):
                return pattern_lower[4:] in target_lower
        elif context_type == 'class':
            if pattern_lower.startswith('class '):
                return pattern_lower[6:] in target_lower
        
        return False
    
    def _calculate_semantic_relevance(self, matches: List[Dict[str, Any]], 
                                   query: SearchQuery) -> float:
        """Calculate relevance score for semantic matches"""
        if not matches:
            return 0.0
        
        total_score = 0.0
        
        for match in matches:
            score = 1.0  # Base score
            
            # Boost score based on context type
            context_type = match.get('context_type', 'text')
            if context_type == 'function':
                score *= 1.2
            elif context_type == 'class':
                score *= 1.1
            
            # Boost score based on query confidence
            score *= query.confidence
            
            total_score += score
        
        return min(total_score / len(matches), 1.0)
    
    def _extract_search_path(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract search path from task, structured format, or kwargs"""
        # Check for structured format first
        structured_match = re.search(r'(?:search|find|grep)\s*\(([^)]+)\)', task, re.IGNORECASE)
        if structured_match:
            args_str = structured_match.group(1)
            
            # Extract path parameter
            path_match = re.search(r'path\s*:\s*["\']([^"\']+)["\']', args_str, re.IGNORECASE)
            if path_match:
                return path_match.group(1)
        
        # Check kwargs
        path_keys = ['path', 'directory', 'folder', 'file_path', 'search_path']
        for key in path_keys:
            if key in kwargs:
                return kwargs[key]
        
        # Extract from task using natural language patterns
        path_patterns = [
            r'in\s+(?:file\s+|directory\s+|folder\s+)?["\']?([^"\'\s]+)["\']?',
            r'from\s+(?:file\s+|directory\s+|folder\s+)?["\']?([^"\'\s]+)["\']?',
            r'under\s+(?:file\s+|directory\s+|folder\s+)?["\']?([^"\'\s]+)["\']?'
        ]
        
        for pattern in path_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_options(self, kwargs: Dict[str, Any], task: str = "") -> Dict[str, Any]:
        """Extract and validate search options from kwargs and structured format"""
        options = {
            'recursive': kwargs.get('recursive', True),
            'case_sensitive': kwargs.get('case_sensitive', False),
            'file_pattern': kwargs.get('file_pattern', '*'),
            'max_results': min(kwargs.get('max_results', 100), self.max_results),
            'max_files': kwargs.get('max_files', 1000),
            'fuzzy_threshold': max(0.0, min(1.0, kwargs.get('fuzzy_threshold', 0.6))),
            'stream': kwargs.get('stream', False),
            'include_binary': kwargs.get('include_binary', False),
            'output_mode': kwargs.get('output_mode', 'content')
        }
        
        # Parse structured format for additional options
        if task:
            structured_match = re.search(r'(?:search|find|grep)\s*\(([^)]+)\)', task, re.IGNORECASE)
            if structured_match:
                args_str = structured_match.group(1)
                
                # Extract glob parameter
                glob_match = re.search(r'glob\s*:\s*["\']([^"\']+)["\']', args_str, re.IGNORECASE)
                if glob_match:
                    options['file_pattern'] = glob_match.group(1)
                
                # Extract output_mode parameter
                mode_match = re.search(r'output_mode\s*:\s*["\']([^"\']+)["\']', args_str, re.IGNORECASE)
                if mode_match:
                    options['output_mode'] = mode_match.group(1)
                
                # Extract case sensitivity
                case_match = re.search(r'case_insensitive\s*:\s*(true|false)', args_str, re.IGNORECASE)
                if case_match:
                    options['case_sensitive'] = case_match.group(1).lower() != 'true'
                
                # Extract context lines
                context_match = re.search(r'context\s*:\s*(\d+)', args_str, re.IGNORECASE)
                if context_match:
                    options['context_lines'] = int(context_match.group(1))
        
        return options
    
    def _validate_path(self, path: str) -> str:
        """Validate and normalize path"""
        return str(pathlib.Path(path).resolve())
    
    def _get_files_to_search(self, search_path: str, options: Dict[str, Any]) -> List[str]:
        """Get list of files to search based on options"""
        files = []
        
        if os.path.isfile(search_path):
            return [search_path]
        
        file_pattern = options['file_pattern']
        recursive = options['recursive']
        include_binary = options['include_binary']
        
        if recursive:
            for root, dirs, filenames in os.walk(search_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if self._should_include_file(file_path, file_pattern, include_binary):
                        files.append(file_path)
        else:
            try:
                for item in os.listdir(search_path):
                    file_path = os.path.join(search_path, item)
                    if os.path.isfile(file_path) and self._should_include_file(file_path, file_pattern, include_binary):
                        files.append(file_path)
            except PermissionError:
                pass
        
        return files
    
    def _should_include_file(self, file_path: str, file_pattern: str, include_binary: bool) -> bool:
        """Check if file should be included in search"""
        # Check file pattern
        if file_pattern != '*' and not fnmatch.fnmatch(os.path.basename(file_path), file_pattern):
            return False
        
        # Check binary files
        if not include_binary and self._is_binary_file(file_path):
            return False
        
        # Check file size
        try:
            if os.path.getsize(file_path) > self.max_file_size:
                return False
        except OSError:
            return False
        
        return True
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Check if file is binary"""
        ext = pathlib.Path(file_path).suffix.lower()
        if ext in self.binary_extensions:
            return True
        
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except (OSError, PermissionError):
            return True
        
        return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return enhanced tool capabilities"""
        return {
            "complexity_levels": ["simple", "moderate", "complex", "advanced"],
            "input_types": ["text", "pattern", "regex", "fuzzy_query", "semantic_query"],
            "output_types": ["structured_results", "streamed_results", "semantic_analysis"],
            "search_modes": ["literal", "regex", "fuzzy", "semantic"],
            "estimated_execution_time": "<5s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": True,
            "resource_intensive": "moderate",
            "supported_intents": [
                "search", "find", "grep", "locate", "match", "fuzzy_search",
                "semantic_search", "code_analysis", "pattern_matching"
            ],
            "features": [
                "semantic_code_understanding",
                "fuzzy_pattern_matching", 
                "real_time_streaming",
                "natural_language_queries",
                "relevance_scoring",
                "multi_language_support"
            ]
        }
    
    def get_examples(self) -> List[str]:
        """Get example usage patterns"""
        return [
            "Search for 'TODO' in Python files",
            "Find function named 'calculate_total'",
            "Fuzzy search for 'calcualte' (with typo)",
            "Find class definitions containing 'User'",
            "Search for import statements in JavaScript files",
            "Find similar code to 'def process_data'",
            "Search for regex pattern '\\d{3}-\\d{3}-\\d{4}' in text files",
            "Find all functions with 'async' in Python code"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate enhanced error response"""
        return {
            "success": False,
            "error": message,
            "error_type": type(exception).__name__ if exception else "SearchError",
            "suggestions": [
                "Ensure search path exists and is readable",
                "Check pattern syntax for regex searches", 
                "Try fuzzy search with '~pattern' for typo tolerance",
                "Use semantic search for code structure queries",
                "Adjust fuzzy_threshold for better fuzzy matching",
                "Use file_pattern to limit search scope",
                f"Maximum file size: {self.max_file_size // (1024*1024)}MB"
            ],
            "metadata": {
                "tool_name": self.name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "capabilities": ["literal", "regex", "fuzzy", "semantic"],
                "supported_languages": list(CodeAnalyzer.LANGUAGE_EXTENSIONS.values())
            }
        }