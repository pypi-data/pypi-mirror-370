#!/usr/bin/env python3
"""
Command-line interface for Urarovite Google Sheets validation library.

This provides a simple command-line interface for non-technical users.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from typing import Any, Dict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from urarovite import get_available_validation_criteria, execute_validation


console = Console()


def load_environment() -> None:
    """Load environment variables from .env file and show helpful messages."""
    # Try to load .env file
    env_loaded = load_dotenv()
    
    if env_loaded:
        console.print("[dim]✅ Loaded environment variables from .env file[/dim]")
    else:
        console.print("[dim]💡 No .env file found - you can create one with your credentials[/dim]")
    
    # Check if auth credentials are available
    auth_secret = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
    if auth_secret:
        console.print("[dim]🔐 Authentication credentials loaded[/dim]")
    else:
        console.print("[yellow]⚠️  No authentication credentials found[/yellow]")
        console.print("[dim]   Create a .env file with: URAROVITE_AUTH_SECRET=your-base64-credentials[/dim]")


def print_banner() -> None:
    """Print the application banner."""
    banner = """
    ██╗   ██╗██████╗  █████╗ ██████╗  ██████╗ ██╗   ██╗██╗████████╗███████╗
    ██║   ██║██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██║   ██║██║╚══██╔══╝██╔════╝
    ██║   ██║██████╔╝███████║██████╔╝██║   ██║██║   ██║██║   ██║   █████╗  
    ██║   ██║██╔══██╗██╔══██║██╔══██╗██║   ██║╚██╗ ██╔╝██║   ██║   ██╔══╝  
    ╚██████╔╝██║  ██║██║  ██║██║  ██║╚██████╔╝ ╚████╔╝ ██║   ██║   ███████╗
     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚═╝   ╚═╝   ╚══════╝
    """
    console.print(Panel(banner, title="Google Sheets Validator", border_style="bright_blue"))


def list_validators() -> None:
    """List all available validation criteria."""
    console.print("\n[bold bright_blue]Available Validation Criteria:[/bold bright_blue]\n")
    
    criteria = get_available_validation_criteria()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    
    for criterion in criteria:
        table.add_row(
            criterion["id"],
            criterion["name"], 
            criterion.get("description", "No description available")
        )
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(criteria)} validators available[/dim]")


def process_forte_csv(
    csv_file: str,
    output_csv: str | None = None,
    target_folder: str = "1S2V36WyAkNCSByYK4H-uJazfWN56SXCD",
    auth_secret: str | None = None,
    mode: str = "fix",
    target_format: str = "sheets"
) -> None:
    """Process a Forte CSV file - validate and copy Google Sheets."""
    
    # Get auth credentials
    if not auth_secret:
        auth_secret = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
        if not auth_secret:
            console.print("[bold red]Error:[/bold red] No authentication credentials provided.")
            console.print("Create a .env file with: URAROVITE_AUTH_SECRET=your-base64-credentials")
            console.print("Or use --auth-secret parameter")
            sys.exit(1)
    
    # Set default output file
    if not output_csv:
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        output_csv = f"./output/{base_name}_processed.csv"
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    console.print(f"\n[bold bright_blue]Processing Forte CSV:[/bold bright_blue] {csv_file}")
    console.print(f"[bold bright_blue]Target folder:[/bold bright_blue] {target_folder}")
    console.print(f"[bold bright_blue]Output CSV:[/bold bright_blue] {output_csv}")
    console.print(f"[bold bright_blue]Mode:[/bold bright_blue] {mode}")
    
    # Import the processing function
    try:
        import pandas as pd
    except ImportError as e:
        console.print(f"[bold red]Import Error:[/bold red] {str(e)}")
        sys.exit(1)
    
    # Process the CSV with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing Forte CSV file...", total=None)
        
        try:
            # Read CSV
            progress.update(task, description="Reading CSV file...")
            df = pd.read_csv(csv_file)
            
            # Initialize result columns
            new_columns = [
                'original_input_validation_fixes', 'original_input_validation_issues', 
                'original_input_validation_summary', 'original_input_copied_url',
                'original_output_validation_fixes', 'original_output_validation_issues', 
                'original_output_validation_summary', 'original_output_copied_url',
                'fixed_input_validation_fixes', 'fixed_input_validation_issues', 
                'fixed_input_validation_summary', 'fixed_input_copied_url',
                'fixed_output_validation_fixes', 'fixed_output_validation_issues', 
                'fixed_output_validation_summary', 'fixed_output_copied_url'
            ]
            
            for col in new_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Define URL column mappings (based on Forte structure)
            url_mappings = {
                'original_input': ['task__data_input_sheet_url', 'task__data_input_sheet_url_new'],
                'original_output': ['task__data_example_output_sheet_url', 'task__data_example_output_sheet_url_new'],
                'fixed_input': ['result__fixed_input_excel_file'],
                'fixed_output': ['result__Fixed output_excel_file']
            }
            
            total_processed = 0
            total_copied = 0
            total_fixes = 0
            
            # Process each row
            for idx, row in df.iterrows():
                progress.update(task, description=f"Processing row {idx + 1}/{len(df)}...")
                
                for category, columns in url_mappings.items():
                    for col in columns:
                        if col in df.columns:
                            url = row.get(col)
                            if pd.notna(url) and str(url).strip() and str(url).startswith('http'):
                                url = str(url).strip()
                                
                                # Process this URL
                                result = process_single_url(
                                    url, category, idx, target_folder, auth_secret, mode, target_format, progress
                                )
                                
                                if result:
                                    # Update DataFrame with results
                                    validation_result = result.get("validation_result", {})
                                    copied_url = result.get("copied_url", "")
                                    
                                    if validation_result:
                                        summary = validation_result.get("summary", {})
                                        fixes = summary.get("total_fixes", 0)
                                        issues = summary.get("total_issues", 0)
                                        
                                        df.loc[idx, f'{category}_validation_fixes'] = fixes
                                        df.loc[idx, f'{category}_validation_issues'] = issues
                                        
                                        # Create summary text
                                        summary_parts = []
                                        if fixes > 0:
                                            summary_parts.append(f"🔧 {fixes} fixes")
                                        if issues > 0:
                                            summary_parts.append(f"⚠️ {issues} issues")
                                        
                                        summary_text = "; ".join(summary_parts) if summary_parts else "No issues"
                                        df.loc[idx, f'{category}_validation_summary'] = summary_text
                                        
                                        total_fixes += fixes
                                    
                                    if copied_url:
                                        df.loc[idx, f'{category}_copied_url'] = copied_url
                                        total_copied += 1
                                    
                                    total_processed += 1
                                break  # Only process first valid URL in each category
            
            # Save results
            progress.update(task, description="Saving results...")
            df.to_csv(output_csv, index=False)
            
        except Exception as e:
            progress.stop()
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)
        
        progress.stop()
    
    # Display results
    display_forte_results(total_processed, total_copied, total_fixes, output_csv)


def process_single_url(url: str, category: str, row_idx: int, target_folder: str, auth_secret: str, mode: str, target_format: str, progress) -> dict | None:
    """Process a single URL - validate and copy if needed."""
    try:
        # Detect if it's an Excel file
        is_excel = 'usp=drive_link' in url or '/file/d/' in url
        
        if is_excel:
            # Excel file - just copy, no validation
            if target_folder:
                try:
                    from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
                    from urarovite.utils.drive import duplicate_file_to_drive_folder
                    
                    drive_service = create_drive_service_from_encoded_creds(auth_secret)
                    folder_url = f"https://drive.google.com/drive/folders/{target_folder}"
                    
                    copy_result = duplicate_file_to_drive_folder(
                        drive_service=drive_service,
                        file_url=url,
                        folder_url=folder_url,
                        prefix_file_name=None  # Use original filename
                    )
                except Exception:
                    return None
                
                if copy_result.get("success"):
                    return {
                        "validation_result": {"summary": {"total_fixes": 0, "total_issues": 0}},
                        "copied_url": copy_result.get("url")
                    }
        else:
            # Google Sheet - validate and copy
            # For now, just do a simple validation
            validation_result = execute_validation(
                check={"id": "empty_cells", "mode": mode},
                sheet_url=url,
                auth_secret=auth_secret,
                target=target_folder,
                target_format=target_format
            )
            
            copied_url = None
            if target_folder and validation_result.get("duplicate_created"):
                # Get the copied URL from the result
                copied_url = validation_result.get("target_output", "")
            
            return {
                "validation_result": validation_result,
                "copied_url": copied_url
            }
    
    except Exception as e:
        progress.update(progress.tasks[0], description=f"Error processing {category} {row_idx}: {str(e)}")
        return None
    
    return None


def display_forte_results(total_processed: int, total_copied: int, total_fixes: int, output_csv: str) -> None:
    """Display Forte processing results."""
    console.print(f"\n[bold green]✅ Forte Processing Complete![/bold green]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("URLs Processed", str(total_processed))
    table.add_row("Files Copied", str(total_copied))
    table.add_row("Total Fixes Applied", str(total_fixes))
    table.add_row("Output CSV", output_csv)
    
    console.print("\n")
    console.print(table)
    console.print(f"\n[dim]Results saved to: {output_csv}[/dim]")


def validate_sheet(
    sheet_url: str, 
    validator_id: str | None = None, 
    mode: str = "flag",
    auth_secret: str | None = None,
    output_format: str = "table"
) -> None:
    """Validate a Google Sheet."""
    
    # Get auth credentials
    if not auth_secret:
        auth_secret = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
        if not auth_secret:
            console.print("[bold red]Error:[/bold red] No authentication credentials provided.")
            console.print("Create a .env file with: URAROVITE_AUTH_SECRET=your-base64-credentials")
            console.print("Or use --auth-secret parameter")
            sys.exit(1)
    
    # Determine which validators to run
    if validator_id:
        check = {"id": validator_id, "mode": mode}
        validator_name = validator_id
    else:
        # Run a common set of validators
        common_validators = ["empty_cells", "tab_names"]
        available_ids = {
            c["id"] 
            for c in get_available_validation_criteria()
        }
        validator_id = next(
            (
                v for v in common_validators 
                if v in available_ids
            ), 
            "empty_cells"
        )
        check = {"id": validator_id, "mode": mode}
        validator_name = f"default ({validator_id})"
    
    # Run validation with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Running {validator_name} validation...", total=None)
        
        try:
            result = execute_validation(
                check=check,
                sheet_url=sheet_url,
                auth_secret=auth_secret
            )
        except Exception as e:
            progress.stop()
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)
        
        progress.stop()
    
    # Display results
    if output_format == "json":
        console.print(json.dumps(result, indent=2))
    else:
        display_results_table(result, validator_name, mode)


def display_results_table(result: Dict[str, Any], validator_name: str, mode: str) -> None:
    """Display validation results in a nice table format."""
    
    # Status panel
    status = "✅ SUCCESS" if not result.get("errors") else "❌ FAILED"
    status_color = "green" if not result.get("errors") else "red"
    
    console.print(f"\n[bold {status_color}]{status}[/bold {status_color}] - {validator_name} validation ({mode} mode)")
    
    # Results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    if mode == "fix":
        table.add_row("Fixes Applied", str(result.get("fixes_applied", 0)))
    else:
        table.add_row("Issues Found", str(result.get("issues_found", 0)))
    
    table.add_row("Errors", str(len(result.get("errors", []))))
    
    if result.get("duplicate_created"):
        table.add_row("Duplicate Created", "✅ Yes")
    
    if result.get("target_output"):
        table.add_row("Output File", result["target_output"])
    
    console.print("\n")
    console.print(table)
    
    # Show errors if any
    if result.get("errors"):
        console.print("\n[bold red]Errors:[/bold red]")
        for i, error in enumerate(result["errors"], 1):
            console.print(f"  {i}. {error}")
    
    # Show summary
    if result.get("automated_log"):
        console.print(f"\n[dim]Summary: {result['automated_log']}[/dim]")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Urarovite - Google Sheets Validation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a Forte CSV file (main feature)
  urarovite process-forte "/path/to/forte_export.csv"

  # Process Forte CSV with custom output location
  urarovite process-forte "/path/to/forte_export.csv" --output "./my_results.csv"

  # Process Forte CSV with custom target folder
  urarovite process-forte "/path/to/forte_export.csv" --target "your-drive-folder-id"

  # Process with credentials directly
  urarovite process-forte "/path/to/forte_export.csv" --auth-secret "your-base64-credentials"

  # List all available validators
  urarovite list

  # Validate a single sheet
  urarovite validate "https://docs.google.com/spreadsheets/d/abc123/edit" --mode fix

Setup:
  Create a .env file in your working directory with:
    URAROVITE_AUTH_SECRET=your-base64-encoded-service-account-credentials

Environment Variables:
  URAROVITE_AUTH_SECRET    Base64-encoded service account credentials
  AUTH_SECRET              Alternative name for credentials (also supported)
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process Forte command (main feature)
    forte_parser = subparsers.add_parser("process-forte", help="Process a Forte CSV file - validate and copy Google Sheets")
    forte_parser.add_argument("csv_file", help="Path to the Forte CSV export file")
    forte_parser.add_argument(
        "--output",
        help="Output CSV file path (default: ./output/{input_name}_processed.csv)"
    )
    forte_parser.add_argument(
        "--target",
        default="1S2V36WyAkNCSByYK4H-uJazfWN56SXCD",
        help="Google Drive folder ID where files will be copied. You can use any folder ID you have access to. (default: 1S2V36WyAkNCSByYK4H-uJazfWN56SXCD)"
    )
    forte_parser.add_argument(
        "--mode",
        choices=["flag", "fix"],
        default="fix", 
        help="Validation mode: 'flag' to report issues, 'fix' to automatically fix them (default: fix)"
    )
    forte_parser.add_argument(
        "--auth-secret",
        help="Base64-encoded service account credentials (or set URAROVITE_AUTH_SECRET env var)"
    )
    forte_parser.add_argument(
        "--local",
        action="store_true",
        help="Download files locally as Excel instead of uploading to Google Sheets"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all available validation criteria")
    
    # Validate command (single sheet)
    validate_parser = subparsers.add_parser("validate", help="Validate a single Google Sheet")
    validate_parser.add_argument("sheet_url", help="Google Sheets URL to validate")
    validate_parser.add_argument(
        "--validator", 
        help="Specific validator ID to run (use 'list' command to see options)"
    )
    validate_parser.add_argument(
        "--mode", 
        choices=["flag", "fix"], 
        default="flag",
        help="Validation mode: 'flag' to report issues, 'fix' to automatically fix them (default: flag)"
    )
    validate_parser.add_argument(
        "--auth-secret",
        help="Base64-encoded service account credentials (or set URAROVITE_AUTH_SECRET env var)"
    )
    validate_parser.add_argument(
        "--output",
        choices=["table", "json"],
        default="table", 
        help="Output format (default: table)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load environment variables
    load_environment()
    
    # Show banner
    print_banner()
    
    # Handle commands
    if args.command == "process-forte":
        # Determine target format based on --local flag
        target_format = "excel" if args.local else "sheets"
        target_folder = None if args.local else args.target
        
        process_forte_csv(
            csv_file=args.csv_file,
            output_csv=args.output,
            target_folder=target_folder,
            auth_secret=args.auth_secret,
            mode=args.mode,
            target_format=target_format
        )
    elif args.command == "list":
        list_validators()
    elif args.command == "validate":
        validate_sheet(
            sheet_url=args.sheet_url,
            validator_id=args.validator,
            mode=args.mode,
            auth_secret=args.auth_secret,
            output_format=args.output
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
