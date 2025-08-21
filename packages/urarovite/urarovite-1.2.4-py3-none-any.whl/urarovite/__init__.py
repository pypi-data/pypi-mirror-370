"""Urarovite - A Google Sheets validation library.

This library provides main functions for integrating with batch processing systems:
- get_available_validation_criteria(): Returns all supported validation checks
- execute_validation(): Executes a single validation check on Google Sheets
- execute_all_validations(): Executes multiple validation checks with shared duplicate
- crawl_and_validate_sheets(): Crawls metadata sheet and validates all referenced sheets

Example usage:
    from urarovite import get_available_validation_criteria, execute_validation, execute_all_validations, crawl_and_validate_sheets

    # Get available validation options
    criteria = get_available_validation_criteria()

    # Execute single validation
    result = execute_validation({"id": "empty_cells", "mode": "fix"}, sheet_url, auth_secret)

    # Execute multiple validations efficiently
    checks = [
        {"id": "empty_cells", "mode": "fix"}
    ]
    result = execute_all_validations(
        checks,
        sheet_url,
        auth_secret
    )

    # Crawl and validate all sheets from metadata
    result = crawl_and_validate_sheets(metadata_sheet_url, auth_secret)
"""

# Main API functions (required by Uvarolite system)
from urarovite.core.api import (
    get_available_validation_criteria,
    execute_validation,
    execute_all_validations,
    crawl_and_validate_sheets,
)

# Core modules for advanced usage
from urarovite import core, auth, validators, utils, config

# Version is now managed by hatch-vcs from Git tags
try:
    from urarovite._version import __version__
except ImportError:
    # Fallback for development installs without build
    __version__ = "dev"

__all__ = [
    # Main API functions
    "get_available_validation_criteria",
    "execute_validation",
    "execute_all_validations",
    "crawl_and_validate_sheets",
    # Core modules
    "core",
    "auth",
    "validators",
    "utils",
    "config",
]
