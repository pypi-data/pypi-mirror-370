"""
Consolidated imputation proposal system.
Contains all logic for proposing imputation methods and calculating confidence scores.
"""

import pandas as pd
from scipy import stats
from typing import Dict, Optional, Callable

from .models import (
    ColumnMetadata,
    MissingnessAnalysis,
    OutlierAnalysis,
    AnalysisConfig,
    ImputationProposal,
    ImputationMethod,
    MissingnessType
)
from .exceptions import apply_exception_handling


# Confidence scoring weights
CONFIDENCE_WEIGHTS = {
    'base': 0.5,
    'missing_low': 0.2,    # < 5% missing
    'missing_med': 0.1,    # < 20% missing  
    'missing_high': -0.2,  # > 50% missing
    'mcar_certain': 0.1,
    'mar_evidence': 0.05,
    'mechanism_unknown': -0.1,
    'outliers_low': 0.05,   # < 5% outliers
    'outliers_high': -0.1,  # > 20% outliers
    'has_constraints': 0.1,
    'constraint_compliance': 0.05,
    'non_nullable_violation': -0.15
}


def propose_imputation_method(
    column_name: str,
    data_series: pd.Series,
    metadata: ColumnMetadata,
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    config: AnalysisConfig,
    full_data: Optional[pd.DataFrame] = None,
    metadata_dict: Optional[Dict[str, ColumnMetadata]] = None,
) -> ImputationProposal:
    """
    Propose the best imputation method based on comprehensive analysis.

    Args:
        column_name: Name of the column
        data_series: The data series to analyze
        metadata: Column metadata
        missingness_analysis: Results of missingness analysis
        outlier_analysis: Results of outlier analysis
        config: Analysis configuration
        full_data: Full dataset (unused in simplified version)
        metadata_dict: Dictionary of all column metadata (unused in simplified version)

    Returns:
        ImputationProposal with method, rationale, and parameters
    """
    # FIRST: Apply exception handling rules
    exception_proposal = apply_exception_handling(
        column_name,
        data_series,
        metadata,
        missingness_analysis,
        outlier_analysis,
        config,
    )

    if exception_proposal is not None:
        return exception_proposal

    # Helper function to calculate confidence score
    def get_confidence_score():
        return calculate_confidence_score(
            missingness_analysis, outlier_analysis, metadata, data_series
        )

    # If no exceptions apply, proceed with normal imputation logic
    missing_pct = missingness_analysis.missing_percentage
    mechanism = missingness_analysis.mechanism

    # Handle unique identifier columns (backup check)
    if metadata.unique_flag:
        return ImputationProposal(
            method=ImputationMethod.MANUAL_BACKFILL,
            rationale="Unique identifier column requires manual backfill to maintain data integrity",
            parameters={"strategy": "manual_review"},
            confidence_score=get_confidence_score(),
        )

    # Handle dependency rule columns (specific calculations)
    dependency_rule = getattr(metadata, 'dependency_rule', None)
    if dependency_rule and metadata.dependent_column:
        return ImputationProposal(
            method=ImputationMethod.BUSINESS_RULE,
            rationale=f"Column has dependency rule on {metadata.dependent_column}: {dependency_rule}",
            parameters={
                "dependent_column": metadata.dependent_column,
                "rule": dependency_rule,
                "rule_type": "dependency",
            },
            confidence_score=get_confidence_score(),
        )

    # Handle business rule columns (general constraints)
    business_rule = getattr(metadata, 'business_rule', None)
    if business_rule and metadata.dependent_column:
        return ImputationProposal(
            method=ImputationMethod.BUSINESS_RULE,
            rationale=f"Column has business rule dependency on {metadata.dependent_column}: {business_rule}",
            parameters={
                "dependent_column": metadata.dependent_column,
                "rule": business_rule,
                "rule_type": "business",
            },
            confidence_score=get_confidence_score(),
        )

    # Handle high missing percentage (>80%)
    if missing_pct > config.missing_threshold:
        return ImputationProposal(
            method=ImputationMethod.CONSTANT_MISSING,
            rationale=f"Very high missing percentage ({missing_pct:.1%}) suggests systematic absence - use constant 'Missing'",
            parameters={"fill_value": "Missing"},
            confidence_score=get_confidence_score(),
        )

    # Method selection by data type and mechanism
    if metadata.data_type == "categorical":
        return propose_categorical_method(
            data_series, metadata, mechanism, missingness_analysis, get_confidence_score
        )

    elif metadata.data_type == "string":
        return propose_string_method(
            data_series, metadata, mechanism, get_confidence_score
        )

    elif metadata.data_type in ["integer", "float"]:
        return propose_numeric_method(
            data_series, metadata, mechanism, missingness_analysis, config, get_confidence_score
        )

    else:
        return _propose_simple_method(metadata.data_type, mechanism, get_confidence_score)


def propose_categorical_method(
    data_series: pd.Series,
    metadata: ColumnMetadata,
    mechanism: MissingnessType,
    missingness_analysis: MissingnessAnalysis,
    get_confidence_score: Callable[[], float]
) -> ImputationProposal:
    """Propose imputation method for categorical data."""
    allowed_values = get_allowed_values_list(metadata)
    
    if allowed_values:
        return _propose_constrained_categorical(
            data_series, metadata, mechanism, allowed_values, get_confidence_score
        )
    else:
        return _propose_unconstrained_categorical(
            data_series, mechanism, missingness_analysis, get_confidence_score
        )


def _propose_constrained_categorical(
    data_series: pd.Series,
    metadata: ColumnMetadata,
    mechanism: MissingnessType,
    allowed_values: list,
    get_confidence_score: Callable[[], float]
) -> ImputationProposal:
    """Propose method for categorical data with allowed_values constraints."""
    if mechanism == MissingnessType.MCAR:
        valid_data = data_series.dropna()
        if len(valid_data) > 0:
            valid_data = valid_data[valid_data.astype(str).isin(allowed_values)]
            most_frequent = valid_data.mode().iloc[0] if len(valid_data.mode()) > 0 else allowed_values[0]
        else:
            most_frequent = allowed_values[0]
        
        return ImputationProposal(
            method=ImputationMethod.MODE,
            rationale=f"Categorical MCAR with {len(allowed_values)} allowed values - use most frequent",
            parameters={
                "strategy": "most_frequent",
                "allowed_values": allowed_values,
                "fill_value": most_frequent
            },
            confidence_score=get_confidence_score()
        )
    else:
        return ImputationProposal(
            method=ImputationMethod.KNN,
            rationale=f"Categorical MAR with {len(allowed_values)} allowed values - use constrained kNN",
            parameters={
                "n_neighbors": min(5, max(3, data_series.count() // 20)),
                "weights": "distance",
                "allowed_values": allowed_values
            },
            confidence_score=get_confidence_score()
        )


def _propose_unconstrained_categorical(
    data_series: pd.Series,
    mechanism: MissingnessType,
    missingness_analysis: MissingnessAnalysis,
    get_confidence_score: Callable[[], float]
) -> ImputationProposal:
    """Propose method for categorical data without constraints."""
    if mechanism == MissingnessType.MCAR:
        return ImputationProposal(
            method=ImputationMethod.MODE,
            rationale="Categorical MCAR - use most frequent category",
            parameters={"strategy": "most_frequent"},
            confidence_score=get_confidence_score()
        )
    else:
        related = ', '.join(missingness_analysis.related_columns[:2]) if missingness_analysis.related_columns else 'unknown'
        return ImputationProposal(
            method=ImputationMethod.KNN,
            rationale=f"Categorical MAR (related to {related}) - use kNN",
            parameters={
                "n_neighbors": min(5, max(3, data_series.count() // 20)),
                "weights": "distance"
            },
            confidence_score=get_confidence_score()
        )


def propose_numeric_method(
    data_series: pd.Series,
    metadata: ColumnMetadata,
    mechanism: MissingnessType,
    missingness_analysis: MissingnessAnalysis,
    config: AnalysisConfig,
    get_confidence_score: Callable[[], float]
) -> ImputationProposal:
    """Propose imputation method for numeric data."""
    non_null_data = data_series.dropna()
    skewness = abs(stats.skew(non_null_data)) if len(non_null_data) > 3 else 0
    
    if mechanism == MissingnessType.MCAR:
        if skewness > config.skewness_threshold:
            return ImputationProposal(
                method=ImputationMethod.MEDIAN,
                rationale=f"Numeric MCAR with high skewness ({skewness:.2f}) - use median",
                parameters={"strategy": "median"},
                confidence_score=get_confidence_score()
            )
        else:
            return ImputationProposal(
                method=ImputationMethod.MEAN,
                rationale=f"Numeric MCAR with low skewness ({skewness:.2f}) - use mean",
                parameters={"strategy": "mean"},
                confidence_score=get_confidence_score()
            )
    else:
        # MAR mechanism
        if len(non_null_data) > 50 and missingness_analysis.related_columns:
            return ImputationProposal(
                method=ImputationMethod.REGRESSION,
                rationale=f"Numeric MAR - use regression with predictors: {', '.join(missingness_analysis.related_columns[:2])}",
                parameters={
                    "predictors": missingness_analysis.related_columns[:3],
                    "estimator": "BayesianRidge"
                },
                confidence_score=get_confidence_score()
            )
        else:
            return ImputationProposal(
                method=ImputationMethod.KNN,
                rationale="Numeric MAR - use kNN (insufficient data for regression)",
                parameters={
                    "n_neighbors": min(5, max(3, len(non_null_data) // 10)),
                    "weights": "distance"
                },
                confidence_score=get_confidence_score()
            )


def propose_string_method(
    data_series: pd.Series,
    metadata: ColumnMetadata,
    mechanism: MissingnessType,
    get_confidence_score: Callable[[], float]
) -> ImputationProposal:
    """Propose imputation method for string data."""
    base_params = {"strategy": "most_frequent"} if mechanism == MissingnessType.MCAR else {
        "n_neighbors": min(5, max(3, data_series.count() // 20)),
        "weights": "distance"
    }
    
    if metadata.max_length:
        base_params["max_length"] = metadata.max_length
        constraint_info = f" and max_length={metadata.max_length}"
    else:
        constraint_info = ""
    
    method = ImputationMethod.MODE if mechanism == MissingnessType.MCAR else ImputationMethod.KNN
    mech_name = "MCAR" if mechanism == MissingnessType.MCAR else "MAR"
    
    return ImputationProposal(
        method=method,
        rationale=f"String data with {mech_name}{constraint_info} - use {'mode' if method == ImputationMethod.MODE else 'kNN'}",
        parameters=base_params,
        confidence_score=get_confidence_score()
    )


def _propose_simple_method(data_type: str, mechanism: MissingnessType, get_confidence_score):
    """Propose method for simple data types (datetime, boolean) and fallback."""
    if data_type == "datetime":
        if mechanism == MissingnessType.MCAR:
            return ImputationProposal(
                method=ImputationMethod.FORWARD_FILL,
                rationale="Datetime MCAR - forward fill for temporal continuity",
                parameters={"method": "ffill", "limit": 3},
                confidence_score=get_confidence_score()
            )
        else:
            return ImputationProposal(
                method=ImputationMethod.BUSINESS_RULE,
                rationale="Datetime MAR - requires business logic",
                parameters={"strategy": "business_logic_required"},
                confidence_score=get_confidence_score()
            )
    elif data_type == "boolean":
        return ImputationProposal(
            method=ImputationMethod.MODE,
            rationale="Boolean data - use most frequent value",
            parameters={"strategy": "most_frequent"},
            confidence_score=get_confidence_score()
        )
    else:
        # Unknown data type fallback
        return ImputationProposal(
            method=ImputationMethod.CONSTANT_MISSING,
            rationale=f"Unknown data type ({data_type}) - safe fallback",
            parameters={"fill_value": "Missing"},
            confidence_score=0.3
        )


def calculate_confidence_score(
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    metadata: ColumnMetadata,
    data_series: pd.Series,
) -> float:
    """Calculate constraint-aware confidence score for imputation proposals."""
    confidence = CONFIDENCE_WEIGHTS['base']
    
    # Missing data impact
    missing_pct = missingness_analysis.missing_percentage
    if missing_pct < 0.05:
        confidence += CONFIDENCE_WEIGHTS['missing_low']
    elif missing_pct < 0.20:
        confidence += CONFIDENCE_WEIGHTS['missing_med'] 
    elif missing_pct > 0.50:
        confidence += CONFIDENCE_WEIGHTS['missing_high']
    
    # Mechanism certainty
    if missingness_analysis.mechanism == MissingnessType.MCAR:
        if not missingness_analysis.p_value or missingness_analysis.p_value > 0.1:
            confidence += CONFIDENCE_WEIGHTS['mcar_certain']
    elif missingness_analysis.mechanism == MissingnessType.MAR:
        if missingness_analysis.related_columns:
            confidence += CONFIDENCE_WEIGHTS['mar_evidence']
    else:
        confidence += CONFIDENCE_WEIGHTS['mechanism_unknown']
    
    # Outlier impact
    if outlier_analysis.outlier_percentage < 0.05:
        confidence += CONFIDENCE_WEIGHTS['outliers_low']
    elif outlier_analysis.outlier_percentage > 0.20:
        confidence += CONFIDENCE_WEIGHTS['outliers_high']
    
    # Constraint awareness
    confidence += _calculate_constraint_impact(metadata, data_series, missingness_analysis.missing_count)
    
    return max(0.1, min(1.0, confidence))


def _calculate_constraint_impact(metadata: ColumnMetadata, data_series: pd.Series, missing_count: int) -> float:
    """Calculate confidence impact from metadata constraints."""
    impact = 0.0
    
    # Constraint availability bonus
    if metadata.allowed_values and str(metadata.allowed_values).strip():
        if metadata.data_type in ["categorical", "string"]:
            impact += CONFIDENCE_WEIGHTS['has_constraints']
    
    if metadata.max_length and metadata.data_type in ["string", "categorical"]:
        impact += CONFIDENCE_WEIGHTS['constraint_compliance']
    
    # Nullable constraint check
    if not metadata.nullable:
        if missing_count > 0:
            impact += CONFIDENCE_WEIGHTS['non_nullable_violation']
        else:
            impact += CONFIDENCE_WEIGHTS['constraint_compliance']
    
    # Data quality compliance
    non_null_data = data_series.dropna()
    if len(non_null_data) > 0:
        impact += _check_data_compliance(metadata, non_null_data)
    
    return impact


def _check_data_compliance(metadata: ColumnMetadata, non_null_data: pd.Series) -> float:
    """Check how well data complies with metadata constraints."""
    compliance_bonus = 0.0
    
    # Max length compliance
    if metadata.data_type in ["string", "categorical"] and metadata.max_length:
        max_actual_length = non_null_data.astype(str).str.len().max()
        if max_actual_length <= metadata.max_length:
            compliance_bonus += CONFIDENCE_WEIGHTS['constraint_compliance']
    
    # Allowed values compliance
    if metadata.data_type in ["categorical", "string"] and metadata.allowed_values:
        allowed_values = get_allowed_values_list(metadata)
        if allowed_values:
            valid_ratio = non_null_data.astype(str).isin(allowed_values).mean()
            compliance_bonus += valid_ratio * 0.1
    
    return compliance_bonus


def get_allowed_values_list(metadata: ColumnMetadata) -> list:
    """Parse allowed_values string into a list of valid values."""
    if not metadata.allowed_values:
        return []

    # Split by comma and clean up
    values = [v.strip() for v in str(metadata.allowed_values).split(",")]
    return [v for v in values if v]