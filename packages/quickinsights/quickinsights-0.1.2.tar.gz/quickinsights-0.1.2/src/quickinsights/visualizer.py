"""
QuickInsights görselleştirme modülü

Bu modül, veri analizi için gerekli görselleştirme fonksiyonlarını içerir.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict

from .utils import create_output_directory, get_correlation_strength

# Matplotlib ayarları
plt.style.use("default")
sns.set_palette("husl")

# Seaborn font uyarılarını kapat
sns.set_style("whitegrid", {"font.family": ["DejaVu Sans", "Arial", "sans-serif"]})

# Türkçe karakter desteği için - Windows uyumlu fontlar
plt.rcParams["font.family"] = ["DejaVu Sans", "Arial", "sans-serif"]
# Font uyarılarını kapat
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "sans-serif"]
# Font uyarılarını tamamen kapat
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


def correlation_matrix(
    df: pd.DataFrame,
    method: str = "pearson",
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Sayısal değişkenler arası korelasyon matrisini görselleştirir.

    Parameters
    ----------
    df : pd.DataFrame
        Sadece sayısal değişkenler içeren veri seti
    method : str, default='pearson'
        Korelasyon hesaplama yöntemi
    save_plot : bool, default=False
        Grafiği kaydetmek isteyip istemediğiniz
    output_dir : str, default="./quickinsights_output"
        Grafiğin kaydedileceği dizin
    """

    if len(df.columns) < 2:
        print("⚠️  Korelasyon matrisi için en az 2 sayısal değişken gerekli!")
        return

    print(f"\n📈 KORELASYON MATRİSİ ({method.upper()})")
    print("-" * 40)

    # Korelasyon matrisini hesapla
    corr_matrix = df.corr(method=method)

    # Korelasyon güçlerini yazdır - daha verimli
    print("Korelasyon Güçleri:")
    col_names = corr_matrix.columns.tolist()
    n_cols = len(col_names)

    # Vectorized printing - tüm korelasyonları aynı anda işle
    for i in range(n_cols):
        for j in range(i + 1, n_cols):
            col1 = col_names[i]
            col2 = col_names[j]
            corr_value = corr_matrix.iloc[i, j]
            strength = get_correlation_strength(corr_value)
            print(f"  {col1} ↔ {col2}: {corr_value:.3f} ({strength})")

    # Matplotlib ile görselleştirme
    plt.figure(figsize=(10, 8))

    # Heatmap oluştur - mask'i daha verimli hesapla
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        cmap="coolwarm",
        center=0,
        square=True,
        fmt=".2f",
        cbar_kws={"shrink": 0.8},
    )

    plt.title(f"Korelasyon Matrisi ({method.upper()})", fontsize=16, pad=20)
    plt.tight_layout()

    if save_plots:
        output_dir = create_output_directory(output_dir)
        plt.savefig(
            f"{output_dir}/correlation_matrix_{method}.png",
            dpi=300,
            bbox_inches="tight",
        )
        print(
            f"💾 Korelasyon matrisi kaydedildi: {output_dir}/correlation_matrix_{method}.png"
        )
        plt.close()  # Belleği temizle
    else:
        plt.show()


def distribution_plots(
    df: pd.DataFrame,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Sayısal değişkenlerin dağılım grafiklerini oluşturur.

    Parameters
    ----------
    df : pd.DataFrame
        Sadece sayısal değişkenler içeren veri seti
    save_plots : bool, default=False
        Grafikleri kaydetmek isteyip istemediğiniz
    output_dir : str, default="./quickinsights_output"
        Grafiklerin kaydedileceği dizin
    """

    if df.empty:
        print("⚠️  Dağılım grafikleri için sayısal değişken bulunamadı!")
        return

    print(f"\n📊 DAĞILIM GRAFİKLERİ ({len(df.columns)} değişken)")
    print("-" * 40)

    # Vectorized plotting - tüm kolonları aynı anda işle
    col_names = df.columns.tolist()
    n_cols = len(col_names)

    # Subplot grid hesapla - daha verimli
    n_rows = (n_cols + 2) // 3  # 3 kolon per satır
    fig, axes = plt.subplots(n_rows, 3, figsize=(15, 5 * n_rows))

    # Axes'i düzleştir - daha verimli erişim için
    if n_rows == 1:
        if n_cols <= 3:
            axes = axes.reshape(-1)  # Tek boyutlu array yap
        else:
            axes = axes.reshape(1, -1)

    # Tüm kolonları aynı anda işle - daha verimli
    for i, col in enumerate(col_names):
        row = i // 3
        col_idx = i % 3

        # Axes erişimini optimize et
        if n_rows == 1 and n_cols <= 3:
            ax = axes[col_idx]
        else:
            ax = axes[row, col_idx]

        # Histogram ve KDE - daha verimli
        sns.histplot(data=df, x=col, kde=True, bins=30, ax=ax)
        ax.set_title(f"{col} Dağılımı", fontsize=12)
        ax.set_xlabel(col)
        ax.set_ylabel("Frekans")
        ax.grid(True, alpha=0.3)

    # Boş subplot'ları gizle - daha verimli
    empty_plots = range(n_cols, n_rows * 3)
    for i in empty_plots:
        row = i // 3
        col_idx = i % 3
        if n_rows == 1:
            axes[col_idx].set_visible(False)
        else:
            axes[row, col_idx].set_visible(False)

    plt.tight_layout()

    if save_plots:
        output_dir = create_output_directory(output_dir)
        plt.savefig(
            f"{output_dir}/distribution_plots_all.png", dpi=300, bbox_inches="tight"
        )
        print(
            f"💾 Tüm dağılım grafikleri kaydedildi: {output_dir}/distribution_plots_all.png"
        )
        plt.close()  # Belleği temizle
    else:
        plt.show()


def summary_stats(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Sayısal değişkenler için istatistiksel özet döndürür.

    Parameters
    ----------
    df : pd.DataFrame
        Sadece sayısal değişkenler içeren veri seti

    Returns
    -------
    dict
        Her değişken için istatistiksel özet
    """

    if df.empty:
        return {}

    # Vectorized operations - tüm kolonları aynı anda işle
    data = df.values
    mask = ~np.isnan(data)

    summary = {}

    # Tüm kolonları aynı anda işle - daha verimli
    for i, col in enumerate(df.columns):
        col_data = data[:, i]
        col_mask = mask[:, i]

        if not np.any(col_mask):
            continue

        valid_data = col_data[col_mask]

        # İstatistikleri daha verimli hesapla
        count = int(np.sum(col_mask))
        mean_val = float(np.mean(valid_data))
        median_val = float(np.median(valid_data))
        std_val = float(np.std(valid_data))
        min_val = float(np.min(valid_data))
        max_val = float(np.max(valid_data))
        q1_val = float(np.percentile(valid_data, 25))
        q3_val = float(np.percentile(valid_data, 75))

        # Skewness ve kurtosis'i sadece gerekirse hesapla
        skewness_val = float(_calculate_skewness(valid_data)) if count >= 3 else 0.0
        kurtosis_val = float(_calculate_kurtosis(valid_data)) if count >= 4 else 0.0

        summary[col] = {
            "count": count,
            "mean": mean_val,
            "median": median_val,
            "std": std_val,
            "min": min_val,
            "max": max_val,
            "q1": q1_val,
            "q3": q3_val,
            "skewness": skewness_val,
            "kurtosis": kurtosis_val,
        }

    return summary


def _calculate_skewness(data: np.ndarray) -> float:
    """Numpy ile skewness hesaplama"""
    if len(data) < 3:
        return 0.0

    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0

    n = len(data)
    skewness = (n / ((n - 1) * (n - 2))) * np.sum(((data - mean) / std) ** 3)
    return skewness


def _calculate_kurtosis(data: np.ndarray) -> float:
    """Numpy ile kurtosis hesaplama"""
    if len(data) < 4:
        return 0.0

    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0

    n = len(data)
    kurtosis = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * np.sum(
        ((data - mean) / std) ** 4
    ) - (3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))
    return kurtosis


def create_interactive_plots(
    df: pd.DataFrame,
    save_html: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Plotly ile interaktif grafikler oluşturur.

    Parameters
    ----------
    df : pd.DataFrame
        Analiz edilecek veri seti
    save_html : bool, default=False
        HTML dosyası olarak kaydetmek isteyip istemediğiniz
    output_dir : str, default="./quickinsights_output"
        Dosyaların kaydedileceği dizin
    """

    if df.empty:
        print("⚠️  İnteraktif grafikler için veri bulunamadı!")
        return

    print(f"\n🎨 İNTERAKTİF GRAFİKLER")
    print("-" * 40)

    # DataFrame kopyalama yapmadan kolon tiplerini belirle
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) >= 2:
        # Korelasyon matrisi (Plotly) - daha verimli
        corr_matrix = df[numeric_cols].corr()

        # Heatmap verilerini hazırla - daha verimli
        z_values = corr_matrix.values
        x_labels = corr_matrix.columns.tolist()
        y_labels = corr_matrix.columns.tolist()

        fig = go.Figure(
            data=go.Heatmap(
                z=z_values,
                x=x_labels,
                y=y_labels,
                colorscale="RdBu",
                zmid=0,
                text=np.round(z_values, 3),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False,
            )
        )

        fig.update_layout(
            title="Korelasyon Matrisi (İnteraktif)", width=800, height=600
        )

        if save_html:
            output_dir = create_output_directory(output_dir)
            fig.write_html(f"{output_dir}/interactive_correlation.html")
            print(f"💾 İnteraktif korelasyon matrisi kaydedildi")

        fig.show()

    # Dağılım grafikleri (Plotly) - daha verimli
    if len(numeric_cols) > 0:
        # Subplot grid hesapla
        n_cols = len(numeric_cols)
        n_rows = (n_cols + 1) // 2

        fig = make_subplots(
            rows=n_rows,
            cols=2,
            subplot_titles=numeric_cols.tolist(),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]] * n_rows,
        )

        # Tüm kolonları aynı anda işle
        for idx, col in enumerate(numeric_cols):
            row = (idx // 2) + 1
            col_idx = (idx % 2) + 1

            # Histogram verilerini hazırla - daha verimli
            col_data = df[col].dropna().values

            fig.add_trace(
                go.Histogram(x=col_data, name=col, nbinsx=30), row=row, col=col_idx
            )

        fig.update_layout(
            title_text="Değişken Dağılımları (İnteraktif)",
            showlegend=False,
            height=300 * n_rows,
        )

        if save_html:
            output_dir = create_output_directory(output_dir)
            fig.write_html(f"{output_dir}/interactive_distributions.html")
            print(f"💾 İnteraktif dağılım grafikleri kaydedildi")

        fig.show()


def box_plots(
    df: pd.DataFrame,
    save_plot: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Sayısal değişkenler için kutu grafikleri oluşturur.

    Parameters
    ----------
    df : pd.DataFrame
        Sadece sayısal değişkenler içeren veri seti
    save_plot : bool, default=False
        Grafiği kaydetmek isteyip istemediğiniz
    output_dir : str, default="./quickinsights_output"
        Grafiğin kaydedileceği dizin
    """

    if df.empty:
        print("⚠️  Kutu grafikleri için sayısal değişken bulunamadı!")
        return

    print(f"\n📦 KUTU GRAFİKLERİ ({len(df.columns)} değişken)")
    print("-" * 40)

    # Vectorized box plotting - tüm kolonları aynı anda işle
    col_names = df.columns.tolist()
    n_cols = len(col_names)

    # Subplot grid hesapla - daha verimli
    n_rows = (n_cols + 2) // 3  # 3 kolon per satır
    fig, axes = plt.subplots(n_rows, 3, figsize=(15, 5 * n_rows))

    # Axes'i düzleştir - daha verimli erişim için
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    # Tüm kolonları aynı anda işle - daha verimli
    for i, col in enumerate(col_names):
        row = i // 3
        col_idx = i % 3

        # Axes erişimini optimize et
        if n_rows == 1 and n_cols <= 3:
            ax = axes[col_idx]
        else:
            ax = axes[row, col_idx]

        # Kutu grafiği - pandas boxplot yerine matplotlib boxplot kullan
        ax.boxplot(df[col].dropna().values)
        ax.set_title(f"{col} Kutu Grafiği", fontsize=12)
        ax.set_ylabel("Değerler")
        ax.grid(True, alpha=0.3)

    # Boş subplot'ları gizle - daha verimli
    empty_plots = range(n_cols, n_rows * 3)
    for i in empty_plots:
        row = i // 3
        col_idx = i % 3
        if n_rows == 1:
            axes[col_idx].set_visible(False)
        else:
            axes[row, col_idx].set_visible(False)

    plt.tight_layout()

    if save_plot:
        output_dir = create_output_directory(output_dir)
        plt.savefig(f"{output_dir}/box_plots_all.png", dpi=300, bbox_inches="tight")
        print(f"💾 Tüm kutu grafikleri kaydedildi: {output_dir}/box_plots_all.png")

    plt.show()
    plt.close()  # Belleği temizle
