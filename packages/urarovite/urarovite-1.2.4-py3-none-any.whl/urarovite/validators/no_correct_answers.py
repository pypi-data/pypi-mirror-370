"""Validator for detecting when input sheets contain no correct answers.

This validator analyzes input sheets to determine if they contain valid data
or if they appear to be templates/blank sheets with no meaningful content.
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Union
from pathlib import Path

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface


class NoCorrectAnswersValidator(BaseValidator):
    """Validator for detecting input sheets with no correct answers."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="no_correct_answers",
            name="Detect No Correct Answers",
            description=(
                "Detects when input sheets contain no valid answers by "
                "comparing input vs expected output patterns and flagging "
                "template/blank cases with confidence scoring."
            ),
        )

    def validate(
        self,
        spreadsheet_source: Union[str, Path, SpreadsheetInterface],
        mode: str,
        auth_credentials: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check if input sheet contains valid answers or is template/blank.

        Args:
            spreadsheet_source: Either a Google Sheets URL, Excel file path,
                or SpreadsheetInterface
            mode: Either "fix" (not applicable) or "flag" (report only)
            auth_credentials: Auth credentials (required for Google Sheets)
            **kwargs: Additional validator-specific parameters

        Returns:
            Dict with validation results including confidence scoring
        """

        def validation_logic(
            spreadsheet: SpreadsheetInterface, result: ValidationResult, **kwargs
        ) -> None:
            # Get all sheet data
            data, sheet_name = self._get_all_sheet_data(spreadsheet)

            if not data:
                result.add_error("Sheet is empty - no data to validate")
                result.details["confidence_score"] = 1.0
                result.details["is_template_or_blank"] = True
                result.details["detection_reasons"] = ["Sheet is completely empty"]
                result.details["sheet_name"] = sheet_name
                result.set_automated_log(
                    "[ERROR] Sheet is completely empty - likely template/blank"
                )
                return

            # Analyze the sheet content for signs of being a template or blank
            analysis_result = self._analyze_sheet_content(data)

            # Set the main result with enhanced details
            total_cells = len(data) * len(data[0]) if data and data[0] else 0
            result.details.update(
                {
                    "confidence_score": analysis_result["confidence_score"],
                    "is_template_or_blank": analysis_result["is_template_or_blank"],
                    "detection_reasons": analysis_result["reasons"],
                    "data_quality_indicators": analysis_result["quality_indicators"],
                    "sheet_name": sheet_name,
                    "total_cells_analyzed": total_cells,
                    "analysis_timestamp": self._get_current_timestamp(),
                }
            )

            if analysis_result["is_template_or_blank"]:
                result.add_issue(1)
                confidence = analysis_result["confidence_score"]
                if mode == "fix":
                    msg = (
                        "[WARNING] Input sheet '{}' appears to be template/blank "
                        "(confidence: {:.1%}). No fixes possible for this validator. "
                        "Reasons: {}"
                    ).format(
                        sheet_name, confidence, ", ".join(analysis_result["reasons"])
                    )
                    result.set_automated_log(msg)
                else:
                    msg = (
                        "[WARNING] Input sheet '{}' appears to be template/blank "
                        "(confidence: {:.1%}). Reasons: {}"
                    ).format(
                        sheet_name, confidence, ", ".join(analysis_result["reasons"])
                    )
                    result.set_automated_log(msg)
            else:
                result.set_automated_log(
                    "[INFO] Input sheet '{}' appears to contain valid data "
                    "(confidence: {:.1%})".format(
                        sheet_name, analysis_result["confidence_score"]
                    )
                )

        # Execute validation using the base class helper
        with self._managed_spreadsheet(
            spreadsheet_source, auth_credentials
        ) as spreadsheet:
            result = ValidationResult()
            validation_logic(spreadsheet, result, **kwargs)
            return result.to_dict()

    def _analyze_sheet_content(self, data: List[List[Any]]) -> Dict[str, Any]:
        """Analyze sheet content to determine if it's a template or contains valid data.

        Args:
            data: 2D list of cell values from the sheet

        Returns:
            Dict containing analysis results with confidence scoring
        """
        if not data:
            return {
                "confidence_score": 1.0,
                "is_template_or_blank": True,
                "reasons": ["Sheet is completely empty"],
                "quality_indicators": {},
            }

        # Calculate various quality indicators
        quality_indicators = self._calculate_quality_indicators(data)

        # Determine if this appears to be a template/blank sheet
        template_indicators = self._identify_template_indicators(
            data, quality_indicators
        )

        # Calculate confidence score based on multiple factors
        confidence_score = self._calculate_confidence_score(
            template_indicators, quality_indicators
        )

        # Determine final classification
        is_template_or_blank = (
            confidence_score > 0.6
        )  # Lowered threshold for classification

        return {
            "confidence_score": confidence_score,
            "is_template_or_blank": is_template_or_blank,
            "reasons": template_indicators["reasons"],
            "quality_indicators": quality_indicators,
        }

    def _calculate_quality_indicators(self, data: List[List[Any]]) -> Dict[str, Any]:
        """Calculate various quality indicators for the sheet data.

        Args:
            data: 2D list of cell values

        Returns:
            Dict containing quality metrics
        """
        total_cells = 0
        empty_cells = 0
        text_cells = 0
        numeric_cells = 0
        formula_cells = 0
        url_cells = 0
        date_cells = 0

        # Common template/placeholder text patterns
        template_patterns = [
            r"^\s*(example|sample|template|placeholder|test|demo|fill|enter|type|input)\s*$",
            r"^\s*[a-zA-Z\s]*\s*here\s*$",
            r"^\s*[a-zA-Z\s]*\s*data\s*$",
            r"^\s*[a-zA-Z\s]*\s*information\s*$",
            r"^\s*[a-zA-Z\s]*\s*details\s*$",
        ]
        template_regex = re.compile("|".join(template_patterns), re.IGNORECASE)

        for row in data:
            for cell_value in row:
                total_cells += 1

                if cell_value is None or str(cell_value).strip() == "":
                    empty_cells += 1
                else:
                    cell_str = str(cell_value).strip()

                    # Check for template/placeholder text
                    if template_regex.search(cell_str):
                        text_cells += 1
                    # Check for formulas
                    elif cell_str.startswith("="):
                        formula_cells += 1
                    # Check for URLs
                    elif "http" in cell_str.lower() or "www." in cell_str.lower():
                        url_cells += 1
                    # Check for dates (basic pattern)
                    elif re.match(r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$", cell_str):
                        date_cells += 1
                    # Check for numbers
                    elif re.match(r"^[\d,]+\.?\d*$", cell_str):
                        numeric_cells += 1
                    else:
                        text_cells += 1

        return {
            "total_cells": total_cells,
            "empty_cells": empty_cells,
            "text_cells": text_cells,
            "numeric_cells": numeric_cells,
            "formula_cells": formula_cells,
            "url_cells": url_cells,
            "date_cells": date_cells,
            "empty_ratio": empty_cells / total_cells if total_cells > 0 else 1.0,
            "template_text_ratio": text_cells / total_cells if total_cells > 0 else 0.0,
        }

    def _identify_template_indicators(
        self, data: List[List[Any]], quality_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify specific indicators that suggest the sheet is a template.

        Args:
            data: 2D list of cell values
            quality_indicators: Calculated quality metrics

        Returns:
            Dict containing template indicators and reasons
        """
        reasons = []
        indicators = []

        # Check for high empty cell ratio
        if quality_indicators["empty_ratio"] > 0.7:  # Lowered from 0.8 to 0.7
            msg = "High empty cell ratio ({:.1%})".format(
                quality_indicators["empty_ratio"]
            )
            reasons.append(msg)
            indicators.append("high_empty_ratio")

        # Check for template-like text patterns
        template_text_count = 0
        template_patterns = [
            "example",
            "sample",
            "template",
            "placeholder",
            "test",
            "demo",
            "fill",
            "enter",
            "type",
            "input",
            "here",
            "data",
            "information",
            "details",
        ]
        for row in data:
            for cell_value in row:
                if cell_value and isinstance(cell_value, str):
                    cell_str = cell_value.strip().lower()
                    if any(pattern in cell_str for pattern in template_patterns):
                        template_text_count += 1

        if template_text_count > 0:
            template_ratio = template_text_count / quality_indicators["total_cells"]
            if template_ratio > 0.05:  # More than 5% template text
                msg = "Contains template/placeholder text ({:.1%})".format(
                    template_ratio
                )
                reasons.append(msg)
                indicators.append("template_text_present")

        # Check for headers only (more lenient)
        if len(data) <= 2 and quality_indicators["empty_ratio"] > 0.3:
            reasons.append("Sheet appears to contain only headers")
            indicators.append("headers_only")

        # Check for repetitive patterns that suggest templates
        if len(data) > 2:
            repetitive_patterns = self._detect_repetitive_patterns(data)
            if repetitive_patterns:
                msg = "Contains repetitive patterns: {}".format(repetitive_patterns)
                reasons.append(msg)
                indicators.append("repetitive_patterns")

        # Check for lack of meaningful data
        meaningful_cells = (
            quality_indicators["numeric_cells"]
            + quality_indicators["date_cells"]
            + quality_indicators["url_cells"]
        )
        total_cells = quality_indicators["total_cells"]
        meaningful_data_ratio = meaningful_cells / total_cells if total_cells > 0 else 0

        if meaningful_data_ratio < 0.15:  # Less than 15% meaningful data
            msg = "Low meaningful data content ({:.1%})".format(meaningful_data_ratio)
            reasons.append(msg)
            indicators.append("low_meaningful_data")

        return {
            "reasons": reasons,
            "indicators": indicators,
            "template_text_count": template_text_count,
            "meaningful_data_ratio": meaningful_data_ratio,
        }

    def _detect_repetitive_patterns(self, data: List[List[Any]]) -> List[str]:
        """Detect repetitive patterns that suggest template content.

        Args:
            data: 2D list of cell values

        Returns:
            List of detected repetitive patterns
        """
        patterns = []

        # Check for repeated rows
        if len(data) > 3:
            row_patterns = {}
            for i, row in enumerate(data[1:], 1):  # Skip header
                row_key = tuple(str(cell).strip() if cell else "" for cell in row)
                if row_key in row_patterns:
                    row_patterns[row_key].append(i)
                else:
                    row_patterns[row_key] = [i]

            # Find rows that appear multiple times
            for row_key, positions in row_patterns.items():
                if len(positions) > 1:
                    patterns.append(f"Repeated row at positions {positions}")

        # Check for repeated columns
        if len(data) > 0 and len(data[0]) > 3:
            for col_idx in range(len(data[0])):
                col_values = [
                    str(row[col_idx]).strip()
                    if col_idx < len(row) and row[col_idx]
                    else ""
                    for row in data
                ]
                if (
                    len(set(col_values)) <= 2 and len(col_values) > 2
                ):  # Only 1-2 unique values
                    patterns.append(f"Column {col_idx + 1} has repetitive content")

        return patterns

    def _calculate_confidence_score(
        self, template_indicators: Dict[str, Any], quality_indicators: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for template/blank detection.

        Args:
            template_indicators: Template detection results
            quality_indicators: Quality metrics

        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_score = 0.0

        # High empty cell ratio (strong indicator)
        if quality_indicators["empty_ratio"] > 0.9:
            base_score += 0.4
        elif quality_indicators["empty_ratio"] > 0.8:
            base_score += 0.3
        elif quality_indicators["empty_ratio"] >= 0.5:  # Changed to >= to include 0.5
            base_score += 0.2

        # Template text presence (strong indicator)
        if "template_text_present" in template_indicators["indicators"]:
            base_score += 0.4  # Increased from 0.3 to 0.4

        # Headers only (moderate indicator)
        if "headers_only" in template_indicators["indicators"]:
            base_score += 0.25

        # Repetitive patterns (moderate indicator)
        if "repetitive_patterns" in template_indicators["indicators"]:
            base_score += 0.2

        # Low meaningful data (moderate indicator)
        if "low_meaningful_data" in template_indicators["indicators"]:
            base_score += 0.2

        # Cap the score at 1.0
        return min(base_score, 1.0)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format.

        Returns:
            str: Current timestamp in ISO format
        """
        return datetime.now(timezone.utc).isoformat()
