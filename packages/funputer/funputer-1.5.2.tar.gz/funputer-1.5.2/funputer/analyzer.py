"""
Streamlined imputation analyzer - core business logic only.
Consolidated from simple_analyzer.py with all essential functionality.
"""

import time
import logging
from typing import List, Dict, Any, Union, Optional
import pandas as pd

from .models import ColumnMetadata, AnalysisConfig, ImputationSuggestion, MissingnessAnalysis, MissingnessType
from .io import load_data
from .exceptions import should_skip_column

logger = logging.getLogger(__name__)


def _analyze_missingness_mechanism(
    target_column: str,
    data: pd.DataFrame,
    metadata_dict: Dict[str, ColumnMetadata],
) -> MissingnessAnalysis:
    """
    Simplified missingness mechanism analysis that defaults to MCAR.
    
    Args:
        target_column: Name of the column to analyze
        data: Full dataset
        metadata_dict: Dictionary mapping column names to metadata

    Returns:
        MissingnessAnalysis object with results
    """
    target_series = data[target_column]
    missing_count = target_series.isna().sum()
    total_count = len(target_series)
    missing_percentage = missing_count / total_count if total_count > 0 else 0.0

    # If no missing values
    if missing_count == 0:
        return MissingnessAnalysis(
            missing_count=0,
            missing_percentage=0.0,
            mechanism=MissingnessType.MCAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="No missing values detected",
        )

    # Check if metadata explicitly indicates MAR through dependent_column
    target_metadata = metadata_dict.get(target_column)
    if target_metadata and target_metadata.dependent_column:
        dependent_col = target_metadata.dependent_column
        if dependent_col in data.columns and not data[dependent_col].isna().all():
            return MissingnessAnalysis(
                missing_count=missing_count,
                missing_percentage=missing_percentage,
                mechanism=MissingnessType.MAR,
                test_statistic=None,
                p_value=None,
                related_columns=[dependent_col],
                rationale=f"Metadata indicates dependency on '{dependent_col}' - classified as MAR",
            )

    # Default to MCAR for all other cases (simplified approach)
    return MissingnessAnalysis(
        missing_count=missing_count,
        missing_percentage=missing_percentage,
        mechanism=MissingnessType.MCAR,
        test_statistic=None,
        p_value=None,
        related_columns=[],
        rationale="Simplified analysis defaults to MCAR unless explicit dependency specified",
    )


class ImputationAnalyzer:
    """
    Streamlined imputation analyzer for intelligent missing data recommendations.
    
    Core functionality:
    - Intelligent imputation recommendations
    - Business rule integration
    - Simple, fast API
    """

    def __init__(self, config: AnalysisConfig = None):
        """Initialize analyzer with configuration."""
        self.config = config or AnalysisConfig()

    def _load_metadata(self, metadata_path: str) -> List[ColumnMetadata]:
        """Load metadata from file path."""
        from .io import load_metadata
        
        logger.info(f"Loading metadata: {metadata_path}")
        metadata = load_metadata(metadata_path, format_type="auto", validate_enterprise=False)
        return metadata

    def analyze(self, metadata_path: str, data_path: str) -> List[ImputationSuggestion]:
        """
        Analyze dataset and return imputation suggestions.

        Args:
            metadata_path: Path to metadata file (CSV or JSON format)
            data_path: Path to data CSV file

        Returns:
            List of ImputationSuggestion objects
        """
        logger.info(f"Analyzing dataset: {data_path}")
        start_time = time.time()
        
        # Load metadata and data
        metadata_list = self._load_metadata(metadata_path)
        metadata_dict = {meta.column_name: meta for meta in metadata_list}
        data = load_data(data_path, metadata_list)

        # Import analysis functions
        from .outliers import analyze_outliers
        from .proposal import propose_imputation_method
        
        # Analyze each column
        suggestions = []
        
        for metadata in metadata_list:
            column_name = metadata.column_name

            # Skip if column doesn't exist or should be skipped
            if column_name not in data.columns:
                logger.warning(f"Column {column_name} not found in data - skipping")
                continue

            if should_skip_column(column_name, self.config):
                logger.info(f"Skipping column {column_name} per configuration")
                continue

            # Analyze single column
            data_series = data[column_name]

            # Step 1: Outlier analysis
            outlier_analysis = analyze_outliers(data_series, metadata, self.config)

            # Step 2: Missingness mechanism analysis
            missingness_analysis = _analyze_missingness_mechanism(
                column_name, data, metadata_dict
            )

            # Step 3: Imputation method proposal
            imputation_proposal = propose_imputation_method(
                column_name,
                data_series,
                metadata,
                missingness_analysis,
                outlier_analysis,
                self.config,
                data,
                metadata_dict,
            )

            # Create suggestion
            suggestion = ImputationSuggestion(
                column_name=column_name,
                missing_count=missingness_analysis.missing_count,
                missing_percentage=missingness_analysis.missing_percentage,
                mechanism=missingness_analysis.mechanism.value,
                proposed_method=imputation_proposal.method.value,
                rationale=imputation_proposal.rationale,
                outlier_count=outlier_analysis.outlier_count,
                outlier_percentage=outlier_analysis.outlier_percentage,
                outlier_handling=outlier_analysis.handling_strategy.value,
                outlier_rationale=outlier_analysis.rationale,
                confidence_score=imputation_proposal.confidence_score,
            )

            suggestions.append(suggestion)

        duration = time.time() - start_time
        logger.info(f"Analysis completed in {duration:.2f}s - {len(suggestions)} suggestions")

        return suggestions

    def analyze_dataframe(
        self,
        data: pd.DataFrame,
        metadata: Union[List[ColumnMetadata], Dict[str, ColumnMetadata]] = None,
    ) -> List[ImputationSuggestion]:
        """
        Analyze DataFrame directly with metadata objects.

        Args:
            data: Pandas DataFrame to analyze
            metadata: List or dict of ColumnMetadata objects. If None, auto-infers metadata

        Returns:
            List of ImputationSuggestion objects
        """
        # Auto-infer metadata if not provided
        if metadata is None:
            from .metadata_inference import infer_metadata_from_dataframe
            logger.info("Auto-inferring metadata from DataFrame...")
            metadata = infer_metadata_from_dataframe(data, warn_user=False)
            
        logger.info(f"Analyzing DataFrame with {len(data)} rows, {len(data.columns)} columns")
        start_time = time.time()
        
        # Import analysis functions
        from .outliers import analyze_outliers
        from .proposal import propose_imputation_method

        # Normalize metadata to dict format
        if isinstance(metadata, list):
            metadata_dict = {meta.column_name: meta for meta in metadata}
            metadata_list = metadata
        else:
            metadata_dict = metadata
            metadata_list = list(metadata.values())
        
        # Analyze each column
        suggestions = []
        for meta in metadata_list:
            column_name = meta.column_name

            # Skip if column doesn't exist or should be skipped
            if column_name not in data.columns:
                logger.warning(f"Column {column_name} not found in data - skipping")
                continue

            if should_skip_column(column_name, self.config):
                logger.info(f"Skipping column {column_name} per configuration")
                continue

            # Analyze single column
            data_series = data[column_name]

            # Step 1: Outlier analysis
            outlier_analysis = analyze_outliers(data_series, meta, self.config)

            # Step 2: Missingness mechanism analysis
            missingness_analysis = _analyze_missingness_mechanism(
                column_name, data, metadata_dict
            )

            # Step 3: Imputation method proposal
            imputation_proposal = propose_imputation_method(
                column_name,
                data_series,
                meta,
                missingness_analysis,
                outlier_analysis,
                self.config,
                data,
                metadata_dict,
            )

            # Create suggestion
            suggestion = ImputationSuggestion(
                column_name=column_name,
                missing_count=missingness_analysis.missing_count,
                missing_percentage=missingness_analysis.missing_percentage,
                mechanism=missingness_analysis.mechanism.value,
                proposed_method=imputation_proposal.method.value,
                rationale=imputation_proposal.rationale,
                outlier_count=outlier_analysis.outlier_count,
                outlier_percentage=outlier_analysis.outlier_percentage,
                outlier_handling=outlier_analysis.handling_strategy.value,
                outlier_rationale=outlier_analysis.rationale,
                confidence_score=imputation_proposal.confidence_score,
            )

            suggestions.append(suggestion)

        duration = time.time() - start_time
        logger.info(f"DataFrame analysis completed in {duration:.2f}s - {len(suggestions)} suggestions")

        return suggestions


# Simple convenience functions for client applications
def analyze_imputation_requirements(
    data_path: Union[str, pd.DataFrame],
    metadata_path: Optional[str] = None,
    config: AnalysisConfig = None,
) -> List[ImputationSuggestion]:
    """
    Simple function to analyze imputation requirements with optional metadata.

    Args:
        data_path: Path to data CSV file OR pandas DataFrame
        metadata_path: Path to metadata file (optional - will auto-infer if not provided)
        config: Optional analysis configuration

    Returns:
        List of ImputationSuggestion objects
    """
    from .metadata_inference import infer_metadata_from_dataframe

    if metadata_path:
        # Use explicit metadata file
        analyzer = ImputationAnalyzer(config)
        return analyzer.analyze(metadata_path, data_path)
    else:
        # Auto-infer metadata from data
        if isinstance(data_path, pd.DataFrame):
            df = data_path
        else:
            try:
                df = pd.read_csv(data_path)
            except Exception as e:
                raise FileNotFoundError(f"Could not load data file {data_path}: {e}")

        inferred_metadata = infer_metadata_from_dataframe(df, warn_user=True)
        return analyze_dataframe(data=df, metadata=inferred_metadata, config=config)


def analyze_dataframe(
    data: pd.DataFrame,
    metadata: Union[List[ColumnMetadata], Dict[str, ColumnMetadata]] = None,
    config: AnalysisConfig = None,
) -> List[ImputationSuggestion]:
    """
    Simple function to analyze DataFrame directly.

    Args:
        data: Pandas DataFrame to analyze
        metadata: Column metadata (list or dict). If None, auto-infers metadata
        config: Optional analysis configuration

    Returns:
        List of ImputationSuggestion objects
    """
    if metadata is None:
        from .metadata_inference import infer_metadata_from_dataframe
        print("🤖 AUTO-INFERRING METADATA: No metadata provided. Using intelligent inference.")
        metadata = infer_metadata_from_dataframe(data, warn_user=False)
    
    analyzer = ImputationAnalyzer(config)
    return analyzer.analyze_dataframe(data, metadata)