"""Centralized mock management for Urarovite tests.

This module provides a high-level interface for managing mocks across
different test scenarios, reducing boilerplate and ensuring consistency.
"""

from contextlib import contextmanager
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional, List, ContextManager
from .fixtures import (
    MockPatches,
    create_mock_spreadsheet,
    create_mock_validator,
    create_mock_duplicate_result,
    mock_successful_auth,
)


class MockManager:
    """High-level mock management for common test scenarios."""

    def __init__(self):
        self._active_patches = []

    @contextmanager
    def validation_scenario(
        self,
        validator_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        auth_success: bool = True,
        duplicate_success: bool = True,
        duplicate_error: Optional[str] = None,
    ):
        """Set up a complete validation test scenario.

        Args:
            validator_configs: Dict of validator_id -> config for mock validators
            auth_success: Whether authentication should succeed
            duplicate_success: Whether duplicate creation should succeed

        Example:
            with mock_manager.validation_scenario({
                "empty_cells": {"fixes_applied": 3},
                "duplicate_rows": {"flags_found": 2}
            }) as mocks:
                result = execute_validation(...)
        """
        # Default validator configs
        if validator_configs is None:
            validator_configs = {"empty_cells": {"fixes_applied": 3, "flags_found": 0}}

        with (
            MockPatches.auth_service() as mock_auth,
            MockPatches.validator_registry() as mock_registry,
            MockPatches.pre_validation_duplicate() as mock_duplicate,
        ):
            # Set up auth
            if auth_success:
                mock_auth.return_value = mock_successful_auth()
            else:
                mock_auth.side_effect = Exception("Auth failed")

            # Set up validators
            validators = {}
            for validator_id, config in validator_configs.items():
                validators[validator_id] = create_mock_validator(**config)
            mock_registry.return_value = validators

            # Set up duplicate creation
            mock_duplicate.return_value = create_mock_duplicate_result(
                success=duplicate_success, error=duplicate_error
            )

            yield {
                "auth": mock_auth,
                "registry": mock_registry,
                "duplicate": mock_duplicate,
                "validators": validators,
            }

    @contextmanager
    def spreadsheet_scenario(
        self,
        source_sheets: Optional[List[str]] = None,
        target_sheets: Optional[List[str]] = None,
        sheet_data: Optional[Dict[str, List[List[Any]]]] = None,
    ):
        """Set up a spreadsheet conversion test scenario.

        Args:
            source_sheets: List of sheet names in source
            target_sheets: List of sheet names in target
            sheet_data: Dict of sheet_name -> data for sheets

        Example:
            with mock_manager.spreadsheet_scenario(
                source_sheets=["Sheet1", "Sheet2"],
                sheet_data={"Sheet1": [["A1", "B1"]]}
            ) as mocks:
                result = convert_google_sheets_to_excel(...)
        """
        # Defaults
        if source_sheets is None:
            source_sheets = ["Sheet1"]
        if target_sheets is None:
            target_sheets = ["Sheet"]
        if sheet_data is None:
            sheet_data = {"Sheet1": [["A1", "B1"]]}

        with (
            MockPatches.spreadsheet_factory() as mock_factory,
            MockPatches.convert_spreadsheet_format() as mock_convert,
            patch(
                "urarovite.auth.google_sheets.create_sheets_service_from_encoded_creds"
            ) as mock_auth_service,
        ):
            # Set up auth service mock with Google Sheets API methods
            mock_sheets_service = Mock()
            mock_sheets_service.spreadsheets.return_value.values.return_value.batchUpdate.return_value.execute.return_value = {
                "replies": [{"updatedCells": 4}]
            }
            mock_auth_service.return_value = mock_sheets_service

            # Create source mock
            mock_source = create_mock_spreadsheet()
            mock_source.get_metadata.return_value = Mock(sheet_names=source_sheets)

            # Set up sheet data
            if len(source_sheets) == 1:
                sheet_name = source_sheets[0]
                data = sheet_data.get(sheet_name, [["A1"]])
                mock_source.get_sheet_data.return_value = Mock(
                    values=data, sheet_name=sheet_name
                )
            else:
                # Multiple sheets - use side_effect
                sheet_data_mocks = []
                for sheet_name in source_sheets:
                    data = sheet_data.get(sheet_name, [["A1"]])
                    sheet_data_mocks.append(Mock(values=data, sheet_name=sheet_name))
                mock_source.get_sheet_data.side_effect = sheet_data_mocks

            # Create target mock
            mock_target = create_mock_spreadsheet()
            mock_target.get_metadata.return_value = Mock(sheet_names=target_sheets)

            mock_factory.side_effect = [mock_source, mock_target]

            # Set up conversion mock
            mock_convert.return_value = {
                "success": True,
                "target_path": "https://docs.google.com/spreadsheets/d/converted123/edit",
                "error": None,
            }

            yield {
                "factory": mock_factory,
                "source": mock_source,
                "target": mock_target,
                "convert_spreadsheet_format": mock_convert,
            }

    @contextmanager
    def integration_scenario(
        self,
        validators: Optional[Dict[str, Dict[str, Any]]] = None,
        auth_success: bool = True,
        duplicate_success: bool = True,
        conversion_success: bool = True,
    ):
        """Set up a complete integration test scenario.

        Args:
            validators: Validator configurations
            auth_success: Whether auth should succeed
            duplicate_success: Whether duplication should succeed
            conversion_success: Whether conversion should succeed
        """
        # Default validators
        if validators is None:
            validators = {
                "empty_cells": {"fixes_applied": 3},
                "duplicate_rows": {"flags_found": 2},
            }

        with (
            MockPatches.auth_service() as mock_auth,
            MockPatches.validator_registry() as mock_registry,
            MockPatches.pre_validation_duplicate() as mock_duplicate,
            MockPatches.convert_spreadsheet_format() as mock_convert,
            patch("urarovite.core.api.LocalExcelOptimizer") as mock_optimizer_class,
        ):
            # Set up all mocks
            if auth_success:
                mock_auth.return_value = mock_successful_auth()
            else:
                mock_auth.side_effect = Exception("Auth failed")

            # Set up optimizer mock
            mock_optimizer = Mock()
            mock_optimizer_class.return_value = mock_optimizer

            # Configure optimizer to return success with validation results
            total_fixes = sum(v.get("fixes_applied", 0) for v in validators.values())
            total_flags = sum(v.get("flags_found", 0) for v in validators.values())

            mock_optimizer.optimize_excel_workflow.return_value = {
                "success": True,
                "working_path": "/tmp/working_file.xlsx",
                "final_output": "/tmp/working_file.xlsx",
                "validation_results": {
                    "fixes_applied": total_fixes,
                    "flags_flagged": total_flags,
                    "errors": [],
                    "automated_logs": [f"Applied {total_fixes} fixes"],
                    "processing_time": 0.3,
                },
                "conversion_info": None,
                "performance_metrics": {
                    "total_time_seconds": 0.5,
                    "optimization_ratio": 2.5,
                    "optimization_enabled": True,
                    "api_calls_saved": 4,
                    "efficiency_gain": "4x faster",
                },
                "error": None,
            }

            # Validators
            validator_mocks = {}
            for validator_id, config in validators.items():
                validator_mocks[validator_id] = create_mock_validator(**config)
            mock_registry.return_value = validator_mocks

            # Duplication
            mock_duplicate.return_value = create_mock_duplicate_result(
                success=duplicate_success
            )

            # Conversion
            mock_convert.return_value = {
                "success": conversion_success,
                "output_path": "/tmp/converted.xlsx" if conversion_success else None,
                "error": None if conversion_success else "Conversion failed",
            }

            yield {
                "auth": mock_auth,
                "registry": mock_registry,
                "duplicate": mock_duplicate,
                "convert": mock_convert,
                "validators": validator_mocks,
            }


# Global instance for easy access
mock_manager = MockManager()


# Convenience decorators using the mock manager
def with_validation_mocks(
    validator_configs=None, auth_success=True, duplicate_success=True
):
    """Decorator for validation tests."""

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with mock_manager.validation_scenario(
                validator_configs, auth_success, duplicate_success
            ) as mocks:
                return test_func(*args, mocks=mocks, **kwargs)

        return wrapper

    return decorator


def with_spreadsheet_mocks(source_sheets=None, target_sheets=None, sheet_data=None):
    """Decorator for spreadsheet tests."""

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with mock_manager.spreadsheet_scenario(
                source_sheets, target_sheets, sheet_data
            ) as mocks:
                return test_func(*args, mocks=mocks, **kwargs)

        return wrapper

    return decorator


def with_integration_mocks(**scenario_kwargs):
    """Decorator for integration tests."""

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with mock_manager.integration_scenario(**scenario_kwargs) as mocks:
                return test_func(*args, mocks=mocks, **kwargs)

        return wrapper

    return decorator
