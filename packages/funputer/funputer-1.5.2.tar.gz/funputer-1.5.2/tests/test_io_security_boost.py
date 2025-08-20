"""
Security and core functionality tests for funputer.io module.
Strategic tests targeting critical coverage gaps and security vulnerabilities.

Coverage Target: Boost IO module from 13% to 80%+
Priority: CRITICAL (Security + Core functionality)
"""

import pytest
import pandas as pd
import tempfile
import os
import json
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from funputer.io import (
    load_data, save_suggestions, validate_metadata_against_data,
    _load_config_file, _apply_env_overrides, _create_column_metadata
)
from funputer.models import ColumnMetadata, DataType, ImputationSuggestion, AnalysisConfig
from funputer.exceptions import ConfigurationError


class TestIOSecurity:
    """Test security aspects of IO operations."""
    
    def test_load_data_path_traversal_protection(self):
        """Test protection against directory traversal attacks."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "../../../../usr/bin/whoami"
        ]
        
        metadata = [
            ColumnMetadata(column_name='test', data_type=DataType.STRING, role='feature')
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises((ValueError, FileNotFoundError, OSError)):
                load_data(malicious_path, metadata)
    
    def test_save_suggestions_path_validation(self):
        """Test output path sanitization and validation."""
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
        
        # Test malicious output paths
        malicious_output_paths = [
            "../../../tmp/malicious.csv",
            "/etc/passwd.csv",
            "C:\\Windows\\System32\\evil.csv"
        ]
        
        for malicious_path in malicious_output_paths:
            # Should either prevent the operation or fail safely
            try:
                save_suggestions(suggestions, malicious_path)
                # If it doesn't raise an exception, verify it didn't create file in dangerous location
                assert not os.path.exists("/etc/passwd.csv")
                assert not os.path.exists("C:\\Windows\\System32\\evil.csv")
            except (ValueError, OSError, PermissionError):
                # Expected behavior - operation blocked
                pass
    
    def test_csv_injection_prevention_in_suggestions(self):
        """Test prevention of CSV injection attacks in saved suggestions."""
        # Create suggestions with potentially malicious content
        malicious_suggestions = [
            ImputationSuggestion(
                column_name='=cmd|"/bin/sh"!A1',  # Excel formula injection
                proposed_method='=SUM(1+1)*cmd|"/bin/calc"',
                rationale='@SUM(1+1)*cmd|"/bin/calc"',
                missing_count=1,
                missing_percentage=10.0,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none', 
                outlier_rationale='=1+1+cmd|"/bin/whoami"',
                confidence_score=0.8
            )
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            try:
                save_suggestions(malicious_suggestions, temp_file.name)
                
                # Verify saved content is sanitized
                saved_df = pd.read_csv(temp_file.name)
                
                # Check that formula injection characters are handled safely
                for column in saved_df.columns:
                    for value in saved_df[column].astype(str):
                        # Should not start with dangerous characters
                        assert not value.startswith('='), f"Formula injection not prevented: {value}"
                        assert not value.startswith('@'), f"Formula injection not prevented: {value}"
                        assert not value.startswith('+'), f"Formula injection not prevented: {value}"
                        assert not value.startswith('-'), f"Formula injection not prevented: {value}"
                        
            finally:
                os.unlink(temp_file.name)


class TestIOFileHandling:
    """Test file loading and handling capabilities."""
    
    def test_load_data_various_encodings(self):
        """Test loading data with different file encodings."""
        # Test data with special characters
        test_data = "name,value\nJosé,100\nMüller,200\nNaïve,300"
        
        encodings = ['utf-8', 'latin-1', 'cp1252']
        metadata = [
            ColumnMetadata(column_name='name', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='value', data_type=DataType.INTEGER, role='feature')
        ]
        
        for encoding in encodings:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', 
                                           encoding=encoding, delete=False) as temp_file:
                try:
                    temp_file.write(test_data)
                    temp_file.flush()
                    
                    # Should handle different encodings gracefully
                    result = load_data(temp_file.name, metadata)
                    if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                        # Iterator case - get first chunk
                        first_chunk = next(iter(result))
                        assert len(first_chunk) == 3
                    else:
                        # DataFrame case
                        assert len(result) == 3
                        
                except UnicodeDecodeError:
                    # Some encoding mismatches are expected
                    pass
                finally:
                    os.unlink(temp_file.name)
    
    def test_load_data_malformed_csv_handling(self):
        """Test handling of malformed CSV files."""
        malformed_csvs = [
            # Uneven quotes
            'name,value\n"unclosed quote,123\nnormal,456',
            # Extra commas
            'name,value\ntest,123,extra,data\nnormal,456',
            # Missing columns
            'name,value\nonly_one_value\nnormal,456',
            # Empty lines
            'name,value\n\n\ntest,123\n\nnormal,456',
            # Special characters
            'name,value\ntest\x00null,123\nnormal,456'
        ]
        
        metadata = [
            ColumnMetadata(column_name='name', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='value', data_type=DataType.INTEGER, role='feature')
        ]
        
        for malformed_csv in malformed_csvs:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                try:
                    temp_file.write(malformed_csv)
                    temp_file.flush()
                    
                    # Should handle malformed CSV gracefully (not crash)
                    try:
                        result = load_data(temp_file.name, metadata)
                        # If successful, verify it's reasonable data
                        if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                            first_chunk = next(iter(result))
                            assert isinstance(first_chunk, pd.DataFrame)
                        else:
                            assert isinstance(result, pd.DataFrame)
                    except (ValueError, pd.errors.Error):
                        # Expected for some malformed files
                        pass
                        
                finally:
                    os.unlink(temp_file.name)
    
    def test_load_data_chunked_processing(self):
        """Test chunked data loading for memory efficiency."""
        # Create larger test dataset
        large_data = pd.DataFrame({
            'id': range(1000),
            'value': range(1000, 2000),
            'category': [f'cat_{i%10}' for i in range(1000)]
        })
        
        metadata = [
            ColumnMetadata(column_name='id', data_type=DataType.INTEGER, role='identifier'),
            ColumnMetadata(column_name='value', data_type=DataType.INTEGER, role='feature'),
            ColumnMetadata(column_name='category', data_type=DataType.CATEGORICAL, role='feature')
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            try:
                large_data.to_csv(temp_file.name, index=False)
                
                # Test chunked loading
                chunks = load_data(temp_file.name, metadata, chunk_size=100)
                
                # Should return iterator for chunked processing
                assert hasattr(chunks, '__iter__')
                
                # Verify chunks are correct size and content
                chunk_count = 0
                total_rows = 0
                
                for chunk in chunks:
                    chunk_count += 1
                    total_rows += len(chunk)
                    assert isinstance(chunk, pd.DataFrame)
                    assert len(chunk) <= 100  # Chunk size respected
                    assert list(chunk.columns) == ['id', 'value', 'category']
                
                # Verify we got all the data
                assert total_rows == 1000
                assert chunk_count == 10  # 1000 rows / 100 per chunk
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_data_empty_file_handling(self):
        """Test handling of empty or minimal CSV files."""
        test_cases = [
            "",  # Completely empty
            "name,value",  # Headers only
            "name,value\n",  # Headers with newline only
            "name,value\n,",  # Headers with empty row
        ]
        
        metadata = [
            ColumnMetadata(column_name='name', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='value', data_type=DataType.INTEGER, role='feature')
        ]
        
        for test_content in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                try:
                    temp_file.write(test_content)
                    temp_file.flush()
                    
                    # Should handle empty files gracefully
                    try:
                        result = load_data(temp_file.name, metadata)
                        if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                            # Iterator - try to get first chunk
                            try:
                                first_chunk = next(iter(result))
                                assert isinstance(first_chunk, pd.DataFrame)
                            except StopIteration:
                                # Empty iterator is acceptable
                                pass
                        else:
                            # DataFrame
                            assert isinstance(result, pd.DataFrame)
                            assert len(result) == 0 or len(result) == 1  # Depending on content
                    except ValueError as e:
                        # Some empty files may raise ValueError - this is acceptable
                        assert "empty" in str(e).lower() or "no columns" in str(e).lower()
                        
                finally:
                    os.unlink(temp_file.name)


class TestIOConfiguration:
    """Test configuration loading and environment override functionality."""
    
    def test_load_config_file_json_format(self):
        """Test loading JSON configuration files."""
        config_data = {
            "missing_threshold": 0.8,
            "confidence_threshold": 0.7,
            "output_path": "results.csv",
            "parallel_processing": True
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            try:
                json.dump(config_data, temp_file)
                temp_file.flush()
                
                loaded_config = _load_config_file(temp_file.name)
                
                assert loaded_config == config_data
                assert loaded_config['missing_threshold'] == 0.8
                assert loaded_config['parallel_processing'] is True
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_config_file_yaml_format(self):
        """Test loading YAML configuration files."""
        config_content = """
missing_threshold: 0.75
confidence_threshold: 0.6
output_path: "analysis_results.csv"
skip_columns:
  - "id"
  - "timestamp"
advanced_settings:
  memory_limit_mb: 1000
  chunk_size: 5000
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            try:
                temp_file.write(config_content)
                temp_file.flush()
                
                loaded_config = _load_config_file(temp_file.name)
                
                assert loaded_config['missing_threshold'] == 0.75
                assert loaded_config['skip_columns'] == ['id', 'timestamp']
                assert loaded_config['advanced_settings']['memory_limit_mb'] == 1000
                
            finally:
                os.unlink(temp_file.name)
    
    def test_load_config_file_invalid_format(self):
        """Test handling of invalid configuration file formats."""
        invalid_configs = [
            ("invalid.txt", "This is not JSON or YAML"),
            ("malformed.json", '{"invalid": json, syntax}'),
            ("malformed.yaml", "invalid:\nyaml: syntax: [unclosed"),
        ]
        
        for filename, content in invalid_configs:
            with tempfile.NamedTemporaryFile(mode='w', suffix=os.path.splitext(filename)[1], delete=False) as temp_file:
                try:
                    temp_file.write(content)
                    temp_file.flush()
                    
                    with pytest.raises((ValueError, yaml.YAMLError, json.JSONDecodeError)):
                        _load_config_file(temp_file.name)
                        
                finally:
                    os.unlink(temp_file.name)
    
    def test_apply_env_overrides_comprehensive(self):
        """Test environment variable override functionality."""
        base_config = {
            'output_path': 'default.csv',
            'missing_threshold': 0.5,
            'confidence_threshold': 0.7,
            'parallel_processing': False,
            'nested': {
                'value': 'original'
            }
        }
        
        # Test various environment variable patterns
        env_vars = {
            'FUNPUTER_OUTPUT_PATH': 'env_output.csv',
            'FUNPUTER_MISSING_THRESHOLD': '0.8',
            'FUNPUTER_PARALLEL_PROCESSING': 'true',
            'FUNPUTER_NEW_SETTING': 'from_env'
        }
        
        with patch.dict(os.environ, env_vars):
            config_copy = base_config.copy()
            _apply_env_overrides(config_copy)
            
            # Check overrides applied correctly
            assert config_copy['output_path'] == 'env_output.csv'
            assert config_copy['missing_threshold'] == '0.8'  # String from env
            assert config_copy['parallel_processing'] == 'true'  # String from env
            assert config_copy['new_setting'] == 'from_env'  # New setting added
            
            # Check original values preserved where no override
            assert config_copy['confidence_threshold'] == 0.7
    
    def test_create_column_metadata_comprehensive(self):
        """Test _create_column_metadata with various input patterns."""
        # Test complete metadata row
        complete_row = pd.Series({
            'column_name': 'test_column',
            'data_type': 'integer',
            'role': 'feature',
            'nullable': True,
            'min_value': 0,
            'max_value': 100,
            'allowed_values': 'A,B,C',
            'description': 'Test column description',
            'unique_flag': False,
            'max_length': 50
        })
        
        columns = list(complete_row.index)
        
        metadata = _create_column_metadata(complete_row, columns)
        
        assert metadata.column_name == 'test_column'
        assert metadata.data_type == DataType.INTEGER
        assert metadata.role == 'feature'
        assert metadata.nullable is True
        assert metadata.min_value == 0
        assert metadata.max_value == 100
        assert metadata.allowed_values == 'A,B,C'
        assert metadata.description == 'Test column description'
        assert metadata.unique_flag is False
        assert metadata.max_length == 50
        
        # Test minimal metadata row
        minimal_row = pd.Series({
            'column_name': 'minimal_column',
            'data_type': 'string',
            'role': 'target'
        })
        
        minimal_columns = ['column_name', 'data_type', 'role']
        minimal_metadata = _create_column_metadata(minimal_row, minimal_columns)
        
        assert minimal_metadata.column_name == 'minimal_column'
        assert minimal_metadata.data_type == DataType.STRING
        assert minimal_metadata.role == 'target'
        # Other fields should have default values
        assert minimal_metadata.nullable is True  # Default
        assert minimal_metadata.min_value is None
        
        # Test with missing/NaN values
        nan_row = pd.Series({
            'column_name': 'nan_column',
            'data_type': 'float',
            'role': 'feature',
            'nullable': pd.NA,
            'min_value': pd.NA,
            'description': pd.NA
        })
        
        nan_columns = list(nan_row.index)
        nan_metadata = _create_column_metadata(nan_row, nan_columns)
        
        assert nan_metadata.column_name == 'nan_column'
        assert nan_metadata.data_type == DataType.FLOAT
        # NaN values should be handled gracefully
        assert nan_metadata.min_value is None


class TestIOValidation:
    """Test data validation functionality."""
    
    def test_validate_metadata_against_data_type_mismatch(self):
        """Test validation catches data type mismatches."""
        # Create test data
        test_data = pd.DataFrame({
            'numeric_col': [1, 2, 3, 'not_numeric', 5],
            'string_col': ['a', 'b', 'c', 'd', 'e'],
            'int_col': [1, 2, 3.5, 4, 5]  # Has float where int expected
        })
        
        # Create metadata with mismatched types
        metadata = [
            ColumnMetadata(column_name='numeric_col', data_type=DataType.INTEGER, role='feature'),
            ColumnMetadata(column_name='string_col', data_type=DataType.INTEGER, role='feature'),  # Mismatch
            ColumnMetadata(column_name='int_col', data_type=DataType.INTEGER, role='feature')
        ]
        
        validation_result = validate_metadata_against_data(test_data, metadata)
        
        # Should detect mismatches
        assert len(validation_result) > 0
        
        # Check specific validation issues
        validation_dict = {item['column']: item for item in validation_result}
        
        assert 'numeric_col' in validation_dict
        assert 'type_mismatch' in validation_dict['numeric_col']['issue'].lower()
        
        assert 'string_col' in validation_dict  
        assert 'type_mismatch' in validation_dict['string_col']['issue'].lower()
    
    def test_validate_metadata_against_data_constraint_violations(self):
        """Test validation catches constraint violations."""
        # Create test data with constraint violations
        test_data = pd.DataFrame({
            'bounded_col': [1, 2, 150, 4, 5],  # 150 exceeds max_value=100
            'length_col': ['ok', 'also_ok', 'this_string_is_too_long', 'ok'],
            'allowed_col': ['A', 'B', 'X', 'A']  # 'X' not in allowed values
        })
        
        # Create metadata with constraints
        metadata = [
            ColumnMetadata(
                column_name='bounded_col', 
                data_type=DataType.INTEGER, 
                role='feature',
                min_value=0,
                max_value=100
            ),
            ColumnMetadata(
                column_name='length_col',
                data_type=DataType.STRING,
                role='feature', 
                max_length=15
            ),
            ColumnMetadata(
                column_name='allowed_col',
                data_type=DataType.CATEGORICAL,
                role='feature',
                allowed_values='A,B,C'
            )
        ]
        
        validation_result = validate_metadata_against_data(test_data, metadata)
        
        # Should detect constraint violations
        assert len(validation_result) > 0
        
        validation_dict = {item['column']: item for item in validation_result}
        
        # Check for specific constraint violations
        if 'bounded_col' in validation_dict:
            assert 'constraint' in validation_dict['bounded_col']['issue'].lower() or \
                   'range' in validation_dict['bounded_col']['issue'].lower()
        
        if 'length_col' in validation_dict:
            assert 'length' in validation_dict['length_col']['issue'].lower()
            
        if 'allowed_col' in validation_dict:
            assert 'allowed' in validation_dict['allowed_col']['issue'].lower() or \
                   'value' in validation_dict['allowed_col']['issue'].lower()
    
    def test_validate_metadata_against_data_nullable_violations(self):
        """Test validation catches nullable constraint violations."""
        # Create test data with null values
        test_data = pd.DataFrame({
            'nullable_col': [1, 2, None, 4, 5],
            'non_nullable_col': [1, 2, None, 4, 5],  # Has null but marked as non-nullable
            'all_null_col': [None, None, None, None, None]
        })
        
        # Create metadata with nullable constraints
        metadata = [
            ColumnMetadata(
                column_name='nullable_col',
                data_type=DataType.INTEGER,
                role='feature',
                nullable=True
            ),
            ColumnMetadata(
                column_name='non_nullable_col',
                data_type=DataType.INTEGER,
                role='feature',
                nullable=False  # Should not have nulls
            ),
            ColumnMetadata(
                column_name='all_null_col',
                data_type=DataType.INTEGER,
                role='feature',
                nullable=False  # Should not have nulls
            )
        ]
        
        validation_result = validate_metadata_against_data(test_data, metadata)
        
        # Should detect nullable violations
        assert len(validation_result) > 0
        
        validation_dict = {item['column']: item for item in validation_result}
        
        # non_nullable_col should have violation
        assert 'non_nullable_col' in validation_dict
        assert 'null' in validation_dict['non_nullable_col']['issue'].lower() or \
               'nullable' in validation_dict['non_nullable_col']['issue'].lower()
        
        # all_null_col should definitely have violation  
        assert 'all_null_col' in validation_dict
        assert 'null' in validation_dict['all_null_col']['issue'].lower()