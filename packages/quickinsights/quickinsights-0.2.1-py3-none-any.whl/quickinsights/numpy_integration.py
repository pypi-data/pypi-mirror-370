"""
QuickInsights - NumPy Integration (minimal, stable implementation)

Provides lightweight analytical helpers used by the public API.
Currently exposes:
- auto_math_analysis
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd


def _to_numpy_array(data: Union[np.ndarray, pd.DataFrame, pd.Series]) -> np.ndarray:
	"""Convert supported data inputs to a numeric NumPy ndarray.

	- DataFrame: uses only numeric columns
	- Series: converted to 1D array
	- ndarray: returned as-is (converted with np.asarray for safety)
	"""
	if isinstance(data, pd.DataFrame):
		numeric = data.select_dtypes(include=[np.number])
		return numeric.values
	if isinstance(data, pd.Series):
		return data.to_numpy()
	return np.asarray(data)


def _descriptive_stats(arr: np.ndarray) -> Dict[str, Any]:
	"""Compute basic descriptive statistics for 1D or 2D arrays."""
	if arr.ndim == 1:
		return {
			"mean": float(np.mean(arr)),
			"std": float(np.std(arr)),
			"min": float(np.min(arr)),
			"max": float(np.max(arr)),
			"median": float(np.median(arr)),
		}
	# 2D+: compute per-column stats for first axis
	return {
		"mean": np.mean(arr, axis=0).tolist(),
		"std": np.std(arr, axis=0).tolist(),
		"min": np.min(arr, axis=0).tolist(),
		"max": np.max(arr, axis=0).tolist(),
		"median": np.median(arr, axis=0).tolist(),
	}


def _correlation(arr: np.ndarray) -> Dict[str, Any]:
	"""Return correlation matrix for 2D arrays; otherwise an error message."""
	if arr.ndim != 2 or arr.shape[1] < 2:
		return {"error": "correlation requires a 2D array with >= 2 columns"}
	corr = np.corrcoef(arr.T)
	return {"correlation_matrix": corr.tolist()}


def auto_math_analysis(
	data: Union[np.ndarray, pd.DataFrame, pd.Series],
	analysis_types: Optional[List[str]] = None,
	auto_detect_operations: bool = True,
	include_visualizations: bool = True,
	save_results: bool = False,
	output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
	"""Perform a small set of safe numerical analyses on the given data.

	Parameters are accepted for backward-compatibility; only core logic is executed.
	"""
	arr = _to_numpy_array(data)
	if arr.size == 0:
		raise ValueError("Empty input data")

	# Determine operations
	if auto_detect_operations and not analysis_types:
		analysis_types = ["descriptive"]
		if arr.ndim == 2 and arr.shape[1] >= 2:
			analysis_types.append("correlation")
	elif not analysis_types:
		analysis_types = ["descriptive"]

	results: Dict[str, Any] = {}
	for op in analysis_types:
		if op == "descriptive":
			results[op] = _descriptive_stats(arr)
		elif op == "correlation":
			results[op] = _correlation(arr)

	insights: List[str] = []
	if "descriptive" in results:
		desc = results["descriptive"]
		# Simple, non-opinionated hint
		if isinstance(desc.get("std"), float) and desc["std"] == 0.0:
			insights.append("All values are identical along the analyzed dimension(s)")

	return {
		"data_shape": arr.shape,
		"analysis_types": analysis_types,
		"results": results,
		"insights": insights,
	}
