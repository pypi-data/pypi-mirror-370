"""
Holographic-style 3D visualization utilities.

Dependencies kept optional; core functions rely on numpy/pandas + (optionally) plotly.
"""

from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd


def _to_numpy_2d(data: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
    if isinstance(data, pd.DataFrame):
        X = data.to_numpy(copy=False)
    elif isinstance(data, np.ndarray):
        X = data
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    return X


def embed_3d_projection(
    data: Union[pd.DataFrame, np.ndarray],
    method: str = "pca",
    random_state: int = 42,
) -> Dict[str, Any]:
    """Project high-dimensional data to 3D for visualization (PCA or UMAP if available)."""
    X = _to_numpy_2d(data)

    if method.lower() == "umap":
        try:
            import umap  # type: ignore

            reducer = umap.UMAP(n_components=3, random_state=random_state)
            Z = reducer.fit_transform(X)
            used = "umap"
        except Exception:
            method = "pca"

    if method.lower() == "pca":
        from sklearn.decomposition import PCA

        reducer = PCA(n_components=3, random_state=random_state)
        Z = reducer.fit_transform(X)
        used = "pca"

    proj = pd.DataFrame(Z, columns=["x", "y", "z"])
    return {"embedding": proj, "method": used}


def volumetric_density_plot(
    data: Union[pd.DataFrame, np.ndarray],
    bins: int = 32,
) -> Dict[str, Any]:
    """Compute a 3D histogram volume (x,y,z) suitable for volumetric plotting."""
    X = _to_numpy_2d(data)
    d = X.shape[1]
    if d != 3:
        if d > 3:
            # Reduce to 3D
            from sklearn.decomposition import PCA
            X = PCA(n_components=3, random_state=42).fit_transform(X)
        else:
            # Pad with zeros to reach 3D
            pad = np.zeros((X.shape[0], 3 - d), dtype=X.dtype)
            X = np.hstack([X, pad])

    # Normalize to [0,1] for stable binning
    Xn = (X - X.min(axis=0, keepdims=True)) / (np.ptp(X, axis=0, keepdims=True) + 1e-12)
    H, edges = np.histogramdd(Xn, bins=bins, range=[[0, 1], [0, 1], [0, 1]])
    return {"volume": H, "edges": edges}


def export_vr_scene_stub(embedding: pd.DataFrame, out_path: str) -> Dict[str, Any]:
    """Export a simple VR-ready JSON scene (stub). Consumers can load into WebXR/Unity.

    This avoids heavy dependencies at this stage; provides a portable format.
    """
    try:
        import json
        import os

        records = embedding[["x", "y", "z"]].to_dict(orient="records")
        scene = {"type": "pointcloud", "points": records}
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(scene, f)
        return {"success": True, "path": out_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


def plotly_embed_3d(
    embedding: pd.DataFrame,
    color: Optional[Union[pd.Series, np.ndarray, str]] = None,
    size: int = 3,
) -> Dict[str, Any]:
    """Create an interactive 3D scatter plot using Plotly.

    Returns {"success": True, "figure": fig} on success, otherwise {"success": False, "error": msg}.
    """
    try:
        import plotly.graph_objects as go

        x = embedding["x"].to_numpy()
        y = embedding["y"].to_numpy()
        z = embedding["z"].to_numpy()
        marker_dict = {"size": size}
        if color is not None:
            marker_dict["color"] = color
            marker_dict["colorscale"] = "Viridis"
            marker_dict["showscale"] = True

        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    mode="markers",
                    marker=marker_dict,
                )
            ]
        )
        fig.update_layout(scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="z"))
        return {"success": True, "figure": fig}
    except Exception as e:
        return {"success": False, "error": str(e)}


