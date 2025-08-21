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
from typing import Any, Dict, List, Optional, Union, get_args, get_origin
import inspect
import json as json_lib

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from urarovite import (
    get_available_validation_criteria,
    execute_validation,
)
from urarovite.validators import get_validator_registry
from urarovite.utils.generic_spreadsheet import (
    convert_google_sheets_to_excel,
)
from urarovite.utils.simple_converter import (
    convert_single_file,
    convert_batch_from_metadata,
    convert_folder_batch,
)


console = Console()


def load_environment() -> None:
    """Load environment variables from .env file and show helpful messages."""
    # Try to load .env file
    env_loaded = load_dotenv()

    if env_loaded:
        console.print("[dim]✅ Loaded environment variables from .env file[/dim]")
    else:
        console.print(
            "[dim]💡 No .env file found - you can create one with your credentials[/dim]"
        )

    # Check if auth credentials are available
    auth_secret = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
    if auth_secret:
        console.print("[dim]🔐 Authentication credentials loaded[/dim]")
    else:
        console.print("[yellow]⚠️  No authentication credentials found[/yellow]")
        console.print(
            "[dim]   Create a .env file with: URAROVITE_AUTH_SECRET=your-base64-credentials[/dim]"
        )


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
    console.print(
        Panel(banner, title="Google Sheets Validator", border_style="bright_blue")
    )


def list_validators() -> None:
    """List all available validation criteria."""
    console.print(
        "\n[bold bright_blue]Available Validation Criteria:[/bold bright_blue]\n"
    )

    criteria = get_available_validation_criteria()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")

    for criterion in criteria:
        table.add_row(
            criterion["id"],
            criterion["name"],
            criterion.get("description", "No description available"),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(criteria)} validators available[/dim]")


def convert_single_file_cli(
    input_file: str,
    output_path: str | None = None,
    auth_secret: str | None = None,
    subject: str | None = None,
    sheet_names: str | None = None,
    output_folder: str | None = None,
    drive_folder_id: str | None = None,
    output_filename: str | None = None,
) -> None:
    """Convert a single Google Sheet or Excel file to another format.
    
    Args:
        input_file: Google Sheets URL or local Excel file path to convert
        output_path: Path where converted file should be saved (optional)
        auth_secret: Base64 encoded service account credentials
        subject: Optional email for domain-wide delegation
        sheet_names: Comma-separated list of sheet names to convert (optional)
        output_folder: Optional folder path for output (overrides output_path if provided)
        drive_folder_id: Optional Google Drive folder ID for creating new Google Sheets
        output_filename: Optional custom filename for output (without extension)
    """
    try:
        # Build auth credentials
        auth_credentials = {}
        if auth_secret:
            auth_credentials["auth_secret"] = auth_secret
        else:
            # Try env fallback
            fallback = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
            if fallback:
                auth_credentials["auth_secret"] = fallback
            else:
                console.print("[red]❌ No authentication credentials found[/red]")
                console.print("[dim]Set URAROVITE_AUTH_SECRET env var or use --auth-secret[/dim]")
                sys.exit(1)
        
        if subject:
            auth_credentials["subject"] = subject
        
        # Parse sheet names if provided
        sheets_list = None
        if sheet_names:
            sheets_list = [name.strip() for name in sheet_names.split(",")]
        
        # Handle default output paths
        if not output_path and not output_folder:
            if input_file.startswith("http") and "docs.google.com" in input_file:
                # Google Sheets → Excel: Default to current directory with auto-generated filename
                from urarovite.utils.sheets import extract_sheet_id
                sheet_id = extract_sheet_id(input_file)
                
                if output_filename:
                    filename = f"{output_filename}.xlsx"
                else:
                    filename = f"sheet_{sheet_id}.xlsx"
                
                output_path = f"./{filename}"
                console.print(f"[dim]No output path specified, using: {output_path}[/dim]")
            else:
                # Excel → Google Sheets: Use "auto" to create new sheet
                output_path = "auto"
                console.print(f"[dim]No output path specified, creating new Google Sheet[/dim]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Determine conversion direction for progress message
            if input_file.startswith("http") and "docs.google.com" in input_file:
                progress_msg = "Converting Google Sheet to Excel..."
            else:
                progress_msg = "Converting Excel to Google Sheets..."
            
            task = progress.add_task(progress_msg, total=None)
            
            result = convert_single_file(
                input_file=input_file,
                output_path=output_path,
                auth_credentials=auth_credentials,
                sheet_names=sheets_list,
                output_folder=output_folder,
                drive_folder_id=drive_folder_id,
                output_filename=output_filename,
            )
            
            progress.update(task, completed=True)
        
        if result["success"]:
            if "output_path" in result and result["output_path"]:
                console.print(f"[green]✅ Successfully converted to {result['output_path']}[/green]")
            elif "output_url" in result and result["output_url"]:
                console.print(f"[green]✅ Successfully converted to Google Sheets: {result['output_url']}[/green]")
            else:
                console.print(f"[green]✅ Successfully converted to Google Sheets[/green]")
            console.print(f"[dim]Converted sheets: {', '.join(result['converted_sheets'])}[/dim]")
        else:
            console.print(f"[red]❌ Conversion failed: {result['error']}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)








def convert_batch_cli(
    metadata_file: str,
    output_location: str,
    auth_secret: str | None = None,
    subject: str | None = None,
    link_columns: str = "",
    output_format: str = "excel",
) -> None:
    """Batch convert multiple sheets/files based on links in specified columns.
    
    Args:
        metadata_file: Google Sheets URL or local Excel file path containing metadata
        output_location: Directory (for Excel output) or Google Drive folder URL (for Sheets output)
        auth_secret: Base64 encoded service account credentials
        subject: Optional email for domain-wide delegation
        link_columns: Comma-separated list of column names containing links to convert
        output_format: Output format - "excel" or "sheets"
    """
    try:
        # Build auth credentials
        auth_credentials = {}
        if auth_secret:
            auth_credentials["auth_secret"] = auth_secret
        else:
            # Try env fallback
            fallback = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
            if fallback:
                auth_credentials["auth_secret"] = fallback
            else:
                console.print("[red]❌ No authentication credentials found[/red]")
                console.print("[dim]Set URAROVITE_AUTH_SECRET env var or use --auth-secret[/dim]")
                sys.exit(1)
        
        if subject:
            auth_credentials["subject"] = subject
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing batch conversion...", total=None)
            
            # Parse link columns
            link_columns_list = [col.strip() for col in link_columns.split(",") if col.strip()]
            if not link_columns_list:
                console.print("[red]❌ No link columns specified. Use --link-columns to specify column names.[/red]")
                sys.exit(1)
            
            result = convert_batch_from_metadata(
                metadata_file=metadata_file,
                output_location=output_location,
                auth_credentials=auth_credentials,
                link_columns=link_columns_list,
                output_format=output_format,
            )
            
            progress.update(task, completed=True)
        
        if result["success"]:
            console.print(f"[green]✅ Batch conversion completed![/green]")
            console.print(f"[dim]Output location: {result['output_location']}[/dim]")
            console.print(f"[dim]Successful: {result['success_count']}, Failed: {result['failure_count']}[/dim]")
            
            # Show details of failed conversions if any
            if result["failed_conversions"]:
                console.print("\n[yellow]Failed conversions:[/yellow]")
                for failure in result["failed_conversions"][:5]:  # Show first 5 failures
                    console.print(f"  [dim]Row {failure['row']}: {failure['error']}[/dim]")
                if len(result["failed_conversions"]) > 5:
                    console.print(f"  [dim]... and {len(result['failed_conversions']) - 5} more[/dim]")
        else:
            console.print(f"[red]❌ Batch conversion failed: {result['error']}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)


def convert_folder_batch_cli(
    input_folder: str,
    drive_folder_id: str,
    auth_secret: str | None = None,
    subject: str | None = None,
    input_column_name: str = "input_url",
    output_column_name: str = "output_url",
    metadata_sheet_name: str = "conversion_metadata",
) -> None:
    """Convert all Excel files in a folder to Google Sheets and create a metadata sheet.
    
    Args:
        input_folder: Local folder containing Excel files to convert
        drive_folder_id: Google Drive folder ID where converted sheets will be created
        auth_secret: Base64 encoded service account credentials
        subject: Optional email for domain-wide delegation
        input_column_name: Name for the input file column in metadata sheet
        output_column_name: Name for the output URL column in metadata sheet
        metadata_sheet_name: Name for the metadata sheet to create
    """
    try:
        # Build auth credentials
        auth_credentials = {}
        if auth_secret:
            auth_credentials["auth_secret"] = auth_secret
        else:
            # Try env fallback
            fallback = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
            if fallback:
                auth_credentials["auth_secret"] = fallback
            else:
                console.print("[red]❌ No authentication credentials found[/red]")
                console.print("[dim]Set URAROVITE_AUTH_SECRET env var or use --auth-secret[/dim]")
                sys.exit(1)
        
        if subject:
            auth_credentials["subject"] = subject
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Converting folder of Excel files to Google Sheets...", total=None)
            
            result = convert_folder_batch(
                input_folder=input_folder,
                drive_folder_id=drive_folder_id,
                auth_credentials=auth_credentials,
                input_column_name=input_column_name,
                output_column_name=output_column_name,
                metadata_sheet_name=metadata_sheet_name,
            )
            
            progress.update(task, completed=True)
        
        if result["success"]:
            console.print(f"[green]✅ Successfully converted {result['successful_conversions']} of {result['total_files']} Excel files[/green]")
            if result["failed_conversions"] > 0:
                console.print(f"[yellow]⚠️  {result['failed_conversions']} files failed to convert[/yellow]")
            console.print(f"[green]📊 Metadata sheet created: {result['metadata_sheet_url']}[/green]")
        else:
            console.print(f"[red]❌ Folder conversion failed: {result['error']}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)


def process_forte_csv(
    csv_file: str,
    output_csv: str | None = None,
    target_folder: str = "1S2V36WyAkNCSByYK4H-uJazfWN56SXCD",
    auth_secret: str | None = None,
    mode: str = "fix",
    target_format: str = "sheets",
) -> None:
    """Process a Forte CSV file - validate and copy Google Sheets using shared processing logic."""

    # Load environment variables from .env if available
    load_environment()

    # Expand user path and validate input file
    csv_file = os.path.expanduser(csv_file)

    if not os.path.exists(csv_file):
        console.print(f"[bold red]Error:[/bold red] CSV file not found: {csv_file}")
        console.print(f"[dim]Looking for:[/dim] {os.path.abspath(csv_file)}")

        # Suggest alternatives
        downloads_dir = os.path.expanduser("~/Downloads")
        if os.path.exists(downloads_dir):
            forte_files = [
                f
                for f in os.listdir(downloads_dir)
                if "forte" in f.lower() and f.endswith(".csv")
            ]
            if forte_files:
                console.print(
                    "\n[blue]💡 Found these Forte CSV files in ~/Downloads:[/blue]"
                )
                for f in forte_files:
                    console.print(f"   [cyan]- {f}[/cyan]")
                console.print(
                    f'\n[dim]Try: python process_forte.py ~/Downloads/"{forte_files[0]}"[/dim]'
                )
        sys.exit(1)

    if not os.path.isfile(csv_file):
        console.print(f"[bold red]Error:[/bold red] Path is not a file: {csv_file}")
        sys.exit(1)

    if os.path.getsize(csv_file) == 0:
        console.print(f"[bold red]Error:[/bold red] CSV file is empty: {csv_file}")
        sys.exit(1)

    # Get auth credentials with better error messaging
    if not auth_secret:
        auth_secret = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
        if not auth_secret:
            console.print(
                "[bold red]Error:[/bold red] No authentication credentials provided."
            )
            console.print("Solutions:")
            console.print(
                "  1. Create a .env file with: AUTH_SECRET=your-base64-credentials"
            )
            console.print(
                "  2. Set environment variable: export AUTH_SECRET=your-credentials"
            )
            console.print("  3. Use --auth-secret parameter")
            console.print(
                "\n[dim]Tip: Make sure your service account has Google Sheets and Drive permissions[/dim]"
            )
            sys.exit(1)

    # Set default output file with timestamp
    if not output_csv:
        from datetime import datetime

        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_csv = f"./output/{base_name}_processed_{timestamp}.csv"

    # Ensure output directory exists
    output_dir = os.path.dirname(output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    console.print(
        f"\n[bold bright_blue]Processing Forte CSV:[/bold bright_blue] {csv_file}"
    )
    console.print(
        f"[bold bright_blue]Target folder:[/bold bright_blue] {target_folder}"
    )
    console.print(f"[bold bright_blue]Output CSV:[/bold bright_blue] {output_csv}")
    console.print(f"[bold bright_blue]Mode:[/bold bright_blue] {mode}")

    # Use shared processing logic with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing Forte CSV file...", total=None)

        try:
            # Import API function instead of direct processing function
            from urarovite.core.api import process_forte_csv_batch
            from urarovite.utils.forte_processing import generate_summary_report

            progress.update(task, description="Processing CSV through API...")

            # Call API function instead of direct processing function
            result = process_forte_csv_batch(
                csv_file_path=csv_file,
                auth_secret=auth_secret,
                target_folder_id=target_folder,
                subject=None,  # CLI doesn't support subject parameter yet
                validation_mode=mode,
                preserve_visual_formatting=True,
                output_file_path=output_csv,
            )

            progress.update(task, description="Processing complete!")

        except Exception as e:
            progress.stop()
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)

        progress.stop()

    # Display results using shared prettified summary generation
    summary_report = generate_summary_report(result)
    print(summary_report)  # Print directly to show colors and formatting

    if not result["success"]:
        sys.exit(1)


def _kebabize(name: str) -> str:
    return name.replace("_", "-")


def _parse_list_value(raw: str, subtype: type) -> list:
    # accept comma-separated or space-separated values; also JSON list
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        try:
            parsed = json_lib.loads(raw)
            if isinstance(parsed, list):
                return [subtype(v) for v in parsed]
        except Exception:
            pass
    parts = []
    for token in raw.replace(",", " ").split():
        parts.append(subtype(token))
    return parts


def _add_typed_argument(parser: argparse.ArgumentParser, param_name: str, annotation: Any, default: Any) -> None:
    kebab = _kebabize(param_name)
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Booleans: expose --foo / --no-foo toggles
    if annotation is bool or origin is bool:
        group = parser.add_mutually_exclusive_group()
        group.add_argument(f"--{kebab}", dest=param_name, action="store_true", help=f"Enable {param_name}")
        group.add_argument(f"--no-{kebab}", dest=param_name, action="store_false", help=f"Disable {param_name}")
        parser.set_defaults(**{param_name: default if default is not inspect._empty else False})
        return

    # Optional[T] -> treat as underlying type with default None
    if origin is Union and type(None) in args:
        inner = next((a for a in args if a is not type(None)), str)
        return _add_typed_argument(
            parser,
            param_name,
            inner,
            default if default is not inspect._empty else None,
        )

    # List[T]
    if origin in (list, List):
        subtype = args[0] if args else str
        if subtype in (int, float, str):
            parser.add_argument(
                f"--{kebab}",
                dest=param_name,
                type=str,
                help=f"List for {param_name} (comma- or space-separated or JSON list)",
            )
            parser.set_defaults(**{param_name: default if default is not inspect._empty else None})
            return

    # Dict[...] via JSON input
    if origin in (dict, Dict):
        parser.add_argument(
            f"--{kebab}",
            dest=param_name,
            type=str,
            help=f"JSON for {param_name}",
        )
        parser.set_defaults(**{param_name: default if default is not inspect._empty else None})
        return

    # Fallback scalar types
    arg_type = str
    if annotation in (int, float, str):
        arg_type = annotation
    parser.add_argument(
        f"--{kebab}", dest=param_name, type=arg_type, default=None if default is inspect._empty else default, help=f"{param_name}"
    )


def _collect_validator_params(validator: Any) -> list:
    sig = inspect.signature(validator.validate)
    params = []
    for name, p in sig.parameters.items():
        if name in {"self", "spreadsheet_source", "mode", "auth_credentials", "kwargs"}:
            continue
        if p.kind in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL):
            continue
        params.append((name, p.annotation, p.default))
    return params


def _coerce_extra_arg(val: Any, annotation: Any) -> Any:
    if val is None:
        return None
    origin = get_origin(annotation)
    args = get_args(annotation)

    if annotation is bool or origin is bool:
        return bool(val)
    if origin in (list, List):
        subtype = args[0] if args else str
        if isinstance(val, list):
            return [subtype(v) for v in val]
        return _parse_list_value(str(val), subtype)
    if origin in (dict, Dict):
        if isinstance(val, dict):
            return val
        try:
            return json_lib.loads(str(val))
        except Exception:
            return {}
    # Optional[T]
    if origin is Union and type(None) in args:
        inner = next((a for a in args if a is not type(None)), str)
        return _coerce_extra_arg(val, inner)
    if annotation in (int, float, str):
        try:
            return annotation(val)
        except Exception:
            return val
    # Fallback
    return val


def register_validator_commands(subparsers: argparse._SubParsersAction) -> Dict[str, Dict[str, Any]]:
    """Dynamically create a subcommand for each validator.

    Returns a mapping of validator_id -> metadata with extras list.
    """
    registry = get_validator_registry()
    meta: Dict[str, Dict[str, Any]] = {}
    for validator_id, validator in registry.items():
        parser = subparsers.add_parser(
            validator_id,
            help=validator.description or validator.name,
            description=f"{validator.name}: {validator.description}",
        )
        parser.add_argument(
            "spreadsheet_source",
            help="Google Sheets URL or Excel file path to validate",
        )
        parser.add_argument(
            "--mode",
            choices=["flag", "fix"],
            required=True,
            help="Validation mode",
        )
        parser.add_argument(
            "--auth-secret",
            dest="auth_secret",
            help="Base64-encoded service account credentials (required for Google Sheets)",
        )
        parser.add_argument(
            "--subject",
            help="Delegation subject email (optional, Google Workspace domain-wide delegation)",
        )
        parser.add_argument(
            "--output",
            choices=["table", "json"],
            default="table",
            help="Output format",
        )
        parser.add_argument(
            "--params",
            dest="_extra_params_json",
            type=str,
            help="Additional parameters as JSON (merged into validator kwargs)",
        )

        # Add validator-specific params
        extras: List[str] = []
        for name, annotation, default in _collect_validator_params(validator):
            try:
                _add_typed_argument(parser, name, annotation, default)
                extras.append(name)
            except Exception:
                # Fallback to string option
                parser.add_argument(f"--{_kebabize(name)}", dest=name, type=str)
                extras.append(name)

        meta[validator_id] = {"validator": validator, "extras": extras}
    return meta


def validate_sheet(
    sheet_url: str,
    validator_id: str | None = None,
    mode: str = "flag",
    auth_secret: str | None = None,
    output_format: str = "table",
) -> None:
    """Validate a Google Sheet."""

    # Get auth credentials
    if not auth_secret:
        auth_secret = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
        if not auth_secret:
            console.print(
                "[bold red]Error:[/bold red] No authentication credentials provided."
            )
            console.print(
                "Create a .env file with: URAROVITE_AUTH_SECRET=your-base64-credentials"
            )
            console.print("Or use --auth-secret parameter")
            sys.exit(1)

    # Determine which validators to run
    if validator_id:
        check = {"id": validator_id, "mode": mode}
        validator_name = validator_id
    else:
        # Run a common set of validators
        common_validators = ["empty_cells", "tab_names"]
        available_ids = {c["id"] for c in get_available_validation_criteria()}
        validator_id = next(
            (v for v in common_validators if v in available_ids), "empty_cells"
        )
        check = {"id": validator_id, "mode": mode}
        validator_name = f"default ({validator_id})"

    # Run validation with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Running {validator_name} validation...", total=None)

        try:
            result = execute_validation(
                check=check, sheet_url=sheet_url, auth_secret=auth_secret
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


def display_results_table(
    result: Dict[str, Any], validator_name: str, mode: str
) -> None:
    """Display validation results in a nice table format."""

    # Status panel
    status = "✅ SUCCESS" if not result.get("errors") else "❌ FAILED"
    status_color = "green" if not result.get("errors") else "red"

    console.print(
        f"\n[bold {status_color}]{status}[/bold {status_color}] - {validator_name} validation ({mode} mode)"
    )

    # Results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    if mode == "fix":
        table.add_row("Fixes Applied", str(result.get("fixes_applied", 0)))
    else:
        table.add_row("Flags Found", str(result.get("flags_found", 0)))

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

  # Convert single Google Sheet to Excel
  urarovite convert single "https://docs.google.com/spreadsheets/d/abc123/edit" "./output.xlsx"
  
  # Convert to output folder (auto-generates filename)
  urarovite convert single "https://docs.google.com/spreadsheets/d/abc123/edit" "./dummy.xlsx" --output-folder "./converted_files/"

  # Convert Excel to Google Sheets
  urarovite convert single "./input.xlsx" "https://docs.google.com/spreadsheets/d/xyz789/edit"

  # Batch convert sheets from links in specified columns
  urarovite convert batch "https://docs.google.com/spreadsheets/d/metadata123/edit" "./converted_files/" --link-columns "input_files,output_files"

Setup:
  Create a .env file in your working directory with:
    URAROVITE_AUTH_SECRET=your-base64-encoded-service-account-credentials

Environment Variables:
  URAROVITE_AUTH_SECRET    Base64-encoded service account credentials
  AUTH_SECRET              Alternative name for credentials (also supported)
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process Forte command (main feature)
    forte_parser = subparsers.add_parser(
        "process-forte",
        help="Process a Forte CSV file - validate and copy Google Sheets",
    )
    forte_parser.add_argument("csv_file", help="Path to the Forte CSV export file")
    forte_parser.add_argument(
        "--output",
        help="Output CSV file path (default: ./output/{input_name}_processed.csv)",
    )
    forte_parser.add_argument(
        "--target",
        default="1S2V36WyAkNCSByYK4H-uJazfWN56SXCD",
        help="Google Drive folder ID where files will be copied. You can use any folder ID you have access to. (default: 1S2V36WyAkNCSByYK4H-uJazfWN56SXCD)",
    )
    forte_parser.add_argument(
        "--mode",
        choices=["flag", "fix"],
        default="fix",
        help="Validation mode: 'flag' to report flags, 'fix' to automatically fix them (default: fix)",
    )
    forte_parser.add_argument(
        "--auth-secret",
        help="Base64-encoded service account credentials (or set URAROVITE_AUTH_SECRET env var)",
    )
    forte_parser.add_argument(
        "--local",
        action="store_true",
        help="Download files locally as Excel instead of uploading to Google Sheets",
    )

    # List command
    subparsers.add_parser("list", help="List all available validation criteria")

    # Validate command (single sheet)
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a single Google Sheet"
    )
    validate_parser.add_argument("sheet_url", help="Google Sheets URL to validate")
    validate_parser.add_argument(
        "--validator",
        help="Specific validator ID to run (use 'list' command to see options)",
    )
    validate_parser.add_argument(
        "--mode",
        choices=["flag", "fix"],
        default="flag",
        help="Validation mode: 'flag' to report flags, 'fix' to automatically fix them (default: flag)",
    )
    validate_parser.add_argument(
        "--auth-secret",
        help="Base64-encoded service account credentials (or set URAROVITE_AUTH_SECRET env var)",
    )
    validate_parser.add_argument(
        "--output",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    # Add convert command group
    convert_parser = subparsers.add_parser("convert", help="Convert between Google Sheets and Excel")
    convert_subparsers = convert_parser.add_subparsers(dest="convert_command", help="Conversion operations")
    
    # Convert single file (Google Sheets or Excel)
    single_file_parser = convert_subparsers.add_parser(
        "single", 
        help="Convert a single Google Sheet or Excel file to another format"
    )
    single_file_parser.add_argument(
        "input_file", 
        help="Google Sheets URL or local Excel file path to convert"
    )
    single_file_parser.add_argument(
        "output_path", 
        nargs="?",
        help="Path where converted file should be saved (optional - defaults to current directory for Excel output, creates new sheet for Google Sheets output)"
    )
    single_file_parser.add_argument(
        "--output-folder",
        help="Output folder path (overrides output_path, generates automatic filename)"
    )
    single_file_parser.add_argument(
        "--auth-secret",
        help="Base64-encoded service account credentials (or set URAROVITE_AUTH_SECRET env var)"
    )
    single_file_parser.add_argument(
        "--subject",
        help="Email for domain-wide delegation (optional)"
    )
    single_file_parser.add_argument(
        "--sheets",
        help="Comma-separated list of sheet names to convert (optional, converts all if not specified)"
    )
    single_file_parser.add_argument(
        "--drive-folder-id",
        help="Google Drive folder ID for creating new Google Sheets (optional, helps avoid access issues)"
    )
    single_file_parser.add_argument(
        "--output-filename",
        help="Custom filename for output (without extension, e.g., 'my_data' becomes 'my_data.xlsx')"
    )
    

    
    # Batch conversion from metadata file
    batch_parser = convert_subparsers.add_parser(
        "batch",
        help="Batch convert multiple sheets/files based on links in specified columns"
    )
    batch_parser.add_argument(
        "metadata_file",
        help="Google Sheets URL or local Excel file path containing metadata"
    )
    batch_parser.add_argument(
        "output_location",
        help="Directory (for Excel output) or Google Drive folder URL (for Sheets output)"
    )
    batch_parser.add_argument(
        "--link-columns",
        required=True,
        help="Comma-separated list of column names containing links to convert (e.g., 'input_files,output_files')"
    )
    batch_parser.add_argument(
        "--output-format",
        choices=["excel", "sheets"],
        default="excel",
        help="Output format (default: excel)"
    )
    batch_parser.add_argument(
        "--auth-secret",
        help="Base64-encoded service account credentials (or set URAROVITE_AUTH_SECRET env var)"
    )
    batch_parser.add_argument(
        "--subject",
        help="Email for domain-wide delegation (optional)"
    )
    
    # Folder batch conversion
    folder_batch_parser = convert_subparsers.add_parser(
        "folder-batch",
        help="Convert all Excel files in a folder to Google Sheets and create a metadata sheet"
    )
    folder_batch_parser.add_argument(
        "input_folder",
        help="Local folder containing Excel files to convert"
    )
    folder_batch_parser.add_argument(
        "drive_folder_id",
        help="Google Drive folder ID where converted sheets will be created"
    )
    folder_batch_parser.add_argument(
        "--input-column-name",
        default="input_url",
        help="Name for the input file column in metadata sheet (default: input_url)"
    )
    folder_batch_parser.add_argument(
        "--output-column-name",
        default="output_url",
        help="Name for the output URL column in metadata sheet (default: output_url)"
    )
    folder_batch_parser.add_argument(
        "--metadata-sheet-name",
        default="conversion_metadata",
        help="Name for the metadata sheet to create (default: conversion_metadata)"
    )
    folder_batch_parser.add_argument(
        "--auth-secret",
        help="Base64-encoded service account credentials (or set URAROVITE_AUTH_SECRET env var)"
    )
    folder_batch_parser.add_argument(
        "--subject",
        help="Email for domain-wide delegation (optional)"
    )

    # Register dynamic validator subcommands before parsing
    validator_meta = register_validator_commands(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Load environment variables
    load_environment()

    # Show banner
    print_banner()

    # Handle commands
    if args.command in validator_meta:
        v = validator_meta[args.command]["validator"]
        extras = validator_meta[args.command]["extras"]

        # Build auth credentials
        auth_credentials: Dict[str, Any] = {}
        if getattr(args, "auth_secret", None):
            auth_credentials["auth_secret"] = args.auth_secret
        else:
            # Try env fallback
            fallback = os.getenv("URAROVITE_AUTH_SECRET") or os.getenv("AUTH_SECRET")
            if fallback:
                auth_credentials["auth_secret"] = fallback
        if getattr(args, "subject", None):
            auth_credentials["subject"] = args.subject

        # Collect extra kwargs typed
        extra_kwargs: Dict[str, Any] = {}
        for name, annotation, default in _collect_validator_params(v):
            if not hasattr(args, name):
                continue
            raw_val = getattr(args, name)
            if raw_val is None:
                continue
            extra_kwargs[name] = _coerce_extra_arg(raw_val, annotation)

        # Merge JSON params if provided
        if getattr(args, "_extra_params_json", None):
            try:
                j = json_lib.loads(args._extra_params_json)
                if isinstance(j, dict):
                    # Do not override explicitly provided flags
                    for k, v in j.items():
                        if k not in extra_kwargs:
                            extra_kwargs[k] = v
            except Exception:
                console.print("[yellow]⚠️  Ignoring invalid --params JSON[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Running {args.command} validation...", total=None)
            try:
                result = v.validate(
                    spreadsheet_source=args.spreadsheet_source,
                    mode=args.mode,
                    auth_credentials=auth_credentials or None,
                    **extra_kwargs,
                )
            except Exception as e:
                progress.stop()
                console.print(f"[bold red]Error:[/bold red] {str(e)}")
                sys.exit(1)

        if args.output == "json":
            console.print(json_lib.dumps(result, indent=2))
        else:
            display_results_table(result, v.name or args.command, args.mode)
        return

    if args.command == "convert":
        if args.convert_command == "single":
            convert_single_file_cli(
                input_file=args.input_file,
                output_path=args.output_path,
                auth_secret=args.auth_secret,
                subject=args.subject,
                sheet_names=args.sheets,
                output_folder=args.output_folder,
                drive_folder_id=args.drive_folder_id,
                output_filename=args.output_filename,
            )

        elif args.convert_command == "batch":
            convert_batch_cli(
                metadata_file=args.metadata_file,
                output_location=args.output_location,
                auth_secret=args.auth_secret,
                subject=args.subject,
                link_columns=args.link_columns,
                output_format=args.output_format,
            )
        elif args.convert_command == "folder-batch":
            convert_folder_batch_cli(
                input_folder=args.input_folder,
                drive_folder_id=args.drive_folder_id,
                auth_secret=args.auth_secret,
                subject=args.subject,
                input_column_name=args.input_column_name,
                output_column_name=args.output_column_name,
                metadata_sheet_name=args.metadata_sheet_name,
            )
        else:
            convert_parser.print_help()
            sys.exit(1)
    elif args.command == "process-forte":
        # Determine target format based on --local flag
        target_format = "excel" if args.local else "sheets"
        target_folder = None if args.local else args.target

        process_forte_csv(
            csv_file=args.csv_file,
            output_csv=args.output,
            target_folder=target_folder,
            auth_secret=args.auth_secret,
            mode=args.mode,
            target_format=target_format,
        )
    elif args.command == "list":
        list_validators()
    elif args.command == "validate":
        validate_sheet(
            sheet_url=args.sheet_url,
            validator_id=args.validator,
            mode=args.mode,
            auth_secret=args.auth_secret,
            output_format=args.output,
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
