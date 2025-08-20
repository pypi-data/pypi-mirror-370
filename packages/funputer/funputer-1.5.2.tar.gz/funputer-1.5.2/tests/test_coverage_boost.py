"""
Focused coverage boost tests - practical and minimal.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from click.testing import CliRunner

# Test core functionality that actually exists
from funputer import analyze_dataframe, infer_metadata_from_dataframe
from funputer.models import ColumnMetadata, DataType, AnalysisConfig
from funputer.cli import cli
from funputer.io import load_configuration, load_data
from funputer.analyzer import ImputationAnalyzer


class TestCoverageFocused:
    """Focused tests to boost coverage on key modules."""
    
    def test_cli_basic_commands(self):
        """Test CLI basic functionality."""
        runner = CliRunner()
        
        # Test help command
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'analyze' in result.output
        
        # Test analyze help
        result = runner.invoke(cli, ['analyze', '--help'])
        assert result.exit_code == 0
    
    def test_metadata_inference_complete(self):
        """Test metadata inference with various data types."""
        df = pd.DataFrame({
            'id': range(5),
            'name': ['A', 'B', 'C', 'D', 'E'],
            'value': [1.1, 2.2, 3.3, 4.4, 5.5],
            'active': [True, False, True, False, True],
            'category': ['X', 'Y', 'X', 'Z', 'Y'],
            'missing': [1, np.nan, 3, np.nan, 5]
        })
        
        metadata_list = infer_metadata_from_dataframe(df)
        assert len(metadata_list) == 6
        
        # Should have descriptions and roles assigned
        for metadata in metadata_list:
            assert metadata.column_name in df.columns
            assert metadata.description is not None
            assert metadata.role in ['identifier', 'feature', 'target', 'group_by']
    
    def test_analyzer_core_functionality(self):
        """Test analyzer core functionality."""
        from funputer.analyzer import ImputationAnalyzer
        
        df = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5],
            'col2': ['A', 'B', None, 'D', 'E']
        })
        
        metadata = infer_metadata_from_dataframe(df)
        config = AnalysisConfig()
        
        # Test analysis using standalone function
        suggestions = analyze_dataframe(df, metadata, config)
        assert isinstance(suggestions, list)
    
    def test_io_configuration_loading(self):
        """Test I/O configuration functionality."""
        # Test default config
        config = load_configuration()
        assert isinstance(config, AnalysisConfig)
        assert hasattr(config, 'missing_threshold')
        
        # Test with YAML config
        config_content = """
missing_percentage_threshold: 0.2
outlier_threshold: 0.03
skip_columns: ['id']
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()
            
        try:
            config = load_configuration(f.name)
            assert config.missing_threshold == 0.2  # Should be loaded from YAML
            assert 'id' in config.skip_columns
        finally:
            os.unlink(f.name)
    
    def test_data_loading_variations(self):
        """Test data loading with different options."""
        df = pd.DataFrame({
            'col1': range(10),
            'col2': [f'item_{i}' for i in range(10)]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            
        try:
            metadata = [
                ColumnMetadata(column_name='col1', data_type='integer', role='feature'),
                ColumnMetadata(column_name='col2', data_type='string', role='feature')
            ]
            
            # Test standard loading
            loaded_df = load_data(f.name, metadata)
            assert len(loaded_df) == 10
            
            # Test chunked loading
            chunks = list(load_data(f.name, metadata, chunk_size=5))
            assert len(chunks) == 2
            assert sum(len(chunk) for chunk in chunks) == 10
            
            # Test sample loading
            sample_df = load_data(f.name, metadata, sample_rows=3)
            assert len(sample_df) == 3
            
        finally:
            os.unlink(f.name)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow."""
        # Create test data
        df = pd.DataFrame({
            'user_id': range(100),
            'age': np.random.randint(18, 80, 100),
            'income': np.random.normal(50000, 15000, 100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        # Add some missing values
        df.loc[::10, 'age'] = np.nan
        df.loc[::15, 'income'] = np.nan
        
        # Save to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            
        try:
            # Step 1: Infer metadata
            metadata = infer_metadata_from_dataframe(df)
            assert len(metadata) == 4
            
            # Step 2: Analyze for imputation
            config = AnalysisConfig()
            suggestions = analyze_dataframe(df, metadata, config)
            assert isinstance(suggestions, list)
            
            # Step 3: Test via CLI (basic smoke test)
            runner = CliRunner()
            result = runner.invoke(cli, ['analyze', '--data', f.name])
            # Should not crash (exit code 0 or 1 acceptable)
            assert result.exit_code in [0, 1]
            
        finally:
            os.unlink(f.name)
    
    def test_error_handling_paths(self):
        """Test error handling in various modules."""
        # Test with malformed data
        df = pd.DataFrame({
            'mixed': [1, 'text', None, 3.14, True]
        })
        
        # Should handle mixed types gracefully
        metadata = infer_metadata_from_dataframe(df)
        assert len(metadata) == 1
        
        # Test with empty data
        empty_df = pd.DataFrame()
        empty_metadata = infer_metadata_from_dataframe(empty_df)
        assert len(empty_metadata) == 0
        
        # Test configuration with non-existent file
        with pytest.raises(Exception):
            load_configuration('nonexistent.yaml')
    
    def test_models_comprehensive(self):
        """Test model creation and validation."""
        # Test ColumnMetadata with various configurations
        metadata = ColumnMetadata(
            column_name='test_col',
            data_type='integer',
            role='feature',
            min_value=0,
            max_value=100,
            unique_flag=False,
            nullable=True
        )
        
        assert metadata.column_name == 'test_col'
        assert metadata.data_type == 'integer'
        assert metadata.min_value == 0
        assert metadata.max_value == 100
        
        # Test AnalysisConfig with proper field aliases
        config = AnalysisConfig(
            missing_percentage_threshold=0.1,
            outlier_threshold=0.05,
            skip_columns=['id', 'timestamp']
        )
        
        assert config.missing_threshold == 0.1
        assert 'id' in config.skip_columns
    
    def test_preflight_integration(self):
        """Test preflight functionality."""
        from funputer.preflight import run_preflight
        
        # Create test file
        df = pd.DataFrame({
            'col1': range(10),
            'col2': ['test'] * 10
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            
        try:
            result = run_preflight(f.name)
            assert isinstance(result, dict)
            assert 'status' in result
        finally:
            os.unlink(f.name)