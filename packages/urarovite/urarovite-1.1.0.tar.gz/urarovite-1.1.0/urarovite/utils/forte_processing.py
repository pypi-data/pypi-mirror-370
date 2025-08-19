"""
Forte CSV Processing Utilities

Shared functions for processing Forte export CSVs and performing bulk validation workflows.
This module provides the core logic used by both the CLI and bash script to ensure consistency.
"""

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from urarovite.utils.drive import duplicate_file_to_drive_folder


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
            "successful_sheet_validations": 0,
            "failed_sheet_validations": 0,
            "total_validator_executions": 0,
            "total_fixes_applied": 0,
            "total_issues_flagged": 0,
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
    Process a single sheet URL: validate and copy.

    Args:
        url: Sheet URL to process
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

    validation_result = None
    copied_url = None

    try:
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

        # Copy file to target folder
        if validation_result.get("success"):
            copy_result = duplicate_file_to_drive_folder(
                url, target_folder_id, auth_secret, subject
            )
            if copy_result.get("success"):
                copied_url = copy_result.get("new_url")

    except Exception as e:
        validation_result = {
            "success": False,
            "summary": {"total_fixes": 0, "total_issues": 0, "checks_processed": 0},
            "errors": [str(e)],
            "details": {},
        }
        logging.error(f"Error processing sheet URL {url}: {e}")

    return {
        "sheet_url": url,
        "validation_result": validation_result,
        "copied_url": copied_url,
    }


def _update_summary_stats(summary: Dict[str, Any], row_result: Dict[str, Any]) -> None:
    """Update summary statistics with results from a processed row."""

    for results_key in ["input_sheet_results", "example_output_sheet_results"]:
        for sheet_result in row_result.get(results_key, []):
            validation_result = sheet_result.get("validation_result", {})

            summary["total_sheets_processed"] += 1

            if validation_result.get("success"):
                summary["successful_sheet_validations"] += 1
            else:
                summary["failed_sheet_validations"] += 1

            # Count validator executions
            checks_processed = validation_result.get("summary", {}).get(
                "checks_processed", 0
            )
            summary["total_validator_executions"] += checks_processed

            # Count fixes and issues
            total_fixes = validation_result.get("summary", {}).get("total_fixes", 0)
            total_issues = validation_result.get("summary", {}).get("total_issues", 0)

            summary["total_fixes_applied"] += total_fixes
            summary["total_issues_flagged"] += total_issues

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
        "result_input_fixes_applied",
        "result_input_issues_found",
        "result_input_validation_summary",
        "result_input_validation_details",
        "result_input_validation_errors",
        "result_output_file_fixed",
        "result_output_fixes_applied",
        "result_output_issues_found",
        "result_output_validation_summary",
        "result_output_validation_details",
        "result_output_validation_errors",
    ]

    for col in new_columns:
        output_df[col] = ""

    # Populate results
    for idx, row_result in enumerate(detailed_results):
        _populate_row_results(output_df, idx, row_result, "input_sheet", "result_input")
        _populate_row_results(
            output_df, idx, row_result, "example_output_sheet", "result_output"
        )

    # Write output CSV
    output_df.to_csv(output_file_path, index=False)


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

        # Set fixed URL
        if result.get("copied_url"):
            df.at[row_idx, f"{prefix}_file_fixed"] = result["copied_url"]

        # Set validation metrics
        summary = validation_result.get("summary", {})
        df.at[row_idx, f"{prefix}_fixes_applied"] = summary.get("total_fixes", 0)
        df.at[row_idx, f"{prefix}_issues_found"] = summary.get("total_issues", 0)

        # Set validation summary
        if validation_result.get("success"):
            validators_run = summary.get("checks_processed", 0)
            fixes = summary.get("total_fixes", 0)
            issues = summary.get("total_issues", 0)

            summary_parts = ["✅ Spreadsheet"]
            if validators_run > 0:
                summary_parts.append(f"🔍 {validators_run} validators run")
            if fixes > 0:
                summary_parts.append(f"🔧 {fixes} fixes")
            if issues > 0:
                summary_parts.append(f"⚠️ {issues} issues")

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
        ("Successful validations", summary["successful_sheet_validations"], "✅"),
        ("Failed validations", summary["failed_sheet_validations"], "❌"),
        ("Total validator executions", summary["total_validator_executions"], "🔍"),
        ("Files copied", summary["files_copied"], "📋"),
        ("Total fixes applied", summary["total_fixes_applied"], "🔧"),
        ("Total issues flagged", summary["total_issues_flagged"], "⚠️"),
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
            total_issues = 0

            for sheet_result in input_results + output_results:
                validation = sheet_result.get("validation_result", {})
                summary_data = validation.get("summary", {})
                total_fixes += summary_data.get("total_fixes", 0)
                total_issues += summary_data.get("total_issues", 0)

            status_icon = "✅" if total_sheets > 0 else "⚪"
            fixes_text = (
                f"{GREEN}{total_fixes} fixes{RESET}"
                if total_fixes > 0
                else f"{total_fixes} fixes"
            )
            issues_text = (
                f"{YELLOW}{total_issues} issues{RESET}"
                if total_issues > 0
                else f"{total_issues} issues"
            )

            report_lines.append(
                f"│ {status_icon} Row {i:2d}: {total_sheets} sheets • {fixes_text} • {issues_text}"
                + " "
                * (
                    70
                    - len(
                        f" Row {i:2d}: {total_sheets} sheets • {total_fixes} fixes • {total_issues} issues"
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
        f"  Successful validations: {summary['successful_sheet_validations']}",
        f"  Failed validations: {summary['failed_sheet_validations']}",
        f"  Total validator executions: {summary['total_validator_executions']}",
        f"  Files copied: {summary['files_copied']}",
        f"  Total fixes applied: {summary['total_fixes_applied']}",
        f"  Total issues flagged: {summary['total_issues_flagged']}",
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
