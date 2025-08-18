"""
Validation Tool - MCP-compliant data validation and verification.

Provides comprehensive validation capabilities for various data types,
formats, and business rules.
"""

import re
import json
import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
from ..base import BaseTool


class ValidationTool(BaseTool):
    """
    Tool for data validation and verification operations.
    
    This tool demonstrates MCP architecture:
    - Stateless operation
    - No LLM dependencies
    - Structured input/output
    - Comprehensive validation rules
    """
    
    def __init__(self):
        """Initialize validation tool."""
        self.name = "Validation"
        self.description = "Validate data formats, types, and business rules"
        self.supported_validations = [
            "email", "url", "phone", "date", "json", "xml", "csv",
            "credit_card", "ssn", "zip_code", "ip_address", "uuid"
        ]
    
    def can_handle(self, task: str) -> bool:
        """Check if task is a validation operation."""
        if not task or not task.strip():
            return False
        
        task_lower = task.lower().strip()
        
        # Validation keywords
        validation_keywords = [
            "validate", "verify", "check", "confirm", "test", "ensure",
            "valid", "invalid", "correct", "incorrect", "format", "pattern"
        ]
        
        # Data type keywords
        data_type_keywords = [
            "email", "url", "phone", "date", "json", "xml", "csv",
            "credit card", "ssn", "zip", "ip", "uuid", "number",
            "string", "boolean", "array", "object"
        ]
        
        # Check for validation keywords
        if any(keyword in task_lower for keyword in validation_keywords):
            return True
        
        # Check for data type keywords
        if any(keyword in task_lower for keyword in data_type_keywords):
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute validation operation."""
        if not task or not task.strip():
            return self._format_error_response(
                "Task cannot be empty",
                "INVALID_INPUT",
                ["Provide a validation request"]
            )
        
        try:
            task_lower = task.lower().strip()
            data_input = kwargs.get("data") or kwargs.get("value") or kwargs.get("input", "")
            
            # Determine validation type
            if "email" in task_lower:
                return self._validate_email(data_input, **kwargs)
            elif "url" in task_lower:
                return self._validate_url(data_input, **kwargs)
            elif "phone" in task_lower:
                return self._validate_phone(data_input, **kwargs)
            elif "date" in task_lower:
                return self._validate_date(data_input, **kwargs)
            elif "json" in task_lower:
                return self._validate_json(data_input, **kwargs)
            elif "number" in task_lower:
                return self._validate_number(data_input, **kwargs)
            elif "pattern" in task_lower or "regex" in task_lower:
                return self._validate_pattern(data_input, **kwargs)
            else:
                return self._validate_generic(data_input, **kwargs)
                
        except Exception as e:
            return self._format_error_response(
                f"Validation failed: {str(e)}",
                "VALIDATION_ERROR",
                ["Check input data and validation parameters"]
            )
    
    def _validate_email(self, email: str, **kwargs) -> Dict[str, Any]:
        """Validate email address format."""
        if not email or not isinstance(email, str):
            return self._format_validation_response(
                "email", email, False, "Empty or invalid email input"
            )
        
        email = email.strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(email_pattern, email))
        
        details = {
            "email": email,
            "is_valid": is_valid,
            "has_at_symbol": "@" in email,
            "has_domain": "." in email.split("@")[-1] if "@" in email else False,
            "valid_length": 5 <= len(email) <= 254
        }
        
        return self._format_validation_response(
            "email", email, is_valid, 
            "Valid email format" if is_valid else "Invalid email format",
            details
        )
    
    def _validate_url(self, url: str, **kwargs) -> Dict[str, Any]:
        """Validate URL format."""
        if not url or not isinstance(url, str):
            return self._format_validation_response(
                "url", url, False, "Empty or invalid URL input"
            )
        
        url = url.strip()
        
        try:
            parsed = urlparse(url)
            is_valid = all([
                parsed.scheme in ['http', 'https', 'ftp', 'ftps'],
                parsed.netloc,
                '.' in parsed.netloc
            ])
            
            details = {
                "url": url,
                "is_valid": is_valid,
                "scheme": parsed.scheme,
                "domain": parsed.netloc,
                "path": parsed.path
            }
            
            return self._format_validation_response(
                "url", url, is_valid,
                "Valid URL format" if is_valid else "Invalid URL format",
                details
            )
            
        except Exception as e:
            return self._format_validation_response(
                "url", url, False, f"URL parsing error: {str(e)}"
            )
    
    def _validate_phone(self, phone: str, **kwargs) -> Dict[str, Any]:
        """Validate phone number format."""
        if not phone or not isinstance(phone, str):
            return self._format_validation_response(
                "phone", phone, False, "Empty or invalid phone input"
            )
        
        phone = phone.strip()
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # US phone number validation
        us_pattern = r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$'
        is_valid = bool(re.match(us_pattern, phone)) or len(cleaned_phone) == 10
        
        details = {
            "phone": phone,
            "cleaned": cleaned_phone,
            "is_valid": is_valid,
            "length": len(cleaned_phone)
        }
        
        return self._format_validation_response(
            "phone", phone, is_valid,
            "Valid phone format" if is_valid else "Invalid phone format",
            details
        )
    
    def _validate_date(self, date_input: str, **kwargs) -> Dict[str, Any]:
        """Validate date format."""
        if not date_input or not isinstance(date_input, str):
            return self._format_validation_response(
                "date", date_input, False, "Empty or invalid date input"
            )
        
        date_input = date_input.strip()
        
        # Common date formats
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
            "%B %d, %Y", "%d %B %Y", "%m-%d-%Y"
        ]
        
        parsed_date = None
        used_format = None
        
        for fmt in formats:
            try:
                parsed_date = datetime.datetime.strptime(date_input, fmt)
                used_format = fmt
                break
            except ValueError:
                continue
        
        is_valid = parsed_date is not None
        
        details = {
            "input": date_input,
            "is_valid": is_valid,
            "parsed_date": parsed_date.isoformat() if parsed_date else None,
            "format_used": used_format
        }
        
        return self._format_validation_response(
            "date", date_input, is_valid,
            "Valid date format" if is_valid else "Invalid date format",
            details
        )
    
    def _validate_json(self, json_input: str, **kwargs) -> Dict[str, Any]:
        """Validate JSON format."""
        if not json_input or not isinstance(json_input, str):
            return self._format_validation_response(
                "json", json_input, False, "Empty or invalid JSON input"
            )
        
        json_input = json_input.strip()
        
        try:
            parsed_json = json.loads(json_input)
            
            details = {
                "input": json_input[:200] + "..." if len(json_input) > 200 else json_input,
                "is_valid": True,
                "type": type(parsed_json).__name__,
                "size": len(json_input)
            }
            
            return self._format_validation_response(
                "json", json_input, True, "Valid JSON format", details
            )
            
        except json.JSONDecodeError as e:
            details = {
                "input": json_input[:200] + "..." if len(json_input) > 200 else json_input,
                "is_valid": False,
                "error": str(e)
            }
            
            return self._format_validation_response(
                "json", json_input, False, f"Invalid JSON: {str(e)}", details
            )
    
    def _validate_number(self, number_input: Union[str, int, float], **kwargs) -> Dict[str, Any]:
        """Validate number format and range."""
        min_value = kwargs.get("min")
        max_value = kwargs.get("max")
        
        try:
            if isinstance(number_input, str):
                number = float(number_input) if '.' in number_input else int(number_input)
            else:
                number = number_input
            
            is_valid = True
            validation_errors = []
            
            if min_value is not None and number < min_value:
                is_valid = False
                validation_errors.append(f"Must be >= {min_value}")
            
            if max_value is not None and number > max_value:
                is_valid = False
                validation_errors.append(f"Must be <= {max_value}")
            
            details = {
                "input": number_input,
                "parsed_number": number,
                "is_valid": is_valid,
                "type": type(number).__name__,
                "validation_errors": validation_errors
            }
            
            return self._format_validation_response(
                "number", number_input, is_valid,
                "Valid number" if is_valid else f"Invalid number: {', '.join(validation_errors)}",
                details
            )
            
        except (ValueError, TypeError) as e:
            return self._format_validation_response(
                "number", number_input, False, f"Cannot parse as number: {str(e)}"
            )
    
    def _validate_pattern(self, data_input: str, **kwargs) -> Dict[str, Any]:
        """Validate data against a regex pattern."""
        pattern = kwargs.get("pattern")
        
        if not pattern:
            return self._format_error_response(
                "No pattern provided for validation",
                "MISSING_PATTERN",
                ["Provide 'pattern' parameter with regex pattern"]
            )
        
        if not data_input or not isinstance(data_input, str):
            return self._format_validation_response(
                "pattern", data_input, False, "Empty or invalid input"
            )
        
        try:
            match = re.match(pattern, data_input)
            is_valid = match is not None
            
            details = {
                "input": data_input,
                "pattern": pattern,
                "is_valid": is_valid,
                "match": match.group() if match else None
            }
            
            return self._format_validation_response(
                "pattern", data_input, is_valid,
                "Matches pattern" if is_valid else "Does not match pattern",
                details
            )
            
        except re.error as e:
            return self._format_error_response(
                f"Invalid regex pattern: {str(e)}",
                "INVALID_PATTERN",
                ["Check regex pattern syntax"]
            )
    
    def _validate_generic(self, data_input: Any, **kwargs) -> Dict[str, Any]:
        """Perform generic validation checks."""
        validations = {
            "is_empty": not bool(data_input),
            "type": type(data_input).__name__,
            "length": len(str(data_input)) if data_input is not None else 0
        }
        
        if isinstance(data_input, str):
            validations.update({
                "is_numeric": data_input.strip().replace('.', '').replace('-', '').isdigit(),
                "is_alphabetic": data_input.strip().replace(' ', '').isalpha(),
                "is_alphanumeric": data_input.strip().replace(' ', '').isalnum()
            })
        
        return self._format_success_response({
            "operation": "generic_validation",
            "input": data_input,
            "validations": validations
        })
    
    def _format_validation_response(self, validation_type: str, input_data: Any, 
                                  is_valid: bool, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a validation response."""
        return self._format_success_response({
            "validation_type": validation_type,
            "input": input_data,
            "is_valid": is_valid,
            "message": message,
            "details": details or {}
        })
    
    def get_examples(self) -> List[str]:
        """Return example validation operations."""
        return [
            "validate email address format",
            "check if URL is valid",
            "verify phone number format",
            "validate date format",
            "check JSON syntax",
            "validate number in range",
            "verify pattern match",
            "check data type"
        ]
    
    def _format_success_response(self, data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a successful response."""
        return {
            "success": True,
            "type": "validation_response",
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
