"""
Shared utilities for the uoapi package.

This package contains common utilities and helper functions
used across different parts of the application.
"""

from .patterns import (
    patterns,
    prereq_patterns,
    extract_course_codes,
    extract_subject_code,
    extract_course_number,
    normalize_course_code,
    extract_credits,
    is_valid_course_code,
    # Legacy exports for backward compatibility
    code_re,
    code_groups,
    credit_re,
    subj_re,
    href_re,
    numbers_re,
    prereq,
)

from .config import (
    Config,
    DatabaseConfig,
    CacheConfig,
    ScrapingConfig,
    APIConfig,
    LoggingConfig,
    RMPConfig,
    config,
    get_config,
    reload_config,
)

__all__ = [
    # Patterns
    "patterns",
    "prereq_patterns",
    "extract_course_codes",
    "extract_subject_code",
    "extract_course_number",
    "normalize_course_code",
    "extract_credits",
    "is_valid_course_code",
    # Legacy pattern exports
    "code_re",
    "code_groups",
    "credit_re",
    "subj_re",
    "href_re",
    "numbers_re",
    "prereq",
    # Configuration
    "Config",
    "DatabaseConfig",
    "CacheConfig",
    "ScrapingConfig",
    "APIConfig",
    "LoggingConfig",
    "RMPConfig",
    "config",
    "get_config",
    "reload_config",
]
