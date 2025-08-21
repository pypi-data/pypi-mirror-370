#!/usr/bin/env python3
"""
Test script for the A1 reference update utility function.
Tests the update_a1_references_in_text function from a1_range_validator.py
"""

import sys
import os
from typing import Dict, Any

# Add the project root to the path so we can import urarovite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from urarovite.utils.a1_range_validator import update_a1_references_in_text


def get_a1_reference_update_examples() -> Dict[str, Any]:
    """Get examples of A1 reference updates for different scenarios.
    
    Returns:
        Dict with update examples
    """
    return {
        "tab_rename_examples": [
            {
                "original": "'Old Tab'!A1",
                "new_tab": "New Tab",
                "result": "'New Tab'!A1"
            },
            {
                "original": "OldTab!A1:B10",
                "new_tab": "NewTab",
                "result": "NewTab!A1:B10"
            }
        ],
        "truncation_examples": [
            {
                "original": "'Very Long Tab Name That Exceeds Excel Limit'!A1",
                "truncated": "Very Long Tab Name That Exceeds",
                "result": "'Very Long Tab Name That Exceeds'!A1"
            },
            {
                "original": "VeryLongTabNameThatExceedsExcelLimit!A1:B10",
                "truncated": "VeryLongTabNameThatExceeds",
                "result": "VeryLongTabNameThatExceeds!A1:B10"
            }
        ],
        "mixed_quotes_examples": [
            {
                "original": "'Sheet1'!A1, Sheet2!B2, \"Sheet3\"!C3",
                "old_tab": "Sheet1",
                "new_tab": "NewSheet1",
                "result": "'NewSheet1'!A1, Sheet2!B2, \"Sheet3\"!C3"
            }
        ]
    }


def test_a1_reference_updates():
    """Test the A1 reference update functionality."""
    
    print("🔍 Testing A1 Reference Update Utility")
    print("=" * 50)
    
    # Test cases with different A1 reference formats
    test_cases = [
        # Basic references
        ("Sheet1!A1", "Sheet1", "NewSheet1"),
        ("Sheet1!B2", "Sheet1", "NewSheet1"),
        ("Sheet1!Z100", "Sheet1", "NewSheet1"),
        
        # Ranges
        ("Sheet1!A1:B10", "Sheet1", "NewSheet1"),
        ("Sheet1!A1:Z100", "Sheet1", "NewSheet1"),
        ("Sheet1!B2:D5", "Sheet1", "NewSheet1"),
        
        # Multiple ranges
        ("Sheet1!A1:B10:D20", "Sheet1", "NewSheet1"),
        ("Sheet1!A1:C5:E10:G15", "Sheet1", "NewSheet1"),
        
        # Quoted tab names
        ("'Sheet1'!A1", "Sheet1", "NewSheet1"),
        ('"Sheet1"!A1', "Sheet1", "NewSheet1"),
        ("'Sheet1'!A1:B10", "Sheet1", "NewSheet1"),
        ('"Sheet1"!A1:B10', "Sheet1", "NewSheet1"),
        
        # Edge case: leading quote but no closing quote
        ("'Sheet1!A1", "Sheet1", "NewSheet1"),
        
        # In formulas
        ("=SUM(Sheet1!A1:A10)", "Sheet1", "NewSheet1"),
        ("=Sheet1!A1 + Sheet1!B1", "Sheet1", "NewSheet1"),
        ("=COUNTIF(Sheet1!A1:A100, Sheet1!B1)", "Sheet1", "NewSheet1"),
        
        # Complex formulas
        ("=IF(Sheet1!A1>0, Sheet1!B1, Sheet1!C1)", "Sheet1", "NewSheet1"),
        ("=VLOOKUP(A1, Sheet1!A1:B100, 2, FALSE)", "Sheet1", "NewSheet1"),
        
        # Mixed quotes
        ("'Sheet1'!A1:B10", "Sheet1", "NewSheet1"),
        ('"Sheet1"!A1:B10', "Sheet1", "NewSheet1"),
        
        # Edge cases
        ("Sheet1!A1:B10:D20:E30", "Sheet1", "NewSheet1"),
        ("Sheet1!A1:B10:D20:E30:F40", "Sheet1", "NewSheet1"),
        
        # No matches (should not change)
        ("Sheet2!A1", "Sheet1", "NewSheet1"),
        ("OtherSheet!B2", "Sheet1", "NewSheet1"),
        ("NoExclamationMark", "Sheet1", "NewSheet1"),
        ("Just text with Sheet1 in it", "Sheet1", "NewSheet1"),
        ("Sheet1 without exclamation", "Sheet1", "NewSheet1"),
        
        # Tab names with spaces
        ("'Old Tab Name'!A1", "Old Tab Name", "New Tab Name"),
        ("'Old Tab Name'!A1:B10", "Old Tab Name", "New Tab Name"),
        
        # Multiple references in one cell
        ("Sheet1!A1 + Sheet1!B1", "Sheet1", "NewSheet1"),
        ("=SUM(Sheet1!A1:A10) + Sheet1!B1", "Sheet1", "NewSheet1"),
    ]
    
    total_tests = len(test_cases)
    successful_updates = 0
    total_references_updated = 0
    
    print(f"Testing {total_tests} test cases...")
    print()
    
    for i, (text, old_tab, new_tab) in enumerate(test_cases, 1):
        print(f"📝 Test {i}: '{text}'")
        print(f"   Old tab: '{old_tab}' → New tab: '{new_tab}'")
        
        # Run the update function
        result = update_a1_references_in_text(text, old_tab, new_tab)
        
        if result["success"]:
            if result["references_updated"] > 0:
                print(f"   ✅ Updated {result['references_updated']} references")
                print(f"   📝 Result: '{result['updated_text']}'")
                for change in result["changes_made"]:
                    print(f"      🔄 {change}")
                successful_updates += 1
                total_references_updated += result["references_updated"]
            else:
                print(f"   ℹ️  No references found (no change needed)")
                print(f"   📝 Result: '{result['updated_text']}'")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Total tests: {total_tests}")
    print(f"Successful updates: {successful_updates}")
    print(f"Total references updated: {total_references_updated}")
    print(f"Success rate: {(successful_updates/total_tests)*100:.1f}%")
    
    # Show examples
    print()
    print("📚 A1 Reference Update Examples")
    print("=" * 50)
    examples = get_a1_reference_update_examples()
    
    # Show tab rename examples
    if "tab_rename_examples" in examples:
        print("🔄 Tab Rename Examples:")
        for example in examples["tab_rename_examples"]:
            print(f"   '{example['original']}' → '{example['result']}'")
    
    # Show truncation examples
    if "truncation_examples" in examples:
        print("\n✂️  Truncation Examples:")
        for example in examples["truncation_examples"]:
            print(f"   '{example['original']}' → '{example['result']}' (truncated to '{example['truncated']}')")
    
    # Show mixed quotes examples
    if "mixed_quotes_examples" in examples:
        print("\n🔤 Mixed Quotes Examples:")
        for example in examples["mixed_quotes_examples"]:
            print(f"   '{example['original']}' → '{example['result']}' (updating '{example['old_tab']}' to '{example['new_tab']}')")

def test_specific_patterns():
    """Test specific problematic patterns you might be encountering."""
    
    print("🎯 Testing Specific Problematic Patterns")
    print("=" * 50)
    
    # Add your specific problematic strings here
    problematic_strings = [
        # Add any specific strings that aren't working
        # "Your problem string here",
    ]
    
    if not problematic_strings:
        print("No specific problematic patterns to test.")
        print("Add your problematic strings to the problematic_strings list above.")
        return
    
    old_tab_name = "Sheet1"
    new_tab_name = "NewSheet1"
    
    for i, text in enumerate(problematic_strings, 1):
        print(f"🔍 Problematic {i}: '{text}'")
        
        result = update_a1_references_in_text(text, old_tab_name, new_tab_name)
        
        if result["success"]:
            if result["references_updated"] > 0:
                print(f"   ✅ Fixed: '{result['updated_text']}'")
                for change in result["changes_made"]:
                    print(f"      🔄 {change}")
            else:
                print(f"   ℹ️  No references found")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        print()

if __name__ == "__main__":
    print("🚀 A1 Reference Update Utility Test Tool")
    print("=" * 50)
    print()
    
    test_a1_reference_updates()
    print()
    test_specific_patterns()
    
    print()
    print("✨ Test complete! Check the output above for any issues.")
    print()
    print("💡 Tips for debugging:")
    print("   1. Look for patterns that show 'No references found' when they should update")
    print("   2. Check if the regex pattern is too restrictive")
    print("   3. Verify that special characters in tab names are properly escaped")
    print("   4. Test with your actual tab names and A1 references")
