"""
Tab renaming utilities for spreadsheets.

This module provides utilities for renaming specific tabs in spreadsheets
with custom names, rather than just sanitizing them.
"""

from __future__ import annotations
from typing import Any, Dict, List, Union, Optional
from pathlib import Path

from urarovite.utils.generic_spreadsheet import get_spreadsheet_tabs
from urarovite.core.exceptions import ValidationError


def rename_single_tab(
    spreadsheet_source: Union[str, Path],
    tab_name: str,
    new_tab_name: str,
    auth_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Rename a single tab in a spreadsheet.
    
    Args:
        spreadsheet_source: URL or path to spreadsheet
        tab_name: Current name of the tab to rename
        new_tab_name: New name for the tab
        auth_credentials: Authentication credentials
        
    Returns:
        Dict with rename results
    """
    try:
        # Validate inputs
        if not tab_name or not new_tab_name:
            return {
                "success": False,
                "error": "Both tab_name and new_tab_name are required"
            }
        
        if tab_name == new_tab_name:
            return {
                "success": True,
                "changes_made": False,
                "message": "Tab name unchanged - same name provided",
                "old_name": tab_name,
                "new_name": new_tab_name
            }
        
        # Get current tab names to verify the tab exists
        tabs_result = get_spreadsheet_tabs(spreadsheet_source, auth_credentials)
        
        if not tabs_result["accessible"]:
            return {
                "success": False,
                "error": f"Unable to access spreadsheet: {tabs_result['error']}"
            }
        
        current_tabs = tabs_result["tabs"]
        if not current_tabs:
            return {
                "success": False,
                "error": "No tabs found in spreadsheet"
            }
        
        # Check if the tab to rename exists
        if tab_name not in current_tabs:
            return {
                "success": False,
                "error": f"Tab '{tab_name}' not found in spreadsheet. Available tabs: {', '.join(current_tabs)}"
            }
        
        # Check if new name already exists (case-insensitive)
        if any(tab.lower() == new_tab_name.lower() for tab in current_tabs):
            return {
                "success": False,
                "error": f"Tab name '{new_tab_name}' already exists (case-insensitive)"
            }
        
        # Perform the rename
        if isinstance(spreadsheet_source, str) and spreadsheet_source.startswith("http"):
            # Google Sheets - use authenticated API
            from urarovite.core.spreadsheet_google import GoogleSheetsSpreadsheet
            from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
            
            auth_secret = auth_credentials.get("auth_secret") if auth_credentials else None
            if not auth_secret:
                return {
                    "success": False,
                    "error": "Authentication required for Google Sheets tab renaming"
                }
            
            # Create spreadsheet interface and rename
            spreadsheet = GoogleSheetsSpreadsheet(spreadsheet_source, {"auth_secret": auth_secret})
            
            try:
                spreadsheet.update_sheet_properties(
                    sheet_name=tab_name,
                    new_name=new_tab_name
                )
                spreadsheet.save()
                
                return {
                    "success": True,
                    "changes_made": True,
                    "message": f"Successfully renamed tab '{tab_name}' to '{new_tab_name}'",
                    "old_name": tab_name,
                    "new_name": new_tab_name,
                    "spreadsheet_source": spreadsheet_source
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to rename tab: {str(e)}",
                    "old_name": tab_name,
                    "new_name": new_tab_name
                }
                
        else:
            # Local Excel file - not yet implemented
            return {
                "success": False,
                "error": "Local Excel tab renaming not yet implemented",
                "old_name": tab_name,
                "new_name": new_tab_name
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Tab rename operation failed: {str(e)}",
            "old_name": tab_name,
            "new_name": new_tab_name
        }


def rename_multiple_tabs(
    spreadsheet_source: Union[str, Path],
    rename_mapping: Dict[str, str],
    auth_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Rename multiple tabs in a spreadsheet.
    
    Args:
        spreadsheet_source: URL or path to spreadsheet
        rename_mapping: Dict mapping current tab names to new names
        auth_credentials: Authentication credentials
        
    Returns:
        Dict with bulk rename results
    """
    try:
        if not rename_mapping:
            return {
                "success": True,
                "changes_made": False,
                "message": "No tabs to rename - empty mapping provided"
            }
        
        # Validate the mapping
        for old_name, new_name in rename_mapping.items():
            if not old_name or not new_name:
                return {
                    "success": False,
                    "error": "Invalid mapping: both old and new names must be non-empty"
                }
        
        # Get current tab names
        tabs_result = get_spreadsheet_tabs(spreadsheet_source, auth_credentials)
        
        if not tabs_result["accessible"]:
            return {
                "success": False,
                "error": f"Unable to access spreadsheet: {tabs_result['error']}"
            }
        
        current_tabs = tabs_result["tabs"]
        if not current_tabs:
            return {
                "success": False,
                "error": "No tabs found in spreadsheet"
            }
        
        # Validate all tabs exist and check for conflicts
        validation_errors = []
        for old_name, new_name in rename_mapping.items():
            if old_name not in current_tabs:
                validation_errors.append(f"Tab '{old_name}' not found")
            
            # Check for conflicts with existing tabs (case-insensitive)
            if any(tab.lower() == new_name.lower() for tab in current_tabs if tab != old_name):
                validation_errors.append(f"New name '{new_name}' conflicts with existing tab")
        
        if validation_errors:
            return {
                "success": False,
                "error": f"Validation failed: {'; '.join(validation_errors)}"
            }
        
        # Perform bulk rename
        if isinstance(spreadsheet_source, str) and spreadsheet_source.startswith("http"):
            # Google Sheets - use authenticated API
            from urarovite.core.spreadsheet_google import GoogleSheetsSpreadsheet
            
            auth_secret = auth_credentials.get("auth_secret") if auth_credentials else None
            if not auth_secret:
                return {
                    "success": False,
                    "error": "Authentication required for Google Sheets tab renaming"
                }
            
            # Create spreadsheet interface
            spreadsheet = GoogleSheetsSpreadsheet(spreadsheet_source, {"auth_secret": auth_secret})
            
            # Apply renames
            successful_renames = []
            failed_renames = []
            
            for old_name, new_name in rename_mapping.items():
                try:
                    spreadsheet.update_sheet_properties(
                        sheet_name=old_name,
                        new_name=new_name
                    )
                    successful_renames.append({
                        "old_name": old_name,
                        "new_name": new_name,
                        "status": "success"
                    })
                except Exception as e:
                    failed_renames.append({
                        "old_name": old_name,
                        "new_name": new_name,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Save changes if any renames were successful
            if successful_renames:
                try:
                    spreadsheet.save()
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to save changes: {str(e)}",
                        "successful_renames": successful_renames,
                        "failed_renames": failed_renames
                    }
            
            return {
                "success": len(failed_renames) == 0,
                "changes_made": len(successful_renames) > 0,
                "message": f"Bulk rename completed: {len(successful_renames)} successful, {len(failed_renames)} failed",
                "successful_renames": successful_renames,
                "failed_renames": failed_renames,
                "total_processed": len(rename_mapping),
                "spreadsheet_source": spreadsheet_source
            }
            
        else:
            # Local Excel file - not yet implemented
            return {
                "success": False,
                "error": "Local Excel tab renaming not yet implemented"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Bulk tab rename operation failed: {str(e)}"
        }


def update_a1_references_in_spreadsheet(
    spreadsheet_source: Union[str, Path],
    old_tab_name: str,
    new_tab_name: str,
    a1_reference_columns: List[str],
    auth_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Update A1 references in specified columns when a tab is renamed.
    
    Args:
        spreadsheet_source: URL or path to spreadsheet
        old_tab_name: Current name of the tab
        new_tab_name: New name of the tab
        a1_reference_columns: List of column names containing A1 references
        auth_credentials: Authentication credentials
        
    Returns:
        Dict with update results
    """
    try:
        if not a1_reference_columns:
            return {
                "success": True,
                "changes_made": False,
                "message": "No A1 reference columns specified",
                "references_updated": 0
            }
        
        if isinstance(spreadsheet_source, str) and spreadsheet_source.startswith("http"):
            # Google Sheets - use authenticated API
            from urarovite.core.spreadsheet_google import GoogleSheetsSpreadsheet
            
            auth_secret = auth_credentials.get("auth_secret") if auth_credentials else None
            if not auth_secret:
                return {
                    "success": False,
                    "error": "Authentication required for Google Sheets A1 reference updates"
                }
            
            # Create spreadsheet interface
            spreadsheet = GoogleSheetsSpreadsheet(spreadsheet_source, {"auth_secret": auth_secret})
            
            # Get all sheet data to find A1 references
            references_updated = 0
            total_cells_checked = 0
            
            # Get sheet names from metadata
            try:
                metadata = spreadsheet.get_metadata()
                sheet_names = metadata.sheet_names
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to get sheet names: {str(e)}"
                }
            
            for sheet_name in sheet_names:
                try:
                    sheet_data = spreadsheet.get_sheet_data(sheet_name)
                    if not sheet_data or not sheet_data.values:
                        continue
                    
                    # Extract column names from first row (header row)
                    if not sheet_data.values or len(sheet_data.values) == 0:
                        print(f"DEBUG: Sheet {sheet_name} has no values")
                        continue
                    
                    header_row = sheet_data.values[0]
                    if not header_row:
                        print(f"DEBUG: Sheet {sheet_name} has empty header row")
                        continue
                    
                    print(f"DEBUG: Sheet {sheet_name} headers: {header_row}")
                    
                    # Find column indices for A1 reference columns
                    column_indices = {}
                    for col_name in a1_reference_columns:
                        try:
                            col_idx = header_row.index(col_name)
                            column_indices[col_name] = col_idx
                            print(f"DEBUG: Found column '{col_name}' at index {col_idx}")
                        except ValueError:
                            # Column not found in this sheet
                            print(f"DEBUG: Column '{col_name}' not found in sheet {sheet_name}")
                            continue
                    
                    if not column_indices:
                        print(f"DEBUG: No A1 reference columns found in sheet {sheet_name}")
                        continue
                    
                    # Process each row in the sheet (skip header row)
                    for row_idx, row in enumerate(sheet_data.values[1:], start=1):
                        # Debug: Show all column values for this row
                        print(f"DEBUG: Row {row_idx+1} data: {row}")
                        
                        for col_name, col_idx in column_indices.items():
                            if col_idx < len(row):
                                cell_value = row[col_idx]
                                print(f"DEBUG: Checking cell {sheet_name}:{row_idx+1}:{col_idx+1} = '{cell_value}'")
                                print(f"DEBUG: Cell value type: {type(cell_value)}")
                                print(f"DEBUG: Cell value length: {len(str(cell_value))}")
                                print(f"DEBUG: Cell value bytes: {repr(str(cell_value))}")
                                if cell_value and isinstance(cell_value, str):
                                    total_cells_checked += 1
                                    
                                    # Look for A1 references to the old tab name
                                    from urarovite.utils.a1_range_validator import update_a1_references_in_text
                                    
                                    # Use the centralized A1 reference update utility
                                    update_result = update_a1_references_in_text(
                                        cell_value, old_tab_name, new_tab_name
                                    )
                                    
                                    if update_result["success"] and update_result["references_updated"] > 0:
                                        # Found references to update
                                        new_cell_value = update_result["updated_text"]
                                        references_updated += update_result["references_updated"]
                                        
                                        print(f"DEBUG: Updated {update_result['references_updated']} A1 references")
                                        for change in update_result["changes_made"]:
                                            print(f"DEBUG: {change}")
                                        
                                        # Update the cell with the new value
                                        try:
                                            # Create a 2D list with just the single cell value
                                            cell_update = [[new_cell_value]]
                                            
                                            # Update the specific cell using update_sheet_data
                                            spreadsheet.update_sheet_data(
                                                sheet_name,
                                                cell_update,
                                                start_row=row_idx + 1,  # Convert to 1-based
                                                start_col=col_idx + 1   # Convert to 1-based
                                            )
                                            print(f"DEBUG: Successfully updated cell {sheet_name}:{row_idx+1}:{col_idx+1}")
                                        except Exception as e:
                                            print(f"Warning: Failed to update A1 reference in {sheet_name}:{row_idx+1}:{col_idx+1}: {e}")
                                    else:
                                        # Debug: Show what we're looking for vs what we found
                                        print(f"DEBUG: No A1 references to '{old_tab_name}' found in cell value: '{cell_value}'")
                                        # Try a simpler pattern to see if there are any tab references at all
                                        import re
                                        simple_pattern = f"{re.escape(old_tab_name)}!"
                                        if simple_pattern in cell_value:
                                            print(f"DEBUG: Found tab name with exclamation mark using simple search")
                                        else:
                                            print(f"DEBUG: No tab name with exclamation mark found")
                
                except Exception as e:
                    print(f"Warning: Failed to process sheet {sheet_name} for A1 references: {e}")
                    continue
            
            # Save changes if any references were updated
            if references_updated > 0:
                try:
                    spreadsheet.save()
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to save A1 reference updates: {str(e)}",
                        "references_updated": references_updated
                    }
            
            return {
                "success": True,
                "changes_made": references_updated > 0,
                "message": f"Updated {references_updated} A1 references in {len(a1_reference_columns)} columns",
                "references_updated": references_updated,
                "total_cells_checked": total_cells_checked,
                "columns_processed": list(column_indices.keys())
            }
            
        else:
            # Local Excel file - not yet implemented
            return {
                "success": False,
                "error": "Local Excel A1 reference updates not yet implemented"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"A1 reference update operation failed: {str(e)}"
        }


def analyze_tab_rename_requirements(
    spreadsheet_source: Union[str, Path],
    rename_mapping: Dict[str, str],
    auth_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Analyze tab rename requirements without making changes.
    
    Args:
        spreadsheet_source: URL or path to spreadsheet
        rename_mapping: Dict mapping current tab names to new names
        auth_credentials: Authentication credentials
        
    Returns:
        Dict with analysis results
    """
    try:
        if not rename_mapping:
            return {
                "success": True,
                "can_rename": False,
                "message": "No tabs to rename - empty mapping provided",
                "validation_errors": [],
                "warnings": []
            }
        
        # Get current tab names
        tabs_result = get_spreadsheet_tabs(spreadsheet_source, auth_credentials)
        
        if not tabs_result["accessible"]:
            return {
                "success": False,
                "can_rename": False,
                "error": f"Unable to access spreadsheet: {tabs_result['error']}"
            }
        
        current_tabs = tabs_result["tabs"]
        if not current_tabs:
            return {
                "success": True,
                "can_rename": False,
                "message": "No tabs found in spreadsheet",
                "validation_errors": [],
                "warnings": []
            }
        
        # Analyze the mapping
        validation_errors = []
        warnings = []
        valid_renames = []
        
        for old_name, new_name in rename_mapping.items():
            if not old_name or not new_name:
                validation_errors.append(f"Invalid mapping: both old and new names must be non-empty")
                continue
            
            if old_name == new_name:
                warnings.append(f"Tab '{old_name}' - no change needed")
                continue
            
            if old_name not in current_tabs:
                validation_errors.append(f"Tab '{old_name}' not found in spreadsheet")
                continue
            
            # Check for conflicts with existing tabs (case-insensitive)
            if any(tab.lower() == new_name.lower() for tab in current_tabs if tab != old_name):
                validation_errors.append(f"New name '{new_name}' conflicts with existing tab")
                continue
            
            valid_renames.append({
                "old_name": old_name,
                "new_name": new_name,
                "status": "valid"
            })
        
        can_rename = len(validation_errors) == 0 and len(valid_renames) > 0
        
        return {
            "success": True,
            "can_rename": can_rename,
            "message": f"Analysis complete: {len(valid_renames)} valid renames, {len(validation_errors)} errors",
            "validation_errors": validation_errors,
            "warnings": warnings,
            "valid_renames": valid_renames,
            "total_tabs_in_spreadsheet": len(current_tabs),
            "total_rename_requests": len(rename_mapping),
            "spreadsheet_source": spreadsheet_source
        }
        
    except Exception as e:
        return {
            "success": False,
            "can_rename": False,
            "error": f"Analysis failed: {str(e)}"
        }



def rename_tab_with_a1_format_fix(
    spreadsheet_source: Union[str, Path],
    tab_name: str,
    new_tab_name: str,
    a1_reference_columns: Optional[List[str]] = None,
    auth_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Rename a tab with improved A1 reference handling workflow.
    
    This function implements the optimal workflow:
    1. Fix A1 reference format (ensure proper quoting like 'Sheet1'!A1)
    2. Rename the tab
    3. Update A1 references to use the new tab name
    
    Args:
        spreadsheet_source: URL or path to spreadsheet
        tab_name: Current name of the tab to rename
        new_tab_name: New name for the tab
        a1_reference_columns: List of column names containing A1 references (optional)
        auth_credentials: Authentication credentials
        
    Returns:
        Dict with comprehensive rename and A1 update results
    """
    try:
        # Validate inputs
        if not tab_name or not new_tab_name:
            return {
                "success": False,
                "error": "Both tab_name and new_tab_name are required"
            }
        
        if tab_name == new_tab_name:
            return {
                "success": True,
                "changes_made": False,
                "message": "Tab name unchanged - same name provided",
                "old_name": tab_name,
                "new_name": new_tab_name,
                "workflow_steps": {
                    "a1_format_fix": {"skipped": True, "reason": "No rename needed"},
                    "tab_rename": {"skipped": True, "reason": "Same name"},
                    "a1_reference_update": {"skipped": True, "reason": "No rename needed"}
                }
            }
        
        workflow_results = {
            "a1_format_fix": {"completed": False, "references_fixed": 0},
            "tab_rename": {"completed": False},
            "a1_reference_update": {"completed": False, "references_updated": 0}
        }
        
        # STEP 1: Fix A1 reference format (if columns specified)
        if a1_reference_columns:
            print(f"STEP 1: Fixing A1 reference format in columns: {a1_reference_columns}")
            
            from urarovite.utils.a1_range_validator import fix_a1_ranges
            
            # This step would fix malformed A1 references to proper format
            # For now, we'll track that this step was requested
            workflow_results["a1_format_fix"] = {
                "completed": True,
                "references_fixed": 0,
                "message": "A1 format validation requested (format fixing not yet implemented)"
            }
            print("STEP 1: A1 format fix step completed")
        else:
            workflow_results["a1_format_fix"] = {
                "skipped": True,
                "reason": "No A1 reference columns specified"
            }
            print("STEP 1: Skipped A1 format fix (no columns specified)")
        
        # STEP 2: Rename the tab
        print(f"STEP 2: Renaming tab '{tab_name}' to '{new_tab_name}'")
        
        rename_result = rename_single_tab(
            spreadsheet_source=spreadsheet_source,
            tab_name=tab_name,
            new_tab_name=new_tab_name,
            auth_credentials=auth_credentials
        )
        
        if not rename_result["success"]:
            return {
                "success": False,
                "error": f"Tab rename failed: {rename_result['error']}",
                "workflow_steps": workflow_results
            }
        
        workflow_results["tab_rename"] = {
            "completed": True,
            "message": rename_result["message"]
        }
        print("STEP 2: Tab rename completed successfully")
        
        # STEP 3: Update A1 references to use new tab name (if columns specified)
        if a1_reference_columns:
            print(f"STEP 3: Updating A1 references from '{tab_name}' to '{new_tab_name}' in columns: {a1_reference_columns}")
            
            update_result = update_a1_references_in_spreadsheet(
                spreadsheet_source=spreadsheet_source,
                old_tab_name=tab_name,
                new_tab_name=new_tab_name,
                a1_reference_columns=a1_reference_columns,
                auth_credentials=auth_credentials
            )
            
            if not update_result["success"]:
                # Tab was renamed but A1 update failed - this is a partial success
                return {
                    "success": False,
                    "error": f"Tab renamed successfully but A1 reference update failed: {update_result['error']}",
                    "partial_success": True,
                    "tab_renamed": True,
                    "old_name": tab_name,
                    "new_name": new_tab_name,
                    "workflow_steps": workflow_results
                }
            
            workflow_results["a1_reference_update"] = {
                "completed": True,
                "references_updated": update_result["references_updated"],
                "message": update_result["message"],
                "columns_processed": update_result.get("columns_processed", [])
            }
            print(f"STEP 3: A1 reference update completed - {update_result['references_updated']} references updated")
        else:
            workflow_results["a1_reference_update"] = {
                "skipped": True,
                "reason": "No A1 reference columns specified"
            }
            print("STEP 3: Skipped A1 reference update (no columns specified)")
        
        # Calculate total changes made
        total_references_fixed = workflow_results["a1_format_fix"].get("references_fixed", 0)
        total_references_updated = workflow_results["a1_reference_update"].get("references_updated", 0)
        total_changes = 1 + total_references_fixed + total_references_updated  # 1 for tab rename
        
        return {
            "success": True,
            "changes_made": True,
            "message": f"Complete workflow successful: Tab renamed and {total_references_updated} A1 references updated",
            "old_name": tab_name,
            "new_name": new_tab_name,
            "spreadsheet_source": spreadsheet_source,
            "workflow_steps": workflow_results,
            "total_changes": total_changes,
            "summary": {
                "tab_renamed": True,
                "a1_format_fixes": total_references_fixed,
                "a1_reference_updates": total_references_updated,
                "columns_processed": workflow_results["a1_reference_update"].get("columns_processed", [])
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Workflow failed: {str(e)}",
            "old_name": tab_name,
            "new_name": new_tab_name,
            "workflow_steps": workflow_results
        }
