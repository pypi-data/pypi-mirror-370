#!/usr/bin/env python3
"""Utilities for validating A1 notation ranges with proper tab name formatting."""

import re
from typing import List, Dict, Any, Tuple, Union
from urarovite.utils.drive import _create_response


def validate_a1_ranges(
    range_text: str,
    strict_mode: bool = True
) -> Dict[str, Any]:
    """Validate A1 notation ranges for proper tab name formatting.
    
    Args:
        range_text: The range text to validate (e.g., "'FY2015_Present'!H2:H201")
        strict_mode: If True, requires all ranges to have proper tab names. If False, allows some flexibility.
        
    Returns:
        Dict with validation results including:
        - success: bool
        - is_valid: bool
        - errors: List of validation errors
        - warnings: List of warnings
        - parsed_ranges: List of parsed range objects
        - suggestions: List of suggested fixes
    """
    try:
        if not range_text or not isinstance(range_text, str):
            return _create_response(False, error="invalid_input", error_msg="Range text must be a non-empty string")
        
        # Split by commas to handle multiple ranges
        range_parts = [part.strip() for part in range_text.split(',') if part.strip()]
        
        if not range_parts:
            return _create_response(False, error="no_ranges", error_msg="No ranges found in input text")
        
        errors = []
        warnings = []
        parsed_ranges = []
        suggestions = []
        
        for i, range_part in enumerate(range_parts):
            range_result = _validate_single_range(range_part, i + 1, strict_mode)
            
            if range_result["errors"]:
                errors.extend(range_result["errors"])
            
            if range_result["warnings"]:
                warnings.extend(range_result["warnings"])
            
            if range_result["suggestions"]:
                suggestions.extend(range_result["suggestions"])
            
            parsed_ranges.append(range_result["parsed_range"])
        
        # Determine overall validity
        is_valid = len(errors) == 0
        
        # Create response
        result = {
            "success": True,
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "parsed_ranges": parsed_ranges,
            "suggestions": suggestions,
            "total_ranges": len(range_parts),
            "valid_ranges": len([r for r in parsed_ranges if r["is_valid"]]),
            "invalid_ranges": len([r for r in parsed_ranges if not r["is_valid"]])
        }
        
        return result
        
    except Exception as e:
        return _create_response(False, error="validation_error", error_msg=f"Validation failed: {str(e)}")


def _validate_single_range(
    range_text: str,
    range_index: int,
    strict_mode: bool
) -> Dict[str, Any]:
    """Validate a single range entry.
    
    Args:
        range_text: Single range text to validate
        range_index: Index of this range in the sequence
        strict_mode: Whether to use strict validation
        
    Returns:
        Dict with validation results for this single range
    """
    errors = []
    warnings = []
    suggestions = []
    
    # Pattern to match proper A1 notation with tab names
    # Matches: 'TabName'!A1, 'TabName'!A1:B10, 'TabName'!A1:B10:D20
    proper_pattern = r"^'([^']+)'!([A-Z]+\d+(?::[A-Z]+\d+)*)$"
    
    # Pattern to match A1 notation without tab names
    no_tab_pattern = r"^([A-Z]+\d+(?::[A-Z]+\d+)*)$"
    
    # Pattern to match malformed tab names (missing quotes, etc.)
    malformed_pattern = r"^([^']*[^']*'[^']*|[^']*'[^']*[^']*)!([A-Z]+\d+(?::[A-Z]+\d+)*)$"
    
    # Pattern to match unquoted tab names (e.g., "Final Data!A1", "Transactions!A1")
    # Must NOT start with a quote to avoid matching already-quoted ranges
    unquoted_tab_pattern = r"^([^']+?)!([A-Z]+\d+(?::[A-Z]+\d+)*)$"
    
    # Pattern to match just cell references without tab or range
    cell_only_pattern = r"^'([^']+)'$"
    
    parsed_range = {
        "original_text": range_text,
        "range_index": range_index,
        "is_valid": False,
        "tab_name": None,
        "cell_reference": None,
        "range_type": None,
        "issues": []
    }
    
    # Check for proper format first
    proper_match = re.match(proper_pattern, range_text)
    if proper_match:
        parsed_range.update({
            "is_valid": True,
            "tab_name": proper_match.group(1),
            "cell_reference": proper_match.group(2),
            "range_type": "proper_tab_with_range"
        })
        return {
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "parsed_range": parsed_range
        }
    
    # Check for no tab name - mark as invalid but don't fix
    no_tab_match = re.match(no_tab_pattern, range_text)
    if no_tab_match:
        cell_ref = no_tab_match.group(1)
        
        # Mark as invalid but we're not fixing ranges without tab names
        errors.append(f"Range {range_index}: '{range_text}' - Missing tab name (cannot fix) - Rule: A1 ranges must include tab name")
        suggestions.append(f"Range {range_index}: Use format 'TabName'!{cell_ref}")
        parsed_range.update({
            "is_valid": False,
            "tab_name": None,
            "cell_reference": cell_ref,
            "range_type": "no_tab_name",
            "issues": ["no_tab_name"]
        })
        
        return {
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "parsed_range": parsed_range
        }
    
    # Check for unquoted tab names - mark as invalid but can be fixed
    unquoted_tab_match = re.match(unquoted_tab_pattern, range_text)
    if unquoted_tab_match:
        tab_name = unquoted_tab_match.group(1).strip()
        cell_ref = unquoted_tab_match.group(2)
        
        # Mark as invalid but this can be fixed by adding quotes
        errors.append(f"Range {range_index}: '{range_text}' - Unquoted tab name '{tab_name}' (can fix) - Rule: Tab names must be quoted")
        suggestions.append(f"Range {range_index}: Use format '{tab_name}'!{cell_ref}")
        parsed_range.update({
            "is_valid": False,
            "tab_name": tab_name,
            "cell_reference": cell_ref,
            "range_type": "unquoted_tab_name",
            "issues": ["unquoted_tab_name"]
        })
        return {
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "parsed_range": parsed_range
        }
    
    # Check for malformed tab names
    malformed_match = re.match(malformed_pattern, range_text)
    if malformed_match:
        cell_ref = malformed_match.group(2)
        malformed_tab = malformed_match.group(1)
        
        errors.append(f"Range {range_index}: '{range_text}' - Malformed tab name '{malformed_tab}' - Rule: Tab names must be properly quoted")
        suggestions.append(f"Range {range_index}: Use format 'TabName'!{cell_ref}")
        parsed_range.update({
            "is_valid": False,
            "tab_name": None,
            "cell_reference": cell_ref,
            "range_type": "malformed_tab_name",
            "issues": ["malformed_tab_name"]
        })
        return {
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "parsed_range": parsed_range
        }
    
    # Check for just tab names
    cell_only_match = re.match(cell_only_pattern, range_text)
    if cell_only_match:
        tab_name = cell_only_match.group(1)
        
        if strict_mode:
            errors.append(f"Range {range_index}: '{range_text}' - Missing cell reference - Rule: A1 ranges must include cell reference")
            suggestions.append(f"Range {range_index}: Use format '{tab_name}'!A1")
            parsed_range.update({
                "is_valid": False,
                "tab_name": tab_name,
                "cell_reference": None,
                "range_type": "no_cell_reference",
                "issues": ["no_cell_reference"]
            })
        else:
            warnings.append(f"Range {range_index}: No cell reference specified")
            parsed_range.update({
                "is_valid": True,
                "tab_name": tab_name,
                "cell_reference": None,
                "range_type": "no_cell_reference",
                "issues": ["no_cell_reference"]
            })
        
        return {
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "parsed_range": parsed_range
        }
    
    # Unknown format
    errors.append(f"Range {range_index}: Unrecognized format '{range_text}'")
    suggestions.append(f"Range {range_index}: Use format 'TabName'!A1 or 'TabName'!A1:B10")
    parsed_range.update({
        "is_valid": False,
        "tab_name": None,
        "cell_reference": None,
        "range_type": "unrecognized_format",
        "issues": ["unrecognized_format"]
    })
    
    return {
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "parsed_range": parsed_range
    }


def fix_a1_ranges(
    range_text: str,
    default_tab_name: str = None
) -> Dict[str, Any]:
    """Attempt to fix common issues in A1 notation ranges.
    
    Args:
        range_text: The range text to fix
        default_tab_name: Default tab name to use when missing
        
    Returns:
        Dict with fix results including:
        - success: bool
        - original_text: str
        - fixed_text: str
        - changes_made: List of changes made
        - warnings: List of warnings about fixes
    """
    try:
        if not range_text or not isinstance(range_text, str):
            return _create_response(False, error="invalid_input", error_msg="Range text must be a non-empty string")
        
        # Split by commas to handle multiple ranges
        range_parts = [part.strip() for part in range_text.split(',') if part.strip()]
        
        if not range_parts:
            return _create_response(False, error="no_ranges", error_msg="No ranges found in input text")
        
        fixed_parts = []
        changes_made = []
        warnings = []
        
        for i, range_part in enumerate(range_parts):
            fixed_part, part_changes, part_warnings = _fix_single_range(
                range_part, i + 1, default_tab_name
            )
            
            fixed_parts.append(fixed_part)
            changes_made.extend(part_changes)
            warnings.extend(part_warnings)
        
        fixed_text = ", ".join(fixed_parts)
        
        return {
            "success": True,
            "original_text": range_text,
            "fixed_text": fixed_text,
            "changes_made": changes_made,
            "warnings": warnings,
            "total_ranges": len(range_parts),
            "ranges_fixed": len([c for c in changes_made if "fixed" in c.lower()])
        }
        
    except Exception as e:
        return _create_response(False, error="fix_error", error_msg=f"Fix operation failed: {str(e)}")


def _fix_single_range(
    range_text: str,
    range_index: int,
    default_tab_name: str = None
) -> Tuple[str, List[str], List[str]]:
    """Fix a single range entry using case-by-case approach.
    
    Args:
        range_text: Single range text to fix
        range_index: Index of this range in the sequence
        default_tab_name: Default tab name to use when missing
        
    Returns:
        Tuple of (fixed_text, changes_made, warnings)
    """
    changes = []
    warnings = []
    
    # Case 1: Already properly formatted - no change needed
    if re.match(r"^'[^']+'![A-Z]+\d+(?::[A-Z]+\d+)*$", range_text):
        return range_text, [], []
    
    # Case 2: No tab name at all (e.g., "A1:K387") - leave as-is
    if re.match(r"^[A-Z]+\d+(?::[A-Z]+\d+)*$", range_text):
        return range_text, [], []  # No change needed
    
    # Case 3: Unquoted tab name (e.g., "Transactions!D2:D71") - add quotes
    if re.match(r"^[^']+![A-Z]+\d+(?::[A-Z]+\d+)*$", range_text):
        parts = range_text.split("!", 1)
        tab_name = parts[0].strip()
        cell_ref = parts[1]
        fixed_text = f"'{tab_name}'!{cell_ref}"
        changes.append(f"Range {range_index}: Added quotes around tab name '{tab_name}'")
        return fixed_text, changes, warnings
    
    # Case 4: Missing opening quote (e.g., "Transactions'!D2:D71")
    if re.match(r"^[^']+'![A-Z]+\d+(?::[A-Z]+\d+)*$", range_text):
        parts = range_text.split("!", 1)
        tab_name = parts[0].rstrip("'").strip()
        cell_ref = parts[1]
        fixed_text = f"'{tab_name}'!{cell_ref}"
        changes.append(f"Range {range_index}: Fixed missing opening quote for tab name '{tab_name}'")
        return fixed_text, changes, warnings
    
    # Case 5: Missing closing quote (e.g., "'Grants!O3:O143")
    if re.match(r"^'[^']+![A-Z]+\d+(?::[A-Z]+\d+)*$", range_text):
        parts = range_text.split("!", 1)
        tab_name = parts[0].lstrip("'").strip()
        cell_ref = parts[1]
        fixed_text = f"'{tab_name}'!{cell_ref}"
        changes.append(f"Range {range_index}: Fixed missing closing quote for tab name '{tab_name}'")
        return fixed_text, changes, warnings
    
    # Case 6: Just tab names (e.g., "'F61', 'B35', 'B36', 'I53'") - leave as-is
    if re.match(r"^'[^']+'(?:, '[^']+')*$", range_text):
        return range_text, [], []  # No change needed
    
    # If no patterns match, return as-is
    return range_text, [], []


def get_a1_validation_examples() -> Dict[str, Any]:
    """Get examples of correct and incorrect A1 notation ranges.
    
    Returns:
        Dict with validation examples
    """
    return {
        "correct_examples": [
            "'FY2015_Present'!H2:H201",
            "'Grants'!A3:A143, 'Grants'!O3:O143",
            "'Sale Price Import'!A3:I594, 'Shipments'!A1:J62",
            "'Data'!A1",
            "'Summary'!B5:D10"
        ],
        "incorrect_examples": [
            "Transactions!D2:D71",  # Missing quotes around tab name
            "Transactions'!D2:D71",  # Missing opening quote
            "A1:K387",  # Missing tab name entirely
            "'Grants'!A3:A143, 'Grants!O3:O143",  # Missing closing quote in second range
            "'F61', 'B35', 'B36', 'I53'"  # Just tab names, no cell references
        ],
        "common_fixes": [
            "Transactions!D2:D71 → 'Transactions'!D2:D71",
            "A1:K387 → 'Sheet1'!A1:K387 (with default tab name)",
            "'Grants!O3:O143 → 'Grants'!O3:O143 (fixed missing quote)"
        ]
    }


def update_a1_references_in_text(
    text: str,
    old_tab_name: str,
    new_tab_name: str
) -> Dict[str, Any]:
    """Update A1 references in text when a tab name changes.
    
    This function finds all A1 references to a specific tab name and updates them
    to use the new tab name, preserving the original quoting style.
    
    Args:
        text: Text containing A1 references (e.g., cell values, formulas)
        old_tab_name: Current name of the tab
        new_tab_name: New name for the tab
        
    Returns:
        Dict with update results including:
        - success: bool
        - original_text: str
        - updated_text: str
        - references_updated: int
        - changes_made: List of specific changes
        - warnings: List of warnings
    """
    try:
        if not text or not isinstance(text, str):
            return _create_response(False, error="invalid_input", error_msg="Text must be a non-empty string")
        
        if not old_tab_name or not new_tab_name:
            return _create_response(False, error="invalid_names", error_msg="Both old and new tab names must be provided")
        
        if old_tab_name == new_tab_name:
            return {
                "success": True,
                "original_text": text,
                "updated_text": text,
                "references_updated": 0,
                "changes_made": [],
                "warnings": ["No changes needed - tab names are identical"]
            }
        
        # More flexible A1 reference pattern
        a1_ref_pattern = r'[A-Z]+\d+(?::[A-Z]+\d+)*'
        
        # Pattern 1: Quoted tab names like 'Sheet1'!A1 or "Sheet1"!A1
        # Also handles edge case: 'Sheet1!A1 (leading quote, no closing quote)
        quoted_pattern = f'(["\'])({re.escape(old_tab_name)})\\1!({a1_ref_pattern})'
        
        # Pattern 2: Unquoted tab names like Sheet1!A1
        unquoted_pattern = f'({re.escape(old_tab_name)})!({a1_ref_pattern})'
        
        all_matches = []
        changes_made = []
        
        # Find quoted matches first
        quoted_matches = list(re.finditer(quoted_pattern, text))
        for match in quoted_matches:
            quote_char = match.group(1)  # The quote character used
            old_tab_ref = match.group(2)  # The old tab name
            cell_ref = match.group(3)    # The A1 reference part
            
            all_matches.append({
                'match': match,
                'type': 'quoted',
                'quote_char': quote_char,
                'old_tab_ref': old_tab_ref,
                'cell_ref': cell_ref,
                'full_match': match.group(0)
            })
        
        # Find unquoted matches
        unquoted_matches = list(re.finditer(unquoted_pattern, text))
        for match in unquoted_matches:
            old_tab_ref = match.group(1)  # The old tab name
            cell_ref = match.group(2)    # The A1 reference part
            
            all_matches.append({
                'match': match,
                'type': 'unquoted',
                'quote_char': '',  # No quotes
                'old_tab_ref': old_tab_ref,
                'cell_ref': cell_ref,
                'full_match': match.group(0)
            })
        
        if not all_matches:
            return {
                "success": True,
                "original_text": text,
                "updated_text": text,
                "references_updated": 0,
                "changes_made": [],
                "warnings": [f"No A1 references to tab '{old_tab_name}' found in text"]
            }
        
        # Update the text
        updated_text = text
        for match_info in all_matches:
            quote_char = match_info['quote_char']
            old_tab_ref = match_info['old_tab_ref']
            cell_ref = match_info['cell_ref']
            full_match = match_info['full_match']
            
            # Build new reference with same quoting style
            if quote_char == "'":
                new_ref = f"'{new_tab_name}'!{cell_ref}"
            elif quote_char == '"':
                new_ref = f'"{new_tab_name}"!{cell_ref}'
            else:
                new_ref = f"{new_tab_name}!{cell_ref}"
            
            # Replace the old reference with the new one
            old_ref = full_match
            updated_text = updated_text.replace(old_ref, new_ref)
            
            changes_made.append(f"Updated '{old_ref}' → '{new_ref}'")
        
        return {
            "success": True,
            "original_text": text,
            "updated_text": updated_text,
            "references_updated": len(all_matches),
            "changes_made": changes_made,
            "warnings": [],
            "patterns_used": {
                "quoted_pattern": quoted_pattern,
                "unquoted_pattern": unquoted_pattern
            }
        }
        
    except Exception as e:
        return _create_response(False, error="update_error", error_msg=f"Update operation failed: {str(e)}")


def update_a1_references_in_spreadsheet_cells(
    spreadsheet,
    sheet_name: str | None,
    column_name: str,
    old_tab_name: str,
    new_tab_name: str
) -> Dict[str, Any]:
    """Update A1 references in a specific column when a tab name changes.
    
    This is a shared utility that both the A1 range fixer and tab renamer can use.
    It uses the correct spreadsheet.update_sheet_data method for cell updates.
    
    Args:
        spreadsheet: SpreadsheetInterface instance
        sheet_name: Name of the sheet to process. If None, processes all sheets.
        column_name: Name of the column containing A1 references
        old_tab_name: Current name of the tab
        new_tab_name: New name for the tab
        
    Returns:
        Dict with update results including:
        - success: bool
        - references_updated: int
        - changes_made: List of specific changes
        - errors: List of errors encountered
    """
    try:
        if not old_tab_name or not new_tab_name:
            return _create_response(False, error="invalid_names", error_msg="Both old and new tab names must be provided")
        
        if old_tab_name == new_tab_name:
            return {
                "success": True,
                "references_updated": 0,
                "changes_made": [],
                "errors": [],
                "message": "No changes needed - tab names are identical"
            }
        
        references_updated = 0
        changes_made = []
        errors = []
        
        if sheet_name is None:
            # Process all sheets
            try:
                metadata = spreadsheet.get_metadata()
                sheet_names = metadata.sheet_names
            except Exception as e:
                return _create_response(False, error="metadata_error", error_msg=f"Failed to get sheet names: {str(e)}")
            
            for current_sheet_name in sheet_names:
                try:
                    # Process single sheet directly
                    sheet_data = spreadsheet.get_sheet_data(current_sheet_name)
                    if not sheet_data or not sheet_data.values:
                        continue
                    
                    # Find the column index
                    headers = sheet_data.values[0] if sheet_data.values else []
                    try:
                        col_idx = headers.index(column_name)
                    except ValueError:
                        continue  # Column not found in this sheet
                    
                    # Process each row (skip header)
                    for row_idx, row in enumerate(sheet_data.values[1:], start=2):  # 1-based row indexing
                        if col_idx < len(row):
                            cell_value = row[col_idx]
                            
                            if cell_value and isinstance(cell_value, str):
                                # Use the existing A1 reference update logic
                                update_result = update_a1_references_in_text(cell_value, old_tab_name, new_tab_name)
                                
                                if update_result["success"] and update_result["references_updated"] > 0:
                                    # Found references to update
                                    new_cell_value = update_result["updated_text"]
                                    references_updated += update_result["references_updated"]
                                    
                                    # Update the cell using the correct method
                                    try:
                                        # Create a 2D list with just the single cell value
                                        cell_update = [[new_cell_value]]
                                        
                                        # Update the specific cell using update_sheet_data
                                        spreadsheet.update_sheet_data(
                                            current_sheet_name,
                                            cell_update,
                                            start_row=row_idx,
                                            start_col=col_idx + 1  # Convert to 1-based column indexing
                                        )
                                        
                                        # Record the change
                                        changes_made.append(f"Sheet '{current_sheet_name}' Row {row_idx}: '{cell_value}' → '{new_cell_value}'")
                                        
                                    except Exception as e:
                                        error_msg = f"Failed to update cell {current_sheet_name}:{row_idx}:{col_idx+1}: {e}"
                                        errors.append(error_msg)
                                        print(f"Warning: {error_msg}")
                except Exception as e:
                    errors.append(f"Sheet '{current_sheet_name}': {str(e)}")
            
            # Save changes if any references were updated
            if references_updated > 0 and not errors:
                try:
                    spreadsheet.save()
                except Exception as e:
                    errors.append(f"Failed to save changes: {e}")
                    return _create_response(False, error="save_failed", error_msg=f"Failed to save: {str(e)}")
            
            return {
                "success": True,
                "references_updated": references_updated,
                "changes_made": changes_made,
                "errors": errors,
                "message": f"Updated {references_updated} A1 references in column '{column_name}' across all sheets"
            }
        else:
            # Process single sheet
            sheet_data = spreadsheet.get_sheet_data(sheet_name)
            if not sheet_data or not sheet_data.values:
                return _create_response(False, error="no_sheet_data", error_msg=f"No data found in sheet '{sheet_name}'")
            
            # Find the column index
            headers = sheet_data.values[0] if sheet_data.values else []
            try:
                col_idx = headers.index(column_name)
            except ValueError:
                return _create_response(False, error="column_not_found", error_msg=f"Column '{column_name}' not found in sheet '{sheet_name}'")
            
            # Process each row (skip header)
            for row_idx, row in enumerate(sheet_data.values[1:], start=2):  # 1-based row indexing
                if col_idx < len(row):
                    cell_value = row[col_idx]
                    
                    if cell_value and isinstance(cell_value, str):
                        # Use the existing A1 reference update logic
                        update_result = update_a1_references_in_text(cell_value, old_tab_name, new_tab_name)
                        
                        if update_result["success"] and update_result["references_updated"] > 0:
                            # Found references to update
                            new_cell_value = update_result["updated_text"]
                            references_updated += update_result["references_updated"]
                            
                            # Update the cell using the correct method
                            try:
                                # Create a 2D list with just the single cell value
                                cell_update = [[new_cell_value]]
                                
                                # Update the specific cell using update_sheet_data
                                spreadsheet.update_sheet_data(
                                    sheet_name,
                                    cell_update,
                                    start_row=row_idx,
                                    start_col=col_idx + 1  # Convert to 1-based column indexing
                                )
                                
                                # Record the change
                                changes_made.append(f"Row {row_idx}: '{cell_value}' → '{new_cell_value}'")
                                
                            except Exception as e:
                                error_msg = f"Failed to update cell {sheet_name}:{row_idx}:{col_idx+1}: {e}"
                                errors.append(error_msg)
                                print(f"Warning: {error_msg}")
            
            # Save changes if any references were updated
            if references_updated > 0 and not errors:
                try:
                    spreadsheet.save()
                except Exception as e:
                    errors.append(f"Failed to save changes: {e}")
                    return _create_response(False, error="save_failed", error_msg=f"Failed to save: {str(e)}")
            
            return {
                "success": True,
                "references_updated": references_updated,
                "changes_made": changes_made,
                "errors": errors,
                "message": f"Updated {references_updated} A1 references in column '{column_name}'"
            }
        
    except Exception as e:
        return _create_response(False, error="update_error", error_msg=f"Update operation failed: {str(e)}")






