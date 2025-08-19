from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quickinsights",
    version="0.2.0",
    author="Eren Ata",
    author_email="erena6466@gmail.com",
    description="A creative and innovative Python library for data analysis with single command",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ErenAta16/quickinsight_library",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0,<2.0.0",
        "numpy>=1.20.0,<2.0.0",
        "matplotlib>=3.3.0,<3.8.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "dask[complete]>=2022.1.0",
        "torch>=1.9.0",
        "transformers>=4.0.0",
        "qiskit>=0.40.0",
        "cupy-cuda11x>=10.0.0; sys_platform != 'win32'",
    ],
    extras_require={
        "fast": [
            "numba>=0.56.0",
            "dask[complete]>=2022.1.0",
        ],
        "gpu": [
            "cupy-cuda11x>=10.0.0",
            "torch>=1.9.0",
        ],
        "ml": [
            "scikit-learn>=1.0.0",
            "torch>=1.9.0",
            "transformers>=4.0.0",
        ],
        "quantum": [
            "qiskit>=0.40.0",
        ],
        "cloud": [
            "boto3>=1.26.0",
            "azure-storage-blob>=12.16.0",
            "google-cloud-storage>=2.8.0",
        ],
        "profiling": [
            "psutil>=5.9.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="data analysis, data science, visualization, pandas, numpy, machine learning, quantum computing, neural networks, big data, dask",
    project_urls={
        "Bug Reports": "https://github.com/ErenAta16/quickinsight_library/issues",
        "Source": "https://github.com/ErenAta16/quickinsight_library",
        "Documentation": "https://github.com/ErenAta16/quickinsight_library/docs",
        "Changelog": "https://github.com/ErenAta16/quickinsight_library/releases",
    },
)
