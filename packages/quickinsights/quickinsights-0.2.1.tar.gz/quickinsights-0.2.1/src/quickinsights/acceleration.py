"""
Performance Acceleration Utilities

- Transparent GPU acceleration via CuPy when available (falls back to NumPy)
- Memory-efficient processing (memmap, chunked apply)
- Simple benchmarking helpers
"""

from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np

try:
    import cupy as cp  # type: ignore
    _CUPY_IMPORTED = True
except Exception:
    cp = None  # type: ignore
    _CUPY_IMPORTED = False


def _is_cupy_usable() -> bool:
    if not _CUPY_IMPORTED:
        return False
    try:
        # Try a tiny computation that requires kernels
        a = cp.arange(8, dtype=cp.float32)  # type: ignore[attr-defined]
        _ = (a * a).sum().item()
        return True
    except Exception:
        return False


_CUPY_USABLE = _is_cupy_usable()


def gpu_available() -> bool:
    return _CUPY_USABLE


def get_array_backend(prefer_gpu: bool = True) -> Dict[str, Any]:
    """Return the array backend module and metadata.

    Example: backend = get_array_backend(); xp = backend["xp"]
    """
    if prefer_gpu and _CUPY_USABLE:
        return {"xp": cp, "name": "cupy", "device": "gpu"}
    return {"xp": np, "name": "numpy", "device": "cpu"}


def _to_backend_array(array: Union[np.ndarray, "cp.ndarray"], xp_module):  # type: ignore[name-defined]
    if xp_module is np:
        if isinstance(array, np.ndarray):
            return array
        # Convert from CuPy to NumPy
        return np.asarray(array.get())  # type: ignore[attr-defined]
    else:
        # xp is CuPy
        if _CUPY_USABLE and not isinstance(array, cp.ndarray):  # type: ignore[attr-defined]
            return cp.asarray(array)  # type: ignore[attr-defined]
        return array


def standardize_array(array: Union[np.ndarray, "cp.ndarray"], axis: int = 0, prefer_gpu: bool = True):  # type: ignore[name-defined]
    backend = get_array_backend(prefer_gpu=prefer_gpu)
    xp = backend["xp"]
    X = _to_backend_array(array, xp)
    try:
        mean = xp.mean(X, axis=axis, keepdims=True)
        std = xp.std(X, axis=axis, keepdims=True)
        std = xp.where(std == 0, 1.0, std)
        Z = (X - mean) / std
        # Always return NumPy on output for interoperability
        if xp is np:
            return Z
        return Z.get()  # type: ignore[attr-defined]
    except Exception:
        # Fallback to CPU
        Xnp = _to_backend_array(array, np)
        mean = np.mean(Xnp, axis=axis, keepdims=True)
        std = np.std(Xnp, axis=axis, keepdims=True)
        std = np.where(std == 0, 1.0, std)
        return (Xnp - mean) / std


def backend_dot(a: Union[np.ndarray, "cp.ndarray"], b: Union[np.ndarray, "cp.ndarray"], prefer_gpu: bool = True):  # type: ignore[name-defined]
    backend = get_array_backend(prefer_gpu=prefer_gpu)
    xp = backend["xp"]
    A = _to_backend_array(a, xp)
    B = _to_backend_array(b, xp)
    try:
        C = xp.dot(A, B)
        if xp is np:
            return C
        return C.get()  # type: ignore[attr-defined]
    except Exception:
        # Fallback to CPU
        A_np = _to_backend_array(a, np)
        B_np = _to_backend_array(b, np)
        return np.dot(A_np, B_np)


def gpu_corrcoef(array: Union[np.ndarray, "cp.ndarray"], prefer_gpu: bool = True) -> np.ndarray:  # type: ignore[name-defined]
    """Compute correlation matrix using GPU if available, else CPU.

    Returns a NumPy ndarray.
    """
    backend = get_array_backend(prefer_gpu=prefer_gpu)
    xp = backend["xp"]
    X = _to_backend_array(array, xp)
    # Ensure 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    # Convert to float
    X = X.astype(xp.float64, copy=False)
    try:
        # Standardize
        X = X - xp.mean(X, axis=0, keepdims=True)
        denom = xp.std(X, axis=0, keepdims=True)
        denom = xp.where(denom == 0, 1.0, denom)
        Xn = X / denom
        # Correlation
        corr = (Xn.T @ Xn) / (Xn.shape[0] - 1)
        if xp is np:
            return corr
        return corr.get()  # type: ignore[attr-defined]
    except Exception:
        # Fallback to CPU
        Xnp = _to_backend_array(array, np)
        if Xnp.ndim == 1:
            Xnp = Xnp.reshape(-1, 1)
        Xnp = Xnp.astype(np.float64, copy=False)
        Xnp = Xnp - np.mean(Xnp, axis=0, keepdims=True)
        denom = np.std(Xnp, axis=0, keepdims=True)
        denom = np.where(denom == 0, 1.0, denom)
        Xn = Xnp / denom
        return (Xn.T @ Xn) / (Xn.shape[0] - 1)


def memmap_array(path: str, dtype: str, shape: Tuple[int, ...], mode: str = "w+") -> np.memmap:
    """Create or open a memory-mapped array on disk."""
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    return np.memmap(path, dtype=dtype, mode=mode, shape=shape)


def chunked_apply(
    func: Callable[[np.ndarray], Any],
    array: np.ndarray,
    chunk_rows: int = 100_000,
) -> List[Any]:
    """Apply a function to row-chunks of a 2D NumPy array and return list of results."""
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    results: List[Any] = []
    n_rows = array.shape[0]
    for start_row in range(0, n_rows, chunk_rows):
        end_row = min(start_row + chunk_rows, n_rows)
        chunk = array[start_row:end_row]
        results.append(func(chunk))
    return results


def benchmark_backend(
    func: Callable[[Any], Any],
    *,
    repeats: int = 3,
    prefer_gpu: bool = True,
) -> Dict[str, Any]:
    """Benchmark a simple function with backend argument: func(xp) -> Any.

    Returns timing for CPU and (if available) GPU.
    """
    import time

    timings: Dict[str, float] = {}

    # CPU
    cpu_backend = {"xp": np, "name": "numpy", "device": "cpu"}
    start = time.time()
    for _ in range(repeats):
        func(cpu_backend["xp"])  # type: ignore[index]
    timings["cpu_seconds"] = time.time() - start

    # GPU optional
    if prefer_gpu and _CUPY_USABLE:
        try:
            start = time.time()
            for _ in range(repeats):
                func(cp)  # type: ignore[name-defined]
            timings["gpu_seconds"] = time.time() - start
        except Exception as e:
            timings["gpu_error"] = str(e)

    return {
        "timings": timings,
        "gpu_available": _CUPY_USABLE,
        "repeats": repeats,
    }


