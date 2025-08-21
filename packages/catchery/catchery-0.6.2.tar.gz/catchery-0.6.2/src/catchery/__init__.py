"""
Catchery is a Python library for building robust and scalable applications.
"""

from .error_handler import (
    AppError,
    ErrorHandler,
    ErrorSeverity,
    get_default_handler,
    log_critical,
    log_error,
    log_info,
    log_warning,
    re_raise_chained,
    safe_operation,
    set_default_handler,
    setup_catchery_logging,
)
from .validation import (
    ensure_enum,
    ensure_int_in_range,
    ensure_list_of_type,
    ensure_non_negative_int,
    ensure_object,
    ensure_string,
    safe_get_attribute,
    validate_object,
    validate_type,
)

__all__ = [
    "AppError",
    "ErrorHandler",
    "ErrorSeverity",
    "get_default_handler",
    "log_critical",
    "log_error",
    "log_info",
    "log_warning",
    "re_raise_chained",
    "safe_operation",
    "set_default_handler",
    "setup_catchery_logging",
    # Validation functions.
    "ensure_enum",
    "ensure_int_in_range",
    "ensure_list_of_type",
    "ensure_non_negative_int",
    "ensure_object",
    "ensure_string",
    "safe_get_attribute",
    "validate_object",
    "validate_type",
]
