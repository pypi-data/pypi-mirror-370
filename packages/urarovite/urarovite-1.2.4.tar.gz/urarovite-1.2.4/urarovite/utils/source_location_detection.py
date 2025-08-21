"""Utilities for detecting source location and determining intelligent defaults.

This module provides functions to analyze spreadsheet sources and determine
appropriate default target locations for duplication.
"""

import re
from typing import Dict, Any, Optional
from pathlib import Path


def determine_source_location(source: str) -> Dict[str, Any]:
    """Determine the location and type of the source spreadsheet.

    Args:
        source: Source spreadsheet path or URL

    Returns:
        Dict with keys:
        - is_remote: Whether the source is remote (Google Sheets)
        - is_google_sheets: Whether the source is Google Sheets
        - location_type: "google_drive", "local", or "unknown"
        - spreadsheet_id: Google Sheets ID if applicable
        - suggested_target: Suggested target location
        - suggested_format: Suggested target format
    """
    # Check if source is a Google Sheets URL
    if isinstance(source, str) and (
        "docs.google.com" in source or "sheets.google.com" in source
    ):
        # Extract spreadsheet ID from URL
        spreadsheet_id = extract_google_sheets_id(source)

        return {
            "is_remote": True,
            "is_google_sheets": True,
            "location_type": "google_drive",
            "spreadsheet_id": spreadsheet_id,
            "suggested_target": None,  # Will be determined by parent folder lookup
            "suggested_format": "sheets",
        }
    else:
        # Local file (Excel or other)
        Path(source)

        return {
            "is_remote": False,
            "is_google_sheets": False,
            "location_type": "local",
            "spreadsheet_id": None,
            "suggested_target": "local",
            "suggested_format": "excel",
        }


def extract_google_sheets_id(url: str) -> Optional[str]:
    """Extract Google Sheets ID from URL.

    Args:
        url: Google Sheets URL

    Returns:
        Spreadsheet ID or None if not found
    """
    # Pattern to match Google Sheets URLs and extract the ID
    patterns = [
        r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
        r"id=([a-zA-Z0-9-_]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_google_sheets_parent_folder(
    spreadsheet_id: str, auth_secret: str
) -> Optional[str]:
    """Get the parent folder ID of a Google Sheets document.

    Args:
        spreadsheet_id: Google Sheets document ID
        auth_secret: Base64 encoded authentication credentials

    Returns:
        Parent folder ID or None if not found/accessible
    """
    try:
        from urarovite.auth.google_drive import create_drive_service_from_encoded_creds

        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)

        # Get file metadata including parents
        file_metadata = (
            drive_service.files().get(fileId=spreadsheet_id, fields="parents").execute()
        )

        parents = file_metadata.get("parents", [])
        if parents:
            # Return the first parent folder ID
            return parents[0]

        return None

    except Exception as e:
        # If we can't get the parent folder, return None
        import logging

        logging.warning(f"Could not get parent folder for {spreadsheet_id}: {e}")
        return None


def determine_intelligent_default_target(
    source: str, auth_secret: Optional[str] = None
) -> Dict[str, Any]:
    """Determine intelligent default target based on source location.

    Args:
        source: Source spreadsheet path or URL
        auth_secret: Authentication secret for Google operations

    Returns:
        Dict with keys: target, target_format, reasoning
    """
    source_info = determine_source_location(source)

    if source_info["is_remote"] and source_info["is_google_sheets"]:
        # Source is Google Sheets - try to duplicate in same location
        if auth_secret and source_info["spreadsheet_id"]:
            # Try to get parent folder
            parent_folder = get_google_sheets_parent_folder(
                source_info["spreadsheet_id"], auth_secret
            )

            if parent_folder:
                return {
                    "target": parent_folder,
                    "target_format": "sheets",
                    "reasoning": f"Source is in Google Drive folder {parent_folder}, duplicating to same location",
                }
            else:
                # Fallback: try to duplicate in Drive root (My Drive)
                # For now, we'll use local as fallback since we can't easily target "My Drive"
                return {
                    "target": "local",
                    "target_format": "excel",
                    "reasoning": "Source is Google Sheets but parent folder not accessible, using local Excel as fallback",
                }
        else:
            # No auth or can't determine folder - fallback to local
            return {
                "target": "local",
                "target_format": "excel",
                "reasoning": "Source is Google Sheets but no authentication provided, using local Excel",
            }
    else:
        # Source is local - keep duplicate local
        return {
            "target": "local",
            "target_format": "excel",
            "reasoning": "Source is local file, creating local duplicate",
        }


def validate_target_compatibility(
    source: str, target: str, target_format: str
) -> Dict[str, Any]:
    """Validate that target and format are compatible with source.

    Args:
        source: Source spreadsheet path or URL
        target: Target location
        target_format: Target format

    Returns:
        Dict with keys: is_valid, warnings, errors
    """
    source_info = determine_source_location(source)
    warnings = []
    errors = []

    # Check format constraints
    if target_format == "sheets" and target == "local":
        errors.append(
            "Format 'sheets' is only allowed for remote targets (Google Drive folder ID)"
        )

    # Check authentication requirements
    if source_info["is_google_sheets"] and target != "local":
        warnings.append(
            "Google Sheets source with remote target requires authentication"
        )

    # Check conversion complexity
    if source_info["is_google_sheets"] and target_format == "excel":
        warnings.append(
            "Converting from Google Sheets to Excel may lose some functionality (formulas, etc.)"
        )
    elif not source_info["is_google_sheets"] and target_format == "sheets":
        warnings.append(
            "Converting from Excel to Google Sheets may have compatibility flags"
        )

    return {"is_valid": len(errors) == 0, "warnings": warnings, "errors": errors}
