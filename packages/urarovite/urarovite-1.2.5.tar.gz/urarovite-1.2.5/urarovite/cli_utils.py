#!/usr/bin/env python3
"""
CLI utilities for Urarovite using the base CLI infrastructure.

This module provides the `run_util` command pattern with various utility operations.
"""

from __future__ import annotations
import argparse
import os
import sys
from typing import Any, Dict, List, Optional

from urarovite.cli_base import (
    SingleBatchUtility, 
    UtilityResult, 
    run_utility_cli,
    create_utility_command
)
from urarovite.utils.generic_spreadsheet import convert_google_sheets_to_excel
from urarovite.utils.simple_converter import (
    convert_single_file,
    convert_batch_from_metadata,
    convert_folder_batch
)


class ConversionUtility(SingleBatchUtility):
    """Utility for converting between Google Sheets and Excel formats."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        # Single mode arguments
        parser.add_argument(
            "input_file",
            help="Google Sheets URL or local Excel file path to convert"
        )
        parser.add_argument(
            "output_path",
            nargs="?",
            help="Path where converted file should be saved"
        )
        parser.add_argument(
            "--output-folder",
            help="Output folder path (overrides output_path, generates automatic filename)"
        )
        parser.add_argument(
            "--sheets",
            help="Comma-separated list of sheet names to convert (optional, converts all if not specified)"
        )
        parser.add_argument(
            "--drive-folder-id",
            help="Google Drive folder ID for creating new Google Sheets (optional)"
        )
        parser.add_argument(
            "--output-filename",
            help="Custom filename for output (without extension)"
        )
        parser.add_argument(
            "--output-format",
            choices=["excel", "sheets"],
            default="excel",
            help="Output format for batch mode (default: excel)"
        )
        
        # Batch mode arguments
        parser.add_argument(
            "--link-columns",
            help="Comma-separated list of column names containing links to convert (batch mode)"
        )
        parser.add_argument(
            "--input-column-name",
            default="input_url",
            help="Column name containing input URLs (folder batch mode)"
        )
        parser.add_argument(
            "--output-column-name",
            default="output_url",
            help="Column name for output URLs (folder batch mode)"
        )
        parser.add_argument(
            "--metadata-sheet-name",
            default="conversion_metadata",
            help="Sheet name containing metadata (folder batch mode)"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        base_args = {
            "input_file": args.input_file,
            "output_path": args.output_path,
            "output_folder": args.output_folder,
            "sheets": args.sheets,
            "drive_folder_id": args.drive_folder_id,
            "output_filename": args.output_filename,
        }
        
        if args.mode == "batch":
            base_args.update({
                "link_columns": args.link_columns,
                "output_format": args.output_format,
            })
        elif args.mode == "single":
            # Single mode specific args
            pass
        
        return base_args
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute single file conversion."""
        try:
            # Parse sheets if provided
            sheets = None
            if kwargs.get("sheets"):
                sheets = [s.strip() for s in kwargs["sheets"].split(",") if s.strip()]
            
            result = convert_single_file(
                input_file=kwargs["input_file"],
                output_path=kwargs.get("output_path"),
                auth_credentials=kwargs.get("auth_credentials", {}),
                sheet_names=sheets,
                output_folder=kwargs.get("output_folder"),
                drive_folder_id=kwargs.get("drive_folder_id"),
                output_filename=kwargs.get("output_filename"),
            )
            
            if result["success"]:
                # Determine output location for metadata
                output_location = "Unknown"
                if "output_path" in result and result["output_path"]:
                    output_location = result["output_path"]
                elif "output_url" in result and result["output_url"]:
                    output_location = result["output_url"]
                
                # Check if any sheet names were truncated
                original_names = result.get("original_sheet_names", [])
                excel_names = result.get("excel_sheet_names", [])
                truncated_info = []
                
                if original_names and excel_names:
                    for orig, excel in zip(original_names, excel_names):
                        if orig != excel:
                            truncated_info.append(f"'{orig}' → '{excel}'")
                
                metadata_dict = {
                    "input_file": kwargs["input_file"],
                    "output_location": output_location,
                    "sheets_converted": len(sheets) if sheets else "All sheets",
                    "converted_sheets": result.get("converted_sheets", [])
                }
                
                if truncated_info:
                    metadata_dict["sheet_name_truncations"] = truncated_info
                
                return UtilityResult(
                    success=True,
                    message="File conversion completed successfully",
                    data=result,
                    metadata=metadata_dict
                )
            else:
                return UtilityResult(
                    success=False,
                    message="File conversion failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="File conversion failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch conversion."""
        try:
            # Parse link columns
            link_columns = kwargs.get("link_columns", "")
            if not link_columns:
                return UtilityResult(
                    success=False,
                    message="Batch conversion requires --link-columns parameter",
                    error="No link columns specified"
                )
            
            link_columns_list = [col.strip() for col in link_columns.split(",") if col.strip()]
            
            result = convert_batch_from_metadata(
                metadata_file=kwargs["input_file"],
                output_location=kwargs.get("output_path", ""),
                auth_credentials=kwargs.get("auth_credentials", {}),
                link_columns=link_columns_list,
                output_format=kwargs.get("output_format", "excel"),
            )
            
            if result["success"]:
                return UtilityResult(
                    success=True,
                    message="Batch conversion completed successfully",
                    data=result,
                    metadata={
                        "successful_conversions": result.get("success_count", 0),
                        "failed_conversions": result.get("failure_count", 0),
                        "output_location": result.get("output_location", "Unknown"),
                        "failed_conversions_details": result.get("failed_conversions", [])
                    }
                )
            else:
                return UtilityResult(
                    success=False,
                    message="Batch conversion failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Batch conversion failed",
                error=str(e)
            )


class FolderBatchConversionUtility(SingleBatchUtility):
    """Utility for converting all Excel files in a folder to Google Sheets."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "input_folder",
            help="Local folder containing Excel files to convert"
        )
        parser.add_argument(
            "drive_folder_id",
            help="Google Drive folder ID where converted sheets will be created"
        )
        parser.add_argument(
            "--input-column-name",
            default="input_url",
            help="Name for the input file column in metadata sheet"
        )
        parser.add_argument(
            "--output-column-name",
            default="output_url",
            help="Name for the output URL column in metadata sheet"
        )
        parser.add_argument(
            "--metadata-sheet-name",
            default="conversion_metadata",
            help="Name for the metadata sheet to create"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "input_folder": args.input_folder,
            "drive_folder_id": args.drive_folder_id,
            "input_column_name": args.input_column_name,
            "output_column_name": args.output_column_name,
            "metadata_sheet_name": args.metadata_sheet_name,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute folder batch conversion (single mode same as batch for this utility)."""
        return self.execute_batch(**kwargs)
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute folder batch conversion."""
        try:
            result = convert_folder_batch(
                input_folder=kwargs["input_folder"],
                drive_folder_id=kwargs["drive_folder_id"],
                auth_credentials=kwargs.get("auth_credentials", {}),
                input_column_name=kwargs["input_column_name"],
                output_column_name=kwargs["output_column_name"],
                metadata_sheet_name=kwargs["metadata_sheet_name"],
            )
            
            if result["success"]:
                return UtilityResult(
                    success=True,
                    message="Folder batch conversion completed successfully",
                    data=result,
                    metadata={
                        "successful_conversions": result.get("successful_conversions", 0),
                        "total_files": result.get("total_files", 0),
                        "failed_conversions": result.get("failed_conversions", 0),
                        "metadata_sheet_url": result.get("metadata_sheet_url", "Unknown")
                    }
                )
            else:
                return UtilityResult(
                    success=False,
                    message="Folder batch conversion failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Folder batch conversion failed",
                error=str(e)
            )


class ValidationUtility(SingleBatchUtility):
    """Utility for running validations on spreadsheets."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "spreadsheet_source",
            help="Google Sheets URL or local Excel file path to validate"
        )
        parser.add_argument(
            "--validator",
            help="Specific validator ID to run (use 'list' command to see options)"
        )
        parser.add_argument(
            "--mode",
            choices=["flag", "fix"],
            default="flag",
            help="Validation mode: 'flag' to report flags, 'fix' to automatically fix them (default: flag)"
        )
        parser.add_argument(
            "--params",
            help="JSON string with additional validator parameters"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "spreadsheet_source": args.spreadsheet_source,
            "validator": args.validator,
            "mode": args.mode,
            "params": args.params,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute single validation."""
        try:
            from urarovite import execute_validation
            
            # Parse params if provided
            extra_params = {}
            if kwargs.get("params"):
                import json
                try:
                    extra_params = json.loads(kwargs["params"])
                except json.JSONDecodeError:
                    return UtilityResult(
                        success=False,
                        message="Invalid JSON in --params",
                        error="Could not parse JSON parameters"
                    )
            
            # Build validation check
            check = {
                "id": kwargs.get("validator", "all"),
                "mode": kwargs["mode"]
            }
            check.update(extra_params)
            
            result = execute_validation(
                check=check,
                sheet_url=kwargs["spreadsheet_source"],
                auth_secret=kwargs.get("auth_credentials", {}).get("auth_secret"),
                subject=kwargs.get("auth_credentials", {}).get("subject"),
            )
            
            return UtilityResult(
                success=True,
                message="Validation completed successfully",
                data=result,
                metadata={
                    "validator": kwargs.get("validator", "all"),
                    "mode": kwargs["mode"],
                    "flags_found": result.get("flags_found", 0),
                    "fixes_applied": result.get("fixes_applied", 0),
                    "errors": result.get("errors", [])
                }
            )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Validation failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch validation."""
        # For now, batch validation just runs the same validation on multiple sheets
        # This could be enhanced to support metadata-based batch validation
        return UtilityResult(
            success=False,
            message="Batch validation not yet implemented",
            error="Batch validation requires metadata sheet with multiple URLs"
        )


class ForteProcessingUtility(SingleBatchUtility):
    """Utility for processing Forte CSV files."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "csv_file",
            help="Path to the Forte CSV export file"
        )
        parser.add_argument(
            "--output",
            help="Output CSV file path (default: ./output/{input_name}_processed.csv)"
        )
        parser.add_argument(
            "--target",
            default="1S2V36WyAkNCSByYK4H-uJazfWN56SXCD",
            help="Google Drive folder ID where files will be copied"
        )
        parser.add_argument(
            "--mode",
            choices=["flag", "fix"],
            default="fix",
            help="Validation mode: 'flag' to report flags, 'fix' to automatically fix them (default: fix)"
        )
        parser.add_argument(
            "--local",
            action="store_true",
            help="Download files locally as Excel instead of uploading to Google Sheets"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "csv_file": args.csv_file,
            "output": args.output,
            "target": args.target,
            "mode": args.mode,
            "local": args.local,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute Forte CSV processing."""
        try:
            # Import the processing function
            from urarovite.core.api import process_forte_csv_batch
            from urarovite.utils.forte_processing import generate_summary_report
            
            # Determine target format based on --local flag
            target_format = "excel" if kwargs.get("local") else "sheets"
            target_folder = None if kwargs.get("local") else kwargs.get("target")
            
            # Set default output file with timestamp
            output_csv = kwargs.get("output")
            if not output_csv:
                from datetime import datetime
                base_name = os.path.splitext(os.path.basename(kwargs["csv_file"]))[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_csv = f"./output/{base_name}_processed_{timestamp}.csv"
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_csv)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Get auth credentials
            auth_credentials = kwargs.get("auth_credentials", {})
            auth_secret = auth_credentials.get("auth_secret")
            if not auth_secret:
                return UtilityResult(
                    success=False,
                    message="No authentication credentials provided",
                    error="Set URAROVITE_AUTH_SECRET env var or use --auth-secret"
                )
            
            # Process the CSV
            result = process_forte_csv_batch(
                csv_file_path=kwargs["csv_file"],
                auth_secret=auth_secret,
                target_folder_id=target_folder,
                subject=auth_credentials.get("subject"),
                validation_mode=kwargs["mode"],
                preserve_visual_formatting=True,
                output_file_path=output_csv,
            )
            
            if result["success"]:
                # Generate summary report
                summary_report = generate_summary_report(result)
                
                return UtilityResult(
                    success=True,
                    message="Forte CSV processing completed successfully",
                    data=result,
                    metadata={
                        "input_file": kwargs["csv_file"],
                        "output_file": output_csv,
                        "target_folder": target_folder,
                        "mode": kwargs["mode"],
                        "target_format": target_format,
                        "summary_report": summary_report
                    }
                )
            else:
                return UtilityResult(
                    success=False,
                    message="Forte CSV processing failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Forte CSV processing failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch Forte processing (same as single for this utility)."""
        return self.execute_single(**kwargs)


class SheetsToExcelDriveUtility(SingleBatchUtility):
    """Utility for converting Google Sheets to Excel and uploading to Google Drive."""
    
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "google_sheets_url",
            help="Google Sheets URL to convert to Excel"
        )
        parser.add_argument(
            "drive_folder_id",
            help="Google Drive folder ID where Excel file will be uploaded"
        )
        parser.add_argument(
            "--filename",
            help="Custom filename for the Excel file (without extension)"
        )
        parser.add_argument(
            "--sheets",
            help="Comma-separated list of sheet names to convert (optional, converts all if not specified)"
        )
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        return {
            "google_sheets_url": args.google_sheets_url,
            "drive_folder_id": args.drive_folder_id,
            "filename": args.filename,
            "sheets": args.sheets,
        }
    
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute Google Sheets to Excel + Drive upload."""
        try:
            from urarovite.utils.generic_spreadsheet import convert_google_sheets_to_excel
            from urarovite.utils.drive import upload_file_to_drive_folder
            from urarovite.utils.sheets import extract_sheet_id
            import tempfile
            import os
            
            # Parse sheet names if provided
            sheets = None
            if kwargs.get("sheets"):
                sheets = [s.strip() for s in kwargs["sheets"].split(",") if s.strip()]
            
            # Create temporary Excel file with proper extension
            import tempfile
            temp_dir = tempfile.mkdtemp()
            temp_excel_path = os.path.join(temp_dir, "temp_conversion.xlsx")
            
            try:
                # Convert Google Sheets to temporary Excel
                conversion_result = convert_google_sheets_to_excel(
                    google_sheets_url=kwargs["google_sheets_url"],
                    excel_file_path=temp_excel_path,
                    auth_credentials=kwargs.get("auth_credentials", {}),
                    sheet_names=sheets,
                )
                
                if not conversion_result["success"]:
                    return UtilityResult(
                        success=False,
                        message="Google Sheets to Excel conversion failed",
                        error=conversion_result.get("error", "Unknown error")
                    )
                
                # Determine filename
                if kwargs.get("filename"):
                    excel_filename = f"{kwargs['filename']}.xlsx"
                else:
                    # Extract from Google Sheets title
                    sheet_id = extract_sheet_id(kwargs["google_sheets_url"])
                    from urarovite.auth.google_sheets import get_gspread_client
                    client = get_gspread_client(kwargs.get("auth_credentials", {}).get("auth_secret"))
                    spreadsheet = client.open_by_key(sheet_id)
                    excel_filename = f"{spreadsheet.title}.xlsx"
                
                # Upload to Drive
                upload_result = upload_file_to_drive_folder(
                    file_path=temp_excel_path,
                    filename=excel_filename,
                    folder_id=kwargs["drive_folder_id"],
                    auth_credentials=kwargs.get("auth_credentials", {}),
                )
                
                if upload_result["success"]:
                    return UtilityResult(
                        success=True,
                        message="Google Sheets successfully converted to Excel and uploaded to Drive",
                        data={
                            "conversion": conversion_result,
                            "upload": upload_result,
                            "drive_file_id": upload_result.get("file_id"),
                            "drive_file_url": upload_result.get("file_url"),
                        },
                        metadata={
                            "input_url": kwargs["google_sheets_url"],
                            "drive_folder_id": kwargs["drive_folder_id"],
                            "excel_filename": excel_filename,
                            "sheets_converted": len(conversion_result.get("converted_sheets", [])),
                            "drive_file_id": upload_result.get("file_id"),
                            "drive_file_url": upload_result.get("file_url"),
                        }
                    )
                else:
                    return UtilityResult(
                        success=False,
                        message="Excel file created but Drive upload failed",
                        error=upload_result.get("error", "Unknown upload error"),
                        data={"conversion": conversion_result}
                    )
                    
            finally:
                # Clean up temporary directory and file
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Google Sheets to Excel + Drive conversion failed",
                error=str(e)
            )
    
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute batch conversion (same as single for this utility)."""
        return self.execute_single(**kwargs)


class UtilityRegistry:
    """Registry of available utilities."""
    
    def __init__(self):
        self._utilities: Dict[str, SingleBatchUtility] = {}
        self._register_default_utilities()
    
    def _register_default_utilities(self):
        """Register the default utilities."""
        self.register("convert", ConversionUtility(
            "convert",
            "Convert between Google Sheets and Excel formats"
        ))
        
        self.register("validate", ValidationUtility(
            "validate", 
            "Run validations on spreadsheets"
        ))
        
        self.register("folder-batch", FolderBatchConversionUtility(
            "folder-batch",
            "Convert all Excel files in a folder to Google Sheets"
        ))
        
        self.register("process-forte", ForteProcessingUtility(
            "process-forte",
            "Process a Forte CSV file - validate and copy Google Sheets"
        ))
        
        self.register("sheets-to-excel-drive", SheetsToExcelDriveUtility(
            "sheets-to-excel-drive",
            "Convert Google Sheets to Excel and upload to Google Drive"
        ))
    
    def register(self, name: str, utility: SingleBatchUtility):
        """Register a new utility."""
        self._utilities[name] = utility
    
    def get_utility(self, name: str) -> Optional[SingleBatchUtility]:
        """Get a utility by name."""
        return self._utilities.get(name)
    
    def list_utilities(self) -> List[str]:
        """List all available utility names."""
        return list(self._utilities.keys())
    
    def get_utility_help(self, name: str) -> Optional[str]:
        """Get help text for a specific utility."""
        utility = self.get_utility(name)
        if utility:
            parser = utility.get_argument_parser()
            return parser.format_help()
        return None


def main():
    """Main entry point for the run_util command."""
    if len(sys.argv) < 2:
        print("Usage: urarovite run_util <utility> [utility_args...]")
        print("\nAvailable utilities:")
        registry = UtilityRegistry()
        for util_name in registry.list_utilities():
            util = registry.get_utility(util_name)
            print(f"  {util_name}: {util.description}")
        sys.exit(1)
    
    utility_name = sys.argv[1]
    utility_args = sys.argv[2:]
    
    registry = UtilityRegistry()
    utility = registry.get_utility(utility_name)
    
    if not utility:
        print(f"Unknown utility: {utility_name}")
        print("\nAvailable utilities:")
        for util_name in registry.list_utilities():
            util = registry.get_utility(util_name)
            print(f"  {util_name}: {util.description}")
        sys.exit(1)
    
    # Run the utility with the provided arguments
    run_utility_cli(utility, utility_args)


if __name__ == "__main__":
    main()
