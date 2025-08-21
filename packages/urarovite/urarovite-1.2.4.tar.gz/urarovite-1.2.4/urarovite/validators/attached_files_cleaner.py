"""Attached files cleaner validator for removing attachment mentions from prompts."""

import re
from typing import Any, Dict, List, Tuple, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetInterface


class AttachedFilesCleanerValidator(BaseValidator):
    """Validator to detect and clean attached file mentions while preserving grammar."""

    def __init__(self):
        """Initialize the attached files cleaner validator."""
        super().__init__(
            validator_id="attached_files_cleaner",
            name="Clean Attached Files Mentions",
            description="Detects 'attached file(s)' mentions in prompt text, removes them and adds editor note while preserving grammar.",
        )

    # File type patterns for matching various attachment types
    FILE_TYPES = r"(?:file|files|document|documents|doc|docs|spreadsheet|spreadsheets|sheet|sheets|workbook|report|reports?|csv|excel|pdf|docx|google\s+sheet|google\s+sheets)"

    # Grammar-preserving replacement rules (apply in order)
    ATTACHMENT_PATTERNS = [
        # Rule 1: Modifier on a noun (safest case) - drop "attached" only
        {
            "pattern": rf"\b(the|this|that|these|those)\s+attached\s+({FILE_TYPES})\b",
            "replacement": r"\1 \2",
            "description": 'Remove "attached" from determiner + attached + noun',
        },
        # Rule 2a: "Please find attached" - convert to proper instruction
        {
            "pattern": r"\bplease\s+find\s+attached\s+",
            "replacement": "Please review ",
            "description": 'Convert "Please find attached" to "Please review"',
        },
        # Rule 2b: Other "see attached" phrases
        {
            "pattern": r"\b(?:please\s+)?see\s+attached\b\.?",
            "replacement": "see the files",
            "description": 'Replace "see attached" phrases',
        },
        # Rule 3: Preposition + attached + noun - drop "attached"
        {
            "pattern": rf"\b(in|from|with|under|on)\s+the\s+attached\s+({FILE_TYPES})\b",
            "replacement": r"\1 the \2",
            "description": 'Remove "attached" from preposition phrases',
        },
        # Rule 4: Bare "the attached" (no noun) - replace with "the file(s)"
        {
            "pattern": r"\bthe\s+attached\b(?!\s+\w)",
            "replacement": "the files",
            "description": 'Replace bare "the attached" with "the files"',
        },
        # Rule 5: Lists and coordinated nouns - delete only "attached"
        {
            "pattern": rf"\battached\s+({FILE_TYPES})\s+and\s+({FILE_TYPES})\b",
            "replacement": r"\1 and \2",
            "description": 'Remove "attached" from coordinated file lists',
        },
        # Rule 6: Specific file-type mentions - remove "attached"
        {
            "pattern": rf"\battached\s+({FILE_TYPES})\b",
            "replacement": r"\1",
            "description": 'Remove "attached" from file type mentions',
        },
        # Rule 6b: Catch "attached" + multi-word file types (like "Google Sheet")
        {
            "pattern": r"\battached\s+((?:google\s+)?(?:sheet|sheets|spreadsheet|document|file|report))\b",
            "replacement": r"\1",
            "description": 'Remove "attached" from compound file type mentions',
        },
        # Rule 7: Parenthetical/label mentions
        {
            "pattern": r"\s*\(attached\)|\s*\[attached\]",
            "replacement": "",
            "description": "Remove parenthetical attachment mentions",
        },
        # Rule 8: Title/caption lines
        {
            "pattern": r"^attached:\s*|^\[attached\]\s*",
            "replacement": "",
            "description": "Remove attachment prefixes from titles",
        },
        # Rule 9: Deictic adverbs with "attached"
        {
            "pattern": r"\bsee\s+the\s+attached\s+(below|above)\b",
            "replacement": r"see \1",
            "description": 'Replace "see the attached below/above" with directional only',
        },
        {
            "pattern": r"\battached\s+(below|above)\b",
            "replacement": r"\1",
            "description": 'Replace "attached below/above" with directional only',
        },
        # Rule 10: "that I have attached" - past tense
        {
            "pattern": r"\bthat\s+I\s+have\s+attached\b",
            "replacement": "provided",
            "description": 'Replace "that I have attached" with "provided"',
        },
        # Rule 11: "data attached in" - no article
        {
            "pattern": r"\bdata\s+attached\s+in\s+",
            "replacement": "data in ",
            "description": 'Remove "attached" from "data attached in"',
        },
        # Rule 12: "Attached is" sentence starters
        {
            "pattern": r"^attached\s+is\s+",
            "replacement": "Here is ",
            "description": 'Replace "Attached is" with "Here is"',
        },
        # Rule 13: Complex compound names with "attached"
        {
            "pattern": r"\bthe\s+attached\s+([A-Z][A-Za-z\s]+(?:analysis|report|spreadsheet|document))\b",
            "replacement": r"the \1",
            "description": 'Remove "attached" from compound document names',
        },
        # Rule 14: General "attached" pattern (will be filtered by _should_skip_mention)
        {
            "pattern": r"\battached\s+to\s+",
            "replacement": "",
            "description": "Catch general attached patterns for filtering",
        },
    ]

    def _should_skip_mention(self, text: str, start: int, end: int) -> bool:
        """Check if an 'attached' mention should be skipped (not a file attachment)."""
        matched_text = text[start:end].lower()

        # Skip "attached to each other" and similar non-file uses
        if (
            "attached to each other"
            in text[max(0, start - 10) : min(len(text), end + 10)].lower()
        ):
            return True
        if "attached to" in matched_text and "other" in text[end : end + 20].lower():
            return True

        return False

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str = "flag",
        auth_credentials: Dict[str, Any] = None,
        target_column: str = "prompt",
        **kwargs,
    ) -> Dict[str, Any]:
        """Validate and optionally clean attached file mentions in prompts.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "flag" or "fix"
            auth_credentials: Authentication credentials (required for Google Sheets)
            target_column: Column to check for attachment mentions (default: "prompt")

        Returns:
            Dictionary containing validation results
        """
        result = ValidationResult()
        spreadsheet = None

        try:
            # Get spreadsheet interface
            spreadsheet = self._get_spreadsheet(
                spreadsheet_source, auth_credentials, read_only=mode != "fix"
            )

            # Get all data from the sheet
            all_data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not all_data:
                result.add_error("Sheet is empty or could not be read")
                return result.to_dict()

            headers = all_data[0]
            data_rows = all_data[1:]

            # Find the target column index
            try:
                target_col_index = headers.index(target_column)
            except ValueError:
                # Column not found - skip validation gracefully
                result.set_automated_log(
                    f"Column '{target_column}' not found in sheet - skipping attached files cleaning"
                )
                return result.to_dict()

            # Check each row for attachment mentions
            for row_index, row in enumerate(
                data_rows, start=2
            ):  # Start at 2 for sheet row numbering
                if target_col_index >= len(row):
                    continue  # Skip rows without enough columns

                prompt_text = row[target_col_index].strip()
                if not prompt_text:
                    continue

                # Find attachment mentions
                mentions = self._find_attachment_mentions(prompt_text)

                if mentions:
                    cell_ref = self._generate_cell_reference(
                        row_index - 2, target_col_index, sheet_name
                    )
                    mentions_str = ", ".join(f'"{m["matched_text"]}"' for m in mentions)

                    if mode == "flag":
                        result.add_detailed_issue(
                            sheet_name=sheet_name,
                            cell=cell_ref,
                            message=f"Found attachment mentions: {mentions_str}",
                            value=prompt_text,
                        )
                    else:  # fix mode
                        cleaned_text, editor_note = self._clean_attachment_mentions(
                            prompt_text, mentions
                        )

                        # Update the row data
                        updated_row = row.copy()
                        if len(updated_row) <= target_col_index:
                            # Extend row if needed
                            updated_row.extend(
                                [""] * (target_col_index + 1 - len(updated_row))
                            )
                        updated_row[target_col_index] = cleaned_text

                        result.add_detailed_fix(
                            sheet_name=sheet_name,
                            cell=cell_ref,
                            message=f"Removed attachment mentions: {mentions_str}",
                            old_value=prompt_text,
                            new_value=cleaned_text,
                        )

                        # Replace the row in our data
                        data_rows[row_index - 2] = updated_row

            if mode == "fix" and result.fixes_applied > 0:
                # Update the sheet with cleaned data
                updated_data = [headers] + data_rows
                self._update_sheet_data(spreadsheet, sheet_name, updated_data)

                # Save changes (important for Excel files)
                spreadsheet.save()

            # Set a summary log message
            if result.fixes_applied > 0:
                result.set_automated_log(
                    f"Cleaned {result.fixes_applied} prompts with attached file mentions"
                )
            elif result.flags_found > 0:
                result.set_automated_log(
                    f"Found {result.flags_found} prompts with attached file mentions"
                )
            else:
                result.set_automated_log("No attached file mentions found")

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
            result.set_automated_log("Validation failed")
        finally:
            # Clean up resources
            if spreadsheet:
                try:
                    spreadsheet.close()
                except Exception:
                    pass  # Ignore cleanup errors

        return result.to_dict()

    def _find_attachment_mentions(self, text: str) -> List[Dict[str, Any]]:
        """Find all attachment mentions in text using grammar-aware patterns.

        Args:
            text: Text to search

        Returns:
            List of dictionaries with mention details
        """
        mentions = []

        for pattern_info in self.ATTACHMENT_PATTERNS:
            pattern = pattern_info["pattern"]
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                # Check if this mention should be skipped (not a file attachment)
                if self._should_skip_mention(text, match.start(), match.end()):
                    continue

                mentions.append(
                    {
                        "matched_text": match.group(),
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                        "pattern": pattern,
                        "description": pattern_info["description"],
                    }
                )

        # Sort by position and remove overlaps (keep longest match)
        mentions.sort(key=lambda x: (x["start_pos"], -(x["end_pos"] - x["start_pos"])))

        filtered_mentions = []
        for mention in mentions:
            # Check if this mention overlaps with any already added
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

    def _clean_attachment_mentions(
        self, text: str, mentions: List[Dict[str, Any]]
    ) -> Tuple[str, str]:
        """Clean attachment mentions from text while preserving grammar.

        Args:
            text: Original text
            mentions: List of mentions to clean

        Returns:
            Tuple of (cleaned_text, editor_note)
        """
        if not mentions:
            return text, ""

        cleaned_text = text

        # Apply pattern replacements in order
        for pattern_info in self.ATTACHMENT_PATTERNS:
            pattern = pattern_info["pattern"]
            replacement = pattern_info["replacement"]

            if callable(replacement):
                # Handle lambda replacements
                def replace_func(match):
                    return replacement(match)

                cleaned_text = re.sub(
                    pattern, replace_func, cleaned_text, flags=re.IGNORECASE
                )
            else:
                # Handle string replacements
                cleaned_text = re.sub(
                    pattern, replacement, cleaned_text, flags=re.IGNORECASE
                )

        # Grammar cleanup (Rule 10)
        cleaned_text = self._apply_grammar_cleanup(cleaned_text)

        # Generate editor note
        if len(mentions) == 1:
            editor_note = "[Editor note: Removed reference to attachments to keep the prompt self-contained.]"
        else:
            editor_note = f"[Editor note: Removed {len(mentions)} references to attachments to keep the prompt self-contained.]"

        # Add editor note to the cleaned text
        final_text = f"{cleaned_text}\n\n{editor_note}"

        return final_text, editor_note

    def _apply_grammar_cleanup(self, text: str) -> str:
        """Apply grammar cleanup after attachment removal.

        Args:
            text: Text after attachment removal

        Returns:
            Grammar-corrected text
        """
        # Fix double spaces
        text = re.sub(r"\s+", " ", text)

        # Fix dangling articles and prepositions
        text = re.sub(
            r"\b(refer to|check|review|see|update|clean)\s+the\s*\.", r"\1 it.", text
        )
        text = re.sub(r"\b(in|from|with)\s+the\s*\.", r"in it.", text)

        # Fix orphaned determiners
        text = re.sub(r"\bthe\s*\.\s*", ". ", text)
        text = re.sub(r"\bthe\s*,\s*", ", ", text)

        # Fix sentence spacing
        text = re.sub(r"\.\s*\.\s*", ". ", text)
        text = re.sub(r",\s*,\s*", ", ", text)

        # Trim and clean up
        text = text.strip()

        return text
