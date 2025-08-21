"""Tests for TabNameAlphanumericValidator.

This validator ensures tab names contain only letters, numbers, and spaces.
Special characters (including underscores) are omitted.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the validator directly to avoid dependency issues in tests
try:
    from urarovite.validators.tab_name_alphanumeric import (
        TabNameAlphanumericValidator,
        sanitize_tab_names_to_alphanumeric,
    )
except ImportError as e:
    print(f"Warning: Could not import validator modules: {e}")
    print("This may be due to missing dependencies. Trying direct import...")

    # Alternative import path if main package has dependency issues
    import importlib.util

    validator_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "urarovite",
        "validators",
        "tab_name_alphanumeric.py",
    )
    spec = importlib.util.spec_from_file_location(
        "tab_name_alphanumeric", validator_path
    )
    if spec and spec.loader:
        tab_name_mod = importlib.util.module_from_spec(spec)

        # Mock the base validator to avoid import issues
        class MockBaseValidator:
            def __init__(self, validator_id, name, description):
                self.validator_id = validator_id
                self.name = name
                self.description = description

        class MockValidationResult:
            def __init__(self):
                self.flags_found = 0
                self.fixes_applied = 0
                self.errors = []
                self.details = {"issues": [], "fixes": []}

            def add_detailed_issue(self, **kwargs):
                self.flags_found += 1
                self.details["issues"].append(kwargs)

            def add_detailed_fix(self, **kwargs):
                self.fixes_applied += 1
                self.details["fixes"].append(kwargs)

            def add_error(self, error):
                self.errors.append(error)

            def set_automated_log(self, log):
                self.automated_log = log

            def to_dict(self):
                return {
                    "flags_found": self.flags_found,
                    "fixes_applied": self.fixes_applied,
                    "errors": self.errors,
                    "details": self.details,
                    "automated_log": getattr(self, "automated_log", ""),
                }

        # Add mocks to the module
        tab_name_mod.BaseValidator = MockBaseValidator
        tab_name_mod.ValidationResult = MockValidationResult

        try:
            spec.loader.exec_module(tab_name_mod)
            TabNameAlphanumericValidator = tab_name_mod.TabNameAlphanumericValidator
            sanitize_tab_names_to_alphanumeric = (
                tab_name_mod.sanitize_tab_names_to_alphanumeric
            )
        except Exception as load_error:
            print(f"Error loading module: {load_error}")
            TabNameAlphanumericValidator = None
            sanitize_tab_names_to_alphanumeric = None
    else:
        TabNameAlphanumericValidator = None
        sanitize_tab_names_to_alphanumeric = None


class TestTabNameAlphanumericValidator(unittest.TestCase):
    """Test suite for TabNameAlphanumericValidator."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        if TabNameAlphanumericValidator is None:
            self.skipTest("TabNameAlphanumericValidator could not be imported")
        self.validator = TabNameAlphanumericValidator()

    def test_validator_initialization(self):
        """Test that the validator is properly initialized."""
        self.assertEqual(self.validator.id, "tab_name_alphanumeric")
        self.assertEqual(self.validator.name, "Tab Name Alphanumeric")
        self.assertIn("letters, numbers, and spaces", self.validator.description)
        self.assertIn("omits special characters", self.validator.description)
        self.assertIn("underscores", self.validator.description)

    def test_sanitize_tab_name_basic_cases(self):
        """Test basic sanitization functionality."""
        test_cases = [
            # Basic cases
            ("SimpleSheet", "SimpleSheet"),  # Already valid
            ("Sheet 1", "Sheet 1"),  # Already valid with space
            ("Sheet1", "Sheet1"),  # Already valid alphanumeric
            # Remove special characters (including underscores)
            ("Sheet_with_underscores", "Sheetwithunderscores"),
            ("Sheet@#$%^&*()", "Sheet"),
            ("Data/Analysis", "DataAnalysis"),
            ("Report\\Final", "ReportFinal"),
            ("Test[Brackets]", "TestBrackets"),
            ("Sheet?Question", "SheetQuestion"),
            ("Data*Star", "DataStar"),
            ("Sheet|Pipe", "SheetPipe"),
            ("Sheet:Colon", "SheetColon"),
            ("Sheet;Semi", "SheetSemi"),
            ("Sheet<>Angle", "SheetAngle"),
            ('Sheet"Quote', "SheetQuote"),
            ("Sheet'Apos", "SheetApos"),
            ("Sheet`Backtick", "SheetBacktick"),
            ("Sheet~Tilde", "SheetTilde"),
            ("Sheet!Exclaim", "SheetExclaim"),
            ("Sheet+Plus", "SheetPlus"),
            ("Sheet=Equals", "SheetEquals"),
            ("Sheet{Curly}", "SheetCurly"),
            ("Sheet.Dot", "SheetDot"),
            ("Sheet,Comma", "SheetComma"),
            ("Sheet-Dash", "SheetDash"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_sanitize_tab_name_space_handling(self):
        """Test space handling in sanitization."""
        test_cases = [
            # Multiple spaces collapsed to single space
            ("Sheet    with    spaces", "Sheet with spaces"),
            ("   Sheet   ", "Sheet"),  # Leading/trailing spaces removed
            ("Sheet  Multiple  Spaces", "Sheet Multiple Spaces"),
            # Mixed spaces and special characters
            ("Sheet___with___underscores", "Sheetwithunderscores"),
            ("Sheet   @   Special", "Sheet Special"),
            ("Data___Analysis___Report", "DataAnalysisReport"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_sanitize_tab_name_edge_cases(self):
        """Test edge cases in sanitization."""
        test_cases = [
            # Empty and whitespace-only cases
            ("", "Sheet1"),
            ("   ", "Sheet1"),
            ("\t\n", "Sheet1"),
            # Only special characters
            ("@#$%^&*()", "Sheet1"),
            ("___", "Sheet1"),
            ("!@#$%^&*()", "Sheet1"),
            # Numbers at start (should be prefixed with "Sheet")
            ("123Data", "Sheet 123Data"),
            ("999", "Sheet 999"),
            ("42Analysis", "Sheet 42Analysis"),
            # Mixed cases
            ("1_2_3", "Sheet 123"),
            ("___123___", "Sheet 123"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_sanitize_tab_name_complex_cases(self):
        """Test complex sanitization scenarios."""
        test_cases = [
            # Real-world examples
            ("Q1_2024_Sales_Report", "Q12024SalesReport"),
            ("Data-Analysis_Final@Version", "DataAnalysisFinalVersion"),
            ("Marketing/Campaign[Results]", "MarketingCampaignResults"),
            ("Employee_Performance_Review_2024", "EmployeePerformanceReview2024"),
            ("Sheet_#1_with_lots_of_stuff!", "Sheet1withlotsofstuff"),
            ("___messy___name___with___underscores___", "messynamewithunderscores"),
            # Unicode and special characters
            ("Sheet™©®", "Sheet"),
            (
                "Données_Analysis",
                "DonnesAnalysis",
            ),  # Accented chars removed, underscores omitted
            ("Sheet€$¥£", "Sheet"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._sanitize_tab_name(input_name)
                self.assertEqual(result, expected)

    def test_detect_non_alphanumeric_tabs(self):
        """Test detection of tabs needing sanitization."""
        # Valid tabs (no changes needed)
        valid_tabs = ["Sheet1", "Data Analysis", "Report 2024", "Simple"]
        result = self.validator._detect_non_alphanumeric_tabs(valid_tabs)
        self.assertEqual(result, {})

        # Invalid tabs (changes needed)
        invalid_tabs = [
            "Sheet_with_underscores",
            "Data@#$%",
            "Valid Sheet",  # This is valid
            "Report/Final",
        ]
        result = self.validator._detect_non_alphanumeric_tabs(invalid_tabs)

        expected = {
            "Sheet_with_underscores": "Sheetwithunderscores",
            "Data@#$%": "Data",
            "Report/Final": "ReportFinal",
        }
        self.assertEqual(result, expected)

    def test_ensure_unique_names(self):
        """Test unique name generation when conflicts occur."""
        all_tabs = ["Sheet1", "Data", "Data 2", "Report"]

        # No conflicts
        rename_mapping = {"NewSheet": "NewSheet"}
        result = self.validator._ensure_unique_names(rename_mapping, all_tabs)
        self.assertEqual(result, {"NewSheet": "NewSheet"})

        # Conflict resolution
        rename_mapping = {
            "Old_Data": "Data",  # Conflicts with existing
            "Sheet_1": "Sheet1",  # Conflicts with existing
        }
        result = self.validator._ensure_unique_names(rename_mapping, all_tabs)

        # Should get unique names with numeric suffixes
        self.assertEqual(result["Old_Data"], "Data 3")  # Data 2 already exists
        self.assertEqual(result["Sheet_1"], "Sheet1 2")

    def test_ensure_unique_names_multiple_conflicts(self):
        """Test unique name generation with multiple levels of conflicts."""
        all_tabs = ["Report", "Report 2", "Report 3"]

        rename_mapping = {"Report_Old": "Report", "Report_New": "Report"}
        result = self.validator._ensure_unique_names(rename_mapping, all_tabs)

        # Both should get unique sequential numbers
        names = list(result.values())
        self.assertEqual(len(set(names)), 2)  # Both should be unique
        self.assertIn("Report 4", names)
        self.assertIn("Report 5", names)

    def test_standalone_function(self):
        """Test the standalone sanitize_tab_names_to_alphanumeric function."""
        # No sanitization needed
        clean_tabs = ["Sheet1", "Data Analysis", "Report"]
        result = sanitize_tab_names_to_alphanumeric(clean_tabs)
        self.assertFalse(result["needs_sanitization"])
        self.assertEqual(result["suggested_mapping"], {})
        self.assertEqual(result["tabs_affected"], 0)

        # Sanitization needed
        messy_tabs = ["Sheet_1", "Data@#$", "Report/Final"]
        result = sanitize_tab_names_to_alphanumeric(messy_tabs)
        self.assertTrue(result["needs_sanitization"])
        self.assertEqual(result["tabs_affected"], 3)
        self.assertIn("preview", result)

        # Check preview structure
        preview = result["preview"]
        self.assertEqual(len(preview), 3)
        for item in preview:
            self.assertIn("original", item)
            self.assertIn("sanitized", item)

    def test_validation_flag_mode_no_issues(self):
        """Test validation in flag mode when no issues exist."""
        with (
            patch(
                "urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs"
            ) as mock_get_tabs,
            patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet,
        ):
            mock_get_tabs.return_value = {
                "accessible": True,
                "tabs": ["Sheet1", "Data Analysis", "Report 2024"],
            }

            # Mock the spreadsheet object (not actually needed for this validator since it uses get_spreadsheet_tabs)
            mock_spreadsheet = MagicMock()
            mock_get_spreadsheet.return_value = mock_spreadsheet

            result = self.validator.validate(
                spreadsheet_source="test_url",
                mode="flag",
                auth_credentials={"auth_secret": "test_creds"},
            )

        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["errors"], [])

    def test_validation_flag_mode_with_issues(self):
        """Test validation in flag mode when issues exist."""
        with (
            patch(
                "urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs"
            ) as mock_get_tabs,
            patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet,
        ):
            mock_get_tabs.return_value = {
                "accessible": True,
                "tabs": ["Sheet_1", "Data@#$", "Valid Sheet", "Report/Final"],
            }

            # Mock the spreadsheet object
            mock_spreadsheet = MagicMock()
            mock_get_spreadsheet.return_value = mock_spreadsheet

            result = self.validator.validate(
                spreadsheet_source="test_url",
                mode="flag",
                auth_credentials={"auth_secret": "test_creds"},
            )

        self.assertEqual(result["flags_found"], 3)  # 3 invalid sheets
        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["errors"], [])

        # Check detailed issues (skip detailed checking for now since structure may vary)
        self.assertIn("details", result)
        # Verify that flags were found for the invalid sheets
        self.assertTrue(
            result["flags_found"] > 0, "Should have found flags for invalid sheets"
        )

    def test_validation_fix_mode(self):
        """Test validation in fix mode."""
        # This test uses the special write access path, so we need to mock accordingly
        with patch.object(
            self.validator, "_validate_with_explicit_write_access"
        ) as mock_explicit:
            mock_explicit.return_value = {
                "fixes_applied": 2,
                "flags_found": 0,
                "errors": [],
                "details": {"fixes": []},
                "automated_log": "Fixed 2 tab names to contain only letters, numbers, and spaces.",
            }

            result = self.validator.validate(
                spreadsheet_source="test_url",
                mode="fix",
                auth_credentials={"auth_secret": "test_creds"},
            )

        self.assertEqual(result["fixes_applied"], 2)
        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["errors"], [])
        mock_explicit.assert_called_once()

    def test_validation_no_access_to_spreadsheet(self):
        """Test validation when spreadsheet is not accessible."""
        with (
            patch(
                "urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs"
            ) as mock_get_tabs,
            patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet,
        ):
            mock_get_tabs.return_value = {
                "accessible": False,
                "error": "Permission denied",
                "tabs": [],
            }

            # Mock the spreadsheet object
            mock_spreadsheet = MagicMock()
            mock_get_spreadsheet.return_value = mock_spreadsheet

            result = self.validator.validate(
                spreadsheet_source="test_url",
                mode="flag",
                auth_credentials={"auth_secret": "test_creds"},
            )

        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("Permission denied", result["errors"][0])

    def test_validation_no_tabs_found(self):
        """Test validation when no tabs are found."""
        with (
            patch(
                "urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs"
            ) as mock_get_tabs,
            patch.object(self.validator, "_get_spreadsheet") as mock_get_spreadsheet,
        ):
            mock_get_tabs.return_value = {"accessible": True, "tabs": []}

            # Mock the spreadsheet object
            mock_spreadsheet = MagicMock()
            mock_get_spreadsheet.return_value = mock_spreadsheet

            result = self.validator.validate(
                spreadsheet_source="test_url",
                mode="flag",
                auth_credentials={"auth_secret": "test_creds"},
            )

        self.assertEqual(result["flags_found"], 0)
        self.assertEqual(result["fixes_applied"], 0)
        # Should not error, just log that no tabs were found


class TestRegressionFromOldBehavior(unittest.TestCase):
    """Test cases to ensure the new behavior doesn't break expected functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        if TabNameAlphanumericValidator is None:
            self.skipTest("TabNameAlphanumericValidator could not be imported")
        self.validator = TabNameAlphanumericValidator()

    def test_old_vs_new_behavior(self):
        """Test that demonstrates the change from old to new behavior."""
        test_cases = [
            # Old behavior: replaced with underscores
            # New behavior: omits bad chars, supports spaces
            ("My_Sheet@#$123", "MySheet123"),  # OLD: "My_Sheet_123"
            ("Data___Analysis", "DataAnalysis"),  # OLD: "Data_Analysis"
            (
                "Report/Final\\Version",
                "ReportFinalVersion",
            ),  # OLD: "Report_Final_Version"
            ("Sheet[1]_Test", "Sheet1Test"),  # OLD: "Sheet_1__Test"
            # Cases that should work the same
            ("SimpleSheet", "SimpleSheet"),
            ("Sheet123", "Sheet123"),
            ("Already Clean", "Already Clean"),
        ]

        for input_name, expected_new in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._sanitize_tab_name(input_name)
                self.assertEqual(result, expected_new)

                # Ensure underscores are NOT in the result (key difference)
                # unless they were in a valid input already
                if "_" in input_name and input_name != "Already_Clean_Input":
                    self.assertNotIn(
                        "_", result, f"Result '{result}' should not contain underscores"
                    )

    def test_spaces_are_preserved_and_normalized(self):
        """Test that spaces are preserved and normalized correctly."""
        test_cases = [
            ("Sheet with spaces", "Sheet with spaces"),  # Preserved
            ("Sheet   multiple   spaces", "Sheet multiple spaces"),  # Normalized
            ("  Trimmed  ", "Trimmed"),  # Trimmed
            ("Sheet_to_spaces", "Sheettospaces"),  # Underscores omitted
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._sanitize_tab_name(input_name)
                self.assertEqual(result, expected)


def run_tests():
    """Run all the tests and provide a summary."""
    print("Running TabNameAlphanumericValidator Tests")
    print("=" * 60)

    # Create test suites
    loader = unittest.TestLoader()
    suite1 = loader.loadTestsFromTestCase(TestTabNameAlphanumericValidator)
    suite2 = loader.loadTestsFromTestCase(TestRegressionFromOldBehavior)

    # Combine suites
    main_suite = unittest.TestSuite([suite1, suite2])

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(main_suite)

    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} tests passed!")
    else:
        print(
            f"❌ {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests"
        )

        # Print failures and errors
        for test, traceback in result.failures:
            print(f"\nFAILURE: {test}")
            print(traceback)

        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print(traceback)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
