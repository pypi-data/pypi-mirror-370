"""
Simple, intelligent imputation analysis for data science.
"""

__version__ = "1.5.2"
__author__ = "Rajesh Ramachander"

# Simple API for client applications
from .analyzer import (
    ImputationAnalyzer,
    analyze_imputation_requirements,
    analyze_dataframe,
)

# Metadata inference for auto-detection
from .metadata_inference import infer_metadata_from_dataframe

# Core models for advanced usage
from .models import ColumnMetadata, AnalysisConfig, ImputationSuggestion


__all__ = [
    # Simple API (recommended for most users)
    "analyze_imputation_requirements",
    "analyze_dataframe",
    "ImputationAnalyzer",
    # Metadata inference
    "infer_metadata_from_dataframe",
    # Core models
    "ColumnMetadata",
    "AnalysisConfig",
    "ImputationSuggestion",
]