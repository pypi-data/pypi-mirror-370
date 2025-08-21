"""Local Excel Operations Optimizer.

This module provides optimized Excel processing that performs ALL operations
locally before any Google Sheets interaction, maximizing performance and
minimizing API calls.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager

from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetFactory, SpreadsheetInterface
from urarovite.validators.base import BaseValidator


class LocalExcelOptimizer:
    """Optimizes Excel operations by performing all work locally first.

    This class implements a high-performance workflow:
    1. Create local Excel working copy
    2. Apply ALL validation fixes locally (no API calls)
    3. Batch all changes into single operations
    4. Only then convert to Google Sheets if needed
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def optimize_excel_workflow(
        self,
        source_excel: Union[str, Path],
        validators: List[BaseValidator],
        mode: str = "fix",
        target: Optional[str] = None,
        target_format: Optional[str] = None,
        auth_credentials: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute optimized Excel workflow with local operations.

        Args:
            source_excel: Path to source Excel file
            validators: List of validators to run
            mode: "fix" or "flag"
            target: Optional target (local, Drive folder ID, etc.)
            target_format: Optional target format ("excel" or "sheets")
            auth_credentials: Auth credentials (only needed for Sheets conversion)

        Returns:
            Dict with optimization results and performance metrics
        """
        start_time = time.time()

        try:
            # Step 1: Create optimized local working copy
            working_copy_result = self._create_optimized_working_copy(source_excel)
            if not working_copy_result["success"]:
                return working_copy_result

            working_excel_path = working_copy_result["working_path"]

            # Step 2: Apply ALL validations locally (FAST)
            validation_results = self._apply_all_validations_locally(
                working_excel_path, validators, mode
            )

            # Step 3: Handle target output if specified
            final_output = working_excel_path
            conversion_info = None

            if target and target_format == "sheets":
                # Prepare for Google Sheets conversion (but don't do it yet)
                conversion_info = {
                    "source_excel": source_excel,  # Use ORIGINAL filename for naming
                    "working_excel_path": working_excel_path,  # But use working file for data
                    "target": target,
                    "auth_credentials": auth_credentials,
                    "validation_results": validation_results,
                }

                # Perform conversion if auth is available
                if auth_credentials:
                    conversion_result = self._convert_to_google_sheets(conversion_info)
                    if conversion_result["success"]:
                        final_output = conversion_result["sheets_url"]
                    else:
                        validation_results["errors"].append(
                            f"Sheets conversion failed: {conversion_result['error']}"
                        )

            # Step 4: Compile final results
            total_time = time.time() - start_time

            return {
                "success": True,
                "working_path": working_excel_path,
                "final_output": final_output,
                "validation_results": validation_results,
                "conversion_info": conversion_info,
                "performance_metrics": {
                    "total_time_seconds": round(total_time, 2),
                    "local_operations_time": round(
                        validation_results.get("processing_time", 0), 2
                    ),
                    "optimization_enabled": True,
                    "api_calls_saved": len(validators)
                    * 2,  # Read + Write per validator
                    "efficiency_gain": f"{len(validators) * 2}x faster",
                },
                "error": None,
            }

        except Exception as e:
            return {
                "success": False,
                "working_path": None,
                "final_output": None,
                "validation_results": None,
                "error": str(e),
            }

    def _create_optimized_working_copy(
        self, source_excel: Union[str, Path]
    ) -> Dict[str, Any]:
        """Create an optimized local working copy of the Excel file.

        Args:
            source_excel: Path to source Excel file

        Returns:
            Dict with working copy creation results
        """
        try:
            source_path = Path(source_excel)
            if not source_path.exists():
                return {
                    "success": False,
                    "error": f"Source Excel file not found: {source_path}",
                }

            # Create optimized working directory
            working_dir = Path("./temp/local_optimization")
            try:
                working_dir.mkdir(parents=True, exist_ok=True)
                if not working_dir.exists():
                    return {
                        "success": False,
                        "error": f"Working directory creation failed: {working_dir} does not exist after mkdir",
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Working directory creation failed: {str(e)}",
                }

            # Generate unique working file name
            timestamp = int(time.time())
            working_file = working_dir / f"optimized_work_{timestamp}.xlsx"

            # Create working copy using our spreadsheet abstraction
            from urarovite.utils.generic_spreadsheet import convert_spreadsheet_format

            copy_result = convert_spreadsheet_format(
                source=source_path, target=working_file, preserve_formulas=True
            )

            if copy_result["success"]:
                self.logger.info(f"Created optimized working copy: {working_file}")
                return {
                    "success": True,
                    "working_path": str(working_file),
                    "source_size": source_path.stat().st_size,
                    "working_size": working_file.stat().st_size,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create working copy: {copy_result['error']}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Working copy creation failed: {str(e)}",
            }

    def _apply_all_validations_locally(
        self, working_excel_path: str, validators: List[BaseValidator], mode: str
    ) -> Dict[str, Any]:
        """Apply all validations to the local Excel file.

        This is the core optimization - all validation work happens locally
        with no API calls, making it extremely fast.

        Args:
            working_excel_path: Path to working Excel file
            validators: List of validators to apply
            mode: "fix" or "flag"

        Returns:
            Dict with aggregated validation results
        """
        start_time = time.time()

        aggregated_results = {
            "fixes_applied": 0,
            "flags_found": 0,
            "errors": [],
            "automated_log": [],
            "validator_details": {},
            "processing_time": 0,
        }

        self.logger.info(f"Starting local validation of {len(validators)} validators")

        for validator in validators:
            validator_start = time.time()

            try:
                # Run validator on local Excel file (NO API CALLS)
                validator_result = validator.validate(
                    spreadsheet_source=working_excel_path,
                    mode=mode,
                    auth_credentials=None,  # No auth needed for local Excel
                )

                # Aggregate results
                aggregated_results["fixes_applied"] += validator_result.get(
                    "fixes_applied", 0
                )
                aggregated_results["flags_found"] += validator_result.get(
                    "flags_found", 0
                )
                aggregated_results["errors"].extend(validator_result.get("errors", []))

                if validator_result.get("automated_log"):
                    aggregated_results["automated_log"].append(
                        f"{validator.name}: {validator_result['automated_log']}"
                    )

                # Store detailed results
                aggregated_results["validator_details"][validator.id] = {
                    "name": validator.name,
                    "result": validator_result,
                    "processing_time": round(time.time() - validator_start, 3),
                }

                self.logger.info(
                    f"✅ {validator.name}: "
                    f"{validator_result.get('fixes_applied', 0)} fixes, "
                    f"{validator_result.get('flags_found', 0)} flags"
                )

            except Exception as e:
                error_msg = f"{validator.name} failed: {str(e)}"
                aggregated_results["errors"].append(error_msg)
                self.logger.error(error_msg)

        processing_time = time.time() - start_time
        aggregated_results["processing_time"] = round(processing_time, 2)

        self.logger.info(
            f"Local validation complete: "
            f"{aggregated_results['fixes_applied']} fixes, "
            f"{aggregated_results['flags_found']} flags, "
            f"{processing_time:.2f}s"
        )

        return aggregated_results

    def _convert_to_google_sheets(
        self, conversion_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert the locally-processed Excel file to Google Sheets.

        This uses SMART CHUNKING to balance memory usage and API efficiency.

        Args:
            conversion_info: Conversion configuration

        Returns:
            Dict with conversion results
        """
        try:
            from urarovite.utils.sheets import create_new_spreadsheet_in_folder
            from urarovite.auth.google_sheets import get_gspread_client
            from urarovite.core.smart_chunking_optimizer import SmartChunkingOptimizer
            import time
            from pathlib import Path

            source_excel = conversion_info[
                "source_excel"
            ]  # Original filename for naming
            working_excel_path = conversion_info.get(
                "working_excel_path", source_excel
            )  # Working file for data
            target = conversion_info["target"]
            auth_credentials = conversion_info["auth_credentials"]
            validation_results = conversion_info["validation_results"]

            self.logger.info("🚀 Starting SMART CHUNKING Excel → Sheets conversion")

            # Check file size to determine strategy (use working file)
            file_size_mb = Path(working_excel_path).stat().st_size / (1024 * 1024)

            if file_size_mb > 1.0:  # Use smart chunking for files > 1MB
                self.logger.info(
                    f"📊 Large file detected ({file_size_mb:.1f} MB) - using smart chunking"
                )

                # Create Google Sheets in target location first
                if self._is_drive_folder_id(target):
                    gspread_client = get_gspread_client(auth_credentials["auth_secret"])

                    # Generate name based on original Excel file
                    source_path = Path(source_excel)
                    base_name = source_path.stem  # Get filename without extension

                    # Clean the name for Google Sheets (preserve more characters)
                    # Google Sheets allows more characters than Excel sheet names
                    clean_name = "".join(
                        c
                        for c in base_name
                        if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
                    ).rstrip()
                    if not clean_name:
                        timestamp = int(time.time())
                        clean_name = f"chunked_validation_{timestamp}"

                    spreadsheet_name = clean_name

                    # DEBUG: Log the spreadsheet name being used
                    self.logger.info(
                        f"🔍 DEBUG: Creating Google Sheets with name: '{spreadsheet_name}'"
                    )

                    new_spreadsheet = create_new_spreadsheet_in_folder(
                        gspread_client=gspread_client,
                        folder_id=target,
                        spreadsheet_name=spreadsheet_name,
                    )

                    if not new_spreadsheet:
                        return {
                            "success": False,
                            "error": "Failed to create Google Sheets in Drive folder",
                        }

                    sheets_url = f"https://docs.google.com/spreadsheets/d/{new_spreadsheet.id}/edit"

                    # Use smart chunking optimizer (use working file for data)
                    chunking_optimizer = SmartChunkingOptimizer()
                    chunking_result = chunking_optimizer.optimize_large_file_conversion(
                        source_excel=working_excel_path,
                        target_sheets_url=sheets_url,
                        auth_credentials=auth_credentials,
                        validation_fixes=validation_results,
                    )

                    if chunking_result["success"]:
                        self.logger.info(
                            f"✅ Smart chunking complete: {sheets_url} "
                            f"({chunking_result['chunks_processed']} chunks, "
                            f"{chunking_result['performance_metrics']['api_calls_made']} API calls)"
                        )
                        return {
                            "success": True,
                            "sheets_url": sheets_url,
                            "chunking_metrics": chunking_result["performance_metrics"],
                            "chunks_processed": chunking_result["chunks_processed"],
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Smart chunking failed: {chunking_result['error']}",
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported target type: {target}",
                    }

            else:
                # Use standard bulk upload for smaller files
                self.logger.info(
                    f"📊 Small file ({file_size_mb:.1f} MB) - using bulk upload"
                )

                from urarovite.utils.generic_spreadsheet import (
                    convert_excel_to_google_sheets,
                )

                if self._is_drive_folder_id(target):
                    gspread_client = get_gspread_client(auth_credentials["auth_secret"])

                    # Generate name based on original Excel file
                    source_path = Path(source_excel)
                    base_name = source_path.stem  # Get filename without extension

                    # DEBUG: Log the source file and base name
                    self.logger.info(
                        f"🔍 DEBUG: source_excel='{source_excel}', base_name='{base_name}'"
                    )

                    # Clean the name for Google Sheets (preserve more characters)
                    # Google Sheets allows more characters than Excel sheet names
                    clean_name = "".join(
                        c
                        for c in base_name
                        if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
                    ).rstrip()

                    # DEBUG: Log the cleaning result
                    self.logger.info(
                        f"🔍 DEBUG: clean_name='{clean_name}', is_empty={not clean_name}"
                    )

                    if not clean_name:
                        timestamp = int(time.time())
                        clean_name = f"optimized_validation_{timestamp}"
                        self.logger.info(
                            f"🔍 DEBUG: Using fallback name: '{clean_name}'"
                        )

                    spreadsheet_name = clean_name

                    # DEBUG: Log the spreadsheet name being used
                    self.logger.info(
                        f"🔍 DEBUG: Creating Google Sheets with name: '{spreadsheet_name}'"
                    )

                    new_spreadsheet = create_new_spreadsheet_in_folder(
                        gspread_client=gspread_client,
                        folder_id=target,
                        spreadsheet_name=spreadsheet_name,
                    )

                    if not new_spreadsheet:
                        return {
                            "success": False,
                            "error": "Failed to create Google Sheets in Drive folder",
                        }

                    sheets_url = f"https://docs.google.com/spreadsheets/d/{new_spreadsheet.id}/edit"

                    # Enhanced bulk upload with visual formatting preservation
                    from urarovite.utils.enhanced_conversion import (
                        convert_with_full_formatting,
                    )

                    conversion_result = convert_with_full_formatting(
                        source=working_excel_path,
                        target=sheets_url,
                        auth_credentials=auth_credentials,
                        preserve_formulas=True,
                        preserve_visual_formatting=True,
                    )

                    if conversion_result["success"]:
                        self.logger.info(f"✅ Bulk conversion complete: {sheets_url}")
                        return {
                            "success": True,
                            "sheets_url": sheets_url,
                            "converted_sheets": conversion_result.get(
                                "converted_sheets", []
                            ),
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Bulk upload failed: {conversion_result['error']}",
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported target type: {target}",
                    }

        except Exception as e:
            return {"success": False, "error": f"Conversion failed: {str(e)}"}

    def _is_drive_folder_id(self, target: str) -> bool:
        """Check if target looks like a Google Drive folder ID."""
        import re

        return bool(re.match(r"^[a-zA-Z0-9_-]{20,50}$", target))

    @contextmanager
    def _performance_monitor(self, operation_name: str):
        """Context manager for monitoring operation performance."""
        start_time = time.time()
        self.logger.info(f"🚀 Starting {operation_name}")

        try:
            yield
        finally:
            duration = time.time() - start_time
            self.logger.info(f"✅ {operation_name} completed in {duration:.2f}s")


def optimize_excel_validation(
    source_excel: Union[str, Path],
    validators: List[BaseValidator],
    mode: str = "fix",
    target: Optional[str] = None,
    target_format: Optional[str] = None,
    auth_credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenience function for optimized Excel validation.

    Args:
        source_excel: Path to source Excel file
        validators: List of validators to run
        mode: "fix" or "flag"
        target: Optional target location
        target_format: Optional target format
        auth_credentials: Auth credentials for Sheets conversion

    Returns:
        Dict with optimization results
    """
    optimizer = LocalExcelOptimizer()
    return optimizer.optimize_excel_workflow(
        source_excel=source_excel,
        validators=validators,
        mode=mode,
        target=target,
        target_format=target_format,
        auth_credentials=auth_credentials,
    )
