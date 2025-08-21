#!/usr/bin/env python3
"""
Smart Pattern Recognition Engine
Provides intelligent pattern suggestions, auto-completion, and pattern learning.
"""

import re
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class PatternSuggestion:
    """Represents a pattern suggestion with metadata"""
    pattern: str
    description: str
    confidence: float
    usage_count: int = 0
    last_used: Optional[datetime] = None
    category: str = "general"
    examples: List[str] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []


class PatternLearner:
    """Learns patterns from user search history and usage"""
    
    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file or os.path.expanduser("~/.metis/search_patterns.json")
        self.pattern_usage = defaultdict(int)
        self.pattern_success = defaultdict(int)
        self.pattern_categories = defaultdict(str)
        self.recent_patterns = []
        self.load_history()
    
    def record_pattern_usage(self, pattern: str, category: str = "general", 
                           success: bool = True, results_count: int = 0):
        """Record pattern usage for learning"""
        self.pattern_usage[pattern] += 1
        self.pattern_categories[pattern] = category
        
        if success and results_count > 0:
            self.pattern_success[pattern] += 1
        
        # Update recent patterns
        self.recent_patterns.insert(0, {
            'pattern': pattern,
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'success': success,
            'results_count': results_count
        })
        
        # Keep only recent 100 patterns
        self.recent_patterns = self.recent_patterns[:100]
        
        self.save_history()
    
    def get_popular_patterns(self, limit: int = 10, category: str = None) -> List[PatternSuggestion]:
        """Get most popular patterns"""
        patterns = []
        
        for pattern, usage_count in Counter(self.pattern_usage).most_common():
            if category and self.pattern_categories[pattern] != category:
                continue
            
            success_rate = self.pattern_success[pattern] / max(usage_count, 1)
            confidence = min(success_rate * (usage_count / 10), 1.0)
            
            patterns.append(PatternSuggestion(
                pattern=pattern,
                description=f"Used {usage_count} times",
                confidence=confidence,
                usage_count=usage_count,
                category=self.pattern_categories[pattern]
            ))
            
            if len(patterns) >= limit:
                break
        
        return patterns
    
    def get_recent_patterns(self, limit: int = 5) -> List[PatternSuggestion]:
        """Get recently used patterns"""
        patterns = []
        
        for recent in self.recent_patterns[:limit]:
            patterns.append(PatternSuggestion(
                pattern=recent['pattern'],
                description=f"Recently used ({recent.get('results_count', 0)} results)",
                confidence=0.8 if recent.get('success', False) else 0.3,
                category=recent.get('category', 'general'),
                last_used=datetime.fromisoformat(recent['timestamp'])
            ))
        
        return patterns
    
    def suggest_similar_patterns(self, query: str, limit: int = 5) -> List[PatternSuggestion]:
        """Suggest patterns similar to the query"""
        suggestions = []
        query_lower = query.lower()
        
        for pattern in self.pattern_usage.keys():
            pattern_lower = pattern.lower()
            
            # Calculate similarity
            similarity = self._calculate_similarity(query_lower, pattern_lower)
            
            if similarity > 0.6:  # Threshold for similarity
                usage_count = self.pattern_usage[pattern]
                confidence = similarity * min(usage_count / 5, 1.0)
                
                suggestions.append(PatternSuggestion(
                    pattern=pattern,
                    description=f"Similar pattern (used {usage_count} times)",
                    confidence=confidence,
                    usage_count=usage_count,
                    category=self.pattern_categories[pattern]
                ))
        
        return sorted(suggestions, key=lambda x: x.confidence, reverse=True)[:limit]
    
    def _calculate_similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        if not a or not b:
            return 0.0
        
        # Simple character-based similarity
        common_chars = set(a) & set(b)
        total_chars = set(a) | set(b)
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)
    
    def load_history(self):
        """Load pattern history from file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    
                    self.pattern_usage.update(data.get('usage', {}))
                    self.pattern_success.update(data.get('success', {}))
                    self.pattern_categories.update(data.get('categories', {}))
                    self.recent_patterns = data.get('recent', [])
        except Exception:
            # Ignore errors loading history
            pass
    
    def save_history(self):
        """Save pattern history to file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            data = {
                'usage': dict(self.pattern_usage),
                'success': dict(self.pattern_success),
                'categories': dict(self.pattern_categories),
                'recent': self.recent_patterns
            }
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Ignore errors saving history
            pass


class PatternTemplateManager:
    """Manages predefined pattern templates for common search tasks"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined pattern templates"""
        templates = {
            # Python patterns
            "python_function": {
                "pattern": r"def\s+{name}\s*\(",
                "description": "Find Python function definition",
                "category": "python",
                "examples": ["def calculate(", "def process_data("],
                "variables": ["name"]
            },
            "python_class": {
                "pattern": r"class\s+{name}\s*[\(:]",
                "description": "Find Python class definition", 
                "category": "python",
                "examples": ["class User(", "class DataProcessor:"],
                "variables": ["name"]
            },
            "python_import": {
                "pattern": r"(?:from\s+{module}\s+)?import\s+{name}",
                "description": "Find Python import statement",
                "category": "python",
                "examples": ["import os", "from datetime import datetime"],
                "variables": ["module", "name"]
            },
            "python_decorator": {
                "pattern": r"@{name}",
                "description": "Find Python decorator usage",
                "category": "python", 
                "examples": ["@property", "@staticmethod"],
                "variables": ["name"]
            },
            
            # JavaScript patterns
            "js_function": {
                "pattern": r"(?:function\s+{name}|const\s+{name}\s*=|\s+{name}\s*[:=]\s*(?:function|\([^)]*\)\s*=>))",
                "description": "Find JavaScript function definition",
                "category": "javascript",
                "examples": ["function calculate(", "const process = ("],
                "variables": ["name"]
            },
            "js_class": {
                "pattern": r"class\s+{name}\s*\{",
                "description": "Find JavaScript class definition",
                "category": "javascript",
                "examples": ["class User {", "class Component {"],
                "variables": ["name"]
            },
            "js_import": {
                "pattern": r"import\s+(?:\{[^}]*{name}[^}]*\}|{name})\s+from",
                "description": "Find JavaScript import statement",
                "category": "javascript",
                "examples": ["import { useState }", "import React from"],
                "variables": ["name"]
            },
            
            # Generic patterns
            "todo_comment": {
                "pattern": r"(?://|#|\*)\s*TODO:?\s*{text}?",
                "description": "Find TODO comments",
                "category": "general",
                "examples": ["// TODO: fix bug", "# TODO implement"],
                "variables": ["text"]
            },
            "fixme_comment": {
                "pattern": r"(?://|#|\*)\s*FIXME:?\s*{text}?",
                "description": "Find FIXME comments", 
                "category": "general",
                "examples": ["// FIXME: memory leak", "# FIXME optimize"],
                "variables": ["text"]
            },
            "email_pattern": {
                "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "description": "Find email addresses",
                "category": "data",
                "examples": ["user@example.com", "admin@company.org"],
                "variables": []
            },
            "url_pattern": {
                "pattern": r"https?://[^\s<>\"']+",
                "description": "Find URLs",
                "category": "data", 
                "examples": ["https://example.com", "http://localhost:3000"],
                "variables": []
            },
            "ip_address": {
                "pattern": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
                "description": "Find IP addresses",
                "category": "data",
                "examples": ["192.168.1.1", "10.0.0.1"],
                "variables": []
            },
            
            # File patterns
            "file_extension": {
                "pattern": r"\.{ext}$",
                "description": "Find files with specific extension",
                "category": "files",
                "examples": [".py$", ".js$", ".txt$"],
                "variables": ["ext"]
            },
            "config_files": {
                "pattern": r"(?:config|settings|\.env|\.ini|\.conf|\.cfg)$",
                "description": "Find configuration files",
                "category": "files", 
                "examples": ["config.json", ".env", "settings.ini"],
                "variables": []
            },
            
            # Error patterns
            "error_log": {
                "pattern": r"(?:ERROR|FATAL|CRITICAL)[:\s]+{message}?",
                "description": "Find error log entries",
                "category": "logs",
                "examples": ["ERROR: Connection failed", "FATAL: Out of memory"],
                "variables": ["message"]
            },
            "exception": {
                "pattern": r"(?:Exception|Error)[:\s]+{message}?",
                "description": "Find exception messages",
                "category": "logs",
                "examples": ["ValueError: invalid literal", "TypeError: unsupported"],
                "variables": ["message"]
            }
        }
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get specific pattern template"""
        return self.templates.get(template_name)
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get templates by category"""
        return [
            {**template, 'name': name}
            for name, template in self.templates.items()
            if template.get('category') == category
        ]
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Search templates by name or description"""
        query_lower = query.lower()
        results = []
        
        for name, template in self.templates.items():
            if (query_lower in name.lower() or 
                query_lower in template.get('description', '').lower()):
                results.append({**template, 'name': name})
        
        return results
    
    def generate_pattern(self, template_name: str, variables: Dict[str, str] = None) -> Optional[str]:
        """Generate pattern from template with variables"""
        template = self.get_template(template_name)
        if not template:
            return None
        
        pattern = template['pattern']
        variables = variables or {}
        
        # Replace variables in pattern
        for var_name in template.get('variables', []):
            placeholder = f"{{{var_name}}}"
            if placeholder in pattern:
                if var_name in variables:
                    pattern = pattern.replace(placeholder, variables[var_name])
                else:
                    # Make variable optional
                    pattern = pattern.replace(placeholder, f"({var_name})?")
        
        return pattern
    
    def get_all_categories(self) -> List[str]:
        """Get all available template categories"""
        categories = set()
        for template in self.templates.values():
            categories.add(template.get('category', 'general'))
        return sorted(categories)


class AutoCompleter:
    """Provides real-time pattern auto-completion"""
    
    def __init__(self, pattern_learner: PatternLearner, template_manager: PatternTemplateManager):
        self.pattern_learner = pattern_learner
        self.template_manager = template_manager
        self.completion_cache = {}
    
    def get_completions(self, partial_query: str, context: Dict[str, Any] = None) -> List[PatternSuggestion]:
        """Get auto-completion suggestions for partial query"""
        if not partial_query or len(partial_query) < 2:
            return []
        
        completions = []
        context = context or {}
        
        # Get completions from different sources
        completions.extend(self._get_history_completions(partial_query))
        completions.extend(self._get_template_completions(partial_query, context))
        completions.extend(self._get_smart_completions(partial_query, context))
        
        # Remove duplicates and sort by confidence
        seen_patterns = set()
        unique_completions = []
        
        for completion in sorted(completions, key=lambda x: x.confidence, reverse=True):
            if completion.pattern not in seen_patterns:
                seen_patterns.add(completion.pattern)
                unique_completions.append(completion)
        
        return unique_completions[:10]  # Top 10 suggestions
    
    def _get_history_completions(self, partial_query: str) -> List[PatternSuggestion]:
        """Get completions from search history"""
        completions = []
        partial_lower = partial_query.lower()
        
        # Get patterns that start with the partial query
        for pattern in self.pattern_learner.pattern_usage.keys():
            if pattern.lower().startswith(partial_lower):
                usage_count = self.pattern_learner.pattern_usage[pattern]
                confidence = min(usage_count / 10, 0.9)
                
                completions.append(PatternSuggestion(
                    pattern=pattern,
                    description=f"From history (used {usage_count} times)",
                    confidence=confidence,
                    usage_count=usage_count,
                    category="history"
                ))
        
        return completions
    
    def _get_template_completions(self, partial_query: str, context: Dict[str, Any]) -> List[PatternSuggestion]:
        """Get completions from pattern templates"""
        completions = []
        language = context.get('language', 'general')
        
        # Search templates
        matching_templates = self.template_manager.search_templates(partial_query)
        
        for template in matching_templates:
            # Generate pattern with context
            pattern = self.template_manager.generate_pattern(
                template['name'], 
                self._extract_variables_from_query(partial_query, template)
            )
            
            if pattern:
                confidence = 0.8 if template.get('category') == language else 0.6
                
                completions.append(PatternSuggestion(
                    pattern=pattern,
                    description=template['description'],
                    confidence=confidence,
                    category=template.get('category', 'general'),
                    examples=template.get('examples', [])
                ))
        
        return completions
    
    def _get_smart_completions(self, partial_query: str, context: Dict[str, Any]) -> List[PatternSuggestion]:
        """Get smart completions based on context and common patterns"""
        completions = []
        partial_lower = partial_query.lower()
        
        # Language-specific smart completions
        language = context.get('language', 'general')
        
        if language == 'python':
            if 'def' in partial_lower:
                completions.append(PatternSuggestion(
                    pattern=f"def {partial_query.split()[-1] if ' ' in partial_query else '.*'}\\(",
                    description="Python function definition",
                    confidence=0.7,
                    category="python"
                ))
            
            if 'class' in partial_lower:
                completions.append(PatternSuggestion(
                    pattern=f"class {partial_query.split()[-1] if ' ' in partial_query else '.*'}[:(]",
                    description="Python class definition", 
                    confidence=0.7,
                    category="python"
                ))
        
        elif language in ['javascript', 'typescript']:
            if 'function' in partial_lower:
                completions.append(PatternSuggestion(
                    pattern=f"function {partial_query.split()[-1] if ' ' in partial_query else '.*'}\\(",
                    description="JavaScript function definition",
                    confidence=0.7,
                    category="javascript"
                ))
        
        # Common search patterns
        if 'todo' in partial_lower:
            completions.append(PatternSuggestion(
                pattern="(?://|#).*TODO.*",
                description="TODO comments",
                confidence=0.6,
                category="general"
            ))
        
        if 'error' in partial_lower:
            completions.append(PatternSuggestion(
                pattern="(?:ERROR|Error).*",
                description="Error messages",
                confidence=0.6,
                category="logs"
            ))
        
        return completions
    
    def _extract_variables_from_query(self, query: str, template: Dict[str, Any]) -> Dict[str, str]:
        """Extract variable values from query for template"""
        variables = {}
        
        # Simple extraction based on query words
        words = query.split()
        template_vars = template.get('variables', [])
        
        if len(words) >= 2 and len(template_vars) >= 1:
            # Use last word as the main variable
            main_var = template_vars[0]
            variables[main_var] = words[-1]
        
        return variables


class PatternValidator:
    """Validates pattern syntax and provides correction suggestions"""
    
    def __init__(self):
        self.common_mistakes = {
            r'\(': '(',  # Unescaped parentheses
            r'\)': ')',
            r'\[': '[',
            r'\]': ']',
            r'\{': '{',
            r'\}': '}',
            r'\.': '.',
            r'\*': '*',
            r'\+': '+',
            r'\?': '?'
        }
    
    def validate_pattern(self, pattern: str, pattern_type: str = "regex") -> Dict[str, Any]:
        """Validate pattern syntax and suggest corrections"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        if pattern_type == "regex":
            try:
                re.compile(pattern)
            except re.error as e:
                result['valid'] = False
                result['errors'].append(f"Invalid regex: {str(e)}")
                result['suggestions'].extend(self._suggest_regex_corrections(pattern, e))
        
        # Check for common mistakes
        warnings = self._check_common_mistakes(pattern)
        result['warnings'].extend(warnings)
        
        return result
    
    def _suggest_regex_corrections(self, pattern: str, error: re.error) -> List[str]:
        """Suggest corrections for regex errors"""
        suggestions = []
        
        # Common regex error corrections
        if "nothing to repeat" in str(error):
            suggestions.append("Escape special characters with backslash (e.g., \\* instead of *)")
            suggestions.append("Use .* for any characters, .+ for one or more characters")
        
        if "unbalanced parenthesis" in str(error):
            suggestions.append("Check that all parentheses are properly closed")
            suggestions.append("Escape literal parentheses with \\( and \\)")
        
        if "bad character range" in str(error):
            suggestions.append("Check character class ranges (e.g., [a-z] not [z-a])")
        
        # Generic suggestions
        suggestions.append("Try using literal search instead of regex")
        suggestions.append("Escape special characters: . * + ? ^ $ | \\ ( ) [ ] { }")
        
        return suggestions
    
    def _check_common_mistakes(self, pattern: str) -> List[str]:
        """Check for common pattern mistakes"""
        warnings = []
        
        # Check for potentially unescaped special characters
        special_chars = ['.', '*', '+', '?', '^', '$', '|', '(', ')', '[', ']', '{', '}']
        for char in special_chars:
            if char in pattern and f"\\{char}" not in pattern:
                if char in ['.', '*', '+', '?']:
                    warnings.append(f"'{char}' has special meaning in regex. Use '\\{char}' for literal match")
        
        # Check for very broad patterns
        if pattern in ['.*', '.+', '.*.*']:
            warnings.append("Pattern may match too broadly and return many results")
        
        # Check for empty character classes
        if '[]' in pattern:
            warnings.append("Empty character class [] will never match")
        
        return warnings


class SmartPatternEngine:
    """Main engine that orchestrates all pattern recognition components"""
    
    def __init__(self, history_file: Optional[str] = None):
        self.pattern_learner = PatternLearner(history_file)
        self.template_manager = PatternTemplateManager()
        self.auto_completer = AutoCompleter(self.pattern_learner, self.template_manager)
        self.pattern_validator = PatternValidator()
    
    def analyze_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze query and provide comprehensive pattern analysis"""
        context = context or {}
        
        analysis = {
            'original_query': query,
            'validation': self.pattern_validator.validate_pattern(query),
            'completions': self.auto_completer.get_completions(query, context),
            'popular_patterns': self.pattern_learner.get_popular_patterns(limit=5),
            'recent_patterns': self.pattern_learner.get_recent_patterns(limit=3),
            'similar_patterns': self.pattern_learner.suggest_similar_patterns(query, limit=3),
            'template_suggestions': self.template_manager.search_templates(query)
        }
        
        return analysis
    
    def record_search_result(self, pattern: str, category: str = "general", 
                           success: bool = True, results_count: int = 0):
        """Record search result for learning"""
        self.pattern_learner.record_pattern_usage(pattern, category, success, results_count)
    
    def get_pattern_suggestions(self, query: str, context: Dict[str, Any] = None) -> List[PatternSuggestion]:
        """Get pattern suggestions for a query"""
        return self.auto_completer.get_completions(query, context)
    
    def get_template_categories(self) -> List[str]:
        """Get all available template categories"""
        return self.template_manager.get_all_categories()
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get templates for a specific category"""
        return self.template_manager.get_templates_by_category(category)