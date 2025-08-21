"""
Text Processing Tool - MCP-compliant text manipulation and analysis.

Provides comprehensive text processing capabilities including formatting,
analysis, transformation, and extraction operations.
"""

import re
import json
from typing import Any, Dict, List, Optional
import datetime
from collections import Counter
from ..base import BaseTool


class TextProcessingTool(BaseTool):
    """
    Tool for text processing, analysis, and transformation operations.
    
    This tool demonstrates MCP architecture:
    - Stateless operation
    - No LLM dependencies
    - Structured input/output
    - Comprehensive text operations
    """
    
    def __init__(self):
        """Initialize text processing tool."""
        self.name = "Text Processing"
        self.description = "Process, analyze, and transform text content"
        self.supported_operations = [
            "format", "analyze", "extract", "transform", "clean", 
            "count", "split", "join", "replace", "validate"
        ]
    
    def can_handle(self, task: str) -> bool:
        """Check if task is a text processing operation."""
        if not task or not task.strip():
            return False
        
        task_lower = task.lower().strip()
        
        # Text processing keywords
        text_operations = [
            "format", "clean", "analyze", "extract", "transform", "process",
            "count", "split", "join", "replace", "validate", "parse",
            "normalize", "capitalize", "lowercase", "uppercase", "trim"
        ]
        
        # Text-related keywords
        text_keywords = [
            "text", "string", "content", "paragraph", "sentence", "word",
            "character", "line", "email", "url", "phone", "number",
            "whitespace", "punctuation", "regex", "pattern"
        ]
        
        # Check for text operations
        if any(op in task_lower for op in text_operations):
            return True
        
        # Check for text keywords
        if any(keyword in task_lower for keyword in text_keywords):
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute text processing operation."""
        if not task or not task.strip():
            return self._format_error_response(
                "Task cannot be empty",
                "INVALID_INPUT",
                ["Provide a text processing request"]
            )
        
        try:
            task_lower = task.lower().strip()
            text_input = kwargs.get("text", "") or kwargs.get("content", "")
            
            # Determine operation type
            if any(word in task_lower for word in ["analyze", "analysis", "stats"]):
                return self._handle_analyze_operation(task, text_input, **kwargs)
            elif any(word in task_lower for word in ["extract", "find", "get"]):
                return self._handle_extract_operation(task, text_input, **kwargs)
            elif any(word in task_lower for word in ["format", "clean", "normalize"]):
                return self._handle_format_operation(task, text_input, **kwargs)
            elif any(word in task_lower for word in ["transform", "convert", "change"]):
                return self._handle_transform_operation(task, text_input, **kwargs)
            elif any(word in task_lower for word in ["count", "number"]):
                return self._handle_count_operation(task, text_input, **kwargs)
            elif any(word in task_lower for word in ["split", "divide"]):
                return self._handle_split_operation(task, text_input, **kwargs)
            elif any(word in task_lower for word in ["join", "combine", "merge"]):
                return self._handle_join_operation(task, text_input, **kwargs)
            elif any(word in task_lower for word in ["replace", "substitute"]):
                return self._handle_replace_operation(task, text_input, **kwargs)
            elif any(word in task_lower for word in ["validate", "check"]):
                return self._handle_validate_operation(task, text_input, **kwargs)
            else:
                return self._handle_generic_operation(task, text_input, **kwargs)
                
        except Exception as e:
            return self._format_error_response(
                f"Text processing failed: {str(e)}",
                "PROCESSING_ERROR",
                ["Check input text and operation parameters"]
            )
    
    def _handle_analyze_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text analysis operations."""
        if not text:
            return self._format_error_response(
                "No text provided for analysis",
                "MISSING_TEXT",
                ["Provide text parameter for analysis"]
            )
        
        # Basic text statistics
        lines = text.splitlines()
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Character analysis
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        
        # Word frequency
        word_freq = Counter(word.lower().strip('.,!?;:"()[]{}') for word in words if word.strip())
        most_common_words = word_freq.most_common(10)
        
        # Character frequency
        char_freq = Counter(char.lower() for char in text if char.isalpha())
        
        # Reading metrics (approximate)
        avg_words_per_sentence = len(words) / max(len(sentences) - 1, 1)  # -1 for empty split at end
        avg_chars_per_word = sum(len(word) for word in words) / max(len(words), 1)
        
        analysis_result = {
            "basic_stats": {
                "characters": char_count,
                "characters_no_spaces": char_count_no_spaces,
                "words": len(words),
                "sentences": len(sentences) - 1 if sentences and not sentences[-1].strip() else len(sentences),
                "lines": len(lines),
                "paragraphs": len(paragraphs)
            },
            "reading_metrics": {
                "avg_words_per_sentence": round(avg_words_per_sentence, 2),
                "avg_characters_per_word": round(avg_chars_per_word, 2),
                "estimated_reading_time_minutes": round(len(words) / 200, 2)  # 200 WPM average
            },
            "word_frequency": {
                "most_common": most_common_words,
                "unique_words": len(word_freq),
                "vocabulary_richness": round(len(word_freq) / max(len(words), 1), 3)
            },
            "character_frequency": dict(char_freq.most_common(10))
        }
        
        return self._format_success_response({
            "operation": "text_analysis",
            "analysis": analysis_result,
            "text_preview": text[:100] + "..." if len(text) > 100 else text
        })
    
    def _handle_extract_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text extraction operations."""
        if not text:
            return self._format_error_response(
                "No text provided for extraction",
                "MISSING_TEXT",
                ["Provide text parameter for extraction"]
            )
        
        task_lower = task.lower()
        extractions = {}
        
        # Email extraction
        if "email" in task_lower:
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            extractions["emails"] = list(set(emails))
        
        # URL extraction
        if "url" in task_lower or "link" in task_lower:
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            extractions["urls"] = list(set(urls))
        
        # Phone number extraction
        if "phone" in task_lower or "number" in task_lower:
            phones = re.findall(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
            extractions["phone_numbers"] = [''.join(phone) for phone in phones]
        
        # Date extraction
        if "date" in task_lower:
            dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', text)
            extractions["dates"] = list(set(dates))
        
        # Number extraction
        if "number" in task_lower and "phone" not in task_lower:
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
            extractions["numbers"] = [float(n) if '.' in n else int(n) for n in set(numbers)]
        
        # Custom pattern extraction
        pattern = kwargs.get("pattern")
        if pattern:
            try:
                custom_matches = re.findall(pattern, text)
                extractions["custom_pattern"] = custom_matches
            except re.error as e:
                return self._format_error_response(
                    f"Invalid regex pattern: {str(e)}",
                    "INVALID_PATTERN",
                    ["Check regex pattern syntax"]
                )
        
        # If no specific extraction requested, extract common patterns
        if not extractions:
            extractions = {
                "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
                "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text),
                "phone_numbers": [''.join(phone) for phone in re.findall(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)]
            }
        
        return self._format_success_response({
            "operation": "text_extraction",
            "extractions": extractions,
            "total_items": sum(len(v) if isinstance(v, list) else 1 for v in extractions.values())
        })
    
    def _handle_format_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text formatting operations."""
        if not text:
            return self._format_error_response(
                "No text provided for formatting",
                "MISSING_TEXT",
                ["Provide text parameter for formatting"]
            )
        
        task_lower = task.lower()
        formatted_text = text
        operations_applied = []
        
        # Clean whitespace
        if "clean" in task_lower or "normalize" in task_lower:
            formatted_text = re.sub(r'\s+', ' ', formatted_text.strip())
            operations_applied.append("whitespace_normalized")
        
        # Remove extra line breaks
        if "line" in task_lower and ("clean" in task_lower or "remove" in task_lower):
            formatted_text = re.sub(r'\n\s*\n', '\n\n', formatted_text)
            operations_applied.append("extra_linebreaks_removed")
        
        # Remove special characters
        if "special" in task_lower and "remove" in task_lower:
            formatted_text = re.sub(r'[^\w\s]', '', formatted_text)
            operations_applied.append("special_characters_removed")
        
        # Capitalize sentences
        if "capitalize" in task_lower and "sentence" in task_lower:
            sentences = re.split(r'([.!?]+)', formatted_text)
            for i in range(0, len(sentences), 2):
                if sentences[i].strip():
                    sentences[i] = sentences[i].strip().capitalize()
            formatted_text = ''.join(sentences)
            operations_applied.append("sentences_capitalized")
        
        # Title case
        if "title" in task_lower:
            formatted_text = formatted_text.title()
            operations_applied.append("title_case_applied")
        
        # Default formatting if no specific operation
        if not operations_applied:
            formatted_text = re.sub(r'\s+', ' ', formatted_text.strip())
            operations_applied.append("basic_formatting")
        
        return self._format_success_response({
            "operation": "text_formatting",
            "original_text": text[:100] + "..." if len(text) > 100 else text,
            "formatted_text": formatted_text,
            "operations_applied": operations_applied,
            "character_change": len(formatted_text) - len(text)
        })
    
    def _handle_transform_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text transformation operations."""
        if not text:
            return self._format_error_response(
                "No text provided for transformation",
                "MISSING_TEXT",
                ["Provide text parameter for transformation"]
            )
        
        task_lower = task.lower()
        transformed_text = text
        transformation = "none"
        
        if "uppercase" in task_lower or "upper" in task_lower:
            transformed_text = text.upper()
            transformation = "uppercase"
        elif "lowercase" in task_lower or "lower" in task_lower:
            transformed_text = text.lower()
            transformation = "lowercase"
        elif "reverse" in task_lower:
            transformed_text = text[::-1]
            transformation = "reverse"
        elif "rot13" in task_lower:
            transformed_text = text.encode('rot13')
            transformation = "rot13"
        elif "base64" in task_lower:
            import base64
            transformed_text = base64.b64encode(text.encode()).decode()
            transformation = "base64_encode"
        else:
            # Default to title case
            transformed_text = text.title()
            transformation = "title_case"
        
        return self._format_success_response({
            "operation": "text_transformation",
            "transformation": transformation,
            "original_text": text,
            "transformed_text": transformed_text
        })
    
    def _handle_count_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text counting operations."""
        if not text:
            return self._format_error_response(
                "No text provided for counting",
                "MISSING_TEXT",
                ["Provide text parameter for counting"]
            )
        
        task_lower = task.lower()
        counts = {}
        
        if "word" in task_lower:
            counts["words"] = len(text.split())
        if "character" in task_lower:
            counts["characters"] = len(text)
            counts["characters_no_spaces"] = len(text.replace(' ', ''))
        if "line" in task_lower:
            counts["lines"] = len(text.splitlines())
        if "sentence" in task_lower:
            sentences = re.split(r'[.!?]+', text)
            counts["sentences"] = len([s for s in sentences if s.strip()])
        if "paragraph" in task_lower:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            counts["paragraphs"] = len(paragraphs)
        
        # If no specific count requested, provide all counts
        if not counts:
            counts = {
                "characters": len(text),
                "characters_no_spaces": len(text.replace(' ', '')),
                "words": len(text.split()),
                "lines": len(text.splitlines()),
                "sentences": len([s for s in re.split(r'[.!?]+', text) if s.strip()]),
                "paragraphs": len([p.strip() for p in text.split('\n\n') if p.strip()])
            }
        
        return self._format_success_response({
            "operation": "text_counting",
            "counts": counts,
            "text_preview": text[:50] + "..." if len(text) > 50 else text
        })
    
    def _handle_split_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text splitting operations."""
        if not text:
            return self._format_error_response(
                "No text provided for splitting",
                "MISSING_TEXT",
                ["Provide text parameter for splitting"]
            )
        
        delimiter = kwargs.get("delimiter", kwargs.get("separator", " "))
        max_splits = kwargs.get("max_splits", -1)
        
        # Extract delimiter from task if not provided
        if delimiter == " ":
            if "line" in task.lower():
                delimiter = "\n"
            elif "comma" in task.lower():
                delimiter = ","
            elif "semicolon" in task.lower():
                delimiter = ";"
            elif "tab" in task.lower():
                delimiter = "\t"
        
        try:
            if max_splits == -1:
                parts = text.split(delimiter)
            else:
                parts = text.split(delimiter, max_splits)
            
            return self._format_success_response({
                "operation": "text_splitting",
                "delimiter": delimiter,
                "parts": parts,
                "part_count": len(parts),
                "max_splits": max_splits if max_splits != -1 else "unlimited"
            })
            
        except Exception as e:
            return self._format_error_response(
                f"Split operation failed: {str(e)}",
                "SPLIT_ERROR",
                ["Check delimiter parameter"]
            )
    
    def _handle_join_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text joining operations."""
        parts = kwargs.get("parts", [])
        separator = kwargs.get("separator", kwargs.get("delimiter", " "))
        
        if not parts:
            # Try to extract parts from text (assume it's a list-like format)
            if text.startswith('[') and text.endswith(']'):
                try:
                    parts = json.loads(text)
                except json.JSONDecodeError:
                    parts = text[1:-1].split(',')
                    parts = [part.strip().strip('"\'') for part in parts]
            else:
                parts = text.splitlines() if '\n' in text else text.split(',')
        
        if not parts:
            return self._format_error_response(
                "No parts provided for joining",
                "MISSING_PARTS",
                ["Provide parts parameter or list-formatted text"]
            )
        
        try:
            joined_text = separator.join(str(part).strip() for part in parts)
            
            return self._format_success_response({
                "operation": "text_joining",
                "separator": separator,
                "parts": parts,
                "part_count": len(parts),
                "joined_text": joined_text
            })
            
        except Exception as e:
            return self._format_error_response(
                f"Join operation failed: {str(e)}",
                "JOIN_ERROR",
                ["Check parts and separator parameters"]
            )
    
    def _handle_replace_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text replacement operations."""
        if not text:
            return self._format_error_response(
                "No text provided for replacement",
                "MISSING_TEXT",
                ["Provide text parameter for replacement"]
            )
        
        old_value = kwargs.get("old", kwargs.get("find", ""))
        new_value = kwargs.get("new", kwargs.get("replace", ""))
        case_sensitive = kwargs.get("case_sensitive", True)
        use_regex = kwargs.get("regex", False)
        
        if not old_value:
            return self._format_error_response(
                "No search value provided",
                "MISSING_SEARCH_VALUE",
                ["Provide 'old' or 'find' parameter"]
            )
        
        try:
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                replaced_text = re.sub(old_value, new_value, text, flags=flags)
                replacements = len(re.findall(old_value, text, flags=flags))
            else:
                if case_sensitive:
                    replaced_text = text.replace(old_value, new_value)
                    replacements = text.count(old_value)
                else:
                    # Case-insensitive replacement
                    pattern = re.escape(old_value)
                    replaced_text = re.sub(pattern, new_value, text, flags=re.IGNORECASE)
                    replacements = len(re.findall(pattern, text, flags=re.IGNORECASE))
            
            return self._format_success_response({
                "operation": "text_replacement",
                "old_value": old_value,
                "new_value": new_value,
                "replacements_made": replacements,
                "case_sensitive": case_sensitive,
                "regex_used": use_regex,
                "original_text": text,
                "replaced_text": replaced_text
            })
            
        except re.error as e:
            return self._format_error_response(
                f"Invalid regex pattern: {str(e)}",
                "INVALID_REGEX",
                ["Check regex pattern syntax"]
            )
        except Exception as e:
            return self._format_error_response(
                f"Replace operation failed: {str(e)}",
                "REPLACE_ERROR",
                ["Check replacement parameters"]
            )
    
    def _handle_validate_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text validation operations."""
        if not text:
            return self._format_error_response(
                "No text provided for validation",
                "MISSING_TEXT",
                ["Provide text parameter for validation"]
            )
        
        task_lower = task.lower()
        validations = {}
        
        # Email validation
        if "email" in task_lower:
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            validations["is_valid_email"] = bool(re.match(email_pattern, text.strip()))
        
        # URL validation
        if "url" in task_lower:
            url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
            validations["is_valid_url"] = bool(re.match(url_pattern, text.strip()))
        
        # Phone validation
        if "phone" in task_lower:
            phone_pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
            validations["is_valid_phone"] = bool(re.match(phone_pattern, text.strip()))
        
        # JSON validation
        if "json" in task_lower:
            try:
                json.loads(text)
                validations["is_valid_json"] = True
            except json.JSONDecodeError:
                validations["is_valid_json"] = False
        
        # Custom pattern validation
        pattern = kwargs.get("pattern")
        if pattern:
            try:
                validations["matches_pattern"] = bool(re.match(pattern, text))
            except re.error as e:
                return self._format_error_response(
                    f"Invalid validation pattern: {str(e)}",
                    "INVALID_PATTERN",
                    ["Check regex pattern syntax"]
                )
        
        # General text validations
        if not validations:
            validations = {
                "is_empty": len(text.strip()) == 0,
                "is_numeric": text.strip().replace('.', '').replace('-', '').isdigit(),
                "is_alphabetic": text.strip().replace(' ', '').isalpha(),
                "is_alphanumeric": text.strip().replace(' ', '').isalnum(),
                "contains_whitespace": ' ' in text or '\t' in text or '\n' in text,
                "is_uppercase": text.isupper(),
                "is_lowercase": text.islower(),
                "is_title_case": text.istitle()
            }
        
        return self._format_success_response({
            "operation": "text_validation",
            "text": text,
            "validations": validations
        })
    
    def _handle_generic_operation(self, task: str, text: str, **kwargs) -> Dict[str, Any]:
        """Handle generic text processing operations."""
        # Default to text analysis
        return self._handle_analyze_operation(task, text, **kwargs)
    
    def get_examples(self) -> List[str]:
        """Return example text processing operations."""
        return [
            "analyze text statistics",
            "extract emails from content",
            "format and clean whitespace",
            "transform text to uppercase",
            "count words in document",
            "split text by commas",
            "join list with semicolons",
            "replace old with new text",
            "validate email format"
        ]
    
    def _format_success_response(self, data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a successful response."""
        return {
            "success": True,
            "type": "text_processing_response",
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
