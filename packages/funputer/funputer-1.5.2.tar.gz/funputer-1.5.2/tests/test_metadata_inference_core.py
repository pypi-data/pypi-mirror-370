"""
Core metadata inference tests - focused on critical functionality.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from funputer.metadata_inference import (
    infer_metadata_from_dataframe, 
    _infer_data_type,
    _infer_constraints
)
from funputer.models import DataType


class TestMetadataInferenceCore:
    """Test core metadata inference functionality."""
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create sample dataframe for testing."""
        return pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'salary': [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
            'is_active': [True, False, True, True, False],
            'department': ['Engineering', 'Sales', 'Engineering', 'Marketing', 'Sales'],
            'score': [85.5, 92.3, 78.1, 88.9, 91.2]
        })
    
    @pytest.fixture
    def dataframe_with_missing(self):
        """Create dataframe with missing values."""
        return pd.DataFrame({
            'complete': [1, 2, 3, 4, 5],
            'some_missing': [1, np.nan, 3, np.nan, 5],
            'mostly_missing': [1, np.nan, np.nan, np.nan, np.nan],
            'text_with_missing': ['A', 'B', None, 'D', 'E']
        })
    
    def test_infer_metadata_from_dataframe_basic(self, sample_dataframe):
        """Test basic metadata inference from dataframe."""
        metadata_list = infer_metadata_from_dataframe(sample_dataframe)
        
        assert len(metadata_list) == 7
        
        # Check column names are preserved
        column_names = [m.column_name for m in metadata_list]
        assert set(column_names) == set(sample_dataframe.columns)
        
        # Check data types are inferred
        name_metadata = next(m for m in metadata_list if m.column_name == 'name')
        assert name_metadata.data_type == DataType.STRING
        
        age_metadata = next(m for m in metadata_list if m.column_name == 'age')
        assert age_metadata.data_type == DataType.INTEGER
        
        salary_metadata = next(m for m in metadata_list if m.column_name == 'salary')
        assert salary_metadata.data_type == DataType.FLOAT
        
        is_active_metadata = next(m for m in metadata_list if m.column_name == 'is_active')
        assert is_active_metadata.data_type == DataType.BOOLEAN
    
    def test_infer_metadata_empty_dataframe(self):
        """Test metadata inference with empty dataframe."""
        df = pd.DataFrame()
        metadata_list = infer_metadata_from_dataframe(df)
        assert len(metadata_list) == 0
    
    def test_infer_metadata_single_column(self):
        """Test metadata inference with single column."""
        df = pd.DataFrame({'single_col': [1, 2, 3]})
        metadata_list = infer_metadata_from_dataframe(df)
        
        assert len(metadata_list) == 1
        assert metadata_list[0].column_name == 'single_col'
        assert metadata_list[0].data_type == DataType.INTEGER
    
    def test_infer_data_type_integer(self):
        """Test integer data type inference."""
        series = pd.Series([1, 2, 3, 4, 5])
        data_type = _infer_data_type(series)
        assert data_type == 'integer'
    
    def test_infer_data_type_float(self):
        """Test float data type inference."""
        series = pd.Series([1.1, 2.2, 3.3, 4.4, 5.5])
        data_type = infer_data_type(series)
        assert data_type == DataType.FLOAT
    
    def test_infer_data_type_string(self):
        """Test string data type inference."""
        series = pd.Series(['a', 'b', 'c', 'd', 'e'])
        data_type = infer_data_type(series)
        assert data_type == DataType.STRING
    
    def test_infer_data_type_boolean(self):
        """Test boolean data type inference."""
        series = pd.Series([True, False, True, False])
        data_type = infer_data_type(series)
        assert data_type == DataType.BOOLEAN
    
    def test_infer_data_type_categorical(self):
        """Test categorical data type inference."""
        # Limited unique values should be categorical
        series = pd.Series(['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B'])
        data_type = infer_data_type(series)
        assert data_type == DataType.CATEGORICAL
    
    def test_infer_data_type_with_missing(self):
        """Test data type inference with missing values."""
        series = pd.Series([1, 2, np.nan, 4, 5])
        data_type = infer_data_type(series)
        assert data_type == DataType.INTEGER
    
    def test_infer_data_type_mixed_types(self):
        """Test data type inference with mixed types."""
        series = pd.Series([1, '2', 3.0, '4', 5])
        data_type = infer_data_type(series)
        # Should default to string when mixed
        assert data_type == DataType.STRING
    
    def test_infer_role_identifier(self):
        """Test role inference for identifier columns."""
        # Column named 'id' with unique values
        series = pd.Series([1, 2, 3, 4, 5], name='id')
        role = infer_role('id', series)
        assert role == 'identifier'
        
        # Column named 'user_id' with unique values
        series = pd.Series(['user1', 'user2', 'user3'], name='user_id')
        role = infer_role('user_id', series)
        assert role == 'identifier'
    
    def test_infer_role_target(self):
        """Test role inference for target columns."""
        # Numeric column that could be a target
        series = pd.Series([100, 200, 150, 300, 250], name='price')
        role = infer_role('price', series)
        # Could be target or feature - depends on implementation
        assert role in ['target', 'feature']
    
    def test_infer_role_feature(self):
        """Test role inference for feature columns."""
        # Regular categorical column
        series = pd.Series(['A', 'B', 'A', 'C', 'B'], name='category')
        role = infer_role('category', series)
        assert role == 'feature'
    
    def test_infer_constraints_basic(self, sample_dataframe):
        """Test basic constraint inference."""
        for column in sample_dataframe.columns:
            series = sample_dataframe[column]
            constraints = _infer_constraints(series)
            
            # Should return a dictionary
            assert isinstance(constraints, dict)
            
            # Should have nullable constraint
            assert 'nullable' in constraints
            assert constraints['nullable'] == True  # No nulls in sample data
    
    def test_infer_constraints_with_missing(self, dataframe_with_missing):
        """Test constraint inference with missing values."""
        series = dataframe_with_missing['some_missing']
        constraints = _infer_constraints(series)
        
        assert constraints['nullable'] == True
    
    def test_infer_metadata_large_dataframe(self):
        """Test metadata inference performance with larger dataframe."""
        # Create larger dataframe to test performance
        size = 10000
        df = pd.DataFrame({
            'id': range(size),
            'category': np.random.choice(['A', 'B', 'C'], size),
            'value': np.random.normal(100, 15, size),
            'flag': np.random.choice([True, False], size)
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        
        assert len(metadata_list) == 4
        
        # Verify correct types inferred
        types_by_column = {m.column_name: m.data_type for m in metadata_list}
        assert types_by_column['id'] == DataType.INTEGER
        assert types_by_column['category'] == DataType.CATEGORICAL
        assert types_by_column['value'] == DataType.FLOAT
        assert types_by_column['flag'] == DataType.BOOLEAN


class TestMetadataInferenceEdgeCases:
    """Test edge cases in metadata inference."""
    
    def test_all_null_column(self):
        """Test inference with all null values."""
        df = pd.DataFrame({'all_null': [None, None, None, None]})
        metadata_list = infer_metadata_from_dataframe(df)
        
        assert len(metadata_list) == 1
        # Should default to string for all null
        assert metadata_list[0].data_type == DataType.STRING
        assert metadata_list[0].nullable == True
    
    def test_single_value_column(self):
        """Test inference with single unique value."""
        df = pd.DataFrame({'constant': [5, 5, 5, 5]})
        metadata_list = infer_metadata_from_dataframe(df)
        
        assert len(metadata_list) == 1
        assert metadata_list[0].data_type == DataType.INTEGER
    
    def test_numeric_strings(self):
        """Test inference with numeric strings."""
        df = pd.DataFrame({'numeric_strings': ['123', '456', '789']})
        metadata_list = infer_metadata_from_dataframe(df)
        
        assert len(metadata_list) == 1
        # Could be inferred as string or integer depending on implementation
        assert metadata_list[0].data_type in [DataType.STRING, DataType.INTEGER]
    
    def test_datetime_like_strings(self):
        """Test inference with datetime-like strings."""
        df = pd.DataFrame({
            'dates': ['2023-01-01', '2023-01-02', '2023-01-03']
        })
        metadata_list = infer_metadata_from_dataframe(df)
        
        assert len(metadata_list) == 1
        # Could be datetime or string
        assert metadata_list[0].data_type in [DataType.DATETIME, DataType.STRING]
    
    def test_very_long_strings(self):
        """Test inference with very long strings."""
        long_string = 'x' * 1000
        df = pd.DataFrame({'long_text': [long_string, long_string[:500], long_string[:750]]})
        metadata_list = infer_metadata_from_dataframe(df)
        
        assert len(metadata_list) == 1
        assert metadata_list[0].data_type == DataType.STRING
        # Should have max_length constraint
        assert hasattr(metadata_list[0], 'max_length')
    
    def test_special_column_names(self):
        """Test inference with special column names."""
        df = pd.DataFrame({
            'column with spaces': [1, 2, 3],
            'column-with-dashes': [4, 5, 6],
            'column_with_underscores': [7, 8, 9],
            '123numeric_start': [10, 11, 12]
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        
        assert len(metadata_list) == 4
        
        # All column names should be preserved
        column_names = [m.column_name for m in metadata_list]
        assert 'column with spaces' in column_names
        assert 'column-with-dashes' in column_names
        assert 'column_with_underscores' in column_names
        assert '123numeric_start' in column_names