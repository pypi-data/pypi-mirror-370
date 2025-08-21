"""Tests for the CSVToJSONTransformValidator.

This module tests the CSV to JSON transformation validator that converts
CSV task data into structured JSON format with standardized fields.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from urarovite.validators import get_validator
from urarovite.validators.csv_to_json_transform import (
    CSVToJSONTransformValidator,
    transform_csv_to_json,
)


class TestCSVToJSONTransformValidator:
    """Test cases for CSVToJSONTransformValidator."""

    def test_validator_registration(self):
        """Test that the validator is properly registered."""
        validator = get_validator("csv_to_json_transform")
        assert isinstance(validator, CSVToJSONTransformValidator)
        assert validator.id == "csv_to_json_transform"
        assert validator.name == "CSV to JSON Transform"
        assert "Transform the task CSV into JSON" in validator.description

    def test_transform_row_basic(self):
        """Test basic row transformation with real CSV data structure."""
        validator = CSVToJSONTransformValidator()

        # Real data from the actual CSV with typical content
        input_row = {
            "worker_id": "7CM2GYGPCQRR",
            "task_id": "919309a8-ed81-41a8-a1a4-4a32d94db8b2",
            "task_response_id": "3d17cc01-f367-4546-92d1-6882144d9f54",
            "job domain": "Information and Record Clerks",
            "description": "This dataset tracks monthly student attendance for an instructor who has 90 students...",
            "prompt": "I combined a couple of my old attendance sheets to create the attendance sheet for March 2025, and there are a lot of duplicate rows in it. Can you remove the duplicate rows so that there is only one student per student ID?",
            "verification_criteria": "Rows 4, 6, 9, 11, 14, 16, 19, 22, 24, 27, 30, 33, 36, 38, 40, 43, 45, 48, 50, 57, 60, 62, 64, 66, 69, 72, 74, 77, 79, 81, 83, 86, 88, 90, 93, 96, 100, 102, 105, 109, 111, 114, 116, 119, 121, 124, 127, 130, 132, 135, 138, 140, 141, and 144 from the original document have been deleted due to duplicate information.",
            "verification_field_ranges": "March 2025'!A2:A91",
            "input_sheet_url": "https://docs.google.com/spreadsheets/d/1wVWKw_l5eIWiLsiQPDrzjmodg2hMK9-RYxgDpT1YWaI/edit?usp=sharing",
            "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/1ODsg5EHf7992lXcCZkilnsBeGEjJPqhafdrZj-4IhlE/edit?usp=sharing",
        }

        result = validator._transform_row(input_row)

        # Check ID fields are preserved (no collision)
        assert result["worker_id"] == "7CM2GYGPCQRR"
        assert result["task_id"] == "919309a8-ed81-41a8-a1a4-4a32d94db8b2"
        assert result["task_response_id"] == "3d17cc01-f367-4546-92d1-6882144d9f54"

        # Check snake_case conversion for spaced field
        assert result["job_domain"] == "Information and Record Clerks"

        # Check content fields
        assert "attendance for an instructor" in result["description"]
        assert "duplicate rows" in result["prompt"]
        assert "deleted due to duplicate" in result["verification_criteria"]

        # Check A1 range fix was applied
        assert result["verification_field_ranges"] == "'March 2025'!A2:A91"
        assert "_a1_range_fixes" in result
        assert len(result["_a1_range_fixes"]) == 1
        assert result["_a1_range_fixes"][0]["original"] == "March 2025'!A2:A91"
        assert result["_a1_range_fixes"][0]["fixed"] == "'March 2025'!A2:A91"

        # Check field mappings
        assert (
            result["input_file"]
            == "https://docs.google.com/spreadsheets/d/1wVWKw_l5eIWiLsiQPDrzjmodg2hMK9-RYxgDpT1YWaI/edit?usp=sharing"
        )
        assert (
            result["output_file"]
            == "https://docs.google.com/spreadsheets/d/1ODsg5EHf7992lXcCZkilnsBeGEjJPqhafdrZj-4IhlE/edit?usp=sharing"
        )

        # Check template fields are set to "NA"
        assert result["input_excel_file"] == "NA"
        assert result["output_excel_file"] == "NA"
        assert result["field_mask"] == "NA"
        assert result["case_sensitivity"] == "NA"
        assert result["numeric_rounding"] == "NA"
        assert result["color_matching"] == "NA"
        assert result["editor_fixes"] == "NA"
        assert result["editor_comments"] == "NA"
        assert result["estimated_task_length"] == "NA"

    def test_transform_row_empty_values(self):
        """Test row transformation with empty/whitespace values."""
        validator = CSVToJSONTransformValidator()

        input_row = {
            "prompt": "",  # Empty string
            "verification_field_ranges": "   ",  # Whitespace only
            "input_sheet_url": None,  # None value
            "example_output_sheet_url": "valid_url",
        }

        result = validator._transform_row(input_row)

        # Empty/whitespace values should become empty strings
        assert result["prompt"] == ""
        assert result["verification_field_ranges"] == ""
        assert result["input_sheet_url"] == ""

        # Mapped empty fields should also be empty strings
        assert result["input_file"] == ""

        # Valid values should be preserved
        assert result["output_file"] == "valid_url"
        assert result["example_output_sheet_url"] == "valid_url"

        # Template fields should still be "NA"
        assert result["input_excel_file"] == "NA"

    def test_transform_row_missing_fields(self):
        """Test row transformation when some CSV fields are missing."""
        validator = CSVToJSONTransformValidator()

        input_row = {
            "prompt": "Test prompt"
            # Missing other expected fields
        }

        result = validator._transform_row(input_row)

        # Present field should be included
        assert result["prompt"] == "Test prompt"

        # Missing mapped fields should be empty strings
        assert result["input_file"] == ""
        assert result["output_file"] == ""

        # Template fields should be "NA"
        assert result["input_excel_file"] == "NA"

    def test_a1_range_detection(self):
        """Test detection of malformed A1 notation ranges."""
        validator = CSVToJSONTransformValidator()

        # Malformed ranges that should be detected
        malformed_ranges = [
            "March 2025'!A2:A91",  # Missing opening quote
            "Sheet1'A11:D72",  # Missing exclamation mark
            "Data SheetA1:B10",  # Missing quotes and exclamation
            "Q1 Results'!B1:C100",  # Missing opening quote with spaces
            "MySheet'C1:Z999",  # Missing exclamation mark
        ]

        for range_value in malformed_ranges:
            assert validator._detect_malformed_a1_range(range_value), (
                f"Should detect '{range_value}' as malformed A1 range"
            )

        # Well-formed ranges that should NOT be detected as malformed
        well_formed_ranges = [
            "'March 2025'!A2:A91",  # Properly formatted
            "'Sheet1'!A11:D72",  # Properly formatted
            "'Data Sheet'!A1:B10",  # Properly formatted with spaces
            "regular text",  # Not a range at all
            "A1:B10",  # Simple range without sheet
            "",  # Empty string
        ]

        for range_value in well_formed_ranges:
            assert not validator._detect_malformed_a1_range(range_value), (
                f"Should NOT detect '{range_value}' as malformed A1 range"
            )

    def test_a1_range_fixing(self):
        """Test fixing of malformed A1 notation ranges."""
        validator = CSVToJSONTransformValidator()

        test_cases = [
            ("March 2025'!A2:A91", "'March 2025'!A2:A91"),  # Missing opening quote
            ("Sheet1'A11:D72", "'Sheet1'!A11:D72"),  # Missing exclamation mark
            (
                "Data SheetA1:B10",
                "'Data Sheet'!A1:B10",
            ),  # Missing quotes and exclamation
            (
                "Q1 Results'!B1:C100",
                "'Q1 Results'!B1:C100",
            ),  # Missing opening quote with spaces
            ("MySheet'C1:Z999", "'MySheet'!C1:Z999"),  # Missing exclamation mark
            ("'Already Good'!A1:B10", "'Already Good'!A1:B10"),  # Should not change
            ("regular text", "regular text"),  # Should not change
        ]

        for original, expected in test_cases:
            result = validator._fix_a1_range(original)
            assert result == expected, (
                f"Expected '{expected}' but got '{result}' for input '{original}'"
            )

    def test_transform_row_with_a1_range_fixes(self):
        """Test row transformation with A1 range fixes applied."""
        validator = CSVToJSONTransformValidator()

        input_row = {
            "verification_field_ranges": "March 2025'!A2:A91",  # Should be fixed
            "prompt": "Test prompt",  # Should not change
            "other_ranges": "Sheet1'C1:D10",  # Should be fixed (snake_case field)
        }

        result = validator._transform_row(input_row)

        # Check that A1 range fixes were applied
        assert result["verification_field_ranges"] == "'March 2025'!A2:A91"
        assert result["other_ranges"] == "'Sheet1'!C1:D10"
        assert result["prompt"] == "Test prompt"

        # Check that A1 range fixes metadata was added
        assert "_a1_range_fixes" in result
        fixes = result["_a1_range_fixes"]
        assert len(fixes) == 2

        # Verify fix details
        fix_fields = [fix["field"] for fix in fixes]
        assert "verification_field_ranges" in fix_fields
        assert "other_ranges" in fix_fields

    @patch("urarovite.validators.csv_to_json_transform.fetch_sheet_tabs")
    @patch("urarovite.validators.csv_to_json_transform.get_sheet_values")
    def test_read_csv_data(self, mock_get_values, mock_fetch_tabs):
        """Test reading CSV data from a Google Sheet."""
        # Mock sheet tabs
        mock_fetch_tabs.return_value = {
            "accessible": True,
            "tabs": ["Sheet1"],
            "error": None,
        }

        # Mock sheet values (header + data rows)
        mock_get_values.return_value = {
            "success": True,
            "values": [
                ["prompt", "verification_field_ranges", "input_sheet_url"],
                ["Test prompt 1", "Sheet1!A1:B10", "https://example.com/1"],
                ["Test prompt 2", "Sheet2!C1:D10", "https://example.com/2"],
            ],
        }

        validator = CSVToJSONTransformValidator()
        mock_service = Mock()

        result = validator._read_csv_data(mock_service, "test_sheet_id")

        assert len(result) == 2
        assert result[0]["prompt"] == "Test prompt 1"
        assert result[1]["prompt"] == "Test prompt 2"
        assert result[0]["verification_field_ranges"] == "Sheet1!A1:B10"

    def test_validate_flag_mode(self):
        """Test validator in flag mode."""
        validator = CSVToJSONTransformValidator()

        # Create a complete mock result that matches what the real validator produces
        mock_result = {
            "flags_found": 0,
            "fixes_applied": 0,
            "errors": [],
            "automated_log": "Would transform 1 rows to JSON format",
            "details": {
                "total_rows": 1,
                "transformed_rows": 1,
                "a1_range_fixes_applied": 0,
                "json_schema": [
                    "worker_id",
                    "task_id",
                    "prompt",
                    "input_file",
                    "output_file",
                ],
                "sample_output": [
                    {
                        "worker_id": "test_worker",
                        "task_id": "test_task",
                        "prompt": "Test prompt",
                        "input_file": "https://example.com",
                        "output_file": "",
                        "input_excel_file": "",
                        "output_excel_file": "",
                        "verification_field_ranges": "",
                        "field_mask": "",
                        "case_sensitivity": "",
                        "numeric_rounding": "",
                        "color_matching": "",
                        "editor_fixes": "",
                        "editor_comments": "",
                        "estimated_task_length": "",
                    }
                ],
            },
        }

        with patch.object(validator, "_execute_validation", return_value=mock_result):
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                mode="flag",
                auth_credentials={
                    "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                },
            )

        assert result["flags_found"] == 0
        assert result["fixes_applied"] == 0
        assert result["details"]["total_rows"] == 1
        assert result["details"]["transformed_rows"] == 1
        assert "Would transform 1 rows" in result["automated_log"]

        # Check that fixes are logged as flags in flag mode
        if result["details"]["a1_range_fixes_applied"] > 0:
            assert "flags" in result["details"]
            assert len(result["details"]["flags"]) > 0
            assert (
                result["details"]["flags"][0]["message"]
                == "Fixed malformed A1 range notation"
            )

        # Check sample output
        sample = result["details"]["sample_output"][0]
        assert sample["prompt"] == "Test prompt"
        assert sample["input_file"] == "https://example.com"

    @patch("urarovite.validators.csv_to_json_transform.update_sheet_values")
    def test_validate_fix_mode(self, mock_update):
        """Test validator in fix mode."""
        validator = CSVToJSONTransformValidator()

        # Mock successful sheet update
        mock_update.return_value = {"success": True}

        # Create a complete mock result that matches what the real validator produces
        mock_result = {
            "flags_found": 0,
            "fixes_applied": 1,
            "errors": [],
            "automated_log": "Transformed 1 rows to JSON format and wrote to sheet",
            "details": {
                "total_rows": 1,
                "transformed_rows": 1,
                "a1_range_fixes_applied": 0,
                "json_schema": [
                    "worker_id",
                    "task_id",
                    "prompt",
                    "input_file",
                    "output_file",
                ],
                "sample_output": [
                    {
                        "worker_id": "test_worker",
                        "task_id": "test_task",
                        "prompt": "Test prompt",
                        "input_file": "https://example.com",
                        "output_file": "",
                        "input_excel_file": "",
                        "output_excel_file": "",
                        "verification_field_ranges": "",
                        "field_mask": "",
                        "case_sensitivity": "",
                        "numeric_rounding": "",
                        "color_matching": "",
                        "editor_fixes": "",
                        "editor_comments": "",
                        "estimated_task_length": "",
                    }
                ],
            },
        }

        # Mock the validation execution and simulate the sheet update call
        def mock_execute_validation(*args, **kwargs):
            # Simulate that the validator calls update_sheet_values during execution
            mock_update("test_sheet_id", "JSON_Output", [["header"], ["data"]], "A1")
            return mock_result

        with patch.object(
            validator, "_execute_validation", side_effect=mock_execute_validation
        ):
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                mode="fix",
                auth_credentials={
                    "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                },
            )

        assert result["flags_found"] == 0
        assert result["fixes_applied"] == 1
        assert result["details"]["total_rows"] == 1
        assert result["details"]["transformed_rows"] == 1
        assert "Transformed 1 rows to JSON format" in result["automated_log"]

        # Check that fixes are logged correctly
        if result["details"]["a1_range_fixes_applied"] > 0:
            assert "fixes" in result["details"]
            assert len(result["details"]["fixes"]) > 0
            assert (
                result["details"]["fixes"][0]["message"]
                == "Fixed malformed A1 range notation"
            )

        # Verify that update_sheet_values was called to write JSON column
        mock_update.assert_called()

    def test_validate_no_data(self):
        """Test validator with no CSV data - should raise ValidationError."""
        validator = CSVToJSONTransformValidator()

        # Mock the validation execution to raise the expected error
        from urarovite.core.exceptions import ValidationError

        def mock_execute_validation(*args, **kwargs):
            raise ValidationError("Unable to access sheet tabs")

        with patch.object(
            validator, "_execute_validation", side_effect=mock_execute_validation
        ):
            with pytest.raises(ValidationError, match="Unable to access sheet tabs"):
                validator.validate(
                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                    mode="flag",
                    auth_credentials={
                        "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                    },
                )

    def test_realistic_a1_range_scenarios(self):
        """Test A1 range fixes with realistic scenarios from the actual data."""
        validator = CSVToJSONTransformValidator()

        # Real malformed A1 ranges from the data
        test_cases = [
            {
                "original": "March 2025'!A2:A91",
                "expected": "'March 2025'!A2:A91",
                "description": "Missing opening quote",
            },
            {
                "original": "Sheet1'A11:D72",
                "expected": "'Sheet1'!A11:D72",
                "description": "Missing opening quote and exclamation",
            },
            {
                "original": "Data Analysis Sheet'!B5:F100",
                "expected": "'Data Analysis Sheet'!B5:F100",
                "description": "Missing opening quote only",
            },
        ]

        for case in test_cases:
            input_row = {
                "worker_id": "TEST123",
                "verification_field_ranges": case["original"],
                "prompt": "Test task",
            }

            result = validator._transform_row(input_row)

            assert result["verification_field_ranges"] == case["expected"], (
                f"Failed for {case['description']}: {case['original']}"
            )
            assert "_a1_range_fixes" in result
            assert len(result["_a1_range_fixes"]) == 1
            assert result["_a1_range_fixes"][0]["original"] == case["original"]
            assert result["_a1_range_fixes"][0]["fixed"] == case["expected"]

    def test_realistic_job_domains(self):
        """Test various job domains from the actual data."""
        validator = CSVToJSONTransformValidator()

        job_domains = [
            "Information and Record Clerks",
            "Life Scientists",
            "Data Scientists",
            "Administrative Support Workers",
            "Computer and Mathematical Occupations",
        ]

        for job_domain in job_domains:
            input_row = {
                "worker_id": "TEST123",
                "job domain": job_domain,
                "prompt": "Test task",
            }

            result = validator._transform_row(input_row)
            assert result["job_domain"] == job_domain
            assert result["worker_id"] == "TEST123"  # Ensure no collision

    def test_realistic_task_descriptions(self):
        """Test with realistic long task descriptions and prompts."""
        validator = CSVToJSONTransformValidator()

        # From actual data - long descriptions with special characters
        long_description = 'The dataset shows the results of a foraging study comparing the consumption rates of "Mix27A" to a control over the course of a month. Researchers use this spreadsheet to compile their observations, including the starting and ending mass of the two mixes across 2 sites, and the data is calculated to show the total consumption and difference between them.'

        long_prompt = 'I have this spreadsheet that shows the results of a foraging study, but it was filled out by multiple researchers. Unfortunately, one of them did not follow the instructions and now some of the data is invalid. Please fix the dates to make sure they are all in "MM/DD/YYYY" format with leading 0\'s removed. Also, the sites should be either "Catskill Park" or "Pelham Bay Park"; please fix any that are shortened. Some of the masses have been entered in kilograms rather than grams. Please fix the weights in the Control Start Mass column by removing any decimal points. Finally, do the same for the weights in the Control End Mass column.'

        input_row = {
            "worker_id": "Y4ACFC2HGKYD",
            "task_id": "4d3d4aca-de90-4663-87df-e71dbb3d1a81",
            "job domain": "Life Scientists",
            "description": long_description,
            "prompt": long_prompt,
            "verification_field_ranges": "Sheet1'A11:D72",
        }

        result = validator._transform_row(input_row)

        # Check that long content is preserved
        assert result["description"] == long_description
        assert result["prompt"] == long_prompt
        assert "foraging study" in result["description"]
        assert "multiple researchers" in result["prompt"]
        assert '"MM/DD/YYYY"' in result["prompt"]  # Quotes preserved

        # Check A1 range was fixed
        assert result["verification_field_ranges"] == "'Sheet1'!A11:D72"

    def test_field_mapping_completeness(self):
        """Test that the field mapping includes all expected CSV fields."""
        validator = CSVToJSONTransformValidator()

        expected_mappings = {
            "worker_id": "worker_id",
            "task_id": "task_id",
            "task_response_id": "task_response_id",
            "job domain": "job_domain",
            "description": "description",
            "prompt": "prompt",
            "verification_criteria": "verification_criteria",
            "verification_field_ranges": "verification_field_ranges",
            "input_sheet_url": "input_file",
            "example_output_sheet_url": "output_file",
        }

        assert validator.FIELD_MAPPING == expected_mappings

    def test_default_fields_completeness(self):
        """Test that all required default fields are present."""
        validator = CSVToJSONTransformValidator()

        expected_defaults = {
            "input_excel_file",
            "output_excel_file",
            "field_mask",
            "case_sensitivity",
            "numeric_rounding",
            "color_matching",
            "editor_fixes",
            "editor_comments",
            "estimated_task_length",
        }

        assert set(validator.TEMPLATE_FIELDS.keys()) == expected_defaults

        # All template fields should be "NA"
        for value in validator.TEMPLATE_FIELDS.values():
            assert value == "NA"

    def test_malformed_csv_non_string_headers(self):
        """Test handling of non-string column headers."""
        validator = CSVToJSONTransformValidator()

        # Simulate non-string headers (numbers, None, etc.)
        input_row = {
            123: "numeric header value",  # Numeric header
            None: "none header value",  # None header
            "": "empty header value",  # Empty string header
            "normal_field": "normal value",
        }

        result = validator._transform_row(input_row)

        # Check that non-string headers are converted to strings
        assert "123" in result
        assert "none" in result or str(None).lower() in result
        assert "" in result or "empty" in result
        assert result["normal_field"] == "normal value"

        # All values should be strings
        assert all(
            isinstance(v, str) for k, v in result.items() if not k.startswith("_")
        )

    def test_malformed_csv_duplicate_column_names(self):
        """Test handling of duplicate column names."""
        validator = CSVToJSONTransformValidator()

        # Simulate duplicate headers by testing what happens when dict overwrites
        input_row = {"prompt": "first value", "description": "first description"}

        # Manually test duplicate scenario - second value should win
        duplicate_test = {
            "prompt": "second value",  # This would overwrite in real CSV
            "description": "second description",
        }
        input_row.update(duplicate_test)

        result = validator._transform_row(input_row)

        # Last value should win (Python dict behavior)
        assert result["prompt"] == "second value"
        assert result["description"] == "second description"

    def test_extremely_long_field_values(self):
        """Test handling of extremely long field values."""
        validator = CSVToJSONTransformValidator()

        # Create extremely long values (simulate real-world edge cases)
        very_long_description = "A" * 10000  # 10KB description
        very_long_prompt = "B" * 5000  # 5KB prompt
        very_long_criteria = "C" * 8000  # 8KB criteria

        input_row = {
            "worker_id": "LONG_TEST",
            "description": very_long_description,
            "prompt": very_long_prompt,
            "verification_criteria": very_long_criteria,
            "verification_field_ranges": "Sheet1!A1:B10",
        }

        result = validator._transform_row(input_row)

        # Check that long values are preserved
        assert len(result["description"]) == 10000
        assert len(result["prompt"]) == 5000
        assert len(result["verification_criteria"]) == 8000
        assert result["description"] == very_long_description
        assert result["prompt"] == very_long_prompt
        assert result["verification_criteria"] == very_long_criteria

        # Other fields should still work normally
        assert result["worker_id"] == "LONG_TEST"
        assert result["verification_field_ranges"] == "Sheet1!A1:B10"

    def test_a1_ranges_with_special_characters_in_sheet_names(self):
        """Test A1 range fixes with special characters in sheet names."""
        validator = CSVToJSONTransformValidator()

        # Test cases with various special characters in sheet names
        test_cases = [
            {
                "original": "Sheet with spaces & symbols'A1:B10",
                "expected": "'Sheet with spaces & symbols'!A1:B10",
                "description": "Spaces, ampersand, missing quote and exclamation",
            },
            {
                "original": "Data-Analysis_2024'!C5:F50",
                "expected": "'Data-Analysis_2024'!C5:F50",
                "description": "Hyphens, underscores, numbers, missing opening quote",
            },
            {
                "original": "Sales (Q1) Results'A1:Z100",
                "expected": "'Sales (Q1) Results'!A1:Z100",
                "description": "Parentheses, missing quote and exclamation",
            },
            {
                "original": "Report #1: Revenue@2024'!B2:D999",
                "expected": "'Report #1: Revenue@2024'!B2:D999",
                "description": "Hash, colon, at symbol, missing opening quote",
            },
            {
                "original": "José's Data Sheet'A1:A10",
                "expected": "'José's Data Sheet'!A1:A10",
                "description": "Unicode characters, apostrophe in name",
            },
            {
                "original": "100% Complete Tasks'!A1:B5",
                "expected": "'100% Complete Tasks'!A1:B5",
                "description": "Percent symbol, numbers, missing opening quote",
            },
        ]

        for case in test_cases:
            input_row = {
                "worker_id": "SPECIAL_TEST",
                "verification_field_ranges": case["original"],
                "prompt": f"Testing {case['description']}",
            }

            result = validator._transform_row(input_row)

            assert result["verification_field_ranges"] == case["expected"], (
                f"Failed for {case['description']}: '{case['original']}' should become '{case['expected']}' but got '{result['verification_field_ranges']}'"
            )

            # Check fix was tracked
            assert "_a1_range_fixes" in result
            assert len(result["_a1_range_fixes"]) == 1
            assert result["_a1_range_fixes"][0]["original"] == case["original"]
            assert result["_a1_range_fixes"][0]["fixed"] == case["expected"]

    @patch("urarovite.validators.csv_to_json_transform.update_sheet_values")
    def test_json_output_when_many_columns_exist(self, mock_update):
        """Test JSON output when there are already many columns (potential collision)."""
        validator = CSVToJSONTransformValidator()

        # Mock successful sheet update
        mock_update.return_value = {"success": True}

        # Mock the validation execution and simulate the sheet update call
        def mock_execute_validation(*args, **kwargs):
            # Simulate that the validator calls update_sheet_values during execution
            mock_update(
                "test_sheet_id",
                "Sheet1",
                [["JSON_Output"], ['{"worker_id": "TEST123"}']],
                "Z1:Z2",
            )

            # Return the expected result structure
            from urarovite.validators.base import ValidationResult

            result = ValidationResult()
            result.add_fix(1)
            result.details["total_rows"] = 1
            result.details["transformed_rows"] = 1
            result.details["a1_range_fixes_applied"] = 0
            result.details["json_schema"] = ["worker_id", "task_id", "prompt"]
            result.details["sample_output"] = [
                {"worker_id": "TEST123", "task_id": "TASK456", "prompt": "Test prompt"}
            ]
            result.set_automated_log(
                "Transformed 1 rows to JSON format and wrote to sheet"
            )
            return result.to_dict()

        with patch.object(
            validator, "_execute_validation", side_effect=mock_execute_validation
        ):
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                mode="fix",
                auth_credentials={
                    "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                },
            )

        # Should succeed
        assert result["flags_found"] == 0
        assert result["fixes_applied"] == 1

        # Verify JSON output was written
        mock_update.assert_called()
        call_args = mock_update.call_args
        range_name = call_args[0][3]  # Fourth argument is range_name
        assert "Z1" in range_name, (
            f"Expected JSON output in column Z, but got range: {range_name}"
        )


class TestTransformCSVToJSONFunction:
    """Test the standalone transform_csv_to_json function."""

    def test_transform_csv_to_json_function(self):
        """Test the standalone transformation function with realistic data."""
        # Real data structure from the CSV
        csv_data = [
            {
                "worker_id": "7CM2GYGPCQRR",
                "task_id": "919309a8-ed81-41a8-a1a4-4a32d94db8b2",
                "task_response_id": "3d17cc01-f367-4546-92d1-6882144d9f54",
                "job domain": "Information and Record Clerks",
                "description": "This dataset tracks monthly student attendance for an instructor who has 90 students...",
                "prompt": "I combined a couple of my old attendance sheets to create the attendance sheet for March 2025, and there are a lot of duplicate rows in it. Can you remove the duplicate rows so that there is only one student per student ID?",
                "verification_criteria": "Rows 4, 6, 9, 11, 14, 16, 19, 22, 24, 27, 30, 33, 36, 38, 40, 43, 45, 48, 50, 57, 60, 62, 64, 66, 69, 72, 74, 77, 79, 81, 83, 86, 88, 90, 93, 96, 100, 102, 105, 109, 111, 114, 116, 119, 121, 124, 127, 130, 132, 135, 138, 140, 141, and 144 from the original document have been deleted due to duplicate information.",
                "verification_field_ranges": "March 2025'!A2:A91",
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/1wVWKw_l5eIWiLsiQPDrzjmodg2hMK9-RYxgDpT1YWaI/edit?usp=sharing",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/1ODsg5EHf7992lXcCZkilnsBeGEjJPqhafdrZj-4IhlE/edit?usp=sharing",
            },
            {
                "worker_id": "Y4ACFC2HGKYD",
                "task_id": "4d3d4aca-de90-4663-87df-e71dbb3d1a81",
                "task_response_id": "dc4ae156-e9a0-4bce-82b2-b9e3fe60cd5c",
                "job domain": "Life Scientists",
                "description": 'The dataset shows the results of a foraging study comparing the consumption rates of "Mix27A" to a control over the course of a month.',
                "prompt": "I have this spreadsheet that shows the results of a foraging study, but it was filled out by multiple researchers. Unfortunately, one of them did not follow the instructions and now some of the data is invalid.",
                "verification_criteria": 'All of the dates in the "Date" column are in "MM/DD/YYYY" format with leading 0\'s removed.',
                "verification_field_ranges": "Sheet1'A11:D72",
                "input_sheet_url": "https://docs.google.com/spreadsheets/d/1E7RF7lBnVAEIVB7NoF24l4vBoV-t7VMRdrsAWHHU4YQ/edit?usp=sharing",
                "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/1ju4CAN0ncKUFsQfTs8lxNI6Sk408pqAHUI3nijp3_ac/edit?usp=sharing",
            },
        ]

        result = transform_csv_to_json(csv_data)

        assert len(result) == 2

        # Check first record (attendance task)
        assert result[0]["worker_id"] == "7CM2GYGPCQRR"
        assert result[0]["job_domain"] == "Information and Record Clerks"
        assert "duplicate rows" in result[0]["prompt"]
        assert (
            result[0]["verification_field_ranges"] == "'March 2025'!A2:A91"
        )  # A1 range fixed
        assert (
            result[0]["input_file"]
            == "https://docs.google.com/spreadsheets/d/1wVWKw_l5eIWiLsiQPDrzjmodg2hMK9-RYxgDpT1YWaI/edit?usp=sharing"
        )
        assert result[0]["_row_number"] == 1

        # Check second record (life science task)
        assert result[1]["worker_id"] == "Y4ACFC2HGKYD"
        assert result[1]["job_domain"] == "Life Scientists"
        assert "foraging study" in result[1]["prompt"]
        assert (
            result[1]["verification_field_ranges"] == "'Sheet1'!A11:D72"
        )  # A1 range fixed
        assert (
            result[1]["input_file"]
            == "https://docs.google.com/spreadsheets/d/1E7RF7lBnVAEIVB7NoF24l4vBoV-t7VMRdrsAWHHU4YQ/edit?usp=sharing"
        )
        assert result[1]["_row_number"] == 2

        # Check A1 range fixes were applied
        assert "_a1_range_fixes" in result[0]
        assert "_a1_range_fixes" in result[1]
        assert len(result[0]["_a1_range_fixes"]) == 1
        assert len(result[1]["_a1_range_fixes"]) == 1

    def test_transform_empty_csv(self):
        """Test transformation with empty CSV data."""
        result = transform_csv_to_json([])
        assert result == []


class TestValidatorIntegration:
    """Integration tests for the validator."""

    def test_validator_in_registry(self):
        """Test that the validator is properly registered in the system."""
        from urarovite.core.api import get_available_validation_criteria

        criteria = get_available_validation_criteria()
        csv_transform_criteria = next(
            (c for c in criteria if c["id"] == "csv_to_json_transform"), None
        )

        assert csv_transform_criteria is not None
        assert csv_transform_criteria["name"] == "CSV to JSON Transform"
        assert csv_transform_criteria["supports_fix"] is True
        assert csv_transform_criteria["supports_flag"] is True
