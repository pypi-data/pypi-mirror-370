#!/usr/bin/env python3
"""
Simplified preflight checks for CSV data files before analysis.

Streamlined version focusing only on CSV support with core validation checks.
Removes legacy JSON/Parquet/Excel support and complex compression handling.
"""

import os
import gzip
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings

# Core dependencies
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)

# Simplified constants
CONFIG = {
    'DEFAULT_SAMPLE_ROWS': 2000,
    'DEFAULT_MAX_SNIFF_BYTES': 65536,
    'ENCODING_CANDIDATES': ['utf-8', 'latin1', 'cp1252'],
    'CSV_DELIMITERS': [',', ';', '\t', '|'],
    'MEMORY_WARNING_THRESHOLD': 1024 * 1024 * 1024,  # 1GB
    'MIN_SAMPLE_THRESHOLD': 50,
    'NULL_PERCENTAGE_WARNING': 50.0,
}

# Compiled regex patterns for performance
PATTERNS = {
    'DATETIME': [
        re.compile(r'\d{4}-\d{2}-\d{2}'),
        re.compile(r'\d{2}/\d{2}/\d{4}'),
        re.compile(r'\d{4}/\d{2}/\d{2}'),
    ],
    'NUMERIC': re.compile(r'^-?[\d,]+\.?\d*$'),
    'BOOLEAN': re.compile(r'^(true|false|yes|no|y|n|1|0)$', re.IGNORECASE),
}


def run_preflight(
    file_path: str,
    sample_rows: int = None,
    max_sniff_bytes: int = None,
    output_json: bool = False,
    silent: bool = False,
    hints: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Run comprehensive preflight checks on a CSV data file.
    
    Args:
        file_path: Path to the data file
        sample_rows: Number of rows to sample for analysis
        max_sniff_bytes: Maximum bytes to read for format detection
        output_json: Whether to return JSON-formatted output
        silent: Whether to suppress logging output
        
    Returns:
        Dictionary containing preflight results and recommendations
    """
    if silent:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Initialize defaults
    sample_rows = sample_rows or CONFIG['DEFAULT_SAMPLE_ROWS']
    max_sniff_bytes = max_sniff_bytes or CONFIG['DEFAULT_MAX_SNIFF_BYTES']
    
    # Initialize report
    report = {
        'file_path': file_path,
        'status': 'unknown',
        'exit_code': 10,  # Default to error
        'checks': {},
        'warnings': [],
        'errors': [],
        'recommendation': {},
        'summary': {}
    }
    
    try:
        # A1: Path and size check
        report['checks']['A1_path_size'] = _check_path_and_size(file_path)
        
        # A2: Format check (CSV only)
        report['checks']['A2_format'] = _check_csv_format(file_path)
        
        # A3: Encoding probe
        report['checks']['A3_encoding'] = _probe_encoding(file_path)
        
        # A4: CSV dialect detection
        report['checks']['A4_csv_dialect'] = _detect_csv_dialect(file_path, report['checks']['A3_encoding'])
        
        # A5: Structure analysis
        report['checks']['A5_structure'] = _analyze_structure(file_path, sample_rows, report['checks'])
        
        # A6: Memory estimation
        report['checks']['A6_memory'] = _estimate_memory_usage(file_path, sample_rows)
        
        # Collect warnings and errors
        for check_name, check_result in report['checks'].items():
            if 'warning' in check_result:
                report['warnings'].append(f"{check_name}: {check_result['warning']}")
            if 'error' in check_result:
                report['errors'].append(f"{check_name}: {check_result['error']}")
        
        # Determine overall status
        if report['errors']:
            report['status'] = 'error'
            report['exit_code'] = 10
        elif report['warnings']:
            report['status'] = 'warning'
            report['exit_code'] = 2
        else:
            report['status'] = 'ok'
            report['exit_code'] = 0
        
        # Generate recommendation
        report['recommendation'] = _decide_recommendation(report)
        
    except Exception as e:
        report['status'] = 'error'
        report['exit_code'] = 10
        report['errors'].append(f"Preflight failed: {str(e)}")
        logger.error(f"Preflight error: {e}")
    
    return report


def _check_path_and_size(path: str) -> Dict[str, Any]:
    """A1: Check file path, existence, and size."""
    result = {'status': 'ok'}
    
    try:
        path_obj = Path(path)
        
        # Check existence
        if not path_obj.exists():
            result['error'] = f"File does not exist: {path}"
            return result
        
        # Check readability
        if not os.access(path, os.R_OK):
            result['error'] = f"File is not readable: {path}"
            return result
        
        # Check size
        file_size = path_obj.stat().st_size
        if file_size == 0:
            result['error'] = "File is empty"
            return result
        
        result['file_size'] = file_size
        result['file_size_mb'] = round(file_size / (1024 * 1024), 2)
        
        # Warning for very large files
        if file_size > CONFIG['MEMORY_WARNING_THRESHOLD']:
            result['warning'] = f"Large file ({result['file_size_mb']} MB) - may require chunked processing"
        
    except Exception as e:
        result['error'] = f"Path check failed: {str(e)}"
    
    return result


def _check_csv_format(path: str) -> Dict[str, Any]:
    """A2: Check if file is a CSV (simplified format check)."""
    result = {'status': 'ok', 'format': 'csv'}
    
    path_obj = Path(path)
    
    # Check compression
    if path_obj.suffix.lower() == '.gz':
        result['compression'] = 'gz'
        stem = path_obj.stem
    else:
        result['compression'] = 'none'
        stem = path_obj.name
    
    # Check extension
    if not stem.lower().endswith('.csv'):
        result['warning'] = f"File extension is not .csv: {stem}"
    
    return result


def _probe_encoding(path: str) -> Dict[str, Any]:
    """A3: Probe file encoding."""
    result = {'status': 'ok', 'encoding': 'utf-8'}
    
    try:
        # Try encodings in order of preference
        for encoding in CONFIG['ENCODING_CANDIDATES']:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    f.read(1024)  # Try to read first 1KB
                result['encoding'] = encoding
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            result['warning'] = "Could not detect encoding - defaulting to utf-8"
            
    except Exception as e:
        result['error'] = f"Encoding detection failed: {str(e)}"
    
    return result


def _detect_csv_dialect(path: str, encoding_info: Dict[str, Any]) -> Dict[str, Any]:
    """A4: Detect CSV dialect (delimiter, quote character, etc.)."""
    result = {'status': 'ok', 'delimiter': ',', 'quotechar': '"'}
    
    try:
        encoding = encoding_info.get('encoding', 'utf-8')
        
        # Read sample for dialect detection
        with open(path, 'r', encoding=encoding) as f:
            sample = f.read(CONFIG['DEFAULT_MAX_SNIFF_BYTES'])
        
        # Try to detect delimiter
        delimiter_counts = {}
        for delimiter in CONFIG['CSV_DELIMITERS']:
            count = sample.count(delimiter)
            if count > 0:
                delimiter_counts[delimiter] = count
        
        if delimiter_counts:
            # Use the most common delimiter
            best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
            result['delimiter'] = best_delimiter
        else:
            result['warning'] = "Could not detect CSV delimiter - using comma"
        
        # Simple header detection
        lines = sample.split('\n')[:5]  # Check first 5 lines
        if lines:
            result['has_header'] = True  # Assume header by default
        
    except Exception as e:
        result['error'] = f"CSV dialect detection failed: {str(e)}"
    
    return result


def _analyze_structure(path: str, sample_rows: int, checks: Dict[str, Any]) -> Dict[str, Any]:
    """A5: Analyze file structure and sample data."""
    result = {'status': 'ok'}
    
    try:
        # Extract info from previous checks
        encoding = checks['A3_encoding'].get('encoding', 'utf-8')
        delimiter = checks['A4_csv_dialect'].get('delimiter', ',')
        
        # Read sample DataFrame
        df = pd.read_csv(
            path,
            encoding=encoding,
            delimiter=delimiter,
            nrows=sample_rows,
            low_memory=False
        )
        
        result['total_columns'] = len(df.columns)
        result['sample_rows'] = len(df)
        result['column_names'] = list(df.columns)
        
        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns)):
            result['warning'] = "Duplicate column names detected"
        
        # Basic data type inference
        column_types = {}
        missing_counts = {}
        
        for col in df.columns:
            # Simple type inference
            series = df[col]
            non_null = series.dropna()
            missing_counts[col] = series.isna().sum()
            
            if len(non_null) == 0:
                column_types[col] = 'all_missing'
            elif pd.api.types.is_numeric_dtype(series):
                if pd.api.types.is_integer_dtype(series):
                    column_types[col] = 'integer'
                else:
                    column_types[col] = 'float'
            elif pd.api.types.is_datetime64_any_dtype(series):
                column_types[col] = 'datetime'
            else:
                column_types[col] = 'string'
        
        result['column_types'] = column_types
        result['missing_counts'] = missing_counts
        result['total_missing'] = sum(missing_counts.values())
        
        # Check for high missing data
        total_cells = len(df) * len(df.columns)
        missing_percentage = (result['total_missing'] / total_cells) * 100 if total_cells > 0 else 0
        
        if missing_percentage > CONFIG['NULL_PERCENTAGE_WARNING']:
            result['warning'] = f"High missing data percentage: {missing_percentage:.1f}%"
        
    except Exception as e:
        result['error'] = f"Structure analysis failed: {str(e)}"
    
    return result


def _estimate_memory_usage(path: str, sample_rows: int) -> Dict[str, Any]:
    """A6: Estimate memory usage for full file processing."""
    result = {'status': 'ok'}
    
    try:
        file_size = Path(path).stat().st_size
        
        # Simple estimation: assume full file will use ~3x file size in memory
        estimated_memory_mb = (file_size * 3) / (1024 * 1024)
        
        result['estimated_memory_mb'] = round(estimated_memory_mb, 1)
        result['file_size_mb'] = round(file_size / (1024 * 1024), 2)
        
        if estimated_memory_mb > 1024:  # > 1GB
            result['warning'] = f"High estimated memory usage: {result['estimated_memory_mb']} MB"
        
    except Exception as e:
        result['error'] = f"Memory estimation failed: {str(e)}"
    
    return result


def _decide_recommendation(report: Dict[str, Any]) -> Dict[str, Any]:
    """Generate recommendation based on preflight results."""
    structure = report['checks'].get('A5_structure', {})
    total_columns = structure.get('total_columns', 0)
    has_warnings = bool(report.get('warnings', []))
    
    # Simplified decision logic
    if total_columns == 0:
        action = 'manual_review'
        reason = "No columns detected - file may be corrupted or invalid CSV format"
    elif total_columns > 50 or has_warnings:
        action = 'generate_metadata'
        reason = "Complex dataset or warnings detected - metadata template recommended"
    else:
        action = 'analyze_infer_only'
        reason = "Simple dataset suitable for direct analysis with auto-inference"
    
    return {
        'action': action,
        'reason': reason,
        'next_steps': _get_next_steps(action)
    }


def _get_next_steps(action: str) -> List[str]:
    """Get recommended next steps based on action."""
    steps_map = {
        'analyze_infer_only': [
            "Run: funputer analyze -d <file> (auto-inference mode)",
            "Review imputation recommendations",
            "Apply suggested methods"
        ],
        'generate_metadata': [
            "Run: funputer init -d <file> to generate metadata template",
            "Review and customize metadata constraints",
            "Run: funputer analyze -m <metadata_file> -d <data_file>"
        ],
        'manual_review': [
            "Manually inspect file format and structure",
            "Ensure file is a valid CSV with proper encoding",
            "Check for data corruption or formatting issues"
        ]
    }
    
    return steps_map.get(action, ["Review file and try again"])


def format_preflight_report(report: Dict[str, Any]) -> str:
    """Format preflight report for console output."""
    lines = []
    
    # Header
    status_emoji = {
        'ok': '✅',
        'warning': '⚠️',
        'error': '❌'
    }.get(report['status'], '❓')
    
    lines.append(f"🔍 Preflight Check:")
    lines.append(f"Preflight Report: {report['file_path']}")
    lines.append(f"Status: {report['status']} (Exit Code: {report['exit_code']})")
    lines.append("")
    
    # Recommendation
    rec = report.get('recommendation', {})
    if rec:
        lines.append(f"RECOMMENDATION: {rec.get('action', 'unknown')}")
        lines.append(f"Reason: {rec.get('reason', 'No reason provided')}")
        lines.append("Next Steps:")
        for step in rec.get('next_steps', []):
            lines.append(f"  • {step}")
        lines.append("")
    
    # Check results
    lines.append("DETAILED CHECKS:")
    for check_name, check_result in report['checks'].items():
        status = "✓" if check_result.get('status') == 'ok' else "✗"
        lines.append(f"  {check_name}: {status}")
    
    # Warnings and errors
    if report.get('warnings'):
        lines.append("")
        lines.append("WARNINGS:")
        for warning in report['warnings']:
            lines.append(f"  ⚠️  {warning}")
    
    if report.get('errors'):
        lines.append("")
        lines.append("ERRORS:")
        for error in report['errors']:
            lines.append(f"  ❌ {error}")
    
    return "\n".join(lines)