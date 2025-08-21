"""Simple spreadsheet conversion utilities.

This module provides two focused utilities:
1. Single file converter - Convert one Google Sheet or Excel file to another format
2. Batch converter - Process links from specified columns in a metadata file
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Union

from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
from urarovite.utils.sheets import extract_sheet_id, get_sheet_values, create_new_spreadsheet_in_folder
from urarovite.utils.generic_spreadsheet import (
    convert_google_sheets_to_excel,
    convert_excel_to_google_sheets,
)
from urarovite.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def convert_single_file(
    input_file: str,
    output_path: Union[str, Path],
    auth_credentials: Dict[str, Any],
    sheet_names: List[str] | None = None,
    output_folder: Union[str, Path] | None = None,
    drive_folder_id: str | None = None,
    output_filename: str | None = None,
) -> Dict[str, Any]:
    """Convert a single Google Sheet or Excel file to another format.
    
    Args:
        input_file: Google Sheets URL or local Excel file path to convert
        output_path: Path where converted file should be saved (or Google Sheets URL for Excel input)
        auth_credentials: Authentication credentials for Google Sheets
        sheet_names: Optional list of specific sheet names to convert
        output_folder: Optional folder path for output (overrides output_path if provided)
        drive_folder_id: Optional Google Drive folder ID for creating new Google Sheets
        output_filename: Optional custom filename (without extension) for the output file
        
    Returns:
        Dictionary with conversion results
    """
    try:
        # Determine if input is Google Sheets or local Excel
        if input_file.startswith("http") and "docs.google.com" in input_file:
            # Google Sheets to Excel
            if output_folder:
                # Create output folder and generate filename
                folder_path = Path(output_folder)
                folder_path.mkdir(parents=True, exist_ok=True)
                
                if output_filename:
                    # Use custom filename
                    filename = f"{output_filename}.xlsx"
                else:
                    # Generate filename from sheet title or ID
                    sheet_id = extract_sheet_id(input_file)
                    filename = f"sheet_{sheet_id}.xlsx"
                
                excel_path = folder_path / filename
            else:
                if output_path is None:
                    # Use "auto" to let the conversion function use the original sheet title
                    excel_path = "auto"
                else:
                    excel_path = output_path
            
            result = convert_google_sheets_to_excel(
                google_sheets_url=input_file,
                excel_file_path=str(excel_path),
                auth_credentials=auth_credentials,
                sheet_names=sheet_names,
            )
        else:
            # Excel to Google Sheets
            if output_folder:
                # For Excel input with output folder, we need to create a new Google Sheet
                # This would require Drive API access to create sheets
                raise ValidationError("Output folder option not yet supported for Excel to Google Sheets conversion")
            
            # Handle "auto" case for creating new Google Sheets
            if str(output_path) == "auto":
                google_sheets_url = "auto"
            elif output_path.startswith("http") and "docs.google.com" in str(output_path):
                google_sheets_url = str(output_path)
            else:
                raise ValidationError("For Excel input, output_path must be a Google Sheets URL or 'auto' to create new sheet")
            
            result = convert_excel_to_google_sheets(
                excel_file_path=input_file,
                google_sheets_url=google_sheets_url,
                auth_credentials=auth_credentials,
                sheet_names=sheet_names,
                drive_folder_id=drive_folder_id,
            )
        
        if result["success"]:
            if "output_path" in result:
                logger.info(f"Successfully converted file to {result['output_path']}")
            else:
                logger.info(f"Successfully converted file to Google Sheets")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to convert file {input_file}: {e}")
        return {
            "success": False,
            "error": str(e),
            "output_path": None,
            "converted_sheets": [],
        }


def convert_batch_from_metadata(
    metadata_file: str,
    output_location: Union[str, Path],
    auth_credentials: Dict[str, Any],
    link_columns: List[str],
    output_format: str = "excel",
) -> Dict[str, Any]:
    """Convert multiple sheets/files based on links found in specified columns.
    
    Args:
        metadata_file: Google Sheets URL or local Excel file path containing metadata
        output_location: Directory (for Excel output) or Google Drive folder URL (for Sheets output)
        auth_credentials: Authentication credentials for Google Sheets
        link_columns: List of column names that contain links to sheets/files to convert
        output_format: Output format - "excel" or "sheets"
        
    Returns:
        Dictionary with batch conversion results
    """
    try:
        # Determine if metadata file is Google Sheets or local Excel
        is_google_sheets = metadata_file.startswith("http") and "docs.google.com" in metadata_file
        
        if is_google_sheets:
            # Handle Google Sheets metadata file
            return _process_google_sheets_metadata(
                metadata_file, output_location, auth_credentials, link_columns, output_format
            )
        else:
            # Handle local Excel metadata file
            return _process_excel_metadata(
                metadata_file, output_location, auth_credentials, link_columns, output_format
            )
            
    except Exception as e:
        logger.error(f"Batch conversion failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "metadata_file": metadata_file,
            "output_location": str(output_location),
            "successful_conversions": [],
            "failed_conversions": [],
        }


def _process_google_sheets_metadata(
    metadata_sheet_url: str,
    output_location: Union[str, Path],
    auth_credentials: Dict[str, Any],
    link_columns: List[str],
    output_format: str,
) -> Dict[str, Any]:
    """Process metadata from Google Sheets file."""
    try:
        # Extract sheet ID from metadata URL
        metadata_sheet_id = extract_sheet_id(metadata_sheet_url)
        if not metadata_sheet_id:
            raise ValidationError(f"Invalid metadata sheet URL: {metadata_sheet_url}")
        
        # Get sheets service
        encoded_creds = auth_credentials.get("auth_secret")
        if not encoded_creds:
            raise ValidationError("No auth_secret found in auth_credentials")
        
        sheets_service = create_sheets_service_from_encoded_creds(encoded_creds)
        
        # Read metadata sheet
        logger.info(f"Reading metadata from Google Sheets: {metadata_sheet_url}")
        values_result = get_sheet_values(sheets_service, metadata_sheet_id, "A:Z")
        
        if not values_result["success"] or not values_result.get("values"):
            raise ValidationError(f"Failed to read metadata sheet: {values_result.get('error', 'No data')}")
        
        values = values_result["values"]
        if len(values) < 2:
            raise ValidationError("Metadata sheet must have at least a header row and one data row")
        
        return _process_metadata_values(
            values, output_location, auth_credentials, link_columns, output_format, "Google Sheets"
        )
        
    except Exception as e:
        logger.error(f"Failed to process Google Sheets metadata: {e}")
        raise


def _process_excel_metadata(
    metadata_file_path: str,
    output_location: Union[str, Path],
    auth_credentials: Dict[str, Any],
    link_columns: List[str],
    output_format: str,
) -> Dict[str, Any]:
    """Process metadata from local Excel file."""
    try:
        # TODO: Implement Excel file reading
        # For now, raise error as this needs pandas/openpyxl implementation
        raise ValidationError("Excel metadata file processing not yet implemented")
        
    except Exception as e:
        logger.error(f"Failed to process Excel metadata: {e}")
        raise


def _process_metadata_values(
    values: List[List[Any]],
    output_location: Union[str, Path],
    auth_credentials: Dict[str, Any],
    link_columns: List[str],
    output_format: str,
    source_type: str,
) -> Dict[str, Any]:
    """Process metadata values and extract links from specified columns."""
    try:
        # Parse headers
        headers = [str(cell).strip().lower() for cell in values[0]]
        
        # Find link column indices
        link_column_indices = []
        for link_col in link_columns:
            col_idx = None
            for i, header in enumerate(headers):
                if link_col.lower() in header:
                    col_idx = i
                    break
            if col_idx is not None:
                link_column_indices.append(col_idx)
            else:
                logger.warning(f"Link column '{link_col}' not found in metadata")
        
        if not link_column_indices:
            raise ValidationError(f"No link columns found. Available columns: {headers}")
        
        # Extract all unique URLs from link columns
        all_urls = set()
        for row_idx, row in enumerate(values[1:], 1):  # Skip header row
            for col_idx in link_column_indices:
                if len(row) > col_idx and row[col_idx]:
                    url = str(row[col_idx]).strip()
                    if url.startswith("http") and "docs.google.com" in url:
                        all_urls.add(url)
        
        if not all_urls:
            logger.warning("No valid Google Sheets URLs found in specified columns")
            return {
                "success": True,
                "metadata_source": source_type,
                "output_location": str(output_location),
                "total_processed": 0,
                "successful_conversions": [],
                "failed_conversions": [],
                "success_count": 0,
                "failure_count": 0,
            }
        
        # Convert each unique URL
        successful_conversions = []
        failed_conversions = []
        
        for url in all_urls:
            try:
                logger.info(f"Converting {url}")
                
                if output_format == "excel":
                    # Convert to Excel
                    output_path = Path(output_location)
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    # Generate filename from sheet title or ID
                    sheet_id = extract_sheet_id(url)
                    filename = f"sheet_{sheet_id}.xlsx"
                    output_file = output_path / filename
                    
                    result = convert_single_file(
                        input_file=url,
                        output_path=output_file,
                        auth_credentials=auth_credentials,
                    )
                    
                    if result["success"]:
                        successful_conversions.append({
                            "source_url": url,
                            "output_path": str(output_file),
                            "converted_sheets": result["converted_sheets"],
                        })
                    else:
                        failed_conversions.append({
                            "source_url": url,
                            "error": result["error"],
                        })
                
                elif output_format == "sheets":
                    # Convert to Google Sheets
                    if not str(output_location).startswith("http") or "docs.google.com" not in str(output_location):
                        raise ValidationError("For Google Sheets output, output_location must be a Google Sheets URL")
                    
                    # For Google Sheets output, we need to create a new sheet for each URL
                    # This is more complex and would require creating multiple sheets
                    logger.warning("Google Sheets output format for batch conversion requires creating multiple sheets - not yet implemented")
                    failed_conversions.append({
                        "source_url": url,
                        "error": "Google Sheets batch output not yet implemented - would require creating multiple sheets",
                    })
                
            except Exception as e:
                logger.error(f"Failed to convert {url}: {e}")
                failed_conversions.append({
                    "source_url": url,
                    "error": str(e),
                })
        
        return {
            "success": True,
            "metadata_source": source_type,
            "output_location": str(output_location),
            "total_processed": len(all_urls),
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions,
            "success_count": len(successful_conversions),
            "failure_count": len(failed_conversions),
        }
        
    except Exception as e:
        logger.error(f"Failed to process metadata values: {e}")
        raise


def create_safe_filename(name: str, fallback_id: str = "") -> str:
    """Create a filesystem-safe filename.
    
    Args:
        name: Original name
        fallback_id: Fallback identifier if name is empty
        
    Returns:
        Safe filename
    """
    if not name:
        name = f"sheet_{fallback_id}" if fallback_id else "unnamed_sheet"
    
    # Remove or replace unsafe characters
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_', '.')).strip()
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = f"sheet_{fallback_id}" if fallback_id else "unnamed_sheet"
    
    return safe_name


def convert_folder_batch(
    input_folder: Union[str, Path],
    drive_folder_id: str,
    auth_credentials: Dict[str, Any],
    input_column_name: str = "input_url",
    output_column_name: str = "output_url",
    metadata_sheet_name: str = "conversion_metadata",
) -> Dict[str, Any]:
    """Convert all Excel files in a folder to Google Sheets and create a metadata sheet.
    
    Args:
        input_folder: Local folder containing Excel files to convert
        drive_folder_id: Google Drive folder ID where converted sheets will be created
        auth_credentials: Authentication credentials for Google Sheets
        input_column_name: Name for the input file column in metadata sheet
        output_column_name: Name for the output URL column in metadata sheet
        metadata_sheet_name: Name for the metadata sheet to create
        
    Returns:
        Dictionary with conversion results including metadata sheet URL
    """
    try:
        input_path = Path(input_folder)
        
        if not input_path.exists() or not input_path.is_dir():
            raise ValidationError(f"Input folder does not exist or is not a directory: {input_path}")
        
        # Find all Excel files in the input folder
        excel_extensions = ['.xlsx', '.xls', '.xlsm']
        excel_files = []
        for ext in excel_extensions:
            excel_files.extend(input_path.glob(f"*{ext}"))
        
        if not excel_files:
            raise ValidationError(f"No Excel files found in {input_path}")
        
        logger.info(f"Found {len(excel_files)} Excel files to convert")
        
        # Convert each Excel file to Google Sheets
        conversion_results = []
        successful_conversions = 0
        failed_conversions = 0
        
        for excel_file in excel_files:
            try:
                logger.info(f"Converting {excel_file.name}...")
                
                # Use the filename (without extension) as the Google Sheets name
                sheet_name = excel_file.stem
                
                result = convert_excel_to_google_sheets(
                    excel_file_path=excel_file,
                    google_sheets_url="auto",
                    auth_credentials=auth_credentials,
                    drive_folder_id=drive_folder_id,
                )
                
                if result["success"]:
                    conversion_results.append({
                        input_column_name: str(excel_file),
                        output_column_name: result["output_url"],
                        "status": "success",
                        "converted_sheets": result["converted_sheets"]
                    })
                    successful_conversions += 1
                    logger.info(f"✅ Successfully converted {excel_file.name}")
                else:
                    conversion_results.append({
                        input_column_name: str(excel_file),
                        output_column_name: "",
                        "status": "failed",
                        "error": result["error"]
                    })
                    failed_conversions += 1
                    logger.warning(f"❌ Failed to convert {excel_file.name}: {result['error']}")
                    
            except Exception as e:
                conversion_results.append({
                    input_column_name: str(excel_file),
                    output_column_name: "",
                    "status": "failed",
                    "error": str(e)
                })
                failed_conversions += 1
                logger.warning(f"❌ Failed to convert {excel_file.name}: {str(e)}")
        
        # Create metadata sheet with conversion results
        logger.info("Creating metadata sheet...")
        
        # Create gspread client for metadata sheet creation
        import gspread
        from urarovite.auth.google_sheets import decode_service_account
        
        if isinstance(auth_credentials, dict):
            encoded_creds = auth_credentials.get("auth_secret")
            if not encoded_creds:
                raise ValidationError("No auth_secret found in auth_credentials")
        else:
            encoded_creds = auth_credentials
        
        service_account_info = decode_service_account(encoded_creds)
        gspread_client = gspread.service_account_from_dict(service_account_info)
        
        # Create metadata spreadsheet
        metadata_spreadsheet = create_new_spreadsheet_in_folder(
            gspread_client, drive_folder_id, metadata_sheet_name
        )
        
        if not metadata_spreadsheet:
            raise ValidationError(f"Failed to create metadata sheet in folder {drive_folder_id}")
        
        # Prepare data for the metadata sheet
        headers = [input_column_name, output_column_name, "status", "converted_sheets", "error"]
        rows = [headers]
        
        for result in conversion_results:
            row = [
                result.get(input_column_name, ""),
                result.get(output_column_name, ""),
                result.get("status", ""),
                ", ".join(result.get("converted_sheets", [])) if result.get("converted_sheets") else "",
                result.get("error", "")
            ]
            rows.append(row)
        
        # Write data to the metadata sheet
        worksheet = metadata_spreadsheet.sheet1
        worksheet.update(rows)
        
        # Format the header row (make it bold)
        try:
            worksheet.format('A1:E1', {'textFormat': {'bold': True}})
        except Exception as e:
            logger.warning(f"Could not format header row: {e}")
        
        metadata_url = metadata_spreadsheet.url
        logger.info(f"✅ Created metadata sheet: {metadata_url}")
        
        return {
            "success": True,
            "total_files": len(excel_files),
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions,
            "metadata_sheet_url": metadata_url,
            "conversion_results": conversion_results,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Folder batch conversion failed: {str(e)}")
        return {
            "success": False,
            "total_files": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "metadata_sheet_url": None,
            "conversion_results": [],
            "error": str(e)
        }
