"""
Tests for core models and data structures.
"""

import pytest
from pydantic import ValidationError

from funputer.models import (
    ColumnMetadata,
    AnalysisConfig,
    ImputationSuggestion,
    DataType,
    MissingnessType,
    ImputationMethod,
    OutlierHandling,
    OutlierAnalysis,
    MissingnessAnalysis,
    ImputationProposal,
)


class TestColumnMetadata:
    """Test ColumnMetadata dataclass."""

    def test_basic_creation(self):
        """Test basic ColumnMetadata creation."""
        meta = ColumnMetadata("age", "integer")
        assert meta.column_name == "age"
        assert meta.data_type == "integer"
        assert meta.min_value is None
        assert meta.max_value is None
        assert meta.unique_flag is False
        assert meta.nullable is True

    def test_full_creation(self):
        """Test ColumnMetadata creation with all available fields."""
        meta = ColumnMetadata(
            column_name="user_id",
            data_type="integer",
            min_value=1,
            max_value=999999,
            max_length=None,
            unique_flag=True,
            nullable=False,
            description="User identifier",
            dependent_column="account_id",
            allowed_values="1,2,3,4,5",
            sentinel_values="-999,-99",
        )

        assert meta.column_name == "user_id"
        assert meta.data_type == "integer"
        assert meta.min_value == 1
        assert meta.max_value == 999999
        assert meta.unique_flag is True
        assert meta.nullable is False
        assert meta.description == "User identifier"
        assert meta.dependent_column == "account_id"
        assert meta.allowed_values == "1,2,3,4,5"
        assert meta.sentinel_values == "-999,-99"


class TestAnalysisConfig:
    """Test AnalysisConfig validation and defaults."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AnalysisConfig()
        assert config.iqr_multiplier == 1.5
        assert config.outlier_threshold == 0.05
        assert config.correlation_threshold == 0.3
        assert config.chi_square_alpha == 0.05
        assert config.point_biserial_threshold == 0.2
        assert config.skewness_threshold == 2.0
        assert config.missing_threshold == 0.8
        assert config.skip_columns == []
        assert config.output_path == "imputation_suggestions.csv"

    def test_custom_config(self):
        """Test custom configuration values."""
        config = AnalysisConfig(
            iqr_multiplier=2.0,
            outlier_percentage_threshold=0.1,
            correlation_threshold=0.5,
            skip_columns=["col1", "col2"],
        )
        assert config.iqr_multiplier == 2.0
        assert config.outlier_threshold == 0.1
        assert config.correlation_threshold == 0.5
        assert config.skip_columns == ["col1", "col2"]

    def test_config_validation_iqr_multiplier(self):
        """Test IQR multiplier validation."""
        # Valid values
        AnalysisConfig(iqr_multiplier=1.0)
        AnalysisConfig(iqr_multiplier=3.0)

        # Invalid values
        with pytest.raises(ValidationError):
            AnalysisConfig(iqr_multiplier=0.0)

        with pytest.raises(ValidationError):
            AnalysisConfig(iqr_multiplier=-1.0)

    def test_config_validation_thresholds(self):
        """Test threshold validation."""
        # Valid thresholds
        AnalysisConfig(outlier_percentage_threshold=0.01)
        AnalysisConfig(correlation_threshold=0.9)
        AnalysisConfig(missing_percentage_threshold=0.95)

        # Invalid thresholds
        with pytest.raises(ValidationError):
            AnalysisConfig(outlier_percentage_threshold=1.5)  # > 0.5

        with pytest.raises(ValidationError):
            AnalysisConfig(correlation_threshold=1.5)  # > 0.9

    def test_config_alias_support(self):
        """Test that aliases work correctly."""
        config = AnalysisConfig(
            outlier_percentage_threshold=0.1, missing_percentage_threshold=0.9
        )
        assert config.outlier_threshold == 0.1
        assert config.missing_threshold == 0.9


class TestEnums:
    """Test enum definitions."""

    def test_data_type_enum(self):
        """Test DataType enum values."""
        assert DataType.INTEGER.value == "integer"
        assert DataType.FLOAT.value == "float"
        assert DataType.STRING.value == "string"
        assert DataType.CATEGORICAL.value == "categorical"
        assert DataType.BOOLEAN.value == "boolean"
        assert DataType.DATETIME.value == "datetime"

    def test_missingness_type_enum(self):
        """Test MissingnessType enum values."""
        assert MissingnessType.MCAR.value == "MCAR"
        assert MissingnessType.MAR.value == "MAR"
        assert MissingnessType.MNAR.value == "MNAR"
        assert MissingnessType.UNKNOWN.value == "Unknown"

    def test_imputation_method_enum(self):
        """Test ImputationMethod enum values."""
        assert ImputationMethod.MEAN.value == "Mean"
        assert ImputationMethod.MEDIAN.value == "Median"
        assert ImputationMethod.MODE.value == "Mode"
        assert ImputationMethod.REGRESSION.value == "Regression"
        assert ImputationMethod.KNN.value == "kNN"
        assert ImputationMethod.BUSINESS_RULE.value == "Business Rule"
        assert ImputationMethod.FORWARD_FILL.value == "Forward Fill"
        assert ImputationMethod.NO_ACTION_NEEDED.value == "No action needed"

    def test_outlier_handling_enum(self):
        """Test OutlierHandling enum values."""
        assert OutlierHandling.CAP_TO_BOUNDS.value == "Cap to bounds"
        assert OutlierHandling.CONVERT_TO_NAN.value == "Convert to NaN"
        assert OutlierHandling.LEAVE_AS_IS.value == "Leave as is"
        assert OutlierHandling.REMOVE_ROWS.value == "Remove rows"


class TestOutlierAnalysis:
    """Test OutlierAnalysis model."""

    def test_outlier_analysis_creation(self):
        """Test OutlierAnalysis model creation."""
        analysis = OutlierAnalysis(
            outlier_count=5,
            outlier_percentage=0.05,
            lower_bound=10.0,
            upper_bound=90.0,
            outlier_values=[1, 2, 95, 98, 99],
            handling_strategy=OutlierHandling.CAP_TO_BOUNDS,
            rationale="Low outlier percentage - cap to bounds",
        )

        assert analysis.outlier_count == 5
        assert analysis.outlier_percentage == 0.05
        assert analysis.lower_bound == 10.0
        assert analysis.upper_bound == 90.0
        assert len(analysis.outlier_values) == 5
        assert analysis.handling_strategy == OutlierHandling.CAP_TO_BOUNDS
        assert "cap to bounds" in analysis.rationale.lower()


class TestMissingnessAnalysis:
    """Test MissingnessAnalysis model."""

    def test_missingness_analysis_creation(self):
        """Test MissingnessAnalysis model creation."""
        analysis = MissingnessAnalysis(
            missing_count=10,
            missing_percentage=0.1,
            mechanism=MissingnessType.MAR,
            test_statistic=2.5,
            p_value=0.01,
            related_columns=["age", "income"],
            rationale="Significant correlation with age and income",
        )

        assert analysis.missing_count == 10
        assert analysis.missing_percentage == 0.1
        assert analysis.mechanism == MissingnessType.MAR
        assert analysis.test_statistic == 2.5
        assert analysis.p_value == 0.01
        assert analysis.related_columns == ["age", "income"]
        assert "correlation" in analysis.rationale.lower()


class TestImputationProposal:
    """Test ImputationProposal model."""

    def test_imputation_proposal_creation(self):
        """Test ImputationProposal model creation."""
        proposal = ImputationProposal(
            method=ImputationMethod.MEAN,
            rationale="Numeric data with low skewness",
            parameters={"strategy": "mean"},
            confidence_score=0.8,
        )

        assert proposal.method == ImputationMethod.MEAN
        assert "numeric" in proposal.rationale.lower()
        assert proposal.parameters["strategy"] == "mean"
        assert proposal.confidence_score == 0.8

    def test_imputation_proposal_validation(self):
        """Test ImputationProposal validation."""
        # Valid confidence score
        ImputationProposal(
            method=ImputationMethod.MEDIAN,
            rationale="Test",
            parameters={},
            confidence_score=0.5,
        )

        # Edge case confidence scores should be allowed
        ImputationProposal(
            method=ImputationMethod.MODE,
            rationale="Test",
            parameters={},
            confidence_score=0.0,
        )

        ImputationProposal(
            method=ImputationMethod.KNN,
            rationale="Test",
            parameters={},
            confidence_score=1.0,
        )


class TestImputationSuggestion:
    """Test ImputationSuggestion model."""

    def test_suggestion_creation(self):
        """Test ImputationSuggestion creation with defaults."""
        suggestion = ImputationSuggestion(
            column_name="age",
            proposed_method="Mean",
            rationale="Numeric data with low skewness",
        )

        assert suggestion.column_name == "age"
        assert suggestion.missing_count == 0
        assert suggestion.missing_percentage == 0.0
        assert suggestion.mechanism == "UNKNOWN"
        assert suggestion.proposed_method == "Mean"
        assert suggestion.rationale == "Numeric data with low skewness"
        assert suggestion.confidence_score == 0.0

    def test_suggestion_full_creation(self):
        """Test ImputationSuggestion creation with all fields."""
        suggestion = ImputationSuggestion(
            column_name="income",
            missing_count=15,
            missing_percentage=0.15,
            mechanism="MAR",
            proposed_method="Regression",
            rationale="Correlated with age and education",
            outlier_count=3,
            outlier_percentage=0.03,
            outlier_handling="Cap to bounds",
            outlier_rationale="Low outlier percentage",
            confidence_score=0.85,
        )

        assert suggestion.column_name == "income"
        assert suggestion.missing_count == 15
        assert suggestion.missing_percentage == 0.15
        assert suggestion.mechanism == "MAR"
        assert suggestion.proposed_method == "Regression"
        assert suggestion.outlier_count == 3
        assert suggestion.confidence_score == 0.85

    def test_suggestion_to_dict(self):
        """Test ImputationSuggestion to_dict conversion."""
        suggestion = ImputationSuggestion(
            column_name="score",
            missing_count=8,
            missing_percentage=0.08,
            mechanism="MCAR",
            proposed_method="Median",
            rationale="High skewness detected",
            confidence_score=0.75,
        )

        result_dict = suggestion.to_dict()

        assert result_dict["Column"] == "score"
        assert result_dict["Missing_Count"] == 8
        assert result_dict["Missing_Percentage"] == "0.1%"
        assert result_dict["Missingness_Mechanism"] == "MCAR"
        assert result_dict["Proposed_Method"] == "Median"
        assert result_dict["Rationale"] == "High skewness detected"
        assert result_dict["Confidence_Score"] == "0.750"

        # Test percentage formatting
        assert "%" in result_dict["Missing_Percentage"]
        assert "%" in result_dict["Outlier_Percentage"]

    def test_suggestion_dict_formatting(self):
        """Test proper formatting in to_dict method."""
        suggestion = ImputationSuggestion(
            column_name="test",
            missing_percentage=12.345,  # Percentage as 12.345%
            outlier_percentage=6.789,  # Percentage as 6.789%
            confidence_score=0.87654,
            proposed_method="Test",
            rationale="Test rationale",
        )

        result_dict = suggestion.to_dict()

        # Test precision formatting
        assert result_dict["Missing_Percentage"] == "12.3%"
        assert result_dict["Outlier_Percentage"] == "6.8%"
        assert result_dict["Confidence_Score"] == "0.877"
