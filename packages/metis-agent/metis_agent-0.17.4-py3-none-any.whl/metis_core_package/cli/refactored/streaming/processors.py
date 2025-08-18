"""
Stream processing functionality.

Handles processing of streaming content, code blocks, and file operations.
"""
import re
import time
from typing import Dict, List, Any, Generator, Tuple, Optional


class StreamProcessor:
    """Processes streaming content and manages code blocks."""
    
    def __init__(self, interface):
        """Initialize with reference to main interface."""
        self.interface = interface
        self.code_block_patterns = self._initialize_code_patterns()
    
    def _initialize_code_patterns(self) -> Dict[str, str]:
        """Initialize regular expressions for code block detection."""
        return {
            'fenced_code': r'```(\w*)\n(.*?)\n```',
            'inline_code': r'`([^`]+)`',
            'file_reference': r'(?:file:|filename:|create file:|write to:)\s*([^\n\s]+)',
            'function_definition': r'def\s+(\w+)\s*\([^)]*\):',
            'class_definition': r'class\s+(\w+)\s*(?:\([^)]*\))?:',
            'import_statement': r'(?:import|from)\s+[\w.]+',
        }
    
    def process_query(self, query: str, session_id: Optional[str] = None) -> Generator[str, None, None]:
        """
        Process a query through the agent and stream the response.
        
        Args:
            query: User query to process
            session_id: Optional session identifier
            
        Yields:
            Response chunks
        """
        try:
            # Get agent response
            agent_response = self.interface.agent.run_agent_processing(query)
            
            if isinstance(agent_response, str):
                # Process the text response
                yield from self._process_text_response(agent_response)
            elif hasattr(agent_response, 'get'):
                # Handle dictionary response
                response_text = agent_response.get('response', str(agent_response))
                yield from self._process_text_response(response_text)
            else:
                # Handle other response types
                yield from self._process_text_response(str(agent_response))
                
        except Exception as e:
            yield f"Error processing query: {str(e)}\n"
    
    def _process_text_response(self, response_text: str) -> Generator[str, None, None]:
        """
        Process text response and handle code blocks.
        
        Args:
            response_text: Text response to process
            
        Yields:
            Processed response chunks
        """
        # Check for code blocks
        code_blocks = self.extract_code_blocks(response_text)
        
        if code_blocks:
            yield from self._stream_code_processing(response_text, code_blocks)
        else:
            # No code blocks - stream as formatted text
            yield from self.interface.formatter.stream_formatted_text(response_text)
    
    def extract_code_blocks(self, text: str) -> List[Tuple[str, str, str, int, int]]:
        """
        Extract code blocks from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples: (content, language, filename, start_pos, end_pos)
        """
        code_blocks = []
        
        # Find fenced code blocks
        for match in re.finditer(self.code_block_patterns['fenced_code'], text, re.DOTALL):
            language = match.group(1) or 'text'
            content = match.group(2).strip()
            
            if content:
                # Try to detect filename from surrounding context
                filename = self._detect_filename_from_context(text, match.start(), match.end())
                
                code_blocks.append((
                    content,
                    language,
                    filename,
                    match.start(),
                    match.end()
                ))
        
        return code_blocks
    
    def _detect_filename_from_context(self, text: str, start_pos: int, end_pos: int) -> str:
        """
        Try to detect filename from surrounding context.
        
        Args:
            text: Full text
            start_pos: Start position of code block
            end_pos: End position of code block
            
        Returns:
            Detected filename or empty string
        """
        # Look for filename in text before code block
        context_before = text[max(0, start_pos - 200):start_pos]
        
        # Check for explicit filename references
        for pattern in [
            r'(?:filename|file|create|save):\s*([^\n\s]+)',
            r'([^\s]+\.(?:py|js|java|cpp|c|go|rs|rb|php|md|txt|json|yaml|yml))',
            r'```\s*([^\s]+\.\w+)'
        ]:
            match = re.search(pattern, context_before, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _stream_code_processing(self, response_text: str, 
                               code_blocks: List[Tuple]) -> Generator[str, None, None]:
        """
        Stream processing of response with code blocks.
        
        Args:
            response_text: Full response text
            code_blocks: Extracted code blocks
            
        Yields:
            Response chunks
        """
        last_pos = 0
        
        for i, (content, language, filename, start_pos, end_pos) in enumerate(code_blocks):
            # Stream text before code block
            if start_pos > last_pos:
                text_before = response_text[last_pos:start_pos]
                if text_before.strip():
                    yield from self.interface.formatter.stream_plain_text(text_before)
            
            # Process code block
            yield from self._stream_file_creation(
                content, language, filename, i + 1, len(code_blocks)
            )
            
            last_pos = end_pos
        
        # Stream remaining text
        if last_pos < len(response_text):
            remaining_text = response_text[last_pos:]
            if remaining_text.strip():
                yield from self.interface.formatter.stream_plain_text(remaining_text)
    
    def _stream_file_creation(self, content: str, language: str, filename: str,
                             index: int, total: int) -> Generator[str, None, None]:
        """
        Stream file creation process.
        
        Args:
            content: File content
            language: Programming language
            filename: Filename (may be empty)
            index: Current file index
            total: Total number of files
            
        Yields:
            Status updates
        """
        # Detect filename if not provided
        if not filename:
            filename, detected_language = self.interface.language_detector.detect_filename_and_language(
                content, language
            )
            if detected_language:
                language = detected_language
        
        # Show file processing header
        yield from self.interface.formatter.show_file_processing_header(
            filename, language, index, total
        )
        
        # Get permission to create/modify file
        if filename and self.interface.permission_manager.get_write_permission(filename, content):
            try:
                # Write file
                full_path = self._get_full_file_path(filename)
                self._write_file_content(full_path, content)
                
                # Update statistics
                self.interface.total_files_processed += 1
                self.interface.total_lines_written += len(content.splitlines())
                
                # Show success message
                yield from self.interface.formatter.show_file_creation_success(filename, full_path)
                
            except Exception as e:
                yield from self.interface.formatter.show_file_creation_error(filename, str(e))
        else:
            # Show code preview if no filename or permission denied
            yield from self.interface.formatter.show_code_preview(content, language)
    
    def _get_full_file_path(self, filename: str) -> str:
        """Get full path for a filename."""
        if os.path.isabs(filename):
            return filename
        return os.path.join(self.interface.project_location, filename)
    
    def _write_file_content(self, file_path: str, content: str):
        """
        Write content to a file.
        
        Args:
            file_path: Full path to file
            content: Content to write
        """
        import os
        
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def analyze_code_complexity(self, content: str) -> Dict[str, Any]:
        """
        Analyze code complexity and characteristics.
        
        Args:
            content: Code content to analyze
            
        Returns:
            Analysis results
        """
        analysis = {
            'lines_of_code': len([line for line in content.splitlines() if line.strip()]),
            'total_lines': len(content.splitlines()),
            'functions': len(re.findall(self.code_block_patterns['function_definition'], content)),
            'classes': len(re.findall(self.code_block_patterns['class_definition'], content)),
            'imports': len(re.findall(self.code_block_patterns['import_statement'], content)),
            'complexity': 'low'
        }
        
        # Determine complexity
        if analysis['lines_of_code'] > 100 or analysis['functions'] > 5 or analysis['classes'] > 2:
            analysis['complexity'] = 'high'
        elif analysis['lines_of_code'] > 50 or analysis['functions'] > 2:
            analysis['complexity'] = 'medium'
        
        return analysis
    
    def validate_code_syntax(self, content: str, language: str) -> Dict[str, Any]:
        """
        Validate code syntax (basic validation).
        
        Args:
            content: Code content
            language: Programming language
            
        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if language == 'python':
            try:
                import ast
                ast.parse(content)
            except SyntaxError as e:
                validation['valid'] = False
                validation['errors'].append(f"Syntax error: {e}")
        
        # Basic validation for other languages could be added here
        
        return validation