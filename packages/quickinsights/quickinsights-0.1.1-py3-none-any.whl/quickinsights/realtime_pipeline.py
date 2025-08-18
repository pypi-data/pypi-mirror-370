"""
QuickInsights - Real-Time Data Pipeline

Bu modül, gerçek zamanlı veri işleme ve analiz için pipeline sistemi sağlar.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Callable
import time
import threading
import queue
from collections import deque
import warnings

warnings.filterwarnings("ignore")

ASYNC_AVAILABLE = False


class DataTransformation:
    """Veri dönüşümü için temel sınıf"""

    def __init__(self, name: str, transform_func: Callable):
        """
        DataTransformation başlatıcısı

        Parameters
        ----------
        name : str
            Dönüşüm adı
        transform_func : Callable
            Dönüşüm fonksiyonu
        """
        self.name = name
        self.transform_func = transform_func
        self.stats = {"processed_count": 0, "error_count": 0, "processing_time": 0.0}

    def transform(self, data: Any) -> Any:
        """
        Veriyi dönüştürür

        Parameters
        ----------
        data : Any
            Dönüştürülecek veri

        Returns
        -------
        Any
            Dönüştürülmüş veri
        """
        start_time = time.time()

        try:
            result = self.transform_func(data)
            self.stats["processed_count"] += 1
            self.stats["processing_time"] += time.time() - start_time
            return result
        except Exception as e:
            self.stats["error_count"] += 1
            print(f"❌ {self.name} dönüşüm hatası: {e}")
            return data

    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndürür"""
        avg_time = (
            self.stats["processing_time"] / self.stats["processed_count"]
            if self.stats["processed_count"] > 0
            else 0
        )

        return {
            **self.stats,
            "avg_processing_time": avg_time,
            "success_rate": (
                1 - self.stats["error_count"] / max(1, self.stats["processed_count"])
            )
            * 100,
        }


class OutlierDetector(DataTransformation):
    """Aykırı değer tespit edici"""

    def __init__(self, method: str = "iqr", threshold: float = 1.5):
        """
        OutlierDetector başlatıcısı

        Parameters
        ----------
        method : str
            Tespit yöntemi ('iqr', 'zscore')
        threshold : float
            Eşik değeri
        """
        self.method = method
        self.threshold = threshold

        # Base class'ı çağır
        super().__init__("OutlierDetector", self._detect_outliers)

        # İstatistikler
        self.feature_stats = {}

    def _detect_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Aykırı değerleri tespit eder"""
        if data.empty:
            return data

        # Sayısal sütunları bul
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        outliers = pd.DataFrame(index=data.index, columns=numeric_cols, dtype=bool)

        for col in numeric_cols:
            if col not in self.feature_stats:
                # İlk kez görülen feature için istatistikleri hesapla
                self.feature_stats[col] = {
                    "mean": data[col].mean(),
                    "std": data[col].std(),
                    "q1": data[col].quantile(0.25),
                    "q3": data[col].quantile(0.75),
                    "iqr": data[col].quantile(0.75) - data[col].quantile(0.25),
                }

            if self.method == "iqr":
                q1 = self.feature_stats[col]["q1"]
                q3 = self.feature_stats[col]["q3"]
                iqr = self.feature_stats[col]["iqr"]

                lower_bound = q1 - self.threshold * iqr
                upper_bound = q3 + self.threshold * iqr

                outliers[col] = (data[col] < lower_bound) | (data[col] > upper_bound)

            elif self.method == "zscore":
                mean = self.feature_stats[col]["mean"]
                std = self.feature_stats[col]["std"]

                z_scores = np.abs((data[col] - mean) / std)
                outliers[col] = z_scores > self.threshold

        return outliers


class AnomalyDetector(DataTransformation):
    """Anomali tespit edici"""

    def __init__(self, window_size: int = 100, threshold: float = 2.0):
        """
        AnomalyDetector başlatıcısı

        Parameters
        ----------
        window_size : int
            Sliding window boyutu
        threshold : float
            Anomali eşiği
        """
        self.window_size = window_size
        self.threshold = threshold
        self.data_buffer = deque(maxlen=window_size)

        # Base class'ı çağır
        super().__init__("AnomalyDetector", self._detect_anomalies)

    def _detect_anomalies(self, data: pd.DataFrame) -> pd.DataFrame:
        """Anomalileri tespit eder"""
        if data.empty:
            return data

        # Veriyi buffer'a ekle
        self.data_buffer.extend(data.values)

        if len(self.data_buffer) < self.window_size:
            # Yeterli veri yoksa
            return pd.DataFrame(False, index=data.index, columns=data.columns)

        # Buffer'dan DataFrame oluştur
        buffer_df = pd.DataFrame(list(self.data_buffer), columns=data.columns)

        # Her feature için anomali tespiti
        anomalies = pd.DataFrame(index=data.index, columns=data.columns, dtype=bool)

        for col in data.columns:
            if col in buffer_df.columns:
                # Son window_size kadar veri için istatistikler
                recent_data = buffer_df[col].tail(self.window_size)
                mean = recent_data.mean()
                std = recent_data.std()

                # Z-score hesapla
                z_scores = np.abs((data[col] - mean) / std)
                anomalies[col] = z_scores > self.threshold

        return anomalies


class TrendAnalyzer(DataTransformation):
    """Trend analiz edici"""

    def __init__(self, window_size: int = 50, min_trend_strength: float = 0.3):
        """
        TrendAnalyzer başlatıcısı

        Parameters
        ----------
        window_size : int
            Trend analizi için window boyutu
        min_trend_strength : float
            Minimum trend gücü
        """
        self.window_size = window_size
        self.min_trend_strength = min_trend_strength
        self.data_buffer = deque(maxlen=window_size)
        self.trends = {}

        # Base class'ı çağır
        super().__init__("TrendAnalyzer", self._analyze_trends)

    def _analyze_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Trend'leri analiz eder"""
        if data.empty:
            return {}

        # Veriyi buffer'a ekle
        self.data_buffer.extend(data.values)

        if len(self.data_buffer) < self.window_size:
            return {}

        # Buffer'dan DataFrame oluştur
        buffer_df = pd.DataFrame(list(self.data_buffer), columns=data.columns)

        trends = {}

        for col in data.columns:
            if col in buffer_df.columns:
                # Son window_size kadar veri
                recent_data = buffer_df[col].tail(self.window_size)

                if len(recent_data) >= 2:
                    # Linear trend
                    x = np.arange(len(recent_data))
                    y = recent_data.values

                    try:
                        # Linear regression
                        slope = np.polyfit(x, y, 1)[0]

                        # Trend gücü (R-squared)
                        y_pred = slope * x + np.mean(y)
                        ss_res = np.sum((y - y_pred) ** 2)
                        ss_tot = np.sum((y - np.mean(y)) ** 2)
                        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

                        if r_squared >= self.min_trend_strength:
                            trends[col] = {
                                "slope": float(slope),
                                "trend_strength": float(r_squared),
                                "direction": (
                                    "increasing" if slope > 0 else "decreasing"
                                ),
                                "magnitude": abs(slope),
                            }
                    except Exception as e:
                        print(f"⚠️  Trend analizi hatası: {e}")
                        pass

        return trends


class RealTimePipeline:
    """
    Gerçek zamanlı veri işleme pipeline'ı

    Streaming veri için real-time transformation ve analytics sağlar.
    """

    def __init__(self, name: str = "RealTimePipeline"):
        """
        RealTimePipeline başlatıcısı

        Parameters
        ----------
        name : str
            Pipeline adı
        """
        self.name = name
        self.transformations = []
        self.data_queue = queue.Queue(maxsize=1000)
        self.results_queue = queue.Queue(maxsize=1000)
        self.is_running = False
        self.processing_thread = None
        self.stats = {
            "total_processed": 0,
            "total_errors": 0,
            "start_time": None,
            "processing_time": 0.0,
        }

    def add_transformation(self, transformation: DataTransformation):
        """
        Pipeline'a dönüşüm ekler

        Parameters
        ----------
        transformation : DataTransformation
            Eklenecek dönüşüm
        """
        self.transformations.append(transformation)
        print(f"✅ {transformation.name} pipeline'a eklendi")

    def add_outlier_detector(self, method: str = "iqr", threshold: float = 1.5):
        """Outlier detector ekler"""
        detector = OutlierDetector(method, threshold)
        self.add_transformation(detector)

    def add_anomaly_detector(self, window_size: int = 100, threshold: float = 2.0):
        """Anomaly detector ekler"""
        detector = AnomalyDetector(window_size, threshold)
        self.add_transformation(detector)

    def add_trend_analyzer(
        self, window_size: int = 50, min_trend_strength: float = 0.3
    ):
        """Trend analyzer ekler"""
        analyzer = TrendAnalyzer(window_size, min_trend_strength)
        self.add_transformation(analyzer)

    def start(self):
        """Pipeline'ı başlatır"""
        if self.is_running:
            print("⚠️  Pipeline zaten çalışıyor")
            return

        if not self.transformations:
            print("❌ Pipeline'da hiç dönüşüm yok")
            return

        self.is_running = True
        self.stats["start_time"] = time.time()

        # Processing thread'i başlat
        self.processing_thread = threading.Thread(
            target=self._process_data, daemon=True
        )
        self.processing_thread.start()

        print(f"🚀 {self.name} başlatıldı")

    def stop(self):
        """Pipeline'ı durdurur"""
        if not self.is_running:
            print("⚠️  Pipeline zaten durmuş")
            return

        self.is_running = False

        if self.processing_thread:
            self.processing_thread.join(timeout=5)

        self.stats["processing_time"] = time.time() - self.stats["start_time"]
        print(f"🛑 {self.name} durduruldu")

    def _process_data(self):
        """Veri işleme thread'i"""
        while self.is_running:
            try:
                # Veri kuyruğundan veri al
                data = self.data_queue.get(timeout=1)

                if data is None:  # Stop signal
                    break

                start_time = time.time()

                # Pipeline boyunca veriyi işle
                processed_data = data.copy()
                results = {}

                for transformation in self.transformations:
                    try:
                        if isinstance(transformation, TrendAnalyzer):
                            # Trend analyzer için özel işlem
                            trend_result = transformation.transform(processed_data)
                            if trend_result:
                                results[f"trends_{transformation.name}"] = trend_result
                        else:
                            # Normal dönüşüm
                            processed_data = transformation.transform(processed_data)
                            results[f"{transformation.name}_result"] = processed_data

                    except Exception as e:
                        print(f"❌ {transformation.name} hatası: {e}")
                        self.stats["total_errors"] += 1

                # Sonuçları results kuyruğuna ekle
                final_result = {
                    "original_data": data,
                    "processed_data": processed_data,
                    "transformation_results": results,
                    "timestamp": time.time(),
                    "processing_time": time.time() - start_time,
                }

                try:
                    self.results_queue.put_nowait(final_result)
                except queue.Full:
                    # Kuyruk doluysa eski sonucu çıkar
                    try:
                        self.results_queue.get_nowait()
                        self.results_queue.put_nowait(final_result)
                    except Exception as e:
                        print(f"⚠️  Kuyruk işleme hatası: {e}")
                        pass

                self.stats["total_processed"] += 1

            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Pipeline işleme hatası: {e}")
                self.stats["total_errors"] += 1

    def process_data(self, data: pd.DataFrame) -> bool:
        """
        Veriyi pipeline'a ekler

        Parameters
        ----------
        data : pd.DataFrame
            İşlenecek veri

        Returns
        -------
        bool
            Başarılı olup olmadığı
        """
        if not self.is_running:
            print("❌ Pipeline çalışmıyor. start() çağırın.")
            return False

        try:
            self.data_queue.put_nowait(data)
            return True
        except queue.Full:
            print("⚠️  Pipeline kuyruğu dolu")
            return False

    def get_results(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        İşlenmiş sonuçları alır

        Parameters
        ----------
        timeout : float
            Bekleme süresi

        Returns
        -------
        Optional[Dict[str, Any]]
            Sonuç veya None
        """
        try:
            return self.results_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Pipeline istatistiklerini döndürür"""
        transformation_stats = {}

        for transformation in self.transformations:
            transformation_stats[transformation.name] = transformation.get_stats()

        return {
            "pipeline_name": self.name,
            "is_running": self.is_running,
            "transformation_count": len(self.transformations),
            "transformation_stats": transformation_stats,
            "pipeline_stats": self.stats.copy(),
        }


class StreamingDataGenerator:
    """Streaming veri üretici"""

    def __init__(self, data_type: str = "random", interval: float = 0.1):
        """
        StreamingDataGenerator başlatıcısı

        Parameters
        ----------
        data_type : str
            Veri türü ('random', 'sine_wave', 'trend')
        interval : float
            Veri üretim aralığı (saniye)
        """
        self.data_type = data_type
        self.interval = interval
        self.is_generating = False
        self.generation_thread = None
        self.counter = 0

    def start_generation(self, callback: Callable[[pd.DataFrame], None]):
        """
        Veri üretimini başlatır

        Parameters
        ----------
        callback : Callable
            Üretilen veri için callback fonksiyonu
        """
        if self.is_generating:
            print("⚠️  Veri üretimi zaten çalışıyor")
            return

        self.is_generating = True
        self.generation_thread = threading.Thread(
            target=self._generate_data, args=(callback,), daemon=True
        )
        self.generation_thread.start()

        print(f"🚀 {self.data_type} veri üretimi başlatıldı")

    def stop_generation(self):
        """Veri üretimini durdurur"""
        self.is_generating = False

        if self.generation_thread:
            self.generation_thread.join(timeout=5)

        print("🛑 Veri üretimi durduruldu")

    def _generate_data(self, callback: Callable[[pd.DataFrame], None]):
        """Veri üretim thread'i"""
        while self.is_generating:
            try:
                # Veri üret
                data = self._create_data_batch()

                # Callback'i çağır
                callback(data)

                # Bekle
                time.sleep(self.interval)
                self.counter += 1

            except Exception as e:
                print(f"❌ Veri üretim hatası: {e}")

    def _create_data_batch(self) -> pd.DataFrame:
        """Veri batch'i oluşturur"""
        batch_size = np.random.randint(10, 51)

        if self.data_type == "random":
            data = {
                "timestamp": pd.date_range(
                    start=pd.Timestamp.now(), periods=batch_size, freq="S"
                ),
                "value1": np.random.normal(100, 20, batch_size),
                "value2": np.random.exponential(50, batch_size),
                "category": np.random.choice(["A", "B", "C"], batch_size),
            }

        elif self.data_type == "sine_wave":
            t = np.linspace(
                self.counter * self.interval,
                (self.counter + batch_size) * self.interval,
                batch_size,
            )
            data = {
                "timestamp": pd.date_range(
                    start=pd.Timestamp.now(), periods=batch_size, freq="S"
                ),
                "value1": 100 + 20 * np.sin(2 * np.pi * 0.1 * t),
                "value2": 50 + 10 * np.cos(2 * np.pi * 0.15 * t),
                "category": np.random.choice(["A", "B", "C"], batch_size),
            }

        elif self.data_type == "trend":
            base_trend = np.linspace(
                self.counter, self.counter + batch_size, batch_size
            )
            data = {
                "timestamp": pd.date_range(
                    start=pd.Timestamp.now(), periods=batch_size, freq="S"
                ),
                "value1": base_trend + np.random.normal(0, 2, batch_size),
                "value2": 100 - base_trend * 0.5 + np.random.normal(0, 3, batch_size),
                "category": np.random.choice(["A", "B", "C"], batch_size),
            }

        else:
            # Default random
            data = {
                "timestamp": pd.date_range(
                    start=pd.Timestamp.now(), periods=batch_size, freq="S"
                ),
                "value1": np.random.normal(100, 20, batch_size),
                "value2": np.random.exponential(50, batch_size),
                "category": np.random.choice(["A", "B", "C"], batch_size),
            }

        return pd.DataFrame(data)


def create_realtime_pipeline_example():
    """Real-time pipeline örneği oluşturur"""
    # Pipeline oluştur
    pipeline = RealTimePipeline("ExamplePipeline")

    # Dönüşümler ekle
    pipeline.add_outlier_detector(method="iqr", threshold=1.5)
    pipeline.add_anomaly_detector(window_size=50, threshold=2.0)
    pipeline.add_trend_analyzer(window_size=30, min_trend_strength=0.2)

    # Veri üretici oluştur
    generator = StreamingDataGenerator(data_type="sine_wave", interval=0.5)

    # Pipeline'ı başlat
    pipeline.start()

    # Veri üretimini başlat
    def data_callback(data):
        # Veriyi pipeline'a gönder
        pipeline.process_data(data)

        # Sonuçları al
        result = pipeline.get_results(timeout=0.1)
        if result:
            print(f"📊 {len(result['original_data'])} veri işlendi")
            print(f"⏱️  İşleme süresi: {result['processing_time']:.3f} saniye")

    generator.start_generation(data_callback)

    # 10 saniye çalıştır
    time.sleep(10)

    # Durdur
    generator.stop_generation()
    pipeline.stop()

    # İstatistikleri göster
    stats = pipeline.get_pipeline_stats()
    print(f"\n📊 Pipeline İstatistikleri:")
    print(f"Toplam işlenen: {stats['pipeline_stats']['total_processed']}")
    print(f"Toplam hata: {stats['pipeline_stats']['total_errors']}")

    return pipeline, generator


if __name__ == "__main__":
    # Örnek çalıştır
    pipeline, generator = create_realtime_pipeline_example()
