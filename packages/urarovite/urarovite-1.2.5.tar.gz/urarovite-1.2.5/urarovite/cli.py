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


# Legacy convert_single_file_cli function removed - use run_util convert instead








# Legacy convert_batch_cli function removed - use run_util convert --mode batch instead


# Legacy convert_folder_batch_cli function removed - use run_util folder-batch instead


# Legacy process_forte_csv function removed - use run_util process-forte instead


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

  # Run utilities with the new CLI pattern
  urarovite run_util convert "input.xlsx" "output.xlsx"
  urarovite run_util validate "sheet_url" --validator "empty_cells" --mode fix

  # Process Forte CSV using the new utility pattern
  urarovite run_util process-forte "/path/to/forte_export.csv" --auth-secret "your-base64-credentials"

  # List all available validators
  urarovite list

  # Validate a single sheet
  urarovite validate "https://docs.google.com/spreadsheets/d/abc123/edit" --mode fix

  # Convert files using the new utility pattern
  urarovite run_util convert "input.xlsx" "output.xlsx"
  urarovite run_util convert "input.xlsx" "output.xlsx" --sheets "Sheet1,Sheet2"
  urarovite run_util convert "metadata.xlsx" "output_folder" --mode batch --link-columns "input,output"
  urarovite run_util folder-batch "./excel_files" "drive_folder_id"

Setup:
  Create a .env file in your working directory with:
    URAROVITE_AUTH_SECRET=your-base64-encoded-service-account-credentials

Environment Variables:
  URAROVITE_AUTH_SECRET    Base64-encoded service account credentials
  AUTH_SECRET              Alternative name for credentials (also supported)
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process Forte command (deprecated - use run_util process-forte instead)
    forte_parser = subparsers.add_parser(
        "process-forte",
        help="[DEPRECATED] Use 'run_util process-forte' instead",
    )

    # List command
    subparsers.add_parser("list", help="List all available validation criteria")

    # Run utility command
    run_util_parser = subparsers.add_parser(
        "run_util", help="Run utility operations with standard CLI patterns"
    )
    run_util_parser.add_argument("utility", help="Utility to run (convert, validate, etc.)")
    run_util_parser.add_argument("utility_args", nargs=argparse.REMAINDER, help="Arguments for the utility")

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

    # Add convert command group (deprecated - use run_util convert instead)
    convert_parser = subparsers.add_parser("convert", help="[DEPRECATED] Use 'run_util convert' instead")

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
        # Legacy convert command - redirect to new run_util pattern
        console.print("[yellow]⚠️  The 'convert' command is deprecated. Use 'run_util convert' instead.[/yellow]")
        console.print("\nExample:")
        console.print("  urarovite run_util convert input.xlsx output.xlsx")
        console.print("  urarovite run_util convert metadata.xlsx output_folder --mode batch --link-columns input,output")
        sys.exit(1)
        
    elif args.command == "process-forte":
        # Legacy process-forte command - redirect to new run_util pattern
        console.print("[yellow]⚠️  The 'process-forte' command is deprecated. Use 'run_util process-forte' instead.[/yellow]")
        console.print("\nExample:")
        console.print("  urarovite run_util process-forte input.csv --mode fix")
        sys.exit(1)
    elif args.command == "run_util":
        from urarovite.cli_utils import UtilityRegistry, run_utility_cli
        
        registry = UtilityRegistry()
        utility = registry.get_utility(args.utility)
        
        if not utility:
            console.print(f"[red]❌ Unknown utility: {args.utility}[/red]")
            console.print("\n[bold]Available utilities:[/bold]")
            for util_name in registry.list_utilities():
                util = registry.get_utility(util_name)
                console.print(f"  [cyan]{util_name}[/cyan]: {util.description}")
            sys.exit(1)
        
        # Run the utility with the provided arguments
        run_utility_cli(utility, args.utility_args)
        
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
