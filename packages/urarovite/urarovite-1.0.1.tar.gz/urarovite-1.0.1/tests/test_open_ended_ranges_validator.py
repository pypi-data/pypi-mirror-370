"""Tests for the OpenEndedRangesValidator.

This module tests the open-ended ranges validator that was migrated
from checker4. It detects unbounded A1 notations that can cause flaky
verification due to sensitivity to trailing empties and layout changes.
"""

import pandas as pd
import pytest
from unittest.mock import patch, Mock, MagicMock
from urarovite.validators import get_validator
from urarovite.validators.open_ended_ranges import run, OpenEndedRangesValidator
from urarovite.auth.google_sheets import get_gspread_client

# Test URLs (same as original checker4 tests)
REAL_INPUT_URL = "https://docs.google.com/spreadsheets/d/1wVWKw_l5eIWiLsiQPDrzjmodg2hMK9-RYxgDpT1YWaI/edit?usp=sharing"
REAL_OUTPUT_URL = "https://docs.google.com/spreadsheets/d/1ODsg5EHf7992lXcCZkilnsBeGEjJPqhafdrZj-4IhlE/edit?usp=sharing"


def _auth_available() -> bool:
    """Check if authentication credentials are available."""
    try:
        get_gspread_client()
        return True
    except Exception:
        return False


class TestOpenEndedRangesValidator:
    """Test cases for OpenEndedRangesValidator."""
    
    def test_validator_registration(self):
        """Test that the validator is properly registered."""
        validator = get_validator("open_ended_ranges")
        assert isinstance(validator, OpenEndedRangesValidator)
        assert validator.id == "open_ended_ranges"
        assert validator.name == "Open-Ended Ranges Detection"
        assert "unbounded A1 notations" in validator.description
    
    def test_validator_bounded_ranges(self):
        """Test validator with properly bounded ranges."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        validator = OpenEndedRangesValidator()
        service = get_gspread_client()
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'Mar 2025'!A2:A91",
        })
        
        result = validator.validate(
            sheets_service=service,
            sheet_id="",  # Not used by this validator
            mode="flag",
            row=row
        )
        
        # Validate result structure
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 1
        assert result["details"]["open_ended"] == []
        assert result["details"]["original"] == "'Mar 2025'!A2:A91"
    
    def test_validator_whole_column(self):
        """Test validator with whole column ranges."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        validator = OpenEndedRangesValidator()
        service = get_gspread_client()
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'Mar 2025'!A:A",
        })
        
        result = validator.validate(
            sheets_service=service,
            sheet_id="",
            mode="flag",
            row=row
        )
        
        # Validate result structure
        assert result["issues_found"] > 0
        assert result["details"]["total_segments"] == 1
        assert len(result["details"]["open_ended"]) == 1
        
        entry = result["details"]["open_ended"][0]
        assert entry["reason"] == "whole_column"
        assert entry["segment"].endswith("A:A")
        assert entry["suggested"].startswith("'Mar 2025'!A1:A")
        assert "tab_bounds" in entry
    
    def test_validator_half_bounded_column(self):
        """Test validator with half-bounded column ranges."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        validator = OpenEndedRangesValidator()
        service = get_gspread_client()
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'Mar 2025'!A1:A",
        })
        
        result = validator.validate(
            sheets_service=service,
            sheet_id="",
            mode="flag",
            row=row
        )
        
        # Validate result structure
        assert result["issues_found"] > 0
        assert len(result["details"]["open_ended"]) == 1
        
        entry = result["details"]["open_ended"][0]
        assert entry["reason"] == "half_bounded_column"
        assert entry["segment"].endswith("A1:A")
        assert "suggested" in entry
    
    def test_validator_whole_row(self):
        """Test validator with whole row ranges."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        validator = OpenEndedRangesValidator()
        service = get_gspread_client()
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'Mar 2025'!3:3",
        })
        
        result = validator.validate(
            sheets_service=service,
            sheet_id="",
            mode="flag",
            row=row
        )
        
        # Validate result structure
        assert result["issues_found"] > 0
        assert len(result["details"]["open_ended"]) == 1
        
        entry = result["details"]["open_ended"][0]
        assert entry["reason"] == "whole_row"
        assert entry["segment"].endswith("3:3")
        assert "suggested" in entry
    
    def test_validator_multiple_segments(self):
        """Test validator with multiple range segments."""
        validator = OpenEndedRangesValidator()
        service = get_gspread_client() if _auth_available() else None
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'Sheet1'!A1:B10@@'Sheet2'!A:A@@'Sheet3'!3:3",
        })
        
        # Mock the spreadsheet since this validator doesn't actually use it
        with patch.object(validator, '_get_spreadsheet') as mock_get_spreadsheet:
            mock_spreadsheet = MagicMock()
            mock_get_spreadsheet.return_value = mock_spreadsheet
            
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test123/edit",
                mode="flag",
                auth_credentials={"auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="},
                row=row
            )
        
        assert "details" in result
        assert result["details"]["total_segments"] == 3
        # Should detect 2 open-ended ranges (A:A and 3:3)
        # Note: actual detection depends on sheet accessibility
    
    def test_validator_missing_row_data(self):
        """Test validator with missing row data."""
        validator = OpenEndedRangesValidator()
        service = get_gspread_client() if _auth_available() else None
        
        # Mock the spreadsheet since this validator doesn't actually use it
        with patch.object(validator, '_get_spreadsheet') as mock_get_spreadsheet:
            mock_spreadsheet = MagicMock()
            mock_get_spreadsheet.return_value = mock_spreadsheet
            
            # Should return empty result instead of raising exception
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test123/edit",
                mode="flag",
                auth_credentials={"auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="}
                # Missing row parameter
            )
        
        assert result["issues_found"] == 0
        assert result["details"]["open_ended_count"] == 0
        assert result["details"]["open_ended"] == []


class TestBackwardCompatibility:
    """Test backward compatibility with the original checker4 interface."""
    
    def test_run_function_bounded(self):
        """Test the run() function with bounded ranges."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'Mar 2025'!A2:A91",
        })
        
        result = run(row)
        
        # Should have same structure as original checker4
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 1
        assert result["details"]["open_ended"] == []
    
    def test_run_function_whole_column(self):
        """Test the run() function with whole column ranges."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'Mar 2025'!A:A",
        })
        
        result = run(row)
        
        # Should have same structure as original checker4
        assert result["issues_found"] > 0
        assert len(result["details"]["open_ended"]) == 1
        entry = result["details"]["open_ended"][0]
        assert entry["reason"] == "whole_column"
        assert entry["segment"].endswith("A:A")
    
    def test_run_function_custom_columns(self):
        """Test the run() function with custom column names."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        row = pd.Series({
            "custom_input": REAL_INPUT_URL,
            "custom_output": REAL_OUTPUT_URL,
            "custom_ranges": "'Mar 2025'!A2:A91",
        })
        
        result = run(
            row,
            field="custom_ranges",
            input_col="custom_input",
            output_col="custom_output"
        )
        
        assert result["issues_found"] == 0


class TestValidatorLogic:
    """Test specific validator logic components."""
    
    def test_is_open_ended_detection(self):
        """Test range classification logic."""
        validator = OpenEndedRangesValidator()
        
        # Test bounded ranges
        bounded_ranges = ["A1:B10", "C5:D20", "A1", "Z99"]
        for range_part in bounded_ranges:
            reason, is_open = validator._is_open_ended(range_part)
            assert not is_open, f"{range_part} should be bounded"
            assert reason is None
        
        # Test whole columns
        whole_col_ranges = ["A:A", "B:C", "A:Z"]
        for range_part in whole_col_ranges:
            reason, is_open = validator._is_open_ended(range_part)
            assert is_open, f"{range_part} should be open-ended"
            assert reason == "whole_column"
        
        # Test whole rows
        whole_row_ranges = ["1:1", "3:5", "10:20"]
        for range_part in whole_row_ranges:
            reason, is_open = validator._is_open_ended(range_part)
            assert is_open, f"{range_part} should be open-ended"
            assert reason == "whole_row"
        
        # Test half-bounded columns
        half_bounded_ranges = ["A1:A", "B10:C", "Z5:Z"]
        for range_part in half_bounded_ranges:
            reason, is_open = validator._is_open_ended(range_part)
            assert is_open, f"{range_part} should be open-ended"
            assert reason == "half_bounded_column"
    
    def test_suggest_data_bound(self):
        """Test bounded range suggestion generation."""
        validator = OpenEndedRangesValidator()
        
        # Test whole column suggestion
        suggestion = validator._suggest_data_bound("Sheet1", "A:A", "whole_column", 100, 5)
        assert suggestion == "Sheet1!A1:A100"
        
        # Test half-bounded column suggestion
        suggestion = validator._suggest_data_bound("Sheet1", "A1:A", "half_bounded_column", 50, 3)
        assert suggestion == "Sheet1!A1:A50"
        
        # Test whole row suggestion
        suggestion = validator._suggest_data_bound("Sheet1", "3:3", "whole_row", 100, 5)
        assert suggestion == "Sheet1!A3:E3"
        
        # Test with empty sheet name
        suggestion = validator._suggest_data_bound("", "A:A", "whole_column", 10, 2)
        assert suggestion == "A1:A10"
    
    def test_get_tab_bounds(self):
        """Test tab bounds detection."""
        validator = OpenEndedRangesValidator()
        
        # Test with None spreadsheet ID
        rows, cols = validator._get_tab_bounds(None, "Sheet1")
        assert rows == 0 and cols == 0
        
        # Test with invalid spreadsheet ID
        rows, cols = validator._get_tab_bounds("invalid_id", "Sheet1")
        assert rows == 0 and cols == 0
        
        # Note: Testing with real spreadsheet IDs would require authentication
        # and is covered in the integration tests above
