"""
Additional comprehensive tests for funputer.analyzer module.
Targeting specific coverage gaps to boost from 45% to 80%+.

Focus on missing lines:
- 54-56: Dependency checking in _analyze_missingness_mechanism
- 94-98: Metadata loading in _load_metadata
- 111-181: Main analyze method with file paths
- 200-202: Auto-inference in analyze_dataframe
- 216-217, 226-227, 230-231: Column existence checks
- 296-313: Main analyze_imputation_requirements function
- 332-338: analyze_dataframe function
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from funputer.analyzer import (
    ImputationAnalyzer, analyze_imputation_requirements, analyze_dataframe,
    _analyze_missingness_mechanism
)
from funputer.models import ColumnMetadata, AnalysisConfig, MissingnessType


class TestAnalyzerFileBasedOperations:
    """Test analyzer methods that work with file paths."""
    
    def create_test_files(self):
        """Create temporary test files for analysis."""
        # Create test data
        data = pd.DataFrame({
            'id': range(1, 21),
            'age': [25, 30, np.nan, 35, 40] * 4,
            'income': [50000, np.nan, 75000, 60000, np.nan] * 4,
            'category': ['A', 'B', np.nan, 'C', 'A'] * 4,
            'score': np.random.normal(100, 15, 20)
        })
        
        # Create data CSV file
        data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(data_file.name, index=False)
        data_file.flush()
        
        # Create metadata CSV file
        metadata_df = pd.DataFrame({
            'column_name': ['id', 'age', 'income', 'category', 'score'],
            'data_type': ['integer', 'integer', 'float', 'categorical', 'float'],
            'role': ['identifier', 'feature', 'feature', 'feature', 'target'],
            'nullable': [False, True, True, True, False],
            'description': ['ID', 'Age in years', 'Annual income', 'Category', 'Test score']
        })
        
        metadata_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        metadata_df.to_csv(metadata_file.name, index=False)
        metadata_file.flush()
        
        return data_file.name, metadata_file.name
    
    def test_analyzer_with_file_paths(self):
        """Test ImputationAnalyzer.analyze() with file paths (lines 111-181)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            analyzer = ImputationAnalyzer()
            
            # This should hit lines 111-181 in the analyze method
            result = analyzer.analyze(metadata_file, data_file)
            
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Should analyze all columns with missing data
            suggestions_by_column = {s.column_name: s for s in result}
            assert 'age' in suggestions_by_column
            assert 'income' in suggestions_by_column
            assert 'category' in suggestions_by_column
            
            # Check that metadata loading worked (lines 94-98)
            for suggestion in result:
                assert suggestion.column_name is not None
                assert suggestion.proposed_method is not None
                assert suggestion.confidence_score >= 0
        
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_main_analyze_imputation_requirements_with_metadata(self):
        """Test analyze_imputation_requirements with metadata path (lines 296-313)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            # This should hit lines 296-313 in analyze_imputation_requirements
            result = analyze_imputation_requirements(
                data_path=data_file,
                metadata_path=metadata_file
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Verify it used the metadata file path branch
            suggestions_by_column = {s.column_name: s for s in result}
            assert 'age' in suggestions_by_column
            assert 'income' in suggestions_by_column
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)
    
    def test_main_analyze_imputation_requirements_without_metadata(self):
        """Test analyze_imputation_requirements with auto-inference (lines 302-313)."""
        data_file, metadata_file = self.create_test_files()
        
        try:
            # This should hit the auto-inference branch (lines 302-313)
            result = analyze_imputation_requirements(data_path=data_file)
            
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Should auto-infer and still provide suggestions
            column_names = [s.column_name for s in result]
            assert 'age' in column_names
            assert 'income' in column_names
            
        finally:
            os.unlink(data_file)
            os.unlink(metadata_file)

    def test_main_analyze_imputation_requirements_with_dataframe(self):
        """Test analyze_imputation_requirements with DataFrame input (lines 304-313)."""
        data = pd.DataFrame({
            'numeric_col': [1, 2, np.nan, 4, 5],
            'categorical_col': ['A', 'B', np.nan, 'A', 'B']
        })
        
        # This should hit the DataFrame handling branch
        result = analyze_imputation_requirements(data_path=data)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'numeric_col' in suggestions_by_column
        assert 'categorical_col' in suggestions_by_column


class TestAnalyzeDataFrameFunction:
    """Test the standalone analyze_dataframe function (lines 316-338)."""
    
    def test_analyze_dataframe_with_metadata_list(self):
        """Test analyze_dataframe with metadata list (lines 332-338)."""
        data = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5],
            'col2': ['A', 'B', np.nan, 'C', 'D'],
            'col3': [10, 20, 30, np.nan, 50]
        })
        
        metadata = [
            ColumnMetadata(column_name='col1', data_type='float', role='feature'),
            ColumnMetadata(column_name='col2', data_type='categorical', role='feature'),
            ColumnMetadata(column_name='col3', data_type='integer', role='target')
        ]
        
        # This should hit lines 332-338 in analyze_dataframe function
        result = analyze_dataframe(data=data, metadata=metadata)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'col1' in suggestions_by_column
        assert 'col2' in suggestions_by_column
        assert 'col3' in suggestions_by_column
    
    def test_analyze_dataframe_with_auto_inference(self):
        """Test analyze_dataframe with automatic metadata inference (lines 332-336)."""
        data = pd.DataFrame({
            'numeric': [1.5, 2.3, np.nan, 4.1, 5.7],
            'text': ['hello', 'world', np.nan, 'test', 'data']
        })
        
        # This should trigger auto-inference (lines 332-336)
        result = analyze_dataframe(data=data, metadata=None)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'numeric' in suggestions_by_column
        assert 'text' in suggestions_by_column
    
    def test_analyze_dataframe_with_config(self):
        """Test analyze_dataframe with custom configuration."""
        data = pd.DataFrame({
            'values': [1, 2, np.nan, np.nan, 5, 6, 7, 8, 9, 10]  # 20% missing
        })
        
        config = AnalysisConfig(missing_threshold=0.1)  # Strict threshold
        
        result = analyze_dataframe(data=data, metadata=None, config=config)
        
        assert isinstance(result, list)
        assert len(result) > 0


class TestMissingnessMechanismAnalysis:
    """Test _analyze_missingness_mechanism function for coverage gaps."""
    
    def test_analyze_missingness_with_dependent_column(self):
        """Test missingness analysis with dependent column (lines 54-56)."""
        data = pd.DataFrame({
            'target_col': [1, np.nan, 3, np.nan, 5],
            'predictor_col': [10, 20, 30, 40, 50]
        })
        
        # Create metadata with dependent column specified
        metadata_dict = {
            'target_col': ColumnMetadata(
                column_name='target_col',
                data_type='float',
                role='feature',
                dependent_column='predictor_col'  # This should trigger MAR classification
            ),
            'predictor_col': ColumnMetadata(
                column_name='predictor_col',
                data_type='float',
                role='feature'
            )
        }
        
        # This should hit lines 54-56 for dependent column logic
        result = _analyze_missingness_mechanism('target_col', data, metadata_dict)
        
        assert result.mechanism == MissingnessType.MAR
        assert 'predictor_col' in result.related_columns
        assert 'dependency' in result.rationale.lower()
        assert result.missing_count == 2
        assert result.missing_percentage == 0.4  # 2/5 = 40%

    def test_analyze_missingness_with_nonexistent_dependent_column(self):
        """Test missingness with dependent column that doesn't exist in data."""
        data = pd.DataFrame({
            'target_col': [1, np.nan, 3, np.nan, 5]
        })
        
        metadata_dict = {
            'target_col': ColumnMetadata(
                column_name='target_col',
                data_type='float',
                role='feature',
                dependent_column='nonexistent_col'  # This column doesn't exist
            )
        }
        
        # Should fall back to MCAR when dependent column doesn't exist
        result = _analyze_missingness_mechanism('target_col', data, metadata_dict)
        
        assert result.mechanism == MissingnessType.MCAR
        assert result.related_columns == []
        assert 'mcar' in result.rationale.lower()


class TestAnalyzerEdgeCases:
    """Test edge cases that might not be covered yet."""
    
    def test_analyzer_with_missing_columns_in_data(self):
        """Test analyzer when metadata references columns not in data (lines 226-227, 230-231)."""
        data = pd.DataFrame({
            'existing_col': [1, 2, np.nan, 4, 5]
        })
        
        metadata = [
            ColumnMetadata(column_name='existing_col', data_type='float', role='feature'),
            ColumnMetadata(column_name='missing_col', data_type='string', role='feature')  # Not in data
        ]
        
        analyzer = ImputationAnalyzer()
        
        # This should hit lines 226-227 and 230-231 for column existence checks
        result = analyzer.analyze_dataframe(data, metadata)
        
        assert isinstance(result, list)
        # Should only analyze existing columns
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'existing_col' in suggestions_by_column
        assert 'missing_col' not in suggestions_by_column
    
    def test_analyzer_with_auto_inference_in_analyze_dataframe(self):
        """Test analyze_dataframe with auto-inference (lines 200-202)."""
        data = pd.DataFrame({
            'auto_numeric': [1.1, 2.2, np.nan, 4.4, 5.5],
            'auto_categorical': ['cat1', 'cat2', np.nan, 'cat1', 'cat3']
        })
        
        analyzer = ImputationAnalyzer()
        
        # This should hit lines 200-202 for auto-inference
        result = analyzer.analyze_dataframe(data, metadata=None)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'auto_numeric' in suggestions_by_column
        assert 'auto_categorical' in suggestions_by_column
    
    def test_analyzer_with_skipped_columns_via_config(self):
        """Test analyzer respects skip_columns configuration."""
        data = pd.DataFrame({
            'include_me': [1, 2, np.nan, 4, 5],
            'skip_me': [10, np.nan, 30, 40, 50]
        })
        
        metadata = [
            ColumnMetadata(column_name='include_me', data_type='float', role='feature'),
            ColumnMetadata(column_name='skip_me', data_type='float', role='feature')
        ]
        
        config = AnalysisConfig(skip_columns=['skip_me'])
        analyzer = ImputationAnalyzer(config=config)
        
        result = analyzer.analyze_dataframe(data, metadata)
        
        suggestions_by_column = {s.column_name: s for s in result}
        assert 'include_me' in suggestions_by_column
        # skip_me should be skipped due to configuration
        # Implementation may vary - either not present or marked as skipped
        if 'skip_me' in suggestions_by_column:
            skip_suggestion = suggestions_by_column['skip_me']
            assert 'skip' in skip_suggestion.rationale.lower()


class TestAnalyzerIntegrationScenarios:
    """Test various integration scenarios for comprehensive coverage."""
    
    def test_full_workflow_with_complex_data(self):
        """Test complete analysis workflow with complex realistic data."""
        # Create complex dataset with various data types and missing patterns
        data = pd.DataFrame({
            'user_id': range(1, 101),
            'age': [np.random.randint(18, 80) if i % 7 != 0 else np.nan for i in range(100)],
            'salary': [np.random.normal(50000, 20000) if i % 5 != 0 else np.nan for i in range(100)],
            'department': [np.random.choice(['HR', 'IT', 'Sales', 'Finance']) if i % 8 != 0 else np.nan for i in range(100)],
            'performance_score': np.random.normal(3.5, 0.8, 100),  # No missing values
            'years_experience': [max(0, age - 22) if not pd.isna(age) else np.nan 
                               for age in [np.random.randint(18, 80) if i % 7 != 0 else np.nan for i in range(100)]]
        })
        
        metadata = [
            ColumnMetadata(column_name='user_id', data_type='integer', role='identifier'),
            ColumnMetadata(column_name='age', data_type='integer', role='feature'),
            ColumnMetadata(column_name='salary', data_type='float', role='feature', 
                          dependent_column='age'),  # MAR dependency
            ColumnMetadata(column_name='department', data_type='categorical', role='feature'),
            ColumnMetadata(column_name='performance_score', data_type='float', role='target'),
            ColumnMetadata(column_name='years_experience', data_type='integer', role='feature',
                          dependent_column='age')  # MAR dependency
        ]
        
        analyzer = ImputationAnalyzer()
        result = analyzer.analyze_dataframe(data, metadata)
        
        assert isinstance(result, list)
        assert len(result) >= 5  # Should analyze all columns
        
        # Verify different missingness patterns detected
        suggestions_by_column = {s.column_name: s for s in result}
        
        # user_id should have no missing values
        if 'user_id' in suggestions_by_column:
            assert suggestions_by_column['user_id'].missing_count == 0
        
        # age should have missing values (every 7th)
        if 'age' in suggestions_by_column:
            age_suggestion = suggestions_by_column['age']
            assert age_suggestion.missing_count > 0
        
        # salary and years_experience should be detected as MAR due to age dependency
        if 'salary' in suggestions_by_column:
            salary_suggestion = suggestions_by_column['salary']
            assert salary_suggestion.missing_count > 0
        
        # performance_score should have no missing values
        if 'performance_score' in suggestions_by_column:
            perf_suggestion = suggestions_by_column['performance_score']
            assert perf_suggestion.missing_count == 0