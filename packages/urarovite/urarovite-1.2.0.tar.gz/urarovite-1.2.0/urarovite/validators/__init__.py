"""Validation modules for the Urarovite library.

This module provides all available validators and a registry system
for managing and accessing them.
"""

from typing import Dict

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.validators.data_quality_updated import (
    EmptyCellsValidatorUpdated as EmptyCellsValidator,
    TabNameValidatorUpdated as TabNameValidator,
)
from urarovite.validators.empty_invalid_ranges import EmptyInvalidRangesValidator
from urarovite.validators.format_validation import (
    VerificationRangesValidator,
)
from urarovite.validators.bulk_rename_spreadsheets import (
    BulkRenameSpreadsheetsValidator,
)
from urarovite.validators.spreadsheet_differences import SpreadsheetDifferencesValidator
from urarovite.validators.tab_name_consistency_fixed import (
    TabNameConsistencyValidator,
)
from urarovite.validators.open_ended_ranges import OpenEndedRangesValidator
from urarovite.validators.sheet_name_quoting import SheetNameQuotingValidator
from urarovite.validators.sheet_accessibility import SheetAccessibilityValidator
from urarovite.validators.identical_outside_ranges import (
    IdenticalOutsideRangesValidator,
)
from urarovite.validators.tab_name_case_collisions import TabNameCaseCollisionsValidator
from urarovite.validators.volatile_formulas import VolatileFormulasValidator
from urarovite.validators.different_within_ranges import DifferentWithinRangesValidator
from urarovite.validators.csv_to_json_transform import CSVToJSONTransformValidator
from urarovite.validators.platform_neutralizer import PlatformNeutralizerValidator
from urarovite.validators.attached_files_cleaner import AttachedFilesCleanerValidator
from urarovite.validators.hidden_unicode import HiddenUnicodeValidator
from urarovite.validators.no_correct_answers import NoCorrectAnswersValidator
from urarovite.validators.whitespace_diff import WhitespaceDiffValidator
from urarovite.validators.cell_value_validation import CellValueValidationValidator
from urarovite.validators.duplicate_overlapping_ranges import (
    DuplicateOverlappingRangesValidator,
)
from urarovite.validators.numeric_rounding_validator import NumericRoundingValidator
from urarovite.validators.unique_id_validator import UniqueIDValidator

# Registry of all available validators
_VALIDATOR_REGISTRY: Dict[str, BaseValidator] = {}


def _initialize_registry() -> None:
    """Initialize the validator registry with all available validators."""
    global _VALIDATOR_REGISTRY

    if _VALIDATOR_REGISTRY:
        return  # Already initialized

    # Data quality validators
    _VALIDATOR_REGISTRY["empty_cells"] = EmptyCellsValidator()
    _VALIDATOR_REGISTRY["tab_names"] = TabNameValidator()

    # Format validation validators

    # Spreadsheet comparison validators
    _VALIDATOR_REGISTRY["tab_name_consistency"] = TabNameConsistencyValidator()
    _VALIDATOR_REGISTRY["open_ended_ranges"] = OpenEndedRangesValidator()
    _VALIDATOR_REGISTRY["invalid_verification_ranges"] = VerificationRangesValidator()

    # Spreadsheet range validators
    _VALIDATOR_REGISTRY["sheet_name_quoting"] = SheetNameQuotingValidator()

    _VALIDATOR_REGISTRY["bulk_rename_spreadsheets"] = BulkRenameSpreadsheetsValidator()
    # Spreadsheet differences validator
    _VALIDATOR_REGISTRY["spreadsheet_differences"] = SpreadsheetDifferencesValidator()

    # Sheet accessibility validator
    _VALIDATOR_REGISTRY["sheet_accessibility"] = SheetAccessibilityValidator()

    _VALIDATOR_REGISTRY["identical_outside_ranges"] = IdenticalOutsideRangesValidator()
    _VALIDATOR_REGISTRY["different_within_ranges"] = DifferentWithinRangesValidator()

    # Empty/invalid ranges validator
    _VALIDATOR_REGISTRY["empty_invalid_ranges"] = EmptyInvalidRangesValidator()

    # Labeling aid validators
    _VALIDATOR_REGISTRY["platform_neutralizer"] = PlatformNeutralizerValidator()
    _VALIDATOR_REGISTRY["attached_files_cleaner"] = AttachedFilesCleanerValidator()

    # CSV to JSON transform validator
    _VALIDATOR_REGISTRY["csv_to_json_transform"] = CSVToJSONTransformValidator()

    # Tab name case collisions validator
    _VALIDATOR_REGISTRY["tab_name_case_collisions"] = TabNameCaseCollisionsValidator()

    # Volatile formulas validator
    _VALIDATOR_REGISTRY["volatile_formulas"] = VolatileFormulasValidator()

    # Hidden Unicode validator
    _VALIDATOR_REGISTRY["hidden_unicode"] = HiddenUnicodeValidator()

    # No correct answers validator
    _VALIDATOR_REGISTRY["no_correct_answers"] = NoCorrectAnswersValidator()
    # Whitespace difference validator
    _VALIDATOR_REGISTRY["whitespace_diff"] = WhitespaceDiffValidator()
    # Cell Value Validation validator
    _VALIDATOR_REGISTRY["cell_value_validation"] = CellValueValidationValidator()
    # Duplicate and overlapping ranges validator
    _VALIDATOR_REGISTRY["duplicate_overlapping_ranges"] = (
        DuplicateOverlappingRangesValidator()
    )
    # Numeric Rounding validator
    _VALIDATOR_REGISTRY["numeric_rounding"] = NumericRoundingValidator()
    # Unique ID properties validator
    _VALIDATOR_REGISTRY["unique_id_properties"] = UniqueIDValidator()


def get_validator_registry() -> Dict[str, BaseValidator]:
    """Get the registry of all available validators.

    Returns:
        Dictionary mapping validator IDs to validator instances
    """
    _initialize_registry()
    return _VALIDATOR_REGISTRY.copy()


def get_validator(validator_id: str) -> BaseValidator:
    """Get a specific validator by ID.

    Args:
        validator_id: The ID of the validator to retrieve

    Returns:
        The validator instance

    Raises:
        KeyError: If validator ID is not found
    """
    _initialize_registry()
    return _VALIDATOR_REGISTRY[validator_id]


# Initialize registry on import
_initialize_registry()

__all__ = [
    # Base classes
    "BaseValidator",
    "ValidationResult",
    # Data quality validators
    "EmptyCellsValidator",
    "TabNameValidator",
    # Format validation validators
    # Spreadsheet comparison validators
    "TabNameConsistencyValidator",
    "OpenEndedRangesValidator",
    "VerificationRangesValidator",
    "BulkRenameSpreadsheetsValidator",
    # Spreadsheet differences validator
    "SpreadsheetDifferencesValidator",
    # Spreadsheet range validators
    "SheetNameQuotingValidator",
    # Sheet accessibility validator
    "SheetAccessibilityValidator",
    "IdenticalOutsideRangesValidator",
    "DifferentWithinRangesValidator",
    # Labeling aid validators
    "PlatformNeutralizerValidator",
    "AttachedFilesCleanerValidator",
    # Empty/invalid ranges validator
    "EmptyInvalidRangesValidator",
    # Registry functions
    "get_validator_registry",
    "get_validator",
    # CSV to JSON transform validator
    "CSVToJSONTransformValidator",
    # Validator registry
    "TabNameCaseCollisionsValidator",
    # Volatile formulas validator
    "VolatileFormulasValidator",
    # Hidden Unicode validator
    "HiddenUnicodeValidator",
    # No correct answers validator
    "NoCorrectAnswersValidator",
    # Whitespace difference validator
    "WhitespaceDiffValidator",
    # Cell Value Validation validator
    "CellValueValidationValidator",
    # Duplicate and Overlapping Ranges validator
    "DuplicateOverlappingRangesValidator",
    # Numeric Rounding validator
    "NumericRoundingValidator",
    # Unique ID properties validator
    "UniqueIDValidator",
]
