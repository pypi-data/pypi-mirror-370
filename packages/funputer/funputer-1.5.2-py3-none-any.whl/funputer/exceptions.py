"""
Exception handling for imputation suggestions to prevent inappropriate recommendations.
Optimized version with consolidated checks and cleaner patterns.
"""

import pandas as pd
from typing import Optional, List, Callable, Tuple
from .models import (
    ImputationProposal,
    ImputationMethod,
    MissingnessType,
    ColumnMetadata,
    MissingnessAnalysis,
    OutlierAnalysis,
    AnalysisConfig,
)


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class MetadataValidationError(Exception):
    """Exception raised for metadata validation errors."""
    pass


class ImputationException:
    """Base class for imputation exceptions with standardized handling."""

    def __init__(self, method: ImputationMethod, rationale: str, confidence: float = 0.0):
        self.method = method
        self.rationale = rationale
        self.confidence = confidence

    def to_proposal(self) -> ImputationProposal:
        """Convert exception to ImputationProposal."""
        return ImputationProposal(
            method=self.method,
            rationale=self.rationale,
            parameters={"exception_handled": True},
            confidence_score=self.confidence,
        )


# Individual check functions (simplified)

def _check_metadata_validation(metadata: ColumnMetadata, data_series: pd.Series) -> Optional[ImputationException]:
    """Check for metadata validation failures."""
    # Check invalid data type
    valid_types = {"integer", "float", "string", "categorical", "datetime", "boolean"}
    if metadata.data_type not in valid_types:
        return ImputationException(
            ImputationMethod.ERROR_INVALID_METADATA,
            f"Invalid data type '{metadata.data_type}'. Valid types: {valid_types}",
            0.0
        )
    
    # Check invalid constraints
    if metadata.min_value is not None and metadata.max_value is not None and metadata.min_value > metadata.max_value:
        return ImputationException(
            ImputationMethod.ERROR_INVALID_METADATA,
            f"Invalid constraints: min_value ({metadata.min_value}) > max_value ({metadata.max_value})",
            0.0
        )
    
    # Check missing column name
    if not metadata.column_name or not metadata.column_name.strip():
        return ImputationException(
            ImputationMethod.ERROR_INVALID_METADATA,
            "Column name is missing or empty",
            0.0
        )
    
    # Check data type mismatch
    if len(data_series.dropna()) > 0:
        non_null = data_series.dropna()
        if metadata.data_type in ["integer", "float"] and not pd.api.types.is_numeric_dtype(non_null):
            return ImputationException(
                ImputationMethod.ERROR_INVALID_METADATA,
                f"Data type mismatch: metadata says '{metadata.data_type}' but data is not numeric",
                0.0
            )
        elif metadata.data_type == "datetime":
            try:
                pd.to_datetime(non_null.head(5))
            except (ValueError, TypeError):
                return ImputationException(
                    ImputationMethod.ERROR_INVALID_METADATA,
                    "Data type mismatch: metadata says 'datetime' but data cannot be parsed as datetime",
                    0.0
                )
    return None


def _check_no_missing_values(missingness: MissingnessAnalysis) -> Optional[ImputationException]:
    """Check if column has no missing values."""
    if missingness.missing_count == 0:
        return ImputationException(
            ImputationMethod.NO_ACTION_NEEDED,
            "No missing values detected - no imputation required",
            1.0
        )
    return None


def _check_unique_identifier(metadata: ColumnMetadata) -> Optional[ImputationException]:
    """Check if column is a unique identifier."""
    if metadata.unique_flag:
        return ImputationException(
            ImputationMethod.MANUAL_BACKFILL,
            "Unique IDs cannot be auto-imputed - requires manual backfill to maintain data integrity",
            0.9
        )
    return None


def _check_all_missing(data_series: pd.Series, missingness: MissingnessAnalysis) -> Optional[ImputationException]:
    """Check if all values are missing."""
    if len(data_series) > 0 and missingness.missing_count == len(data_series):
        return ImputationException(
            ImputationMethod.MANUAL_BACKFILL,
            "No observed values to base imputation on - requires manual data collection",
            0.8
        )
    return None


def _check_mnar_without_rule(missingness: MissingnessAnalysis, metadata: ColumnMetadata) -> Optional[ImputationException]:
    """Check MNAR/UNKNOWN without business rule."""
    if (missingness.mechanism in [MissingnessType.MNAR, MissingnessType.UNKNOWN] 
        and not getattr(metadata, 'business_rule', None)):
        return ImputationException(
            ImputationMethod.MANUAL_BACKFILL,
            "MNAR/Unknown mechanism detected with no domain rule - requires manual investigation",
            0.7
        )
    return None


def _check_nullable_violation(missingness: MissingnessAnalysis, metadata: ColumnMetadata) -> Optional[ImputationException]:
    """Check nullable constraint violation."""
    if metadata.nullable is False and missingness.missing_count > 0:
        return ImputationException(
            ImputationMethod.ERROR_INVALID_METADATA,
            f"Column '{metadata.column_name}' has nullable=False but contains {missingness.missing_count} missing values",
            0.0
        )
    return None


def _check_allowed_values(data_series: pd.Series, metadata: ColumnMetadata) -> Optional[ImputationException]:
    """Check allowed values constraint."""
    if not metadata.allowed_values or len(data_series.dropna()) == 0:
        return None
        
    # Parse allowed values
    allowed = [v.strip() for v in str(metadata.allowed_values).split(",") if v.strip()]
    if not allowed:
        return None
        
    # Check for violations
    non_null = data_series.dropna()
    invalid = non_null[~non_null.astype(str).isin(allowed)]
    
    if len(invalid) > 0:
        unique_invalid = list(invalid.unique()[:5])  # First 5 for readability
        return ImputationException(
            ImputationMethod.ERROR_INVALID_METADATA,
            f"Column '{metadata.column_name}' contains invalid values: {unique_invalid}. Allowed: {allowed}",
            0.0
        )
    return None


def _check_max_length(data_series: pd.Series, metadata: ColumnMetadata) -> Optional[ImputationException]:
    """Check max length constraint."""
    if (metadata.max_length is None or 
        metadata.data_type not in ["string", "categorical"] or
        len(data_series.dropna()) == 0):
        return None
        
    max_actual = data_series.dropna().astype(str).str.len().max()
    if max_actual > metadata.max_length:
        return ImputationException(
            ImputationMethod.ERROR_INVALID_METADATA,
            f"Column '{metadata.column_name}' has max_length={metadata.max_length} but contains values up to {max_actual} characters",
            0.0
        )
    return None


# Define checks in priority order
EXCEPTION_CHECKS: List[Tuple[str, Callable]] = [
    # (name, function with appropriate signature)
    ("metadata_validation", lambda d, m, mi, o, c: _check_metadata_validation(m, d)),
    ("no_missing", lambda d, m, mi, o, c: _check_no_missing_values(mi)),
    ("unique_id", lambda d, m, mi, o, c: _check_unique_identifier(m)),
    ("all_missing", lambda d, m, mi, o, c: _check_all_missing(d, mi)),
    ("mnar_no_rule", lambda d, m, mi, o, c: _check_mnar_without_rule(mi, m)),
    ("nullable_violation", lambda d, m, mi, o, c: _check_nullable_violation(mi, m)),
    ("allowed_values", lambda d, m, mi, o, c: _check_allowed_values(d, m)),
    ("max_length", lambda d, m, mi, o, c: _check_max_length(d, m)),
]


def apply_exception_handling(
    column_name: str,
    data_series: pd.Series,
    metadata: ColumnMetadata,
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    config: AnalysisConfig,
) -> Optional[ImputationProposal]:
    """
    Apply all exception handling rules in priority order.

    Args:
        column_name: Name of the column
        data_series: The data series
        metadata: Column metadata
        missingness_analysis: Results of missingness analysis
        outlier_analysis: Results of outlier analysis
        config: Analysis configuration

    Returns:
        ImputationProposal if exception applies, None if normal processing should continue
    """
    # Check if column should be skipped entirely
    if should_skip_column(column_name, config):
        return None  # Handled at higher level by omitting from output
    
    # Apply checks in priority order
    for check_name, check_func in EXCEPTION_CHECKS:
        exception = check_func(data_series, metadata, missingness_analysis, outlier_analysis, config)
        if exception:
            return exception.to_proposal()
    
    # No exceptions apply - proceed with normal imputation
    return None


def should_skip_column(column_name: str, config: AnalysisConfig) -> bool:
    """
    Determine if a column should be completely omitted from analysis output.

    Args:
        column_name: Name of the column
        config: Analysis configuration

    Returns:
        True if column should be skipped, False otherwise
    """
    return column_name in config.skip_columns


