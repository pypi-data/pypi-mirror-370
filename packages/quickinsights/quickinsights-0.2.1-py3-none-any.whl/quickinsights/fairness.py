"""
QuickInsights - Fairness Mini-Audit

Lightweight fairness checks for binary classification across a protected attribute.
Computes per-group:
- PPR (positive prediction rate)
- TPR (true positive rate), FPR (false positive rate) when y_true provided
And overall:
- Demographic parity difference (max PPR - min PPR)
- Disparate impact ratio (min PPR / max PPR)
- Equalized odds deltas (max-min for TPR and FPR) if applicable
"""

from typing import Any, Dict, Optional, Union
import numpy as np
import pandas as pd


def fairness_mini_audit(
    y_true: Optional[Union[pd.Series, np.ndarray]],
    y_pred: Union[pd.Series, np.ndarray],
    group: Union[pd.Series, np.ndarray],
    positive_label: Union[int, float, str] = 1,
    di_threshold: float = 0.8,
) -> Dict[str, Any]:
    """
    Compute basic fairness metrics across groups for a binary classification task.

    Parameters:
    - y_true: true labels (optional; if None, only PPR-based metrics are computed)
    - y_pred: predicted labels (required)
    - group: protected attribute (same length), can be categorical or string/numeric
    - positive_label: label considered positive
    - di_threshold: disparate impact threshold (80% rule default: 0.8)

    Returns:
    - dict with per-group and overall metrics, flags when DI < threshold
    """
    y_pred = _to_series(y_pred, name="y_pred")
    group = _to_series(group, name="group")
    if len(y_pred) != len(group):
        return {"error": "Length mismatch between y_pred and group"}
    y_true_s = None
    if y_true is not None:
        y_true_s = _to_series(y_true, name="y_true")
        if len(y_true_s) != len(y_pred):
            return {"error": "Length mismatch between y_true and y_pred"}

    # Normalize positives
    pos_mask = y_pred == positive_label

    # Per-group metrics
    groups = group.astype(str).fillna("<NA>")
    per_group: Dict[str, Dict[str, float]] = {}
    for g in sorted(groups.unique()):
        idx = groups == g
        n = int(idx.sum())
        if n == 0:
            continue
        ppr = float(pos_mask[idx].mean())
        metrics = {"count": n, "ppr": ppr}
        if y_true_s is not None:
            yt = y_true_s[idx]
            yp = y_pred[idx]
            denom_pos = max(1, int((yt == positive_label).sum()))
            denom_neg = max(1, int((yt != positive_label).sum()))
            tpr = float(((yp == positive_label) & (yt == positive_label)).sum() / denom_pos)
            fpr = float(((yp == positive_label) & (yt != positive_label)).sum() / denom_neg)
            metrics.update({"tpr": tpr, "fpr": fpr})
        per_group[g] = metrics

    if not per_group:
        return {"error": "No valid groups"}

    # Overall diffs and ratios
    pprs = [m["ppr"] for m in per_group.values()]
    max_ppr, min_ppr = max(pprs), min(pprs)
    dp_diff = float(max_ppr - min_ppr)
    di_ratio = float(min_ppr / max_ppr) if max_ppr > 0 else np.nan

    result: Dict[str, Any] = {
        "per_group": per_group,
        "demographic_parity_diff": dp_diff,
        "disparate_impact_ratio": di_ratio,
        "di_below_threshold": (di_ratio < di_threshold) if not np.isnan(di_ratio) else False,
        "positive_label": positive_label,
    }

    if y_true_s is not None:
        tprs = [m.get("tpr") for m in per_group.values() if "tpr" in m]
        fprs = [m.get("fpr") for m in per_group.values() if "fpr" in m]
        if tprs:
            result["equalized_odds_tpr_delta"] = float(max(tprs) - min(tprs))
        if fprs:
            result["equalized_odds_fpr_delta"] = float(max(fprs) - min(fprs))

    # Simple insights
    insights = []
    if result.get("di_below_threshold"):
        insights.append("Disparate impact below threshold (80% rule)")
    if dp_diff > 0.2:
        insights.append("Large demographic parity difference detected")
    result["insights"] = insights

    return result


def _to_series(x: Union[pd.Series, np.ndarray], name: str) -> pd.Series:
    if isinstance(x, pd.Series):
        s = x.reset_index(drop=True).copy()
        s.name = name
        return s
    return pd.Series(np.asarray(x), name=name)


