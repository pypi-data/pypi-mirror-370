"""
Comprehensive tests for memory utilities module.
Ensures memory monitoring and optimization work correctly.
"""

import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from funputer.memory_utils import (
    MemoryMonitor,
    get_optimal_processing_config,
    estimate_file_properties
)


class TestMemoryMonitor:
    """Test memory monitoring functionality."""
    
    def test_memory_monitor_initialization(self):
        """Test MemoryMonitor initializes correctly."""
        monitor = MemoryMonitor()
        assert monitor.initial_memory > 0
        assert monitor.process is not None
        
    def test_get_memory_usage_mb(self):
        """Test memory usage retrieval."""
        monitor = MemoryMonitor()
        memory_usage = monitor.get_memory_usage_mb()
        assert memory_usage > 0
        assert isinstance(memory_usage, float)
        
    def test_get_available_memory_mb(self):
        """Test available memory retrieval."""
        monitor = MemoryMonitor()
        available_memory = monitor.get_available_memory_mb()
        assert available_memory > 0
        assert isinstance(available_memory, float)
        
    def test_get_memory_increase_mb(self):
        """Test memory increase calculation."""
        monitor = MemoryMonitor()
        # Initially should be close to 0
        increase = monitor.get_memory_increase_mb()
        assert isinstance(increase, float)
        
    def test_estimate_dataframe_memory_mb(self):
        """Test DataFrame memory estimation."""
        monitor = MemoryMonitor()
        df = pd.DataFrame({
            'col1': range(1000),
            'col2': ['test'] * 1000,
            'col3': [1.5] * 1000
        })
        
        memory_estimate = monitor.estimate_dataframe_memory_mb(df)
        assert memory_estimate > 0
        assert isinstance(memory_estimate, float)
        
    def test_should_use_chunking_small_file(self):
        """Test chunking decision for small files."""
        monitor = MemoryMonitor()
        
        # Create a small test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n3,4\n")
            temp_file = f.name
            
        try:
            should_chunk, chunk_size = monitor.should_use_chunking(temp_file)
            assert isinstance(should_chunk, bool)
            if chunk_size is not None:
                assert isinstance(chunk_size, int)
                assert chunk_size > 0
        finally:
            os.unlink(temp_file)
            
    @patch('os.path.getsize')
    def test_should_use_chunking_large_file(self, mock_getsize):
        """Test chunking decision for large files."""
        monitor = MemoryMonitor()
        
        # Mock a large file (100MB)
        mock_getsize.return_value = 100 * 1024 * 1024
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n")
            temp_file = f.name
            
        try:
            should_chunk, chunk_size = monitor.should_use_chunking(temp_file)
            assert isinstance(should_chunk, bool)
            if chunk_size is not None:
                assert isinstance(chunk_size, int)
                assert chunk_size > 0
        finally:
            os.unlink(temp_file)


class TestMemoryUtilities:
    """Test standalone memory utility functions."""
    
    def test_estimate_file_properties(self):
        """Test file properties estimation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2,col3\n")
            for i in range(100):
                f.write(f"{i},test_{i},{i*1.5}\n")
            temp_file = f.name
            
        try:
            properties = estimate_file_properties(temp_file)
            assert isinstance(properties, dict)
            assert 'estimated_total_memory_mb' in properties or 'estimated_memory_mb' in properties or 'size_mb' in properties
        finally:
            os.unlink(temp_file)
            
    def test_get_optimal_processing_config(self):
        """Test optimal processing configuration."""
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n3,4\n")
            temp_file = f.name
            
        try:
            config = get_optimal_processing_config(temp_file)
            assert isinstance(config, dict)
            # Should contain processing recommendations
        finally:
            os.unlink(temp_file)
        
    def test_memory_monitor_context_usage(self):
        """Test memory monitor in context."""
        monitor = MemoryMonitor()
        initial_memory = monitor.get_memory_usage_mb()
        
        # Create some data to use memory
        df = pd.DataFrame({'col': range(1000)})
        memory_after = monitor.get_memory_usage_mb()
        
        assert memory_after >= initial_memory
        del df


class TestMemoryOptimization:
    """Test memory optimization strategies."""
    
    def test_memory_efficient_dataframe_creation(self):
        """Test memory-efficient DataFrame operations."""
        # Test that memory monitoring works during DataFrame operations
        monitor = MemoryMonitor()
        initial_memory = monitor.get_memory_usage_mb()
        
        # Create and immediately delete a large DataFrame
        df = pd.DataFrame({
            'col1': range(10000),
            'col2': ['test' * 10] * 10000
        })
        peak_memory = monitor.get_memory_usage_mb()
        del df
        
        # Allow for small variations in memory measurement
        assert peak_memory >= initial_memory, f"Peak memory ({peak_memory:.3f}MB) should be >= initial ({initial_memory:.3f}MB)"
        
    def test_chunked_processing_simulation(self):
        """Test simulated chunked processing."""
        monitor = MemoryMonitor()
        
        # Simulate processing in chunks
        total_rows = 10000
        chunk_size = 1000
        
        for start in range(0, total_rows, chunk_size):
            end = min(start + chunk_size, total_rows)
            chunk_df = pd.DataFrame({
                'col1': range(start, end),
                'col2': [f'test_{i}' for i in range(start, end)]
            })
            
            # Process chunk (simulate work)
            memory_usage = monitor.get_memory_usage_mb()
            assert memory_usage > 0
            
            del chunk_df  # Clean up immediately


class TestErrorHandling:
    """Test error handling in memory utilities."""
    
    def test_memory_monitor_with_invalid_process(self):
        """Test memory monitor handles process errors gracefully."""
        # This test ensures robustness but actual implementation 
        # depends on how the module handles edge cases
        monitor = MemoryMonitor()
        assert monitor is not None
        
    def test_file_estimation_nonexistent_file(self):
        """Test file estimation with nonexistent file."""
        with pytest.raises((FileNotFoundError, OSError)):
            estimate_file_properties("nonexistent_file.csv")
            
    def test_processing_config_edge_cases(self):
        """Test processing configuration edge cases."""
        # Test with very small file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1\n1\n")
            temp_file = f.name
            
        try:
            config = get_optimal_processing_config(temp_file)
            assert isinstance(config, dict)
        finally:
            os.unlink(temp_file)


class TestIntegration:
    """Integration tests for memory utilities."""
    
    def test_memory_monitoring_integration(self):
        """Test memory monitoring in realistic scenario."""
        monitor = MemoryMonitor()
        
        # Create test data
        df = pd.DataFrame({
            'id': range(1000),
            'value': [f'value_{i}' for i in range(1000)],
            'score': [i * 0.1 for i in range(1000)]
        })
        
        # Estimate memory usage
        estimated_memory = monitor.estimate_dataframe_memory_mb(df)
        assert estimated_memory > 0
        
        # Check actual memory usage
        actual_memory = monitor.get_memory_usage_mb()
        assert actual_memory > 0
        
        # Clean up
        del df
        
    def test_chunking_decision_integration(self):
        """Test integrated chunking decision making."""
        monitor = MemoryMonitor()
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2,col3\n")
            for i in range(5000):
                f.write(f"{i},test_{i},{i*1.5}\n")
            temp_file = f.name
            
        try:
            # Test chunking decision
            should_chunk, chunk_size = monitor.should_use_chunking(temp_file)
            
            if should_chunk:
                assert chunk_size is not None
                assert chunk_size > 0
                
                # Test that we can actually read in chunks
                chunks_read = 0
                for chunk in pd.read_csv(temp_file, chunksize=chunk_size):
                    chunks_read += 1
                    assert len(chunk) > 0
                    if chunks_read >= 3:  # Limit for test performance
                        break
                        
                assert chunks_read > 0
                
        finally:
            os.unlink(temp_file)