"""
QuickInsights ana analiz modülü

Bu modül, veri setleri üzerinde kapsamlı analiz yapan ana fonksiyonları içerir.
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from typing import Dict

from .visualizer import (
    correlation_matrix,
    distribution_plots,
    summary_stats,
    create_interactive_plots,
    box_plots,
)
from .utils import (
    get_data_info,
    detect_outliers,
)


def validate_dataframe(df) -> bool:
    """
    DataFrame'in geçerli olup olmadığını kontrol eder.

    Parameters
    ----------
    df : Any
        Kontrol edilecek veri

    Returns
    -------
    bool
        DataFrame geçerliyse True, değilse False

    Raises
    ------
    ValueError
        DataFrame boşsa
    TypeError
        DataFrame değilse
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Veri bir DataFrame olmalıdır!")

    if df.empty:
        raise ValueError("DataFrame boş olamaz!")

    return True


def analyze(df, show_plots=True, save_plots=False, output_dir="./quickinsights_output"):
    """
    Veri seti üzerinde kapsamlı analiz yapar.

    Parameters
    ----------
    df : pandas.DataFrame
        Analiz edilecek veri seti
    show_plots : bool, default True
        Grafikleri göster
    save_plots : bool, default False
        Grafikleri kaydet
    output_dir : str, default "./quickinsights_output"
        Grafiklerin kaydedileceği dizin

    Returns
    -------
    dict
        Analiz sonuçları
    """
    # DataFrame validation
    validate_dataframe(df)

    print("🔍 QuickInsights - Veri Seti Analizi Başlıyor...")
    print("=" * 60)

    # Çıktı dizinini oluştur
    if save_plots:
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Çıktı dizini: {output_dir}")

    # Veri seti bilgileri
    print("\n📊 Veri Seti Bilgileri:")
    print(f"   📏 Boyut: {df.shape[0]} satır, {df.shape[1]} sütun")
    print(f"   💾 Bellek kullanımı: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    # Veri türleri
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    print(f"   🔢 Sayısal değişkenler: {len(numeric_cols)}")
    print(f"   📝 Kategorik değişkenler: {len(categorical_cols)}")

    # Eksik değer analizi
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        print("\n⚠️  Eksik Değerler:")
        for col, missing_count in missing_data[missing_data > 0].items():
            percentage = (missing_count / len(df)) * 100
            print(f"   {col}: {missing_count} ({percentage:.1f}%)")
    else:
        print("\n✅ Eksik değer bulunamadı!")

    # Sayısal değişken analizi
    if len(numeric_cols) > 0:
        print("\n🔢 Sayısal Değişken Analizi:")
        analyze_numeric(df[numeric_cols], show_plots=False)

    # Kategorik değişken analizi
    if len(categorical_cols) > 0:
        print("\n📝 Kategorik Değişken Analizi:")
        analyze_categorical(df[categorical_cols], show_plots=False)

    # Görselleştirmeler
    if show_plots or save_plots:
        if save_plots:
            print("\n📈 Görselleştirmeler oluşturuluyor ve kaydediliyor...")
        else:
            print("\n📈 Görselleştirmeler oluşturuluyor...")

        # Korelasyon matrisi (sadece sayısal değişkenler için)
        if len(numeric_cols) > 1:
            correlation_matrix(
                df[numeric_cols], save_plots=save_plots, output_dir=output_dir
            )

        # Dağılım grafikleri
        if len(numeric_cols) > 0:
            distribution_plots(
                df[numeric_cols], save_plots=save_plots, output_dir=output_dir
            )

        # Box plot'lar
        if len(numeric_cols) > 0:
            box_plots(df[numeric_cols], save_plots=save_plots, output_dir=output_dir)

        # İnteraktif grafikler
        if len(numeric_cols) > 0:
            create_interactive_plots(
                df[numeric_cols], save_plots=save_plots, output_dir=output_dir
            )

    # Özet istatistikler
    print("\n📊 Özet İstatistikler:")
    summary_stats(df)

    # Sonuçları döndür
    results = {
        "data_info": get_data_info(df),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "missing_data": missing_data.to_dict(),
        "output_directory": output_dir if save_plots else None,
    }

    print("\n✅ Analiz tamamlandı!")
    return results


def analyze_numeric(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> dict:
    """
    Sayısal değişkenler üzerinde detaylı analiz yapar.

    Parameters
    ----------
    df : pd.DataFrame
        Sadece sayısal değişkenler içeren veri seti
    show_plots : bool, default=True
        Grafikleri göstermek isteyip istemediğiniz
    save_plots : bool, default=False
        Grafikleri kaydetmek isteyip istemediğiniz
    output_dir : str, default="./quickinsights_output"
        Grafiklerin kaydedileceği dizin

    Returns
    -------
    dict
        Sayısal analiz sonuçları
    """

    if df.empty:
        print("⚠️  Sayısal değişken bulunamadı!")
        return {}

    print(f"\n🔢 SAYISAL DEĞİŞKEN ANALİZİ ({len(df.columns)} değişken)")
    print("-" * 50)

    # İstatistiksel özet
    summary = summary_stats(df)

    # Vectorized printing - tüm kolonları aynı anda işle
    col_names = df.columns.tolist()
    means = [summary[col]["mean"] for col in col_names]
    medians = [summary[col]["median"] for col in col_names]
    stds = [summary[col]["std"] for col in col_names]
    mins = [summary[col]["min"] for col in col_names]
    maxs = [summary[col]["max"] for col in col_names]
    q1s = [summary[col]["q1"] for col in col_names]
    q3s = [summary[col]["q3"] for col in col_names]

    # Batch printing
    for i, col in enumerate(col_names):
        print(f"\n📊 {col}:")
        print(f"   Ortalama: {means[i]:.4f}")
        print(f"   Medyan: {medians[i]:.4f}")
        print(f"   Standart sapma: {stds[i]:.4f}")
        print(f"   Minimum: {mins[i]:.4f}")
        print(f"   Maksimum: {maxs[i]:.4f}")
        print(f"   Çeyrekler: Q1={q1s[i]:.4f}, Q3={q3s[i]:.4f}")

    # Görselleştirmeler
    if show_plots:
        distribution_plots(df, save_plots=save_plots, output_dir=output_dir)

    return summary


def analyze_categorical(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> dict:
    """
    Kategorik değişkenler üzerinde detaylı analiz yapar.

    Parameters
    ----------
    df : pd.DataFrame
        Sadece kategorik değişkenler içeren veri seti
    show_plots : bool, default=True
        Grafikleri göstermek isteyip istemediğiniz
    save_plots : bool, default=False
        Grafikleri kaydetmek isteyip istemediğiniz
    output_dir : str, default="./quickinsights_output"
        Grafiklerin kaydedileceği dizin

    Returns
    -------
    dict
        Kategorik analiz sonuçları
    """

    if df.empty:
        print("⚠️  Kategorik değişken bulunamadı!")
        return {}

    print(f"\n🏷️  KATEGORİK DEĞİŞKEN ANALİZİ ({len(df.columns)} değişken)")
    print("-" * 50)

    # Vectorized operations - tüm kolonları aynı anda işle
    col_names = df.columns.tolist()

    # Tüm kolonlar için value_counts'ları aynı anda hesapla
    value_counts_list = [df[col].value_counts() for col in col_names]
    missing_counts = df.isnull().sum()

    results = {}

    # Batch processing - tüm kolonları aynı anda işle
    for i, col in enumerate(col_names):
        value_counts = value_counts_list[i]
        missing = missing_counts[col]

        print(f"\n📊 {col}:")
        print(f"   Benzersiz değer sayısı: {len(value_counts)}")
        print(
            f"   En yaygın değer: '{value_counts.index[0]}' ({value_counts.iloc[0]} kez)"
        )

        if missing > 0:
            print(f"   Eksik değerler: {missing}")

        print(f"   İlk 5 değer: {list(value_counts.head().index)}")

        results[col] = {
            "unique_count": len(value_counts),
            "most_common": value_counts.index[0],
            "most_common_count": value_counts.iloc[0],
            "missing_count": missing,
            "value_counts": value_counts,
        }

    return results


def summary_stats(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    DataFrame için özet istatistikler hesaplar.

    Parameters
    ----------
    df : pd.DataFrame
        Analiz edilecek veri seti

    Returns
    -------
    Dict[str, Dict[str, float]]
        Her kolon için özet istatistikler
    """
    stats = {}

    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                stats[col] = {
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q1": float(col_data.quantile(0.25)),
                    "q3": float(col_data.quantile(0.75)),
                }

    return stats


def box_plots(
    df: pd.DataFrame,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Sayısal değişkenler için box plot'lar oluşturur.

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
        print("⚠️  Box plot için sayısal değişken bulunamadı!")
        return

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        print("⚠️  Box plot için sayısal değişken bulunamadı!")
        return

    print(f"\n📦 Box Plot'lar oluşturuluyor ({len(numeric_cols)} değişken)...")

    # Box plot'ları oluştur
    fig, axes = plt.subplots(1, len(numeric_cols), figsize=(5 * len(numeric_cols), 6))

    if len(numeric_cols) == 1:
        axes = [axes]

    for i, col in enumerate(numeric_cols):
        df[col].plot(kind="box", ax=axes[i])
        axes[i].set_title(f"Box Plot - {col}")
        axes[i].set_ylabel("Değer")

    plt.tight_layout()

    if save_plots:
        output_dir = create_output_directory(output_dir)
        plt.savefig(f"{output_dir}/box_plots.png", dpi=300, bbox_inches="tight")
        print(f"💾 Box plot'lar kaydedildi: {output_dir}/box_plots.png")
        plt.close()
    else:
        plt.show()


def create_interactive_plots(
    df: pd.DataFrame,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Sayısal değişkenler için interaktif grafikler oluşturur.

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
        print("⚠️  İnteraktif grafik için sayısal değişken bulunamadı!")
        return

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        print("⚠️  İnteraktif grafik için sayısal değişken bulunamadı!")
        return

    print(f"\n🎨 İnteraktif grafikler oluşturuluyor ({len(numeric_cols)} değişken)...")

    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # Scatter plot matrix
        if len(numeric_cols) > 1:
            fig = px.scatter_matrix(df[numeric_cols], title="Scatter Plot Matrix")

            if save_plots:
                output_dir = create_output_directory(output_dir)
                fig.write_html(f"{output_dir}/scatter_matrix.html")
                print(f"💾 Scatter matrix kaydedildi: {output_dir}/scatter_matrix.html")
            else:
                fig.show()

        # Histogram'lar
        for col in numeric_cols:
            fig = px.histogram(df, x=col, title=f"Histogram - {col}")

            if save_plots:
                output_dir = create_output_directory(output_dir)
                fig.write_html(f"{output_dir}/histogram_{col}.html")
                print(f"💾 Histogram kaydedildi: {output_dir}/histogram_{col}.html")
            else:
                fig.show()

    except ImportError:
        print("⚠️  Plotly bulunamadı. İnteraktif grafikler oluşturulamıyor.")
        print("   Kurulum: pip install plotly")


def create_output_directory(output_dir: str) -> str:
    """
    Çıktı dizinini oluşturur.

    Parameters
    ----------
    output_dir : str
        Oluşturulacak dizin yolu

    Returns
    -------
    str
        Oluşturulan dizin yolu
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Çıktı dizini oluşturuldu: {output_dir}")
    return output_dir


class LazyAnalyzer:
    """
    Lazy evaluation ile veri analizi yapan sınıf.

    Bu sınıf, analizleri sadece gerektiğinde yapar ve sonuçları cache'ler.
    Böylece tekrar analizler çok daha hızlı olur.
    """

    def __init__(self, df: pd.DataFrame):
        """
        LazyAnalyzer'ı başlatır.

        Parameters
        ----------
        df : pd.DataFrame
            Analiz edilecek veri seti
        """
        self.df = df
        self._results = {}
        self._data_info = None
        self._numeric_analysis = None
        self._categorical_analysis = None
        self._correlation_matrix = None
        self._outliers = None

        # DataFrame kopyalama yapmadan kolon tiplerini belirle
        self._numeric_cols = df.select_dtypes(include=[np.number]).columns
        self._categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns

        print("🚀 LazyAnalyzer başlatıldı!")
        print(f"   📊 Veri seti boyutu: {df.shape}")
        print(
            f"   💾 Bellek kullanımı: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        )

    def get_data_info(self):
        """Veri seti genel bilgilerini döndürür (lazy)"""
        if self._data_info is None:
            print("🔍 Veri seti bilgileri hesaplanıyor...")
            self._data_info = get_data_info(self.df)
        return self._data_info

    def get_numeric_analysis(self):
        """Sayısal analiz sonuçlarını döndürür (lazy)"""
        if self._numeric_analysis is None:
            print("🔢 Sayısal analiz yapılıyor...")
            if len(self._numeric_cols) > 0:
                self._numeric_analysis = analyze_numeric(
                    self.df[self._numeric_cols], show_plots=False
                )
            else:
                self._numeric_analysis = {}
        return self._numeric_analysis

    def get_categorical_analysis(self):
        """Kategorik analiz sonuçlarını döndürür (lazy)"""
        if self._categorical_analysis is None:
            print("🏷️  Kategorik analiz yapılıyor...")
            if len(self._categorical_cols) > 0:
                self._categorical_analysis = analyze_categorical(
                    self.df[self._categorical_cols], show_plots=False
                )
            else:
                self._categorical_analysis = {}
        return self._categorical_analysis

    def get_correlation_matrix(self):
        """Korelasyon matrisini döndürür (lazy)"""
        if self._correlation_matrix is None:
            print("📊 Korelasyon matrisi hesaplanıyor...")
            if len(self._numeric_cols) > 1:
                # Korelasyon hesaplama
                self._correlation_matrix = self.df[self._numeric_cols].corr()
            else:
                self._correlation_matrix = pd.DataFrame()
        return self._correlation_matrix

    def get_outliers(self, method: str = "iqr", threshold: float = 1.5):
        """Aykırı değerleri döndürür (lazy)"""
        if self._outliers is None:
            print("⚠️  Aykırı değerler tespit ediliyor...")
            if len(self._numeric_cols) > 0:
                self._outliers = detect_outliers(
                    self.df[self._numeric_cols], method=method, threshold=threshold
                )
            else:
                self._outliers = {}
        return self._outliers

    def compute(self):
        """Tüm analizleri yapar ve sonuçları döndürür"""
        print("🚀 Tüm analizler yapılıyor...")

        results = {
            "data_info": self.get_data_info(),
            "numeric_analysis": self.get_numeric_analysis(),
            "categorical_analysis": self.get_categorical_analysis(),
            "correlation_matrix": self.get_correlation_matrix(),
            "outliers": self.get_outliers(),
        }

        print("✅ Tüm analizler tamamlandı!")
        return results

    def get_summary(self):
        """Tüm analizlerin özetini döndürür"""
        print("📋 Tüm analizler yapılıyor...")

        summary = {
            "data_info": self.get_data_info(),
            "numeric_analysis": self.get_numeric_analysis(),
            "categorical_analysis": self.get_categorical_analysis(),
            "correlation_matrix": self.get_correlation_matrix(),
            "outliers": self.get_outliers(),
        }

        return summary

    def show_plots(
        self, save_plots: bool = False, output_dir: str = "./quickinsights_output"
    ):
        """Görselleştirmeleri gösterir"""
        print("📈 Görselleştirmeler oluşturuluyor...")

        # Korelasyon matrisi
        if len(self._numeric_cols) > 1:
            correlation_matrix(
                self.df[self._numeric_cols], save_plot=save_plots, output_dir=output_dir
            )

        # Dağılım grafikleri
        if len(self._numeric_cols) > 0:
            distribution_plots(
                self.df[self._numeric_cols],
                save_plots=save_plots,
                output_dir=output_dir,
            )

    def get_cache_status(self):
        """Cache durumunu gösterir"""
        status = {
            "data_info": self._data_info is not None,
            "numeric_analysis": self._numeric_analysis is not None,
            "categorical_analysis": self._categorical_analysis is not None,
            "correlation_matrix": self._correlation_matrix is not None,
            "outliers": self._outliers is not None,
        }

        print("📊 Cache Durumu:")
        for key, cached in status.items():
            status_icon = "✅" if cached else "⏳"
            cache_text = "Cache'de" if cached else "Henüz hesaplanmadı"
            print(f"   {status_icon} {key}: {cache_text}")

        return status

    def clear_cache(self):
        """Cache'i temizler"""
        self._results = {}
        self._data_info = None
        self._numeric_analysis = None
        self._categorical_analysis = None
        self._correlation_matrix = None
        self._outliers = None
        print("🗑️  Cache temizlendi!")
