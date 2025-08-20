"""
Automatic metadata inference from pandas DataFrames.

Simplified functional approach for intelligent column metadata detection
when no explicit metadata file is provided.
"""

import pandas as pd
import numpy as np
import logging
import warnings
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import re

from .models import ColumnMetadata, FIELD_DEFAULTS

# Suppress pandas warnings for cleaner output
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)
warnings.filterwarnings("ignore", message="Could not infer format")
warnings.filterwarnings("ignore", message=".*falling back to `dateutil`.*")

logger = logging.getLogger(__name__)


# Configuration constants
CATEGORICAL_THRESHOLD_RATIO = 0.1
CATEGORICAL_THRESHOLD_ABSOLUTE = 50
DATETIME_SAMPLE_SIZE = 100
MIN_ROWS_FOR_STATS = 10
MIN_UNIQUE_THRESHOLD = 20
SEQUENTIAL_ID_THRESHOLD = 0.8

# Pattern recognition constants
DATETIME_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
    r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
    r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
    r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
]

ID_INDICATORS = ["id", "key", "pk", "uuid", "guid", "_id", "identifier"]
TIME_INDICATORS = ["time", "date", "timestamp", "created", "updated", "modified"]
GROUP_INDICATORS = ["category", "group", "type", "class", "status", "state", "region", "department"]


def infer_metadata_from_dataframe(
    df: pd.DataFrame, warn_user: bool = True, **kwargs
) -> List[ColumnMetadata]:
    """
    Infer metadata for all columns in a DataFrame.
    
    Args:
        df: Input DataFrame
        warn_user: Whether to warn user about inference limitations
        **kwargs: Additional arguments (maintained for compatibility)
        
    Returns:
        List of ColumnMetadata objects
    """
    if df.empty:
        logger.warning("Empty DataFrame provided - no metadata to infer")
        return []

    if warn_user:
        logger.info(f"Inferring metadata for {len(df.columns)} columns from {len(df)} rows")

    metadata_list = []
    
    for column_name in df.columns:
        try:
            metadata = _infer_column_metadata(df, column_name)
            metadata_list.append(metadata)
        except Exception as e:
            logger.warning(f"Failed to infer metadata for column '{column_name}': {e}")
            # Create fallback metadata
            metadata = ColumnMetadata(
                column_name=column_name,
                data_type='string',
                description=f'Failed inference for {column_name}'
            )
            metadata_list.append(metadata)

    if warn_user and metadata_list:
        logger.info(f"Successfully inferred metadata for {len(metadata_list)} columns")

    return metadata_list


def _infer_column_metadata(df: pd.DataFrame, column_name: str) -> ColumnMetadata:
    """Infer metadata for a single column."""
    column_data = df[column_name]
    
    # Basic data type inference
    data_type = _infer_data_type(column_data)
    
    # Constraints and properties
    constraints = _infer_constraints(column_data, data_type)
    
    # Column characteristics
    unique_flag = _infer_uniqueness(column_data)
    role = _infer_role(column_name, column_data, unique_flag)
    
    # Infer other boolean flags
    do_not_impute = _infer_do_not_impute(role, unique_flag)
    time_index = _infer_time_index(column_name, data_type)
    group_by = _infer_group_by(column_name, data_type, column_data)
    
    # Create metadata object
    return ColumnMetadata(
        column_name=column_name,
        data_type=data_type,
        description=_generate_description(column_name, data_type),
        role=role,
        do_not_impute=do_not_impute,
        time_index=time_index,
        group_by=group_by,
        unique_flag=unique_flag,
        nullable=True,  # Default to nullable
        **constraints
    )


def _infer_data_type(column_data: pd.Series) -> str:
    """Infer the data type of a column."""
    # Handle empty or all-null columns
    if column_data.isna().all():
        return 'string'
    
    # Get pandas dtype
    dtype = column_data.dtype
    
    # Numeric types
    if pd.api.types.is_integer_dtype(dtype):
        return 'integer'
    elif pd.api.types.is_float_dtype(dtype):
        return 'float'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'boolean'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'datetime'
    
    # Object dtype - need deeper analysis
    if dtype == 'object':
        return _infer_object_type(column_data)
    
    # Default fallback
    return 'string'


def _infer_object_type(column_data: pd.Series) -> str:
    """Infer type for object columns."""
    non_null = column_data.dropna()
    
    if len(non_null) == 0:
        return 'string'
    
    # Try datetime detection
    if _is_datetime_column(non_null):
        return 'datetime'
    
    # Try boolean detection
    if _is_boolean_column(non_null):
        return 'boolean'
    
    # Try integer detection
    if _could_be_integer(non_null):
        return 'integer'
    
    # Check if categorical
    if _is_categorical_column(non_null):
        return 'categorical'
    
    return 'string'


def _is_datetime_column(column_data: pd.Series) -> bool:
    """Check if column contains datetime values."""
    if len(column_data) == 0:
        return False
        
    sample_size = min(DATETIME_SAMPLE_SIZE, len(column_data))
    sample = column_data.head(sample_size).astype(str)
    
    # Check for common datetime patterns
    datetime_count = 0
    for value in sample:
        if any(re.search(pattern, str(value)) for pattern in DATETIME_PATTERNS):
            datetime_count += 1
    
    # If most values match datetime patterns, it's likely datetime
    return datetime_count / len(sample) > 0.7


def _is_boolean_column(column_data: pd.Series) -> bool:
    """Check if column contains boolean-like values."""
    unique_values = set(str(v).lower() for v in column_data.unique())
    boolean_values = {'true', 'false', '0', '1', 'yes', 'no', 'y', 'n'}
    
    return unique_values.issubset(boolean_values) and len(unique_values) <= 4


def _could_be_integer(column_data: pd.Series) -> bool:
    """Check if string column could be integer."""
    try:
        # Try to convert sample to numeric
        sample = column_data.head(100)
        converted = pd.to_numeric(sample, errors='coerce')
        
        # Check if conversion was successful and values are integers
        if converted.notna().sum() / len(sample) > 0.8:
            return (converted == converted.astype('Int64')).all()
    except:
        pass
    
    return False


def _is_categorical_column(column_data: pd.Series) -> bool:
    """Check if column should be treated as categorical."""
    unique_count = column_data.nunique()
    total_count = len(column_data)
    
    if total_count == 0:
        return False
    
    # Low unique ratio suggests categorical
    unique_ratio = unique_count / total_count
    
    return (unique_ratio <= CATEGORICAL_THRESHOLD_RATIO or 
            unique_count <= CATEGORICAL_THRESHOLD_ABSOLUTE)


def _infer_constraints(column_data: pd.Series, data_type: str) -> Dict:
    """Infer value constraints for the column."""
    constraints = {}
    
    if data_type in ['integer', 'float']:
        non_null = column_data.dropna()
        if len(non_null) > 0:
            constraints['min_value'] = float(non_null.min())
            constraints['max_value'] = float(non_null.max())
    
    elif data_type == 'string':
        non_null = column_data.dropna().astype(str)
        if len(non_null) > 0:
            constraints['max_length'] = int(non_null.str.len().max())
    
    elif data_type == 'categorical':
        # For categorical data, store allowed values
        unique_vals = column_data.dropna().unique()
        if len(unique_vals) <= 20:  # Only for manageable number of values
            constraints['allowed_values'] = ','.join(str(v) for v in sorted(unique_vals))
    
    return constraints


def _infer_uniqueness(column_data: pd.Series) -> bool:
    """Check if column values should be unique."""
    non_null = column_data.dropna()
    
    if len(non_null) < 2:
        return False
    
    unique_ratio = non_null.nunique() / len(non_null)
    return unique_ratio > 0.95  # 95% unique suggests it should be unique


def _infer_role(column_name: str, column_data: pd.Series, unique_flag: bool) -> str:
    """Infer the role of the column."""
    column_lower = column_name.lower()
    
    # Check for identifier patterns
    if unique_flag and any(indicator in column_lower for indicator in ID_INDICATORS):
        return 'identifier'
    
    # Check for time index patterns
    if any(indicator in column_lower for indicator in TIME_INDICATORS):
        return 'time_index'
    
    # Check for grouping patterns
    if any(indicator in column_lower for indicator in GROUP_INDICATORS):
        return 'group_by'
    
    # Default to feature
    return 'feature'


def _infer_do_not_impute(role: str, unique_flag: bool) -> bool:
    """Determine if column should not be imputed."""
    return role == 'identifier' or unique_flag


def _infer_time_index(column_name: str, data_type: str) -> bool:
    """Check if column is a time index."""
    column_lower = column_name.lower()
    return (data_type == 'datetime' and 
            any(indicator in column_lower for indicator in TIME_INDICATORS))


def _infer_group_by(column_name: str, data_type: str, column_data: pd.Series) -> bool:
    """Check if column is suitable for grouping."""
    column_lower = column_name.lower()
    
    # Name-based detection
    if any(indicator in column_lower for indicator in GROUP_INDICATORS):
        return True
    
    # Data-based detection for categorical columns
    if data_type == 'categorical':
        unique_count = column_data.nunique()
        # Good grouping columns have reasonable number of groups
        return 2 <= unique_count <= 50
    
    return False


def _generate_description(column_name: str, data_type: str) -> str:
    """Generate a human-readable description."""
    return f"Auto-inferred {data_type} column: {column_name}"