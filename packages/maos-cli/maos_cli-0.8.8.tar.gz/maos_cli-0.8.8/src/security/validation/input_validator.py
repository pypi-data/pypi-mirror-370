"""Comprehensive input validation and sanitization."""

import re
import logging
import html
import json
from typing import Any, Dict, List, Optional, Union, Pattern, Callable
from dataclasses import dataclass
from enum import Enum
import bleach

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Input validation error."""
    pass


class ValidationSeverity(Enum):
    """Validation error severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationRule:
    """Input validation rule."""
    name: str
    pattern: Optional[Union[str, Pattern]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_chars: Optional[str] = None
    forbidden_chars: Optional[str] = None
    custom_validator: Optional[Callable[[str], bool]] = None
    required: bool = False
    severity: ValidationSeverity = ValidationSeverity.MEDIUM
    error_message: str = "Validation failed"


class InputValidator:
    """Comprehensive input validator with security focus."""
    
    def __init__(self):
        # Common validation patterns
        self.patterns = {
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'username': re.compile(r'^[a-zA-Z0-9_-]{3,50}$'),
            'password': re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'),
            'agent_id': re.compile(r'^[a-zA-Z0-9_-]{1,100}$'),
            'task_id': re.compile(r'^[a-zA-Z0-9_-]{1,100}$'),
            'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'),
            'ip_address': re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'),
            'jwt_token': re.compile(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$'),
            'api_key': re.compile(r'^maos_key_[A-Za-z0-9_-]{32,}$')
        }
        
        # Dangerous patterns to detect
        self.dangerous_patterns = {
            'sql_injection': [
                re.compile(r"('|(\\')|(;)|(\\)|(\-\-)|(%27)|(%3D)|(\')|(\'))", re.IGNORECASE),
                re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b", re.IGNORECASE)
            ],
            'xss': [
                re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
                re.compile(r"javascript:", re.IGNORECASE),
                re.compile(r"on\w+\s*=", re.IGNORECASE),
                re.compile(r"<iframe[^>]*>", re.IGNORECASE)
            ],
            'path_traversal': [
                re.compile(r"\.\./"),
                re.compile(r"\.\.\\"),
                re.compile(r"%2e%2e%2f", re.IGNORECASE),
                re.compile(r"~[/\\]")
            ],
            'command_injection': [
                re.compile(r"[;&|`]"),
                re.compile(r"\$\(.*\)"),
                re.compile(r"`.*`")
            ]
        }
        
        # Predefined validation rules
        self.rules = {
            'email': ValidationRule(
                name="email",
                pattern=self.patterns['email'],
                max_length=255,
                error_message="Invalid email format"
            ),
            'username': ValidationRule(
                name="username", 
                pattern=self.patterns['username'],
                min_length=3,
                max_length=50,
                error_message="Username must be 3-50 alphanumeric characters, hyphens, or underscores"
            ),
            'password': ValidationRule(
                name="password",
                pattern=self.patterns['password'],
                min_length=8,
                max_length=128,
                severity=ValidationSeverity.HIGH,
                error_message="Password must be at least 8 characters with uppercase, lowercase, number, and special character"
            ),
            'agent_id': ValidationRule(
                name="agent_id",
                pattern=self.patterns['agent_id'],
                max_length=100,
                required=True,
                error_message="Invalid agent ID format"
            ),
            'safe_text': ValidationRule(
                name="safe_text",
                max_length=10000,
                forbidden_chars="<>&\"'",
                error_message="Text contains potentially dangerous characters"
            )
        }
        
        # HTML sanitizer
        self.html_sanitizer = bleach.Cleaner(
            tags=[],  # No HTML tags allowed
            attributes={},
            strip=True,
            strip_comments=True
        )
    
    def validate_input(
        self,
        value: Any,
        rule_name: str,
        custom_rules: Optional[List[ValidationRule]] = None
    ) -> Dict[str, Any]:
        """Validate input against rule."""
        try:
            # Convert to string if not already
            str_value = str(value) if value is not None else ""
            
            # Get validation rule
            rule = None
            if custom_rules:
                rule = next((r for r in custom_rules if r.name == rule_name), None)
            if not rule:
                rule = self.rules.get(rule_name)
            
            if not rule:
                return {"valid": False, "error": f"Unknown validation rule: {rule_name}"}
            
            # Check required
            if rule.required and not str_value:
                return {
                    "valid": False,
                    "error": f"{rule.name} is required",
                    "severity": rule.severity.value
                }
            
            # Skip validation for empty optional fields
            if not str_value and not rule.required:
                return {"valid": True}
            
            # Length validation
            if rule.min_length and len(str_value) < rule.min_length:
                return {
                    "valid": False,
                    "error": f"{rule.name} must be at least {rule.min_length} characters",
                    "severity": rule.severity.value
                }
            
            if rule.max_length and len(str_value) > rule.max_length:
                return {
                    "valid": False,
                    "error": f"{rule.name} must be at most {rule.max_length} characters",
                    "severity": rule.severity.value
                }
            
            # Pattern validation
            if rule.pattern:
                pattern = rule.pattern if isinstance(rule.pattern, Pattern) else re.compile(rule.pattern)
                if not pattern.match(str_value):
                    return {
                        "valid": False,
                        "error": rule.error_message,
                        "severity": rule.severity.value
                    }
            
            # Character validation
            if rule.allowed_chars:
                if not all(c in rule.allowed_chars for c in str_value):
                    return {
                        "valid": False,
                        "error": f"{rule.name} contains invalid characters",
                        "severity": rule.severity.value
                    }
            
            if rule.forbidden_chars:
                if any(c in rule.forbidden_chars for c in str_value):
                    return {
                        "valid": False,
                        "error": f"{rule.name} contains forbidden characters",
                        "severity": rule.severity.value
                    }
            
            # Custom validation
            if rule.custom_validator:
                if not rule.custom_validator(str_value):
                    return {
                        "valid": False,
                        "error": rule.error_message,
                        "severity": rule.severity.value
                    }
            
            # Security validation
            security_result = self._check_security_patterns(str_value)
            if not security_result["safe"]:
                return {
                    "valid": False,
                    "error": f"Security violation detected: {security_result['threat_type']}",
                    "severity": ValidationSeverity.CRITICAL.value,
                    "threat_detected": security_result["threat_type"]
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "valid": False,
                "error": f"Validation system error: {str(e)}",
                "severity": ValidationSeverity.HIGH.value
            }
    
    def _check_security_patterns(self, value: str) -> Dict[str, Any]:
        """Check for dangerous security patterns."""
        try:
            for threat_type, patterns in self.dangerous_patterns.items():
                for pattern in patterns:
                    if pattern.search(value):
                        return {
                            "safe": False,
                            "threat_type": threat_type,
                            "pattern": pattern.pattern
                        }
            
            return {"safe": True}
            
        except Exception as e:
            logger.error(f"Security pattern check error: {e}")
            return {"safe": False, "threat_type": "unknown", "error": str(e)}
    
    def validate_json(self, json_str: str, max_depth: int = 10, max_size: int = 1024*1024) -> Dict[str, Any]:
        """Validate JSON input with security checks."""
        try:
            # Size check
            if len(json_str) > max_size:
                return {
                    "valid": False,
                    "error": f"JSON too large (max {max_size} bytes)",
                    "severity": ValidationSeverity.MEDIUM.value
                }
            
            # Parse JSON
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                return {
                    "valid": False,
                    "error": f"Invalid JSON: {str(e)}",
                    "severity": ValidationSeverity.MEDIUM.value
                }
            
            # Depth check (prevent deeply nested objects)
            if self._get_json_depth(data) > max_depth:
                return {
                    "valid": False,
                    "error": f"JSON too deeply nested (max depth {max_depth})",
                    "severity": ValidationSeverity.HIGH.value
                }
            
            # Check for dangerous content in JSON values
            security_result = self._check_json_security(data)
            if not security_result["safe"]:
                return {
                    "valid": False,
                    "error": f"Dangerous content in JSON: {security_result['threat_type']}",
                    "severity": ValidationSeverity.CRITICAL.value,
                    "threat_detected": security_result["threat_type"]
                }
            
            return {"valid": True, "data": data}
            
        except Exception as e:
            logger.error(f"JSON validation error: {e}")
            return {
                "valid": False,
                "error": f"JSON validation system error: {str(e)}",
                "severity": ValidationSeverity.HIGH.value
            }
    
    def _get_json_depth(self, obj, depth=0):
        """Calculate JSON object depth."""
        if isinstance(obj, dict):
            return max([self._get_json_depth(v, depth + 1) for v in obj.values()], default=depth)
        elif isinstance(obj, list):
            return max([self._get_json_depth(item, depth + 1) for item in obj], default=depth)
        else:
            return depth
    
    def _check_json_security(self, obj) -> Dict[str, Any]:
        """Recursively check JSON object for security threats."""
        try:
            if isinstance(obj, str):
                return self._check_security_patterns(obj)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    # Check key
                    key_result = self._check_security_patterns(str(key))
                    if not key_result["safe"]:
                        return key_result
                    
                    # Check value
                    value_result = self._check_json_security(value)
                    if not value_result["safe"]:
                        return value_result
                        
            elif isinstance(obj, list):
                for item in obj:
                    item_result = self._check_json_security(item)
                    if not item_result["safe"]:
                        return item_result
            
            return {"safe": True}
            
        except Exception as e:
            logger.error(f"JSON security check error: {e}")
            return {"safe": False, "threat_type": "unknown", "error": str(e)}
    
    def sanitize_input(self, value: str, sanitization_type: str = "html") -> str:
        """Sanitize input based on type."""
        try:
            if not isinstance(value, str):
                value = str(value)
            
            if sanitization_type == "html":
                # Remove HTML tags and escape entities
                return self.html_sanitizer.clean(html.escape(value))
                
            elif sanitization_type == "sql":
                # Basic SQL injection prevention
                return value.replace("'", "''").replace(";", "").replace("--", "")
                
            elif sanitization_type == "filename":
                # Safe filename
                safe_chars = re.sub(r'[^a-zA-Z0-9._-]', '', value)
                return safe_chars[:255]  # Limit length
                
            elif sanitization_type == "alphanumeric":
                # Only alphanumeric characters
                return re.sub(r'[^a-zA-Z0-9]', '', value)
                
            elif sanitization_type == "whitespace":
                # Normalize whitespace
                return ' '.join(value.split())
                
            else:
                # Default: escape HTML entities
                return html.escape(value)
                
        except Exception as e:
            logger.error(f"Sanitization error: {e}")
            return ""
    
    def validate_batch(
        self,
        inputs: Dict[str, Any],
        rules: Dict[str, str]
    ) -> Dict[str, Any]:
        """Validate multiple inputs at once."""
        try:
            results = {}
            all_valid = True
            errors = []
            
            for field, rule_name in rules.items():
                if field in inputs:
                    result = self.validate_input(inputs[field], rule_name)
                    results[field] = result
                    
                    if not result["valid"]:
                        all_valid = False
                        errors.append(f"{field}: {result['error']}")
                else:
                    # Check if field is required
                    rule = self.rules.get(rule_name)
                    if rule and rule.required:
                        all_valid = False
                        errors.append(f"{field}: Field is required")
                        results[field] = {"valid": False, "error": "Field is required"}
                    else:
                        results[field] = {"valid": True}
            
            return {
                "valid": all_valid,
                "results": results,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Batch validation error: {e}")
            return {
                "valid": False,
                "error": f"Batch validation system error: {str(e)}",
                "severity": ValidationSeverity.HIGH.value
            }
    
    def add_rule(self, rule: ValidationRule):
        """Add custom validation rule."""
        self.rules[rule.name] = rule
    
    def get_rule(self, rule_name: str) -> Optional[ValidationRule]:
        """Get validation rule by name."""
        return self.rules.get(rule_name)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Test basic validation
            test_result = self.validate_input("test@example.com", "email")
            
            return {
                "status": "healthy" if test_result["valid"] else "unhealthy",
                "rules_count": len(self.rules),
                "patterns_count": len(self.patterns),
                "test_validation": test_result
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}