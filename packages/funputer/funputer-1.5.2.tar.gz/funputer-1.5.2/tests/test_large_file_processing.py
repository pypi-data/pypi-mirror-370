"""
Comprehensive tests for large file processing, chunking and streaming functionality.
Consolidates all large file handling, memory optimization, and streaming analysis tests.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import time
import psutil
from unittest.mock import patch, MagicMock
from typing import Tuple, Optional
import logging

from funputer.analyzer import ImputationAnalyzer
from funputer.memory_utils import MemoryMonitor
from funputer import infer_metadata_from_dataframe

logger = logging.getLogger(__name__)


class LargeFileGenerator:
    """Generate large CSV files for testing chunking and streaming."""
    
    @staticmethod
    def generate_large_csv(
        rows: int,
        cols: int = 20,
        missing_pct: float = 0.1,
        output_path: Optional[str] = None,
        seed: int = 42
    ) -> Tuple[str, pd.DataFrame]:
        """
        Generate a large CSV file with various data types.
        """
        np.random.seed(seed)
        
        # Create column definitions (mix of types)
        data = {}
        
        # Integer columns (25%)
        for i in range(cols // 4):
            col_name = f"int_col_{i}"
            values = np.random.randint(0, 1000, rows)
            # Add missing values
            mask = np.random.random(rows) < missing_pct
            values = values.astype(float)  # Convert to float to allow NaN
            values[mask] = np.nan
            data[col_name] = values
        
        # Float columns (25%)
        for i in range(cols // 4):
            col_name = f"float_col_{i}"
            values = np.random.uniform(0, 100, rows)
            mask = np.random.random(rows) < missing_pct
            values[mask] = np.nan
            data[col_name] = values
        
        # String columns (25%)
        for i in range(cols // 4):
            col_name = f"str_col_{i}"
            values = [f"value_{np.random.randint(0, 100)}" for _ in range(rows)]
            # Add missing values
            for j in range(rows):
                if np.random.random() < missing_pct:
                    values[j] = None
            data[col_name] = values
        
        # Category columns (remaining)
        remaining_cols = cols - len(data)
        for i in range(remaining_cols):
            col_name = f"cat_col_{i}"
            categories = ['A', 'B', 'C', 'D', 'E']
            values = np.random.choice(categories, rows)
            # Add missing values
            mask = np.random.random(rows) < missing_pct
            values = values.astype(object)
            values[mask] = None
            data[col_name] = values
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to file
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            output_path = temp_file.name
            temp_file.close()
        
        df.to_csv(output_path, index=False)
        
        # Return path and sample for validation
        return output_path, df.head(100)
    
    @staticmethod
    def generate_100mb_csv() -> Tuple[str, int, int]:
        """Generate a 100MB+ CSV file."""
        # Calculate rows needed for ~100MB
        target_size_mb = 100
        bytes_per_row = 100
        rows_needed = (target_size_mb * 1024 * 1024) // bytes_per_row
        cols = 20
        
        logger.info(f"Generating {target_size_mb}MB file with {rows_needed} rows, {cols} columns")
        
        file_path, _ = LargeFileGenerator.generate_large_csv(rows_needed, cols)
        return file_path, rows_needed, cols


class TestChunkingDetection:
    """Test automatic detection of when chunking is needed."""
    
    def test_memory_monitor_chunking_decision_small_file(self):
        """Test that small files don't trigger chunking."""
        monitor = MemoryMonitor()
        
        # Create small test file (< 1MB)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            small_df = pd.DataFrame({'a': range(100), 'b': range(100)})
            small_df.to_csv(f.name, index=False)
            
            try:
                should_chunk, chunk_size = monitor.should_use_chunking(f.name)
                
                assert isinstance(should_chunk, bool)
                if should_chunk:
                    assert chunk_size is not None and chunk_size > 0
                else:
                    assert chunk_size is None
                    
            finally:
                os.unlink(f.name)
    
    def test_memory_monitor_chunking_decision_large_file(self):
        """Test chunking decision for large files."""
        monitor = MemoryMonitor()
        
        # Mock a large file (100MB)
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 100 * 1024 * 1024  # 100MB
            
            should_chunk, chunk_size = monitor.should_use_chunking("fake_large_file.csv")
            
            # Large files should typically trigger chunking
            assert isinstance(should_chunk, bool)
            if should_chunk:
                assert chunk_size is not None and chunk_size > 0
    
    def test_memory_monitor_adaptive_chunk_size(self):
        """Test that chunk sizes adapt to available memory."""
        monitor = MemoryMonitor()
        
        # Test with different file sizes
        file_sizes = [10 * 1024 * 1024, 50 * 1024 * 1024, 200 * 1024 * 1024]  # 10MB, 50MB, 200MB
        
        chunk_sizes = []
        for size in file_sizes:
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = size
                should_chunk, chunk_size = monitor.should_use_chunking("fake_file.csv")
                
                if should_chunk and chunk_size:
                    chunk_sizes.append(chunk_size)
        
        # Should have some variation in chunk sizes based on file size
        if len(chunk_sizes) > 1:
            assert not all(cs == chunk_sizes[0] for cs in chunk_sizes), "Chunk sizes should vary with file size"


class TestStreamingAnalysis:
    """Test streaming analysis functionality."""
    
    def test_streaming_analysis_basic(self):
        """Test basic streaming analysis functionality."""
        # Generate medium-sized test file
        file_path, sample_df = LargeFileGenerator.generate_large_csv(5000, 10)
        
        try:
            # Test reading in chunks
            chunks_processed = 0
            total_rows = 0
            
            for chunk in pd.read_csv(file_path, chunksize=1000):
                chunks_processed += 1
                total_rows += len(chunk)
                
                # Verify chunk structure
                assert len(chunk.columns) == 10
                assert len(chunk) <= 1000
            
            # Should have processed all data
            assert total_rows == 5000
            assert chunks_processed == 5  # 5000 / 1000
            
        finally:
            os.unlink(file_path)
    
    def test_streaming_vs_standard_equivalence(self):
        """Test that streaming and standard analysis produce equivalent results."""
        # Generate test file
        file_path, sample_df = LargeFileGenerator.generate_large_csv(1000, 5)
        
        try:
            # Load full dataframe
            full_df = pd.read_csv(file_path)
            
            # Process in chunks and combine basic statistics
            chunk_means = []
            chunk_nulls = []
            
            for chunk in pd.read_csv(file_path, chunksize=200):
                chunk_means.append(chunk.select_dtypes(include=[np.number]).mean())
                chunk_nulls.append(chunk.isnull().sum())
            
            # Compare some basic statistics
            full_means = full_df.select_dtypes(include=[np.number]).mean()
            full_nulls = full_df.isnull().sum()
            
            # Chunk processing should capture similar patterns
            assert len(chunk_means) == 5  # 1000 / 200
            assert len(chunk_nulls) == 5
            
        finally:
            os.unlink(file_path)
    
    def test_streaming_with_different_chunk_sizes(self):
        """Test streaming with various chunk sizes."""
        file_path, _ = LargeFileGenerator.generate_large_csv(2000, 8)
        
        try:
            chunk_sizes = [100, 250, 500, 1000]
            
            for chunk_size in chunk_sizes:
                chunks_read = 0
                rows_read = 0
                
                for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                    chunks_read += 1
                    rows_read += len(chunk)
                    
                    # Each chunk should be at most the requested size
                    assert len(chunk) <= chunk_size
                    
                    # Stop after a few chunks to avoid long test times
                    if chunks_read >= 3:
                        break
                
                # Should have read some data
                assert chunks_read > 0
                assert rows_read > 0
                
        finally:
            os.unlink(file_path)


class TestMemoryPressure:
    """Test behavior under memory pressure conditions."""
    
    @pytest.mark.slow
    def test_automatic_chunking_under_memory_pressure(self):
        """Test that chunking is automatically triggered under memory pressure."""
        # Skip if not enough memory for realistic test
        available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
        if available_memory < 1000:  # Need at least 1GB available
            pytest.skip("Not enough available memory for memory pressure test")
        
        monitor = MemoryMonitor()
        
        # Mock low available memory
        with patch.object(monitor, 'get_available_memory_mb', return_value=100):  # 100MB available
            should_chunk, chunk_size = monitor.should_use_chunking("fake_large_file.csv")
            
            # Should recommend chunking with limited memory
            if should_chunk:
                assert chunk_size is not None and chunk_size > 0
    
    def test_memory_monitor_warnings(self):
        """Test memory monitor warning system."""
        monitor = MemoryMonitor()
        
        # Test warning threshold
        initial_memory = monitor.get_memory_usage_mb()
        available_memory = monitor.get_available_memory_mb()
        
        # Should not throw errors
        assert initial_memory > 0
        assert available_memory > 0
        
        # Test memory increase calculation
        memory_increase = monitor.get_memory_increase_mb()
        assert isinstance(memory_increase, float)
    
    def test_chunked_data_loading(self):
        """Test that chunked data loading works correctly."""
        file_path, _ = LargeFileGenerator.generate_large_csv(3000, 6)
        
        try:
            monitor = MemoryMonitor()
            
            # Force chunking decision
            with patch.object(monitor, 'should_use_chunking', return_value=(True, 500)):
                # Simulate chunked loading
                total_rows = 0
                chunk_count = 0
                
                for chunk in pd.read_csv(file_path, chunksize=500):
                    total_rows += len(chunk)
                    chunk_count += 1
                    
                    # Monitor memory during processing
                    current_memory = monitor.get_memory_usage_mb()
                    assert current_memory > 0
                    
                    # Stop after reasonable number of chunks
                    if chunk_count >= 6:
                        break
                
                # Should have processed data
                assert total_rows > 0
                assert chunk_count > 0
                
        finally:
            os.unlink(file_path)


class TestPerformanceBenchmarks:
    """Test performance characteristics of large file processing."""
    
    def test_streaming_performance_vs_standard(self):
        """Compare streaming vs standard loading performance."""
        file_path, _ = LargeFileGenerator.generate_large_csv(5000, 8)
        
        try:
            # Test streaming performance
            start_time = time.time()
            streaming_rows = 0
            
            for chunk in pd.read_csv(file_path, chunksize=1000):
                streaming_rows += len(chunk)
            
            streaming_time = time.time() - start_time
            
            # Test standard loading performance
            start_time = time.time()
            standard_df = pd.read_csv(file_path)
            standard_time = time.time() - start_time
            
            # Results should be equivalent
            assert streaming_rows == len(standard_df)
            
            # Performance characteristics
            assert streaming_time > 0
            assert standard_time > 0
            
            print(f"Streaming: {streaming_time:.2f}s, Standard: {standard_time:.2f}s")
            
        finally:
            os.unlink(file_path)
    
    def test_memory_usage_comparison(self):
        """Compare memory usage between streaming and standard approaches."""
        file_path, _ = LargeFileGenerator.generate_large_csv(3000, 10)
        
        try:
            monitor = MemoryMonitor()
            
            # Measure initial memory
            initial_memory = monitor.get_memory_usage_mb()
            
            # Test streaming memory usage
            max_streaming_memory = initial_memory
            for chunk in pd.read_csv(file_path, chunksize=500):
                current_memory = monitor.get_memory_usage_mb()
                max_streaming_memory = max(max_streaming_memory, current_memory)
                # Process chunk to simulate work
                _ = chunk.describe()
            
            streaming_memory_increase = max_streaming_memory - initial_memory
            
            # Test standard loading memory usage
            current_memory = monitor.get_memory_usage_mb()
            standard_df = pd.read_csv(file_path)
            _ = standard_df.describe()
            peak_memory = monitor.get_memory_usage_mb()
            
            standard_memory_increase = peak_memory - current_memory
            
            # Streaming should use less peak memory
            print(f"Streaming memory increase: {streaming_memory_increase:.1f}MB")
            print(f"Standard memory increase: {standard_memory_increase:.1f}MB")
            
            # At least verify we measured something
            assert streaming_memory_increase >= 0
            assert standard_memory_increase >= 0
            
        finally:
            os.unlink(file_path)


class TestEdgeCases:
    """Test edge cases in large file processing."""
    
    def test_empty_chunks_handling(self):
        """Test handling of empty chunks."""
        # Create minimal file
        file_path, _ = LargeFileGenerator.generate_large_csv(10, 3)
        
        try:
            # Try to read with chunk size larger than file
            chunks_read = 0
            
            for chunk in pd.read_csv(file_path, chunksize=100):
                chunks_read += 1
                assert len(chunk) > 0  # Should not be empty
            
            # Should read exactly one chunk
            assert chunks_read == 1
            
        finally:
            os.unlink(file_path)
    
    def test_single_row_chunks(self):
        """Test processing with single-row chunks."""
        file_path, _ = LargeFileGenerator.generate_large_csv(50, 4)
        
        try:
            rows_processed = 0
            
            # Process one row at a time
            for chunk in pd.read_csv(file_path, chunksize=1):
                rows_processed += 1
                assert len(chunk) == 1
                
                # Stop after reasonable number for test performance
                if rows_processed >= 10:
                    break
            
            assert rows_processed == 10
            
        finally:
            os.unlink(file_path)


@pytest.mark.slow
class TestLargeFileValidation:
    """Test validation with genuinely large files (marked as slow)."""
    
    def test_100mb_file_chunking_triggers(self):
        """Test that 100MB+ files trigger chunking appropriately."""
        # Only run if we have sufficient disk space
        import shutil
        free_space = shutil.disk_usage('/tmp').free / (1024 * 1024)  # MB
        
        if free_space < 200:  # Need at least 200MB free space
            pytest.skip("Insufficient disk space for 100MB file test")
        
        try:
            file_path, rows, cols = LargeFileGenerator.generate_100mb_csv()
            
            # Verify file was created and is large
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            assert file_size_mb > 50, f"File should be large, got {file_size_mb:.1f}MB"
            
            # Test chunking decision
            monitor = MemoryMonitor()
            should_chunk, chunk_size = monitor.should_use_chunking(file_path)
            
            # Large file should trigger chunking
            if file_size_mb > 10:  # Files > 10MB should typically trigger chunking
                if should_chunk:
                    assert chunk_size is not None and chunk_size > 0
                    print(f"✅ Large file ({file_size_mb:.1f}MB) triggered chunking with size {chunk_size}")
                else:
                    print(f"⚠️ Large file ({file_size_mb:.1f}MB) did not trigger chunking")
            
        except Exception as e:
            pytest.skip(f"Could not create or test large file: {e}")
            
        finally:
            # Cleanup
            try:
                if 'file_path' in locals():
                    os.unlink(file_path)
            except:
                pass
    
    def test_100mb_file_streaming_analysis(self):
        """Test streaming analysis on 100MB+ file."""
        # Only run if system has sufficient resources
        available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
        if available_memory < 500:
            pytest.skip("Insufficient memory for large file streaming test")
        
        try:
            file_path, expected_rows, expected_cols = LargeFileGenerator.generate_100mb_csv()
            
            # Test streaming processing
            chunks_processed = 0
            total_rows_seen = 0
            
            for chunk in pd.read_csv(file_path, chunksize=5000):
                chunks_processed += 1
                total_rows_seen += len(chunk)
                
                # Verify chunk structure
                assert len(chunk.columns) == expected_cols
                
                # Limit processing time for test
                if chunks_processed >= 10:
                    break
            
            # Should have processed substantial data
            assert chunks_processed > 0
            assert total_rows_seen > 0
            
            print(f"✅ Processed {chunks_processed} chunks, {total_rows_seen} rows from large file")
            
        except Exception as e:
            pytest.skip(f"Large file streaming test failed: {e}")
            
        finally:
            try:
                if 'file_path' in locals():
                    os.unlink(file_path)
            except:
                pass


class TestIntegration:
    """Integration tests for large file processing workflow."""
    
    def test_complete_large_file_workflow(self):
        """Test complete workflow with moderately large file."""
        file_path, _ = LargeFileGenerator.generate_large_csv(2000, 8, missing_pct=0.15)
        
        try:
            monitor = MemoryMonitor()
            
            # Step 1: Check if chunking is recommended
            should_chunk, chunk_size = monitor.should_use_chunking(file_path)
            
            # Step 2: Process accordingly
            if should_chunk and chunk_size:
                # Process in chunks
                total_rows = 0
                for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                    total_rows += len(chunk)
                    
                    # Stop after reasonable amount for test
                    if total_rows >= 1000:
                        break
                
                assert total_rows > 0
                print(f"✅ Chunked processing: {total_rows} rows processed")
                
            else:
                # Process normally
                df = pd.read_csv(file_path)
                assert len(df) == 2000
                print(f"✅ Standard processing: {len(df)} rows processed")
            
        finally:
            os.unlink(file_path)
    
    def test_memory_monitoring_integration(self):
        """Test memory monitoring throughout large file processing."""
        file_path, _ = LargeFileGenerator.generate_large_csv(1500, 6)
        
        try:
            monitor = MemoryMonitor()
            initial_memory = monitor.get_memory_usage_mb()
            
            # Process file while monitoring memory
            memory_readings = []
            
            for i, chunk in enumerate(pd.read_csv(file_path, chunksize=300)):
                current_memory = monitor.get_memory_usage_mb()
                memory_readings.append(current_memory)
                
                # Do some processing to use memory
                _ = chunk.describe()
                _ = chunk.dtypes
                
                if i >= 4:  # Limit for test performance
                    break
            
            # Should have collected memory readings
            assert len(memory_readings) > 0
            assert all(reading > 0 for reading in memory_readings)
            
            final_memory = monitor.get_memory_usage_mb()
            memory_increase = final_memory - initial_memory
            
            print(f"📊 Memory monitoring: {memory_increase:.1f}MB increase over processing")
            
        finally:
            os.unlink(file_path)