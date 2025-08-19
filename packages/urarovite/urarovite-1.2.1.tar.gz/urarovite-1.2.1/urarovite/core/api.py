"""Main API functions for the Urarovite validation library.

This module provides the main functions that integrate with the
Uvarolite batch processing system:
1. get_available_validation_criteria() - Returns all supported validation criteria
2. execute_validation() - Executes validation checks on Google Sheets
3. execute_all_validations() - Executes all validation checks on a single spreadsheet
4. crawl_and_validate_sheets() - Crawls through a spreadsheet and validates input/output sheets
"""

from __future__ import annotations

import logging
import time
from typing import Any

from urarovite.config import VALIDATION_CRITERIA
from urarovite.validators import get_validator_registry
from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
from urarovite.utils.sheets import extract_sheet_id
from urarovite.core.exceptions import (
    ValidationError,
    AuthenticationError,
    SheetAccessError,
)
from urarovite.core.local_excel_optimizer import LocalExcelOptimizer
from urarovite.utils.progress import (
    show_error,
    show_success,
    show_operation_progress,
    show_validation_summary,
)

# Set up logging
logger = logging.getLogger(__name__)


def get_available_validation_criteria() -> list[dict[str, str]]:
    """Return list of all validation criteria this library supports.

    Returns:
        List of criteria dictionaries with 'id' and 'name' fields

    Example:
        [
            {"id": "empty_cells", "name": "Fix Empty Cells"},

            ...
        ]
    """
    try:
        # Convert from our internal format to the required API format
        return [
            {
                "id": criterion["id"],
                "name": criterion["name"],
                "description": criterion["description"],
                "supports_fix": criterion["supports_fix"],
                "supports_flag": criterion["supports_flag"],
            }
            for criterion in VALIDATION_CRITERIA
        ]
    except Exception as e:
        logger.error(f"Error getting validation criteria: {e}")
        # Even if there's an error, return an empty list rather than raising
        return []


def _should_use_local_excel_optimizer(
    sheet_url: str, target: str | None = None, target_format: str | None = None
) -> bool:
    """Determine if we should use the local Excel optimizer.

    The optimizer is beneficial when:
    1. Source is an Excel file (local processing is faster)
    2. Multiple operations will be performed
    3. Target is Google Sheets (batch conversion is more efficient)

    Args:
        sheet_url: Source URL or file path
        target: Target location
        target_format: Target format

    Returns:
        True if local Excel optimizer should be used
    """
    # Check if source is Excel file
    is_excel_source = isinstance(sheet_url, str) and (
        sheet_url.endswith(".xlsx") or sheet_url.endswith(".xls")
    )

    # Check if we're doing format conversion
    is_format_conversion = target_format == "sheets"

    # Use optimizer for Excel sources, especially with format conversion
    return is_excel_source and (is_format_conversion or target is not None)


def execute_validation(
    check: dict[str, str],
    sheet_url: str,
    auth_secret: str | None = None,
    subject: str | None = None,
    target: str | None = None,
    target_format: str | None = None,
    preserve_visual_formatting: bool = True,  # DEFAULT: Always preserve visual formatting
) -> dict[str, Any]:
    """Execute a validation check on a Google Sheets document or Excel file with progress tracking.

    Args:
        check: Single validation check to apply, containing:
            - id: Must match an ID from get_available_validation_criteria()
            - mode: Either "fix" (auto-correct) or "flag" (report only)
        sheet_url: Google Sheets URL or path to Excel file (.xlsx, .xls) to validate
        auth_secret: Base64 encoded service account credentials (required for Google Sheets, optional for Excel)
        subject: Optional email subject for delegation (for domain-wide delegation, Google Sheets only)
        target: Optional target destination for validation results:
            - Google Drive folder ID: Save to specified Google Drive folder (e.g., "1A2B3C4D5E6F7G8H9I0J")
            - "local": Save to local directory (./output/)
            - None: Default to local Excel file (./output/) (default behavior)
        target_format: Format specification for target output:
            - "sheets": Google Sheets format (only allowed for remote targets)
            - "excel": Excel format (.xlsx) (allowed for any target)
            - None: Auto-detect based on source format (default behavior)
        preserve_visual_formatting: Whether to preserve fonts, colors, borders, etc. during conversion (default: True - RECOMMENDED)

    Returns:
        Dict with validation results:
        {
            "fixes_applied": int,      # Count of flags fixed
            "flags_found": int,       # Count of flags found but not fixed
            "errors": list[str],       # Error messages (empty list if no errors)
            "automated_log": str,      # Log messages from the validation process
            "target_output": str,      # Path/URL of target output (when target specified or fix mode)
            "duplicate_created": str   # Path/URL of duplicate created (only in fix mode)
        }

    Example:
        # Google Sheets (modify in place)
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            auth_secret="eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsIC4uLn0="
        )

        # Save to Google Drive folder as Google Sheets
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url="https://docs.google.com/spreadsheets/d/source123",
            target="1A2B3C4D5E6F7G8H9I0J",  # Google Drive folder ID
            target_format="sheets",
            auth_secret="eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsIC4uLn0="
        )

        # Save to Google Drive folder as Excel
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url="https://docs.google.com/spreadsheets/d/source123",
            target="1A2B3C4D5E6F7G8H9I0J",  # Google Drive folder ID
            target_format="excel",
            auth_secret="eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsIC4uLn0="
        )

        # Save to local directory as Excel
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url="https://docs.google.com/spreadsheets/d/source123",
            target="local",
            target_format="excel",
            auth_secret="eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsIC4uLn0="
        )

        # Default behavior (saves to local Excel file)
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url="https://docs.google.com/spreadsheets/d/source123",
            auth_secret="eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsIC4uLn0="
            # No target specified - defaults to local Excel file
        )
    """
    result = {
        "fixes_applied": 0,
        "flags_found": 0,
        "errors": [],
        "automated_logs": "",
        "target_output": None,
        "duplicate_created": None,
        "details": {},  # Add this to include detailed flags/fixes
    }

    start_time = time.time()
    logger.info(f"Starting validation execution for: {sheet_url}")

    # Extract check info for progress display (with safe defaults)
    check_id = check.get("id", "unknown") if check else "unknown"
    check_mode = check.get("mode", "flag") if check else "flag"
    operation_description = f"Validating with {check_id} ({check_mode} mode)"

    # Use progress tracking for the entire operation
    with show_operation_progress(operation_description, total=4) as progress:
        try:
            # Step 1: Input validation
            progress.update(1, description="Validating inputs...")
            if not check:
                result["errors"].append("No validation check specified")
                show_error("No validation check specified")
                return result

            if not sheet_url:
                result["errors"].append(
                    "Input source (Google Sheets URL or Excel file path) is required"
                )
                show_error("Input source is required")
                return result

            # Determine input type
            is_google_sheets = "docs.google.com" in sheet_url
            is_excel_file = sheet_url.endswith(".xlsx") or sheet_url.endswith(".xls")

            if not is_google_sheets and not is_excel_file:
                result["errors"].append(
                    f"Invalid input source. Must be a Google Sheets URL or Excel file (.xlsx, .xls). Provided: {sheet_url}"
                )
                show_error(f"Invalid input source: {sheet_url}")
                return result

            # Step 2: Authentication and setup
            progress.update(1, description="Setting up authentication...")
            if is_google_sheets:
                if not auth_secret:
                    result["errors"].append(
                        "Authentication credentials are required for Google Sheets (provide auth_secret with base64 encoded service account)"
                    )
                    show_error("Authentication credentials required for Google Sheets")
                    return result

                # Extract sheet ID from URL
                sheet_id = extract_sheet_id(sheet_url)
                if not sheet_id:
                    result["errors"].append(f"Invalid Google Sheets URL: {sheet_url}")
                    logger.error(f"Invalid Google Sheets URL provided: {sheet_url}")
                    show_error(f"Invalid Google Sheets URL: {sheet_url}")
                    return result

                logger.info(f"Extracted sheet ID: {sheet_id}")

                # Create Google Sheets service from base64 encoded credentials
                try:
                    logger.info("Creating Google Sheets API service")
                    create_sheets_service_from_encoded_creds(auth_secret, subject)
                    logger.info("Successfully authenticated with Google Sheets API")
                except Exception as e:
                    result["errors"].append(f"Authentication failed: {str(e)}")
                    logger.error(f"Authentication failed: {str(e)}")
                    show_error(f"Authentication failed: {str(e)}")
                    return result
            else:
                # Excel file - check if file exists
                from pathlib import Path

                excel_path = Path(sheet_url)
                if not excel_path.exists():
                    result["errors"].append(f"Excel file not found: {sheet_url}")
                    show_error(f"Excel file not found: {sheet_url}")
                    return result
                logger.info(f"Processing Excel file: {sheet_url}")

            # Step 3: Preparing validation
            progress.update(1, description="Preparing validation...")
            validator_registry = get_validator_registry()

            # Step 4: Executing validation
            progress.update(1, description=f"Executing {check_id} validation...")

            # Process the validation check
            try:
                check_id = check.get("id")
                mode = check.get("mode", "flag")  # Default to flag mode

                if not check_id:
                    result["errors"].append("Check missing required 'id' field")
                    return result

                if mode not in ["fix", "flag"]:
                    result["errors"].append(
                        f"Invalid mode '{mode}' for check '{check_id}'. Must be 'fix' or 'flag'"
                    )
                    return result

                # Get the validator for this check
                validator = validator_registry.get(check_id)
                if not validator:
                    result["errors"].append(f"Unknown validation check: '{check_id}'")
                    return result

                logger.info(f"Running validation check: {check_id} in {mode} mode")

                # Check if we should use the local Excel optimizer
                if _should_use_local_excel_optimizer(sheet_url, target, target_format):
                    logger.info(
                        "🚀 Using Local Excel Optimizer for maximum performance"
                    )

                    # Prepare auth credentials for optimizer
                    optimizer_auth_credentials = None
                    if auth_secret:
                        optimizer_auth_credentials = {"auth_secret": auth_secret}
                        if subject:
                            optimizer_auth_credentials["subject"] = subject

                    optimizer = LocalExcelOptimizer()
                    optimizer_result = optimizer.optimize_excel_workflow(
                        source_excel=sheet_url,
                        validators=[validator],
                        mode=mode,
                        target=target,
                        target_format=target_format,
                        auth_credentials=optimizer_auth_credentials,
                    )

                    if optimizer_result["success"]:
                        # Convert optimizer results to standard format
                        validation_results = optimizer_result["validation_results"]
                        result["fixes_applied"] = validation_results["fixes_applied"]
                        result["flags_found"] = validation_results["flags_found"]
                        result["errors"] = validation_results["errors"]
                        result["automated_logs"] = "; ".join(
                            validation_results.get("automated_log", [])
                        )
                        result["duplicate_created"] = optimizer_result["final_output"]
                        result["target_output"] = optimizer_result["final_output"]

                        # Add performance metrics
                        result["performance_metrics"] = optimizer_result[
                            "performance_metrics"
                        ]

                        logger.info(
                            f"✅ Local Excel Optimizer completed: "
                            f"{result['fixes_applied']} fixes, "
                            f"{result['flags_found']} flags, "
                            f"{optimizer_result['performance_metrics']['total_time_seconds']}s"
                        )

                        return result
                    else:
                        logger.warning(
                            f"Local Excel Optimizer failed: {optimizer_result['error']}"
                        )
                        # Fall back to standard processing
                        result["errors"].append(
                            f"Optimizer failed: {optimizer_result['error']}"
                        )

                # Standard processing (fallback or non-Excel sources)

                # Prepare authentication credentials
                if is_google_sheets:
                    auth_credentials = {"auth_secret": auth_secret}
                    if subject:
                        auth_credentials["subject"] = subject
                else:
                    # Excel files don't need authentication
                    auth_credentials = None

                # Determine working spreadsheet (original or duplicate)
                working_spreadsheet = sheet_url

                # If in fix mode, create duplicate first
                if mode == "fix":
                    logger.info(
                        "Fix mode detected - creating duplicate before validation"
                    )
                    duplicate_result = _create_pre_validation_duplicate(
                        source=sheet_url,
                        target=target,
                        target_format=target_format,
                        auth_credentials=auth_credentials,
                        auth_secret=auth_secret,
                        preserve_visual_formatting=preserve_visual_formatting,
                    )

                    if not duplicate_result["success"]:
                        result["errors"].append(
                            f"Failed to create duplicate: {duplicate_result['error']}"
                        )
                        logger.error(
                            f"Duplicate creation failed: {duplicate_result['error']}"
                        )
                        return result

                    working_spreadsheet = duplicate_result["working_path"]

                    # For Excel → Google Sheets workflow, the working_path is the Excel file to work on
                    # and output_path will be set after conversion
                    if duplicate_result.get("conversion_pending"):
                        result["duplicate_created"] = duplicate_result[
                            "working_path"
                        ]  # Excel working file
                        result["_conversion_pending"] = duplicate_result[
                            "conversion_pending"
                        ]
                    else:
                        result["duplicate_created"] = duplicate_result["output_path"]

                        logger.info(
                            f"Created duplicate at: {duplicate_result['output_path']}"
                        )
                else:
                    # Flag mode - work on original spreadsheet
                    working_spreadsheet = sheet_url

                # Execute validation on working spreadsheet
                validation_result = validator.validate(
                    spreadsheet_source=working_spreadsheet,
                    mode=mode,
                    auth_credentials=auth_credentials,
                )

                # Aggregate results
                if mode == "fix":
                    result["fixes_applied"] += validation_result.get("fixes_applied", 0)
                    result["flags_found"] += validation_result.get("flags_found", 0)
                else:
                    result["flags_found"] += validation_result.get("flags_found", 0)

                result["errors"].extend(validation_result.get("errors", []))
                result["details"] = validation_result.get("details", {})

                # Use automated log from validator if available, otherwise generate generic message
                automated_log = validation_result.get("automated_log", "")

                if not automated_log:
                    # Fallback for validators that don't provide automated_log yet
                    if mode == "fix" and result["fixes_applied"] > 0:
                        automated_log = f"Applied {result['fixes_applied']} fixes"
                        logger.info(f"Validation {check_id}: {automated_log}")
                    elif mode == "flag" and result["flags_found"] > 0:
                        automated_log = f"Flagged {result['flags_found']} flags"
                        logger.info(f"Validation {check_id}: {automated_log}")
                    else:
                        automated_log = "No flags found"
                        logger.info(f"Validation {check_id}: {automated_log}")
                else:
                    logger.info(f"Validation {check_id}: {automated_log}")

                result["automated_logs"] = automated_log

                # For fix mode, the target output was already created as duplicate
                # For flag mode, we might still need to handle target output
                if target and mode == "flag":
                    try:
                        logger.info(f"Processing target output for flag mode: {target}")
                        target_result = _handle_target_output(
                            source=working_spreadsheet,
                            target=target,
                            target_format=target_format,
                            auth_credentials=auth_credentials,
                            auth_secret=auth_secret,
                            preserve_visual_formatting=preserve_visual_formatting,
                        )

                        if not target_result["success"]:
                            result["errors"].append(
                                f"Target output failed: {target_result['error']}"
                            )
                            logger.error(
                                f"Target output failed: {target_result['error']}"
                            )
                        else:
                            result["target_output"] = target_result["output_path"]
                            logger.info(
                                f"Successfully saved to target: {target_result['output_path']}"
                            )

                    except Exception as e:
                        error_msg = f"Target processing failed: {str(e)}"
                        result["errors"].append(error_msg)
                        logger.error(error_msg)
                elif mode == "fix" and "duplicate_created" in result:
                    # For fix mode, the target output is the duplicate we created
                    result["target_output"] = result["duplicate_created"]

                # Log completion timing
                duration = time.time() - start_time
                logger.info(
                    f"Validation {check_id} completed successfully in {duration:.2f} seconds"
                )

            except ValidationError as e:
                result["errors"].append(
                    f"Validation error in check '{check_id}': {str(e)}"
                )
            except Exception as e:
                result["errors"].append(
                    f"Unexpected error in check '{check_id}': {str(e)}"
                )
                logger.exception(f"Unexpected error in validation check {check_id}")

        except AuthenticationError as e:
            result["errors"].append(f"Authentication error: {str(e)}")
            logger.error(f"Authentication error: {str(e)}")
        except SheetAccessError as e:
            result["errors"].append(f"Sheet access error: {str(e)}")
            logger.error(f"Sheet access error: {str(e)}")
        except Exception as e:
            result["errors"].append(f"Unexpected error: {str(e)}")
            logger.exception("Unexpected error in execute_validation")

    # Handle post-validation conversion for Excel → Google Sheets workflow
    if (
        mode == "fix"
        and result.get("duplicate_created")
        and not result.get("errors")
        and result.get("_conversion_pending")
    ):
        logger.info("Post-validation conversion: Excel → Google Sheets")
        try:
            conversion_info = result["_conversion_pending"]
            fixed_excel_path = result["duplicate_created"]

            # Now convert the fixed Excel file to Google Sheets
            from urarovite.utils.sheets import create_new_spreadsheet_in_folder
            from urarovite.auth.google_sheets import get_gspread_client
            from urarovite.utils.generic_spreadsheet import (
                convert_excel_to_google_sheets,
            )

            # Create Google Sheets service
            gspread_client = get_gspread_client(conversion_info["auth_secret"])

            # Create new Google Sheets document in the specified folder
            new_spreadsheet = create_new_spreadsheet_in_folder(
                gspread_client=gspread_client,
                folder_id=conversion_info["folder_id"],
                spreadsheet_name=conversion_info["spreadsheet_name"],
            )

            if new_spreadsheet:
                # Convert the fixed Excel file to Google Sheets
                new_sheets_url = (
                    f"https://docs.google.com/spreadsheets/d/{new_spreadsheet.id}/edit"
                )

                conversion_result = convert_excel_to_google_sheets(
                    excel_file_path=fixed_excel_path,
                    google_sheets_url=new_sheets_url,
                    auth_credentials={"auth_secret": conversion_info["auth_secret"]},
                    create_new_sheets=True,
                )

                if conversion_result["success"]:
                    # Update result with Google Sheets URL
                    result["target_output"] = new_sheets_url
                    result["duplicate_created"] = new_sheets_url
                    logger.info(
                        f"Successfully converted fixed Excel to Google Sheets: {new_sheets_url}"
                    )
                else:
                    result["errors"].append(
                        f"Post-validation conversion failed: {conversion_result['error']}"
                    )
                    logger.error(
                        f"Post-validation conversion failed: {conversion_result['error']}"
                    )
            else:
                result["errors"].append(
                    "Failed to create Google Sheets document for post-validation conversion"
                )
                logger.error(
                    "Failed to create Google Sheets document for post-validation conversion"
                )

        except Exception as e:
            result["errors"].append(f"Post-validation conversion error: {str(e)}")
            logger.error(f"Post-validation conversion error: {str(e)}")

        # Clean up the internal conversion info
        if "_conversion_pending" in result:
            del result["_conversion_pending"]

    # Final timing log
    total_duration = time.time() - start_time
    logger.info(f"Validation execution completed in {total_duration:.2f} seconds")

    # Display results summary
    if result.get("errors"):
        # Show errors
        error_details = "; ".join(result["errors"])
        show_error("Validation completed with errors", error_details)
    else:
        # Show success with summary
        success_msg = "Validation completed successfully"
        if result.get("fixes_applied", 0) > 0:
            success_msg += f" - {result['fixes_applied']} fixes applied"
        elif result.get("flags_found", 0) > 0:
            success_msg += f" - {result['flags_found']} flags found"

        details = f"Completed in {total_duration:.2f} seconds"
        if result.get("duplicate_created"):
            details += " | Duplicate created"
        if result.get("target_output"):
            details += f" | Output: {result['target_output']}"

        show_success(success_msg, details)

    # Show detailed summary if enabled
    show_validation_summary(result)

    return result


def execute_all_validations(
    checks: list[dict[str, str]],
    sheet_url: str,
    auth_secret: str | None = None,
    subject: str | None = None,
    target: str | None = None,
    target_format: str | None = None,
    preserve_visual_formatting: bool = True,
) -> dict[str, Any]:
    """Execute all validation checks on a single spreadsheet with shared duplicate.

    This function is optimized for batch validation - it creates a single duplicate
    for all validations to work on, rather than creating separate duplicates for each.

    Args:
        checks: List of validation check dictionaries with 'id' and 'mode' keys
        sheet_url: URL or path to the spreadsheet to validate (Google Sheets, Google Drive file, or local Excel)
        auth_secret: Base64 encoded service account credentials (required for Google Drive files)
        subject: Email address for domain-wide delegation (optional)
        target: Target destination for output ("local", Google Drive folder ID, or None)
        target_format: Output format ("excel" or "sheets", auto-detected if None)
        preserve_visual_formatting: Whether to preserve visual formatting during conversion

    Returns:
        Dict containing:
        - success: Whether all validations completed without critical errors
        - results: List of individual validation results
        - shared_duplicate: Path/URL of the shared working duplicate
        - target_output: Final output location (if target specified)
        - summary: Aggregate statistics
        - errors: List of any critical errors

    Example:
        >>> checks = [
        ...     {"id": "empty_cells", "mode": "fix"},
        ...     {"id": "tab_names", "mode": "fix"},
        ... ]
        >>> result = execute_all_validations(checks, sheet_url, auth_secret)
        >>> print(f"Total fixes: {result['summary']['total_fixes']}")
    """
    import time
    import logging

    logger = logging.getLogger(__name__)
    start_time = time.time()

    # Initialize result structure
    result = {
        "success": True,
        "results": [],
        "shared_duplicate": None,
        "target_output": None,
        "summary": {
            "total_fixes": 0,
            "total_flags": 0,
            "total_errors": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "checks_processed": len(checks),
        },
        "errors": [],
        "performance_metrics": {
            "total_time_seconds": 0,
            "duplicate_creation_time": 0,
            "validation_time": 0,
            "checks_per_second": 0,
        },
    }

    if not checks:
        result["errors"].append("No validation checks provided")
        result["success"] = False
        return result

    try:
        logger.info(f"Starting batch validation with {len(checks)} checks")

        # Determine if any check requires fix mode (needs duplicate)
        needs_duplicate = any(check.get("mode") == "fix" for check in checks)

        # Set up authentication and determine source type
        auth_credentials = None

        # Detect file type automatically for Google Drive URLs
        source_is_google = False
        file_type = None

        if isinstance(sheet_url, str):
            # Check if this is any Google Drive URL (not just sheets.google.com)
            is_google_drive_url = (
                "drive.google.com" in sheet_url
                or "docs.google.com" in sheet_url
                or "sheets.google.com" in sheet_url
            )

            if is_google_drive_url:
                if not auth_secret:
                    result["errors"].append(
                        "Authentication required for Google Drive files"
                    )
                    result["success"] = False
                    return result

                # Get actual file type from Google Drive API
                logger.info("Detecting file type for Google Drive URL...")
                from urarovite.utils.drive import get_file_metadata

                try:
                    metadata = get_file_metadata(sheet_url, auth_secret)
                    if metadata["success"]:
                        file_type = metadata["mimeType"]
                        source_is_google = metadata["is_google_sheets"]
                        logger.info(
                            f"Detected file type: {file_type} (Google Sheets: {source_is_google})"
                        )
                    else:
                        result["errors"].append(
                            f"Failed to detect file type: {metadata.get('error_msg', 'Unknown error')}"
                        )
                        result["success"] = False
                        return result
                except Exception as e:
                    result["errors"].append(f"Failed to detect file type: {str(e)}")
                    result["success"] = False
                    return result
            else:
                # Local Excel file or other non-Google URL
                source_is_google = False

        if source_is_google:
            # Authentication already validated above for Google Drive URLs
            auth_credentials = {"auth_secret": auth_secret}
            if subject:
                auth_credentials["subject"] = subject

        # Create shared duplicate if needed
        working_spreadsheet = sheet_url
        duplicate_creation_start = time.time()

        if needs_duplicate:
            logger.info("Creating shared duplicate for batch validation")
            duplicate_result = _create_pre_validation_duplicate(
                source=sheet_url,
                target=target,
                target_format=target_format,
                auth_credentials=auth_credentials,
                auth_secret=auth_secret,
                preserve_visual_formatting=preserve_visual_formatting,
            )

            if not duplicate_result["success"]:
                result["errors"].append(
                    f"Failed to create shared duplicate: {duplicate_result['error']}"
                )
                result["success"] = False
                return result

            working_spreadsheet = duplicate_result["working_path"]
            result["shared_duplicate"] = (
                duplicate_result["output_path"] or duplicate_result["working_path"]
            )

            # Handle conversion pending (Excel → Sheets workflow)
            conversion_pending = duplicate_result.get("conversion_pending")
        else:
            conversion_pending = None

        result["performance_metrics"]["duplicate_creation_time"] = (
            time.time() - duplicate_creation_start
        )

        # Execute all validations on the shared duplicate
        validation_start = time.time()

        for check in checks:
            check_id = check.get("id")
            check_mode = check.get("mode", "flag")

            logger.info(f"Executing validation: {check_id} in {check_mode} mode")

            try:
                # Execute individual validation
                validation_result = execute_validation(
                    check=check,
                    sheet_url=working_spreadsheet,
                    auth_secret=auth_secret,
                    subject=subject,
                    target=None,  # Don't create individual outputs
                    target_format=None,
                )

                # Aggregate results
                # Store individual result
                individual_result = {
                    "check_id": check_id,
                    "mode": check_mode,
                    "fixes_applied": validation_result.get("fixes_applied", 0),
                    "flags_found": validation_result.get("flags_found", 0),
                    "errors": validation_result.get("errors", []),
                    "automated_logs": validation_result.get("automated_logs", ""),
                    "details": validation_result.get("details", {}),
                    "success": len(validation_result.get("errors", [])) == 0,
                }

                result["results"].append(individual_result)

                # Aggregate detailed information at the top level
                individual_details = validation_result.get("details", {})
                if individual_details:
                    if "details" not in result:
                        result["details"] = {"flags": [], "fixes": []}

                    # Add flags with validator context
                    if "flags" in individual_details:
                        for issue in individual_details["flags"]:
                            issue_with_validator = issue.copy()
                            issue_with_validator["validator"] = check_id
                            result["details"]["flags"].append(issue_with_validator)

                    # Add fixes with validator context
                    if "fixes" in individual_details:
                        for fix in individual_details["fixes"]:
                            fix_with_validator = fix.copy()
                            fix_with_validator["validator"] = check_id
                            result["details"]["fixes"].append(fix_with_validator)

                # Update summary
                result["summary"]["total_fixes"] += validation_result.get(
                    "fixes_applied", 0
                )
                result["summary"]["total_flags"] += validation_result.get(
                    "flags_found", 0
                )
                result["summary"]["total_errors"] += len(
                    validation_result.get("errors", [])
                )

                if len(validation_result.get("errors", [])) == 0:
                    result["summary"]["successful_validations"] += 1
                else:
                    result["summary"]["failed_validations"] += 1
                    # Add individual errors to main error list
                    result["errors"].extend(validation_result.get("errors", []))

            except Exception as e:
                error_msg = f"Validation '{check_id}' failed: {str(e)}"
                result["errors"].append(error_msg)
                result["summary"]["failed_validations"] += 1
                result["summary"]["total_errors"] += 1
                logger.error(error_msg)

                # Add failed validation to results
                result["results"].append(
                    {
                        "check_id": check_id,
                        "mode": check_mode,
                        "fixes_applied": 0,
                        "flags_found": 0,
                        "errors": [error_msg],
                        "automated_logs": "",
                        "success": False,
                        "details": {},
                    }
                )

        result["performance_metrics"]["validation_time"] = (
            time.time() - validation_start
        )

        # Handle final output and conversion if needed
        if conversion_pending:
            logger.info("Converting Excel working file to Google Sheets")
            try:
                # Use the same conversion logic as execute_validation
                from urarovite.utils.sheets import create_new_spreadsheet_in_folder
                from urarovite.auth.google_sheets import get_gspread_client
                from urarovite.utils.generic_spreadsheet import (
                    convert_excel_to_google_sheets,
                )

                # Create Google Sheets service
                gspread_client = get_gspread_client(conversion_pending["auth_secret"])

                # Create new Google Sheets document in the specified folder
                new_spreadsheet = create_new_spreadsheet_in_folder(
                    gspread_client=gspread_client,
                    folder_id=conversion_pending["folder_id"],
                    spreadsheet_name=conversion_pending["spreadsheet_name"],
                )

                if new_spreadsheet:
                    # Convert the fixed Excel file to Google Sheets
                    new_sheets_url = f"https://docs.google.com/spreadsheets/d/{new_spreadsheet.id}/edit"

                    conversion_result = convert_excel_to_google_sheets(
                        excel_file_path=working_spreadsheet,
                        google_sheets_url=new_sheets_url,
                        auth_credentials={
                            "auth_secret": conversion_pending["auth_secret"]
                        },
                        create_new_sheets=True,
                    )

                    if conversion_result["success"]:
                        result["target_output"] = new_sheets_url
                        result["shared_duplicate"] = new_sheets_url
                        logger.info(
                            f"Successfully converted Excel to Google Sheets: {new_sheets_url}"
                        )
                    else:
                        result["errors"].append(
                            f"Final conversion failed: {conversion_result['error']}"
                        )
                        logger.error(
                            f"Final conversion failed: {conversion_result['error']}"
                        )
                else:
                    result["errors"].append(
                        "Failed to create Google Sheets document for final conversion"
                    )
                    logger.error(
                        "Failed to create Google Sheets document for final conversion"
                    )

            except Exception as e:
                result["errors"].append(f"Final conversion failed: {str(e)}")
                logger.error(f"Final conversion error: {str(e)}")

        elif target and needs_duplicate:
            # For Google Sheets -> Excel, the working spreadsheet IS the final output
            # For other cases, handle target output normally
            source_is_google = isinstance(sheet_url, str) and (
                "docs.google.com" in sheet_url or "sheets.google.com" in sheet_url
            )

            if not (
                source_is_google and target == "local" and target_format == "excel"
            ):
                # Handle final target output for non-direct cases
                logger.info("Creating final target output after validation")
                try:
                    target_result = _handle_target_output(
                        source=working_spreadsheet,
                        target=target,
                        target_format=target_format,
                        auth_credentials=auth_credentials,
                        auth_secret=auth_secret,
                        preserve_visual_formatting=preserve_visual_formatting,
                    )

                    if target_result["success"]:
                        result["target_output"] = target_result["output_path"]
                        logger.info(
                            f"Final target output created: {target_result['output_path']}"
                        )
                    else:
                        result["errors"].append(
                            f"Final target output failed: {target_result['error']}"
                        )
                        logger.error(
                            f"Final target output failed: {target_result['error']}"
                        )

                except Exception as e:
                    result["errors"].append(f"Final target output failed: {str(e)}")
                    logger.error(f"Final target output error: {str(e)}")
            else:
                # For Google Sheets -> local Excel, the working spreadsheet is the final output
                result["target_output"] = working_spreadsheet
                logger.info(
                    f"Working spreadsheet is final output: {working_spreadsheet}"
                )

        elif target and not needs_duplicate:
            # Handle target output for flag-only validations
            try:
                target_result = _handle_target_output(
                    source=working_spreadsheet,
                    target=target,
                    target_format=target_format,
                    auth_credentials=auth_credentials,
                    auth_secret=auth_secret,
                    preserve_visual_formatting=preserve_visual_formatting,
                )

                if target_result["success"]:
                    result["target_output"] = target_result["output_path"]
                else:
                    result["errors"].append(
                        f"Target output failed: {target_result['error']}"
                    )

            except Exception as e:
                result["errors"].append(f"Target output failed: {str(e)}")

        # Calculate final performance metrics
        total_time = time.time() - start_time
        result["performance_metrics"]["total_time_seconds"] = total_time
        result["performance_metrics"]["checks_per_second"] = (
            len(checks) / total_time if total_time > 0 else 0
        )

        # Determine overall success
        if result["summary"]["failed_validations"] > 0 or result["errors"]:
            result["success"] = False

        logger.info(
            f"Batch validation completed in {total_time:.2f}s - {result['summary']['successful_validations']}/{len(checks)} successful"
        )

        # Handle temp file management after validation completion
        if (
            needs_duplicate
            and duplicate_result.get("needs_move_to_output")
            and target == "local"
        ):
            # For local target only: move from temp to output
            from pathlib import Path
            import shutil

            working_path = Path(duplicate_result["working_path"])
            output_path = Path(duplicate_result["output_path"])

            if working_path.exists():
                try:
                    # Move file from temp to output for local target
                    shutil.move(str(working_path), str(output_path))
                    logger.info(
                        f"Moved validation file from temp to output: {output_path}"
                    )
                    result["shared_duplicate"] = str(output_path)
                except Exception as e:
                    logger.warning(f"Failed to move temp file to output: {str(e)}")
        elif needs_duplicate and target != "local":
            # For Google Drive targets: temp files will be cleaned up after upload
            logger.debug(
                f"Temp validation file will be cleaned up after Drive upload: {duplicate_result.get('working_path')}"
            )

    except Exception as e:
        result["errors"].append(f"Batch validation failed: {str(e)}")
        result["success"] = False
        logger.error(f"Batch validation failed: {str(e)}")

    return result


def crawl_and_validate_sheets(
    metadata_sheet_url: str,
    auth_secret: str | None = None,
    subject: str | None = None,
    target: str | None = None,
    target_format: str | None = None,
    validation_mode: str = "fix",
    preserve_visual_formatting: bool = True,
) -> dict[str, Any]:
    """Crawl through a metadata sheet and validate all referenced input/output sheets.

    This function reads a metadata spreadsheet that contains information about
    input and output sheets, extracts the sheet URLs/paths, and runs all available
    validations on both the input and output sheets for each row.

    Args:
        metadata_sheet_url: URL or path to the metadata spreadsheet to crawl
        auth_secret: Base64 encoded service account credentials (required for Google Sheets)
        subject: Email address for domain-wide delegation (optional)
        target: Target destination for output ("local", Google Drive folder ID, or None)
        target_format: Output format ("excel" or "sheets", auto-detected if None)
        validation_mode: Mode for validations ("fix" or "flag", default: "fix")
        preserve_visual_formatting: Whether to preserve visual formatting during conversion

    Returns:
        Dict containing:
        - success: Whether the crawling and validation completed successfully
        - metadata_info: Information about the metadata sheet
        - processed_sheets: List of results for each input/output sheet pair
        - summary: Aggregate statistics across all validations
        - errors: List of any critical errors

    Example:
        >>> result = crawl_and_validate_sheets(
        ...     metadata_sheet_url="https://docs.google.com/spreadsheets/d/abc123",
        ...     auth_secret="eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsIC4uLn0=",
        ...     validation_mode="fix",
        ... )
        >>> print(f"Processed {len(result['processed_sheets'])} sheet pairs")
    """
    import time
    import logging
    from urarovite.core.spreadsheet import SpreadsheetFactory
    from urarovite.config import VALIDATION_CRITERIA

    logger = logging.getLogger(__name__)
    start_time = time.time()

    # Initialize result structure
    result = {
        "success": True,
        "metadata_info": {},
        "processed_sheets": [],
        "summary": {
            "total_sheet_pairs": 0,
            "successful_pairs": 0,
            "failed_pairs": 0,
            "total_input_fixes": 0,
            "total_output_fixes": 0,
            "total_input_flags": 0,
            "total_output_flags": 0,
            "total_errors": 0,
        },
        "errors": [],
        "performance_metrics": {
            "total_time_seconds": 0,
            "crawling_time": 0,
            "validation_time": 0,
            "pairs_per_second": 0,
        },
    }

    # Use progress tracking for the entire operation
    operation_description = "Crawling and validating sheets from metadata"
    with show_operation_progress(operation_description, total=4) as progress:
        try:
            # Step 1: Validate inputs and setup authentication
            progress.update(
                1, description="Setting up authentication and validating inputs..."
            )

            if not metadata_sheet_url:
                result["errors"].append("Metadata sheet URL is required")
                result["success"] = False
                return result

            # Determine if metadata sheet is Google Sheets
            is_google_sheets = "docs.google.com" in metadata_sheet_url
            is_excel_file = metadata_sheet_url.endswith(
                ".xlsx"
            ) or metadata_sheet_url.endswith(".xls")

            if not is_google_sheets and not is_excel_file:
                result["errors"].append(
                    f"Invalid metadata sheet source. Must be a Google Sheets URL or Excel file. Provided: {metadata_sheet_url}"
                )
                result["success"] = False
                return result

            # Setup authentication credentials
            auth_credentials = None
            if is_google_sheets:
                if not auth_secret:
                    result["errors"].append(
                        "Authentication credentials are required for Google Sheets"
                    )
                    result["success"] = False
                    return result

                auth_credentials = {"auth_secret": auth_secret}
                if subject:
                    auth_credentials["subject"] = subject

            # Step 2: Crawl metadata sheet
            progress.update(1, description="Crawling metadata sheet...")
            crawling_start = time.time()

            sheet_pairs = []
            try:
                # Open the metadata spreadsheet
                with SpreadsheetFactory.create_spreadsheet(
                    metadata_sheet_url, auth_credentials
                ) as metadata_spreadsheet:
                    # Get metadata about the spreadsheet
                    metadata_info = metadata_spreadsheet.get_metadata()
                    result["metadata_info"] = {
                        "title": metadata_info.title,
                        "sheet_names": metadata_info.sheet_names,
                        "spreadsheet_type": metadata_info.spreadsheet_type,
                        "url": metadata_info.url,
                        "file_path": str(metadata_info.file_path)
                        if metadata_info.file_path
                        else None,
                    }

                    logger.info(f"Processing metadata sheet: {metadata_info.title}")
                    logger.info(
                        f"Found {len(metadata_info.sheet_names)} sheets: {metadata_info.sheet_names}"
                    )

                    # Process each sheet in the metadata spreadsheet
                    for sheet_name in metadata_info.sheet_names:
                        try:
                            # Get data from the current sheet
                            sheet_data = metadata_spreadsheet.get_sheet_data(sheet_name)

                            if not sheet_data.values or len(sheet_data.values) < 2:
                                logger.warning(
                                    f"Sheet '{sheet_name}' appears to be empty or has no data rows"
                                )
                                continue

                            # Extract header row to find relevant columns
                            headers = sheet_data.values[0] if sheet_data.values else []

                            # Look for columns that might contain sheet references
                            # Common column names that might contain input/output sheet references
                            input_sheet_cols = []
                            output_sheet_cols = []

                            for i, header in enumerate(headers):
                                if not header:
                                    continue

                                header_lower = str(header).lower()

                                # Look for input sheet columns
                                if any(
                                    keyword in header_lower
                                    for keyword in [
                                        "input_sheet",
                                        "input sheet",
                                        "source_sheet",
                                        "source sheet",
                                        "example_input",
                                        "input_url",
                                        "input file",
                                    ]
                                ):
                                    input_sheet_cols.append(i)

                                # Look for output sheet columns
                                elif any(
                                    keyword in header_lower
                                    for keyword in [
                                        "output_sheet",
                                        "output sheet",
                                        "target_sheet",
                                        "target sheet",
                                        "example_output",
                                        "output_url",
                                        "output file",
                                    ]
                                ):
                                    output_sheet_cols.append(i)

                            # If no specific input/output columns found, look for any URL/file columns
                            if not input_sheet_cols and not output_sheet_cols:
                                for i, header in enumerate(headers):
                                    if not header:
                                        continue

                                    header_lower = str(header).lower()
                                    if any(
                                        keyword in header_lower
                                        for keyword in [
                                            "url",
                                            "file",
                                            "sheet",
                                            "spreadsheet",
                                            "document",
                                        ]
                                    ):
                                        # Assume first URL column is input, second is output
                                        if not input_sheet_cols:
                                            input_sheet_cols.append(i)
                                        elif not output_sheet_cols:
                                            output_sheet_cols.append(i)

                            logger.info(
                                f"Sheet '{sheet_name}': Found input columns at indices {input_sheet_cols}, output columns at indices {output_sheet_cols}"
                            )

                            # Process data rows
                            for row_idx, row in enumerate(
                                sheet_data.values[1:], start=2
                            ):  # Skip header row
                                if not row or all(not cell for cell in row):
                                    continue  # Skip empty rows

                                # Extract input sheet URLs/paths
                                input_sheets = []
                                for col_idx in input_sheet_cols:
                                    if col_idx < len(row) and row[col_idx]:
                                        input_sheets.append(str(row[col_idx]).strip())

                                # Extract output sheet URLs/paths
                                output_sheets = []
                                for col_idx in output_sheet_cols:
                                    if col_idx < len(row) and row[col_idx]:
                                        output_sheets.append(str(row[col_idx]).strip())

                                # Create sheet pairs for validation
                                if input_sheets or output_sheets:
                                    sheet_pairs.append(
                                        {
                                            "row_number": row_idx,
                                            "sheet_name": sheet_name,
                                            "input_sheets": input_sheets,
                                            "output_sheets": output_sheets,
                                            "metadata_row": row[
                                                : min(len(row), 10)
                                            ],  # Store first 10 columns for context
                                        }
                                    )

                            logger.info(
                                f"Sheet '{sheet_name}': Found {len([p for p in sheet_pairs if p['sheet_name'] == sheet_name])} sheet pairs"
                            )

                        except Exception as e:
                            error_msg = (
                                f"Error processing sheet '{sheet_name}': {str(e)}"
                            )
                            result["errors"].append(error_msg)
                            logger.error(error_msg)
                            continue

                    result["summary"]["total_sheet_pairs"] = len(sheet_pairs)
                    logger.info(f"Total sheet pairs found: {len(sheet_pairs)}")

            except Exception as e:
                error_msg = f"Failed to crawl metadata sheet: {str(e)}"
                result["errors"].append(error_msg)
                result["success"] = False
                logger.error(error_msg)
                return result

            result["performance_metrics"]["crawling_time"] = (
                time.time() - crawling_start
            )

            # Step 3: Validate all discovered sheet pairs
            progress.update(
                1, description=f"Validating {len(sheet_pairs)} sheet pairs..."
            )
            validation_start = time.time()

            # Get all available validation criteria
            available_validations = get_available_validation_criteria()

            # Create validation checks for all available validators
            validation_checks = []
            for validation_criterion in available_validations:
                validation_checks.append(
                    {"id": validation_criterion["id"], "mode": validation_mode}
                )

            logger.info(
                f"Running {len(validation_checks)} validation checks in {validation_mode} mode"
            )

            # Process each sheet pair
            for pair_idx, sheet_pair in enumerate(sheet_pairs):
                pair_result = {
                    "row_number": sheet_pair["row_number"],
                    "sheet_name": sheet_pair["sheet_name"],
                    "input_sheets": sheet_pair["input_sheets"],
                    "output_sheets": sheet_pair["output_sheets"],
                    "input_results": [],
                    "output_results": [],
                    "success": True,
                    "errors": [],
                }

                logger.info(
                    f"Processing pair {pair_idx + 1}/{len(sheet_pairs)} (Row {sheet_pair['row_number']})"
                )

                # Validate input sheets
                for input_sheet in sheet_pair["input_sheets"]:
                    if not input_sheet:
                        continue

                    try:
                        logger.info(f"Validating input sheet: {input_sheet}")
                        input_result = execute_all_validations(
                            checks=validation_checks,
                            sheet_url=input_sheet,
                            auth_secret=auth_secret,
                            subject=subject,
                            target=target,
                            target_format=target_format,
                            preserve_visual_formatting=preserve_visual_formatting,
                        )

                        pair_result["input_results"].append(
                            {"sheet_url": input_sheet, "result": input_result}
                        )

                        # Update summary statistics
                        if input_result["success"]:
                            result["summary"]["total_input_fixes"] += input_result[
                                "summary"
                            ]["total_fixes"]
                            result["summary"]["total_input_flags"] += input_result[
                                "summary"
                            ]["total_flags"]
                        else:
                            pair_result["success"] = False
                            pair_result["errors"].extend(input_result.get("errors", []))
                            result["summary"]["total_errors"] += len(
                                input_result.get("errors", [])
                            )

                    except Exception as e:
                        error_msg = (
                            f"Failed to validate input sheet '{input_sheet}': {str(e)}"
                        )
                        pair_result["errors"].append(error_msg)
                        pair_result["success"] = False
                        result["summary"]["total_errors"] += 1
                        logger.error(error_msg)

                # Validate output sheets
                for output_sheet in sheet_pair["output_sheets"]:
                    if not output_sheet:
                        continue

                    try:
                        logger.info(f"Validating output sheet: {output_sheet}")
                        output_result = execute_all_validations(
                            checks=validation_checks,
                            sheet_url=output_sheet,
                            auth_secret=auth_secret,
                            subject=subject,
                            target=target,
                            target_format=target_format,
                            preserve_visual_formatting=preserve_visual_formatting,
                        )

                        pair_result["output_results"].append(
                            {"sheet_url": output_sheet, "result": output_result}
                        )

                        # Update summary statistics
                        if output_result["success"]:
                            result["summary"]["total_output_fixes"] += output_result[
                                "summary"
                            ]["total_fixes"]
                            result["summary"]["total_output_flags"] += output_result[
                                "summary"
                            ]["total_flags"]
                        else:
                            pair_result["success"] = False
                            pair_result["errors"].extend(
                                output_result.get("errors", [])
                            )
                            result["summary"]["total_errors"] += len(
                                output_result.get("errors", [])
                            )

                    except Exception as e:
                        error_msg = f"Failed to validate output sheet '{output_sheet}': {str(e)}"
                        pair_result["errors"].append(error_msg)
                        pair_result["success"] = False
                        result["summary"]["total_errors"] += 1
                        logger.error(error_msg)

                # Update pair statistics
                if pair_result["success"]:
                    result["summary"]["successful_pairs"] += 1
                else:
                    result["summary"]["failed_pairs"] += 1
                    result["errors"].extend(pair_result["errors"])

                result["processed_sheets"].append(pair_result)

            result["performance_metrics"]["validation_time"] = (
                time.time() - validation_start
            )

            # Step 4: Write back fixed URLs/paths to metadata sheet
            progress.update(
                1, description="Updating metadata sheet with fixed URLs/paths..."
            )
            logger.info("Writing fixed URLs/paths back to metadata sheet...")
            try:
                _write_fixed_urls_to_metadata(
                    metadata_spreadsheet_url=metadata_sheet_url,
                    auth_credentials=auth_credentials,
                    processed_sheets=result["processed_sheets"],
                    target_format=target_format or "sheets",
                )
                logger.info("Successfully updated metadata sheet with fixed URLs/paths")
            except Exception as e:
                error_msg = f"Failed to update metadata sheet: {str(e)}"
                result["errors"].append(error_msg)
                logger.error(error_msg)

            # Determine overall success
            if result["summary"]["failed_pairs"] > 0 or result["errors"]:
                result["success"] = False

            logger.info(
                f"Crawling and validation completed: {result['summary']['successful_pairs']}/{result['summary']['total_sheet_pairs']} pairs successful"
            )

        except Exception as e:
            error_msg = f"Crawling and validation failed: {str(e)}"
            result["errors"].append(error_msg)
            result["success"] = False
            logger.error(error_msg)

    # Calculate final performance metrics
    total_time = time.time() - start_time
    result["performance_metrics"]["total_time_seconds"] = total_time
    result["performance_metrics"]["pairs_per_second"] = (
        result["summary"]["total_sheet_pairs"] / total_time if total_time > 0 else 0
    )

    # Display results summary
    if result.get("errors"):
        error_details = f"{len(result['errors'])} errors occurred"
        show_error("Crawling completed with errors", error_details)
    else:
        success_msg = f"Successfully crawled and validated {result['summary']['total_sheet_pairs']} sheet pairs"
        details = f"Completed in {total_time:.2f} seconds | {result['summary']['total_input_fixes'] + result['summary']['total_output_fixes']} total fixes applied"
        show_success(success_msg, details)

    return result


def _handle_target_output(
    source: str,
    target: str,
    target_format: str | None,
    auth_credentials: dict[str, Any] | None,
    auth_secret: str | None,
    preserve_visual_formatting: bool = True,
) -> dict[str, Any]:
    """Handle target output for validation results.

    Args:
        source: Source spreadsheet URL or path
        target: Target destination (Google Drive folder ID, "local", or None)
        target_format: Format specification ("sheets" or "excel")
        auth_credentials: Authentication credentials for spreadsheet operations
        auth_secret: Base64 encoded auth secret for Google Sheets
        preserve_visual_formatting: Whether to preserve visual formatting during conversion

    Returns:
        Dict with keys: success, output_path, error
    """
    try:
        from urarovite.utils.generic_spreadsheet import convert_spreadsheet_format
        from urarovite.utils.drive import duplicate_file_to_drive_folder
        from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
        from pathlib import Path
        import time

        # Validate target_format parameter
        if target_format and target_format not in ["sheets", "excel"]:
            return {
                "success": False,
                "output_path": None,
                "error": f"Invalid target_format '{target_format}'. Must be 'sheets' or 'excel'",
            }

        # Determine source format
        source_is_google = isinstance(source, str) and (
            "docs.google.com" in source or "sheets.google.com" in source
        )

        # Auto-detect format if not specified
        if not target_format:
            target_format = "sheets" if source_is_google else "excel"

        # Validate format constraints
        # For Google Sheets format, allow:
        # - Explicit folder IDs (target != "local" and target is not None)
        # - Intelligent defaults (target == "" when source is Google Sheets)
        is_remote_target = (target != "local" and target is not None) or (
            target == "" and source_is_google
        )
        if target_format == "sheets" and not is_remote_target:
            return {
                "success": False,
                "output_path": None,
                "error": "Format 'sheets' requires a remote target (Google Drive folder ID) or intelligent defaults (empty target with Google Sheets source)",
            }

        # Handle different target scenarios
        if target is None:
            # Default behavior - save as Excel file to local directory
            target = "local"
            target_format = "excel"
        elif target == "" and source_is_google and target_format == "sheets":
            # Empty target with Google Sheets source - this should not happen with explicit target
            # But fallback gracefully
            return {
                "success": False,
                "output_path": None,
                "error": "Google Sheets format requires a specific target folder ID",
            }

        if target == "local":
            # Save to local directory
            if target_format != "excel":
                return {
                    "success": False,
                    "output_path": None,
                    "error": "Local target only supports 'excel' format",
                }

            # Create local output path
            timestamp = int(time.time())
            local_dir = Path("./output")
            local_dir.mkdir(exist_ok=True)

            # Generate filename based on source
            try:
                # Try to get the original spreadsheet name
                from urarovite.core.spreadsheet import SpreadsheetFactory

                with SpreadsheetFactory.create_spreadsheet(
                    source, auth_credentials
                ) as spreadsheet:
                    metadata = spreadsheet.get_metadata()
                    original_name = metadata.title
                    # Clean the name for filesystem use (preserve more valid characters)
                    # Allow: letters, numbers, spaces, hyphens, underscores, periods, parentheses, square brackets
                    clean_name = "".join(
                        c
                        for c in original_name
                        if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
                    ).rstrip()
                    if clean_name:
                        base_filename = f"{clean_name}.xlsx"
                    else:
                        # Fallback to timestamp-based naming
                        base_filename = f"validation_results_{timestamp}.xlsx"
            except Exception:
                # Fallback naming if metadata extraction fails
                if source_is_google:
                    base_filename = f"validation_results_{timestamp}.xlsx"
                else:
                    source_path = Path(source)
                    base_filename = f"{source_path.stem}.xlsx"

            target_path = local_dir / base_filename

            # Check if the exact target file already exists (avoid overwriting recent work)
            # Only reuse if the target has the SAME name (not timestamp-based files)
            if target_path.exists() and not base_filename.startswith(
                "validation_results_"
            ):
                # File exists and it's not a timestamp-based file, check if it's recent
                file_mtime = target_path.stat().st_mtime
                current_time = time.time()

                # If file was modified within last 60 seconds, reuse it
                if current_time - file_mtime < 60:
                    logger.info(f"Reusing existing output file: {target_path}")
                    return {
                        "success": True,
                        "output_path": str(target_path),
                        "error": None,
                    }

            # Convert to local Excel file
            conversion_result = convert_spreadsheet_format(
                source=source,
                target=str(target_path),
                auth_credentials={"auth_secret": auth_secret}
                if source_is_google
                else None,
                preserve_formulas=True,  # CRITICAL: Preserve formulas during duplication
                preserve_visual_formatting=preserve_visual_formatting,  # Preserve visual formatting
            )

            if conversion_result["success"]:
                return {"success": True, "output_path": str(target_path), "error": None}
            else:
                return {
                    "success": False,
                    "output_path": None,
                    "error": conversion_result["error"],
                }

        else:
            # Assume target is a Google Drive folder ID
            if not auth_secret:
                return {
                    "success": False,
                    "output_path": None,
                    "error": "Authentication required for Google Drive operations",
                }

            # Validate folder ID format (basic check)
            if not _is_valid_drive_folder_id(target):
                return {
                    "success": False,
                    "output_path": None,
                    "error": f"Invalid Google Drive folder ID format: {target}",
                }

            return _handle_drive_folder_target(
                source=source,
                folder_id=target,
                target_format=target_format,
                auth_secret=auth_secret,
            )

    except Exception as e:
        return {"success": False, "output_path": None, "error": str(e)}


def _create_pre_validation_duplicate(
    source: str,
    target: str | None,
    target_format: str | None,
    auth_credentials: dict[str, Any] | None,
    auth_secret: str | None,
    preserve_visual_formatting: bool = True,
) -> dict[str, Any]:
    """Create a duplicate of the source spreadsheet before validation.

    Args:
        source: Source spreadsheet URL or path
        target: Target destination (Google Drive folder ID, "local", or None)
        target_format: Format specification ("sheets" or "excel")
        auth_credentials: Authentication credentials for spreadsheet operations
        auth_secret: Base64 encoded auth secret for Google Sheets
        preserve_visual_formatting: Whether to preserve visual formatting during conversion

    Returns:
        Dict with keys: success, working_path, output_path, error
        - working_path: Path/URL to use for validation (may be temporary)
        - output_path: Final output path/URL for user reference
    """
    try:
        import time
        from pathlib import Path

        # Determine source format using automatic detection for Google Drive URLs
        source_is_google = False

        if isinstance(source, str):
            # Check if this is any Google Drive URL
            is_google_drive_url = (
                "drive.google.com" in source
                or "docs.google.com" in source
                or "sheets.google.com" in source
            )

            if is_google_drive_url and auth_secret:
                # Get actual file type from Google Drive API
                from urarovite.utils.drive import get_file_metadata

                try:
                    metadata = get_file_metadata(source, auth_secret)
                    if metadata["success"]:
                        source_is_google = metadata["is_google_sheets"]
                    else:
                        # If we can't get metadata, fall back to URL detection
                        source_is_google = "docs.google.com/spreadsheets" in source
                except Exception:
                    # If detection fails, fall back to URL detection
                    source_is_google = "docs.google.com/spreadsheets" in source
            else:
                # Local file or URL-based detection fallback
                source_is_google = "docs.google.com/spreadsheets" in source

        # Handle target and format defaults
        if target is None:
            target = "local"
            target_format = "excel"

        # Auto-detect format if not specified
        if not target_format:
            target_format = "sheets" if source_is_google else "excel"

        # Validate format constraints
        # For Google Sheets format, allow:
        # - Explicit folder IDs (target != "local" and target is not None)
        # - Intelligent defaults (target == "" when source is Google Sheets)
        is_remote_target = (target != "local" and target is not None) or (
            target == "" and source_is_google
        )
        if target_format == "sheets" and not is_remote_target:
            return {
                "success": False,
                "working_path": None,
                "output_path": None,
                "error": "Format 'sheets' requires a remote target (Google Drive folder ID) or intelligent defaults (empty target with Google Sheets source)",
            }

        # Handle different target scenarios
        if target == "" and source_is_google and target_format == "sheets":
            # Empty target with Google Sheets source - this should not happen with explicit target
            # But fallback gracefully
            return {
                "success": False,
                "working_path": None,
                "output_path": None,
                "error": "Google Sheets format requires a specific target folder ID",
            }

        if target == "local":
            # Create duplicate in temp first, then move to output later
            timestamp = int(time.time())
            temp_dir = Path("./temp")
            temp_dir.mkdir(exist_ok=True)
            output_dir = Path("./output")
            output_dir.mkdir(exist_ok=True)

            # Generate filename based on source
            if source_is_google:
                # For Google Sheets, create properly named file directly (no separate duplicate needed)
                try:
                    from urarovite.core.spreadsheet import SpreadsheetFactory

                    with SpreadsheetFactory.create_spreadsheet(
                        source, auth_credentials
                    ) as spreadsheet:
                        metadata = spreadsheet.get_metadata()
                        original_name = metadata.title
                        clean_name = "".join(
                            c
                            for c in original_name
                            if c.isalnum() or c in (" ", "-", "_", ".", "(", ")")
                        ).rstrip()
                        if clean_name:
                            base_filename = f"{clean_name}.xlsx"
                        else:
                            base_filename = f"validation_duplicate_{timestamp}.xlsx"
                except Exception:
                    # Fallback to timestamp if metadata extraction fails
                    base_filename = f"validation_duplicate_{timestamp}.xlsx"
            else:
                # For Excel files, create duplicate with timestamp
                # Check if source is a URL (Google Drive link) vs local file
                if isinstance(source, str) and (
                    "drive.google.com" in source or "docs.google.com" in source
                ):
                    # This is a Google Drive URL - try to get the actual file title
                    try:
                        from urarovite.utils.drive import extract_google_file_id
                        from urarovite.auth.google_drive import (
                            create_drive_service_from_encoded_creds,
                        )

                        file_id = extract_google_file_id(source)
                        if file_id and auth_secret:
                            drive_service = create_drive_service_from_encoded_creds(
                                auth_secret
                            )
                            file_metadata = (
                                drive_service.files()
                                .get(
                                    fileId=file_id,
                                    fields="name",
                                    supportsAllDrives=True,
                                )
                                .execute()
                            )

                            drive_name = file_metadata.get("name", "")
                            if drive_name:
                                # Clean the name for filesystem use
                                clean_name = "".join(
                                    c
                                    if c.isalnum()
                                    or c in (" ", "-", "_", ".", "(", ")", "[", "]")
                                    else "_"
                                    for c in drive_name
                                ).rstrip()
                                if clean_name and not clean_name.endswith(".xlsx"):
                                    base_filename = (
                                        f"{clean_name}_duplicate_{timestamp}.xlsx"
                                    )
                                else:
                                    base_filename = f"{clean_name.replace('.xlsx', '')}_duplicate_{timestamp}.xlsx"
                            else:
                                base_filename = (
                                    f"excel_from_drive_duplicate_{timestamp}.xlsx"
                                )
                        else:
                            base_filename = (
                                f"excel_from_drive_duplicate_{timestamp}.xlsx"
                            )
                    except Exception:
                        # Fallback to generic name if title extraction fails
                        base_filename = f"excel_from_drive_duplicate_{timestamp}.xlsx"
                else:
                    # This is a local Excel file - use its filename
                    source_path = Path(source)
                    base_filename = f"{source_path.stem}_duplicate_{timestamp}.xlsx"

            # Create in temp directory first
            temp_path = temp_dir / base_filename
            final_output_path = output_dir / base_filename

            # Check for existing files based on source type
            if source_is_google:
                # For Google Sheets -> Excel: Check if properly named file exists and is recent
                if temp_path.exists():
                    file_mtime = temp_path.stat().st_mtime
                    current_time = time.time()

                    # If file was modified within last 60 seconds, reuse it
                    if current_time - file_mtime < 60:
                        logger.info(f"Reusing existing temp file: {temp_path}")
                        return {
                            "success": True,
                            "working_path": str(temp_path),
                            "output_path": str(
                                final_output_path
                            ),  # Will be moved later
                            "error": None,
                        }
            else:
                # For Excel files: Check for recent timestamp-based duplicates
                existing_duplicates = []
                current_time = time.time()

                for existing_file in temp_dir.glob("*_duplicate_*.xlsx"):
                    try:
                        # Extract timestamp from filename
                        name_parts = existing_file.stem.split("_")
                        if len(name_parts) >= 3 and name_parts[-1].isdigit():
                            file_timestamp = int(name_parts[-1])
                            # If file was created within last 60 seconds, consider it recent
                            if current_time - file_timestamp < 60:
                                existing_duplicates.append(
                                    (existing_file, file_timestamp)
                                )
                    except (ValueError, IndexError):
                        continue

                # Use the most recent duplicate if available
                if existing_duplicates:
                    existing_duplicates.sort(
                        key=lambda x: x[1], reverse=True
                    )  # Sort by timestamp, newest first
                    existing_temp_path = existing_duplicates[0][0]
                    logger.info(
                        f"Reusing existing temp duplicate: {existing_temp_path}"
                    )

                    return {
                        "success": True,
                        "working_path": str(existing_temp_path),
                        "output_path": str(final_output_path),  # Will be moved later
                        "error": None,
                    }

            # Convert to local Excel file
            from urarovite.utils.generic_spreadsheet import convert_spreadsheet_format

            # For Google Drive URLs, we always need auth credentials regardless of file type
            # because even Excel files on Google Drive require authentication to access
            needs_auth = isinstance(source, str) and (
                "drive.google.com" in source
                or "docs.google.com" in source
                or "sheets.google.com" in source
            )

            conversion_result = convert_spreadsheet_format(
                source=source,
                target=str(temp_path),
                auth_credentials={"auth_secret": auth_secret} if needs_auth else None,
                preserve_formulas=True,  # CRITICAL: Preserve formulas during duplication
                preserve_visual_formatting=preserve_visual_formatting,  # Preserve visual formatting
                source_file_type="excel",  # Override URL-based detection with correct type
            )

            if conversion_result["success"]:
                # For local target, move from temp to output after validation
                return {
                    "success": True,
                    "working_path": str(temp_path),
                    "output_path": str(final_output_path),  # Will be moved later
                    "error": None,
                    "needs_move_to_output": True,  # Flag to indicate move needed
                }
            else:
                return {
                    "success": False,
                    "working_path": None,
                    "output_path": None,
                    "error": conversion_result["error"],
                }

        else:
            # Assume target is a Google Drive folder ID
            if not auth_secret:
                return {
                    "success": False,
                    "working_path": None,
                    "output_path": None,
                    "error": "Authentication required for Google Drive operations",
                }

            # Validate folder ID format
            if not _is_valid_drive_folder_id(target):
                return {
                    "success": False,
                    "working_path": None,
                    "output_path": None,
                    "error": f"Invalid Google Drive folder ID format: {target}",
                }

            return _create_drive_folder_duplicate(
                source=source,
                folder_id=target,
                target_format=target_format,
                auth_secret=auth_secret,
                preserve_visual_formatting=preserve_visual_formatting,
            )

    except Exception as e:
        return {
            "success": False,
            "working_path": None,
            "output_path": None,
            "error": str(e),
        }


def _create_drive_folder_duplicate(
    source: str,
    folder_id: str,
    target_format: str,
    auth_secret: str,
    preserve_visual_formatting: bool = True,
) -> dict[str, Any]:
    """Create duplicate in Google Drive folder."""
    try:
        from urarovite.utils.drive import duplicate_file_to_drive_folder
        from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
        from urarovite.auth.google_sheets import (
            create_sheets_service_from_encoded_creds,
        )
        import time

        # Determine source format
        source_is_google = isinstance(source, str) and (
            "docs.google.com" in source or "sheets.google.com" in source
        )

        if target_format == "sheets":
            # Save as Google Sheets to Drive folder
            if source_is_google:
                # Google Sheets to Google Sheets - use Drive API to duplicate
                drive_service = create_drive_service_from_encoded_creds(auth_secret)
                sheets_service = create_sheets_service_from_encoded_creds(auth_secret)
                folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

                result = duplicate_file_to_drive_folder(
                    drive_service=drive_service,
                    file_url=source,
                    folder_url=folder_url,
                    prefix_file_name="validation_",
                    sheets_service=sheets_service,
                )

                if result["success"]:
                    return {
                        "success": True,
                        "working_path": result[
                            "url"
                        ],  # Use the duplicate for validation
                        "output_path": result["url"],
                        "error": None,
                    }
                else:
                    return {
                        "success": False,
                        "working_path": None,
                        "output_path": None,
                        "error": result.get(
                            "error", "Failed to duplicate to Drive folder"
                        ),
                    }
            else:
                # Excel to Google Sheets - OPTIMIZED WORKFLOW:
                # 1. Create local Excel duplicate for validation work
                # 2. Apply all fixes to Excel file (much faster than Google Sheets API)
                # 3. Convert the fixed Excel file to Google Sheets
                # 4. Upload to Drive folder
                try:
                    from urarovite.utils.generic_spreadsheet import (
                        convert_spreadsheet_format,
                    )
                    from urarovite.utils.sheets import create_new_spreadsheet_in_folder
                    from urarovite.auth.google_sheets import get_gspread_client
                    from urarovite.utils.generic_spreadsheet import (
                        convert_excel_to_google_sheets,
                    )
                    import time
                    from pathlib import Path

                    # Step 1: Create local Excel duplicate for validation work
                    timestamp = int(time.time())
                    temp_dir = Path("./temp")
                    temp_dir.mkdir(exist_ok=True)
                    temp_excel_path = temp_dir / f"validation_work_{timestamp}.xlsx"

                    # Copy Excel file to temp location for validation work
                    # For Google Drive URLs, we always need auth credentials regardless of file type
                    needs_auth = isinstance(source, str) and (
                        "drive.google.com" in source
                        or "docs.google.com" in source
                        or "sheets.google.com" in source
                    )

                    excel_copy_result = convert_spreadsheet_format(
                        source=source,
                        target=str(temp_excel_path),
                        auth_credentials={"auth_secret": auth_secret}
                        if needs_auth
                        else None,
                        preserve_formulas=True,
                        preserve_visual_formatting=preserve_visual_formatting,
                        source_file_type="excel",  # Override URL-based detection with correct type
                    )

                    if not excel_copy_result["success"]:
                        return {
                            "success": False,
                            "working_path": None,
                            "output_path": None,
                            "error": f"Failed to create Excel working copy: {excel_copy_result['error']}",
                        }

                    # Step 2: Return the Excel working file for validation
                    # (Validation fixes will be applied to this Excel file)
                    # Step 3 (conversion to Google Sheets) will happen after validation
                    return {
                        "success": True,
                        "working_path": str(temp_excel_path),
                        "output_path": None,  # Will be set after conversion
                        "error": None,
                        "conversion_pending": {
                            "target_format": "sheets",
                            "folder_id": folder_id,
                            "auth_secret": auth_secret,
                            "spreadsheet_name": _get_spreadsheet_name_from_source(
                                source
                            ),
                        },
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "working_path": None,
                        "output_path": None,
                        "error": f"Excel to Google Sheets preparation failed: {str(e)}",
                    }

        elif target_format == "excel":
            # Save as Excel to Drive folder
            # First create local duplicate, then upload to Drive
            timestamp = int(time.time())
            temp_dir = Path("./temp")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / f"validation_duplicate_{timestamp}.xlsx"

            # Convert to temporary Excel file
            from urarovite.utils.generic_spreadsheet import convert_spreadsheet_format

            conversion_result = convert_spreadsheet_format(
                source=source,
                target=str(temp_path),
                auth_credentials={"auth_secret": auth_secret}
                if source_is_google
                else None,
                preserve_formulas=True,  # CRITICAL: Preserve formulas during duplication
                preserve_visual_formatting=preserve_visual_formatting,  # Preserve visual formatting
            )

            if not conversion_result["success"]:
                return {
                    "success": False,
                    "working_path": None,
                    "output_path": None,
                    "error": f"Conversion failed: {conversion_result['error']}",
                }

            # For now, use the local file for validation
            # TODO: Implement actual upload to Drive folder
            return {
                "success": True,
                "working_path": str(temp_path),
                "output_path": str(temp_path),
                "error": None,
                "note": "Excel file created locally. Drive upload not yet implemented.",
            }

        else:
            return {
                "success": False,
                "working_path": None,
                "output_path": None,
                "error": f"Unsupported target_format: {target_format}",
            }

    except Exception as e:
        return {
            "success": False,
            "working_path": None,
            "output_path": None,
            "error": str(e),
        }


def _is_valid_drive_folder_id(folder_id: str) -> bool:
    """Check if string looks like a valid Google Drive folder ID."""
    # Basic validation - Drive IDs are typically 25-50 alphanumeric characters
    if not folder_id or not isinstance(folder_id, str):
        return False
    import re

    return bool(re.match(r"^[a-zA-Z0-9_-]{20,50}$", folder_id))


def _get_spreadsheet_name_from_source(source: str) -> str:
    """Extract a clean spreadsheet name from source path or URL."""
    from pathlib import Path

    # For Excel files, use the filename without extension
    if not ("docs.google.com" in source or "sheets.google.com" in source):
        source_path = Path(source)
        base_name = source_path.stem
    else:
        # For Google Sheets, we'd need to fetch metadata, but for now use a fallback
        base_name = "Converted_Spreadsheet"

    # Clean the name for Google Sheets (preserve more characters)
    # Google Sheets allows more characters than Excel sheet names
    clean_name = "".join(
        c
        for c in base_name
        if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
    ).rstrip()
    if not clean_name:
        clean_name = "Converted_Spreadsheet"

    return clean_name


def _write_fixed_urls_to_metadata(
    metadata_spreadsheet_url: str,
    auth_credentials: dict[str, Any] | None,
    processed_sheets: list[dict[str, Any]],
    target_format: str,
) -> None:
    """Write fixed URLs/paths back to the metadata spreadsheet.

    Args:
        metadata_spreadsheet_url: URL or path to the metadata spreadsheet
        auth_credentials: Authentication credentials for spreadsheet operations
        processed_sheets: List of processed sheet results with fixed URLs/paths
        target_format: Target format ("sheets" or "excel") to determine column names

    Raises:
        ValidationError: If unable to update the metadata spreadsheet
    """
    from urarovite.core.spreadsheet import SpreadsheetFactory
    from pathlib import Path
    import os

    logger = logging.getLogger(__name__)

    try:
        # Open the metadata spreadsheet for writing
        with SpreadsheetFactory.create_spreadsheet(
            metadata_spreadsheet_url, auth_credentials
        ) as metadata_spreadsheet:
            metadata_info = metadata_spreadsheet.get_metadata()

            # Get list of sheet names that have processed data
            processed_sheet_names = set(
                result.get("sheet_name") for result in processed_sheets
            )

            # Track if we've already added columns to avoid duplicates
            columns_added = False

            # Process each sheet in the metadata spreadsheet that has processed data
            for sheet_name in metadata_info.sheet_names:
                # Only process sheets that have corresponding processed data
                if sheet_name not in processed_sheet_names:
                    logger.info(f"Skipping sheet '{sheet_name}' - no processed data")
                    continue

                logger.info(
                    f"Processing metadata sheet '{sheet_name}' with processed data"
                )
                try:
                    # Get current data from the sheet
                    sheet_data = metadata_spreadsheet.get_sheet_data(sheet_name)

                    if not sheet_data.values or len(sheet_data.values) < 2:
                        continue  # Skip empty sheets

                    # Get header row and find existing columns
                    headers = sheet_data.values[0] if sheet_data.values else []
                    headers = [
                        str(h) if h else "" for h in headers
                    ]  # Ensure all headers are strings

                    # Determine column names based on target format
                    if target_format == "sheets":
                        input_fixed_col = "input_sheet_url_fixed"
                        output_fixed_col = "example_output_sheet_url_fixed"
                    else:  # excel
                        input_fixed_col = "input_sheet_path_fixed"
                        output_fixed_col = "example_output_sheet_path_fixed"

                    # Define validator output column names
                    input_fixes_col = "input_fixes_applied"
                    input_flags_col = "input_flags_found"
                    input_summary_col = "input_validation_summary"
                    input_errors_col = "input_validation_errors"

                    output_fixes_col = "output_fixes_applied"
                    output_flags_col = "output_flags_found"
                    output_summary_col = "output_validation_summary"
                    output_errors_col = "output_validation_errors"

                    # Find or create column indices for all new columns
                    column_indices = {}

                    # Define all columns we want to track
                    all_columns = [
                        input_fixed_col,
                        output_fixed_col,
                        input_fixes_col,
                        input_flags_col,
                        input_summary_col,
                        input_errors_col,
                        output_fixes_col,
                        output_flags_col,
                        output_summary_col,
                        output_errors_col,
                    ]

                    # Look for existing columns (exact match first, then case-insensitive)
                    for i, header in enumerate(headers):
                        header_str = str(header).strip()
                        header_lower = header_str.lower()
                        for col_name in all_columns:
                            # Exact match first
                            if header_str == col_name:
                                column_indices[col_name] = i
                                break
                            # Case-insensitive match
                            elif header_lower == col_name.lower():
                                column_indices[col_name] = i
                                break

                    # Add new columns if they don't exist (only on first processed sheet to avoid duplicates)
                    headers_modified = False
                    if not columns_added:
                        for col_name in all_columns:
                            if col_name not in column_indices:
                                column_indices[col_name] = len(headers)
                                headers.append(col_name)
                                headers_modified = True
                        if headers_modified:
                            columns_added = True  # Mark that we've added columns
                    else:
                        # For subsequent sheets, just map existing column positions
                        for col_name in all_columns:
                            if col_name not in column_indices:
                                # Try to find the column by searching headers again
                                for i, header in enumerate(headers):
                                    if str(header).strip().lower() == col_name.lower():
                                        column_indices[col_name] = i
                                        break

                    # Prepare updated data
                    updated_values = []

                    # Add header row (potentially modified)
                    updated_values.append(headers)

                    # Process data rows
                    for row_idx, row in enumerate(
                        sheet_data.values[1:], start=2
                    ):  # Skip header
                        # Extend row to match new column count if needed
                        updated_row = list(row) + [""] * (len(headers) - len(row))

                        # Find corresponding processed sheet results
                        matching_results = [
                            result
                            for result in processed_sheets
                            if result.get("sheet_name") == sheet_name
                            and result.get("row_number") == row_idx
                        ]

                        if matching_results:
                            result = matching_results[0]

                            # Process input sheets
                            input_fixed_urls = []
                            input_total_fixes = 0
                            input_total_flags = 0
                            input_summaries = []
                            input_error_list = []

                            for input_result in result.get("input_results", []):
                                validation_result = input_result.get("result", {})

                                # Collect fixed URLs/paths
                                if target_format == "sheets":
                                    # For Google Sheets, use the target_output URL if available
                                    if validation_result.get("target_output"):
                                        input_fixed_urls.append(
                                            validation_result["target_output"]
                                        )
                                    elif validation_result.get("duplicate_created"):
                                        input_fixed_urls.append(
                                            validation_result["duplicate_created"]
                                        )
                                    else:
                                        # Fallback: Look for duplicate files in the output directory
                                        # This handles cases where Excel files were created instead of Google Sheets
                                        input_sheet_url = input_result.get(
                                            "sheet_url", ""
                                        )
                                        if input_sheet_url:
                                            # Try to find the duplicate file based on naming patterns
                                            from pathlib import Path

                                            output_dir = Path("output")
                                            if output_dir.exists():
                                                # Look for duplicate files that might correspond to this sheet
                                                for file_path in output_dir.glob(
                                                    "*duplicate*.xlsx"
                                                ):
                                                    input_fixed_urls.append(
                                                        f"./output/{file_path.name}"
                                                    )
                                                    break  # Just take the first match for now
                                else:
                                    # For Excel, use relative paths
                                    if validation_result.get("target_output"):
                                        abs_path = validation_result["target_output"]
                                        rel_path = _get_relative_path(
                                            metadata_spreadsheet_url, abs_path
                                        )
                                        input_fixed_urls.append(rel_path)
                                    else:
                                        # Fallback: Look for duplicate files in the output directory
                                        from pathlib import Path

                                        output_dir = Path("output")
                                        if output_dir.exists():
                                            # Look for duplicate files that might correspond to this sheet
                                            for file_path in output_dir.glob(
                                                "*duplicate*.xlsx"
                                            ):
                                                rel_path = _get_relative_path(
                                                    metadata_spreadsheet_url,
                                                    str(file_path.absolute()),
                                                )
                                                input_fixed_urls.append(rel_path)
                                                break  # Just take the first match for now

                                # Collect validation statistics
                                summary = validation_result.get("summary", {})
                                input_total_fixes += summary.get("total_fixes", 0)
                                input_total_flags += summary.get("total_flags", 0)

                                # Collect validation summaries
                                if summary.get("successful_validations", 0) > 0:
                                    input_summaries.append(
                                        f"✅ {summary.get('successful_validations', 0)} successful"
                                    )
                                if summary.get("failed_validations", 0) > 0:
                                    input_summaries.append(
                                        f"❌ {summary.get('failed_validations', 0)} failed"
                                    )

                                # Collect errors
                                errors = validation_result.get("errors", [])
                                input_error_list.extend(
                                    errors[:3]
                                )  # Limit to first 3 errors per sheet

                            # Process output sheets
                            output_fixed_urls = []
                            output_total_fixes = 0
                            output_total_flags = 0
                            output_summaries = []
                            output_error_list = []

                            for output_result in result.get("output_results", []):
                                validation_result = output_result.get("result", {})

                                # Collect fixed URLs/paths
                                if target_format == "sheets":
                                    # For Google Sheets, use the target_output URL if available
                                    if validation_result.get("target_output"):
                                        output_fixed_urls.append(
                                            validation_result["target_output"]
                                        )
                                    elif validation_result.get("duplicate_created"):
                                        output_fixed_urls.append(
                                            validation_result["duplicate_created"]
                                        )
                                    else:
                                        # Fallback: Look for duplicate files in the output directory
                                        # This handles cases where Excel files were created instead of Google Sheets
                                        output_sheet_url = output_result.get(
                                            "sheet_url", ""
                                        )
                                        if output_sheet_url:
                                            # Try to find the duplicate file based on naming patterns
                                            from pathlib import Path

                                            output_dir = Path("output")
                                            if output_dir.exists():
                                                # Look for duplicate files that might correspond to this sheet
                                                for file_path in output_dir.glob(
                                                    "*duplicate*.xlsx"
                                                ):
                                                    output_fixed_urls.append(
                                                        f"./output/{file_path.name}"
                                                    )
                                                    break  # Just take the first match for now
                                else:
                                    # For Excel, use relative paths
                                    if validation_result.get("target_output"):
                                        abs_path = validation_result["target_output"]
                                        rel_path = _get_relative_path(
                                            metadata_spreadsheet_url, abs_path
                                        )
                                        output_fixed_urls.append(rel_path)
                                    else:
                                        # Fallback: Look for duplicate files in the output directory
                                        from pathlib import Path

                                        output_dir = Path("output")
                                        if output_dir.exists():
                                            # Look for duplicate files that might correspond to this sheet
                                            for file_path in output_dir.glob(
                                                "*duplicate*.xlsx"
                                            ):
                                                rel_path = _get_relative_path(
                                                    metadata_spreadsheet_url,
                                                    str(file_path.absolute()),
                                                )
                                                output_fixed_urls.append(rel_path)
                                                break  # Just take the first match for now

                                # Collect validation statistics
                                summary = validation_result.get("summary", {})
                                output_total_fixes += summary.get("total_fixes", 0)
                                output_total_flags += summary.get("total_flags", 0)

                                # Collect validation summaries
                                if summary.get("successful_validations", 0) > 0:
                                    output_summaries.append(
                                        f"✅ {summary.get('successful_validations', 0)} successful"
                                    )
                                if summary.get("failed_validations", 0) > 0:
                                    output_summaries.append(
                                        f"❌ {summary.get('failed_validations', 0)} failed"
                                    )

                                # Collect errors
                                errors = validation_result.get("errors", [])
                                output_error_list.extend(
                                    errors[:3]
                                )  # Limit to first 3 errors per sheet

                            # Update the row with all collected data
                            if input_fixed_urls and input_fixed_col in column_indices:
                                updated_row[column_indices[input_fixed_col]] = (
                                    "; ".join(input_fixed_urls)
                                )

                            if output_fixed_urls and output_fixed_col in column_indices:
                                updated_row[column_indices[output_fixed_col]] = (
                                    "; ".join(output_fixed_urls)
                                )

                            # Update input validation columns
                            if (
                                input_total_fixes > 0
                                and input_fixes_col in column_indices
                            ):
                                updated_row[column_indices[input_fixes_col]] = str(
                                    input_total_fixes
                                )

                            if (
                                input_total_flags > 0
                                and input_flags_col in column_indices
                            ):
                                updated_row[column_indices[input_flags_col]] = str(
                                    input_total_flags
                                )

                            if input_summaries and input_summary_col in column_indices:
                                updated_row[column_indices[input_summary_col]] = (
                                    "; ".join(input_summaries)
                                )

                            if input_error_list and input_errors_col in column_indices:
                                error_text = "; ".join(
                                    input_error_list[:5]
                                )  # Limit to 5 errors total
                                if len(input_error_list) > 5:
                                    error_text += f"; +{len(input_error_list) - 5} more"
                                updated_row[column_indices[input_errors_col]] = (
                                    error_text
                                )

                            # Update output validation columns
                            if (
                                output_total_fixes > 0
                                and output_fixes_col in column_indices
                            ):
                                updated_row[column_indices[output_fixes_col]] = str(
                                    output_total_fixes
                                )

                            if (
                                output_total_flags > 0
                                and output_flags_col in column_indices
                            ):
                                updated_row[column_indices[output_flags_col]] = str(
                                    output_total_flags
                                )

                            if (
                                output_summaries
                                and output_summary_col in column_indices
                            ):
                                updated_row[column_indices[output_summary_col]] = (
                                    "; ".join(output_summaries)
                                )

                            if (
                                output_error_list
                                and output_errors_col in column_indices
                            ):
                                error_text = "; ".join(
                                    output_error_list[:5]
                                )  # Limit to 5 errors total
                                if len(output_error_list) > 5:
                                    error_text += (
                                        f"; +{len(output_error_list) - 5} more"
                                    )
                                updated_row[column_indices[output_errors_col]] = (
                                    error_text
                                )

                        updated_values.append(updated_row)

                    # Update the sheet with new data
                    if headers_modified or any(
                        result.get("input_results") or result.get("output_results")
                        for result in processed_sheets
                        if result.get("sheet_name") == sheet_name
                    ):
                        logger.info(
                            f"Updating sheet '{sheet_name}' with fixed URLs/paths"
                        )
                        # Use a dynamic range that accommodates new columns
                        from urarovite.utils.sheets import col_index_to_letter

                        max_cols = (
                            max(len(row) for row in updated_values)
                            if updated_values
                            else len(headers)
                        )
                        end_col_letter = col_index_to_letter(max_cols - 1)
                        range_name = f"A1:{end_col_letter}{len(updated_values)}"

                        metadata_spreadsheet.update_sheet_data(
                            sheet_name=sheet_name,
                            values=updated_values,
                            range_name=range_name,
                        )

                except Exception as e:
                    logger.error(f"Error updating sheet '{sheet_name}': {str(e)}")
                    continue

            # Save changes
            metadata_spreadsheet.save()
            logger.info("Successfully saved metadata sheet with fixed URLs/paths")

    except Exception as e:
        raise ValidationError(f"Failed to write fixed URLs to metadata sheet: {str(e)}")


def _get_relative_path(metadata_location: str, target_path: str) -> str:
    """Get relative path from metadata location to target file.

    Args:
        metadata_location: Location of the metadata spreadsheet
        target_path: Absolute path to the target file

    Returns:
        Relative path string
    """
    from pathlib import Path

    try:
        # For Google Sheets metadata, use relative to current working directory
        if "docs.google.com" in metadata_location:
            current_dir = Path.cwd()
            target_file = Path(target_path)
            return str(target_file.relative_to(current_dir))

        # For Excel metadata files, use relative to the metadata file location
        metadata_path = Path(metadata_location)
        target_file = Path(target_path)

        # Get relative path from metadata file directory to target file
        return str(target_file.relative_to(metadata_path.parent))

    except Exception:
        # If relative path calculation fails, return just the filename
        return Path(target_path).name


def _handle_drive_folder_target(
    source: str,
    folder_id: str,
    target_format: str,
    auth_secret: str,
    preserve_visual_formatting: bool = True,
) -> dict[str, Any]:
    """Handle saving to Google Drive folder."""
    try:
        from urarovite.utils.generic_spreadsheet import convert_spreadsheet_format
        from urarovite.utils.drive import duplicate_file_to_drive_folder
        from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
        from urarovite.auth.google_sheets import (
            create_sheets_service_from_encoded_creds,
        )
        import time

        # Determine source format
        source_is_google = isinstance(source, str) and (
            "docs.google.com" in source or "sheets.google.com" in source
        )

        if target_format == "sheets":
            # Save as Google Sheets to Drive folder
            if source_is_google:
                # Google Sheets to Google Sheets - use Drive API to duplicate
                drive_service = create_drive_service_from_encoded_creds(auth_secret)
                sheets_service = create_sheets_service_from_encoded_creds(auth_secret)
                folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

                result = duplicate_file_to_drive_folder(
                    drive_service=drive_service,
                    file_url=source,
                    folder_url=folder_url,
                    prefix_file_name=None,  # Use original name without prefix
                    sheets_service=sheets_service,
                )

                if result["success"]:
                    return {
                        "success": True,
                        "output_path": result["url"],
                        "error": None,
                    }
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "error": result.get(
                            "error", "Failed to duplicate to Drive folder"
                        ),
                    }
            else:
                # Excel to Google Sheets - convert Excel to Sheets and upload to Drive
                try:
                    # Step 1: Create a new Google Sheets document in the Drive folder
                    from urarovite.utils.sheets import create_new_spreadsheet_in_folder
                    from urarovite.auth.google_sheets import get_gspread_client
                    from urarovite.utils.generic_spreadsheet import (
                        convert_excel_to_google_sheets,
                    )
                    import time

                    # Create Google Sheets service
                    gspread_client = get_gspread_client(auth_secret)

                    # Generate name based on source Excel file
                    from pathlib import Path

                    source_path = Path(source)
                    base_name = source_path.stem  # Get filename without extension

                    # Clean the name for Google Sheets (preserve more characters)
                    # Google Sheets allows more characters than Excel sheet names
                    clean_name = "".join(
                        c
                        for c in base_name
                        if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
                    ).rstrip()
                    if not clean_name:
                        clean_name = "Converted_Spreadsheet"

                    spreadsheet_name = clean_name

                    # Create new Google Sheets document in the specified folder
                    new_spreadsheet = create_new_spreadsheet_in_folder(
                        gspread_client=gspread_client,
                        folder_id=folder_id,
                        spreadsheet_name=spreadsheet_name,
                    )

                    if not new_spreadsheet:
                        return {
                            "success": False,
                            "output_path": None,
                            "error": "Failed to create new Google Sheets document in Drive folder",
                        }

                    # Step 2: Convert Excel data to the new Google Sheets
                    new_sheets_url = f"https://docs.google.com/spreadsheets/d/{new_spreadsheet.id}/edit"

                    conversion_result = convert_excel_to_google_sheets(
                        excel_file_path=source,
                        google_sheets_url=new_sheets_url,
                        auth_credentials={"auth_secret": auth_secret},
                        create_new_sheets=True,
                    )

                    if conversion_result["success"]:
                        return {
                            "success": True,
                            "output_path": new_sheets_url,
                            "error": None,
                        }
                    else:
                        return {
                            "success": False,
                            "output_path": None,
                            "error": f"Excel to Google Sheets conversion failed: {conversion_result['error']}",
                        }

                except Exception as e:
                    return {
                        "success": False,
                        "output_path": None,
                        "error": f"Excel to Google Sheets conversion failed: {str(e)}",
                    }

        elif target_format == "excel":
            # Save as Excel to Drive folder
            # First convert to local Excel, then upload to Drive
            from pathlib import Path

            timestamp = int(time.time())
            temp_path = f"./temp/validation_results_{timestamp}.xlsx"
            Path("./temp").mkdir(exist_ok=True)

            # Convert to temporary Excel file
            conversion_result = convert_spreadsheet_format(
                source=source,
                target=temp_path,
                auth_credentials={"auth_secret": auth_secret}
                if source_is_google
                else None,
                preserve_formulas=True,  # CRITICAL: Preserve formulas during duplication
                preserve_visual_formatting=preserve_visual_formatting,  # Preserve visual formatting
            )

            if not conversion_result["success"]:
                return {
                    "success": False,
                    "output_path": None,
                    "error": f"Conversion failed: {conversion_result['error']}",
                }

            # Upload Excel file to Drive folder
            # This would require implementing file upload to Drive
            # For now, return the local path
            return {
                "success": True,
                "output_path": temp_path,
                "error": None,
                "note": "Excel file created locally. Drive upload not yet implemented.",
            }

        else:
            return {
                "success": False,
                "output_path": None,
                "error": f"Unsupported target_format: {target_format}",
            }

    except Exception as e:
        return {"success": False, "output_path": None, "error": str(e)}


def process_forte_csv_batch(
    csv_file_path: str,
    auth_secret: str,
    target_folder_id: str,
    subject: str | None = None,
    validation_mode: str = "fix",
    preserve_visual_formatting: bool = True,
    output_file_path: str | None = None,
) -> dict[str, Any]:
    """Process a Forte export CSV file through the API.

    This function provides a centralized API endpoint for processing Forte CSV files,
    serving as the main entry point that the CLI and other interfaces should use.

    Args:
        csv_file_path: Path to the Forte export CSV file
        auth_secret: Base64 encoded service account credentials
        target_folder_id: Google Drive folder ID for output files
        subject: Email for domain-wide delegation (optional)
        validation_mode: Validation mode ("fix" or "flag")
        preserve_visual_formatting: Whether to preserve visual formatting during conversion
        output_file_path: Path for output CSV file (optional)

    Returns:
        Dictionary containing processing results and summary

    Example:
        >>> result = process_forte_csv_batch(
        ...     csv_file_path="/path/to/forte_export.csv",
        ...     auth_secret="eyJ0eXBlIjogInNlcnVpY2VfYWNjb3VudCIsIC4uLn0=",
        ...     target_folder_id="1A2B3C4D5E6F7G8H9I0J",
        ...     validation_mode="fix",
        ... )
        >>> print(f"Processed {result['summary']['total_sheets_processed']} sheets")
    """
    # Import shared processing logic
    from urarovite.utils.forte_processing import process_forte_csv

    # Call the shared processing function through the API
    return process_forte_csv(
        csv_file_path=csv_file_path,
        auth_secret=auth_secret,
        target_folder_id=target_folder_id,
        subject=subject,
        validation_mode=validation_mode,
        preserve_visual_formatting=preserve_visual_formatting,
        output_file_path=output_file_path,
    )
