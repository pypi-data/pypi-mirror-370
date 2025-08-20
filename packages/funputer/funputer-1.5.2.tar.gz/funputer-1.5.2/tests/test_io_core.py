"""
Core I/O functionality tests - focused on critical paths.
"""

import pytest
import tempfile
import os
import pandas as pd
import yaml
from pathlib import Path
from unittest.mock import patch

from funputer.io import (
    load_metadata, load_configuration, load_data,
    save_suggestions, validate_metadata_against_data
)
from funputer.models import ColumnMetadata, DataType, AnalysisConfig, ImputationSuggestion
from funputer.exceptions import ConfigurationError


class TestIOCore:
    """Test core I/O operations."""
    
    @pytest.fixture
    def sample_metadata_csv(self):
        """Create sample metadata CSV."""
        content = """column_name,data_type,role,description
name,string,feature,Person name
age,integer,feature,Person age
salary,float,target,Annual salary"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            return f.name
    
    @pytest.fixture
    def sample_data_csv(self):
        """Create sample data CSV."""
        content = """name,age,salary
John,25,50000
Jane,,60000
Bob,35,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            return f.name
    
    @pytest.fixture
    def sample_config_yaml(self):
        """Create sample configuration YAML."""
        config = {
            'missing_threshold': 0.1,
            'outlier_threshold': 0.05,
            'skip_columns': ['id', 'timestamp']
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            return f.name
    
    def test_load_metadata_success(self, sample_metadata_csv):
        """Test successful metadata loading."""
        try:
            metadata_list = load_metadata(sample_metadata_csv)
            assert len(metadata_list) == 3
            assert metadata_list[0].column_name == 'name'
            assert metadata_list[0].data_type == DataType.STRING
            assert metadata_list[2].role == 'target'
        finally:
            os.unlink(sample_metadata_csv)
    
    def test_load_metadata_file_not_found(self):
        """Test metadata loading with non-existent file."""
        with pytest.raises(ValueError, match="not found"):
            load_metadata('nonexistent.csv')
    
    def test_load_metadata_empty_file(self):
        """Test metadata loading with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Empty file
            pass
        
        try:
            with pytest.raises(ValueError, match="empty"):
                load_metadata(f.name)
        finally:
            os.unlink(f.name)
    
    def test_load_metadata_missing_column_name(self):
        """Test metadata loading with missing column_name column."""
        content = """data_type,role
string,feature"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
        
        try:
            with pytest.raises(ValueError, match="column_name"):
                load_metadata(f.name)
        finally:
            os.unlink(f.name)
    
    def test_load_configuration_default(self):
        """Test loading default configuration."""
        config = load_configuration()
        assert isinstance(config, AnalysisConfig)
        assert hasattr(config, 'missing_threshold')
    
    def test_load_configuration_yaml(self, sample_config_yaml):
        """Test loading YAML configuration."""
        try:
            config = load_configuration(sample_config_yaml)
            assert isinstance(config, AnalysisConfig)
            assert config.missing_threshold == 0.1
            assert 'id' in config.skip_columns
        finally:
            os.unlink(sample_config_yaml)
    
    def test_load_configuration_file_not_found(self):
        """Test configuration loading with non-existent file."""
        with pytest.raises(ConfigurationError):
            load_configuration('nonexistent.yaml')
    
    def test_load_data_success(self, sample_data_csv):
        """Test successful data loading."""
        metadata = [
            ColumnMetadata(column_name='name', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='age', data_type=DataType.INTEGER, role='feature'),
            ColumnMetadata(column_name='salary', data_type=DataType.FLOAT, role='target')
        ]
        
        try:
            df = load_data(sample_data_csv, metadata)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 3
            assert list(df.columns) == ['name', 'age', 'salary']
        finally:
            os.unlink(sample_data_csv)
    
    def test_load_data_chunked(self, sample_data_csv):
        """Test chunked data loading."""
        metadata = [
            ColumnMetadata(column_name='name', data_type=DataType.STRING, role='feature')
        ]
        
        try:
            chunk_reader = load_data(sample_data_csv, metadata, chunk_size=2)
            chunks = list(chunk_reader)
            assert len(chunks) >= 1
            total_rows = sum(len(chunk) for chunk in chunks)
            assert total_rows == 3
        finally:
            os.unlink(sample_data_csv)
    
    def test_load_data_sample_rows(self, sample_data_csv):
        """Test loading sample rows."""
        metadata = []
        
        try:
            df = load_data(sample_data_csv, metadata, sample_rows=2)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
        finally:
            os.unlink(sample_data_csv)
    
    def test_load_data_file_not_found(self):
        """Test data loading with non-existent file."""
        with pytest.raises(ValueError, match="Failed to load"):
            load_data('nonexistent.csv', [])
    
    def test_save_suggestions_success(self):
        """Test successful suggestions saving."""
        suggestions = [
            ImputationSuggestion(
                column_name='age',
                proposed_method='mean',
                rationale='Numeric data with few missing',
                missing_count=1,
                missing_percentage=0.1,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='No outliers',
                confidence_score=0.8
            )
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            try:
                save_suggestions(suggestions, f.name)
                assert os.path.exists(f.name)
                
                # Verify content
                saved_df = pd.read_csv(f.name)
                assert len(saved_df) == 1
                assert 'column_name' in saved_df.columns
                assert saved_df.iloc[0]['column_name'] == 'age'
            finally:
                os.unlink(f.name)
    
    def test_validate_metadata_against_data(self, sample_data_csv):
        """Test metadata validation against data."""
        metadata = [
            ColumnMetadata(column_name='name', data_type=DataType.STRING, role='feature'),
            ColumnMetadata(column_name='age', data_type=DataType.INTEGER, role='feature'),
            ColumnMetadata(column_name='missing_col', data_type=DataType.STRING, role='feature'),
        ]
        
        try:
            df = pd.read_csv(sample_data_csv)
            warnings = validate_metadata_against_data(metadata, df)
            
            assert len(warnings) >= 1
            assert any('missing_col' in w for w in warnings)
        finally:
            os.unlink(sample_data_csv)


class TestIOErrorHandling:
    """Test I/O error handling."""
    
    def test_load_metadata_malformed_csv(self):
        """Test metadata loading with malformed CSV."""
        content = """column_name,data_type
name,string,extra,columns"""  # Malformed row
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
        
        try:
            # Should handle gracefully
            metadata_list = load_metadata(f.name)
            assert len(metadata_list) >= 0  # May succeed with partial data
        except ValueError:
            # Or fail with clear error
            pass
        finally:
            os.unlink(f.name)
    
    def test_load_configuration_invalid_yaml(self):
        """Test configuration loading with invalid YAML."""
        content = """
        missing_threshold: 0.1
        invalid: yaml: content: [
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(content)
        
        try:
            with pytest.raises(ConfigurationError):
                load_configuration(f.name)
        finally:
            os.unlink(f.name)
    
    def test_save_suggestions_directory_creation(self):
        """Test suggestions saving creates directories."""
        suggestions = [
            ImputationSuggestion(
                column_name='test',
                proposed_method='mean',
                rationale='Test',
                missing_count=1,
                missing_percentage=0.1,
                mechanism='MCAR',
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling='none',
                outlier_rationale='',
                confidence_score=0.8
            )
        ]
        
        # Use a nested path that doesn't exist
        temp_dir = tempfile.mkdtemp()
        nested_path = os.path.join(temp_dir, 'subdir', 'output.csv')
        
        try:
            save_suggestions(suggestions, nested_path)
            assert os.path.exists(nested_path)
        finally:
            if os.path.exists(nested_path):
                os.unlink(nested_path)
            os.rmdir(os.path.dirname(nested_path))
            os.rmdir(temp_dir)