"""
Comprehensive tests for funputer.memory_utils module.
Targeting 0% → 60%+ coverage (47+ lines covered).

Priority: HIGHEST ROI - +3.7% overall coverage
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import warnings
from pathlib import Path
from unittest.mock import patch, MagicMock

from funputer.memory_utils import (
    MemoryMonitor, get_optimal_processing_config, estimate_file_properties
)


class TestMemoryMonitor:
    """Test MemoryMonitor class functionality."""
    
    def test_memory_monitor_initialization(self):
        """Test MemoryMonitor initialization (lines 17-19)."""
        monitor = MemoryMonitor()
        
        assert hasattr(monitor, 'process')
        assert hasattr(monitor, 'initial_memory')
        assert monitor.initial_memory > 0
        assert isinstance(monitor.initial_memory, float)
    
    def test_get_memory_usage_mb(self):
        """Test memory usage retrieval (lines 21-23)."""
        monitor = MemoryMonitor()
        
        memory_usage = monitor.get_memory_usage_mb()
        
        assert isinstance(memory_usage, float)
        assert memory_usage > 0
        # Should be reasonable (between 1MB and 10GB)
        assert 1 < memory_usage < 10000
    
    def test_get_available_memory_mb(self):
        """Test available memory retrieval (lines 25-27)."""
        monitor = MemoryMonitor()
        
        available_memory = monitor.get_available_memory_mb()
        
        assert isinstance(available_memory, float)
        assert available_memory > 0
        # Should be reasonable amount available
        assert available_memory > 10  # At least 10MB available
    
    def test_get_memory_increase_mb(self):
        """Test memory increase calculation (lines 29-31)."""
        monitor = MemoryMonitor()
        
        # Create some data to increase memory usage
        data = pd.DataFrame(np.random.randn(1000, 10))
        
        memory_increase = monitor.get_memory_increase_mb()
        
        assert isinstance(memory_increase, float)
        # Memory increase can be positive, negative, or zero
        assert -1000 < memory_increase < 1000  # Reasonable bounds
    
    def test_estimate_dataframe_memory_mb(self):
        """Test DataFrame memory estimation (lines 33-35)."""
        monitor = MemoryMonitor()
        
        # Create test DataFrame
        df = pd.DataFrame({
            'col1': range(1000),
            'col2': ['test'] * 1000,
            'col3': np.random.randn(1000)
        })
        
        memory_estimate = monitor.estimate_dataframe_memory_mb(df)
        
        assert isinstance(memory_estimate, float)
        assert memory_estimate > 0
        # Should be reasonable for 1000 rows x 3 cols
        assert 0.01 < memory_estimate < 100  # Between 0.01MB and 100MB
    
    def test_should_use_chunking_small_file(self):
        """Test chunking decision for small files (lines 52-77)."""
        monitor = MemoryMonitor()
        
        # Create small test file
        small_data = pd.DataFrame({'col': range(100)})
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        small_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        
        try:
            should_chunk, chunk_size = monitor.should_use_chunking(temp_file.name)
            
            # Small file should not require chunking
            assert should_chunk is False
            assert chunk_size is None
            
        finally:
            os.unlink(temp_file.name)
    
    def test_should_use_chunking_large_file(self):
        """Test chunking decision for large files (lines 56-71)."""
        monitor = MemoryMonitor()
        
        # Mock file size to appear large
        with patch('pathlib.Path.stat') as mock_stat:
            # Mock 50MB file
            mock_stat.return_value.st_size = 50 * 1024 * 1024
            
            should_chunk, chunk_size = monitor.should_use_chunking('fake_file.csv')
            
            # Large file should require chunking
            assert should_chunk is True
            assert chunk_size is not None
            assert isinstance(chunk_size, int)
            assert 1000 <= chunk_size <= 100000  # Within expected bounds
    
    def test_should_use_chunking_low_memory(self):
        """Test chunking decision with low available memory (lines 74-75)."""
        monitor = MemoryMonitor()
        
        # Create small file but mock low available memory
        with patch.object(monitor, 'get_available_memory_mb') as mock_memory:
            # Mock very low available memory (50MB)
            mock_memory.return_value = 50.0
            
            # Mock small file size
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 5 * 1024 * 1024  # 5MB file
                
                should_chunk, chunk_size = monitor.should_use_chunking(
                    'fake_file.csv', 
                    available_memory_threshold=100.0  # Threshold higher than available
                )
                
                # Should chunk due to low memory
                assert should_chunk is True
                assert chunk_size == 5000
    
    def test_should_use_chunking_exception_handling(self):
        """Test chunking with file access errors (lines 79-80)."""
        monitor = MemoryMonitor()
        
        # Test with nonexistent file
        should_chunk, chunk_size = monitor.should_use_chunking('nonexistent_file.csv')
        
        # Should handle error gracefully
        assert should_chunk is False
        assert chunk_size is None
    
    def test_warn_if_memory_high_normal_usage(self):
        """Test memory warning with normal usage (lines 82-96)."""
        monitor = MemoryMonitor()
        
        # Mock normal memory usage
        with patch.object(monitor, 'get_memory_usage_mb') as mock_usage:
            with patch.object(monitor, 'get_available_memory_mb') as mock_available:
                with patch('psutil.virtual_memory') as mock_virtual:
                    # Mock normal usage (50% of 8GB = 4GB used)
                    mock_usage.return_value = 4000.0  # 4GB
                    mock_available.return_value = 4000.0  # 4GB available
                    mock_virtual.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB total
                    
                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter("always")
                        
                        monitor.warn_if_memory_high(threshold_pct=80.0)
                        
                        # Should not warn for normal usage (50% < 80%)
                        assert len(w) == 0
    
    def test_warn_if_memory_high_high_usage(self):
        """Test memory warning with high usage (lines 92-93)."""
        monitor = MemoryMonitor()
        
        # Mock high memory usage
        with patch.object(monitor, 'get_memory_usage_mb') as mock_usage:
            with patch.object(monitor, 'get_available_memory_mb') as mock_available:
                with patch('psutil.virtual_memory') as mock_virtual:
                    # Mock high usage (85% of 8GB = 6.8GB used)
                    mock_usage.return_value = 6800.0  # 6.8GB
                    mock_available.return_value = 1200.0  # 1.2GB available
                    mock_virtual.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB total
                    
                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter("always")
                        
                        monitor.warn_if_memory_high(threshold_pct=80.0)
                        
                        # Should warn for high usage (85% > 80%)
                        assert len(w) == 1
                        assert "High memory usage" in str(w[0].message)
    
    def test_warn_if_memory_low_available(self):
        """Test memory warning with low available memory (lines 95-96)."""
        monitor = MemoryMonitor()
        
        # Mock low available memory
        with patch.object(monitor, 'get_memory_usage_mb') as mock_usage:
            with patch.object(monitor, 'get_available_memory_mb') as mock_available:
                with patch('psutil.virtual_memory') as mock_virtual:
                    # Normal usage but very low available memory
                    mock_usage.return_value = 2000.0  # 2GB
                    mock_available.return_value = 50.0   # Only 50MB available
                    mock_virtual.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB total
                    
                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter("always")
                        
                        monitor.warn_if_memory_high(threshold_pct=80.0)
                        
                        # Should warn for low available memory (50MB < 200MB)
                        assert len(w) == 1
                        assert "Low available memory" in str(w[0].message)


class TestOptimalProcessingConfig:
    """Test get_optimal_processing_config function."""
    
    def test_get_optimal_processing_config_small_file(self):
        """Test processing config for small file (lines 113-133)."""
        # Create small test file
        small_data = pd.DataFrame({'col': range(100)})
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        small_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        
        try:
            config = get_optimal_processing_config(temp_file.name)
            
            assert isinstance(config, dict)
            assert 'use_chunking' in config
            assert 'chunk_size' in config
            assert 'current_memory_mb' in config
            assert 'available_memory_mb' in config
            assert 'use_parallel' in config
            assert 'max_workers' in config
            
            # Small file should not require chunking
            assert config['use_chunking'] is False
            assert config['chunk_size'] is None
            
            # Without target_columns, should not use parallel processing
            assert config['use_parallel'] is False
            assert config['max_workers'] == 1
            
        finally:
            os.unlink(temp_file.name)
    
    def test_get_optimal_processing_config_with_target_columns(self):
        """Test processing config with target columns (lines 125-131)."""
        small_data = pd.DataFrame({'col': range(100)})
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        small_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        
        try:
            # Test with many target columns
            config = get_optimal_processing_config(temp_file.name, target_columns=10)
            
            # Should recommend parallel processing
            assert config['use_parallel'] is True
            assert config['max_workers'] > 1
            assert config['max_workers'] <= 8  # Max workers cap
            
            # Test with few target columns
            config_few = get_optimal_processing_config(temp_file.name, target_columns=2)
            
            # Should not use parallel processing for few columns
            assert config_few['use_parallel'] is False
            assert config_few['max_workers'] == 1
            
        finally:
            os.unlink(temp_file.name)
    
    def test_get_optimal_processing_config_cpu_count_integration(self):
        """Test CPU count integration (lines 124-126)."""
        small_data = pd.DataFrame({'col': range(100)})
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        small_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        
        try:
            # Mock CPU count
            with patch('psutil.cpu_count') as mock_cpu:
                mock_cpu.return_value = 4
                
                config = get_optimal_processing_config(temp_file.name, target_columns=10)
                
                # Max workers should be limited by CPU count
                assert config['max_workers'] <= 4
                
        finally:
            os.unlink(temp_file.name)


class TestEstimateFileProperties:
    """Test estimate_file_properties function."""
    
    def test_estimate_file_properties_basic(self):
        """Test basic file property estimation (lines 151-179)."""
        # Create test CSV file
        test_data = pd.DataFrame({
            'col1': range(500),
            'col2': ['test'] * 500,
            'col3': np.random.randn(500)
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        test_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        
        try:
            properties = estimate_file_properties(temp_file.name, sample_size=100)
            
            assert isinstance(properties, dict)
            assert 'estimated_columns' in properties
            assert 'sample_rows' in properties
            assert 'sample_memory_mb' in properties
            assert 'estimated_total_rows' in properties
            assert 'estimated_total_memory_mb' in properties
            
            # Check values are reasonable
            assert properties['estimated_columns'] == 3
            assert properties['sample_rows'] == 100  # Limited by sample_size
            assert properties['sample_memory_mb'] > 0
            assert properties['estimated_total_rows'] > 100  # Should estimate more
            assert properties['estimated_total_memory_mb'] > 0
            
        finally:
            os.unlink(temp_file.name)
    
    def test_estimate_file_properties_nonexistent_file(self):
        """Test file property estimation with nonexistent file (lines 152-153)."""
        with pytest.raises(FileNotFoundError) as exc_info:
            estimate_file_properties('nonexistent_file.csv')
        
        assert 'No such file or directory' in str(exc_info.value)
    
    def test_estimate_file_properties_not_a_file(self):
        """Test file property estimation with directory (lines 155-156)."""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            with pytest.raises(OSError) as exc_info:
                estimate_file_properties(temp_dir)
            
            assert 'Not a regular file' in str(exc_info.value)
            
        finally:
            os.rmdir(temp_dir)
    
    def test_estimate_file_properties_empty_file(self):
        """Test file property estimation with empty file (lines 169-177)."""
        # Create empty CSV file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write('col1,col2,col3\n')  # Header only
        temp_file.flush()
        
        try:
            properties = estimate_file_properties(temp_file.name, sample_size=100)
            
            # Should handle empty file gracefully
            assert properties['estimated_columns'] == 3
            assert properties['sample_rows'] == 0
            assert properties['sample_memory_mb'] >= 0
            
        finally:
            os.unlink(temp_file.name)
    
    def test_estimate_file_properties_corrupt_csv(self):
        """Test file property estimation with corrupt CSV (lines 183-184)."""
        # Create invalid CSV file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write('invalid,csv,format\nwith,unmatched,quotes"and"stuff')
        temp_file.flush()
        
        try:
            with pytest.raises(OSError) as exc_info:
                estimate_file_properties(temp_file.name)
            
            assert 'Failed to read file properties' in str(exc_info.value)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_estimate_file_properties_custom_sample_size(self):
        """Test file property estimation with custom sample size."""
        # Create test CSV file with more rows
        test_data = pd.DataFrame({
            'col1': range(1000),
            'col2': ['test'] * 1000
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        test_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        
        try:
            # Test with custom sample size
            properties = estimate_file_properties(temp_file.name, sample_size=50)
            
            assert properties['sample_rows'] == 50  # Should respect sample_size
            assert properties['estimated_columns'] == 2
            
        finally:
            os.unlink(temp_file.name)


class TestMemoryUtilsIntegration:
    """Integration tests for memory utilities."""
    
    def test_memory_monitor_integration_workflow(self):
        """Test complete memory monitoring workflow."""
        # Create monitor
        monitor = MemoryMonitor()
        
        # Check initial state
        initial_memory = monitor.get_memory_usage_mb()
        available_memory = monitor.get_available_memory_mb()
        
        assert initial_memory > 0
        assert available_memory > 0
        
        # Create some data and check memory increase
        data = pd.DataFrame(np.random.randn(1000, 20))
        memory_estimate = monitor.estimate_dataframe_memory_mb(data)
        
        assert memory_estimate > 0
        
        # Check memory increase
        memory_increase = monitor.get_memory_increase_mb()
        
        # Memory increase should be reasonable
        assert -100 < memory_increase < 100  # Within 100MB change
        
        # Test warning system
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            monitor.warn_if_memory_high(threshold_pct=99.0)  # High threshold
            # Should not warn with high threshold
            assert len(w) <= 1  # May warn about low available memory
    
    def test_end_to_end_processing_recommendation(self):
        """Test complete processing recommendation workflow."""
        # Create test file
        test_data = pd.DataFrame({
            'col' + str(i): np.random.randn(2000) for i in range(8)
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        test_data.to_csv(temp_file.name, index=False)
        temp_file.flush()
        
        try:
            # Get file properties
            properties = estimate_file_properties(temp_file.name, sample_size=200)
            
            # Get processing config
            config = get_optimal_processing_config(
                temp_file.name, 
                target_columns=properties['estimated_columns']
            )
            
            # Verify complete workflow
            assert properties['estimated_columns'] == 8
            assert config['use_parallel'] is True  # Should parallelize 8 columns
            assert config['max_workers'] > 1
            
            # Verify memory info is provided
            assert config['current_memory_mb'] > 0
            assert config['available_memory_mb'] > 0
            
        finally:
            os.unlink(temp_file.name)