"""
Final tests to achieve 100% coverage on analyzer.py.
Targeting remaining 8 lines: 131-132, 135-136, 216-217, 309-310.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock

from funputer.analyzer import ImputationAnalyzer, analyze_imputation_requirements
from funputer.models import ColumnMetadata, AnalysisConfig


class TestAnalyzerFinalCoverage:
    """Final tests to reach 100% analyzer coverage."""
    
    def test_analyzer_with_missing_column_in_metadata(self, caplog):
        """Test analyzer with metadata referencing non-existent columns (lines 131-132)."""
        data = pd.DataFrame({
            'existing_col': [1, 2, np.nan, 4, 5]
        })
        
        metadata = [
            ColumnMetadata(column_name='existing_col', data_type='float', role='feature'),
            ColumnMetadata(column_name='nonexistent_col', data_type='string', role='feature')
        ]
        
        analyzer = ImputationAnalyzer()
        
        # This should trigger lines 131-132 (warning log for missing column)
        with caplog.at_level('WARNING'):
            result = analyzer.analyze_dataframe(data, metadata)
        
        # Should log warning about missing column
        assert any('not found in data' in record.message for record in caplog.records)
        
        # Should still return results for existing columns
        assert isinstance(result, list)
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'existing_col' in suggestions_by_column
        assert 'nonexistent_col' not in suggestions_by_column
    
    def test_analyzer_with_skip_columns_config(self, caplog):
        """Test analyzer with skip_columns configuration (lines 135-136)."""
        data = pd.DataFrame({
            'include_me': [1, 2, np.nan, 4, 5],
            'skip_me': [10, np.nan, 30, 40, 50]
        })
        
        metadata = [
            ColumnMetadata(column_name='include_me', data_type='float', role='feature'),
            ColumnMetadata(column_name='skip_me', data_type='float', role='feature')
        ]
        
        # Configure to skip a column
        config = AnalysisConfig(skip_columns=['skip_me'])
        analyzer = ImputationAnalyzer(config=config)
        
        # This should trigger lines 135-136 (info log for skipped column)
        with caplog.at_level('INFO'):
            result = analyzer.analyze_dataframe(data, metadata)
        
        # Should log info about skipped column
        assert any('Skipping column' in record.message for record in caplog.records)
        
        # Should only analyze non-skipped columns
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'include_me' in suggestions_by_column
        # skip_me should not be in results since it was skipped
        assert 'skip_me' not in suggestions_by_column
    
    def test_analyze_dataframe_with_metadata_dict(self):
        """Test analyze_dataframe with metadata as dict (lines 216-217)."""
        data = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5],
            'col2': ['A', 'B', np.nan, 'C', 'D']
        })
        
        # Pass metadata as dict instead of list
        metadata_dict = {
            'col1': ColumnMetadata(column_name='col1', data_type='float', role='feature'),
            'col2': ColumnMetadata(column_name='col2', data_type='categorical', role='feature')
        }
        
        analyzer = ImputationAnalyzer()
        
        # This should trigger lines 216-217 (dict to list conversion)
        result = analyzer.analyze_dataframe(data, metadata_dict)
        
        assert isinstance(result, list)
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'col1' in suggestions_by_column
        assert 'col2' in suggestions_by_column
    
    def test_analyze_imputation_requirements_file_read_error(self):
        """Test file read error handling (lines 309-310)."""
        # Create a temporary file path that will cause read error
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write invalid CSV content
            f.write("invalid,csv,content\nno proper structure here")
            f.flush()
            invalid_file = f.name
        
        try:
            # Mock pd.read_csv to raise an exception
            with patch('funputer.analyzer.pd.read_csv') as mock_read_csv:
                mock_read_csv.side_effect = Exception("Simulated read error")
                
                # This should trigger lines 309-310 (exception handling)
                with pytest.raises(FileNotFoundError) as exc_info:
                    analyze_imputation_requirements(data_path=invalid_file)
                
                # Should wrap the original exception in FileNotFoundError
                assert "Could not load data file" in str(exc_info.value)
                assert "Simulated read error" in str(exc_info.value)
        
        finally:
            os.unlink(invalid_file)
    
    def test_complete_coverage_verification(self):
        """Comprehensive test to verify all major paths work together."""
        # Create test data with various scenarios
        data = pd.DataFrame({
            'id': range(1, 11),
            'feature1': [1, 2, np.nan, 4, 5, 6, np.nan, 8, 9, 10],
            'feature2': ['A', 'B', 'C', np.nan, 'E', 'F', 'G', np.nan, 'I', 'J'],
            'target': [100, 200, 300, 400, np.nan, 600, 700, 800, 900, 1000]
        })
        
        # Test all major entry points
        analyzer = ImputationAnalyzer()
        
        # 1. Test analyze_dataframe with list
        metadata_list = [
            ColumnMetadata(column_name='id', data_type='integer', role='identifier'),
            ColumnMetadata(column_name='feature1', data_type='float', role='feature'),
            ColumnMetadata(column_name='feature2', data_type='categorical', role='feature'),
            ColumnMetadata(column_name='target', data_type='float', role='target')
        ]
        result1 = analyzer.analyze_dataframe(data, metadata_list)
        
        # 2. Test analyze_dataframe with dict
        metadata_dict = {meta.column_name: meta for meta in metadata_list}
        result2 = analyzer.analyze_dataframe(data, metadata_dict)
        
        # 3. Test analyze_dataframe with None (auto-inference)
        result3 = analyzer.analyze_dataframe(data, None)
        
        # All should return valid results
        for result in [result1, result2, result3]:
            assert isinstance(result, list)
            assert len(result) > 0
            suggestions_by_column = {s.column_name: s for s in result}
            assert 'feature1' in suggestions_by_column
            assert 'feature2' in suggestions_by_column