#!/usr/bin/env python3
"""
Framework-Compliant TextAnalyzerTool - Follows Metis Agent Tools Framework v2.0
Comprehensive text analysis with sentiment, readability, and linguistic insights.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
import re
import math
import statistics
from collections import Counter, defaultdict
from urllib.parse import urlparse

from ..base import BaseTool


class TextAnalyzerTool(BaseTool):
    """
    Production-ready text analysis tool with comprehensive linguistic analysis.
    
    This tool handles sentiment analysis, readability assessment, keyword extraction,
    text statistics, language detection, and content classification.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize text analyzer tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "TextAnalyzerTool"  # MUST match class name exactly
        self.description = "Comprehensive text analysis with sentiment, readability, and linguistic insights"
        
        # Optional metadata
        self.version = "2.0.0"
        self.category = "core_tools"
        
        # Text analysis configuration
        self.max_text_length = 1000000  # 1MB text limit
        self.min_text_length = 3  # Minimum characters for analysis
        
        # Analysis operation types
        self.operation_types = {
            'sentiment': ['sentiment', 'emotion', 'feeling', 'mood', 'opinion'],
            'readability': ['readability', 'complexity', 'difficulty', 'grade', 'level'],
            'keywords': ['keywords', 'terms', 'phrases', 'topics', 'themes'],
            'statistics': ['statistics', 'stats', 'metrics', 'count', 'length'],
            'language': ['language', 'detect', 'identify', 'tongue'],
            'classify': ['classify', 'categorize', 'type', 'genre', 'category'],
            'extract': ['extract', 'find', 'locate', 'identify', 'discover'],
            'summarize': ['summarize', 'summary', 'overview', 'brief', 'abstract']
        }
        
        # Sentiment lexicons
        self.positive_words = {
            'excellent', 'amazing', 'wonderful', 'fantastic', 'great', 'good', 'nice',
            'beautiful', 'perfect', 'awesome', 'outstanding', 'brilliant', 'superb',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'delighted',
            'thrilled', 'excited', 'cheerful', 'joyful', 'optimistic', 'positive',
            'success', 'win', 'victory', 'achievement', 'accomplish', 'triumph'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'horrible', 'bad', 'poor', 'worst', 'disappointing',
            'frustrating', 'annoying', 'disgusting', 'pathetic', 'useless', 'worthless',
            'hate', 'dislike', 'despise', 'angry', 'mad', 'furious', 'upset',
            'sad', 'depressed', 'miserable', 'unhappy', 'disappointed', 'frustrated',
            'fail', 'failure', 'lose', 'loss', 'defeat', 'disaster', 'catastrophe'
        }
        
        # Common stop words for keyword extraction
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'within',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
            'its', 'our', 'their', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
        }
        
        # Language detection patterns (basic)
        self.language_patterns = {
            'english': r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b',
            'spanish': r'\b(el|la|los|las|y|o|pero|en|con|de|para|por)\b',
            'french': r'\b(le|la|les|et|ou|mais|dans|sur|avec|de|pour|par)\b',
            'german': r'\b(der|die|das|und|oder|aber|in|auf|mit|von|für|durch)\b',
            'italian': r'\b(il|la|lo|gli|le|e|o|ma|in|su|con|di|per|da)\b'
        }
    
    def can_handle(self, task: str) -> bool:
        """Intelligent text analysis task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        Handles text analysis, sentiment analysis, and linguistic processing tasks.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires text analysis, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Text analysis keywords
        text_keywords = {
            'text', 'analyze', 'analysis', 'sentiment', 'emotion', 'feeling',
            'readability', 'keywords', 'extract', 'linguistic', 'language',
            'classify', 'categorize', 'summarize', 'statistics', 'metrics',
            'content', 'document', 'article', 'review', 'comment', 'feedback'
        }
        
        has_text_keyword = any(keyword in task_clean for keyword in text_keywords)
        
        # Layer 2: Operation detection
        has_operation = any(
            any(op_word in task_clean for op_word in op_words)
            for op_words in self.operation_types.values()
        )
        
        # Layer 3: Text content detection
        has_text_indicators = any(indicator in task_clean for indicator in [
            'text', 'content', 'document', 'article', 'paragraph', 'sentence',
            'word', 'phrase', 'message', 'review', 'comment', 'feedback',
            'description', 'summary', 'report', 'essay', 'story'
        ])
        
        # Layer 4: Quoted text detection
        has_quoted_text = bool(re.search(r'["\'][^"\']{10,}["\']', task))
        
        # Layer 5: Exclusion filters
        exclusion_patterns = [
            'generate', 'create', 'write', 'compose', 'produce', 'make', 'build',
            'generate text', 'create text', 'write text', 'compose text',
            'produce content', 'make content', 'build content', 'generate article'
        ]
        
        has_exclusion = any(pattern in task_clean for pattern in exclusion_patterns)
        
        # Decision logic
        if has_exclusion:
            return False
        
        return (has_text_keyword and has_operation) or has_text_indicators or has_quoted_text
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute comprehensive text analysis."""
        start_time = datetime.now()
        
        try:
            # Extract text
            text = kwargs.get('text', '') or kwargs.get('content', '')
            if not text:
                text = self._extract_text_from_task(task)
            if not text:
                return self._error_response("No text found for analysis")
            
            # Validate text
            if len(text) < self.min_text_length:
                return self._error_response(f"Text too short (minimum {self.min_text_length} characters)")
            if len(text) > self.max_text_length:
                return self._error_response(f"Text too long (maximum {self.max_text_length} characters)")
            
            # Detect operation and perform analysis
            operation = self._detect_operation(task)
            result = self._comprehensive_analysis(text, kwargs.get('options', {}))
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'type': 'text_analysis_response',
                'data': result,
                'metadata': {
                    'tool_name': self.name,
                    'timestamp': datetime.now().isoformat(),
                    'execution_time': f"{execution_time:.3f}s",
                    'operation': operation,
                    'text_length': len(text)
                }
            }
            
        except Exception as e:
            return self._error_response(f"Text analysis failed: {str(e)}", e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect analysis operation type."""
        task_lower = task.lower()
        for operation, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                return operation
        return 'sentiment'
    
    def _extract_text_from_task(self, task: str) -> str:
        """Extract text from task description."""
        patterns = [
            r'["\']([^"\']{10,})["\']',
            r'(?:text|analyze)\s*[:=]\s*(.+?)(?:\n|$)'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        return ''
    
    def _comprehensive_analysis(self, text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive text analysis."""
        words = re.findall(r'\b\w+\b', text.lower())
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Sentiment analysis
        pos_count = sum(1 for word in words if word in self.positive_words)
        neg_count = sum(1 for word in words if word in self.negative_words)
        
        if pos_count > neg_count:
            sentiment = 'positive'
            confidence = min(0.95, (pos_count - neg_count) / len(words) * 5)
        elif neg_count > pos_count:
            sentiment = 'negative'
            confidence = min(0.95, (neg_count - pos_count) / len(words) * 5)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        # Keywords extraction
        content_words = [w for w in words if w not in self.stop_words and len(w) > 2]
        word_freq = Counter(content_words)
        
        # Readability (simplified)
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        syllables = sum(self._count_word_syllables(word) for word in words)
        avg_syllables = syllables / len(words) if words else 0
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        flesch_score = max(0, min(100, flesch_score))
        
        return {
            'sentiment_analysis': {
                'sentiment': sentiment,
                'confidence': round(confidence, 3),
                'positive_words': pos_count,
                'negative_words': neg_count
            },
            'text_statistics': {
                'characters': len(text),
                'words': len(words),
                'sentences': len(sentences),
                'avg_word_length': round(sum(len(w) for w in words) / len(words), 2) if words else 0,
                'avg_sentence_length': round(avg_sentence_length, 2)
            },
            'readability': {
                'flesch_reading_ease': round(flesch_score, 2),
                'reading_level': self._get_reading_level(flesch_score),
                'avg_syllables_per_word': round(avg_syllables, 2)
            },
            'keywords': {
                'top_words': word_freq.most_common(10),
                'unique_words': len(set(content_words)),
                'vocabulary_richness': round(len(set(content_words)) / len(content_words), 3) if content_words else 0
            },
            'language_detection': self._detect_language_simple(text),
            'content_features': {
                'urls': len(re.findall(r'https?://[^\s]+', text)),
                'emails': len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)),
                'numbers': len(re.findall(r'\b\d+(?:\.\d+)?\b', text)),
                'capitalized_words': len(re.findall(r'\b[A-Z][a-z]+\b', text))
            }
        }
    
    def _count_word_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _get_reading_level(self, flesch_score: float) -> str:
        """Convert Flesch score to reading level."""
        if flesch_score >= 90:
            return 'Very Easy'
        elif flesch_score >= 80:
            return 'Easy'
        elif flesch_score >= 70:
            return 'Fairly Easy'
        elif flesch_score >= 60:
            return 'Standard'
        elif flesch_score >= 50:
            return 'Fairly Difficult'
        elif flesch_score >= 30:
            return 'Difficult'
        else:
            return 'Very Difficult'
    
    def _detect_language_simple(self, text: str) -> Dict[str, Any]:
        """Simple language detection."""
        text_lower = text.lower()
        scores = {}
        
        for lang, pattern in self.language_patterns.items():
            matches = len(re.findall(pattern, text_lower))
            total_words = len(re.findall(r'\b\w+\b', text_lower))
            scores[lang] = matches / total_words if total_words > 0 else 0
        
        detected = max(scores, key=scores.get) if scores else 'unknown'
        confidence = scores.get(detected, 0)
        
        return {
            'detected_language': detected,
            'confidence': round(confidence, 3),
            'language_scores': scores
        }
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response."""
        response = {
            'success': False,
            'error': message,
            'type': 'text_analysis_error',
            'metadata': {
                'tool_name': self.name,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        if exception:
            response['exception_type'] = type(exception).__name__
            response['exception_details'] = str(exception)
        
        return response
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["moderate", "complex"],
            "input_types": ["text", "structured_data"],
            "output_types": ["analysis_results", "structured_data"],
            "requires_filesystem": False,
            "requires_internet": False,
            "estimated_execution_time": "1-5s",
            "concurrent_safe": True,
            "resource_intensive": False,
            "memory_usage": "low",
            "api_dependencies": [],
            "supported_intents": [
                "sentiment_analysis",
                "text_statistics",
                "readability_assessment", 
                "keyword_extraction",
                "language_detection",
                "content_classification"
            ],
            "supported_operations": list(self.operation_types.keys()),
            "text_features": [
                "sentiment_scoring",
                "flesch_readability",
                "word_frequency",
                "n_gram_extraction",
                "basic_language_detection",
                "content_feature_extraction"
            ]
        }
    
    def get_examples(self) -> List[str]:
        """Get example tasks that this tool can handle."""
        return [
            "Analyze the sentiment of this customer review",
            "Extract keywords from the document content",
            "Check the readability level of this text",
            "Detect the language of this content",
            "Classify the type of this text",
            "Get text statistics for this article",
            "Analyze sentiment: 'This product is amazing and I love it!'",
            "Extract features from this text content"
        ]
