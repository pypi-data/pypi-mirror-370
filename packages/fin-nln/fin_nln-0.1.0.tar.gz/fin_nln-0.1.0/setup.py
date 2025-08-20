from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fin_nln",
    version="0.1.0",
    author="Ross Ede",
    author_email="your.email@example.com",  # Add your email
    description="A Python library for detecting nonlinearity in financial time series",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ross-Ede/fin_nln",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "statsmodels>=0.13.0",
        "yfinance>=0.2.0",
        "nolds>=0.5.2",
        "arch>=5.0.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "sphinx>=5.0.0",
        ],
        "plotting": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],
    },
    python_requires=">=3.8",
    keywords="finance, time-series, nonlinearity, econometrics, statistics",
    project_urls={
        "Bug Reports": "https://github.com/Ross-Ede/fin_nln/issues",
        "Source": "https://github.com/Ross-Ede/fin_nln",
        "Documentation": "https://github.com/Ross-Ede/fin_nln/wiki",
    },
) 