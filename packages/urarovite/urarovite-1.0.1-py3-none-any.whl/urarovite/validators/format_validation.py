"""Format validation validators for common data formats.

This module implements validators for checking and fixing common data formats
such as email addresses, phone numbers, dates, and URLs.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Union
from urllib.parse import urlparse
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface
from urarovite.validators.sheet_name_quoting import run as validate_sheet_name_quoting


class EmailValidator(BaseValidator):
    """Validator for email address formats."""
    
    # Basic email regex pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_emails",
            name="Validate Email Addresses",
            description="Checks email format and optionally flags invalid emails"
        )
    
    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        email_columns: List[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate email addresses in specified columns.
        
        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            email_columns: List of 1-based column indices containing emails
            
        Returns:
            Dict with validation results
        """
        def validation_logic(
            spreadsheet: SpreadsheetInterface,
            result: ValidationResult,
            **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)
            
            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return
            
            # Auto-detect email columns if not specified
            detected_email_columns = email_columns
            if detected_email_columns is None:
                detected_email_columns = self._detect_email_columns(data)
            
            invalid_emails = []
            
            # Check each specified column for invalid emails
            for row_idx, row in enumerate(data):
                for col_idx in detected_email_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        email = str(row[col_zero_based]).strip()
                        
                        if email and not self._is_valid_email(email):
                            cell_ref = self._generate_cell_reference(
                                row_idx, col_zero_based
                            )
                            invalid_emails.append({
                                "row": row_idx + 1,
                                "col": col_idx,
                                "cell_ref": cell_ref,
                                "email": email,
                                "issue": "Invalid format"
                            })
            
            # Record results
            if invalid_emails:
                result.add_issue(len(invalid_emails))
                result.details["invalid_emails"] = invalid_emails
                result.set_automated_log(
                    f"Invalid emails found: {len(invalid_emails)} entries"
                )
                # Note: Fix mode does nothing for this validator since we cannot
                # automatically correct invalid email addresses
            else:
                result.set_automated_log("No issues found")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if an email address is valid."""
        return bool(self.EMAIL_PATTERN.match(email))
    
    def _detect_email_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain email addresses."""
        email_columns = []
        
        if not data:
            return email_columns
        
        # Check first few rows for email-like content
        sample_rows = data[:min(10, len(data))]
        
        for col_idx in range(len(data[0]) if data else 0):
            email_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    if self._is_valid_email(str(row[col_idx]).strip()):
                        email_count += 1
            
            # If more than 50% of non-empty cells look like emails, include this column
            if total_non_empty > 0 and email_count / total_non_empty > 0.5:
                email_columns.append(col_idx + 1)  # Convert to 1-based
        
        return email_columns


class PhoneNumberValidator(BaseValidator):
    """Validator for phone number formats."""
    
    # Basic phone number patterns
    PHONE_PATTERNS = [
        re.compile(r'^\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$'),  # US format
        re.compile(r'^\+?(\d{1,3})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})$'),  # International
    ]
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_phone_numbers",
            name="Validate Phone Numbers", 
            description="Validates phone number formats and consistency"
        )
    
    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        phone_columns: List[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate phone numbers in specified columns.
        
        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (standardize format) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            phone_columns: List of 1-based column indices containing phone numbers
            
        Returns:
            Dict with validation results
        """
        def validation_logic(
            spreadsheet: SpreadsheetInterface,
            result: ValidationResult,
            **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)
            
            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return
            
            # Auto-detect phone columns if not specified
            detected_phone_columns = phone_columns
            if detected_phone_columns is None:
                detected_phone_columns = self._detect_phone_columns(data)
            
            invalid_phones = []
            fixes_to_apply = []
            
            # Check and optionally prepare fixes for phone numbers
            for row_idx, row in enumerate(data):
                for col_idx in detected_phone_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        phone = str(row[col_zero_based]).strip()
                        
                        if phone:
                            standardized = self._standardize_phone(phone)
                            cell_ref = self._generate_cell_reference(row_idx, col_zero_based)
                            
                            if not standardized:
                                invalid_phones.append({
                                    "row": row_idx + 1,
                                    "col": col_idx,
                                    "cell_ref": cell_ref,
                                    "phone": phone,
                                    "issue": "Invalid format"
                                })
                            elif mode == "fix" and standardized != phone:
                                fixes_to_apply.append({
                                    "row": row_idx,
                                    "col": col_zero_based,
                                    "new_value": standardized
                                })
            
            # Apply fixes if in fix mode
            if mode == "fix" and fixes_to_apply:
                self._apply_fixes_to_sheet(spreadsheet, sheet_name, data, fixes_to_apply)
                spreadsheet.save()
            
            # Record results
            if invalid_phones:
                if mode == "fix":
                    standardized_count = len(fixes_to_apply)
                    result.add_fix(standardized_count)
                    result.details["standardized_phones"] = invalid_phones
                    result.set_automated_log(f"Standardized phone numbers: {standardized_count} entries")
                else:
                    result.add_issue(len(invalid_phones))
                    result.details["invalid_phones"] = invalid_phones
                    result.set_automated_log(f"Invalid phone numbers found: {len(invalid_phones)} entries")
            else:
                result.set_automated_log("No issues found")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )
    
    def _standardize_phone(self, phone: str) -> str:
        """Standardize phone number format."""
        # Remove all non-digit characters except +
        re.sub(r'[^\d+]', '', phone)
        
        # Try to match against patterns and standardize
        for pattern in self.PHONE_PATTERNS:
            if pattern.match(phone):
                # For US numbers, standardize to (XXX) XXX-XXXX
                digits = re.sub(r'[^\d]', '', phone)
                if len(digits) == 10:
                    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                elif len(digits) == 11 and digits[0] == '1':
                    return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return ""  # Invalid phone number
    
    def _detect_phone_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain phone numbers."""
        phone_columns = []
        
        if not data:
            return phone_columns
        
        # Check first few rows for phone-like content
        sample_rows = data[:min(10, len(data))]
        
        for col_idx in range(len(data[0]) if data else 0):
            phone_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    phone_str = str(row[col_idx]).strip()
                    if any(pattern.match(phone_str) for pattern in self.PHONE_PATTERNS):
                        phone_count += 1
            
            # If more than 50% of non-empty cells look like phone numbers, include this column
            if total_non_empty > 0 and phone_count / total_non_empty > 0.5:
                phone_columns.append(col_idx + 1)  # Convert to 1-based
        
        return phone_columns


class DateValidator(BaseValidator):
    """Validator for date formats."""
    
    # Common date formats to try
    DATE_FORMATS = [
        "%Y-%m-%d",      # 2023-12-25
        "%m/%d/%Y",      # 12/25/2023
        "%d/%m/%Y",      # 25/12/2023
        "%Y/%m/%d",      # 2023/12/25
        "%m-%d-%Y",      # 12-25-2023
        "%d-%m-%Y",      # 25-12-2023
        "%B %d, %Y",     # December 25, 2023
        "%d %B %Y",      # 25 December 2023
        "%m/%d/%y",      # 12/25/23
        "%d/%m/%y",      # 25/12/23
    ]
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_dates",
            name="Validate Date Formats",
            description="Checks and standardizes date formats"
        )
    
    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        date_columns: List[int] = None,
        target_format: str = "%Y-%m-%d",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate and optionally standardize date formats.
        
        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (standardize format) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            date_columns: List of 1-based column indices containing dates
            target_format: Target date format for standardization
            
        Returns:
            Dict with validation results
        """
        def validation_logic(
            spreadsheet: SpreadsheetInterface,
            result: ValidationResult,
            **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)
            
            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return
            
            # Auto-detect date columns if not specified
            detected_date_columns = date_columns
            if detected_date_columns is None:
                detected_date_columns = self._detect_date_columns(data)
            
            date_issues = []
            fixes_to_apply = []
            
            # Check and optionally prepare fixes for dates
            for row_idx, row in enumerate(data):
                for col_idx in detected_date_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        date_str = str(row[col_zero_based]).strip()
                        
                        if date_str:
                            parsed_date, original_format = self._parse_date(date_str)
                            cell_ref = self._generate_cell_reference(row_idx, col_zero_based)
                            
                            if not parsed_date:
                                date_issues.append({
                                    "row": row_idx + 1,
                                    "col": col_idx,
                                    "cell_ref": cell_ref,
                                    "date": date_str,
                                    "issue": "Invalid date format"
                                })
                            elif mode == "fix" and original_format != target_format:
                                standardized = parsed_date.strftime(target_format)
                                fixes_to_apply.append({
                                    "row": row_idx,
                                    "col": col_zero_based,
                                    "new_value": standardized
                                })
                                date_issues.append({
                                    "row": row_idx + 1,
                                    "col": col_idx,
                                    "cell_ref": cell_ref,
                                    "original": date_str,
                                    "standardized": standardized
                                })
            
            # Apply fixes if in fix mode
            if mode == "fix" and fixes_to_apply:
                self._apply_fixes_to_sheet(spreadsheet, sheet_name, data, fixes_to_apply)
                spreadsheet.save()
            
            # Record results
            if date_issues:
                if mode == "fix":
                    valid_fixes = [d for d in date_issues if "standardized" in d]
                    result.add_fix(len(valid_fixes))
                    result.details["standardized_dates"] = valid_fixes
                    result.set_automated_log(f"Standardized dates: {len(valid_fixes)} entries")
                    
                    invalid_dates = [d for d in date_issues if "issue" in d]
                    if invalid_dates:
                        result.add_issue(len(invalid_dates))
                        result.details["invalid_dates"] = invalid_dates
                else:
                    result.add_issue(len(date_issues))
                    result.details["date_issues"] = date_issues
                    result.set_automated_log(f"Date format issues found: {len(date_issues)} entries")
            else:
                result.set_automated_log("No issues found")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, 
            date_columns=date_columns, target_format=target_format, **kwargs
        )
    
    def _parse_date(self, date_str: str) -> tuple[datetime, str]:
        """Try to parse a date string using various formats."""
        for fmt in self.DATE_FORMATS:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed, fmt
            except ValueError:
                continue
        return None, None
    
    def _detect_date_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain dates."""
        date_columns = []
        
        if not data:
            return date_columns
        
        # Check first few rows for date-like content
        sample_rows = data[:min(10, len(data))]
        
        for col_idx in range(len(data[0]) if data else 0):
            date_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    date_str = str(row[col_idx]).strip()
                    if self._parse_date(date_str)[0]:
                        date_count += 1
            
            # If more than 50% of non-empty cells look like dates, include this column
            if total_non_empty > 0 and date_count / total_non_empty > 0.5:
                date_columns.append(col_idx + 1)  # Convert to 1-based
        
        return date_columns


class URLValidator(BaseValidator):
    """Validator for URL formats."""
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_urls",
            name="Validate URLs",
            description="Validates URL format and accessibility"
        )
    
    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        url_columns: List[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate URLs in specified columns.
        
        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            url_columns: List of 1-based column indices containing URLs
            
        Returns:
            Dict with validation results
        """
        def validation_logic(
            spreadsheet: SpreadsheetInterface,
            result: ValidationResult,
            **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)
            
            if not data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return
            
            # Auto-detect URL columns if not specified
            detected_url_columns = url_columns
            if detected_url_columns is None:
                detected_url_columns = self._detect_url_columns(data)
            
            invalid_urls = []
            
            # Check URLs
            for row_idx, row in enumerate(data):
                for col_idx in detected_url_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        url = str(row[col_zero_based]).strip()
                        
                        if url and not self._is_valid_url(url):
                            cell_ref = self._generate_cell_reference(row_idx, col_zero_based)
                            invalid_urls.append({
                                "row": row_idx + 1,
                                "col": col_idx,
                                "cell_ref": cell_ref,
                                "url": url,
                                "issue": "Invalid URL format"
                            })
            
            # Record results
            if invalid_urls:
                result.add_issue(len(invalid_urls))
                result.details["invalid_urls"] = invalid_urls
                result.set_automated_log(f"Invalid URLs found: {len(invalid_urls)} entries")
                # Note: Fix mode does nothing for this validator since we cannot
                # automatically correct invalid URLs
            else:
                result.set_automated_log("No issues found")

        return self._execute_validation(
            validation_logic, spreadsheet_source, auth_credentials, **kwargs
        )
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _detect_url_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain URLs."""
        url_columns = []
        
        if not data:
            return url_columns
        
        # Check first few rows for URL-like content
        sample_rows = data[:min(10, len(data))]
        
        for col_idx in range(len(data[0]) if data else 0):
            url_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    url_str = str(row[col_idx]).strip()
                    if self._is_valid_url(url_str):
                        url_count += 1
            
            # If more than 50% of non-empty cells look like URLs, include this column
            if total_non_empty > 0 and url_count / total_non_empty > 0.5:
                url_columns.append(col_idx + 1)  # Convert to 1-based
        
        return url_columns
    
class VerificationRangesValidator(BaseValidator):
    """Validator for verification ranges."""
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_verification_ranges",
            name="Validate Verification Ranges",
            description="Validates verification ranges for proper A1 notation, @@ separators, and quoted tab names"
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        verification_ranges_columns: List[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate verification ranges in specified columns.
        
        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (auto-quote tabs and fix separators) or "flag" (report only)
            auth_credentials: Authentication credentials (required for Google Sheets)
            verification_ranges_columns: List of 1-based column indices containing verification ranges

        Returns:
            Dict with validation results
        """
        result = ValidationResult()
        spreadsheet = None
        
        try:
            # Get spreadsheet interface
            spreadsheet = self._get_spreadsheet(spreadsheet_source, auth_credentials, read_only=mode != 'fix')
            
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)
            
            if not data:
                result.add_error("Sheet is empty - no data to validate")
                result.set_automated_log("Sheet is empty - no data to validate")
                return result.to_dict()
            
            # Auto-detect verification ranges columns if not specified
            if verification_ranges_columns is None:
                verification_ranges_columns = self._detect_verification_ranges_columns(data)
            
            invalid_ranges = []
            fixed_data = []
            
            # Check and optionally fix verification ranges
            for row_idx, row in enumerate(data):
                fixed_row = list(row)
                
                for col_idx in verification_ranges_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        ranges_str = str(row[col_zero_based]).strip()
                        
                        if ranges_str:
                            validation_result = self._validate_ranges(ranges_str)
                            
                            if not validation_result["ok"]:
                                if mode == "fix":
                                    # Try to fix the ranges
                                    fixed_ranges = self._fix_ranges(ranges_str)
                                    if fixed_ranges != ranges_str:
                                        fixed_row[col_zero_based] = fixed_ranges
                                        invalid_ranges.append({
                                            "row": row_idx + 1,
                                            "col": col_idx,
                                            "original": ranges_str,
                                            "fixed": fixed_ranges,
                                            "issues": validation_result["failing_segments"]
                                        })
                                    else:
                                        invalid_ranges.append({
                                            "row": row_idx + 1,
                                            "col": col_idx,
                                            "ranges_str": ranges_str,
                                            "issue": "Cannot auto-fix verification range format",
                                            "failing_segments": validation_result["failing_segments"]
                                        })
                                else:
                                    invalid_ranges.append({
                                        "row": row_idx + 1,
                                        "col": col_idx,
                                        "ranges_str": ranges_str,
                                        "issue": "Invalid verification range format",
                                        "failing_segments": validation_result["failing_segments"]
                                    })
                
                fixed_data.append(fixed_row)
            
            # Record results
            if invalid_ranges:
                if mode == "fix":
                    # Update the sheet with fixed data
                    self._update_sheet_data(spreadsheet, sheet_name, fixed_data)
                    
                    # Save changes (important for Excel files)
                    spreadsheet.save()
                    
                    fixed_count = len([r for r in invalid_ranges if "fixed" in r])
                    unfixed_count = len([r for r in invalid_ranges if "fixed" not in r])
                    
                    if fixed_count > 0:
                        result.add_fix(fixed_count)
                        result.details["fixed_ranges"] = [r for r in invalid_ranges if "fixed" in r]
                        result.set_automated_log(f"Fixed verification ranges: {fixed_count} ranges")
                    
                    if unfixed_count > 0:
                        result.add_issue(unfixed_count)
                        result.details["unfixed_ranges"] = [r for r in invalid_ranges if "fixed" not in r]
                        if fixed_count == 0:  # Only set log if no fixes were applied
                            result.set_automated_log(f"Invalid verification ranges: {unfixed_count} ranges")
                else:
                    result.add_issue(len(invalid_ranges))
                    result.details["invalid_ranges"] = invalid_ranges
                    result.set_automated_log(f"Invalid verification ranges: {len(invalid_ranges)} ranges")
            else:
                result.set_automated_log("No issues found")
            
        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
        finally:
            # Clean up resources
            if spreadsheet:
                try:
                    spreadsheet.close()
                except Exception:
                    pass  # Ignore cleanup errors
        
        return result.to_dict()
    
    def _validate_ranges(self, ranges_str: str) -> Dict[str, Any]:
        """Validate verification ranges using sheet name quoting validator."""
        result = validate_sheet_name_quoting(ranges_str)
        # Convert ValidationResult format to old format for backward compatibility
        return {
            "ok": result["issues_found"] == 0,
            "failing_segments": result["details"].get("failing_segments", []),
            "total_segments": result["details"].get("total_segments", 0),
            "original": result["details"].get("original", ranges_str)
        }
    
    def _fix_ranges(self, ranges_str: str) -> str:
        """Fix common issues in verification ranges."""
        # Split by @@ and clean up segments
        segments = [s.strip() for s in ranges_str.split("@@") if s.strip()]
        fixed_segments = []
        
        for segment in segments:
            fixed_segment = self._fix_segment(segment)
            fixed_segments.append(fixed_segment)
        
        return "@@".join(fixed_segments)
    
    def _fix_segment(self, segment: str) -> str:
        """Fix a single range segment."""
        segment = segment.strip()
        
        # If segment already starts with a quoted sheet name, return as-is
        if re.match(r"^'[^']+'!", segment):
            return segment
        
        # Check if there's an exclamation mark (sheet!range format)
        if "!" in segment:
            sheet_part, range_part = segment.split("!", 1)
            sheet_part = sheet_part.strip()
            range_part = range_part.strip()
            
            # If sheet name contains spaces or special characters, quote it
            if self._needs_quoting(sheet_part):
                # Remove existing quotes if malformed
                if sheet_part.startswith("'") and not sheet_part.endswith("'"):
                    sheet_part = sheet_part[1:]
                elif sheet_part.endswith("'") and not sheet_part.startswith("'"):
                    sheet_part = sheet_part[:-1]
                elif sheet_part.startswith("'") and sheet_part.endswith("'"):
                    # Already properly quoted, just return
                    return f"'{sheet_part[1:-1]}'!{range_part}"
                
                return f"'{sheet_part}'!{range_part}"
            else:
                # No spaces/special chars, but still needs quotes for consistency
                return f"'{sheet_part}'!{range_part}"
        else:
            # Whole sheet reference, quote it
            if self._needs_quoting(segment):
                return f"'{segment}'"
            else:
                return f"'{segment}'"
    
    def _needs_quoting(self, sheet_name: str) -> bool:
        """Check if a sheet name needs quoting (has spaces or special characters)."""
        # According to the spec, we want to quote all sheet names for consistency
        # but especially those with spaces or non-alphanumeric characters
        return not re.match(r'^[a-zA-Z0-9_]+$', sheet_name)
    
    def _detect_verification_ranges_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain verification ranges."""
        verification_ranges_columns = []
        
        if not data:
            return verification_ranges_columns
        
        # Check first few rows for verification ranges
        sample_rows = data[:min(10, len(data))]

        for col_idx in range(len(data[0]) if data else 0):
            verification_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    ranges_str = str(row[col_idx]).strip()
                    if self._looks_like_verification_range(ranges_str):
                        verification_count += 1
            
            # If more than 50% of non-empty cells look like verification ranges, include this column
            if total_non_empty > 0 and verification_count / total_non_empty > 0.5:
                verification_ranges_columns.append(col_idx + 1)  # Convert to 1-based
        
        return verification_ranges_columns
    
    def _looks_like_verification_range(self, ranges_str: str) -> bool:
        """Check if a string looks like a verification range."""
        if not ranges_str:
            return False
        
        # Look for patterns that suggest A1 notation ranges
        # - Contains letters followed by numbers (A1, B2, etc.)
        # - Contains exclamation marks (sheet references)
        # - Contains @@ separators
        # - Contains colons (range separators)
        patterns = [
            r'[A-Z]+\d+',      # A1 notation
            r'!',              # Sheet reference
            r'@@',             # Segment separator
            r'[A-Z]+\d+:[A-Z]+\d+',  # Range notation
        ]
        
        return any(re.search(pattern, ranges_str) for pattern in patterns)