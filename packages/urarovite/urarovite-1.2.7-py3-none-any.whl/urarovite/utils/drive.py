"""
Google Drive utilities for the Urarovite validation library.

This module provides consolidated functionality for:
- File ID extraction from various Google URLs
- File type detection and metadata retrieval
- File operations (download, upload, duplicate, move)
- Authentication and service creation
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from googleapiclient.errors import HttpError

# Configure logging
logger = logging.getLogger(__name__)

# URL pattern constants
FOLDER_ID_RE = re.compile(r"/folders/([a-zA-Z0-9-_]+)")
QUERY_ID_RE = re.compile(r"[?&]id=([a-zA-Z0-9-_]+)")
FILE_ID_PATTERNS = [
    r"/d/([a-zA-Z0-9_-]{10,})",  # /d/<id>/
    r"id=([a-zA-Z0-9_-]{10,})",  # ?id=<id>
    r"spreadsheets/d/([a-zA-Z0-9_-]{10,})",  # spreadsheets/d/<id>
    r"drive/folders/([a-zA-Z0-9_-]{10,})",  # folders/<id>
]

# MIME type constants
GOOGLE_SHEETS_MIMETYPE = "application/vnd.google-apps.spreadsheet"
EXCEL_MIMETYPES = [
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",  # .xls
    "application/vnd.ms-excel.sheet.macroEnabled.12",  # .xlsm
]

# Standard response structure
def _create_response(success: bool, **kwargs) -> Dict[str, Any]:
    """Create a standardized response dictionary."""
    response = {"success": success}
    response.update(kwargs)
    return response


def _extract_auth_secret(auth_credentials: Union[Dict[str, Any], str]) -> Optional[str]:
    """Extract auth secret from various credential formats."""
    if isinstance(auth_credentials, str):
        return auth_credentials
    
    # Try different possible keys
    for key in ["auth_secret", "encoded_credentials", "encoded_creds"]:
        if key in auth_credentials:
            return auth_credentials[key]
    
    return None


def extract_folder_id(url: str | None) -> Optional[str]:
    """Extract folder ID from Google Drive folder URL.
    
    Args:
        url: Google Drive folder URL
        
    Returns:
        Folder ID if found, None otherwise
    """
    if not url:
        return None
    
    match = FOLDER_ID_RE.search(url)
    if match:
        return match.group(1)
    
    match = QUERY_ID_RE.search(url)
    return match.group(1) if match else None


def extract_google_file_id(url: str) -> str | None:
    """Extract Google Drive file ID from various URL formats.
    
    Args:
        url: Google Drive file URL
        
    Returns:
        File ID if found, None otherwise
    """
    for pattern in FILE_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_parent_folder_id(sheets_url: str, auth_secret: str) -> Optional[str]:
    """Get the parent folder ID of a Google Sheets document.
    
    Args:
        sheets_url: URL of the Google Sheets document
        auth_secret: Base64 encoded service account credentials
        
    Returns:
        Parent folder ID, or None if not found
        
    Raises:
        Exception: If unable to access the file or Drive API
    """
    from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
    
    # Extract file ID from the URL
    file_id = extract_google_file_id(sheets_url)
    if not file_id:
        return None
    
    try:
        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)
        
        # Get file metadata including parents
        file_metadata = (
            drive_service.files().get(fileId=file_id, fields="parents").execute()
        )
        
        # Return the first parent folder ID (files can have multiple parents but usually have one)
        parents = file_metadata.get("parents", [])
        return parents[0] if parents else None
        
    except Exception as e:
        # Log the error but don't fail completely
        logger.warning(f"Failed to get parent folder for {sheets_url}: {str(e)}")
        return None


def get_file_metadata(
    file_url: str, 
    auth_credentials: Union[Dict[str, Any], str]
) -> Dict[str, Any]:
    """Get metadata for a Google Drive file including mimetype.
    
    Args:
        file_url: Google Drive file URL
        auth_credentials: Authentication credentials (dict with 'auth_secret' key or raw secret)
        
    Returns:
        Dict containing file metadata or error info
        
    Example:
        {
            "success": True,
            "id": "1ABC123...",
            "name": "My Spreadsheet",
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "is_google_sheets": True,
            "is_excel": False,
            "is_supported_spreadsheet": True
        }
    """
    from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
    
    try:
        # Extract file ID from URL
        file_id = extract_google_file_id(file_url)
        if not file_id:
            return _create_response(
                False, 
                error="invalid_url",
                error_msg="Could not extract file ID from URL"
            )
        
        # Extract auth secret
        auth_secret = _extract_auth_secret(auth_credentials)
        if not auth_secret:
            return _create_response(
                False,
                error="no_auth",
                error_msg="No authentication credentials provided"
            )
        
        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)
        
        # Get file metadata
        file_metadata = (
            drive_service.files()
            .get(
                fileId=file_id,
                fields="id,name,mimeType,parents,driveId",
                supportsAllDrives=True,
            )
            .execute()
        )
        
        mime_type = file_metadata.get("mimeType", "")
        
        # Classify file type
        is_google_sheets = mime_type == GOOGLE_SHEETS_MIMETYPE
        is_excel = mime_type in EXCEL_MIMETYPES
        is_supported_spreadsheet = is_google_sheets or is_excel
        
        return _create_response(
            True,
            id=file_metadata.get("id"),
            name=file_metadata.get("name", "Unknown"),
            mimeType=mime_type,
            is_google_sheets=is_google_sheets,
            is_excel=is_excel,
            is_supported_spreadsheet=is_supported_spreadsheet,
            parents=file_metadata.get("parents", []),
            driveId=file_metadata.get("driveId"),
        )
        
    except HttpError as e:
        error_code = f"http_{e.resp.status}"
        error_msg = str(e)
        
        return _create_response(False, error=error_code, error_msg=error_msg)
        
    except Exception as e:
        return _create_response(
            False, 
            error=f"exception_{e.__class__.__name__}", 
            error_msg=str(e)
        )


def download_file_from_drive(
    file_url: str, 
    local_path: str, 
    auth_credentials: Union[Dict[str, Any], str]
) -> Dict[str, Any]:
    """Download a file from Google Drive to local disk.
    
    Args:
        file_url: Google Drive file URL
        local_path: Local path where the file should be saved
        auth_credentials: Authentication credentials (dict with 'auth_secret' key or raw secret)
        
    Returns:
        Dict with success status and error info if applicable
    """
    from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
    from googleapiclient.http import MediaIoBaseDownload
    import io
    
    try:
        # Extract file ID from URL
        file_id = extract_google_file_id(file_url)
        if not file_id:
            return _create_response(False, error="Could not extract file ID from URL")
        
        # Extract auth secret
        auth_secret = _extract_auth_secret(auth_credentials)
        if not auth_secret:
            return _create_response(False, error="No auth_secret found in auth_credentials")
        
        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)
        
        # Download the file
        request = drive_service.files().get_media(fileId=file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        # Write to local file
        with open(local_path, "wb") as f:
            f.write(fh.getvalue())
        
        return _create_response(True, local_path=local_path)
        
    except Exception as e:
        return _create_response(False, error=f"Failed to download file: {str(e)}")


def upload_file_to_drive_folder(
    file_path: str,
    filename: str,
    folder_id: str,
    auth_credentials: Union[Dict[str, Any], str],
) -> Dict[str, Any]:
    """Upload a local file to a Google Drive folder.
    
    Args:
        file_path: Local path to the file to upload
        filename: Name to give the file in Drive
        folder_id: Google Drive folder ID where the file will be uploaded
        auth_credentials: Authentication credentials (dict with 'auth_secret' key or raw secret)
        
    Returns:
        Dict with keys:
        - success: Boolean indicating if upload succeeded
        - file_id: The ID of the uploaded file when successful, else None
        - file_url: URL of the uploaded file when successful, else None
        - error: Error message on failure, otherwise None
    """
    from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
    from googleapiclient.http import MediaFileUpload
    import os
    
    try:
        # Validate inputs
        if not os.path.exists(file_path):
            return _create_response(
                False,
                file_id=None,
                file_url=None,
                error=f"Local file not found: {file_path}"
            )
        
        if not folder_id:
            return _create_response(
                False,
                file_id=None,
                file_url=None,
                error="No folder ID provided"
            )
        
        # Extract auth secret
        auth_secret = _extract_auth_secret(auth_credentials)
        if not auth_secret:
            return _create_response(
                False,
                file_id=None,
                file_url=None,
                error="No authentication credentials provided"
            )
        
        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)
        
        # Prepare file metadata
        file_metadata = {
            "name": filename,
            "parents": [folder_id]
        }
        
        # Create media upload object
        media = MediaFileUpload(file_path, resumable=True)
        
        # Upload the file
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True
        ).execute()
        
        return _create_response(
            True,
            file_id=file.get("id"),
            file_url=file.get("webViewLink"),
            error=None
        )
        
    except Exception as e:
        return _create_response(
            False,
            file_id=None,
            file_url=None,
            error=str(e)
        )


def duplicate_file_to_drive_folder(
    drive_service: Any,
    file_url: str,
    folder_url: str,
    prefix_file_name: str | None = None,
    sheets_service: Any | None = None,
) -> Dict[str, Any]:
    """Duplicate a Google Drive file into a target folder.
    
    Args:
        drive_service: Google Drive API service instance.
        file_url: Full URL of the source Drive file to duplicate.
        folder_url: Full URL of the destination Drive folder.
        prefix_file_name: Optional string to prepend to the duplicated file's name.
        sheets_service: Optional Google Sheets API service instance. If provided,
                       will use actual spreadsheet title for Google Sheets files.
        
    Returns:
        Dict with keys:
        - success: Boolean
        - id: The ID of the newly created file when successful, else None.
        - url: URL of the duplicated file or sheet when successful, else None.
        - error: Error code string on failure, otherwise None.
        - error_msg: Optional raw error message from the API when available.
    """
    file_id = extract_google_file_id(file_url)
    
    if not file_id:
        return _create_response(False, id=None, url=None, error="Invalid file url")
    
    folder_id = extract_folder_id(folder_url)
    if not folder_id:
        return _create_response(
            False, 
            id=None, 
            url=None, 
            error="missing_or_malformed_url"
        )
    
    try:
        src = (
            drive_service.files()
            .get(fileId=file_id, fields="id,name,mimeType", supportsAllDrives=True)
            .execute()
        )
        
        src_mime = src.get("mimeType", "")
        
        # Get the proper filename - use spreadsheet title for Google Sheets if possible
        if src_mime == GOOGLE_SHEETS_MIMETYPE and sheets_service:
            try:
                # Get actual spreadsheet title from Sheets API
                spreadsheet_metadata = (
                    sheets_service.spreadsheets()
                    .get(spreadsheetId=file_id, fields="properties.title")
                    .execute()
                )
                spreadsheet_title = spreadsheet_metadata.get("properties", {}).get(
                    "title", ""
                )
                
                if spreadsheet_title:
                    # Only sanitize if title contains invalid filesystem characters
                    invalid_chars = '<>:"/\\|?*'
                    if any(char in spreadsheet_title for char in invalid_chars):
                        # Minimal sanitization - only replace problematic characters
                        name = "".join(
                            c if c not in invalid_chars else "_"
                            for c in spreadsheet_title
                        ).rstrip()
                    else:
                        name = spreadsheet_title
                else:
                    # Fallback to Drive API name
                    name = src.get("name", "Copy")
            except Exception:
                # Fallback to Drive API name if Sheets API fails
                name = src.get("name", "Copy")
        else:
            # Use Drive API name for non-spreadsheet files or when no Sheets service
            name = src.get("name", "Copy")
        
        if prefix_file_name:
            name = f"{prefix_file_name}{name}"
        
        body = {"name": name, "parents": [folder_id]}
        dup = (
            drive_service.files()
            .copy(
                fileId=file_id,
                body=body,
                fields="id,webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )
        
        new_id = dup.get("id")
        
        if src_mime == GOOGLE_SHEETS_MIMETYPE:
            new_url = f"https://docs.google.com/spreadsheets/d/{new_id}/edit"
        else:
            new_url = (
                dup.get("webViewLink")
                or f"https://drive.google.com/file/d/{new_id}/view"
            )
        
        return _create_response(True, id=new_id, url=new_url, error=None)
        
    except Exception as e:
        msg = str(e)
        if "HttpError 403" in msg or "HttpError 404" in msg:
            return _create_response(
                False,
                id=None,
                url=None,
                error="forbidden_or_not_found",
                error_msg=msg,
            )
        return _create_response(
            False,
            id=None,
            url=None,
            error=f"request_exception:{e.__class__.__name__}",
            error_msg=msg,
        )


def move_sheets_to_folder(
    drive_service: Any,
    sheet_urls: List[str],
    folder_url: str,
) -> List[Dict[str, Any]]:
    """Move files to the destination folder.
    
    - If only_google_sheets=True, skips non‑Sheets files.
    - Works with My Drive and Shared drives (if you have permission).
    
    Args:
        drive_service: Google Drive API service instance
        sheet_urls: List of file URLs to move
        folder_url: Destination folder URL
        
    Returns:
        List of dictionaries, one for each file, with keys:
        - success: Boolean
        - id: The ID of the moved file when successful, else None.
        - name: Name of the file when successful, else None.
        - error: Error code string on failure, otherwise None.
        - error_msg: Optional raw error message from the API when available.
    """
    results = []
    
    # Extract folder ID from URL
    folder_id = extract_folder_id(folder_url)
    if not folder_id:
        # Return error for all files if folder URL is invalid
        return [
            _create_response(
                False,
                id=None,
                name=None,
                error="missing_or_malformed_folder_url",
                error_msg=f"Could not extract folder ID from: {folder_url}",
            )
            for _ in sheet_urls
        ]
    
    # We'll set supportsAllDrives on read & write in case of Shared drives
    for sheet_url in sheet_urls:
        # Extract file ID from URL
        file_id = extract_google_file_id(sheet_url)
        if not file_id:
            results.append(
                _create_response(
                    False,
                    id=None,
                    name=None,
                    error="invalid_file_url",
                    error_msg=f"Could not extract file ID from: {sheet_url}",
                )
            )
            continue
        
        try:
            file = (
                drive_service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, parents, mimeType, driveId",
                    supportsAllDrives=True,
                )
                .execute()
            )
            
            name = file.get("name", "Unknown")
            parents = file.get("parents", [])
            
            add_parents = folder_id
            remove_parents = ",".join(parents) if parents else ""
            
            drive_service.files().update(
                fileId=file_id,
                addParents=add_parents,
                removeParents=remove_parents,
                fields="id, name, parents",
                supportsAllDrives=True,
            ).execute()
            
            results.append(
                _create_response(True, id=file_id, name=name, error=None, error_msg=None)
            )
            
        except HttpError as e:
            # Helpful error context
            status = getattr(e, "status_code", None) or getattr(e, "resp", {}).get(
                "status"
            )
            error_msg = f"HTTP {status} - {e}"
            
            if status in [403, 404]:
                error_code = "forbidden_or_not_found"
            else:
                error_code = f"http_error_{status}"
            
            results.append(
                _create_response(
                    False,
                    id=file_id,
                    name=None,
                    error=error_code,
                    error_msg=error_msg,
                )
            )
            
        except Exception as e:
            results.append(
                _create_response(
                    False,
                    id=file_id,
                    name=None,
                    error=f"request_exception:{e.__class__.__name__}",
                    error_msg=str(e),
                )
            )
    
    return results


def extract_original_filename_from_source(
    source_url_or_path: str,
    auth_credentials: Union[Dict[str, Any], str],
    downloaded_file_path: str = None,
) -> Dict[str, Any]:
    """Extract the original filename from various spreadsheet sources using existing utilities.
    
    This function consolidates filename extraction logic from multiple sources:
    1. Custom filename (if provided)
    2. Google Sheets API title (for spreadsheet URLs)
    3. Excel file content (first sheet name)
    4. Drive API metadata
    5. Local file path
    6. Fallback names
    
    Args:
        source_url_or_path: URL or file path to extract filename from
        auth_credentials: Authentication credentials (dict with 'auth_secret' key or raw secret)
        downloaded_file_path: Optional path to downloaded Excel file for content extraction
        
    Returns:
        Dict with keys:
        - success: Boolean indicating if extraction succeeded
        - filename: Extracted filename if successful, else fallback name
        - source: String indicating which method was used
        - error: Error message on failure, otherwise None
    """
    try:
        from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
        
        # Try Google Sheets API title first (most reliable for spreadsheets)
        file_id = extract_google_file_id(source_url_or_path)
        if file_id and source_url_or_path.startswith("http"):
            try:
                auth_secret = _extract_auth_secret(auth_credentials)
                if auth_secret:
                    sheets_service = create_sheets_service_from_encoded_creds(auth_secret)
                    
                    # Get actual spreadsheet title from Sheets API
                    spreadsheet_metadata = (
                        sheets_service.spreadsheets()
                        .get(spreadsheetId=file_id, fields="properties.title")
                        .execute()
                    )
                    spreadsheet_title = spreadsheet_metadata.get("properties", {}).get("title", "")
                    
                    if spreadsheet_title:
                        # For Google Sheets, preserve the full original title
                        # Only replace truly invalid characters that Google Sheets doesn't allow
                        invalid_chars = '<>:"/\\|?*'
                        if any(char in spreadsheet_title for char in invalid_chars):
                            filename = "".join(
                                c if c not in invalid_chars else "_"
                                for c in spreadsheet_title
                            ).rstrip()
                        else:
                            filename = spreadsheet_title
                        
                        return _create_response(
                            True,
                            filename=filename,
                            source="sheets_api_title",
                            error=None
                        )
            except Exception as e:
                # Continue to next method
                pass
        
        # Try to get original name from Drive API metadata first (before Excel content)
        # This helps when we have an Excel file that was converted from Google Sheets
        if file_id:
            try:
                metadata = get_file_metadata(source_url_or_path, auth_credentials)
                if metadata.get("success") and metadata.get("name"):
                    original_name = metadata["name"]
                    # Remove extension if present
                    if original_name.endswith('.xlsx'):
                        original_name = original_name[:-5]
                    elif original_name.endswith('.xls'):
                        original_name = original_name[:-4]
                    
                    # For Google Sheets, use more permissive naming (preserve more characters)
                    # Google Sheets allows more characters than filesystem-safe names
                    invalid_chars = '<>:"/\\|?*'
                    if any(char in original_name for char in invalid_chars):
                        filename = "".join(
                            c if c not in invalid_chars else "_"
                            for c in original_name
                        ).rstrip()
                    else:
                        filename = original_name
                    
                    # Clean up common conversion suffixes that might have been added
                    # Remove patterns like "_excel_1", "_excel_2", etc.
                    import re
                    filename = re.sub(r'_excel_\d+$', '', filename)
                    # Remove patterns like "_1", "_2" at the end if they look like conversion suffixes
                    filename = re.sub(r'_\d+$', '', filename)
                    
                    return _create_response(
                        True,
                        filename=filename,
                        source="drive_metadata",
                        error=None
                    )
            except Exception as e:
                # Continue to next method
                pass
        
        # Try Excel content extraction (for downloaded files)
        if downloaded_file_path:
            try:
                import pandas as pd
                excel_file = pd.ExcelFile(downloaded_file_path)
                if excel_file.sheet_names:
                    first_sheet = excel_file.sheet_names[0]
                    # For Google Sheets, use more permissive naming (preserve more characters)
                    # Google Sheets allows more characters than filesystem-safe names
                    invalid_chars = '<>:"/\\|?*'
                    if any(char in first_sheet for char in invalid_chars):
                        filename = "".join(
                            c if c not in invalid_chars else "_"
                            for c in first_sheet
                        ).rstrip()
                    else:
                        filename = first_sheet
                    
                    if filename and filename != "unnamed_sheet":
                        return _create_response(
                            True,
                            filename=filename,
                            source="excel_content",
                            error=None
                        )
            except Exception as e:
                # Continue to next method
                pass
        

        
        # Try local file path
        if not source_url_or_path.startswith("http"):
            import pathlib
            filename = pathlib.Path(source_url_or_path).stem
            if filename:
                return _create_response(
                    True,
                    filename=filename,
                    source="local_file",
                    error=None
                )
        
        # Fallback names
        if file_id:
            fallback_name = f"Excel_File_{file_id[:8]}"
        else:
            fallback_name = "Converted_Excel_File"
        
        return _create_response(
            True,
            filename=fallback_name,
            source="fallback",
            error="Could not extract original filename, using fallback"
        )
        
    except Exception as e:
        return _create_response(
            False,
            filename="Converted_Excel_File",
            source="error_fallback",
            error=str(e)
        )


def detect_spreadsheet_type(
    source_url_or_path: str, 
    auth_secret: str | None = None
) -> Dict[str, Any]:
    """Centralized spreadsheet file type detection for the entire codebase.
    
    This function provides unified file type detection that handles:
    - Google Sheets URLs (docs.google.com and sheets.google.com)
    - Google Drive URLs with mimetype detection
    - Local Excel files (.xlsx, .xls, .xlsm)
    
    Args:
        source_url_or_path: URL or file path to analyze
        auth_secret: Base64 encoded service account credentials (required for
                    Drive API calls)
        
    Returns:
        Dict containing detection results:
        {
            "file_type": str,           # "google_sheets", "excel_from_drive",
                                       # "local_excel", or "unknown"
            "is_google_sheets": bool,   # True if Google Sheets document
            "is_excel_file": bool,      # True if Excel file (local or from Drive)
            "is_supported": bool,       # True if supported spreadsheet format
            "source_type": str,         # "google_direct", "google_drive",
                                       # "local_file", "unknown"
            "requires_auth": bool,      # True if authentication is needed
            "metadata": Dict,           # Additional file metadata (for Drive files)
            "error": str | None,        # Error message if detection failed
        }
        
    Example:
        >>> result = detect_spreadsheet_type("https://drive.google.com/.../view",
                                           auth_secret)
        >>> print(result["file_type"])  # "google_sheets"
        >>> print(result["is_supported"])  # True
    """
    # Initialize result structure
    result = {
        "file_type": "unknown",
        "is_google_sheets": False,
        "is_excel_file": False,
        "is_supported": False,
        "source_type": "unknown",
        "requires_auth": False,
        "metadata": {},
        "error": None,
    }
    
    try:
        # Detect URL patterns and source type
        is_google_url = (
            "docs.google.com" in source_url_or_path
            or "sheets.google.com" in source_url_or_path
        )
        is_drive_url = "drive.google.com" in source_url_or_path
        is_local_file = not (is_google_url or is_drive_url)
        
        if is_google_url:
            # Google URL - but need to check if it's actually a Google Sheet or Excel file
            result.update(
                {
                    "source_type": "google_direct",
                    "requires_auth": True,
                }
            )
            
            # Even docs.google.com URLs can point to Excel files hosted on Drive
            # We need to check the actual mimetype to be sure
            if auth_secret:
                # Get actual file metadata to determine type
                metadata_result = get_file_metadata(source_url_or_path, auth_secret)
                if metadata_result.get("success"):
                    mime_type = metadata_result.get("mimeType", "")
                    result["metadata"] = metadata_result
                    
                    if mime_type == GOOGLE_SHEETS_MIMETYPE:
                        result.update(
                            {
                                "file_type": "google_sheets",
                                "is_google_sheets": True,
                                "is_supported": True,
                            }
                        )
                    elif mime_type in EXCEL_MIMETYPES:
                        result.update(
                            {
                                "file_type": "excel_from_drive",
                                "is_excel_file": True,
                                "is_supported": True,
                            }
                        )
                    else:
                        result.update(
                            {
                                "file_type": "unsupported_drive_file",
                                "error": f"Unsupported file type: {mime_type}",
                            }
                        )
                else:
                    # Metadata retrieval failed - fall back to assuming Google Sheets
                    logger.warning(
                        f"Could not get metadata for {source_url_or_path}, "
                        "assuming Google Sheets"
                    )
                    result.update(
                        {
                            "file_type": "google_sheets",
                            "is_google_sheets": True,
                            "is_supported": True,
                            "error": "metadata_unavailable_assuming_sheets",
                        }
                    )
            else:
                # No auth provided - assume Google Sheets with warning
                logger.warning(
                    f"No auth provided for Google URL {source_url_or_path}, "
                    "assuming Google Sheets"
                )
                result.update(
                    {
                        "file_type": "google_sheets",
                        "is_google_sheets": True,
                        "is_supported": True,
                        "error": "no_auth_assuming_sheets",
                    }
                )
                
        elif is_drive_url:
            # Google Drive URL - need to check mimetype
            result["source_type"] = "google_drive"
            result["requires_auth"] = True
            
            if auth_secret:
                # Get actual file metadata to determine type
                metadata_result = get_file_metadata(source_url_or_path, auth_secret)
                if metadata_result.get("success"):
                    mime_type = metadata_result.get("mimeType", "")
                    result["metadata"] = metadata_result
                    
                    if mime_type == GOOGLE_SHEETS_MIMETYPE:
                        result.update(
                            {
                                "file_type": "google_sheets",
                                "is_google_sheets": True,
                                "is_supported": True,
                            }
                        )
                    elif mime_type in EXCEL_MIMETYPES:
                        result.update(
                            {
                                "file_type": "excel_from_drive",
                                "is_excel_file": True,
                                "is_supported": True,
                            }
                        )
                    else:
                        result.update(
                            {
                                "file_type": "unsupported_drive_file",
                                "error": f"Unsupported file type: {mime_type}",
                            }
                        )
                else:
                    # Metadata retrieval failed - use fallback logic
                    logger.warning(
                        f"Could not get metadata for {source_url_or_path}, "
                        "assuming Google Sheets"
                    )
                    result.update(
                        {
                            "file_type": "google_sheets",
                            "is_google_sheets": True,
                            "is_supported": True,
                            "error": "metadata_unavailable_assuming_sheets",
                        }
                    )
            else:
                # No auth provided - assume Google Sheets with warning
                logger.warning(
                    f"No auth provided for Drive URL {source_url_or_path}, "
                    "assuming Google Sheets"
                )
                result.update(
                    {
                        "file_type": "google_sheets",
                        "is_google_sheets": True,
                        "is_supported": True,
                        "error": "no_auth_assuming_sheets",
                    }
                )
                
        elif is_local_file:
            # Local file - check extension
            result["source_type"] = "local_file"
            result["requires_auth"] = False
            
            path = Path(source_url_or_path)
            extension = path.suffix.lower()
            
            if extension in [".xlsx", ".xls", ".xlsm"]:
                result.update(
                    {
                        "file_type": "local_excel",
                        "is_excel_file": True,
                        "is_supported": True,
                        "metadata": {
                            "name": path.name,
                            "extension": extension,
                            "exists": path.exists() if path.is_absolute() else None,
                        },
                    }
                )
            else:
                result.update(
                    {
                        "file_type": "unsupported_local_file",
                        "error": f"Unsupported file extension: {extension}",
                    }
                )
                
        else:
            # Unknown URL pattern
            result.update(
                {
                    "file_type": "unknown",
                    "error": "unrecognized_url_pattern",
                }
            )
            
        # Log detection result
        logger.debug(
            f"Detected file type: {result['file_type']} for {source_url_or_path}"
        )
        
    except Exception as e:
        logger.error(f"Error detecting file type for {source_url_or_path}: {e}")
        result.update(
            {
                "file_type": "detection_error",
                "error": f"detection_failed: {str(e)}",
            }
        )
    
    return result


# Backward compatibility aliases
download_drive_file = download_file_from_drive
get_drive_file_metadata = get_file_metadata
