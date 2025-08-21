# Pre-Validation Duplication Tests

This directory contains comprehensive tests for the new pre-validation duplication workflow implemented in the Urarovite validation API.

## Overview

The pre-validation duplication workflow ensures that when validation is run in "fix" mode, a duplicate of the source spreadsheet is created at the target location BEFORE any validation occurs. This protects the original data while providing a clean, validated copy.

## Testing Infrastructure

All tests use the centralized mocking infrastructure for consistent, maintainable testing:

- **MockManager**: High-level scenario-based mocking (`mock_manager.validation_scenario()`, `mock_manager.integration_scenario()`)
- **BaseTestCase**: Common setup providing `encoded_creds`, `temp_dir`, and utility methods
- **MockPatches**: Centralized patch decorators for consistent mocking patterns
- **Dramatic Code Reduction**: ~52% fewer lines compared to manual mocking approaches

## Test Files

### 1. `test_api_pre_validation_duplication.py`
**Core API workflow tests**

- ✅ **Fix mode creates duplicate**: Verifies that fix mode triggers duplication
- ✅ **Flag mode no duplicate**: Verifies that flag mode skips duplication  
- ✅ **Duplicate creation failure**: Tests error handling when duplication fails
- ✅ **Excel source handling**: Tests Excel files without authentication
- ✅ **Authentication validation**: Tests auth requirements for different sources

**Key test classes:**
- `TestPreValidationDuplication`: Main workflow tests
- `TestCreatePreValidationDuplicate`: Duplication function tests
- `TestCreateDriveFolderDuplicate`: Google Drive folder tests
- `TestDriveFolderIdValidation`: Drive folder ID format validation
- `TestIntegrationWorkflow`: End-to-end integration tests

### 2. `test_spreadsheet_conversion.py`
**Spreadsheet format conversion tests**

- ✅ **Google Sheets to Excel**: Conversion functionality
- ✅ **Excel to Google Sheets**: Reverse conversion
- ✅ **Format auto-detection**: Automatic format detection
- ✅ **Copy operations**: Same-format copying (Sheets→Sheets, Excel→Excel)
- ✅ **Error handling**: Conversion failure scenarios
- ✅ **Sheet selection**: Converting specific sheets only

**Key test classes:**
- `TestConvertGoogleSheetsToExcel`: Google Sheets → Excel conversion
- `TestConvertExcelToGoogleSheets`: Excel → Google Sheets conversion  
- `TestConvertSpreadsheetFormat`: Auto-detection and orchestration
- `TestCopyFunctions`: Same-format copy operations
- `TestErrorHandling`: Comprehensive error scenarios

### 3. `test_target_format_validation.py`
**Target and format validation tests**

- ✅ **Format constraints**: "sheets" only for remote, "excel" for any target
- ✅ **Target validation**: Local vs. Drive folder ID validation
- ✅ **Auto-detection**: Format auto-detection based on source
- ✅ **Drive folder IDs**: Validation of Google Drive folder ID formats
- ✅ **Error scenarios**: Invalid combinations and missing auth

**Key test classes:**
- `TestTargetFormatValidation`: Core validation logic
- `TestDriveFolderIdValidation`: Drive folder ID format tests
- `TestLocalTargetHandling`: Local target processing
- `TestErrorHandling`: Error propagation and handling

### 4. `test_integration_pre_validation_workflow.py`
**End-to-end integration tests**

- ✅ **Complete workflows**: Full fix and flag mode workflows
- ✅ **Multiple scenarios**: Google Sheets→Local, Sheets→Drive, Excel→Local
- ✅ **Error propagation**: How errors flow through the complete workflow
- ✅ **Edge cases**: Zero fixes, unknown validators, large datasets
- ✅ **Parameter validation**: Input validation and error handling

**Key test classes:**
- `TestCompleteWorkflowIntegration`: Full end-to-end workflows
- `TestWorkflowEdgeCases`: Boundary conditions and edge cases

## Test Coverage

### Core Functionality
- ✅ Pre-validation duplication (fix mode only)
- ✅ Target and format validation
- ✅ Google Drive folder operations
- ✅ Local file operations
- ✅ Format conversion (Google Sheets ↔ Excel)
- ✅ Authentication handling

### Error Scenarios
- ✅ Duplication failures
- ✅ Invalid target/format combinations
- ✅ Missing authentication
- ✅ Invalid Drive folder IDs
- ✅ Conversion failures
- ✅ Validation errors

### Integration Points
- ✅ Validator registry integration
- ✅ SpreadsheetFactory integration
- ✅ Google Drive API integration
- ✅ File system operations
- ✅ Error propagation through layers

## Running Tests

### Run All Pre-Validation Tests
```bash
python run_pre_validation_tests.py
```

### Run Individual Test Files
```bash
# Core API tests
python -m pytest tests/test_api_pre_validation_duplication.py -v

# Conversion tests
python -m pytest tests/test_spreadsheet_conversion.py -v

# Validation tests
python -m pytest tests/test_target_format_validation.py -v

# Integration tests
python -m pytest tests/test_integration_pre_validation_workflow.py -v
```

### Run Specific Test Classes
```bash
# Test only duplication workflow
python -m pytest tests/test_api_pre_validation_duplication.py::TestPreValidationDuplication -v

# Test only format validation
python -m pytest tests/test_target_format_validation.py::TestTargetFormatValidation -v
```

### Run with Coverage
```bash
python -m pytest tests/test_*pre_validation*.py --cov=urarovite.core.api --cov-report=html
```

## Test Data and Mocking

### Mocked Components
- **Validator Registry**: Mocked to return test validators
- **SpreadsheetFactory**: Mocked to return test spreadsheet objects
- **Google Drive API**: Mocked for Drive operations
- **File System**: Uses temporary directories for safe testing
- **Conversion Functions**: Mocked to simulate success/failure scenarios

### Test Credentials
```python
SAMPLE_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "test-project",
    "private_key_id": "key123",
    "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
    "client_email": "test@test-project.iam.gserviceaccount.com",
    "client_id": "123456789",
}
```

### Temporary Files
All tests use temporary directories that are automatically cleaned up after each test to ensure no side effects.

## Test Scenarios Covered

### Fix Mode Workflows
1. **Google Sheets → Local Excel**
   - Creates duplicate locally
   - Validates on duplicate
   - Returns duplicate path

2. **Google Sheets → Drive Folder (Sheets)**
   - Duplicates to Drive folder
   - Validates on Drive duplicate
   - Returns Drive URL

3. **Google Sheets → Drive Folder (Excel)**
   - Converts to local Excel
   - Validates on local copy
   - (Drive upload not yet implemented)

4. **Excel → Local Excel**
   - Creates local duplicate
   - Validates on duplicate
   - No authentication needed

### Flag Mode Workflows
1. **Analysis Only**
   - No duplication created
   - Validates on original
   - Optional report generation

2. **Report Generation**
   - Analyzes original
   - Saves report to target
   - Original untouched

### Error Scenarios
1. **Duplication Failures**
   - Permission denied
   - Invalid target format
   - Missing authentication

2. **Validation Errors**
   - Unknown validator
   - Validation exceptions
   - Partial failures

3. **Format/Target Errors**
   - Invalid combinations
   - Malformed Drive folder IDs
   - Unsupported formats

## Expected Behavior

### Fix Mode
```
1. Check mode = "fix" ✓
2. Create duplicate at target ✓
3. Validate on duplicate ✓
4. Apply fixes to duplicate ✓
5. Return duplicate location ✓
```

### Flag Mode
```
1. Check mode = "flag" ✓
2. Skip duplication ✓
3. Validate on original ✓
4. Generate report (optional) ✓
5. Return analysis results ✓
```

## Assertions and Verifications

### Workflow Assertions
- ✅ Correct mode detection
- ✅ Duplication only in fix mode
- ✅ Validation on correct source (original vs. duplicate)
- ✅ Proper error propagation
- ✅ Return value completeness

### Mock Verifications
- ✅ Function call counts and arguments
- ✅ Authentication parameter passing
- ✅ Target/format parameter validation
- ✅ Error condition handling

### State Verifications
- ✅ File creation/cleanup
- ✅ Return value structure
- ✅ Error message content
- ✅ Success/failure status

## Maintenance Notes

### Adding New Tests
1. Follow existing naming conventions
2. Use appropriate test class organization
3. Include both success and failure scenarios
4. Mock external dependencies appropriately
5. Clean up temporary resources

### Updating Tests
1. Update mocks when API changes
2. Add new test scenarios for new features
3. Maintain backward compatibility tests
4. Update documentation accordingly

### Test Dependencies
- `pytest`: Test framework
- `unittest.mock`: Mocking framework
- `tempfile`: Temporary file/directory creation
- `pathlib`: Path manipulation
- `base64`, `json`: Test data encoding

The test suite provides comprehensive coverage of the pre-validation duplication workflow, ensuring reliability and maintainability of this critical feature.
