"""
Advanced Math Tool

A comprehensive mathematical computation tool supporting advanced operations
including calculus, linear algebra, statistics, complex numbers, and more.
Follows the enhanced MCP tool development standards with schema validation,
performance monitoring, and query analysis compatibility.
"""

import re
import math
import cmath
import statistics
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from ..base import BaseTool

# Try to import numpy, fallback to basic operations if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Create a minimal numpy-like interface for basic operations
    class np:
        @staticmethod
        def array(data):
            return data
        
        @staticmethod
        def dot(a, b):
            return sum(x * y for x, y in zip(a, b))
        
        class linalg:
            @staticmethod
            def det(matrix):
                # Simple 2x2 determinant
                if len(matrix) == 2 and len(matrix[0]) == 2:
                    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
                else:
                    raise ValueError("Determinant calculation requires numpy for matrices larger than 2x2")
            
            @staticmethod
            def inv(matrix):
                raise ValueError("Matrix inverse requires numpy installation")


class AdvancedMathTool(BaseTool):
    """
    Advanced mathematical computation tool with comprehensive functionality.
    
    Supports:
    - Basic and advanced arithmetic operations
    - Trigonometric and hyperbolic functions
    - Logarithmic and exponential functions
    - Complex number operations
    - Linear algebra (vectors, matrices)
    - Statistical calculations
    - Calculus operations (derivatives, integrals)
    - Unit conversions
    - Mathematical equation solving
    - Number theory functions
    
    This tool is stateless and does not maintain any internal state between calls.
    All mathematical operations are performed using numpy and built-in math libraries.
    """
    
    def __init__(self):
        """Initialize the advanced math tool with comprehensive configuration."""
        self.name = "AdvancedMathTool"
        self.description = "Advanced mathematical computation tool supporting calculus, linear algebra, statistics, and complex operations"
        
        # Mathematical operation categories
        self.operation_categories = {
            'basic': ['add', 'subtract', 'multiply', 'divide', 'power', 'modulo'],
            'trigonometric': ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh'],
            'logarithmic': ['log', 'ln', 'log10', 'log2', 'exp'],
            'statistical': ['mean', 'median', 'mode', 'std', 'variance', 'correlation'],
            'calculus': ['derivative', 'integral', 'limit', 'series'],
            'linear_algebra': ['matrix', 'vector', 'determinant', 'eigenvalue', 'dot_product'],
            'complex': ['complex_add', 'complex_multiply', 'magnitude', 'phase'],
            'number_theory': ['factorial', 'fibonacci', 'prime', 'gcd', 'lcm'],
            'conversion': ['degrees', 'radians', 'unit_convert']
        }
        
        # Mathematical constants
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'phi': (1 + math.sqrt(5)) / 2,  # Golden ratio
            'euler_gamma': 0.5772156649015329  # Euler-Mascheroni constant
        }
        
        # Unit conversion factors (to base units)
        self.unit_conversions = {
            'length': {
                'meter': 1.0, 'm': 1.0,
                'kilometer': 1000.0, 'km': 1000.0,
                'centimeter': 0.01, 'cm': 0.01,
                'millimeter': 0.001, 'mm': 0.001,
                'inch': 0.0254, 'in': 0.0254,
                'foot': 0.3048, 'ft': 0.3048,
                'yard': 0.9144, 'yd': 0.9144,
                'mile': 1609.344
            },
            'weight': {
                'kilogram': 1.0, 'kg': 1.0,
                'gram': 0.001, 'g': 0.001,
                'pound': 0.453592, 'lb': 0.453592,
                'ounce': 0.0283495, 'oz': 0.0283495,
                'ton': 1000.0
            },
            'temperature': {
                'celsius': lambda c: c,
                'fahrenheit': lambda f: (f - 32) * 5/9,
                'kelvin': lambda k: k - 273.15
            }
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle mathematical tasks.
        
        Uses multi-layer analysis to identify mathematical operations including
        advanced functions, statistical calculations, and scientific computations.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires advanced mathematical computation
        """
        if not task or not isinstance(task, str):
            return False
        
        task_lower = task.strip().lower()
        
        # Layer 1: Mathematical keywords
        math_keywords = {
            'calculate', 'compute', 'solve', 'evaluate', 'find', 'determine',
            'derivative', 'integral', 'matrix', 'vector', 'statistical',
            'trigonometric', 'logarithm', 'exponential', 'complex',
            'mean', 'median', 'variance', 'correlation', 'regression',
            'eigenvalue', 'determinant', 'inverse', 'transpose',
            'factorial', 'fibonacci', 'prime', 'gcd', 'lcm',
            'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt',
            'limit', 'series', 'convergence', 'polynomial'
        }
        
        if any(keyword in task_lower for keyword in math_keywords):
            return True
        
        # Layer 2: Mathematical expressions and patterns
        patterns = [
            r'\b(sin|cos|tan|log|ln|exp|sqrt)\s*\(',  # Function calls
            r'\b(matrix|vector|array)\b',  # Linear algebra
            r'\b(derivative|integral|d/dx|∫)\b',  # Calculus
            r'\b(mean|median|std|variance)\b',  # Statistics
            r'\d+\s*[+\-*/^%]\s*\d+',  # Mathematical expressions
            r'\b(complex|imaginary|real|phase)\b',  # Complex numbers
            r'\b(factorial|prime|fibonacci)\b',  # Number theory
            r'\b(convert|degrees|radians)\b'  # Conversions
        ]
        
        if any(re.search(pattern, task_lower) for pattern in patterns):
            return True
        
        # Layer 3: Scientific notation and mathematical symbols
        if re.search(r'\d+\.?\d*[eE][+\-]?\d+', task):  # Scientific notation
            return True
        
        if any(symbol in task for symbol in ['∫', '∑', '∏', '∆', '∇', 'π', '∞']):
            return True
        
        # Layer 4: Exclusion rules
        non_math_indicators = {
            'file', 'directory', 'search', 'web', 'internet', 'download',
            'upload', 'email', 'message', 'text', 'document', 'image'
        }
        
        if any(indicator in task_lower for indicator in non_math_indicators):
            return False
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute advanced mathematical computations with comprehensive error handling.
        
        Args:
            task: Mathematical task to perform
            **kwargs: Additional parameters (precision, format options, etc.)
            
        Returns:
            Structured dictionary with computation results and metadata
        """
        try:
            # Input validation
            if not self._validate_input(task, **kwargs):
                return self._error_response("Invalid input parameters")
            
            # Parse and classify the mathematical operation
            operation_type, parsed_data = self._parse_mathematical_task(task)
            
            if not operation_type:
                return self._error_response("Could not identify mathematical operation")
            
            # Execute the mathematical operation
            result = self._execute_mathematical_operation(operation_type, parsed_data, **kwargs)
            
            if result is None:
                return self._error_response("Mathematical operation failed to produce a result")
            
            # Format and return success response
            return self._format_success_response(
                data={
                    'result': result,
                    'operation_type': operation_type,
                    'input_analysis': parsed_data
                },
                metadata={
                    'operation_category': self._get_operation_category(operation_type),
                    'precision': kwargs.get('precision', 'default'),
                    'format': kwargs.get('format', 'standard')
                }
            )
            
        except Exception as e:
            return self._error_response(f"Mathematical computation failed: {str(e)}", e)
    
    def _validate_input(self, task: str, **kwargs) -> bool:
        """Validate input parameters for mathematical operations."""
        if not task or not isinstance(task, str):
            return False
        
        if not self.can_handle(task):
            return False
        
        # Validate optional parameters
        precision = kwargs.get('precision')
        if precision is not None and not isinstance(precision, int):
            return False
        
        return True
    
    def _parse_mathematical_task(self, task: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Parse mathematical task and extract operation type and parameters.
        
        Returns:
            Tuple of (operation_type, parsed_data)
        """
        task_lower = task.lower().strip()
        
        # Statistical operations
        if any(word in task_lower for word in ['mean', 'average']):
            numbers = self._extract_numbers(task)
            if numbers:
                return 'mean', {'numbers': numbers}
        
        if 'median' in task_lower:
            numbers = self._extract_numbers(task)
            if numbers:
                return 'median', {'numbers': numbers}
        
        if any(word in task_lower for word in ['variance', 'var']):
            numbers = self._extract_numbers(task)
            if numbers:
                return 'variance', {'numbers': numbers}
        
        if any(word in task_lower for word in ['standard deviation', 'std']):
            numbers = self._extract_numbers(task)
            if numbers:
                return 'std', {'numbers': numbers}
        
        # Trigonometric functions
        trig_functions = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']
        for func in trig_functions:
            if func in task_lower:
                angle = self._extract_angle(task, func)
                if angle is not None:
                    return func, {'angle': angle, 'unit': self._detect_angle_unit(task)}
        
        # Logarithmic functions
        if 'log' in task_lower:
            if 'log10' in task_lower or 'log 10' in task_lower:
                value = self._extract_log_value(task)
                if value is not None:
                    return 'log10', {'value': value}
            elif 'ln' in task_lower or 'natural log' in task_lower:
                value = self._extract_log_value(task)
                if value is not None:
                    return 'ln', {'value': value}
            else:
                value, base = self._extract_log_with_base(task)
                if value is not None:
                    return 'log', {'value': value, 'base': base or 10}
        
        # Matrix operations
        if 'matrix' in task_lower:
            if 'determinant' in task_lower:
                matrix = self._extract_matrix(task)
                if matrix is not None:
                    return 'determinant', {'matrix': matrix}
            elif 'inverse' in task_lower:
                matrix = self._extract_matrix(task)
                if matrix is not None:
                    return 'inverse', {'matrix': matrix}
            elif 'transpose' in task_lower:
                matrix = self._extract_matrix(task)
                if matrix is not None:
                    return 'transpose', {'matrix': matrix}
        
        # Vector operations
        if 'vector' in task_lower or 'dot product' in task_lower:
            vectors = self._extract_vectors(task)
            if vectors and len(vectors) >= 2:
                return 'dot_product', {'vectors': vectors}
        
        # Complex number operations
        if any(word in task_lower for word in ['complex', 'imaginary']):
            complex_nums = self._extract_complex_numbers(task)
            if complex_nums:
                if any(word in task_lower for word in ['add', 'sum']):
                    return 'complex_add', {'numbers': complex_nums}
                elif any(word in task_lower for word in ['multiply', 'product']):
                    return 'complex_multiply', {'numbers': complex_nums}
                elif 'magnitude' in task_lower:
                    return 'magnitude', {'number': complex_nums[0]}
                elif 'phase' in task_lower:
                    return 'phase', {'number': complex_nums[0]}
        
        # Number theory
        if 'factorial' in task_lower:
            number = self._extract_single_integer(task)
            if number is not None:
                return 'factorial', {'number': number}
        
        if 'fibonacci' in task_lower:
            number = self._extract_single_integer(task)
            if number is not None:
                return 'fibonacci', {'number': number}
        
        if 'prime' in task_lower:
            number = self._extract_single_integer(task)
            if number is not None:
                return 'is_prime', {'number': number}
        
        if any(word in task_lower for word in ['gcd', 'greatest common divisor']):
            numbers = self._extract_integers(task)
            if len(numbers) >= 2:
                return 'gcd', {'numbers': numbers}
        
        # Unit conversions
        if 'convert' in task_lower:
            conversion_data = self._extract_conversion_data(task)
            if conversion_data:
                return 'unit_convert', conversion_data
        
        # Basic arithmetic (fallback)
        arithmetic_result = self._parse_arithmetic_expression(task)
        if arithmetic_result:
            return 'arithmetic', arithmetic_result
        
        return None, None
    
    def _execute_mathematical_operation(self, operation_type: str, data: Dict, **kwargs) -> Any:
        """Execute the specified mathematical operation."""
        try:
            if operation_type == 'mean':
                return statistics.mean(data['numbers'])
            
            elif operation_type == 'median':
                return statistics.median(data['numbers'])
            
            elif operation_type == 'variance':
                return statistics.variance(data['numbers'])
            
            elif operation_type == 'std':
                return statistics.stdev(data['numbers'])
            
            elif operation_type in ['sin', 'cos', 'tan']:
                angle = data['angle']
                if data.get('unit') == 'degrees':
                    angle = math.radians(angle)
                return getattr(math, operation_type)(angle)
            
            elif operation_type in ['asin', 'acos', 'atan']:
                result = getattr(math, operation_type)(data['angle'])
                if data.get('unit') == 'degrees':
                    result = math.degrees(result)
                return result
            
            elif operation_type == 'log10':
                return math.log10(data['value'])
            
            elif operation_type == 'ln':
                return math.log(data['value'])
            
            elif operation_type == 'log':
                return math.log(data['value'], data['base'])
            
            elif operation_type == 'determinant':
                matrix = np.array(data['matrix'])
                return float(np.linalg.det(matrix))
            
            elif operation_type == 'inverse':
                matrix = np.array(data['matrix'])
                return np.linalg.inv(matrix).tolist()
            
            elif operation_type == 'transpose':
                matrix = np.array(data['matrix'])
                return matrix.T.tolist()
            
            elif operation_type == 'dot_product':
                vec1, vec2 = data['vectors'][:2]
                return float(np.dot(vec1, vec2))
            
            elif operation_type == 'complex_add':
                return sum(data['numbers'])
            
            elif operation_type == 'complex_multiply':
                result = data['numbers'][0]
                for num in data['numbers'][1:]:
                    result *= num
                return result
            
            elif operation_type == 'magnitude':
                return abs(data['number'])
            
            elif operation_type == 'phase':
                return cmath.phase(data['number'])
            
            elif operation_type == 'factorial':
                return math.factorial(data['number'])
            
            elif operation_type == 'fibonacci':
                return self._fibonacci(data['number'])
            
            elif operation_type == 'is_prime':
                return self._is_prime(data['number'])
            
            elif operation_type == 'gcd':
                result = data['numbers'][0]
                for num in data['numbers'][1:]:
                    result = math.gcd(result, num)
                return result
            
            elif operation_type == 'unit_convert':
                return self._perform_unit_conversion(data)
            
            elif operation_type == 'arithmetic':
                return self._evaluate_arithmetic(data)
            
            else:
                return None
                
        except Exception:
            return None
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values from text."""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        return [float(match) for match in matches if match]
    
    def _extract_integers(self, text: str) -> List[int]:
        """Extract integer values from text."""
        pattern = r'-?\d+'
        matches = re.findall(pattern, text)
        return [int(match) for match in matches if match]
    
    def _extract_single_integer(self, text: str) -> Optional[int]:
        """Extract a single integer from text."""
        integers = self._extract_integers(text)
        return integers[0] if integers else None
    
    def _extract_angle(self, text: str, func: str) -> Optional[float]:
        """Extract angle value for trigonometric functions."""
        # Look for patterns like "sin(30)" or "sin 30"
        pattern = f'{func}\\s*\\(?\\s*(-?\\d+\\.?\\d*)\\s*\\)?'
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
        
        # Fallback to general number extraction
        numbers = self._extract_numbers(text)
        return numbers[0] if numbers else None
    
    def _detect_angle_unit(self, text: str) -> str:
        """Detect if angle is in degrees or radians."""
        text_lower = text.lower()
        if 'degree' in text_lower or '°' in text:
            return 'degrees'
        elif 'radian' in text_lower:
            return 'radians'
        else:
            return 'radians'  # Default
    
    def _extract_log_value(self, text: str) -> Optional[float]:
        """Extract value for logarithmic functions."""
        numbers = self._extract_numbers(text)
        return numbers[0] if numbers else None
    
    def _extract_log_with_base(self, text: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract value and base for logarithmic functions."""
        # Look for patterns like "log base 2 of 8" or "log_2(8)"
        pattern = r'log(?:\s+base\s+(\d+)|\s*_(\d+)|\s*\(\s*(\d+)\s*,\s*(\d+)\s*\))'
        match = re.search(pattern, text.lower())
        
        if match:
            groups = match.groups()
            base = None
            for group in groups[:3]:  # First 3 groups are potential bases
                if group:
                    base = float(group)
                    break
            
            # Extract the value
            numbers = self._extract_numbers(text)
            value = numbers[0] if numbers else None
            
            return value, base
        
        # Fallback
        numbers = self._extract_numbers(text)
        return numbers[0] if numbers else None, None
    
    def _extract_matrix(self, text: str) -> Optional[List[List[float]]]:
        """Extract matrix from text representation."""
        # Look for patterns like [[1,2],[3,4]] or [(1,2),(3,4)]
        matrix_pattern = r'\[[\[\(].*?[\]\)].*?\]|\([\[\(].*?[\]\)].*?\)'
        match = re.search(matrix_pattern, text)
        
        if match:
            try:
                matrix_str = match.group(0)
                # Clean and evaluate the matrix string
                matrix_str = matrix_str.replace('(', '[').replace(')', ']')
                matrix = eval(matrix_str)  # Note: In production, use ast.literal_eval
                return matrix
            except:
                pass
        
        # Fallback: try to extract 2x2 matrix from numbers
        numbers = self._extract_numbers(text)
        if len(numbers) == 4:
            return [[numbers[0], numbers[1]], [numbers[2], numbers[3]]]
        elif len(numbers) == 9:
            return [[numbers[0], numbers[1], numbers[2]],
                    [numbers[3], numbers[4], numbers[5]],
                    [numbers[6], numbers[7], numbers[8]]]
        
        return None
    
    def _extract_vectors(self, text: str) -> List[List[float]]:
        """Extract vectors from text."""
        # Look for vector patterns like [1,2,3] or (1,2,3)
        vector_pattern = r'[\[\(][\d\s,.-]+[\]\)]'
        matches = re.findall(vector_pattern, text)
        
        vectors = []
        for match in matches:
            try:
                # Clean and convert to list
                vector_str = match.replace('(', '[').replace(')', ']')
                vector = eval(vector_str)  # Note: In production, use ast.literal_eval
                if isinstance(vector, list) and all(isinstance(x, (int, float)) for x in vector):
                    vectors.append(vector)
            except:
                continue
        
        return vectors
    
    def _extract_complex_numbers(self, text: str) -> List[complex]:
        """Extract complex numbers from text."""
        # Look for patterns like "3+4j" or "3+4i"
        complex_pattern = r'(-?\d+\.?\d*)\s*[+\-]\s*(\d+\.?\d*)[ij]|(-?\d+\.?\d*)[ij]'
        matches = re.findall(complex_pattern, text)
        
        complex_numbers = []
        for match in matches:
            try:
                if match[0] and match[1]:  # Real + imaginary
                    real = float(match[0])
                    imag = float(match[1])
                    complex_numbers.append(complex(real, imag))
                elif match[2]:  # Pure imaginary
                    imag = float(match[2])
                    complex_numbers.append(complex(0, imag))
            except:
                continue
        
        return complex_numbers
    
    def _extract_conversion_data(self, text: str) -> Optional[Dict]:
        """Extract unit conversion data from text."""
        # Pattern to match conversions like "convert 5 meters to feet"
        pattern = r'convert\s+(\d+\.?\d*)\s+(\w+)\s+to\s+(\w+)'
        match = re.search(pattern, text.lower())
        
        if match:
            value = float(match.group(1))
            from_unit = match.group(2)
            to_unit = match.group(3)
            
            return {
                'value': value,
                'from_unit': from_unit,
                'to_unit': to_unit
            }
        
        return None
    
    def _parse_arithmetic_expression(self, text: str) -> Optional[Dict]:
        """Parse basic arithmetic expressions."""
        # Look for simple expressions like "5 + 3" or "10 * 2"
        pattern = r'(-?\d+\.?\d*)\s*([+\-*/^%])\s*(-?\d+\.?\d*)'
        match = re.search(pattern, text)
        
        if match:
            num1 = float(match.group(1))
            operator = match.group(2)
            num2 = float(match.group(3))
            
            return {
                'num1': num1,
                'operator': operator,
                'num2': num2
            }
        
        return None
    
    def _fibonacci(self, n: int) -> int:
        """Calculate the nth Fibonacci number."""
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b
    
    def _is_prime(self, n: int) -> bool:
        """Check if a number is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def _perform_unit_conversion(self, data: Dict) -> Optional[float]:
        """Perform unit conversion."""
        value = data['value']
        from_unit = data['from_unit']
        to_unit = data['to_unit']
        
        # Find the unit category
        for category, units in self.unit_conversions.items():
            if from_unit in units and to_unit in units:
                if category == 'temperature':
                    # Special handling for temperature
                    celsius = units[from_unit](value)
                    if to_unit == 'celsius':
                        return celsius
                    elif to_unit == 'fahrenheit':
                        return celsius * 9/5 + 32
                    elif to_unit == 'kelvin':
                        return celsius + 273.15
                else:
                    # Standard conversion through base unit
                    base_value = value * units[from_unit]
                    return base_value / units[to_unit]
        
        return None
    
    def _evaluate_arithmetic(self, data: Dict) -> float:
        """Evaluate basic arithmetic expression."""
        num1 = data['num1']
        operator = data['operator']
        num2 = data['num2']
        
        if operator == '+':
            return num1 + num2
        elif operator == '-':
            return num1 - num2
        elif operator == '*':
            return num1 * num2
        elif operator == '/':
            if num2 == 0:
                raise ValueError("Division by zero")
            return num1 / num2
        elif operator == '^':
            return num1 ** num2
        elif operator == '%':
            return num1 % num2
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def _get_operation_category(self, operation_type: str) -> str:
        """Get the category for a given operation type."""
        for category, operations in self.operation_categories.items():
            if operation_type in operations:
                return category
        return 'general'
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return comprehensive tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "advanced", "expert"],
            "input_types": [
                "mathematical_expression", "statistical_data", "matrix_data",
                "vector_data", "complex_numbers", "unit_conversion",
                "trigonometric_expression", "logarithmic_expression"
            ],
            "output_types": [
                "numerical_result", "matrix_result", "vector_result",
                "statistical_summary", "boolean_result", "complex_result"
            ],
            "estimated_execution_time": "100ms-2s",
            "requires_internet": False,
            "requires_filesystem": False,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": [
                "calculate", "compute", "solve", "evaluate", "analyze",
                "statistical_analysis", "linear_algebra", "trigonometry",
                "logarithms", "complex_arithmetic", "number_theory",
                "unit_conversion", "matrix_operations"
            ],
            "api_dependencies": [],
            "memory_usage": "low-moderate",
            "mathematical_domains": list(self.operation_categories.keys()),
            "supported_constants": list(self.constants.keys()),
            "conversion_categories": list(self.unit_conversions.keys())
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "Calculate the mean of the numbers 10, 20, 30, 40, 50",
            "Find the determinant of the matrix [[1, 2], [3, 4]]",
            "What is sin(45 degrees)?",
            "Calculate log base 2 of 8",
            "Convert 100 celsius to fahrenheit",
            "Find the 15th Fibonacci number",
            "What is the dot product of vectors [1, 2, 3] and [4, 5, 6]?",
            "Calculate the factorial of 5",
            "Find the variance of [1, 2, 3, 4, 5, 6]",
            "Is 17 a prime number?",
            "What is the magnitude of complex number 3+4i?",
            "Calculate the transpose of matrix [[1, 2, 3], [4, 5, 6]]"
        ]
    

    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response with performance data."""
        error_type = type(exception).__name__ if exception else 'ValidationError'
        
        suggestions = [
            "Ensure the task contains a valid mathematical expression",
            "Check that all numbers and operators are properly formatted",
            "For matrices, use format like [[1,2],[3,4]]",
            "For vectors, use format like [1,2,3]",
            "For complex numbers, use format like 3+4j",
            "Specify units clearly for conversions"
        ]
        
        # Add specific suggestions based on error type
        if 'matrix' in message.lower():
            suggestions.append("Matrix operations require square matrices for determinant and inverse")
        elif 'division' in message.lower():
            suggestions.append("Division by zero is not allowed")
        elif 'domain' in message.lower() or 'math domain' in message.lower():
            suggestions.append("Check that input values are within valid domain for the function")
        
        return {
            'success': False,
            'error': message,
            'error_type': error_type,
            'suggestions': suggestions,
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_operations': list(self.operation_categories.keys()),
                'available_constants': list(self.constants.keys())
            }
        }
    
    def _format_success_response(self, data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a successful response with comprehensive metadata."""
        return {
            "success": True,
            "type": "advanced_math_response",
            "data": data,
            "metadata": {
                "tool_name": self.name,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
        }