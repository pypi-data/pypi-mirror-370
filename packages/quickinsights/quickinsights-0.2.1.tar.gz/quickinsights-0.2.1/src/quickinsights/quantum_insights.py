"""
Quantum-inspired utilities for large-scale data analysis.

Designed to be practical on CPUs with conventional Python stack while drawing
inspiration from quantum concepts (superposition sampling, amplitude encoding,
annealing-style optimization).
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


def _to_numpy_2d(data: Union[pd.DataFrame, np.ndarray]) -> Tuple[np.ndarray, Optional[List[str]]]:
    if isinstance(data, pd.DataFrame):
        return data.to_numpy(copy=False), list(data.columns)
    if isinstance(data, np.ndarray):
        if data.ndim == 1:
            return data.reshape(-1, 1), None
        return data, None
    raise TypeError(f"Unsupported data type: {type(data)}")


def quantum_superposition_sample(
    data: Union[pd.DataFrame, np.ndarray],
    n_samples: int = 10000,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Quantum superposition-inspired row sampling.

    Approximates leverage scores via randomized projection and samples rows
    without replacement proportional to projected energy. This keeps rare yet
    informative modes while maintaining a representative subset.
    """
    X, columns = _to_numpy_2d(data)
    n_rows = X.shape[0]
    if n_rows == 0:
        return {"error": "Empty input"}
    n_take = min(n_samples, n_rows)

    # Center
    Xc = X - np.mean(X, axis=0, keepdims=True)

    # Random projection for leverage approximation
    rng = np.random.default_rng(random_state)
    proj_dim = max(2, min(64, Xc.shape[1]))
    R = rng.normal(size=(Xc.shape[1], proj_dim)) / np.sqrt(proj_dim)
    Z = Xc @ R
    energy = np.sum(Z ** 2, axis=1)
    energy = np.maximum(energy, 1e-12)
    probs = energy / np.sum(energy)

    # Sample without replacement according to probs
    idx = rng.choice(n_rows, size=n_take, replace=False, p=probs)
    subset = X[idx]
    df_subset = (
        pd.DataFrame(subset, columns=columns) if columns is not None else pd.DataFrame(subset)
    )

    return {
        "indices": idx.tolist(),
        "subset": df_subset,
        "projection_dim": int(proj_dim),
    }


def amplitude_pca(
    data: Union[pd.DataFrame, np.ndarray],
    n_components: int = 10,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Amplitude-encoding-inspired dimensionality reduction.

    Uses randomized SVD PCA for speed on high-dimensional data.
    """
    X, columns = _to_numpy_2d(data)
    if X.size == 0:
        return {"error": "Empty input"}

    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    n_comp = max(1, min(n_components, min(Xs.shape) - 1))
    pca = PCA(n_components=n_comp, svd_solver="randomized", random_state=random_state)
    Z = pca.fit_transform(Xs)

    comps = pd.DataFrame(Z, columns=[f"pc_{i+1}" for i in range(Z.shape[1])])
    return {
        "components": comps,
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "n_components": int(Z.shape[1]),
    }


def quantum_correlation_map(
    data: Union[pd.DataFrame, np.ndarray],
    n_blocks: int = 5,
    block_size: int = 20000,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Robust high-dimensional correlation via median-of-means on random blocks.

    Splits rows into blocks, computes Pearson correlation per block, then aggregates
    by element-wise median to reduce noise and outliers.
    """
    X, columns = _to_numpy_2d(data)
    if X.shape[1] < 2:
        return {"error": "Need at least 2 features"}
    n = X.shape[0]
    if n == 0:
        return {"error": "Empty input"}

    rng = np.random.default_rng(random_state)
    block_corrs = []
    for _ in range(max(1, n_blocks)):
        if n <= block_size:
            idx = np.arange(n)
        else:
            idx = rng.choice(n, size=block_size, replace=False)
        Xi = X[idx]
        # Coerce to float and handle NaNs
        Xi = Xi.astype(float, copy=False)
        Xi = np.nan_to_num(Xi, nan=np.nanmean(Xi, axis=0))
        with np.errstate(invalid="ignore"):
            c = np.corrcoef(Xi, rowvar=False)
        block_corrs.append(c)

    C = np.median(np.stack(block_corrs, axis=0), axis=0)
    corr_df = pd.DataFrame(C, columns=columns, index=columns) if columns is not None else pd.DataFrame(C)
    return {
        "correlation": corr_df,
        "method": "median_of_means",
        "n_blocks": int(max(1, n_blocks)),
    }


def quantum_anneal_optimize(
    estimator,
    param_grid: Dict[str, List[Any]],
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    max_iter: int = 30,  # Changed from max_iters to max_iter for consistency
    cv_folds: int = 3,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Annealing-style hyperparameter search over discrete grids.

    - Starts from a random configuration
    - At each step, proposes a neighbor by changing one parameter
    - Accepts improvements; accepts worse with small probability that decays over time
    """
    # Input validation
    if estimator is None:
        return {"error": "Estimator cannot be None"}
    
    from sklearn.model_selection import cross_val_score
    rng = np.random.default_rng(random_state)

    # Helpers
    keys = list(param_grid.keys())
    values = [v for v in param_grid.values()]
    if any(len(v) == 0 for v in values):
        return {"error": "Empty search space"}

    def random_config():
        return {k: rng.choice(v) for k, v in param_grid.items()}

    def neighbor(cfg: Dict[str, Any]):
        k = rng.choice(keys)
        choices = param_grid[k]
        if len(choices) == 1:
            return cfg.copy()
        new_val = rng.choice([c for c in choices if c != cfg[k]])
        new_cfg = cfg.copy()
        new_cfg[k] = new_val
        return new_cfg

    def score_cfg(cfg: Dict[str, Any]):
        model = estimator.__class__(**{**estimator.get_params(), **cfg})
        try:
            s = cross_val_score(model, X, y, cv=cv_folds, scoring=None, n_jobs=None)
            return float(np.mean(s))
        except Exception:
            return -np.inf

    # Init
    current = random_config()
    current_score = score_cfg(current)
    best = current.copy()
    best_score = current_score

    # Annealing loop
    for t in range(1, max_iter + 1):
        cand = neighbor(current)
        cand_score = score_cfg(cand)
        if cand_score >= current_score:
            current, current_score = cand, cand_score
        else:
            # temperature decays ~ 1/sqrt(t)
            T = max(1e-6, 1.0 / np.sqrt(t))
            accept_prob = np.exp((cand_score - current_score) / max(1e-9, T))
            if rng.random() < accept_prob:
                current, current_score = cand, cand_score
        if current_score > best_score:
            best, best_score = current.copy(), current_score

    return {
        "best_params": best,
        "best_score": float(best_score),
        "start_params": current,
        "iterations": int(max_iter),
    }


