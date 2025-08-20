"""
Comprehensive tests for funputer.cli module.
Targeting 0% → 80%+ coverage for CLI commands.

Coverage areas:
- analyze command (lines 28-130)  
- validate command (lines 132-196)
- Error handling, file I/O, verbose logging
- Output formatting and saving
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from funputer.cli import cli, analyze, validate
from funputer.models import AnalysisConfig


class TestCLIAnalyzeCommand:
    """Test the analyze command comprehensively."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
    def create_test_files(self, with_missing=True):
        """Create test data and metadata files."""
        # Create test data
        data = pd.DataFrame({
            'id': range(1, 21),
            'age': [25, 30, np.nan if with_missing else 30, 35, 40] * 4,
            'income': [50000, np.nan if with_missing else 60000, 75000, 60000, np.nan if with_missing else 70000] * 4,
            'category': ['A', 'B', np.nan if with_missing else 'C', 'C', 'A'] * 4,
            'score': np.random.normal(100, 15, 20)
        })
        
        # Create temporary data file
        data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(data_file.name, index=False)
        data_file.flush()
        
        # Create metadata file
        metadata_df = pd.DataFrame({
            'column_name': ['id', 'age', 'income', 'category', 'score'],
            'data_type': ['integer', 'integer', 'float', 'categorical', 'float'],
            'role': ['identifier', 'feature', 'feature', 'feature', 'target'],
            'nullable': [False, True, True, True, False]
        })
        
        metadata_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        metadata_df.to_csv(metadata_file.name, index=False)
        metadata_file.flush()
        
        return data_file.name, metadata_file.name
    
    def test_analyze_basic_execution(self):
        """Test basic analyze command execution (lines 50-81)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            # Test basic analyze command with metadata
            result = self.runner.invoke(analyze, [
                '--data', data_file,
                '--metadata', metadata_file
            ])
            
            assert result.exit_code == 0
            assert 'Analysis Results' in result.output
            assert 'columns' in result.output
            assert 'Analysis complete!' in result.output
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_analyze_with_auto_inference(self):
        """Test analyze command with automatic metadata inference (lines 75-81)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            # Test auto-inference (no metadata file)
            result = self.runner.invoke(analyze, [
                '--data', data_file
            ])
            
            assert result.exit_code == 0
            assert 'Analysis Results' in result.output
            assert 'Analysis complete!' in result.output
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_analyze_with_verbose_logging(self):
        """Test analyze command with verbose logging (lines 46-48, 57-58, 68-69, 77-78)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            # Test with verbose flag
            result = self.runner.invoke(analyze, [
                '--data', data_file,
                '--metadata', metadata_file,
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert 'Analysis Results' in result.output
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_analyze_with_output_file(self):
        """Test analyze command with output file saving (lines 117-120)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            # Create output file
            output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            output_file.close()
            
            # Test with output file
            result = self.runner.invoke(analyze, [
                '--data', data_file,
                '--metadata', metadata_file,
                '--output', output_file.name
            ])
            
            assert result.exit_code == 0
            assert 'Analysis Results' in result.output
            assert f'Results saved to: {output_file.name}' in result.output
            
            # Verify output file was created and has content
            assert os.path.exists(output_file.name)
            assert os.path.getsize(output_file.name) > 0
            
            os.unlink(output_file.name)
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_analyze_missing_data_file_error(self):
        """Test analyze command with missing data file (lines 52-55)."""
        result = self.runner.invoke(analyze, [
            '--data', 'nonexistent_file.csv'
        ])
        
        assert result.exit_code == 1
        assert 'Data file not found' in result.output
        assert '❌' in result.output
    
    def test_analyze_missing_metadata_file_error(self):
        """Test analyze command with missing metadata file (lines 63-66)."""
        data_file, _ = self.create_test_files()
        
        try:
            result = self.runner.invoke(analyze, [
                '--data', data_file,
                '--metadata', 'nonexistent_metadata.csv'
            ])
            
            assert result.exit_code == 1
            assert 'Metadata file not found' in result.output
            assert '❌' in result.output
            
        finally:
            os.unlink(data_file)
    
    def test_analyze_no_suggestions_generated(self):
        """Test analyze command when no suggestions are generated (lines 82-84)."""
        # Create data file with no missing values
        data_file, metadata_file = self.create_test_files(with_missing=False)
        
        try:
            # Mock analyze_imputation_requirements to return empty list
            with patch('funputer.cli.analyze_imputation_requirements') as mock_analyze:
                mock_analyze.return_value = []
                
                result = self.runner.invoke(analyze, [
                    '--data', data_file,
                    '--metadata', metadata_file
                ])
                
                assert result.exit_code == 1
                assert 'No imputation suggestions generated' in result.output
                
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_analyze_exception_handling(self):
        """Test analyze command exception handling (lines 124-129)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            # Mock analyze_imputation_requirements to raise exception
            with patch('funputer.cli.analyze_imputation_requirements') as mock_analyze:
                mock_analyze.side_effect = ValueError("Simulated analysis error")
                
                result = self.runner.invoke(analyze, [
                    '--data', data_file,
                    '--metadata', metadata_file
                ])
                
                assert result.exit_code == 1
                assert 'Error during analysis' in result.output
                assert 'Simulated analysis error' in result.output
                
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_analyze_exception_handling_with_verbose(self):
        """Test analyze command exception handling with verbose output (lines 126-128)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            # Mock analyze_imputation_requirements to raise exception
            with patch('funputer.cli.analyze_imputation_requirements') as mock_analyze:
                mock_analyze.side_effect = ValueError("Simulated verbose error")
                
                result = self.runner.invoke(analyze, [
                    '--data', data_file,
                    '--metadata', metadata_file,
                    '--verbose'
                ])
                
                assert result.exit_code == 1
                assert 'Error during analysis' in result.output
                
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_analyze_detailed_output_formatting(self):
        """Test detailed output formatting for suggestions (lines 87-115)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            result = self.runner.invoke(analyze, [
                '--data', data_file,
                '--metadata', metadata_file
            ])
            
            assert result.exit_code == 0
            
            # Should show detailed analysis results
            assert 'Analysis Results' in result.output
            assert 'columns' in result.output
            assert 'Summary:' in result.output
            assert 'Columns with missing data:' in result.output
            assert 'Total missing values:' in result.output
            assert 'Average confidence:' in result.output
            
            # Should show individual column details for columns with missing data
            # The output format should include column names, missing counts, methods, etc.
            # This tests lines 94-108 in the detailed suggestion output
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)


class TestCLIValidateCommand:
    """Test the validate command comprehensively."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def create_test_data_file(self, valid=True):
        """Create test data file."""
        if valid:
            data = pd.DataFrame({
                'id': range(1, 11),
                'value': [10, 20, np.nan, 40, 50, 60, np.nan, 80, 90, 100],
                'category': ['A', 'B', 'C'] * 3 + ['A']
            })
        else:
            # Create problematic data
            data = pd.DataFrame({
                'bad_col': [1, 'text', None, 'mixed', 5]
            })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        return temp_file.name
    
    def test_validate_basic_execution(self):
        """Test basic validate command execution (lines 154-171)."""
        data_file = self.create_test_data_file()
        
        try:
            # Mock preflight functions
            with patch('funputer.preflight.run_preflight') as mock_preflight:
                with patch('funputer.preflight.format_preflight_report') as mock_format:
                    mock_preflight.return_value = {'exit_code': 0, 'status': 'passed'}
                    mock_format.return_value = "✅ Validation passed!"
                    
                    result = self.runner.invoke(validate, [
                        '--data', data_file
                    ])
                    
                    assert result.exit_code == 0
                    assert 'Validation passed' in result.output
                    
        finally:
            os.unlink(data_file)
    
    def test_validate_with_verbose_logging(self):
        """Test validate command with verbose logging (lines 151-152, 163-164)."""
        data_file = self.create_test_data_file()
        
        try:
            # Mock preflight functions  
            with patch('funputer.preflight.run_preflight') as mock_preflight:
                with patch('funputer.preflight.format_preflight_report') as mock_format:
                    mock_preflight.return_value = {'exit_code': 0}
                    mock_format.return_value = "Detailed validation report"
                    
                    result = self.runner.invoke(validate, [
                        '--data', data_file,
                        '--verbose'
                    ])
                    
                    # Should complete successfully
                    assert result.exit_code == 0
                    
        finally:
            os.unlink(data_file)
    
    def test_validate_with_json_output(self):
        """Test validate command with JSON output (lines 173-177)."""
        data_file = self.create_test_data_file()
        
        try:
            json_output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json_output_file.close()
            
            # Mock preflight functions
            with patch('funputer.preflight.run_preflight') as mock_preflight:
                with patch('funputer.preflight.format_preflight_report') as mock_format:
                    mock_report = {'exit_code': 0, 'status': 'passed', 'details': 'All good'}
                    mock_preflight.return_value = mock_report
                    mock_format.return_value = "Validation report"
                    
                    result = self.runner.invoke(validate, [
                        '--data', data_file,
                        '--json-out', json_output_file.name
                    ])
                    
                    assert result.exit_code == 0
                    assert f'Validation report saved to: {json_output_file.name}' in result.output
                    
                    # Verify JSON file was created
                    assert os.path.exists(json_output_file.name)
                    
                    os.unlink(json_output_file.name)
                    
        finally:
            os.unlink(data_file)
    
    def test_validate_missing_data_file(self):
        """Test validate command with missing data file (lines 158-161)."""
        result = self.runner.invoke(validate, [
            '--data', 'nonexistent_file.csv'
        ])
        
        assert result.exit_code == 1
        assert 'Data file not found' in result.output
        assert '❌' in result.output
    
    def test_validate_with_warnings(self):
        """Test validate command with warnings (lines 183-184)."""
        data_file = self.create_test_data_file()
        
        try:
            # Mock preflight to return warning status
            with patch('funputer.preflight.run_preflight') as mock_preflight:
                with patch('funputer.preflight.format_preflight_report') as mock_format:
                    mock_preflight.return_value = {'exit_code': 2}
                    mock_format.return_value = "⚠️ Validation warnings"
                    
                    result = self.runner.invoke(validate, [
                        '--data', data_file
                    ])
                    
                    assert result.exit_code == 2
                    assert 'Data validation passed with warnings' in result.output
                    
        finally:
            os.unlink(data_file)
    
    def test_validate_with_failure(self):
        """Test validate command with validation failure (lines 185-186)."""
        data_file = self.create_test_data_file()
        
        try:
            # Mock preflight to return failure status
            with patch('funputer.preflight.run_preflight') as mock_preflight:
                with patch('funputer.preflight.format_preflight_report') as mock_format:
                    mock_preflight.return_value = {'exit_code': 10}
                    mock_format.return_value = "❌ Validation failed"
                    
                    result = self.runner.invoke(validate, [
                        '--data', data_file
                    ])
                    
                    assert result.exit_code == 10
                    assert 'Data validation failed' in result.output
                    
        finally:
            os.unlink(data_file)
    
    def test_validate_exception_handling(self):
        """Test validate command exception handling (lines 190-195)."""
        data_file = self.create_test_data_file()
        
        try:
            # Mock run_preflight to raise exception
            with patch('funputer.preflight.run_preflight') as mock_preflight:
                mock_preflight.side_effect = Exception("Validation error")
                
                result = self.runner.invoke(validate, [
                    '--data', data_file
                ])
                
                assert result.exit_code == 1
                assert 'Error during validation' in result.output
                assert 'Validation error' in result.output
                
        finally:
            os.unlink(data_file)
    
    def test_validate_exception_with_verbose(self):
        """Test validate command exception with verbose traceback (lines 192-194)."""
        data_file = self.create_test_data_file()
        
        try:
            # Mock run_preflight to raise exception
            with patch('funputer.preflight.run_preflight') as mock_preflight:
                mock_preflight.side_effect = Exception("Verbose validation error")
                
                result = self.runner.invoke(validate, [
                    '--data', data_file,
                    '--verbose'
                ])
                
                assert result.exit_code == 1
                assert 'Error during validation' in result.output
                
        finally:
            os.unlink(data_file)


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_group_help(self):
        """Test CLI group help command (lines 17-20)."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'FunPuter - Intelligent Imputation Analysis' in result.output
        assert 'analyze' in result.output
        assert 'validate' in result.output
    
    def test_analyze_command_help(self):
        """Test analyze command help."""
        result = self.runner.invoke(cli, ['analyze', '--help'])
        
        assert result.exit_code == 0
        assert 'Analyze dataset for missing data imputation' in result.output
        assert '--data' in result.output
        assert '--metadata' in result.output
        assert '--output' in result.output
        assert '--verbose' in result.output
    
    def test_validate_command_help(self):
        """Test validate command help."""
        result = self.runner.invoke(cli, ['validate', '--help'])
        
        assert result.exit_code == 0
        assert 'Run basic data validation checks' in result.output
        assert '--data' in result.output
        assert '--json-out' in result.output
        assert '--verbose' in result.output
    
    def test_full_workflow_integration(self):
        """Test complete CLI workflow: validate then analyze."""
        # Create test data file
        data = pd.DataFrame({
            'id': range(1, 11),
            'feature1': [1, 2, np.nan, 4, 5, 6, np.nan, 8, 9, 10],
            'feature2': ['A', 'B', 'C', np.nan, 'E', 'F', 'G', np.nan, 'I', 'J']
        })
        
        data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(data_file.name, index=False)
        data_file.flush()
        
        try:
            # Step 1: Validate the data
            with patch('funputer.preflight.run_preflight') as mock_preflight:
                with patch('funputer.preflight.format_preflight_report') as mock_format:
                    mock_preflight.return_value = {'exit_code': 0}
                    mock_format.return_value = "✅ Data validation passed"
                    
                    validate_result = self.runner.invoke(validate, [
                        '--data', data_file.name
                    ])
                    
                    assert validate_result.exit_code == 0
                    assert 'Data validation passed' in validate_result.output
            
            # Step 2: Analyze the data  
            analyze_result = self.runner.invoke(analyze, [
                '--data', data_file.name
            ])
            
            assert analyze_result.exit_code == 0
            assert 'Analysis Results' in analyze_result.output
            assert 'Analysis complete!' in analyze_result.output
            
        finally:
            os.unlink(data_file.name)