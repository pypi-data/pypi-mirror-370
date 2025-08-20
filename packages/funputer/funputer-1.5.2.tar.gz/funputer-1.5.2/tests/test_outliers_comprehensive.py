"""
Comprehensive tests for funputer.outliers module.
Targeting 73% → 80%+ coverage.

Missing lines to cover: [38, 42, 66, 67, 69, 70, 71, 73, 74, 99, 113, 120, 134, 135, 137, 145, 158]
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

from funputer.outliers import (
    detect_outliers_iqr, detect_outliers_zscore, suggest_outlier_handling,
    analyze_outliers, _check_business_rule_violations, _get_percentage_based_strategy,
    OUTLIER_CONFIG
)
from funputer.models import ColumnMetadata, AnalysisConfig, OutlierHandling


class TestOutlierDetection:
    """Test outlier detection functions."""
    
    def test_detect_outliers_iqr_with_default_multiplier(self):
        """Test IQR detection with default multiplier (line 38)."""
        series = pd.Series([1, 2, 3, 4, 5, 10, 100])  # 100 is clear outlier
        
        # Call without multiplier to hit line 38
        outliers, lower_bound, upper_bound = detect_outliers_iqr(series, iqr_multiplier=None)
        
        assert len(outliers) > 0
        assert 100 in outliers  # Should detect 100 as outlier
        assert lower_bound < upper_bound
        
    def test_detect_outliers_iqr_empty_series(self):
        """Test IQR detection with empty series after dropna (line 42)."""
        series = pd.Series([np.nan, np.nan, np.nan])  # All NaN
        
        outliers, lower_bound, upper_bound = detect_outliers_iqr(series)
        
        assert outliers == []
        assert np.isnan(lower_bound)
        assert np.isnan(upper_bound)
    
    def test_detect_outliers_zscore_with_default_threshold(self):
        """Test Z-score detection with default threshold (lines 66-67)."""
        series = pd.Series([1, 2, 3, 4, 5, 100])  # 100 is clear outlier
        
        # Call without threshold to hit lines 66-67
        outliers = detect_outliers_zscore(series, threshold=None)
        
        assert len(outliers) > 0
        assert 100 in outliers
    
    def test_detect_outliers_zscore_empty_series(self):
        """Test Z-score detection with empty series after dropna (lines 69-71)."""
        series = pd.Series([np.nan, np.nan, np.nan])  # All NaN
        
        outliers = detect_outliers_zscore(series)
        
        assert outliers == []
    
    def test_detect_outliers_zscore_calculation(self):
        """Test Z-score calculation path (lines 73-74)."""
        # Create series with known outlier
        series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])
        
        outliers = detect_outliers_zscore(series, threshold=2.0)  # Lower threshold
        
        assert len(outliers) > 0
        assert 100 in outliers


class TestOutlierHandling:
    """Test outlier handling suggestion logic."""
    
    def test_suggest_handling_high_outlier_percentage(self):
        """Test handling suggestion for high outlier percentage (line 99)."""
        outlier_analysis = {
            "outlier_count": 25,
            "outlier_percentage": 0.25,  # 25% - above high threshold
            "lower_bound": 0,
            "upper_bound": 100
        }
        
        metadata = ColumnMetadata(column_name='test', data_type='float', role='feature')
        config = AnalysisConfig()
        
        strategy, rationale = suggest_outlier_handling(outlier_analysis, metadata, config)
        
        assert strategy == OutlierHandling.LEAVE_AS_IS
        assert "High outlier percentage" in rationale
        assert "data distribution issue" in rationale
    
    def test_suggest_handling_categorical_data(self):
        """Test handling suggestion for categorical data (line 113)."""
        outlier_analysis = {
            "outlier_count": 5,
            "outlier_percentage": 0.05,
            "lower_bound": None,
            "upper_bound": None
        }
        
        metadata = ColumnMetadata(column_name='category', data_type='categorical', role='feature')
        config = AnalysisConfig()
        
        strategy, rationale = suggest_outlier_handling(outlier_analysis, metadata, config)
        
        assert strategy == OutlierHandling.LEAVE_AS_IS
        assert "Categorical data" in rationale
        assert "valid categories" in rationale
    
    def test_suggest_handling_business_rule_violations(self):
        """Test handling suggestion for business rule violations (line 120)."""
        outlier_analysis = {
            "outlier_count": 3,
            "outlier_percentage": 0.03,
            "lower_bound": -10,  # Below business min
            "upper_bound": 110   # Above business max
        }
        
        metadata = ColumnMetadata(
            column_name='score', 
            data_type='float', 
            role='feature',
            min_value=0,    # Business rule: minimum 0
            max_value=100   # Business rule: maximum 100
        )
        config = AnalysisConfig()
        
        # Mock the business rule check to return True
        with patch('funputer.outliers._check_business_rule_violations') as mock_check:
            mock_check.return_value = True
            
            strategy, rationale = suggest_outlier_handling(outlier_analysis, metadata, config)
        
        assert strategy == OutlierHandling.CAP_TO_BOUNDS
        assert "business rules" in rationale
        assert "cap to valid range" in rationale
        
    def test_check_business_rule_violations_with_bounds(self):
        """Test business rule violation checking (lines 134-137)."""
        outlier_analysis = {
            "lower_bound": -5,   # Below min_value
            "upper_bound": 105   # Above max_value
        }
        
        metadata = ColumnMetadata(
            column_name='test', 
            data_type='float', 
            role='feature',
            min_value=0,
            max_value=100
        )
        
        result = _check_business_rule_violations(outlier_analysis, metadata)
        
        assert result is True  # Should detect violations
    
    def test_get_percentage_based_strategy_low_outliers(self):
        """Test percentage-based strategy for low outliers (line 145)."""
        metadata = ColumnMetadata(column_name='test', data_type='float', role='feature')
        config = AnalysisConfig(outlier_threshold=0.10)  # 10% threshold
        
        # Low outlier percentage (below threshold)
        strategy, rationale = _get_percentage_based_strategy(0.05, metadata, config)
        
        assert strategy == OutlierHandling.CAP_TO_BOUNDS
        assert "Low outlier percentage" in rationale
        assert "cap to statistical bounds" in rationale
    
    def test_get_percentage_based_strategy_manual_review(self):
        """Test percentage-based strategy requiring manual review (line 158)."""
        metadata = ColumnMetadata(column_name='test', data_type='float', role='feature')
        config = AnalysisConfig(outlier_threshold=0.02)  # Very low threshold
        
        # High outlier percentage requiring manual review
        strategy, rationale = _get_percentage_based_strategy(0.15, metadata, config)
        
        assert strategy == OutlierHandling.LEAVE_AS_IS
        assert "manual review" in rationale


class TestOutlierAnalysisIntegration:
    """Test the main analyze_outliers function."""
    
    def test_analyze_outliers_comprehensive_workflow(self):
        """Test complete outlier analysis workflow."""
        # Create data with clear outliers
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 100, 200])
        
        metadata = ColumnMetadata(
            column_name='values',
            data_type='float',
            role='feature'
        )
        
        config = AnalysisConfig()
        
        result = analyze_outliers(data, metadata, config)
        
        assert isinstance(result.outlier_count, int)
        assert result.outlier_count > 0
        assert result.outlier_percentage > 0
        assert result.lower_bound is not None
        assert result.upper_bound is not None
        assert len(result.outlier_values) > 0
        assert result.handling_strategy in OutlierHandling
        assert result.rationale is not None
    
    def test_analyze_outliers_edge_cases(self):
        """Test various edge cases for complete coverage."""
        
        # Test 1: Non-numeric data type
        text_data = pd.Series(['A', 'B', 'C', 'D'])
        metadata_text = ColumnMetadata(
            column_name='category',
            data_type='string',
            role='feature'
        )
        config = AnalysisConfig()
        
        result = analyze_outliers(text_data, metadata_text, config)
        
        assert result.outlier_count == 0
        assert result.outlier_percentage == 0.0
        assert result.lower_bound is None
        assert result.upper_bound is None
        assert result.outlier_values == []
        assert result.handling_strategy == OutlierHandling.LEAVE_AS_IS
        assert "Non-numeric data type" in result.rationale
        
        # Test 2: Data with unique flag
        unique_data = pd.Series([1, 2, 3, 100])
        metadata_unique = ColumnMetadata(
            column_name='id',
            data_type='integer',
            role='identifier',
            unique_flag=True
        )
        
        result = analyze_outliers(unique_data, metadata_unique, config)
        
        # Should detect outliers but suggest leaving as is due to unique flag
        assert result.outlier_count > 0
        assert result.handling_strategy == OutlierHandling.LEAVE_AS_IS
        assert "Unique identifier" in result.rationale
        
        # Test 3: High outlier percentage
        high_outlier_data = pd.Series([1, 100, 200, 300, 400])  # 80% outliers
        metadata_normal = ColumnMetadata(
            column_name='values',
            data_type='float',
            role='feature'
        )
        
        result = analyze_outliers(high_outlier_data, metadata_normal, config)
        
        assert result.outlier_percentage > 0.2  # High percentage
        assert result.handling_strategy == OutlierHandling.LEAVE_AS_IS
        assert "High outlier percentage" in result.rationale


class TestOutlierConstants:
    """Test that outlier configuration constants are accessible."""
    
    def test_outlier_config_constants(self):
        """Test that all required constants are defined."""
        assert 'default_iqr_multiplier' in OUTLIER_CONFIG
        assert 'default_zscore_threshold' in OUTLIER_CONFIG
        assert 'high_outlier_threshold' in OUTLIER_CONFIG
        assert 'medium_outlier_threshold' in OUTLIER_CONFIG
        assert 'min_samples_for_detection' in OUTLIER_CONFIG
        assert 'max_outliers_to_store' in OUTLIER_CONFIG
        
        # Test default values are reasonable
        assert OUTLIER_CONFIG['default_iqr_multiplier'] == 1.5
        assert OUTLIER_CONFIG['default_zscore_threshold'] == 3.0
        assert OUTLIER_CONFIG['high_outlier_threshold'] == 0.2
        assert OUTLIER_CONFIG['medium_outlier_threshold'] == 0.1