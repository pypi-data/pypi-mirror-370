"""
Focused metadata inference tests using only public API.
"""

import pytest
import pandas as pd
import numpy as np

from funputer.metadata_inference import infer_metadata_from_dataframe
from funputer.models import DataType


class TestMetadataInferenceFocused:
    """Test metadata inference with focused, practical scenarios."""
    
    def test_infer_basic_types(self):
        """Test inference of basic data types."""
        df = pd.DataFrame({
            'integer_col': [1, 2, 3, 4, 5],
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'string_col': ['A', 'B', 'C', 'D', 'E'],
            'boolean_col': [True, False, True, False, True]
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        assert len(metadata_list) == 4
        
        # Convert to dict for easier testing
        metadata_dict = {m.column_name: m for m in metadata_list}
        
        assert metadata_dict['integer_col'].data_type == DataType.INTEGER
        assert metadata_dict['float_col'].data_type == DataType.FLOAT
        assert metadata_dict['string_col'].data_type == DataType.STRING
        assert metadata_dict['boolean_col'].data_type == DataType.BOOLEAN
    
    def test_infer_with_missing_values(self):
        """Test inference with missing values."""
        df = pd.DataFrame({
            'int_with_nan': [1, 2, np.nan, 4, 5],
            'str_with_none': ['A', 'B', None, 'D', 'E'],
            'float_with_nan': [1.1, np.nan, 3.3, np.nan, 5.5]
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        assert len(metadata_list) == 3
        
        # All should be inferred as nullable
        for metadata in metadata_list:
            assert metadata.nullable == True
    
    def test_infer_categorical(self):
        """Test categorical inference."""
        df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B'] * 10,  # Repeated values
            'non_category': [f'unique_{i}' for i in range(80)]  # All unique
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        metadata_dict = {m.column_name: m for m in metadata_list}
        
        # Category with repeated values should be categorical
        assert metadata_dict['category'].data_type == DataType.CATEGORICAL
        
        # Unique strings should stay string
        assert metadata_dict['non_category'].data_type == DataType.STRING
    
    def test_infer_roles(self):
        """Test role inference."""
        df = pd.DataFrame({
            'id': range(100),  # Unique integers - should be identifier
            'user_id': [f'user_{i}' for i in range(100)],  # Unique strings - should be identifier
            'category': np.random.choice(['A', 'B', 'C'], 100),  # Should be feature
            'target_value': np.random.normal(100, 15, 100)  # Could be target
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        metadata_dict = {m.column_name: m for m in metadata_list}
        
        # ID columns should be identifiers
        assert metadata_dict['id'].role == 'identifier'
        assert metadata_dict['user_id'].role == 'identifier'
        
        # Category should be feature
        assert metadata_dict['category'].role == 'feature'
    
    def test_empty_dataframe(self):
        """Test with empty dataframe."""
        df = pd.DataFrame()
        metadata_list = infer_metadata_from_dataframe(df)
        assert len(metadata_list) == 0
    
    def test_single_row(self):
        """Test with single row dataframe."""
        df = pd.DataFrame({
            'col1': [1],
            'col2': ['text'],
            'col3': [True]
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        assert len(metadata_list) == 3
        
        metadata_dict = {m.column_name: m for m in metadata_list}
        assert metadata_dict['col1'].data_type == DataType.INTEGER
        assert metadata_dict['col2'].data_type == DataType.STRING
        assert metadata_dict['col3'].data_type == DataType.BOOLEAN
    
    def test_all_null_column(self):
        """Test column with all null values."""
        df = pd.DataFrame({
            'normal_col': [1, 2, 3],
            'all_null': [None, None, None]
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        metadata_dict = {m.column_name: m for m in metadata_list}
        
        assert metadata_dict['normal_col'].data_type == DataType.INTEGER
        assert metadata_dict['all_null'].nullable == True
        # All null should default to string
        assert metadata_dict['all_null'].data_type == DataType.STRING
    
    def test_large_dataframe_performance(self):
        """Test performance with larger dataframe."""
        size = 10000
        df = pd.DataFrame({
            'id': range(size),
            'category': np.random.choice(['A', 'B', 'C', 'D'], size),
            'value': np.random.normal(100, 15, size),
            'flag': np.random.choice([True, False], size),
            'text': [f'item_{i}' for i in range(size)]
        })
        
        # Should complete quickly
        import time
        start = time.time()
        metadata_list = infer_metadata_from_dataframe(df)
        duration = time.time() - start
        
        assert len(metadata_list) == 5
        assert duration < 5.0  # Should complete within 5 seconds
        
        # Check types are reasonable
        metadata_dict = {m.column_name: m for m in metadata_list}
        assert metadata_dict['id'].data_type == DataType.INTEGER
        assert metadata_dict['category'].data_type == DataType.CATEGORICAL
        assert metadata_dict['value'].data_type == DataType.FLOAT
        assert metadata_dict['flag'].data_type == DataType.BOOLEAN
        assert metadata_dict['text'].data_type == DataType.STRING
    
    def test_edge_case_numeric_strings(self):
        """Test with numeric strings."""
        df = pd.DataFrame({
            'numeric_strings': ['123', '456', '789', '012'],
            'mixed_strings': ['123', 'abc', '456', 'def']
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        metadata_dict = {m.column_name: m for m in metadata_list}
        
        # Both should be strings since they contain text representations
        assert metadata_dict['numeric_strings'].data_type == DataType.STRING
        assert metadata_dict['mixed_strings'].data_type == DataType.STRING
    
    def test_mixed_types_column(self):
        """Test column with truly mixed types."""
        df = pd.DataFrame({
            'mixed': [1, 'text', 3.14, True, None]
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        metadata_dict = {m.column_name: m for m in metadata_list}
        
        # Mixed types should default to string
        assert metadata_dict['mixed'].data_type == DataType.STRING
        assert metadata_dict['mixed'].nullable == True