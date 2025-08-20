"""
QuickInsights - Anomaly Explanation

Provides lightweight anomaly detection plus per-feature contribution hints.
Methods:
- isolation_forest (default): anomaly scores from IsolationForest
- zscore: flag outliers via z-score and explain via per-feature z-scores
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd


def anomaly_explain(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "isolation_forest",
    contamination: float = 0.1,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Detect anomalies and return explanations per anomaly.

    Returns dict with keys: 'anomaly_indices', 'scores', 'explanations', 'method'.
    """
    if df.empty:
        return {"error": "Empty DataFrame"}

    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    if not cols:
        return {"error": "No numeric columns to analyze"}

    X = df[cols].astype(float).to_numpy()

    if method == "zscore":
        mean = np.nanmean(X, axis=0)
        std = np.nanstd(X, axis=0) + 1e-12
        z = (X - mean) / std
        scores = np.nanmax(np.abs(z), axis=1)
        thresh = np.quantile(scores, 1 - contamination)
        anomalous = np.where(scores >= thresh)[0].tolist()
        explanations: List[Dict[str, Any]] = []
        for idx in anomalous:
            contribs = {cols[j]: float(abs(z[idx, j])) for j in range(len(cols))}
            top = sorted(contribs.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
            explanations.append({
                "index": int(idx),
                "contributors": [{"feature": k, "z": v} for k, v in top],
                "score": float(scores[idx]),
            })
        return {
            "method": method,
            "anomaly_indices": anomalous,
            "scores": [float(scores[i]) for i in anomalous],
            "explanations": explanations,
        }

    # isolation_forest default
    try:
        from sklearn.ensemble import IsolationForest
    except Exception:
        # Fallback to zscore
        return anomaly_explain(df, columns=columns, method="zscore", contamination=contamination, top_k=top_k)

    rng = np.random.RandomState(42)
    iso = IsolationForest(contamination=contamination, random_state=rng)
    iso.fit(X)
    raw_scores = -iso.decision_function(X)  # higher -> more anomalous
    thresh = np.quantile(raw_scores, 1 - contamination)
    anomalous_idx = np.where(raw_scores >= thresh)[0]

    # Simple contribution proxy: per-feature absolute deviation vs median
    med = np.median(X, axis=0)
    mad = np.median(np.abs(X - med), axis=0) + 1e-12
    deviations = np.abs((X - med) / mad)

    explanations: List[Dict[str, Any]] = []
    for idx in anomalous_idx.tolist():
        contribs = {cols[j]: float(deviations[idx, j]) for j in range(len(cols))}
        top = sorted(contribs.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        explanations.append({
            "index": int(idx),
            "contributors": [{"feature": k, "deviation": v} for k, v in top],
            "score": float(raw_scores[idx]),
        })

    return {
        "method": method,
        "anomaly_indices": [int(i) for i in anomalous_idx.tolist()],
        "scores": [float(raw_scores[i]) for i in anomalous_idx.tolist()],
        "explanations": explanations,
    }


