"""Tests for the SheetAccessibilityValidator."""

import pytest
from unittest.mock import patch, MagicMock
from urarovite.validators.sheet_accessibility import SheetAccessibilityValidator


class TestSheetAccessibilityValidator:
    """Test the SheetAccessibilityValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SheetAccessibilityValidator()
        self.test_spreadsheet_url = (
            "https://docs.google.com/spreadsheets/d/test_id/edit"
        )
        self.test_auth_credentials = {"auth_secret": "fake_auth_secret"}

    def test_validate_accessible_urls(self):
        """Test validation of accessible Google Sheets URLs."""
        # Mock data with Google Sheets URLs
        test_data = [
            ["Header1", "Sheet URL", "Header3"],
            [
                "Data1",
                "https://docs.google.com/spreadsheets/d/accessible123/edit",
                "Data3",
            ],
            [
                "Data2",
                "https://docs.google.com/spreadsheets/d/accessible456/edit",
                "Data4",
            ],
        ]

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                with patch.object(self.validator, "_detect_url_columns") as mock_detect:
                    with patch.object(
                        self.validator, "_check_url_accessibility"
                    ) as mock_check:
                        mock_get_data.return_value = (test_data, "Sheet1")
                        mock_spreadsheet = MagicMock()
                        mock_get_spreadsheet.return_value = mock_spreadsheet
                        mock_detect.return_value = [2]  # Column 2 contains URLs
                        mock_check.return_value = {"accessible": True, "error": None}

                        result = self.validator.validate(
                            spreadsheet_source=self.test_spreadsheet_url,
                            mode="flag",
                            auth_credentials=self.test_auth_credentials,
                        )

                        # Verify results
                        assert result["flags_found"] == 0
                        assert result["fixes_applied"] == 0
                        assert len(result["errors"]) == 0
                        assert "flags" not in result["details"]

    def test_validate_inaccessible_urls(self):
        """Test validation of inaccessible Google Sheets URLs."""
        # Mock data with mix of accessible and inaccessible URLs
        test_data = [
            ["Header1", "Sheet URL", "Header3"],
            [
                "Data1",
                "https://docs.google.com/spreadsheets/d/accessible123/edit",
                "Data3",
            ],
            [
                "Data2",
                "https://docs.google.com/spreadsheets/d/inaccessible456/edit",
                "Data4",
            ],
        ]

        def mock_check_accessibility(url, auth_secret=None, subject=None):
            if "inaccessible" in url:
                return {"accessible": False, "error": "403 Forbidden"}
            return {"accessible": True, "error": None}

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                with patch.object(self.validator, "_detect_url_columns") as mock_detect:
                    with patch.object(
                        self.validator, "_check_url_accessibility"
                    ) as mock_check:
                        mock_get_data.return_value = (test_data, "Sheet1")
                        mock_spreadsheet = MagicMock()
                        mock_get_spreadsheet.return_value = mock_spreadsheet
                        mock_detect.return_value = [2]  # Column 2 contains URLs
                        mock_check.side_effect = mock_check_accessibility

                        result = self.validator.validate(
                            spreadsheet_source=self.test_spreadsheet_url,
                            mode="flag",
                            auth_credentials=self.test_auth_credentials,
                        )

                        # Verify results
                        assert result["flags_found"] == 1
                        assert result["fixes_applied"] == 0
                        assert len(result["errors"]) == 0
                        assert "flags" in result["details"]
                        assert len(result["details"]["flags"]) == 1
                        assert (
                            result["details"]["flags"][0]["value"]
                            == "https://docs.google.com/spreadsheets/d/inaccessible456/edit"
                        )

    def test_validate_no_urls_found(self):
        """Test validation when no Google Sheets URLs are found."""
        # Mock data without Google Sheets URLs
        test_data = [
            ["Header1", "Header2", "Header3"],
            ["Data1", "https://example.com", "Data3"],
            ["Data2", "Not a URL", "Data4"],
        ]

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                mock_get_data.return_value = (test_data, "Sheet1")
                mock_spreadsheet = MagicMock()
                mock_get_spreadsheet.return_value = mock_spreadsheet

                result = self.validator.validate(
                    spreadsheet_source=self.test_spreadsheet_url,
                    mode="flag",
                    auth_credentials=self.test_auth_credentials,
                )

                # Verify results
                assert result["flags_found"] == 0
                assert result["fixes_applied"] == 0
                assert len(result["errors"]) == 0  # No errors should be added
                assert "No Google Sheets URLs found" in result["details"]["message"]

    def test_validate_empty_sheet(self):
        """Test validation of empty sheet."""
        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                mock_get_data.return_value = ([], "Sheet1")
                mock_spreadsheet = MagicMock()
                mock_get_spreadsheet.return_value = mock_spreadsheet

                result = self.validator.validate(
                    spreadsheet_source=self.test_spreadsheet_url,
                    mode="flag",
                    auth_credentials=self.test_auth_credentials,
                )

                # Verify results
                assert result["flags_found"] == 0
                assert result["fixes_applied"] == 0
                assert len(result["errors"]) == 1
                assert "Sheet is empty" in result["errors"][0]

    def test_validate_missing_auth_secret(self):
        """Test validation when auth_credentials is missing."""
        test_data = [
            ["Header1", "Sheet URL", "Header3"],
            ["Data1", "https://docs.google.com/spreadsheets/d/test123/edit", "Data3"],
        ]

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                mock_get_data.return_value = (test_data, "Sheet1")
                mock_spreadsheet = MagicMock()
                mock_get_spreadsheet.return_value = mock_spreadsheet

                result = self.validator.validate(
                    spreadsheet_source=self.test_spreadsheet_url,
                    mode="flag",
                    # No auth_credentials provided
                )

                # Verify results
                assert result["flags_found"] == 0
                assert result["fixes_applied"] == 0
                assert len(result["errors"]) == 0  # No errors should be added
                assert (
                    "Authentication credentials not provided"
                    in result["details"]["message"]
                )

    def test_detect_url_columns(self):
        """Test URL column detection."""
        test_data = [
            ["Name", "Sheet URL", "Description", "Another URL"],
            [
                "Test1",
                "https://docs.google.com/spreadsheets/d/abc123/edit",
                "Desc1",
                "https://example.com",
            ],
            [
                "Test2",
                "https://docs.google.com/spreadsheets/d/def456/edit",
                "Desc2",
                "https://docs.google.com/spreadsheets/d/ghi789/edit",
            ],
        ]

        url_columns = self.validator._detect_url_columns(test_data)

        # Should detect columns 2 and 4 (1-based indexing)
        assert 2 in url_columns  # "Sheet URL" column
        assert 4 in url_columns  # "Another URL" column
        assert len(url_columns) == 2

    def test_extract_sheet_id(self):
        """Test spreadsheet ID extraction from URLs."""
        # Valid URLs
        assert (
            self.validator._extract_sheet_id(
                "https://docs.google.com/spreadsheets/d/1ABC123def456/edit"
            )
            == "1ABC123def456"
        )

        assert (
            self.validator._extract_sheet_id(
                "https://docs.google.com/spreadsheets/d/test-sheet_123/edit?usp=sharing"
            )
            == "test-sheet_123"
        )

        # Invalid URLs
        assert self.validator._extract_sheet_id("https://example.com") is None
        assert self.validator._extract_sheet_id("") is None
        assert self.validator._extract_sheet_id(None) is None

    def test_fix_mode_error(self):
        """Test that fix mode returns appropriate error."""
        test_data = [
            ["Header1", "Sheet URL"],
            ["Data1", "https://docs.google.com/spreadsheets/d/inaccessible123/edit"],
        ]

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(
                self.validator, "_get_spreadsheet"
            ) as mock_get_spreadsheet:
                with patch.object(self.validator, "_detect_url_columns") as mock_detect:
                    with patch.object(
                        self.validator, "_check_url_accessibility"
                    ) as mock_check:
                        mock_get_data.return_value = (test_data, "Sheet1")
                        mock_spreadsheet = MagicMock()
                        mock_get_spreadsheet.return_value = mock_spreadsheet
                        mock_detect.return_value = [2]  # Column 2 contains URLs
                        mock_check.return_value = {
                            "accessible": False,
                            "error": "forbidden",
                        }

                        result = self.validator.validate(
                            spreadsheet_source=self.test_spreadsheet_url,
                            mode="fix",
                            auth_credentials=self.test_auth_credentials,
                        )

                        # Verify that fix mode doesn't produce errors (just flags flags)
                        assert result["flags_found"] == 1
                        assert result["fixes_applied"] == 0
                        assert (
                            len(result["errors"]) == 0
                        )  # Fix mode should not add errors
                        assert "flags" in result["details"]
                        assert (
                            result["details"]["flags"][0]["value"]
                            == "https://docs.google.com/spreadsheets/d/inaccessible123/edit"
                        )
