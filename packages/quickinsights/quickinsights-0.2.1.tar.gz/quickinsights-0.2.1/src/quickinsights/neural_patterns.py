"""
Neural-inspired pattern mining and anomaly scoring utilities.

Lightweight implementations designed for large datasets, avoiding heavy deep learning
dependencies by default. Falls back to robust classical methods when needed.
"""

from typing import Any, Dict, Optional, Tuple, Union, List

import numpy as np
import pandas as pd


def _to_2d_numpy(data: Union[pd.DataFrame, np.ndarray]) -> Tuple[np.ndarray, Optional[List[str]]]:
    if isinstance(data, pd.DataFrame):
        return data.to_numpy(copy=False), list(data.columns)
    if isinstance(data, np.ndarray):
        if data.ndim == 1:
            return data.reshape(-1, 1), None
        return data, None
    raise TypeError(f"Unsupported data type: {type(data)}")


def neural_pattern_mining(
    data: Union[pd.DataFrame, np.ndarray],
    n_patterns: int = 5,
    random_state: int = 42,
    batch_size: int = 4096,
) -> Dict[str, Any]:
    """Discover recurring patterns via MiniBatch KMeans clustering.

    Returns cluster centers (patterns) in original feature scale, labels, and counts.
    """
    X, columns = _to_2d_numpy(data)
    if X.size == 0:
        return {"error": "Empty input"}

    # Standardize for stable clustering
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import MiniBatchKMeans

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_clusters = max(1, min(n_patterns, X_scaled.shape[0]))
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        batch_size=batch_size,
        n_init="auto",
    )
    labels = kmeans.fit_predict(X_scaled)

    # Centers back to original scale
    centers_scaled = kmeans.cluster_centers_
    centers = scaler.inverse_transform(centers_scaled)

    # Counts per cluster
    unique, counts = np.unique(labels, return_counts=True)
    cluster_counts = {int(k): int(v) for k, v in zip(unique, counts)}

    centers_df = pd.DataFrame(centers, columns=columns) if columns is not None else pd.DataFrame(centers)

    return {
        "pattern_centers": centers_df,
        "labels": labels,
        "counts": cluster_counts,
        "n_patterns": int(n_clusters),
    }


def autoencoder_anomaly_scores(
    data: Union[pd.DataFrame, np.ndarray],
    hidden_ratio: float = 0.5,
    random_state: int = 42,
    max_iter: int = 200,
) -> Dict[str, Any]:
    """Compute anomaly scores via reconstruction error using a lightweight autoencoder surrogate.

    Primary: MLPRegressor learns X -> X reconstruction. Fallback: PCA reconstruction error.
    Returns per-sample MSE scores and the method used.
    """
    X, columns = _to_2d_numpy(data)
    if X.size == 0:
        return {"error": "Empty input"}

    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_features = X_scaled.shape[1]
    hidden_dim = max(1, int(max(1, hidden_ratio) if hidden_ratio < 1 else hidden_ratio))
    if hidden_ratio < 1:
        hidden_dim = max(1, int(round(n_features * hidden_ratio)))
    hidden_dim = min(hidden_dim, max(1, n_features - 1))

    try:
        from sklearn.neural_network import MLPRegressor

        model = MLPRegressor(
            hidden_layer_sizes=(hidden_dim,),
            activation="relu",
            solver="adam",
            random_state=random_state,
            max_iter=max_iter,
            tol=1e-4,
            early_stopping=True,
            n_iter_no_change=10,
        )
        model.fit(X_scaled, X_scaled)
        X_rec = model.predict(X_scaled)
        method_used = "mlp_autoencoder"
    except Exception:
        # Fallback to PCA reconstruction error
        from sklearn.decomposition import PCA

        pca = PCA(n_components=hidden_dim, random_state=random_state)
        Z = pca.fit_transform(X_scaled)
        X_rec = pca.inverse_transform(Z)
        method_used = "pca_reconstruction"

    # MSE per sample
    errors = np.mean((X_scaled - X_rec) ** 2, axis=1)
    # Normalize scores to [0,1] for interpretability
    min_e, max_e = float(np.min(errors)), float(np.max(errors))
    if max_e > min_e:
        scores = (errors - min_e) / (max_e - min_e)
    else:
        scores = np.zeros_like(errors)

    return {
        "scores": scores,
        "method": method_used,
        "hidden_dim": int(hidden_dim),
        "n_samples": int(X.shape[0]),
        "n_features": int(X.shape[1]),
    }


def sequence_signature_extract(
    data: Union[pd.Series, pd.DataFrame, np.ndarray],
    window: int = 64,
    step: int = 16,
    n_components: int = 2,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Extract compact signatures from a (multi)variate time series via FFT+PCA.

    Returns a DataFrame with [start, end, sig_1..sig_k] per window.
    """
    # Convert input to 2D array with time along axis 0
    if isinstance(data, pd.Series):
        X = data.to_numpy(copy=False).reshape(-1, 1)
    elif isinstance(data, pd.DataFrame):
        X = data.to_numpy(copy=False)
    elif isinstance(data, np.ndarray):
        X = data
        if X.ndim == 1:
            X = X.reshape(-1, 1)
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")

    n_samples = X.shape[0]
    if n_samples < window:
        return {"error": "Not enough samples for the specified window size"}
    if step <= 0:
        return {"error": "Step must be positive"}

    # Build sliding windows
    windows = []
    indices = []
    for start in range(0, n_samples - window + 1, step):
        end = start + window
        seg = X[start:end]
        # FFT magnitude per feature, then flatten
        fft_mag = np.abs(np.fft.rfft(seg, axis=0))
        windows.append(fft_mag.flatten())
        indices.append((start, end))

    W = np.vstack(windows)

    # Dimensionality reduction
    from sklearn.decomposition import PCA
    pca = PCA(n_components=max(1, n_components), random_state=random_state)
    Z = pca.fit_transform(W)

    # Build signatures DataFrame
    cols = [f"sig_{i+1}" for i in range(Z.shape[1])]
    sig_df = pd.DataFrame(Z, columns=cols)
    sig_df.insert(0, "start", [s for s, _ in indices])
    sig_df.insert(1, "end", [e for _, e in indices])

    return {
        "signatures": sig_df,
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "n_windows": int(Z.shape[0]),
    }





