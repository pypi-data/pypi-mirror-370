"""
QuickInsights - Pandas Integration (minimal, stable implementation)

Exposes small, reliable helpers used by the public API:
- smart_group_analysis
- smart_pivot_table
- intelligent_merge
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from .utils import validate_dataframe


def smart_group_analysis(
	df: pd.DataFrame,
	group_columns: Optional[Union[str, List[str]]] = None,
	value_columns: Optional[Union[str, List[str]]] = None,
	auto_detect_groups: bool = True,
	auto_detect_values: bool = True,
	aggregation_functions: Optional[Dict[str, List[str]]] = None,
	include_visualizations: bool = True,
	save_results: bool = False,
	output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
	df = validate_dataframe(df)

	if group_columns is None and auto_detect_groups:
		group_columns = _auto_detect_group_columns(df)
	if value_columns is None and auto_detect_values:
		value_columns = _auto_detect_value_columns(df)

	if isinstance(group_columns, str):
		group_columns = [group_columns]
	if isinstance(value_columns, str):
		value_columns = [value_columns]

	if not group_columns or not value_columns:
		raise ValueError("group_columns and value_columns must be provided or auto-detected")

	if aggregation_functions is None:
		aggregation_functions = {col: ["mean", "sum", "count", "std"] for col in value_columns}

	grouped = df.groupby(group_columns).agg(aggregation_functions)

	return {
		"grouped_data": grouped,
		"group_columns": group_columns,
		"value_columns": value_columns,
		"aggregation_functions": aggregation_functions,
	}


def smart_pivot_table(
	df: pd.DataFrame,
	index_columns: Optional[Union[str, List[str]]] = None,
	columns: Optional[Union[str, List[str]]] = None,
	values: Optional[Union[str, List[str]]] = None,
	auto_detect_structure: bool = True,
	suggest_aggregations: bool = True,
	include_visualizations: bool = True,
	save_results: bool = False,
	output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
	df = validate_dataframe(df)

	if auto_detect_structure:
		detected = _detect_optimal_pivot_structure(df)
		index_columns = index_columns or detected.get("index")
		columns = columns or detected.get("columns")
		values = values or detected.get("values")

	if isinstance(index_columns, str):
		index_columns = [index_columns]
	if isinstance(columns, str):
		columns = [columns]
	if isinstance(values, str):
		values = [values]

	if not values:
		raise ValueError("values must be provided or auto-detected")

	pivot_tables: Dict[str, pd.DataFrame] = {}
	for value_col in values:
		pivot_tables[value_col] = df.pivot_table(
			index=index_columns,
			columns=columns,
			values=value_col,
			aggfunc="mean",
			fill_value=0,
		)

	return {
		"pivot_tables": pivot_tables,
		"index_columns": index_columns,
		"columns": columns,
		"values": values,
	}


def intelligent_merge(
	left_df: pd.DataFrame,
	right_df: pd.DataFrame,
	left_key: Optional[Union[str, List[str]]] = None,
	right_key: Optional[Union[str, List[str]]] = None,
	auto_detect_keys: bool = True,
	suggest_merge_strategy: bool = True,
	include_visualizations: bool = True,
	save_results: bool = False,
	output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
	left_df = validate_dataframe(left_df)
	right_df = validate_dataframe(right_df)

	if auto_detect_keys and (left_key is None or right_key is None):
		detected = _auto_detect_merge_keys(left_df, right_df)
		left_key = left_key or detected.get("left_key")
		right_key = right_key or detected.get("right_key")

	if left_key is None or right_key is None:
		raise ValueError("left_key and right_key must be provided or auto-detected")

	merged_inner = pd.merge(left_df, right_df, left_on=left_key, right_on=right_key, how="inner")

	return {
		"merge_results": {"inner": merged_inner},
		"left_key": left_key,
		"right_key": right_key,
	}


# --------- helpers ---------

def _auto_detect_group_columns(df: pd.DataFrame) -> List[str]:
	cats = df.select_dtypes(include=["object", "category"]).columns.tolist()
	return cats[:2]


def _auto_detect_value_columns(df: pd.DataFrame) -> List[str]:
	return df.select_dtypes(include=[np.number]).columns.tolist()[:3]


def _detect_optimal_pivot_structure(df: pd.DataFrame) -> Dict[str, List[str]]:
	cats = df.select_dtypes(include=["object", "category"]).columns.tolist()
	nums = df.select_dtypes(include=[np.number]).columns.tolist()
	return {
		"index": cats[:1] if cats else [],
		"columns": cats[1:2] if len(cats) > 1 else [],
		"values": nums[:1] if nums else [],
	}


def _auto_detect_merge_keys(left_df: pd.DataFrame, right_df: pd.DataFrame) -> Dict[str, Optional[Union[str, List[str]]]]:
	left_cols = set(left_df.columns)
	right_cols = set(right_df.columns)
	common = list(left_cols.intersection(right_cols))
	if not common:
		return {"left_key": None, "right_key": None}
	key = common[0]
	return {"left_key": key, "right_key": key}
