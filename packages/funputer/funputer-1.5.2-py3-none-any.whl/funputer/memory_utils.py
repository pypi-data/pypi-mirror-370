"""
Memory usage monitoring and optimization utilities.
Provides tools for tracking memory usage and determining optimal processing strategies.
"""

import psutil
import pandas as pd
import os
import warnings
from typing import Optional, Dict, Any, Tuple
from pathlib import Path


class MemoryMonitor:
    """Monitor memory usage and provide processing recommendations."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage_mb()
        
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_available_memory_mb(self) -> float:
        """Get available system memory in MB."""
        return psutil.virtual_memory().available / 1024 / 1024
    
    def get_memory_increase_mb(self) -> float:
        """Get memory increase since monitor creation."""
        return self.get_memory_usage_mb() - self.initial_memory
    
    def estimate_dataframe_memory_mb(self, df: pd.DataFrame) -> float:
        """Estimate DataFrame memory usage in MB."""
        return df.memory_usage(deep=True).sum() / 1024 / 1024
    
    def should_use_chunking(
        self, 
        file_path: str, 
        available_memory_threshold: float = 100.0
    ) -> Tuple[bool, Optional[int]]:
        """
        Determine if chunking should be used based on file size and available memory.
        
        Args:
            file_path: Path to the data file
            available_memory_threshold: Minimum MB to keep available
            
        Returns:
            Tuple of (should_chunk, recommended_chunk_size)
        """
        try:
            file_size_mb = Path(file_path).stat().st_size / 1024 / 1024
            available_memory = self.get_available_memory_mb()
            
            # Trigger chunking for files > 10MB
            if file_size_mb > 10:
                # Adaptive chunk sizing based on file size
                if file_size_mb < 50:
                    base_chunk_size = 5000
                elif file_size_mb < 100:
                    base_chunk_size = 10000
                else:
                    base_chunk_size = 20000
                
                # Adjust based on available memory
                memory_factor = min(available_memory / 1000, 2.0)
                chunk_size = int(base_chunk_size * memory_factor)
                chunk_size = max(1000, min(chunk_size, 100000))
                
                return True, chunk_size
            
            # Also trigger chunking if available memory is very low
            if available_memory < available_memory_threshold * 2:
                return True, 5000
            
            return False, None
            
        except Exception:
            return False, None
    
    def warn_if_memory_high(self, threshold_pct: float = 80.0) -> None:
        """Issue warning if memory usage is high."""
        current = self.get_memory_usage_mb()
        available = self.get_available_memory_mb()
        
        # Get total system memory
        total_memory = psutil.virtual_memory().total / 1024 / 1024
        usage_pct = (current / total_memory) * 100 if total_memory > 0 else 0
        
        # Warn if usage is high
        if usage_pct > threshold_pct:
            warnings.warn(f"High memory usage: {usage_pct:.1f}%")
        
        if available < 200:
            warnings.warn(f"Low available memory: only {available:.1f}MB free")


def get_optimal_processing_config(
    file_path: str, 
    target_columns: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get optimal processing configuration based on system resources and data size.
    
    Args:
        file_path: Path to the data file
        target_columns: Expected number of columns to process
        
    Returns:
        Dictionary with processing recommendations
    """
    monitor = MemoryMonitor()
    should_chunk, chunk_size = monitor.should_use_chunking(file_path)
    
    config = {
        'use_chunking': should_chunk,
        'chunk_size': chunk_size,
        'current_memory_mb': monitor.get_memory_usage_mb(),
        'available_memory_mb': monitor.get_available_memory_mb(),
    }
    
    # Add parallelization recommendations
    cpu_count = psutil.cpu_count()
    if target_columns and target_columns >= 4:
        max_workers = min(cpu_count, target_columns, 8)
        config['use_parallel'] = max_workers > 1
        config['max_workers'] = max_workers
    else:
        config['use_parallel'] = False
        config['max_workers'] = 1
    
    return config


def estimate_file_properties(file_path: str, sample_size: int = 1000) -> Dict[str, Any]:
    """
    Estimate file properties by sampling the first few rows.
    
    Args:
        file_path: Path to the CSV file
        sample_size: Number of rows to sample
        
    Returns:
        Dictionary with estimated properties
        
    Raises:
        FileNotFoundError: If file doesn't exist
        OSError: If file cannot be read
    """
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"No such file or directory: '{file_path}'")
    
    if not file_path_obj.is_file():
        raise OSError(f"Not a regular file: '{file_path}'")
    
    try:
        sample_df = pd.read_csv(file_path, nrows=sample_size)
        
        properties = {
            'estimated_columns': len(sample_df.columns),
            'sample_rows': len(sample_df),
            'sample_memory_mb': sample_df.memory_usage(deep=True).sum() / 1024 / 1024,
        }
        
        # Estimate total rows based on file size
        file_size_bytes = file_path_obj.stat().st_size
        if len(sample_df) > 0:
            sample_size_bytes = len(sample_df.to_csv(index=False).encode())
            bytes_per_row = sample_size_bytes / len(sample_df)
            
            properties['estimated_total_rows'] = int(file_size_bytes / bytes_per_row)
            properties['estimated_total_memory_mb'] = (
                properties['sample_memory_mb'] * 
                properties['estimated_total_rows'] / len(sample_df)
            )
        
        return properties
        
    except (FileNotFoundError, OSError):
        raise
    except Exception as e:
        raise OSError(f"Failed to read file properties: {e}") from e