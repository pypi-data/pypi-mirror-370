"""
Comprehensive tests for funputer.io module.
Targeting 51% → 80%+ coverage (42+ lines covered).

Priority: HIGH IMPACT - +3.3% overall coverage
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from funputer.io import (
    load_metadata, load_configuration, save_suggestions, load_data,
    get_column_metadata, validate_metadata_against_data,
    _load_metadata_csv, _create_column_metadata, _load_config_file,
    _apply_env_overrides, _ensure_dir_exists
)
from funputer.models import ColumnMetadata, AnalysisConfig, ImputationSuggestion
from funputer.exceptions import ConfigurationError, MetadataValidationError


class TestLoadMetadata:
    """Test metadata loading functionality."""
    
    def create_test_metadata_csv(self, valid=True):
        """Create test metadata CSV file."""
        if valid:
            metadata_data = pd.DataFrame({
                'column_name': ['id', 'age', 'income', 'category'],
                'data_type': ['integer', 'integer', 'float', 'categorical'],
                'role': ['identifier', 'feature', 'feature', 'feature'],
                'nullable': [False, True, True, True],
                'description': ['ID column', 'Age in years', 'Annual income', 'Category']
            })
        else:
            # Missing required column
            metadata_data = pd.DataFrame({
                'data_type': ['integer', 'float'],
                'description': ['Test col 1', 'Test col 2']
            })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        metadata_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        return temp_file.name
    
    def test_load_metadata_success(self):
        """Test successful metadata loading (lines 22-28)."""
        metadata_file = self.create_test_metadata_csv()
        
        try:
            metadata = load_metadata(metadata_file)
            
            assert isinstance(metadata, list)
            assert len(metadata) == 4
            assert all(isinstance(m, ColumnMetadata) for m in metadata)
            assert metadata[0].column_name == 'id'
            assert metadata[1].data_type == 'integer'
            
        finally:
            os.unlink(metadata_file)
    
    def test_load_metadata_file_not_found(self):
        """Test metadata loading with missing file (lines 24-25)."""
        with pytest.raises(ValueError) as exc_info:
            load_metadata('nonexistent_file.csv')
        
        assert 'Metadata file not found' in str(exc_info.value)
    
    def test_load_metadata_csv_read_error(self):
        """Test CSV reading error (lines 33-36)."""
        # Create file that cannot be read as CSV
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        # Write binary data that will cause CSV read error
        temp_file.write('\x00\x01\x02\x03\x04')  # Binary data
        temp_file.flush()
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_metadata(temp_file.name)
            
            assert 'Failed to read metadata CSV' in str(exc_info.value)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_load_metadata_csv_empty(self):
        """Test empty metadata CSV (lines 39-40)."""
        # Create empty CSV file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write('')  # Completely empty
        temp_file.flush()
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_metadata(temp_file.name)
            
            assert 'Metadata CSV is empty' in str(exc_info.value)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_load_metadata_csv_missing_column_name(self):
        """Test metadata CSV without column_name (lines 42-43)."""
        invalid_metadata_file = self.create_test_metadata_csv(valid=False)
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_metadata(invalid_metadata_file)
            
            assert 'column_name' in str(exc_info.value)
            
        finally:
            os.unlink(invalid_metadata_file)
    
    def test_load_metadata_csv_metadata_creation_error(self):
        """Test metadata creation error (lines 51-52)."""
        metadata_data = pd.DataFrame({
            'column_name': ['test_col'],
            'data_type': ['float']
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        metadata_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        
        try:
            with patch('funputer.io._create_column_metadata') as mock_create:
                mock_create.side_effect = Exception("Test creation error")
                
                with pytest.raises(ValueError) as exc_info:
                    load_metadata(temp_file.name)
                
                assert 'Failed to create metadata' in str(exc_info.value)
            
        finally:
            os.unlink(temp_file.name)


class TestColumnMetadataOperations:
    """Test column metadata utility functions."""
    
    def test_validate_metadata_against_data_missing_in_data(self):
        """Test metadata validation with columns missing in data (lines 78-79)."""
        metadata_list = [
            ColumnMetadata(column_name='col1', data_type='integer', role='feature'),
            ColumnMetadata(column_name='missing_col', data_type='float', role='feature')
        ]
        
        data_df = pd.DataFrame({'col1': [1, 2, 3]})
        
        warnings = validate_metadata_against_data(metadata_list, data_df)
        
        assert len(warnings) == 1
        assert 'Columns in metadata not found in data' in warnings[0]
        assert 'missing_col' in warnings[0]
    
    def test_validate_metadata_against_data_missing_in_metadata(self):
        """Test metadata validation with columns missing in metadata (lines 82-83)."""
        metadata_list = [
            ColumnMetadata(column_name='col1', data_type='integer', role='feature')
        ]
        
        data_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'extra_col': [4, 5, 6]
        })
        
        warnings = validate_metadata_against_data(metadata_list, data_df)
        
        assert len(warnings) == 1
        assert 'Columns in data not found in metadata' in warnings[0]
        assert 'extra_col' in warnings[0]


class TestLoadConfiguration:
    """Test configuration loading functionality."""
    
    def test_load_configuration_default(self):
        """Test loading default configuration (lines 90-91)."""
        config = load_configuration(config_path=None)
        
        assert isinstance(config, AnalysisConfig)
        assert config.missing_threshold > 0
        assert config.outlier_threshold > 0
    
    def test_load_configuration_file_error(self):
        """Test configuration loading error (lines 97-98)."""
        with pytest.raises(ConfigurationError) as exc_info:
            load_configuration('nonexistent_config.yaml')
        
        assert 'Failed to load configuration' in str(exc_info.value)
    
    def test_load_config_file_not_found(self):
        """Test config file not found (lines 260-261)."""
        with pytest.raises(FileNotFoundError) as exc_info:
            _load_config_file('nonexistent.yaml')
        
        assert 'Configuration file not found' in str(exc_info.value)
    
    def test_load_config_file_unsupported_format(self):
        """Test unsupported config format (lines 266-267)."""
        # Create a non-YAML file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write('some config content')
        temp_file.flush()
        
        try:
            with pytest.raises(ValueError) as exc_info:
                _load_config_file(temp_file.name)
            
            assert 'Unsupported configuration format' in str(exc_info.value)
            
        finally:
            os.unlink(temp_file.name)


class TestEnvironmentOverrides:
    """Test environment variable configuration overrides."""
    
    @patch.dict(os.environ, {'FUNPUTER_OUTPUT_PATH': '/custom/path.csv'})
    def test_apply_env_overrides_string_value(self):
        """Test environment override for string value (lines 281-289)."""
        config_dict = {}
        
        _apply_env_overrides(config_dict)
        
        assert config_dict['output_path'] == '/custom/path.csv'
    
    @patch.dict(os.environ, {'FUNPUTER_MISSING_THRESHOLD': '0.9'})
    def test_apply_env_overrides_float_value(self):
        """Test environment override for float value (lines 284-285)."""
        config_dict = {}
        
        _apply_env_overrides(config_dict)
        
        assert config_dict['missing_threshold'] == 0.9
    
    @patch.dict(os.environ, {'FUNPUTER_SKIP_COLUMNS': 'col1,col2,col3'})
    def test_apply_env_overrides_list_value(self):
        """Test environment override for list value (lines 286-287)."""
        config_dict = {}
        
        _apply_env_overrides(config_dict)
        
        assert config_dict['skip_columns'] == ['col1', 'col2', 'col3']


class TestSaveSuggestions:
    """Test saving imputation suggestions."""
    
    def test_save_suggestions_with_sanitization(self):
        """Test suggestion saving with sanitization (lines 121-124)."""
        suggestions = [
            ImputationSuggestion(
                column_name='test_col',
                missing_count=1,
                missing_percentage=0.1,
                mechanism='MCAR',
                proposed_method='Mean',
                rationale='Test rationale',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='Leave as is',
                outlier_rationale='No outliers',
                confidence_score=0.8
            )
        ]
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.close()
        
        try:
            # Mock the security module since it may not exist
            with patch('funputer.io.SecurityValidator') as mock_validator:
                mock_instance = MagicMock()
                mock_validator.return_value = mock_instance
                mock_instance.sanitize_dataframe.return_value = pd.DataFrame([suggestions[0].to_dict()])
                
                save_suggestions(suggestions, temp_file.name, sanitize_output=True)
                
                # Verify sanitization was called
                mock_validator.assert_called_once()
                mock_instance.sanitize_dataframe.assert_called_once()
            
        finally:
            os.unlink(temp_file.name)
    
    def test_ensure_dir_exists(self):
        """Test directory creation (lines 293-295)."""
        # Create a nested path that doesn't exist
        temp_dir = tempfile.mkdtemp()
        nested_path = os.path.join(temp_dir, 'level1', 'level2', 'file.csv')
        
        try:
            _ensure_dir_exists(nested_path)
            
            # Verify directories were created
            assert os.path.exists(os.path.dirname(nested_path))
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)


class TestLoadData:
    """Test data loading functionality."""
    
    def create_test_data_csv(self, rows=100):
        """Create test data CSV file."""
        data = pd.DataFrame({
            'id': range(rows),
            'value': np.random.randn(rows),
            'category': ['A', 'B', 'C'] * (rows // 3) + ['A'] * (rows % 3)
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        return temp_file.name
    
    def test_load_data_file_not_found(self):
        """Test data loading with missing file (lines 153-154)."""
        metadata = [ColumnMetadata(column_name='test', data_type='float', role='feature')]
        
        with pytest.raises(FileNotFoundError) as exc_info:
            load_data('nonexistent_file.csv', metadata)
        
        assert 'Data file not found' in str(exc_info.value)
    
    def test_load_data_not_a_file(self):
        """Test data loading with directory path (lines 155-156)."""
        temp_dir = tempfile.mkdtemp()
        metadata = [ColumnMetadata(column_name='test', data_type='float', role='feature')]
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_data(temp_dir, metadata)
            
            assert 'Path is not a file' in str(exc_info.value)
            
        finally:
            os.rmdir(temp_dir)
    
    def test_load_data_chunked_with_validation(self):
        """Test chunked data loading with metadata validation (lines 167-174)."""
        data_file = self.create_test_data_csv(rows=200)
        metadata = [
            ColumnMetadata(column_name='missing_col', data_type='float', role='feature')  # Not in data
        ]
        
        try:
            with patch('funputer.io.logging.getLogger') as mock_logger:
                mock_log = MagicMock()
                mock_logger.return_value = mock_log
                
                chunk_reader = load_data(data_file, metadata, chunk_size=50)
                
                # Should log warnings about metadata mismatch
                mock_log.warning.assert_called()
            
        finally:
            os.unlink(data_file)
    
    def test_load_data_sample_rows(self):
        """Test data loading with sample rows (lines 178-180)."""
        data_file = self.create_test_data_csv(rows=200)
        metadata = []
        
        try:
            data_df = load_data(data_file, metadata, sample_rows=50)
            
            assert isinstance(data_df, pd.DataFrame)
            assert len(data_df) == 50  # Should only load 50 rows
            
        finally:
            os.unlink(data_file)
    
    def test_load_data_empty_file(self):
        """Test loading empty data file (lines 186-187)."""
        # Create empty CSV file (header only)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write('col1,col2,col3\n')  # Header only
        temp_file.flush()
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_data(temp_file.name, [])
            
            assert 'Data file is empty' in str(exc_info.value)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_load_data_with_metadata_validation_warnings(self):
        """Test data loading with metadata validation warnings (lines 190-197)."""
        data_file = self.create_test_data_csv()
        
        # Create metadata that doesn't match data columns
        metadata = [
            ColumnMetadata(column_name='nonexistent_col', data_type='float', role='feature')
        ]
        
        try:
            with patch('funputer.io.logging.getLogger') as mock_logger:
                mock_log = MagicMock()
                mock_logger.return_value = mock_log
                
                data_df = load_data(data_file, metadata)
                
                # Should log warnings but still return data
                assert isinstance(data_df, pd.DataFrame)
                mock_log.warning.assert_called()
            
        finally:
            os.unlink(data_file)
    
    def test_load_data_exception_handling(self):
        """Test data loading exception handling (lines 201-202)."""
        # Create file that will cause pandas read error
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write('\x00\x01\x02\x03')  # Binary content that will fail CSV parsing
        temp_file.flush()
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_data(temp_file.name, [])
            
            assert 'Failed to load data' in str(exc_info.value)
            
        finally:
            os.unlink(temp_file.name)


class TestCreateColumnMetadata:
    """Test column metadata creation from CSV row."""
    
    def test_create_column_metadata_missing_column_name(self):
        """Test metadata creation with missing column name (lines 209-210)."""
        row = pd.Series({
            'data_type': 'float',
            'description': 'Test column'
        })
        available_columns = pd.Index(['data_type', 'description'])
        
        with pytest.raises(ValueError) as exc_info:
            _create_column_metadata(row, available_columns)
        
        assert 'column_name is required' in str(exc_info.value)
    
    def test_create_column_metadata_with_optional_fields(self):
        """Test metadata creation with optional fields (lines 222-248)."""
        row = pd.Series({
            'column_name': 'test_col',
            'data_type': 'integer',
            'nullable': True,
            'min_value': 0,
            'max_value': 100,
            'max_length': 10,
            'unique_flag': False,
            'role': 'feature'
        })
        available_columns = pd.Index([
            'column_name', 'data_type', 'nullable', 'min_value', 
            'max_value', 'max_length', 'unique_flag', 'role'
        ])
        
        metadata = _create_column_metadata(row, available_columns)
        
        assert metadata.column_name == 'test_col'
        assert metadata.nullable is True
        assert metadata.min_value == 0.0
        assert metadata.max_value == 100.0
        assert metadata.max_length == 10
        assert metadata.unique_flag is False
        assert metadata.role == 'feature'
    
    def test_create_column_metadata_type_conversion_errors(self):
        """Test metadata creation with type conversion errors (lines 238-246)."""
        row = pd.Series({
            'column_name': 'test_col',
            'data_type': 'integer',
            'min_value': 'not_a_number',  # Should convert to None
            'max_length': 'not_an_integer'  # Should convert to None
        })
        available_columns = pd.Index(['column_name', 'data_type', 'min_value', 'max_length'])
        
        metadata = _create_column_metadata(row, available_columns)
        
        assert metadata.column_name == 'test_col'
        assert metadata.min_value is None  # Failed conversion
        assert metadata.max_length is None  # Failed conversion
    
    def test_create_column_metadata_validation_error(self):
        """Test metadata creation with validation error (lines 252-253)."""
        row = pd.Series({
            'column_name': 'test_col',
            'data_type': 'float',
        })
        available_columns = pd.Index(['column_name', 'data_type'])
        
        # Mock ColumnMetadata to raise ValidationError
        with patch('funputer.io.ColumnMetadata') as mock_metadata:
            from pydantic import ValidationError
            mock_metadata.side_effect = ValidationError([], ColumnMetadata)
            
            with pytest.raises(ValueError) as exc_info:
                _create_column_metadata(row, available_columns)
            
            assert 'Validation error for column' in str(exc_info.value)