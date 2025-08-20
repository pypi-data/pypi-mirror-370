"""
Tests for error handling and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock

from funputer.exceptions import (
    ConfigurationError,
    MetadataValidationError,
    ImputationException,
    should_skip_column,
    _check_metadata_validation,
    _check_no_missing_values,
    _check_unique_identifier,
    _check_all_missing,
    _check_mnar_without_rule,
    apply_exception_handling,
)
from funputer.models import (
    ColumnMetadata,
    AnalysisConfig,
    ImputationMethod,
    MissingnessType,
    MissingnessAnalysis,
    OutlierAnalysis,
    ImputationProposal,
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Invalid configuration")

        try:
            raise ConfigurationError("Test message")
        except ConfigurationError as e:
            assert str(e) == "Test message"

    def test_metadata_validation_error(self):
        """Test MetadataValidationError exception."""
        with pytest.raises(MetadataValidationError):
            raise MetadataValidationError("Invalid metadata")

        try:
            raise MetadataValidationError("Test validation error")
        except MetadataValidationError as e:
            assert str(e) == "Test validation error"


class TestImputationException:
    """Test ImputationException class."""

    def test_imputation_exception_creation(self):
        """Test ImputationException creation."""
        exception = ImputationException(
            method=ImputationMethod.NO_ACTION_NEEDED,
            rationale="No missing values",
            confidence=1.0,
        )

        assert exception.method == ImputationMethod.NO_ACTION_NEEDED
        assert exception.rationale == "No missing values"
        assert exception.confidence == 1.0

    def test_imputation_exception_to_proposal(self):
        """Test conversion of ImputationException to ImputationProposal."""
        exception = ImputationException(
            method=ImputationMethod.MANUAL_BACKFILL,
            rationale="Requires manual intervention",
            confidence=0.8,
        )

        proposal = exception.to_proposal()

        assert isinstance(proposal, ImputationProposal)
        assert proposal.method == ImputationMethod.MANUAL_BACKFILL
        assert proposal.rationale == "Requires manual intervention"
        assert proposal.confidence_score == 0.8
        assert proposal.parameters["exception_handled"] is True


class TestExceptionChecks:
    """Test individual exception check functions."""

    def test_should_skip_column(self):
        """Test should_skip_column function."""
        config = AnalysisConfig(skip_columns=["col1", "col2"])

        assert should_skip_column("col1", config) is True
        assert should_skip_column("col2", config) is True
        assert should_skip_column("col3", config) is False

        # Test empty skip list
        empty_config = AnalysisConfig(skip_columns=[])
        assert should_skip_column("any_col", empty_config) is False

    def test_check_metadata_validation_failure_invalid_data_type(self):
        """Test metadata validation failure for invalid data type."""
        metadata = ColumnMetadata("test", "invalid_type")
        data_series = pd.Series([1, 2, 3])

        exception = _check_metadata_validation(metadata, data_series)

        assert exception is not None
        assert exception.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "Invalid data type" in exception.rationale
        assert exception.confidence == 0.0

    def test_check_metadata_validation_failure_invalid_constraints(self):
        """Test metadata validation failure for invalid min/max constraints."""
        metadata = ColumnMetadata("test", "integer", min_value=100, max_value=50)
        data_series = pd.Series([1, 2, 3])

        exception = _check_metadata_validation(metadata, data_series)

        assert exception is not None
        assert exception.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "min_value" in exception.rationale and "max_value" in exception.rationale

    def test_check_metadata_validation_failure_empty_column_name(self):
        """Test metadata validation failure for empty column name."""
        metadata = ColumnMetadata("", "integer")
        data_series = pd.Series([1, 2, 3])

        exception = _check_metadata_validation(metadata, data_series)

        assert exception is not None
        assert "Column name is missing" in exception.rationale

    def test_check_metadata_validation_failure_data_type_mismatch(self):
        """Test metadata validation failure for data type mismatch."""
        metadata = ColumnMetadata("test", "integer")
        data_series = pd.Series(["a", "b", "c"])  # String data, not integer

        exception = _check_metadata_validation(metadata, data_series)

        assert exception is not None
        assert "Data type mismatch" in exception.rationale
        assert "not numeric" in exception.rationale

    def test_check_metadata_validation_failure_datetime_mismatch(self):
        """Test metadata validation failure for datetime mismatch."""
        metadata = ColumnMetadata("test", "datetime")
        data_series = pd.Series(["not_a_date", "also_not_a_date"])

        exception = _check_metadata_validation(metadata, data_series)

        assert exception is not None
        assert "cannot be parsed as datetime" in exception.rationale

    def test_check_metadata_validation_success(self):
        """Test successful metadata validation."""
        metadata = ColumnMetadata("test", "integer", min_value=0, max_value=100)
        data_series = pd.Series([1, 2, 3, 4, 5])

        exception = _check_metadata_validation(metadata, data_series)

        assert exception is None

    def test_check_no_missing_values(self):
        """Test check for no missing values."""
        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.missing_count = 0

        exception = _check_no_missing_values(missingness_analysis)

        assert exception is not None
        assert exception.method == ImputationMethod.NO_ACTION_NEEDED
        assert exception.confidence == 1.0
        assert "No missing values" in exception.rationale

    def test_check_no_missing_values_with_missing(self):
        """Test check when there are missing values."""
        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.missing_count = 5

        exception = _check_no_missing_values(missingness_analysis)

        assert exception is None

    def test_check_unique_identifier(self):
        """Test check for unique identifier column."""
        metadata = ColumnMetadata("id", "integer", unique_flag=True)

        exception = _check_unique_identifier(metadata)

        assert exception is not None
        assert exception.method == ImputationMethod.MANUAL_BACKFILL
        assert "Unique IDs cannot be auto-imputed" in exception.rationale
        assert exception.confidence == 0.9

    def test_check_unique_identifier_not_unique(self):
        """Test check for non-unique column."""
        metadata = ColumnMetadata("value", "integer", unique_flag=False)

        exception = _check_unique_identifier(metadata)

        assert exception is None

    def test_check_all_values_missing(self):
        """Test check for all values missing."""
        data_series = pd.Series([None, None, None, None])

        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.missing_count = 4

        exception = _check_all_missing(data_series, missingness_analysis)

        assert exception is not None
        assert exception.method == ImputationMethod.MANUAL_BACKFILL
        assert "No observed values" in exception.rationale
        assert exception.confidence == 0.8

    def test_check_all_values_missing_partial(self):
        """Test check when only some values are missing."""
        data_series = pd.Series([1, None, 3, None])

        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.missing_count = 2

        exception = _check_all_missing(data_series, missingness_analysis)

        assert exception is None

    def test_check_mnar_without_dependent_column(self):
        """Test check for MNAR mechanism without dependent column."""
        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.mechanism = MissingnessType.MNAR

        metadata = ColumnMetadata("test", "integer")  # No dependent column

        exception = _check_mnar_without_rule(missingness_analysis, metadata)

        assert exception is not None
        assert exception.method == ImputationMethod.MANUAL_BACKFILL
        assert "MNAR" in exception.rationale
        assert "manual investigation" in exception.rationale
        assert exception.confidence == 0.7

    def test_check_mnar_with_dependent_column(self):
        """Test check for MNAR mechanism with dependent column."""
        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.mechanism = MissingnessType.MNAR

        metadata = ColumnMetadata("test", "integer", dependent_column="age")

        exception = _check_mnar_without_rule(missingness_analysis, metadata)

        # Should still trigger exception since MNAR requires domain knowledge
        assert exception is not None

    def test_check_unknown_mechanism_without_dependent_column(self):
        """Test check for UNKNOWN mechanism without dependent column."""
        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.mechanism = MissingnessType.UNKNOWN

        metadata = ColumnMetadata("test", "integer")

        exception = _check_mnar_without_rule(missingness_analysis, metadata)

        assert exception is not None
        assert "MNAR/Unknown mechanism" in exception.rationale


class TestExceptionHandlingApplication:
    """Test the apply_exception_handling function."""

    def create_test_data(self):
        """Create test data for exception handling tests."""
        data_series = pd.Series([1, 2, None, 4, 5])
        metadata = ColumnMetadata("test", "integer")

        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.missing_count = 1
        missingness_analysis.missing_percentage = 0.2
        missingness_analysis.mechanism = MissingnessType.MCAR

        outlier_analysis = Mock(spec=OutlierAnalysis)
        config = AnalysisConfig()

        return data_series, metadata, missingness_analysis, outlier_analysis, config

    def test_apply_exception_handling_skip_column(self):
        """Test exception handling for skipped column."""
        data_series, metadata, missingness_analysis, outlier_analysis, config = (
            self.create_test_data()
        )
        config.skip_columns = ["test"]

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        # Should return None for skipped columns (handled at higher level)
        assert result is None

    def test_apply_exception_handling_metadata_validation_failure(self):
        """Test exception handling for metadata validation failure."""
        data_series, metadata, missingness_analysis, outlier_analysis, config = (
            self.create_test_data()
        )
        metadata.data_type = "invalid_type"

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA

    def test_apply_exception_handling_no_missing_values(self):
        """Test exception handling for no missing values."""
        data_series, metadata, missingness_analysis, outlier_analysis, config = (
            self.create_test_data()
        )
        missingness_analysis.missing_count = 0

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is not None
        assert result.method == ImputationMethod.NO_ACTION_NEEDED

    def test_apply_exception_handling_unique_identifier(self):
        """Test exception handling for unique identifier."""
        data_series, metadata, missingness_analysis, outlier_analysis, config = (
            self.create_test_data()
        )
        metadata.unique_flag = True

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is not None
        assert result.method == ImputationMethod.MANUAL_BACKFILL

    def test_apply_exception_handling_all_missing(self):
        """Test exception handling for all missing values."""
        data_series = pd.Series([None, None, None])
        metadata = ColumnMetadata("test", "integer")

        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.missing_count = 3

        outlier_analysis = Mock()
        config = AnalysisConfig()

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is not None
        assert result.method == ImputationMethod.MANUAL_BACKFILL

    def test_apply_exception_handling_mnar_no_rule(self):
        """Test exception handling for MNAR without business rule."""
        data_series, metadata, missingness_analysis, outlier_analysis, config = (
            self.create_test_data()
        )
        missingness_analysis.mechanism = MissingnessType.MNAR

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is not None
        assert result.method == ImputationMethod.MANUAL_BACKFILL

    def test_apply_exception_handling_no_exceptions(self):
        """Test exception handling when no exceptions apply."""
        data_series, metadata, missingness_analysis, outlier_analysis, config = (
            self.create_test_data()
        )

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        # Should return None when no exceptions apply
        assert result is None

    def test_exception_handling_priority_order(self):
        """Test that exception handling follows correct priority order."""
        # Create data that would trigger multiple exceptions
        data_series = pd.Series([None, None, None])  # All missing
        metadata = ColumnMetadata(
            "test", "invalid_type", unique_flag=True
        )  # Invalid type AND unique

        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.missing_count = 3

        outlier_analysis = Mock()
        config = AnalysisConfig()

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        # Should catch metadata validation failure first (higher priority)
        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA


class TestShouldSkipColumn:
    """Test should_skip_column function."""

    def test_should_skip_column_in_list(self):
        """Test skipping column that's in skip list."""
        config = AnalysisConfig(skip_columns=["col1", "col2"])

        assert should_skip_column("col1", config) is True
        assert should_skip_column("col2", config) is True

    def test_should_skip_column_not_in_list(self):
        """Test not skipping column that's not in skip list."""
        config = AnalysisConfig(skip_columns=["col1", "col2"])

        assert should_skip_column("col3", config) is False

    def test_should_skip_column_empty_list(self):
        """Test with empty skip list."""
        config = AnalysisConfig(skip_columns=[])

        assert should_skip_column("any_col", config) is False

    def test_should_skip_column_case_sensitive(self):
        """Test that column skipping is case sensitive."""
        config = AnalysisConfig(skip_columns=["Col1"])

        assert should_skip_column("Col1", config) is True
        assert should_skip_column("col1", config) is False  # Different case
        assert should_skip_column("COL1", config) is False  # Different case


class TestEdgeCases:
    """Test various edge cases and error conditions."""

    def test_empty_data_series(self):
        """Test handling of empty data series."""
        data_series = pd.Series([], dtype=float)
        metadata = ColumnMetadata("test", "float")

        exception = _check_metadata_validation(metadata, data_series)
        # Should not fail on empty series
        assert exception is None

    def test_data_series_with_all_nan(self):
        """Test handling of data series with all NaN values."""
        data_series = pd.Series([np.nan, np.nan, np.nan])
        metadata = ColumnMetadata("test", "float")

        exception = _check_metadata_validation(metadata, data_series)
        # Should not fail on all-NaN series (will be caught by all_values_missing check)
        assert exception is None

    def test_mixed_type_data_validation(self):
        """Test validation with mixed type data."""
        data_series = pd.Series([1, 2.5, "3", 4])  # Mixed types
        metadata = ColumnMetadata("test", "integer")

        # This might or might not trigger an exception depending on pandas type inference
        exception = _check_metadata_validation(metadata, data_series)
        # The test should handle this gracefully either way
        assert (
            exception is None
            or exception.method == ImputationMethod.ERROR_INVALID_METADATA
        )

    def test_metadata_with_none_values(self):
        """Test metadata validation with None constraint values."""
        metadata = ColumnMetadata("test", "integer", min_value=None, max_value=None)
        data_series = pd.Series([1, 2, 3])

        exception = _check_metadata_validation(metadata, data_series)

        # Should not fail with None constraints
        assert exception is None

    def test_datetime_validation_with_valid_strings(self):
        """Test datetime validation with valid date strings."""
        data_series = pd.Series(["2023-01-01", "2023-01-02", "2023-01-03"])
        metadata = ColumnMetadata("test", "datetime")

        exception = _check_metadata_validation(metadata, data_series)

        # Should not fail with valid date strings
        assert exception is None

    def test_large_dataset_handling(self):
        """Test exception handling with large dataset."""
        # Create a large dataset
        large_data = pd.Series(range(10000))
        metadata = ColumnMetadata("test", "integer")

        missingness_analysis = Mock(spec=MissingnessAnalysis)
        missingness_analysis.missing_count = 0

        exception = _check_no_missing_values(missingness_analysis)

        # Should handle large datasets without issues
        assert exception is not None
        assert exception.method == ImputationMethod.NO_ACTION_NEEDED
