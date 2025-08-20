"""
QuickInsights - Feature Engineering (AutoFE) with Leakage Guard

Generates lightweight, safe feature candidates and optionally filters
leaky/suspicious ones via simple guards.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


def _is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def _safe_name(*parts: str) -> str:
    return "__".join([p.replace(" ", "_") for p in parts])


def autofe_generate_features(
    df: pd.DataFrame,
    target: Optional[Union[str, pd.Series]] = None,
    max_interactions: int = 2,
    datetime_features: bool = True,
    text_features: bool = False,
    leakage_guard: bool = True,
    return_defs: bool = False,
) -> Dict[str, Any]:
    """
    Lightweight AutoFE: numeric transforms, pairwise interactions, basic datetime.

    Parameters:
    - df: input DataFrame
    - target: target column name or Series (used only for leakage checks)
    - max_interactions: up to 2 (pairwise). Values >2 are treated as 2
    - datetime_features: extract year, month, day, dow when applicable
    - text_features: if True, add length/word_count for object columns
    - leakage_guard: drop features that look like proxies/copies of the target
    - return_defs: include feature definition metadata

    Returns dict with keys: 'features' (DataFrame), 'added_columns', 'dropped_columns', 'insights'
    """
    if df.empty:
        return {"error": "Empty DataFrame"}

    work = df.copy()
    added: List[str] = []
    dropped: List[str] = []
    definitions: Dict[str, Dict[str, Any]] = {}
    insights: List[str] = []

    # Numeric transforms
    numeric_cols = [c for c in work.columns if _is_numeric(work[c])]
    for col in numeric_cols:
        s = work[col].astype(float)
        # log1p for positive values
        if (s > 0).sum() > max(5, len(s) * 0.05):
            new_col = _safe_name(col, "log1p")
            work[new_col] = np.log1p(s.clip(lower=1e-12))
            added.append(new_col)
            definitions[new_col] = {"type": "transform", "base": col, "op": "log1p"}
        # sqrt for non-negative
        if (s >= 0).all():
            new_col = _safe_name(col, "sqrt")
            work[new_col] = np.sqrt(s)
            added.append(new_col)
            definitions[new_col] = {"type": "transform", "base": col, "op": "sqrt"}
        # zscore
        if s.std() > 0:
            new_col = _safe_name(col, "zscore")
            work[new_col] = (s - s.mean()) / (s.std() + 1e-12)
            added.append(new_col)
            definitions[new_col] = {"type": "transform", "base": col, "op": "zscore"}

    # Ratios and interactions (pairwise)
    if max_interactions >= 2 and len(numeric_cols) >= 2:
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                a, b = numeric_cols[i], numeric_cols[j]
                sa = work[a].astype(float)
                sb = work[b].astype(float)
                # product
                prod_col = _safe_name(a, "x", b)
                work[prod_col] = sa * sb
                added.append(prod_col)
                definitions[prod_col] = {"type": "interaction", "op": "product", "cols": [a, b]}
                # ratio (avoid div-by-zero)
                if (np.abs(sb) > 1e-12).any():
                    ratio_col = _safe_name(a, "div", b)
                    work[ratio_col] = sa / (sb.replace({0: np.nan}) + 1e-12)
                    added.append(ratio_col)
                    definitions[ratio_col] = {"type": "interaction", "op": "ratio", "cols": [a, b]}

    # Datetime features
    if datetime_features:
        dt_cols = [c for c in work.columns if pd.api.types.is_datetime64_any_dtype(work[c])]
        for col in dt_cols:
            base = work[col]
            for comp, getter in [
                ("year", base.dt.year),
                ("month", base.dt.month),
                ("day", base.dt.day),
                ("dow", base.dt.dayofweek),
            ]:
                new_col = _safe_name(col, comp)
                work[new_col] = getter.astype(float)
                added.append(new_col)
                definitions[new_col] = {"type": "datetime", "base": col, "comp": comp}

    # Basic text stats
    if text_features:
        obj_cols = [c for c in work.columns if work[c].dtype == "object"]
        for col in obj_cols:
            new_col = _safe_name(col, "len")
            work[new_col] = work[col].astype(str).str.len().astype(float)
            added.append(new_col)
            definitions[new_col] = {"type": "text", "base": col, "op": "len"}
            new_col2 = _safe_name(col, "words")
            work[new_col2] = work[col].astype(str).str.split().map(len).astype(float)
            added.append(new_col2)
            definitions[new_col2] = {"type": "text", "base": col, "op": "words"}

    # Leakage guard: drop columns that are near-duplicates of target
    if leakage_guard and target is not None:
        if isinstance(target, str) and target in work.columns:
            y = work[target]
        elif isinstance(target, pd.Series):
            y = target.reset_index(drop=True)
            if len(y) != len(work):
                # align to length if mismatch
                y = pd.Series(y.values[: len(work)])
        else:
            y = None

        if y is not None and _is_numeric(y):
            y = y.astype(float)
            for col in list(added):
                s = work[col].astype(float)
                # exact or near-exact copy
                same_mask = (s.round(6) == y.round(6)) | ((s - y).abs() < 1e-6)
                if same_mask.mean() > 0.999:
                    work.drop(columns=[col], inplace=True, errors="ignore")
                    dropped.append(col)
                    added.remove(col)
            insights.append(f"Leakage guard removed {len(dropped)} features similar to target")

    result: Dict[str, Any] = {
        "features": work,
        "added_columns": added,
        "dropped_columns": dropped,
        "insights": insights,
    }
    if return_defs:
        result["definitions"] = definitions
    return result


def leakage_guard_check(
    df: pd.DataFrame,
    target: Union[str, pd.Series],
    candidate_columns: Optional[List[str]] = None,
    threshold: float = 0.999,
) -> Dict[str, Any]:
    """
    Identify columns that are (near) copies of the target to avoid leakage.

    Returns dict with 'flagged' list and simple reasons.
    """
    if isinstance(target, str):
        if target not in df.columns:
            return {"error": f"Target '{target}' not in DataFrame"}
        y = df[target]
    else:
        y = pd.Series(target)

    flagged: List[Dict[str, Any]] = []
    if not _is_numeric(y):
        return {"flagged": []}
    y = y.astype(float)

    if candidate_columns is not None:
        cols = list(candidate_columns)
    else:
        # If target is a column name, exclude it; if it's a Series, include all columns
        if isinstance(target, str):
            cols = [c for c in df.columns if c != target]
        else:
            cols = list(df.columns)
    for col in cols:
        if not _is_numeric(df[col]):
            continue
        s = df[col].astype(float)
        same_mask = (s.round(6) == y.round(6)) | ((s - y).abs() < 1e-6)
        if same_mask.mean() >= threshold:
            flagged.append({"column": col, "reason": "near-duplicate-of-target", "match_ratio": float(same_mask.mean())})

    return {"flagged": flagged}


