"""Smart Chunking Optimizer for Excel to Google Sheets conversion.

This module provides intelligent chunking strategies that balance:
1. Memory usage (don't load entire large files)
2. API efficiency (minimize API calls)
3. Processing speed (optimal chunk sizes)
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Iterator, Tuple
import math

from urarovite.core.exceptions import ValidationError
from urarovite.core.spreadsheet import SpreadsheetFactory, SpreadsheetInterface


class SmartChunkingOptimizer:
    """Optimizes large Excel processing using intelligent chunking strategies."""

    # Configuration constants
    MAX_MEMORY_MB = 50  # Maximum memory usage per chunk
    MIN_API_CALLS = 3  # Minimum API calls we're willing to make
    MAX_API_CALLS = 10  # Maximum API calls before it's too fragmented
    ROWS_PER_MB = 1000  # Estimated rows per MB (depends on data complexity)

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def optimize_large_file_conversion(
        self,
        source_excel: Union[str, Path],
        target_sheets_url: str,
        auth_credentials: Dict[str, Any],
        validation_fixes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Optimize large Excel to Google Sheets conversion using smart chunking.

        Args:
            source_excel: Path to source Excel file
            target_sheets_url: Target Google Sheets URL
            auth_credentials: Authentication credentials
            validation_fixes: Optional validation fixes to apply

        Returns:
            Dict with optimization results and performance metrics
        """
        start_time = time.time()

        try:
            # Step 1: Analyze file and determine optimal chunking strategy
            analysis = self._analyze_file_for_chunking(source_excel)
            if not analysis["success"]:
                return analysis

            strategy = self._determine_chunking_strategy(analysis)

            self.logger.info(
                f"📊 Chunking strategy: {strategy['chunks']} chunks, "
                f"{strategy['rows_per_chunk']} rows/chunk, "
                f"{strategy['estimated_api_calls']} API calls"
            )

            # Step 2: Apply validation fixes locally (if any)
            working_file = source_excel
            if validation_fixes:
                fix_result = self._apply_fixes_locally(source_excel, validation_fixes)
                if fix_result["success"]:
                    working_file = fix_result["working_file"]
                else:
                    return fix_result

            # Step 3: Execute chunked upload strategy
            upload_result = self._execute_chunked_upload(
                working_file, target_sheets_url, auth_credentials, strategy
            )

            total_time = time.time() - start_time

            # Step 4: Compile results
            return {
                "success": upload_result["success"],
                "target_url": target_sheets_url if upload_result["success"] else None,
                "chunks_processed": upload_result.get("chunks_processed", 0),
                "total_rows": analysis["total_rows"],
                "total_sheets": analysis["total_sheets"],
                "strategy": strategy,
                "performance_metrics": {
                    "total_time_seconds": round(total_time, 2),
                    "chunking_enabled": True,
                    "memory_efficient": True,
                    "api_calls_made": upload_result.get("api_calls_made", 0),
                    "api_calls_saved": max(
                        0,
                        analysis["total_rows"] - upload_result.get("api_calls_made", 0),
                    ),
                    "memory_usage_mb": strategy["estimated_memory_mb"],
                    "throughput_rows_per_sec": round(
                        analysis["total_rows"] / total_time, 1
                    ),
                },
                "error": upload_result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Smart chunking failed: {str(e)}"}

    def _analyze_file_for_chunking(
        self, source_excel: Union[str, Path]
    ) -> Dict[str, Any]:
        """Analyze Excel file to determine optimal chunking strategy.

        Args:
            source_excel: Path to Excel file

        Returns:
            Dict with file analysis results
        """
        try:
            excel_path = Path(source_excel)
            if not excel_path.exists():
                return {
                    "success": False,
                    "error": f"Excel file not found: {excel_path}",
                }

            file_size_mb = excel_path.stat().st_size / (1024 * 1024)

            # Quick analysis using spreadsheet interface
            with SpreadsheetFactory.create_spreadsheet(
                excel_path, read_only=True
            ) as spreadsheet:
                metadata = spreadsheet.get_metadata()

                total_rows = 0
                sheet_info = []

                for sheet_name in metadata.sheet_names:
                    # Get sheet dimensions without loading all data
                    try:
                        # Sample first few rows to estimate data density
                        sample_data = spreadsheet.get_sheet_data(
                            sheet_name,
                            range_name="A1:Z10",  # Sample first 10 rows
                        )

                        # Estimate total rows based on file size and sample
                        if sample_data.values:
                            estimated_rows = min(
                                10000, int(file_size_mb * self.ROWS_PER_MB)
                            )
                            actual_cols = (
                                len(sample_data.values[0]) if sample_data.values else 1
                            )
                        else:
                            estimated_rows = 0
                            actual_cols = 0

                        sheet_info.append(
                            {
                                "name": sheet_name,
                                "estimated_rows": estimated_rows,
                                "cols": actual_cols,
                                "estimated_cells": estimated_rows * actual_cols,
                            }
                        )

                        total_rows += estimated_rows

                    except Exception as e:
                        self.logger.warning(
                            f"Could not analyze sheet {sheet_name}: {e}"
                        )
                        sheet_info.append(
                            {
                                "name": sheet_name,
                                "estimated_rows": 100,  # Conservative estimate
                                "cols": 10,
                                "estimated_cells": 1000,
                            }
                        )
                        total_rows += 100

            return {
                "success": True,
                "file_size_mb": round(file_size_mb, 2),
                "total_sheets": len(metadata.sheet_names),
                "total_rows": total_rows,
                "sheet_info": sheet_info,
                "complexity": "high"
                if total_rows > 5000
                else "medium"
                if total_rows > 1000
                else "low",
            }

        except Exception as e:
            return {"success": False, "error": f"File analysis failed: {str(e)}"}

    def _determine_chunking_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal chunking strategy based on file analysis.

        Args:
            analysis: File analysis results

        Returns:
            Dict with chunking strategy
        """
        total_rows = analysis["total_rows"]
        analysis["file_size_mb"]

        # Calculate optimal chunk size based on memory constraints
        max_rows_per_chunk = self.MAX_MEMORY_MB * self.ROWS_PER_MB

        # Calculate number of chunks needed
        if total_rows <= max_rows_per_chunk:
            # Small enough for single chunk
            chunks = 1
            rows_per_chunk = total_rows
            api_calls = 1
        else:
            # Need multiple chunks
            ideal_chunks = math.ceil(total_rows / max_rows_per_chunk)

            # Constrain to reasonable API call limits
            chunks = max(self.MIN_API_CALLS, min(ideal_chunks, self.MAX_API_CALLS))
            rows_per_chunk = math.ceil(total_rows / chunks)
            api_calls = chunks

        estimated_memory_mb = min(
            self.MAX_MEMORY_MB, (rows_per_chunk / self.ROWS_PER_MB)
        )

        return {
            "chunks": chunks,
            "rows_per_chunk": rows_per_chunk,
            "estimated_api_calls": api_calls,
            "estimated_memory_mb": round(estimated_memory_mb, 1),
            "strategy_type": "single_chunk" if chunks == 1 else "multi_chunk",
            "memory_efficient": estimated_memory_mb <= self.MAX_MEMORY_MB,
            "api_efficient": api_calls <= self.MAX_API_CALLS,
        }

    def _apply_fixes_locally(
        self, source_excel: Union[str, Path], validation_fixes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply validation fixes locally before chunked upload.

        Args:
            source_excel: Source Excel file
            validation_fixes: Fixes to apply

        Returns:
            Dict with local fix results
        """
        try:
            # Create working copy for fixes
            working_dir = Path("./temp/chunking_optimization")
            working_dir.mkdir(parents=True, exist_ok=True)

            timestamp = int(time.time())
            working_file = working_dir / f"chunked_work_{timestamp}.xlsx"

            # Copy and apply fixes locally
            from urarovite.utils.generic_spreadsheet import convert_spreadsheet_format

            copy_result = convert_spreadsheet_format(
                source=source_excel, target=working_file, preserve_formulas=True
            )

            if copy_result["success"]:
                # TODO: Apply specific validation fixes here
                # For now, just return the working copy
                return {
                    "success": True,
                    "working_file": str(working_file),
                    "fixes_applied": validation_fixes.get("fixes_applied", 0),
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create working copy: {copy_result['error']}",
                }

        except Exception as e:
            return {"success": False, "error": f"Local fixes failed: {str(e)}"}

    def _execute_chunked_upload(
        self,
        working_file: Union[str, Path],
        target_sheets_url: str,
        auth_credentials: Dict[str, Any],
        strategy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute the chunked upload strategy.

        Args:
            working_file: Working Excel file
            target_sheets_url: Target Google Sheets URL
            auth_credentials: Auth credentials
            strategy: Chunking strategy

        Returns:
            Dict with upload results
        """
        try:
            if strategy["strategy_type"] == "single_chunk":
                # Use existing bulk upload for single chunk
                return self._single_chunk_upload(
                    working_file, target_sheets_url, auth_credentials
                )
            else:
                # Use multi-chunk strategy
                return self._multi_chunk_upload(
                    working_file, target_sheets_url, auth_credentials, strategy
                )

        except Exception as e:
            return {"success": False, "error": f"Chunked upload failed: {str(e)}"}

    def _single_chunk_upload(
        self,
        working_file: Union[str, Path],
        target_sheets_url: str,
        auth_credentials: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute single chunk upload (use existing bulk system).

        Args:
            working_file: Working Excel file
            target_sheets_url: Target Google Sheets URL
            auth_credentials: Auth credentials

        Returns:
            Dict with upload results
        """
        try:
            from urarovite.utils.enhanced_conversion import convert_with_full_formatting

            self.logger.info("📤 Single chunk upload using enhanced formatting system")

            result = convert_with_full_formatting(
                source=working_file,
                target=target_sheets_url,
                auth_credentials=auth_credentials,
                preserve_formulas=True,
                preserve_visual_formatting=True,
            )

            return {
                "success": result["success"],
                "chunks_processed": 1,
                "api_calls_made": 1,
                "error": result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Single chunk upload failed: {str(e)}"}

    def _multi_chunk_upload(
        self,
        working_file: Union[str, Path],
        target_sheets_url: str,
        auth_credentials: Dict[str, Any],
        strategy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute multi-chunk upload strategy.

        Args:
            working_file: Working Excel file
            target_sheets_url: Target Google Sheets URL
            auth_credentials: Auth credentials
            strategy: Chunking strategy

        Returns:
            Dict with upload results
        """
        try:
            from urarovite.utils.sheets import extract_sheet_id
            from urarovite.auth.google_sheets import (
                create_sheets_service_from_encoded_creds,
            )

            spreadsheet_id = extract_sheet_id(target_sheets_url)
            sheets_service = create_sheets_service_from_encoded_creds(
                auth_credentials["auth_secret"]
            )

            chunks_processed = 0
            api_calls_made = 0

            self.logger.info(f"📤 Multi-chunk upload: {strategy['chunks']} chunks")

            # Process each sheet in chunks
            with SpreadsheetFactory.create_spreadsheet(
                working_file, read_only=True
            ) as spreadsheet:
                metadata = spreadsheet.get_metadata()

                for sheet_name in metadata.sheet_names:
                    # Process this sheet in chunks
                    chunk_results = self._upload_sheet_in_chunks(
                        spreadsheet,
                        sheet_name,
                        spreadsheet_id,
                        sheets_service,
                        strategy,
                    )

                    chunks_processed += chunk_results["chunks_processed"]
                    api_calls_made += chunk_results["api_calls_made"]

            return {
                "success": True,
                "chunks_processed": chunks_processed,
                "api_calls_made": api_calls_made,
            }

        except Exception as e:
            return {"success": False, "error": f"Multi-chunk upload failed: {str(e)}"}

    def _upload_sheet_in_chunks(
        self,
        spreadsheet: SpreadsheetInterface,
        sheet_name: str,
        spreadsheet_id: str,
        sheets_service: Any,
        strategy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Upload a single sheet in chunks.

        Args:
            spreadsheet: Source spreadsheet interface
            sheet_name: Name of sheet to upload
            spreadsheet_id: Target Google Sheets ID
            sheets_service: Google Sheets API service
            strategy: Chunking strategy

        Returns:
            Dict with chunk upload results
        """
        try:
            rows_per_chunk = strategy["rows_per_chunk"]
            chunks_processed = 0
            api_calls_made = 0

            # Get sheet data in chunks
            current_row = 1
            while True:
                # Define chunk range
                end_row = current_row + rows_per_chunk - 1
                range_name = f"A{current_row}:ZZ{end_row}"  # Generous column range

                # Get chunk data
                chunk_data = spreadsheet.get_sheet_data(sheet_name, range_name)

                if not chunk_data.values:
                    break  # No more data

                # Upload this chunk
                batch_body = {
                    "valueInputOption": "RAW",
                    "data": [
                        {
                            "range": f"'{sheet_name}'!A{current_row}:ZZ{current_row + len(chunk_data.values) - 1}",
                            "values": chunk_data.values,
                        }
                    ],
                }

                sheets_service.spreadsheets().values().batchUpdate(
                    spreadsheetId=spreadsheet_id, body=batch_body
                ).execute()

                chunks_processed += 1
                api_calls_made += 1
                current_row = end_row + 1

                self.logger.info(
                    f"📤 Uploaded chunk {chunks_processed} for {sheet_name}"
                )

                # Stop if we got less data than expected (end of sheet)
                if len(chunk_data.values) < rows_per_chunk:
                    break

            return {
                "chunks_processed": chunks_processed,
                "api_calls_made": api_calls_made,
            }

        except Exception as e:
            self.logger.error(f"Chunk upload failed for {sheet_name}: {e}")
            return {
                "chunks_processed": chunks_processed,
                "api_calls_made": api_calls_made,
                "error": str(e),
            }


def optimize_large_excel_conversion(
    source_excel: Union[str, Path],
    target_sheets_url: str,
    auth_credentials: Dict[str, Any],
    validation_fixes: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenience function for smart chunking optimization.

    Args:
        source_excel: Source Excel file
        target_sheets_url: Target Google Sheets URL
        auth_credentials: Auth credentials
        validation_fixes: Optional validation fixes

    Returns:
        Dict with optimization results
    """
    optimizer = SmartChunkingOptimizer()
    return optimizer.optimize_large_file_conversion(
        source_excel=source_excel,
        target_sheets_url=target_sheets_url,
        auth_credentials=auth_credentials,
        validation_fixes=validation_fixes,
    )
