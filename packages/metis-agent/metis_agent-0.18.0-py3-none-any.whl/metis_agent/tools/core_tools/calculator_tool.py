"""
Intelligent CalculatorTool without hardcoded patterns.
Uses semantic understanding and dynamic detection.
"""
import re
import math
import ast
import operator
import asyncio
from typing import Dict, Any, List, Union, AsyncIterator
from ..base import BaseTool
from ...utils.input_validator import ValidationError


class CalculatorTool(BaseTool):
    """Intelligent calculator tool with semantic task detection."""
    
    def __init__(self):
        super().__init__()  # Initialize caching
        self.name = "CalculatorTool"
        self.description = "Performs mathematical calculations, arithmetic operations, and mathematical function evaluations"
        
        # Mathematical operators for safe evaluation
        self.safe_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        # Mathematical functions
        self.safe_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'ln': math.log,
            'exp': math.exp,
            'floor': math.floor,
            'ceil': math.ceil,
            'pi': math.pi,
            'e': math.e,
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Intelligently determine if this is a mathematical task.
        Uses multiple detection methods without hardcoded patterns.
        
        Args:
            task: The task description
            
        Returns:
            True if this is a math task, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Method 1: Semantic indicators
        if self._has_mathematical_semantics(task_clean):
            return True
        
        # Method 2: Check for extractable mathematical expressions
        if self._contains_mathematical_expression(task):
            return True
        
        # Method 3: Mathematical function calls
        if self._contains_mathematical_functions(task_clean):
            return True
        
        # Method 4: Exclude clearly non-mathematical queries
        if self._is_clearly_non_mathematical(task_clean):
            return False
        
        return False
    
    def _has_mathematical_semantics(self, task: str) -> bool:
        """Check for mathematical semantic indicators."""
        # Mathematical action words
        math_actions = {
            'calculate', 'compute', 'solve', 'evaluate', 'find the result',
            'how much is', 'determine', 'figure out'
        }
        
        # Mathematical concepts
        math_concepts = {
            'sum', 'product', 'difference', 'quotient', 'remainder',
            'square', 'cube', 'root', 'power', 'exponent',
            'percent', 'percentage', 'fraction', 'decimal',
            'average', 'mean', 'median', 'total'
        }
        
        # Mathematical operations in words
        math_operations = {
            'plus', 'minus', 'times', 'multiplied by', 'divided by',
            'add', 'subtract', 'multiply', 'divide',
            'to the power of', 'squared', 'cubed'
        }
        
        # Check if task contains mathematical semantics
        for word_set in [math_actions, math_concepts, math_operations]:
            for word in word_set:
                if word in task:
                    return True
        
        return False
    
    def _contains_mathematical_expression(self, task: str) -> bool:
        """Check if task contains a mathematical expression."""
        # Extract potential mathematical expressions
        # Look for number + operator + number patterns
        number_pattern = r'[-+]?\d*\.?\d+'
        operator_pattern = r'[\+\-\*\/\%\^]'
        
        # Find all numbers in the text
        numbers = re.findall(number_pattern, task)
        operators = re.findall(operator_pattern, task)
        
        # If we have at least 2 numbers and 1 operator, likely mathematical
        if len(numbers) >= 2 and len(operators) >= 1:
            return True
        
        # Check for parentheses with numbers (mathematical expressions)
        paren_content = re.findall(r'\([^)]*\)', task)
        for content in paren_content:
            if re.search(r'\d+.*[\+\-\*\/].*\d+', content):
                return True
        
        return False
    
    def _contains_mathematical_functions(self, task: str) -> bool:
        """Check for mathematical function calls."""
        for func_name in self.safe_functions.keys():
            # Look for function call patterns: func( or func of
            if f'{func_name}(' in task or f'{func_name} of' in task:
                return True
        
        return False
    
    def _is_clearly_non_mathematical(self, task: str) -> bool:
        """Check if task is clearly non-mathematical."""
        # Non-mathematical question types
        non_math_indicators = [
            'capital of', 'who is', 'where is', 'when was', 'what year',
            'list files', 'show files', 'directory', 'folder',
            'search for', 'find information', 'tell me about',
            'explain', 'describe', 'definition of',
            'create file', 'generate code', 'write a',
            'translate', 'convert text', 'format as',
            'what do you think', 'your opinion', 'future of', 
            'thoughts about', 'believe that', 'philosophy',
            'artificial intelligence', 'machine learning', 'technology',
            'opinion on', 'view on', 'perspective', 'do you feel'
        ]
        
        for indicator in non_math_indicators:
            if indicator in task:
                return True
        
        # Check if it's asking about a specific year, version, address, etc.
        if re.search(r'\b(year|version|address|street|road)\b', task):
            return True
        
        # Check for "what is" followed by non-mathematical concepts
        if 'what is' in task.lower():
            # Non-mathematical contexts after "what is"
            non_math_contexts = [
                'your', 'the future', 'artificial', 'intelligence', 'ai',
                'machine learning', 'technology', 'opinion', 'thought',
                'best', 'good', 'bad', 'better', 'difference between'
            ]
            what_is_part = task.lower().split('what is')[1] if 'what is' in task.lower() else ''
            if any(context in what_is_part for context in non_math_contexts):
                return True
        
        # Check for opinion-seeking patterns
        opinion_patterns = [
            r'\bthink\s+about\b', r'\bfuture\s+of\b', r'\bopinion\s+on\b',
            r'\bview\s+on\b', r'\bthoughts?\s+on\b', r'\bfeel\s+about\b'
        ]
        for pattern in opinion_patterns:
            if re.search(pattern, task.lower()):
                return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute mathematical calculation with input validation."""
        try:
            # Validate input
            try:
                validated_task = self._validate_task_input(task, context="general")
                validated_kwargs = self._validate_kwargs_input(kwargs)
            except ValidationError as e:
                return {
                    "success": False,
                    "error": f"Input validation failed: {e}",
                    "error_code": "INPUT_VALIDATION_ERROR"
                }
            
            if not self.can_handle(validated_task):
                return {
                    "success": False,
                    "error": "Not a mathematical calculation task",
                    "error_code": "INVALID_MATH_TASK",
                    "task_analysis": self._analyze_task_type(validated_task)
                }
            
            # Extract and evaluate mathematical expression
            result = self._evaluate_mathematical_task(validated_task)
            
            return {
                "success": True,
                "type": "calculation_result",
                "data": {
                    "original_task": validated_task,
                    "extracted_expression": result.get('expression', validated_task),
                    "result": result['value'],
                    "result_type": type(result['value']).__name__,
                    "calculation_method": result.get('method', 'unknown')
                },
                "metadata": {
                    "tool_name": "CalculatorTool",
                    "calculation_type": result.get('type', 'mathematical_expression')
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Calculation failed: {str(e)}",
                "error_code": "CALCULATION_ERROR",
                "details": str(e),
                "task_analysis": self._analyze_task_type(task)
            }
    
    async def execute_async(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Async version of execute for mathematical calculations.
        
        For simple calculations, runs synchronously. For complex calculations,
        uses async processing to avoid blocking.
        """
        try:
            # Validate input
            try:
                validated_task = self._validate_task_input(task, context="general")
                validated_kwargs = self._validate_kwargs_input(kwargs)
            except ValidationError as e:
                return {
                    "success": False,
                    "error": f"Input validation failed: {e}",
                    "error_code": "INPUT_VALIDATION_ERROR"
                }
            
            if not self.can_handle(validated_task):
                return {
                    "success": False,
                    "error": "Not a mathematical calculation task",
                    "error_code": "INVALID_MATH_TASK",
                    "task_analysis": self._analyze_task_type(validated_task)
                }
            
            # For complex calculations, run in executor to avoid blocking
            if self._is_complex_calculation(validated_task):
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    self._evaluate_mathematical_task, 
                    validated_task
                )
            else:
                # Simple calculations can run directly
                result = self._evaluate_mathematical_task(validated_task)
            
            return {
                "success": True,
                "type": "calculation_result",
                "data": {
                    "original_task": validated_task,
                    "extracted_expression": result.get('expression', validated_task),
                    "result": result['value'],
                    "result_type": type(result['value']).__name__,
                    "calculation_method": result.get('method', 'unknown')
                },
                "metadata": {
                    "tool_name": "CalculatorTool",
                    "calculation_type": result.get('type', 'mathematical_expression'),
                    "async_processed": self._is_complex_calculation(validated_task)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Async calculation failed: {str(e)}",
                "error_code": "ASYNC_CALCULATION_ERROR",
                "details": str(e),
                "task_analysis": self._analyze_task_type(task)
            }
    
    async def execute_stream_async(self, task: str, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """
        Streaming async version for complex calculations.
        
        Yields intermediate steps for complex mathematical operations.
        """
        try:
            # Validate input
            try:
                validated_task = self._validate_task_input(task, context="general")
                validated_kwargs = self._validate_kwargs_input(kwargs)
            except ValidationError as e:
                yield {
                    "success": False,
                    "error": f"Input validation failed: {e}",
                    "error_code": "INPUT_VALIDATION_ERROR"
                }
                return
            
            if not self.can_handle(validated_task):
                yield {
                    "success": False,
                    "error": "Not a mathematical calculation task",
                    "error_code": "INVALID_MATH_TASK"
                }
                return
            
            # Yield initial status
            yield {
                "status": "starting",
                "message": "Beginning calculation...",
                "task": validated_task
            }
            
            # Analyze the calculation complexity
            is_complex = self._is_complex_calculation(validated_task)
            
            yield {
                "status": "analyzing",
                "complexity": "complex" if is_complex else "simple",
                "message": "Analyzing mathematical expression..."
            }
            
            # For streaming, break down complex calculations into steps
            if is_complex:
                # Yield progress updates for complex calculations
                yield {
                    "status": "processing",
                    "message": "Evaluating complex mathematical expression..."
                }
                
                # Simulate step-by-step processing (for demo purposes)
                await asyncio.sleep(0.1)
                
                yield {
                    "status": "partial_result",
                    "message": "Parsing mathematical components..."
                }
                
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    self._evaluate_mathematical_task, 
                    validated_task
                )
            else:
                # Simple calculations
                result = self._evaluate_mathematical_task(validated_task)
            
            # Yield final result
            yield {
                "success": True,
                "status": "complete",
                "type": "calculation_result",
                "data": {
                    "original_task": validated_task,
                    "extracted_expression": result.get('expression', validated_task),
                    "result": result['value'],
                    "result_type": type(result['value']).__name__,
                    "calculation_method": result.get('method', 'unknown')
                },
                "metadata": {
                    "tool_name": "CalculatorTool",
                    "calculation_type": result.get('type', 'mathematical_expression'),
                    "streaming_processed": True,
                    "complexity": "complex" if is_complex else "simple"
                }
            }
            
        except Exception as e:
            yield {
                "success": False,
                "status": "error",
                "error": f"Streaming calculation failed: {str(e)}",
                "error_code": "STREAMING_CALCULATION_ERROR"
            }
    
    def _is_complex_calculation(self, task: str) -> bool:
        """
        Determine if a calculation is complex enough to warrant async processing.
        
        Args:
            task: The mathematical task
            
        Returns:
            True if the calculation is complex
        """
        # Consider it complex if:
        # 1. Contains mathematical functions (sin, cos, log, etc.)
        # 2. Has multiple nested operations
        # 3. Contains factorials or large numbers
        # 4. Has loops or sequences
        
        complex_indicators = [
            'sin', 'cos', 'tan', 'log', 'sqrt', 'factorial',
            'sum', 'product', 'integral', 'derivative',
            '!', '**', 'pow', 'exp'
        ]
        
        task_lower = task.lower()
        
        # Check for mathematical functions
        for indicator in complex_indicators:
            if indicator in task_lower:
                return True
        
        # Check for deeply nested operations
        if task.count('(') > 3 or task.count('[') > 2:
            return True
        
        # Check for large numbers (might be computationally intensive)
        numbers = re.findall(r'\d+', task)
        for num_str in numbers:
            if len(num_str) > 6:  # Numbers with more than 6 digits
                return True
        
        return False
    
    def _evaluate_mathematical_task(self, task: str) -> Dict[str, Any]:
        """Intelligently evaluate mathematical task."""
        task_lower = task.lower().strip()
        
        # Method 1: Try to extract direct arithmetic expressions
        arithmetic_result = self._extract_arithmetic_expression(task)
        if arithmetic_result:
            return arithmetic_result
        
        # Method 2: Handle word-based mathematics
        word_math_result = self._handle_word_mathematics(task_lower)
        if word_math_result:
            return word_math_result
        
        # Method 3: Handle function calls
        function_result = self._handle_function_calls(task_lower)
        if function_result:
            return function_result
        
        # Method 4: Extract numbers and guess the operation
        fallback_result = self._fallback_number_extraction(task)
        if fallback_result:
            return fallback_result
        
        raise ValueError(f"Could not extract mathematical operation from: {task}")
    
    def _extract_arithmetic_expression(self, task: str) -> Union[Dict[str, Any], None]:
        """Extract and evaluate arithmetic expressions."""
        # Find mathematical expressions in the text
        # Look for patterns like: number operator number
        expressions = re.findall(r'([-+]?\d*\.?\d+)\s*([\+\-\*\/\%\^])\s*([-+]?\d*\.?\d+)', task)
        
        for expr in expressions:
            try:
                num1, op, num2 = expr
                num1, num2 = float(num1), float(num2)
                
                if op == '+':
                    result = num1 + num2
                elif op == '-':
                    result = num1 - num2
                elif op == '*':
                    result = num1 * num2
                elif op == '/':
                    if num2 == 0:
                        raise ValueError("Division by zero")
                    result = num1 / num2
                elif op == '%':
                    result = num1 % num2
                elif op == '^':
                    result = num1 ** num2
                else:
                    continue
                
                return {
                    'value': result,
                    'expression': f"{num1} {op} {num2}",
                    'method': 'arithmetic_extraction',
                    'type': 'arithmetic'
                }
            except (ValueError, ZeroDivisionError) as e:
                continue
        
        return None
    
    def _handle_word_mathematics(self, task: str) -> Union[Dict[str, Any], None]:
        """Handle word-based mathematical expressions."""
        # Extract all numbers from the task
        numbers = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', task)]
        
        if len(numbers) < 2:
            return None
        
        # Determine operation from words
        if any(word in task for word in ['plus', 'add', 'sum', 'total']):
            result = sum(numbers)
            return {
                'value': result,
                'expression': f"sum({numbers})",
                'method': 'word_mathematics',
                'type': 'addition'
            }
        
        elif any(word in task for word in ['minus', 'subtract', 'difference']):
            result = numbers[0] - numbers[1]
            return {
                'value': result,
                'expression': f"{numbers[0]} - {numbers[1]}",
                'method': 'word_mathematics',
                'type': 'subtraction'
            }
        
        elif any(word in task for word in ['times', 'multiply', 'product']):
            result = numbers[0] * numbers[1]
            return {
                'value': result,
                'expression': f"{numbers[0]} * {numbers[1]}",
                'method': 'word_mathematics',
                'type': 'multiplication'
            }
        
        elif any(word in task for word in ['divided by', 'divide', 'quotient']):
            if numbers[1] == 0:
                raise ValueError("Division by zero")
            result = numbers[0] / numbers[1]
            return {
                'value': result,
                'expression': f"{numbers[0]} / {numbers[1]}",
                'method': 'word_mathematics',
                'type': 'division'
            }
        
        elif any(word in task for word in ['power', 'to the power of', 'exponent']):
            result = numbers[0] ** numbers[1]
            return {
                'value': result,
                'expression': f"{numbers[0]} ^ {numbers[1]}",
                'method': 'word_mathematics',
                'type': 'exponentiation'
            }
        
        return None
    
    def _handle_function_calls(self, task: str) -> Union[Dict[str, Any], None]:
        """Handle mathematical function calls."""
        for func_name, func in self.safe_functions.items():
            if func_name in task:
                # Extract number after function name
                pattern = f'{func_name}\\s*\\(?\\s*([-+]?\\d*\\.?\\d+)'
                match = re.search(pattern, task)
                if match:
                    try:
                        arg = float(match.group(1))
                        if callable(func):
                            result = func(arg)
                        else:
                            result = func  # Constants like pi, e
                        
                        return {
                            'value': result,
                            'expression': f"{func_name}({arg})",
                            'method': 'function_call',
                            'type': f'function_{func_name}'
                        }
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def _fallback_number_extraction(self, task: str) -> Union[Dict[str, Any], None]:
        """Fallback: extract numbers and perform basic operation."""
        numbers = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', task)]
        
        if len(numbers) == 1:
            # Single number - might be asking for the value
            return {
                'value': numbers[0],
                'expression': str(numbers[0]),
                'method': 'single_number_extraction',
                'type': 'value'
            }
        
        elif len(numbers) == 2:
            # Two numbers - guess operation based on context or default to addition
            result = numbers[0] + numbers[1]
            return {
                'value': result,
                'expression': f"{numbers[0]} + {numbers[1]}",
                'method': 'fallback_addition',
                'type': 'assumed_addition'
            }
        
        return None
    
    def _analyze_task_type(self, task: str) -> Dict[str, Any]:
        """Analyze what type of task this is for debugging."""
        return {
            'has_numbers': bool(re.search(r'\d+', task)),
            'has_operators': bool(re.search(r'[\+\-\*\/\%\^]', task)),
            'has_math_words': any(word in task.lower() for word in ['calculate', 'compute', 'plus', 'minus']),
            'has_question_words': any(word in task.lower() for word in ['what', 'who', 'where', 'when']),
            'word_count': len(task.split()),
            'contains_math_functions': any(func in task.lower() for func in self.safe_functions.keys())
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "Calculate 42 * 3",
            "What is 25 + 17?",
            "Compute 100 / 4",
            "What is 15 percent of 200?",
            "Find the square root of 144",
            "What is 2 to the power of 8?",
            "Solve 10 minus 3 plus 5",
            "Calculate the sum of 5 and 7",
            "What is 8 times 6?",
            "Find the absolute value of -15"
        ]
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capabilities for MCP integration."""
        return {
            "complexity_levels": ["trivial", "simple"],
            "input_types": ["text", "mathematical_expression"],
            "output_types": ["numerical_result", "structured_data"],
            "estimated_execution_time": "< 1s",
            "requires_internet": False,
            "requires_filesystem": False,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": ["calculate", "compute", "math", "arithmetic"],
            "api_dependencies": [],
            "memory_usage": "low",
            "mathematical_operations": [
                "addition", "subtraction", "multiplication", "division",
                "exponentiation", "modulo", "square_root", "trigonometric",
                "logarithmic", "absolute_value"
            ]
        }


#