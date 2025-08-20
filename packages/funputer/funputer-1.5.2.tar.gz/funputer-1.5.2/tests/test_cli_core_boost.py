"""
Comprehensive tests for funputer.cli module.
Strategic tests targeting CLI command coverage and error handling.

Coverage Target: Boost CLI module from 0% to 80%+
Priority: CRITICAL (User interface)
"""

import pytest
import os
import tempfile
import json
import pandas as pd
import numpy as np
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from funputer.cli import cli
from funputer.models import ImputationSuggestion, AnalysisConfig


class TestCLIAnalyzeCommand:
    """Test the analyze command functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.test_data = pd.DataFrame({
            'id': range(1, 21),
            'age': [25, 30, np.nan, 35, 40] * 4,
            'income': np.random.normal(50000, 10000, 20),
            'category': ['A', 'B', np.nan, 'C', 'A'] * 4
        })
        # Add some missing values to income
        self.test_data.loc[::7, 'income'] = np.nan
    
    def create_test_data_file(self):
        """Create a temporary test data file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        return temp_file.name
    
    def create_test_metadata_file(self):
        """Create a temporary metadata file."""
        metadata_df = pd.DataFrame({
            'column_name': ['id', 'age', 'income', 'category'],
            'data_type': ['integer', 'integer', 'float', 'categorical'],
            'role': ['identifier', 'feature', 'feature', 'feature'],
            'nullable': [False, True, True, True],
            'description': ['ID column', 'Age in years', 'Annual income', 'Category']
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        metadata_df.to_csv(temp_file.name, index=False)
        temp_file.flush()
        return temp_file.name
    
    def test_analyze_command_help(self):
        """Test analyze command help output."""
        result = self.runner.invoke(cli, ['analyze', '--help'])
        
        assert result.exit_code == 0
        assert 'analyze' in result.output.lower()
        assert '--data' in result.output
        assert '--metadata' in result.output
        assert '--output' in result.output
        assert '--verbose' in result.output
    
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_analyze_command_basic_execution(self, mock_analyze):
        """Test basic analyze command execution."""
        # Mock successful analysis
        mock_suggestions = [
            ImputationSuggestion(
                column_name='age',
                proposed_method='mean',
                rationale='Numeric data with normal distribution',
                missing_count=4,
                missing_percentage=20.0,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='No outliers detected',
                confidence_score=0.85
            )
        ]
        mock_analyze.return_value = mock_suggestions
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, ['analyze', '--data', data_file])
            
            assert result.exit_code == 0
            assert mock_analyze.called
            assert 'Analysis Results' in result.output
            assert 'age' in result.output
            assert 'mean' in result.output
            assert 'Confidence: 0.85' in result.output
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_analyze_command_with_metadata_file(self, mock_analyze):
        """Test analyze command with explicit metadata file."""
        # Mock successful analysis
        mock_suggestions = [
            ImputationSuggestion(
                column_name='age',
                proposed_method='median',
                rationale='Numeric data with skewed distribution',
                missing_count=4,
                missing_percentage=20.0,
                mechanism='MCAR',
                outlier_count=1,
                outlier_percentage=5.0,
                outlier_handling='keep',
                outlier_rationale='Outliers within acceptable range',
                confidence_score=0.78
            )
        ]
        mock_analyze.return_value = mock_suggestions
        
        data_file = self.create_test_data_file()
        metadata_file = self.create_test_metadata_file()
        
        try:
            result = self.runner.invoke(cli, [
                'analyze', 
                '--data', data_file,
                '--metadata', metadata_file
            ])
            
            assert result.exit_code == 0
            assert mock_analyze.called
            
            # Check that it was called with metadata path
            call_args = mock_analyze.call_args
            assert 'metadata_path' in call_args.kwargs
            assert call_args.kwargs['metadata_path'] == metadata_file
            
            assert 'Analysis Results' in result.output
            assert 'age' in result.output
            assert 'median' in result.output
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    @patch('funputer.cli.save_suggestions')
    def test_analyze_command_with_output_file(self, mock_save, mock_analyze):
        """Test analyze command with output file."""
        # Mock successful analysis
        mock_suggestions = [
            ImputationSuggestion(
                column_name='category',
                proposed_method='mode',
                rationale='Categorical data - use most frequent',
                missing_count=4,
                missing_percentage=20.0,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='No outliers in categorical data',
                confidence_score=0.90
            )
        ]
        mock_analyze.return_value = mock_suggestions
        
        data_file = self.create_test_data_file()
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
                result = self.runner.invoke(cli, [
                    'analyze',
                    '--data', data_file,
                    '--output', output_file.name
                ])
                
                assert result.exit_code == 0
                assert mock_analyze.called
                assert mock_save.called
                
                # Check that save_suggestions was called with correct arguments
                save_call_args = mock_save.call_args
                assert save_call_args[0][0] == mock_suggestions  # First arg: suggestions
                assert save_call_args[0][1] == output_file.name   # Second arg: output path
                
                assert f'Results saved to: {output_file.name}' in result.output
                
                os.unlink(output_file.name)
                
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_analyze_command_verbose_mode(self, mock_analyze):
        """Test analyze command with verbose output."""
        mock_suggestions = [
            ImputationSuggestion(
                column_name='income',
                proposed_method='regression',
                rationale='Numeric data with relationship to other variables',
                missing_count=3,
                missing_percentage=15.0,
                mechanism='MAR',
                outlier_count=2,
                outlier_percentage=10.0,
                outlier_handling='cap',
                outlier_rationale='Cap outliers to reduce impact',
                confidence_score=0.72
            )
        ]
        mock_analyze.return_value = mock_suggestions
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'analyze',
                '--data', data_file,
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert 'Analyzing dataset' in result.output
            assert 'Auto-inferring metadata' in result.output
            assert 'Analysis Results' in result.output
            
        finally:
            os.unlink(data_file)
    
    def test_analyze_command_missing_data_file(self):
        """Test analyze command with missing data file."""
        result = self.runner.invoke(cli, [
            'analyze',
            '--data', 'nonexistent_file.csv'
        ])
        
        assert result.exit_code == 1
        assert 'Error: Data file not found' in result.output
    
    def test_analyze_command_missing_metadata_file(self):
        """Test analyze command with missing metadata file."""
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'analyze',
                '--data', data_file,
                '--metadata', 'nonexistent_metadata.csv'
            ])
            
            assert result.exit_code == 1
            assert 'Error: Metadata file not found' in result.output
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_analyze_command_no_suggestions_generated(self, mock_analyze):
        """Test analyze command when no suggestions are generated."""
        # Mock empty analysis result
        mock_analyze.return_value = []
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'analyze',
                '--data', data_file
            ])
            
            assert result.exit_code == 1
            assert 'No imputation suggestions generated' in result.output
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_analyze_command_exception_handling(self, mock_analyze):
        """Test analyze command exception handling."""
        # Mock analysis raising exception
        mock_analyze.side_effect = Exception("Analysis failed for test")
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'analyze',
                '--data', data_file
            ])
            
            assert result.exit_code == 1
            assert 'Error during analysis' in result.output
            assert 'Analysis failed for test' in result.output
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_analyze_command_exception_handling_verbose(self, mock_analyze):
        """Test analyze command exception handling with verbose output."""
        # Mock analysis raising exception
        mock_analyze.side_effect = ValueError("Detailed analysis error")
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'analyze',
                '--data', data_file,
                '--verbose'
            ])
            
            assert result.exit_code == 1
            assert 'Error during analysis' in result.output
            # Verbose mode should show more details
            assert 'Detailed analysis error' in result.output
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_analyze_command_summary_statistics(self, mock_analyze):
        """Test analyze command summary statistics output."""
        # Mock analysis with multiple suggestions including outliers
        mock_suggestions = [
            ImputationSuggestion(
                column_name='age',
                proposed_method='mean',
                rationale='Numeric MCAR',
                missing_count=5,
                missing_percentage=25.0,
                mechanism='MCAR',
                outlier_count=2,
                outlier_percentage=10.0,
                outlier_handling='remove',
                outlier_rationale='Remove extreme outliers',
                confidence_score=0.85
            ),
            ImputationSuggestion(
                column_name='income',
                proposed_method='regression',
                rationale='Numeric MAR',
                missing_count=3,
                missing_percentage=15.0,
                mechanism='MAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='No outliers detected',
                confidence_score=0.75
            ),
            ImputationSuggestion(
                column_name='category',
                proposed_method='mode',
                rationale='Categorical MCAR',
                missing_count=2,
                missing_percentage=10.0,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='N/A for categorical',
                confidence_score=0.90
            )
        ]
        mock_analyze.return_value = mock_suggestions
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'analyze',
                '--data', data_file
            ])
            
            assert result.exit_code == 0
            
            # Check summary statistics
            assert 'Summary:' in result.output
            assert 'Columns with missing data: 3' in result.output
            assert 'Total missing values: 10' in result.output  # 5 + 3 + 2
            assert 'Average confidence: 0.83' in result.output  # (0.85 + 0.75 + 0.90) / 3
            
            # Check outlier information is displayed
            assert 'Outliers: 2 (10.0%)' in result.output
            
        finally:
            os.unlink(data_file)


class TestCLIValidateCommand:
    """Test the validate command functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.test_data = pd.DataFrame({
            'id': range(1, 11),
            'name': [f'item_{i}' for i in range(1, 11)],
            'value': [10.5, 20.1, np.nan, 15.3, 25.7, 30.2, np.nan, 18.9, 22.4, 27.8],
            'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']
        })
    
    def create_test_data_file(self):
        """Create a temporary test data file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        return temp_file.name
    
    def test_validate_command_help(self):
        """Test validate command help output."""
        result = self.runner.invoke(cli, ['validate', '--help'])
        
        assert result.exit_code == 0
        assert 'validate' in result.output.lower()
        assert '--data' in result.output
        assert '--json-out' in result.output
        assert '--verbose' in result.output
        assert 'validation' in result.output.lower()
    
    @patch('funputer.cli.run_preflight')
    @patch('funputer.cli.format_preflight_report')
    def test_validate_command_basic_execution(self, mock_format, mock_preflight):
        """Test basic validate command execution."""
        # Mock successful validation
        mock_report = {
            'status': 'passed',
            'warnings': [],
            'errors': [],
            'exit_code': 0
        }
        mock_preflight.return_value = mock_report
        mock_format.return_value = "✅ Data validation passed!"
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, ['validate', '--data', data_file])
            
            assert result.exit_code == 0
            assert mock_preflight.called
            assert mock_format.called
            assert 'Data validation passed!' in result.output
            
            # Check that preflight was called with correct path
            preflight_call_args = mock_preflight.call_args
            assert preflight_call_args[0][0] == data_file
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.run_preflight')
    @patch('funputer.cli.format_preflight_report')
    def test_validate_command_with_warnings(self, mock_format, mock_preflight):
        """Test validate command with validation warnings."""
        # Mock validation with warnings
        mock_report = {
            'status': 'passed_with_warnings',
            'warnings': ['Missing metadata for some columns'],
            'errors': [],
            'exit_code': 2
        }
        mock_preflight.return_value = mock_report
        mock_format.return_value = "⚠️  Data validation passed with warnings."
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, ['validate', '--data', data_file])
            
            assert result.exit_code == 2
            assert 'passed with warnings' in result.output
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.run_preflight')
    @patch('funputer.cli.format_preflight_report')
    def test_validate_command_with_json_output(self, mock_format, mock_preflight):
        """Test validate command with JSON output."""
        # Mock validation report
        mock_report = {
            'status': 'passed',
            'data_shape': [10, 4],
            'missing_data': {
                'total_missing': 2,
                'columns_with_missing': ['value']
            },
            'warnings': [],
            'errors': [],
            'exit_code': 0
        }
        mock_preflight.return_value = mock_report
        mock_format.return_value = "✅ Validation complete"
        
        data_file = self.create_test_data_file()
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
                result = self.runner.invoke(cli, [
                    'validate',
                    '--data', data_file,
                    '--json-out', json_file.name
                ])
                
                assert result.exit_code == 0
                assert f'Validation report saved to: {json_file.name}' in result.output
                
                # Check that JSON file was created and contains expected data
                assert os.path.exists(json_file.name)
                
                with open(json_file.name, 'r') as f:
                    saved_report = json.load(f)
                    assert saved_report['status'] == 'passed'
                    assert saved_report['data_shape'] == [10, 4]
                
                os.unlink(json_file.name)
                
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.run_preflight')
    @patch('funputer.cli.format_preflight_report')
    def test_validate_command_verbose_mode(self, mock_format, mock_preflight):
        """Test validate command with verbose output."""
        mock_report = {
            'status': 'passed',
            'exit_code': 0
        }
        mock_preflight.return_value = mock_report
        mock_format.return_value = "Validation complete"
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'validate',
                '--data', data_file,
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert 'Validating dataset' in result.output
            
        finally:
            os.unlink(data_file)
    
    def test_validate_command_missing_data_file(self):
        """Test validate command with missing data file."""
        result = self.runner.invoke(cli, [
            'validate',
            '--data', 'nonexistent_file.csv'
        ])
        
        assert result.exit_code == 1
        assert 'Error: Data file not found' in result.output
    
    @patch('funputer.cli.run_preflight')
    def test_validate_command_validation_failure(self, mock_preflight):
        """Test validate command when validation fails."""
        # Mock validation failure
        mock_report = {
            'status': 'failed',
            'errors': ['Data format is invalid', 'Missing required columns'],
            'exit_code': 1
        }
        mock_preflight.return_value = mock_report
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, ['validate', '--data', data_file])
            
            assert result.exit_code == 1
            assert 'Data validation failed' in result.output
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.run_preflight')
    def test_validate_command_exception_handling(self, mock_preflight):
        """Test validate command exception handling."""
        # Mock preflight raising exception
        mock_preflight.side_effect = Exception("Validation system error")
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'validate',
                '--data', data_file
            ])
            
            assert result.exit_code == 1
            assert 'Error during validation' in result.output
            assert 'Validation system error' in result.output
            
        finally:
            os.unlink(data_file)
    
    @patch('funputer.cli.run_preflight')
    def test_validate_command_exception_handling_verbose(self, mock_preflight):
        """Test validate command exception handling with verbose output."""
        # Mock preflight raising exception
        mock_preflight.side_effect = ValueError("Detailed validation error")
        
        data_file = self.create_test_data_file()
        
        try:
            result = self.runner.invoke(cli, [
                'validate',
                '--data', data_file,
                '--verbose'
            ])
            
            assert result.exit_code == 1
            assert 'Error during validation' in result.output
            # Should show traceback in verbose mode
            
        finally:
            os.unlink(data_file)


class TestCLIMainCommand:
    """Test main CLI group and global options."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_main_help(self):
        """Test main CLI help output."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'FunPuter' in result.output
        assert 'Intelligent Imputation Analysis' in result.output
        assert 'analyze' in result.output
        assert 'validate' in result.output
    
    def test_cli_no_arguments(self):
        """Test CLI with no arguments shows help."""
        result = self.runner.invoke(cli, [])
        
        assert result.exit_code == 0
        assert 'Usage:' in result.output
        assert 'Commands:' in result.output
    
    def test_cli_invalid_command(self):
        """Test CLI with invalid command."""
        result = self.runner.invoke(cli, ['invalid_command'])
        
        assert result.exit_code != 0
        assert 'No such command' in result.output or 'Usage:' in result.output
    
    def test_analyze_command_missing_required_data(self):
        """Test analyze command without required --data option."""
        result = self.runner.invoke(cli, ['analyze'])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()
    
    def test_validate_command_missing_required_data(self):
        """Test validate command without required --data option."""
        result = self.runner.invoke(cli, ['validate'])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()


class TestCLIIntegrationScenarios:
    """Test CLI integration scenarios and workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.sample_data = pd.DataFrame({
            'customer_id': range(1, 101),
            'age': [25 + i % 50 for i in range(100)],
            'income': np.random.normal(50000, 15000, 100),
            'category': np.random.choice(['Bronze', 'Silver', 'Gold'], 100),
            'satisfaction': np.random.choice([1, 2, 3, 4, 5], 100)
        })
        
        # Add missing values
        self.sample_data.loc[::10, 'age'] = np.nan
        self.sample_data.loc[::15, 'income'] = np.nan
        self.sample_data.loc[::20, 'category'] = np.nan
    
    def create_sample_files(self):
        """Create sample data and metadata files."""
        # Create data file
        data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.sample_data.to_csv(data_file.name, index=False)
        data_file.flush()
        
        # Create metadata file
        metadata_df = pd.DataFrame({
            'column_name': ['customer_id', 'age', 'income', 'category', 'satisfaction'],
            'data_type': ['integer', 'integer', 'float', 'categorical', 'integer'],
            'role': ['identifier', 'feature', 'feature', 'feature', 'target'],
            'nullable': [False, True, True, True, False],
            'min_value': [1, 18, 0, None, 1],
            'max_value': [None, 100, None, None, 5],
            'description': [
                'Unique customer identifier',
                'Customer age in years', 
                'Annual income in dollars',
                'Customer category',
                'Satisfaction rating'
            ]
        })
        
        metadata_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        metadata_df.to_csv(metadata_file.name, index=False)
        metadata_file.flush()
        
        return data_file.name, metadata_file.name
    
    @patch('funputer.cli.run_preflight')
    @patch('funputer.cli.format_preflight_report') 
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_complete_workflow_validate_then_analyze(self, mock_analyze, mock_format, mock_preflight):
        """Test complete workflow: validate data then analyze."""
        # Mock validation success
        mock_report = {'status': 'passed', 'exit_code': 0}
        mock_preflight.return_value = mock_report
        mock_format.return_value = "✅ Validation passed"
        
        # Mock analysis success
        mock_suggestions = [
            ImputationSuggestion(
                column_name='age',
                proposed_method='median',
                rationale='Numeric data with outliers',
                missing_count=10,
                missing_percentage=10.0,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='No outliers',
                confidence_score=0.80
            )
        ]
        mock_analyze.return_value = mock_suggestions
        
        data_file, metadata_file = self.create_sample_files()
        
        try:
            # Step 1: Validate
            validate_result = self.runner.invoke(cli, [
                'validate', '--data', data_file
            ])
            assert validate_result.exit_code == 0
            
            # Step 2: Analyze  
            analyze_result = self.runner.invoke(cli, [
                'analyze', '--data', data_file, '--metadata', metadata_file
            ])
            assert analyze_result.exit_code == 0
            
            # Both should have succeeded
            assert mock_preflight.called
            assert mock_analyze.called
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    @patch('funputer.cli.save_suggestions')
    def test_end_to_end_analysis_with_output(self, mock_save, mock_analyze):
        """Test end-to-end analysis workflow with file output."""
        # Mock comprehensive analysis result
        mock_suggestions = [
            ImputationSuggestion(
                column_name='age',
                proposed_method='median',
                rationale='Numeric with skewed distribution',
                missing_count=10,
                missing_percentage=10.0,
                mechanism='MCAR',
                outlier_count=2,
                outlier_percentage=2.0,
                outlier_handling='cap',
                outlier_rationale='Cap extreme values',
                confidence_score=0.82
            ),
            ImputationSuggestion(
                column_name='income',
                proposed_method='regression',
                rationale='Numeric MAR - correlates with age',
                missing_count=7,
                missing_percentage=7.0,
                mechanism='MAR',
                outlier_count=3,
                outlier_percentage=3.0,
                outlier_handling='remove',
                outlier_rationale='Remove income outliers',
                confidence_score=0.75
            ),
            ImputationSuggestion(
                column_name='category',
                proposed_method='mode',
                rationale='Categorical MCAR',
                missing_count=5,
                missing_percentage=5.0,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='No outliers in categorical',
                confidence_score=0.88
            )
        ]
        mock_analyze.return_value = mock_suggestions
        
        data_file, metadata_file = self.create_sample_files()
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as output_file:
                result = self.runner.invoke(cli, [
                    'analyze',
                    '--data', data_file,
                    '--metadata', metadata_file,
                    '--output', output_file.name,
                    '--verbose'
                ])
                
                assert result.exit_code == 0
                
                # Check verbose output
                assert 'Using metadata file' in result.output
                assert 'Analyzing dataset' in result.output
                
                # Check analysis results display
                assert 'Analysis Results (3 columns)' in result.output
                assert 'Columns with missing data: 3' in result.output
                assert 'Total missing values: 22' in result.output
                assert 'Average confidence: 0.82' in result.output
                
                # Check individual suggestions display
                assert 'age' in result.output and 'median' in result.output
                assert 'income' in result.output and 'regression' in result.output  
                assert 'category' in result.output and 'mode' in result.output
                
                # Check outlier information display
                assert 'Outliers: 2 (2.0%)' in result.output
                assert 'Outliers: 3 (3.0%)' in result.output
                
                # Check output file handling
                assert f'Results saved to: {output_file.name}' in result.output
                assert mock_save.called
                
                os.unlink(output_file.name)
                
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    @patch('funputer.cli.analyze_imputation_requirements')
    def test_auto_metadata_inference_workflow(self, mock_analyze):
        """Test workflow with automatic metadata inference."""
        # Mock analysis with auto-inferred metadata
        mock_suggestions = [
            ImputationSuggestion(
                column_name='age',
                proposed_method='mean',
                rationale='Auto-inferred numeric feature',
                missing_count=10,
                missing_percentage=10.0,
                mechanism='MCAR',
                outlier_count=1,
                outlier_percentage=1.0,
                outlier_handling='keep',
                outlier_rationale='Outlier within range',
                confidence_score=0.70
            )
        ]
        mock_analyze.return_value = mock_suggestions
        
        data_file, metadata_file = self.create_sample_files()
        
        try:
            # Analyze without metadata file (auto-inference)
            result = self.runner.invoke(cli, [
                'analyze',
                '--data', data_file,
                '--verbose'
            ])
            
            assert result.exit_code == 0
            
            # Check that it indicates auto-inference
            assert 'Auto-inferring metadata' in result.output
            assert 'Analysis Results' in result.output
            
            # Verify analyze was called without metadata_path
            call_args = mock_analyze.call_args
            assert 'data_path' in call_args.kwargs
            assert call_args.kwargs.get('metadata_path') is None
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)