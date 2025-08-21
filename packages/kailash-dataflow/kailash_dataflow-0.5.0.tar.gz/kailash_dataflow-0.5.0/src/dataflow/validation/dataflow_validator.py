"""DataFlow Validator Module."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ValidationSeverity(Enum):
    """Severity levels for validation suggestions."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationSuggestion:
    """A validation suggestion for improving data or operations."""

    field: str
    message: str
    severity: ValidationSeverity
    suggestion: str
    rule_type: Optional[str] = None
    current_value: Optional[Any] = None
    suggested_value: Optional[Any] = None


from typing import Any, Dict, List, Optional


class DataFlowValidator:
    """Validates data and operations in DataFlow."""

    def __init__(self):
        self.validators: Dict[str, List[Callable]] = {}

    def add_validator(
        self,
        field_name: str,
        validator: Callable[[Any], bool],
        error_message: str = "Validation failed",
    ):
        """Add a validator for a field."""
        if field_name not in self.validators:
            self.validators[field_name] = []

        self.validators[field_name].append(
            {"validator": validator, "error_message": error_message}
        )

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate data against registered validators."""
        errors = {}

        for field_name, field_validators in self.validators.items():
            if field_name not in data:
                continue

            field_value = data[field_name]
            field_errors = []

            for validator_info in field_validators:
                try:
                    if not validator_info["validator"](field_value):
                        field_errors.append(validator_info["error_message"])
                except Exception as e:
                    field_errors.append(f"Validation error: {str(e)}")

            if field_errors:
                errors[field_name] = field_errors

        return errors

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        pattern = r"^\+?1?\d{9,15}$"
        return bool(re.match(pattern, phone))

    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        pattern = r"^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$"
        return bool(re.match(pattern, url))

    def validate_sql_injection(self, value: str) -> bool:
        """Check for potential SQL injection patterns."""
        dangerous_patterns = [
            r"(^|\s)(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s",
            r"(;|--|\*|\/\*|\*\/|xp_|sp_)",
            r"(UNION\s+ALL|UNION\s+SELECT)",
            r"(OR\s+1\s*=\s*1|AND\s+1\s*=\s*1)",
        ]

        value_upper = value.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, value_upper):
                return False

        return True


class DataFlowValidationError(Exception):
    """Raised when validation fails."""

    pass


class ValidationRule:
    """A validation rule."""

    def __init__(self, field: str, rule_type: str, value: Any = None):
        self.field = field
        self.rule_type = rule_type
        self.value = value

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data against rule."""
        if self.field not in data:
            return self.rule_type == "optional"

        field_value = data[self.field]

        if self.rule_type == "required":
            return field_value is not None
        elif self.rule_type == "type":
            return isinstance(field_value, self.value)
        elif self.rule_type == "min":
            return field_value >= self.value
        elif self.rule_type == "max":
            return field_value <= self.value
        elif self.rule_type == "pattern":
            return bool(re.match(self.value, str(field_value)))

        return True


class DataFlowValidator:
    """Validates DataFlow operations."""

    def __init__(self):
        self.rules = []

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule."""
        self.rules.append(rule)

    def validate(self, data: Dict[str, Any]):
        """Validate data against all rules."""
        for rule in self.rules:
            if not rule.validate(data):
                raise DataFlowValidationError(
                    f"Validation failed for field '{rule.field}' with rule '{rule.rule_type}'"
                )
