"""
Big data processing utilities for QuickInsights.

This module provides utilities for handling large datasets including:
- Dask integration
- GPU acceleration
- Memory mapping
- Streaming data processing
- Distributed computing
"""

import os
import warnings
from typing import Any, Callable, Dict, List, Optional, Union, Generator
import numpy as np
import pandas as pd

# Big data constants
DEFAULT_CHUNK_SIZE = 10000
MAX_MEMORY_USAGE = 0.8  # 80% of available memory


def get_big_data_utils():
    """Lazy import for big data utilities."""
    return {
        "process_large_file": process_large_file,
        "stream_data": stream_data,
        "get_dask_status": get_dask_status,
        "get_gpu_status": get_gpu_status,
        "get_memory_mapping_status": get_memory_mapping_status,
        "get_distributed_status": get_distributed_status,
        "detect_engines": detect_engines,
        "select_dataframe_engine": select_dataframe_engine,
        "read_table_auto": read_table_auto,
    }


def process_large_file(
    file_path: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    processor: Optional[Callable] = None,
) -> Generator[pd.DataFrame, None, None]:
    """
    Process large files in chunks.

    Args:
        file_path: Path to the file to process
        chunk_size: Size of each chunk
        processor: Optional function to process each chunk

    Yields:
        DataFrame chunks
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Try to determine file type and use appropriate reader
        if file_path.endswith(".csv"):
            chunks = pd.read_csv(file_path, chunksize=chunk_size)
        elif file_path.endswith(".parquet"):
            chunks = pd.read_parquet(file_path, chunksize=chunk_size)
        elif file_path.endswith(".json"):
            chunks = pd.read_json(file_path, lines=True, chunksize=chunk_size)
        else:
            # Default to CSV
            chunks = pd.read_csv(file_path, chunksize=chunk_size)

        for chunk in chunks:
            if processor:
                chunk = processor(chunk)
            yield chunk

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        raise


def stream_data(
    data_source: Union[str, pd.DataFrame, np.ndarray],
    batch_size: int = DEFAULT_CHUNK_SIZE,
    transform_func: Optional[Callable] = None,
) -> Generator[Any, None, None]:
    """
    Stream data in batches for processing.

    Args:
        data_source: Source of data (file path, DataFrame, or array)
        batch_size: Size of each batch
        transform_func: Optional transformation function

    Yields:
        Data batches
    """
    if isinstance(data_source, str):
        # File source
        for batch in process_large_file(data_source, batch_size):
            if transform_func:
                batch = transform_func(batch)
            yield batch
    elif isinstance(data_source, pd.DataFrame):
        # DataFrame source
        for i in range(0, len(data_source), batch_size):
            batch = data_source.iloc[i : i + batch_size]
            if transform_func:
                batch = transform_func(batch)
            yield batch
    elif isinstance(data_source, np.ndarray):
        # Array source
        for i in range(0, len(data_source), batch_size):
            batch = data_source[i : i + batch_size]
            if transform_func:
                batch = transform_func(batch)
            yield batch
    else:
        raise TypeError("Unsupported data source type")


def get_dask_status() -> Dict[str, bool]:
    """
    Check Dask availability and status.

    Returns:
        Dictionary with Dask feature availability
    """
    status = {
        "dask_available": False,
        "dask_dataframe": False,
        "dask_array": False,
        "dask_ml": False,
        "distributed": False,
    }

    try:
        import dask

        status["dask_available"] = True

        try:
            import dask.dataframe as dd

            status["dask_dataframe"] = True
        except ImportError:
            pass

        try:
            import dask.array as da

            status["dask_array"] = True
        except ImportError:
            pass

        # dask_ml removed - not essential for core functionality

        try:
            import distributed

            status["distributed"] = True
        except ImportError:
            pass

    except ImportError:
        pass

    return status


def get_gpu_status() -> Dict[str, bool]:
    """
    Check GPU acceleration availability.

    Returns:
        Dictionary with GPU feature availability
    """
    status = {"cupy_available": False, "cuda_available": False, "gpu_memory": 0}

    try:
        import cupy as cp

        status["cupy_available"] = True

        try:
            # Check CUDA availability
            device = cp.cuda.Device(0)
            status["cuda_available"] = True

            # Get GPU memory info
            meminfo = cp.cuda.runtime.memGetInfo()
            status["gpu_memory"] = meminfo[1] / (1024**3)  # GB

        except Exception:
            status["cuda_available"] = False

    except ImportError:
        pass

    return status


def get_memory_mapping_status() -> bool:
    """
    Check if memory mapping is available.

    Returns:
        True if memory mapping is available
    """
    MEMORY_MAPPING_AVAILABLE = False
    return MEMORY_MAPPING_AVAILABLE


def get_distributed_status() -> Dict[str, bool]:
    """
    Check distributed computing availability.

    Returns:
        Dictionary with distributed computing feature availability
    """
    status = {
        "ray_available": False,
        "spark_available": False,
        "celery_available": False,
    }

    try:
        import ray

        status["ray_available"] = True
    except ImportError:
        pass

    # pyspark removed - not essential for core functionality

    try:
        import celery

        status["celery_available"] = True
    except ImportError:
        pass

    return status


def estimate_memory_usage(df: pd.DataFrame) -> Dict[str, float]:
    """
    Estimate memory usage of a DataFrame.

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary with memory usage estimates
    """
    memory_info = {}

    # Current memory usage
    memory_info["current_mb"] = df.memory_usage(deep=True).sum() / 1024 / 1024

    # Estimated memory usage for different dtypes
    memory_info["optimized_mb"] = 0

    for col in df.columns:
        col_type = df[col].dtype

        if col_type != "object":
            c_min = df[col].min()
            c_max = df[col].max()

            if str(col_type)[:3] == "int":
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    memory_info["optimized_mb"] += len(df) * 1 / 1024 / 1024
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    memory_info["optimized_mb"] += len(df) * 2 / 1024 / 1024
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    memory_info["optimized_mb"] += len(df) * 4 / 1024 / 1024
                else:
                    memory_info["optimized_mb"] += len(df) * 8 / 1024 / 1024
            else:
                if (
                    c_min > np.finfo(np.float16).min
                    and c_max < np.finfo(np.float16).max
                ):
                    memory_info["optimized_mb"] += len(df) * 2 / 1024 / 1024
                elif (
                    c_min > np.finfo(np.float32).min
                    and c_max < np.finfo(np.float32).max
                ):
                    memory_info["optimized_mb"] += len(df) * 4 / 1024 / 1024
                else:
                    memory_info["optimized_mb"] += len(df) * 8 / 1024 / 1024
        else:
            # Estimate category memory usage
            unique_count = df[col].nunique()
            if unique_count < len(df) * 0.5:  # If less than 50% unique values
                memory_info["optimized_mb"] += len(df) * 1 / 1024 / 1024
            else:
                memory_info["optimized_mb"] += len(df) * 8 / 1024 / 1024

    memory_info["savings_mb"] = memory_info["current_mb"] - memory_info["optimized_mb"]
    memory_info["savings_percent"] = (
        memory_info["savings_mb"] / memory_info["current_mb"]
    ) * 100

    return memory_info


def get_system_memory_info() -> Dict[str, float]:
    """
    Get system memory information.

    Returns:
        Dictionary with system memory info
    """
    try:
        import psutil

        memory = psutil.virtual_memory()

        return {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent_used": memory.percent,
            "free_gb": memory.free / (1024**3),
        }
    except ImportError:
        return {
            "total_gb": 0.0,
            "available_gb": 0.0,
            "used_gb": 0.0,
            "percent_used": 0.0,
            "free_gb": 0.0,
        }


def check_memory_constraints(
    estimated_memory_mb: float, safety_margin: float = 0.2
) -> Dict[str, Any]:
    """
    Check if estimated memory usage fits within system constraints.

    Args:
        estimated_memory_mb: Estimated memory usage in MB
        safety_margin: Safety margin as a fraction of available memory

    Returns:
        Dictionary with memory constraint check results
    """
    system_memory = get_system_memory_info()
    available_memory_mb = system_memory["available_gb"] * 1024

    max_allowed_mb = available_memory_mb * (1 - safety_margin)

    return {
        "fits_in_memory": estimated_memory_mb <= max_allowed_mb,
        "estimated_mb": estimated_memory_mb,
        "max_allowed_mb": max_allowed_mb,
        "available_mb": available_memory_mb,
        "safety_margin": safety_margin,
        "recommendation": (
            "Use chunked processing"
            if estimated_memory_mb > max_allowed_mb
            else "Safe to process"
        ),
    }


# ==========================================================
# Auto engine selector: pandas | polars | duckdb
# ==========================================================
def detect_engines() -> Dict[str, bool]:
    """Detect availability of optional dataframe/query engines."""
    available = {"pandas": True, "polars": False, "duckdb": False}
    try:
        import polars as _pl  # noqa: F401
        available["polars"] = True
    except Exception:
        pass
    try:
        import duckdb as _dd  # noqa: F401
        available["duckdb"] = True
    except Exception:
        pass
    return available


def select_dataframe_engine(
    df: Optional[pd.DataFrame] = None,
    file_path: Optional[str] = None,
    row_count_estimate: Optional[int] = None,
    memory_limit_mb: Optional[float] = None,
    prefer: str = "auto",
) -> Dict[str, Any]:
    """
    Heuristically select a dataframe engine.

    - If prefer != auto and engine is available, choose it.
    - Else use simple heuristics:
      * If DuckDB available and file is parquet/csv and rows are large -> duckdb
      * Else if Polars available and rows are large -> polars
      * Else fallback to pandas
    """
    avail = detect_engines()
    reason = []

    # If DataFrame is provided, use its row count
    if df is not None:
        row_count_estimate = len(df)

    if prefer != "auto" and avail.get(prefer, False):
        return {"engine": prefer, "reason": f"user_preference:{prefer}", "available": avail}

    # Guess large if unknown
    is_large = bool(row_count_estimate and row_count_estimate > 1_000_000)
    if file_path:
        lower = file_path.lower()
        if any(lower.endswith(ext) for ext in [".parquet", ".csv"]):
            if avail["duckdb"] and (is_large or lower.endswith(".parquet")):
                reason.append("duckdb_for_parquet_or_large_csv")
                return {"selected_engine": "duckdb", "reason": ",".join(reason), "available": avail}
    
    if avail["polars"] and (is_large or (row_count_estimate and row_count_estimate > 200_000)):
        reason.append("polars_for_large_tabular")
        return {"selected_engine": "polars", "reason": ",".join(reason), "available": avail}

    return {"selected_engine": "pandas", "reason": "default_or_small", "available": avail}


def read_table_auto(
    file_path: str,
    prefer: str = "auto",
    row_count_estimate: Optional[int] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Read a table using the selected engine, returning a pandas.DataFrame for API consistency.

    Supports CSV/Parquet. Falls back to pandas if engines are unavailable.
    """
    sel = select_dataframe_engine(file_path=file_path, row_count_estimate=row_count_estimate, prefer=prefer)
    engine = sel["selected_engine"]

    if engine == "duckdb":
        try:
            import duckdb
            if file_path.lower().endswith(".parquet"):
                q = f"SELECT * FROM parquet_scan('{file_path}')"
                return duckdb.sql(q).df()
            elif file_path.lower().endswith(".csv"):
                q = f"SELECT * FROM read_csv_auto('{file_path}')"
                return duckdb.sql(q).df()
        except Exception:
            pass

    if engine == "polars":
        try:
            import polars as pl
            if file_path.lower().endswith(".parquet"):
                return pl.scan_parquet(file_path).collect().to_pandas()
            elif file_path.lower().endswith(".csv"):
                return pl.scan_csv(file_path).collect().to_pandas()
        except Exception:
            pass

    # Fallback to pandas
    if file_path.lower().endswith(".parquet"):
        return pd.read_parquet(file_path, **{k: v for k, v in kwargs.items() if k != "chunksize"})
    return pd.read_csv(file_path, **kwargs)
