"""
Essential preflight tests to boost coverage from 10% to 43%+.
Targeting the main preflight workflow to reach 80%+ overall coverage.

Priority: CRITICAL - Need +61 lines to reach 80% overall
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import gzip
from pathlib import Path
from unittest.mock import patch, MagicMock

from funputer.preflight import (
    run_preflight, _check_path_and_size, _check_csv_format, 
    _probe_encoding, _detect_csv_dialect, _analyze_structure,
    _estimate_memory_usage, _decide_recommendation,
    format_preflight_report, CONFIG, PATTERNS
)


class TestPreflightMain:
    """Test main preflight workflow (lines 67-132)."""
    
    def create_test_csv(self, content="id,name,value\n1,test,10.5\n2,data,20.0\n"):
        """Create test CSV file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(content)
        temp_file.flush()
        return temp_file.name
    
    def test_run_preflight_basic_success(self):
        """Test basic successful preflight run (lines 67-84, 86-104, 113-124)."""
        csv_file = self.create_test_csv()
        
        try:
            result = run_preflight(csv_file)
            
            assert isinstance(result, dict)
            assert 'file_path' in result
            assert 'status' in result
            assert 'exit_code' in result
            assert 'checks' in result
            assert 'warnings' in result
            assert 'errors' in result
            assert 'recommendation' in result
            
            # Should have all required check keys
            expected_checks = ['A1_path_size', 'A2_format', 'A3_encoding', 'A4_csv_dialect', 'A5_structure', 'A6_memory']
            for check in expected_checks:
                assert check in result['checks']
            
            # Should succeed for valid CSV
            assert result['status'] in ['ok', 'warning']
            assert result['exit_code'] in [0, 2]
            
        finally:
            os.unlink(csv_file)
    
    def test_run_preflight_with_silent_logging(self):
        """Test preflight with silent logging (lines 67-68)."""
        csv_file = self.create_test_csv()
        
        try:
            with patch('logging.getLogger') as mock_logger:
                mock_log = MagicMock()
                mock_logger.return_value = mock_log
                
                result = run_preflight(csv_file, silent=True)
                
                # Should set logging level to ERROR
                mock_log.setLevel.assert_called_with(logging.ERROR)
                assert result['status'] in ['ok', 'warning']
            
        finally:
            os.unlink(csv_file)
    
    def test_run_preflight_custom_parameters(self):
        """Test preflight with custom parameters (lines 71-72)."""
        csv_file = self.create_test_csv()
        
        try:
            result = run_preflight(
                csv_file, 
                sample_rows=100,
                max_sniff_bytes=1024
            )
            
            assert result['status'] in ['ok', 'warning']
            
        finally:
            os.unlink(csv_file)
    
    def test_run_preflight_with_warnings_and_errors(self):
        """Test preflight error/warning collection (lines 106-110)."""
        # Mock check results to include warnings and errors
        with patch('funputer.preflight._check_path_and_size') as mock_path:
            with patch('funputer.preflight._check_csv_format') as mock_format:
                mock_path.return_value = {'status': 'ok'}
                mock_format.return_value = {
                    'status': 'warning',
                    'warning': 'Test warning message'
                }
                
                csv_file = self.create_test_csv()
                
                try:
                    result = run_preflight(csv_file)
                    
                    # Should collect warnings
                    assert len(result['warnings']) > 0
                    assert any('Test warning message' in w for w in result['warnings'])
                    
                finally:
                    os.unlink(csv_file)
    
    def test_run_preflight_status_determination(self):
        """Test status and exit code determination (lines 113-121)."""
        csv_file = self.create_test_csv()
        
        try:
            # Test with errors
            with patch('funputer.preflight._check_path_and_size') as mock_check:
                mock_check.return_value = {
                    'status': 'error',
                    'error': 'Test error'
                }
                
                result = run_preflight(csv_file)
                
                assert result['status'] == 'error'
                assert result['exit_code'] == 10
                assert len(result['errors']) > 0
            
            # Test with warnings only
            with patch('funputer.preflight._check_path_and_size') as mock_check:
                with patch('funputer.preflight._check_csv_format') as mock_format:
                    mock_check.return_value = {'status': 'ok'}
                    mock_format.return_value = {
                        'status': 'warning',
                        'warning': 'Test warning'
                    }
                    
                    result = run_preflight(csv_file)
                    
                    assert result['status'] == 'warning'
                    assert result['exit_code'] == 2
            
        finally:
            os.unlink(csv_file)
    
    def test_run_preflight_exception_handling(self):
        """Test preflight exception handling (lines 126-131)."""
        # Mock a check to raise an exception
        with patch('funputer.preflight._check_path_and_size') as mock_check:
            mock_check.side_effect = Exception("Simulated error")
            
            csv_file = self.create_test_csv()
            
            try:
                with patch('funputer.preflight.logger') as mock_logger:
                    result = run_preflight(csv_file)
                    
                    assert result['status'] == 'error'
                    assert result['exit_code'] == 10
                    assert len(result['errors']) > 0
                    assert any('Preflight failed' in e for e in result['errors'])
                    mock_logger.error.assert_called()
                
            finally:
                os.unlink(csv_file)


class TestCheckPathAndSize:
    """Test path and size checking (lines 135-200)."""
    
    def test_check_path_and_size_success(self):
        """Test successful path and size check (lines 137-165)."""
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        csv_file.write('test,data\n1,2\n')
        csv_file.flush()
        
        try:
            result = _check_path_and_size(csv_file.name)
            
            assert result['status'] == 'ok'
            assert 'file_size_bytes' in result
            assert 'file_size_mb' in result
            assert result['file_size_bytes'] > 0
            
        finally:
            os.unlink(csv_file.name)
    
    def test_check_path_and_size_nonexistent_file(self):
        """Test path check with nonexistent file (lines 143-145)."""
        result = _check_path_and_size('nonexistent_file.csv')
        
        assert 'error' in result
        assert 'does not exist' in result['error']
    
    def test_check_path_and_size_unreadable_file(self):
        """Test path check with unreadable file (lines 148-150)."""
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        csv_file.write('test,data\n')
        csv_file.flush()
        
        try:
            # Mock os.access to return False (unreadable)
            with patch('os.access', return_value=False):
                result = _check_path_and_size(csv_file.name)
                
                assert 'error' in result
                assert 'not readable' in result['error']
            
        finally:
            os.unlink(csv_file.name)


class TestCheckCSVFormat:
    """Test CSV format checking."""
    
    def test_check_csv_format_valid_csv(self):
        """Test CSV format check with valid file."""
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        csv_file.write('id,name,value\n1,test,10\n2,data,20\n')
        csv_file.flush()
        
        try:
            result = _check_csv_format(csv_file.name)
            
            assert result['status'] == 'ok'
            assert result['format'] == 'csv'
            
        finally:
            os.unlink(csv_file.name)
    
    def test_check_csv_format_compressed_file(self):
        """Test CSV format check with compressed file."""
        # Create gzipped CSV file
        csv_content = 'id,name,value\n1,test,10\n2,data,20\n'
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv.gz', delete=False)
        
        with gzip.open(temp_file.name, 'wt') as f:
            f.write(csv_content)
        
        try:
            result = _check_csv_format(temp_file.name)
            
            assert result['format'] in ['csv', 'csv.gz']
            
        finally:
            os.unlink(temp_file.name)


class TestProbeEncoding:
    """Test encoding detection."""
    
    def test_probe_encoding_utf8(self):
        """Test encoding probe with UTF-8 file."""
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        csv_file.write('id,name\n1,test\n2,café\n')
        csv_file.flush()
        
        try:
            result = _probe_encoding(csv_file.name)
            
            assert result['encoding'] in ['utf-8', 'UTF-8']
            assert result['confidence'] > 0
            
        finally:
            os.unlink(csv_file.name)
    
    def test_probe_encoding_latin1(self):
        """Test encoding probe with Latin-1 file."""
        csv_content = 'id,name\n1,café\n2,naïve\n'
        
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False)
        temp_file.write(csv_content.encode('latin-1'))
        temp_file.flush()
        
        try:
            result = _probe_encoding(temp_file.name)
            
            assert result['encoding'] in ['latin-1', 'ISO-8859-1', 'utf-8']
            assert result['confidence'] >= 0
            
        finally:
            os.unlink(temp_file.name)


class TestDetectCSVDialect:
    """Test CSV dialect detection."""
    
    def test_detect_csv_dialect_comma_separated(self):
        """Test dialect detection for comma-separated values."""
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        csv_file.write('id,name,value\n1,test,10\n2,data,20\n')
        csv_file.flush()
        
        try:
            encoding_result = {'encoding': 'utf-8'}
            result = _detect_csv_dialect(csv_file.name, encoding_result)
            
            assert result['delimiter'] == ','
            assert result['has_header'] is True
            
        finally:
            os.unlink(csv_file.name)
    
    def test_detect_csv_dialect_semicolon_separated(self):
        """Test dialect detection for semicolon-separated values."""
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        csv_file.write('id;name;value\n1;test;10\n2;data;20\n')
        csv_file.flush()
        
        try:
            encoding_result = {'encoding': 'utf-8'}
            result = _detect_csv_dialect(csv_file.name, encoding_result)
            
            assert result['delimiter'] == ';'
            assert result['has_header'] is True
            
        finally:
            os.unlink(csv_file.name)


class TestAnalyzeStructure:
    """Test structure analysis."""
    
    def test_analyze_structure_basic(self):
        """Test basic structure analysis."""
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        csv_file.write('id,name,value,missing\n1,test,10.5,\n2,data,20.0,\n3,more,30.5,value\n')
        csv_file.flush()
        
        try:
            # Mock encoding and dialect results
            checks = {
                'A3_encoding': {'encoding': 'utf-8'},
                'A4_csv_dialect': {'delimiter': ',', 'has_header': True}
            }
            
            result = _analyze_structure(csv_file.name, 1000, checks)
            
            assert result['column_count'] == 4
            assert result['row_count'] > 0
            assert 'columns' in result
            assert len(result['columns']) == 4
            
            # Check missing data detection
            missing_col = next((c for c in result['columns'] if c['name'] == 'missing'), None)
            assert missing_col is not None
            assert missing_col['null_count'] > 0
            
        finally:
            os.unlink(csv_file.name)


class TestEstimateMemoryUsage:
    """Test memory usage estimation."""
    
    def test_estimate_memory_usage_basic(self):
        """Test basic memory usage estimation."""
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        # Create larger CSV to get meaningful memory estimate
        for i in range(1000):
            csv_file.write(f'{i},test_{i},value_{i}\n')
        csv_file.flush()
        
        try:
            result = _estimate_memory_usage(csv_file.name, 100)
            
            assert 'estimated_memory_mb' in result
            assert 'memory_warning' in result
            assert result['estimated_memory_mb'] > 0
            
        finally:
            os.unlink(csv_file.name)


class TestDecideRecommendation:
    """Test recommendation decision logic."""
    
    def test_decide_recommendation_basic(self):
        """Test basic recommendation decision."""
        report = {
            'status': 'ok',
            'checks': {
                'A5_structure': {
                    'column_count': 5,
                    'row_count': 1000
                },
                'A6_memory': {
                    'estimated_memory_mb': 10
                }
            },
            'warnings': [],
            'errors': []
        }
        
        result = _decide_recommendation(report)
        
        assert 'action' in result
        assert 'rationale' in result
        assert result['action'] in ['analyze_infer_only', 'generate_metadata']


class TestFormatPreflightReport:
    """Test report formatting."""
    
    def test_format_preflight_report_success(self):
        """Test formatting successful preflight report."""
        report = {
            'status': 'ok',
            'exit_code': 0,
            'file_path': 'test.csv',
            'checks': {
                'A1_path_size': {'status': 'ok', 'file_size_mb': 1.5}
            },
            'warnings': [],
            'errors': [],
            'recommendation': {
                'action': 'analyze_infer_only',
                'rationale': 'File looks good'
            }
        }
        
        result = format_preflight_report(report)
        
        assert isinstance(result, str)
        assert '✅' in result or 'ok' in result.lower()
        assert 'test.csv' in result
    
    def test_format_preflight_report_with_warnings(self):
        """Test formatting preflight report with warnings."""
        report = {
            'status': 'warning',
            'exit_code': 2,
            'file_path': 'test.csv',
            'checks': {},
            'warnings': ['Test warning message'],
            'errors': [],
            'recommendation': {
                'action': 'generate_metadata',
                'rationale': 'Issues detected'
            }
        }
        
        result = format_preflight_report(report)
        
        assert isinstance(result, str)
        assert '⚠️' in result or 'warning' in result.lower()
        assert 'Test warning message' in result
    
    def test_format_preflight_report_with_errors(self):
        """Test formatting preflight report with errors."""
        report = {
            'status': 'error',
            'exit_code': 10,
            'file_path': 'test.csv',
            'checks': {},
            'warnings': [],
            'errors': ['Test error message'],
            'recommendation': {
                'action': 'manual_review',
                'rationale': 'Serious issues found'
            }
        }
        
        result = format_preflight_report(report)
        
        assert isinstance(result, str)
        assert '❌' in result or 'error' in result.lower()
        assert 'Test error message' in result


class TestPreflightConfiguration:
    """Test preflight configuration and constants."""
    
    def test_config_constants_exist(self):
        """Test that all required configuration constants exist."""
        required_keys = [
            'DEFAULT_SAMPLE_ROWS',
            'DEFAULT_MAX_SNIFF_BYTES', 
            'ENCODING_CANDIDATES',
            'CSV_DELIMITERS',
            'MEMORY_WARNING_THRESHOLD',
            'MIN_SAMPLE_THRESHOLD',
            'NULL_PERCENTAGE_WARNING'
        ]
        
        for key in required_keys:
            assert key in CONFIG
            assert CONFIG[key] is not None
    
    def test_patterns_compiled(self):
        """Test that regex patterns are compiled."""
        assert 'DATETIME' in PATTERNS
        assert 'NUMERIC' in PATTERNS
        assert 'BOOLEAN' in PATTERNS
        
        # Test patterns work
        assert PATTERNS['NUMERIC'].match('123.45')
        assert PATTERNS['BOOLEAN'].match('true')
        assert PATTERNS['BOOLEAN'].match('FALSE')