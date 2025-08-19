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
