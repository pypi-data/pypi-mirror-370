# QuickInsights - Hızlı Veri Keşfi

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)](https://pypi.org/project/quickinsights/)

**QuickInsights**, veri analizi öğrenenler ve hızlı veri keşfi yapmak isteyenler için tasarlanmış Python kütüphanesidir. Tek satır kod ile veri setiniz hakkında kapsamlı analiz ve görselleştirmeler elde edebilirsiniz.

## 🚀 Özellikler

### 📊 Temel Analiz
- **Veri Seti Genel Bilgileri**: Satır/sütun sayısı, bellek kullanımı, veri tipleri
- **Eksik Değer Analizi**: Eksik değer sayısı ve oranları
- **Sayısal Değişken Analizi**: İstatistiksel özetler, dağılımlar
- **Kategorik Değişken Analizi**: Frekans tabloları, en yaygın değerler
- **Aykırı Değer Tespiti**: IQR ve Z-score yöntemleri

### 🎨 Görselleştirme
- **Korelasyon Matrisi**: Heatmap ile korelasyon analizi
- **Dağılım Grafikleri**: Histogram ve KDE grafikleri
- **Kutu Grafikleri**: Aykırı değer görselleştirme
- **İnteraktif Grafikler**: Plotly ile interaktif analiz

### ⚡ Performans Optimizasyonları
- **Vectorized Operations**: NumPy ile hızlandırılmış hesaplamalar
- **Lazy Evaluation**: Sadece gerektiğinde analiz yapma
- **Caching System**: Sonuçları cache'leme
- **Parallel Processing**: Çoklu iş parçacığı desteği
- **Chunked Analysis**: Büyük veri setleri için parçalı analiz
- **Memory Optimization**: Veri tipi optimizasyonu
- **GPU Acceleration**: CuPy ile GPU desteği (opsiyonel)
- **Cloud Integration**: AWS, Azure, Google Cloud desteği

## 📦 Kurulum

### Temel Kurulum
```bash
pip install quickinsights
```

### Gelişmiş Özellikler ile Kurulum
```bash
# Hızlı işlemler için
pip install quickinsights[fast]

# GPU desteği için
pip install quickinsights[gpu]

# Cloud desteği için
pip install quickinsights[cloud]

# Profiling için
pip install quickinsights[profiling]

# Tüm özellikler
pip install quickinsights[fast,gpu,cloud,profiling]
```

### Geliştirici Kurulumu
```bash
git clone https://github.com/erena6466/quickinsights.git
cd quickinsights
pip install -e .
```

## 🎯 Hızlı Başlangıç

### Basit Kullanım
```python
import quickinsights as qi
import pandas as pd

# Veri setini yükle
df = pd.read_csv('your_data.csv')

# Kapsamlı analiz
results = qi.analyze(df)
```

### Detaylı Analiz
```python
# Sayısal değişkenler için
numeric_analysis = qi.analyze_numeric(df)

# Kategorik değişkenler için
categorical_analysis = qi.analyze_categorical(df)

# Aykırı değer tespiti
outliers = qi.detect_outliers(df)
```

### Lazy Analyzer (Önerilen)
```python
# Lazy evaluation ile analiz
lazy_analyzer = qi.LazyAnalyzer(df)

# Sadece gerektiğinde analiz yap
data_info = lazy_analyzer.get_data_info()
numeric_analysis = lazy_analyzer.get_numeric_analysis()

# Tüm analizleri yap
all_results = lazy_analyzer.compute()
```

### Paralel Analiz
```python
# Paralel analiz
parallel_results = qi.parallel_analysis(df, n_jobs=4)

# Chunked analiz (büyük veri setleri için)
chunk_results = qi.chunked_analysis(df, chunk_size=10000)
```

## 🔧 Gelişmiş Özellikler

### Veri Tipi Optimizasyonu
```python
# Bellek kullanımını optimize et
optimized_df = qi.optimize_dtypes(df)
```

### GPU Hızlandırma
```python
# GPU desteği kontrol et
if qi.get_gpu_status():
    # GPU ile analiz
    gpu_results = qi.gpu_summary_stats(df)
```

### Cloud Entegrasyonu
```python
# Cloud veri yöneticisi
cloud_manager = qi.CloudDataManager()
cloud_results = cloud_manager.analyze_cloud_dataset('s3://bucket/data.csv')
```

## 📚 Dokümantasyon

Detaylı dokümantasyon için:
- [API Reference](docs/api.md)
- [Performance Guide](docs/performance.md)
- [Examples](examples/)
- [Optimization Roadmap](OPTIMIZATION_ROADMAP.md)

## 🧪 Test

```bash
# Tüm testleri çalıştır
python -m pytest tests/

# Coverage ile test
python -m pytest --cov=quickinsights tests/
```

## 📈 Performans

QuickInsights, aşağıdaki optimizasyonlarla hızlandırılmıştır:

- **Vectorized Operations**: 10-100x hızlanma
- **Lazy Evaluation**: Cache ile anında erişim
- **Parallel Processing**: 2-4x hızlanma
- **Memory Optimization**: %30-50 bellek tasarrufu
- **GPU Acceleration**: 5-20x hızlanma (GPU'da)

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- [Pandas](https://pandas.pydata.org/) - Veri analizi
- [NumPy](https://numpy.org/) - Sayısal hesaplamalar
- [Matplotlib](https://matplotlib.org/) - Görselleştirme
- [Seaborn](https://seaborn.pydata.org/) - İstatistiksel görselleştirme
- [Plotly](https://plotly.com/) - İnteraktif grafikler
- [Numba](https://numba.pydata.org/) - JIT compilation
- [Dask](https://dask.org/) - Paralel işleme

## 📞 İletişim

- **Proje**: [GitHub Issues](https://github.com/yourusername/quickinsights/issues)
- **Email**: your.email@example.com
- **Website**: [https://quickinsights.readthedocs.io](https://quickinsights.readthedocs.io)

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
