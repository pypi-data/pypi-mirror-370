"""
Performance optimization utilities for QuickInsights.

This module provides performance-related utilities including:
- Lazy evaluation and caching
- Parallel processing
- Memory optimization
- Performance profiling
- Benchmark utilities
"""

import time
import functools
import threading
from typing import Any, Callable, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np
import pandas as pd

# Performance constants
CACHE_SIZE = 1000
CACHE_TTL = 3600  # 1 hour
MAX_WORKERS = 4
CHUNK_SIZE = 10000

# Global cache
_cache: Dict[str, Any] = {}
_cache_timestamps: Dict[str, float] = {}
_cache_lock = threading.Lock()


def get_performance_utils():
    """Lazy import for performance utilities."""
    return {
        "lazy_evaluate": lazy_evaluate,
        "cache_result": cache_result,
        "parallel_process": parallel_process,
        "chunked_process": chunked_process,
        "memory_optimize": memory_optimize,
        "performance_profile": performance_profile,
        "benchmark_function": benchmark_function,
    }


def lazy_evaluate(func: Callable) -> Callable:
    """
    Decorator for lazy evaluation of functions.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function that evaluates lazily
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Store the function call for later evaluation
        return lambda: func(*args, **kwargs)

    # Test if the function is callable
    if not callable(func):
        raise TypeError("lazy_evaluate can only be applied to callable objects")

    return wrapper


def cache_result(ttl: int = CACHE_TTL, max_size: int = CACHE_SIZE):
    """
    Decorator for caching function results.

    Args:
        ttl: Time to live in seconds
        max_size: Maximum cache size

    Returns:
        Decorated function with caching
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            args_str = str(args)
            kwargs_str = str(sorted(kwargs.items()))
            key = f"{func.__name__}:{hash(args_str + kwargs_str)}"

            with _cache_lock:
                # Check if result exists and is not expired
                if key in _cache:
                    if time.time() - _cache_timestamps[key] < ttl:
                        return _cache[key]
                    else:
                        # Remove expired entry
                        del _cache[key]
                        del _cache_timestamps[key]

                # Clean up old entries if cache is full
                if len(_cache) >= max_size:
                    _cleanup_old_cache(ttl)

                # Execute function and cache result
                result = func(*args, **kwargs)
                _cache[key] = result
                _cache_timestamps[key] = time.time()

                return result

        return wrapper

    return decorator


def _cleanup_old_cache(ttl: int):
    """Clean up expired cache entries."""
    current_time = time.time()
    expired_keys = [
        key
        for key, timestamp in _cache_timestamps.items()
        if current_time - timestamp > ttl
    ]

    for key in expired_keys:
        del _cache[key]
        del _cache_timestamps[key]


def parallel_process(
    func: Callable,
    data: List[Any],
    max_workers: int = MAX_WORKERS,
    use_processes: bool = False,
) -> List[Any]:
    """
    Process data in parallel using threads or processes.

    Args:
        func: Function to apply to each item
        data: List of data items
        max_workers: Maximum number of workers
        use_processes: Use ProcessPoolExecutor if True, ThreadPoolExecutor otherwise

    Returns:
        List of processed results
    """
    executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    with executor_class(max_workers=max_workers) as executor:
        results = list(executor.map(func, data))

    return results


def chunked_process(
    func: Callable,
    data: Union[pd.DataFrame, np.ndarray, List[Any]],
    chunk_size: int = CHUNK_SIZE,
    max_workers: int = MAX_WORKERS,
) -> List[Any]:
    """
    Process large datasets in chunks.

    Args:
        func: Function to apply to each chunk
        data: Data to process
        chunk_size: Size of each chunk
        max_workers: Maximum number of workers

    Returns:
        List of processed chunk results
    """
    # Validate input data
    if not hasattr(data, "__len__"):
        raise TypeError("Data must have a length (DataFrame, array, or list)")

    if isinstance(data, pd.DataFrame):
        chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
    elif isinstance(data, np.ndarray):
        chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
    else:
        chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, chunks))

    return results


def memory_optimize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage.

    Args:
        df: Input DataFrame

    Returns:
        Memory-optimized DataFrame
    """
    optimized_df = df.copy()

    for col in optimized_df.columns:
        col_type = optimized_df[col].dtype

        if col_type != "object":
            c_min = optimized_df[col].min()
            c_max = optimized_df[col].max()

            if str(col_type)[:3] == "int":
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    optimized_df[col] = optimized_df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    optimized_df[col] = optimized_df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    optimized_df[col] = optimized_df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    optimized_df[col] = optimized_df[col].astype(np.int64)
            else:
                if (
                    c_min > np.finfo(np.float16).min
                    and c_max < np.finfo(np.float16).max
                ):
                    optimized_df[col] = optimized_df[col].astype(np.float16)
                elif (
                    c_min > np.finfo(np.float32).min
                    and c_max < np.finfo(np.float32).max
                ):
                    optimized_df[col] = optimized_df[col].astype(np.float32)
                else:
                    optimized_df[col] = optimized_df[col].astype(np.float64)
        else:
            optimized_df[col] = optimized_df[col].astype("category")

    return optimized_df


def performance_profile(func: Callable) -> Callable:
    """
    Decorator to profile function performance.

    Args:
        func: Function to profile

    Returns:
        Wrapped function with performance profiling
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = _get_memory_usage()

        result = func(*args, **kwargs)

        end_time = time.time()
        end_memory = _get_memory_usage()

        execution_time = end_time - start_time
        memory_used = end_memory - start_memory

        print(f"⚡ Performance Profile for {func.__name__}:")
        print(f"   ⏱️  Execution Time: {execution_time:.4f}s")
        print(f"   💾 Memory Used: {memory_used:.2f} MB")

        return result

    return wrapper


def benchmark_function(
    func: Callable, test_data: Any, iterations: int = 100, warmup: int = 10
) -> Dict[str, float]:
    """
    Benchmark a function's performance.

    Args:
        func: Function to benchmark
        test_data: Test data to use
        iterations: Number of iterations for benchmarking
        warmup: Number of warmup runs

    Returns:
        Dictionary with benchmark results
    """
    # Warmup runs
    for _ in range(warmup):
        try:
            func(test_data)
        except TypeError:
            # Function doesn't take arguments, call without
            func()

    # Actual benchmark
    times = []
    for _ in range(iterations):
        start_time = time.time()
        try:
            func(test_data)
        except TypeError:
            # Function doesn't take arguments, call without
            func()
        end_time = time.time()
        times.append(end_time - start_time)

    times = np.array(times)

    return {
        "mean_time": float(np.mean(times)),
        "std_time": float(np.std(times)),
        "min_time": float(np.min(times)),
        "max_time": float(np.max(times)),
        "total_time": float(np.sum(times)),
    }


def _get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil

        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0


# Performance status functions
def get_lazy_evaluation_status() -> bool:
    """Check if lazy evaluation is available."""
    return True


def get_caching_status() -> bool:
    """Check if caching is available."""
    return True


def get_parallel_processing_status() -> bool:
    """Check if parallel processing is available."""
    return True


def get_chunked_processing_status() -> bool:
    """Check if chunked processing is available."""
    return True


def get_memory_optimization_status() -> bool:
    """Check if memory optimization is available."""
    return True


def get_performance_profiling_status() -> bool:
    """Check if performance profiling is available."""
    return True


def get_benchmark_status() -> bool:
    """Check if benchmarking is available."""
    return True


def memory_usage(data: Any) -> Dict[str, Any]:
    """
    Analyze memory usage of data structures.
    
    Args:
        data: Data to analyze (numpy array, pandas DataFrame, etc.)
        
    Returns:
        Dictionary with memory usage information
    """
    try:
        import psutil
        
        # Get current process memory
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # Analyze data memory
        if hasattr(data, 'nbytes'):
            data_memory = data.nbytes
        elif hasattr(data, 'memory_usage'):
            data_memory = data.memory_usage(deep=True).sum()
        else:
            data_memory = 0
        
        # Get system memory info
        system_memory = psutil.virtual_memory()
        
        results = {
            'data_memory_bytes': data_memory,
            'data_memory_mb': data_memory / (1024 * 1024),
            'data_memory_gb': data_memory / (1024 * 1024 * 1024),
            'process_memory_rss': process_memory.rss,
            'process_memory_vms': process_memory.vms,
            'system_memory_total': system_memory.total,
            'system_memory_available': system_memory.available,
            'system_memory_percent': system_memory.percent,
            'memory_efficiency': (data_memory / process_memory.rss) * 100 if process_memory.rss > 0 else 0
        }
        
        # Add data type specific information
        if hasattr(data, 'dtype'):
            results['data_type'] = str(data.dtype)
        if hasattr(data, 'shape'):
            results['data_shape'] = data.shape
        if hasattr(data, 'size'):
            results['data_size'] = data.size
            
        return results
        
    except ImportError:
        print("⚠️  psutil not available, returning basic memory info")
        return {
            'data_memory_bytes': getattr(data, 'nbytes', 0),
            'data_memory_mb': getattr(data, 'nbytes', 0) / (1024 * 1024),
            'error': 'psutil not available'
        }
    except Exception as e:
        return {'error': str(e)}


def measure_execution_time(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Measure execution time of a function.
    
    Args:
        func: Function to measure
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Dictionary with execution time information
    """
    try:
        import psutil
        
        # Get initial memory and CPU
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        initial_cpu = process.cpu_percent()
        
        # Measure execution time
        start_time = time.time()
        start_cpu = time.time()
        
        # Execute function
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_cpu = time.time()
        
        # Get final memory and CPU
        final_memory = process.memory_info().rss
        final_cpu = process.cpu_percent()
        
        execution_time = end_time - start_time
        cpu_time = end_cpu - start_cpu
        
        # Calculate memory delta
        memory_delta = final_memory - initial_memory
        
        results = {
            'execution_time_seconds': execution_time,
            'execution_time_ms': execution_time * 1000,
            'cpu_time_seconds': cpu_time,
            'memory_delta_bytes': memory_delta,
            'memory_delta_mb': memory_delta / (1024 * 1024),
            'initial_memory_mb': initial_memory / (1024 * 1024),
            'final_memory_mb': final_memory / (1024 * 1024),
            'function_name': func.__name__,
            'function_result': result,
            'performance_score': 1.0 / execution_time if execution_time > 0 else float('inf')
        }
        
        # Add performance categorization
        if execution_time < 0.001:
            results['performance_category'] = 'Excellent (< 1ms)'
        elif execution_time < 0.01:
            results['performance_category'] = 'Good (< 10ms)'
        elif execution_time < 0.1:
            results['performance_category'] = 'Fair (< 100ms)'
        elif execution_time < 1.0:
            results['performance_category'] = 'Slow (< 1s)'
        else:
            results['performance_category'] = 'Very Slow (≥ 1s)'
        
        return results
        
    except Exception as e:
        return {'error': str(e)}


def cpu_usage() -> Dict[str, Any]:
    """
    Get current CPU usage information.
    
    Returns:
        Dictionary with CPU usage information
    """
    try:
        import psutil
        
        # Get CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Get per-CPU usage
        per_cpu = psutil.cpu_percent(interval=1, percpu=True)
        
        # Get CPU times
        cpu_times = psutil.cpu_times()
        
        results = {
            'cpu_percent_total': cpu_percent,
            'cpu_count': cpu_count,
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'per_cpu_usage': per_cpu,
            'cpu_freq_current': cpu_freq.current if cpu_freq else None,
            'cpu_freq_min': cpu_freq.min if cpu_freq else None,
            'cpu_freq_max': cpu_freq.max if cpu_freq else None,
            'cpu_times_user': cpu_times.user,
            'cpu_times_system': cpu_times.system,
            'cpu_times_idle': cpu_times.idle,
            'cpu_times_iowait': getattr(cpu_times, 'iowait', 0),
            'cpu_times_irq': getattr(cpu_times, 'irq', 0),
            'cpu_times_softirq': getattr(cpu_times, 'softirq', 0),
            'cpu_times_steal': getattr(cpu_times, 'steal', 0),
            'cpu_times_guest': getattr(cpu_times, 'guest', 0),
            'cpu_times_guest_nice': getattr(cpu_times, 'guest_nice', 0)
        }
        
        # Calculate CPU utilization
        total_time = sum(cpu_times)
        if total_time > 0:
            results['cpu_utilization'] = {
                'user_percent': (cpu_times.user / total_time) * 100,
                'system_percent': (cpu_times.system / total_time) * 100,
                'idle_percent': (cpu_times.idle / total_time) * 100,
                'iowait_percent': (getattr(cpu_times, 'iowait', 0) / total_time) * 100
            }
        
        # Add CPU load information
        try:
            load_avg = psutil.getloadavg()
            results['load_average'] = {
                '1_min': load_avg[0],
                '5_min': load_avg[1],
                '15_min': load_avg[2]
            }
        except AttributeError:
            results['load_average'] = None
        
        return results
        
    except ImportError:
        return {'error': 'psutil not available'}
    except Exception as e:
        return {'error': str(e)}


def optimization_suggestions(data: Any, operation_type: str = 'general') -> Dict[str, Any]:
    """
    Generate optimization suggestions for data and operations.
    
    Args:
        data: Data to analyze
        operation_type: Type of operation ('general', 'memory', 'speed', 'parallel')
        
    Returns:
        Dictionary with optimization suggestions
    """
    try:
        suggestions = {
            'operation_type': operation_type,
            'suggestions': [],
            'priority': [],
            'estimated_improvement': {},
            'implementation_difficulty': {}
        }
        
        # Analyze data characteristics
        data_size = 0
        data_type = 'unknown'
        is_sparse = False
        
        if hasattr(data, 'nbytes'):
            data_size = data.nbytes
            data_type = 'numpy_array'
        elif hasattr(data, 'memory_usage'):
            data_size = data.memory_usage(deep=True).sum()
            data_type = 'pandas_dataframe'
        elif hasattr(data, 'shape'):
            data_size = getattr(data, 'nbytes', 0)
            data_type = 'array_like'
        
        # Memory optimization suggestions
        if operation_type in ['general', 'memory']:
            if data_size > 100 * 1024 * 1024:  # > 100MB
                suggestions['suggestions'].append("Consider using memory mapping (np.memmap) for large arrays")
                suggestions['priority'].append("High")
                suggestions['estimated_improvement']['memory_mapping'] = "50-80% memory reduction"
                suggestions['implementation_difficulty']['memory_mapping'] = "Medium"
            
            if data_type == 'pandas_dataframe':
                suggestions['suggestions'].append("Use appropriate data types (int8, float32, category)")
                suggestions['priority'].append("Medium")
                suggestions['estimated_improvement']['data_types'] = "20-40% memory reduction"
                suggestions['implementation_difficulty']['data_types'] = "Low"
            
            if hasattr(data, 'dtype') and str(data.dtype) == 'object':
                suggestions['suggestions'].append("Convert object dtypes to specific types")
                suggestions['priority'].append("Medium")
                suggestions['estimated_improvement']['dtype_conversion'] = "30-60% memory reduction"
                suggestions['implementation_difficulty']['dtype_conversion'] = "Low"
        
        # Speed optimization suggestions
        if operation_type in ['general', 'speed']:
            if data_size > 50 * 1024 * 1024:  # > 50MB
                suggestions['suggestions'].append("Use vectorized operations instead of loops")
                suggestions['priority'].append("High")
                suggestions['estimated_improvement']['vectorization'] = "10-100x speed improvement"
                suggestions['implementation_difficulty']['vectorization'] = "Low"
            
            if hasattr(data, 'shape') and len(data.shape) > 2:
                suggestions['suggestions'].append("Consider flattening or reshaping for better performance")
                suggestions['priority'].append("Medium")
                suggestions['estimated_improvement']['reshaping'] = "2-5x speed improvement"
                suggestions['implementation_difficulty']['reshaping'] = "Low"
            
            suggestions['suggestions'].append("Use numba JIT compilation for custom functions")
            suggestions['priority'].append("Medium")
            suggestions['estimated_improvement']['numba'] = "2-10x speed improvement"
            suggestions['implementation_difficulty']['numba'] = "Medium"
        
        # Parallel processing suggestions
        if operation_type in ['general', 'parallel']:
            if data_size > 10 * 1024 * 1024:  # > 10MB
                suggestions['suggestions'].append("Use parallel processing for independent operations")
                suggestions['priority'].append("Medium")
                suggestions['estimated_improvement']['parallel'] = "2-8x speed improvement"
                suggestions['implementation_difficulty']['parallel'] = "Medium"
            
            suggestions['suggestions'].append("Consider using Dask for out-of-memory operations")
            suggestions['priority'].append("Low")
            suggestions['estimated_improvement']['dask'] = "Scalable to any data size"
            suggestions['implementation_difficulty']['dask'] = "High"
        
        # GPU acceleration suggestions
        if operation_type in ['general', 'speed']:
            try:
                import cupy
                suggestions['suggestions'].append("Use CuPy for GPU acceleration of numpy operations")
                suggestions['priority'].append("Medium")
                suggestions['estimated_improvement']['gpu'] = "5-20x speed improvement"
                suggestions['implementation_difficulty']['gpu'] = "Medium"
            except ImportError:
                suggestions['suggestions'].append("Install CuPy for GPU acceleration")
                suggestions['priority'].append("Low")
                suggestions['estimated_improvement']['gpu'] = "5-20x speed improvement"
                suggestions['implementation_difficulty']['gpu'] = "High"
        
        # Caching suggestions
        if operation_type in ['general', 'speed']:
            suggestions['suggestions'].append("Implement function result caching for repeated calls")
            suggestions['priority'].append("Low")
            suggestions['estimated_improvement']['caching'] = "2-10x speed improvement for repeated calls"
            suggestions['implementation_difficulty']['caching'] = "Low"
        
        # Chunking suggestions
        if data_size > 100 * 1024 * 1024:  # > 100MB
            suggestions['suggestions'].append("Process data in chunks to reduce memory pressure")
            suggestions['priority'].append("High")
            suggestions['estimated_improvement']['chunking'] = "Prevents out-of-memory errors"
            suggestions['implementation_difficulty']['chunking'] = "Medium"
        
        # Add data-specific suggestions
        if data_type == 'pandas_dataframe':
            if hasattr(data, 'columns') and len(data.columns) > 100:
                suggestions['suggestions'].append("Consider feature selection to reduce dimensionality")
                suggestions['priority'].append("Medium")
                suggestions['estimated_improvement']['feature_selection'] = "20-50% speed improvement"
                suggestions['implementation_difficulty']['feature_selection'] = "Medium"
        
        # Summary
        suggestions['summary'] = {
            'total_suggestions': len(suggestions['suggestions']),
            'high_priority': suggestions['priority'].count('High'),
            'medium_priority': suggestions['priority'].count('Medium'),
            'low_priority': suggestions['priority'].count('Low'),
            'estimated_total_improvement': "2-100x overall improvement potential"
        }
        
        return suggestions
        
    except Exception as e:
        return {'error': str(e)}
