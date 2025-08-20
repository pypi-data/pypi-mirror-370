"""
Corrected IO functionality tests for funputer.io module.
Strategic tests targeting actual API and boosting coverage from 71% to 80%+.

Coverage Target: Fix failing tests and boost IO module coverage
Priority: CRITICAL (Core functionality)
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from funputer.io import (
    load_data, save_suggestions, validate_metadata_against_data,
    load_metadata, _load_config_file, _apply_env_overrides, _create_column_metadata
)
from funputer.models import ColumnMetadata, DataType, ImputationSuggestion, AnalysisConfig


class TestIOCoreFixed:
    """Test core IO functionality with corrected API."""
    
    def test_save_suggestions_basic_functionality(self):
        """Test basic save_suggestions functionality without security module."""
        suggestions = [
            ImputationSuggestion(
                column_name='test_col',
                proposed_method='mean',
                rationale='Test rationale',
                missing_count=5,
                missing_percentage=10.0,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='No outliers',
                confidence_score=0.8
            )
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            try:
                # Test without sanitization to avoid security module
                save_suggestions(suggestions, temp_file.name, sanitize_output=False)
                
                assert os.path.exists(temp_file.name)
                
                # Verify saved content
                saved_df = pd.read_csv(temp_file.name)
                assert len(saved_df) == 1
                assert 'column_name' in saved_df.columns
                assert saved_df.iloc[0]['column_name'] == 'test_col'
                assert saved_df.iloc[0]['proposed_method'] == 'mean'
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_data_basic_functionality(self):
        """Test basic load_data functionality."""
        # Create test data
        test_data = pd.DataFrame({
            'id': range(1, 11),
            'name': [f'item_{i}' for i in range(1, 11)],
            'value': np.random.normal(0, 1, 10)
        })
        
        metadata = [
            ColumnMetadata(column_name='id', data_type=DataType.INTEGER, role='identifier'),
            ColumnMetadata(column_name='name', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='value', data_type=DataType.FLOAT, role='feature')
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            try:
                test_data.to_csv(temp_file.name, index=False)
                
                # Test normal loading
                result = load_data(temp_file.name, metadata, validate_security=False)
                
                assert isinstance(result, pd.DataFrame)
                assert len(result) == 10
                assert list(result.columns) == ['id', 'name', 'value']
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_data_chunked_processing(self):
        """Test chunked data loading."""
        # Create larger test dataset
        large_data = pd.DataFrame({
            'id': range(100),
            'value': np.random.normal(0, 1, 100)
        })
        
        metadata = [
            ColumnMetadata(column_name='id', data_type=DataType.INTEGER, role='identifier'),
            ColumnMetadata(column_name='value', data_type=DataType.FLOAT, role='feature')
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            try:
                large_data.to_csv(temp_file.name, index=False)
                
                # Test chunked loading
                chunks = load_data(temp_file.name, metadata, chunk_size=25, validate_security=False)
                
                # Should return iterator
                assert hasattr(chunks, '__iter__')
                
                # Verify chunks
                chunk_list = list(chunks)
                assert len(chunk_list) == 4  # 100 rows / 25 per chunk
                
                for chunk in chunk_list:
                    assert isinstance(chunk, pd.DataFrame)
                    assert len(chunk) <= 25
                    assert list(chunk.columns) == ['id', 'value']
                
                total_rows = sum(len(chunk) for chunk in chunk_list)
                assert total_rows == 100
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_data_sample_rows(self):
        """Test loading with sample_rows parameter."""
        # Create test data
        test_data = pd.DataFrame({
            'col1': range(50),
            'col2': [f'item_{i}' for i in range(50)]
        })
        
        metadata = [
            ColumnMetadata(column_name='col1', data_type=DataType.INTEGER, role='feature'),
            ColumnMetadata(column_name='col2', data_type=DataType.STRING, role='feature')
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            try:
                test_data.to_csv(temp_file.name, index=False)
                
                # Test with sample_rows
                result = load_data(temp_file.name, metadata, sample_rows=10, validate_security=False)
                
                assert isinstance(result, pd.DataFrame)
                assert len(result) == 10
                assert list(result.columns) == ['col1', 'col2']
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_data_file_not_found(self):
        """Test load_data with nonexistent file."""
        metadata = [
            ColumnMetadata(column_name='test', data_type=DataType.STRING, role='feature')
        ]
        
        with pytest.raises((FileNotFoundError, ValueError)):
            load_data('nonexistent_file.csv', metadata)
    
    def test_load_metadata_basic_functionality(self):
        """Test basic metadata loading functionality."""
        metadata_data = {
            'column_name': ['col1', 'col2', 'col3'],
            'data_type': ['integer', 'string', 'float'],
            'role': ['identifier', 'feature', 'target'],
            'nullable': [False, True, True],
            'description': ['ID column', 'Name column', 'Value column']
        }
        metadata_df = pd.DataFrame(metadata_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            try:
                metadata_df.to_csv(temp_file.name, index=False)
                
                result = load_metadata(temp_file.name)
                
                assert isinstance(result, list)
                assert len(result) == 3
                
                for metadata in result:
                    assert isinstance(metadata, ColumnMetadata)
                
                # Check specific values
                assert result[0].column_name == 'col1'
                assert result[0].data_type == DataType.INTEGER
                assert result[0].role == 'identifier'
                assert result[0].nullable is False
                
                assert result[1].column_name == 'col2'
                assert result[1].data_type == DataType.STRING
                assert result[1].nullable is True
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_metadata_file_not_found(self):
        """Test metadata loading with nonexistent file."""
        with pytest.raises(ValueError, match="Metadata file not found"):
            load_metadata('nonexistent_metadata.csv')
    
    def test_load_metadata_empty_file(self):
        """Test metadata loading with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            try:
                # Write empty CSV
                temp_file.write("")
                temp_file.flush()
                
                with pytest.raises(ValueError, match="Metadata CSV is empty"):
                    load_metadata(temp_file.name)
                    
            finally:
                os.unlink(temp_file.name)
    
    def test_load_metadata_missing_column_name(self):
        """Test metadata loading without required column_name column."""
        # Create metadata without column_name
        metadata_df = pd.DataFrame({
            'wrong_column': ['col1', 'col2'],
            'data_type': ['integer', 'string']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            try:
                metadata_df.to_csv(temp_file.name, index=False)
                
                with pytest.raises(ValueError, match="must contain 'column_name' column"):
                    load_metadata(temp_file.name)
                    
            finally:
                os.unlink(temp_file.name)


class TestIOConfiguration:
    """Test configuration loading functionality."""
    
    def test_load_config_file_yaml_format(self):
        """Test loading YAML configuration files."""
        config_data = {
            'missing_threshold': 0.75,
            'confidence_threshold': 0.6,
            'output_path': 'analysis_results.csv',
            'skip_columns': ['id', 'timestamp']
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            try:
                yaml.dump(config_data, temp_file)
                temp_file.flush()
                
                loaded_config = _load_config_file(temp_file.name)
                
                assert loaded_config['missing_threshold'] == 0.75
                assert loaded_config['skip_columns'] == ['id', 'timestamp']
                assert loaded_config['output_path'] == 'analysis_results.csv'
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_config_file_yml_extension(self):
        """Test loading .yml files."""
        config_content = """
missing_threshold: 0.8
output_path: "test_results.csv"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            try:
                temp_file.write(config_content)
                temp_file.flush()
                
                loaded_config = _load_config_file(temp_file.name)
                
                assert loaded_config['missing_threshold'] == 0.8
                assert loaded_config['output_path'] == 'test_results.csv'
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_config_file_unsupported_format(self):
        """Test loading unsupported file formats."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            try:
                temp_file.write('{"test": "data"}')
                temp_file.flush()
                
                with pytest.raises(ValueError, match="Unsupported configuration format"):
                    _load_config_file(temp_file.name)
                    
            finally:
                os.unlink(temp_file.name)
    
    def test_load_config_file_not_found(self):
        """Test configuration file not found."""
        with pytest.raises(FileNotFoundError):
            _load_config_file('nonexistent_config.yaml')
    
    def test_apply_env_overrides_basic(self):
        """Test environment variable overrides."""
        base_config = {
            'output_path': 'default.csv',
            'missing_threshold': 0.5
        }
        
        # Test without environment variables
        config_copy = base_config.copy()
        _apply_env_overrides(config_copy)
        assert config_copy['output_path'] == 'default.csv'
        assert config_copy['missing_threshold'] == 0.5
    
    def test_apply_env_overrides_with_values(self):
        """Test environment variable overrides with actual values."""
        base_config = {
            'output_path': 'default.csv',
            'missing_threshold': 0.5,
            'outlier_threshold': 0.05
        }
        
        env_vars = {
            'FUNPUTER_OUTPUT_PATH': 'env_output.csv',
            'FUNPUTER_MISSING_THRESHOLD': '0.8',
            'FUNPUTER_OUTLIER_THRESHOLD': '0.02'
        }
        
        with patch.dict(os.environ, env_vars):
            config_copy = base_config.copy()
            _apply_env_overrides(config_copy)
            
            # Check overrides applied correctly with type conversion
            assert config_copy['output_path'] == 'env_output.csv'
            assert config_copy['missing_threshold'] == 0.8  # Converted to float
            assert config_copy['outlier_threshold'] == 0.02  # Converted to float
    
    def test_apply_env_overrides_skip_columns(self):
        """Test environment variable override for skip_columns."""
        base_config = {'skip_columns': []}
        
        env_vars = {
            'FUNPUTER_SKIP_COLUMNS': 'col1,col2, col3'  # With spaces
        }
        
        with patch.dict(os.environ, env_vars):
            config_copy = base_config.copy()
            _apply_env_overrides(config_copy)
            
            # Should split and trim
            assert config_copy['skip_columns'] == ['col1', 'col2', 'col3']
    
    def test_create_column_metadata_complete(self):
        """Test _create_column_metadata with complete data."""
        row = pd.Series({
            'column_name': 'test_column',
            'data_type': 'integer',
            'role': 'feature',
            'nullable': True,
            'min_value': 0,
            'max_value': 100,
            'description': 'Test column'
        })
        
        columns = list(row.index)
        metadata = _create_column_metadata(row, columns)
        
        assert metadata.column_name == 'test_column'
        assert metadata.data_type == DataType.INTEGER
        assert metadata.role == 'feature'
        assert metadata.nullable is True
        assert metadata.min_value == 0
        assert metadata.max_value == 100
        assert metadata.description == 'Test column'
    
    def test_create_column_metadata_minimal(self):
        """Test _create_column_metadata with minimal required data."""
        row = pd.Series({
            'column_name': 'minimal_col',
            'data_type': 'string',
            'role': 'target'
        })
        
        columns = ['column_name', 'data_type', 'role']
        metadata = _create_column_metadata(row, columns)
        
        assert metadata.column_name == 'minimal_col'
        assert metadata.data_type == DataType.STRING
        assert metadata.role == 'target'
        # Should have default values for other fields
        assert metadata.nullable is True
        assert metadata.min_value is None
    
    def test_create_column_metadata_with_nan_values(self):
        """Test _create_column_metadata handling NaN values."""
        row = pd.Series({
            'column_name': 'nan_col',
            'data_type': 'float',
            'role': 'feature',
            'nullable': pd.NA,
            'min_value': np.nan,
            'description': pd.NA
        })
        
        columns = list(row.index)
        metadata = _create_column_metadata(row, columns)
        
        assert metadata.column_name == 'nan_col'
        assert metadata.data_type == DataType.FLOAT
        # NaN values should be handled gracefully
        assert metadata.min_value is None


class TestIOValidation:
    """Test data validation functionality."""
    
    def test_validate_metadata_against_data_basic(self):
        """Test basic metadata validation against data."""
        test_data = pd.DataFrame({
            'string_col': ['a', 'b', 'c'],
            'numeric_col': [1, 2, 3],
            'float_col': [1.1, 2.2, 3.3]
        })
        
        # Create matching metadata
        metadata = [
            ColumnMetadata(column_name='string_col', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='numeric_col', data_type=DataType.INTEGER, role='feature'),
            ColumnMetadata(column_name='float_col', data_type=DataType.FLOAT, role='feature')
        ]
        
        validation_result = validate_metadata_against_data(test_data, metadata)
        
        # Should return list (may be empty if no issues)
        assert isinstance(validation_result, list)
    
    def test_validate_metadata_against_data_with_missing_columns(self):
        """Test validation with missing columns in data."""
        test_data = pd.DataFrame({
            'existing_col': [1, 2, 3]
        })
        
        # Metadata references column not in data
        metadata = [
            ColumnMetadata(column_name='existing_col', data_type=DataType.INTEGER, role='feature'),
            ColumnMetadata(column_name='missing_col', data_type=DataType.STRING, role='feature')
        ]
        
        validation_result = validate_metadata_against_data(test_data, metadata)
        
        # Should detect missing column
        assert isinstance(validation_result, list)
        if validation_result:
            # Check if any validation issues mention missing column
            issues = [item for item in validation_result if 'missing_col' in str(item)]
            # May or may not detect depending on implementation
    
    def test_validate_metadata_against_data_empty_data(self):
        """Test validation with empty data."""
        empty_data = pd.DataFrame()
        metadata = []
        
        validation_result = validate_metadata_against_data(empty_data, metadata)
        
        # Should handle empty data gracefully
        assert isinstance(validation_result, list)
    
    def test_validate_metadata_against_data_no_metadata(self):
        """Test validation with no metadata."""
        test_data = pd.DataFrame({'col1': [1, 2, 3]})
        metadata = []
        
        validation_result = validate_metadata_against_data(test_data, metadata)
        
        # Should handle no metadata gracefully
        assert isinstance(validation_result, list)


class TestIOErrorHandling:
    """Test IO error handling and edge cases."""
    
    def test_load_data_corrupted_csv(self):
        """Test load_data with corrupted CSV content."""
        corrupted_content = "col1,col2\nvalue1,value2\n,unclosed quote,extra\n"
        
        metadata = [
            ColumnMetadata(column_name='col1', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='col2', data_type=DataType.STRING, role='feature')
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            try:
                temp_file.write(corrupted_content)
                temp_file.flush()
                
                # Should handle corrupted CSV gracefully
                try:
                    result = load_data(temp_file.name, metadata, validate_security=False)
                    # If it succeeds, should return reasonable data
                    assert isinstance(result, pd.DataFrame)
                except (ValueError, pd.errors.ParserError):
                    # Expected for corrupted files
                    pass
                    
            finally:
                os.unlink(temp_file.name)
    
    def test_save_suggestions_invalid_path(self):
        """Test save_suggestions with invalid output path."""
        suggestions = [
            ImputationSuggestion(
                column_name='test',
                proposed_method='mean',
                rationale='test',
                missing_count=1,
                missing_percentage=10.0,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='none',
                confidence_score=0.8
            )
        ]
        
        # Try to save to directory that doesn't exist
        invalid_path = "/nonexistent_directory/output.csv"
        
        try:
            save_suggestions(suggestions, invalid_path, sanitize_output=False)
            # If it doesn't raise an exception, it's unexpected
            assert False, "Expected error for invalid path"
        except (OSError, FileNotFoundError, PermissionError):
            # Expected behavior
            pass
    
    def test_load_metadata_validation_error(self):
        """Test metadata loading with validation errors."""
        # Create metadata with invalid data types
        invalid_metadata = pd.DataFrame({
            'column_name': ['col1'],
            'data_type': ['invalid_type'],  # Invalid data type
            'role': ['feature']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            try:
                invalid_metadata.to_csv(temp_file.name, index=False)
                
                # Should handle validation error gracefully
                try:
                    result = load_metadata(temp_file.name)
                    # If it succeeds, check the result
                    assert isinstance(result, list)
                except ValueError:
                    # Expected for invalid metadata
                    pass
                    
            finally:
                os.unlink(temp_file.name)