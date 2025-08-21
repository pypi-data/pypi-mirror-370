from unittest.mock import MagicMock, patch

from urarovite.validators import get_validator
from urarovite.validators.volatile_formulas import VolatileFormulasValidator, run


def _mock_sheets_service_with_workbook(workbook):
    service = MagicMock()
    service.spreadsheets.return_value.get.return_value.execute.return_value = workbook
    return service


class TestVolatileFormulasValidator:
    """Test suite for the VolatileFormulasValidator."""

    def test_validator_registration(self):
        """T
        Test that the validator is properly registered.
        """
        validator = get_validator("volatile_formulas")
        assert isinstance(validator, VolatileFormulasValidator)
        assert validator.id == "volatile_formulas"
        assert "Volatile" in validator.name

    @patch("urarovite.utils.generic_spreadsheet.get_spreadsheet_formulas")
    def test_detects_all_issue_types(self, mock_get_formulas):
        """
        Test that the validator detects all issue types in flag mode.
        """
        # Mock formulas data in the new format
        mock_get_formulas.return_value = {
            "Sheet1": {
                "A1": "=NOW()",
                "B1": "=TODAY()",
                "C1": "=RAND()",
                "D1": "=RANDBETWEEN(1,10)",
                "E1": "=OFFSET(A1,1,1)",
                "F1": '=INDIRECT("A1")',
                "G1": "='https://docs.google.com/spreadsheets/d/external/edit#gid=0'!A1",
                "H1": "=Sheet2!A1",
            }
        }

        workbook = {
            "sheets": [
                {
                    "properties": {"title": "Sheet1"},
                    "data": [
                        {
                            "rowData": [
                                {
                                    "values": [
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": "=NOW()"
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": "=today()"
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": "=Rand()"
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": "=randbetween(1,10)"
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": "=OFFSET(A1,1,1)"
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": '=INDIRECT("A1")'
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": '=IMPORTRANGE("key", "Sheet!A1")'
                                            }
                                        },
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": "='Other Tab'!B2"
                                            }
                                        },
                                        {"userEnteredValue": {"formulaValue": "=A1+1"}},
                                    ]
                                }
                            ]
                        }
                    ],
                }
            ]
        }
        service = _mock_sheets_service_with_workbook(workbook)
        url = "https://docs.google.com/spreadsheets/d/TEST_ID/edit"

        validator = VolatileFormulasValidator()

        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            with patch.object(
                validator, "_create_sheets_service", return_value=service
            ):
                with patch(
                    "urarovite.validators.volatile_formulas.fetch_workbook_with_formulas",
                    return_value=workbook,
                ):
                    mock_spreadsheet = MagicMock()
                    mock_get_spreadsheet.return_value = mock_spreadsheet

                    result = validator.validate(
                        spreadsheet_source=url,
                        mode="flag",
                        auth_credentials={"encoded_credentials": "fake_creds"},
                    )

        assert result["flags_found"] == 9
        flags = result["details"].get("flags", [])
        types = [i["type"] for i in flags]
        functions = [
            i.get("function") for i in flags if i["type"] == "volatile_function"
        ]
        assert "volatile_function" in types
        assert "external_reference" in types
        assert "cross_tab_reference" in types
        assert set(
            ["NOW", "TODAY", "RAND", "RANDBETWEEN", "OFFSET", "INDIRECT"]
        ).issubset(set(functions))
        assert (
            result["automated_log"].lower().startswith("flagged ")
            or "Flagged" in result["automated_log"]
        )

    @patch("urarovite.utils.generic_spreadsheet.get_spreadsheet_formulas")
    def test_no_flags(self, mock_get_formulas):
        """
        Test that the validator returns no flags when there are no volatile functions.
        """
        # Mock empty formulas data
        mock_get_formulas.return_value = {}
        workbook = {
            "sheets": [
                {
                    "properties": {"title": "Sheet1"},
                    "data": [
                        {
                            "rowData": [
                                {
                                    "values": [
                                        {"userEnteredValue": {"formulaValue": "=A1+1"}},
                                        {
                                            "userEnteredValue": {
                                                "formulaValue": "=SUM(A1:A3)"
                                            }
                                        },
                                    ]
                                }
                            ]
                        }
                    ],
                }
            ]
        }
        service = _mock_sheets_service_with_workbook(workbook)
        url = "https://docs.google.com/spreadsheets/d/TEST_ID/edit"
        validator = VolatileFormulasValidator()

        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            with patch.object(
                validator, "_create_sheets_service", return_value=service
            ):
                with patch(
                    "urarovite.validators.volatile_formulas.fetch_workbook_with_formulas",
                    return_value=workbook,
                ):
                    mock_spreadsheet = MagicMock()
                    mock_get_spreadsheet.return_value = mock_spreadsheet

                    result = validator.validate(
                        spreadsheet_source=url,
                        mode="flag",
                        auth_credentials={"encoded_credentials": "fake_creds"},
                    )
        assert result["flags_found"] == 0
        assert result["automated_log"] == "No flags found"

    @patch("urarovite.utils.generic_spreadsheet.get_spreadsheet_formulas")
    def test_missing_sheet_url(self, mock_get_formulas):
        """
        Test that the validator returns no flags when the sheet URL is missing.
        """
        # Mock the error that would occur with an invalid source
        from urarovite.core.exceptions import ValidationError

        mock_get_formulas.side_effect = ValidationError("Unsupported file format: ")
        validator = VolatileFormulasValidator()

        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            mock_spreadsheet = MagicMock()
            mock_get_spreadsheet.return_value = mock_spreadsheet

            result = validator.validate(
                spreadsheet_source="",
                mode="flag",
                auth_credentials={"encoded_credentials": "fake_creds"},
            )

        assert result["flags_found"] == 0
        assert "Unsupported file format" in result["errors"][0]
        assert "Failed to fetch workbook formulas" in result["automated_log"]

    def test_unexpected_error_handling(self):
        """
        Test that the validator returns no flags when there is an unexpected error.
        """
        service = MagicMock()
        service.spreadsheets.return_value.get.return_value.execute.side_effect = (
            Exception("boom")
        )
        url = "https://docs.google.com/spreadsheets/d/TEST_ID/edit"
        validator = VolatileFormulasValidator()

        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            with patch.object(
                validator, "_create_sheets_service", return_value=service
            ):
                with patch(
                    "urarovite.validators.volatile_formulas.fetch_workbook_with_formulas",
                    side_effect=Exception("boom"),
                ):
                    mock_spreadsheet = MagicMock()
                    mock_get_spreadsheet.return_value = mock_spreadsheet

                    result = validator.validate(
                        spreadsheet_source=url,
                        mode="flag",
                        auth_credentials={"encoded_credentials": "fake_creds"},
                    )
        assert result["flags_found"] == 0
        # The exception should be caught and handled as an error
        assert len(result["errors"]) > 0
        assert any("boom" in str(e) for e in result["errors"])
        assert "boom" in result["automated_log"]
