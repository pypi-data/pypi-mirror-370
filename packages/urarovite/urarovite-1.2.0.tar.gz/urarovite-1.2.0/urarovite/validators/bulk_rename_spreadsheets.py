from __future__ import annotations
from typing import Any, Dict, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.utils.sheets import bulk_rename_spreadsheets_from_range
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.core.exceptions import ValidationError


class BulkRenameSpreadsheetsValidator(BaseValidator):
    def __init__(self) -> None:
        super().__init__(
            validator_id="bulk_rename_spreadsheets",
            name="Bulk Rename Spreadsheets",
            description="Bulk rename spreadsheet titles from a template range (A=url, B=title)",
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            template_sheet_url = kwargs.get("template_sheet_url")
            a1_range = kwargs.get("range")

            if not template_sheet_url or not a1_range:
                result.add_error("Missing template_sheet_url or range")
                result.set_automated_log("Completed with errors")
                result.add_issue(1)
                return

            # For now, we still need the sheets_service for the bulk rename utility
            # TODO: Update bulk_rename_spreadsheets_from_range to use abstraction layer
            try:
                sheets_service = self._create_sheets_service(auth_credentials)
            except ValidationError as e:
                result.add_error(str(e))
                return

            op = bulk_rename_spreadsheets_from_range(
                sheets_service=sheets_service,
                template_spreadsheet_url=template_sheet_url,
                range=a1_range,
            )

            if not op.get("success", False):
                failures = op.get("failures", [])
                if failures:
                    result.add_issue(len(failures))

                    for failure in failures:
                        result.add_error(failure.get("error", "operation_failed"))
                else:
                    result.add_error(str(op.get("error", "operation_failed")))
                result.set_automated_log("Completed with errors")
            else:
                renamed = int(op["renamed"]) if op.get("renamed") is not None else 0
                if renamed == 0:
                    result.set_automated_log("No rows processed")
                else:
                    result.add_fix(renamed)
                    result.set_automated_log("Renamed successfully")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )


def run(
    sheets_service: Any,
    template_sheet_url: str,
    range: str,
) -> Dict[str, Any]:
    """Backward compatibility function for the old interface."""
    v = BulkRenameSpreadsheetsValidator()
    return v.validate(
        spreadsheet_source="",  # Not used by this validator
        mode="fix",
        auth_credentials=None,  # No auth for backward compatibility
        template_sheet_url=template_sheet_url,
        range=range,
    )
