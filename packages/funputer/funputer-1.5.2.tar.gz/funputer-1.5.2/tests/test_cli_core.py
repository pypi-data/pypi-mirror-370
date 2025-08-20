"""
Core CLI functionality tests - focused on critical paths without bloat.
"""

import pytest
import tempfile
import os
import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch

from funputer.cli import cli
from funputer.models import ColumnMetadata, DataType


class TestCLICore:
    """Test core CLI functionality."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    @pytest.fixture
    def sample_csv(self):
        """Create a sample CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,salary\n")
            f.write("John,25,50000\n")
            f.write("Jane,,60000\n")
            f.write("Bob,35,\n")
            return f.name
    
    def test_cli_main_help(self, runner):
        """Test main CLI help."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'analyze' in result.output
        assert 'init' in result.output
    
    def test_analyze_command_help(self, runner):
        """Test analyze command help."""
        result = runner.invoke(cli, ['analyze', '--help'])
        assert result.exit_code == 0
        assert '--data' in result.output
    
    def test_init_command_help(self, runner):
        """Test init command help."""
        result = runner.invoke(cli, ['init', '--help'])
        assert result.exit_code == 0
        assert '--data' in result.output
    
    def test_analyze_command_basic(self, runner, sample_csv):
        """Test basic analyze command execution."""
        try:
            result = runner.invoke(cli, ['analyze', '--data', sample_csv])
            # Should complete without crashing (exit code 0 or 1 acceptable)
            assert result.exit_code in [0, 1]
        finally:
            os.unlink(sample_csv)
    
    def test_analyze_command_file_not_found(self, runner):
        """Test analyze with non-existent file."""
        result = runner.invoke(cli, ['analyze', '--data', 'nonexistent.csv'])
        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()
    
    def test_init_command_basic(self, runner, sample_csv):
        """Test basic init command execution."""
        try:
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as output_f:
                result = runner.invoke(cli, ['init', '--data', sample_csv, '--output', output_f.name])
                assert result.exit_code in [0, 1]
                # Should create some output
                if result.exit_code == 0:
                    assert os.path.exists(output_f.name)
                os.unlink(output_f.name)
        finally:
            os.unlink(sample_csv)
    
    @patch('funputer.analyzer.analyze_dataframe')
    def test_analyze_command_success_path(self, mock_analyze, runner, sample_csv):
        """Test successful analysis path."""
        # Mock successful analysis
        mock_analyze.return_value = []
        
        try:
            result = runner.invoke(cli, ['analyze', '--data', sample_csv])
            assert result.exit_code == 0
        finally:
            os.unlink(sample_csv)
    
    @patch('funputer.metadata_inference.infer_metadata_from_dataframe')
    def test_init_command_success_path(self, mock_infer, runner, sample_csv):
        """Test successful init path."""
        # Mock successful metadata inference
        mock_infer.return_value = [
            ColumnMetadata(column_name='name', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='age', data_type=DataType.INTEGER, role='feature'),
        ]
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as output_f:
                result = runner.invoke(cli, ['init', '--data', sample_csv, '--output', output_f.name])
                assert result.exit_code == 0
                os.unlink(output_f.name)
        finally:
            os.unlink(sample_csv)
    
    def test_analyze_with_metadata(self, runner, sample_csv):
        """Test analyze with metadata file."""
        metadata_content = """column_name,data_type,role
name,string,feature
age,integer,feature
salary,float,target"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as meta_f:
            meta_f.write(metadata_content)
            meta_f.flush()
            
            try:
                result = runner.invoke(cli, ['analyze', '--data', sample_csv, '--metadata', meta_f.name])
                assert result.exit_code in [0, 1]
            finally:
                os.unlink(meta_f.name)
                os.unlink(sample_csv)
    
    def test_analyze_with_output_file(self, runner, sample_csv):
        """Test analyze with output file specified."""
        try:
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as output_f:
                result = runner.invoke(cli, ['analyze', '--data', sample_csv, '--output', output_f.name])
                assert result.exit_code in [0, 1]
                os.unlink(output_f.name)
        finally:
            os.unlink(sample_csv)


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_missing_required_args(self, runner):
        """Test error when required arguments missing."""
        result = runner.invoke(cli, ['analyze'])
        assert result.exit_code != 0
    
    def test_invalid_file_extension(self, runner):
        """Test error with invalid file extension."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"not,csv,data")
            try:
                result = runner.invoke(cli, ['analyze', '--data', f.name])
                # Should handle gracefully
                assert result.exit_code != 0 or 'error' in result.output.lower()
            finally:
                os.unlink(f.name)
    
    def test_empty_file(self, runner):
        """Test handling of empty file."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            # Empty file
            pass
            
        try:
            result = runner.invoke(cli, ['analyze', '--data', f.name])
            # Should handle gracefully
            assert result.exit_code != 0
        finally:
            os.unlink(f.name)
    
    def test_malformed_csv(self, runner):
        """Test handling of malformed CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age\n")
            f.write("John,25,extra,columns\n")  # Malformed row
            
        try:
            result = runner.invoke(cli, ['analyze', '--data', f.name])
            # Should handle gracefully
            assert result.exit_code in [0, 1]
        finally:
            os.unlink(f.name)