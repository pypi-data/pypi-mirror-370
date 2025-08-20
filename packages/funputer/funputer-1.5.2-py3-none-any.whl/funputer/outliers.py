"""
Outlier detection and handling strategies.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from scipy import stats

from .models import OutlierAnalysis, OutlierHandling, ColumnMetadata, AnalysisConfig

# Outlier detection constants for consistency
OUTLIER_CONFIG = {
    'default_iqr_multiplier': 1.5,
    'default_zscore_threshold': 3.0,
    'high_outlier_threshold': 0.2,  # 20% outliers suggests data issue
    'medium_outlier_threshold': 0.1,  # 10% outliers
    'min_samples_for_detection': 10,
    'max_outliers_to_store': 10,
    'min_correlation_threshold': 0.3
}


def detect_outliers_iqr(
    series: pd.Series, iqr_multiplier: float = None
) -> Tuple[List[float], float, float]:
    """
    Detect outliers using IQR method with configurable multiplier.

    Args:
        series: Pandas series to analyze
        iqr_multiplier: Multiplier for IQR calculation (uses default if None)

    Returns:
        Tuple of (outlier_values, lower_bound, upper_bound)
    """
    if iqr_multiplier is None:
        iqr_multiplier = OUTLIER_CONFIG['default_iqr_multiplier']
    
    clean_series = series.dropna()
    if len(clean_series) == 0:
        return [], np.nan, np.nan

    # Calculate quartiles and bounds
    q1, q3 = clean_series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower_bound = q1 - iqr_multiplier * iqr
    upper_bound = q3 + iqr_multiplier * iqr

    # Find outliers efficiently
    outliers = clean_series[(clean_series < lower_bound) | (clean_series > upper_bound)]
    return outliers.tolist(), lower_bound, upper_bound


def detect_outliers_zscore(series: pd.Series, threshold: float = None) -> List[float]:
    """
    Detect outliers using Z-score method with configurable threshold.

    Args:
        series: Pandas series to analyze
        threshold: Z-score threshold for outlier detection (uses default if None)

    Returns:
        List of outlier values
    """
    if threshold is None:
        threshold = OUTLIER_CONFIG['default_zscore_threshold']
    
    clean_series = series.dropna()
    if len(clean_series) == 0:
        return []

    z_scores = np.abs(stats.zscore(clean_series))
    return clean_series[z_scores > threshold].tolist()


def suggest_outlier_handling(
    outlier_analysis: dict, metadata: ColumnMetadata, config: AnalysisConfig
) -> Tuple[OutlierHandling, str]:
    """
    Suggest outlier handling strategy with centralized decision logic.

    Args:
        outlier_analysis: Dictionary with outlier analysis results
        metadata: Column metadata
        config: Analysis configuration

    Returns:
        Tuple of (handling_strategy, rationale)
    """
    outlier_count = outlier_analysis["outlier_count"]
    outlier_percentage = outlier_analysis["outlier_percentage"]

    # Early returns for simple cases
    if outlier_count == 0:
        return OutlierHandling.LEAVE_AS_IS, "No outliers detected"
    
    if outlier_percentage > OUTLIER_CONFIG['high_outlier_threshold']:
        return (
            OutlierHandling.LEAVE_AS_IS,
            f"High outlier percentage ({outlier_percentage:.1%}) suggests "
            "potential data distribution issue - investigate before handling"
        )
    
    # Column-specific rules
    if metadata.unique_flag:
        return (
            OutlierHandling.LEAVE_AS_IS,
            "Unique identifier column - outliers should not be modified"
        )
    
    if metadata.data_type == "categorical":
        return (
            OutlierHandling.LEAVE_AS_IS,
            "Categorical data - outliers represent valid categories"
        )
    
    # Business rule violations check
    if _check_business_rule_violations(outlier_analysis, metadata):
        return (
            OutlierHandling.CAP_TO_BOUNDS,
            f"Outliers violate business rules (min: {metadata.min_value}, "
            f"max: {metadata.max_value}) - cap to valid range"
        )
    
    # Percentage-based decisions for numeric data
    return _get_percentage_based_strategy(outlier_percentage, metadata, config)

def _check_business_rule_violations(outlier_analysis: dict, metadata: ColumnMetadata) -> bool:
    """Check if outliers violate business rules."""
    if metadata.min_value is None and metadata.max_value is None:
        return False
    
    lower_bound = outlier_analysis.get("lower_bound")
    upper_bound = outlier_analysis.get("upper_bound")
    
    return (
        (metadata.min_value is not None and lower_bound < metadata.min_value) or
        (metadata.max_value is not None and upper_bound > metadata.max_value)
    )

def _get_percentage_based_strategy(outlier_percentage: float, metadata: ColumnMetadata, config: AnalysisConfig) -> Tuple[OutlierHandling, str]:
    """Get outlier handling strategy based on percentage thresholds."""
    if outlier_percentage < config.outlier_threshold and metadata.data_type in ["integer", "float"]:
        return (
            OutlierHandling.CAP_TO_BOUNDS,
            f"Low outlier percentage ({outlier_percentage:.1%}) - "
            "cap to statistical bounds to preserve data distribution"
        )
    
    if outlier_percentage < OUTLIER_CONFIG['medium_outlier_threshold']:
        return (
            OutlierHandling.CONVERT_TO_NAN,
            f"Medium outlier percentage ({outlier_percentage:.1%}) - "
            "convert to NaN for imputation to avoid bias"
        )
    
    return (
        OutlierHandling.LEAVE_AS_IS,
        f"Outlier percentage ({outlier_percentage:.1%}) requires manual review"
    )


def analyze_outliers(
    series: pd.Series, metadata: ColumnMetadata, config: AnalysisConfig
) -> OutlierAnalysis:
    """
    Perform comprehensive outlier analysis with streamlined logic.

    Args:
        series: Pandas series to analyze
        metadata: Column metadata
        config: Analysis configuration

    Returns:
        OutlierAnalysis object with results and recommendations
    """
    # Skip outlier detection for non-numeric data types
    if metadata.data_type not in ["integer", "float"]:
        return OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            lower_bound=None,
            upper_bound=None,
            outlier_values=[],
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale=f"Non-numeric data type ({metadata.data_type}) - no outlier detection"
        )

    # Detect outliers and calculate metrics
    outlier_values, lower_bound, upper_bound = detect_outliers_iqr(
        series, config.iqr_multiplier
    )
    
    outlier_count = len(outlier_values)
    total_non_null = series.count()
    outlier_percentage = outlier_count / total_non_null if total_non_null > 0 else 0.0

    # Create analysis dict and get strategy
    outlier_analysis_dict = {
        "outlier_count": outlier_count,
        "outlier_percentage": outlier_percentage,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
    }
    
    handling_strategy, rationale = suggest_outlier_handling(
        outlier_analysis_dict, metadata, config
    )

    return OutlierAnalysis(
        outlier_count=outlier_count,
        outlier_percentage=outlier_percentage,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        outlier_values=outlier_values[:OUTLIER_CONFIG['max_outliers_to_store']],
        handling_strategy=handling_strategy,
        rationale=rationale,
    )
