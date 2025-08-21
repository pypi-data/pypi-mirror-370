"""Platform neutralizer validator for removing platform-specific language."""

import re
from typing import Any, Dict, List, Tuple, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface


class PlatformNeutralizerValidator(BaseValidator):
    """Validator to detect and neutralize platform-specific mentions like Excel/Google Sheets."""

    def __init__(self):
        """Initialize the platform neutralizer validator."""
        super().__init__(
            validator_id="platform_neutralizer",
            name="Neutralize Platform-Specific Language",
            description="Detects 'Excel'/'Google Sheets' mentions in prompts and replaces with neutral phrasing.",
        )

    # Platform-specific terms and their neutral replacements (context-aware)
    PLATFORM_REPLACEMENTS = {
        # Excel variations with context
        r"\bin\s+Excel\s+(?:file|document|workbook|spreadsheet)\b": "in a spreadsheet",
        r"\bthe\s+Excel\s+(?:file|document|workbook|spreadsheet)\b": "the spreadsheet",
        r"\ban?\s+Excel\s+(?:file|document|workbook|spreadsheet)\b": "a spreadsheet",
        r"\bExcel\s+(?:file|document|workbook|spreadsheet)\b": "spreadsheet",
        r"\bExcel\s+(?:sheet|worksheet)\b": "worksheet",
        r"\ban?\s+Excel\b": "a spreadsheet",
        r"\bthe\s+Excel\b": "the spreadsheet",
        r"\buse\s+Excel\b": "use a spreadsheet",
        r"\bExcel\b": "spreadsheet",
        # Google Sheets variations with context
        r"\bin\s+Google\s+Sheets?\b": "in a spreadsheet",
        r"\bthe\s+Google\s+Sheets?\b": "the spreadsheet",
        r"\ban?\s+Google\s+Sheets?\b": "a spreadsheet",
        r"\bGoogle\s+Sheets?\b": "spreadsheet",
        r"\bin\s+Google\s+(?:spreadsheet|workbook)\b": "in a spreadsheet",
        r"\bthe\s+Google\s+(?:spreadsheet|workbook)\b": "the spreadsheet",
        r"\bGoogle\s+(?:spreadsheet|workbook)\b": "spreadsheet",
        # File/document combinations
        r"\bGoogle\s+(?:Sheets?\s+)?(?:file|document)\b": "spreadsheet",
        r"\bExcel\s+(?:chart|graph)\b": "chart",
        r"\bGoogle\s+(?:Sheets?\s+)?(?:chart|graph)\b": "chart",
    }

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str = "flag",
        auth_credentials: Dict[str, Any] = None,
        target_column: str = "prompt",
        **kwargs,
    ) -> Dict[str, Any]:
        """Validate and optionally fix platform-specific language in prompts.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "flag" or "fix"
            auth_credentials: Authentication credentials (required for Google Sheets)
            target_column: Column to check for platform mentions (default: "prompt")

        Returns:
            Dictionary containing validation results
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Get all data from the sheet
            all_data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not all_data:
                result.details["message"] = "No data found to validate"
                result.set_automated_log("No data found to validate")
                return

            headers = all_data[0]
            data_rows = all_data[1:]

            # Find the target column index
            try:
                target_col_index = headers.index(target_column)
            except ValueError:
                # Column not found - skip validation gracefully
                result.set_automated_log(
                    f"Column '{target_column}' not found in sheet - skipping platform neutralization"
                )
                return

            fixes_to_apply = []

            # Check each row for platform mentions
            for row_index, row in enumerate(
                data_rows, start=2
            ):  # Start at 2 for sheet row numbering
                if target_col_index >= len(row):
                    continue  # Skip rows without enough columns

                prompt_text = str(row[target_col_index]).strip()
                if not prompt_text:
                    continue

                # Find platform mentions
                mentions = self._find_platform_mentions(prompt_text)

                if mentions:
                    cell_ref = self._generate_cell_reference(
                        row_index - 2, target_col_index, sheet_name
                    )
                    mentions_str = ", ".join(f'"{m["original"]}"' for m in mentions)

                    if mode == "flag":
                        result.add_detailed_issue(
                            sheet_name=sheet_name,
                            cell=cell_ref,
                            message=f"Found platform-specific language: {mentions_str}",
                            value=prompt_text,
                        )
                    else:  # fix mode
                        cleaned_text, editor_note = self._neutralize_platform_language(
                            prompt_text, mentions
                        )

                        # Prepare fix
                        fixes_to_apply.append(
                            {
                                "row": row_index
                                - 2,  # Convert to 0-based for data_rows
                                "col": target_col_index,
                                "new_value": cleaned_text,
                            }
                        )

                        result.add_detailed_fix(
                            sheet_name=sheet_name,
                            cell=cell_ref,
                            message=f"Neutralized platform-specific language: {mentions_str}",
                            old_value=prompt_text,
                            new_value=cleaned_text,
                        )

            # Apply fixes if in fix mode
            if mode == "fix" and fixes_to_apply:
                # Apply fixes to the data_rows first
                for fix in fixes_to_apply:
                    row_idx = fix["row"]
                    col_idx = fix["col"]
                    new_value = fix["new_value"]

                    # Ensure row has enough columns
                    if len(data_rows[row_idx]) <= col_idx:
                        data_rows[row_idx].extend(
                            [""] * (col_idx + 1 - len(data_rows[row_idx]))
                        )

                    data_rows[row_idx][col_idx] = new_value

                # Update the sheet with cleaned data
                updated_data = [headers] + data_rows
                self._update_sheet_data(spreadsheet, sheet_name, updated_data)
                spreadsheet.save()

            # Set a summary log message
            if result.fixes_applied > 0:
                result.set_automated_log(
                    f"Neutralized platform language in {result.fixes_applied} prompts"
                )
            elif result.flags_found > 0:
                result.set_automated_log(
                    f"Found {result.flags_found} prompts with platform-specific language"
                )
            else:
                result.set_automated_log("No platform-specific language found")

        return self._execute_validation(
            validation_logic,
            spreadsheet_source,
            auth_credentials,
            target_column=target_column,
            **kwargs,
        )

    def _find_platform_mentions(self, text: str) -> List[Dict[str, str]]:
        """Find platform-specific mentions in text.

        Args:
            text: Text to search

        Returns:
            List of dictionaries with mention details
        """
        mentions = []

        for pattern, replacement in self.PLATFORM_REPLACEMENTS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mentions.append(
                    {
                        "original": match.group(),
                        "replacement": replacement,
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                        "pattern": pattern,
                    }
                )

        # Sort by position and remove overlaps
        mentions.sort(key=lambda x: x["start_pos"])

        # Remove overlapping mentions (keep the first/longest)
        filtered_mentions = []
        for mention in mentions:
            overlaps = False
            for existing in filtered_mentions:
                if (
                    mention["start_pos"] < existing["end_pos"]
                    and mention["end_pos"] > existing["start_pos"]
                ):
                    overlaps = True
                    break

            if not overlaps:
                filtered_mentions.append(mention)

        return filtered_mentions

    def _neutralize_platform_language(
        self, text: str, mentions: List[Dict[str, str]]
    ) -> Tuple[str, str]:
        """Replace platform-specific language with neutral terms.

        Args:
            text: Original text
            mentions: List of mentions to replace

        Returns:
            Tuple of (neutralized_text, editor_note)
        """
        if not mentions:
            return text, ""

        # Work backwards to preserve positions
        cleaned_text = text
        replaced_terms = []

        for mention in reversed(mentions):
            start_pos = mention["start_pos"]
            end_pos = mention["end_pos"]
            replacement = mention["replacement"]
            original = mention["original"]

            # Replace the mention
            cleaned_text = (
                cleaned_text[:start_pos] + replacement + cleaned_text[end_pos:]
            )
            replaced_terms.append(f"'{original}' → '{replacement}'")

        # Generate editor note
        if len(replaced_terms) == 1:
            editor_note = (
                f"[Editor: Neutralized platform language: {replaced_terms[0]}]"
            )
        else:
            editor_note = f"[Editor: Neutralized {len(replaced_terms)} platform terms: {', '.join(replaced_terms)}]"

        # Add editor note to the text
        final_text = f"{cleaned_text}\n\n{editor_note}"

        return final_text, editor_note
