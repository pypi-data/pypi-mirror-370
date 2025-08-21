from unittest.mock import patch, MagicMock

from urarovite.validators import get_validator
from urarovite.validators.hidden_unicode import HiddenUnicodeValidator, run
from urarovite.core.spreadsheet import SpreadsheetMetadata


def test_validator_registration():
    """
    Test that the validator is registered and has the correct name.
    """
    validator = get_validator("hidden_unicode")
    assert isinstance(validator, HiddenUnicodeValidator)
    assert validator.id == "hidden_unicode"
    assert "Hidden Unicode".lower() in validator.name.lower()


def test_detect_hidden_unicode_cells():
    """
    Test that the validator detects hidden unicode cells.
    """
    validator = HiddenUnicodeValidator()
    data = [
        ["H1", "H2"],
        ["A\u00a0B", "C"],
        ["X", "Y\u2009Z\u200b"],
    ]
    sheet_url = "https://docs.google.com/spreadsheets/d/sheet123/edit"

    # Mock the spreadsheet interface
    mock_spreadsheet = MagicMock()
    mock_metadata = SpreadsheetMetadata(
        spreadsheet_id="test_id",
        title="Test Sheet",
        sheet_names=["Sheet1"],
        spreadsheet_type="google_sheets",
    )
    mock_spreadsheet.get_metadata.return_value = mock_metadata
    # Create a mock SheetData object with the values attribute
    mock_sheet_data = MagicMock()
    mock_sheet_data.values = data
    mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

    with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
        result = validator.validate(
            spreadsheet_source=sheet_url,
            mode="flag",
            auth_credentials={"encoded_credentials": "fake_creds"},
        )

    assert result["flags_found"] == 2
    assert "flags" in result["details"]
    assert len(result["details"]["flags"]) == 2

    # Verify details of the logged flags
    issue_map = {
        (issue["sheet"], issue["cell"]): issue for issue in result["details"]["flags"]
    }

    assert ("Sheet1", "Sheet1!A2") in issue_map
    assert "NO-BREAK SPACE" in issue_map[("Sheet1", "Sheet1!A2")]["message"]

    assert ("Sheet1", "Sheet1!B3") in issue_map
    assert "THIN SPACE" in issue_map[("Sheet1", "Sheet1!B3")]["message"]
    assert "ZERO WIDTH SPACE" in issue_map[("Sheet1", "Sheet1!B3")]["message"]

    assert "Found hidden Unicode in 2 cells." in result["automated_log"]


def test_no_flags_found():
    """
    Test that the validator does not find any flags in a sheet with no hidden unicode.
    """
    validator = HiddenUnicodeValidator()
    data = [["A", "B"], ["C", "D"]]
    sheet_url = "https://docs.google.com/spreadsheets/d/sheet123/edit"

    # Mock the spreadsheet interface
    mock_spreadsheet = MagicMock()
    mock_metadata = SpreadsheetMetadata(
        spreadsheet_id="test_id",
        title="Test Sheet",
        sheet_names=["Sheet1"],
        spreadsheet_type="google_sheets",
    )
    mock_spreadsheet.get_metadata.return_value = mock_metadata
    # Create a mock SheetData object with the values attribute
    mock_sheet_data = MagicMock()
    mock_sheet_data.values = data
    mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

    with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
        result = validator.validate(
            spreadsheet_source=sheet_url,
            mode="flag",
            auth_credentials={"encoded_credentials": "fake_creds"},
        )

    assert result["flags_found"] == 0
    assert result["automated_log"] == "No flags found"
    assert "flags" not in result["details"]


def test_empty_sheet():
    """
    Test that the validator does not find any flags in an empty sheet.
    """
    validator = HiddenUnicodeValidator()
    sheet_url = "https://docs.google.com/spreadsheets/d/sheet123/edit"

    # Mock the spreadsheet interface
    mock_spreadsheet = MagicMock()
    mock_metadata = SpreadsheetMetadata(
        spreadsheet_id="test_id",
        title="Test Sheet",
        sheet_names=["Sheet1"],
        spreadsheet_type="google_sheets",
    )
    mock_spreadsheet.get_metadata.return_value = mock_metadata
    mock_spreadsheet.get_sheet_data.return_value = []

    with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
        result = validator.validate(
            spreadsheet_source=sheet_url,
            mode="flag",
            auth_credentials={"encoded_credentials": "fake_creds"},
        )

    assert result["flags_found"] == 0
    assert result["automated_log"] == "No flags found"


def test_invalid_url():
    """
    Test that the validator handles invalid sheet URLs properly.
    """
    validator = HiddenUnicodeValidator()
    sheet_url = "not-a-url"

    # Mock _get_spreadsheet to raise an exception for invalid URL
    with patch.object(
        validator, "_get_spreadsheet", side_effect=Exception("Invalid URL")
    ):
        result = validator.validate(
            spreadsheet_source=sheet_url,
            mode="flag",
            auth_credentials={"encoded_credentials": "fake_creds"},
        )

    assert result["flags_found"] == 0
    assert any("Unexpected error" in e for e in result["errors"])


def test_run_function_delegates():
    """
    Test that the run function delegates to the validator.
    """
    with patch(
        "urarovite.validators.hidden_unicode.HiddenUnicodeValidator.validate",
        return_value={"flags_found": 0, "details": {}},
    ) as mock_validate:
        res = run("https://docs.google.com/spreadsheets/d/sheet123/edit", mode="flag")
        assert res["flags_found"] == 0
        assert mock_validate.called
