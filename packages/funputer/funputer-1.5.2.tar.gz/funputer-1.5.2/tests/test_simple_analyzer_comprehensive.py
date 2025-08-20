"""
Comprehensive tests for funputer.simple_analyzer module targeting 85% coverage.

Tests cover the core functionality that's currently missing coverage:
- Streaming analysis functionality
- Memory monitoring integration
- Security integration
- Error handling and edge cases
- Internal helper methods
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from typing import List, Dict

from funputer.analyzer import (
    ImputationAnalyzer,
    analyze_imputation_requirements,
    analyze_dataframe,
    _analyze_missingness_mechanism
)
from funputer.models import (
    ColumnMetadata, AnalysisConfig, ImputationSuggestion, 
    MissingnessAnalysis, MissingnessType, OutlierAnalysis, OutlierHandling
)


class TestImputationAnalyzerCore:
    """Test core functionality of ImputationAnalyzer."""
    
    def test_analyzer_initialization_with_security(self):
        """Test analyzer initialization with security enabled."""
        analyzer = ImputationAnalyzer(enable_security=True)
        
        assert analyzer.enable_security is True
        assert hasattr(analyzer, '_memory_monitor')
        assert hasattr(analyzer, '_security_logger')
    
    def test_analyzer_initialization_without_security(self):
        """Test analyzer initialization with security disabled."""
        analyzer = ImputationAnalyzer(enable_security=False)
        
        assert analyzer.enable_security is False
        assert hasattr(analyzer, '_memory_monitor')
        assert not hasattr(analyzer, '_security_logger')
    
    def test_load_metadata_auto_format(self, tmp_path):
        """Test automatic metadata format loading."""
        # Create test metadata CSV
        metadata_csv = tmp_path / "metadata.csv"
        metadata_content = """column_name,data_type,description
age,numeric,Age in years
name,string,Person name"""
        
        metadata_csv.write_text(metadata_content)
        
        analyzer = ImputationAnalyzer()
        metadata = analyzer._load_metadata_auto_format(str(metadata_csv))
        
        assert len(metadata) == 2
        assert metadata[0].column_name == "age"
        assert metadata[1].column_name == "name"
    
    def test_analyze_streaming_mode_detection(self, tmp_path):
        """Test automatic streaming mode detection."""
        # Create test files
        metadata_csv = tmp_path / "metadata.csv"
        metadata_content = """column_name,data_type,description
value1,numeric,Test value 1
value2,numeric,Test value 2"""
        metadata_csv.write_text(metadata_content)
        
        data_csv = tmp_path / "data.csv"
        data_content = "value1,value2\n" + "\n".join([f"{i},{i*2}" for i in range(100)])
        data_csv.write_text(data_content)
        
        analyzer = ImputationAnalyzer()
        
        with patch.object(analyzer._memory_monitor, 'should_use_chunking') as mock_chunking:
            mock_chunking.return_value = (True, 50)  # Should use streaming with chunk size 50
            
            suggestions = analyzer.analyze(str(metadata_csv), str(data_csv))
            
            assert len(suggestions) == 2
            mock_chunking.assert_called_once()
    
    def test_analyze_standard_mode(self, tmp_path):
        """Test standard in-memory analysis mode."""
        # Create small test files
        metadata_csv = tmp_path / "metadata.csv"
        metadata_content = """column_name,data_type,description
value,numeric,Test value"""
        metadata_csv.write_text(metadata_content)
        
        data_csv = tmp_path / "data.csv"
        data_content = """value
10
20
"""
        data_csv.write_text(data_content)
        
        analyzer = ImputationAnalyzer()
        
        with patch.object(analyzer._memory_monitor, 'should_use_chunking') as mock_chunking:
            mock_chunking.return_value = (False, None)  # Don't use streaming
            
            suggestions = analyzer.analyze(str(metadata_csv), str(data_csv))
            
            assert len(suggestions) == 1
            assert suggestions[0].column_name == "value"
    
    def test_streaming_analysis_process_chunk(self):
        """Test streaming analysis chunk processing."""
        analyzer = ImputationAnalyzer()
        
        # Create test chunk
        chunk = pd.DataFrame({
            'age': [25, 30, 35, None, 40],
            'score': [80, 90, None, 85, 95]
        })
        
        # Initialize column stats
        metadata_dict = {
            'age': ColumnMetadata(column_name='age', data_type='numeric'),
            'score': ColumnMetadata(column_name='score', data_type='numeric')
        }
        
        column_stats = {
            'age': {'total_count': 0, 'missing_count': 0, 'outlier_count': 0, 'sample_values': [], 'metadata': metadata_dict['age']},
            'score': {'total_count': 0, 'missing_count': 0, 'outlier_count': 0, 'sample_values': [], 'metadata': metadata_dict['score']}
        }
        
        # Process chunk
        analyzer._process_chunk(chunk, column_stats, metadata_dict)
        
        # Verify stats updated
        assert column_stats['age']['total_count'] == 5
        assert column_stats['age']['missing_count'] == 1
        assert column_stats['score']['total_count'] == 5
        assert column_stats['score']['missing_count'] == 1
        assert len(column_stats['age']['sample_values']) > 0
    
    def test_generate_suggestions_from_stats(self):
        """Test suggestion generation from accumulated statistics."""
        analyzer = ImputationAnalyzer()
        
        # Create mock column stats
        column_stats = {
            'age': {
                'total_count': 100,
                'missing_count': 10,
                'outlier_count': 5,
                'sample_values': [25, 30, 35, 40, 45, 50],
                'metadata': ColumnMetadata(column_name='age', data_type='numeric')
            }
        }
        
        suggestions = analyzer._generate_suggestions_from_stats(column_stats)
        
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.column_name == 'age'
        assert suggestion.missing_count == 10
        assert suggestion.missing_percentage == 0.1
        assert suggestion.outlier_count == 5
        assert suggestion.confidence_score <= 0.9  # Streaming has lower confidence
    
    def test_analyze_dataframe_parallel_processing_recommendation(self):
        """Test parallel processing recommendation logic."""
        analyzer = ImputationAnalyzer()
        
        # Create large-ish DataFrame
        data = pd.DataFrame({
            f'col_{i}': range(100) for i in range(10)  # 10 columns, 100 rows
        })
        
        metadata = [ColumnMetadata(column_name=f'col_{i}', data_type='numeric') for i in range(10)]
        
        with patch('funputer.parallel_processor.get_parallel_processing_recommendation') as mock_rec:
            mock_rec.return_value = {'use_parallel': True, 'max_workers': 4}
            
            with patch('funputer.parallel_processor.ParallelColumnAnalyzer') as mock_parallel:
                mock_parallel_instance = MagicMock()
                mock_parallel_instance.analyze_columns_parallel.return_value = []
                mock_parallel.return_value = mock_parallel_instance
                
                suggestions = analyzer.analyze_dataframe(data, metadata, use_parallel=True, max_workers=4)
                
                mock_parallel.assert_called_once()
                mock_parallel_instance.analyze_columns_parallel.assert_called_once()
    
    def test_analyze_dataframe_parallel_fallback_to_sequential(self):
        """Test parallel processing fallback to sequential on error."""
        analyzer = ImputationAnalyzer()
        
        data = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        metadata = [ColumnMetadata(column_name='value', data_type='numeric')]
        
        with patch('funputer.parallel_processor.ParallelColumnAnalyzer') as mock_parallel:
            mock_parallel.side_effect = Exception("Parallel processing failed")
            
            # Should fallback to sequential without raising
            suggestions = analyzer.analyze_dataframe(data, metadata, use_parallel=True)
            
            assert len(suggestions) == 1
            assert suggestions[0].column_name == 'value'
    
    def test_analyze_dataframe_with_metadata_auto_inference(self):
        """Test DataFrame analysis with automatic metadata inference."""
        analyzer = ImputationAnalyzer()
        
        data = pd.DataFrame({
            'age': [25, 30, 35],
            'name': ['John', 'Jane', 'Bob'],
            'active': [True, False, True]
        })
        
        with patch('funputer.metadata_inference.infer_metadata_from_dataframe') as mock_infer:
            mock_metadata = [
                ColumnMetadata(column_name='age', data_type='numeric'),
                ColumnMetadata(column_name='name', data_type='string'),
                ColumnMetadata(column_name='active', data_type='boolean')
            ]
            mock_infer.return_value = mock_metadata
            
            suggestions = analyzer.analyze_dataframe(data, metadata=None)
            
            mock_infer.assert_called_once_with(data, warn_user=False)
            assert len(suggestions) == 3
    
    def test_analyze_dataset_cli_method(self, tmp_path):
        """Test CLI-oriented analysis method."""
        # Create test files
        metadata_csv = tmp_path / "metadata.csv"
        metadata_content = """column_name,data_type,description
value,numeric,Test value"""
        metadata_csv.write_text(metadata_content)
        
        data_csv = tmp_path / "data.csv"
        data_content = """value
10
20
"""
        data_csv.write_text(data_content)
        
        analyzer = ImputationAnalyzer()
        result = analyzer.analyze_dataset_cli(str(metadata_csv), str(data_csv))
        
        assert 'suggestions' in result
        assert 'summary' in result
        assert result['summary']['total_columns'] == 1
        assert 'average_confidence' in result['summary']
    
    def test_save_results_method(self, tmp_path):
        """Test save results functionality."""
        output_path = tmp_path / "output.csv"
        config = AnalysisConfig(output_path=str(output_path))
        analyzer = ImputationAnalyzer(config)
        
        suggestions = [
            ImputationSuggestion(
                column_name="test",
                missing_count=5,
                missing_percentage=0.1,
                mechanism="MCAR",
                proposed_method="mean",
                rationale="Test",
                outlier_count=0,
                outlier_percentage=0.0,
                outlier_handling="leave_as_is",
                outlier_rationale="No outliers",
                confidence_score=0.8
            )
        ]
        
        with patch('funputer.io.save_suggestions') as mock_save:
            analyzer.save_results(suggestions)
            mock_save.assert_called_once_with(suggestions, str(output_path))


class TestMissingnessAnalysis:
    """Test missingness mechanism analysis functionality."""
    
    def test_analyze_missingness_mechanism_no_missing(self):
        """Test missingness analysis with no missing values."""
        data = pd.DataFrame({'col': [1, 2, 3, 4, 5]})
        metadata_dict = {'col': ColumnMetadata(column_name='col', data_type='numeric')}
        config = AnalysisConfig()
        
        result = _analyze_missingness_mechanism('col', data, metadata_dict, config)
        
        assert result.missing_count == 0
        assert result.missing_percentage == 0.0
        assert result.mechanism == MissingnessType.MCAR
        assert "No missing values detected" in result.rationale
    
    def test_analyze_missingness_mechanism_with_dependency(self):
        """Test missingness analysis with dependent column specified."""
        data = pd.DataFrame({
            'target': [1, None, 3, None, 5],
            'dependent': ['A', 'B', 'A', 'B', 'A']
        })
        
        metadata_dict = {
            'target': ColumnMetadata(column_name='target', data_type='numeric', dependent_column='dependent'),
            'dependent': ColumnMetadata(column_name='dependent', data_type='string')
        }
        config = AnalysisConfig()
        
        result = _analyze_missingness_mechanism('target', data, metadata_dict, config)
        
        assert result.missing_count == 2
        assert result.missing_percentage == 0.4
        assert result.mechanism == MissingnessType.MAR
        assert 'dependent' in result.related_columns
        assert "Metadata indicates dependency" in result.rationale
    
    def test_analyze_missingness_mechanism_default_mcar(self):
        """Test missingness analysis defaults to MCAR."""
        data = pd.DataFrame({'col': [1, None, 3, None, 5]})
        metadata_dict = {'col': ColumnMetadata(column_name='col', data_type='numeric')}
        config = AnalysisConfig()
        
        result = _analyze_missingness_mechanism('col', data, metadata_dict, config)
        
        assert result.missing_count == 2
        assert result.missing_percentage == 0.4
        assert result.mechanism == MissingnessType.MCAR
        assert "Simplified analysis defaults to MCAR" in result.rationale
    
    def test_analyze_missingness_mechanism_dependent_column_missing(self):
        """Test missingness analysis when dependent column doesn't exist."""
        data = pd.DataFrame({'col': [1, None, 3, None, 5]})
        metadata_dict = {
            'col': ColumnMetadata(column_name='col', data_type='numeric', dependent_column='nonexistent')
        }
        config = AnalysisConfig()
        
        result = _analyze_missingness_mechanism('col', data, metadata_dict, config)
        
        # Should default to MCAR when dependent column doesn't exist
        assert result.mechanism == MissingnessType.MCAR
        assert "defaults to MCAR" in result.rationale


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_analyze_imputation_requirements_with_dataframe_input(self):
        """Test convenience function with DataFrame input."""
        data = pd.DataFrame({
            'age': [25, None, 35],
            'name': ['John', 'Jane', None]
        })
        
        with patch('funputer.metadata_inference.infer_metadata_from_dataframe') as mock_infer:
            mock_metadata = [
                ColumnMetadata(column_name='age', data_type='numeric'),
                ColumnMetadata(column_name='name', data_type='string')
            ]
            mock_infer.return_value = mock_metadata
            
            suggestions = analyze_imputation_requirements(data)
            
            mock_infer.assert_called_once_with(data, warn_user=True)
            assert len(suggestions) == 2
    
    def test_analyze_imputation_requirements_file_loading_error(self):
        """Test convenience function with file loading error."""
        with pytest.raises(FileNotFoundError, match="Could not load data file"):
            analyze_imputation_requirements("/nonexistent/file.csv")
    
    def test_analyze_dataframe_function_with_auto_inference(self):
        """Test analyze_dataframe function with automatic metadata inference."""
        data = pd.DataFrame({
            'value1': [1, 2, None],
            'value2': ['A', 'B', 'C']
        })
        
        with patch('funputer.metadata_inference.infer_metadata_from_dataframe') as mock_infer:
            mock_metadata = [
                ColumnMetadata(column_name='value1', data_type='numeric'),
                ColumnMetadata(column_name='value2', data_type='string')
            ]
            mock_infer.return_value = mock_metadata
            
            suggestions = analyze_dataframe(data, metadata=None)
            
            mock_infer.assert_called_once_with(data, warn_user=False)
            assert len(suggestions) == 2
    
    def test_analyze_dataframe_function_with_provided_metadata(self):
        """Test analyze_dataframe function with provided metadata."""
        data = pd.DataFrame({'value': [1, 2, 3]})
        metadata = [ColumnMetadata(column_name='value', data_type='numeric')]
        
        suggestions = analyze_dataframe(data, metadata=metadata)
        
        assert len(suggestions) == 1
        assert suggestions[0].column_name == 'value'


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""
    
    def test_analyze_empty_data_handling(self):
        """Test analysis with empty data."""
        analyzer = ImputationAnalyzer()
        data = pd.DataFrame()
        metadata = []
        
        suggestions = analyzer.analyze_dataframe(data, metadata)
        
        assert len(suggestions) == 0
    
    def test_analyze_with_missing_columns_in_data(self):
        """Test analysis when metadata specifies columns not in data."""
        analyzer = ImputationAnalyzer()
        
        data = pd.DataFrame({'existing_col': [1, 2, 3]})
        metadata = [
            ColumnMetadata(column_name='existing_col', data_type='numeric'),
            ColumnMetadata(column_name='missing_col', data_type='string')
        ]
        
        # Should skip missing columns without error
        suggestions = analyzer.analyze_dataframe(data, metadata)
        
        assert len(suggestions) == 1
        assert suggestions[0].column_name == 'existing_col'
    
    def test_streaming_analysis_memory_monitoring(self, tmp_path):
        """Test memory monitoring during streaming analysis."""
        # Create test files
        metadata_csv = tmp_path / "metadata.csv"
        metadata_content = """column_name,data_type,description
value,numeric,Test value"""
        metadata_csv.write_text(metadata_content)
        
        data_csv = tmp_path / "data.csv"
        data_content = "value\n" + "\n".join([str(i) for i in range(50)])
        data_csv.write_text(data_content)
        
        analyzer = ImputationAnalyzer()
        
        with patch.object(analyzer._memory_monitor, 'should_use_chunking') as mock_chunking:
            mock_chunking.return_value = (True, 20)  # Use streaming
            
            with patch.object(analyzer._memory_monitor, 'warn_if_memory_high') as mock_warn:
                suggestions = analyzer.analyze(str(metadata_csv), str(data_csv))
                
                # Memory warning should be called during chunk processing
                mock_warn.assert_called()
    
    def test_analyze_with_invalid_metadata_path(self):
        """Test analysis with invalid metadata path."""
        analyzer = ImputationAnalyzer()
        
        with pytest.raises(Exception):  # Should raise an error for invalid path
            analyzer.analyze("/nonexistent/metadata.csv", "/also/nonexistent.csv")
    
    def test_streaming_analysis_with_no_chunks(self, tmp_path):
        """Test streaming analysis behavior when no data chunks are available."""
        # Create empty data file
        metadata_csv = tmp_path / "metadata.csv"
        metadata_content = """column_name,data_type,description
value,numeric,Test value"""
        metadata_csv.write_text(metadata_content)
        
        data_csv = tmp_path / "data.csv"
        data_csv.write_text("value\n")  # Header only
        
        analyzer = ImputationAnalyzer()
        
        with patch.object(analyzer._memory_monitor, 'should_use_chunking') as mock_chunking:
            mock_chunking.return_value = (True, 20)  # Force streaming mode
            
            # Should handle gracefully without crashing
            suggestions = analyzer._analyze_streaming(str(metadata_csv), str(data_csv), 20)
            
            assert isinstance(suggestions, list)


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_complete_analysis_workflow_with_all_data_types(self, tmp_path):
        """Test complete analysis workflow with various data types."""
        # Create comprehensive metadata
        metadata_csv = tmp_path / "metadata.csv"
        metadata_content = """column_name,data_type,description,nullable
age,numeric,Person age,false
name,string,Full name,true
salary,numeric,Annual salary,true
active,boolean,Active status,false
category,categorical,User category,true"""
        
        metadata_csv.write_text(metadata_content)
        
        # Create comprehensive data
        data_csv = tmp_path / "data.csv"
        data_content = """age,name,salary,active,category
25,John,50000,true,premium
30,,60000,false,standard
35,Bob,,true,premium
40,Alice,70000,false,
28,Charlie,55000,true,standard"""
        
        data_csv.write_text(data_content)
        
        # Run analysis
        analyzer = ImputationAnalyzer()
        suggestions = analyzer.analyze(str(metadata_csv), str(data_csv))
        
        # Verify comprehensive results
        assert len(suggestions) == 5
        
        # Check that each column has appropriate suggestions
        suggestion_dict = {s.column_name: s for s in suggestions}
        
        # Age should have no missing values
        assert suggestion_dict['age'].missing_count == 0
        
        # Name should have missing values
        assert suggestion_dict['name'].missing_count > 0
        
        # Salary should have missing values  
        assert suggestion_dict['salary'].missing_count > 0
        
        # Active should have no missing values
        assert suggestion_dict['active'].missing_count == 0
        
        # Category should have missing values
        assert suggestion_dict['category'].missing_count > 0
    
    def test_performance_monitoring_integration(self):
        """Test integration with performance monitoring."""
        analyzer = ImputationAnalyzer()
        
        # Create data that should trigger performance considerations
        large_data = pd.DataFrame({
            f'col_{i}': np.random.randint(0, 100, 1000) for i in range(50)
        })
        
        metadata = [ColumnMetadata(column_name=f'col_{i}', data_type='numeric') for i in range(50)]
        
        with patch('funputer.parallel_processor.get_parallel_processing_recommendation') as mock_rec:
            mock_rec.return_value = {'use_parallel': False, 'max_workers': 1}
            
            start_time = pd.Timestamp.now()
            suggestions = analyzer.analyze_dataframe(large_data, metadata)
            end_time = pd.Timestamp.now()
            
            # Should complete in reasonable time
            duration = (end_time - start_time).total_seconds()
            assert duration < 30  # Should complete within 30 seconds
            assert len(suggestions) == 50
    
    def test_security_integration(self):
        """Test security integration in analyzer."""
        analyzer = ImputationAnalyzer(enable_security=True)
        
        # Create data with potential security concerns
        suspicious_data = pd.DataFrame({
            'normal_col': [1, 2, 3, 4, 5],
            'suspicious_col': ['=SUM(A1:A10)', 'normal_value', '@import_something', 'another_normal', '+FORMULA()']
        })
        
        metadata = [
            ColumnMetadata(column_name='normal_col', data_type='numeric'),
            ColumnMetadata(column_name='suspicious_col', data_type='string')
        ]
        
        # Should complete analysis despite suspicious content
        suggestions = analyzer.analyze_dataframe(suspicious_data, metadata)
        
        assert len(suggestions) == 2
        assert suggestions[0].column_name in ['normal_col', 'suspicious_col']
        assert suggestions[1].column_name in ['normal_col', 'suspicious_col']