#!/usr/bin/env python3
"""
Tests for the new CLI utilities infrastructure.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

from urarovite.cli_base import (
    BaseUtility,
    SingleBatchUtility,
    UtilityResult,
    UtilityCommandRunner,
    create_utility_command,
    run_utility_cli
)
from urarovite.cli_utils import (
    ConversionUtility,
    ValidationUtility,
    UtilityRegistry
)


class TestUtilityResult:
    """Test the UtilityResult dataclass."""
    
    def test_utility_result_creation(self):
        """Test creating a UtilityResult."""
        result = UtilityResult(
            success=True,
            message="Test message",
            data={"key": "value"},
            metadata={"count": 5}
        )
        
        assert result.success is True
        assert result.message == "Test message"
        assert result.data == {"key": "value"}
        assert result.metadata == {"count": 5}
        assert result.error is None
    
    def test_utility_result_with_error(self):
        """Test creating a UtilityResult with an error."""
        result = UtilityResult(
            success=False,
            message="Operation failed",
            error="Something went wrong"
        )
        
        assert result.success is False
        assert result.message == "Operation failed"
        assert result.error == "Something went wrong"


class TestBaseUtility:
    """Test the BaseUtility abstract base class."""
    
    def test_base_utility_creation(self):
        """Test creating a concrete BaseUtility."""
        class ConcreteUtility(BaseUtility):
            def execute_single(self, **kwargs):
                return UtilityResult(success=True, message="Done")
            
            def execute_batch(self, **kwargs):
                return UtilityResult(success=True, message="Batch done")
            
            def _add_utility_arguments(self, parser):
                parser.add_argument("input", help="Input file")
        
        utility = ConcreteUtility("test", "Test utility")
        assert utility.name == "test"
        assert utility.description == "Test utility"
    
    def test_base_utility_abstract_methods(self):
        """Test that BaseUtility cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseUtility("test", "Test")


class TestSingleBatchUtility:
    """Test the SingleBatchUtility class."""
    
    def test_single_batch_utility_creation(self):
        """Test creating a SingleBatchUtility."""
        class TestUtility(SingleBatchUtility):
            def _add_utility_arguments(self, parser):
                parser.add_argument("input", help="Input file")
            
            def execute_single(self, **kwargs):
                return UtilityResult(success=True, message="Single done")
            
            def execute_batch(self, **kwargs):
                return UtilityResult(success=True, message="Batch done")
        
        utility = TestUtility("test", "Test utility")
        assert utility.name == "test"
        assert utility.description == "Test utility"
    
    def test_single_batch_utility_argument_parser(self):
        """Test that SingleBatchUtility creates proper argument parser."""
        class TestUtility(SingleBatchUtility):
            def _add_utility_arguments(self, parser):
                parser.add_argument("input", help="Input file")
            
            def execute_single(self, **kwargs):
                return UtilityResult(success=True, message="Done")
            
            def execute_batch(self, **kwargs):
                return UtilityResult(success=True, message="Done")
        
        utility = TestUtility("test", "Test utility")
        parser = utility.get_argument_parser()
        
        # Check that common arguments are present
        args = parser.parse_args(["test_input", "--output", "json", "--auth-secret", "test", "--subject", "user@test.com"])
        assert args.output == "json"
        assert args.auth_secret == "test"
        assert args.subject == "user@test.com"
        assert args.mode == "single"  # Default mode


class TestConversionUtility:
    """Test the ConversionUtility class."""
    
    def test_conversion_utility_creation(self):
        """Test creating a ConversionUtility."""
        utility = ConversionUtility("convert", "Convert files")
        assert utility.name == "convert"
        assert utility.description == "Convert files"
    
    def test_conversion_utility_argument_parser(self):
        """Test that ConversionUtility creates proper argument parser."""
        utility = ConversionUtility("convert", "Convert files")
        parser = utility.get_argument_parser()
        
        # Test single mode arguments
        args = parser.parse_args([
            "input.xlsx", "output.xlsx", 
            "--sheets", "Sheet1,Sheet2",
            "--output-folder", "./output"
        ])
        
        assert args.input_file == "input.xlsx"
        assert args.output_path == "output.xlsx"
        assert args.sheets == "Sheet1,Sheet2"
        assert args.output_folder == "./output"
        assert args.mode == "single"  # Default mode
    
    def test_conversion_utility_batch_mode(self):
        """Test that ConversionUtility handles batch mode correctly."""
        utility = ConversionUtility("convert", "Convert files")
        parser = utility.get_argument_parser()
        
        args = parser.parse_args([
            "metadata.xlsx", "output_folder",
            "--mode", "batch",
            "--link-columns", "input,output"
        ])
        
        assert args.mode == "batch"
        assert args.link_columns == "input,output"


class TestValidationUtility:
    """Test the ValidationUtility class."""
    
    def test_validation_utility_creation(self):
        """Test creating a ValidationUtility."""
        utility = ValidationUtility("validate", "Validate spreadsheets")
        assert utility.name == "validate"
        assert utility.description == "Validate spreadsheets"
    
    def test_validation_utility_argument_parser(self):
        """Test that ValidationUtility creates proper argument parser."""
        utility = ValidationUtility("validate", "Validate spreadsheets")
        parser = utility.get_argument_parser()
        
        args = parser.parse_args([
            "sheet_url",
            "--validator", "empty_cells",
            "--validation-mode", "fix",
            "--params", '{"param1": "value1"}'
        ])
        
        assert args.spreadsheet_source == "sheet_url"
        assert args.validator == "empty_cells"
        assert args.validation_mode == "fix"
        assert args.params == '{"param1": "value1"}'


class TestUtilityRegistry:
    """Test the UtilityRegistry class."""
    
    def test_utility_registry_creation(self):
        """Test creating a UtilityRegistry."""
        registry = UtilityRegistry()
        assert "convert" in registry.list_utilities()
        assert "validate" in registry.list_utilities()
    
    def test_utility_registry_get_utility(self):
        """Test getting utilities from registry."""
        registry = UtilityRegistry()
        
        convert_util = registry.get_utility("convert")
        assert convert_util is not None
        assert convert_util.name == "convert"
        
        unknown_util = registry.get_utility("unknown")
        assert unknown_util is None
    
    def test_utility_registry_register_new_utility(self):
        """Test registering a new utility."""
        registry = UtilityRegistry()
        
        class TestUtility(SingleBatchUtility):
            def _add_utility_arguments(self, parser):
                parser.add_argument("input", help="Input file")
            
            def execute_single(self, **kwargs):
                return UtilityResult(success=True, message="Done")
            
            def execute_batch(self, **kwargs):
                return UtilityResult(success=True, message="Done")
        
        utility = TestUtility("test", "Test utility")
        registry.register("test", utility)
        
        assert "test" in registry.list_utilities()
        assert registry.get_utility("test") == utility


class TestUtilityCommandRunner:
    """Test the UtilityCommandRunner class."""
    
    def test_utility_command_runner_creation(self):
        """Test creating a UtilityCommandRunner."""
        class TestUtility(SingleBatchUtility):
            def _add_utility_arguments(self, parser):
                parser.add_argument("input", help="Input file")
            
            def execute_single(self, **kwargs):
                return UtilityResult(success=True, message="Done")
            
            def execute_batch(self, **kwargs):
                return UtilityResult(success=True, message="Done")
        
        utility = TestUtility("test", "Test utility")
        runner = UtilityCommandRunner(utility)
        assert runner.utility == utility


class TestFactoryFunctions:
    """Test the factory functions."""
    
    def test_create_utility_command(self):
        """Test creating a utility with the factory function."""
        def single_op(**kwargs):
            return UtilityResult(success=True, message="Single done")
        
        def batch_op(**kwargs):
            return UtilityResult(success=True, message="Batch done")
        
        def setup_args(parser):
            parser.add_argument("input", help="Input file")
        
        utility = create_utility_command(
            name="factory-test",
            description="Factory created utility",
            single_func=single_op,
            batch_func=batch_op,
            argument_setup=setup_args
        )
        
        assert utility.name == "factory-test"
        assert utility.description == "Factory created utility"
        
        # Test that it works
        result = utility.execute_single()
        assert result.success is True
        assert result.message == "Single done"


if __name__ == "__main__":
    pytest.main([__file__])
