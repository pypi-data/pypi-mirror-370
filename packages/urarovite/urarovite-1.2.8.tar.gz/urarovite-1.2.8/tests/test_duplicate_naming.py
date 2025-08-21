"""Test duplicate file naming functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from urarovite.utils.generic_spreadsheet import _generate_unique_filename


class TestDuplicateNaming:
    """Test the duplicate file naming utility."""

    def test_no_duplicate_exists(self, tmp_path):
        """Test when no duplicate file exists."""
        file_path = tmp_path / "test_file.txt"
        result = _generate_unique_filename(file_path)
        assert result == file_path

    def test_simple_duplicate(self, tmp_path):
        """Test when a simple duplicate file exists."""
        # Create an existing file
        existing_file = tmp_path / "test_file.txt"
        existing_file.write_text("existing content")
        
        # Test the same filename
        file_path = tmp_path / "test_file.txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (1) version
        expected = tmp_path / "test_file (1).txt"
        assert result == expected
        assert not result.exists()  # The new name shouldn't exist yet

    def test_multiple_duplicates(self, tmp_path):
        """Test when multiple duplicate files exist."""
        # Create existing files
        (tmp_path / "test_file.txt").write_text("existing 1")
        (tmp_path / "test_file (1).txt").write_text("existing 2")
        (tmp_path / "test_file (2).txt").write_text("existing 3")
        
        # Test the same filename
        file_path = tmp_path / "test_file.txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (3) version
        expected = tmp_path / "test_file (3).txt"
        assert result == expected
        assert not result.exists()

    def test_already_numbered_filename(self, tmp_path):
        """Test when the filename already has a number suffix."""
        # Create existing files
        (tmp_path / "test_file (1).txt").write_text("existing 1")
        (tmp_path / "test_file (2).txt").write_text("existing 2")
        
        # Test a filename that already has a number
        file_path = tmp_path / "test_file (1).txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (3) version
        expected = tmp_path / "test_file (3).txt"
        assert result == expected
        assert not result.exists()

    def test_complex_filename_with_spaces(self, tmp_path):
        """Test with complex filenames containing spaces."""
        # Create existing files
        (tmp_path / "My Document (1).xlsx").write_text("existing 1")
        (tmp_path / "My Document (2).xlsx").write_text("existing 2")
        
        # Test the same filename
        file_path = tmp_path / "My Document.xlsx"
        result = _generate_unique_filename(file_path)
        
        # Should return (3) version
        expected = tmp_path / "My Document (3).xlsx"
        assert result == expected
        assert not result.exists()

    def test_filename_with_parentheses_in_name(self, tmp_path):
        """Test with filenames that contain parentheses in the actual name."""
        # Create existing files
        (tmp_path / "Project (Q4) Report.txt").write_text("existing 1")
        (tmp_path / "Project (Q4) Report (1).txt").write_text("existing 2")
        
        # Test the same filename
        file_path = tmp_path / "Project (Q4) Report.txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (2) version
        expected = tmp_path / "Project (Q4) Report (2).txt"
        assert result == expected
        assert not result.exists()

    def test_no_extension(self, tmp_path):
        """Test with files that have no extension."""
        # Create existing files
        (tmp_path / "README").write_text("existing 1")
        (tmp_path / "README (1)").write_text("existing 2")
        
        # Test the same filename
        file_path = tmp_path / "README"
        result = _generate_unique_filename(file_path)
        
        # Should return (2) version
        expected = tmp_path / "README (2)"
        assert result == expected
        assert not result.exists()

    def test_large_number_gap(self, tmp_path):
        """Test when there are gaps in the numbering sequence."""
        # Create existing files with gaps
        (tmp_path / "test_file.txt").write_text("existing 1")
        (tmp_path / "test_file (1).txt").write_text("existing 2")
        (tmp_path / "test_file (5).txt").write_text("existing 3")
        
        # Test the same filename
        file_path = tmp_path / "test_file.txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (6) version (next after highest existing)
        expected = tmp_path / "test_file (6).txt"
        assert result == expected
        assert not result.exists()

    def test_mixed_naming_patterns(self, tmp_path):
        """Test with mixed naming patterns in the directory."""
        # Create files with various naming patterns
        (tmp_path / "test_file.txt").write_text("existing 1")
        (tmp_path / "test_file (1).txt").write_text("existing 2")
        (tmp_path / "test_file_copy.txt").write_text("existing 3")
        (tmp_path / "test_file_v2.txt").write_text("existing 4")
        
        # Test the same filename
        file_path = tmp_path / "test_file.txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (2) version (next after highest numbered)
        expected = tmp_path / "test_file (2).txt"
        assert result == expected
        assert not result.exists()

    def test_pathlib_path_handling(self, tmp_path):
        """Test that the function works correctly with Path objects."""
        # Create existing file
        existing_file = tmp_path / "test_file.txt"
        existing_file.write_text("existing content")
        
        # Test with Path object
        file_path = Path(tmp_path) / "test_file.txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (1) version
        expected = Path(tmp_path) / "test_file (1).txt"
        assert result == expected
        assert isinstance(result, Path)
        assert not result.exists()

    def test_unicode_filename(self, tmp_path):
        """Test with Unicode filenames."""
        # Create existing file with Unicode
        existing_file = tmp_path / "café.txt"
        existing_file.write_text("existing content")
        
        # Test the same filename
        file_path = tmp_path / "café.txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (1) version
        expected = tmp_path / "café (1).txt"
        assert result == expected
        assert not result.exists()

    def test_special_characters_in_filename(self, tmp_path):
        """Test with special characters in filename."""
        # Create existing file with special characters
        existing_file = tmp_path / "file-name_with.underscores.txt"
        existing_file.write_text("existing content")
        
        # Test the same filename
        file_path = tmp_path / "file-name_with.underscores.txt"
        result = _generate_unique_filename(file_path)
        
        # Should return (1) version
        expected = tmp_path / "file-name_with.underscores (1).txt"
        assert result == expected
        assert not result.exists()
