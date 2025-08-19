"""
Command-line interface for Urarovite library.

This script provides a CLI for running
validations on Google Sheets or Excel files.
"""

from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd

# New API imports
from urarovite import get_available_validation_criteria

from urarovite.auth import create_sheets_service_from_encoded_creds
from urarovite.utils.sheets import extract_sheet_id


def ensure_sheets_service(encoded_creds: str, subject: str | None = None) -> bool:
    """Ensure OAuth credentials for Google Sheets API using base64 encoded credentials.

    Updated to use the new auth module structure.

    Returns True if credentials were successfully initialized, else False.

    Args:
        encoded_creds: Base64 encoded service account JSON
        subject: Optional email for domain-wide delegation
    """
    try:
        create_sheets_service_from_encoded_creds(encoded_creds, subject)
        print("🔐 OAuth credentials ready for Google Sheets API.")
        return True
    except Exception as e:
        print("❌ Failed to obtain OAuth credentials:", e)
        print(
            "   Ensure the base64 encoded credentials are valid and properly configured."
        )
        return False


def demonstrate_new_api() -> None:
    """Demonstrate the new validation API."""
    print("\n" + "=" * 70)
    print("🚀 NEW VALIDATION API DEMONSTRATION")
    print("=" * 70)

    # 1. Show available validation criteria
    print("\n1. Available Validation Criteria:")
    print("-" * 50)
    criteria = get_available_validation_criteria()

    for i, criterion in enumerate(criteria, 1):
        print(f"  {i:2d}. {criterion['name']} (id: {criterion['id']})")

    print(f"\n   Total available validators: {len(criteria)}")

    # 2. Example validation configuration
    print("\n2. Example Validation Configuration:")
    print("-" * 50)

    example_checks = [
        {"id": "empty_cells", "mode": "fix"},
        {"id": "tab_names", "mode": "fix"},
    ]

    print("   Validation checks to run:")
    for check in example_checks:
        mode_desc = (
            "🔧 Fix automatically" if check["mode"] == "fix" else "🔍 Flag flags only"
        )
        validator_name = next(
            (c["name"] for c in criteria if c["id"] == check["id"]), check["id"]
        )
        print(f"     • {validator_name} - {mode_desc}")

    # 3. Integration example
    print("\n3. Integration with Uvarolite System:")
    print("-" * 50)
    print("   The library provides the exact API required:")
    print()
    print("   ```python")
    print(
        "   from urarovite import get_available_validation_criteria, execute_validation"
    )
    print()
    print("   # Get available options")
    print("   criteria = get_available_validation_criteria()")
    print()
    print("   # Execute validations")
    print("   checks = [{'id': 'empty_cells', 'mode': 'fix'}]")
    print("   result = execute_validation(checks, sheet_url, auth_secret)")
    print("   ```")
    print()
    print("   Returns: {'fixes_applied': N, 'flags_flagged': N, 'errors': [...]}")


def analyze_sample_data() -> pd.DataFrame:
    """Load and analyze sample data, returning it for further processing."""
    print("\n" + "=" * 70)
    print("📊 SAMPLE DATA ANALYSIS")
    print("=" * 70)

    data_file = Path("_data-projects/data_cleaning_targeted.csv")
    if not data_file.exists():
        print(f"❌ Sample data file not found: {data_file}")
        print("   Please ensure you're running from the project root directory")
        sys.exit(1)

    print(f"\n🔍 Loading sample data from {data_file}...")
    df: pd.DataFrame = pd.read_csv(data_file)  # type: ignore[no-untyped-call]
    print(f"   Loaded {len(df)} rows")
    print(f"   Columns: {list(df.columns)}")

    # Check data quality
    required_cols = [
        "verification_field_ranges",
        "input_sheet_url",
        "example_output_sheet_url",
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        sys.exit(1)

    # Analyze data completeness
    df_with_ranges = df[
        df["verification_field_ranges"].notna()
        & (df["verification_field_ranges"] != "")
    ]

    df_with_urls = df[df["input_sheet_url"].notna() & (df["input_sheet_url"] != "")]

    print(f"   Rows with verification ranges: {len(df_with_ranges)}")
    print(f"   Rows with input sheet URLs: {len(df_with_urls)}")

    if len(df_with_ranges) == 0:
        print("❌ No rows found with verification_field_ranges data")
        sys.exit(1)

    return df_with_ranges


def demonstrate_sheet_analysis(df: pd.DataFrame) -> None:
    """Demonstrate sheet analysis using the new utility functions."""
    print("\n" + "=" * 70)
    print("🔗 GOOGLE SHEETS ANALYSIS")
    print("=" * 70)

    # Analyze first few URLs
    sample_size = min(3, len(df))
    print(f"\n📋 Analyzing first {sample_size} Google Sheets URLs...")

    for i in range(sample_size):
        row = df.iloc[i]
        sheet_url = row.get("input_sheet_url", "")
        task_id = row.get("task_id", "N/A")

        print(f"\n   Row {i + 1} (Task ID: {task_id}):")
        print(f"     URL: {sheet_url[:80]}{'...' if len(sheet_url) > 80 else ''}")

        # Extract sheet ID using new utility
        sheet_id = extract_sheet_id(sheet_url)
        if sheet_id:
            print(f"     Sheet ID: {sheet_id}")
            print("     ✅ Valid Google Sheets URL")
        else:
            print("     ❌ Invalid or malformed URL")

        # Show verification ranges
        ranges = row.get("verification_field_ranges", "")
        if ranges:
            print(
                f"     Verification ranges: {ranges[:60]}{'...' if len(ranges) > 60 else ''}"
            )


def main() -> None:
    """Main application entry point with comprehensive demonstration."""
    print("🌟 URAROVITE VALIDATION LIBRARY")

    # 1. Demonstrate new validation API
    demonstrate_new_api()

    # 2. Load and analyze sample data
    df_with_ranges = analyze_sample_data()

    # 3. Demonstrate Google Sheets analysis
    demonstrate_sheet_analysis(df_with_ranges)

    # 4. Setup OAuth (optional)
    print("\n" + "=" * 70)
    print("🔐 AUTHENTICATION SETUP")
    print("=" * 70)

    print("\nAttempting to set up OAuth credentials...")
    print("(This will open a browser window on first run)")

    if ensure_sheets_service(
        encoded_creds="YOUR_BASE64_ENCODED_CREDENTIALS_HERE",
        subject=None,  # Optional: provide a subject email for domain-wide delegation
    ):
        print("✅ Google Sheets OAuth credentials successfully initialized.")
    else:
        print(
            "⚠️ Google Sheets OAuth not configured properly. Some features may be restricted."
        )
        print(
            "   To enable full functionality, ensure your credentials are correctly provided."
        )

    # 6. Final summary
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)

    print("\n🎯 Library Features:")
    print("   ✅ Clean API with 2 required functions for Uvarolite integration")
    print(
        "   ✅ 19 built-in validation criteria (empty cells, duplicates, tab names, etc.)"
    )
    print("   ✅ Robust error handling - no exceptions bubble up")
    print("   ✅ Flexible authentication (OAuth + service accounts)")
    print("   ✅ Full backward compatibility with existing code")
    print("   ✅ Type hints and comprehensive documentation")

    print("\n🔄 Updates:")
    print("   • New integrations use clean get_available_validation_criteria()")
    print("     and execute_validation() functions")

    print("\n🚀 Ready for production use with Uvarolite batch processing system!")


if __name__ == "__main__":
    main()
