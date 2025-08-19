"""
Forte CSV Processing Utilities

Shared functions for processing Forte export CSVs and performing bulk validation workflows.
This module provides the core logic used by both the CLI and bash script to ensure consistency.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from urarovite.utils.drive import duplicate_file_to_drive_folder
from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds


def process_forte_csv(
    csv_file_path: Union[str, Path],
    auth_secret: str,
    target_folder_id: str,
    subject: Optional[str] = None,
    validation_mode: str = "fix",
    preserve_visual_formatting: bool = True,
    output_file_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Process a Forte export CSV file and perform validation on all sheet URLs.

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
    """
    # Initialize result structure
    result = {
        "success": True,
        "summary": {
            "total_sheets_processed": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "total_validator_executions": 0,
            "total_fixes_applied": 0,
            "total_flags_found": 0,
            "files_copied": 0,
        },
        "detailed_results": [],
        "errors": [],
    }

    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)

        # Process each row
        for index, row in df.iterrows():
            row_result = process_csv_row(
                row,
                auth_secret,
                target_folder_id,
                subject,
                validation_mode,
                preserve_visual_formatting,
            )

            # Add row results to overall results
            result["detailed_results"].append(row_result)

            # Update summary statistics
            _update_summary_stats(result["summary"], row_result)

        # Generate output CSV if path provided
        if output_file_path:
            _generate_output_csv(df, result["detailed_results"], output_file_path)
            # Generate bulk review CSV
            _generate_bulk_review_csv(df, result["detailed_results"], output_file_path)

    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Error processing CSV: {str(e)}")
        logging.error(f"Error in process_forte_csv: {e}")

    return result


def process_csv_row(
    row: pd.Series,
    auth_secret: str,
    target_folder_id: str,
    subject: Optional[str] = None,
    validation_mode: str = "fix",
    preserve_visual_formatting: bool = True,
) -> Dict[str, Any]:
    """
    Process a single CSV row containing sheet URLs.

    Args:
        row: Pandas Series representing a CSV row
        auth_secret: Base64 encoded service account credentials
        target_folder_id: Google Drive folder ID for output files
        subject: Email for domain-wide delegation (optional)
        validation_mode: Validation mode ("fix" or "flag")
        preserve_visual_formatting: Whether to preserve visual formatting

    Returns:
        Dictionary containing row processing results
    """
    row_result = {
        "row_index": row.name,
        "input_sheet_results": [],
        "example_output_sheet_results": [],
    }

    # Process result input file URL (Forte processing results)
    input_url = None
    if pd.notna(row.get("result__fixed_input_excel_file")):
        input_url = row["result__fixed_input_excel_file"]
    elif pd.notna(row.get("input_sheet_url")):  # Fallback for non-Forte CSVs
        input_url = row["input_sheet_url"]

    if input_url:
        input_result = process_sheet_url(
            input_url,
            auth_secret,
            target_folder_id,
            subject,
            validation_mode,
            preserve_visual_formatting,
        )
        row_result["input_sheet_results"].append(input_result)

    # Process result output file URL (Forte processing results)
    output_url = None
    if pd.notna(row.get("result__Fixed output_excel_file")):
        output_url = row["result__Fixed output_excel_file"]
    elif pd.notna(row.get("example_output_sheet_url")):  # Fallback for non-Forte CSVs
        output_url = row["example_output_sheet_url"]

    if output_url:
        output_result = process_sheet_url(
            output_url,
            auth_secret,
            target_folder_id,
            subject,
            validation_mode,
            preserve_visual_formatting,
        )
        row_result["example_output_sheet_results"].append(output_result)

    return row_result


def process_sheet_url(
    url: str,
    auth_secret: str,
    target_folder_id: str,
    subject: Optional[str] = None,
    validation_mode: str = "fix",
    preserve_visual_formatting: bool = True,
) -> Dict[str, Any]:
    """
    Process a single sheet URL: validate and upload to Google Drive.

    Args:
        url: Sheet URL to process (Google Sheets URL, Google Drive Excel URL, or local path)
        auth_secret: Base64 encoded service account credentials
        target_folder_id: Google Drive folder ID for output files
        subject: Email for domain-wide delegation (optional)
        validation_mode: Validation mode ("fix" or "flag")
        preserve_visual_formatting: Whether to preserve visual formatting

    Returns:
        Dictionary containing sheet processing results
    """
    # Import API functions here to avoid circular import
    from urarovite.core.api import (
        execute_all_validations,
        get_available_validation_criteria,
    )
    from urarovite.utils.drive import get_file_metadata

    validation_result = None
    copied_url = None
    file_type = "unknown"

    try:
        # Detect file type and source
        is_google_url = "docs.google.com" in url or "sheets.google.com" in url
        is_drive_url = "drive.google.com" in url
        is_local_file = not (is_google_url or is_drive_url)

        if is_drive_url:
            # Get file metadata to determine type
            try:
                metadata_result = get_file_metadata(url, auth_secret)
                if metadata_result.get("success"):
                    mime_type = metadata_result.get("mimeType", "")
                    if mime_type == "application/vnd.google-apps.spreadsheet":
                        file_type = "google_sheets"
                    elif mime_type in [
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "application/vnd.ms-excel",
                    ]:
                        file_type = "excel_from_drive"
                    else:
                        file_type = "other_drive_file"
                else:
                    logging.warning(
                        f"Could not get metadata for {url}, treating as Google Sheets"
                    )
                    file_type = "google_sheets"
            except Exception as e:
                logging.warning(f"Error getting file metadata for {url}: {e}")
                file_type = "google_sheets"
        elif is_google_url:
            file_type = "google_sheets"
        elif is_local_file:
            # Check file extension for local files
            if url.lower().endswith((".xlsx", ".xls", ".xlsm")):
                file_type = "local_excel"
            else:
                file_type = "unknown_local"

        logging.info(f"Processing {url} as file type: {file_type}")

        # Perform validation (API automatically detects file type)
        validation_result = execute_all_validations(
            checks=[
                {"id": check["id"], "mode": validation_mode}
                for check in get_available_validation_criteria()
            ],
            sheet_url=url,
            auth_secret=auth_secret,
            subject=subject,
            target=None,  # Don't create duplicates during validation
            target_format=None,
            preserve_visual_formatting=preserve_visual_formatting,
        )

        # Handle formatting fallback if needed
        if not validation_result.get("success") and preserve_visual_formatting:
            if "This operation is not supported for this document" in str(
                validation_result.get("errors", [])
            ):
                # Retry without preserving formatting
                validation_result = execute_all_validations(
                    checks=[
                        {"id": check["id"], "mode": validation_mode}
                        for check in get_available_validation_criteria()
                    ],
                    sheet_url=url,
                    auth_secret=auth_secret,
                    subject=subject,
                    target=None,
                    target_format=None,
                    preserve_visual_formatting=False,  # Fallback
                )

        # Upload processed file to Google Drive based on file type
        # Be more forgiving - upload even if some validators failed (e.g., config issues)
        validation_successful = validation_result.get("success", False)
        total_fixes = validation_result.get("summary", {}).get("total_fixes", 0)
        total_flags = validation_result.get("summary", {}).get("total_flags", 0)

        logging.info(
            f"🔍 Validation result: success={validation_successful}, fixes={total_fixes}, flags={total_flags} for {url}"
        )

        # Upload if validation succeeded OR if we have any fixes/flags (meaning processing happened)
        if validation_successful or total_fixes > 0 or total_flags > 0:
            logging.info(
                f"✅ Uploading processed file to Drive for {url} (validation occurred)"
            )
            copied_url = _upload_processed_file_to_drive(
                url=url,
                file_type=file_type,
                target_folder_id=target_folder_id,
                auth_secret=auth_secret,
                subject=subject,
                preserve_visual_formatting=preserve_visual_formatting,
            )

            # Clean up temp files after successful upload to Google Drive
            if copied_url:
                logging.info(
                    f"🧹 Starting cleanup after successful upload to {copied_url}"
                )
                _cleanup_temp_files_after_upload(validation_result, url)

        else:
            logging.warning(
                f"❌ No validation processing occurred for {url}, skipping Drive upload"
            )

    except Exception as e:
        validation_result = {
            "success": False,
            "summary": {"total_fixes": 0, "total_flags": 0, "checks_processed": 0},
            "errors": [str(e)],
            "details": {},
        }
        logging.error(f"Error processing sheet URL {url}: {e}")

    return {
        "sheet_url": url,
        "validation_result": validation_result,
        "copied_url": copied_url,
        "file_type": file_type,
    }


def _upload_processed_file_to_drive(
    url: str,
    file_type: str,
    target_folder_id: str,
    auth_secret: str,
    subject: Optional[str] = None,
    preserve_visual_formatting: bool = True,
) -> Optional[str]:
    """
    Upload processed file to Google Drive based on file type.

    Args:
        url: Source file URL or path
        file_type: Type of file (google_sheets, excel_from_drive, local_excel, etc.)
        target_folder_id: Google Drive folder ID for output
        auth_secret: Base64 encoded service account credentials
        subject: Email for domain-wide delegation (optional)
        preserve_visual_formatting: Whether to preserve visual formatting

    Returns:
        Google Drive URL of uploaded file, or None if failed
    """
    from urarovite.utils.generic_spreadsheet import convert_spreadsheet_format
    import tempfile
    import os

    try:
        if file_type == "google_sheets":
            # For Google Sheets, just duplicate to target folder
            drive_service = create_drive_service_from_encoded_creds(
                auth_secret, subject=subject
            )
            sheets_service = create_sheets_service_from_encoded_creds(
                auth_secret, subject=subject
            )
            folder_url = f"https://drive.google.com/drive/folders/{target_folder_id}"

            copy_result = duplicate_file_to_drive_folder(
                drive_service=drive_service,
                file_url=url,
                folder_url=folder_url,
                prefix_file_name="validated_",
                sheets_service=sheets_service,
            )
            if copy_result.get("success"):
                return copy_result.get("url")

        elif file_type in ["excel_from_drive", "local_excel"]:
            # For Excel files, convert to Google Sheets and upload to Drive
            with tempfile.TemporaryDirectory() as temp_dir:
                if file_type == "excel_from_drive":
                    # Download Excel from Google Drive first
                    from urarovite.utils.drive import download_file_from_drive

                    temp_excel_path = os.path.join(temp_dir, "temp_excel.xlsx")
                    download_result = download_file_from_drive(
                        file_url=url,
                        local_path=temp_excel_path,
                        auth_credentials={"auth_secret": auth_secret},
                    )

                    if not download_result.get("success"):
                        logging.error(
                            f"Failed to download Excel from Drive: {download_result.get('error')}"
                        )
                        return None

                    source_file = temp_excel_path
                else:
                    # Local Excel file
                    source_file = url

                # Create target Google Sheets URL in the target folder
                folder_url = (
                    f"https://drive.google.com/drive/folders/{target_folder_id}"
                )

                # Convert Excel to Google Sheets
                conversion_result = convert_spreadsheet_format(
                    source=source_file,
                    target="auto",  # Auto-generate name from source
                    auth_credentials={"auth_secret": auth_secret, "subject": subject}
                    if subject
                    else {"auth_secret": auth_secret},
                    preserve_formulas=True,
                    preserve_visual_formatting=preserve_visual_formatting,
                    target_file_type="google_sheets",
                    use_temp_directory=True,  # Use temp/ since this will be uploaded to Drive
                )

                if conversion_result.get("success"):
                    # The conversion creates a new Google Sheets file
                    # Now we need to move it to the target folder
                    sheets_url = conversion_result.get("output_path")
                    if sheets_url:
                        # Extract file ID and move to target folder
                        from urarovite.utils.drive import extract_google_file_id

                        file_id = extract_google_file_id(sheets_url)

                        if file_id:
                            # Move to target folder
                            drive_service = create_drive_service_from_encoded_creds(
                                auth_secret, subject=subject
                            )

                            try:
                                # Update file parents to move to target folder
                                drive_service.files().update(
                                    fileId=file_id,
                                    addParents=target_folder_id,
                                    supportsAllDrives=True,
                                ).execute()

                                # Rename to add validation prefix
                                current_metadata = (
                                    drive_service.files()
                                    .get(
                                        fileId=file_id,
                                        fields="name",
                                        supportsAllDrives=True,
                                    )
                                    .execute()
                                )

                                current_name = current_metadata.get(
                                    "name", "Validated File"
                                )
                                new_name = f"validated_{current_name}"

                                drive_service.files().update(
                                    fileId=file_id,
                                    body={"name": new_name},
                                    supportsAllDrives=True,
                                ).execute()

                                return f"https://docs.google.com/spreadsheets/d/{file_id}/edit"

                            except Exception as e:
                                logging.error(
                                    f"Failed to move/rename converted file: {e}"
                                )
                                # Return the original URL even if move failed
                                return sheets_url
                        else:
                            return sheets_url
                    else:
                        logging.error(
                            "Conversion succeeded but no output_path returned"
                        )
                        return None
                else:
                    logging.error(
                        f"Excel to Google Sheets conversion failed: {conversion_result.get('error')}"
                    )
                    return None
        else:
            logging.warning(f"Unknown file type {file_type}, cannot upload to Drive")
            return None

    except Exception as e:
        logging.error(f"Error uploading processed file to Drive: {e}")
        return None


def _cleanup_temp_files_after_upload(
    validation_result: Dict[str, Any], url: str
) -> None:
    """
    Clean up temporary files after successful upload to Google Drive.

    Args:
        validation_result: The validation result containing file paths
        url: Original URL for logging purposes
    """
    import os
    from pathlib import Path

    try:
        # Look for shared_duplicate path in validation result
        shared_duplicate = validation_result.get("shared_duplicate")
        logging.info(f"🔍 Cleanup checking shared_duplicate: {shared_duplicate}")

        if shared_duplicate and isinstance(shared_duplicate, str):
            duplicate_path = Path(shared_duplicate)

            # Clean up validation files from temp/ or output/ after successful Drive upload
            if duplicate_path.exists() and (
                "temp" in duplicate_path.parts or "output" in duplicate_path.parts
            ):
                try:
                    os.remove(duplicate_path)
                    logging.info(
                        f"🗑️  Cleaned up validation file after Drive upload: {duplicate_path}"
                    )
                except Exception as e:
                    logging.warning(
                        f"⚠️  Failed to clean up validation file {duplicate_path}: {str(e)}"
                    )
            elif duplicate_path.exists():
                logging.info(
                    f"🚫 Skipping cleanup for protected file: {duplicate_path}"
                )
            else:
                logging.info(f"🚫 File doesn't exist for cleanup: {duplicate_path}")

        # Also clean up any temp files in the temp directory that match patterns
        temp_dir = Path("./temp")
        if temp_dir.exists():
            # Clean up old validation work files (older than 1 hour)
            import time

            current_time = time.time()

            for temp_file in temp_dir.glob("validation_work_*.xlsx"):
                try:
                    file_mtime = temp_file.stat().st_mtime
                    if current_time - file_mtime > 3600:  # 1 hour old
                        temp_file.unlink()
                        logging.debug(f"🗑️  Cleaned up old temp file: {temp_file}")
                except Exception as e:
                    logging.debug(
                        f"Failed to clean up old temp file {temp_file}: {str(e)}"
                    )

    except Exception as e:
        logging.warning(f"⚠️  Error during temp file cleanup for {url}: {str(e)}")


def _update_summary_stats(summary: Dict[str, Any], row_result: Dict[str, Any]) -> None:
    """Update summary statistics with results from a processed row."""

    for results_key in ["input_sheet_results", "example_output_sheet_results"]:
        for sheet_result in row_result.get(results_key, []):
            validation_result = sheet_result.get("validation_result", {})

            summary["total_sheets_processed"] += 1

            # Count individual validator successes/failures instead of sheet-level success
            validation_summary = validation_result.get("summary", {})
            summary["successful_validations"] += validation_summary.get(
                "successful_validations", 0
            )
            summary["failed_validations"] += validation_summary.get(
                "failed_validations", 0
            )

            # Count validator executions
            checks_processed = validation_summary.get("checks_processed", 0)
            summary["total_validator_executions"] += checks_processed

            # Count fixes and flags
            total_fixes = validation_summary.get("total_fixes", 0)
            total_flags = validation_summary.get("total_flags", 0)

            summary["total_fixes_applied"] += total_fixes
            summary["total_flags_found"] += total_flags

            # Count copied files
            if sheet_result.get("copied_url"):
                summary["files_copied"] += 1


def _generate_output_csv(
    original_df: pd.DataFrame,
    detailed_results: List[Dict[str, Any]],
    output_file_path: Union[str, Path],
) -> None:
    """Generate output CSV file with validation results."""

    # Create a copy of the original DataFrame
    output_df = original_df.copy()

    # Add new columns for validation results (processing Forte result files)
    new_columns = [
        "result_input_file_fixed",
        "result_input_drive_url",
        "result_input_file_type",
        "result_input_fixes_applied",
        "result_input_flags_found",
        "result_input_validation_summary",
        "result_input_validation_details",
        "result_input_validation_errors",
        "result_output_file_fixed",
        "result_output_drive_url",
        "result_output_file_type",
        "result_output_fixes_applied",
        "result_output_flags_found",
        "result_output_validation_summary",
        "result_output_validation_details",
        "result_output_validation_errors",
        # New detailed columns
        "result_input_issues_found",
        "result_input_errors_count",
        "result_input_validation_fixes",
        "result_input_validation_flags",
        "result_input_validation_errors_detail",
        "result_output_issues_found",
        "result_output_errors_count",
        "result_output_validation_fixes",
        "result_output_validation_flags",
        "result_output_validation_errors_detail",
    ]

    # Initialize string columns
    string_columns = [
        col
        for col in new_columns
        if "validation_" in col
        and col.endswith(
            ("summary", "details", "errors", "fixes", "flags", "errors_detail")
        )
        or col.endswith(("file_fixed", "drive_url", "file_type"))
    ]
    for col in string_columns:
        output_df[col] = ""

    # Initialize integer count columns with proper int64 dtype
    int_columns = [
        col
        for col in new_columns
        if col.endswith(
            ("fixes_applied", "flags_found", "issues_found", "errors_count")
        )
    ]
    for col in int_columns:
        output_df[col] = pd.Series(0, dtype="int64", index=output_df.index)

    # Populate results
    for idx, row_result in enumerate(detailed_results):
        _populate_row_results(output_df, idx, row_result, "input_sheet", "result_input")
        _populate_row_results(
            output_df, idx, row_result, "example_output_sheet", "result_output"
        )

    # Write output CSV
    output_df.to_csv(output_file_path, index=False)


def _generate_bulk_review_csv(
    original_df: pd.DataFrame,
    detailed_results: List[Dict[str, Any]],
    output_file_path: Union[str, Path],
) -> None:
    """Generate bulk review CSV file with id, status, and feedback columns."""

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create bulk review filename
    output_path = Path(output_file_path)
    bulk_review_path = output_path.parent / f"bulk_review_{timestamp}.csv"

    # Create bulk review DataFrame
    bulk_review_rows = []

    for idx, row_result in enumerate(detailed_results):
        # Get the original row data to extract ID
        original_row = original_df.iloc[idx]

        # Extract ID - try common ID column names
        id_value = None
        for id_col in ["id", "Id", "ID", "identifier", "Identifier"]:
            if id_col in original_row:
                id_value = original_row[id_col]
                break

        # Fallback to row index if no ID column found
        if id_value is None:
            id_value = f"row_{idx + 1}"

        # Collect all flags from both input and output sheets
        all_flags = []

        # Process input sheet results
        input_results = row_result.get("input_sheet_results", [])
        for result in input_results:
            validation_result = result.get("validation_result", {})
            details_data = validation_result.get("details", {})

            # Extract flags from details
            if "flags" in details_data:
                all_flags.extend(details_data["flags"])
            elif "issues" in details_data:
                all_flags.extend(details_data["issues"])
            else:
                # Legacy format with per-validator details
                for validator_id, validator_details in details_data.items():
                    if (
                        isinstance(validator_details, dict)
                        and "issues" in validator_details
                    ):
                        all_flags.extend(validator_details["issues"])

        # Process output sheet results
        output_results = row_result.get("example_output_sheet_results", [])
        for result in output_results:
            validation_result = result.get("validation_result", {})
            details_data = validation_result.get("details", {})

            # Extract flags from details
            if "flags" in details_data:
                all_flags.extend(details_data["flags"])
            elif "issues" in details_data:
                all_flags.extend(details_data["issues"])
            else:
                # Legacy format with per-validator details
                for validator_id, validator_details in details_data.items():
                    if (
                        isinstance(validator_details, dict)
                        and "issues" in validator_details
                    ):
                        all_flags.extend(validator_details["issues"])

        # Determine status based on flags
        status = "To revise" if all_flags else "Pending review"

        # Generate human-readable feedback
        feedback = _generate_feedback_text(all_flags)

        bulk_review_rows.append(
            {"id": id_value, "status": status, "feedback": feedback}
        )

    # Create DataFrame and save
    bulk_review_df = pd.DataFrame(bulk_review_rows)
    bulk_review_df.to_csv(bulk_review_path, index=False)

    logging.info(f"Generated bulk review CSV: {bulk_review_path}")


def _generate_feedback_text(flags: List[Dict[str, Any]]) -> str:
    """Generate human-readable feedback text from validation flags."""

    if not flags:
        return "Spreadsheet AutoQA: No issues found."

    feedback_lines = ["Spreadsheet AutoQA: Issues found that need to be addressed:\n"]

    # Group flags by validator for better organization
    validator_groups = {}
    for flag in flags:
        validator = flag.get("validator", "Unknown validator")
        if validator not in validator_groups:
            validator_groups[validator] = []
        validator_groups[validator].append(flag)

    for validator, validator_flags in validator_groups.items():
        feedback_lines.append(f"• {validator.replace('_', ' ').title()}:")

        for flag in validator_flags:
            # Extract meaningful information from the flag
            if "message" in flag:
                feedback_lines.append(f"  - {flag['message']}")
            elif "description" in flag:
                feedback_lines.append(f"  - {flag['description']}")
            elif "cell" in flag and "issue" in flag:
                feedback_lines.append(f"  - Cell {flag['cell']}: {flag['issue']}")
            elif "issue" in flag:
                feedback_lines.append(f"  - {flag['issue']}")
            else:
                # Fallback: try to create a readable message from available data
                flag_info = []
                for key in ["cell", "range", "sheet", "value"]:
                    if key in flag and flag[key]:
                        flag_info.append(f"{key}: {flag[key]}")

                if flag_info:
                    feedback_lines.append(f"  - {', '.join(flag_info)}")
                else:
                    feedback_lines.append("  - Issue detected (details not available)")

        feedback_lines.append("")  # Add blank line between validators

    return "\n".join(feedback_lines).strip()


def _populate_row_results(
    df: pd.DataFrame,
    row_idx: int,
    row_result: Dict[str, Any],
    results_key: str,
    prefix: str,
) -> None:
    """Populate a single row's results in the output DataFrame."""

    results_list = row_result.get(f"{results_key}_results", [])

    if results_list:
        result = results_list[0]  # Take first result
        validation_result = result.get("validation_result", {})

        # Set fixed URL and related info
        if result.get("copied_url"):
            df.at[row_idx, f"{prefix}_file_fixed"] = result["copied_url"]
            df.at[row_idx, f"{prefix}_drive_url"] = result[
                "copied_url"
            ]  # Same as file_fixed for now

        # Set file type if available
        if result.get("file_type"):
            df.at[row_idx, f"{prefix}_file_type"] = result["file_type"]

        # Set validation metrics - separate columns for fixes, flags, and errors
        summary = validation_result.get("summary", {})
        validation_errors = validation_result.get("errors", [])

        # Extract detailed fixes, flags (issues), and errors per validator
        details_data = validation_result.get("details", {})
        validator_fixes = {}
        validator_flags = {}
        validator_errors = {}

        # Process detailed results to extract per-validator metrics
        if details_data:
            # Handle different details formats
            if "fixes" in details_data or "flags" in details_data:
                # Format with top-level aggregated fixes/flags/issues
                # Process fixes - store full fix objects
                for fix in details_data.get("fixes", []):
                    validator = fix.get("validator", "unknown")
                    if validator not in validator_fixes:
                        validator_fixes[validator] = []
                    validator_fixes[validator].append(fix)

                # Process flags (issues) - store full flag objects
                for flag in details_data.get("flags", []):
                    validator = flag.get("validator", "unknown")
                    if validator not in validator_flags:
                        validator_flags[validator] = []
                    validator_flags[validator].append(flag)

                # Also check for "issues" key (alternative name for flags)
                for issue in details_data.get("issues", []):
                    validator = issue.get("validator", "unknown")
                    if validator not in validator_flags:
                        validator_flags[validator] = []
                    validator_flags[validator].append(issue)
            else:
                # Legacy format with per-validator details
                for validator_id, validator_details in details_data.items():
                    if isinstance(validator_details, dict):
                        validator_fixes[validator_id] = validator_details.get(
                            "fixes", []
                        )
                        validator_flags[validator_id] = validator_details.get(
                            "issues", []
                        )

        # Process top-level errors by validator - store full error objects
        for error in validation_errors:
            # Extract validator name from error message if formatted properly
            validator = "unknown"
            if " validator:" in error:
                validator = error.split(" validator:")[0]
            if validator not in validator_errors:
                validator_errors[validator] = []

            # Create error object with full details
            error_obj = {"message": error, "validator": validator}
            validator_errors[validator].append(error_obj)

        # Calculate totals from detailed per-validator data
        total_fixes = sum(len(fixes) for fixes in validator_fixes.values())
        total_flags = sum(len(flags) for flags in validator_flags.values())
        total_errors = sum(len(errors) for errors in validator_errors.values())

        # Set summary metrics - ensure integer types
        df.at[row_idx, f"{prefix}_fixes_applied"] = int(
            total_fixes or summary.get("total_fixes", 0)
        )
        df.at[row_idx, f"{prefix}_issues_found"] = int(
            total_flags or summary.get("total_issues", 0)
        )
        df.at[row_idx, f"{prefix}_errors_count"] = int(
            total_errors or len(validation_errors)
        )

        # Set per-validator columns - always use JSON format even for empty dicts
        df.at[row_idx, f"{prefix}_validation_fixes"] = json.dumps(
            validator_fixes, indent=2, ensure_ascii=False
        )
        df.at[row_idx, f"{prefix}_validation_flags"] = json.dumps(
            validator_flags, indent=2, ensure_ascii=False
        )
        df.at[row_idx, f"{prefix}_validation_errors_detail"] = json.dumps(
            validator_errors, indent=2, ensure_ascii=False
        )

        # Set validation summary
        if validation_result.get("success"):
            validators_run = summary.get("checks_processed", 0)
            fixes = summary.get("total_fixes", 0)
            issues = summary.get("total_issues", 0)
            errors = len(validation_errors)

            summary_parts = ["✅ Spreadsheet"]
            if validators_run > 0:
                summary_parts.append(f"🔍 {validators_run} validators run")
            if fixes > 0:
                summary_parts.append(f"🔧 {fixes} fixes")
            if issues > 0:
                summary_parts.append(f"⚠️ {issues} issues")
            if errors > 0:
                summary_parts.append(f"❌ {errors} errors")

            df.at[row_idx, f"{prefix}_validation_summary"] = " | ".join(summary_parts)
        else:
            df.at[row_idx, f"{prefix}_validation_summary"] = "❌ Validation failed"

        # Set detailed information
        detailed_summary = {}

        # Include top-level errors
        validation_errors = validation_result.get("errors", [])
        if validation_errors:
            detailed_summary["validation_errors"] = validation_errors

        # Include details from validators
        details_data = validation_result.get("details", {})
        if details_data:
            for validator_id, validator_details in details_data.items():
                detailed_summary[validator_id] = validator_details

        # Set details and errors
        # Format JSON output for better readability and debugging
        df.at[row_idx, f"{prefix}_validation_details"] = (
            json.dumps(detailed_summary, indent=2, ensure_ascii=False)
            if detailed_summary
            else "No validation details available"
        )
        df.at[row_idx, f"{prefix}_validation_errors"] = (
            json.dumps(validation_errors, indent=2, ensure_ascii=False)
            if validation_errors
            else ""
        )


def generate_summary_report(result: Dict[str, Any]) -> str:
    """Generate a beautifully formatted, human-readable summary report."""

    summary = result["summary"]
    success = result["success"]

    # Color constants for terminal output
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    PURPLE = "\033[95m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    # Header with fancy border
    header_text = "FORTE PROCESSING RESULTS"
    header_border = "╔" + "═" * 58 + "╗"
    header_line = f"║{header_text:^58}║"
    footer_border = "╚" + "═" * 58 + "╝"

    report_lines = [
        f"\n{CYAN}{header_border}",
        f"{header_line}",
        f"{footer_border}{RESET}",
        "",
    ]

    # Status with appropriate color
    status_color = GREEN if success else RED
    status_text = "SUCCESS" if success else "FAILED"
    status_icon = "✅" if success else "❌"
    report_lines.append(
        f"{BOLD}{status_color}{status_icon} Overall Status: {status_text}{RESET}"
    )
    report_lines.append("")

    # Summary Statistics with visual formatting
    report_lines.extend(
        [
            f"{BOLD}{BLUE}📊 Summary Statistics:{RESET}",
            "┌─" + "─" * 50 + "┐",
        ]
    )

    # Format statistics with proper alignment and colors
    stats = [
        ("Sheet URLs processed", summary["total_sheets_processed"], "🔗"),
        ("Successful validations", summary["successful_validations"], "✅"),
        ("Failed validations", summary["failed_validations"], "❌"),
        ("Total validator executions", summary["total_validator_executions"], "🔍"),
        ("Files copied", summary["files_copied"], "📋"),
        ("Total fixes applied", summary["total_fixes_applied"], "🔧"),
        ("Total flags flagged", summary["total_flags_found"], "⚠️"),
    ]

    for label, value, icon in stats:
        # Color code based on the type of statistic
        if "failed" in label.lower() or "error" in label.lower():
            color = RED if value > 0 else GREEN
        elif (
            "success" in label.lower()
            or "fix" in label.lower()
            or "copied" in label.lower()
        ):
            color = GREEN if value > 0 else RESET
        elif "issue" in label.lower() or "flagged" in label.lower():
            color = YELLOW if value > 0 else GREEN
        else:
            color = CYAN

        report_lines.append(f"│ {icon} {label:<30} {color}{value:>12}{RESET} │")

    report_lines.append("└─" + "─" * 50 + "┘")
    report_lines.append("")

    # Performance metrics if available
    perf_metrics = result.get("performance_metrics", {})
    if perf_metrics and perf_metrics.get("total_time_seconds"):
        total_time = perf_metrics["total_time_seconds"]
        report_lines.extend(
            [
                f"{BOLD}{PURPLE}⏱️  Performance Metrics:{RESET}",
                f"   Processing time: {CYAN}{total_time:.2f} seconds{RESET}",
                "",
            ]
        )

    # File outputs
    output_files = []
    if result.get("output_csv_file"):
        output_files.append(("Output CSV", result["output_csv_file"]))

    # Look for JSON results file pattern
    output_dir = Path("./output")
    if output_dir.exists():
        json_files = list(output_dir.glob("forte_processing_results_*.json"))
        if json_files:
            latest_json = max(json_files, key=lambda f: f.stat().st_mtime)
            output_files.append(("Results JSON", str(latest_json)))

    if output_files:
        report_lines.extend(
            [
                f"{BOLD}{PURPLE}💾 Output Files:{RESET}",
            ]
        )
        for file_type, file_path in output_files:
            # Truncate very long paths
            display_path = str(file_path)
            if len(display_path) > 50:
                display_path = "..." + display_path[-47:]
            report_lines.append(f"   📄 {file_type}: {CYAN}{display_path}{RESET}")
        report_lines.append("")

    # Detailed breakdown if we have row-level results
    detailed_results = result.get("detailed_results", [])
    if detailed_results and len(detailed_results) <= 10:  # Only show for small datasets
        report_lines.extend(
            [
                f"{BOLD}{BLUE}📋 Row-by-Row Breakdown:{RESET}",
                "┌─" + "─" * 70 + "┐",
            ]
        )

        for i, row_result in enumerate(detailed_results, 1):
            input_results = row_result.get("input_sheet_results", [])
            output_results = row_result.get("example_output_sheet_results", [])

            total_sheets = len(input_results) + len(output_results)
            total_fixes = 0
            total_flags = 0

            for sheet_result in input_results + output_results:
                validation = sheet_result.get("validation_result", {})
                summary_data = validation.get("summary", {})
                total_fixes += summary_data.get("total_fixes", 0)
                total_flags += summary_data.get("total_flags", 0)

            status_icon = "✅" if total_sheets > 0 else "⚪"
            fixes_text = (
                f"{GREEN}{total_fixes} fixes{RESET}"
                if total_fixes > 0
                else f"{total_fixes} fixes"
            )
            flags_text = (
                f"{YELLOW}{total_flags} flags{RESET}"
                if total_flags > 0
                else f"{total_flags} flags"
            )

            report_lines.append(
                f"│ {status_icon} Row {i:2d}: {total_sheets} sheets • {fixes_text} • {flags_text}"
                + " "
                * (
                    70
                    - len(
                        f" Row {i:2d}: {total_sheets} sheets • {total_fixes} fixes • {total_flags} flags"
                    )
                    - 3
                )
                + "│"
            )

        report_lines.append("└─" + "─" * 70 + "┘")
        report_lines.append("")

    # Errors section with enhanced formatting
    if result["errors"]:
        report_lines.extend(
            [
                f"{BOLD}{RED}❌ Errors Encountered:{RESET}",
                "┌─" + "─" * 60 + "┐",
            ]
        )

        for i, error in enumerate(result["errors"], 1):
            # Wrap long error messages
            error_lines = []
            if len(error) > 55:
                words = error.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) <= 55:
                        current_line += word + " "
                    else:
                        if current_line:
                            error_lines.append(current_line.strip())
                        current_line = word + " "
                if current_line:
                    error_lines.append(current_line.strip())
            else:
                error_lines = [error]

            for j, line in enumerate(error_lines):
                prefix = f"{i}. " if j == 0 else "   "
                report_lines.append(f"│ {RED}{prefix}{line:<55}{RESET} │")

        report_lines.append("└─" + "─" * 60 + "┘")

    # Footer with helpful information
    if success:
        report_lines.extend(
            [
                "",
                f"{GREEN}{BOLD}🎉 Processing completed successfully!{RESET}",
            ]
        )
        if summary["total_fixes_applied"] > 0:
            report_lines.append(
                f"   {CYAN}Applied {summary['total_fixes_applied']} fixes across {summary['total_sheets_processed']} sheets{RESET}"
            )
    else:
        report_lines.extend(
            [
                "",
                f"{RED}{BOLD}⚠️  Processing completed with errors{RESET}",
                f"   {YELLOW}Check the error details above for troubleshooting information{RESET}",
            ]
        )

    return "\n".join(report_lines)


def generate_plain_summary_report(result: Dict[str, Any]) -> str:
    """Generate a plain text summary report without colors or fancy formatting."""

    summary = result["summary"]
    success = result["success"]

    report_lines = [
        "",
        "=" * 60,
        "FORTE PROCESSING RESULTS",
        "=" * 60,
        "",
        f"Overall Status: {'SUCCESS' if success else 'FAILED'}",
        "",
        "Summary Statistics:",
        f"  Sheet URLs processed: {summary['total_sheets_processed']}",
        f"  Successful validations: {summary['successful_validations']}",
        f"  Failed validations: {summary['failed_validations']}",
        f"  Total validator executions: {summary['total_validator_executions']}",
        f"  Files copied: {summary['files_copied']}",
        f"  Total fixes applied: {summary['total_fixes_applied']}",
        f"  Total flags flagged: {summary['total_flags_found']}",
        "",
    ]

    # Performance metrics if available
    perf_metrics = result.get("performance_metrics", {})
    if perf_metrics and perf_metrics.get("total_time_seconds"):
        total_time = perf_metrics["total_time_seconds"]
        report_lines.extend(
            [
                "Performance:",
                f"  Processing time: {total_time:.2f} seconds",
                "",
            ]
        )

    # File outputs
    if result.get("output_csv_file"):
        report_lines.extend(
            [
                "Output Files:",
                f"  CSV: {result['output_csv_file']}",
                "",
            ]
        )

    # Errors
    if result["errors"]:
        report_lines.extend(
            [
                "Errors:",
                *[f"  - {error}" for error in result["errors"]],
                "",
            ]
        )

    # Footer
    if success:
        report_lines.append("Processing completed successfully!")
        if summary["total_fixes_applied"] > 0:
            report_lines.append(
                f"Applied {summary['total_fixes_applied']} fixes across {summary['total_sheets_processed']} sheets"
            )
    else:
        report_lines.extend(
            [
                "Processing completed with errors",
                "Check the error details above for troubleshooting information",
            ]
        )

    report_lines.append("")
    return "\n".join(report_lines)
