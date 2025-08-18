"""Tests for the TabNameConsistencyValidator.

This module tests the tab name consistency validator that was migrated
from checker3. It validates that tab names referenced in verification
ranges exist with exact casing in both input and output spreadsheets.
"""

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from urarovite.validators import get_validator
from urarovite.validators.tab_name_consistency import run, TabNameConsistencyValidator
from urarovite.auth.google_sheets import get_gspread_client

# Test URLs (same as original checker3 tests)
REAL_INPUT_URL = "https://docs.google.com/spreadsheets/d/1wVWKw_l5eIWiLsiQPDrzjmodg2hMK9-RYxgDpT1YWaI/edit?usp=sharing"
REAL_OUTPUT_URL = "https://docs.google.com/spreadsheets/d/1ODsg5EHf7992lXcCZkilnsBeGEjJPqhafdrZj-4IhlE/edit?usp=sharing"


def _auth_available() -> bool:
    """Check if authentication credentials are available."""
    try:
        get_gspread_client()
        return True
    except Exception:
        return False


class TestTabNameConsistencyValidator:
    """Test cases for TabNameConsistencyValidator."""
    
    def test_validator_registration(self):
        """Test that the validator is properly registered."""
        validator = get_validator("tab_name_consistency")
        assert isinstance(validator, TabNameConsistencyValidator)
        assert validator.id == "tab_name_consistency"
        assert validator.name == "Tab Name Consistency"
        assert "tab names referenced in verification ranges" in validator.description
    
    def test_validator_present_tabs(self):
        """Test validator with tabs that exist in both spreadsheets."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        validator = TabNameConsistencyValidator()
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
        assert result["details"]["missing_in_input"] == []
        assert result["details"]["missing_in_output"] == []
        assert result["details"]["case_mismatches_input"] == []
        assert result["details"]["case_mismatches_output"] == []
        assert "Mar 2025" in result["referenced_tabs"]
        assert result["sheets"]["input"]["accessible"] is True
        assert result["sheets"]["output"]["accessible"] is True
    
    def test_validator_missing_tabs(self):
        """Test validator with tabs that don't exist in either spreadsheet."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        validator = TabNameConsistencyValidator()
        service = get_gspread_client()
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'March 2025'!A2:A91",  # Note: "March" vs "Mar"
        })
        
        result = validator.validate(
            sheets_service=service,
            sheet_id="",  # Not used by this validator
            mode="flag",
            row=row
        )
        
        # Validate result structure
        assert result["issues_found"] > 0
        assert "March 2025" in result["details"]["missing_in_input"]
        assert "March 2025" in result["details"]["missing_in_output"]
        assert "March 2025" in result["referenced_tabs"]
    
    @patch.object(TabNameConsistencyValidator, '_get_spreadsheet')
    def test_validator_no_ranges(self, mock_get_spreadsheet):
        """Test validator with no verification ranges."""
        validator = TabNameConsistencyValidator()
        
        # Mock spreadsheet
        mock_spreadsheet = MagicMock()
        mock_get_spreadsheet.return_value = mock_spreadsheet
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "",  # Empty ranges
        })
        
        with patch('urarovite.validators.tab_name_consistency.fetch_sheet_tabs') as mock_fetch:
            with patch('urarovite.auth.google_sheets.create_sheets_service_from_encoded_creds') as mock_create_service:
                mock_create_service.return_value = MagicMock()
                mock_fetch.return_value = {"accessible": True, "tabs": ["Sheet1", "Sheet2"]}
                
                result = validator.validate(
                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                    mode="flag",
                    auth_credentials={"encoded_creds": "fake_creds"},
                    row=row
                )
                
                assert len(result["errors"]) > 0
                assert "no_verification_ranges" in result["errors"]
    
    @patch.object(TabNameConsistencyValidator, '_get_spreadsheet')
    def test_validator_invalid_urls(self, mock_get_spreadsheet):
        """Test validator with invalid spreadsheet URLs."""
        validator = TabNameConsistencyValidator()
        
        # Mock spreadsheet
        mock_spreadsheet = MagicMock()
        mock_get_spreadsheet.return_value = mock_spreadsheet
        
        row = pd.Series({
            "input_sheet_url": "invalid_url",
            "example_output_sheet_url": "also_invalid",
            "verification_field_ranges": "'Sheet1'!A1:A10",
        })
        
        with patch('urarovite.validators.tab_name_consistency.fetch_sheet_tabs') as mock_fetch:
            with patch('urarovite.auth.google_sheets.create_sheets_service_from_encoded_creds') as mock_create_service:
                mock_create_service.return_value = MagicMock()
                mock_fetch.return_value = {"accessible": False, "tabs": []}
                
                result = validator.validate(
                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                    mode="flag",
                    auth_credentials={"encoded_creds": "fake_creds"},
                    row=row
                )
                
                assert len(result["errors"]) > 0
                assert result["details"]["sheets"]["input"]["accessible"] is False
                assert result["details"]["sheets"]["output"]["accessible"] is False
    
    def test_validator_missing_row_data(self):
        """Test validator with missing row data."""
        validator = TabNameConsistencyValidator()
        
        with patch.object(validator, '_get_spreadsheet') as mock_get_spreadsheet:
            mock_spreadsheet = MagicMock()
            mock_get_spreadsheet.return_value = mock_spreadsheet
            
            # Should return empty result instead of raising exception
            result = validator.validate(
                spreadsheet_source="dummy_source",  # Not used by this validator
                mode="flag",
                auth_credentials={"encoded_creds": "fake_creds"}
                # Missing row parameter
            )
            
            assert result["issues_found"] == 0
            assert result["details"]["missing_in_input"] == []
            assert result["details"]["missing_in_output"] == []
            assert result["details"]["case_mismatches_input"] == []
            assert result["details"]["case_mismatches_output"] == []
            assert result["errors"] == []


class TestBackwardCompatibility:
    """Test backward compatibility with the original checker3 interface."""
    
    def test_run_function_present_tabs(self):
        """Test the run() function with tabs that exist."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'Mar 2025'!A2:A91",
        })
        
        result = run(row)
        
        # Should have same structure as original checker3
        assert result["issues_found"] == 0
        assert result["details"]["missing_in_input"] == []
        assert result["details"]["missing_in_output"] == []
        assert result["details"]["case_mismatches_input"] == []
        assert result["details"]["case_mismatches_output"] == []
        assert "Mar 2025" in result["referenced_tabs"]
    
    def test_run_function_missing_tabs(self):
        """Test the run() function with missing tabs."""
        if not _auth_available():  # pragma: no cover
            pytest.skip("Google Sheets authentication credentials not available")
        
        row = pd.Series({
            "input_sheet_url": REAL_INPUT_URL,
            "example_output_sheet_url": REAL_OUTPUT_URL,
            "verification_field_ranges": "'March 2025'!A2:A91",
        })
        
        result = run(row)
        
        # Should have same structure as original checker3
        assert result["issues_found"] > 0
        assert "March 2025" in result["details"]["missing_in_input"]
        assert "March 2025" in result["details"]["missing_in_output"]
    
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
            input_col="custom_input",
            output_col="custom_output",
            ranges_col="custom_ranges"
        )
        
        assert result["issues_found"] == 0
        assert "Mar 2025" in result["referenced_tabs"]


class TestValidatorLogic:
    """Test specific validator logic components."""
    
    def test_parse_referenced_tabs(self):
        """Test tab name parsing from verification ranges."""
        validator = TabNameConsistencyValidator()
        
        # Test single tab
        tabs = validator._parse_referenced_tabs("'Sheet1'!A1:A10")
        assert tabs == ["Sheet1"]
        
        # Test multiple tabs with @@ separator (order may vary due to set() usage)
        tabs = validator._parse_referenced_tabs("'Sheet1'!A1:A10@@'Sheet2'!B1:B10")
        assert set(tabs) == {"Sheet1", "Sheet2"}
        
        # Test tab without quotes (should return empty list as implementation only handles quoted names)
        tabs = validator._parse_referenced_tabs("Sheet1!A1:A10")
        assert tabs == []
        
        # Test empty ranges
        tabs = validator._parse_referenced_tabs("")
        assert tabs == []
        
        # Test None ranges
        tabs = validator._parse_referenced_tabs(None)
        assert tabs == []
    
    def test_extract_sheet_id(self):
        """Test sheet ID extraction from URLs."""
        validator = TabNameConsistencyValidator()
        
        # Test valid URL
        sheet_id = validator._extract_sheet_id(
            "https://docs.google.com/spreadsheets/d/1wVWKw_l5eIWiLsiQPDrzjmodg2hMK9-RYxgDpT1YWaI/edit"
        )
        assert sheet_id == "1wVWKw_l5eIWiLsiQPDrzjmodg2hMK9-RYxgDpT1YWaI"
        
        # Test invalid URL
        sheet_id = validator._extract_sheet_id("invalid_url")
        assert sheet_id == ""
        
        # Test None URL
        sheet_id = validator._extract_sheet_id(None)
        assert sheet_id == ""
    
    def test_create_case_map(self):
        """Test case mapping creation."""
        validator = TabNameConsistencyValidator()
        
        tabs = ["Sheet1", "SHEET2", "sheet3"]
        case_map = validator._create_case_map(tabs)
        
        assert case_map["sheet1"] == "Sheet1"
        assert case_map["sheet2"] == "SHEET2"
        assert case_map["sheet3"] == "sheet3"
