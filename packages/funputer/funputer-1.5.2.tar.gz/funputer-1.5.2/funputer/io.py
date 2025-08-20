"""
Simplified I/O operations focusing on CSV support only.

Streamlined version with JSON format support removed and simplified validation.
"""

import pandas as pd
import yaml
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from .models import ColumnMetadata, AnalysisConfig, ImputationSuggestion
from .exceptions import ConfigurationError, MetadataValidationError
from pydantic import ValidationError


def load_metadata(
    metadata_path: str, format_type: str = "auto", validate_enterprise: bool = True
) -> List[ColumnMetadata]:
    """Load metadata from CSV file (JSON support removed)."""
    metadata_path = Path(metadata_path)
    
    if not metadata_path.exists():
        raise ValueError(f"Metadata file not found: {metadata_path}")
    
    # Only CSV format supported
    return _load_metadata_csv(str(metadata_path))


def _load_metadata_csv(metadata_path: str) -> List[ColumnMetadata]:
    """Load metadata from CSV file with simplified validation."""
    try:
        metadata_df = pd.read_csv(metadata_path)
    except Exception as e:
        raise ValueError(f"Failed to read metadata CSV: {e}")
    
    # Basic validation
    if metadata_df.empty:
        raise ValueError("Metadata CSV is empty")
    
    if 'column_name' not in metadata_df.columns:
        raise ValueError("Metadata CSV must contain 'column_name' column")
    
    # Convert to ColumnMetadata objects
    metadata_list = []
    for _, row in metadata_df.iterrows():
        try:
            metadata = _create_column_metadata(row, metadata_df.columns)
            metadata_list.append(metadata)
        except Exception as e:
            raise ValueError(f"Failed to create metadata for column '{row.get('column_name', 'unknown')}': {e}")
    
    return metadata_list


def get_column_metadata(
    metadata_list: List[ColumnMetadata], column_name: str
) -> Optional[ColumnMetadata]:
    """Get metadata for a specific column."""
    for metadata in metadata_list:
        if metadata.column_name == column_name:
            return metadata
    return None


def validate_metadata_against_data(
    metadata_list: List[ColumnMetadata], data_df: pd.DataFrame
) -> List[str]:
    """Validate metadata against actual data with simplified checks."""
    warnings = []
    
    # Check for missing columns in data
    metadata_columns = {m.column_name for m in metadata_list}
    data_columns = set(data_df.columns)
    
    missing_in_data = metadata_columns - data_columns
    if missing_in_data:
        warnings.append(f"Columns in metadata not found in data: {missing_in_data}")
    
    missing_in_metadata = data_columns - metadata_columns
    if missing_in_metadata:
        warnings.append(f"Columns in data not found in metadata: {missing_in_metadata}")
    
    return warnings


def load_configuration(config_path: Optional[str] = None) -> AnalysisConfig:
    """Load configuration from YAML file (JSON support removed)."""
    if config_path is None:
        return AnalysisConfig()
    
    try:
        config_dict = _load_config_file(config_path)
        _apply_env_overrides(config_dict)
        return AnalysisConfig(**config_dict)
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {e}")


def save_suggestions(
    suggestions: List[ImputationSuggestion], 
    output_path: str,
    sanitize_output: bool = True
) -> None:
    """
    Save imputation suggestions to CSV file with security sanitization.
    
    Args:
        suggestions: List of imputation suggestions
        output_path: Path to save CSV file
        sanitize_output: Enable output sanitization to prevent CSV injection
    """
    _ensure_dir_exists(output_path)
    
    # Convert to dictionaries for CSV output
    rows = [suggestion.to_dict() for suggestion in suggestions]
    df = pd.DataFrame(rows)
    
    # Sanitize output if enabled
    if sanitize_output:
        from .security import SecurityValidator
        validator = SecurityValidator()
        df = validator.sanitize_dataframe(df)
    
    df.to_csv(output_path, index=False)


def load_data(
    data_path: str, 
    metadata: List[ColumnMetadata],
    chunk_size: Optional[int] = None,
    sample_rows: Optional[int] = None,
    validate_security: bool = True
) -> Union[pd.DataFrame, pd.io.parsers.TextFileReader]:
    """
    Load data CSV file with optional chunked processing and security validation.
    
    Args:
        data_path: Path to the CSV file
        metadata: Column metadata for validation
        chunk_size: If provided, returns iterator for chunked processing
        sample_rows: If provided, only loads first N rows for sampling
        validate_security: Enable security validation (recommended)
        
    Returns:
        DataFrame if chunk_size is None, otherwise TextFileReader iterator
    """
    try:
        # Basic validation instead of security module
        if validate_security:
            # Simple path validation without full security module
            if not Path(data_path).exists():
                raise FileNotFoundError(f"Data file not found: {data_path}")
            if not Path(data_path).is_file():
                raise ValueError(f"Path is not a file: {data_path}")
        # Determine loading strategy based on parameters
        if chunk_size is not None:
            # Return chunked reader for large datasets
            chunk_reader = pd.read_csv(
                data_path, 
                chunksize=chunk_size,
                low_memory=True  # More memory efficient for chunks
            )
            
            # Validate first chunk if metadata provided
            if metadata:
                first_chunk = next(iter(pd.read_csv(data_path, chunksize=chunk_size, nrows=100)))
                warnings = validate_metadata_against_data(metadata, first_chunk)
                if warnings:
                    import logging
                    logger = logging.getLogger(__name__)
                    for warning in warnings:
                        logger.warning(warning)
            
            return chunk_reader
            
        elif sample_rows is not None:
            # Load only sample for metadata inference or testing
            data_df = pd.read_csv(data_path, nrows=sample_rows, low_memory=False)
        else:
            # Standard full loading
            data_df = pd.read_csv(data_path, low_memory=False)
        
        # Basic validation
        if data_df.empty:
            raise ValueError("Data file is empty")
        
        # Validate against metadata if provided
        if metadata:
            warnings = validate_metadata_against_data(metadata, data_df)
            if warnings:
                # Just log warnings, don't fail
                import logging
                logger = logging.getLogger(__name__)
                for warning in warnings:
                    logger.warning(warning)
        
        return data_df
        
    except Exception as e:
        raise ValueError(f"Failed to load data from {data_path}: {e}")


def _create_column_metadata(row: pd.Series, available_columns: pd.Index) -> ColumnMetadata:
    """Create ColumnMetadata from DataFrame row with simplified field mapping."""
    # Required fields
    column_name = str(row.get('column_name', ''))
    if not column_name:
        raise ValueError("column_name is required")
    
    data_type = str(row.get('data_type', 'string'))
    
    # Optional fields with defaults
    kwargs = {
        'column_name': column_name,
        'data_type': data_type,
        'description': str(row.get('description', f'Column: {column_name}')),
    }
    
    # Add optional fields if they exist in the CSV
    optional_fields = [
        'min_value', 'max_value', 'max_length', 'unique_flag', 'nullable',
        'dependent_column', 'allowed_values', 'role', 'do_not_impute',
        'sentinel_values', 'time_index', 'group_by', 'business_rule',
        'meaning_of_missing', 'dependency_rule', 'order_by', 'fallback_method',
        'policy_version'
    ]
    
    for field in optional_fields:
        if field in available_columns and pd.notna(row.get(field)):
            value = row[field]
            
            # Type conversion for specific fields
            if field in ['unique_flag', 'nullable', 'do_not_impute', 'time_index', 'group_by']:
                kwargs[field] = bool(value) if value in [True, False, 'True', 'False', 'TRUE', 'FALSE'] else bool(value)
            elif field in ['min_value', 'max_value']:
                try:
                    kwargs[field] = float(value) if value != '' else None
                except (ValueError, TypeError):
                    kwargs[field] = None
            elif field == 'max_length':
                try:
                    kwargs[field] = int(value) if value != '' else None
                except (ValueError, TypeError):
                    kwargs[field] = None
            else:
                kwargs[field] = str(value) if value != '' else None
    
    try:
        return ColumnMetadata(**kwargs)
    except ValidationError as e:
        raise ValueError(f"Validation error for column '{column_name}': {e}")


def _load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file only."""
    config_path_obj = Path(config_path)
    
    if not config_path_obj.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r") as f:
        if config_path.endswith(".yaml") or config_path.endswith(".yml"):
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration format. Only YAML files are supported: {config_path}")


def _apply_env_overrides(config_dict: Dict[str, Any]) -> None:
    """Apply environment variable overrides to configuration."""
    # Simple environment overrides for common settings
    env_mappings = {
        'FUNPUTER_OUTPUT_PATH': 'output_path',
        'FUNPUTER_SKIP_COLUMNS': 'skip_columns',
        'FUNPUTER_MISSING_THRESHOLD': 'missing_threshold',
        'FUNPUTER_OUTLIER_THRESHOLD': 'outlier_threshold'
    }
    
    for env_var, config_key in env_mappings.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            # Type conversion
            if config_key in ['missing_threshold', 'outlier_threshold']:
                config_dict[config_key] = float(value)
            elif config_key == 'skip_columns':
                config_dict[config_key] = [col.strip() for col in value.split(',')]
            else:
                config_dict[config_key] = value


def _ensure_dir_exists(file_path: str) -> None:
    """Ensure directory exists for the given file path."""
    directory = Path(file_path).parent
    directory.mkdir(parents=True, exist_ok=True)