"""
Language and file type detection for streaming interface.

Handles detection of programming languages and generation of appropriate filenames.
"""
import re
from typing import Tuple, Dict, List, Optional


class LanguageDetector:
    """Detects programming languages and generates filenames."""
    
    def __init__(self):
        """Initialize language detection patterns and mappings."""
        self.language_patterns = self._initialize_language_patterns()
        self.extension_mappings = self._initialize_extension_mappings()
        self.filename_generators = self._initialize_filename_generators()
    
    def _initialize_language_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for language detection."""
        return {
            'python': [
                r'def\s+\w+\s*\([^)]*\)\s*:',
                r'import\s+\w+',
                r'from\s+\w+\s+import',
                r'class\s+\w+\s*(?:\([^)]*\))?\s*:',
                r'if\s+__name__\s*==\s*["\']__main__["\']',
                r'print\s*\(',
                r'#\s*.*python',
                r'#!/usr/bin/env python',
            ],
            'javascript': [
                r'function\s+\w+\s*\([^)]*\)\s*\{',
                r'const\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'=>\s*\{',
                r'console\.log\(',
                r'require\s*\(',
                r'import\s+.*\s+from',
                r'export\s+(default\s+)?',
            ],
            'java': [
                r'public\s+class\s+\w+',
                r'private\s+\w+\s+\w+',
                r'public\s+static\s+void\s+main',
                r'import\s+java\.',
                r'System\.out\.println',
                r'@Override',
                r'package\s+[\w.]+;',
            ],
            'cpp': [
                r'#include\s*<[^>]+>',
                r'int\s+main\s*\(',
                r'std::\w+',
                r'using\s+namespace\s+std;',
                r'cout\s*<<',
                r'cin\s*>>',
                r'class\s+\w+\s*\{',
            ],
            'c': [
                r'#include\s*<[^>]+\.h>',
                r'int\s+main\s*\(',
                r'printf\s*\(',
                r'scanf\s*\(',
                r'struct\s+\w+\s*\{',
                r'typedef\s+\w+',
            ],
            'go': [
                r'package\s+\w+',
                r'import\s*\(',
                r'func\s+\w+\s*\([^)]*\)',
                r'fmt\.Print',
                r'go\s+\w+\(',
                r'type\s+\w+\s+struct\s*\{',
            ],
            'rust': [
                r'fn\s+\w+\s*\([^)]*\)',
                r'let\s+mut\s+\w+',
                r'use\s+\w+::',
                r'struct\s+\w+\s*\{',
                r'impl\s+\w+\s*\{',
                r'println!\s*\(',
                r'#\[derive\(',
            ],
            'ruby': [
                r'def\s+\w+',
                r'class\s+\w+',
                r'module\s+\w+',
                r'require\s+["\']',
                r'puts\s+',
                r'@\w+\s*=',
                r'end\s*$',
            ],
            'php': [
                r'<\?php',
                r'\$\w+\s*=',
                r'function\s+\w+\s*\(',
                r'class\s+\w+\s*\{',
                r'echo\s+',
                r'require_once\s+',
                r'->\w+',
            ],
            'html': [
                r'<!DOCTYPE\s+html>',
                r'<html\b',
                r'<head\b',
                r'<body\b',
                r'<div\b',
                r'<p\b',
                r'<script\b',
                r'<style\b',
            ],
            'css': [
                r'\w+\s*\{[^}]*\}',
                r'@media\s+',
                r'@import\s+',
                r'color\s*:\s*',
                r'font-size\s*:\s*',
                r'margin\s*:\s*',
                r'padding\s*:\s*',
            ],
            'sql': [
                r'SELECT\s+.*\s+FROM',
                r'INSERT\s+INTO',
                r'UPDATE\s+.*\s+SET',
                r'DELETE\s+FROM',
                r'CREATE\s+TABLE',
                r'ALTER\s+TABLE',
                r'DROP\s+TABLE',
            ],
            'shell': [
                r'#!/bin/bash',
                r'#!/bin/sh',
                r'echo\s+',
                r'\$\{?\w+\}?',
                r'if\s+\[.*\];\s*then',
                r'for\s+\w+\s+in',
                r'while\s+\[.*\]',
            ],
            'yaml': [
                r'^\s*\w+\s*:\s*\w+',
                r'^\s*-\s+\w+',
                r'version\s*:\s*',
                r'apiVersion\s*:\s*',
                r'metadata\s*:\s*',
            ],
            'json': [
                r'^\s*\{',
                r'"\w+"\s*:\s*',
                r'^\s*\[',
                r'}\s*,?\s*$',
                r']\s*,?\s*$',
            ],
            'markdown': [
                r'^#\s+',
                r'^\s*[-*+]\s+',
                r'^\s*\d+\.\s+',
                r'\[.*\]\(.*\)',
                r'```\w*',
                r'^\s*>',
            ]
        }
    
    def _initialize_extension_mappings(self) -> Dict[str, str]:
        """Initialize language to file extension mappings."""
        return {
            'python': '.py',
            'javascript': '.js',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'go': '.go',
            'rust': '.rs',
            'ruby': '.rb',
            'php': '.php',
            'html': '.html',
            'css': '.css',
            'sql': '.sql',
            'shell': '.sh',
            'bash': '.sh',
            'yaml': '.yaml',
            'json': '.json',
            'markdown': '.md',
            'text': '.txt',
            'xml': '.xml',
        }
    
    def _initialize_filename_generators(self) -> Dict[str, callable]:
        """Initialize filename generators for different languages."""
        return {
            'python': self._generate_python_filename,
            'javascript': self._generate_javascript_filename,
            'java': self._generate_java_filename,
            'cpp': self._generate_cpp_filename,
            'c': self._generate_c_filename,
            'go': self._generate_go_filename,
            'rust': self._generate_rust_filename,
            'ruby': self._generate_ruby_filename,
            'php': self._generate_php_filename,
            'html': self._generate_html_filename,
            'css': self._generate_css_filename,
            'sql': self._generate_sql_filename,
            'shell': self._generate_shell_filename,
            'yaml': self._generate_yaml_filename,
            'json': self._generate_json_filename,
            'markdown': self._generate_markdown_filename,
        }
    
    def detect_language(self, content: str, filename_hint: str = "") -> str:
        """
        Detect programming language from content.
        
        Args:
            content: Code content to analyze
            filename_hint: Optional filename hint
            
        Returns:
            Detected language name
        """
        # First try filename-based detection
        if filename_hint:
            lang_from_filename = self._detect_language_from_filename(filename_hint)
            if lang_from_filename != 'text':
                return lang_from_filename
        
        # Content-based detection
        content_lower = content.lower()
        language_scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))
                score += matches
            
            if score > 0:
                language_scores[language] = score
        
        if language_scores:
            # Return language with highest score
            return max(language_scores.items(), key=lambda x: x[1])[0]
        
        return 'text'
    
    def _detect_language_from_filename(self, filename: str) -> str:
        """Detect language from filename extension."""
        filename_lower = filename.lower()
        
        extension_mappings = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.jsx': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'css',
            '.sass': 'css',
            '.sql': 'sql',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.txt': 'text',
            '.xml': 'xml',
        }
        
        for ext, lang in extension_mappings.items():
            if filename_lower.endswith(ext):
                return lang
        
        return 'text'
    
    def detect_filename_and_language(self, content: str, language_hint: str = "") -> Tuple[str, str]:
        """
        Detect both filename and language from content.
        
        Args:
            content: Code content
            language_hint: Optional language hint
            
        Returns:
            Tuple of (filename, language)
        """
        # First detect language
        detected_language = language_hint or self.detect_language(content)
        
        # Generate appropriate filename
        filename = self._generate_filename(content, detected_language)
        
        return filename, detected_language
    
    def _generate_filename(self, content: str, language: str) -> str:
        """
        Generate appropriate filename for content.
        
        Args:
            content: Code content
            language: Programming language
            
        Returns:
            Generated filename
        """
        # Use language-specific generator if available
        generator = self.filename_generators.get(language)
        if generator:
            return generator(content)
        
        # Fallback to generic filename
        extension = self.extension_mappings.get(language, '.txt')
        return f"generated_code{extension}"
    
    def _generate_python_filename(self, content: str) -> str:
        """Generate Python filename based on content."""
        # Look for class names
        class_match = re.search(r'class\s+(\w+)', content)
        if class_match:
            return f"{class_match.group(1).lower()}.py"
        
        # Look for main function
        if 'if __name__ == "__main__"' in content:
            return "main.py"
        
        # Look for function names
        func_match = re.search(r'def\s+(\w+)', content)
        if func_match and func_match.group(1) != '__init__':
            return f"{func_match.group(1)}.py"
        
        return "script.py"
    
    def _generate_javascript_filename(self, content: str) -> str:
        """Generate JavaScript filename based on content."""
        # Look for React components
        if 'React' in content or 'Component' in content:
            component_match = re.search(r'(?:class|function)\s+(\w+)', content)
            if component_match:
                return f"{component_match.group(1)}.jsx"
            return "Component.jsx"
        
        # Look for function names
        func_match = re.search(r'function\s+(\w+)', content)
        if func_match:
            return f"{func_match.group(1)}.js"
        
        # Check if it's a module
        if 'export' in content or 'module.exports' in content:
            return "module.js"
        
        return "script.js"
    
    def _generate_java_filename(self, content: str) -> str:
        """Generate Java filename based on content."""
        # Java files must match class name
        class_match = re.search(r'public\s+class\s+(\w+)', content)
        if class_match:
            return f"{class_match.group(1)}.java"
        
        return "Main.java"
    
    def _generate_cpp_filename(self, content: str) -> str:
        """Generate C++ filename based on content."""
        # Look for main function
        if 'int main(' in content:
            return "main.cpp"
        
        # Look for class names
        class_match = re.search(r'class\s+(\w+)', content)
        if class_match:
            return f"{class_match.group(1).lower()}.cpp"
        
        return "program.cpp"
    
    def _generate_c_filename(self, content: str) -> str:
        """Generate C filename based on content."""
        if 'int main(' in content:
            return "main.c"
        
        return "program.c"
    
    def _generate_go_filename(self, content: str) -> str:
        """Generate Go filename based on content."""
        # Look for package name
        package_match = re.search(r'package\s+(\w+)', content)
        if package_match and package_match.group(1) == 'main':
            return "main.go"
        elif package_match:
            return f"{package_match.group(1)}.go"
        
        return "program.go"
    
    def _generate_rust_filename(self, content: str) -> str:
        """Generate Rust filename based on content."""
        if 'fn main(' in content:
            return "main.rs"
        
        return "lib.rs"
    
    def _generate_ruby_filename(self, content: str) -> str:
        """Generate Ruby filename based on content."""
        # Look for class names
        class_match = re.search(r'class\s+(\w+)', content)
        if class_match:
            return f"{class_match.group(1).lower()}.rb"
        
        return "script.rb"
    
    def _generate_php_filename(self, content: str) -> str:
        """Generate PHP filename based on content."""
        # Look for class names
        class_match = re.search(r'class\s+(\w+)', content)
        if class_match:
            return f"{class_match.group(1)}.php"
        
        return "index.php"
    
    def _generate_html_filename(self, content: str) -> str:
        """Generate HTML filename based on content."""
        # Look for title
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            title = re.sub(r'[^a-zA-Z0-9]', '_', title_match.group(1).lower())
            return f"{title}.html"
        
        return "index.html"
    
    def _generate_css_filename(self, content: str) -> str:
        """Generate CSS filename based on content."""
        return "styles.css"
    
    def _generate_sql_filename(self, content: str) -> str:
        """Generate SQL filename based on content."""
        # Check for specific operations
        if re.search(r'CREATE\s+TABLE', content, re.IGNORECASE):
            return "schema.sql"
        elif re.search(r'INSERT\s+INTO', content, re.IGNORECASE):
            return "data.sql"
        
        return "query.sql"
    
    def _generate_shell_filename(self, content: str) -> str:
        """Generate shell script filename based on content."""
        return "script.sh"
    
    def _generate_yaml_filename(self, content: str) -> str:
        """Generate YAML filename based on content."""
        # Look for specific YAML types
        if 'apiVersion:' in content:
            return "deployment.yaml"
        elif 'version:' in content:
            return "config.yaml"
        
        return "data.yaml"
    
    def _generate_json_filename(self, content: str) -> str:
        """Generate JSON filename based on content."""
        # Look for specific JSON structures
        if '"name":' in content and '"version":' in content:
            return "package.json"
        elif '"dependencies":' in content:
            return "config.json"
        
        return "data.json"
    
    def _generate_markdown_filename(self, content: str) -> str:
        """Generate Markdown filename based on content."""
        # Look for first header
        header_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
        if header_match:
            title = re.sub(r'[^a-zA-Z0-9]', '_', header_match.group(1).lower())
            return f"{title}.md"
        
        return "README.md"