#!/usr/bin/env python3
"""
Base CLI utilities for Urarovite.

This module provides abstracted boilerplate for utility commands with shared logic
for single vs batch operations, output flags, and authentication handling.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Type variables for generic utility classes
T = TypeVar('T')
U = TypeVar('U')


@dataclass
class UtilityResult:
    """Standard result structure for utility operations."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseUtility(ABC, Generic[T, U]):
    """Base class for utility operations with standard CLI patterns."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute_single(self, **kwargs) -> UtilityResult:
        """Execute utility on a single target."""
        pass
    
    @abstractmethod
    def execute_batch(self, **kwargs) -> UtilityResult:
        """Execute utility on multiple targets."""
        pass
    
    def get_argument_parser(self) -> argparse.ArgumentParser:
        """Get the argument parser for this utility."""
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Common arguments
        parser.add_argument(
            "--output",
            choices=["table", "json", "quiet"],
            default="table",
            help="Output format (default: table)"
        )
        parser.add_argument(
            "--auth-secret",
            help="Base64-encoded service account credentials (or set URAROVITE_AUTH_SECRET env var)"
        )
        parser.add_argument(
            "--subject",
            help="Email for domain-wide delegation (optional)"
        )
        
        # Add utility-specific arguments
        self._add_utility_arguments(parser)
        
        return parser
    
    @abstractmethod
    def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add utility-specific arguments to the parser."""
        pass
    
    def _get_auth_credentials(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract authentication credentials from args or environment."""
        auth_credentials = {}
        
        if args.auth_secret:
            auth_credentials["auth_secret"] = args.auth_secret
        else:
            # Try env fallback
            fallback = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
            if fallback:
                auth_credentials["auth_secret"] = fallback
            else:
                console.print("[red]❌ No authentication credentials found[/red]")
                console.print("[dim]Set URAROVITE_AUTH_SECRET env var or use --auth-secret[/dim]")
                sys.exit(1)
        
        if args.subject:
            auth_credentials["subject"] = args.subject
        
        return auth_credentials
    
    def _display_result(self, result: UtilityResult, output_format: str) -> None:
        """Display the result in the specified format."""
        if output_format == "json":
            output_data = {
                "success": result.success,
                "message": result.message,
                "error": result.error,
                "data": result.data,
                "metadata": result.metadata
            }
            console.print(json.dumps(output_data, indent=2))
        elif output_format == "table":
            self._display_result_table(result)
        # "quiet" format does nothing
    
    def _display_result_table(self, result: UtilityResult) -> None:
        """Display result in a formatted table."""
        if result.success:
            console.print(f"[green]✅ {result.message}[/green]")
            
            if result.metadata:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Metric", style="cyan", no_wrap=True)
                table.add_column("Value", style="green")
                
                for key, value in result.metadata.items():
                    table.add_row(key, str(value))
                
                console.print(table)
        else:
            console.print(f"[red]❌ {result.message}[/red]")
            if result.error:
                console.print(f"[dim]Error: {result.error}[/dim]")


class SingleBatchUtility(BaseUtility[T, U]):
    """Utility that supports both single and batch operations."""
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
    
    def get_argument_parser(self) -> argparse.ArgumentParser:
        """Get argument parser with single/batch mode selection."""
        parser = super().get_argument_parser()
        
        # Add mode selection
        parser.add_argument(
            "--mode",
            choices=["single", "batch"],
            default="single",
            help="Operation mode: single target or batch processing (default: single)"
        )
        
        return parser
    
    def execute(self, args: argparse.Namespace) -> UtilityResult:
        """Execute utility based on mode."""
        try:
            # Auto-detect batch mode if --url-columns is provided
            if hasattr(args, 'url_columns') and args.url_columns and args.mode == "single":
                args.mode = "batch"
            
            if args.mode == "single":
                return self._execute_single_with_progress(args)
            else:
                return self._execute_batch_with_progress(args)
        except Exception as e:
            return UtilityResult(
                success=False,
                message="Utility execution failed",
                error=str(e)
            )
    
    def _execute_single_with_progress(self, args: argparse.Namespace) -> UtilityResult:
        """Execute single operation with progress indicator."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Executing {self.name}...", total=None)
            
            # Get auth credentials
            auth_credentials = self._get_auth_credentials(args)
            
            # Execute utility
            result = self.execute_single(
                auth_credentials=auth_credentials,
                **self._extract_utility_args(args)
            )
            
            progress.update(task, completed=True)
        
        return result
    
    def _execute_batch_with_progress(self, args: argparse.Namespace) -> UtilityResult:
        """Execute batch operation with progress indicator."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Executing {self.name} in batch mode...", total=None)
            
            # Get auth credentials
            auth_credentials = self._get_auth_credentials(args)
            
            # Execute utility
            result = self.execute_batch(
                auth_credentials=auth_credentials,
                **self._extract_utility_args(args)
            )
            
            progress.update(task, completed=True)
        
        # Automatically add result column to input spreadsheet if it's a Google Sheets URL
        # Note: We want to add result columns even for failed operations to show "Failed" status
        if result.data and "results" in result.data:
            self._add_result_column_to_batch_results(args, result)
        
        return result
    
    def _add_result_column_to_batch_results(self, args: argparse.Namespace, result: UtilityResult) -> None:
        """Automatically add result column to the input spreadsheet for batch operations.
        
        This method checks if the batch operation used a Google Sheets URL as metadata file
        and automatically adds a result column showing "Passed" or "Failed" for each row.
        """
        try:
            # Check if we have batch results
            if not result.data or "results" not in result.data:
                return
            
            # Get the metadata file path from args (check common argument names)
            metadata_file = None
            for arg_name in ['metadata_file', 'input_file', 'spreadsheet_source']:
                if hasattr(args, arg_name):
                    metadata_file = getattr(args, arg_name)
                    break
            
            if not metadata_file or not metadata_file.startswith("http"):
                return
            
            # Check if we have auth credentials
            auth_credentials = self._get_auth_credentials(args)
            if not auth_credentials or "auth_secret" not in auth_credentials:
                print("⚠️ Warning: No auth credentials available to update metadata spreadsheet")
                return
            
            # Use the proper utilities to read and write spreadsheet data
            try:
                from urarovite.utils.generic_spreadsheet import get_spreadsheet_data, update_spreadsheet_data
                
                # Get current spreadsheet data
                current_data = get_spreadsheet_data(
                    metadata_file, 
                    "A1:Z1000",  # Get a large range to ensure we capture all data
                    auth_credentials
                )
                
                if not current_data["success"]:
                    print(f"⚠️ Warning: Failed to read spreadsheet data: {current_data.get('error', 'Unknown error')}")
                    return
                
                values = current_data["values"]
                if not values:
                    print("⚠️ Warning: No data found in spreadsheet to update")
                    return
                
                # Get headers from first row
                headers = values[0]
                
                # Add result column if it doesn't exist
                result_column_name = f"{self.name} result"
                if result_column_name not in headers:
                    headers.append(result_column_name)
                
                # Create new values with results
                new_values = [headers]  # Start with headers
                
                # Add data rows with results
                for i, row in enumerate(values[1:], 1):  # Skip header row, start counting from 1
                    # Extend row to match header length
                    while len(row) < len(headers):
                        row.append("")
                    
                    # Find the result for this row
                    result_value = "Failed"  # Default to "Failed" if no result found
                    for batch_result in result.data["results"]:
                        if batch_result.get("row") == i:
                            status = batch_result.get("status", "unknown")
                            # Check various success indicators
                            is_success = (
                                status in ["success", "analyzed", "successful"] or
                                batch_result.get("success", False) or
                                "error" not in batch_result or not batch_result["error"]
                            )
                            result_value = "Passed" if is_success else "Failed"
                            break
                    
                    # Set result in the appropriate column
                    result_col_idx = headers.index(result_column_name)
                    if result_col_idx < len(row):
                        row[result_col_idx] = result_value
                    else:
                        row.append(result_value)
                    
                    new_values.append(row)
                
                # Get the first sheet name for updating
                from urarovite.utils.generic_spreadsheet import get_spreadsheet_tabs
                tabs_result = get_spreadsheet_tabs(metadata_file, auth_credentials)
                if tabs_result["accessible"] and tabs_result["tabs"]:
                    first_sheet_name = tabs_result["tabs"][0]
                else:
                    first_sheet_name = "Sheet1"  # Default fallback
                
                # Update the spreadsheet with new data
                update_result = update_spreadsheet_data(
                    metadata_file,
                    first_sheet_name,  # Use first sheet name
                    new_values,
                    "A1",  # Start from A1
                    auth_credentials
                )
                
                if update_result["success"]:
                    print(f"✅ Results written back to metadata spreadsheet: {result_column_name} column added")
                else:
                    print(f"⚠️ Warning: Failed to update spreadsheet: {update_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"⚠️ Warning: Failed to update metadata spreadsheet: {str(e)}")
                
        except Exception as e:
            print(f"⚠️ Warning: Error processing batch results: {str(e)}")
    
    def _extract_utility_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract utility-specific arguments from parsed args."""
        # This should be implemented by subclasses to extract their specific args
        return {}


class UtilityCommandRunner:
    """Runner for utility commands with standard CLI patterns."""
    
    def __init__(self, utility: BaseUtility):
        self.utility = utility
    
    def run(self, argv: Optional[List[str]] = None) -> None:
        """Run the utility command."""
        parser = self.utility.get_argument_parser()
        args = parser.parse_args(argv)
        
        # Execute utility
        if hasattr(self.utility, 'execute'):
            # SingleBatchUtility
            result = self.utility.execute(args)
        else:
            # BaseUtility - determine mode based on args
            auth_credentials = self.utility._get_auth_credentials(args)
            result = self._determine_and_execute(args, auth_credentials)
        
        # Display result
        self.utility._display_result(result, args.output)
        
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)
    
    def _determine_and_execute(self, args: argparse.Namespace, auth_credentials: Dict[str, Any]) -> UtilityResult:
        """Determine execution mode and execute for BaseUtility."""
        # This is a fallback for utilities that don't implement SingleBatchUtility
        # Subclasses should override this behavior
        return UtilityResult(
            success=False,
            message="Utility execution not implemented",
            error="This utility does not support automatic mode detection"
        )


def create_utility_command(
    name: str,
    description: str,
    single_func: Callable[..., UtilityResult],
    batch_func: Callable[..., UtilityResult],
    argument_setup: Callable[[argparse.ArgumentParser], None]
) -> SingleBatchUtility:
    """Factory function to create a utility command with standard patterns."""
    
    class GeneratedUtility(SingleBatchUtility):
        def _add_utility_arguments(self, parser: argparse.ArgumentParser) -> None:
            argument_setup(parser)
        
        def execute_single(self, **kwargs) -> UtilityResult:
            return single_func(**kwargs)
        
        def execute_batch(self, **kwargs) -> UtilityResult:
            return batch_func(**kwargs)
    
    return GeneratedUtility(name, description)


def run_utility_cli(
    utility: BaseUtility,
    argv: Optional[List[str]] = None
) -> None:
    """Run a utility command with standard CLI handling."""
    runner = UtilityCommandRunner(utility)
    runner.run(argv)


# Example usage pattern:
# 
# class MyUtility(SingleBatchUtility):
#     def _add_utility_arguments(self, parser):
#         parser.add_argument("input_file", help="Input file path")
#         parser.add_argument("--output", help="Output path")
#     
#     def execute_single(self, **kwargs):
#         # Single operation logic
#         return UtilityResult(success=True, message="Single operation completed")
#     
#     def execute_batch(self, **kwargs):
#         # Batch operation logic
#         return UtilityResult(success=True, message="Batch operation completed")
# 
# if __name__ == "__main__":
#     utility = MyUtility("my-util", "Description of my utility")
#     run_utility_cli(utility)
