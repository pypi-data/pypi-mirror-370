# QuickInsights

A creative and innovative Python library for data analysis that goes beyond basic libraries like NumPy and Pandas. Provides advanced features for big data analysis with a single command.

## What is it?

QuickInsights is a Python package that provides comprehensive data analysis capabilities through an intuitive interface. It aims to be a powerful tool for data scientists, analysts, and researchers who need to perform complex data analysis tasks efficiently.

## Main Features

- **Comprehensive Data Analysis**: Single-command data set analysis with detailed insights
- **Advanced Visualization**: Integration with Matplotlib, Seaborn and Plotly for professional charts
- **Performance Optimization**: Lazy evaluation, caching, parallel processing for large datasets
- **Cloud Integration**: Support for AWS S3, Azure Blob, Google Cloud Storage
- **AI-Powered Insights**: Automatic pattern detection and trend analysis using machine learning
- **Real-time Pipeline**: Streaming data processing capabilities
- **Modular Architecture**: Easily extensible and customizable framework

## Installation

### From PyPI (Recommended)

```bash
pip install quickinsights
```

### From Test PyPI (Developer Version)

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ quickinsights
```

### From Source

```bash
git clone https://github.com/erena6466/quickinsights.git
cd quickinsights
pip install -e .
```

## Quick Start

```python
import quickinsights as qi
import pandas as pd

# Sample dataset
df = pd.DataFrame({
    'A': [1, 2, 3, 4, 5],
    'B': [4, 5, 6, 7, 8],
    'C': ['a', 'b', 'a', 'b', 'a']
})

# Comprehensive analysis with single command
result = qi.analyze(df, show_plots=True, save_plots=True)

# Dataset information
info = qi.get_data_info(df)

# Outlier detection
outliers = qi.detect_outliers(df)

# Performance optimization
optimized_df = qi.memory_optimize(df)
```

## Advanced Usage

### AI-Powered Analysis

```python
from quickinsights.ai_insights import AIInsightEngine

ai_engine = AIInsightEngine(df)
insights = ai_engine.get_insights()
trends = ai_engine.predict_trends()
```

### Cloud Integration

```python
# Upload to AWS S3
qi.upload_to_cloud('data.csv', 'aws', 'my-bucket/data.csv', bucket_name='my-bucket')

# Process data from cloud
result = qi.process_cloud_data('aws', 'my-bucket/data.csv', processor_func, bucket_name='my-bucket')
```

### Real-time Pipeline

```python
from quickinsights.realtime_pipeline import RealTimePipeline

pipeline = RealTimePipeline()
pipeline.add_transformation(lambda x: x * 2)
pipeline.add_filter(lambda x: x > 10)
results = pipeline.process_stream(data_stream)
```

## Dependencies

- **Core**: pandas>=1.3.0, numpy>=1.20.0, matplotlib>=3.3.0
- **Visualization**: seaborn>=0.11.0, plotly>=5.0.0
- **Scientific**: scipy>=1.7.0
- **Optional**: numba, dask, cupy, boto3, azure-storage-blob, google-cloud-storage

## Documentation

For detailed API documentation, see [docs/api.md](docs/api.md).

For command list, see [COMMANDS.md](COMMANDS.md).

## Contributing

To contribute, please read [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License.

## Support

- **GitHub Issues**: [https://github.com/erena6466/quickinsights/issues](https://github.com/erena6466/quickinsights/issues)
- **Documentation**: [docs/](docs/) folder
- **Examples**: [examples/](examples/) folder

## Project Status

- **Core Library**: Completed
- **Modular Architecture**: Completed
- **Test Suite**: 100% success rate
- **PyPI Release**: Version 0.1.1 available
- **Documentation**: Comprehensive documentation

## Future Plans

- [ ] Enhanced ML algorithms
- [ ] Web dashboard interface
- [ ] Performance benchmarks
- [ ] Community building
- [ ] Additional data sources

---

**QuickInsights** - Simplifying data analysis and enhancing performance with Python 🚀
