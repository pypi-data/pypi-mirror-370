"""
Centralized tab name sanitization utilities.

This module provides centralized functions for sanitizing tab names to be
alphanumeric with spaces only, ensuring maximum compatibility across systems.
Underscores are converted to spaces for better readability.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.utils.generic_spreadsheet import get_spreadsheet_tabs
from urarovite.core.exceptions import ValidationError


def sanitize_tab_name(tab_name: str) -> str:
    """Sanitize a tab name to be alphanumeric with spaces only.
    
    Args:
        tab_name: The original tab name
        
    Returns:
        Sanitized tab name with only alphanumeric characters and spaces
    """
    if not tab_name:
        return "Sheet1"  # Default name for empty tab names
    
    # First convert underscores to spaces (underscores are bad, spaces are good)
    sanitized = tab_name.replace("_", " ")
    
    # Keep only alphanumeric characters and spaces (omit all other chars)
    sanitized = re.sub(r"[^a-zA-Z0-9 ]", "", sanitized)
    
    # Collapse consecutive spaces to single space
    sanitized = re.sub(r" +", " ", sanitized)
    
    # Remove leading/trailing spaces
    sanitized = sanitized.strip()
    
    # Ensure the name isn't empty after sanitization
    if not sanitized:
        return "Sheet1"
    
    # Ensure it starts with a letter (not a number or space)
    if sanitized and sanitized[0].isdigit():
        sanitized = f"Sheet {sanitized}"
    
    return sanitized


def detect_non_alphanumeric_tabs(tab_names: List[str]) -> Dict[str, str]:
    """Detect tabs that need alphanumeric sanitization.
    
    Args:
        tab_names: List of tab names to check
        
    Returns:
        Dict mapping original tab names to their sanitized versions
        (only includes tabs that actually need changes)
    """
    rename_mapping = {}
    
    for tab_name in tab_names:
        sanitized_name = sanitize_tab_name(tab_name)
        
        # Only include if the name actually changes
        if tab_name != sanitized_name:
            rename_mapping[tab_name] = sanitized_name
    
    return rename_mapping


def ensure_unique_names(
    rename_mapping: Dict[str, str], all_tab_names: List[str]
) -> Dict[str, str]:
    """Ensure all sanitized names are unique by adding numeric suffixes if needed.
    
    Args:
        rename_mapping: Dict of original names to sanitized names
        all_tab_names: All existing tab names
        
    Returns:
        Updated rename mapping with unique names
    """
    # Track which names are already used (including existing tab names)
    used_names = set()
    
    # Add all existing tab names that aren't being renamed
    for tab_name in all_tab_names:
        if tab_name not in rename_mapping:
            used_names.add(tab_name.lower())
    
    # Process renames and ensure uniqueness
    final_mapping = {}
    for original_name, sanitized_name in rename_mapping.items():
        # Make sure the sanitized name is unique
        unique_name = sanitized_name
        counter = 1
        
        while unique_name.lower() in used_names:
            counter += 1
            unique_name = f"{sanitized_name} {counter}"
        
        final_mapping[original_name] = unique_name
        used_names.add(unique_name.lower())
    
    return final_mapping


def analyze_tab_names_for_sanitization(tab_names: List[str]) -> Dict[str, Any]:
    """Analyze tab names and suggest sanitization changes.
    
    Args:
        tab_names: List of tab names to analyze
        
    Returns:
        Dict with sanitization analysis and suggested rename mapping
    """
    rename_mapping = detect_non_alphanumeric_tabs(tab_names)
    
    if not rename_mapping:
        return {
            "needs_sanitization": False,
            "suggested_mapping": {},
            "tabs_affected": 0,
            "summary": "All tab names are already alphanumeric with spaces only"
        }
    
    unique_mapping = ensure_unique_names(rename_mapping, tab_names)
    
    return {
        "needs_sanitization": True,
        "suggested_mapping": unique_mapping,
        "tabs_affected": len(unique_mapping),
        "summary": f"Found {len(unique_mapping)} tabs needing sanitization",
        "preview": [
            {"original": orig, "sanitized": san} for orig, san in unique_mapping.items()
        ]
    }


def get_spreadsheet_tab_analysis(
    spreadsheet_source: Union[str, Path], 
    auth_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Get tab names from a spreadsheet and analyze them for sanitization needs.
    
    Args:
        spreadsheet_source: URL or path to spreadsheet
        auth_credentials: Authentication credentials
        
    Returns:
        Dict with tab analysis and sanitization recommendations
    """
    try:
        # Get tab names using generic utility
        tabs_result = get_spreadsheet_tabs(spreadsheet_source, auth_credentials)
        
        if not tabs_result["accessible"]:
            raise ValidationError(f"Unable to access spreadsheet: {tabs_result['error']}")
        
        tab_names = tabs_result["tabs"]
        if not tab_names:
            return {
                "success": True,
                "tabs_found": 0,
                "analysis": {
                    "needs_sanitization": False,
                    "suggested_mapping": {},
                    "tabs_affected": 0,
                    "summary": "No tabs found in spreadsheet"
                }
            }
        
        # Analyze the tab names
        analysis = analyze_tab_names_for_sanitization(tab_names)
        
        return {
            "success": True,
            "tabs_found": len(tab_names),
            "tab_names": tab_names,
            "analysis": analysis
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tabs_found": 0,
            "analysis": None
        }


def sanitize_spreadsheet_tab_names(
    spreadsheet_source: Union[str, Path],
    auth_credentials: Dict[str, Any] = None,
    dry_run: bool = True
) -> Dict[str, Any]:
    """Sanitize tab names in a spreadsheet (read-only analysis by default).
    
    Args:
        spreadsheet_source: URL or path to spreadsheet
        auth_credentials: Authentication credentials
        dry_run: If True, only analyze without making changes
        
    Returns:
        Dict with sanitization results
    """
    try:
        # Get analysis first
        analysis_result = get_spreadsheet_tab_analysis(spreadsheet_source, auth_credentials)
        
        if not analysis_result["success"]:
            return analysis_result
        
        if not analysis_result["analysis"]["needs_sanitization"]:
            return {
                "success": True,
                "changes_made": False,
                "message": "No sanitization needed - all tab names are already alphanumeric",
                "analysis": analysis_result["analysis"]
            }
        
        if dry_run:
            return {
                "success": True,
                "changes_made": False,
                "message": "Flag-only mode completed - no changes made",
                "analysis": analysis_result["analysis"],
                "preview": analysis_result["analysis"]["preview"]
            }
        
        # Implement actual tab renaming logic
        try:
            from urarovite.core.spreadsheet import SpreadsheetInterface
            from urarovite.utils.generic_spreadsheet import get_spreadsheet_tabs
            
            # Get the rename mapping
            rename_mapping = analysis_result["analysis"]["suggested_mapping"]
            
            # Create spreadsheet interface for write operations
            if isinstance(spreadsheet_source, str) and spreadsheet_source.startswith("http"):
                # Google Sheets - need to create interface with write access
                from urarovite.core.spreadsheet_google import GoogleSheetsSpreadsheet
                from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
                
                auth_secret = auth_credentials.get("auth_secret") if auth_credentials else None
                if not auth_secret:
                    return {
                        "success": False,
                        "changes_made": False,
                        "error": "Authentication required for Google Sheets tab renaming",
                        "analysis": analysis_result["analysis"]
                    }
                
                # Extract sheet ID from URL
                from urarovite.utils.sheets import extract_sheet_id
                sheet_id = extract_sheet_id(spreadsheet_source)
                
                # Create service and spreadsheet interface
                service = create_sheets_service_from_encoded_creds(auth_secret)
                spreadsheet = GoogleSheetsSpreadsheet(spreadsheet_source, {"auth_secret": auth_secret})
                
                # Apply the renames
                changes_applied = 0
                for original_name, new_name in rename_mapping.items():
                    try:
                        # Use the spreadsheet interface to rename the sheet
                        spreadsheet.update_sheet_properties(
                            sheet_name=original_name, 
                            new_name=new_name
                        )
                        changes_applied += 1
                    except Exception as e:
                        # Continue with other renames even if one fails
                        print(f"Warning: Failed to rename '{original_name}' to '{new_name}': {e}")
                
                # Save changes
                spreadsheet.save()
                
                return {
                    "success": True,
                    "changes_made": True,
                    "message": f"Successfully renamed {changes_applied} tab(s)",
                    "analysis": analysis_result["analysis"],
                    "changes_applied": changes_applied
                }
                
            else:
                # Local Excel file - not yet implemented
                return {
                    "success": False,
                    "changes_made": False,
                    "error": "Local Excel tab renaming not yet implemented",
                    "analysis": analysis_result["analysis"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "changes_made": False,
                "error": f"Failed to apply tab renames: {str(e)}",
                "analysis": analysis_result["analysis"]
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "changes_made": False
        }
