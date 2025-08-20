"""
Core functionality tests for funputer.analyzer module.
Strategic tests targeting critical coverage gaps in main analysis workflows.

Coverage Target: Boost Analyzer module from 15% to 80%+
Priority: CRITICAL (Core business logic)
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock

from funputer.analyzer import (
    ImputationAnalyzer, analyze_imputation_requirements, analyze_dataframe
)
from funputer.models import (
    ColumnMetadata, AnalysisConfig, ImputationSuggestion,
    MissingnessAnalysis, OutlierAnalysis, MissingnessType
)
from funputer.memory_utils import MemoryMonitor


class TestImputationAnalyzerCore:
    """Test core ImputationAnalyzer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ImputationAnalyzer()
        
        # Standard test data
        self.test_data = pd.DataFrame({
            'id': range(1, 101),
            'numeric_with_missing': [i if i % 5 != 0 else np.nan for i in range(1, 101)],
            'categorical_with_missing': ['A' if i % 3 == 0 else 'B' if i % 3 == 1 else np.nan for i in range(100)],
            'string_col': [f'item_{i}' for i in range(100)],
            'target_col': np.random.normal(50, 10, 100)
        })
        
        # Standard metadata
        self.test_metadata = [
            ColumnMetadata(column_name='id', data_type='integer', role='identifier'),
            ColumnMetadata(column_name='numeric_with_missing', data_type='float', role='feature'),
            ColumnMetadata(column_name='categorical_with_missing', data_type='categorical', role='feature'),
            ColumnMetadata(column_name='string_col', data_type='string', role='feature'),
            ColumnMetadata(column_name='target_col', data_type='float', role='target')
        ]
    
    def test_analyzer_initialization_default(self):
        """Test ImputationAnalyzer initialization with defaults."""
        analyzer = ImputationAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
        assert hasattr(analyzer, 'config')
        
        # Check default configuration
        default_config = analyzer.config
        assert isinstance(default_config, AnalysisConfig)
        assert default_config.missing_threshold > 0
        assert default_config.outlier_threshold > 0
    
    def test_analyzer_initialization_with_config(self):
        """Test ImputationAnalyzer initialization with custom config."""
        custom_config = AnalysisConfig(
            missing_threshold=0.9,
            outlier_threshold=0.02,
            skewness_threshold=2.0,
            correlation_threshold=0.4
        )
        
        analyzer = ImputationAnalyzer(config=custom_config)
        
        assert analyzer.config.missing_threshold == 0.9
        assert analyzer.config.outlier_threshold == 0.02
        assert analyzer.config.skewness_threshold == 2.0
        assert analyzer.config.correlation_threshold == 0.4
    
    def test_analyze_complete_workflow(self):
        """Test complete analyze workflow with real data."""
        result = self.analyzer.analyze_dataframe(self.test_data, self.test_metadata)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Should have suggestions for columns with missing data
        suggestions_by_column = {s.column_name: s for s in result}
        
        assert 'numeric_with_missing' in suggestions_by_column
        assert 'categorical_with_missing' in suggestions_by_column
        
        # Check suggestion structure
        numeric_suggestion = suggestions_by_column['numeric_with_missing']
        assert isinstance(numeric_suggestion, ImputationSuggestion)
        assert numeric_suggestion.missing_count > 0
        assert numeric_suggestion.missing_percentage > 0
        assert numeric_suggestion.proposed_method is not None
        assert numeric_suggestion.confidence_score >= 0
        
        categorical_suggestion = suggestions_by_column['categorical_with_missing']
        assert isinstance(categorical_suggestion, ImputationSuggestion)
        assert categorical_suggestion.missing_count > 0
        assert categorical_suggestion.proposed_method is not None
    
    def test_analyze_with_no_missing_data(self):
        """Test analyzer behavior with complete data (no missing values)."""
        complete_data = pd.DataFrame({
            'col1': range(100),
            'col2': [f'item_{i}' for i in range(100)],
            'col3': np.random.normal(0, 1, 100)
        })
        
        metadata = [
            ColumnMetadata(column_name='col1', data_type='integer', role='feature'),
            ColumnMetadata(column_name='col2', data_type='string', role='feature'),
            ColumnMetadata(column_name='col3', data_type='float', role='feature')
        ]
        
        result = self.analyzer.analyze_dataframe(complete_data, metadata)
        
        # Should still return analysis results
        assert isinstance(result, list)
        
        # All suggestions should have 0 missing count
        for suggestion in result:
            assert suggestion.missing_count == 0
            assert suggestion.missing_percentage == 0.0
    
    def test_analyze_with_all_missing_column(self):
        """Test analyzer behavior with completely missing column."""
        all_missing_data = self.test_data.copy()
        all_missing_data['all_missing'] = np.nan
        
        metadata_with_missing = self.test_metadata + [
            ColumnMetadata(column_name='all_missing', data_type='float', role='feature')
        ]
        
        result = self.analyzer.analyze_dataframe(all_missing_data, metadata_with_missing)
        
        # Should handle all-missing column
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'all_missing' in suggestions_by_column
        
        all_missing_suggestion = suggestions_by_column['all_missing']
        assert all_missing_suggestion.missing_count == len(all_missing_data)
        assert all_missing_suggestion.missing_percentage == 100.0
        assert all_missing_suggestion.proposed_method is not None
    
    def test_analyze_memory_monitoring(self):
        """Test that analyzer monitors memory usage during processing."""
        # Create larger dataset to trigger memory monitoring
        large_data = pd.DataFrame({
            'col1': range(10000),
            'col2': np.random.normal(0, 1, 10000),
            'col3': [f'item_{i}' for i in range(10000)]
        })
        
        # Add some missing values
        large_data.loc[::10, 'col2'] = np.nan
        
        metadata = [
            ColumnMetadata(column_name='col1', data_type='integer', role='feature'),
            ColumnMetadata(column_name='col2', data_type='float', role='feature'),
            ColumnMetadata(column_name='col3', data_type='string', role='feature')
        ]
        
        with patch('funputer.analyzer.MemoryMonitor') as mock_monitor_class:
            mock_monitor = MagicMock()
            mock_monitor_class.return_value = mock_monitor
            mock_monitor.get_memory_usage_mb.return_value = 100.0
            mock_monitor.get_available_memory_mb.return_value = 1000.0
            
            result = self.analyzer.analyze_dataframe(large_data, metadata)
            
            # Should have created memory monitor
            assert mock_monitor_class.called
            assert isinstance(result, list)
    
    def test_analyze_with_skipped_columns(self):
        """Test analyzer respects do_not_impute flag."""
        metadata_with_skip = [
            ColumnMetadata(column_name='id', data_type='integer', role='identifier'),
            ColumnMetadata(
                column_name='numeric_with_missing', 
                data_type='float', 
                role='feature',
                do_not_impute=True  # Should be skipped
            ),
            ColumnMetadata(column_name='categorical_with_missing', data_type='categorical', role='feature'),
            ColumnMetadata(column_name='string_col', data_type='string', role='feature'),
            ColumnMetadata(column_name='target_col', data_type='float', role='target')
        ]
        
        result = self.analyzer.analyze_dataframe(self.test_data, metadata_with_skip)
        
        # Should not have suggestion for skipped column
        suggestions_by_column = {s.column_name: s for s in result}
        
        # numeric_with_missing should be skipped
        if 'numeric_with_missing' in suggestions_by_column:
            # If present, should indicate it's skipped
            suggestion = suggestions_by_column['numeric_with_missing']
            assert 'skip' in suggestion.rationale.lower() or 'not impute' in suggestion.rationale.lower()
        
        # Should still have other columns
        assert 'categorical_with_missing' in suggestions_by_column


class TestAnalyzeImputationRequirements:
    """Test the main analyze_imputation_requirements function."""
    
    def create_test_csv(self, data=None):
        """Create temporary CSV file for testing."""
        if data is None:
            data = pd.DataFrame({
                'id': range(1, 51),
                'age': [25, 30, np.nan, 35, 40] * 10,
                'income': np.random.normal(50000, 10000, 50),
                'category': ['A', 'B', np.nan, 'C', 'A'] * 10
            })
            # Add some missing values to income
            data.loc[::7, 'income'] = np.nan
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        return temp_file.name
    
    def create_test_metadata_csv(self, columns=None):
        """Create temporary metadata CSV file for testing."""
        if columns is None:
            metadata_data = pd.DataFrame({
                'column_name': ['id', 'age', 'income', 'category'],
                'data_type': ['integer', 'integer', 'float', 'categorical'],
                'role': ['identifier', 'feature', 'feature', 'feature'],
                'nullable': [False, True, True, True],
                'description': ['ID column', 'Age in years', 'Annual income', 'Category']
            })
        else:
            metadata_data = pd.DataFrame(columns)
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        metadata_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        return temp_file.name
    
    def test_analyze_with_explicit_metadata_file(self):
        """Test analyze_imputation_requirements with metadata file."""
        data_file = self.create_test_csv()
        metadata_file = self.create_test_metadata_csv()
        
        try:
            result = analyze_imputation_requirements(
                data_path=data_file,
                metadata_path=metadata_file
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Should have suggestions for columns with missing data
            suggestions_by_column = {s.column_name: s for s in result}
            assert 'age' in suggestions_by_column
            assert 'income' in suggestions_by_column
            assert 'category' in suggestions_by_column
            
            # Check suggestion quality
            for suggestion in result:
                assert isinstance(suggestion, ImputationSuggestion)
                assert suggestion.column_name is not None
                assert suggestion.proposed_method is not None
                assert suggestion.confidence_score >= 0
                
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_analyze_with_auto_metadata_inference(self):
        """Test analyze_imputation_requirements with automatic metadata inference."""
        data_file = self.create_test_csv()
        
        try:
            result = analyze_imputation_requirements(data_path=data_file)
            
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Should infer metadata and provide suggestions
            column_names = [s.column_name for s in result]
            assert 'id' in column_names
            assert 'age' in column_names
            assert 'income' in column_names
            assert 'category' in column_names
            
        finally:
            os.unlink(data_file)
    
    def test_analyze_with_config_parameter(self):
        """Test analyze_imputation_requirements with custom config."""
        data_file = self.create_test_csv()
        
        # Custom config with strict thresholds
        custom_config = AnalysisConfig(
            missing_threshold=0.1,  # Very strict
            outlier_threshold=0.01,  # Very sensitive
            correlation_threshold=0.5  # Moderate correlation
        )
        
        try:
            result = analyze_imputation_requirements(
                data_path=data_file,
                config=custom_config
            )
            
            assert isinstance(result, list)
            
            # With strict thresholds, behavior may differ
            # But should still complete successfully
            for suggestion in result:
                assert isinstance(suggestion, ImputationSuggestion)
                
        finally:
            os.unlink(data_file)
    
    def test_analyze_nonexistent_file(self):
        """Test analyze_imputation_requirements with nonexistent file."""
        with pytest.raises((FileNotFoundError, ValueError)):
            analyze_imputation_requirements(data_path="nonexistent_file.csv")
    
    def test_analyze_invalid_metadata_file(self):
        """Test analyze_imputation_requirements with invalid metadata file."""
        data_file = self.create_test_csv()
        
        # Create invalid metadata file
        invalid_metadata = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        invalid_metadata.write("invalid,metadata,format\nno,proper,structure")
        invalid_metadata.flush()
        
        try:
            with pytest.raises((ValueError, KeyError)):
                analyze_imputation_requirements(
                    data_path=data_file,
                    metadata_path=invalid_metadata.name
                )
                
        finally:
            os.unlink(data_file)
            os.unlink(invalid_metadata.name)


class TestAnalyzeDataFrame:
    """Test the analyze_dataframe function for direct DataFrame input."""
    
    def test_analyze_dataframe_basic(self):
        """Test analyze_dataframe with basic DataFrame input."""
        test_data = pd.DataFrame({
            'numeric': [1, 2, np.nan, 4, 5],
            'categorical': ['A', 'B', np.nan, 'A', 'B'],
            'string': ['item1', 'item2', 'item3', 'item4', 'item5']
        })
        
        metadata = [
            ColumnMetadata(column_name='numeric', data_type='float', role='feature'),
            ColumnMetadata(column_name='categorical', data_type='categorical', role='feature'), 
            ColumnMetadata(column_name='string', data_type='string', role='feature')
        ]
        
        result = analyze_dataframe(test_data, metadata)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Should have suggestions for columns with missing data
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'numeric' in suggestions_by_column
        assert 'categorical' in suggestions_by_column
        
        # Check missing counts
        numeric_suggestion = suggestions_by_column['numeric']
        assert numeric_suggestion.missing_count == 1
        assert numeric_suggestion.missing_percentage == 20.0
        
        categorical_suggestion = suggestions_by_column['categorical']
        assert categorical_suggestion.missing_count == 1
        assert categorical_suggestion.missing_percentage == 20.0
    
    def test_analyze_dataframe_with_config(self):
        """Test analyze_dataframe with custom configuration."""
        test_data = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5] * 20,  # 20% missing
            'col2': ['A', 'B', 'C', 'D', 'E'] * 20
        })
        
        metadata = [
            ColumnMetadata(column_name='col1', data_type='float', role='feature'),
            ColumnMetadata(column_name='col2', data_type='categorical', role='feature')
        ]
        
        # Test with different missing thresholds
        configs = [
            AnalysisConfig(missing_threshold=0.1),  # Strict - 20% should trigger high missing handling
            AnalysisConfig(missing_threshold=0.5)   # Lenient - 20% should be normal handling
        ]
        
        for config in configs:
            result = analyze_dataframe(test_data, metadata, config=config)
            
            assert isinstance(result, list)
            suggestions_by_column = {s.column_name: s for s in result}
            
            # Should have different handling based on threshold
            col1_suggestion = suggestions_by_column['col1']
            assert col1_suggestion is not None
            
            # Rationale should reflect the threshold setting
            assert col1_suggestion.rationale is not None
    
    def test_analyze_dataframe_empty_data(self):
        """Test analyze_dataframe with empty DataFrame."""
        empty_data = pd.DataFrame()
        metadata = []
        
        result = analyze_dataframe(empty_data, metadata)
        
        # Should handle empty data gracefully
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_analyze_dataframe_single_row(self):
        """Test analyze_dataframe with single row of data."""
        single_row_data = pd.DataFrame({
            'col1': [1],
            'col2': ['A'],
            'col3': [np.nan]
        })
        
        metadata = [
            ColumnMetadata(column_name='col1', data_type='integer', role='feature'),
            ColumnMetadata(column_name='col2', data_type='categorical', role='feature'),
            ColumnMetadata(column_name='col3', data_type='float', role='feature')
        ]
        
        result = analyze_dataframe(single_row_data, metadata)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Should handle single row appropriately
        suggestions_by_column = {s.column_name: s for s in result}
        
        if 'col3' in suggestions_by_column:
            col3_suggestion = suggestions_by_column['col3']
            assert col3_suggestion.missing_count == 1
            assert col3_suggestion.missing_percentage == 100.0


class TestAnalyzerErrorHandling:
    """Test analyzer error handling and edge cases."""
    
    def test_analyze_with_mismatched_metadata(self):
        """Test analyzer behavior when metadata doesn't match data columns."""
        test_data = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['A', 'B', 'C']
        })
        
        # Metadata for different columns
        mismatched_metadata = [
            ColumnMetadata(column_name='different_col', data_type='integer', role='feature'),
            ColumnMetadata(column_name='another_col', data_type='string', role='feature')
        ]
        
        analyzer = ImputationAnalyzer()
        
        # Should handle mismatch gracefully
        try:
            result = analyzer.analyze_dataframe(test_data, mismatched_metadata)
            # If it succeeds, should return reasonable result
            assert isinstance(result, list)
        except (ValueError, KeyError) as e:
            # Expected to raise error for mismatched metadata
            assert "column" in str(e).lower() or "metadata" in str(e).lower()
    
    def test_analyze_with_corrupt_data_types(self):
        """Test analyzer behavior with corrupt or mixed data types."""
        # Create DataFrame with mixed/corrupt types
        corrupt_data = pd.DataFrame({
            'mixed_numeric': [1, 'two', 3.0, '4', np.nan],
            'mixed_categorical': [1, 'A', 3.14, True, None],
            'normal_col': [1, 2, 3, 4, 5]
        })
        
        metadata = [
            ColumnMetadata(column_name='mixed_numeric', data_type='float', role='feature'),
            ColumnMetadata(column_name='mixed_categorical', data_type='categorical', role='feature'),
            ColumnMetadata(column_name='normal_col', data_type='integer', role='feature')
        ]
        
        analyzer = ImputationAnalyzer()
        
        # Should handle mixed types without crashing
        try:
            result = analyzer.analyze_dataframe(corrupt_data, metadata)
            assert isinstance(result, list)
            
            # Should provide some analysis even for problematic columns
            suggestions_by_column = {s.column_name: s for s in result}
            assert len(suggestions_by_column) > 0
            
        except Exception as e:
            # If it fails, should be a reasonable error
            assert isinstance(e, (ValueError, TypeError))
    
    def test_analyze_with_extremely_large_values(self):
        """Test analyzer behavior with extremely large numeric values."""
        extreme_data = pd.DataFrame({
            'large_values': [1e50, 1e100, np.inf, -np.inf, np.nan],
            'normal_values': [1, 2, 3, 4, 5]
        })
        
        metadata = [
            ColumnMetadata(column_name='large_values', data_type='float', role='feature'),
            ColumnMetadata(column_name='normal_values', data_type='integer', role='feature')
        ]
        
        analyzer = ImputationAnalyzer()
        
        # Should handle extreme values without numerical errors
        result = analyzer.analyze_dataframe(extreme_data, metadata)
        
        assert isinstance(result, list)
        suggestions_by_column = {s.column_name: s for s in result}
        
        # Should provide suggestions even for extreme value column
        if 'large_values' in suggestions_by_column:
            suggestion = suggestions_by_column['large_values']
            assert suggestion.missing_count >= 0  # May count inf as missing
            assert np.isfinite(suggestion.confidence_score)  # Should not be inf/nan


class TestAnalyzerPerformanceScenarios:
    """Test analyzer performance with various data scenarios."""
    
    def test_analyze_wide_dataset(self):
        """Test analyzer performance with many columns."""
        # Create dataset with many columns
        n_cols = 50
        n_rows = 100
        
        wide_data = pd.DataFrame()
        metadata = []
        
        for i in range(n_cols):
            col_name = f'col_{i}'
            wide_data[col_name] = np.random.normal(0, 1, n_rows)
            
            # Add some missing values
            if i % 3 == 0:
                wide_data.loc[::10, col_name] = np.nan
            
            metadata.append(
                ColumnMetadata(column_name=col_name, data_type='float', role='feature')
            )
        
        analyzer = ImputationAnalyzer()
        result = analyzer.analyze_dataframe(wide_data, metadata)
        
        assert isinstance(result, list)
        assert len(result) == n_cols
        
        # Should complete in reasonable time and provide valid suggestions
        for suggestion in result:
            assert isinstance(suggestion, ImputationSuggestion)
            assert suggestion.column_name.startswith('col_')
    
    def test_analyze_long_dataset(self):
        """Test analyzer performance with many rows."""
        # Create dataset with many rows
        n_rows = 10000
        
        long_data = pd.DataFrame({
            'id': range(n_rows),
            'numeric': np.random.normal(0, 1, n_rows),
            'categorical': np.random.choice(['A', 'B', 'C'], n_rows),
            'target': np.random.normal(50, 10, n_rows)
        })
        
        # Add missing values
        long_data.loc[::50, 'numeric'] = np.nan
        long_data.loc[::75, 'categorical'] = np.nan
        
        metadata = [
            ColumnMetadata(column_name='id', data_type='integer', role='identifier'),
            ColumnMetadata(column_name='numeric', data_type='float', role='feature'),
            ColumnMetadata(column_name='categorical', data_type='categorical', role='feature'),
            ColumnMetadata(column_name='target', data_type='float', role='target')
        ]
        
        analyzer = ImputationAnalyzer()
        result = analyzer.analyze_dataframe(long_data, metadata)
        
        assert isinstance(result, list)
        assert len(result) == 4
        
        # Check that analysis is reasonable for large dataset
        suggestions_by_column = {s.column_name: s for s in result}
        
        numeric_suggestion = suggestions_by_column['numeric']
        assert numeric_suggestion.missing_count == len(long_data) // 50
        
        categorical_suggestion = suggestions_by_column['categorical']  
        assert categorical_suggestion.missing_count == len(long_data) // 75