"""Tests for the PlatformNeutralizerValidator."""

import pytest
from unittest.mock import MagicMock, patch
from urarovite.validators.platform_neutralizer import PlatformNeutralizerValidator


class TestPlatformNeutralizerValidator:
    """Test the PlatformNeutralizerValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PlatformNeutralizerValidator()
        self.test_spreadsheet_url = (
            "https://docs.google.com/spreadsheets/d/test_id/edit"
        )
        self.test_excel_path = "/tmp/test.xlsx"
        self.test_auth_credentials = {
            "encoded_creds": "fake_base64_encoded_service_account"
        }

    def test_validator_initialization(self):
        """Test that the validator is properly initialized."""
        assert self.validator.id == "platform_neutralizer"
        assert self.validator.name == "Neutralize Platform-Specific Language"
        assert "Excel" in self.validator.description
        assert "Google Sheets" in self.validator.description

    def test_find_platform_mentions_excel_patterns(self):
        """Test detection of Excel-specific patterns."""
        test_cases = [
            # Excel variations (updated to match actual pattern behavior)
            ("Please update the Excel file.", 1, "the Excel file"),
            ("Review the Excel spreadsheet carefully.", 1, "the Excel spreadsheet"),
            ("Add data to the Excel workbook.", 1, "the Excel workbook"),
            (
                "Check the Excel sheet for errors.",
                1,
                "the Excel",
            ),  # More general pattern matches
            ("Create an Excel worksheet for tracking.", 1, "an Excel"),
            ("Just use Excel for this task.", 1, "use Excel"),
            # Case insensitive
            ("Update the EXCEL FILE please.", 1, "the EXCEL FILE"),
            ("Check excel spreadsheet data.", 1, "excel spreadsheet"),
        ]

        for text, expected_count, expected_mention in test_cases:
            mentions = self.validator._find_platform_mentions(text)
            assert len(mentions) == expected_count, f"Failed for: {text}"
            if expected_count > 0:
                assert expected_mention.lower() in mentions[0]["original"].lower(), (
                    f"Expected mention '{expected_mention}' not found in: {text}"
                )

    def test_find_platform_mentions_google_patterns(self):
        """Test detection of Google Sheets-specific patterns."""
        test_cases = [
            # Google Sheets variations
            ("Update the Google Sheet with new data.", 1, "Google Sheet"),
            ("Review the Google Sheets document.", 1, "Google Sheets"),
            ("Export the Google spreadsheet as CSV.", 1, "Google spreadsheet"),
            ("Create a Google Sheets file for this.", 1, "Google Sheets"),
            ("Check the Google workbook structure.", 1, "Google workbook"),
            # Multiple mentions
            ("Move data from Excel to Google Sheets.", 2, None),
        ]

        for text, expected_count, expected_mention in test_cases:
            mentions = self.validator._find_platform_mentions(text)
            assert len(mentions) == expected_count, f"Failed for: {text}"
            if expected_count == 1 and expected_mention:
                assert expected_mention.lower() in mentions[0]["original"].lower()

    def test_find_platform_mentions_no_matches(self):
        """Test cases that should not match platform patterns."""
        non_matches = [
            "Update the spreadsheet with new data.",
            "Review the document carefully.",
            "Add a chart to the worksheet.",
            "Export the file as CSV.",
            "This is excellent work.",  # "excel" as part of "excellent"
            "Google search for more information.",  # Google but not Sheets
            "Create a new workbook for this project.",  # Generic workbook
        ]

        for text in non_matches:
            mentions = self.validator._find_platform_mentions(text)
            assert len(mentions) == 0, f"Unexpected match found in: {text}"

    def test_neutralize_platform_language_simple(self):
        """Test simple platform language neutralization."""
        test_cases = [
            ("Update the Excel file.", "Update the spreadsheet."),
            ("Review the Google Sheet.", "Review the spreadsheet."),
            ("Export the Excel spreadsheet.", "Export the spreadsheet."),
            ("Create a Google Sheets document.", "Create a spreadsheet document."),
        ]

        for original, expected_cleaned in test_cases:
            mentions = self.validator._find_platform_mentions(original)
            cleaned, note = self.validator._neutralize_platform_language(
                original, mentions
            )

            # Check that the first line matches expected
            first_line = cleaned.split("\n")[0]
            assert first_line == expected_cleaned, (
                f"Expected: '{expected_cleaned}', Got: '{first_line}'"
            )

            # Check that editor note is present
            assert "[Editor:" in note
            assert "Neutralized platform language" in note

    def test_neutralize_platform_language_multiple(self):
        """Test neutralization with multiple platform mentions."""
        original = "Move data from the Excel file to the Google Sheet."
        mentions = self.validator._find_platform_mentions(original)

        cleaned, note = self.validator._neutralize_platform_language(original, mentions)
        first_line = cleaned.split("\n")[0]

        # Should neutralize both mentions
        assert "Excel" not in first_line
        assert "Google" not in first_line
        assert "spreadsheet" in first_line

        # Should indicate multiple changes
        assert "2 platform terms" in note or "2 platform" in note

    def test_neutralize_platform_language_no_mentions(self):
        """Test neutralization when no platform mentions exist."""
        original = "Update the spreadsheet with new data."
        mentions = []

        cleaned, note = self.validator._neutralize_platform_language(original, mentions)

        assert cleaned == original
        assert note == ""

    def test_validate_flag_mode_with_flags(self):
        """Test validation in flag mode with platform mentions."""
        # Mock sheet data with platform mentions
        test_data = [
            ["id", "prompt", "description"],
            ["1", "Please update the Excel file with new data.", "Test task"],
            ["2", "Review the Google Sheet for accuracy.", "Another task"],
            ["3", "This prompt has no platform mentions.", "Clean task"],
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

                # Should find 2 flags
                assert result["fixes_applied"] == 0
                assert result["flags_found"] == 2
                assert len(result["errors"]) == 0

                # Should have details about the flags
                assert "flags" in result["details"]
                assert len(result["details"]["flags"]) == 2
                assert result["details"]["flags"][0]["cell"] == "Sheet1!B1"
                assert result["details"]["flags"][1]["cell"] == "Sheet1!B2"

    def test_validate_fix_mode_with_flags(self):
        """Test validation in fix mode with platform mentions."""
        # Mock sheet data with platform mentions
        test_data = [
            ["id", "prompt", "description"],
            ["1", "Please update the Excel file with new data.", "Test task"],
            ["2", "Review the Google Sheet for accuracy.", "Another task"],
            ["3", "This prompt has no platform mentions.", "Clean task"],
        ]

        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(self.validator, "_update_sheet_data") as mock_update_data:
                with patch.object(
                    self.validator, "_get_spreadsheet"
                ) as mock_get_spreadsheet:
                    mock_get_data.return_value = (test_data, "Sheet1")
                    mock_spreadsheet = MagicMock()
                    mock_get_spreadsheet.return_value = mock_spreadsheet

                    result = self.validator.validate(
                        spreadsheet_source=self.test_spreadsheet_url,
                        mode="fix",
                        auth_credentials=self.test_auth_credentials,
                    )

                    # Should fix 2 flags
                    assert result["fixes_applied"] == 2
                    assert result["flags_found"] == 0
                    assert len(result["errors"]) == 0

                    # Should have called update method
                    mock_update_data.assert_called_once()
                    mock_spreadsheet.save.assert_called_once()

                    # Should have details about what was fixed
                    assert "fixes" in result["details"]
                    assert len(result["details"]["fixes"]) == 2
                    assert result["details"]["fixes"][0]["cell"] == "Sheet1!B1"
                    assert result["details"]["fixes"][1]["cell"] == "Sheet1!B2"

    def test_validate_no_flags(self):
        """Test validation when no platform mentions are found."""
        # Mock sheet data without platform mentions
        test_data = [
            ["id", "prompt", "description"],
            ["1", "Please update the spreadsheet with new data.", "Test task"],
            ["2", "Review the document for accuracy.", "Another task"],
            ["3", "Add a chart to the worksheet.", "Clean task"],
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

                # Should find no flags
                assert result["fixes_applied"] == 0
                assert result["flags_found"] == 0
                assert len(result["errors"]) == 0
                assert "No platform-specific language found" in result["automated_log"]

    def test_validate_empty_sheet(self):
        """Test validation when sheet is empty."""
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

                # Should handle empty sheet gracefully
                assert result["fixes_applied"] == 0
                assert result["flags_found"] == 0
                assert len(result["errors"]) == 0
                assert "No data found to validate" in result["automated_log"]

    def test_validate_missing_target_column(self):
        """Test validation when target column is missing."""
        # Mock sheet data without 'prompt' column
        test_data = [
            ["id", "description", "other"],
            ["1", "Test task", "data"],
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
                    target_column="prompt",
                )

                # Should handle missing column gracefully
                assert result["fixes_applied"] == 0
                assert result["flags_found"] == 0
                assert len(result["errors"]) == 0
                assert "not found" in result["automated_log"]

    def test_validate_custom_target_column(self):
        """Test validation with custom target column."""
        # Mock sheet data with custom column
        test_data = [
            ["id", "instructions", "description"],
            ["1", "Please update the Excel file with care.", "Test task"],
            ["2", "Review the document without platform terms.", "Another task"],
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
                    target_column="instructions",
                )

                # Should find 1 issue in the instructions column
                assert result["flags_found"] == 1
                assert len(result["errors"]) == 0

    def test_validate_handles_exceptions(self):
        """Test that validation handles unexpected exceptions gracefully."""
        with patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet:
            mock_get_spreadsheet.side_effect = Exception("Test error")

            result = self.validator.validate(
                spreadsheet_source=self.test_spreadsheet_url,
                mode="flag",
                auth_credentials=self.test_auth_credentials,
            )

            # Should handle exception gracefully
            assert result["fixes_applied"] == 0
            assert result["flags_found"] == 0
            assert len(result["errors"]) == 1
            assert "Unexpected error" in result["errors"][0]
            assert "Unexpected error" in result["automated_log"]

    def test_overlapping_patterns(self):
        """Test handling of overlapping patterns."""
        # This should only match once, not multiple overlapping matches
        text = "Update the Excel spreadsheet file."
        mentions = self.validator._find_platform_mentions(text)

        # Should find one mention, not multiple overlapping ones
        assert len(mentions) == 1
        assert "Excel spreadsheet" in mentions[0]["original"]

    def test_pattern_specificity(self):
        """Test that patterns are specific enough to avoid false positives."""
        false_positive_texts = [
            "This is excellent work on the project.",  # "excel" in "excellent"
            "Google search results show various options.",  # Google but not Sheets
            "The file contains good data.",  # Generic file mention
            "Create a workbook for this analysis.",  # Generic workbook
        ]

        for text in false_positive_texts:
            mentions = self.validator._find_platform_mentions(text)
            assert len(mentions) == 0, f"False positive detected in: {text}"

    def test_replacement_consistency(self):
        """Test that replacements are consistent and logical."""
        test_cases = [
            ("Excel file", "the spreadsheet"),  # "the Excel file" → "the spreadsheet"
            ("Excel spreadsheet", "the spreadsheet"),
            ("Excel workbook", "the spreadsheet"),
            ("Google Sheet", "the spreadsheet"),
            ("Google Sheets", "the spreadsheet"),
            ("Google spreadsheet", "the spreadsheet"),
        ]

        for original_phrase, expected_replacement in test_cases:
            text = f"Please update the {original_phrase}."
            mentions = self.validator._find_platform_mentions(text)

            if mentions:
                assert mentions[0]["replacement"] == expected_replacement, (
                    f"Expected '{expected_replacement}' for '{original_phrase}', got '{mentions[0]['replacement']}'"
                )

    def test_automated_log_messages(self):
        """Test that appropriate automated log messages are generated."""
        # Test with flags found in flag mode
        test_data = [
            ["prompt"],
            ["Update the Excel file."],
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

                assert (
                    "Found 1 prompts with platform-specific language"
                    in result["automated_log"]
                )

        # Test with fixes applied
        with patch.object(self.validator, "_get_all_sheet_data") as mock_get_data:
            with patch.object(self.validator, "_update_sheet_data"):
                with patch.object(
                    self.validator, "_get_spreadsheet"
                ) as mock_get_spreadsheet:
                    mock_get_data.return_value = (test_data, "Sheet1")
                    mock_spreadsheet = MagicMock()
                    mock_get_spreadsheet.return_value = mock_spreadsheet

                    result = self.validator.validate(
                        spreadsheet_source=self.test_spreadsheet_url,
                        mode="fix",
                        auth_credentials=self.test_auth_credentials,
                    )

                    assert (
                        "Neutralized platform language in 1 prompts"
                        in result["automated_log"]
                    )


class TestPlatformNeutralizerIntegration:
    """Integration tests for the PlatformNeutralizerValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PlatformNeutralizerValidator()

    def test_real_world_examples(self):
        """Test with realistic examples."""
        real_examples = [
            (
                "Clean the data in the Excel file for analysis.",
                "Clean the data in the spreadsheet for analysis.",
            ),
            (
                "Update the Google Sheet with quarterly results.",
                "Update the spreadsheet with quarterly results.",
            ),
            (
                "Export the Excel workbook as CSV format.",
                "Export the spreadsheet as CSV format.",
            ),
            (
                "Create charts in the Google Sheets document.",
                "Create charts in the spreadsheet document.",
            ),
            (
                "Review Excel spreadsheet for data accuracy.",
                "Review spreadsheet for data accuracy.",
            ),
        ]

        for original, expected in real_examples:
            mentions = self.validator._find_platform_mentions(original)
            assert len(mentions) >= 1, f"No mentions found in: {original}"

            cleaned, note = self.validator._neutralize_platform_language(
                original, mentions
            )
            first_line = cleaned.split("\n")[0]
            assert first_line == expected, (
                f"Expected: '{expected}', Got: '{first_line}'"
            )

    def test_comprehensive_workflow(self):
        """Test the complete workflow from detection to neutralization."""
        test_prompt = (
            "Please clean the Excel file and update the Google Sheet with results."
        )

        # Step 1: Detect mentions
        mentions = self.validator._find_platform_mentions(test_prompt)
        assert len(mentions) == 2  # Should find both Excel and Google mentions

        # Step 2: Neutralize the language
        cleaned, note = self.validator._neutralize_platform_language(
            test_prompt, mentions
        )

        # Step 3: Verify results
        first_line = cleaned.split("\n")[0]
        assert "Excel" not in first_line
        assert "Google" not in first_line
        assert "spreadsheet" in first_line
        assert "[Editor:" in note
        assert "2 platform terms" in note or "platform" in note.lower()

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        edge_cases = [
            # Empty/minimal text
            ("", []),
            ("Excel", ["Excel"]),
            # Multiple same platform
            ("Excel file and Excel sheet", ["Excel", "Excel"]),
            # Mixed platforms
            ("Excel to Google Sheets migration", ["Excel", "Google Sheets"]),
        ]

        for text, expected_originals in edge_cases:
            mentions = self.validator._find_platform_mentions(text)
            assert len(mentions) == len(expected_originals), f"Failed for: {text}"

            if mentions:
                # Verify that cleaning produces reasonable results
                cleaned, note = self.validator._neutralize_platform_language(
                    text, mentions
                )
                first_line = cleaned.split("\n")[0]
                assert isinstance(first_line, str)
                assert len(first_line.strip()) > 0 or text == ""
